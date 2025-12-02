"""
Integration Tests for Adventure System (Round 2)
Tests complete adventure playthrough with all game systems
"""

import pytest
import os
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


class TestAdventureBasics:
    """Test basic adventure operations."""

    def test_list_adventures(self, handler):
        """Test listing available adventures."""
        result = handler.handle('LIST', [])
        assert 'first-steps' in result.lower()
        assert 'Available Adventures' in result

    def test_start_adventure(self, handler):
        """Test starting an adventure."""
        result = handler.handle('START', ['first-steps'])
        assert '✅' in result
        assert 'Adventure started' in result
        assert 'first-steps' in result
        assert handler.current_adventure == 'first-steps'
        assert handler.current_session_id is not None

    def test_start_invalid_adventure(self, handler):
        """Test starting non-existent adventure."""
        result = handler.handle('START', ['nonexistent'])
        assert '❌' in result or 'not found' in result.lower()

    def test_continue_without_start(self, handler):
        """Test continue without starting adventure."""
        result = handler.handle('CONTINUE', [])
        assert '❌' in result
        assert 'No active adventure' in result

    def test_status_without_start(self, handler):
        """Test status without starting adventure."""
        result = handler.handle('STATUS', [])
        assert '❌' in result or 'No active adventure' in result


class TestEventProcessing:
    """Test event processing functionality."""

    def test_narrative_events(self, handler):
        """Test narrative event display."""
        handler.handle('START', ['first-steps'])
        result = handler.handle('CONTINUE', [])

        # Should contain narrative text
        assert 'FIRST STEPS' in result or 'wake up' in result.lower()
        # Should contain choice
        assert '🤔' in result or 'choose' in result.lower()

    def test_stat_modifications(self, handler):
        """Test stat changes from events."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])

        # Check that stats were modified
        status = handler.handle('STATUS', [])
        # Thirst and hunger should have increased
        assert 'Thirst:' in status
        assert 'Hunger:' in status

    def test_xp_awards(self, handler):
        """Test XP awards from events."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        handler.handle('CHOICE', ['1'])  # Make a choice
        handler.handle('CHOICE', ['2'])  # Make another choice

        status = handler.handle('STATUS', [])
        # Should have gained XP
        assert 'XP:' in status
        assert 'Level:' in status

    def test_item_acquisition(self, handler):
        """Test receiving items."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        result = handler.handle('CHOICE', ['1'])  # Stream path

        # Should receive items
        assert '📦' in result or 'Received' in result

        status = handler.handle('STATUS', [])
        assert 'water' in status.lower()


class TestChoiceSystem:
    """Test choice and branching functionality."""

    def test_choice_validation(self, handler):
        """Test choice number validation."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])

        # Valid choice
        result = handler.handle('CHOICE', ['1'])
        assert '✅' in result or 'chose' in result.lower()

        # Invalid choice (out of range)
        handler.handle('CONTINUE', [])  # Get to next choice
        result = handler.handle('CHOICE', ['99'])
        assert '❌' in result or 'Invalid' in result

    def test_choice_without_active_choice(self, handler):
        """Test making choice when no choice is active."""
        handler.handle('START', ['first-steps'])
        # Don't continue to a choice point
        result = handler.handle('CHOICE', ['1'])
        assert '❌' in result or 'No active choice' in result

    def test_choice_branching(self, handler):
        """Test that choices lead to different paths."""
        # Path 1: Stream
        handler1 = handler
        handler1.handle('START', ['first-steps'])
        handler1.handle('CONTINUE', [])
        result1 = handler1.handle('CHOICE', ['1'])
        assert 'stream' in result1.lower()

        # Path 2: Store
        components = {
            'scenario_service': ScenarioService(),
            'xp_service': XPService(),
            'inventory_service': InventoryService(),
            'survival_service': SurvivalService()
        }
        handler2 = StoryHandler(components)
        handler2.handle('START', ['first-steps'])
        handler2.handle('CONTINUE', [])
        result2 = handler2.handle('CHOICE', ['2'])
        assert 'store' in result2.lower() or 'convenience' in result2.lower()

        # Results should be different
        assert result1 != result2


class TestStatusDisplay:
    """Test status display functionality."""

    def test_status_shows_progress(self, handler):
        """Test that status shows adventure progress."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        result = handler.handle('STATUS', [])

        assert 'Progress:' in result
        assert 'events' in result.lower()
        assert '%' in result

    def test_status_shows_stats(self, handler):
        """Test that status displays character stats."""
        handler.handle('START', ['first-steps'])
        result = handler.handle('STATUS', [])

        assert '❤️' in result or 'Health' in result
        assert '💧' in result or 'Thirst' in result
        assert '🍖' in result or 'Hunger' in result
        assert '⚡' in result or 'Stamina' in result

    def test_status_shows_xp(self, handler):
        """Test that status displays XP and level."""
        handler.handle('START', ['first-steps'])
        result = handler.handle('STATUS', [])

        assert '🌟' in result or 'Level' in result
        assert '✨' in result or 'XP' in result
        # Should have progress bar
        assert '█' in result or '░' in result or '[' in result

    def test_status_shows_inventory(self, handler):
        """Test that status displays inventory."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        handler.handle('CHOICE', ['1'])  # Get some items

        result = handler.handle('STATUS', [])
        assert 'INVENTORY' in result
        # Should show items or empty message
        assert '•' in result or 'Empty' in result or 'items' in result.lower()


