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
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from io import StringIO
import uuid


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

    def __init__(self, db_path: str = "memory/notifications.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema on first run."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    title TEXT,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration_ms INTEGER,
                    sticky BOOLEAN DEFAULT 0,
                    action_count INTEGER DEFAULT 0,
                    dismissed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notification_actions (
                    id TEXT PRIMARY KEY,
                    notification_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    action_type TEXT,
                    callback_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(notification_id) REFERENCES notifications(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notification_exports (
                    id TEXT PRIMARY KEY,
                    export_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    format TEXT NOT NULL,
                    file_path TEXT,
                    record_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_actions_notification_id ON notification_actions(notification_id)"
            )
            conn.commit()

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
        timestamp = datetime.utcnow().isoformat()

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
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM notification_actions WHERE notification_id = ?", (notification_id,))
            conn.execute("DELETE FROM notifications WHERE id = ?", (notification_id,))
            conn.commit()
        return True

    async def clear_old_notifications(self, days: int = 30) -> int:
        """Remove notifications older than N days."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

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
            "exported_at": datetime.utcnow().isoformat(),
            "total_records": len(notifications),
            "notifications": notifications,
        }
        return {
            "format": "json",
            "content": json.dumps(data, indent=2),
            "filename": f"notification-history-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json",
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
            "filename": f"notification-history-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv",
        }

    async def _export_markdown(
        self, notifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Export to Markdown format."""
        lines = [
            "# Notification History Export\n",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n",
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
            "filename": f"notification-history-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.md",
        }
