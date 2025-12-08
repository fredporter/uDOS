#!/usr/bin/env python3
"""
uDOS v1.0.8 - Knowledge Manager Service

Manages local knowledge base for offline-first learning and reference.
Integrates with ASK command to provide context-aware responses from local content.

Features:
- Markdown file indexing and search
- Full-text search across knowledge base
- Tag system for content organization
- Integration with AI commands for enhanced context
- File change monitoring and auto-reindexing

Version: 1.0.8
Author: Fred Porter
"""

import os
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import re
from dataclasses import dataclass
import time


@dataclass
class KnowledgeItem:
    """Represents a knowledge base item."""
    file_path: str
    title: str
    content: str
    tags: List[str]
    category: str
    last_modified: float
    word_count: int
    checksum: str


class KnowledgeManager:
    """Manages local knowledge base with full-text search and indexing."""

    def __init__(self, knowledge_path: Optional[str] = None):
        """Initialize knowledge manager."""
        if knowledge_path is None:
            # Default to knowledge/ folder in project root
            project_root = Path(__file__).parent.parent.parent
            knowledge_path = project_root / "knowledge"

        self.knowledge_path = Path(knowledge_path)
        self.db_path = self.knowledge_path.parent / "memory" / "user" / "knowledge.db"

        # Ensure directories exist
        self.knowledge_path.mkdir(exist_ok=True)
        self.db_path.parent.mkdir(exist_ok=True)

        # Initialize database
        self._init_database()

        # Load index
        self._indexed_files = {}
        self._load_index()

    def _init_database(self):
        """Initialize SQLite database for knowledge indexing."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    category TEXT NOT NULL,
                    last_modified REAL NOT NULL,
                    word_count INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_title ON knowledge_items(title)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_category ON knowledge_items(category)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_checksum ON knowledge_items(checksum)
            """)

            # Full-text search table
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                    file_path, title, content, tags, category,
                    content='knowledge_items', content_rowid='id'
                )
            """)

            # Triggers to keep FTS table in sync
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_fts_insert AFTER INSERT ON knowledge_items BEGIN
                    INSERT INTO knowledge_fts(rowid, file_path, title, content, tags, category)
                    VALUES (new.id, new.file_path, new.title, new.content, new.tags, new.category);
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_fts_delete AFTER DELETE ON knowledge_items BEGIN
                    DELETE FROM knowledge_fts WHERE rowid = old.id;
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_fts_update AFTER UPDATE ON knowledge_items BEGIN
                    DELETE FROM knowledge_fts WHERE rowid = old.id;
                    INSERT INTO knowledge_fts(rowid, file_path, title, content, tags, category)
                    VALUES (new.id, new.file_path, new.title, new.content, new.tags, new.category);
                END
            """)

            conn.commit()

    def _load_index(self):
        """Load existing index from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT file_path, checksum, last_modified
                FROM knowledge_items
            """)

            for file_path, checksum, last_modified in cursor.fetchall():
                self._indexed_files[file_path] = {
                    'checksum': checksum,
                    'last_modified': last_modified
                }

    def _parse_markdown_file(self, file_path: Path) -> Optional[KnowledgeItem]:
        """Parse a markdown file and extract metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title (first # heading or filename)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else file_path.stem

            # Extract tags from content (hashtag style)
            tags = list(set(re.findall(r'#(\w+)', content)))

            # Determine category from folder structure
            relative_path = file_path.relative_to(self.knowledge_path)
            category = str(relative_path.parent) if relative_path.parent != Path('.') else 'general'

            # Calculate metrics
            word_count = len(content.split())
            checksum = hashlib.md5(content.encode()).hexdigest()
            last_modified = file_path.stat().st_mtime

            return KnowledgeItem(
                file_path=str(file_path),
                title=title,
                content=content,
                tags=tags,
                category=category,
                last_modified=last_modified,
                word_count=word_count,
                checksum=checksum
            )

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def _needs_reindex(self, file_path: Path) -> bool:
        """Check if file needs to be reindexed."""
        file_path_str = str(file_path)

        if file_path_str not in self._indexed_files:
            return True

        current_mtime = file_path.stat().st_mtime
        indexed_mtime = self._indexed_files[file_path_str]['last_modified']

        return current_mtime > indexed_mtime

    def index_knowledge_base(self, force_reindex: bool = False) -> Dict[str, int]:
        """Index all markdown files in knowledge base."""
        stats = {
            'total_files': 0,
            'new_files': 0,
            'updated_files': 0,
            'deleted_files': 0,
            'errors': 0
        }

        # Find all markdown files
        markdown_files = set()
        for pattern in ['**/*.md', '**/*.markdown']:
            markdown_files.update(self.knowledge_path.glob(pattern))

        stats['total_files'] = len(markdown_files)

        with sqlite3.connect(self.db_path) as conn:
            # Track which files we've seen
            processed_files = set()

            for file_path in markdown_files:
                try:
                    file_path_str = str(file_path)
                    processed_files.add(file_path_str)

                    # Check if needs indexing
                    if not force_reindex and not self._needs_reindex(file_path):
                        continue

                    # Parse file
                    item = self._parse_markdown_file(file_path)
                    if not item:
                        stats['errors'] += 1
                        continue

                    # Check if exists
                    cursor = conn.execute(
                        "SELECT id FROM knowledge_items WHERE file_path = ?",
                        (file_path_str,)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing
                        conn.execute("""
                            UPDATE knowledge_items SET
                                title = ?, content = ?, tags = ?, category = ?,
                                last_modified = ?, word_count = ?, checksum = ?
                            WHERE file_path = ?
                        """, (
                            item.title, item.content, json.dumps(item.tags),
                            item.category, item.last_modified, item.word_count,
                            item.checksum, file_path_str
                        ))
                        stats['updated_files'] += 1
                    else:
                        # Insert new
                        conn.execute("""
                            INSERT INTO knowledge_items (
                                file_path, title, content, tags, category,
                                last_modified, word_count, checksum, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            file_path_str, item.title, item.content,
                            json.dumps(item.tags), item.category,
                            item.last_modified, item.word_count, item.checksum,
                            time.time()
                        ))
                        stats['new_files'] += 1

                    # Update local index
                    self._indexed_files[file_path_str] = {
                        'checksum': item.checksum,
                        'last_modified': item.last_modified
                    }

                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")
                    stats['errors'] += 1

            # Remove deleted files
            cursor = conn.execute("SELECT file_path FROM knowledge_items")
            indexed_files = [row[0] for row in cursor.fetchall()]

            for file_path_str in indexed_files:
                if file_path_str not in processed_files:
                    conn.execute("DELETE FROM knowledge_items WHERE file_path = ?", (file_path_str,))
                    if file_path_str in self._indexed_files:
                        del self._indexed_files[file_path_str]
                    stats['deleted_files'] += 1

            conn.commit()

        return stats

    def search(self, query: str, limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Search knowledge base with full-text search."""
        results = []

        with sqlite3.connect(self.db_path) as conn:
            # Build FTS query
            if category:
                sql = """
                    SELECT k.file_path, k.title, k.content, k.tags, k.category,
                           k.word_count, bm25(knowledge_fts) as score
                    FROM knowledge_fts f
                    JOIN knowledge_items k ON k.id = f.rowid
                    WHERE knowledge_fts MATCH ? AND k.category = ?
                    ORDER BY score
                    LIMIT ?
                """
                params = (query, category, limit)
            else:
                sql = """
                    SELECT k.file_path, k.title, k.content, k.tags, k.category,
                           k.word_count, bm25(knowledge_fts) as score
                    FROM knowledge_fts f
                    JOIN knowledge_items k ON k.id = f.rowid
                    WHERE knowledge_fts MATCH ?
                    ORDER BY score
                    LIMIT ?
                """
                params = (query, limit)

            cursor = conn.execute(sql, params)

            for row in cursor.fetchall():
                file_path, title, content, tags_json, category, word_count, score = row

                # Extract snippet around matching terms
                snippet = self._extract_snippet(content, query)

                results.append({
                    'file_path': file_path,
                    'title': title,
                    'snippet': snippet,
                    'tags': json.loads(tags_json) if tags_json else [],
                    'category': category,
                    'word_count': word_count,
                    'score': score
                })

        return results

    def _extract_snippet(self, content: str, query: str, snippet_length: int = 200) -> str:
        """Extract a snippet around the first match of query terms."""
        # Simple snippet extraction - find first occurrence of any query term
        words = query.lower().split()
        content_lower = content.lower()

        earliest_pos = len(content)
        for word in words:
            pos = content_lower.find(word)
            if pos != -1 and pos < earliest_pos:
                earliest_pos = pos

        if earliest_pos == len(content):
            # No match found, return beginning
            return content[:snippet_length] + ("..." if len(content) > snippet_length else "")

        # Extract snippet around match
        start = max(0, earliest_pos - snippet_length // 2)
        end = start + snippet_length
        snippet = content[start:end]

        # Clean up
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def get_by_category(self, category: str) -> List[Dict]:
        """Get all knowledge items in a category."""
        results = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT file_path, title, tags, word_count, last_modified
                FROM knowledge_items
                WHERE category = ?
                ORDER BY title
            """, (category,))

            for row in cursor.fetchall():
                file_path, title, tags_json, word_count, last_modified = row
                results.append({
                    'file_path': file_path,
                    'title': title,
                    'tags': json.loads(tags_json) if tags_json else [],
                    'word_count': word_count,
                    'last_modified': datetime.fromtimestamp(last_modified).isoformat()
                })

        return results

    def get_categories(self) -> List[Dict]:
        """Get all categories with counts."""
        categories = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count, SUM(word_count) as total_words
                FROM knowledge_items
                GROUP BY category
                ORDER BY category
            """)

            for category, count, total_words in cursor.fetchall():
                categories.append({
                    'category': category,
                    'count': count,
                    'total_words': total_words or 0
                })

        return categories

    def get_statistics(self) -> Dict:
        """Get knowledge base statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total_items,
                    SUM(word_count) as total_words,
                    COUNT(DISTINCT category) as total_categories,
                    MAX(last_modified) as last_updated
                FROM knowledge_items
            """)

            row = cursor.fetchone()
            total_items, total_words, total_categories, last_updated = row

            return {
                'total_items': total_items or 0,
                'total_words': total_words or 0,
                'total_categories': total_categories or 0,
                'last_updated': datetime.fromtimestamp(last_updated).isoformat() if last_updated else None,
                'database_size': self.db_path.stat().st_size if self.db_path.exists() else 0
            }

    def get_content(self, file_path: str) -> Optional[str]:
        """Get full content of a knowledge item."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT content FROM knowledge_items WHERE file_path = ?",
                (file_path,)
            )
            row = cursor.fetchone()
            return row[0] if row else None


# Global instance
_knowledge_manager = None

def get_knowledge_manager() -> KnowledgeManager:
    """Get global knowledge manager instance."""
    global _knowledge_manager
    if _knowledge_manager is None:
        _knowledge_manager = KnowledgeManager()
    return _knowledge_manager
