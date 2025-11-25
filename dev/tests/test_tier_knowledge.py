"""
uDOS v1.0.20 - 4-Tier Knowledge Bank Test Suite
Tests tier storage, privacy controls, search, and statistics
"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime

from core.services.tier_knowledge_manager import TierKnowledgeManager
from core.services.knowledge_types import KnowledgeTier, KnowledgeType


class TestTierKnowledgeManager(unittest.TestCase):
    """Test TierKnowledgeManager functionality."""

    def setUp(self):
        """Create temporary database for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_knowledge.db"
        self.manager = TierKnowledgeManager(db_path=self.db_path, user_id="test_user")

    def test_database_initialization(self):
        """Test database creation and table structure."""
        self.assertTrue(self.db_path.exists())

        # Verify tables exist
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {'tier_knowledge', 'tier_knowledge_fts', 'knowledge_barter', 'tier_privacy'}
        self.assertTrue(expected_tables.issubset(tables))

        conn.close()

    def test_add_personal_knowledge(self):
        """Test adding knowledge to personal tier (tier 0)."""
        item = self.manager.add_knowledge(
            tier=KnowledgeTier.PERSONAL,
            knowledge_type=KnowledgeType.SURVIVAL,
            title="Water Purification",
            content="Boil water for 3 minutes to kill bacteria",
            tags=["water", "survival", "health"]
        )

        self.assertEqual(item.tier, KnowledgeTier.PERSONAL)
        self.assertEqual(item.type, KnowledgeType.SURVIVAL)
        self.assertEqual(item.title, "Water Purification")
        self.assertEqual(item.author_id, "test_user")
        self.assertTrue(item.encrypted)  # Personal tier should be encrypted
        self.assertIsNotNone(item.checksum)

    def test_add_shared_knowledge(self):
        """Test adding knowledge to shared tier (tier 1)."""
        item = self.manager.add_knowledge(
            tier=KnowledgeTier.SHARED,
            knowledge_type=KnowledgeType.RECIPE,
            title="Sourdough Starter",
            content="Mix flour and water, feed daily",
            tags=["food", "recipe", "bread"]
        )

        self.assertEqual(item.tier, KnowledgeTier.SHARED)
        self.assertEqual(item.type, KnowledgeType.RECIPE)
        self.assertEqual(item.author_id, "test_user")

    def test_add_group_knowledge(self):
        """Test adding knowledge to group tier (tier 2) - anonymous."""
        item = self.manager.add_knowledge(
            tier=KnowledgeTier.GROUP,
            knowledge_type=KnowledgeType.GUIDE,
            title="Solar Panel Installation",
            content="Step-by-step guide for off-grid solar",
            tags=["energy", "solar", "DIY"]
        )

        self.assertEqual(item.tier, KnowledgeTier.GROUP)
        self.assertEqual(item.author_id, "anonymous")  # Group tier should be anonymous

    def test_search_knowledge(self):
        """Test full-text search across tiers."""
        # Add test knowledge
        self.manager.add_knowledge(
            KnowledgeTier.PERSONAL, KnowledgeType.SURVIVAL,
            "Water Filter", "How to build a water filter", ["water", "filter"]
        )
        self.manager.add_knowledge(
            KnowledgeTier.PUBLIC, KnowledgeType.GUIDE,
            "Solar Water Heater", "Build a solar water heater", ["water", "solar"]
        )
        self.manager.add_knowledge(
            KnowledgeTier.SHARED, KnowledgeType.TIP,
            "Coffee Tips", "Best coffee brewing tips", ["coffee", "drink"]
        )

        # Search for "water"
        results = self.manager.search_knowledge("water")
        self.assertEqual(len(results), 2)  # Should find both water-related items

        # Search with tier filter
        results = self.manager.search_knowledge("water", tier=KnowledgeTier.PERSONAL)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Water Filter")

        # Search with tag filter
        results = self.manager.search_knowledge("water", tags=["solar"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Solar Water Heater")

    def test_get_knowledge_increments_views(self):
        """Test that viewing knowledge increments view count."""
        item = self.manager.add_knowledge(
            KnowledgeTier.PUBLIC, KnowledgeType.REFERENCE,
            "Test Item", "Test content", []
        )

        initial_views = item.views

        # Get knowledge twice
        retrieved1 = self.manager.get_knowledge(item.id)
        retrieved2 = self.manager.get_knowledge(item.id)

        self.assertEqual(retrieved2.views, initial_views + 2)

    def test_get_tier_stats(self):
        """Test tier statistics calculation."""
        # Add knowledge to different tiers
        self.manager.add_knowledge(KnowledgeTier.PERSONAL, KnowledgeType.NOTE, "Note 1", "Content", [])
        self.manager.add_knowledge(KnowledgeTier.PERSONAL, KnowledgeType.NOTE, "Note 2", "Content", [])
        self.manager.add_knowledge(KnowledgeTier.SHARED, KnowledgeType.TIP, "Tip 1", "Content", [])
        self.manager.add_knowledge(KnowledgeTier.PUBLIC, KnowledgeType.GUIDE, "Guide 1", "Content", [])

        stats = self.manager.get_tier_stats()

        self.assertEqual(stats['PERSONAL']['total'], 2)
        self.assertEqual(stats['PERSONAL']['owned'], 2)
        self.assertEqual(stats['SHARED']['total'], 1)
        self.assertEqual(stats['PUBLIC']['total'], 1)

    def test_checksum_validation(self):
        """Test content checksum calculation."""
        content = "Test content for checksum"
        checksum1 = self.manager._calculate_checksum(content)
        checksum2 = self.manager._calculate_checksum(content)

        self.assertEqual(checksum1, checksum2)  # Same content = same checksum

        different_checksum = self.manager._calculate_checksum("Different content")
        self.assertNotEqual(checksum1, different_checksum)


class TestKnowledgeTypes(unittest.TestCase):
    """Test knowledge type enums and data structures."""

    def test_knowledge_tier_values(self):
        """Test tier enum values."""
        self.assertEqual(KnowledgeTier.PERSONAL.value, 0)
        self.assertEqual(KnowledgeTier.SHARED.value, 1)
        self.assertEqual(KnowledgeTier.GROUP.value, 2)
        self.assertEqual(KnowledgeTier.PUBLIC.value, 3)

    def test_knowledge_type_enum(self):
        """Test knowledge type enum."""
        types = [KnowledgeType.SURVIVAL, KnowledgeType.SKILL, KnowledgeType.RECIPE,
                KnowledgeType.GUIDE, KnowledgeType.REFERENCE, KnowledgeType.NOTE,
                KnowledgeType.LINK, KnowledgeType.EXPERIENCE, KnowledgeType.TIP,
                KnowledgeType.WARNING]

        self.assertEqual(len(types), 10)  # Should have 10 types

    def test_tier_descriptions(self):
        """Test tier descriptions dictionary."""
        from core.services.knowledge_types import TIER_DESCRIPTIONS

        self.assertIn(KnowledgeTier.PERSONAL, TIER_DESCRIPTIONS)
        self.assertIn('icon', TIER_DESCRIPTIONS[KnowledgeTier.PERSONAL])
        self.assertIn('name', TIER_DESCRIPTIONS[KnowledgeTier.PERSONAL])
        self.assertIn('description', TIER_DESCRIPTIONS[KnowledgeTier.PERSONAL])


if __name__ == '__main__':
    print("="*60)
    print("uDOS v1.0.20 - 4-Tier Knowledge Bank Test Suite")
    print("="*60)
    print()

    # Run tests
    unittest.main(verbosity=2)
