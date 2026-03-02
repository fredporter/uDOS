from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from wizard.services.store.base import WizardStore


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SQLiteWizardStore(WizardStore):
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS scheduler_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    schedule TEXT DEFAULT 'daily',
                    state TEXT DEFAULT 'plant',
                    provider TEXT,
                    enabled INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 5,
                    need INTEGER DEFAULT 5,
                    mission TEXT,
                    objective TEXT,
                    resource_cost INTEGER DEFAULT 1,
                    requires_network INTEGER DEFAULT 0,
                    kind TEXT,
                    payload TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS task_runs (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    result TEXT,
                    output TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS task_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    state TEXT NOT NULL,
                    scheduled_for TEXT NOT NULL,
                    processed_at TEXT,
                    created_at TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    need INTEGER DEFAULT 5,
                    resource_cost INTEGER DEFAULT 1,
                    requires_network INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS launch_sessions (
                    session_id TEXT PRIMARY KEY,
                    target TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    launcher TEXT,
                    workspace TEXT,
                    profile_id TEXT,
                    auth_json TEXT DEFAULT '{}',
                    state TEXT NOT NULL,
                    payload_json TEXT DEFAULT '{}',
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS monitoring_alerts (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    service TEXT,
                    metadata_json TEXT DEFAULT '{}',
                    acknowledged INTEGER DEFAULT 0,
                    resolved INTEGER DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS monitoring_audit (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    service TEXT NOT NULL,
                    user_name TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    duration_ms REAL,
                    metadata_json TEXT DEFAULT '{}',
                    error TEXT
                );
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    sticky INTEGER NOT NULL DEFAULT 0,
                    action_count INTEGER DEFAULT 0,
                    dismissed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS operator_accounts (
                    subject TEXT PRIMARY KEY,
                    email TEXT,
                    display_name TEXT,
                    role TEXT NOT NULL DEFAULT 'operator',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )

    def _json_dump(self, value: Any) -> str:
        return json.dumps(value or {})

    def _json_load(self, value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    def get_scheduler_settings(self) -> dict[str, Any]:
        defaults = {"max_tasks_per_tick": 2, "tick_seconds": 60, "allow_network": True}
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM scheduler_settings").fetchall()
        for row in rows:
            defaults[row["key"]] = self._json_load(row["value"])
        return defaults

    def update_scheduler_settings(self, updates: dict[str, Any]) -> dict[str, Any]:
        settings = self.get_scheduler_settings()
        settings.update({k: v for k, v in updates.items() if v is not None})
        with self._connect() as conn:
            for key, value in settings.items():
                conn.execute(
                    "INSERT OR REPLACE INTO scheduler_settings (key, value) VALUES (?, ?)",
                    (key, self._json_dump(value)),
                )
        return settings

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        task_id = payload.get("id") or f"task_{uuid.uuid4().hex[:12]}"
        now = _utc_now()
        record = {
            "id": task_id,
            "name": payload["name"],
            "description": payload.get("description", ""),
            "schedule": payload.get("schedule", "daily"),
            "state": payload.get("state", "plant"),
            "provider": payload.get("provider"),
            "enabled": 1 if payload.get("enabled", True) else 0,
            "priority": int(payload.get("priority", 5)),
            "need": int(payload.get("need", 5)),
            "mission": payload.get("mission"),
            "objective": payload.get("objective"),
            "resource_cost": int(payload.get("resource_cost", 1)),
            "requires_network": 1 if payload.get("requires_network", False) else 0,
            "kind": payload.get("kind"),
            "payload": payload.get("payload") or {},
            "created_at": payload.get("created_at", now),
            "updated_at": now,
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    id, name, description, schedule, state, provider, enabled, priority, need,
                    mission, objective, resource_cost, requires_network, kind, payload,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record["name"],
                    record["description"],
                    record["schedule"],
                    record["state"],
                    record["provider"],
                    record["enabled"],
                    record["priority"],
                    record["need"],
                    record["mission"],
                    record["objective"],
                    record["resource_cost"],
                    record["requires_network"],
                    record["kind"],
                    self._json_dump(record["payload"]),
                    record["created_at"],
                    record["updated_at"],
                ),
            )
        return self.get_task(task_id) or record

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["payload"] = self._json_load(data.get("payload"))
        data["enabled"] = bool(data.get("enabled"))
        data["requires_network"] = bool(data.get("requires_network"))
        return data

    def list_tasks(self, *, state: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if state:
                rows = conn.execute("SELECT * FROM tasks WHERE state = ? LIMIT ?", (state, limit)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM tasks LIMIT ?", (limit,)).fetchall()
        return [self.get_task(row["id"]) for row in rows if row]

    def get_task_by_kind(self, kind: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT id FROM tasks WHERE kind = ? LIMIT 1", (kind,)).fetchone()
        return self.get_task(row["id"]) if row else None

    def schedule_task(self, task_id: str, scheduled_for: datetime) -> dict[str, Any]:
        scheduled_iso = scheduled_for.isoformat()
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        with self._connect() as conn:
            task = conn.execute(
                "SELECT priority, need, resource_cost, requires_network FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
            dup = conn.execute(
                "SELECT run_id FROM task_queue WHERE task_id = ? AND state IN ('pending', 'processing')",
                (task_id,),
            ).fetchone()
            if dup:
                return {"task_id": task_id, "run_id": dup["run_id"], "state": "pending", "scheduled_for": scheduled_iso}
            if not task:
                raise KeyError(task_id)
            conn.execute(
                "INSERT INTO task_runs (id, task_id, state, created_at) VALUES (?, ?, ?, ?)",
                (run_id, task_id, "sprout", _utc_now()),
            )
            conn.execute(
                """
                INSERT INTO task_queue (
                    task_id, run_id, state, scheduled_for, processed_at, created_at,
                    priority, need, resource_cost, requires_network
                ) VALUES (?, ?, 'pending', ?, NULL, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    run_id,
                    scheduled_iso,
                    _utc_now(),
                    task["priority"],
                    task["need"],
                    task["resource_cost"],
                    task["requires_network"],
                ),
            )
            conn.execute(
                "UPDATE tasks SET state = 'sprout', updated_at = ? WHERE id = ?",
                (_utc_now(), task_id),
            )
        return {"task_id": task_id, "run_id": run_id, "state": "pending", "scheduled_for": scheduled_iso}

    def _queue_rows(self, where_sql: str = "", params: tuple[Any, ...] = (), *, limit: int = 50) -> list[dict[str, Any]]:
        sql = f"""
            SELECT q.*, t.name, t.schedule, t.priority, t.need, t.mission, t.objective,
                   t.resource_cost, t.requires_network, t.kind, t.payload
            FROM task_queue q
            JOIN tasks t ON q.task_id = t.id
            {where_sql}
            ORDER BY q.scheduled_for ASC
            LIMIT ?
        """
        with self._connect() as conn:
            rows = conn.execute(sql, (*params, limit)).fetchall()
        data = []
        for row in rows:
            item = dict(row)
            item["payload"] = self._json_load(item.get("payload"))
            item["requires_network"] = bool(item.get("requires_network"))
            data.append(item)
        return data

    def get_pending_queue(self, *, limit: int = 10) -> list[dict[str, Any]]:
        return self._queue_rows(
            "WHERE q.state = 'pending' AND q.scheduled_for <= ?",
            (_utc_now(),),
            limit=limit,
        )

    def get_scheduled_queue(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._queue_rows(limit=limit)

    def claim_due_queue_items(self, *, limit: int = 10) -> list[dict[str, Any]]:
        claimed: list[dict[str, Any]] = []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT q.id
                FROM task_queue q
                WHERE q.state = 'pending' AND q.scheduled_for <= ?
                ORDER BY q.scheduled_for ASC
                LIMIT ?
                """,
                (_utc_now(), limit),
            ).fetchall()
            for row in rows:
                updated = conn.execute(
                    "UPDATE task_queue SET state = 'processing', processed_at = ? WHERE id = ? AND state = 'pending'",
                    (_utc_now(), row["id"]),
                )
                if updated.rowcount:
                    claimed.append(self._queue_rows("WHERE q.id = ?", (row["id"],), limit=1)[0])
        return claimed

    def complete_task_run(self, run_id: str, *, result: str, output: str) -> bool:
        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                "UPDATE task_runs SET state = 'compost', result = ?, output = ?, completed_at = ? WHERE id = ?",
                (result, output, now, run_id),
            )
            row = conn.execute("SELECT task_id FROM task_runs WHERE id = ?", (run_id,)).fetchone()
            conn.execute(
                "UPDATE task_queue SET state = 'completed', processed_at = ? WHERE run_id = ?",
                (now, run_id),
            )
            if row:
                conn.execute(
                    "UPDATE tasks SET state = 'harvest', updated_at = ? WHERE id = ?",
                    (now, row["task_id"]),
                )
        return True

    def get_execution_history(self, *, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM task_runs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_task_history(self, task_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM task_runs WHERE task_id = ? ORDER BY created_at DESC LIMIT ?",
                (task_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_last_run_time(self, task_id: str) -> datetime | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT completed_at FROM task_runs
                WHERE task_id = ? AND completed_at IS NOT NULL
                ORDER BY completed_at DESC LIMIT 1
                """,
                (task_id,),
            ).fetchone()
        if not row or not row["completed_at"]:
            return None
        return datetime.fromisoformat(str(row["completed_at"]).replace("Z", "+00:00"))

    def get_task_stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            task_rows = conn.execute("SELECT state, COUNT(*) as count FROM tasks GROUP BY state").fetchall()
            pending = conn.execute("SELECT COUNT(*) as count FROM task_queue WHERE state = 'pending'").fetchone()
            today = conn.execute(
                "SELECT COUNT(*) as count FROM task_runs WHERE result = 'success' AND completed_at >= ?",
                (datetime.now(timezone.utc).date().isoformat(),),
            ).fetchone()
        return {
            "tasks": {row["state"]: row["count"] for row in task_rows},
            "pending_queue": pending["count"] if pending else 0,
            "successful_today": today["count"] if today else 0,
        }

    def create_launch_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO launch_sessions (
                    session_id, target, mode, launcher, workspace, profile_id,
                    auth_json, state, payload_json, error, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["session_id"],
                    payload["target"],
                    payload["mode"],
                    payload.get("launcher"),
                    payload.get("workspace"),
                    payload.get("profile_id"),
                    self._json_dump(payload.get("auth", {})),
                    payload["state"],
                    self._json_dump(payload),
                    payload.get("error"),
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )
        return payload

    def update_launch_session(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE launch_sessions
                SET target = ?, mode = ?, launcher = ?, workspace = ?, profile_id = ?,
                    auth_json = ?, state = ?, payload_json = ?, error = ?, updated_at = ?
                WHERE session_id = ?
                """,
                (
                    payload["target"],
                    payload["mode"],
                    payload.get("launcher"),
                    payload.get("workspace"),
                    payload.get("profile_id"),
                    self._json_dump(payload.get("auth", {})),
                    payload["state"],
                    self._json_dump(payload),
                    payload.get("error"),
                    payload["updated_at"],
                    session_id,
                ),
            )
        return payload

    def get_launch_session(self, session_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload_json FROM launch_sessions WHERE session_id = ?", (session_id,)).fetchone()
        if not row:
            raise FileNotFoundError(f"Launch session not found: {session_id}")
        return self._json_load(row["payload_json"])

    def list_launch_sessions(self, *, target: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if target:
            sql = "SELECT payload_json FROM launch_sessions WHERE lower(target) = lower(?) ORDER BY updated_at DESC LIMIT ?"
            params = (target, limit)
        else:
            sql = "SELECT payload_json FROM launch_sessions ORDER BY updated_at DESC LIMIT ?"
            params = (limit,)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [self._json_load(row["payload_json"]) for row in rows]

    def list_alerts(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM monitoring_alerts ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        alerts = []
        for row in rows:
            item = dict(row)
            item["metadata"] = self._json_load(item.pop("metadata_json", "{}"))
            item["acknowledged"] = bool(item.get("acknowledged"))
            item["resolved"] = bool(item.get("resolved"))
            alerts.append(item)
        return alerts

    def upsert_alert(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO monitoring_alerts (
                    id, type, severity, message, timestamp, service, metadata_json, acknowledged, resolved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["id"],
                    payload["type"],
                    payload["severity"],
                    payload["message"],
                    payload["timestamp"],
                    payload.get("service"),
                    self._json_dump(payload.get("metadata")),
                    1 if payload.get("acknowledged") else 0,
                    1 if payload.get("resolved") else 0,
                ),
            )
        return payload

    def list_audit_entries(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM monitoring_audit ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()
        entries = []
        for row in rows:
            item = dict(row)
            item["metadata"] = self._json_load(item.pop("metadata_json", "{}"))
            item["user"] = item.pop("user_name")
            item["success"] = bool(item.get("success"))
            entries.append(item)
        return entries

    def append_audit_entry(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO monitoring_audit (
                    id, timestamp, operation, service, user_name, success, duration_ms, metadata_json, error
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["id"],
                    payload["timestamp"],
                    payload["operation"],
                    payload["service"],
                    payload["user"],
                    1 if payload.get("success", True) else 0,
                    payload.get("duration_ms"),
                    self._json_dump(payload.get("metadata")),
                    payload.get("error"),
                ),
            )
        return payload

    def save_notification(self, payload: dict[str, Any]) -> str:
        notification_id = payload.get("id") or f"toast-{uuid.uuid4().hex[:12]}"
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO notifications (
                    id, type, title, message, timestamp, duration_ms, sticky, action_count, dismissed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    notification_id,
                    payload["type"],
                    payload.get("title"),
                    payload["message"],
                    payload["timestamp"],
                    int(payload.get("duration_ms", 5000)),
                    1 if payload.get("sticky") else 0,
                    int(payload.get("action_count", 0)),
                    payload.get("dismissed_at"),
                ),
            )
        return notification_id

    def get_notifications(self, *, limit: int = 20, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS count FROM notifications").fetchone()["count"]
            rows = conn.execute(
                "SELECT * FROM notifications ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return ([dict(row) for row in rows], total)

    def search_notifications(
        self,
        *,
        query: str | None = None,
        type_filter: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM notifications WHERE 1=1"
        params: list[Any] = []
        if query:
            sql += " AND (title LIKE ? OR message LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        if type_filter:
            sql += " AND type = ?"
            params.append(type_filter)
        if start_date:
            sql += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND timestamp <= ?"
            params.append(end_date)
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    def delete_notification(self, notification_id: str) -> bool:
        with self._connect() as conn:
            conn.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
        return True

    def clear_old_notifications(self, *, cutoff_iso: str) -> int:
        with self._connect() as conn:
            result = conn.execute("DELETE FROM notifications WHERE timestamp < ?", (cutoff_iso,))
        return result.rowcount

    def get_notification_stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS count FROM notifications").fetchone()["count"]
            by_type = conn.execute("SELECT type, COUNT(*) AS count FROM notifications GROUP BY type").fetchall()
        return {"total": total, "by_type": {row["type"]: row["count"] for row in by_type}}

    def get_operator_profile(self, subject: str, email: str | None = None) -> dict[str, Any]:
        now = _utc_now()
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM operator_accounts WHERE subject = ?", (subject,)).fetchone()
            if not row:
                conn.execute(
                    """
                    INSERT INTO operator_accounts (subject, email, display_name, role, created_at, updated_at)
                    VALUES (?, ?, ?, 'operator', ?, ?)
                    """,
                    (subject, email, email or subject, now, now),
                )
                row = conn.execute("SELECT * FROM operator_accounts WHERE subject = ?", (subject,)).fetchone()
            elif email and row["email"] != email:
                conn.execute(
                    "UPDATE operator_accounts SET email = ?, updated_at = ? WHERE subject = ?",
                    (email, now, subject),
                )
                row = conn.execute("SELECT * FROM operator_accounts WHERE subject = ?", (subject,)).fetchone()
        return dict(row)

    def set_operator_role(self, subject: str, role: str) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                "UPDATE operator_accounts SET role = ?, updated_at = ? WHERE subject = ?",
                (role, _utc_now(), subject),
            )
            row = conn.execute("SELECT * FROM operator_accounts WHERE subject = ?", (subject,)).fetchone()
        if not row:
            raise KeyError(subject)
        return dict(row)
