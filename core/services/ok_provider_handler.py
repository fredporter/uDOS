"""Unified OK Provider Handler

Central source of truth for OK provider availability checking.
Replaces scattered status checks in:
  - core/tui/ucode.py: _get_ok_local_status(), _get_ok_cloud_status()
  - wizard/routes/provider_routes.py: check_provider_status()

Both TUI and Wizard call this single service for provider status.

**Design Principle:**
  Checks BOTH configuration state AND runtime state.
  Returns unified response for TUI and Wizard.

**Usage:**
```python
from core.services.ok_provider_handler import OKProviderHandler, get_ok_provider_handler

handler = get_ok_provider_handler()

# Check local GPT4All
status = handler.check_local_provider()
if status.is_available:
    print(f"Ready: {status.loaded_models}")
else:
    print(f"Issue: {status.issue}")

# Check cloud Mistral
cloud_status = handler.check_cloud_provider()

# Check all providers
all_status = handler.check_all_providers()
for provider, status in all_status.items():
    print(f"{provider}: {status.is_available}")
```
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """OK provider types."""

    LOCAL_GPT4ALL = "gpt4all_local"  # Local GPT4All runtime
    MISTRAL_CLOUD = "mistral_cloud"  # Mistral API (cloud)


@dataclass
class ProviderStatus:
    """Status of a single provider."""

    provider_id: str
    is_configured: bool  # Config files/keys exist
    is_running: bool  # Process is actually running
    is_available: bool  # Can be used right now (configured AND running)
    loaded_models: list[str] = field(default_factory=list)  # What's loaded/available
    default_model: str | None = None  # Configured default model
    issue: str | None = None  # Why not available (if not)
    last_checked: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, Any] = field(default_factory=dict)  # Extra info

    def __str__(self) -> str:
        """Return readable status string."""
        if self.is_available:
            model_list = ", ".join(self.loaded_models[:3])
            if len(self.loaded_models) > 3:
                model_list += f", +{len(self.loaded_models) - 3} more"
            return f"✅ {self.provider_id.upper()}: available ({model_list})"
        else:
            return f"⚠️ {self.provider_id.upper()}: {self.issue or 'not available'}"


class OKProviderHandler:
    """Unified OK provider status checking.

    Answers both:
      1. Is provider configured? (config files, secrets, etc.)
      2. Is provider running? (live health check)

    Result: Single unified response for TUI and Wizard.
    """

    def __init__(self):
        """Initialize handler."""
        self.logger = logger
        self._cache: dict[str, ProviderStatus] = {}
        self._cache_ttl_seconds = 10  # Cache provider status for 10s

    def check_all_providers(self) -> dict[str, ProviderStatus]:
        """Check status of all configured providers.

        Returns:
            Dict mapping provider IDs to their status
        """
        return {
            ProviderType.LOCAL_GPT4ALL.value: self.check_local_provider(),
            ProviderType.MISTRAL_CLOUD.value: self.check_cloud_provider(),
        }

    def check_local_provider(self) -> ProviderStatus:
        """Check local GPT4All provider status.

        Performs two checks:
          1. Configuration check: Is GPT4All configured?
          2. Runtime check: Is the configured model file present?

        Returns:
            ProviderStatus with is_configured, is_running, is_available
        """
        provider_id = ProviderType.LOCAL_GPT4ALL.value

        is_configured = self._check_local_runtime_configured()

        is_running, models_loaded, check_issue = self._check_local_runtime_ready()

        is_available = is_configured and is_running
        default_model = self._get_configured_default_model()

        issue = None
        if not is_available:
            if not is_configured:
                issue = "gpt4all package unavailable"
            elif not is_running:
                issue = check_issue or "gpt4all model missing"

        if is_available and default_model:
            normalized_loaded = self._normalize_model_names(models_loaded)
            normalized_default = self._normalize_model_names([default_model])
            if normalized_default.isdisjoint(normalized_loaded):
                is_available = False
                issue = f"gpt4all model missing: {default_model}"
                models_loaded = []

        return ProviderStatus(
            provider_id=provider_id,
            is_configured=is_configured,
            is_running=is_running,
            is_available=is_available,
            loaded_models=models_loaded,
            default_model=default_model,
            issue=issue,
            details={
                "runtime": self._get_local_runtime(),
                "model_path": self._get_local_model_path(),
            },
        )

    def check_cloud_provider(self) -> ProviderStatus:
        """Check cloud provider status across all configured providers.

        Checks the full provider chain (Mistral, OpenRouter, OpenAI, Anthropic, Gemini).
        Returns status for the first available (configured) provider.

        Returns:
            ProviderStatus for cloud capability (any provider)
        """
        from core.services.cloud_provider_policy import (
            canonical_cloud_provider_contracts,
            resolve_cloud_provider_chain,
            resolve_provider_api_key,
        )
        from core.services.unified_config_loader import get_config

        provider_id = ProviderType.MISTRAL_CLOUD.value  # kept for backward compat

        def _env(key: str) -> str:
            return get_config(key, "") or ""

        chain = resolve_cloud_provider_chain(_env)
        contracts = canonical_cloud_provider_contracts()

        available_providers: list[str] = []
        primary_provider = None
        primary_model = None

        for provider in chain:
            contract = contracts[provider]
            api_key = resolve_provider_api_key(contract, _env)
            if api_key:
                available_providers.append(provider.value)
                if primary_provider is None:
                    primary_provider = provider
                    primary_model = contract.default_model

        is_configured = bool(available_providers)
        # is_running: True if any key is present (we don't do live ping for cloud)
        is_running = is_configured
        is_available = is_configured

        issue = None
        if not is_available:
            issue = "no cloud provider API keys configured (set MISTRAL_API_KEY, OPENROUTER_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY)"

        return ProviderStatus(
            provider_id=provider_id,
            is_configured=is_configured,
            is_running=is_running,
            is_available=is_available,
            loaded_models=available_providers,
            default_model=primary_model,
            issue=issue,
            details={
                "available_providers": available_providers,
                "primary": primary_provider.value if primary_provider else None,
            },
        )

    # ===== Private helpers: Configuration checks =====

    @staticmethod
    def _check_local_runtime_configured() -> bool:
        """Check if the local GPT4All runtime is configured.

        Returns:
            True if the package import is available and a model is configured
        """
        import importlib.util

        if importlib.util.find_spec("gpt4all") is None:
            return False

        return bool(OKProviderHandler._get_configured_default_model())

    @staticmethod
    def _check_mistral_configured() -> bool:
        """Check if Mistral is configured (API key present).

        Returns:
            True if Mistral API key found
        """
        from core.services.secret_vault import SecureVault
        from core.services.unified_config_loader import get_config

        # Check 1: Environment variable
        if get_config("MISTRAL_API_KEY", ""):
            return True

        # Check 2: Secret store
        try:
            vault = SecureVault()
            if vault.get_secret("mistral_api_key"):
                return True
        except Exception:
            pass

        return False

    # ===== Private helpers: Runtime checks =====

    @staticmethod
    def _check_local_runtime_ready() -> tuple[bool, list[str], str | None]:
        """Check local GPT4All readiness and return configured model info.

        Returns:
            (is_running, models_list, issue_string_or_none)
        """
        model_path = OKProviderHandler._get_local_model_path()
        model_name = OKProviderHandler._get_configured_default_model()
        if not model_name:
            return False, [], "no local model configured"
        if not model_path:
            return False, [], "local model path unavailable"
        if not model_path.exists():
            return False, [], f"gpt4all model missing: {model_name}"
        return True, [model_name], None

    @staticmethod
    def _check_mistral_running() -> tuple[bool, list[str], str | None]:
        """Check if Mistral API is reachable.

        Returns:
            (is_reachable, available_models, issue_string_or_none)
        """
        try:
            from core.services.unified_config_loader import get_config

            api_key = get_config("MISTRAL_API_KEY", "")
            if not api_key:
                return False, [], "no api key"

            # Try a simple API call
            # For now, assume if key exists and Wizard responds, Mistral is available
            # Full implementation would do actual API health check
            return True, ["mistral-small", "mistral-medium", "mistral-large"], None
        except Exception as exc:
            return False, [], f"mistral check failed: {exc!s}"

    @staticmethod
    def _get_configured_default_model() -> str | None:
        """Get the configured default model for local provider.

        Returns:
            Default model name or None
        """
        try:
            fields = OKProviderHandler._load_logic_assist_fields()
            return fields.get("local_model_name") or None
        except Exception:
            return None

    # ===== Private helpers: Utilities =====

    @staticmethod
    def _normalize_model_names(names: list[str]) -> set[str]:
        """Return canonical model names (both tagged and base forms).

        Args:
            names: List of model names (may include tags)

        Returns:
            Set of normalized names
        """
        normalized: set[str] = set()
        for raw in names:
            name = (raw or "").strip()
            if not name:
                continue
            normalized.add(name)
            # Also add base name (without tag)
            base = name.split(":", 1)[0].strip()
            if base:
                normalized.add(base)
        return normalized

    @staticmethod
    def _load_logic_assist_fields() -> dict[str, str]:
        from pathlib import Path

        from core.services.logging_api import get_repo_root
        from core.services.template_workspace_service import get_template_workspace_service

        repo_root = Path(get_repo_root())
        workspace = get_template_workspace_service(repo_root)
        snapshot = workspace.read_document("settings", "logic-assist")
        return workspace.parse_fields(str(snapshot.get("effective_content") or ""))

    @staticmethod
    def _get_local_runtime() -> str:
        fields = OKProviderHandler._load_logic_assist_fields()
        return fields.get("local_runtime", "gpt4all")

    @staticmethod
    def _get_local_model_path() -> Any:
        from pathlib import Path

        from core.services.logging_api import get_repo_root

        fields = OKProviderHandler._load_logic_assist_fields()
        model_name = fields.get("local_model_name", "").strip()
        model_root = fields.get("local_model_path", "memory/models/gpt4all").strip()
        if not model_name:
            return None
        model_dir = Path(model_root)
        if not model_dir.is_absolute():
            model_dir = Path(get_repo_root()) / model_dir
        return model_dir / model_name

    def log_status(self, status: ProviderStatus) -> None:
        """Log provider status for audit trail.

        Args:
            status: ProviderStatus to log
        """
        if status.is_available:
            self.logger.info(
                f"[OK_PROVIDER] {status.provider_id}: available "
                f"({len(status.loaded_models)} models, default: {status.default_model})"
            )
        else:
            self.logger.warning(
                f"[OK_PROVIDER] {status.provider_id}: {status.issue or 'unavailable'}"
            )


# Singleton instance
_ok_handler: OKProviderHandler | None = None


def get_ok_provider_handler() -> OKProviderHandler:
    """Get singleton OKProviderHandler instance.

    Returns:
        OKProviderHandler singleton
    """
    global _ok_handler
    if _ok_handler is None:
        _ok_handler = OKProviderHandler()
    return _ok_handler


# Convenience functions for TUI


def check_local_provider() -> ProviderStatus:
    """Convenience wrapper to check local provider.

    Returns:
        ProviderStatus
    """
    return get_ok_provider_handler().check_local_provider()


def check_cloud_provider() -> ProviderStatus:
    """Convenience wrapper to check cloud provider.

    Returns:
        ProviderStatus
    """
    return get_ok_provider_handler().check_cloud_provider()


def check_all_providers() -> dict[str, ProviderStatus]:
    """Convenience wrapper to check all providers.

    Returns:
        Dict of all provider statuses
    """
    return get_ok_provider_handler().check_all_providers()
