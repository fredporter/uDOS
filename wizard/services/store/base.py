from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class WizardStore(ABC):
    @abstractmethod
    def get_scheduler_settings(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update_scheduler_settings(self, updates: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_task(self, task_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def list_tasks(self, *, state: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_task_by_kind(self, kind: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def schedule_task(self, task_id: str, scheduled_for: datetime) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_pending_queue(self, *, limit: int = 10) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_scheduled_queue(self, *, limit: int = 50) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def claim_due_queue_items(self, *, limit: int = 10) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def release_queue_item(
        self,
        queue_id: int,
        *,
        scheduled_for: datetime | None = None,
        reason: str | None = None,
        backoff_seconds: int | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def retry_queue_item(self, queue_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def complete_task_run(self, run_id: str, *, result: str, output: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_execution_history(self, *, limit: int = 50) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_task_history(self, task_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_last_run_time(self, task_id: str) -> datetime | None:
        raise NotImplementedError

    @abstractmethod
    def get_task_stats(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def create_launch_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def update_launch_session(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_launch_session(self, session_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_launch_sessions(self, *, target: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def list_alerts(self, *, limit: int = 100) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def upsert_alert(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_audit_entries(self, *, limit: int = 100) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def append_audit_entry(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def save_notification(self, payload: dict[str, Any]) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_notifications(self, *, limit: int = 20, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        raise NotImplementedError

    @abstractmethod
    def search_notifications(
        self,
        *,
        query: str | None = None,
        type_filter: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def delete_notification(self, notification_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def clear_old_notifications(self, *, cutoff_iso: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_notification_stats(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_operator_profile(self, subject: str, email: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def set_operator_role(self, subject: str, role: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_device_record(self, device_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def list_device_records(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def upsert_device_record(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def delete_device_record(self, device_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_runtime_state(self, key: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    def set_runtime_state(self, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
