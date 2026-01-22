"""
Sync Executor Service (Wizard)

Processes queued Notion changes and maintains local markdown mirrors.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from wizard.services.block_mapper import BlockMapper
from wizard.services.logging_manager import get_logger
from wizard.services.notion_sync_service import NotionSyncService
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard.sync-executor")


class SyncExecutor:
    """Execute queued sync operations and manage bidirectional sync."""

    def __init__(self, db_path: Optional[str] = None, local_root: Optional[str] = None):
        repo_root = get_repo_root()
        default_db = repo_root / "memory" / "wizard" / "notion_sync.db"
        default_root = repo_root / "memory" / "wizard" / "synced"

        self.db_path = db_path or str(default_db)
        self.local_root = Path(local_root) if local_root else default_root
        self.local_root.mkdir(parents=True, exist_ok=True)

        self.sync_service = NotionSyncService(db_path=self.db_path)
        self.block_mapper = BlockMapper()
        self.conn = self.sync_service.conn

    def process_pending_syncs(self, limit: int = 10) -> Dict:
        pending = self.sync_service.list_pending_syncs(limit=limit)
        results = {
            "processed": len(pending),
            "succeeded": 0,
            "failed": 0,
            "conflicts": 0,
            "details": [],
        }

        for item in pending:
            queue_id = item["id"]
            try:
                self.sync_service.mark_processing(queue_id)
                payload = json.loads(item["payload"])
                action = item["action"]

                if action == "create":
                    result = self._apply_create(queue_id, payload)
                elif action == "update":
                    result = self._apply_update(queue_id, payload)
                elif action == "delete":
                    result = self._apply_delete(queue_id, payload)
                else:
                    raise ValueError(f"Unknown action: {action}")

                conflict = self._detect_conflict(queue_id, result)
                if conflict:
                    results["conflicts"] += 1
                    result["conflict"] = conflict

                local_file = result.get("local_file")
                self.sync_service.mark_completed(queue_id, local_file)
                results["succeeded"] += 1
                results["details"].append(
                    {"queue_id": queue_id, "status": "completed", **result}
                )
            except Exception as exc:
                results["failed"] += 1
                self.sync_service.mark_failed(queue_id, str(exc))
                results["details"].append(
                    {"queue_id": queue_id, "status": "failed", "error": str(exc)}
                )
                logger.error(f"[WIZ] Sync queue {queue_id} failed: {exc}")

        return results

    def _apply_create(self, queue_id: int, payload: dict) -> Dict:
        block_id = payload.get("id", f"block_{queue_id}")
        markdown = self.block_mapper.from_notion_blocks([payload])
        local_file = self.local_root / f"{block_id}.md"
        local_file.write_text(markdown, encoding="utf-8")
        content_hash = hashlib.sha256(markdown.encode()).hexdigest()
        self.conn.execute(
            """
            INSERT INTO block_mappings (notion_block_id, local_file_path, content_hash)
            VALUES (?, ?, ?)
            """,
            (block_id, str(local_file), content_hash),
        )
        self.conn.commit()
        return {"local_file": str(local_file), "block_id": block_id, "action": "create"}

    def _apply_update(self, queue_id: int, payload: dict) -> Dict:
        block_id = payload.get("id", f"block_{queue_id}")
        cursor = self.conn.execute(
            "SELECT local_file_path FROM block_mappings WHERE notion_block_id=?",
            (block_id,),
        )
        row = cursor.fetchone()
        if not row:
            return self._apply_create(queue_id, payload)

        local_file = Path(row[0])
        new_markdown = self.block_mapper.from_notion_blocks([payload])
        existing_markdown = (
            local_file.read_text(encoding="utf-8") if local_file.exists() else ""
        )
        existing_hash = (
            hashlib.sha256(existing_markdown.encode()).hexdigest()
            if existing_markdown
            else ""
        )
        new_hash = hashlib.sha256(new_markdown.encode()).hexdigest()
        updated = new_hash != existing_hash

        if updated:
            local_file.write_text(new_markdown, encoding="utf-8")
            self.conn.execute(
                "UPDATE block_mappings SET content_hash=?, last_synced=CURRENT_TIMESTAMP WHERE notion_block_id=?",
                (new_hash, block_id),
            )
            self.conn.commit()

        return {
            "local_file": str(local_file),
            "block_id": block_id,
            "updated": updated,
            "action": "update",
        }

    def _apply_delete(self, queue_id: int, payload: dict) -> Dict:
        block_id = payload.get("id", f"block_{queue_id}")
        cursor = self.conn.execute(
            "SELECT local_file_path FROM block_mappings WHERE notion_block_id=?",
            (block_id,),
        )
        row = cursor.fetchone()
        deleted = False
        if row:
            local_file = Path(row[0])
            if local_file.exists():
                local_file.unlink()
                deleted = True
            self.conn.execute(
                "DELETE FROM block_mappings WHERE notion_block_id=?", (block_id,)
            )
            self.conn.commit()
        return {"block_id": block_id, "deleted": deleted, "action": "delete"}

    def _detect_conflict(self, queue_id: int, change_result: dict) -> Optional[Dict]:
        cursor = self.conn.execute(
            """
            SELECT sh.synced_at, bm.last_synced
            FROM sync_history sh
            LEFT JOIN block_mappings bm ON sh.notion_block_id = bm.notion_block_id
            WHERE sh.id = ?
            LIMIT 1
            """,
            (queue_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return None

    def sync_from_notion(self, database_id: Optional[str] = None) -> Dict:
        return self.process_pending_syncs(limit=100)

    def get_sync_stats(self) -> Dict:
        queue_stats = self.sync_service.get_sync_status()
        local_files = list(self.local_root.glob("*.md"))
        cursor = self.conn.execute("SELECT COUNT(*) FROM block_mappings")
        mapped_blocks = cursor.fetchone()[0]
        return {
            "queue": queue_stats,
            "local_files": len(local_files),
            "mapped_blocks": mapped_blocks,
            "last_sync": self._get_last_sync_time(),
        }

    def _get_last_sync_time(self) -> Optional[str]:
        cursor = self.conn.execute(
            "SELECT MAX(synced_at) FROM sync_history WHERE status='completed'"
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] else None

    def clear_completed_syncs(self, keep_days: int = 30) -> int:
        cursor = self.conn.execute(
            f"""
            DELETE FROM sync_history
            WHERE status='completed'
              AND datetime(synced_at) < datetime('now', '-{keep_days} days')
            """
        )
        self.conn.commit()
        return cursor.rowcount

    def sync_to_notion(self) -> Dict:
        results = {
            "scanned": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "conflicts": 0,
            "details": [],
        }
        if not self.local_root.exists():
            return results

        markdown_files = list(self.local_root.glob("*.md"))
        results["scanned"] = len(markdown_files)
        # Placeholder: actual Notion push not yet implemented
        return results
