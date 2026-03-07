"""
Notification History Service
=============================

Persists toast notifications to SQLite, provides search/filter/export capabilities.

Features:
  - Save notifications with metadata
  - Paginated history retrieval
  - Full-text search with filters
  - Export to JSON, CSV, Markdown
  - Auto-cleanup of old records
  - Statistics aggregation
"""

import json
import csv
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from io import StringIO
import uuid

from wizard.services.deploy_mode import is_managed_mode
from wizard.services.path_utils import get_repo_root
from wizard.services.store import get_wizard_store
from wizard.services.store.base import WizardStore


@dataclass
class Notification:
    """Notification record."""
    id: str
    type: str  # info, success, warning, error, progress
    title: Optional[str]
    message: str
    timestamp: str
    duration_ms: int
    sticky: bool
    action_count: int = 0
    dismissed_at: Optional[str] = None


@dataclass
class ExportRequest:
    """Export parameters."""
    format: str  # json, csv, markdown
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    type_filter: Optional[str] = None
    limit: int = 500


class NotificationHistoryService:
    """SQLite-based notification history."""

    def __init__(
        self,
        db_path: str | None = None,
        *,
        store: WizardStore | None = None,
    ):
        self.repo_root = get_repo_root()
        if db_path:
            self.db_path = Path(db_path)
            self._using_default_db = False
        else:
            self.db_path = self.repo_root / "memory" / "wizard" / "ops.db"
            self._using_default_db = True
        self._managed = is_managed_mode()
        self.store = store or get_wizard_store(
            None if self._managed else self.db_path
        )
        if not self._managed:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_schema()
            if self._using_default_db:
                self._migrate_legacy_notifications()

    def _init_schema(self):
        """Initialize database schema on first run from shared SQL."""
        schema_path = Path(__file__).parent / "schemas" / "notifications_schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Notification schema file missing: {schema_path}")
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_path.read_text(encoding="utf-8"))
            conn.commit()

    def _migrate_legacy_notifications(self) -> None:
        legacy_db = self.repo_root / "memory" / "notifications.db"
        if not legacy_db.exists() or legacy_db.resolve() == self.db_path.resolve():
            return
        with sqlite3.connect(legacy_db) as source:
            table = source.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'"
            ).fetchone()
            if not table:
                return
            source.row_factory = sqlite3.Row
            rows = source.execute(
                """
                SELECT id, type, title, message, timestamp, duration_ms, sticky, action_count, dismissed_at
                FROM notifications
                """
            ).fetchall()
        if not rows:
            return
        with sqlite3.connect(self.db_path) as target:
            target.executemany(
                """
                INSERT INTO notifications (
                    id, type, title, message, timestamp, duration_ms, sticky, action_count, dismissed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING
                """,
                [
                    (
                        row["id"],
                        row["type"],
                        row["title"],
                        row["message"],
                        row["timestamp"],
                        int(row["duration_ms"] or 0),
                        int(row["sticky"] or 0),
                        int(row["action_count"] or 0),
                        row["dismissed_at"],
                    )
                    for row in rows
                ],
            )
            target.commit()

    async def save_notification(
        self,
        type_: str,
        title: Optional[str],
        message: str,
        duration_ms: int = 5000,
        sticky: bool = False,
    ) -> str:
        """Save a notification to history."""
        notification_id = f"toast-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        if self._managed:
            return self.store.save_notification(
                {
                    "id": notification_id,
                    "type": type_,
                    "title": title,
                    "message": message,
                    "timestamp": timestamp,
                    "duration_ms": duration_ms,
                    "sticky": sticky,
                }
            )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO notifications
                (id, type, title, message, timestamp, duration_ms, sticky)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    notification_id,
                    type_,
                    title,
                    message,
                    timestamp,
                    duration_ms,
                    1 if sticky else 0,
                ),
            )
            conn.commit()

        return notification_id

    async def get_notifications(
        self, limit: int = 20, offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated notification history."""
        if self._managed:
            return self.store.get_notifications(limit=limit, offset=offset)
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get total count
            count_result = conn.execute(
                "SELECT COUNT(*) as count FROM notifications"
            ).fetchone()
            total = count_result["count"]

            # Get page
            rows = conn.execute(
                """
                SELECT * FROM notifications
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()

            notifications = [dict(row) for row in rows]

        return notifications, total

    async def search_notifications(
        self,
        query: Optional[str] = None,
        type_filter: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search notifications with filters."""
        if self._managed:
            return self.store.search_notifications(
                query=query,
                type_filter=type_filter,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            sql = "SELECT * FROM notifications WHERE 1=1"
            params: List[Any] = []

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

            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]

    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a single notification."""
        if self._managed:
            return self.store.delete_notification(notification_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM notification_actions WHERE notification_id = ?", (notification_id,))
            conn.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
            conn.commit()
        return True

    async def clear_old_notifications(self, days: int = 30) -> int:
        """Remove notifications older than N days."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

        if self._managed:
            return self.store.clear_old_notifications(cutoff_iso=cutoff)

        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "DELETE FROM notifications WHERE timestamp < ?",
                (cutoff,),
            )
            count = result.rowcount
            conn.commit()

        return count

    async def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        if self._managed:
            return self.store.get_notification_stats()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            total = conn.execute("SELECT COUNT(*) as count FROM notifications").fetchone()["count"]
            by_type = conn.execute(
                "SELECT type, COUNT(*) as count FROM notifications GROUP BY type"
            ).fetchall()

            stats = {
                "total": total,
                "by_type": {row["type"]: row["count"] for row in by_type},
            }

        return stats

    async def export_notifications(
        self, format_: str, req: ExportRequest
    ) -> Dict[str, Any]:
        """Export notifications to JSON/CSV/Markdown."""
        notifications, _ = await self.search_notifications(
            query=None,
            type_filter=req.type_filter,
            start_date=req.start_date,
            end_date=req.end_date,
            limit=req.limit,
        )

        if format_ == "json":
            return await self._export_json(notifications)
        elif format_ == "csv":
            return await self._export_csv(notifications)
        elif format_ == "markdown":
            return await self._export_markdown(notifications)
        else:
            raise ValueError(f"Unknown format: {format_}")

    async def _export_json(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export to JSON format."""
        data = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_records": len(notifications),
            "notifications": notifications,
        }
        return {
            "format": "json",
            "content": json.dumps(data, indent=2),
            "filename": f"notification-history-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json",
        }

    async def _export_csv(self, notifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export to CSV format."""
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "type",
                "title",
                "message",
                "timestamp",
                "duration_ms",
                "sticky",
                "action_count",
            ],
        )
        writer.writeheader()
        for notif in notifications:
            writer.writerow(
                {
                    "id": notif.get("id"),
                    "type": notif.get("type"),
                    "title": notif.get("title", ""),
                    "message": notif.get("message"),
                    "timestamp": notif.get("timestamp"),
                    "duration_ms": notif.get("duration_ms"),
                    "sticky": notif.get("sticky"),
                    "action_count": notif.get("action_count", 0),
                }
            )
        return {
            "format": "csv",
            "content": output.getvalue(),
            "filename": f"notification-history-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.csv",
        }

    async def _export_markdown(
        self, notifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Export to Markdown format."""
        lines = [
            "# Notification History Export\n",
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
            f"\n## Summary\n",
            f"- Total: {len(notifications)} notifications\n",
        ]

        # Count by type
        by_type: Dict[str, int] = {}
        for notif in notifications:
            type_ = notif.get("type", "unknown")
            by_type[type_] = by_type.get(type_, 0) + 1

        type_summary = " | ".join([f"{t}: {c}" for t, c in sorted(by_type.items())])
        lines.append(f"- {type_summary}\n")
        lines.append("\n## Notifications\n")

        # Group by type
        for type_ in sorted(by_type.keys()):
            type_notifs = [n for n in notifications if n.get("type") == type_]
            lines.append(f"### {type_.capitalize()} ({len(type_notifs)})\n")

            for notif in type_notifs:
                timestamp = notif.get("timestamp", "")
                title = notif.get("title", "")
                message = notif.get("message", "")

                if timestamp:
                    timestamp_short = timestamp.split("T")[1].split(".")[0]
                else:
                    timestamp_short = "??:??"

                if title:
                    lines.append(f"- **[{timestamp_short}]** {title}: {message}\n")
                else:
                    lines.append(f"- **[{timestamp_short}]** {message}\n")

            lines.append("\n")

        return {
            "format": "markdown",
            "content": "".join(lines),
            "filename": f"notification-history-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.md",
        }
