"""uCLI/uCODE command contract helpers (v1.3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set


CONTRACT_PATH = Path(__file__).resolve().parent.parent.parent / "core" / "config" / "ucli_command_contract_v1_3_16.json"


_DEFAULT_COMMANDS = {
    "STATUS",
    "HELP",
    "MAP",
    "PANEL",
    "FIND",
    "TELL",
    "GOTO",
    "BAG",
    "GRAB",
    "SPAWN",
    "STORY",
    "RUN",
    "BINDER",
    "USER",
    "GAMEPLAY",
    "PLAY",
    "RULE",
    "UID",
    "DEV",
    "WIZARD",
    "CONFIG",
    "SAVE",
    "LOAD",
    "FILE",
    "NEW",
    "EDIT",
    "NPC",
    "TALK",
    "REPLY",
    "LOGS",
    "REPAIR",
    "REBOOT",
    "SONIC",
    "SETUP",
    "HEALTH",
    "VERIFY",
    "DRAW",
    "TAG",
}


_DEFAULT_DEPRECATED_ALIASES = {}


def _load_contract() -> Dict:
    if not CONTRACT_PATH.exists():
        return {}
    try:
        data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def load_ucode_allowlist_from_contract() -> Set[str]:
    contract = _load_contract()
    ucode = contract.get("ucode") if isinstance(contract.get("ucode"), dict) else {}
    commands = ucode.get("commands") if isinstance(ucode.get("commands"), list) else []
    command_set = {str(item).strip().upper() for item in commands if str(item).strip()}
    return command_set or set(_DEFAULT_COMMANDS)


def load_ucode_deprecated_aliases() -> Dict[str, str]:
    contract = _load_contract()
    ucode = contract.get("ucode") if isinstance(contract.get("ucode"), dict) else {}
    aliases = ucode.get("deprecated_aliases") if isinstance(ucode.get("deprecated_aliases"), dict) else {}
    parsed = {
        str(alias).strip().upper(): str(canonical).strip().upper()
        for alias, canonical in aliases.items()
        if str(alias).strip() and str(canonical).strip()
    }
    return parsed or dict(_DEFAULT_DEPRECATED_ALIASES)


def load_launcher_subcommands() -> List[str]:
    contract = _load_contract()
    launcher = contract.get("launcher") if isinstance(contract.get("launcher"), dict) else {}
    values = launcher.get("subcommands") if isinstance(launcher.get("subcommands"), list) else []
    parsed = [str(item).strip().lower() for item in values if str(item).strip()]
    return parsed or ["help", "tui", "wizard", "prompt", "cmd"]


def load_launcher_deprecated_aliases() -> Dict[str, str]:
    contract = _load_contract()
    launcher = contract.get("launcher") if isinstance(contract.get("launcher"), dict) else {}
    aliases = (
        launcher.get("deprecated_aliases")
        if isinstance(launcher.get("deprecated_aliases"), dict)
        else {}
    )
    parsed = {
        str(alias).strip().lower(): str(canonical).strip().lower()
        for alias, canonical in aliases.items()
        if str(alias).strip() and str(canonical).strip()
    }
    return parsed or {
        "core": "tui",
        "server": "wizard",
        "command": "cmd",
        "run": "cmd",
    }
