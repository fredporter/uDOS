"""
Anchor Store (Core)

SQLite-backed storage for anchors, instances, bindings, and events.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.logging_api import get_logger, get_repo_root
from core.services.anchor_validation import is_valid_anchor_id, is_valid_locid

logger = get_logger("core.anchor_store")


def _utc_now() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class AnchorInstanceRecord:
    instance_id: str
    anchor_id: str
    profile_id: Optional[str]
    space_id: Optional[str]
    seed: Optional[str]
    meta_json: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class AnchorStore:
    """Anchor persistence in SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        repo_root = get_repo_root()
        if db_path is None:
            db_path = repo_root / "memory" / "bank" / "anchors" / "anchors.db"
        self.db_path = Path(db_path)
        self.schema_path = repo_root / "core" / "schemas" / "anchors_schema.sql"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def utc_now(self) -> str:
        return _utc_now()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Missing anchor schema: {self.schema_path}")
        schema = self.schema_path.read_text(encoding="utf-8")
        with self._connect() as conn:
            conn.executescript(schema)

    def create_instance(self, anchor_id: str, profile_id: Optional[str] = None, space_id: Optional[str] = None, seed: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> AnchorInstanceRecord:
        if not is_valid_anchor_id(anchor_id):
            raise ValueError(f"Invalid anchor id: {anchor_id}")
        instance_id = str(uuid.uuid4())
        now = _utc_now()
        meta_json = json.dumps(meta or {})
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO anchor_instances
                (instance_id, anchor_id, profile_id, space_id, seed, meta_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (instance_id, anchor_id, profile_id, space_id, seed, meta_json, now, now),
            )
            conn.commit()
        return AnchorInstanceRecord(
            instance_id=instance_id,
            anchor_id=anchor_id,
            profile_id=profile_id,
            space_id=space_id,
            seed=seed,
            meta_json=meta or {},
            created_at=now,
            updated_at=now,
        )

    def destroy_instance(self, instance_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM anchor_instances WHERE instance_id = ?", (instance_id,))
            conn.commit()

    def add_binding(
        self,
        locid: str,
        anchor_id: str,
        coord_kind: str,
        coord_payload: Dict[str, Any],
        instance_id: Optional[str] = None,
        label: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> str:
        if not is_valid_locid(locid):
            raise ValueError(f"Invalid LocId: {locid}")
        if not is_valid_anchor_id(anchor_id):
            raise ValueError(f"Invalid anchor id: {anchor_id}")
        binding_id = str(uuid.uuid4())
        now = _utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO locid_bindings
                (binding_id, locid, anchor_id, instance_id, coord_kind, coord_json, label, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    binding_id,
                    locid,
                    anchor_id,
                    instance_id,
                    coord_kind,
                    json.dumps(coord_payload or {}),
                    label,
                    tags,
                    now,
                    now,
                ),
            )
            conn.commit()
        return binding_id

    def add_event(
        self,
        anchor_id: str,
        instance_id: str,
        event_type: str,
        locid: Optional[str] = None,
        coord_kind: Optional[str] = None,
        coord_payload: Optional[Dict[str, Any]] = None,
        data_payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not is_valid_anchor_id(anchor_id):
            raise ValueError(f"Invalid anchor id: {anchor_id}")
        if locid and not is_valid_locid(locid):
            raise ValueError(f"Invalid LocId: {locid}")
        event_id = str(uuid.uuid4())
        now = int(datetime.utcnow().timestamp() * 1000)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO anchor_events
                (event_id, ts, anchor_id, instance_id, type, locid, coord_kind, coord_json, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    now,
                    anchor_id,
                    instance_id,
                    event_type,
                    locid,
                    coord_kind,
                    json.dumps(coord_payload or {}) if coord_payload is not None else None,
                    json.dumps(data_payload or {}) if data_payload is not None else None,
                ),
            )
            conn.commit()
        return event_id
