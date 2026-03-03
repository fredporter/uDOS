"""
Helper utilities for DESTROY command handling.
"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List
from core.services.destructive_ops import (
    ensure_memory_layout,
    remove_path,
    resolve_vault_root as resolve_vault_root_shared,
)
from core.services.time_utils import utc_day_string, utc_filename_timestamp, utc_now_iso


def destroy_menu_options() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "title": "WIPE USER DATA",
            "short": "Wipe User Data (clear users, API keys)",
            "details": [
                "Clear all user profiles, roles, and API keys",
                "Resets .env identity + Wizard keystore",
                "Preserves memory/logs",
            ],
            "usage": "DESTROY 1",
            "cleanup": {
                "wipe_user": True,
                "compost": False,
                "reload_repair": False,
            },
            "plan": ["🗑️  Wipe user profiles and API keys"],
        },
        {
            "id": 2,
            "title": "ARCHIVE MEMORY (COMPOST)",
            "short": "Archive Memory (compost /memory)",
            "details": [
                "Archive /memory to .compost/<date>/trash/<timestamp>",
                "Preserves data history",
                "Frees up /memory space",
                "Keeps users intact",
            ],
            "usage": "DESTROY 2",
            "cleanup": {
                "wipe_user": False,
                "compost": True,
                "reload_repair": False,
            },
            "plan": ["🗑️  Archive /memory to compost"],
        },
        {
            "id": 3,
            "title": "WIPE + COMPOST + REBOOT",
            "short": "Wipe + Archive + Reload (complete cleanup)",
            "details": [
                "Both: wipe user data AND archive memory",
                "Hot reload + repair after cleanup",
                "Complete fresh start (keeps framework)",
            ],
            "usage": "DESTROY 3",
            "cleanup": {
                "wipe_user": True,
                "compost": True,
                "reload_repair": True,
            },
            "plan": [
                "🗑️  Wipe user profiles and API keys",
                "🗑️  Archive /memory to compost",
                "🔧 Hot reload and run repair",
            ],
        },
        {
            "id": 4,
            "title": "NUCLEAR RESET (FACTORY RESET)",
            "short": "Nuclear Reset (factory defaults - DANGER!)",
            "details": [
                "⚠️  DANGER: Everything wiped to factory defaults",
                "Deletes: users, memory, config, logs, API keys",
                "Requires additional confirmation",
                "Admin only - cannot be undone easily",
            ],
            "usage": "DESTROY 4",
            "action": "nuclear",
        },
        {
            "id": 0,
            "title": "HELP",
            "short": "Help",
            "details": ["Show detailed command reference"],
            "usage": "DESTROY 0",
            "action": "help",
        },
    ]


def format_destroy_options(options: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for option in options:
        lines.append(f"  {option['id']}. {option['title']}")
        for detail in option.get("details", []):
            lines.append(f"    • {detail}")
        if option.get("usage"):
            lines.append(f"    Usage: {option['usage']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def build_nuclear_confirmation_text() -> str:
    return """
╔════════════════════════════════════════╗
║    ⚠️  NUCLEAR RESET CONFIRMATION ⚠️     ║
╚════════════════════════════════════════╝

This will DESTROY:
  • All user profiles and permissions
  • All configuration files
  • All memory/logs
  • All API keys and credentials
  • System will RESET to factory defaults

This is IRREVERSIBLE (though .compost/ is preserved).

Only admin users can perform this action.

Current status:
  Users: Multiple
  Memory: Populated
  Config: Custom
""".strip()


def build_destroy_help_text(formatted_options: str) -> str:
    return f"""
╔════════════════════════════════════════╗
║       DESTROY COMMAND HELP             ║
╚════════════════════════════════════════╝

DESTROY is the system cleanup and reset command. It safely removes
runtime state, archives mutable data, and optionally reinitializes the system.

v1.5 open-box rule:
  • Markdown/data libraries are split from runtime code
  • uDOS can be reinstalled while user data persists
  • DESTROY/RESTORE exists to make that separation operational

SYNTAX:
  DESTROY              Show menu with numbered options
  DESTROY [0-4]       Execute numeric option
  DESTROY --help      Show this help

NUMERIC OPTIONS:

{formatted_options}

LEGACY FLAG SUPPORT (still works):
  --wipe-user       Clear user profiles and API keys
  --compost         Archive /memory to .compost/<date>/trash/
  --reload-repair   Hot reload + repair after cleanup
  --reset-all       NUCLEAR: Complete factory reset
  --scrub-memory    Permanently delete /memory (no archive)
  --scrub-vault     Permanently delete VAULT_ROOT (no archive)
  --confirm         Skip confirmations (required for --reset-all)

LEGACY EXAMPLES:
  DESTROY --wipe-user
  DESTROY --compost
  DESTROY --wipe-user --compost
  DESTROY --wipe-user --compost --reload-repair
  DESTROY --reset-all --confirm
  DESTROY --scrub-memory --confirm
  DESTROY --scrub-vault --confirm

SAFETY:
  • Requires admin or destroy permission
  • Most ops ask for confirmation before proceeding
  • Nuclear reset (option 4) requires explicit user action
  • All actions logged to audit trail
  • Archived data preserved in .compost/<date>/trash/

