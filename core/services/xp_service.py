"""
Experience Point System for uDOS v1.0.18
Tracks XP across categories, manages skill trees, and handles achievements.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum


class XPCategory(Enum):
    """XP earning categories"""
    USAGE = "usage"              # Time spent using uDOS
    INFORMATION = "information"  # Knowledge consumed
    CONTRIBUTION = "contribution"  # Knowledge/skills/resources added
    CONNECTION = "connection"    # Network of trusted contacts


class SkillTree(Enum):
    """Survival skill categories"""
    SHELTER = "shelter"      # Building, construction
    FOOD = "food"            # Gardening, foraging, preservation
    WATER = "water"          # Collection, purification, storage
    MEDICINE = "medicine"    # First aid, herbal remedies
    DEFENSE = "defense"      # Security, protection
    TOOLS = "tools"          # Crafting, repair


class XPService:
    """
    Manages experience points, skill progression, and achievements.

    XP Flow:
    1. Award XP for actions (command usage, reading, contributing)
    2. XP accumulates in categories
    3. Skills level up when category XP reaches thresholds
    4. Achievements unlock at milestones
    """

    def __init__(self, db_path: str = "memory/xp.db"):
        """Initialize XP service with database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # XP transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS xp_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                amount INTEGER NOT NULL,
                reason TEXT,
                context TEXT
            )
        """)

        # Skills table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                skill TEXT PRIMARY KEY,
                level INTEGER DEFAULT 1,
                xp INTEGER DEFAULT 0,
                last_updated TEXT
            )
        """)

        # Achievements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                unlocked INTEGER DEFAULT 0,
                unlocked_at TEXT,
                requirement TEXT
            )
        """)

        # Initialize default skills
        for skill in SkillTree:
            cursor.execute("""
                INSERT OR IGNORE INTO skills (skill, level, xp, last_updated)
                VALUES (?, 1, 0, ?)
            """, (skill.value, datetime.now().isoformat()))

        # Initialize default achievements
        self._init_achievements(cursor)

        conn.commit()
        conn.close()

    def _init_achievements(self, cursor):
        """Initialize default achievements"""
        achievements = [
            ("first_command", "First Steps", "Execute your first uDOS command", "usage:1"),
            ("novice_user", "Novice User", "Earn 100 Usage XP", "usage:100"),
            ("apprentice_user", "Apprentice User", "Earn 500 Usage XP", "usage:500"),
            ("expert_user", "Expert User", "Earn 2000 Usage XP", "usage:2000"),
            ("master_user", "Master User", "Earn 5000 Usage XP", "usage:5000"),

            ("knowledge_seeker", "Knowledge Seeker", "Read your first survival guide", "information:1"),
            ("student", "Student", "Earn 100 Information XP", "information:100"),
            ("scholar", "Scholar", "Earn 500 Information XP", "information:500"),
            ("sage", "Sage", "Earn 2000 Information XP", "information:2000"),

            ("contributor", "Contributor", "Add your first knowledge", "contribution:1"),
            ("benefactor", "Benefactor", "Earn 100 Contribution XP", "contribution:100"),
            ("patron", "Patron", "Earn 500 Contribution XP", "contribution:500"),

            ("networker", "Networker", "Make your first connection", "connection:1"),
            ("community_member", "Community Member", "Earn 100 Connection XP", "connection:100"),

            ("shelter_novice", "Shelter Novice", "Reach level 5 in Shelter", "skill:shelter:5"),
            ("food_novice", "Food Novice", "Reach level 5 in Food", "skill:food:5"),
            ("water_novice", "Water Novice", "Reach level 5 in Water", "skill:water:5"),
            ("medicine_novice", "Medicine Novice", "Reach level 5 in Medicine", "skill:medicine:5"),
            ("defense_novice", "Defense Novice", "Reach level 5 in Defense", "skill:defense:5"),
            ("tools_novice", "Tools Novice", "Reach level 5 in Tools", "skill:tools:5"),

            ("survivalist", "Survivalist", "Reach level 10 in any skill", "skill:any:10"),
            ("jack_of_trades", "Jack of Trades", "Reach level 5 in all skills", "skills:all:5"),
            ("master_survivalist", "Master Survivalist", "Reach level 20 in any skill", "skill:any:20"),
        ]

        for ach_id, name, desc, req in achievements:
            cursor.execute("""
                INSERT OR IGNORE INTO achievements (id, name, description, requirement)
                VALUES (?, ?, ?, ?)
            """, (ach_id, name, desc, req))

    def award_xp(self, category: XPCategory, amount: int, reason: str = "", context: str = "") -> Dict:
        """
        Award XP to a category.

        Args:
            category: XP category
            amount: XP amount to award
            reason: Why XP was awarded
            context: Additional context (command, guide, etc)

        Returns:
            Dict with award details and any achievements unlocked
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Record transaction
        cursor.execute("""
            INSERT INTO xp_transactions (timestamp, category, amount, reason, context)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), category.value, amount, reason, context))

        conn.commit()

        # Check for achievements (pass total XP after this transaction)
        total_xp = self.get_category_xp(category)
        achievements_unlocked = self._check_achievements(cursor, category, total_xp)

        # Commit achievement unlocks
        conn.commit()
        conn.close()

        return {
            "category": category.value,
            "amount": amount,
            "reason": reason,
            "total_xp": self.get_category_xp(category),
            "achievements": achievements_unlocked
        }

    def get_category_xp(self, category: XPCategory) -> int:
        """Get total XP for a category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT SUM(amount) FROM xp_transactions WHERE category = ?
        """, (category.value,))

        result = cursor.fetchone()[0]
        conn.close()

        return result if result else 0

    def get_total_xp(self) -> int:
        """Get total XP across all categories"""
        return sum(self.get_category_xp(cat) for cat in XPCategory)

    def get_xp_breakdown(self) -> Dict[str, int]:
        """Get XP breakdown by category"""
        return {cat.value: self.get_category_xp(cat) for cat in XPCategory}

    def update_skill_xp(self, skill: SkillTree, xp_amount: int) -> Dict:
        """
        Add XP to a skill and handle level ups.

        Args:
            skill: Skill to update
            xp_amount: XP to add

        Returns:
            Dict with skill status and level up info
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current skill data
        cursor.execute("SELECT level, xp FROM skills WHERE skill = ?", (skill.value,))
        current_level, current_xp = cursor.fetchone()

        # Add XP
        new_xp = current_xp + xp_amount

        # Calculate level (exponential growth: level N requires N^2 * 100 XP)
        new_level = self._calculate_level(new_xp)
        leveled_up = new_level > current_level

        # Update database
        cursor.execute("""
            UPDATE skills
            SET level = ?, xp = ?, last_updated = ?
            WHERE skill = ?
        """, (new_level, new_xp, datetime.now().isoformat(), skill.value))

        conn.commit()

        # Check for skill-based achievements
        achievements = self._check_skill_achievements(cursor, skill, new_level)

        conn.close()

        return {
            "skill": skill.value,
            "previous_level": current_level,
            "new_level": new_level,
            "leveled_up": leveled_up,
            "xp": new_xp,
            "next_level_xp": self._xp_for_level(new_level + 1),
            "achievements": achievements
        }

    def _calculate_level(self, xp: int) -> int:
        """
        Calculate level from XP.
        Level N starts at (N-1)^2 * 100 XP.
        E.g., Level 1: 0-99 XP, Level 2: 100-399 XP, Level 3: 400-899 XP
        """
        level = 1
        while level ** 2 * 100 <= xp:
            level += 1
        return level

    def _xp_for_level(self, level: int) -> int:
        """Calculate XP where level starts (not ends)"""
        return (level - 1) ** 2 * 100

    def get_skill_status(self, skill: SkillTree) -> Dict:
        """Get current status of a skill"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT level, xp, last_updated FROM skills WHERE skill = ?", (skill.value,))
        level, xp, last_updated = cursor.fetchone()

        conn.close()

        # Calculate XP needed for next level (not cumulative, just the increment)
        current_level_base = self._xp_for_level(level)
        next_level_total = self._xp_for_level(level + 1)
        next_level_increment = next_level_total - current_level_base

        # Progress within current level
        xp_into_level = xp - current_level_base
        progress = xp_into_level / next_level_increment if next_level_increment > 0 else 0

        return {
            "skill": skill.value,
            "level": level,
            "xp": xp,
            "next_level_xp": next_level_increment,  # Show increment, not cumulative
            "progress_percent": int(progress * 100),
            "last_updated": last_updated
        }

    def get_all_skills(self) -> List[Dict]:
        """Get status of all skills"""
        return [self.get_skill_status(skill) for skill in SkillTree]

    def _check_achievements(self, cursor, category: XPCategory, total_xp: int) -> List[Dict]:
        """Check and unlock category-based achievements"""
        unlocked = []        # Get locked achievements for this category
        cursor.execute("""
            SELECT id, name, description, requirement
            FROM achievements
            WHERE unlocked = 0 AND requirement LIKE ?
        """, (f"{category.value}:%",))

        for ach_id, name, desc, req in cursor.fetchall():
            # Parse requirement (e.g., "usage:100")
            req_xp = int(req.split(':')[1])

            if total_xp >= req_xp:
                # Unlock achievement
                cursor.execute("""
                    UPDATE achievements
                    SET unlocked = 1, unlocked_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), ach_id))

                unlocked.append({
                    "id": ach_id,
                    "name": name,
                    "description": desc
                })

        return unlocked

    def _check_skill_achievements(self, cursor, skill: SkillTree, level: int) -> List[Dict]:
        """Check and unlock skill-based achievements"""
        unlocked = []

        # Check skill-specific achievements
        cursor.execute("""
            SELECT id, name, description, requirement
            FROM achievements
            WHERE unlocked = 0 AND (
                requirement LIKE ? OR
                requirement LIKE 'skill:any:%' OR
                requirement LIKE 'skills:all:%'
            )
        """, (f"skill:{skill.value}:%",))

        for ach_id, name, desc, req in cursor.fetchall():
            should_unlock = False

            if req.startswith(f"skill:{skill.value}:"):
                # Specific skill level
                req_level = int(req.split(':')[2])
                should_unlock = level >= req_level

            elif req.startswith("skill:any:"):
                # Any skill reaches level
                req_level = int(req.split(':')[2])
                should_unlock = level >= req_level

            elif req.startswith("skills:all:"):
                # All skills reach level
                req_level = int(req.split(':')[2])
                cursor.execute("SELECT MIN(level) FROM skills")
                min_level = cursor.fetchone()[0]
                should_unlock = min_level >= req_level

            if should_unlock:
                cursor.execute("""
                    UPDATE achievements
                    SET unlocked = 1, unlocked_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), ach_id))

                unlocked.append({
                    "id": ach_id,
                    "name": name,
                    "description": desc
                })

        return unlocked

    def get_achievements(self, unlocked_only: bool = False) -> List[Dict]:
        """Get all achievements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT id, name, description, unlocked, unlocked_at FROM achievements"
        if unlocked_only:
            query += " WHERE unlocked = 1"
        query += " ORDER BY unlocked DESC, id"

        cursor.execute(query)

        achievements = []
        for ach_id, name, desc, unlocked, unlocked_at in cursor.fetchall():
            achievements.append({
                "id": ach_id,
                "name": name,
                "description": desc,
                "unlocked": bool(unlocked),
                "unlocked_at": unlocked_at
            })

        conn.close()
        return achievements

    def get_recent_xp(self, limit: int = 10) -> List[Dict]:
        """Get recent XP transactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, category, amount, reason, context
            FROM xp_transactions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        transactions = []
        for ts, cat, amount, reason, context in cursor.fetchall():
            transactions.append({
                "timestamp": ts,
                "category": cat,
                "amount": amount,
                "reason": reason,
                "context": context
            })

        conn.close()
        return transactions
