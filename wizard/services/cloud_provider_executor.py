"""Cloud Provider Executor

Multi-provider fallback chain executor for uDOS Wizard cloud mode.

Replaces the Mistral-hardcoded path with a deterministic fallback chain
using all configured providers (Mistral → OpenRouter → OpenAI → Anthropic → Gemini).
"""

from __future__ import annotations

import os
from typing import Any

from core.services.cloud_provider_policy import (
    CloudProvider,
    FailoverReason,
    attach_auth,
    canonical_cloud_provider_contracts,
    classify_failover_reason,
    parse_cloud_response,
    prepare_cloud_request,
    resolve_cloud_provider_chain,
    resolve_provider_api_key,
    should_failover,
)
from wizard.services.logging_api import get_logger
from wizard.services.quota_tracker import APIProvider, get_quota_tracker

logger = get_logger("wizard.cloud-executor")

_SYSTEM_PROMPT = (
    "You are the uDOS Wizard Dev Mode assistant. Use the provided context."
)


def _load_context() -> str:
    """Load uDOS OK context bundle as a text string."""
    try:
        from wizard.services.ok_context_store import write_ok_context_bundle

        ctx_path = write_ok_context_bundle()
        return ctx_path.read_text()
    except Exception as exc:
        logger.debug("Context bundle unavailable: %s", exc)
        return ""


def _inject_context_into_request(
    req_payload: dict[str, Any],
    context: str,
    provider: CloudProvider,
) -> dict[str, Any]:
    """Inject uDOS system context into the provider request payload."""
    if not context.strip():
        return req_payload

    payload = dict(req_payload)
    system_content = f"{_SYSTEM_PROMPT}\n\n{context}"

    if provider in {CloudProvider.MISTRAL, CloudProvider.OPENROUTER, CloudProvider.OPENAI}:
        # OpenAI-style: prepend a system message
        messages = list(payload.get("messages", []))
        messages = [{"role": "system", "content": system_content}] + [
            m for m in messages if m.get("role") != "system"
        ]
        payload["messages"] = messages

    elif provider == CloudProvider.ANTHROPIC:
        # Anthropic Messages API: top-level "system" field
        payload["system"] = system_content

    elif provider == CloudProvider.GEMINI:
        # Gemini: prepend context to the first user part
        contents = list(payload.get("contents", []))
        if contents and isinstance(contents[0], dict):
            parts = list(contents[0].get("parts", []))
            if parts and isinstance(parts[0], dict) and "text" in parts[0]:
                parts[0] = {"text": f"{system_content}\n\nUser request: {parts[0]['text']}"}
            contents[0] = dict(contents[0])
            contents[0]["parts"] = parts
        payload["contents"] = contents

    return payload


def _env_getter(key: str) -> str:
    """Unified env getter using UnifiedConfigLoader with os.environ fallback."""
    try:
        from core.services.unified_config_loader import get_config
        return get_config(key, "") or ""
    except Exception:
        return os.environ.get(key, "")


def _provider_to_quota_provider(provider: CloudProvider) -> APIProvider | None:
    mapping = {
        CloudProvider.MISTRAL: APIProvider.MISTRAL,
        CloudProvider.OPENROUTER: APIProvider.MISTRAL,
        CloudProvider.OPENAI: APIProvider.OPENAI,
        CloudProvider.ANTHROPIC: APIProvider.ANTHROPIC,
        CloudProvider.GEMINI: APIProvider.GEMINI,
    }
    return mapping.get(provider)


def _estimated_tokens(prompt: str, estimated_tokens: int | None = None) -> int:
    if estimated_tokens is not None:
        return max(int(estimated_tokens), 0)
    words = max(len((prompt or "").split()), 1)
    return words * 2


def get_cloud_execution_plan(
    prompt: str = "",
    *,
    estimated_tokens: int | None = None,
) -> dict[str, Any]:
    chain = resolve_cloud_provider_chain(_env_getter)
    contracts = canonical_cloud_provider_contracts()
    quota = get_quota_tracker()
    estimate = _estimated_tokens(prompt, estimated_tokens)
    available: list[str] = []
    unavailable: list[str] = []
    quota_ready: list[str] = []
    blocked_by_quota: list[str] = []
    providers: list[dict[str, Any]] = []

    for provider in chain:
        contract = contracts[provider]
        api_key = resolve_provider_api_key(contract, _env_getter)
        configured = bool(api_key)
        quota_provider = _provider_to_quota_provider(provider)
        quota_allowed = True
        if quota_provider is not None:
            quota_allowed = quota.can_request(quota_provider, estimate)
        entry = {
            "provider": provider.value,
            "configured": configured,
            "quota_allowed": quota_allowed,
        }
        providers.append(entry)
        if configured:
            available.append(provider.value)
            if quota_allowed:
                quota_ready.append(provider.value)
            else:
                blocked_by_quota.append(provider.value)
        else:
            unavailable.append(provider.value)

    return {
        "ready": bool(quota_ready),
        "issue": None if quota_ready else ("all configured providers blocked by quota" if available else "no cloud provider API keys configured"),
        "available_providers": available,
        "unavailable_providers": unavailable,
        "quota_ready_providers": quota_ready,
        "blocked_by_quota": blocked_by_quota,
        "primary": quota_ready[0] if quota_ready else (available[0] if available else None),
        "estimated_tokens": estimate,
        "providers": providers,
    }


