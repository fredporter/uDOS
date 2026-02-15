"""OK mode configuration/status helpers for uCODE routes."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def load_ai_modes_config() -> Dict[str, Any]:
    try:
        from core.services.logging_api import get_repo_root

        path = get_repo_root() / "core" / "config" / "ok_modes.json"
        if not path.exists():
            return {"modes": {}}
        return json.loads(path.read_text())
    except Exception:
        return {"modes": {}}


def write_ok_modes_config(config: Dict[str, Any]) -> None:
    from core.services.logging_api import get_repo_root

    path = get_repo_root() / "core" / "config" / "ok_modes.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, indent=2))


def is_dev_mode_active() -> bool:
    env_active = os.getenv("UDOS_DEV_MODE") in ("1", "true", "yes")
    try:
        from wizard.services.dev_mode_service import get_dev_mode_service

        status = get_dev_mode_service().get_status()
        return bool(status.get("active")) or env_active
    except Exception:
        return env_active


def get_ok_default_models() -> Dict[str, str]:
    config = load_ai_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    default_models = mode.get("default_models") or {}
    core_model = default_models.get("core") or "mistral-small-latest"
    dev_model = default_models.get("dev") or default_models.get("core") or "devstral-small-2"
    return {"core": core_model, "dev": dev_model}


def get_ok_default_model(purpose: str = "general") -> str:
    models = get_ok_default_models()
    dev_active = is_dev_mode_active()
    if purpose == "coding" or dev_active:
        return models["dev"] if dev_active else models["core"]
    return models["core"]


def resolve_ok_model(requested_model: Optional[str], purpose: str = "general") -> str:
    model = (requested_model or "").strip()
    if model:
        return model
    return get_ok_default_model(purpose=purpose)


def ok_auto_fallback_enabled() -> bool:
    config = load_ai_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    return bool(mode.get("auto_fallback", True))


def get_ok_context_window() -> int:
    try:
        from wizard.services.vibe_service import VibeConfig

        return VibeConfig().context_window
    except Exception:
        return 8192


def fetch_ollama_models(endpoint: str) -> Dict[str, Any]:
    url = endpoint.rstrip("/") + "/api/tags"
    try:
        import requests

        resp = requests.get(url, timeout=2)
        if resp.status_code != 200:
            return {"reachable": False, "error": f"HTTP {resp.status_code}"}
        payload = resp.json()
        models = [m.get("name") for m in payload.get("models", []) if m.get("name")]
        return {"reachable": True, "models": models}
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}


def get_ok_local_status() -> Dict[str, Any]:
    config = load_ai_modes_config()
    mode = (config.get("modes") or {}).get("ofvibe", {})
    endpoint = mode.get("ollama_endpoint", "http://127.0.0.1:11434")
    model = get_ok_default_model()
    tags = fetch_ollama_models(endpoint)
    if not tags.get("reachable"):
        return {
            "ready": False,
            "issue": "ollama down",
            "model": model,
            "ollama_endpoint": endpoint,
            "detail": tags.get("error"),
            "models": [],
        }
    models = tags.get("models") or []
    if model and model not in models:
        return {
            "ready": False,
            "issue": "missing model",
            "model": model,
            "ollama_endpoint": endpoint,
            "detail": None,
            "models": models,
        }
    return {
        "ready": True,
        "issue": None,
        "model": model,
        "ollama_endpoint": endpoint,
        "detail": None,
        "models": models,
    }


def get_ok_cloud_status() -> Dict[str, Any]:
    try:
        from wizard.services.mistral_api import MistralAPI

        client = MistralAPI()
        if client.available():
            return {"ready": True, "issue": None}
        return {"ready": False, "issue": "mistral api key missing"}
    except Exception as exc:
        return {"ready": False, "issue": str(exc)}
