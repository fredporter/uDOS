"""
Tests for Knowledge Integration Service
"""

import os
import sys
import pytest
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.services.knowledge_service import KnowledgeService
from core.services.xp_service import XPService, SkillTree


class TestKnowledgeService:
    """Test KnowledgeService functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test knowledge"""
        temp = tempfile.mkdtemp()

        # Create knowledge directory structure
        knowledge_dir = os.path.join(temp, "knowledge")
        os.makedirs(os.path.join(knowledge_dir, "building"), exist_ok=True)
        os.makedirs(os.path.join(knowledge_dir, "water"), exist_ok=True)
        os.makedirs(os.path.join(knowledge_dir, "food"), exist_ok=True)

        # Create test knowledge files
        with open(os.path.join(knowledge_dir, "building", "shelter_basics.md"), 'w') as f:
            f.write("""# Shelter Building Basics

This guide covers the fundamentals of building emergency shelters using natural materials.

## Key Principles
- Location selection
- Material gathering
- Basic construction techniques

Essential knowledge for survival scenarios.
""")

        with open(os.path.join(knowledge_dir, "water", "purification.md"), 'w') as f:
            f.write("""# Water Purification Methods

---
tags: [water, purification, survival]
---

# Water Purification

Learn multiple methods to purify water:
- Boiling
- Chemical treatment
- Filtration
- UV sterilization

Critical survival skill.
""")

        with open(os.path.join(knowledge_dir, "food", "foraging.md"), 'w') as f:
            f.write("""# Wild Food Foraging

This comprehensive guide teaches plant identification and safe foraging practices.

Contains detailed information about edible plants, safety protocols, and seasonal availability.
""")

        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def knowledge_service(self, temp_dir):
        """Create KnowledgeService instance"""
        return KnowledgeService(
            data_dir=os.path.join(temp_dir, "data"),
            knowledge_dir=os.path.join(temp_dir, "knowledge")
        )

    @pytest.fixture
    def xp_service(self, temp_dir):
        """Create XPService instance"""
        return XPService(db_path=os.path.join(temp_dir, "data", "xp.db"))

    def test_init_database(self, knowledge_service):
        """Test database initialization"""
        assert os.path.exists(knowledge_service.db_path)

    def test_index_knowledge_base(self, knowledge_service):
        """Test indexing knowledge files"""
        result = knowledge_service.index_knowledge_base()

        assert result['indexed'] == 3
        assert result['total_items'] == 3
        assert result.get('errors') is None

    def test_extract_metadata(self, knowledge_service, temp_dir):
        """Test metadata extraction from markdown"""
        filepath = os.path.join(temp_dir, "knowledge", "water", "purification.md")
        metadata = knowledge_service._extract_metadata(filepath)

        assert metadata['title'] == 'Water Purification Methods'
        assert metadata['word_count'] > 0
        assert 'purification' in metadata['tags']

    def test_determine_skill_tree(self, knowledge_service):
        """Test skill tree determination from path"""
        assert knowledge_service._determine_skill_tree("building/shelter.md") == SkillTree.SHELTER.value
        assert knowledge_service._determine_skill_tree("water/wells.md") == SkillTree.WATER.value
        assert knowledge_service._determine_skill_tree("food/garden.md") == SkillTree.FOOD.value

    def test_can_access_knowledge_public(self, knowledge_service, xp_service):
        """Test access check for public knowledge"""
        # Index first
        knowledge_service.index_knowledge_base()

        # Public knowledge (level 0) should be accessible
        access = knowledge_service.can_access_knowledge(1, xp_service)

        assert access['access'] is True

    def test_can_access_knowledge_locked(self, knowledge_service, xp_service, temp_dir):
        """Test access check for level-locked knowledge"""
        # Index knowledge
        knowledge_service.index_knowledge_base()

        # Manually set a knowledge item to require level 3
        import sqlite3
        conn = sqlite3.connect(knowledge_service.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE knowledge_items SET required_level = 3, skill_tree = ? WHERE id = 1",
                      (SkillTree.SHELTER.value,))
        conn.commit()
        conn.close()

        # Check access without sufficient skill
        access = knowledge_service.can_access_knowledge(1, xp_service)

        assert access['access'] is False
        assert access['required_level'] == 3
        # XP service initializes skills at level 1
        assert access['current_level'] < access['required_level']

    def test_read_knowledge(self, knowledge_service, xp_service):
        """Test reading knowledge and XP award"""
        # Index knowledge
        knowledge_service.index_knowledge_base()

        # Read knowledge
        result = knowledge_service.read_knowledge(1, xp_service, time_spent_seconds=120)

        assert result['read'] is True
        assert result['xp_awarded'] > 0
        assert 'title' in result

    def test_read_knowledge_insufficient_level(self, knowledge_service, xp_service):
        """Test reading locked knowledge"""
        # Index and lock knowledge
        knowledge_service.index_knowledge_base()

        import sqlite3
        conn = sqlite3.connect(knowledge_service.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE knowledge_items SET required_level = 5, skill_tree = ? WHERE id = 1",
                      (SkillTree.SHELTER.value,))
        conn.commit()
        conn.close()

        # Try to read
        result = knowledge_service.read_knowledge(1, xp_service)

        assert 'error' in result

    def test_contribute_knowledge(self, knowledge_service, xp_service):
        """Test knowledge contribution"""
        # Index knowledge
        knowledge_service.index_knowledge_base()

        # Make contribution
        result = knowledge_service.contribute_knowledge(
            knowledge_id=1,
            contribution_type="correction",
            description="Fixed typo in shelter guide",
            xp_service=xp_service
        )

        assert result['contributed'] is True
        assert result['xp_awarded'] > 0
        assert result['type'] == "correction"

    def test_search_knowledge_by_query(self, knowledge_service):
        """Test searching knowledge by query"""
        knowledge_service.index_knowledge_base()

        results = knowledge_service.search_knowledge(query="water")

        assert len(results) > 0
        assert any('water' in r['title'].lower() or 'water' in r.get('category', '').lower()
                  for r in results)

    def test_search_knowledge_by_skill_tree(self, knowledge_service):
        """Test filtering by skill tree"""
        knowledge_service.index_knowledge_base()

        results = knowledge_service.search_knowledge(skill_tree=SkillTree.WATER)

        assert len(results) > 0
        assert all(r['skill_tree'] == SkillTree.WATER.value for r in results)

    def test_search_with_access_filter(self, knowledge_service, xp_service):
        """Test search with accessibility check"""
        knowledge_service.index_knowledge_base()

        results = knowledge_service.search_knowledge(xp_service=xp_service)

        assert len(results) > 0
        # All should be accessible since they're level 0
        assert all(r.get('accessible', False) for r in results)

    def test_get_reading_stats(self, knowledge_service, xp_service):
        """Test reading statistics"""
        knowledge_service.index_knowledge_base()

        # Read some knowledge
        knowledge_service.read_knowledge(1, xp_service, time_spent_seconds=60)
        knowledge_service.read_knowledge(2, xp_service, time_spent_seconds=120)

        stats = knowledge_service.get_reading_stats()

        assert stats['total_reads'] == 2
        assert stats['total_xp'] > 0
        assert stats['total_time_hours'] > 0

    def test_get_total_knowledge_count(self, knowledge_service):
        """Test counting total knowledge items"""
        knowledge_service.index_knowledge_base()

        count = knowledge_service.get_total_knowledge_count()

        assert count == 3

    def test_get_knowledge_by_skill(self, knowledge_service):
        """Test getting knowledge by skill tree"""
        knowledge_service.index_knowledge_base()

        water_knowledge = knowledge_service.get_knowledge_by_skill(SkillTree.WATER)

        assert len(water_knowledge) > 0
        assert all(k['skill_tree'] == SkillTree.WATER.value for k in water_knowledge)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
