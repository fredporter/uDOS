"""
uDOS v1.1.18 Part 3 - Archive Indexing System

SQLite-based indexing for fast backup search across workspace.
Enables fuzzy search, filtering by date/size/type, and quick lookups.

Database Schema:
- files: Original file metadata (path, size, hash)
- backups: Individual backup records (timestamp, type, size, compression)
- index_metadata: Index version, last_updated, workspace_root
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class ArchiveIndex:
    """SQLite-based index for fast backup search."""

    DB_VERSION = 1
    DEFAULT_DB_PATH = Path.home() / '.udos' / 'archive_index.db'

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize archive index.

        Args:
            db_path: Path to SQLite database (default: ~/.udos/archive_index.db)
        """
        self.db_path = db_path or self.DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize database schema if not exists."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Files table - original file metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                size INTEGER,
                hash TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP,
                UNIQUE(path)
            )
        ''')

        # Backups table - individual backup records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER NOT NULL,
                backup_path TEXT UNIQUE NOT NULL,
                backup_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,  -- full, incremental, compressed
                size INTEGER NOT NULL,
                base_backup_id INTEGER,  -- for incremental backups
                compression TEXT,  -- gzip, none
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
                FOREIGN KEY (base_backup_id) REFERENCES backups(id)
            )
        ''')

        # Index metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS index_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')

        # Indexes for fast search
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_name ON files(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files(path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backups_file_id ON backups(file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backups_timestamp ON backups(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backups_type ON backups(type)')

        # Set initial metadata
        cursor.execute(
            'INSERT OR IGNORE INTO index_metadata (key, value) VALUES (?, ?)',
            ('version', str(self.DB_VERSION))
        )
        cursor.execute(
            'INSERT OR IGNORE INTO index_metadata (key, value) VALUES (?, ?)',
            ('last_updated', datetime.now().isoformat())
        )

        conn.commit()
        conn.close()

    def add_file(self, file_path: Path, size: Optional[int] = None,
                 file_hash: Optional[str] = None) -> int:
        """Add or update file record.

        Args:
            file_path: Path to original file
            size: File size in bytes
            file_hash: SHA256 hash of file content

        Returns:
            File ID in database
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        path_str = str(file_path.resolve())
        name = file_path.name
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime) if file_path.exists() else None

        cursor.execute('''
            INSERT INTO files (path, name, size, hash, last_modified)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                size = excluded.size,
                hash = excluded.hash,
                last_modified = excluded.last_modified
        ''', (path_str, name, size, file_hash, mtime))

        file_id = cursor.lastrowid if cursor.lastrowid > 0 else cursor.execute(
            'SELECT id FROM files WHERE path = ?', (path_str,)
        ).fetchone()[0]

        conn.commit()
        conn.close()

        return file_id

    def add_backup(self, file_path: Path, backup_path: Path, backup_type: str,
                   backup_size: int, timestamp: str, compression: Optional[str] = None,
                   base_backup_path: Optional[Path] = None) -> int:
        """Add backup record to index.

        Args:
            file_path: Original file path
            backup_path: Path to backup file
            backup_type: 'full', 'incremental', or 'compressed'
            backup_size: Size of backup in bytes
            timestamp: Backup timestamp (YYYYMMDD_HHMMSS format)
            compression: Compression type ('gzip' or None)
            base_backup_path: Base backup for incremental backups

        Returns:
            Backup ID in database
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get or create file record
        file_id = self.add_file(file_path)

        # Get base backup ID if incremental
        base_backup_id = None
        if base_backup_path:
            cursor.execute(
                'SELECT id FROM backups WHERE backup_path = ?',
                (str(base_backup_path.resolve()),)
            )
            result = cursor.fetchone()
            if result:
                base_backup_id = result[0]

        backup_path_str = str(backup_path.resolve())
        backup_name = backup_path.name

        cursor.execute('''
            INSERT INTO backups (
                file_id, backup_path, backup_name, timestamp, type,
                size, base_backup_id, compression
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(backup_path) DO UPDATE SET
                type = excluded.type,
                size = excluded.size,
                base_backup_id = excluded.base_backup_id,
                compression = excluded.compression
        ''', (file_id, backup_path_str, backup_name, timestamp, backup_type,
              backup_size, base_backup_id, compression))

        backup_id = cursor.lastrowid

        # Update index metadata
        cursor.execute(
            'UPDATE index_metadata SET value = ? WHERE key = ?',
            (datetime.now().isoformat(), 'last_updated')
        )

        conn.commit()
        conn.close()

        return backup_id

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for files and backups matching query.

        Args:
            query: Search term (fuzzy matched against file names and paths)
            limit: Maximum results to return

        Returns:
            List of matching records with file and backup info
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Fuzzy search using LIKE with wildcards
        pattern = f'%{query}%'

        cursor.execute('''
            SELECT
                f.id as file_id,
                f.path as file_path,
                f.name as file_name,
                f.size as file_size,
                COUNT(b.id) as backup_count,
                MAX(b.timestamp) as latest_backup,
                SUM(b.size) as total_backup_size
            FROM files f
            LEFT JOIN backups b ON f.id = b.file_id
            WHERE f.name LIKE ? OR f.path LIKE ?
            GROUP BY f.id
            ORDER BY backup_count DESC, f.name ASC
            LIMIT ?
        ''', (pattern, pattern, limit))

        results = []
        for row in cursor.fetchall():
            results.append({
                'file_id': row['file_id'],
                'file_path': row['file_path'],
                'file_name': row['file_name'],
                'file_size': row['file_size'],
                'backup_count': row['backup_count'],
                'latest_backup': row['latest_backup'],
                'total_backup_size': row['total_backup_size'] or 0
            })

        conn.close()
        return results

    def get_file_backups(self, file_path: Path) -> List[Dict[str, Any]]:
        """Get all backups for a specific file.

        Args:
            file_path: Path to original file

        Returns:
            List of backup records for the file
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        path_str = str(file_path.resolve())

        cursor.execute('''
            SELECT
                b.id,
                b.backup_path,
                b.backup_name,
                b.timestamp,
                b.type,
                b.size,
                b.compression,
                b.created,
                bb.backup_name as base_backup_name
            FROM backups b
            JOIN files f ON b.file_id = f.id
            LEFT JOIN backups bb ON b.base_backup_id = bb.id
            WHERE f.path = ?
            ORDER BY b.timestamp DESC
        ''', (path_str,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'backup_path': row['backup_path'],
                'backup_name': row['backup_name'],
                'timestamp': row['timestamp'],
                'type': row['type'],
                'size': row['size'],
                'compression': row['compression'],
                'created': row['created'],
                'base_backup': row['base_backup_name']
            })

        conn.close()
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.

        Returns:
            Dictionary with index stats (file count, backup count, total size, etc.)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Get counts
        cursor.execute('SELECT COUNT(*) FROM files')
        file_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM backups')
        backup_count = cursor.fetchone()[0]

        # Get total backup size
        cursor.execute('SELECT SUM(size) FROM backups')
        total_size = cursor.fetchone()[0] or 0

        # Get breakdown by type
        cursor.execute('''
            SELECT type, COUNT(*) as count, SUM(size) as total_size
            FROM backups
            GROUP BY type
        ''')
        type_breakdown = {}
        for row in cursor.fetchall():
            type_breakdown[row[0]] = {
                'count': row[1],
                'size': row[2] or 0
            }

        # Get metadata
        cursor.execute('SELECT value FROM index_metadata WHERE key = ?', ('last_updated',))
        last_updated = cursor.fetchone()[0]

        conn.close()

        return {
            'file_count': file_count,
            'backup_count': backup_count,
            'total_size': total_size,
            'type_breakdown': type_breakdown,
            'last_updated': last_updated
        }

    def rebuild_index(self, archive_dirs: List[Path], progress_callback=None):
        """Rebuild index from scratch by scanning archive directories.

        Args:
            archive_dirs: List of .archive directories to scan
            progress_callback: Optional callback(current, total, message)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute('DELETE FROM backups')
        cursor.execute('DELETE FROM files')
        conn.commit()

        total_backups = 0
        processed = 0

        # Count total backups first for progress reporting
        for archive_dir in archive_dirs:
            backups_dir = archive_dir / 'backups'
            if backups_dir.exists():
                total_backups += len(list(backups_dir.iterdir()))

        # Process each archive
        for archive_dir in archive_dirs:
            backups_dir = archive_dir / 'backups'
            if not backups_dir.exists():
                continue

            # Get original file path (3 levels up from backups/)
            original_dir = archive_dir.parent

            for backup_file in backups_dir.iterdir():
                if backup_file.is_file():
                    processed += 1

                    if progress_callback and processed % 10 == 0:
                        progress_callback(processed, total_backups,
                                        f"Indexing: {backup_file.name}")

                    # Parse backup filename: YYYYMMDD_HHMMSS_original_name.ext[.gz/.diff]
                    name_parts = backup_file.name.split('_', 2)
                    if len(name_parts) < 3:
                        continue

                    timestamp = f"{name_parts[0]}_{name_parts[1]}"
                    original_name = name_parts[2]

                    # Remove .gz or .diff extension
                    if original_name.endswith('.gz'):
                        original_name = original_name[:-3]
                        compression = 'gzip'
                        backup_type = 'compressed'
                    elif original_name.endswith('.diff'):
                        original_name = original_name[:-5]
                        compression = None
                        backup_type = 'incremental'
                    else:
                        compression = None
                        backup_type = 'full'

                    # Reconstruct original file path
                    original_file = original_dir / original_name

                    # Add to index
                    self.add_backup(
                        file_path=original_file,
                        backup_path=backup_file,
                        backup_type=backup_type,
                        backup_size=backup_file.stat().st_size,
                        timestamp=timestamp,
                        compression=compression
                    )

        conn.close()

        if progress_callback:
            progress_callback(total_backups, total_backups, "Indexing complete")


def get_archive_index(db_path: Optional[Path] = None) -> ArchiveIndex:
    """Factory function to get archive index instance.

    Args:
        db_path: Optional custom database path

    Returns:
        ArchiveIndex instance
    """
    return ArchiveIndex(db_path)
