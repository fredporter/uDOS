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


def get_hotkey_map() -> List[Dict[str, str]]:
    """Return the canonical key map shared between UI and automation."""
    return [
        {"key": "Tab", "action": "Command Selector", "notes": "Opens the TAB menu even in fallback mode."},
        {"key": "F1", "action": "Status / Help banner", "notes": "Displays Self-Healer + Hot Reload stats."},
        {"key": "F2", "action": "Logs / Diagnostics", "notes": "Shows logs and diagnostics summary."},
        {"key": "F3", "action": "REPAIR shortcut", "notes": "Triggers SelfHealer checks via CLI."},
        {"key": "F4", "action": "RESTART / HOT RELOAD", "notes": "Reloads handlers and restarts watchers."},
        {"key": "F5", "action": "Extension palette", "notes": "Opens the plugin menu (LibraryManager metadata)."},
        {"key": "F6", "action": "Script / PATTERN", "notes": "Runs PATTERN/system script banners for automation."},
        {"key": "F7", "action": "Sonic Device DB", "notes": "Shows Sonic USB/media capabilities from the device DB."},
        {"key": "F8", "action": "Hotkey Center", "notes": "Reloads this key map (including automation hints)."},
        {"key": "↑ / ↓", "action": "Command history", "notes": "Shared with SmartPrompt history/predictor."},
        {"key": "Enter", "action": "Confirm input", "notes": "Approves Date/Time/Timezone with overrides."},
    ]


def get_hotkey_payload(memory_root: Path) -> Dict[str, Any]:
    """Return the payload that automation scripts consume."""
    logs_dir = memory_root / "logs"
    snapshot_path = logs_dir / "hotkey-center.png"
    return {
        "key_map": get_hotkey_map(),
        "snapshot": str(snapshot_path),
        "last_updated": datetime.utcnow().isoformat(),
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
