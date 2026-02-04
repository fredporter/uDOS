import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from wizard.services.path_utils import get_repo_root

SCHEMA_PATH = get_repo_root() / "v1-3" / "core" / "src" / "spatial" / "schema.sql"


def _ensure_spatial_schema(db_path: Path) -> None:
    if not SCHEMA_PATH.exists():
        return
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(SCHEMA_PATH.read_text())
    finally:
        conn.close()


def get_spatial_db_path(create: bool = False) -> Optional[Path]:
    """Locate (or optionally create) the spatial state DB."""
    vault_root = get_repo_root() / "vault"
    candidates = [
        vault_root / ".udos" / "state.db",
        vault_root / "05_DATA" / "sqlite" / "udos.db",
    ]
    for candidate in candidates:
        if candidate.exists():
            if create:
                _ensure_spatial_schema(candidate)
            return candidate
    if not create:
        return None
    candidate = candidates[0]
    candidate.parent.mkdir(parents=True, exist_ok=True)
    _ensure_spatial_schema(candidate)
    return candidate


def fetch_spatial_rows(db_path: Path, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Run a query against the spatial database and return dicts."""
    _ensure_spatial_schema(db_path)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
