"""OK mode configuration/status helpers for uCODE routes."""

from __future__ import annotations

from typing import Any

from core.services.json_utils import read_json_file, write_json_file
from core.services.logging_api import get_repo_root
from core.services.unified_config_loader import get_bool_config
from wizard.services.logic_assist_service import get_logic_assist_service

_OK_MODES_PATH_SEGMENTS = ("core", "config", "ok_modes.json")


def _ok_modes_path():
    return get_repo_root().joinpath(*_OK_MODES_PATH_SEGMENTS)


def load_ok_modes_config() -> dict[str, Any]:
    try:
        return read_json_file(_ok_modes_path(), default={"modes": {}})
    except Exception:
        return {"modes": {}}


def write_ok_modes_config(config: dict[str, Any]) -> None:
    write_json_file(_ok_modes_path(), config)


def is_dev_mode_active() -> bool:
    env_active = get_bool_config("UDOS_DEV_MODE", False)
    try:
        from wizard.services.dev_mode_service import get_dev_mode_service

        status = get_dev_mode_service().get_status()
        return bool(status.get("active")) or env_active
    except Exception:
        return env_active


def get_ok_default_models() -> dict[str, str]:
    config = load_ok_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    default_models = mode.get("default_models") or {}
    core_model = default_models.get("core") or "mistral-small-latest"
    dev_model = (
        default_models.get("dev") or default_models.get("core") or "devstral-small-2"
    )
    return {"core": core_model, "dev": dev_model}


def get_ok_default_model(purpose: str = "general") -> str:
    models = get_ok_default_models()
    dev_active = is_dev_mode_active()
    if purpose == "coding" or dev_active:
        return models["dev"] if dev_active else models["core"]
    return models["core"]


def resolve_ok_model(requested_model: str | None, purpose: str = "general") -> str:
    model = (requested_model or "").strip()
    if model:
        return model
    return get_ok_default_model(purpose=purpose)


def ok_auto_fallback_enabled() -> bool:
    config = load_ok_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    return bool(mode.get("auto_fallback", True))


def get_ok_context_window() -> int:
    try:
        from wizard.services.vibe_service import DevModeToolConfig

        return DevModeToolConfig().context_window
    except Exception:
        return 8192


def get_ok_local_status() -> dict[str, Any]:
    """Return local status from the v1.5 logic-assist runtime."""
    full_status = get_logic_assist_service().get_status()
    status = full_status["local"]
    context = full_status.get("context") or {}
    conversations = full_status.get("conversations") or {}
    cache = full_status.get("cache") or {}
    model = status.get("model") or get_ok_default_model()
    raw_issue = (status.get("issue") or "").strip().lower()

    issue: str | None = None
    if not status.get("ready"):
        if "model missing" in raw_issue:
            issue = "missing model"
        elif raw_issue:
            issue = "local runtime down"

    return {
        "ready": bool(status.get("ready")),
        "issue": issue,
        "model": model,
        "runtime": status.get("runtime", "gpt4all"),
        "model_path": status.get("model_path"),
        "detail": None,
        "context_hash": context.get("hash"),
        "context_files": context.get("count", 0),
        "conversation_store": conversations.get("stored", 0),
        "cache_entries": cache.get("entries", 0),
        "models": [model] if model else [],
    }


def get_ok_cloud_status() -> dict[str, Any]:
    try:
        from wizard.services.cloud_provider_executor import get_cloud_availability

        return get_cloud_availability()
    except Exception as exc:
        return {"ready": False, "issue": str(exc)}
