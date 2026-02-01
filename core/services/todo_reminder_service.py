"""
Todo reminder/timer service
===========================

Schedules horizon-based checks against the TodoManager so due-soon alerts can
land in the health-training log and trigger notification history entries.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.services.health_training import append_training_entry
from core.services.notification_history_service import record_notification
from core.services.todo_service import Task, TodoManager, get_service


class TodoReminderService:
    """Reminder service that keeps TodoManager tasks visible to automation."""

    DEFAULT_HORIZON_HOURS = 24
    DEFAULT_LIMIT = 6

    def __init__(self, manager: Optional[TodoManager] = None):
        self.manager = manager or get_service()

    def due_soon(
        self, horizon_hours: Optional[int] = None, limit: Optional[int] = None
    ) -> List[Task]:
        """Return tasks whose due_date sits within the next `horizon_hours`."""
        horizon = timedelta(hours=horizon_hours or self.DEFAULT_HORIZON_HOURS)
        now = datetime.utcnow()
        tasks = [
            task
            for task in self.manager.list_pending()
            if now <= task.due_date <= now + horizon
        ]
        tasks.sort(key=lambda t: t.due_date)
        if limit:
            return tasks[:limit]
        return tasks

    def log_reminder(
        self,
        horizon_hours: Optional[int] = None,
        limit: Optional[int] = None,
        context: str = "todo",
    ) -> Optional[Dict[str, object]]:
        """Create a reminder entry and persist it if tasks are due soon."""
        tasks = self.due_soon(horizon_hours=horizon_hours, limit=limit)
        if not tasks:
            return None

        horizon = horizon_hours or self.DEFAULT_HORIZON_HOURS
        payload = {
            "event": "todo_reminder",
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "horizon_hours": horizon,
            "task_count": len(tasks),
            "tasks": [
                {
                    "task_id": task.task_id,
                    "title": task.title,
                    "due_date": task.due_date.isoformat(),
                    "remaining_hours": task.remaining_hours,
                    "status": task.status,
                }
                for task in tasks
            ],
            "message": f"{len(tasks)} task(s) due within the next {horizon} hour(s)",
        }
        append_training_entry(payload)
        record_notification(
            {
                "timestamp": payload["timestamp"],
                "source": "todo-reminder",
                "message": payload["message"],
                "tasks": payload["tasks"],
            }
        )
        return payload


def get_reminder_service(manager: Optional[TodoManager] = None) -> TodoReminderService:
    return TodoReminderService(manager=manager)
