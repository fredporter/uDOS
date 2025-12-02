"""
Knowledge Integration Service for v1.0.18
Links knowledge base to XP system with skill-based unlocks
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

try:
    from extensions.play.services.game_mechanics.xp_service import XPService, SkillTree
except ImportError:
    # Fallback if play extension not installed
    XPService = None
    SkillTree = None


class KnowledgeLevel(str):
    """Knowledge access levels based on skill progression"""
    PUBLIC = "public"           # Available to all
    BASIC = "basic"             # Skill level 1+
    INTERMEDIATE = "intermediate"  # Skill level 3+
    ADVANCED = "advanced"       # Skill level 5+
    EXPERT = "expert"           # Skill level 8+
    MASTER = "master"           # Skill level 10+


class KnowledgeService:
    """
    Manages knowledge access, tracking, and XP integration

    Features:
    - Skill-based knowledge unlocking
    - Reading progress tracking
    - XP rewards for knowledge consumption
    - Knowledge contribution system
    - Search with skill filters
    """

    def __init__(self, data_dir: str = "data", knowledge_dir: str = "knowledge"):
        """Initialize knowledge service"""
        self.data_dir = data_dir
        self.knowledge_dir = knowledge_dir

        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "knowledge.db")

        self._init_database()

    def _init_database(self):
        """Create knowledge tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Knowledge items with metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                title TEXT,
                category TEXT,
                skill_tree TEXT,
                required_level INTEGER DEFAULT 0,
                xp_value INTEGER DEFAULT 10,
                word_count INTEGER DEFAULT 0,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Reading history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reading_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER,
                read_at TEXT DEFAULT CURRENT_TIMESTAMP,
                time_spent_seconds INTEGER DEFAULT 0,
                completion_percent INTEGER DEFAULT 0,
                xp_awarded INTEGER DEFAULT 0,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge_items(id)
            )
        """)

        # Knowledge contributions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_contributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER,
                contribution_type TEXT,
                description TEXT,
                contributed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                xp_awarded INTEGER DEFAULT 0,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge_items(id)
            )
        """)

        # Knowledge unlocks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_unlocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                unlock_method TEXT,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge_items(id)
            )
        """)

        conn.commit()
        conn.close()

    def index_knowledge_base(self) -> Dict[str, Any]:
        """
        Scan knowledge directory and index all markdown files

        Returns:
            Dict with indexing results
        """
        if not os.path.exists(self.knowledge_dir):
            return {"error": "Knowledge directory not found"}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        indexed = 0
        errors = []

        for root, dirs, files in os.walk(self.knowledge_dir):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, self.knowledge_dir)

                    try:
                        # Extract metadata from file
                        metadata = self._extract_metadata(filepath)

                        # Determine skill tree from path
                        skill_tree = self._determine_skill_tree(rel_path)

                        # Insert or update
                        cursor.execute("""
                            INSERT INTO knowledge_items
                            (path, title, category, skill_tree, required_level,
                             xp_value, word_count, tags)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(path) DO UPDATE SET
                                title = excluded.title,
                                category = excluded.category,
                                skill_tree = excluded.skill_tree,
                                word_count = excluded.word_count,
                                last_updated = CURRENT_TIMESTAMP
                        """, (
                            rel_path,
                            metadata.get('title', filename),
                            metadata.get('category', 'general'),
                            skill_tree,
                            metadata.get('required_level', 0),
                            metadata.get('xp_value', 10),
                            metadata.get('word_count', 0),
                            json.dumps(metadata.get('tags', []))
                        ))

                        indexed += 1

                    except Exception as e:
                        errors.append(f"{rel_path}: {str(e)}")

        conn.commit()
        conn.close()

        return {
            "indexed": indexed,
            "errors": errors if errors else None,
            "total_items": self.get_total_knowledge_count()
        }

    def _extract_metadata(self, filepath: str) -> Dict[str, Any]:
        """Extract metadata from markdown file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count words
        word_count = len(content.split())

        # Extract title (first # heading)
        title = None
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # Extract tags from front matter or content
        tags = []
        if '---' in content:
            # Simple YAML front matter parsing
            parts = content.split('---')
            if len(parts) >= 2:
                front_matter = parts[1]
                for line in front_matter.split('\n'):
                    if 'tags:' in line.lower():
                        # Extract tags
                        tags_str = line.split(':', 1)[1].strip()
                        tags = [t.strip() for t in tags_str.replace('[', '').replace(']', '').split(',')]

        return {
            'title': title or os.path.basename(filepath),
            'word_count': word_count,
            'tags': tags,
            'category': os.path.basename(os.path.dirname(filepath))
        }

    def _determine_skill_tree(self, path: str) -> Optional[str]:
        """Determine which skill tree a knowledge item belongs to"""
        path_lower = path.lower()

        if any(x in path_lower for x in ['building', 'shelter', 'construction']):
            return SkillTree.SHELTER.value
        elif any(x in path_lower for x in ['food', 'garden', 'forage']):
            return SkillTree.FOOD.value
        elif any(x in path_lower for x in ['water', 'purif', 'well']):
            return SkillTree.WATER.value
        elif any(x in path_lower for x in ['medical', 'medicine', 'health', 'first-aid']):
            return SkillTree.MEDICINE.value
        elif any(x in path_lower for x in ['defense', 'security', 'weapon']):
            return SkillTree.DEFENSE.value
        elif any(x in path_lower for x in ['tool', 'craft', 'repair']):
            return SkillTree.TOOLS.value

        return None

    def can_access_knowledge(self, knowledge_id: int, xp_service: XPService) -> Dict[str, Any]:
        """
        Check if player has sufficient skill level to access knowledge

        Args:
            knowledge_id: Knowledge item ID
            xp_service: XPService instance to check skill levels

        Returns:
            Dict with access status and requirements
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT skill_tree, required_level, title
            FROM knowledge_items WHERE id = ?
        """, (knowledge_id,))

        result = cursor.fetchone()
        conn.close()

        if not result:
            return {"error": "Knowledge item not found"}

        skill_tree_str, required_level, title = result

        if not skill_tree_str or required_level == 0:
            return {"access": True, "title": title}

        # Check skill level
        skill_tree = SkillTree(skill_tree_str)
        skill_status = xp_service.get_skill_status(skill_tree)
        current_level = skill_status.get('level', 0)

        has_access = current_level >= required_level

        return {
            "access": has_access,
            "title": title,
            "required_skill": skill_tree_str,
            "required_level": required_level,
            "current_level": current_level,
            "xp_needed": skill_status.get('xp_to_next', 0) if not has_access else 0
        }

    def read_knowledge(self, knowledge_id: int, xp_service: XPService,
                      time_spent_seconds: int = 60) -> Dict[str, Any]:
        """
        Record knowledge reading and award XP

        Args:
            knowledge_id: Knowledge item ID
            xp_service: XPService instance for awarding XP
            time_spent_seconds: Time spent reading

        Returns:
            Dict with reading result and XP awarded
        """
        # Check access
        access = self.can_access_knowledge(knowledge_id, xp_service)
        if not access.get('access'):
            return {"error": "Insufficient skill level", "requirements": access}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get knowledge details
        cursor.execute("""
            SELECT xp_value, title, skill_tree
            FROM knowledge_items WHERE id = ?
        """, (knowledge_id,))

        result = cursor.fetchone()
        if not result:
            conn.close()
            return {"error": "Knowledge item not found"}

        xp_value, title, skill_tree_str = result

        # Calculate XP based on time spent (with diminishing returns)
        base_xp = xp_value
        time_bonus = min(time_spent_seconds // 60, 10)  # Max 10 min bonus
        total_xp = base_xp + time_bonus

        # Award XP
        from core.services.xp_service import XPCategory
        xp_result = xp_service.award_xp(
            category=XPCategory.INFORMATION,
            amount=total_xp,
            reason=f"Read: {title}",
            context=f"knowledge:{knowledge_id}"
        )

        # Record reading
        cursor.execute("""
            INSERT INTO reading_history
            (knowledge_id, time_spent_seconds, completion_percent, xp_awarded)
            VALUES (?, ?, ?, ?)
        """, (knowledge_id, time_spent_seconds, 100, total_xp))

        conn.commit()
        conn.close()

        return {
            "read": True,
            "title": title,
            "xp_awarded": total_xp,
            "skill_tree": skill_tree_str,
            "xp_result": xp_result
        }

    def contribute_knowledge(self, knowledge_id: int, contribution_type: str,
                            description: str, xp_service: XPService) -> Dict[str, Any]:
        """
        Record knowledge contribution and award XP

        Contribution types: correction, addition, example, resource
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Determine XP award based on contribution type
        xp_awards = {
            'correction': 25,
            'addition': 50,
            'example': 35,
            'resource': 40,
            'translation': 60
        }

        xp_value = xp_awards.get(contribution_type, 20)

        # Award XP
        from extensions.play.services.game_mechanics.xp_service import XPCategory
        xp_result = xp_service.award_xp(
            category=XPCategory.CONTRIBUTION,
            amount=xp_value,
            reason=f"Knowledge contribution: {contribution_type}",
            context=f"knowledge:{knowledge_id}"
        )

        # Record contribution
        cursor.execute("""
            INSERT INTO knowledge_contributions
            (knowledge_id, contribution_type, description, xp_awarded)
            VALUES (?, ?, ?, ?)
        """, (knowledge_id, contribution_type, description, xp_value))

        conn.commit()
        conn.close()

        return {
            "contributed": True,
            "type": contribution_type,
            "xp_awarded": xp_value,
            "xp_result": xp_result
        }

    def search_knowledge(self, query: str = "", skill_tree: Optional[SkillTree] = None,
                        max_results: int = 20, xp_service: Optional[XPService] = None) -> List[Dict]:
        """
        Search knowledge base with optional skill filtering

        Args:
            query: Search term
            skill_tree: Filter by skill tree
            max_results: Maximum results to return
            xp_service: If provided, filter by accessible items only
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sql = "SELECT id, title, category, skill_tree, required_level, xp_value, path FROM knowledge_items WHERE 1=1"
        params = []

        if query:
            sql += " AND (title LIKE ? OR category LIKE ? OR tags LIKE ?)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])

        if skill_tree:
            sql += " AND skill_tree = ?"
            params.append(skill_tree.value)

        sql += f" LIMIT {max_results}"

        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()

        items = []
        for row in results:
            item_id, title, category, skill_tree_str, req_level, xp_val, path = row

            item = {
                "id": item_id,
                "title": title,
                "category": category,
                "skill_tree": skill_tree_str,
                "required_level": req_level,
                "xp_value": xp_val,
                "path": path
            }

            # Check access if XP service provided
            if xp_service:
                access = self.can_access_knowledge(item_id, xp_service)
                item["accessible"] = access.get("access", False)
                item["current_level"] = access.get("current_level", 0)

            items.append(item)

        return items

    def get_reading_stats(self) -> Dict[str, Any]:
        """Get reading statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total_reads,
                SUM(xp_awarded) as total_xp,
                SUM(time_spent_seconds) as total_time,
                AVG(completion_percent) as avg_completion
            FROM reading_history
        """)

        result = cursor.fetchone()
        conn.close()

        if not result:
            return {"total_reads": 0, "total_xp": 0, "total_time": 0, "avg_completion": 0}

        return {
            "total_reads": result[0] or 0,
            "total_xp": result[1] or 0,
            "total_time_hours": round((result[2] or 0) / 3600, 2),
            "avg_completion": round(result[3] or 0, 1)
        }

    def get_total_knowledge_count(self) -> int:
        """Get total knowledge items indexed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM knowledge_items")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_knowledge_by_skill(self, skill_tree: SkillTree) -> List[Dict]:
        """Get all knowledge items for a skill tree"""
        return self.search_knowledge(skill_tree=skill_tree, max_results=100)
