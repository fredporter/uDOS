"""
Tests for XP System (v1.0.18)
"""

import pytest
import sqlite3
from pathlib import Path
from core.services.xp_service import XPService, XPCategory, SkillTree
from core.commands.xp_handler import XPCommandHandler, award_usage_xp, award_information_xp


@pytest.fixture
def xp_service(tmp_path):
    """Create XP service with temporary database"""
    db_path = tmp_path / "test_xp.db"
    return XPService(str(db_path))


@pytest.fixture
def xp_handler(xp_service):
    """Create XP command handler"""
    handler = XPCommandHandler()
    handler.xp_service = xp_service
    return handler


class TestXPService:
    """Test XP service functionality"""

    def test_init_creates_database(self, tmp_path):
        """Test database initialization"""
        db_path = tmp_path / "xp.db"
        service = XPService(str(db_path))

        assert db_path.exists()

        # Check tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        assert "xp_transactions" in tables
        assert "skills" in tables
        assert "achievements" in tables

    def test_init_creates_default_skills(self, xp_service):
        """Test default skills are created"""
        skills = xp_service.get_all_skills()

        assert len(skills) == 6
        assert all(s['level'] == 1 for s in skills)
        assert all(s['xp'] == 0 for s in skills)

    def test_award_xp_records_transaction(self, xp_service):
        """Test awarding XP creates transaction"""
        result = xp_service.award_xp(
            XPCategory.USAGE,
            10,
            reason="Test command",
            context="TEST"
        )

        assert result['category'] == 'usage'
        assert result['amount'] == 10
        assert result['total_xp'] == 10

    def test_award_xp_accumulates(self, xp_service):
        """Test XP accumulates correctly"""
        xp_service.award_xp(XPCategory.USAGE, 10)
        xp_service.award_xp(XPCategory.USAGE, 20)
        xp_service.award_xp(XPCategory.USAGE, 15)

        total = xp_service.get_category_xp(XPCategory.USAGE)
        assert total == 45

    def test_get_total_xp(self, xp_service):
        """Test total XP across categories"""
        xp_service.award_xp(XPCategory.USAGE, 10)
        xp_service.award_xp(XPCategory.INFORMATION, 20)
        xp_service.award_xp(XPCategory.CONTRIBUTION, 30)

        total = xp_service.get_total_xp()
        assert total == 60

    def test_get_xp_breakdown(self, xp_service):
        """Test XP breakdown by category"""
        xp_service.award_xp(XPCategory.USAGE, 10)
        xp_service.award_xp(XPCategory.INFORMATION, 20)

        breakdown = xp_service.get_xp_breakdown()

        assert breakdown['usage'] == 10
        assert breakdown['information'] == 20
        assert breakdown['contribution'] == 0
        assert breakdown['connection'] == 0

    def test_skill_level_calculation(self, xp_service):
        """Test skill level calculation"""
        # Level N requires N^2 * 100 total XP
        # Level 1: 0-99 XP
        # Level 2: 100-399 XP  (2^2*100 = 400)
        # Level 3: 400-899 XP  (3^2*100 = 900)
        # Level 4: 900-1599 XP (4^2*100 = 1600)

        assert xp_service._calculate_level(0) == 1
        assert xp_service._calculate_level(99) == 1
        assert xp_service._calculate_level(100) == 2
        assert xp_service._calculate_level(399) == 2
        assert xp_service._calculate_level(400) == 3
        assert xp_service._calculate_level(899) == 3
        assert xp_service._calculate_level(900) == 4

    def test_update_skill_xp(self, xp_service):
        """Test updating skill XP"""
        result = xp_service.update_skill_xp(SkillTree.SHELTER, 50)

        assert result['skill'] == 'shelter'
        assert result['xp'] == 50
        assert result['new_level'] == 1
        assert not result['leveled_up']

    def test_skill_level_up(self, xp_service):
        """Test skill leveling up"""
        # Add enough XP to level up
        result = xp_service.update_skill_xp(SkillTree.FOOD, 100)

        assert result['new_level'] == 2
        assert result['leveled_up']
        assert result['previous_level'] == 1

    def test_get_skill_status(self, xp_service):
        """Test getting skill status"""
        xp_service.update_skill_xp(SkillTree.WATER, 50)

        status = xp_service.get_skill_status(SkillTree.WATER)

        assert status['skill'] == 'water'
        assert status['level'] == 1
        assert status['xp'] == 50
        assert status['next_level_xp'] == 100  # Cumulative to level 2
        assert status['progress_percent'] == 50

    def test_get_all_skills(self, xp_service):
        """Test getting all skills"""
        xp_service.update_skill_xp(SkillTree.SHELTER, 100)
        xp_service.update_skill_xp(SkillTree.MEDICINE, 200)

        skills = xp_service.get_all_skills()

        assert len(skills) == 6

        shelter = next(s for s in skills if s['skill'] == 'shelter')
        assert shelter['level'] == 2

        medicine = next(s for s in skills if s['skill'] == 'medicine')
        assert medicine['level'] == 2

    def test_achievement_unlock_on_xp(self, xp_service):
        """Test achievement unlocks when XP threshold reached"""
        # Award enough XP to unlock "Novice User" (100 XP)
        result = xp_service.award_xp(XPCategory.USAGE, 100, reason="Test")

        assert len(result['achievements']) > 0
        assert any(a['id'] == 'novice_user' for a in result['achievements'])

    def test_achievement_unlock_on_skill_level(self, xp_service):
        """Test achievement unlocks when skill reaches level"""
        # Level up shelter to 5 (requires 5^2 * 100 = 2500 total XP)
        result = xp_service.update_skill_xp(SkillTree.SHELTER, 2500)

        assert len(result['achievements']) > 0
        assert any(a['id'] == 'shelter_novice' for a in result['achievements'])

    def test_get_achievements(self, xp_service):
        """Test getting achievements"""
        # Unlock an achievement
        xp_service.award_xp(XPCategory.USAGE, 1)

        achievements = xp_service.get_achievements()

        assert len(achievements) > 0
        assert any(a['unlocked'] for a in achievements)

    def test_get_unlocked_achievements_only(self, xp_service):
        """Test filtering for unlocked achievements"""
        xp_service.award_xp(XPCategory.USAGE, 100)

        unlocked = xp_service.get_achievements(unlocked_only=True)

        assert all(a['unlocked'] for a in unlocked)

    def test_get_recent_xp(self, xp_service):
        """Test getting recent XP transactions"""
        xp_service.award_xp(XPCategory.USAGE, 10, reason="Command 1")
        xp_service.award_xp(XPCategory.USAGE, 20, reason="Command 2")
        xp_service.award_xp(XPCategory.INFORMATION, 15, reason="Read guide")

        recent = xp_service.get_recent_xp(limit=2)

        assert len(recent) == 2
        assert recent[0]['reason'] == "Read guide"  # Most recent first
        assert recent[1]['reason'] == "Command 2"


