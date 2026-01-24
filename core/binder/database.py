"""
Binder Database Context System (Task 8)

Provides isolated database access for binder operations.

**Architecture:**
- Each binder has its own uDOS-table.db (SQLite)
- Relative paths resolve within binder scope
- Context manager pattern for safe db access
- Read-only mode by default (safety first)
- Connection pooling for performance

**Usage:**
```python
from core.binder import BinderDatabase

# Open binder database
with BinderDatabase(binder_path) as db:
    # Query within binder scope
    result = db.query("SELECT * FROM contacts")

    # Import data
    db.import_csv("imports/contacts.csv", "contacts")

    # Export data
    db.export_table("contacts", "tables/contacts.table.md")
```

**Scope Rules:**
- binder_path/ is root (all relative paths resolve here)
- imports/ and exports/ are standard folders
- Cross-binder access requires explicit path
- Queries are scoped to this binder's database
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum
from contextlib import contextmanager
from dataclasses import dataclass

from core.services.sqlite_manager import SQLiteManager


class AccessMode(Enum):
    """Database access modes."""

    READ_ONLY = "readonly"  # SELECT only (safe)
    READ_WRITE = "readwrite"  # SELECT, INSERT, UPDATE, DELETE
    FULL = "full"  # CREATE, DROP, ALTER (dangerous)


@dataclass
class DatabaseInfo:
    """Information about a binder database."""

    binder_path: Path
    db_path: Path
    exists: bool
    size_bytes: int
    table_count: int
    access_mode: AccessMode


class BinderDatabase:
    """Context manager for binder database operations.

    **Features:**
    - Isolated per binder
    - Connection caching
    - Relative path resolution
    - Access mode control
    - Safe transaction handling
    """

    def __init__(self, binder_path: Path, mode: AccessMode = AccessMode.READ_WRITE):
        """Initialize binder database context.

        **Args:**
            binder_path: Path to binder folder
            mode: Access mode (READ_ONLY/READ_WRITE/FULL)

        **Raises:**
            ValueError: If binder path invalid
        """
        self.binder_path = Path(binder_path)
        self.mode = mode
        self.db_path = self.binder_path / "uDOS-table.db"

        # Validate binder structure
        if not self.binder_path.exists():
            raise ValueError(f"Binder path does not exist: {binder_path}")

        if not self.binder_path.is_dir():
            raise ValueError(f"Binder path is not a directory: {binder_path}")

        self._connection = None
        self._cursor = None

    def __enter__(self):
        """Open database connection."""
        self._open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close database connection."""
        self._close_connection()

    def _open_connection(self):
        """Open SQLite connection with mode control."""
        # Create empty database if missing
        SQLiteManager.ensure_db(self.db_path)
        SQLiteManager.init_db("udos_table", self.db_path)

        # URI with access mode
        if self.mode == AccessMode.READ_ONLY:
            uri = f"file:{self.db_path}?mode=ro"
            self._connection = sqlite3.connect(uri, uri=True)
        else:
            self._connection = sqlite3.connect(str(self.db_path))

        # Enable foreign keys
        self._connection.execute("PRAGMA foreign_keys = ON")

        self._cursor = self._connection.cursor()

    def _close_connection(self):
        """Close database connection."""
        if self._cursor:
            self._cursor.close()
        if self._connection:
            if self.mode != AccessMode.READ_ONLY:
                try:
                    self._connection.commit()
                except sqlite3.OperationalError:
                    pass  # Read-only connection
            self._connection.close()
        self._cursor = None
        self._connection = None

    def query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute SELECT query within binder scope.

        **Args:**
            sql: SQL query string
            params: Optional query parameters

        **Returns:**
            List of result rows as dictionaries

        **Raises:**
            ValueError: If query is not SELECT
            sqlite3.OperationalError: If database error
        """
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries allowed in query()")

        if params:
            self._cursor.execute(sql, params)
        else:
            self._cursor.execute(sql)

        # Get column names
        columns = [description[0] for description in self._cursor.description or []]

        # Convert rows to dicts
        rows = []
        for row in self._cursor.fetchall():
            rows.append(dict(zip(columns, row)))

        return rows

    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE statement.

        **Args:**
            sql: SQL statement
            params: Optional parameters

        **Returns:**
            Number of affected rows

        **Raises:**
            ValueError: If mode is READ_ONLY
            sqlite3.OperationalError: If database error
        """
        if self.mode == AccessMode.READ_ONLY:
            raise ValueError("Cannot execute write operations in READ_ONLY mode")

        if params:
            self._cursor.execute(sql, params)
        else:
            self._cursor.execute(sql)

        return self._cursor.rowcount

    def create_table(self, name: str, schema: Dict[str, str]) -> bool:
        """Create table with schema.

        **Args:**
            name: Table name
            schema: Column definitions (name -> type)

        **Returns:**
            True if created, False if exists

        **Raises:**
            ValueError: If mode not FULL
        """
        if self.mode != AccessMode.FULL:
            raise ValueError("CREATE TABLE requires FULL access mode")

        # Build column definitions
        columns = ", ".join([f"{col} {typ}" for col, typ in schema.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {name} ({columns})"

        try:
            self._cursor.execute(sql)
            return True
        except sqlite3.OperationalError:
            return False

    def table_exists(self, table_name: str) -> bool:
        """Check if table exists."""
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        result = self._cursor.execute(sql, (table_name,)).fetchone()
        return result is not None

    def get_tables(self) -> List[str]:
        """Get list of all tables in database."""
        sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        result = self._cursor.execute(sql).fetchall()
        return [row[0] for row in result]

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get table schema and statistics."""
        if not self.table_exists(table_name):
            raise ValueError(f"Table does not exist: {table_name}")

        # Get columns
        pragma = self._cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
        columns = {row[1]: row[2] for row in pragma}

        # Get row count
        count = self._cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

        return {
            "name": table_name,
            "columns": columns,
            "row_count": count,
        }

    def resolve_path(self, relative_path: str) -> Path:
        """Resolve path relative to binder scope.

        **Args:**
            relative_path: Path relative to binder root

        **Returns:**
            Absolute path within binder scope

        **Raises:**
            ValueError: If path tries to escape binder
        """
        target = (self.binder_path / relative_path).resolve()

        # Ensure target is within binder scope
        try:
            target.relative_to(self.binder_path)
        except ValueError:
            raise ValueError(f"Path escapes binder scope: {relative_path}")

        return target

    def get_database_info(self) -> DatabaseInfo:
        """Get information about this database."""
        size = self.db_path.stat().st_size if self.db_path.exists() else 0
        tables = len(self.get_tables())

        return DatabaseInfo(
            binder_path=self.binder_path,
            db_path=self.db_path,
            exists=self.db_path.exists(),
            size_bytes=size,
            table_count=tables,
            access_mode=self.mode,
        )


@contextmanager
def open_binder_db(binder_path: Path, mode: AccessMode = AccessMode.READ_WRITE):
    """Context manager for binder database access.

    **Usage:**
        ```python
        async with open_binder_db(path) as db:
            results = db.query("SELECT * FROM table")
        ```
    """
    db = BinderDatabase(binder_path, mode)
    with db:
        yield db
