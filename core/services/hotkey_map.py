"""Canonical v1.5 TUI keybinding map and payload helpers."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

def get_hotkey_map() -> List[Dict[str, str]]:
    """Return the canonical interaction model shared by UI and automation."""
    return [
        {"key": "Ctrl+C", "action": "Immediate exit", "notes": "Global hard exit unless explicitly overridden."},
        {"key": "Esc", "action": "Cancel / go back", "notes": "Global cancel and back navigation."},
        {"key": "Enter", "action": "Confirm / execute", "notes": "Global confirmation action."},
        {"key": "Tab", "action": "Next field/pane", "notes": "Moves focus forward across panes/fields."},
        {"key": "Shift+Tab", "action": "Previous field/pane", "notes": "Moves focus backward across panes/fields."},
        {"key": "Ctrl+L", "action": "Redraw screen", "notes": "Refreshes terminal rendering."},
        {"key": "?", "action": "Toggle help overlay", "notes": "Opens context help without leaving screen."},
        {"key": ":", "action": "Command palette", "notes": "Opens fuzzy command launcher."},
        {"key": "/", "action": "Search / filter", "notes": "Enters filter mode in lists and selectors."},
        {"key": "↑ ↓", "action": "Move selection", "notes": "Shared list/menu navigation."},
        {"key": "← →", "action": "Change column/level", "notes": "Shared horizontal navigation."},
        {"key": "Home / End", "action": "Jump bounds", "notes": "Jump to start/end of current list."},
        {"key": "PgUp / PgDn", "action": "Page navigation", "notes": "Page-wise list movement."},
        {"key": "j k h l", "action": "Optional vim nav", "notes": "Power-user alternative navigation keys."},
        {"key": "Space", "action": "Toggle multi-select", "notes": "Used in multi-select controls."},
        {"key": "a / x", "action": "Select all / clear", "notes": "Multi-select batch actions."},
        {"key": "n / N", "action": "Search next/prev", "notes": "Navigate current search results."},
        {"key": "Ctrl+A / Ctrl+E", "action": "Input line bounds", "notes": "Move to start/end of line."},
        {"key": "Ctrl+U / Ctrl+W / Ctrl+K", "action": "Input delete ops", "notes": "Delete line/word/to-end."},
        {"key": "Ctrl+Y / Ctrl+D", "action": "Paste buffer / delete char", "notes": "Shell-style text editing."},
        {"key": "F1", "action": "Help", "notes": "System-level teletext help."},
        {"key": "F2", "action": "System status", "notes": "Runtime status and health summary."},
        {"key": "F3", "action": "Logs", "notes": "Open runtime logs view."},
        {"key": "F4", "action": "Extensions", "notes": "Open extension/plug-in surface."},
        {"key": "F5", "action": "Refresh", "notes": "Refresh active panel/screen."},
        {"key": "F6", "action": "Toggle panels", "notes": "Cycle or toggle panel layout."},
        {"key": "F7", "action": "Missions", "notes": "Open mission/workflow surface."},
        {"key": "F8", "action": "Environment", "notes": "Open environment/config surface."},
        {"key": "F9", "action": "Settings", "notes": "Open runtime settings."},
        {"key": "F10", "action": "Exit", "notes": "Exit shortcut with explicit key target."},
        {"key": "Ctrl+R", "action": "Wizard rerun task", "notes": "Unlocked at Wizard rank."},
        {"key": "Ctrl+P", "action": "Wizard project switcher", "notes": "Unlocked at Wizard rank."},
        {"key": "Ctrl+T", "action": "Wizard task runner", "notes": "Unlocked at Wizard rank."},
        {"key": "Ctrl+O", "action": "Wizard object explorer", "notes": "Unlocked at Wizard rank."},
        {"key": "Ctrl+G", "action": "Wizard scaffold generate", "notes": "Unlocked at Wizard rank."},
    ]


def _get_repo_root_from(memory_root: Path) -> Path:
    """Return the repository root path assuming `/memory` sits directly under repo root."""
    return memory_root.parent


def _build_status_payload(memory_root: Path) -> Dict[str, Any]:
    """Return status payload for automation and UI contracts."""
    repo_root = _get_repo_root_from(memory_root)
    doc_path = repo_root / "docs" / "specs" / "TUI-KEYBINDINGS-v1.5.md"
    status = {
        "hotkey_register": str(memory_root / "logs" / "hotkey-center.json"),
        "doc_path": str(doc_path),
        "doc_last_modified": None,
        "principles": [
            "Consistency: same controls across every screen",
            "Predictability: Unix/Vim-friendly behavior",
            "Safety: bracketed paste with atomic insert behavior",
            "Speed: full keyboard navigation for expert users",
        ],
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
        "last_updated": datetime.now(timezone.utc).isoformat(),
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
