"""Utility helpers for setup route handlers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from fastapi import HTTPException, Request

from core.locations import LocationService
from wizard.services.path_utils import get_repo_root


def get_system_timezone_info() -> Dict[str, str]:
    now = datetime.now().astimezone()
    tzinfo = now.tzinfo or timezone.utc
    tz_name = getattr(tzinfo, "key", None) or tzinfo.tzname(now) or "UTC"
    return {
        "timezone": tz_name,
        "local_time": now.strftime("%Y-%m-%d %H:%M"),
    }


def collect_timezone_options() -> List[Dict[str, Any]]:
    service = LocationService()
    mapping: Dict[str, Dict[str, Any]] = {}
    for loc in service.get_all_locations():
        tz = str(loc.get("timezone") or "").strip()
        if not tz:
            continue
        label = f"{loc.get('name')} ({loc.get('region', 'global')})"
        candidate = {
            "timezone": tz,
            "label": label,
            "location_id": loc.get("id"),
            "location_name": loc.get("name"),
        }
        existing = mapping.get(tz)
        if not existing or loc.get("type") == "major-city":
            mapping[tz] = candidate
    return sorted(mapping.values(), key=lambda item: item["label"])


def apply_setup_defaults(
    story_state: Dict[str, Any],
    overrides: Dict[str, Any],
    highlight_fields: Optional[Sequence[str]] = None,
) -> None:
    highlight = set(highlight_fields or [])
    answers = story_state.get("answers") or {}
    for section in story_state.get("sections", []):
        for question in section.get("questions", []):
            if not question:
                continue
            name = question.get("name")
            if not name:
                continue
            if name in overrides and overrides[name] is not None:
                value = overrides[name]
                answers[name] = value
                question["value"] = value
                if question.get("meta") is None:
                    question["meta"] = {}
                meta = question["meta"]
                meta["default_value"] = value
                meta["previous_value"] = value
                if name in highlight:
                    meta["show_previous_overlay"] = True
                if name == "user_timezone":
                    meta["options_endpoint"] = "/api/setup/data/timezones"
            elif name in overrides and overrides[name] is None:
                answers.pop(name, None)
    story_state["answers"] = answers


def apply_capabilities_to_wizard_config(capabilities: Dict[str, bool]) -> None:
    if not capabilities:
        return
    config_path = get_repo_root() / "wizard" / "config" / "wizard.json"
    if not config_path.exists():
        return
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        return
    mapping = {
        "web_proxy": "web_proxy_enabled",
        "ok_gateway": "ok_gateway_enabled",
        "github_push": "github_push_enabled",
        "icloud": "icloud_enabled",
        "plugin_repo": "plugin_repo_enabled",
        "plugin_auto_update": "plugin_auto_update",
    }
    updated = False
    for cap_key, config_key in mapping.items():
        if cap_key in capabilities:
            config[config_key] = bool(capabilities[cap_key])
            updated = True
    if updated:
        config_path.write_text(json.dumps(config, indent=2))


def validate_location_id(location_id: Optional[str]) -> None:
    if not location_id:
        raise HTTPException(status_code=400, detail="Location must be selected")
    service = LocationService()
    if not service.get_location(location_id):
        raise HTTPException(
            status_code=400,
            detail="Location must be a valid uDOS grid code from the core dataset",
        )


def resolve_location_name(location_id: str) -> str:
    service = LocationService()
    loc = service.get_location(location_id)
    return loc.get("name") if loc else location_id


def is_ghost_mode(username: Optional[str], role: Optional[str]) -> bool:
    username_norm = (username or "").strip().lower()
    role_norm = (role or "").strip().lower()
    return username_norm == "ghost" or role_norm == "ghost"


def is_local_request(request: Request) -> bool:
    client_host = request.client.host if request.client else ""
    return client_host in {"127.0.0.1", "::1", "localhost"}


def load_env_identity(logger=None) -> Dict[str, str]:
    try:
        env_path = get_repo_root() / ".env"
        if not env_path.exists():
            return {}

        env_vars: Dict[str, str] = {}
        with open(env_path, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')

        identity = {}
        if env_vars.get("USER_NAME"):
            identity["user_username"] = env_vars["USER_NAME"]
        if env_vars.get("USER_DOB"):
            identity["user_dob"] = env_vars["USER_DOB"]
        if env_vars.get("USER_ROLE"):
            identity["user_role"] = env_vars["USER_ROLE"]
        if env_vars.get("UDOS_TIMEZONE"):
            identity["user_timezone"] = env_vars["UDOS_TIMEZONE"]
        if env_vars.get("UDOS_LOCATION"):
            identity["user_location"] = env_vars["UDOS_LOCATION"]
        if env_vars.get("OS_TYPE"):
            identity["install_os_type"] = env_vars["OS_TYPE"]
        return identity
    except Exception as exc:
        if logger:
            logger.debug(f"Could not load identity from .env: {exc}")
        return {}