RECOVERY:
  • If you compost, see .compost/<date>/trash/ for your data
  • BACKUP/RESTORE and UNDO work with the same open-box data split
  • Users can be recreated: USER create [name] [role]
  • Config can be restored from git or .compost
  • Use STORY tui-setup to reconfigure

NEXT STEPS AFTER CLEANUP:
  1. DESTROY 1          # Wipe user data
  2. DESTROY 3          # Complete cleanup
  3. STORY tui-setup    # Run setup story
  4. SETUP              # View your profile
  5. WIZARD start       # Start Wizard Server
""".strip()


def resolve_vault_root(repo_root: Path) -> Path:
    return resolve_vault_root_shared(repo_root)


def reset_local_env(repo_root: Path) -> List[str]:
    from core.services.config_sync_service import ConfigSyncManager

    results = []
    env_mgr = ConfigSyncManager()
    env_dict = env_mgr.load_env_dict()
    os_type = env_dict.get("OS_TYPE", "mac")
    udos_root = env_dict.get("UDOS_ROOT", str(repo_root))
    vault_root = env_dict.get("VAULT_ROOT")

    updates = {
        "USER_NAME": "Ghost",
        "USER_DOB": "1980-01-01",
        "USER_ROLE": "ghost",
        "USER_PASSWORD": "",
        "UDOS_LOCATION": "",
        "UDOS_TIMEZONE": "",
        "OS_TYPE": os_type,
        "UDOS_ROOT": udos_root,
        "WIZARD_ADMIN_TOKEN": None,
        "WIZARD_KEY": str(uuid.uuid4()),
        "UDOS_INSTALLATION_ID": None,
        "UDOS_VIEWPORT_COLS": None,
        "UDOS_VIEWPORT_ROWS": None,
        "UDOS_VIEWPORT_SOURCE": None,
        "UDOS_VIEWPORT_UPDATED_AT": None,
        "UDOS_MASTER_USER": None,
        "UDOS_INSTALL_PATH": None,
        "UDOS_USERNAME": None,
        "USER_ID": None,
        "USER_TIME": None,
        "USER_LOCATION": None,
        "USER_TIMEZONE": None,
        "VAULT_MD_ROOT": None,
    }
    if vault_root:
        updates["VAULT_ROOT"] = vault_root

    ok, msg = env_mgr.update_env_vars(updates)
    if ok:
        results.append("✓ Reset .env identity + tokens")
    else:
        results.append(f"⚠️  Failed to reset .env: {msg}")

    token_paths = [
        repo_root / "memory" / "private" / "wizard_admin_token.txt",
        repo_root / "memory" / "bank" / "private" / "wizard_admin_token.txt",
    ]
    removed = 0
    for path in token_paths:
        try:
            if remove_path(path):
                removed += 1
        except Exception:
            pass
    results.append(f"✓ Removed {removed} wizard admin token files")

    local_paths = [
        repo_root / "memory" / "user" / "profile.json",
        repo_root / "memory" / "config" / "udos.md",
    ]
    removed_local = 0
    for path in local_paths:
        try:
            if remove_path(path):
                removed_local += 1
        except Exception:
            pass
    results.append(f"✓ Removed {removed_local} local profile files")
    return results


def reset_wizard_keystore(repo_root: Path) -> List[str]:
    results = []
    tomb_path = repo_root / "wizard" / "secrets.tomb"
    if not tomb_path.exists():
        results.append("✓ Wizard keystore already reset (no secrets.tomb)")
        return results

    archive_root = repo_root / ".compost" / "wizard-reset"
    archive_root.mkdir(exist_ok=True)
    timestamp = utc_filename_timestamp()
    backup_path = archive_root / f"secrets.tomb.backup.{timestamp}"
    try:
        shutil.move(str(tomb_path), str(backup_path))
        results.append(f"✓ Archived secrets.tomb to {backup_path}")
    except Exception as exc:
        results.append(f"⚠️  Failed to archive secrets.tomb: {exc}")
    return results


def archive_memory_to_compost(
    repo_root: Path,
    user_name: str,
    action: str,
    reason: str,
    metadata_filename: str,
) -> tuple[List[str], str]:
    lines: List[str] = []
    memory_path = repo_root / "memory"
    if not memory_path.exists():
        return lines, ""

    archive_root = repo_root / ".compost"
    archive_root.mkdir(exist_ok=True)
    date_folder = utc_day_string()
    timestamp = utc_filename_timestamp()
    compost_dir = archive_root / date_folder / "trash" / timestamp
    compost_dir.mkdir(parents=True, exist_ok=True)

    metadata_file = compost_dir / metadata_filename
    metadata = {
        "archived_at": utc_now_iso(),
        "archived_by": user_name,
        "action": action,
        "reason": reason,
    }
    try:
        metadata_file.write_text(json.dumps(metadata, indent=2))
    except Exception:
        pass

    shutil.move(str(memory_path), str(compost_dir / "memory"))
    ensure_memory_layout(memory_path)

    lines.append(f"✓ Archived to .compost/{date_folder}/trash/{timestamp}")
    lines.append("✓ Recreated empty memory directories")
    return lines, timestamp
