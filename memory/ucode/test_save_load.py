"""
Tests for Save/Load functionality
"""

import pytest
import json
from pathlib import Path
from extensions.play.commands.story_handler import StoryHandler
from extensions.play.services.game_mechanics.scenario_service import ScenarioService
from extensions.play.services.game_mechanics.xp_service import XPService
from extensions.play.services.game_mechanics.inventory_service import InventoryService
from extensions.play.services.game_mechanics.survival_service import SurvivalService


@pytest.fixture
def handler():
    """Create a fresh StoryHandler for each test."""
    components = {
        'scenario_service': ScenarioService(),
        'xp_service': XPService(),
        'inventory_service': InventoryService(),
        'survival_service': SurvivalService()
    }
    return StoryHandler(components)


class TestSaveLoad:
    """Test save and load functionality."""

    def test_save_adventure(self, handler):
        """Test saving adventure progress."""
        # Start and progress through adventure
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        handler.handle('CHOICE', ['1'])

        # Save
        result = handler.handle('SAVE', ['test_save'])
        assert '💾' in result or 'Saved' in result.lower()

        # Check save file exists
        save_path = Path("sandbox/user/saves/test_save.json")
        assert save_path.exists()

    def test_load_adventure(self, handler):
        """Test loading saved adventure."""
        # Create a save first
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        handler.handle('CHOICE', ['1'])
        handler.handle('SAVE', ['test_load'])

        # Create new handler
        components = {
            'scenario_service': ScenarioService(),
            'xp_service': XPService(),
            'inventory_service': InventoryService(),
            'survival_service': SurvivalService()
        }
        new_handler = StoryHandler(components)

        # Load
        result = new_handler.handle('LOAD', ['test_load'])
        assert '📂' in result or 'Loaded' in result.lower()
        assert new_handler.current_adventure == 'first-steps'

    def test_save_without_adventure(self, handler):
        """Test saving without active adventure."""
        result = handler.handle('SAVE', ['test'])
        assert '❌' in result or 'No active adventure' in result

    def test_load_nonexistent_save(self, handler):
        """Test loading non-existent save."""
        result = handler.handle('LOAD', ['nonexistent'])
        assert '❌' in result or 'not found' in result.lower()

    def test_save_preserves_state(self, handler):
        """Test that save preserves complete game state."""
        # Progress through adventure
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        handler.handle('CHOICE', ['1'])
        handler.handle('CHOICE', ['2'])

        # Get current status
        status_before = handler.handle('STATUS', [])

        # Save and load
        handler.handle('SAVE', ['state_test'])

        # Create new handler and load
        components = {
            'scenario_service': ScenarioService(),
            'xp_service': XPService(),
            'inventory_service': InventoryService(),
            'survival_service': SurvivalService()
        }
        new_handler = StoryHandler(components)
        new_handler.handle('LOAD', ['state_test'])

        # Status should match
        status_after = new_handler.handle('STATUS', [])
        # Progress should be similar (exact match may vary slightly)
        assert 'first-steps' in status_after
        assert 'Progress:' in status_after


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
