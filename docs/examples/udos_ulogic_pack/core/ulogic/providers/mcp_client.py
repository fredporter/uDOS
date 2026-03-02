from __future__ import annotations
from typing import Any, Dict
import json
from .queue import DeferredQueue

class McpClient:
    def __init__(self, queue: DeferredQueue):
        self.queue = queue

    def call_tool(self, tool_name: str, payload: Dict[str, Any]) -> str:
        self.queue.enqueue({"type": "mcp.call", "tool": tool_name, "payload": payload})
        return json.dumps({"ok": False, "deferred": True, "tool": tool_name, "payload": payload}, indent=2)
