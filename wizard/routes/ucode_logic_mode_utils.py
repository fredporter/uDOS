"""Logic-assist configuration/status helpers for uCODE routes."""

from __future__ import annotations

from typing import Any

from core.services.unified_config_loader import get_bool_config
from wizard.services.logic_assist_profile import (
    load_logic_assist_profile,
    write_logic_assist_field,
)


def load_logic_modes_config() -> dict[str, Any]:
    profile = load_logic_assist_profile()
    return {
        "modes": {
            "logic_assist": {
                "default_models": {
                    "core": profile.local_model_name,
                    "dev": profile.local_model_name,
                },
                "auto_fallback": profile.network_enabled,
            }
        }
    }


def write_logic_modes_config(config: dict[str, Any]) -> None:
    mode = (config.get("modes") or {}).get("logic_assist", {})
    if "auto_fallback" in mode:
        write_logic_assist_field(
            "network_enabled", "true" if mode.get("auto_fallback") else "false"
        )


def is_dev_mode_active() -> bool:
    env_active = get_bool_config("UDOS_DEV_MODE", False)
    try:
        from wizard.services.dev_mode_service import get_dev_mode_service

        status = get_dev_mode_service().get_status()
        return bool(status.get("active")) or env_active
    except Exception:
        return env_active


def get_logic_default_models() -> dict[str, str]:
    profile = load_logic_assist_profile()
    return {
        "core": profile.local_model_name,
        "dev": profile.local_model_name,
    }


def get_logic_default_model(purpose: str = "general") -> str:
    models = get_logic_default_models()
    dev_active = is_dev_mode_active()
    if purpose == "coding" or dev_active:
        return models["dev"]
    return models["core"]


def resolve_logic_model(requested_model: str | None, purpose: str = "general") -> str:
    model = (requested_model or "").strip()
    if model:
        return model
    return get_logic_default_model(purpose=purpose)


def logic_auto_fallback_enabled() -> bool:
    profile = load_logic_assist_profile()
    return profile.network_enabled and profile.auto_defer_when_exceeded


def get_logic_context_window() -> int:
    profile = load_logic_assist_profile()
    return profile.local_context_window


def get_logic_local_status() -> dict[str, Any]:
    from wizard.services.logic_assist_service import get_logic_assist_service

    status = get_logic_assist_service().get_status()["local"]
    return {
        "ready": bool(status.get("ready")),
        "issue": status.get("issue"),
        "model": status.get("model"),
        "model_path": status.get("model_path"),
        "runtime": status.get("runtime", "gpt4all"),
        "detail": None,
    }


def get_logic_network_status() -> dict[str, Any]:
    from wizard.services.logic_assist_service import get_logic_assist_service

    status = get_logic_assist_service().get_status()["network"]
    return {
        "ready": bool(status.get("ready")),
        "issue": status.get("issue"),
        "available_providers": status.get("available_providers", []),
        "primary": status.get("primary"),
        "budget": status.get("budget", {}),
    }


def write_logic_default_model(profile: str, model: str) -> dict[str, Any]:
    field_name = "local_model_name"
    snapshot = write_logic_assist_field(field_name, model)
    return {
        "profile": profile,
        "model": model,
        "effective_path": snapshot.get("effective_path"),
    }
