"""
Hotkey map helpers
==================

Shared helper for documenting and recording the key bindings used by the TUI
command prompt (Tab, F1-F8, arrow history, etc.). Allows automation scripts to
compare the current bindings via JSON payloads/snapshots.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.health_training import read_last_todo_reminder


def get_hotkey_map() -> List[Dict[str, str]]:
    """Return the canonical key map shared between UI and automation."""
    return [
        {"key": "Tab", "action": "Command Selector", "notes": "Opens the TAB menu even in fallback mode."},
        {"key": "F1", "action": "Status / Help banner", "notes": "Displays Self-Healer + Hot Reload stats."},
        {"key": "F2", "action": "Logs / Diagnostics", "notes": "Shows logs and diagnostics summary."},
        {"key": "F3", "action": "REPAIR shortcut", "notes": "Triggers SelfHealer checks via CLI."},
        {"key": "F4", "action": "RESTART / HOT RELOAD", "notes": "Reloads handlers and restarts watchers."},
        {"key": "F5", "action": "Extension palette", "notes": "Opens the plugin menu (LibraryManager metadata)."},
        {"key": "F6", "action": "Script / DRAW PAT", "notes": "Runs DRAW PAT/system script banners for automation."},
        {"key": "F7", "action": "Sonic Device DB", "notes": "Shows Sonic USB/media capabilities from the device DB."},
        {"key": "F8", "action": "Hotkey Center", "notes": "Reloads this key map (including automation hints)."},
        {"key": "↑ / ↓", "action": "Command history", "notes": "Shared with SmartPrompt history/predictor."},
        {"key": "Enter", "action": "Confirm input", "notes": "Approves Date/Time/Timezone with overrides."},
    ]


def _get_repo_root_from(memory_root: Path) -> Path:
    """Return the repository root path assuming `/memory` sits directly under repo root."""
    return memory_root.parent


def _build_status_payload(memory_root: Path) -> Dict[str, Any]:
    """Return the status payload describing the plugin/Sonic story + register paths."""
    repo_root = _get_repo_root_from(memory_root)
    doc_path = repo_root / "core" / "docs" / "WIZARD-SONIC-PLUGIN-ECOSYSTEM.md"
    status = {
        "hotkey_register": str(memory_root / "logs" / "hotkey-center.json"),
        "doc_path": str(doc_path),
        "doc_last_modified": None,
        "deliverables": [
            "Wizard config page now routes `.venv → secrets → installers → hotkeys` and shares manifest validation with CLI installs.",
            "CLI `PLUGIN install` and `/api/library/.../install` log every manifest/health event to `memory/logs/health-training.log`.",
            "Sonic Screwdriver USB builder scripts, device DB sync, media logs, and Windows launch parameters are captured in `core/docs/WIZARD-SONIC-PLUGIN-ECOSYSTEM.md`.",
        ],
        "todo_reminder": read_last_todo_reminder(),
    }
    if doc_path.exists():
        status["doc_last_modified"] = datetime.fromtimestamp(doc_path.stat().st_mtime).isoformat()
    return status


def get_hotkey_payload(memory_root: Path) -> Dict[str, Any]:
    """Return the payload that automation scripts consume."""
    logs_dir = memory_root / "logs"
    snapshot_path = logs_dir / "hotkey-center.png"
    return {
        "key_map": get_hotkey_map(),
        "snapshot": str(snapshot_path),
        "last_updated": datetime.utcnow().isoformat(),
        "status": _build_status_payload(memory_root),
    }


def write_hotkey_payload(memory_root: Path) -> Dict[str, Any]:
    """Persist the hotkey payload to `memory/logs/hotkey-center.json` and return it."""
    payload = get_hotkey_payload(memory_root)
    logs_dir = memory_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    json_path = logs_dir / "hotkey-center.json"
    json_path.write_text(json.dumps(payload, indent=2))
    return payload


def read_hotkey_payload(memory_root: Path) -> Optional[Dict[str, Any]]:
    """Read the persisted hotkey payload (if any)."""
    json_path = memory_root / "logs" / "hotkey-center.json"
    if not json_path.exists():
        return None
    try:
        return json.loads(json_path.read_text())
    except json.JSONDecodeError:
        return None
