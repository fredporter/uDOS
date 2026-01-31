"""
SQLite Manager (Core)

Centralized helpers for SQLite database access and schema initialization.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, Optional

from core.services.logging_service import get_repo_root


class SQLiteManager:
    """SQLite helpers for Core."""

    @staticmethod
    def open_db(db_path: Path, read_only: bool = False) -> sqlite3.Connection:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        if read_only:
            uri = f"file:{db_path}?mode=ro"
            return sqlite3.connect(uri, uri=True)
        return sqlite3.connect(str(db_path))

    @staticmethod
    def ensure_db(db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        if not db_path.exists():
            db_path.touch()

    @staticmethod
    def apply_schema(db_path: Path, schema_path: Path) -> bool:
        if not schema_path.exists():
            return False
        conn = sqlite3.connect(str(db_path))
        try:
            conn.executescript(schema_path.read_text())
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def _load_schemas() -> Dict[str, str]:
        config_path = get_repo_root() / "core" / "config" / "sqlite.json"
        if not config_path.exists():
            return {}
        try:
            data = json.loads(config_path.read_text())
        except json.JSONDecodeError:
            return {}
        return data.get("schemas", {})

    @staticmethod
    def init_db(schema_id: str, db_path: Path) -> bool:
        schemas = SQLiteManager._load_schemas()
        rel_path = schemas.get(schema_id)
        if not rel_path:
            return False
        schema_path = get_repo_root() / rel_path
        return SQLiteManager.apply_schema(db_path, schema_path)
