"""
Task Scheduler Service - Organic Cron Model (Wizard)
"""

import json
import socket
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.system_info_service import get_system_info_service
from core.services.maintenance_utils import compost_cleanup
from wizard.services.repair_service import get_repair_service

logger = get_logger("wizard.tasks")


class TaskScheduler:
    """Manage task scheduling and execution with organic cron model."""

    def __init__(self, db_path: Optional[Path] = None):
        repo_root = get_repo_root()
        default_db = repo_root / "memory" / "wizard" / "tasks.db"
        self.db_path = Path(db_path or default_db)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"[WIZ] Task scheduler using {self.db_path}")

    def _init_db(self) -> None:
        schema_path = Path(__file__).parent / "schemas" / "task_schema.sql"
        try:
            with sqlite3.connect(self.db_path) as conn:
                if schema_path.exists():
                    conn.executescript(schema_path.read_text())
                else:
                    conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS tasks (
                            id TEXT PRIMARY KEY,
                            name TEXT,
                            description TEXT,
                            schedule TEXT,
                            state TEXT DEFAULT 'plant',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE TABLE IF NOT EXISTS task_runs (
                            id TEXT PRIMARY KEY,
                            task_id TEXT,
                            state TEXT,
                            result TEXT,
                            output TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            completed_at TIMESTAMP,
                            FOREIGN KEY(task_id) REFERENCES tasks(id)
                        );
                        CREATE TABLE IF NOT EXISTS task_queue (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            task_id TEXT,
                            run_id TEXT,
                            state TEXT,
                            scheduled_for TIMESTAMP,
                            processed_at TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY(task_id) REFERENCES tasks(id)
                        );
                        """
                    )
                self._ensure_columns(conn)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS scheduler_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    );
                    """
                )
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] DB init error: {exc}")

    def _ensure_columns(self, conn: sqlite3.Connection) -> None:
        columns = self._get_columns(conn, "tasks")
        self._add_column(conn, "tasks", columns, "provider", "TEXT")
        self._add_column(conn, "tasks", columns, "enabled", "INTEGER DEFAULT 1")
        self._add_column(conn, "tasks", columns, "priority", "INTEGER DEFAULT 5")
        self._add_column(conn, "tasks", columns, "need", "INTEGER DEFAULT 5")
        self._add_column(conn, "tasks", columns, "mission", "TEXT")
        self._add_column(conn, "tasks", columns, "objective", "TEXT")
        self._add_column(conn, "tasks", columns, "resource_cost", "INTEGER DEFAULT 1")
        self._add_column(conn, "tasks", columns, "requires_network", "INTEGER DEFAULT 0")
        self._add_column(conn, "tasks", columns, "kind", "TEXT")
        self._add_column(conn, "tasks", columns, "payload", "TEXT")

        queue_columns = self._get_columns(conn, "task_queue")
        self._add_column(conn, "task_queue", queue_columns, "priority", "INTEGER DEFAULT 5")
        self._add_column(conn, "task_queue", queue_columns, "need", "INTEGER DEFAULT 5")
        self._add_column(conn, "task_queue", queue_columns, "resource_cost", "INTEGER DEFAULT 1")
        self._add_column(conn, "task_queue", queue_columns, "requires_network", "INTEGER DEFAULT 0")

    def get_settings(self) -> Dict[str, Any]:
        defaults = {
            "max_tasks_per_tick": 2,
            "tick_seconds": 60,
            "allow_network": True,
        }
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT key, value FROM scheduler_settings")
                rows = {row["key"]: row["value"] for row in cursor.fetchall()}
            for key, value in rows.items():
                try:
                    defaults[key] = json.loads(value)
                except json.JSONDecodeError:
                    defaults[key] = value
        except sqlite3.Error:
            pass
        return defaults

    def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        settings = self.get_settings()
        settings.update({k: v for k, v in updates.items() if v is not None})
        try:
            with sqlite3.connect(self.db_path) as conn:
                for key, value in settings.items():
                    conn.execute(
                        "INSERT OR REPLACE INTO scheduler_settings (key, value) VALUES (?, ?)",
                        (key, json.dumps(value)),
                    )
                conn.commit()
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Scheduler settings update error: {exc}")
        return settings

    def _get_columns(self, conn: sqlite3.Connection, table: str) -> set:
        cursor = conn.execute(f"PRAGMA table_info({table});")
        return {row[1] for row in cursor.fetchall()}

    def _add_column(
        self,
        conn: sqlite3.Connection,
        table: str,
        columns: set,
        column: str,
        definition: str,
    ) -> None:
        if column in columns:
            return
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def create_task(
        self,
        name: str,
        description: str = "",
        schedule: str = "daily",
        provider: Optional[str] = None,
        enabled: bool = True,
        priority: int = 5,
        need: int = 5,
        mission: Optional[str] = None,
        objective: Optional[str] = None,
        resource_cost: int = 1,
        requires_network: bool = False,
        kind: Optional[str] = None,
        payload: Optional[dict] = None,
    ) -> Dict[str, Any]:
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                self._ensure_columns(conn)
                conn.execute(
                    """INSERT INTO tasks (
                        id, name, description, schedule, state, provider, enabled,
                        priority, need, mission, objective, resource_cost, requires_network,
                        kind, payload
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task_id,
                        name,
                        description,
                        schedule,
                        "plant",
                        provider,
                        1 if enabled else 0,
                        priority,
                        need,
                        mission,
                        objective,
                        resource_cost,
                        1 if requires_network else 0,
                        kind,
                        json.dumps(payload or {}),
                    ),
                )
                conn.commit()
            return {
                "id": task_id,
                "name": name,
                "description": description,
                "schedule": schedule,
                "provider": provider,
                "enabled": enabled,
                "priority": priority,
                "need": need,
                "mission": mission,
                "objective": objective,
                "resource_cost": resource_cost,
                "requires_network": requires_network,
                "kind": kind,
                "payload": payload or {},
                "state": "plant",
                "created_at": datetime.now().isoformat(),
            }
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Create task error: {exc}")
            return {"error": str(exc)}

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                data = dict(row)
                if "payload" in data and isinstance(data["payload"], str):
                    try:
                        data["payload"] = json.loads(data["payload"])
                    except json.JSONDecodeError:
                        pass
                return data
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Get task error: {exc}")
            return None

    def list_tasks(
        self, state: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                if state:
                    cursor = conn.execute(
                        "SELECT * FROM tasks WHERE state = ? LIMIT ?", (state, limit)
                    )
                else:
                    cursor = conn.execute("SELECT * FROM tasks LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] List tasks error: {exc}")
            return []

    def schedule_task(
        self, task_id: str, scheduled_for: Optional[datetime] = None
    ) -> Dict[str, Any]:
        scheduled_for = scheduled_for or datetime.now()
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                self._ensure_columns(conn)
                cursor = conn.execute(
                    "SELECT priority, need, resource_cost, requires_network FROM tasks WHERE id = ?",
                    (task_id,),
                )
                task_row = cursor.fetchone() or (5, 5, 1, 0)
                # Prevent scheduling duplicates for the same task if a pending run already exists
                dup_check = conn.execute(
                    "SELECT run_id FROM task_queue WHERE task_id = ? AND state = 'pending'",
                    (task_id,),
                ).fetchone()
                if dup_check:
                    return {
                        "task_id": task_id,
                        "run_id": dup_check["run_id"],
                        "state": "pending",
                        "scheduled_for": scheduled_for.isoformat(),
                        "note": "duplicate avoided",
                    }
                conn.execute(
                    """INSERT INTO task_runs (id, task_id, state) VALUES (?, ?, ?)""",
                    (run_id, task_id, "sprout"),
                )
                conn.execute(
                    """INSERT INTO task_queue
                    (task_id, run_id, state, scheduled_for, priority, need, resource_cost, requires_network)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task_id,
                        run_id,
                        "pending",
                        scheduled_for,
                        task_row[0],
                        task_row[1],
                        task_row[2],
                        task_row[3],
                    ),
                )
                conn.execute(
                    "UPDATE tasks SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    ("sprout", task_id),
                )
                conn.commit()
            return {
                "task_id": task_id,
                "run_id": run_id,
                "state": "pending",
                "scheduled_for": scheduled_for.isoformat(),
            }
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Schedule task error: {exc}")
            return {"error": str(exc)}

    def get_pending_queue(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT q.*, t.name, t.schedule, t.priority, t.need, t.mission,
                           t.objective, t.resource_cost, t.requires_network,
                           t.kind, t.payload
                    FROM task_queue q
                    JOIN tasks t ON q.task_id = t.id
                    WHERE q.state = 'pending' AND q.scheduled_for <= CURRENT_TIMESTAMP
                    LIMIT ?
                    """,
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Pending queue error: {exc}")
            return []

    def get_scheduled_queue(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT q.*, t.name, t.schedule, t.priority, t.need, t.mission,
                           t.objective, t.resource_cost, t.requires_network,
                           t.kind, t.payload
                    FROM task_queue q
                    JOIN tasks t ON q.task_id = t.id
                    ORDER BY q.scheduled_for ASC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = []
                for row in cursor.fetchall():
                    data = dict(row)
                    if isinstance(data.get("payload"), str):
                        try:
                            data["payload"] = json.loads(data["payload"])
                        except json.JSONDecodeError:
                            pass
                    rows.append(data)
                return rows
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Scheduled queue error: {exc}")
            return []

    def mark_processing(self, queue_id: int) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE task_queue SET state = 'processing' WHERE id = ?",
                    (queue_id,),
                )
                conn.commit()
            return True
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Mark processing error: {exc}")
            return False

    def complete_task(
        self, run_id: str, result: str = "success", output: str = ""
    ) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """UPDATE task_runs SET state='compost', result=?, output=?, completed_at=CURRENT_TIMESTAMP WHERE id=?""",
                    (result, output, run_id),
                )
                cursor = conn.execute(
                    "SELECT task_id FROM task_runs WHERE id = ?", (run_id,)
                )
                row = cursor.fetchone()
                task_id = row[0] if row else None
                conn.execute(
                    "UPDATE task_queue SET state='completed', processed_at=CURRENT_TIMESTAMP WHERE run_id=?",
                    (run_id,),
                )
                if task_id:
                    conn.execute(
                        "UPDATE tasks SET state=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                        ("harvest", task_id),
                    )
                conn.commit()
            return True
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Complete task error: {exc}")
            return False

    def get_task_history(self, task_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """SELECT * FROM task_runs WHERE task_id = ? ORDER BY created_at DESC LIMIT ?""",
                    (task_id, limit),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Task history error: {exc}")
            return []

    def get_execution_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """SELECT * FROM task_runs ORDER BY created_at DESC LIMIT ?""",
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Execution history error: {exc}")
            return []

    def get_task_runs(self, task_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return self.get_task_history(task_id, limit)

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        scheduled = self.schedule_task(task_id, datetime.now())
        if "error" in scheduled:
            return scheduled
        return {"scheduled": scheduled}

    def _task_due(self, task: Dict[str, Any]) -> bool:
        schedule = (task.get("schedule") or "daily").lower()
        last_run = self._get_last_run_time(task["id"])
        now = datetime.now()
        if schedule in {"once", "one"}:
            return last_run is None
        if schedule in {"hourly", "hour"}:
            return last_run is None or (now - last_run) >= timedelta(hours=1)
        if schedule in {"weekly", "week"}:
            return last_run is None or (now - last_run) >= timedelta(days=7)
        return last_run is None or (now - last_run) >= timedelta(days=1)

    def _get_last_run_time(self, task_id: str) -> Optional[datetime]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """SELECT completed_at FROM task_runs
                       WHERE task_id = ? AND completed_at IS NOT NULL
                       ORDER BY completed_at DESC LIMIT 1""",
                    (task_id,),
                )
                row = cursor.fetchone()
                if row and row[0]:
                    return datetime.fromisoformat(row[0])
        except Exception:
            return None
        return None

    def schedule_due_tasks(self) -> int:
        """Schedule due tasks into the queue."""
        scheduled = 0
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            self._ensure_columns(conn)
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE enabled = 1",
            )
            for row in cursor.fetchall():
                task = dict(row)
                if not self._task_due(task):
                    continue
                self.schedule_task(task["id"], datetime.now())
                scheduled += 1
        return scheduled

    def _score_task(self, task: Dict[str, Any]) -> int:
        priority = int(task.get("priority") or 5)
        need = int(task.get("need") or 5)
        score = priority * 2 + need
        if task.get("mission"):
            score += 1
        if task.get("objective"):
            score += 1
        return score

    def _resources_ok(self, task: Dict[str, Any]) -> bool:
        stats = get_system_info_service(get_repo_root()).get_system_stats()
        cpu = stats.get("cpu", {}).get("percent", 0)
        mem = stats.get("memory", {}).get("percent", 0)
        disk = stats.get("disk", {}).get("percent", 0)

        priority = int(task.get("priority") or 5)
        need = int(task.get("need") or 5)
        resource_cost = int(task.get("resource_cost") or 1)

        if cpu < 85 and mem < 88 and disk < 95:
            return True

        # Under pressure: allow only high-priority or low-cost work
        if priority >= 8 or need >= 8 or resource_cost <= 1:
            return True
        return False

    def _network_available(self) -> bool:
        try:
            socket.create_connection(("1.1.1.1", 53), timeout=1).close()
            return True
        except OSError:
            return False

    def run_pending(self, max_tasks: Optional[int] = None) -> Dict[str, Any]:
        """Schedule due tasks and execute a paced batch."""
        settings = self.get_settings()
        if max_tasks is None:
            max_tasks = int(settings.get("max_tasks_per_tick", 2))
        allow_network = bool(settings.get("allow_network", True))
        scheduled = self.schedule_due_tasks()
        pending = self.get_pending_queue(limit=20)
        if not pending:
            return {"scheduled": scheduled, "executed": 0}

        pending.sort(key=self._score_task, reverse=True)
        executed = 0
        network_ok = self._network_available() if allow_network else False
        for item in pending:
            if executed >= max_tasks:
                break
            if not self._resources_ok(item):
                continue
            if item.get("requires_network") and not network_ok:
                continue
            if not self.mark_processing(item["id"]):
                continue
            result, output = self._execute_task_item(item)
            self.complete_task(item["run_id"], result=result, output=output)
            executed += 1
        return {"scheduled": scheduled, "executed": executed}

    def _execute_task_item(self, item: Dict[str, Any]) -> tuple[str, str]:
        kind = item.get("kind")
        payload_raw = item.get("payload") or "{}"
        try:
            payload = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
        except json.JSONDecodeError:
            payload = {}

        if kind == "compost_cleanup":
            days = int(payload.get("days", 30))
            dry_run = bool(payload.get("dry_run", False))
            result = compost_cleanup(days=days, dry_run=dry_run)
            return "success", json.dumps(result)
        if kind == "backup_target":
            target_key = payload.get("target")
            notes = payload.get("notes")
            if not target_key:
                return "error", "backup_target missing payload.target"
            result = get_repair_service().backup_target(target_key, notes)
            return ("success" if result.get("success") else "error", json.dumps(result))

        return "skipped", "No executor for task kind"

    def ensure_daily_compost_cleanup(self, days: int = 30, dry_run: bool = False) -> None:
        if self.get_task_by_kind("compost_cleanup"):
            return
        self.create_task(
            name="Daily compost cleanup",
            description="Automatically clean .compost entries older than retention window",
            schedule="daily",
            priority=6,
            need=5,
            resource_cost=1,
            requires_network=False,
            kind="compost_cleanup",
            payload={"days": days, "dry_run": dry_run},
        )

    def get_task_by_kind(self, kind: str) -> Optional[Dict[str, Any]]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE kind = ? LIMIT 1",
                    (kind,),
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error:
            return None

    def get_stats(self) -> Dict[str, Any]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT state, COUNT(*) as count FROM tasks GROUP BY state"
                )
                task_stats = {row[0]: row[1] for row in cursor.fetchall()}
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM task_queue WHERE state = 'pending'"
                )
                pending_count = cursor.fetchone()[0]
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM task_runs WHERE result = 'success' AND completed_at > datetime('now', '-1 day')"
                )
                successful_today = cursor.fetchone()[0]
                return {
                    "tasks": task_stats,
                    "pending_queue": pending_count,
                    "successful_today": successful_today,
                }
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Stats error: {exc}")
            return {}