def _try_provider(
    provider: CloudProvider,
    prompt: str,
    context: str,
) -> tuple[str, str, FailoverReason]:
    """Attempt one provider. Returns (response, model, failover_reason).

    On success: (response_text, model_name, FailoverReason.NONE)
    On failure: ("", "", reason_for_failover)
    """
    contracts = canonical_cloud_provider_contracts()
    contract = contracts[provider]

    api_key = resolve_provider_api_key(contract, _env_getter)
    if not api_key:
        logger.debug("Provider %s: no API key", provider.value)
        return "", "", FailoverReason.AUTH_MISSING

    try:
        import requests

        req = prepare_cloud_request(contract, prompt, _env_getter)
        payload = _inject_context_into_request(req.payload, context, provider)
        authed_req = attach_auth(contract, req, api_key)
        # Use the payload with context injected (not the original payload)
        authed_req_with_context = type(authed_req)(
            url=authed_req.url,
            headers=authed_req.headers,
            payload=payload,
            timeout_seconds=authed_req.timeout_seconds,
            model_name=authed_req.model_name,
        )

        resp = requests.post(
            authed_req_with_context.url,
            json=authed_req_with_context.payload,
            headers=authed_req_with_context.headers,
            timeout=authed_req_with_context.timeout_seconds,
        )

        if resp.status_code == 200:
            response_text = parse_cloud_response(contract, resp.json())
            logger.info("Cloud OK via %s model=%s", provider.value, req.model_name)
            return response_text, req.model_name, FailoverReason.NONE

        reason = classify_failover_reason(resp.status_code)
        logger.debug(
            "Provider %s: HTTP %s → %s", provider.value, resp.status_code, reason.value
        )
        return "", "", reason

    except requests.exceptions.Timeout:
        logger.debug("Provider %s: timeout", provider.value)
        return "", "", FailoverReason.UNREACHABLE
    except requests.exceptions.ConnectionError:
        logger.debug("Provider %s: connection error", provider.value)
        return "", "", FailoverReason.UNREACHABLE
    except Exception as exc:
        logger.warn("Provider %s: unexpected error: %s", provider.value, exc)
        return "", "", FailoverReason.UNKNOWN


def run_cloud_with_fallback(prompt: str) -> tuple[str, str]:
    result = run_cloud_with_fallback_detail(prompt)
    return result["response"], result["model"]


def run_cloud_with_fallback_detail(
    prompt: str,
    *,
    estimated_tokens: int | None = None,
) -> dict[str, Any]:
    """Run a cloud OK request using the configured provider fallback chain.

    Args:
        prompt: User prompt text

    Returns:
        (response_text, model_name) tuple — same signature as MistralAPI.chat()

    Raises:
        RuntimeError: If all providers in the chain fail or are unconfigured.
    """
    chain = resolve_cloud_provider_chain(_env_getter)
    context = _load_context()
    plan = get_cloud_execution_plan(prompt, estimated_tokens=estimated_tokens)
    quota = get_quota_tracker()
    estimate = int(plan.get("estimated_tokens") or 0)
    skipped: list[str] = []
    attempts: list[dict[str, Any]] = []

    for provider in chain:
        quota_provider = _provider_to_quota_provider(provider)
        if quota_provider is not None and not quota.can_request(quota_provider, estimate):
            attempts.append(
                {
                    "provider": provider.value,
                    "result": "skipped",
                    "reason": "quota_exceeded",
                }
            )
            skipped.append(f"{provider.value}:quota_exceeded")
            continue
        response, model, reason = _try_provider(provider, prompt, context)

        if reason == FailoverReason.NONE:
            attempts.append(
                {
                    "provider": provider.value,
                    "result": "success",
                    "model": model,
                }
            )
            return {
                "response": response,
                "model": model,
                "provider": provider.value,
                "attempts": attempts,
                "plan": plan,
            }

        attempts.append(
            {
                "provider": provider.value,
                "result": "failed",
                "reason": reason.value,
            }
        )
        skipped.append(f"{provider.value}:{reason.value}")

        if not should_failover(reason):
            # Non-retriable error — stop chain
            logger.warn(
                "Cloud chain stopped at %s (non-retriable: %s)", provider.value, reason.value
            )
            break

        logger.debug("Failing over from %s (%s)", provider.value, reason.value)

    attempts_summary = ", ".join(skipped) if skipped else "none"
    raise RuntimeError(
        f"All cloud providers failed or unconfigured. Attempts: [{attempts_summary}]. "
        "Configure at least one provider API key (MISTRAL_API_KEY, OPENROUTER_API_KEY, "
        "OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY)."
    )


def get_cloud_availability() -> dict[str, Any]:
    """Return multi-provider availability status for the cloud chain.

    Returns:
        Dict with ready flag, available providers, and issue summary.
    """
    return get_cloud_execution_plan()
