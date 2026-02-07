from typing import Any, Dict, List

from core.commands.base import BaseCommandHandler
from core.services.hotkey_map import get_hotkey_payload
from core.services.maintenance_utils import get_memory_root
from core.services.logging_api import get_logger
from core.tui.output import OutputToolkit

logger = get_logger("hotkey-handler")


class HotkeyHandler(BaseCommandHandler):
    """Show the current hotkey map and snapshot info."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict[str, Any]:
        memory_root = get_memory_root()
        payload = get_hotkey_payload(memory_root)
        lines = [
            OutputToolkit.banner("HOTKEYS"),
            f"Snapshot: {payload.get('snapshot')}",
            f"Last updated: {payload.get('last_updated')}",
            "",
            "Key bindings:",
        ]
        for entry in payload.get("key_map", []):
            lines.append(f"  • {entry['key']}: {entry['action']} → {entry['notes']}")

        logger.info("[LOCAL] Displayed hotkey map")
        return {
            "status": "success",
            "output": "\n".join(lines),
            "payload": payload,
        }
