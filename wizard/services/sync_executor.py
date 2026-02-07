"""
Sync Executor Service (Wizard)

Minimal queue executor stub used by /api/sync-executor routes.
Provides safe, no-op implementations until the real executor is installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class SyncExecutionRecord:
    timestamp: str
    status: str
    detail: str


@dataclass
class SyncExecutor:
    queue: List[Dict[str, Any]] = field(default_factory=list)
    history: List[SyncExecutionRecord] = field(default_factory=list)

    def _record(self, status: str, detail: str) -> None:
        self.history.append(
            SyncExecutionRecord(
                timestamp=datetime.utcnow().isoformat(),
                status=status,
                detail=detail,
            )
        )
        if len(self.history) > 200:
            self.history = self.history[-200:]

    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "ready",
            "queued": len(self.queue),
            "last_run": self.history[-1].timestamp if self.history else None,
        }

    def execute_queue(self) -> Dict[str, Any]:
        if not self.queue:
            self._record("idle", "No sync jobs queued")
            return {"status": "idle", "message": "No sync jobs queued"}

        processed = len(self.queue)
        self.queue.clear()
        self._record("success", f"Processed {processed} queued sync jobs")
        return {"status": "success", "processed": processed}

    def get_queue(self) -> Dict[str, Any]:
        return {"queue": list(self.queue)}

    def get_execution_history(self, limit: int = 50) -> Dict[str, Any]:
        items = self.history[-limit:] if limit else self.history
        return {
            "history": [
                {"timestamp": h.timestamp, "status": h.status, "detail": h.detail}
                for h in items
            ]
        }
