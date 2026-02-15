"""
Wizard Setup Manager
====================

Provides setup status, required variables, and path validation for Wizard.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from wizard.services.path_utils import get_repo_root, get_memory_dir
from core.locations import LocationService
from wizard.services.setup_state import setup_state
from wizard.services.setup_profiles import load_user_profile, load_install_profile
from core.services.integration_registry import get_wizard_required_variables


def validate_database_paths() -> Dict[str, Any]:
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


def get_required_variables() -> Dict[str, Dict[str, Any]]:
    config = _load_wizard_config()
    variables = get_wizard_required_variables()
    for key, data in variables.items():
        env_var = data.get("env_var")
        data["status"] = "configured" if env_var and os.getenv(env_var) else "optional"
    return variables


def _is_ghost_mode(username: Optional[str], role: Optional[str]) -> bool:
    username_norm = (username or "").strip().lower()
    role_norm = (role or "").strip().lower()
    return username_norm == "ghost" or role_norm == "ghost"


def get_full_config_status() -> Dict[str, Any]:
    config = _load_wizard_config()
    user_result = load_user_profile()
    install_result = load_install_profile()
    ghost_mode = _is_ghost_mode(
        (user_result.data or {}).get("username"),
        (user_result.data or {}).get("role"),
    )
    return {
        "server": {
            "host": config.get("host", "0.0.0.0"),
            "port": config.get("port", 8765),
            "debug": config.get("debug", False),
        },
        "services": {
            "github": {
                "configured": bool(os.getenv("GITHUB_TOKEN")),
                "status": "ready" if os.getenv("GITHUB_TOKEN") else "not-configured",
            },
            "ai": {
                "configured": bool(os.getenv("MISTRAL_API_KEY")),
                "status": "ready" if os.getenv("MISTRAL_API_KEY") else "not-configured",
            },
        },
        "databases": validate_database_paths(),
        "setup": {
            **setup_state.get_status(),
            "ghost_mode": ghost_mode,
        },
        "profiles": {
            "user": user_result.data,
            "install": install_result.data,
            "ghost_mode": ghost_mode,
        },
        "features": {
            "ok_gateway_enabled": config.get("ok_gateway_enabled", False),
            "github_push_enabled": config.get("github_push_enabled", False),
            "web_proxy_enabled": config.get("web_proxy_enabled", False),
        },
        "logging": {
            "directory": str(get_memory_dir() / "logs"),
        },
    }


def get_paths() -> Dict[str, Any]:
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


def _load_wizard_config() -> Dict[str, Any]:
    config_path = get_repo_root() / "wizard" / "config" / "wizard.json"
    defaults = {
        "ok_gateway_enabled": False,
        "github_push_enabled": False,
        "web_proxy_enabled": False,
    }
    if not config_path.exists():
        return defaults.copy()
    try:
        parsed = json.loads(config_path.read_text())
        if not isinstance(parsed, dict):
            return defaults.copy()
        return {**defaults, **parsed}
    except Exception:
        return defaults.copy()


_location_service: LocationService | None = None


def _get_location_service() -> LocationService:
    global _location_service
    if _location_service is None:
        _location_service = LocationService()
    return _location_service


def search_locations(query: str, timezone_hint: str | None = None, limit: int = 10) -> List[Dict[str, Any]]:
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
        if timezone_hint and str(loc.get("timezone", "")).lower() == timezone_hint.lower():
            score += 1
        matches.append(
            {
                "id": loc.get("id"),
                "name": name,
                "timezone": loc.get("timezone"),
                "region": loc.get("region"),
                "type": loc.get("type"),
                "layer": loc.get("layer"),
                "cell": loc.get("cell"),
                "score": score,
            }
        )
    matches.sort(key=lambda m: (-m["score"], m["name"]))
    return matches[: max(1, limit)]


def get_default_location_for_timezone(timezone_hint: str | None) -> Optional[Dict[str, Any]]:
    if not timezone_hint:
        return None
    matches = search_locations("", timezone_hint=timezone_hint, limit=1)
    return matches[0] if matches else None
