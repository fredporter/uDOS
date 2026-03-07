"""
Task Scheduler Service - Organic Cron Model (Wizard)
"""

import json
import socket
import logging
import sqlite3
import uuid
import hashlib
from datetime import UTC, datetime, timedelta, time
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.logging_api import get_logger
from wizard.services.deploy_mode import is_managed_mode
from wizard.services.path_utils import get_repo_root
from wizard.services.system_info_service import get_system_info_service
from wizard.services.store.base import WizardStore
from wizard.services.store import get_wizard_store
from core.services.maintenance_utils import compost_cleanup, run_housekeeping
from core.services.time_utils import parse_utc_datetime, utc_now, utc_now_iso
from core.workflows.scheduler import WorkflowScheduler
from wizard.services.repair_service import get_repair_service
from wizard.services.quota_tracker import APIProvider, get_quota_tracker
from wizard.services.workflow_manager import WorkflowManager

logger = get_logger("wizard.tasks")

WINDOW_SCHEDULES = {"off_peak", "weekday-evening", "business_hours", "weekend"}
DEFAULT_SETTINGS = {
    "max_tasks_per_tick": 2,
    "tick_seconds": 60,
    "allow_network": True,
    "off_peak_start_hour": 20,
    "off_peak_end_hour": 6,
    "api_budget_daily": 10,
    "api_budget_used": 0,
    "api_budget_day": "",
    "defer_alert_threshold": 3,
    "backoff_alert_minutes": 120,
    "auto_retry_deferred_reasons": ["network_unavailable"],
    "auto_retry_deferred_limit": 10,
    "maintenance_retry_dry_run": False,
    "auto_retry_deferred_policy": {
        "network_unavailable": {"enabled": True, "limit": 10, "dry_run": False, "window": ""},
    },
    "backoff_policy": {
        "waiting_for_window": {"base_minutes": 15, "max_minutes": 360},
        "resource_pressure": {"base_minutes": 15, "max_minutes": 240},
        "network_unavailable": {"base_minutes": 10, "max_minutes": 120},
        "api_budget_exhausted": {"base_minutes": 60, "max_minutes": 1440},
        "waiting_for_workflow_phase": {"base_minutes": 30, "max_minutes": 360},
        "waiting_for_workflow_state": {"base_minutes": 60, "max_minutes": 720},
    },
}


def _serialize_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    return _coerce_utc(value).isoformat()


