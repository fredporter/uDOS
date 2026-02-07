"""Centralized Ghost Mode guard for destructive commands."""

from typing import Dict, List, Optional

from core.services.user_service import is_ghost_mode


def _normalize(params: List[str]) -> List[str]:
    return [p.upper() for p in params or []]


def ghost_mode_block(command: str, params: Optional[List[str]] = None) -> Optional[Dict]:
    """Return a blocking response if Ghost Mode forbids the command."""
    if not is_ghost_mode():
        return None

    cmd = (command or "").upper()
    tokens = _normalize(params or [])

    # Allow non-destructive access paths
    if cmd == "RUN" and tokens[:1] == ["PARSE"]:
        return None
    if cmd == "BINDER":
        if not tokens or tokens[:1] in (["PICK"], ["CHAPTERS"]):
            return None
    if cmd == "SEED" and tokens[:1] in ([], ["STATUS"], ["HELP"]):
        return None
    if cmd == "PLUGIN" and tokens[:1] in ([], ["LIST"], ["HELP"], ["INFO"]):
        return None
    if cmd == "WIZARD" and tokens[:1] in ([], ["STATUS"], ["HELP"]):
        return None
    if cmd == "CONFIG":
        if not tokens or tokens[:1] in (["SHOW"], ["STATUS"], ["LIST"], ["VARS"], ["VARIABLES"]):
            return None
        if tokens[:1] == ["--HELP"] or tokens[:1] == ["HELP"]:
            return None
        # Allow CONFIG <key> (read-only get)
        if len(tokens) == 1 and not tokens[0].startswith("--") and tokens[0] not in {
            "EDIT",
            "SETUP",
        }:
            return None
    if cmd == "SETUP" and tokens[:1] in ([], ["--PROFILE"], ["--VIEW"], ["--SHOW"], ["--HELP"], ["HELP"]):
        return None
    if cmd == "PROVIDER" and tokens[:1] in ([], ["LIST"]):
        return None
    if cmd == "PROVIDER" and tokens[:1] == ["STATUS"] and len(tokens) >= 2:
        return None
    if cmd == "INTEGRATION" and tokens[:1] in ([], ["STATUS"], ["GITHUB"], ["MISTRAL"], ["OLLAMA"]):
        return None
    if cmd == "MIGRATE" and tokens[:1] in ([], ["CHECK"], ["STATUS"]):
        return None
    if cmd == "USER" and tokens[:1] in ([], ["LIST"], ["PERMS"], ["CURRENT"], ["HELP"], ["-H"], ["--HELP"], ["?"]):
        return None
    if cmd == "UID" and tokens[:1] in ([], ["DECODE"], ["--HELP"]):
        return None
    if cmd == "DATASET" and tokens[:1] in ([], ["LIST"], ["VALIDATE"], ["HELP"]):
        return None
    if cmd == "SONIC" and tokens[:1] in ([], ["STATUS"], ["HELP"], ["LIST"], ["SYNC"], ["PLUGIN"]):
        return None
    if cmd in {"HOTKEY", "HOTKEYS", "PATTERN"}:
        return None

    blocked_commands = {
        "REPAIR",
        "BACKUP",
        "RESTORE",
        "TIDY",
        "CLEAN",
        "COMPOST",
        "UNDO",
        "DESTROY",
        "RUN",
        "BINDER",
        "SEED",
        "PLUGIN",
        "WIZARD",
        "NEW",
        "EDIT",
        "SAVE",
        "LOAD",
    }

    dry_run_commands = {
        "REPAIR",
        "BACKUP",
        "RESTORE",
        "TIDY",
        "CLEAN",
        "COMPOST",
        "UNDO",
        "CONFIG",
        "PROVIDER",
        "INTEGRATION",
        "MIGRATE",
        "USER",
        "UID",
        "DATASET",
        "SONIC",
        "SONIC+",
        "HOTKEY",
        "HOTKEYS",
        "PATTERN",
    }

    if cmd in dry_run_commands:
        return {
            "status": "warning",
            "message": f"Ghost Mode is read-only ({cmd} dry-run)",
            "output": "Ghost Mode active: operation simulated only (no changes made). Run SETUP to exit Ghost Mode.",
            "dry_run": True,
        }

    if cmd in blocked_commands:
        return {
            "status": "warning",
            "message": f"Ghost Mode is read-only ({cmd} blocked)",
            "output": "Ghost Mode active: write-capable commands are disabled. Run SETUP to exit Ghost Mode.",
        }

    return None
