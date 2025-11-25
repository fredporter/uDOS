"""
Test Suite for v1.1.3.1 - XP & Achievement System
Tests: Experience points, achievements, skill progression, competence tracking

Test Coverage (55 tests total):
- XP System: 12 tests
- Achievement System: 10 tests
- Skill Progression: 10 tests
- Competence Tracking: 8 tests
- Leaderboards: 7 tests
- Integration: 8 tests

Author: uDOS Development Team
Version: 1.1.3.1
Date: 2025-11-24
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))


class XPCategory:
    """XP earning categories"""
    USAGE = "usage"           # Using commands, features
    INFORMATION = "information"  # Reading guides, learning
    CONTRIBUTION = "contribution"  # Sharing knowledge, helping others


class XPEvent:
    """Represents an XP earning event"""

    def __init__(self, category: str, amount: int, source: str,
                 user_id: str, timestamp: float = None):
        self.category = category
        self.amount = amount
        self.source = source  # Command, guide, contribution type
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now().timestamp()

    def to_dict(self):
        return {
            'category': self.category,
            'amount': self.amount,
            'source': self.source,
            'user_id': self.user_id,
            'timestamp': self.timestamp
        }


class XPSystem:
    """Experience point tracking and management"""

    XP_VALUES = {
        # Usage category
        'command_execute': 1,
        'command_master': 50,  # Execute same command 100 times
        'feature_discovery': 10,
        'daily_login': 5,
        'streak_bonus': 25,  # 7-day streak

        # Information category
        'guide_read': 5,
        'guide_complete': 15,
        'skill_learn': 20,
        'quiz_pass': 30,
        'certification': 100,

        # Contribution category
        'knowledge_share': 25,
        'guide_create': 50,
        'code_submit': 40,
        'bug_report': 15,
        'help_user': 20,
        'trade_complete': 10,
        'mission_contribute': 35,
    }

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.total_xp = 0
        self.category_xp = {
            XPCategory.USAGE: 0,
            XPCategory.INFORMATION: 0,
            XPCategory.CONTRIBUTION: 0
        }
        self.events = []
        self.level = 1
        self.streak_days = 0
        self.last_activity = None

    def award_xp(self, category: str, source: str, multiplier: float = 1.0) -> int:
        """Award XP for an action"""
        base_xp = self.XP_VALUES.get(source, 0)
        amount = int(base_xp * multiplier)

        event = XPEvent(category, amount, source, self.user_id)
        self.events.append(event)

        self.total_xp += amount
        self.category_xp[category] = self.category_xp.get(category, 0) + amount

        # Check for level up
        self._check_level_up()

        return amount

    def _check_level_up(self):
        """Check if user leveled up (100 XP per level)"""
        new_level = (self.total_xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
            return True
        return False

    def get_level_progress(self) -> Dict:
        """Get current level and progress to next"""
        current_level_xp = (self.level - 1) * 100
        next_level_xp = self.level * 100
        progress = self.total_xp - current_level_xp
        needed = next_level_xp - self.total_xp

        return {
            'level': self.level,
            'progress': progress,
            'needed': needed,
            'percentage': (progress / 100) * 100
        }

    def update_streak(self) -> bool:
        """Update daily login streak"""
        now = datetime.now()

        if self.last_activity is None:
            self.streak_days = 1
            self.last_activity = now
            return True

        last = datetime.fromtimestamp(self.last_activity.timestamp())
        days_since = (now - last).days

        if days_since == 1:
            # Consecutive day
            self.streak_days += 1
            self.last_activity = now

            # Award streak bonus at 7 days
            if self.streak_days % 7 == 0:
                self.award_xp(XPCategory.USAGE, 'streak_bonus')

            return True
        elif days_since > 1:
            # Streak broken
            self.streak_days = 1
            self.last_activity = now
            return False

        return False

    def get_category_breakdown(self) -> Dict:
        """Get XP breakdown by category"""
        total = max(self.total_xp, 1)  # Avoid division by zero
        return {
            'usage': {
                'xp': self.category_xp.get(XPCategory.USAGE, 0),
                'percentage': (self.category_xp.get(XPCategory.USAGE, 0) / total) * 100
            },
            'information': {
                'xp': self.category_xp.get(XPCategory.INFORMATION, 0),
                'percentage': (self.category_xp.get(XPCategory.INFORMATION, 0) / total) * 100
            },
            'contribution': {
                'xp': self.category_xp.get(XPCategory.CONTRIBUTION, 0),
                'percentage': (self.category_xp.get(XPCategory.CONTRIBUTION, 0) / total) * 100
            }
        }


class Achievement:
    """Represents an achievement/badge"""

    def __init__(self, id: str, name: str, description: str,
                 xp_reward: int, condition: Dict):
        self.id = id
        self.name = name
        self.description = description
        self.xp_reward = xp_reward
        self.condition = condition  # {'type': 'xp_total', 'value': 1000}
        self.icon = "🏆"
        self.tier = "bronze"  # bronze, silver, gold, platinum

    def check_unlock(self, user_stats: Dict) -> bool:
        """Check if achievement should unlock"""
        cond_type = self.condition.get('type')
        cond_value = self.condition.get('value')

        if cond_type == 'xp_total':
            return user_stats.get('total_xp', 0) >= cond_value
        elif cond_type == 'xp_category':
            category = self.condition.get('category')
            return user_stats.get('category_xp', {}).get(category, 0) >= cond_value
        elif cond_type == 'level':
            return user_stats.get('level', 1) >= cond_value
        elif cond_type == 'streak':
            return user_stats.get('streak_days', 0) >= cond_value
        elif cond_type == 'guides_read':
            return user_stats.get('guides_read', 0) >= cond_value
        elif cond_type == 'contributions':
            return user_stats.get('contributions', 0) >= cond_value

        return False


class AchievementSystem:
    """Manage achievements and unlocks"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.unlocked = set()
        self.achievements = self._initialize_achievements()
        self.unlock_history = []

    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Create default achievements"""
        return {
            # XP milestones
            'xp_100': Achievement(
                'xp_100', 'First Steps', 'Earn 100 XP',
                10, {'type': 'xp_total', 'value': 100}
            ),
            'xp_1000': Achievement(
                'xp_1000', 'Dedicated', 'Earn 1,000 XP',
                50, {'type': 'xp_total', 'value': 1000}
            ),
            'xp_10000': Achievement(
                'xp_10000', 'Master', 'Earn 10,000 XP',
                200, {'type': 'xp_total', 'value': 10000}
            ),

            # Level milestones
            'level_10': Achievement(
                'level_10', 'Level 10', 'Reach level 10',
                25, {'type': 'level', 'value': 10}
            ),
            'level_50': Achievement(
                'level_50', 'Level 50', 'Reach level 50',
                100, {'type': 'level', 'value': 50}
            ),

            # Streak achievements
            'streak_7': Achievement(
                'streak_7', 'Week Warrior', '7-day streak',
                30, {'type': 'streak', 'value': 7}
            ),
            'streak_30': Achievement(
                'streak_30', 'Month Master', '30-day streak',
                150, {'type': 'streak', 'value': 30}
            ),

            # Category specialists
            'usage_master': Achievement(
                'usage_master', 'Power User', '1,000 Usage XP',
                50, {'type': 'xp_category', 'category': 'usage', 'value': 1000}
            ),
            'info_scholar': Achievement(
                'info_scholar', 'Scholar', '1,000 Information XP',
                50, {'type': 'xp_category', 'category': 'information', 'value': 1000}
            ),
            'contributor': Achievement(
                'contributor', 'Contributor', '1,000 Contribution XP',
                50, {'type': 'xp_category', 'category': 'contribution', 'value': 1000}
            ),
        }

    def check_achievements(self, user_stats: Dict) -> List[Achievement]:
        """Check for newly unlocked achievements"""
        newly_unlocked = []

        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in self.unlocked:
                if achievement.check_unlock(user_stats):
                    self.unlocked.add(achievement_id)
                    self.unlock_history.append({
                        'id': achievement_id,
                        'name': achievement.name,
                        'timestamp': datetime.now().timestamp()
                    })
                    newly_unlocked.append(achievement)

        return newly_unlocked

    def get_progress(self, achievement_id: str, user_stats: Dict) -> Dict:
        """Get progress toward achievement"""
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return {}

        cond_type = achievement.condition.get('type')
        target = achievement.condition.get('value')

        current = 0
        if cond_type == 'xp_total':
            current = user_stats.get('total_xp', 0)
        elif cond_type == 'level':
            current = user_stats.get('level', 1)
        elif cond_type == 'streak':
            current = user_stats.get('streak_days', 0)

        return {
            'achievement': achievement.name,
            'current': current,
            'target': target,
            'percentage': min((current / target) * 100, 100),
            'unlocked': achievement_id in self.unlocked
        }


class SkillTree:
    """Skill progression tree"""

    def __init__(self, name: str):
        self.name = name
        self.skills = {}
        self.unlocked = set()

    def add_skill(self, skill_id: str, name: str,
                  prerequisites: List[str] = None, xp_cost: int = 0):
        """Add skill to tree"""
        self.skills[skill_id] = {
            'name': name,
            'prerequisites': prerequisites or [],
            'xp_cost': xp_cost,
            'level': 0,
            'max_level': 5
        }

    def unlock_skill(self, skill_id: str, current_xp: int) -> bool:
        """Unlock a skill"""
        skill = self.skills.get(skill_id)
        if not skill:
            return False

        # Check prerequisites
        for prereq in skill['prerequisites']:
            if prereq not in self.unlocked:
                return False

        # Check XP requirement
        if current_xp < skill['xp_cost']:
            return False

        self.unlocked.add(skill_id)
        skill['level'] = 1
        return True

    def level_up_skill(self, skill_id: str) -> bool:
        """Increase skill level"""
        if skill_id not in self.unlocked:
            return False

        skill = self.skills[skill_id]
        if skill['level'] < skill['max_level']:
            skill['level'] += 1
            return True

        return False

    def get_available_skills(self) -> List[str]:
        """Get skills that can be unlocked"""
        available = []
        for skill_id, skill in self.skills.items():
            if skill_id not in self.unlocked:
                # Check prerequisites
                prereqs_met = all(p in self.unlocked for p in skill['prerequisites'])
                if prereqs_met:
                    available.append(skill_id)
        return available


class CompetenceTracker:
    """Track user competence across different areas"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.competencies = {
            'survival': 0,
            'technical': 0,
            'social': 0,
            'creative': 0,
            'leadership': 0
        }
        self.skill_uses = {}  # Track frequency of skill usage

    def record_skill_use(self, skill: str, competency: str):
        """Record usage of a skill"""
        self.skill_uses[skill] = self.skill_uses.get(skill, 0) + 1

        # Increase competency (diminishing returns)
        current = self.competencies.get(competency, 0)
        gain = max(1, 10 - (current // 100))  # Less gain at higher levels
        self.competencies[competency] = current + gain

    def get_competency_level(self, competency: str) -> str:
        """Get competency level (novice, intermediate, advanced, expert)"""
        score = self.competencies.get(competency, 0)

        if score >= 1000:
            return 'expert'
        elif score >= 500:
            return 'advanced'
        elif score >= 200:
            return 'intermediate'
        else:
            return 'novice'

    def get_strongest_competencies(self, limit: int = 3) -> List[tuple]:
        """Get top competencies"""
        sorted_comps = sorted(
            self.competencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_comps[:limit]


class Leaderboard:
    """Global and category leaderboards"""

    def __init__(self):
        self.rankings = {}

    def update_ranking(self, user_id: str, total_xp: int,
                       category_xp: Dict, level: int):
        """Update user's ranking"""
        self.rankings[user_id] = {
            'total_xp': total_xp,
            'category_xp': category_xp,
            'level': level,
            'timestamp': datetime.now().timestamp()
        }

    def get_top_users(self, limit: int = 10) -> List[tuple]:
        """Get top users by total XP"""
        sorted_users = sorted(
            self.rankings.items(),
            key=lambda x: x[1]['total_xp'],
            reverse=True
        )
        return [(user_id, data['total_xp'], data['level'])
                for user_id, data in sorted_users[:limit]]

    def get_category_leaders(self, category: str, limit: int = 10) -> List[tuple]:
        """Get top users in a category"""
        sorted_users = sorted(
            self.rankings.items(),
            key=lambda x: x[1]['category_xp'].get(category, 0),
            reverse=True
        )
        return [(user_id, data['category_xp'].get(category, 0))
                for user_id, data in sorted_users[:limit]]

    def get_user_rank(self, user_id: str) -> int:
        """Get user's global rank"""
        sorted_users = sorted(
            self.rankings.items(),
            key=lambda x: x[1]['total_xp'],
            reverse=True
        )
        for rank, (uid, _) in enumerate(sorted_users, 1):
            if uid == user_id:
                return rank
        return -1


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestXPSystem(unittest.TestCase):
    """Test XP system (12 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.xp = XPSystem('user1')

    def test_xp_initialization(self):
        """Test XP system initialization"""
        self.assertEqual(self.xp.total_xp, 0)
        self.assertEqual(self.xp.level, 1)
        self.assertEqual(len(self.xp.events), 0)

    def test_award_xp_usage(self):
        """Test awarding usage XP"""
        amount = self.xp.award_xp(XPCategory.USAGE, 'command_execute')
        self.assertEqual(amount, 1)
        self.assertEqual(self.xp.total_xp, 1)

    def test_award_xp_information(self):
        """Test awarding information XP"""
        amount = self.xp.award_xp(XPCategory.INFORMATION, 'guide_read')
        self.assertEqual(amount, 5)
        self.assertEqual(self.xp.category_xp[XPCategory.INFORMATION], 5)

    def test_award_xp_contribution(self):
        """Test awarding contribution XP"""
        amount = self.xp.award_xp(XPCategory.CONTRIBUTION, 'knowledge_share')
        self.assertEqual(amount, 25)
        self.assertEqual(self.xp.category_xp[XPCategory.CONTRIBUTION], 25)

    def test_xp_multiplier(self):
        """Test XP multiplier"""
        amount = self.xp.award_xp(XPCategory.USAGE, 'command_execute', multiplier=2.0)
        self.assertEqual(amount, 2)

    def test_level_up(self):
        """Test leveling up"""
        # Award 100 XP to reach level 2
        self.xp.award_xp(XPCategory.USAGE, 'certification')  # 100 XP
        self.assertEqual(self.xp.level, 2)

    def test_level_progress(self):
        """Test level progress calculation"""
        self.xp.total_xp = 150
        self.xp.level = 2

        progress = self.xp.get_level_progress()
        self.assertEqual(progress['level'], 2)
        self.assertEqual(progress['progress'], 50)
        self.assertEqual(progress['needed'], 50)

    def test_streak_start(self):
        """Test starting a streak"""
        result = self.xp.update_streak()
        self.assertTrue(result)
        self.assertEqual(self.xp.streak_days, 1)

    def test_streak_continue(self):
        """Test continuing a streak"""
        self.xp.update_streak()
        self.xp.last_activity = datetime.now() - timedelta(days=1)

        result = self.xp.update_streak()
        self.assertTrue(result)
        self.assertEqual(self.xp.streak_days, 2)

    def test_streak_broken(self):
        """Test streak breaking"""
        self.xp.update_streak()
        self.xp.last_activity = datetime.now() - timedelta(days=3)

        result = self.xp.update_streak()
        self.assertFalse(result)
        self.assertEqual(self.xp.streak_days, 1)

    def test_category_breakdown(self):
        """Test XP category breakdown"""
        self.xp.award_xp(XPCategory.USAGE, 'command_execute')  # 1
        self.xp.award_xp(XPCategory.INFORMATION, 'guide_read')  # 5
        self.xp.award_xp(XPCategory.CONTRIBUTION, 'knowledge_share')  # 25

        breakdown = self.xp.get_category_breakdown()
        self.assertAlmostEqual(breakdown['usage']['percentage'], 3.23, places=1)
        self.assertAlmostEqual(breakdown['information']['percentage'], 16.13, places=1)
        self.assertAlmostEqual(breakdown['contribution']['percentage'], 80.65, places=1)

    def test_xp_event_tracking(self):
        """Test XP events are tracked"""
        self.xp.award_xp(XPCategory.USAGE, 'command_execute')
        self.xp.award_xp(XPCategory.INFORMATION, 'guide_read')

        self.assertEqual(len(self.xp.events), 2)
        self.assertEqual(self.xp.events[0].source, 'command_execute')


class TestAchievementSystem(unittest.TestCase):
    """Test achievement system (10 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.achievements = AchievementSystem('user1')

    def test_achievement_initialization(self):
        """Test achievement system initialization"""
        self.assertEqual(len(self.achievements.unlocked), 0)
        self.assertGreater(len(self.achievements.achievements), 0)

    def test_achievement_unlock_xp_total(self):
        """Test XP total achievement unlock"""
        user_stats = {'total_xp': 100, 'level': 2}
        unlocked = self.achievements.check_achievements(user_stats)

        self.assertGreater(len(unlocked), 0)
        self.assertIn('xp_100', self.achievements.unlocked)

    def test_achievement_unlock_level(self):
        """Test level achievement unlock"""
        user_stats = {'total_xp': 1000, 'level': 10}
        unlocked = self.achievements.check_achievements(user_stats)

        self.assertIn('level_10', self.achievements.unlocked)

    def test_achievement_unlock_streak(self):
        """Test streak achievement unlock"""
        user_stats = {'streak_days': 7}
        unlocked = self.achievements.check_achievements(user_stats)

        self.assertIn('streak_7', self.achievements.unlocked)

    def test_achievement_no_duplicate_unlock(self):
        """Test achievements don't unlock twice"""
        user_stats = {'total_xp': 100}

        unlocked1 = self.achievements.check_achievements(user_stats)
        unlocked2 = self.achievements.check_achievements(user_stats)

        self.assertGreater(len(unlocked1), 0)
        self.assertEqual(len(unlocked2), 0)

    def test_achievement_progress(self):
        """Test achievement progress tracking"""
        user_stats = {'total_xp': 50}
        progress = self.achievements.get_progress('xp_100', user_stats)

        self.assertEqual(progress['current'], 50)
        self.assertEqual(progress['target'], 100)
        self.assertEqual(progress['percentage'], 50)

    def test_category_achievement(self):
        """Test category-specific achievement"""
        user_stats = {
            'category_xp': {'usage': 1000}
        }
        unlocked = self.achievements.check_achievements(user_stats)

        self.assertIn('usage_master', self.achievements.unlocked)

    def test_unlock_history(self):
        """Test unlock history tracking"""
        user_stats = {'total_xp': 100}
        self.achievements.check_achievements(user_stats)

        self.assertGreater(len(self.achievements.unlock_history), 0)
        self.assertEqual(self.achievements.unlock_history[0]['id'], 'xp_100')

    def test_multiple_achievements_unlock(self):
        """Test multiple achievements unlock at once"""
        user_stats = {'total_xp': 1000, 'level': 10}
        unlocked = self.achievements.check_achievements(user_stats)

        self.assertGreaterEqual(len(unlocked), 2)

    def test_achievement_check_unlock(self):
        """Test individual achievement check"""
        achievement = self.achievements.achievements['xp_100']
        user_stats = {'total_xp': 150}

        result = achievement.check_unlock(user_stats)
        self.assertTrue(result)


class TestSkillProgression(unittest.TestCase):
    """Test skill tree and progression (10 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.tree = SkillTree('Survival')
        self.tree.add_skill('water_basics', 'Water Basics', xp_cost=0)
        self.tree.add_skill('water_advanced', 'Water Purification',
                           prerequisites=['water_basics'], xp_cost=100)

    def test_skill_tree_creation(self):
        """Test skill tree creation"""
        self.assertEqual(self.tree.name, 'Survival')
        self.assertEqual(len(self.tree.skills), 2)

    def test_unlock_basic_skill(self):
        """Test unlocking skill with no prerequisites"""
        result = self.tree.unlock_skill('water_basics', 0)
        self.assertTrue(result)
        self.assertIn('water_basics', self.tree.unlocked)

    def test_unlock_with_prerequisites(self):
        """Test unlocking skill with prerequisites"""
        self.tree.unlock_skill('water_basics', 0)
        result = self.tree.unlock_skill('water_advanced', 100)

        self.assertTrue(result)
        self.assertIn('water_advanced', self.tree.unlocked)

    def test_unlock_missing_prerequisites(self):
        """Test unlock fails without prerequisites"""
        result = self.tree.unlock_skill('water_advanced', 100)
        self.assertFalse(result)

    def test_unlock_insufficient_xp(self):
        """Test unlock fails with insufficient XP"""
        self.tree.unlock_skill('water_basics', 0)
        result = self.tree.unlock_skill('water_advanced', 50)

        self.assertFalse(result)

    def test_skill_level_up(self):
        """Test leveling up a skill"""
        self.tree.unlock_skill('water_basics', 0)
        result = self.tree.level_up_skill('water_basics')

        self.assertTrue(result)
        self.assertEqual(self.tree.skills['water_basics']['level'], 2)

    def test_skill_max_level(self):
        """Test skill max level cap"""
        self.tree.unlock_skill('water_basics', 0)

        # Level up to max (5)
        for _ in range(4):
            self.tree.level_up_skill('water_basics')

        # Try to exceed max
        result = self.tree.level_up_skill('water_basics')
        self.assertFalse(result)
        self.assertEqual(self.tree.skills['water_basics']['level'], 5)

    def test_get_available_skills(self):
        """Test getting available skills"""
        available = self.tree.get_available_skills()

        self.assertIn('water_basics', available)
        self.assertNotIn('water_advanced', available)  # Prerequisites not met

    def test_available_after_unlock(self):
        """Test available skills update after unlock"""
        self.tree.unlock_skill('water_basics', 0)
        available = self.tree.get_available_skills()

        self.assertNotIn('water_basics', available)  # Already unlocked
        self.assertIn('water_advanced', available)  # Now available

    def test_skill_chain(self):
        """Test skill dependency chain"""
        self.tree.add_skill('water_expert', 'Water Expert',
                           prerequisites=['water_advanced'], xp_cost=200)

        # Unlock chain
        self.tree.unlock_skill('water_basics', 0)
        self.tree.unlock_skill('water_advanced', 100)
        result = self.tree.unlock_skill('water_expert', 200)

        self.assertTrue(result)


class TestCompetenceTracking(unittest.TestCase):
    """Test competence tracking (8 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.tracker = CompetenceTracker('user1')

    def test_competence_initialization(self):
        """Test competence tracker initialization"""
        self.assertEqual(len(self.tracker.competencies), 5)
        self.assertEqual(self.tracker.competencies['survival'], 0)

    def test_record_skill_use(self):
        """Test recording skill usage"""
        self.tracker.record_skill_use('water_purify', 'survival')

        self.assertGreater(self.tracker.competencies['survival'], 0)
        self.assertEqual(self.tracker.skill_uses['water_purify'], 1)

    def test_multiple_skill_uses(self):
        """Test multiple uses of same skill"""
        for _ in range(5):
            self.tracker.record_skill_use('coding', 'technical')

        self.assertEqual(self.tracker.skill_uses['coding'], 5)

    def test_competency_levels(self):
        """Test competency level classification"""
        self.assertEqual(self.tracker.get_competency_level('survival'), 'novice')

        self.tracker.competencies['survival'] = 250
        self.assertEqual(self.tracker.get_competency_level('survival'), 'intermediate')

        self.tracker.competencies['survival'] = 600
        self.assertEqual(self.tracker.get_competency_level('survival'), 'advanced')

        self.tracker.competencies['survival'] = 1200
        self.assertEqual(self.tracker.get_competency_level('survival'), 'expert')

    def test_diminishing_returns(self):
        """Test diminishing returns on competency gain"""
        # First use gives 10
        self.tracker.record_skill_use('skill1', 'survival')
        first_gain = self.tracker.competencies['survival']

        # Set to high level
        self.tracker.competencies['survival'] = 500

        # Next use gives less
        self.tracker.record_skill_use('skill2', 'survival')
        second_gain = self.tracker.competencies['survival'] - 500

        self.assertLess(second_gain, first_gain)

    def test_strongest_competencies(self):
        """Test getting strongest competencies"""
        self.tracker.competencies['survival'] = 500
        self.tracker.competencies['technical'] = 300
        self.tracker.competencies['social'] = 100

        strongest = self.tracker.get_strongest_competencies(2)

        self.assertEqual(len(strongest), 2)
        self.assertEqual(strongest[0][0], 'survival')
        self.assertEqual(strongest[1][0], 'technical')

    def test_multiple_competencies(self):
        """Test tracking multiple competencies"""
        self.tracker.record_skill_use('water', 'survival')
        self.tracker.record_skill_use('code', 'technical')
        self.tracker.record_skill_use('trade', 'social')

        self.assertGreater(self.tracker.competencies['survival'], 0)
        self.assertGreater(self.tracker.competencies['technical'], 0)
        self.assertGreater(self.tracker.competencies['social'], 0)

    def test_skill_use_frequency(self):
        """Test skill usage frequency tracking"""
        self.tracker.record_skill_use('favorite_skill', 'survival')
        self.tracker.record_skill_use('favorite_skill', 'survival')
        self.tracker.record_skill_use('favorite_skill', 'survival')
        self.tracker.record_skill_use('other_skill', 'survival')

        self.assertEqual(self.tracker.skill_uses['favorite_skill'], 3)
        self.assertEqual(self.tracker.skill_uses['other_skill'], 1)


class TestLeaderboards(unittest.TestCase):
    """Test leaderboard system (7 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.leaderboard = Leaderboard()

    def test_leaderboard_initialization(self):
        """Test leaderboard initialization"""
        self.assertEqual(len(self.leaderboard.rankings), 0)

    def test_update_ranking(self):
        """Test updating user ranking"""
        self.leaderboard.update_ranking('user1', 100,
                                       {'usage': 50, 'information': 30, 'contribution': 20},
                                       2)

        self.assertIn('user1', self.leaderboard.rankings)
        self.assertEqual(self.leaderboard.rankings['user1']['total_xp'], 100)

    def test_get_top_users(self):
        """Test getting top users"""
        self.leaderboard.update_ranking('user1', 100, {}, 2)
        self.leaderboard.update_ranking('user2', 500, {}, 5)
        self.leaderboard.update_ranking('user3', 250, {}, 3)

        top = self.leaderboard.get_top_users(2)

        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], 'user2')  # Highest XP
        self.assertEqual(top[1][0], 'user3')

    def test_category_leaders(self):
        """Test category-specific leaderboard"""
        self.leaderboard.update_ranking('user1', 100, {'usage': 80}, 2)
        self.leaderboard.update_ranking('user2', 100, {'usage': 50}, 2)

        leaders = self.leaderboard.get_category_leaders('usage', 10)

        self.assertEqual(leaders[0][0], 'user1')
        self.assertEqual(leaders[0][1], 80)

    def test_user_rank(self):
        """Test getting user's rank"""
        self.leaderboard.update_ranking('user1', 100, {}, 2)
        self.leaderboard.update_ranking('user2', 500, {}, 5)
        self.leaderboard.update_ranking('user3', 250, {}, 3)

        rank = self.leaderboard.get_user_rank('user3')
        self.assertEqual(rank, 2)

    def test_user_not_ranked(self):
        """Test user not in rankings"""
        rank = self.leaderboard.get_user_rank('nonexistent')
        self.assertEqual(rank, -1)

    def test_leaderboard_limit(self):
        """Test leaderboard respects limit"""
        for i in range(20):
            self.leaderboard.update_ranking(f'user{i}', i * 10, {}, i)

        top = self.leaderboard.get_top_users(5)
        self.assertEqual(len(top), 5)


class TestIntegration(unittest.TestCase):
    """Integration tests (8 tests)"""

    def test_xp_achievement_integration(self):
        """Test XP earning triggers achievements"""
        xp = XPSystem('user1')
        achievements = AchievementSystem('user1')

        # Earn XP
        xp.award_xp(XPCategory.USAGE, 'certification')  # 100 XP

        # Check achievements
        stats = {
            'total_xp': xp.total_xp,
            'level': xp.level,
            'category_xp': xp.category_xp
        }
        unlocked = achievements.check_achievements(stats)

        self.assertGreater(len(unlocked), 0)

    def test_skill_unlock_xp_requirement(self):
        """Test skill unlock requires XP"""
        xp = XPSystem('user1')
        tree = SkillTree('Combat')
        tree.add_skill('basic_attack', 'Basic Attack', xp_cost=0)
        tree.add_skill('power_strike', 'Power Strike',
                      prerequisites=['basic_attack'], xp_cost=100)

        # Try unlock without XP
        tree.unlock_skill('basic_attack', 0)
        result = tree.unlock_skill('power_strike', xp.total_xp)
        self.assertFalse(result)

        # Earn XP and unlock
        xp.award_xp(XPCategory.USAGE, 'certification')
        result = tree.unlock_skill('power_strike', xp.total_xp)
        self.assertTrue(result)

    def test_competence_from_skill_use(self):
        """Test competence tracking from skill usage"""
        tracker = CompetenceTracker('user1')

        # Use survival skills
        tracker.record_skill_use('water_purify', 'survival')
        tracker.record_skill_use('fire_start', 'survival')
        tracker.record_skill_use('shelter_build', 'survival')

        level = tracker.get_competency_level('survival')
        self.assertIn(level, ['novice', 'intermediate'])

    def test_leaderboard_updates(self):
        """Test leaderboard updates from XP"""
        xp1 = XPSystem('user1')
        xp2 = XPSystem('user2')
        leaderboard = Leaderboard()

        # Award different amounts
        xp1.award_xp(XPCategory.USAGE, 'certification')  # 100
        xp2.award_xp(XPCategory.CONTRIBUTION, 'guide_create')  # 50

        # Update leaderboard
        leaderboard.update_ranking('user1', xp1.total_xp, xp1.category_xp, xp1.level)
        leaderboard.update_ranking('user2', xp2.total_xp, xp2.category_xp, xp2.level)

        # Check rankings
        top = leaderboard.get_top_users(2)
        self.assertEqual(top[0][0], 'user1')

    def test_achievement_xp_reward(self):
        """Test achievement unlocks award XP"""
        xp = XPSystem('user1')
        achievements = AchievementSystem('user1')

        # Earn enough for achievement
        xp.award_xp(XPCategory.USAGE, 'certification')

        stats = {'total_xp': xp.total_xp, 'level': xp.level, 'category_xp': xp.category_xp}
        unlocked = achievements.check_achievements(stats)

        # Award achievement bonuses
        for achievement in unlocked:
            xp.award_xp(XPCategory.USAGE, 'feature_discovery')  # Bonus

        self.assertGreater(xp.total_xp, 100)

    def test_skill_tree_progression_path(self):
        """Test complete skill tree progression"""
        xp = XPSystem('user1')
        tree = SkillTree('Survival')

        # Build skill tree
        tree.add_skill('s1', 'Level 1', xp_cost=0)
        tree.add_skill('s2', 'Level 2', prerequisites=['s1'], xp_cost=50)
        tree.add_skill('s3', 'Level 3', prerequisites=['s2'], xp_cost=100)

        # Progress through tree
        tree.unlock_skill('s1', 0)

        xp.award_xp(XPCategory.INFORMATION, 'guide_complete')  # 15
        xp.award_xp(XPCategory.INFORMATION, 'quiz_pass')  # 30
        xp.award_xp(XPCategory.INFORMATION, 'guide_read')  # 5

        tree.unlock_skill('s2', xp.total_xp)

        xp.award_xp(XPCategory.INFORMATION, 'certification')  # 100

        result = tree.unlock_skill('s3', xp.total_xp)
        self.assertTrue(result)

    def test_streak_bonus_integration(self):
        """Test streak bonus awards XP"""
        xp = XPSystem('user1')

        # Build 7-day streak
        xp.update_streak()
        for _ in range(6):
            xp.last_activity = datetime.now() - timedelta(days=1)
            xp.update_streak()

        # Should have earned streak bonus
        streak_xp = sum(e.amount for e in xp.events if e.source == 'streak_bonus')
        self.assertEqual(streak_xp, 25)

    def test_full_progression_workflow(self):
        """Test complete progression workflow"""
        xp = XPSystem('user1')
        achievements = AchievementSystem('user1')
        tracker = CompetenceTracker('user1')
        leaderboard = Leaderboard()

        # User activities
        xp.award_xp(XPCategory.USAGE, 'daily_login')
        xp.award_xp(XPCategory.INFORMATION, 'guide_read')
        xp.award_xp(XPCategory.CONTRIBUTION, 'help_user')

        tracker.record_skill_use('helping', 'social')

        # Update systems
        stats = {'total_xp': xp.total_xp, 'level': xp.level, 'category_xp': xp.category_xp}
        achievements.check_achievements(stats)
        leaderboard.update_ranking('user1', xp.total_xp, xp.category_xp, xp.level)

        # Verify integration
        self.assertEqual(xp.total_xp, 30)
        self.assertGreater(tracker.competencies['social'], 0)
        self.assertEqual(leaderboard.get_user_rank('user1'), 1)


def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestXPSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAchievementSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillProgression))
    suite.addTests(loader.loadTestsFromTestCase(TestCompetenceTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestLeaderboards))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
