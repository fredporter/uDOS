"""
uDOS v1.0.6 - Command History System
Provides intelligent command history with persistent storage, search, and smart suggestions
"""

import sqlite3
import os
import json
import time
import difflib
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from prompt_toolkit.history import History


class CommandHistory(History):
    """
    Advanced command history with persistent SQLite storage, intelligent search,
    and context-aware suggestions. Replaces basic InMemoryHistory.
    """

    def __init__(self, history_file: str = None, max_entries: int = 10000):
        """
        Initialize enhanced history system.

        Args:
            history_file: Path to SQLite database file
            max_entries: Maximum number of entries to keep
        """
        self.max_entries = max_entries
        self._loaded = False  # Required by prompt_toolkit History interface

        # Default history location
        if history_file is None:
            history_dir = Path("memory/logs")
            history_dir.mkdir(parents=True, exist_ok=True)
            history_file = str(history_dir / "command_history.db")

        self.db_path = history_file
        self._init_database()

        # In-memory cache for fast access
        self._entries_cache = []
        self._load_cache()

        # Search and suggestion settings
        self.fuzzy_threshold = 0.6
        self.max_suggestions = 10
        self._loaded = True  # Mark as loaded after initialization

    def _init_database(self):
        """Initialize SQLite database with proper schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    session_id TEXT,
                    command_type TEXT,
                    execution_time REAL,
                    success BOOLEAN,
                    frequency INTEGER DEFAULT 1,
                    last_used REAL NOT NULL,
                    context TEXT
                )
            ''')

            # Create indexes for fast searching
            conn.execute('CREATE INDEX IF NOT EXISTS idx_command ON command_history(command)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON command_history(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_frequency ON command_history(frequency)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_last_used ON command_history(last_used)')

            conn.commit()

    def _load_cache(self):
        """Load recent entries into memory cache for fast access."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT command, timestamp, frequency
                FROM command_history
                ORDER BY last_used DESC
                LIMIT ?
            ''', (self.max_entries,))

            self._entries_cache = [row[0] for row in cursor.fetchall()]

    async def load(self):
        """
        Async load method required by prompt_toolkit History interface.
        Yields commands from the cache.
        """
        if not self._loaded:
            return

        for command in self._entries_cache:
            yield command

    def append_string(self, string: str) -> None:
        """
        Add a command to history with intelligent deduplication and metadata.

        Args:
            string: Command string to add
        """
        if not string.strip():
            return

        command = string.strip()
        current_time = time.time()

        # Extract command type for categorization
        command_type = self._extract_command_type(command)

        with sqlite3.connect(self.db_path) as conn:
            # Check if command exists recently (within 5 minutes)
            cursor = conn.execute('''
                SELECT id, frequency FROM command_history
                WHERE command = ? AND timestamp > ?
                ORDER BY timestamp DESC LIMIT 1
            ''', (command, current_time - 300))

            existing = cursor.fetchone()

            if existing:
                # Update frequency and last_used for existing recent command
                conn.execute('''
                    UPDATE command_history
                    SET frequency = frequency + 1, last_used = ?
                    WHERE id = ?
                ''', (current_time, existing[0]))
            else:
                # Insert new command
                conn.execute('''
                    INSERT INTO command_history
                    (command, timestamp, command_type, last_used)
                    VALUES (?, ?, ?, ?)
                ''', (command, current_time, command_type, current_time))

            conn.commit()

        # Update cache
        if command not in self._entries_cache[:10]:  # Only update if not in recent cache
            self._entries_cache.insert(0, command)
            self._entries_cache = self._entries_cache[:self.max_entries]

        # Cleanup old entries if needed
        self._cleanup_old_entries()

    def _extract_command_type(self, command: str) -> str:
        """Extract the primary command type for categorization."""
        parts = command.upper().split()
        if not parts:
            return "UNKNOWN"

        # Handle multi-word commands
        if len(parts) >= 2:
            two_word = f"{parts[0]} {parts[1]}"
            if two_word in ["GRID PANEL", "POKE LIST", "POKE START", "POKE STOP",
                           "POKE STATUS", "POKE HEALTH", "POKE RESTART"]:
                return two_word

        return parts[0]

    def _cleanup_old_entries(self):
        """Remove old entries to maintain max_entries limit."""
        with sqlite3.connect(self.db_path) as conn:
            # Keep only the most recent max_entries based on last_used
            conn.execute('''
                DELETE FROM command_history
                WHERE id NOT IN (
                    SELECT id FROM command_history
                    ORDER BY last_used DESC
                    LIMIT ?
                )
            ''', (self.max_entries,))
            conn.commit()

    def __iter__(self):
        """Iterate through history entries (required by prompt_toolkit)."""
        return iter(self._entries_cache)

    def __getitem__(self, index: int) -> str:
        """Get history entry by index (required by prompt_toolkit)."""
        return self._entries_cache[index]

    def __len__(self) -> int:
        """Get number of entries in cache (required by prompt_toolkit)."""
        return len(self._entries_cache)

    def load_history_strings(self) -> List[str]:
        """Load history entries as strings (required by prompt_toolkit)."""
        return self._entries_cache

    def store_string(self, string: str) -> None:
        """Store a history entry (required by prompt_toolkit)."""
        self.append_string(string)

    def search_history(self, query: str, limit: int = 20) -> List[Tuple[str, float, int]]:
        """
        Search command history with intelligent ranking.

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of (command, score, frequency) tuples, ordered by relevance
        """
        if not query.strip():
            return []

        query = query.strip().lower()
        results = []

        with sqlite3.connect(self.db_path) as conn:
            # Full-text search with frequency weighting
            cursor = conn.execute('''
                SELECT DISTINCT command, frequency, last_used
                FROM command_history
                WHERE LOWER(command) LIKE ?
                ORDER BY frequency DESC, last_used DESC
                LIMIT ?
            ''', (f'%{query}%', limit * 2))  # Get more to filter better

            for command, frequency, last_used in cursor.fetchall():
                # Calculate relevance score
                score = self._calculate_relevance_score(command, query, frequency, last_used)
                if score > 0.1:  # Minimum relevance threshold
                    results.append((command, score, frequency))

        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _calculate_relevance_score(self, command: str, query: str, frequency: int, last_used: float) -> float:
        """
        Calculate relevance score for search results.

        Factors:
        - Exact match bonus
        - Fuzzy similarity
        - Usage frequency
        - Recency
        """
        command_lower = command.lower()
        query_lower = query.lower()

        # Exact match gets highest score
        if query_lower == command_lower:
            return 1.0

        # Prefix match gets high score
        if command_lower.startswith(query_lower):
            prefix_score = 0.8
        else:
            prefix_score = 0.0

        # Fuzzy similarity using difflib
        similarity = difflib.SequenceMatcher(None, query_lower, command_lower).ratio()

        # Frequency boost (log scale to prevent dominance)
        frequency_score = min(1.0, frequency / 10.0)

        # Recency boost (commands used in last day get boost)
        current_time = time.time()
        days_ago = (current_time - last_used) / 86400  # Convert to days
        recency_score = max(0.0, 1.0 - (days_ago / 7.0))  # Decay over a week

        # Combine scores with weights
        final_score = (
            prefix_score * 0.4 +
            similarity * 0.3 +
            frequency_score * 0.2 +
            recency_score * 0.1
        )

        return final_score

    def get_suggestions(self, partial_command: str, limit: int = 5) -> List[str]:
        """
        Get intelligent command suggestions based on partial input.

        Args:
            partial_command: Partial command being typed
            limit: Maximum suggestions to return

        Returns:
            List of suggested completions
        """
        if not partial_command.strip():
            # Return recent frequent commands
            return self._get_frequent_commands(limit)

        # Search for matches
        results = self.search_history(partial_command, limit)
        return [cmd for cmd, score, freq in results]

    def _get_frequent_commands(self, limit: int) -> List[str]:
        """Get most frequently used commands."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT DISTINCT command
                FROM command_history
                ORDER BY frequency DESC, last_used DESC
                LIMIT ?
            ''', (limit,))

            return [row[0] for row in cursor.fetchall()]

    def get_command_stats(self) -> Dict:
        """Get statistics about command usage."""
        with sqlite3.connect(self.db_path) as conn:
            # Total commands
            total = conn.execute('SELECT COUNT(*) FROM command_history').fetchone()[0]

            # Unique commands
            unique = conn.execute('SELECT COUNT(DISTINCT command) FROM command_history').fetchone()[0]

            # Most frequent command types
            cursor = conn.execute('''
                SELECT command_type, COUNT(*) as count
                FROM command_history
                GROUP BY command_type
                ORDER BY count DESC
                LIMIT 5
            ''')
            top_types = cursor.fetchall()

            # Recent activity (last 24 hours)
            recent_cutoff = time.time() - 86400
            recent = conn.execute(
                'SELECT COUNT(*) FROM command_history WHERE timestamp > ?',
                (recent_cutoff,)
            ).fetchone()[0]

            return {
                'total_commands': total,
                'unique_commands': unique,
                'recent_activity': recent,
                'top_command_types': top_types,
                'database_path': self.db_path
            }

    def export_history(self, filepath: str, format: str = 'json') -> bool:
        """
        Export command history to file.

        Args:
            filepath: Output file path
            format: Export format ('json', 'csv', 'txt')

        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT command, timestamp, command_type, frequency, last_used
                    FROM command_history
                    ORDER BY timestamp DESC
                ''')

                data = cursor.fetchall()

                if format == 'json':
                    export_data = []
                    for row in data:
                        export_data.append({
                            'command': row[0],
                            'timestamp': datetime.fromtimestamp(row[1]).isoformat(),
                            'command_type': row[2],
                            'frequency': row[3],
                            'last_used': datetime.fromtimestamp(row[4]).isoformat()
                        })

                    with open(filepath, 'w') as f:
                        json.dump(export_data, f, indent=2)

                elif format == 'txt':
                    with open(filepath, 'w') as f:
                        for row in data:
                            timestamp = datetime.fromtimestamp(row[1]).strftime('%Y-%m-%d %H:%M:%S')
                            f.write(f"{timestamp} | {row[0]}\n")

                return True

        except Exception as e:
            print(f"Export failed: {e}")
            return False

    def clear_history(self, older_than_days: int = None) -> int:
        """
        Clear command history.

        Args:
            older_than_days: Only clear entries older than this many days

        Returns:
            Number of entries removed
        """
        with sqlite3.connect(self.db_path) as conn:
            if older_than_days:
                cutoff_time = time.time() - (older_than_days * 86400)
                cursor = conn.execute(
                    'DELETE FROM command_history WHERE timestamp < ?',
                    (cutoff_time,)
                )
            else:
                cursor = conn.execute('DELETE FROM command_history')

            deleted_count = cursor.rowcount
            conn.commit()

        # Reload cache
        self._load_cache()

        return deleted_count
