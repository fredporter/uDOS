import sqlite3
import tempfile
import unittest
from pathlib import Path

from empire.services.storage import ensure_schema


class StorageSchemaMigrationTests(unittest.TestCase):
    def test_ensure_schema_upgrades_legacy_tasks_table_before_creating_indexes(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "legacy.db"
            with sqlite3.connect(str(db_path)) as conn:
                conn.execute(
                    """
                    CREATE TABLE tasks (
                        task_id TEXT PRIMARY KEY,
                        title TEXT,
                        category TEXT,
                        source TEXT,
                        created_at TEXT,
                        status TEXT,
                        notes TEXT
                    )
                    """
                )

            ensure_schema(db_path)

            with sqlite3.connect(str(db_path)) as conn:
                columns = {row[1] for row in conn.execute("PRAGMA table_info(tasks)").fetchall()}
                indexes = {row[1] for row in conn.execute("PRAGMA index_list(tasks)").fetchall()}

            self.assertIn("review_status", columns)
            self.assertIn("source_ref", columns)
            self.assertIn("record_id", columns)
            self.assertIn("idx_tasks_review_status", indexes)


if __name__ == "__main__":
    unittest.main()
