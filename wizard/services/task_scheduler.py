"""
Task Scheduler Service - Organic Cron Model (Wizard)
"""

import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

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
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] DB init error: {exc}")

    def create_task(
        self, name: str, description: str = "", schedule: str = "daily"
    ) -> Dict[str, Any]:
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO tasks (id, name, description, schedule, state)
                    VALUES (?, ?, ?, ?, ?)""",
                    (task_id, name, description, schedule, "plant"),
                )
                conn.commit()
            return {
                "id": task_id,
                "name": name,
                "description": description,
                "schedule": schedule,
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
                return dict(row) if row else None
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
                conn.execute(
                    """INSERT INTO task_runs (id, task_id, state) VALUES (?, ?, ?)""",
                    (run_id, task_id, "sprout"),
                )
                conn.execute(
                    """INSERT INTO task_queue (task_id, run_id, state, scheduled_for) VALUES (?, ?, ?, ?)""",
                    (task_id, run_id, "pending", scheduled_for),
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
                    SELECT q.*, t.name, t.schedule FROM task_queue q
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
