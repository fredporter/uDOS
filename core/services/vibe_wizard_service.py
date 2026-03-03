"""
Vibe Wizard Service

Manages automation workflows, task scheduling, and orchestration.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import time

from core.services.logging_manager import get_logger
from core.services.persistence_service import get_persistence_service
from core.services.time_utils import utc_now_iso_z


@dataclass
class AutomationTask:
    """Automation task representation."""
    id: str
    name: str
    description: str
    status: str  # "idle", "running", "completed", "failed"
    created: str
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    schedule: Optional[str] = None  # cron expression


class VibeWizardService:
    """Manage automation workflows and task scheduling."""

    _DATA_FILE = "wizard_tasks"
    _STATS_FILE = "wizard_task_stats"

    def __init__(self):
        """Initialize wizard service."""
        self.logger = get_logger("vibe-wizard-service")
        self.persistence_service = get_persistence_service()
        self.tasks: Dict[str, AutomationTask] = {}
        self.task_stats: Dict[str, Dict[str, float | int]] = {}
        self._active_runs: Dict[str, float] = {}
        self._load_tasks()
        self._load_stats()

    def _load_tasks(self) -> None:
        """Load automation tasks from persistent storage."""
        self.logger.debug("Loading automation tasks from persistence...")
        data = self.persistence_service.read_data(self._DATA_FILE)
        if data and "tasks" in data:
            self.tasks = {
                task_id: AutomationTask(**task_data)
                for task_id, task_data in data["tasks"].items()
            }
            self.logger.info(f"Loaded {len(self.tasks)} automation tasks.")
        else:
            self.logger.warning("No persistent task data found.")

    def _save_tasks(self) -> None:
        """Save automation tasks to persistent storage."""
        self.logger.debug("Saving automation tasks to persistence...")
        data = {
            "tasks": {
                task_id: asdict(task) for task_id, task in self.tasks.items()
            }
        }
        self.persistence_service.write_data(self._DATA_FILE, data)

    def _load_stats(self) -> None:
        """Load per-task run statistics from persistent storage."""
        data = self.persistence_service.read_data(self._STATS_FILE)
        raw_stats = data.get("stats", {}) if data else {}
        self.task_stats = {
            task_id: {
                "total_runs": int(entry.get("total_runs", 0)),
                "successful_runs": int(entry.get("successful_runs", 0)),
                "failed_runs": int(entry.get("failed_runs", 0)),
                "average_duration_sec": float(entry.get("average_duration_sec", 0.0)),
            }
            for task_id, entry in raw_stats.items()
        }

    def _save_stats(self) -> None:
        """Persist per-task run statistics."""
        self.persistence_service.write_data(self._STATS_FILE, {"stats": self.task_stats})

    def _ensure_task_stats(self, task_id: str) -> Dict[str, float | int]:
        """Get or initialize task stats record."""
        if task_id not in self.task_stats:
            self.task_stats[task_id] = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "average_duration_sec": 0.0,
            }
        return self.task_stats[task_id]

    def list_tasks(self) -> Dict[str, Any]:
        """List all automation tasks."""
        tasks = [asdict(t) for t in self.tasks.values()]
        return {
            "status": "success",
            "tasks": tasks,
            "count": len(tasks),
        }

    def start_task(self, task_id: str) -> Dict[str, Any]:
        """
        Start an automation task.

        Args:
            task_id: Task ID

        Returns:
            Dict with execution status
        """
        if task_id not in self.tasks:
            return {
                "status": "error",
                "message": f"Task not found: {task_id}",
            }

        task = self.tasks[task_id]
        task.status = "running"
        task.last_run = utc_now_iso_z()
        self._active_runs[task_id] = time.perf_counter()
        self._save_tasks()

        self.logger.info(f"Started task: {task_id}")

        return {
            "status": "success",
            "message": f"Task started: {task.name}",
            "task_id": task_id,
            "task": asdict(task),
        }

    def stop_task(self, task_id: str) -> Dict[str, Any]:
        """
        Stop a running automation task.

        Args:
            task_id: Task ID

        Returns:
            Dict with stop status
        """
        if task_id not in self.tasks:
            return {
                "status": "error",
                "message": f"Task not found: {task_id}",
            }

        task = self.tasks[task_id]

        if task.status != "running":
            return {
                "status": "error",
                "message": f"Task is not running: {task_id}",
            }

        task.status = "idle"
        stats = self._ensure_task_stats(task_id)
        elapsed = max(0.0, time.perf_counter() - self._active_runs.pop(task_id, time.perf_counter()))
        total_runs = int(stats["total_runs"]) + 1
        successful_runs = int(stats["successful_runs"]) + 1
        prev_avg = float(stats["average_duration_sec"])
        stats["total_runs"] = total_runs
        stats["successful_runs"] = successful_runs
        stats["average_duration_sec"] = ((prev_avg * (total_runs - 1)) + elapsed) / total_runs
        self._save_tasks()
        self._save_stats()

        self.logger.info(f"Stopped task: {task_id}")

        return {
            "status": "success",
            "message": f"Task stopped: {task.name}",
            "task_id": task_id,
        }

    def task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get detailed status of an automation task.

        Args:
            task_id: Task ID

        Returns:
            Dict with task status and metrics
        """
        if task_id not in self.tasks:
            return {
                "status": "error",
                "message": f"Task not found: {task_id}",
            }

        task = self.tasks[task_id]
        stats = self._ensure_task_stats(task_id)
        is_running = task.status == "running"
        current_duration = (
            max(0.0, time.perf_counter() - self._active_runs.get(task_id, time.perf_counter()))
            if is_running
            else 0.0
        )

        return {
            "status": "success",
            "task": asdict(task),
            "metrics": {
                "total_runs": int(stats["total_runs"]),
                "successful_runs": int(stats["successful_runs"]),
                "failed_runs": int(stats["failed_runs"]),
                "average_duration_sec": round(float(stats["average_duration_sec"]), 2),
                "current_run_duration_sec": round(current_duration, 2),
            },
        }


# Global singleton
_wizard_service: Optional[VibeWizardService] = None


def get_wizard_service() -> VibeWizardService:
    """Get or create the global wizard service."""
    global _wizard_service
    if _wizard_service is None:
        _wizard_service = VibeWizardService()
    return _wizard_service