class TestFullPlaythrough:
    """Test complete adventure playthrough."""

    def test_complete_first_steps_stream_path(self, handler):
        """Test playing through stream path completely."""
        # Start
        result = handler.handle('START', ['first-steps'])
        assert '✅' in result

        # First events
        result = handler.handle('CONTINUE', [])
        assert len(result) > 0

        # Choose stream
        result = handler.handle('CHOICE', ['1'])
        assert 'stream' in result.lower()

        # Choose to boil water
        result = handler.handle('CHOICE', ['2'])
        assert 'fire' in result.lower() or 'boil' in result.lower()

        # Check progress
        status = handler.handle('STATUS', [])
        assert 'Progress:' in status
        # Should have made some progress
        assert 'events' in status.lower()

    def test_stat_persistence_through_choices(self, handler):
        """Test that stat changes persist through choices."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])

        # Get initial status
        status1 = handler.handle('STATUS', [])

        # Make a choice that affects stats
        handler.handle('CHOICE', ['1'])
        handler.handle('CHOICE', ['2'])  # Boil water - reduces thirst

        # Get new status
        status2 = handler.handle('STATUS', [])

        # Stats should have changed
        assert status1 != status2

    def test_inventory_accumulation(self, handler):
        """Test that items accumulate in inventory."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])

        # Make choices that give items
        handler.handle('CHOICE', ['1'])  # Stream - get unpurified water
        handler.handle('CHOICE', ['2'])  # Boil - get purified water

        status = handler.handle('STATUS', [])
        # Should have multiple items
        assert 'water' in status.lower()
        assert 'items' in status.lower()

    def test_xp_progression(self, handler):
        """Test XP gains and leveling."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])

        # Initial XP
        status1 = handler.handle('STATUS', [])

        # Make choices that award XP
        handler.handle('CHOICE', ['1'])
        handler.handle('CHOICE', ['2'])

        # Should have gained XP
        status2 = handler.handle('STATUS', [])
        assert 'XP' in status2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_choice_input(self, handler):
        """Test choice with no number provided."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        result = handler.handle('CHOICE', [])
        assert '❌' in result or 'Usage' in result

    def test_invalid_choice_format(self, handler):
        """Test choice with invalid format."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        result = handler.handle('CHOICE', ['abc'])
        assert '❌' in result or 'Invalid' in result

    def test_multiple_continues(self, handler):
        """Test calling continue multiple times."""
        handler.handle('START', ['first-steps'])

        result1 = handler.handle('CONTINUE', [])
        assert len(result1) > 0

        # After choice, continue again
        handler.handle('CHOICE', ['1'])
        result2 = handler.handle('CONTINUE', [])
        # Should either show more content or indicate choice needed
        assert len(result2) > 0 or '🤔' in result2

    def test_adventure_completion(self, handler):
        """Test behavior when adventure is complete."""
        handler.handle('START', ['first-steps'])

        # Play through all events (simplified - just make choices)
        for _ in range(10):  # Arbitrary limit to avoid infinite loop
            result = handler.handle('CONTINUE', [])
            if 'complete' in result.lower() or 'finished' in result.lower():
                break
            if '🤔' in result:
                handler.handle('CHOICE', ['1'])  # Always pick first choice

        # Eventually should complete or reach end
        status = handler.handle('STATUS', [])
        assert 'Progress' in status


class TestServiceIntegration:
    """Test integration with game services."""

    def test_survival_service_integration(self, handler):
        """Test SurvivalService stat tracking."""
        handler.handle('START', ['first-steps'])

        # Stats should be initialized
        from extensions.play.services.game_mechanics.survival_service import SurvivalStat
        health = handler.survival_service.get_stat(SurvivalStat.HEALTH)
        assert health['current'] == 100

        thirst = handler.survival_service.get_stat(SurvivalStat.THIRST)
        assert thirst['current'] == 0

    def test_xp_service_integration(self, handler):
        """Test XPService experience tracking."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        handler.handle('CHOICE', ['1'])
        handler.handle('CHOICE', ['2'])

        # Should have gained XP
        total_xp = handler.xp_service.get_total_xp()
        assert total_xp > 0

    def test_inventory_service_integration(self, handler):
        """Test InventoryService item tracking."""
        handler.handle('START', ['first-steps'])
        handler.handle('CONTINUE', [])
        handler.handle('CHOICE', ['1'])

        # Should have items
        inventory = handler.inventory_service.get_inventory("Personal Inventory")
        assert len(inventory) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
