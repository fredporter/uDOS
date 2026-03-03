"""Wizard-owned task review service for Empire."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from wizard.services.empire_extension_service import get_empire_extension_service
from wizard.services.empire_scope_service import get_empire_scope_service


class EmpireTaskService:
    """Manage task review state for Empire-derived tasks."""

    def __init__(self) -> None:
        self.empire = get_empire_extension_service()
        self.scope_service = get_empire_scope_service()

    def _storage(self):
        return self.empire._import_module("empire.services.storage")

    def _resolve_db_path(self, scope: str = "master", binder_id: str | None = None) -> Path:
        resolved = self.scope_service.resolve(scope=scope, binder_id=binder_id)
        return Path(resolved["db_path"])

    def review_task(
        self,
        *,
        task_id: str,
        scope: str = "master",
        binder_id: str | None = None,
        review_status: str,
        status: str | None = None,
        due_hint: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        if review_status not in {"pending_review", "ready", "approved", "needs_changes"}:
            raise ValueError("review_status must be pending_review, ready, approved, or needs_changes")
        db_path = self._resolve_db_path(scope=scope, binder_id=binder_id)
        if not self.empire.get_task(task_id, scope=scope, binder_id=binder_id):
            raise ValueError(f"Unknown task: {task_id}")
        self._storage().update_task_review(
            task_id=task_id,
            review_status=review_status,
            status=status,
            due_hint=due_hint,
            notes=notes,
            db_path=db_path,
        )
        return self.empire.get_task(task_id, scope=scope, binder_id=binder_id) or {"task_id": task_id}


_service: EmpireTaskService | None = None


def get_empire_task_service() -> EmpireTaskService:
    global _service
    if _service is None:
        _service = EmpireTaskService()
    return _service
