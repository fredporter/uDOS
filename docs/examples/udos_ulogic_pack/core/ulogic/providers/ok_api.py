from __future__ import annotations
from typing import Any, Dict
import json
from .queue import DeferredQueue

class OkApiClient:
    def __init__(self, queue: DeferredQueue):
        self.queue = queue

    def call(self, endpoint: str, payload: Dict[str, Any]) -> str:
        self.queue.enqueue({"type": "ok.call", "endpoint": endpoint, "payload": payload})
        return json.dumps({"ok": False, "deferred": True, "endpoint": endpoint, "payload": payload}, indent=2)
