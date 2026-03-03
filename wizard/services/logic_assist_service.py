"""v1.5 logic-assist runtime service."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from pathlib import Path
from typing import Any

from core.services.time_utils import utc_now_iso_z
from wizard.services.cloud_provider_executor import (
    get_cloud_availability,
    run_cloud_with_fallback,
)
from wizard.services.local_model_gpt4all import GPT4AllLocalAssist
from wizard.services.logging_api import get_logger
from wizard.services.logic_assist_profile import (
    LogicAssistProfile,
    load_logic_assist_profile,
)
from wizard.services.quota_tracker import APIProvider, get_quota_tracker, record_usage

logger = get_logger("wizard.logic-assist")


@dataclass
class LogicAssistRequest:
    prompt: str
    model: str = ""
    system_prompt: str = ""
    max_tokens: int = 1024
    temperature: float | None = None
    mode: str | None = None
    force_network: bool = False
    allow_network: bool = True
    offline_required: bool = False
    conversation_id: str | None = None
    workspace: str = "core"
    privacy: str = "internal"
    tags: list[str] = field(default_factory=list)
    actor: str | None = None


@dataclass
class LogicAssistResponse:
    success: bool
    content: str = ""
    model: str = ""
    provider: str = ""
    backend: str = ""
    cost: float = 0.0
    route: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    timestamp: str = field(default_factory=utc_now_iso_z)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LogicAssistService:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.profile = load_logic_assist_profile(repo_root)
        self.local = GPT4AllLocalAssist(self.profile, repo_root)
        self.quota = get_quota_tracker()
        self.cache_root = repo_root / "memory" / "wizard" / "logic_cache"
        self.cache_root.mkdir(parents=True, exist_ok=True)

    def get_status(self) -> dict[str, Any]:
        local = self.local.status().to_dict()
        network = get_cloud_availability()
        return {
            "schema": "udos-logic-assist-v1.5",
            "profile": self.profile.to_dict(),
            "local": local,
            "network": {
                **network,
                "budget": self._budget_status(),
            },
        }

    def list_models(self) -> list[dict[str, Any]]:
        local = self.local.status()
        models = [
            {
                "id": self.profile.local_model_name,
                "provider": "gpt4all",
                "tier": "local",
                "available": local.ready,
                "path": local.model_path,
            }
        ]
        network = get_cloud_availability()
        for provider_id in network.get("available_providers", []):
            models.append(
                {
                    "id": provider_id,
                    "provider": provider_id,
                    "tier": self._provider_tier(provider_id),
                    "available": True,
                }
            )
        return models

    async def complete(
        self, request: LogicAssistRequest, device_id: str
    ) -> LogicAssistResponse:
        prompt = (request.prompt or "").strip()
        if not prompt:
            return LogicAssistResponse(success=False, error="prompt is required")

        cache_key = self._cache_key(prompt, request)
        if self.profile.response_cache_enabled:
            cached = self._read_cache(cache_key)
            if cached:
                return LogicAssistResponse(**cached)

        local_status = self.local.status()
        use_network = bool(request.force_network)
        if request.offline_required:
            use_network = False
        elif not local_status.ready and request.allow_network and self.profile.network_enabled:
            use_network = True

        try:
            if use_network:
                content, model = run_cloud_with_fallback(prompt)
                provider = self.profile.network_primary_provider
                backend = "wizard-network"
                cost = self._estimate_network_cost(prompt, content, provider)
                self._record_network_usage(provider, prompt, content, cost)
                response = LogicAssistResponse(
                    success=True,
                    content=content,
                    model=model,
                    provider=provider,
                    backend=backend,
                    cost=cost,
                    route={
                        "mode": request.mode or "general",
                        "source": "network",
                        "tier": self._provider_tier(provider),
                    },
                )
            else:
                content = self.local.generate(prompt, system=request.system_prompt)
                response = LogicAssistResponse(
                    success=True,
                    content=content,
                    model=self.profile.local_model_name,
                    provider="gpt4all",
                    backend="local-assist",
                    cost=0.0,
                    route={
                        "mode": request.mode or "general",
                        "source": "local",
                        "tier": "local",
                    },
                )
        except Exception as exc:
            logger.warn("logic assist request failed: %s", exc)
            response = LogicAssistResponse(success=False, error=str(exc))

        if response.success and self.profile.response_cache_enabled:
            self._write_cache(cache_key, response.to_dict())
        return response

    def _budget_status(self) -> dict[str, Any]:
        quotas = self.quota.get_all_quotas()
        return {
            "daily_limit_usd": self.profile.daily_limit_usd,
            "tier0_daily_limit_usd": self.profile.tier0_daily_limit_usd,
            "tier1_daily_limit_usd": self.profile.tier1_daily_limit_usd,
            "tier2_daily_limit_usd": self.profile.tier2_daily_limit_usd,
            "providers": quotas,
        }

    def _provider_tier(self, provider_id: str) -> str:
        normalized = provider_id.lower()
        if normalized == self.profile.network_tier0_provider:
            return "tier0"
        if normalized == self.profile.network_tier1_provider:
            return "tier1"
        if normalized == self.profile.network_tier2_provider:
            return "tier2"
        return "tier1"

    def _estimate_network_cost(
        self, prompt: str, content: str, provider_id: str
    ) -> float:
        input_tokens = max(len(prompt.split()), 1)
        output_tokens = max(len(content.split()), 1)
        tier = self._provider_tier(provider_id)
        if tier == "tier0":
            return 0.0
        if tier == "tier1":
            return round(((input_tokens + output_tokens) / 1000) * 0.002, 6)
        return round(((input_tokens + output_tokens) / 1000) * 0.01, 6)

    def _record_network_usage(
        self, provider_id: str, prompt: str, content: str, cost: float
    ) -> None:
        provider_map = {
            "openrouter": APIProvider.MISTRAL,
            "mistral": APIProvider.MISTRAL,
            "openai": APIProvider.OPENAI,
            "anthropic": APIProvider.ANTHROPIC,
            "gemini": APIProvider.GEMINI,
        }
        provider = provider_map.get(provider_id.lower())
        if provider is None:
            return
        record_usage(
            provider=provider,
            input_tokens=max(len(prompt.split()), 1),
            output_tokens=max(len(content.split()), 1),
            cost=cost,
        )

    def _cache_key(self, prompt: str, request: LogicAssistRequest) -> str:
        digest = hashlib.sha256()
        digest.update(prompt.encode("utf-8"))
        digest.update((request.mode or "").encode("utf-8"))
        digest.update(request.workspace.encode("utf-8"))
        return digest.hexdigest()

    def _cache_path(self, cache_key: str) -> Path:
        return self.cache_root / f"{cache_key}.json"

    def _read_cache(self, cache_key: str) -> dict[str, Any] | None:
        path = self._cache_path(cache_key)
        if not path.exists():
            return None
        import json

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def _write_cache(self, cache_key: str, payload: dict[str, Any]) -> None:
        import json

        path = self._cache_path(cache_key)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


_LOGIC_ASSIST: LogicAssistService | None = None


def get_logic_assist_service(repo_root: Path | None = None) -> LogicAssistService:
    global _LOGIC_ASSIST
    resolved = repo_root or Path(__file__).resolve().parents[2]
    if _LOGIC_ASSIST is None or _LOGIC_ASSIST.repo_root != resolved:
        _LOGIC_ASSIST = LogicAssistService(resolved)
    return _LOGIC_ASSIST
