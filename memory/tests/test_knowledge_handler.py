"""
Test suite for KnowledgeCommandHandler v1.0.18
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.services.xp_service import XPService, SkillTree
from core.services.knowledge_service import KnowledgeService
from core.commands.knowledge_handler import KnowledgeCommandHandler


class TestKnowledgeCommandHandler:
    """Test knowledge command handler."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def knowledge_base(self, temp_dir):
        """Create test knowledge base."""
        knowledge_dir = os.path.join(temp_dir, 'knowledge')

        # Create knowledge directories
        building_dir = os.path.join(knowledge_dir, 'building')
        water_dir = os.path.join(knowledge_dir, 'water')
        food_dir = os.path.join(knowledge_dir, 'food')

        os.makedirs(building_dir, exist_ok=True)
        os.makedirs(water_dir, exist_ok=True)
        os.makedirs(food_dir, exist_ok=True)

        # Create test markdown files
        shelter_content = """# Shelter Basics

Learn how to build basic emergency shelter.

## Materials
- Tarps
- Rope
- Branches

## Steps
1. Find suitable location
2. Gather materials
3. Construct frame
4. Add covering
"""

        water_content = """# Water Purification Methods

---
tags: water, health, purification
---

Essential knowledge for safe drinking water.

## Methods
- Boiling
- Filtering
- Chemical treatment
"""

        food_content = """# Foraging Guide

Advanced guide to identifying edible plants.

## Safety
- Always positively identify plants
- Test small amounts first
- Know poisonous look-alikes
"""

        # Write files
        with open(os.path.join(building_dir, 'shelter_basics.md'), 'w') as f:
            f.write(shelter_content)

        with open(os.path.join(water_dir, 'purification.md'), 'w') as f:
            f.write(water_content)

        with open(os.path.join(food_dir, 'foraging.md'), 'w') as f:
            f.write(food_content)

        return knowledge_dir

    @pytest.fixture
    def services(self, temp_dir, knowledge_base):
        """Create service instances."""
        xp_db = os.path.join(temp_dir, 'xp.db')

        xp_service = XPService(xp_db)
        knowledge_service = KnowledgeService(
            data_dir=temp_dir,
            knowledge_dir=knowledge_base
        )

        return xp_service, knowledge_service

    @pytest.fixture
    def handler(self, services):
        """Create command handler."""
        xp_service, knowledge_service = services
        return KnowledgeCommandHandler(xp_service, knowledge_service)

    def test_index_command(self, handler, knowledge_base, temp_dir):
        """Test INDEX command."""
        result = handler.handle_command('INDEX', [])

        assert result['success'] is True
        assert result['indexed'] == 3
        assert result['total'] == 3
        assert 'message' in result

    def test_search_command(self, handler, knowledge_base, temp_dir):
        """Test SEARCH command."""
        # Index first
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            # Search
            result = handler.handle_command('SEARCH', ['water'])

            assert result['success'] is True
            assert result['query'] == 'water'
            assert result['count'] >= 1
            assert 'results' in result
        finally:
            os.chdir(original_cwd)

    def test_search_command_with_skill_tree(self, handler, knowledge_base, temp_dir):
        """Test SEARCH command with skill tree filter."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            result = handler.handle_command('SEARCH', ['', 'WATER'])

            assert result['success'] is True
            assert result['skill_tree'] == 'WATER'
        finally:
            os.chdir(original_cwd)

    def test_search_command_invalid_skill_tree(self, handler):
        """Test SEARCH command with invalid skill tree."""
        result = handler.handle_command('SEARCH', ['query', 'INVALID'])

        assert result['success'] is False
        assert 'error' in result
        assert 'valid_trees' in result

    def test_search_command_no_query(self, handler):
        """Test SEARCH command without query."""
        result = handler.handle_command('SEARCH', [])

        assert result['success'] is False
        assert 'error' in result

    def test_list_command(self, handler, knowledge_base, temp_dir):
        """Test LIST command."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            result = handler.handle_command('LIST', [])

            assert result['success'] is True
            assert result['skill_tree'] == 'ALL'
            assert result['count'] == 3
        finally:
            os.chdir(original_cwd)

    def test_list_command_with_skill_tree(self, handler, knowledge_base, temp_dir):
        """Test LIST command with skill tree filter."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            result = handler.handle_command('LIST', ['SHELTER'])

            assert result['success'] is True
            assert result['skill_tree'] == 'SHELTER'
            assert result['count'] == 1
        finally:
            os.chdir(original_cwd)

    def test_read_command(self, handler, knowledge_base, temp_dir):
        """Test READ command."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            # Get knowledge ID
            list_result = handler.handle_command('LIST', [])
            knowledge_id = list_result['items'][0]['id']

            # Read
            result = handler.handle_command('READ', [str(knowledge_id)])

            assert result['success'] is True
            assert result['knowledge_id'] == knowledge_id
            assert result['xp_awarded'] > 0
            assert 'message' in result
        finally:
            os.chdir(original_cwd)

    def test_read_command_with_time(self, handler, knowledge_base, temp_dir):
        """Test READ command with time parameter."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            list_result = handler.handle_command('LIST', [])
            knowledge_id = list_result['items'][0]['id']

            result = handler.handle_command('READ', [str(knowledge_id), '120'])

            assert result['success'] is True
        finally:
            os.chdir(original_cwd)

    def test_read_command_invalid_id(self, handler):
        """Test READ command with invalid ID."""
        result = handler.handle_command('READ', ['invalid'])

        assert result['success'] is False
        assert 'error' in result

    def test_read_command_no_args(self, handler):
        """Test READ command without arguments."""
        result = handler.handle_command('READ', [])

        assert result['success'] is False
        assert 'error' in result

    def test_contribute_command(self, handler, knowledge_base, temp_dir):
        """Test CONTRIBUTE command."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            list_result = handler.handle_command('LIST', [])
            knowledge_id = list_result['items'][0]['id']

            result = handler.handle_command('CONTRIBUTE',
                [str(knowledge_id), 'correction', 'Fixed', 'typo'])

            assert result['success'] is True
            assert result['knowledge_id'] == knowledge_id
            assert result['contribution_type'] == 'correction'
            assert result['xp_awarded'] > 0
        finally:
            os.chdir(original_cwd)

    def test_contribute_command_invalid_type(self, handler, knowledge_base, temp_dir):
        """Test CONTRIBUTE command with invalid type."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            list_result = handler.handle_command('LIST', [])
            knowledge_id = list_result['items'][0]['id']

            result = handler.handle_command('CONTRIBUTE',
                [str(knowledge_id), 'invalid', 'test'])

            assert result['success'] is False
            assert 'valid_types' in result
        finally:
            os.chdir(original_cwd)

    def test_contribute_command_insufficient_args(self, handler):
        """Test CONTRIBUTE command without enough arguments."""
        result = handler.handle_command('CONTRIBUTE', ['1', 'correction'])

        assert result['success'] is False
        assert 'error' in result
        assert 'valid_types' in result

    def test_stats_command(self, handler, knowledge_base, temp_dir):
        """Test STATS command."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            # Read something first
            list_result = handler.handle_command('LIST', [])
            knowledge_id = list_result['items'][0]['id']
            handler.handle_command('READ', [str(knowledge_id)])

            # Get stats
            result = handler.handle_command('STATS', [])

            assert result['success'] is True
            assert result['total_reads'] == 1
            assert result['total_xp'] > 0
            assert 'message' in result
        finally:
            os.chdir(original_cwd)

    def test_info_command(self, handler, knowledge_base, temp_dir):
        """Test INFO command."""
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            handler.handle_command('INDEX', [])

            list_result = handler.handle_command('LIST', [])
            knowledge_id = list_result['items'][0]['id']

            result = handler.handle_command('INFO', [str(knowledge_id)])

            assert result['success'] is True
            assert 'item' in result
            assert result['item']['id'] == knowledge_id
            assert 'title' in result['item']
            assert 'accessible' in result['item']
        finally:
            os.chdir(original_cwd)

    def test_info_command_invalid_id(self, handler):
        """Test INFO command with invalid ID."""
        result = handler.handle_command('INFO', ['999'])

        assert result['success'] is False
        assert 'error' in result

    def test_info_command_no_args(self, handler):
        """Test INFO command without arguments."""
        result = handler.handle_command('INFO', [])

        assert result['success'] is False
        assert 'error' in result

    def test_unknown_command(self, handler):
        """Test unknown command."""
        result = handler.handle_command('UNKNOWN', [])

        assert result['success'] is False
        assert 'error' in result
        assert 'available_commands' in result
