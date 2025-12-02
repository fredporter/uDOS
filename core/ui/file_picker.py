"""
uDOS v1.0.7 - Smart File Picker Service
Advanced file selection with fuzzy search, filtering, and intelligent suggestions
"""

import os
import re
import difflib
import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set
from datetime import datetime, timedelta
import subprocess


class FilePicker:
    """
    Smart file picker with fuzzy search, recent files tracking, and workspace integration.
    Leverages command history patterns for persistent file access tracking.
    """

    def __init__(self, workspace_manager=None):
        """
        Initialize file picker service.

        Args:
            workspace_manager: WorkspaceManager instance for workspace integration
        """
        from core.utils.files import WorkspaceManager
        self.workspace_manager = workspace_manager or WorkspaceManager()

        # Initialize file access tracking database
        self.db_path = Path("sandbox/logs/file_access.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        # Folder shortcuts for quick navigation
        self.folder_shortcuts = {
            'sandbox': Path('sandbox'),
            'memory': Path('memory'),
            'knowledge': Path('knowledge'),
            'public': Path('memory/public'),
            'private': Path('memory/private'),
            'groups': Path('memory/groups'),
            'shared': Path('memory/shared'),
            'planet': Path('memory/planet'),
            'user': Path('sandbox/user')
        }

        # Search and filtering settings
        self.fuzzy_threshold = 0.6
        self.max_suggestions = 20
        self.max_recent = 50

        # File type filtering
        self.common_extensions = {
            'text': {'.txt', '.md', '.rst', '.log'},
            'code': {'.py', '.js', '.ts', '.html', '.css', '.json', '.yaml', '.yml'},
            'config': {'.ini', '.cfg', '.conf', '.env', '.toml'},
            'script': {'.sh', '.bash', '.zsh', '.bat', '.ps1', '.upy'},
            'data': {'.csv', '.xml', '.sql', '.db', '.sqlite'},
            'doc': {'.pdf', '.doc', '.docx', '.odt'}
        }

    def _init_database(self):
        """Initialize SQLite database for file access tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    workspace TEXT NOT NULL,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_type TEXT DEFAULT 'open',
                    file_size INTEGER,
                    file_mtime REAL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS file_bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL UNIQUE,
                    workspace TEXT NOT NULL,
                    bookmark_name TEXT,
                    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_access_time
                ON file_access(access_time)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_path
                ON file_access(file_path)
            """)

    def record_file_access(self, file_path: str, workspace: str = None,
                          access_type: str = 'open'):
        """
        Record file access for recent files tracking.

        Args:
            file_path: Path to accessed file
            workspace: Workspace name
            access_type: Type of access (open, edit, create, delete)
        """
        if workspace is None:
            workspace = self.workspace_manager.current_workspace

        # Get file stats if file exists
        file_size = None
        file_mtime = None
        full_path = self.workspace_manager.get_workspace_path(workspace) / file_path

        if full_path.exists():
            stat = full_path.stat()
            file_size = stat.st_size
            file_mtime = stat.st_mtime

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO file_access
                (file_path, workspace, access_type, file_size, file_mtime)
                VALUES (?, ?, ?, ?, ?)
            """, (file_path, workspace, access_type, file_size, file_mtime))

            # Clean up old entries (keep only last 1000)
            conn.execute("""
                DELETE FROM file_access
                WHERE id NOT IN (
                    SELECT id FROM file_access
                    ORDER BY access_time DESC
                    LIMIT 1000
                )
            """)

    def get_recent_files(self, count: int = 20, workspace: str = None,
                        days: int = 30) -> List[Dict]:
        """
        Get recently accessed files.

        Args:
            count: Maximum number of files to return
            workspace: Filter by workspace (None for all)
            days: Number of days to look back

        Returns:
            List of file info dictionaries
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        query = """
            SELECT file_path, workspace, MAX(access_time) as last_access,
                   COUNT(*) as access_count, file_size, file_mtime
            FROM file_access
            WHERE access_time > ?
        """
        params = [cutoff_time.isoformat()]

        if workspace:
            query += " AND workspace = ?"
            params.append(workspace)

        query += """
            GROUP BY file_path, workspace
            ORDER BY last_access DESC
            LIMIT ?
        """
        params.append(count)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            results = []
            for row in cursor:
                file_info = dict(row)

                # Check if file still exists
                full_path = self.workspace_manager.get_workspace_path(
                    file_info['workspace']
                ) / file_info['file_path']

                file_info['exists'] = full_path.exists()
                file_info['is_recent'] = True

                if file_info['exists']:
                    file_info['current_size'] = full_path.stat().st_size
                    file_info['extension'] = full_path.suffix.lower()
                    file_info['file_type'] = self._classify_file_type(
                        file_info['extension']
                    )

                results.append(file_info)

            return results

    def fuzzy_search_files(self, pattern: str, workspace: str = None,
                          max_results: int = None, include_content: bool = False) -> List[Dict]:
        """
        Perform fuzzy search across files in workspace(s).

        Args:
            pattern: Search pattern
            workspace: Workspace to search (None for all)
            max_results: Maximum results to return
            include_content: Whether to search file contents (slower)

        Returns:
            List of matching files with relevance scores
        """
        if max_results is None:
            max_results = self.max_suggestions

        workspaces_to_search = []
        if workspace:
            workspaces_to_search = [workspace]
        else:
            workspaces_to_search = list(self.workspace_manager.WORKSPACES.keys())

        all_matches = []

        for ws in workspaces_to_search:
            try:
                ws_path = self.workspace_manager.get_workspace_path(ws)
                if not ws_path.exists():
                    continue

                # Get all files in workspace
                for file_path in ws_path.rglob('*'):
                    if file_path.is_file() and not self._should_ignore_file(file_path):
                        relative_path = file_path.relative_to(ws_path)

                        # Calculate filename match score
                        filename_score = self._calculate_fuzzy_score(
                            pattern.lower(),
                            file_path.name.lower()
                        )

                        # Calculate path match score
                        path_score = self._calculate_fuzzy_score(
                            pattern.lower(),
                            str(relative_path).lower()
                        )

                        # Use best score
                        best_score = max(filename_score, path_score)

                        if best_score >= self.fuzzy_threshold:
                            file_info = {
                                'file_path': str(relative_path),
                                'workspace': ws,
                                'full_path': str(file_path),
                                'score': best_score,
                                'size': file_path.stat().st_size,
                                'mtime': file_path.stat().st_mtime,
                                'extension': file_path.suffix.lower(),
                                'file_type': self._classify_file_type(file_path.suffix.lower()),
                                'exists': True,
                                'is_recent': False
                            }

                            # Add git status if available
                            file_info['git_status'] = self._get_git_status(file_path)

                            all_matches.append(file_info)

            except Exception as e:
                # Skip workspace if there's an error
                continue

        # Sort by relevance score and return top matches
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        return all_matches[:max_results]

    def _calculate_fuzzy_score(self, pattern: str, text: str) -> float:
        """Calculate fuzzy match score between pattern and text."""
        if pattern in text:
            # Exact substring match gets high score
            return 0.9 + (len(pattern) / len(text)) * 0.1

        # Use difflib for fuzzy matching
        similarity = difflib.SequenceMatcher(None, pattern, text).ratio()
        return similarity

    def _classify_file_type(self, extension: str) -> str:
        """Classify file type based on extension."""
        for file_type, extensions in self.common_extensions.items():
            if extension in extensions:
                return file_type
        return 'other'

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Determine if file should be ignored in search."""
        ignore_patterns = {
            # Hidden files
            r'^\.',
            # Compiled/cache files
            r'\.pyc$', r'\.pyo$', r'__pycache__',
            # System files
            r'\.DS_Store$', r'Thumbs\.db$',
            # Backup files
            r'~$', r'\.bak$', r'\.swp$', r'\.tmp$'
        }

        filename = file_path.name
        for pattern in ignore_patterns:
            if re.search(pattern, filename):
                return True

        return False

    def _get_git_status(self, file_path: Path) -> Optional[str]:
        """Get git status for file if in git repository."""
        try:
            # Check if we're in a git repo
            result = subprocess.run(
                ['git', 'status', '--porcelain', str(file_path)],
                capture_output=True,
                text=True,
                cwd=file_path.parent,
                timeout=2
            )

            if result.returncode == 0 and result.stdout.strip():
                status = result.stdout.strip()[:2]
                status_map = {
                    'M ': 'modified',
                    ' M': 'modified',
                    'A ': 'added',
                    'D ': 'deleted',
                    'R ': 'renamed',
                    'C ': 'copied',
                    '??': 'untracked'
                }
                return status_map.get(status, 'unknown')
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            # Git not available or not a git repo
            pass

        return None

    def add_bookmark(self, file_path: str, workspace: str,
                    bookmark_name: str = None, tags: List[str] = None) -> bool:
        """
        Add file to bookmarks.

        Args:
            file_path: Path to file
            workspace: Workspace name
            bookmark_name: Optional custom name for bookmark
            tags: Optional list of tags

        Returns:
            True if bookmark added successfully
        """
        tags_str = ','.join(tags) if tags else ''

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO file_bookmarks
                    (file_path, workspace, bookmark_name, tags)
                    VALUES (?, ?, ?, ?)
                """, (file_path, workspace, bookmark_name, tags_str))
            return True
        except Exception:
            return False

    def get_bookmarks(self, workspace: str = None) -> List[Dict]:
        """
        Get bookmarked files.

        Args:
            workspace: Filter by workspace (None for all)

        Returns:
            List of bookmark dictionaries
        """
        query = "SELECT * FROM file_bookmarks"
        params = []

        if workspace:
            query += " WHERE workspace = ?"
            params.append(workspace)

        query += " ORDER BY created_time DESC"

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)

            bookmarks = []
            for row in cursor:
                bookmark = dict(row)
                bookmark['tags'] = bookmark['tags'].split(',') if bookmark['tags'] else []

                # Check if file still exists
                full_path = self.workspace_manager.get_workspace_path(
                    bookmark['workspace']
                ) / bookmark['file_path']
                bookmark['exists'] = full_path.exists()

                bookmarks.append(bookmark)

            return bookmarks

    def remove_bookmark(self, file_path: str, workspace: str) -> bool:
        """Remove file from bookmarks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM file_bookmarks
                    WHERE file_path = ? AND workspace = ?
                """, (file_path, workspace))
                return cursor.rowcount > 0
        except Exception:
            return False
