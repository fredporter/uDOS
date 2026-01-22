"""
Notion Webhook Service (Wizard)

Handles:
- Webhook signature verification (HMAC-SHA256)
- Block change queueing
- SQLite storage
- Sync status tracking
"""

import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from wizard.services.block_mapper import BlockMapper
from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard.notion-sync")


class NotionSyncService:
    """Manage Notion webhook processing and queue."""

    def __init__(self, db_path: Optional[str] = None):
        self.webhook_secret = os.getenv("NOTION_WEBHOOK_SECRET", "")
        repo_root = get_repo_root()
        default_db = repo_root / "memory" / "wizard" / "notion_sync.db"
        self.db_path = Path(db_path) if db_path else default_db
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_connection()
        self._init_tables()
        self.block_mapper = BlockMapper()

    def _init_connection(self) -> None:
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")

    def _init_tables(self) -> None:
        schema_path = Path(__file__).parent / "schemas" / "sync_schema.sql"
        if schema_path.exists():
            self.conn.executescript(schema_path.read_text())
            self.conn.commit()

    def verify_webhook_signature(self, body: bytes, signature_header: str) -> bool:
        if not self.webhook_secret:
            return True
        if not signature_header:
            return True
        if not signature_header.startswith("Signature="):
            return False

        provided_sig = signature_header[len("Signature=") :]
        expected_sig = hmac.new(
            self.webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(provided_sig, expected_sig)

    def enqueue_webhook(self, payload: dict) -> Dict[str, any]:
        queued = 0
        failed = 0
        queue_ids: List[int] = []

        action_map = {
            "block.create": "create",
            "block.update": "update",
            "block.delete": "delete",
        }
        action = action_map.get(payload.get("type"), "update")

        changes = payload.get("changes", []) or [payload]
        for change in changes:
            try:
                block_id = change.get("id") or payload.get("id")
                if not block_id:
                    failed += 1
                    continue

                block_type = change.get("type", "paragraph")
                runtime_type = self._detect_runtime_block(change)

                cursor = self.conn.execute(
                    """
                    INSERT INTO sync_queue (notion_block_id, database_id, block_type, runtime_type, action, payload, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending')
                    """,
                    (
                        block_id,
                        payload.get("database_id", ""),
                        block_type,
                        runtime_type,
                        action,
                        json.dumps(change),
                    ),
                )
                self.conn.commit()
                queue_ids.append(cursor.lastrowid)
                queued += 1
            except Exception as exc:
                failed += 1
                logger.error(f"[WIZ] Failed to queue block {change.get('id')}: {exc}")

        return {"queued": queued, "failed": failed, "queue_ids": queue_ids}

    def _detect_runtime_block(self, block: dict) -> Optional[str]:
        caption = block.get("caption", [])
        if caption and isinstance(caption, list):
            caption_text = " ".join(text.get("plain_text", "") for text in caption)
            for rt in ["STATE", "FORM", "IF", "NAV", "PANEL", "MAP", "SET"]:
                if f"[uDOS:{rt}]" in caption_text:
                    return rt

        annotations = block.get("annotations", {})
        if "runtime_type" in annotations:
            return annotations["runtime_type"]

        return None

    def get_sync_status(self) -> Dict[str, int]:
        cursor = self.conn.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status='processing' THEN 1 ELSE 0 END) as processing,
                SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed
            FROM sync_queue
            """
        )
        row = cursor.fetchone()
        return {
            "total": row[0] or 0,
            "pending": row[1] or 0,
            "processing": row[2] or 0,
            "completed": row[3] or 0,
            "failed": row[4] or 0,
        }

    def list_pending_syncs(self, limit: int = 10) -> List[Dict]:
        cursor = self.conn.execute(
            """
            SELECT id, notion_block_id, database_id, block_type, runtime_type, action, payload, created_at
            FROM sync_queue
            WHERE status='pending'
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def mark_processing(self, queue_id: int) -> None:
        self.conn.execute(
            "UPDATE sync_queue SET status='processing' WHERE id=?", (queue_id,)
        )
        self.conn.commit()

    def mark_completed(
        self, queue_id: int, local_file_path: Optional[str] = None
    ) -> None:
        self.conn.execute(
            """
            UPDATE sync_queue 
            SET status='completed', processed_at=CURRENT_TIMESTAMP
            WHERE id=?
            """,
            (queue_id,),
        )
        if local_file_path:
            self.conn.execute(
                """
                INSERT INTO sync_history (notion_block_id, local_file_path, action, status)
                SELECT notion_block_id, ?, action, 'completed'
                FROM sync_queue WHERE id=?
                """,
                (local_file_path, queue_id),
            )
        self.conn.commit()

    def mark_failed(self, queue_id: int, error_message: str) -> None:
        self.conn.execute(
            """
            UPDATE sync_queue 
            SET status='failed', processed_at=CURRENT_TIMESTAMP, error_message=?
            WHERE id=?
            """,
            (error_message, queue_id),
        )
        self.conn.commit()

    def close(self) -> None:
        if hasattr(self, "conn"):
            self.conn.close()

    def __del__(self):
        self.close()
