"""SCHEDULER command handler - Wizard task scheduling controls."""

from __future__ import annotations

from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import sqlite3
import uuid

from core.commands.base import BaseCommandHandler
from core.tui.output import OutputToolkit
from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("scheduler-handler")


class SchedulerHandler(BaseCommandHandler):
    """Handler for SCHEDULER command - list/run/log Wizard tasks."""

    def __init__(self):
        super().__init__()
        self.db_path = get_repo_root() / "memory" / "wizard" / "tasks.db"

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        if not params:
            return self._list_tasks()

        action = params[0].upper()
        args = params[1:]

        if action in {"LIST", "LS"}:
            return self._list_tasks()
        if action in {"RUN", "EXECUTE", "TRIGGER"}:
            return self._run_task(args)
        if action in {"LOG", "LOGS", "HISTORY"}:
            return self._show_logs(args)
        if action in {"HELP", "--HELP", "-H", "?"}:
            return self._help()

        return {
            "status": "error",
            "message": f"Unknown SCHEDULER option: {action}",
            "output": self._help_text(),
        }

    def _help_text(self) -> str:
        return "\n".join(
            [
                OutputToolkit.banner("SCHEDULER"),
                "SCHEDULER LIST             Show scheduled tasks",
                "SCHEDULER RUN <task_id>    Trigger a task immediately",
                "SCHEDULER LOG [id]         View task runs (task_id or run_id)",
            ]
        )

    def _help(self) -> Dict:
        return {"status": "success", "output": self._help_text()}

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _list_tasks(self) -> Dict:
        banner = OutputToolkit.banner("SCHEDULER TASKS")
        if not self.db_path.exists():
            return {
                "status": "error",
                "message": "Scheduler database not found",
                "output": banner + "\n❌ Missing memory/wizard/tasks.db",
            }

        rows = []
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        t.id,
                        t.name,
                        t.schedule,
                        t.enabled,
                        t.requires_network,
                        t.kind,
                        (
                            SELECT completed_at
                            FROM task_runs r
                            WHERE r.task_id = t.id
                            ORDER BY r.created_at DESC
                            LIMIT 1
                        ) AS last_completed,
                        (
                            SELECT result
                            FROM task_runs r
                            WHERE r.task_id = t.id
                            ORDER BY r.created_at DESC
                            LIMIT 1
                        ) AS last_result
                    FROM tasks t
                    ORDER BY t.updated_at DESC
                    """
                )
                rows = cursor.fetchall()
        except Exception as exc:
            logger.error("[SCHEDULER] Failed to list tasks: %s", exc)
            return {"status": "error", "message": f"Failed to read tasks: {exc}"}

        lines = [banner, ""]
        if not rows:
            lines.append("(no scheduled tasks found)")
            return {"status": "success", "output": "\n".join(lines)}

        for row in rows:
            task_id, name, schedule, enabled, requires_network, kind, last_completed, last_result = row
            enabled_label = "enabled" if enabled else "disabled"
            network_label = "net" if requires_network else "offline"
            lines.append(f"- {name} [{task_id}]")
            lines.append(f"  Schedule: {schedule} | {enabled_label} | {network_label}")
            if kind:
                lines.append(f"  Kind: {kind}")
            if last_completed or last_result:
                lines.append(f"  Last: {last_result or 'unknown'} @ {last_completed or 'n/a'}")
            lines.append("")

        return {"status": "success", "output": "\n".join(lines)}

    def _resolve_task_id(self, identifier: str) -> Optional[str]:
        if identifier.lower().startswith("task_"):
            return identifier
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM tasks WHERE name = ? ORDER BY updated_at DESC LIMIT 1",
                (identifier,),
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def _run_task(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("SCHEDULER RUN")
        if not args:
            return {
                "status": "error",
                "message": "Missing task id",
                "output": banner + "\nUsage: SCHEDULER RUN <task_id>",
            }

        if not self.db_path.exists():
            return {
                "status": "error",
                "message": "Scheduler database not found",
                "output": banner + "\n❌ Missing memory/wizard/tasks.db",
            }

        identifier = args[0]
        try:
            task_id = self._resolve_task_id(identifier)
        except Exception as exc:
            return {
                "status": "error",
                "message": f"Failed to resolve task: {exc}",
                "output": banner,
            }
        if not task_id:
            return {
                "status": "error",
                "message": f"Task not found: {identifier}",
                "output": banner + "\nRun: SCHEDULER LIST",
            }

        run_id = f"run_{uuid.uuid4().hex[:12]}"
        scheduled_for = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO task_runs (id, task_id, state, started_at, created_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                    (run_id, task_id, "sprout", None),
                )
                cursor.execute(
                    """
                    INSERT INTO task_queue (task_id, run_id, state, scheduled_for, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (task_id, run_id, "pending", scheduled_for),
                )
                conn.commit()
        except Exception as exc:
            logger.error("[SCHEDULER] Failed to queue task %s: %s", task_id, exc)
            return {
                "status": "error",
                "message": f"Failed to queue task: {exc}",
                "output": banner,
            }

        lines = [
            banner,
            "",
            f"✅ Queued task {task_id}",
            f"Run ID: {run_id}",
            f"Scheduled for: {scheduled_for} UTC",
        ]
        return {"status": "success", "output": "\n".join(lines)}

    def _show_logs(self, args: List[str]) -> Dict:
        banner = OutputToolkit.banner("SCHEDULER LOGS")
        if not self.db_path.exists():
            return {
                "status": "error",
                "message": "Scheduler database not found",
                "output": banner + "\n❌ Missing memory/wizard/tasks.db",
            }

        identifier = args[0] if args else None

        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                if identifier and identifier.lower().startswith("run_"):
                    cursor.execute(
                        """
                        SELECT r.id, r.task_id, t.name, r.state, r.started_at, r.completed_at, r.result, r.output
                        FROM task_runs r
                        LEFT JOIN tasks t ON t.id = r.task_id
                        WHERE r.id = ?
                        """,
                        (identifier,),
                    )
                    row = cursor.fetchone()
                    if not row:
                        return {
                            "status": "error",
                            "message": f"Run not found: {identifier}",
                            "output": banner,
                        }
                    run_id, task_id, name, state, started_at, completed_at, result, output = row
                    lines = [
                        banner,
                        "",
                        f"Run: {run_id}",
                        f"Task: {name or task_id}",
                        f"State: {state}",
                        f"Started: {started_at or 'n/a'}",
                        f"Completed: {completed_at or 'n/a'}",
                        f"Result: {result or 'n/a'}",
                    ]
                    if output:
                        lines.append("")
                        lines.append("Output:")
                        lines.append(output[:1200])
                    return {"status": "success", "output": "\n".join(lines)}

                task_filter = None
                if identifier:
                    task_filter = self._resolve_task_id(identifier) or identifier

                if task_filter:
                    cursor.execute(
                        """
                        SELECT r.id, r.task_id, t.name, r.state, r.started_at, r.completed_at, r.result
                        FROM task_runs r
                        LEFT JOIN tasks t ON t.id = r.task_id
                        WHERE r.task_id = ?
                        ORDER BY r.created_at DESC
                        LIMIT 20
                        """,
                        (task_filter,),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT r.id, r.task_id, t.name, r.state, r.started_at, r.completed_at, r.result
                        FROM task_runs r
                        LEFT JOIN tasks t ON t.id = r.task_id
                        ORDER BY r.created_at DESC
                        LIMIT 20
                        """
                    )
                rows = cursor.fetchall()
        except Exception as exc:
            logger.error("[SCHEDULER] Failed to read logs: %s", exc)
            return {"status": "error", "message": f"Failed to read logs: {exc}"}

        lines = [banner, ""]
        if not rows:
            lines.append("(no task runs found)")
            return {"status": "success", "output": "\n".join(lines)}

        for row in rows:
            run_id, task_id, name, state, started_at, completed_at, result = row
            lines.append(f"- {run_id}  {name or task_id}")
            lines.append(f"  State: {state} | Result: {result or 'n/a'}")
            lines.append(f"  Started: {started_at or 'n/a'} | Completed: {completed_at or 'n/a'}")
            lines.append("")

        return {"status": "success", "output": "\n".join(lines)}
