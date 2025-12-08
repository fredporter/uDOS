"""
uDOS v1.0.20 - 4-Tier Knowledge Bank Manager
Manages knowledge across 4 privacy tiers with barter exchange system
Extends v1.0.8 KnowledgeManager with tier-based privacy controls
"""

import sqlite3
import hashlib
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from .types import (
    KnowledgeTier, KnowledgeType, KnowledgeItem,
    PrivacySettings, KnowledgeTransaction, TIER_DESCRIPTIONS
)


class TierKnowledgeManager:
    """
    Manages knowledge across 4 privacy tiers with barter system.

    Tier 0 (PERSONAL): Private, encrypted, local-only
    Tier 1 (SHARED): Explicitly shared with specific users
    Tier 2 (GROUP): Community knowledge, anonymous
    Tier 3 (PUBLIC): Global knowledge bank, read-only

    This is separate from the v1.0.8 KnowledgeManager which manages
    the markdown-based public knowledge library.
    """

    def __init__(self, db_path: Optional[Path] = None, user_id: Optional[str] = None):
        """
        Initialize Tier Knowledge Manager.

        Args:
            db_path: Path to tier knowledge database (default: memory/tiers/knowledge.db)
            user_id: Current user ID for privacy controls
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "memory" / "tiers" / "knowledge.db"

        self.db_path = db_path
        self.user_id = user_id or "anonymous"
        self.privacy_settings = PrivacySettings()

        # Create directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Knowledge items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tier_knowledge (
                id TEXT PRIMARY KEY,
                tier INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                author_id TEXT,
                created_at TEXT,
                updated_at TEXT,
                shared_with TEXT,
                group_id TEXT,
                views INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                encrypted INTEGER DEFAULT 0,
                checksum TEXT
            )
        ''')

        # Full-text search index
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS tier_knowledge_fts USING fts5(
                id UNINDEXED,
                title,
                content,
                tags
            )
        ''')

        # Barter transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_barter (
                id TEXT PRIMARY KEY,
                from_user TEXT NOT NULL,
                to_user TEXT NOT NULL,
                offered_knowledge_id TEXT NOT NULL,
                requested_knowledge_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                completed_at TEXT,
                notes TEXT
            )
        ''')

        # Privacy settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tier_privacy (
                user_id TEXT PRIMARY KEY,
                settings TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of content."""
        return hashlib.sha256(content.encode()).hexdigest()

    def add_knowledge(
        self,
        tier: KnowledgeTier,
        knowledge_type: KnowledgeType,
        title: str,
        content: str,
        tags: Optional[List[str]] = None
    ) -> KnowledgeItem:
        """
        Add new knowledge to the specified tier.

        Args:
            tier: Privacy tier (0-3)
            knowledge_type: Type of knowledge
            title: Knowledge title
            content: Knowledge content
            tags: Optional categorization tags

        Returns:
            Created KnowledgeItem
        """
        # Create knowledge item
        item = KnowledgeItem(
            id=str(uuid.uuid4()),
            tier=tier,
            type=knowledge_type,
            title=title,
            content=content,
            tags=tags or [],
            author_id=self.user_id if tier != KnowledgeTier.GROUP else "anonymous",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            checksum=self._calculate_checksum(content)
        )

        # Encrypt if required
        if tier == KnowledgeTier.PERSONAL and self.privacy_settings.encrypt_tier_0:
            item.encrypted = True
        elif tier == KnowledgeTier.SHARED and self.privacy_settings.encrypt_tier_1:
            item.encrypted = True

        # Save to database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        data = item.to_dict()
        cursor.execute('''
            INSERT INTO tier_knowledge (
                id, tier, type, title, content, tags, author_id,
                created_at, updated_at, shared_with, group_id,
                views, rating, encrypted, checksum
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id'], data['tier'], data['type'], data['title'],
            data['content'], data['tags'], data['author_id'],
            data['created_at'], data['updated_at'], data['shared_with'],
            data['group_id'], data['views'], data['rating'],
            data['encrypted'], data['checksum']
        ))

        # Add to FTS index
        cursor.execute('''
            INSERT INTO tier_knowledge_fts (id, title, content, tags)
            VALUES (?, ?, ?, ?)
        ''', (item.id, item.title, item.content, ','.join(item.tags)))

        conn.commit()
        conn.close()

        return item

    def search_knowledge(
        self,
        query: str,
        tier: Optional[KnowledgeTier] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[KnowledgeItem]:
        """
        Search knowledge across accessible tiers.

        Args:
            query: Search query
            tier: Filter by specific tier (None = all accessible)
            tags: Filter by tags
            limit: Maximum results to return

        Returns:
            List of matching KnowledgeItem objects
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query - FTS5 table columns are id, title, content, tags
        sql = '''
            SELECT k.* FROM tier_knowledge k
            JOIN tier_knowledge_fts fts ON k.id = fts.id
            WHERE tier_knowledge_fts MATCH ?
        '''
        params = [query]

        # Filter by tier
        if tier is not None:
            sql += ' AND k.tier = ?'
            params.append(tier.value)

        # Filter by tags
        if tags:
            tag_conditions = ' OR '.join(['k.tags LIKE ?' for _ in tags])
            sql += f' AND ({tag_conditions})'
            params.extend([f'%{tag}%' for tag in tags])

        sql += ' ORDER BY k.created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        # Convert to KnowledgeItem objects
        results = [KnowledgeItem.from_dict(dict(row)) for row in rows]

        return results

    def get_knowledge(self, knowledge_id: str) -> Optional[KnowledgeItem]:
        """
        Get specific knowledge item by ID.

        Args:
            knowledge_id: Knowledge item ID

        Returns:
            KnowledgeItem or None if not found/accessible
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Increment view count first
        cursor.execute('UPDATE tier_knowledge SET views = views + 1 WHERE id = ?', (knowledge_id,))
        conn.commit()

        # Then get the item
        cursor.execute('SELECT * FROM tier_knowledge WHERE id = ?', (knowledge_id,))
        row = cursor.fetchone()

        conn.close()

        if not row:
            return None

        item = KnowledgeItem.from_dict(dict(row))

        return item

    def get_tier_stats(self) -> Dict[str, Any]:
        """
        Get statistics about knowledge in each tier.

        Returns:
            Dictionary with tier statistics
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        stats = {}

        for tier in KnowledgeTier:
            cursor.execute('''
                SELECT COUNT(*), AVG(views), SUM(CASE WHEN author_id = ? THEN 1 ELSE 0 END)
                FROM tier_knowledge WHERE tier = ?
            ''', (self.user_id, tier.value))

            total, avg_views, owned = cursor.fetchone()

            stats[tier.name] = {
                'total': total or 0,
                'avg_views': avg_views or 0.0,
                'owned': owned or 0,
                'description': TIER_DESCRIPTIONS[tier]
            }

        conn.close()

        return stats