def _coerce_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class TaskScheduler:
    """Manage task scheduling and execution with organic cron model."""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        *,
        store: WizardStore | None = None,
    ):
        repo_root = get_repo_root()
        default_db = repo_root / "memory" / "wizard" / "ops.db"
        self.db_path = Path(db_path or default_db)
        self._managed = is_managed_mode()
        self.store = store or get_wizard_store(
            None if self._managed else self.db_path
        )
        self.workflow_scheduler = WorkflowScheduler(Path(repo_root))
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._managed:
            self._init_db()
        logger.info(f"[WIZ] Task scheduler using {self.db_path}")

    def _init_db(self) -> None:
        schema_path = Path(__file__).parent / "schemas" / "task_schema.sql"
        try:
            with sqlite3.connect(self.db_path) as conn:
                if not schema_path.exists():
                    raise FileNotFoundError(f"Task schema file missing: {schema_path}")
                conn.executescript(schema_path.read_text(encoding="utf-8"))
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
        self._add_column(conn, "task_queue", queue_columns, "defer_reason", "TEXT")
        self._add_column(conn, "task_queue", queue_columns, "defer_count", "INTEGER DEFAULT 0")
        self._add_column(conn, "task_queue", queue_columns, "backoff_seconds", "INTEGER DEFAULT 0")
        self._add_column(conn, "task_queue", queue_columns, "last_deferred_at", "TEXT")

    def get_settings(self) -> Dict[str, Any]:
        if self._managed:
            return self._normalize_settings(self.store.get_scheduler_settings())
        defaults = dict(DEFAULT_SETTINGS)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT key, value FROM scheduler_settings")
                rows = {}
                for row in cursor.fetchall():
                    try:
                        key = row["key"]
                        value = row["value"]
                    except (TypeError, KeyError, IndexError):
                        # Fallback if row_factory is not honored for any reason.
                        key = row[0] if row else None
                        value = row[1] if row and len(row) > 1 else None
                    if key is None:
                        continue
                    rows[key] = value
            for key, value in rows.items():
                try:
                    defaults[key] = json.loads(value)
                except json.JSONDecodeError:
                    defaults[key] = value
        except sqlite3.Error:
            pass
        return self._normalize_settings(defaults)

    def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        settings = self.get_settings()
        settings.update({k: v for k, v in updates.items() if v is not None})
        settings = self._normalize_settings(settings)
        if self._managed:
            return self.store.update_scheduler_settings(settings)
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

    def _normalize_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(DEFAULT_SETTINGS)
        merged.update(settings or {})
        merged["max_tasks_per_tick"] = int(merged.get("max_tasks_per_tick", 2) or 2)
        merged["tick_seconds"] = int(merged.get("tick_seconds", 60) or 60)
        merged["allow_network"] = bool(merged.get("allow_network", True))
        start_hour = merged.get("off_peak_start_hour", 20)
        end_hour = merged.get("off_peak_end_hour", 6)
        merged["off_peak_start_hour"] = int(20 if start_hour is None else start_hour) % 24
        merged["off_peak_end_hour"] = int(6 if end_hour is None else end_hour) % 24
        merged["api_budget_daily"] = int(merged.get("api_budget_daily", 10) or 0)
        merged["api_budget_used"] = int(merged.get("api_budget_used", 0) or 0)
        merged["api_budget_day"] = str(merged.get("api_budget_day", "") or "")
        merged["defer_alert_threshold"] = int(merged.get("defer_alert_threshold", 3) or 0)
        merged["backoff_alert_minutes"] = int(merged.get("backoff_alert_minutes", 120) or 0)
        auto_retry_reasons = merged.get("auto_retry_deferred_reasons") or []
        if not isinstance(auto_retry_reasons, list):
            auto_retry_reasons = [str(auto_retry_reasons)]
        merged["auto_retry_deferred_reasons"] = [
            str(reason).strip()
            for reason in auto_retry_reasons
            if str(reason).strip()
        ]
        merged["auto_retry_deferred_limit"] = int(merged.get("auto_retry_deferred_limit", 10) or 0)
        merged["maintenance_retry_dry_run"] = bool(merged.get("maintenance_retry_dry_run", False))
        merged["auto_retry_deferred_policy"] = self._normalize_auto_retry_policy(
            merged.get("auto_retry_deferred_policy")
        )
        merged["backoff_policy"] = self._normalize_backoff_policy(merged.get("backoff_policy"))
        return merged

    def _normalize_auto_retry_policy(self, policy: Dict[str, Any] | None) -> Dict[str, Dict[str, Any]]:
        defaults = json.loads(json.dumps(DEFAULT_SETTINGS["auto_retry_deferred_policy"]))
        if not isinstance(policy, dict):
            return defaults
        normalized = defaults
        for reason, entry in policy.items():
            if not isinstance(reason, str) or not reason.strip():
                continue
            if not isinstance(entry, dict):
                continue
            normalized[reason.strip()] = {
                "enabled": bool(entry.get("enabled", True)),
                "limit": max(0, int(entry.get("limit", 10) or 0)),
                "dry_run": bool(entry.get("dry_run", False)),
                "window": str(entry.get("window", "") or "").strip(),
            }
        return normalized

    def _normalize_backoff_policy(self, policy: Dict[str, Any] | None) -> Dict[str, Dict[str, int]]:
        defaults = json.loads(json.dumps(DEFAULT_SETTINGS["backoff_policy"]))
        if not isinstance(policy, dict):
            return defaults
        normalized = defaults
        for reason, entry in policy.items():
            if reason not in normalized or not isinstance(entry, dict):
                continue
            base_minutes = int(entry.get("base_minutes", normalized[reason]["base_minutes"]) or 1)
            max_minutes = int(entry.get("max_minutes", normalized[reason]["max_minutes"]) or base_minutes)
            normalized[reason] = {
                "base_minutes": max(1, base_minutes),
                "max_minutes": max(base_minutes, max_minutes),
            }
        return normalized

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
        if self._managed:
            return self.store.create_task(
                {
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
                }
            )
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        try:
            now_iso = utc_now_iso()
            with sqlite3.connect(self.db_path) as conn:
                self._ensure_columns(conn)
                conn.execute(
                    """INSERT INTO tasks (
                        id, name, description, schedule, state, provider, enabled,
                        priority, need, mission, objective, resource_cost, requires_network,
                        kind, payload, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                        now_iso,
                        now_iso,
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
                "created_at": now_iso,
            }
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Create task error: {exc}")
            return {"error": str(exc)}

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        if self._managed:
            return self.store.get_task(task_id)
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
        if self._managed:
            return self.store.list_tasks(state=state, limit=limit)
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
        scheduled_for = _coerce_utc(scheduled_for or utc_now())
        if self._managed:
            return self.store.schedule_task(task_id, scheduled_for)
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        try:
            now_iso = utc_now_iso()
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
                        "run_id": dup_check[0],
                        "state": "pending",
                        "scheduled_for": scheduled_for.isoformat(),
                        "note": "duplicate avoided",
                    }
                conn.execute(
                    """INSERT INTO task_runs (id, task_id, state, created_at) VALUES (?, ?, ?, ?)""",
                    (run_id, task_id, "sprout", now_iso),
                )
                conn.execute(
                    """INSERT INTO task_queue
                    (task_id, run_id, state, scheduled_for, created_at, priority, need, resource_cost, requires_network)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        task_id,
                        run_id,
                        "pending",
                        _serialize_dt(scheduled_for),
                        now_iso,
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
        if self._managed:
            return self.store.get_pending_queue(limit=limit)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT q.*, t.name, t.schedule, t.provider, t.priority, t.need, t.mission,
                           t.objective, t.resource_cost, t.requires_network,
                           t.kind, t.payload
                    FROM task_queue q
                    JOIN tasks t ON q.task_id = t.id
                    WHERE q.state = 'pending' AND q.scheduled_for <= ?
                    LIMIT ?
                    """,
                    (_serialize_dt(utc_now()), limit),
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Pending queue error: {exc}")
            return []

    def get_scheduled_queue(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self._managed:
            return self.store.get_scheduled_queue(limit=limit)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT q.*, t.name, t.schedule, t.provider, t.priority, t.need, t.mission,
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
        if self._managed:
            return False
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
        if self._managed:
            return self.store.complete_task_run(run_id, result=result, output=output)
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

    def release_queue_item(
        self,
        queue_id: int,
        scheduled_for: datetime | None = None,
        reason: str | None = None,
        backoff_seconds: int | None = None,
    ) -> bool:
        if self._managed:
            return self.store.release_queue_item(
                queue_id,
                scheduled_for=scheduled_for,
                reason=reason,
                backoff_seconds=backoff_seconds,
            )
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE task_queue
                    SET state = 'pending',
                        processed_at = NULL,
                        scheduled_for = COALESCE(?, scheduled_for),
                        defer_reason = COALESCE(?, defer_reason),
                        defer_count = COALESCE(defer_count, 0) + 1,
                        backoff_seconds = COALESCE(?, backoff_seconds),
                        last_deferred_at = ?
                    WHERE id = ?
                    """,
                    (
                        _serialize_dt(scheduled_for),
                        reason,
                        backoff_seconds,
                        _serialize_dt(utc_now()),
                        queue_id,
                    ),
                )
                conn.commit()
            return True
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Release queue item error: {exc}")
            return False

    def retry_queue_item(self, queue_id: int) -> Dict[str, Any] | None:
        if self._managed:
            return self.store.retry_queue_item(queue_id)
        now = _serialize_dt(utc_now())
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                result = conn.execute(
                    """
                    UPDATE task_queue
                    SET state = 'pending',
                        processed_at = NULL,
                        scheduled_for = ?,
                        defer_reason = NULL,
                        defer_count = 0,
                        backoff_seconds = 0,
                        last_deferred_at = NULL
                    WHERE id = ?
                    """,
                    (now, queue_id),
                )
                conn.commit()
                if not result.rowcount:
                    return None
                cursor = conn.execute(
                    """
                    SELECT q.*, t.name, t.schedule, t.provider, t.priority, t.need, t.mission,
                           t.objective, t.resource_cost, t.requires_network,
                           t.kind, t.payload
                    FROM task_queue q
                    JOIN tasks t ON q.task_id = t.id
                    WHERE q.id = ?
                    LIMIT 1
                    """,
                    (queue_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                data = dict(row)
                if isinstance(data.get("payload"), str):
                    try:
                        data["payload"] = json.loads(data["payload"])
                    except json.JSONDecodeError:
                        pass
                return data
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Retry queue item error: {exc}")
            return None

    def retry_deferred_items(
        self,
        *,
        reason: str | None = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        items = self.get_scheduled_queue(limit=max(1, limit * 4))
        retried: List[Dict[str, Any]] = []
        for item in items:
            if not item.get("defer_reason"):
                continue
            if reason and item.get("defer_reason") != reason:
                continue
            queue_id = item.get("id")
            if queue_id is None:
                continue
            refreshed = self.retry_queue_item(int(queue_id))
            if refreshed:
                retried.append(refreshed)
            if len(retried) >= limit:
                break
        return retried

    def list_deferred_items(
        self,
        *,
        reason: str | None = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        deferred: List[Dict[str, Any]] = []
        for item in self.get_scheduled_queue(limit=max(1, limit * 4)):
            item_reason = str(item.get("defer_reason") or "").strip()
            if not item_reason:
                continue
            if reason and item_reason != reason:
                continue
            deferred.append(item)
            if len(deferred) >= limit:
                break
        return deferred

    def get_defer_reason_counts(self, limit: int = 200) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for item in self.get_scheduled_queue(limit=limit):
            reason = str(item.get("defer_reason") or "").strip()
            if not reason:
                continue
            counts[reason] = counts.get(reason, 0) + 1
        return counts

    def _defer_base_seconds(self, reason: str, settings: Dict[str, Any]) -> int:
        policy = settings.get("backoff_policy", {})
        entry = policy.get(reason, {})
        return int(entry.get("base_minutes", 15) or 15) * 60

    def _defer_max_seconds(self, reason: str, settings: Dict[str, Any]) -> int:
        policy = settings.get("backoff_policy", {})
        entry = policy.get(reason, {})
        return int(entry.get("max_minutes", 240) or 240) * 60

    def _defer_jitter_seconds(self, item: Dict[str, Any], reason: str, ceiling: int = 300) -> int:
        seed = f"{item.get('task_id', '')}:{item.get('run_id', '')}:{reason}".encode("utf-8")
        digest = hashlib.sha256(seed).hexdigest()
        return int(digest[:8], 16) % max(1, ceiling + 1)

    def _compute_defer_backoff(self, item: Dict[str, Any], reason: str, settings: Dict[str, Any]) -> int:
        defer_count = int(item.get("defer_count") or 0)
        base = self._defer_base_seconds(reason, settings)
        maximum = self._defer_max_seconds(reason, settings)
        scaled = min(base * (2 ** defer_count), maximum)
        return min(maximum, scaled + self._defer_jitter_seconds(item, reason))

    def _defer_queue_item(
        self,
        item: Dict[str, Any],
        *,
        reason: str,
        now: datetime,
        settings: Dict[str, Any],
        preferred_time: datetime | None = None,
    ) -> bool:
        backoff_seconds = self._compute_defer_backoff(item, reason, settings)
        retry_at = now + timedelta(seconds=backoff_seconds)
        if preferred_time is not None:
            retry_at = max(retry_at, preferred_time)
        return self.release_queue_item(
            int(item["id"]),
            scheduled_for=retry_at,
            reason=reason,
            backoff_seconds=backoff_seconds,
        )

    def get_task_history(self, task_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        if self._managed:
            return self.store.get_task_history(task_id, limit=limit)
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
        if self._managed:
            return self.store.get_execution_history(limit=limit)
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
        scheduled = self.schedule_task(task_id, utc_now())
        if "error" in scheduled:
            return scheduled
        return {"scheduled": scheduled}

    def _task_window(self, task: Dict[str, Any]) -> str | None:
        payload = task.get("payload") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        for candidate in (payload.get("window"), task.get("schedule")):
            if isinstance(candidate, str) and candidate.strip():
                value = candidate.strip().lower()
                if value in WINDOW_SCHEDULES or ":" in value or "@" in value:
                    return value
        return None

    def _window_rule(self, window: str, settings: Dict[str, Any]) -> tuple[set[int] | None, time, time]:
        if window == "off_peak":
            return None, time(hour=settings["off_peak_start_hour"]), time(hour=settings["off_peak_end_hour"])
        if window == "weekday-evening":
            return {0, 1, 2, 3, 4}, time(hour=18), time(hour=23)
        if window == "business_hours":
            return {0, 1, 2, 3, 4}, time(hour=9), time(hour=17)
        if window == "weekend":
            return {5, 6}, time(hour=0), time(hour=23, minute=59)
        if "@" in window:
            days_part, hours_part = window.split("@", 1)
            weekdays = {
                "mon": 0,
                "tue": 1,
                "wed": 2,
                "thu": 3,
                "fri": 4,
                "sat": 5,
                "sun": 6,
            }
            allowed_days = {weekdays[token.strip()[:3]] for token in days_part.split(",") if token.strip()[:3] in weekdays}
            window = hours_part
            return allowed_days or None, *self._window_rule(window, settings)[1:]
        if "-" in window and ":" in window:
            start_raw, end_raw = window.split("-", 1)
            start_hour, start_minute = [int(part) for part in start_raw.split(":", 1)]
            end_hour, end_minute = [int(part) for part in end_raw.split(":", 1)]
            return None, time(hour=start_hour, minute=start_minute), time(hour=end_hour, minute=end_minute)
        return None, time(hour=0), time(hour=23, minute=59)

    def _within_window(self, task: Dict[str, Any], now: datetime, settings: Dict[str, Any]) -> bool:
        window = self._task_window(task)
        if not window:
            return True
        allowed_days, start_at, end_at = self._window_rule(window, settings)
        current_time = now.time()
        if allowed_days is not None and now.weekday() not in allowed_days:
            return False
        if start_at <= end_at:
            return start_at <= current_time <= end_at
        return current_time >= start_at or current_time <= end_at

    def _next_window_start(self, task: Dict[str, Any], now: datetime, settings: Dict[str, Any]) -> datetime:
        window = self._task_window(task)
        if not window:
            return now
        allowed_days, start_at, _end_at = self._window_rule(window, settings)
        for day_offset in range(0, 8):
            candidate_date = (now + timedelta(days=day_offset)).date()
            candidate = datetime.combine(candidate_date, start_at, tzinfo=UTC)
            if day_offset == 0 and candidate <= now:
                candidate += timedelta(days=1)
            if allowed_days is not None and candidate.weekday() not in allowed_days:
                continue
            return candidate
        return now + timedelta(hours=1)

    def _task_budget_units(self, task: Dict[str, Any]) -> int:
        payload = task.get("payload") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        return int(payload.get("budget_units") or task.get("resource_cost") or 1)

    def _task_estimated_tokens(self, task: Dict[str, Any]) -> int:
        payload = task.get("payload") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        if payload.get("estimated_tokens") is not None:
            return max(int(payload.get("estimated_tokens") or 0), 0)
        return self._task_budget_units(task) * 1000

    def _task_quota_provider(self, task: Dict[str, Any]) -> APIProvider | None:
        provider = str(task.get("provider") or "").strip().lower()
        mapping = {
            "openrouter": APIProvider.MISTRAL,
            "mistral": APIProvider.MISTRAL,
            "openai": APIProvider.OPENAI,
            "anthropic": APIProvider.ANTHROPIC,
            "gemini": APIProvider.GEMINI,
        }
        return mapping.get(provider)

    def _budget_state(self, settings: Dict[str, Any], now: datetime) -> Dict[str, Any]:
        today = now.date().isoformat()
        if settings.get("api_budget_day") != today:
            settings["api_budget_day"] = today
            settings["api_budget_used"] = 0
        return settings

    def _budget_allows(self, task: Dict[str, Any], settings: Dict[str, Any], now: datetime) -> bool:
        settings = self._budget_state(settings, now)
        if not (task.get("requires_network") or task.get("provider")):
            return True
        budget_daily = int(settings.get("api_budget_daily", 0) or 0)
        if budget_daily <= 0:
            return False
        within_scheduler_budget = (
            int(settings.get("api_budget_used", 0) or 0) + self._task_budget_units(task) <= budget_daily
        )
        if not within_scheduler_budget:
            return False
        quota_provider = self._task_quota_provider(task)
        if quota_provider is None:
            return True
        return get_quota_tracker().can_request(
            quota_provider,
            self._task_estimated_tokens(task),
        )

    def _record_budget_use(self, task: Dict[str, Any], settings: Dict[str, Any], now: datetime) -> Dict[str, Any]:
        settings = self._budget_state(settings, now)
        if task.get("requires_network") or task.get("provider"):
            settings["api_budget_used"] = int(settings.get("api_budget_used", 0) or 0) + self._task_budget_units(task)
            settings = self.update_settings(
                {
                    "api_budget_day": settings["api_budget_day"],
                    "api_budget_used": settings["api_budget_used"],
                }
            )
        return settings

    def _task_due(self, task: Dict[str, Any]) -> bool:
        schedule = (task.get("schedule") or "daily").lower()
        last_run = self._get_last_run_time(task["id"])
        now = utc_now()
        if schedule in WINDOW_SCHEDULES:
            schedule = "daily"
        if schedule in {"once", "one"}:
            return last_run is None
        if schedule in {"hourly", "hour"}:
            return last_run is None or (now - last_run) >= timedelta(hours=1)
        if schedule in {"weekly", "week"}:
            return last_run is None or (now - last_run) >= timedelta(days=7)
        return last_run is None or (now - last_run) >= timedelta(days=1)

    def _get_last_run_time(self, task_id: str) -> Optional[datetime]:
        if self._managed:
            return self.store.get_last_run_time(task_id)
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
                    return parse_utc_datetime(row[0])
        except Exception:
            return None
        return None

    def schedule_due_tasks(self) -> int:
        """Schedule due tasks into the queue."""
        scheduled = 0
        settings = self.get_settings()
        tasks = self.list_tasks(limit=1000)
        now = utc_now()
        for task in tasks:
            if not task.get("enabled", True):
                continue
            if not self._task_due(task):
                continue
            scheduled_for = now if self._within_window(task, now, settings) else self._next_window_start(task, now, settings)
            self.schedule_task(task["id"], scheduled_for)
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
        pending = (
            self.store.claim_due_queue_items(limit=20)
            if self._managed
            else self.get_pending_queue(limit=20)
        )
        if not pending:
            return {"scheduled": scheduled, "executed": 0}

        pending.sort(key=self._score_task, reverse=True)
        executed = 0
        network_ok = self._network_available() if allow_network else False
        deferred = 0
        now = utc_now()
        for item in pending:
            if executed >= max_tasks:
                break
            if not self._within_window(item, now, settings):
                self._defer_queue_item(
                    item,
                    reason="waiting_for_window",
                    now=now,
                    settings=settings,
                    preferred_time=self._next_window_start(item, now, settings),
                )
                deferred += 1
                continue
            if not self._resources_ok(item):
                self._defer_queue_item(
                    item,
                    reason="resource_pressure",
                    now=now,
                    settings=settings,
                )
                deferred += 1
                continue
            if item.get("requires_network") and not network_ok:
                self._defer_queue_item(
                    item,
                    reason="network_unavailable",
                    now=now,
                    settings=settings,
                )
                deferred += 1
                continue
            if not self._budget_allows(item, settings, now):
                self._defer_queue_item(
                    item,
                    reason="api_budget_exhausted",
                    now=now,
                    settings=settings,
                    preferred_time=self._next_window_start(item, now + timedelta(days=1), settings),
                )
                deferred += 1
                continue
            if (not self._managed) and (not self.mark_processing(item["id"])):
                continue
            execution = self._execute_task_item(item)
            if execution.get("defer_reason"):
                defer_until = execution.get("defer_until")
                scheduled_for = None
                if isinstance(defer_until, datetime):
                    scheduled_for = defer_until
                elif isinstance(defer_until, str):
                    try:
                        scheduled_for = parse_utc_datetime(defer_until)
                    except ValueError:
                        scheduled_for = now + timedelta(hours=1)
                self._defer_queue_item(
                    item,
                    reason=str(execution["defer_reason"]),
                    now=now,
                    settings=settings,
                    preferred_time=scheduled_for,
                )
                deferred += 1
                continue
            self.complete_task(item["run_id"], result=str(execution["result"]), output=str(execution["output"]))
            settings = self._record_budget_use(item, settings, now)
            executed += 1
        return {"scheduled": scheduled, "executed": executed, "deferred": deferred}

    def _ensure_workflow_from_source(self, payload: Dict[str, Any]) -> str:
        workflow_id = str(payload.get("workflow_id") or Path(str(payload.get("source_path", "workflow"))).stem)
        try:
            self.workflow_scheduler.load_spec(workflow_id)
            return workflow_id
        except FileNotFoundError:
            source_path = payload.get("source_path")
            if not source_path:
                raise
            source = Path(str(source_path))
            if not source.is_absolute():
                source = Path(get_repo_root()) / source
            markdown = source.read_text(encoding="utf-8")
            self.workflow_scheduler.create_workflow_from_markdown(
                workflow_id,
                markdown,
                source_path=source,
                project=str(payload.get("project") or workflow_id),
            )
            return workflow_id

    def _execute_workflow_phase(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = self._ensure_workflow_from_source(payload)
        phase_index = max(0, int(payload.get("phase_index", 1)) - 1)
        state = self.workflow_scheduler.load_state(workflow_id)

        if phase_index < state.current_phase_index:
            return {
                "result": "success",
                "output": f"Workflow phase already complete for {workflow_id}",
            }

        if phase_index > state.current_phase_index:
            return {
                "result": "deferred",
                "output": f"Waiting for workflow {workflow_id} to reach phase {phase_index + 1}",
                "defer_reason": "waiting_for_workflow_phase",
                "defer_until": state.next_run_at or (utc_now() + timedelta(hours=1)).isoformat(),
            }

        state = self.workflow_scheduler.run_workflow(workflow_id)
        current_phase = state.phases[state.current_phase_index]
        if state.status in {"awaiting_approval", "waiting"}:
            return {
                "result": "deferred",
                "output": f"Workflow {workflow_id} waiting in state {state.status}",
                "defer_reason": "waiting_for_workflow_state",
                "defer_until": state.next_run_at or (utc_now() + timedelta(hours=12)).isoformat(),
            }

        if current_phase.status == "failed":
            return {"result": "error", "output": current_phase.last_error or f"Workflow {workflow_id} failed"}

        return {
            "result": "success",
            "output": json.dumps(
                {
                    "workflow_id": workflow_id,
                    "status": state.status,
                    "current_phase_index": state.current_phase_index,
                    "next_run_at": state.next_run_at,
                }
            ),
        }

    def _execute_task_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
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
            return {"result": "success", "output": json.dumps(result)}
        if kind == "health_housekeeping":
            scope = str(payload.get("scope", "knowledge"))
            apply = bool(payload.get("apply", True))
            result = run_housekeeping(scope, apply=apply)
            return {"result": "success", "output": json.dumps(result)}
        if kind == "backup_target":
            target_key = payload.get("target")
            notes = payload.get("notes")
            if not target_key:
                return {"result": "error", "output": "backup_target missing payload.target"}
            result = get_repair_service().backup_target(target_key, notes)
            return {"result": "success" if result.get("success") else "error", "output": json.dumps(result)}
        if kind == "workflow_phase":
            return self._execute_workflow_phase(payload)
        if isinstance(kind, str) and kind.startswith("dev_scheduler:"):
            project_id = payload.get("workflow_project_id")
            if not project_id:
                return {"result": "error", "output": "dev scheduler task missing payload.workflow_project_id"}
            manager = WorkflowManager()
            result = manager.run_workflow(project_id)
            return {"result": "success", "output": json.dumps(result)}

        return {"result": "skipped", "output": "No executor for task kind"}

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

    def ensure_daily_health_housekeeping(
        self,
        scope: str = "knowledge",
        apply: bool = True,
    ) -> None:
        if self.get_task_by_kind("health_housekeeping"):
            return
        self.create_task(
            name="Daily health housekeeping",
            description="Tidy/CLEAN scoped uDOS data with elastic .compost retention",
            schedule="daily",
            priority=6,
            need=5,
            resource_cost=1,
            requires_network=False,
            kind="health_housekeeping",
            payload={"scope": scope, "apply": apply},
        )

    def get_task_by_kind(self, kind: str) -> Optional[Dict[str, Any]]:
        if self._managed:
            return self.store.get_task_by_kind(kind)
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
        settings = self.get_settings()
        budget = self._budget_state(settings, utc_now())
        if self._managed:
            stats = self.store.get_task_stats()
            stats["api_budget"] = {
                "daily": budget["api_budget_daily"],
                "used": budget["api_budget_used"],
                "remaining": max(0, budget["api_budget_daily"] - budget["api_budget_used"]),
                "day": budget["api_budget_day"],
            }
            stats["defer_reasons"] = self.get_defer_reason_counts()
            return stats
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
                    "api_budget": {
                        "daily": budget["api_budget_daily"],
                        "used": budget["api_budget_used"],
                        "remaining": max(0, budget["api_budget_daily"] - budget["api_budget_used"]),
                        "day": budget["api_budget_day"],
                    },
                    "defer_reasons": self.get_defer_reason_counts(),
                }
        except sqlite3.Error as exc:
            logger.error(f"[WIZ] Stats error: {exc}")
            return {}
