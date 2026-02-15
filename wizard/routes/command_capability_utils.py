"""Command capability checks for Wizard/uCLI route gating."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _wizard_root_from_here() -> Path:
    return Path(__file__).resolve().parent.parent


def _wizard_manifest_path(wizard_root: Optional[Path] = None) -> Path:
    root = wizard_root or _wizard_root_from_here()
    return root / "command_manifests" / "wizard_required_commands.json"


def load_wizard_required_commands(wizard_root: Optional[Path] = None) -> Dict[str, List[str]]:
    manifest_path = _wizard_manifest_path(wizard_root)
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    commands = payload.get("commands")
    if not isinstance(commands, dict):
        return {}

    out: Dict[str, List[str]] = {}
    for key, requirements in commands.items():
        if not isinstance(key, str):
            continue
        req_list = [item for item in (requirements or []) if isinstance(item, str) and item]
        out[key.upper()] = req_list
    return out


def detect_wizard_capabilities(wizard_root: Optional[Path] = None) -> Dict[str, bool]:
    root = wizard_root or _wizard_root_from_here()
    repo_root = root.parent
    dashboard_root = root / "dashboard"
    dev_root = repo_root / "dev"
    sonic_root = repo_root / "sonic"
    groovebox_root = repo_root / "groovebox"

    wizard_gui = dashboard_root.exists() and (
        (dashboard_root / "src").exists() or (dashboard_root / "dist").exists()
    )

    networking = hasattr(socket, "AF_INET") and hasattr(socket, "SOCK_STREAM")
    dev_mode_active = False
    try:
        from wizard.services.dev_mode_service import get_dev_mode_service

        dev_mode_active = bool(get_dev_mode_service().get_status().get("active"))
    except Exception:
        dev_mode_active = False

    return {
        "wizard_server": True,
        "wizard_gui": bool(wizard_gui),
        "networking": bool(networking),
        "module_dev": bool(dev_root.exists()),
        "module_sonic": bool(sonic_root.exists()),
        "module_groovebox": bool(groovebox_root.exists()),
        "dev_mode_active": bool(dev_mode_active),
    }


def check_command_capabilities(
    command: str,
    required_map: Dict[str, List[str]],
    capabilities: Dict[str, bool],
) -> Tuple[bool, Optional[str], List[str]]:
    cmd = (command or "").upper().strip()
    requirements = required_map.get(cmd, [])
    if not requirements:
        return True, None, []

    missing = [item for item in requirements if not capabilities.get(item, False)]
    if not missing:
        return True, None, requirements

    return (
        False,
        f"{cmd} unavailable: missing capabilities ({', '.join(missing)})",
        requirements,
    )
