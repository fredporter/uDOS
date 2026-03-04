"""Wizard Setup Manager
====================

Provides setup status, required variables, and path validation for Wizard.
"""

from __future__ import annotations

import os
from typing import Any

from core.locations import LocationService
from core.services.integration_registry import get_wizard_required_variables
from core.services.unified_config_loader import get_config
from wizard.services.path_utils import get_memory_dir, get_repo_root
from wizard.services.setup_profiles import load_install_profile, load_user_profile
from wizard.services.setup_state import setup_state
from wizard.services.wizard_config import load_wizard_config_data


def validate_database_paths() -> dict[str, Any]:
    memory_root = get_memory_dir()
    paths = {
        "memory_root": memory_root,
        "logs": memory_root / "logs",
        "wizard_data": memory_root / "wizard",
    }
    results = {}
    for name, path in paths.items():
        path.mkdir(parents=True, exist_ok=True)
        results[name] = {
            "path": str(path),
            "exists": path.exists(),
            "writable": path.is_dir() and os.access(path, os.W_OK),
        }
    return results


def get_required_variables() -> dict[str, dict[str, Any]]:
    config = _load_wizard_config()
    variables = get_wizard_required_variables()
    for key, data in variables.items():
        env_var = data.get("env_var")
        data["status"] = "configured" if env_var and get_config(env_var) else "optional"
    return variables


def _is_ghost_mode(username: str | None, role: str | None) -> bool:
    username_norm = (username or "").strip().lower()
    role_norm = (role or "").strip().lower()
    return username_norm == "ghost" or role_norm == "ghost"


def get_full_config_status() -> dict[str, Any]:
    config = _load_wizard_config()
    user_result = load_user_profile()
    install_result = load_install_profile()
    ghost_mode = _is_ghost_mode(
        (user_result.data or {}).get("username"), (user_result.data or {}).get("role")
    )
    return {
        "server": {
            "host": config.get("host", "0.0.0.0"),
            "port": config.get("port", 8765),
            "debug": config.get("debug", False),
        },
        "services": {
            "github": {
                "configured": bool(get_config("GITHUB_TOKEN")),
                "status": "ready" if get_config("GITHUB_TOKEN") else "not-configured",
            },
            "ai": {
                "configured": bool(get_config("MISTRAL_API_KEY")),
                "status": "ready"
                if get_config("MISTRAL_API_KEY")
                else "not-configured",
            },
        },
        "databases": validate_database_paths(),
        "setup": {**setup_state.get_status(), "ghost_mode": ghost_mode},
        "profiles": {
            "user": user_result.data,
            "install": install_result.data,
            "ghost_mode": ghost_mode,
        },
        "features": {
            "logic_assist_enabled": config.get("logic_assist_enabled", False),
            "github_push_enabled": config.get("github_push_enabled", False),
            "web_proxy_enabled": config.get("web_proxy_enabled", False),
        },
        "logging": {"directory": str(get_memory_dir() / "logs")},
    }


def get_paths() -> dict[str, Any]:
    root = get_repo_root()
    return {
        "root": str(root),
        "installation": {
            "core": str(root / "core"),
            "extensions": str(root / "extensions"),
            "wizard": str(root / "wizard"),
            "dev": str(root / "dev"),
        },
        "data": {
            "memory_root": str(root / "memory"),
            "logs": str(root / "memory" / "logs"),
            "wizard_data": str(root / "memory" / "wizard"),
        },
        "documentation": {
            "readme": str(root / "README.md"),
            "agents": str(root / "AGENTS.md"),
            "roadmap": str(root / "docs" / "roadmap.md"),
        },
    }


def _load_wizard_config() -> dict[str, Any]:
    defaults = {
        "logic_assist_enabled": False,
        "github_push_enabled": False,
        "web_proxy_enabled": False,
    }
    return load_wizard_config_data(defaults=defaults)


_location_service: LocationService | None = None


def _get_location_service() -> LocationService:
    global _location_service
    if _location_service is None:
        _location_service = LocationService()
    return _location_service


def search_locations(
    query: str, timezone_hint: str | None = None, limit: int = 10
) -> list[dict[str, Any]]:
    service = _get_location_service()
    query_norm = (query or "").strip().lower()
    matches = []
    for loc in service.get_all_locations():
        name = loc.get("name", "")
        if query_norm and query_norm not in name.lower():
            continue
        score = 0
        if query_norm and name.lower().startswith(query_norm):
            score += 2
        if (
            timezone_hint
            and str(loc.get("timezone", "")).lower() == timezone_hint.lower()
        ):
            score += 1
        matches.append({
            "id": loc.get("id"),
            "name": name,
            "timezone": loc.get("timezone"),
            "region": loc.get("region"),
            "type": loc.get("type"),
            "layer": loc.get("layer"),
            "cell": loc.get("cell"),
            "score": score,
        })
    matches.sort(key=lambda m: (-m["score"], m["name"]))
    return matches[: max(1, limit)]


def get_default_location_for_timezone(
    timezone_hint: str | None,
) -> dict[str, Any] | None:
    if not timezone_hint:
        return None
    matches = search_locations("", timezone_hint=timezone_hint, limit=1)
    return matches[0] if matches else None
