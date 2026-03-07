from __future__ import annotations

import json
import sqlite3

from core.services.background_service_manager import WizardProcessManager


def test_scheduler_status_reads_heartbeat_from_ops_db(tmp_path):
    db_path = tmp_path / "memory" / "wizard" / "ops.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE scheduler_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO scheduler_settings (key, value) VALUES (?, ?)",
            (
                "automation_heartbeat:run_due_tasks",
                json.dumps(
                    {
                        "last_success_at": "2099-01-01T00:00:00Z",
                        "last_status": "success",
                    }
                ),
            ),
        )
        conn.commit()

    manager = WizardProcessManager(repo_root=tmp_path)
    status = manager._scheduler_status()

    assert status["healthy"] is True
    assert status["run_due_tasks"]["overdue"] is False
