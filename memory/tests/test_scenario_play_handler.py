"""
Tests for Scenario Play Handler
"""

import os
import sys
import pytest
import tempfile
import shutil
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.commands.scenario_play_handler import ScenarioPlayHandler


class TestScenarioPlayHandler:
    """Test ScenarioPlayHandler functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory"""
        temp = tempfile.mkdtemp()

        # Create scenarios directory
        scenarios_dir = os.path.join(temp, "memory", "scenarios")
        os.makedirs(scenarios_dir, exist_ok=True)

        # Create test scenario
        test_scenario = {
            "metadata": {
                "name": "test_scenario",
                "title": "Test Scenario",
                "type": "tutorial",
                "difficulty": 1,
                "estimated_minutes": 15,
                "description": "A test scenario",
                "xp_reward": 50
            },
            "initial_variables": {
                "test_var": "hello"
            },
            "events": [
                {
                    "type": "narrative",
                    "text": "Welcome to the test!"
                },
                {
                    "type": "choice",
                    "prompt": "Choose one:",
                    "options": [
                        {"text": "Option A", "variable": "choice", "value": "a"},
                        {"text": "Option B", "variable": "choice", "value": "b"}
                    ]
                },
                {
                    "type": "narrative",
                    "text": "You chose wisely."
                },
                {
                    "type": "xp_award",
                    "amount": 25,
                    "category": "usage",
                    "reason": "Test completion"
                },
                {
                    "type": "end",
                    "outcome": "success",
                    "message": "Test complete!"
                }
            ]
        }

        with open(os.path.join(scenarios_dir, "test_scenario.json"), 'w') as f:
            json.dump(test_scenario, f)

        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def handler(self, temp_dir):
        """Create handler instance"""
        # Change to temp directory so handler finds scenarios
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        handler = ScenarioPlayHandler(data_dir=os.path.join(temp_dir, "data"))

        yield handler

        os.chdir(original_dir)

    def test_list_scenarios(self, handler):
        """Test listing available scenarios"""
        result = handler.handle_command("PLAY", ["list"])

        assert result['type'] == 'scenario_list'
        assert result['count'] >= 1

        # Check test scenario is in list
        scenarios = result['scenarios']
        test_scenario = next((s for s in scenarios if s['name'] == 'test_scenario'), None)
        assert test_scenario is not None
        assert test_scenario['title'] == 'Test Scenario'

    def test_start_scenario(self, handler):
        """Test starting a scenario"""
        result = handler.handle_command("PLAY", ["start", "test_scenario"])

        assert result['type'] == 'scenario_events'
        assert len(result['events']) > 0

        # First event should be narrative
        first_event = result['events'][0]
        assert first_event['type'] == 'narrative'
        assert 'Welcome' in first_event['text']

    def test_make_choice(self, handler):
        """Test making a choice in scenario"""
        # Start scenario
        handler.handle_command("PLAY", ["start", "test_scenario"])

        # Should be awaiting choice now
        assert handler.awaiting_choice is True

        # Make choice
        result = handler.handle_command("PLAY", ["choose", "1"])

        assert result['type'] == 'choice_and_continue'
        assert result['choice_result']['option'] == 'Option A'

    def test_scenario_status(self, handler):
        """Test getting scenario status"""
        # Start scenario
        handler.handle_command("PLAY", ["start", "test_scenario"])

        # Get status
        result = handler.handle_command("PLAY", ["status"])

        assert result['type'] == 'scenario_status'
        assert 'session_info' in result
        assert 'variables' in result

    def test_save_progress(self, handler):
        """Test saving scenario progress"""
        # Start scenario
        handler.handle_command("PLAY", ["start", "test_scenario"])

        # Save
        result = handler.handle_command("PLAY", ["save"])

        assert 'saved' in result or 'error' not in result

    def test_quit_scenario(self, handler):
        """Test quitting scenario"""
        # Start scenario
        handler.handle_command("PLAY", ["start", "test_scenario"])

        # Quit
        result = handler.handle_command("PLAY", ["quit"])

        assert result['type'] == 'scenario_quit'
        assert handler.engine.current_session_id is None

    def test_invalid_scenario(self, handler):
        """Test starting non-existent scenario"""
        result = handler.handle_command("PLAY", ["start", "nonexistent"])

        assert 'error' in result

    def test_invalid_choice(self, handler):
        """Test invalid choice number"""
        # Start scenario
        handler.handle_command("PLAY", ["start", "test_scenario"])

        # Try invalid choice
        result = handler.handle_command("PLAY", ["choose", "99"])

        assert 'error' in result

    def test_help_command(self, handler):
        """Test help display"""
        result = handler.handle_command("PLAY", [])

        assert result['type'] == 'help'
        assert 'PLAY LIST' in result['message']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
