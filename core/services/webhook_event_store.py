"""
Webhook Event Store for uDOS v1.2.6
Persistent storage and analytics for webhook events.

Features:
- SQLite-based event history
- Event replay capability
- Analytics and metrics
- Automatic cleanup (retention policies)
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading


@dataclass
class WebhookEvent:
    """Webhook event record."""
    id: Optional[int] = None
    webhook_id: str = ""
    platform: str = ""
    event_type: str = ""
    payload: str = ""  # JSON string
    headers: str = ""  # JSON string
    response_status: str = ""
    response_data: str = ""  # JSON string
    execution_time_ms: float = 0.0
    error: Optional[str] = None
    created_at: str = ""
    replayed_from: Optional[int] = None


class WebhookEventStore:
    """Manage webhook event history and analytics."""

    def __init__(self, db_path: str = "memory/system/webhook_events.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize database schema."""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS webhook_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    webhook_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    headers TEXT NOT NULL,
                    response_status TEXT NOT NULL,
                    response_data TEXT,
                    execution_time_ms REAL NOT NULL,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    replayed_from INTEGER,
                    FOREIGN KEY (replayed_from) REFERENCES webhook_events(id)
                )
            """)

            # Create indexes for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_webhook_id
                ON webhook_events(webhook_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_platform
                ON webhook_events(platform)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_created_at
                ON webhook_events(created_at DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type
                ON webhook_events(event_type)
            """)

            conn.commit()
            conn.close()

    def record_event(self, webhook_id: str, platform: str, event_type: str,
                    payload: Dict, headers: Dict, response_status: str,
                    response_data: Dict, execution_time_ms: float,
                    error: Optional[str] = None) -> int:
        """
        Record a webhook event.

        Returns:
            Event ID
        """
        event = WebhookEvent(
            webhook_id=webhook_id,
            platform=platform,
            event_type=event_type,
            payload=json.dumps(payload),
            headers=json.dumps(headers),
            response_status=response_status,
            response_data=json.dumps(response_data),
            execution_time_ms=execution_time_ms,
            error=error,
            created_at=datetime.now().isoformat()
        )

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO webhook_events (
                    webhook_id, platform, event_type, payload, headers,
                    response_status, response_data, execution_time_ms,
                    error, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.webhook_id, event.platform, event.event_type,
                event.payload, event.headers, event.response_status,
                event.response_data, event.execution_time_ms,
                event.error, event.created_at
            ))

            event_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return event_id

    def get_event(self, event_id: int) -> Optional[WebhookEvent]:
        """Get event by ID."""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM webhook_events WHERE id = ?
            """, (event_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return WebhookEvent(**dict(row))
            return None

    def list_events(self, platform: Optional[str] = None,
                   webhook_id: Optional[str] = None,
                   event_type: Optional[str] = None,
                   limit: int = 100,
                   offset: int = 0) -> List[WebhookEvent]:
        """
        List webhook events with optional filtering.

        Args:
            platform: Filter by platform
            webhook_id: Filter by webhook ID
            event_type: Filter by event type
            limit: Maximum results
            offset: Results offset for pagination

        Returns:
            List of webhook events
        """
        query = "SELECT * FROM webhook_events WHERE 1=1"
        params = []

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        if webhook_id:
            query += " AND webhook_id = ?"
            params.append(webhook_id)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [WebhookEvent(**dict(row)) for row in rows]

    def get_analytics(self, days: int = 7) -> Dict:
        """
        Get webhook analytics for the specified time period.

        Args:
            days: Number of days to analyze

        Returns:
            Analytics dictionary with metrics
        """
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Total events
            cursor.execute("""
                SELECT COUNT(*) as total FROM webhook_events
                WHERE created_at >= ?
            """, (start_date,))
            total_events = cursor.fetchone()['total']

            # Events by platform
            cursor.execute("""
                SELECT platform, COUNT(*) as count
                FROM webhook_events
                WHERE created_at >= ?
                GROUP BY platform
            """, (start_date,))
            by_platform = {row['platform']: row['count'] for row in cursor.fetchall()}

            # Events by type
            cursor.execute("""
                SELECT event_type, COUNT(*) as count
                FROM webhook_events
                WHERE created_at >= ?
                GROUP BY event_type
                ORDER BY count DESC
                LIMIT 10
            """, (start_date,))
            by_event_type = {row['event_type']: row['count'] for row in cursor.fetchall()}

            # Success rate
            cursor.execute("""
                SELECT
                    SUM(CASE WHEN response_status = 'success' THEN 1 ELSE 0 END) as success,
                    SUM(CASE WHEN response_status = 'error' THEN 1 ELSE 0 END) as error
                FROM webhook_events
                WHERE created_at >= ?
            """, (start_date,))
            status_row = cursor.fetchone()
            success_count = status_row['success'] or 0
            error_count = status_row['error'] or 0
            success_rate = (success_count / total_events * 100) if total_events > 0 else 0

            # Average execution time
            cursor.execute("""
                SELECT AVG(execution_time_ms) as avg_time
                FROM webhook_events
                WHERE created_at >= ?
            """, (start_date,))
            avg_time = cursor.fetchone()['avg_time'] or 0

            # Events over time (daily)
            cursor.execute("""
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM webhook_events
                WHERE created_at >= ?
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """, (start_date,))
            events_over_time = [
                {'date': row['date'], 'count': row['count']}
                for row in cursor.fetchall()
            ]

            # Recent errors
            cursor.execute("""
                SELECT id, platform, event_type, error, created_at
                FROM webhook_events
                WHERE created_at >= ? AND error IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 10
            """, (start_date,))
            recent_errors = [dict(row) for row in cursor.fetchall()]

            conn.close()

            return {
                'period_days': days,
                'total_events': total_events,
                'success_count': success_count,
                'error_count': error_count,
                'success_rate': round(success_rate, 2),
                'avg_execution_time_ms': round(avg_time, 2),
                'by_platform': by_platform,
                'by_event_type': by_event_type,
                'events_over_time': events_over_time,
                'recent_errors': recent_errors
            }

    def replay_event(self, event_id: int) -> Tuple[Optional[WebhookEvent], Optional[int]]:
        """
        Prepare event for replay.

        Returns:
            Tuple of (original_event, new_event_id if recorded)
        """
        event = self.get_event(event_id)
        if not event:
            return None, None

        # Create replay record
        payload = json.loads(event.payload)
        headers = json.loads(event.headers)

        return event, None  # Return event for external replay handling

    def cleanup_old_events(self, days: int = 90) -> int:
        """
        Delete events older than specified days.

        Args:
            days: Keep events newer than this many days

        Returns:
            Number of events deleted
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM webhook_events
                WHERE created_at < ?
            """, (cutoff_date,))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            return deleted_count

    def get_event_count(self, platform: Optional[str] = None) -> int:
        """Get total event count."""
        query = "SELECT COUNT(*) as total FROM webhook_events"
        params = []

        if platform:
            query += " WHERE platform = ?"
            params.append(platform)

        with self._lock:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            conn.close()

            return count


# Global event store instance
_event_store = None


def get_event_store() -> WebhookEventStore:
    """Get global webhook event store."""
    global _event_store
    if _event_store is None:
        _event_store = WebhookEventStore()
    return _event_store
