"""Dev State Helper
================

Lightweight helper to reflect Wizard DEV mode state in local TUI.
Uses a short TTL cache to avoid spamming the Wizard API.
"""

from __future__ import annotations

import time

from core.services.stdlib_http import HTTPError, http_get
from core.services.unified_config_loader import get_config
from core.services.wizard_runtime_config import get_loopback_wizard_base_url

_CACHE_ACTIVE: bool | None = None
_CACHE_TS: float = 0.0
_CACHE_TTL = 2.0
def _loopback_wizard_base_url(raw_base_url: str) -> str:
    return get_loopback_wizard_base_url(raw_base_url)


def _env_dev_active() -> bool | None:
    raw = get_config("UDOS_DEV_MODE", "")
    if raw == "":
        return None
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def get_dev_active(force: bool = False, ttl: float = _CACHE_TTL) -> bool | None:
    global _CACHE_ACTIVE, _CACHE_TS
    now = time.time()
    if not force and _CACHE_ACTIVE is not None and (now - _CACHE_TS) < ttl:
        return _CACHE_ACTIVE

    base_url = _loopback_wizard_base_url(
        get_config("WIZARD_BASE_URL", "")
    )
    admin_token = get_config("WIZARD_ADMIN_TOKEN", "")
    if not admin_token:
        active = _env_dev_active()
        _CACHE_ACTIVE = active
        _CACHE_TS = now
        return active

    try:
        resp = http_get(
            f"{base_url}/api/dev/status",
            headers={"X-Admin-Token": admin_token},
            timeout=1,
        )
        if resp.get("status_code") == 200:
            data = resp.get("json") or {}
            active = bool(data.get("active"))
            import os

            os.environ["UDOS_DEV_MODE"] = "1" if active else "0"
        else:
            active = _env_dev_active()
    except HTTPError:
        active = _env_dev_active()

    _CACHE_ACTIVE = active
    _CACHE_TS = now
    return active


def get_dev_state_label() -> str:
    active = get_dev_active()
    return "ON" if active else "OFF"
