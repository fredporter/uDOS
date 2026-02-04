import hashlib
import os
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

TASK_PATTERN = re.compile(r"^- \[([ xX])\] (.+)")
METADATA_PATTERN = re.compile(r"(📅\s*(\d{4}-\d{2}-\d{2}))|(🛫\s*(\d{4}-\d{2}-\d{2}))|(⏫|⏬)|(#\w+)")


def find_state_db() -> Path:
    vault = Path(os.getenv("VAULT_ROOT", "/workspace/vault"))
    candidates = [
        vault / ".udos" / "state.db",
        vault / "05_DATA" / "sqlite" / "udos.db",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    candidates[0].parent.mkdir(parents=True, exist_ok=True)
    return candidates[0]


class TaskIndexer:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or find_state_db()
        self._ensure_schema()

    def _ensure_schema(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
              file_path TEXT PRIMARY KEY,
              mtime INTEGER NOT NULL,
              hash TEXT NOT NULL
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
              id TEXT PRIMARY KEY,
              file_path TEXT NOT NULL,
              line INTEGER NOT NULL,
              text TEXT NOT NULL,
              status TEXT NOT NULL,
              due TEXT,
              start TEXT,
              priority INTEGER,
              tags TEXT,
              created_at INTEGER NOT NULL,
              updated_at INTEGER NOT NULL,
              FOREIGN KEY(file_path) REFERENCES files(file_path) ON DELETE CASCADE
            )
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tasks_status_due ON tasks(status, due)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tasks_file ON tasks(file_path)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_files_mtime ON files(mtime)
        """
        )
        conn.commit()
        conn.close()

    def index_vault(self, vault_root: Path) -> Dict[str, int]:
        counts = {"open": 0, "done": 0}
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        for md in sorted(vault_root.rglob("*.md")):
            rel = md.relative_to(vault_root).as_posix()
            self._update_file_entry(cursor, rel, md)
            cursor.execute("DELETE FROM tasks WHERE file_path = ?", (rel,))
            self._process_file(cursor, vault_root, md, counts)
        conn.commit()
        conn.close()
        return counts

    def _process_file(self, cursor, vault_root: Path, path: Path, counts: Dict[str, int]):
        rel = path.relative_to(vault_root).as_posix()
        now = int(os.path.getmtime(path))
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line_no, line in enumerate(fh, start=1):
                match = TASK_PATTERN.match(line.strip())
                if not match:
                    continue
                status = "done" if match.group(1).lower() == "x" else "open"
                text = match.group(2).strip()
                meta = self._extract_metadata(line)
                task_id = hashlib.sha1(f"{rel}:{line_no}".encode("utf-8")).hexdigest()
                priority = self._score_priority(meta.get("symbols", []))
                tags = ",".join(meta.get("tags", []))
                cursor.execute(
                    """
                    INSERT INTO tasks(id, file_path, line, text, status, due, start,
                      priority, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                      status = excluded.status,
                      text = excluded.text,
                      due = excluded.due,
                      start = excluded.start,
                      priority = excluded.priority,
                      tags = excluded.tags,
                      updated_at = excluded.updated_at
                """,
                    (
                        task_id,
                        rel,
                        line_no,
                        text,
                        status,
                        meta.get("due"),
                        meta.get("start"),
                        priority,
                        tags,
                        now,
                        now,
                    ),
                )
                counts[status] += 1

    def _update_file_entry(self, cursor, rel_path: str, full_path: Path) -> None:
        if not full_path.exists():
            return
        mtime = int(full_path.stat().st_mtime)
        digest = hashlib.sha256(full_path.read_bytes()).hexdigest()
        cursor.execute(
            """
            INSERT INTO files(file_path, mtime, hash)
            VALUES (?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
              mtime = excluded.mtime,
              hash = excluded.hash
        """,
            (rel_path, mtime, digest),
        )

    def _extract_metadata(self, line: str) -> Dict[str, any]:
        data: Dict[str, any] = {"tags": [], "symbols": []}
        for match in METADATA_PATTERN.finditer(line):
            if match.group(2):
                data["due"] = match.group(2)
            if match.group(4):
                data["start"] = match.group(4)
            if match.group(5):
                data["symbols"].append(match.group(5))
            if match.group(6):
                data["tags"].append(match.group(6))
        return data

    def _score_priority(self, symbols: List[str]) -> int:
        if "⏫" in symbols:
            return 2
        if "⏬" in symbols:
            return -2
        return 0
