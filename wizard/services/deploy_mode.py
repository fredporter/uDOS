from __future__ import annotations

import os


LOCAL = "local"
MANAGED = "managed"


def get_deploy_mode() -> str:
    raw = (os.environ.get("UDOS_DEPLOY_MODE") or LOCAL).strip().lower()
    if raw == MANAGED:
        return MANAGED
    return LOCAL


def is_managed_mode() -> bool:
    return get_deploy_mode() == MANAGED


def require_managed_env(var_name: str) -> str:
    value = (os.environ.get(var_name) or "").strip()
    if value:
        return value
    raise RuntimeError(f"Missing required managed environment variable: {var_name}")
