"""
Anchor Registry Service (Core)

SQLite-backed anchor registry with default seed import.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.services.logging_api import get_logger, get_repo_root

logger = get_logger("core.anchor_registry")


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class AnchorRecord:
    anchor_id: str
    title: str
    description: Optional[str]
    version: Optional[str]
    capabilities: Dict[str, Any]
    created_at: str
    updated_at: str


class AnchorRegistryService:
    """SQLite-backed anchor registry."""

    def __init__(self, db_path: Optional[Path] = None):
        repo_root = get_repo_root()
        if db_path is None:
            db_path = repo_root / "memory" / "bank" / "anchors" / "anchors.db"
        self.db_path = Path(db_path)
        self.schema_path = repo_root / "core" / "schemas" / "anchors_schema.sql"
        self.defaults_path = repo_root / "core" / "src" / "spatial" / "anchors.default.json"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()
        self._seed_defaults()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Missing anchor schema: {self.schema_path}")
        schema = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(schema)
        logger.info("[LOCAL] Anchor schema ready")

    def _seed_defaults(self) -> None:
        if not self.defaults_path.exists():
            return
        with self._connect() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM anchors")
            if cur.fetchone()[0] > 0:
                return
        try:
            data = json.loads(self.defaults_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("[LOCAL] anchors.default.json invalid JSON; skipping seed")
            return

        anchors = data.get("anchors", [])
        for anchor in anchors:
            anchor_id = anchor.get("anchorId")
            title = anchor.get("title")
            if not anchor_id or not title:
                continue
            record = AnchorRecord(
                anchor_id=anchor_id,
                title=title,
                description=anchor.get("description"),
                version=anchor.get("version"),
                capabilities=anchor.get("capabilities") or {},
                created_at=_utc_now(),
                updated_at=_utc_now(),
            )
            self.register_anchor(record)
        logger.info("[LOCAL] Seeded default anchors")

    def list_anchors(self) -> List[AnchorRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT anchor_id, title, description, version, capabilities_json, created_at, updated_at FROM anchors"
            ).fetchall()
        anchors: List[AnchorRecord] = []
        for row in rows:
            capabilities = {}
            try:
                capabilities = json.loads(row[4]) if row[4] else {}
            except json.JSONDecodeError:
                capabilities = {}
            anchors.append(
                AnchorRecord(
                    anchor_id=row[0],
                    title=row[1],
                    description=row[2],
                    version=row[3],
                    capabilities=capabilities,
                    created_at=row[5],
                    updated_at=row[6],
                )
            )
        return anchors

    def get_anchor(self, anchor_id: str) -> Optional[AnchorRecord]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT anchor_id, title, description, version, capabilities_json, created_at, updated_at FROM anchors WHERE anchor_id = ?",
                (anchor_id,),
            ).fetchone()
        if not row:
            return None
        try:
            capabilities = json.loads(row[4]) if row[4] else {}
        except json.JSONDecodeError:
            capabilities = {}
        return AnchorRecord(
            anchor_id=row[0],
            title=row[1],
            description=row[2],
            version=row[3],
            capabilities=capabilities,
            created_at=row[5],
            updated_at=row[6],
        )

    def register_anchor(self, record: AnchorRecord) -> None:
        payload = json.dumps(record.capabilities or {})
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO anchors
                (anchor_id, title, description, version, capabilities_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.anchor_id,
                    record.title,
                    record.description,
                    record.version,
                    payload,
                    record.created_at,
                    record.updated_at,
                ),
            )
            conn.commit()
