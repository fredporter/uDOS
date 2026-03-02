from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from wizard.services.deploy_mode import require_managed_env
from wizard.services.store.base import WizardStore

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None
    dict_row = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class PostgresWizardStore(WizardStore):
    def __init__(self, dsn: str | None = None):
        if psycopg is None:
            raise RuntimeError("psycopg is required for managed Wizard store support")
        self.dsn = dsn or require_managed_env("SUPABASE_DB_DSN")

    def _connect(self):
        return psycopg.connect(self.dsn, row_factory=dict_row)

    def get_scheduler_settings(self) -> dict[str, Any]:
        defaults = {"max_tasks_per_tick": 2, "tick_seconds": 60, "allow_network": True}
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT key, value FROM scheduler_settings")
            for row in cur.fetchall():
                defaults[row["key"]] = row["value"]
        return defaults

    def update_scheduler_settings(self, updates: dict[str, Any]) -> dict[str, Any]:
        settings = self.get_scheduler_settings()
        settings.update({k: v for k, v in updates.items() if v is not None})
        with self._connect() as conn, conn.cursor() as cur:
            for key, value in settings.items():
                cur.execute(
                    """
                    INSERT INTO scheduler_settings (key, value)
                    VALUES (%s, %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """,
                    (key, json.dumps(value)),
                )
        return settings

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        task_id = payload.get("id") or f"task_{uuid.uuid4().hex[:12]}"
        now = _utc_now()
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (
                    id, name, description, schedule, state, provider, enabled, priority, need,
                    mission, objective, resource_cost, requires_network, kind, payload,
                    created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    task_id,
                    payload["name"],
                    payload.get("description", ""),
                    payload.get("schedule", "daily"),
                    payload.get("state", "plant"),
                    payload.get("provider"),
                    bool(payload.get("enabled", True)),
                    int(payload.get("priority", 5)),
                    int(payload.get("need", 5)),
                    payload.get("mission"),
                    payload.get("objective"),
                    int(payload.get("resource_cost", 1)),
                    bool(payload.get("requires_network", False)),
                    payload.get("kind"),
                    json.dumps(payload.get("payload") or {}),
                    payload.get("created_at", now),
                    now,
                ),
            )
        return self.get_task(task_id) or {"id": task_id, **payload}

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            row = cur.fetchone()
        if not row:
            return None
        row["payload"] = row.get("payload") or {}
        return row

    def list_tasks(self, *, state: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        sql = "SELECT * FROM tasks"
        params: tuple[Any, ...] = ()
        if state:
            sql += " WHERE state = %s"
            params = (state,)
        sql += " LIMIT %s"
        params = (*params, limit)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return rows

    def get_task_by_kind(self, kind: str) -> dict[str, Any] | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE kind = %s LIMIT 1", (kind,))
            return cur.fetchone()

    def schedule_task(self, task_id: str, scheduled_for: datetime) -> dict[str, Any]:
        scheduled_iso = scheduled_for.isoformat()
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT priority, need, resource_cost, requires_network FROM tasks WHERE id = %s",
                (task_id,),
            )
            task = cur.fetchone()
            cur.execute(
                "SELECT run_id FROM task_queue WHERE task_id = %s AND state IN ('pending', 'processing') LIMIT 1",
                (task_id,),
            )
            dup = cur.fetchone()
            if dup:
                return {"task_id": task_id, "run_id": dup["run_id"], "state": "pending", "scheduled_for": scheduled_iso}
            if not task:
                raise KeyError(task_id)
            cur.execute(
                "INSERT INTO task_runs (id, task_id, state, created_at) VALUES (%s, %s, %s, %s)",
                (run_id, task_id, "sprout", _utc_now()),
            )
            cur.execute(
                """
                INSERT INTO task_queue (
                    task_id, run_id, state, scheduled_for, created_at,
                    priority, need, resource_cost, requires_network
                ) VALUES (%s, %s, 'pending', %s, %s, %s, %s, %s, %s)
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
            cur.execute("UPDATE tasks SET state = 'sprout', updated_at = %s WHERE id = %s", (_utc_now(), task_id))
        return {"task_id": task_id, "run_id": run_id, "state": "pending", "scheduled_for": scheduled_iso}

    def _queue_rows(self, where_sql: str = "", params: tuple[Any, ...] = (), *, limit: int = 50) -> list[dict[str, Any]]:
        sql = f"""
            SELECT q.*, t.name, t.schedule, t.priority, t.need, t.mission, t.objective,
                   t.resource_cost, t.requires_network, t.kind, t.payload
            FROM task_queue q
            JOIN tasks t ON q.task_id = t.id
            {where_sql}
            ORDER BY q.scheduled_for ASC
            LIMIT %s
        """
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql, (*params, limit))
            return cur.fetchall()

    def get_pending_queue(self, *, limit: int = 10) -> list[dict[str, Any]]:
        return self._queue_rows("WHERE q.state = 'pending' AND q.scheduled_for <= %s", (_utc_now(),), limit=limit)

    def get_scheduled_queue(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._queue_rows(limit=limit)

    def claim_due_queue_items(self, *, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                WITH claimed AS (
                    SELECT id
                    FROM task_queue
                    WHERE state = 'pending' AND scheduled_for <= %s
                    ORDER BY scheduled_for ASC
                    LIMIT %s
                    FOR UPDATE SKIP LOCKED
                )
                UPDATE task_queue q
                SET state = 'processing', processed_at = %s
                FROM claimed
                WHERE q.id = claimed.id
                RETURNING q.id
                """,
                (_utc_now(), limit, _utc_now()),
            )
            rows = cur.fetchall()
        claimed = []
        for row in rows:
            claimed.extend(self._queue_rows("WHERE q.id = %s", (row["id"],), limit=1))
        return claimed

    def complete_task_run(self, run_id: str, *, result: str, output: str) -> bool:
        now = _utc_now()
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE task_runs SET state = 'compost', result = %s, output = %s, completed_at = %s WHERE id = %s",
                (result, output, now, run_id),
            )
            cur.execute("SELECT task_id FROM task_runs WHERE id = %s", (run_id,))
            row = cur.fetchone()
            cur.execute("UPDATE task_queue SET state = 'completed', processed_at = %s WHERE run_id = %s", (now, run_id))
            if row:
                cur.execute("UPDATE tasks SET state = 'harvest', updated_at = %s WHERE id = %s", (now, row["task_id"]))
        return True

    def get_execution_history(self, *, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM task_runs ORDER BY created_at DESC LIMIT %s", (limit,))
            return cur.fetchall()

    def get_task_history(self, task_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM task_runs WHERE task_id = %s ORDER BY created_at DESC LIMIT %s", (task_id, limit))
            return cur.fetchall()

    def get_last_run_time(self, task_id: str) -> datetime | None:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT completed_at FROM task_runs WHERE task_id = %s AND completed_at IS NOT NULL ORDER BY completed_at DESC LIMIT 1",
                (task_id,),
            )
            row = cur.fetchone()
        if not row or not row["completed_at"]:
            return None
        value = row["completed_at"]
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    def get_task_stats(self) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT state, COUNT(*) AS count FROM tasks GROUP BY state")
            task_rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) AS count FROM task_queue WHERE state = 'pending'")
            pending = cur.fetchone()
            cur.execute("SELECT COUNT(*) AS count FROM task_runs WHERE result = 'success' AND completed_at >= %s", (datetime.now(timezone.utc).date().isoformat(),))
            today = cur.fetchone()
        return {
            "tasks": {row["state"]: row["count"] for row in task_rows},
            "pending_queue": pending["count"] if pending else 0,
            "successful_today": today["count"] if today else 0,
        }

    def create_launch_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO launch_sessions (
                    session_id, target, mode, launcher, workspace, profile_id,
                    auth_json, state, payload_json, error, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload["session_id"],
                    payload["target"],
                    payload["mode"],
                    payload.get("launcher"),
                    payload.get("workspace"),
                    payload.get("profile_id"),
                    json.dumps(payload.get("auth", {})),
                    payload["state"],
                    json.dumps(payload),
                    payload.get("error"),
                    payload["created_at"],
                    payload["updated_at"],
                ),
            )
        return payload

    def update_launch_session(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                UPDATE launch_sessions
                SET target = %s, mode = %s, launcher = %s, workspace = %s, profile_id = %s,
                    auth_json = %s, state = %s, payload_json = %s, error = %s, updated_at = %s
                WHERE session_id = %s
                """,
                (
                    payload["target"],
                    payload["mode"],
                    payload.get("launcher"),
                    payload.get("workspace"),
                    payload.get("profile_id"),
                    json.dumps(payload.get("auth", {})),
                    payload["state"],
                    json.dumps(payload),
                    payload.get("error"),
                    payload["updated_at"],
                    session_id,
                ),
            )
        return payload

    def get_launch_session(self, session_id: str) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT payload_json FROM launch_sessions WHERE session_id = %s", (session_id,))
            row = cur.fetchone()
        if not row:
            raise FileNotFoundError(f"Launch session not found: {session_id}")
        return row["payload_json"]

    def list_launch_sessions(self, *, target: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        sql = "SELECT payload_json FROM launch_sessions"
        params: tuple[Any, ...] = ()
        if target:
            sql += " WHERE lower(target) = lower(%s)"
            params = (target,)
        sql += " ORDER BY updated_at DESC LIMIT %s"
        params = (*params, limit)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return [row["payload_json"] for row in rows]

    def list_alerts(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM monitoring_alerts ORDER BY timestamp DESC LIMIT %s", (limit,))
            return cur.fetchall()

    def upsert_alert(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO monitoring_alerts (
                    id, type, severity, message, timestamp, service, metadata, acknowledged, resolved
                ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    acknowledged = EXCLUDED.acknowledged,
                    resolved = EXCLUDED.resolved,
                    metadata = EXCLUDED.metadata,
                    message = EXCLUDED.message
                """,
                (
                    payload["id"],
                    payload["type"],
                    payload["severity"],
                    payload["message"],
                    payload["timestamp"],
                    payload.get("service"),
                    json.dumps(payload.get("metadata") or {}),
                    bool(payload.get("acknowledged")),
                    bool(payload.get("resolved")),
                ),
            )
        return payload

    def list_audit_entries(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM monitoring_audit ORDER BY timestamp DESC LIMIT %s", (limit,))
            return cur.fetchall()

    def append_audit_entry(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO monitoring_audit (
                    id, timestamp, operation, service, user_name, success, duration_ms, metadata, error
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    payload["id"],
                    payload["timestamp"],
                    payload["operation"],
                    payload["service"],
                    payload["user"],
                    bool(payload.get("success", True)),
                    payload.get("duration_ms"),
                    json.dumps(payload.get("metadata") or {}),
                    payload.get("error"),
                ),
            )
        return payload

    def save_notification(self, payload: dict[str, Any]) -> str:
        notification_id = payload.get("id") or f"toast-{uuid.uuid4().hex[:12]}"
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notifications (
                    id, type, title, message, timestamp, duration_ms, sticky, action_count, dismissed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    notification_id,
                    payload["type"],
                    payload.get("title"),
                    payload["message"],
                    payload["timestamp"],
                    int(payload.get("duration_ms", 5000)),
                    bool(payload.get("sticky")),
                    int(payload.get("action_count", 0)),
                    payload.get("dismissed_at"),
                ),
            )
        return notification_id

    def get_notifications(self, *, limit: int = 20, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM notifications")
            total = cur.fetchone()["count"]
            cur.execute("SELECT * FROM notifications ORDER BY timestamp DESC LIMIT %s OFFSET %s", (limit, offset))
            rows = cur.fetchall()
        return rows, total

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
            sql += " AND (coalesce(title, '') ILIKE %s OR message ILIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])
        if type_filter:
            sql += " AND type = %s"
            params.append(type_filter)
        if start_date:
            sql += " AND timestamp >= %s"
            params.append(start_date)
        if end_date:
            sql += " AND timestamp <= %s"
            params.append(end_date)
        sql += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    def delete_notification(self, notification_id: str) -> bool:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
        return True

    def clear_old_notifications(self, *, cutoff_iso: str) -> int:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM notifications WHERE timestamp < %s", (cutoff_iso,))
            return cur.rowcount

    def get_notification_stats(self) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM notifications")
            total = cur.fetchone()["count"]
            cur.execute("SELECT type, COUNT(*) AS count FROM notifications GROUP BY type")
            rows = cur.fetchall()
        return {"total": total, "by_type": {row["type"]: row["count"] for row in rows}}

    def get_operator_profile(self, subject: str, email: str | None = None) -> dict[str, Any]:
        now = _utc_now()
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT * FROM operator_accounts WHERE subject = %s", (subject,))
            row = cur.fetchone()
            if not row:
                cur.execute(
                    """
                    INSERT INTO operator_accounts (subject, email, display_name, role, created_at, updated_at)
                    VALUES (%s, %s, %s, 'operator', %s, %s)
                    RETURNING *
                    """,
                    (subject, email, email or subject, now, now),
                )
                row = cur.fetchone()
            elif email and row.get("email") != email:
                cur.execute(
                    "UPDATE operator_accounts SET email = %s, updated_at = %s WHERE subject = %s RETURNING *",
                    (email, now, subject),
                )
                row = cur.fetchone()
        return row

    def set_operator_role(self, subject: str, role: str) -> dict[str, Any]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE operator_accounts SET role = %s, updated_at = %s WHERE subject = %s RETURNING *",
                (role, _utc_now(), subject),
            )
            row = cur.fetchone()
        if not row:
            raise KeyError(subject)
        return row
