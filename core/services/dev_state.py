"""
Dev State Helper
================

Lightweight helper to reflect Wizard DEV mode state in local TUI.
Uses a short TTL cache to avoid spamming the Wizard API.
"""

from __future__ import annotations

import os
import time
from typing import Optional

_CACHE_ACTIVE: Optional[bool] = None
_CACHE_TS: float = 0.0
_CACHE_TTL = 2.0


def _env_dev_active() -> Optional[bool]:
    raw = os.getenv("UDOS_DEV_MODE")
    if raw is None:
        return None
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def get_dev_active(force: bool = False, ttl: float = _CACHE_TTL) -> Optional[bool]:
    global _CACHE_ACTIVE, _CACHE_TS
    now = time.time()
    if not force and _CACHE_ACTIVE is not None and (now - _CACHE_TS) < ttl:
        return _CACHE_ACTIVE

    base_url = os.getenv("WIZARD_BASE_URL", "http://localhost:8765").rstrip("/")
    admin_token = os.getenv("WIZARD_ADMIN_TOKEN")
    if not admin_token:
        active = _env_dev_active()
        _CACHE_ACTIVE = active
        _CACHE_TS = now
        return active

    try:
        import requests  # type: ignore

        resp = requests.get(
            f"{base_url}/api/dev/status",
            headers={"X-Admin-Token": admin_token},
            timeout=0.5,
        )
        if resp.ok:
            data = resp.json()
            active = bool(data.get("active"))
            os.environ["UDOS_DEV_MODE"] = "1" if active else "0"
        else:
            active = _env_dev_active()
    except Exception:
        active = _env_dev_active()

    _CACHE_ACTIVE = active
    _CACHE_TS = now
    return active


def get_dev_state_label() -> str:
    active = get_dev_active()
    return "ON" if active else "OFF"