class TestXPCommandHandler:
    """Test XP command handler"""

    def test_xp_status_command(self, xp_handler):
        """Test XP STATUS command"""
        # Award some XP
        xp_handler.xp_service.award_xp(XPCategory.USAGE, 50)
        xp_handler.xp_service.award_xp(XPCategory.INFORMATION, 30)

        result = xp_handler.handle_command("XP", [])

        assert result['type'] == 'xp_status'
        assert result['total_xp'] == 80
        assert 'message' in result

    def test_xp_breakdown_command(self, xp_handler):
        """Test XP BREAKDOWN command"""
        xp_handler.xp_service.award_xp(XPCategory.USAGE, 100)
        xp_handler.xp_service.award_xp(XPCategory.INFORMATION, 50)

        result = xp_handler.handle_command("XP", ["BREAKDOWN"])

        assert result['type'] == 'xp_breakdown'
        assert result['breakdown']['usage'] == 100
        assert result['breakdown']['information'] == 50
        assert result['total'] == 150

    def test_xp_history_command(self, xp_handler):
        """Test XP HISTORY command"""
        xp_handler.xp_service.award_xp(XPCategory.USAGE, 10, reason="Test 1")
        xp_handler.xp_service.award_xp(XPCategory.USAGE, 20, reason="Test 2")

        result = xp_handler.handle_command("XP", ["HISTORY", "2"])

        assert result['type'] == 'xp_history'
        assert len(result['transactions']) == 2

    def test_skill_command(self, xp_handler):
        """Test SKILL command"""
        xp_handler.xp_service.update_skill_xp(SkillTree.SHELTER, 150)

        result = xp_handler.handle_command("SKILL", ["shelter"])

        assert result['type'] == 'skill_status'
        assert result['skill']['skill'] == 'shelter'
        assert result['skill']['level'] == 2

    def test_skills_command(self, xp_handler):
        """Test SKILLS command"""
        xp_handler.xp_service.update_skill_xp(SkillTree.SHELTER, 100)
        xp_handler.xp_service.update_skill_xp(SkillTree.FOOD, 200)

        result = xp_handler.handle_command("SKILLS", [])

        assert result['type'] == 'skills_status'
        assert len(result['skills']) == 6

    def test_achievements_command(self, xp_handler):
        """Test ACHIEVEMENTS command"""
        xp_handler.xp_service.award_xp(XPCategory.USAGE, 100)

        result = xp_handler.handle_command("ACHIEVEMENTS", [])

        assert result['type'] == 'achievements'
        assert result['unlocked_count'] > 0
        assert result['total_count'] > 0

    def test_achievements_unlocked_filter(self, xp_handler):
        """Test ACHIEVEMENTS UNLOCKED command"""
        xp_handler.xp_service.award_xp(XPCategory.USAGE, 100)

        result = xp_handler.handle_command("ACHIEVEMENTS", ["UNLOCKED"])

        assert result['type'] == 'achievements'
        assert all(a['unlocked'] for a in result['achievements'])


class TestXPHelpers:
    """Test XP helper functions"""

    def test_award_usage_xp(self, xp_service):
        """Test usage XP helper"""
        award_usage_xp("TEST_COMMAND", xp_service)

        total = xp_service.get_category_xp(XPCategory.USAGE)
        assert total == 1

    def test_award_information_xp(self, xp_service):
        """Test information XP helper"""
        award_information_xp(20, "Test Guide", xp_service)

        total = xp_service.get_category_xp(XPCategory.INFORMATION)
        assert total == 20

    def test_multiple_usage_awards(self, xp_service):
        """Test multiple usage XP awards accumulate"""
        award_usage_xp("CMD1", xp_service)
        award_usage_xp("CMD2", xp_service)
        award_usage_xp("CMD3", xp_service)

        total = xp_service.get_category_xp(XPCategory.USAGE)
        assert total == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
