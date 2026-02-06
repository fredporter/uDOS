"""
Sync Executor

Minimal queue executor for sync tasks. Provides status, queue, and history.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.path_utils import get_repo_root
from wizard.services.logging_manager import get_logger

logger = get_logger("sync-executor")


@dataclass
class SyncJob:
    job_id: str
    action: str
    created_at: str
    payload: Dict[str, Any]


@dataclass
class SyncExecution:
    job_id: str
    action: str
    status: str
    started_at: str
    finished_at: str
    detail: str


class SyncExecutor:
    def __init__(self) -> None:
        repo_root = get_repo_root()
        self.state_path = repo_root / "memory" / "wizard" / "sync_executor.json"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state = self._load_state()

    def get_status(self) -> Dict[str, Any]:
        return {
            "queue_depth": len(self._state["queue"]),
            "history_count": len(self._state["history"]),
            "last_execution": self._state["history"][0]["finished_at"] if self._state["history"] else None,
        }

    def get_queue(self) -> List[Dict[str, Any]]:
        return list(self._state["queue"])

    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self._state["history"])[:limit]

    def enqueue(self, action: str, payload: Optional[Dict[str, Any]] = None) -> SyncJob:
        job = SyncJob(
            job_id=f"job-{datetime.utcnow().timestamp()}",
            action=action,
            created_at=self._now(),
            payload=payload or {},
        )
        self._state["queue"].append(asdict(job))
        self._save_state()
        return job

    def execute_queue(self) -> Dict[str, Any]:
        executed: List[Dict[str, Any]] = []
        while self._state["queue"]:
            job = self._state["queue"].pop(0)
            execution = SyncExecution(
                job_id=job["job_id"],
                action=job["action"],
                status="completed",
                started_at=self._now(),
                finished_at=self._now(),
                detail="Executed placeholder sync action",
            )
            executed.append(asdict(execution))
            self._state["history"].insert(0, asdict(execution))

        self._save_state()
        return {"status": "success", "executed": executed}

    def _load_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return {"queue": [], "history": []}
        try:
            raw = json.loads(self.state_path.read_text())
            if not isinstance(raw, dict):
                return {"queue": [], "history": []}
            raw.setdefault("queue", [])
            raw.setdefault("history", [])
            return raw
        except Exception:
            return {"queue": [], "history": []}

    def _save_state(self) -> None:
        self.state_path.write_text(json.dumps(self._state, indent=2))

    def _now(self) -> str:
        return datetime.utcnow().isoformat() + "Z"
