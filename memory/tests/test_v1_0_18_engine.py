"""
Tests for v1.0.18 Scenario Engine
Tests event processing and scenario execution
"""

import os
import sys
import pytest
import tempfile
import shutil
import json

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.services.scenario_service import ScenarioService, ScenarioType
from core.services.scenario_engine import ScenarioEngine, EventType
from core.services.xp_service import XPService, XPCategory
from core.services.inventory_service import InventoryService, ItemCategory
from core.services.survival_service import SurvivalService, SurvivalStat, StatusEffect


class TestScenarioEngine:
    """Test ScenarioEngine functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def services(self, temp_dir):
        """Create service instances"""
        scenario_service = ScenarioService(data_dir=temp_dir)
        xp_service = XPService(db_path=os.path.join(temp_dir, "xp.db"))
        inventory_service = InventoryService(data_dir=temp_dir)
        survival_service = SurvivalService(data_dir=temp_dir)

        return {
            'scenario': scenario_service,
            'xp': xp_service,
            'inventory': inventory_service,
            'survival': survival_service
        }

    @pytest.fixture
    def engine(self, services):
        """Create ScenarioEngine instance"""
        return ScenarioEngine(
            scenario_service=services['scenario'],
            xp_service=services['xp'],
            inventory_service=services['inventory'],
            survival_service=services['survival']
        )

    @pytest.fixture
    def test_script_path(self, temp_dir):
        """Create a test scenario script"""
        script = {
            "metadata": {
                "name": "test_scenario",
                "title": "Test Scenario",
                "type": "tutorial"
            },
            "initial_variables": {
                "player_name": "Tester",
                "score": 0
            },
            "events": [
                {
                    "type": "narrative",
                    "text": "Welcome, {player_name}!"
                },
                {
                    "type": "xp_award",
                    "amount": 50,
                    "category": "usage",
                    "reason": "Test XP"
                }
            ]
        }

        path = os.path.join(temp_dir, "test_scenario.json")
        with open(path, 'w') as f:
            json.dump(script, f)

        return path

    def test_load_scenario_script(self, engine, test_script_path):
        """Test loading scenario script from file"""
        script = engine.load_scenario_script(test_script_path)

        assert "metadata" in script
        assert script["metadata"]["name"] == "test_scenario"

    def test_load_nonexistent_script(self, engine):
        """Test loading script that doesn't exist"""
        result = engine.load_scenario_script("/nonexistent/path.json")

        assert "error" in result

    def test_start_scenario_from_script(self, engine, services, test_script_path):
        """Test starting scenario from script"""
        # Register scenario first
        services['scenario'].register_scenario(
            "test_scenario", ScenarioType.TUTORIAL, "Test"
        )

        result = engine.start_scenario_from_script(test_script_path)

        assert "session_id" in result
        assert engine.current_session_id is not None

    def test_process_narrative_event(self, engine, services):
        """Test processing narrative event"""
        # Setup session
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        # Set variable for substitution
        services['scenario'].set_variable(session['session_id'], "player_name", "Hero")

        event = {
            "type": "narrative",
            "text": "Hello, {player_name}!",
            "speaker": "Guide"
        }

        result = engine.process_event(event)

        assert result['type'] == 'narrative'
        assert result['text'] == "Hello, Hero!"
        assert result['speaker'] == "Guide"

    def test_process_choice_event(self, engine, services):
        """Test processing choice event"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        event = {
            "type": "choice",
            "prompt": "What do you choose?",
            "options": [
                {"text": "Option A", "value": "a"},
                {"text": "Option B", "value": "b"}
            ]
        }

        result = engine.process_event(event)

        assert result['type'] == 'choice'
        assert result['requires_input'] is True
        assert len(result['options']) == 2

    def test_process_item_give(self, engine, services):
        """Test giving items to player"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        event = {
            "type": "item_give",
            "item": "Test Item",
            "quantity": 2,
            "category": "misc",
            "weight": 1.0,
            "volume": 0.5
        }

        result = engine.process_event(event)

        assert result['type'] == 'item_give'
        assert result['item'] == "Test Item"

        # Verify item in inventory
        inventory = services['inventory'].get_inventory()
        assert len(inventory) == 1
        assert inventory[0]['name'] == "Test Item"

    def test_process_item_take(self, engine, services):
        """Test taking items from player"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        # Add item first
        services['inventory'].add_item("Test Item", category=ItemCategory.MISC, quantity=5)

        event = {
            "type": "item_take",
            "item": "Test Item",
            "quantity": 2
        }

        result = engine.process_event(event)

        assert result['type'] == 'item_take'

        # Verify quantity reduced
        inventory = services['inventory'].get_inventory()
        assert inventory[0]['quantity'] == 3

    def test_process_stat_change(self, engine, services):
        """Test changing survival stats"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        # Set initial stat
        services['survival'].set_stat(SurvivalStat.HEALTH, 100)

        event = {
            "type": "stat_change",
            "stat": "health",
            "change": -20
        }

        result = engine.process_event(event)

        assert result['type'] == 'stat_change'
        assert result['new_value'] == 80

    def test_process_effect_add(self, engine, services):
        """Test adding status effects"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        event = {
            "type": "effect_add",
            "effect": "tired",
            "duration": 2
        }

        result = engine.process_event(event)

        assert result['type'] == 'effect_add'

        # Verify effect added
        effects = services['survival'].get_active_effects()
        assert len(effects) > 0

    def test_process_xp_award(self, engine, services):
        """Test awarding XP"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        event = {
            "type": "xp_award",
            "amount": 100,
            "category": "usage",
            "reason": "Test XP"
        }

        result = engine.process_event(event)

        assert result['type'] == 'xp_award'
        assert result['amount'] == 100

        # Verify XP awarded
        total = services['xp'].get_total_xp()
        assert total == 100

    def test_process_time_pass(self, engine, services):
        """Test time passage and decay"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        # Set initial stats
        services['survival'].set_stat(SurvivalStat.HUNGER, 0)

        event = {
            "type": "time_pass",
            "hours": 2
        }

        result = engine.process_event(event)

        assert result['type'] == 'time_pass'
        assert result['hours'] == 2

        # Verify hunger increased (2 hours * 10 per hour = 20)
        hunger_dict = services['survival'].get_stat(SurvivalStat.HUNGER)
        assert hunger_dict['current'] == 20

    def test_process_checkpoint(self, engine, services):
        """Test creating checkpoint"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']
        engine.event_index = 5

        event = {
            "type": "checkpoint",
            "name": "test_checkpoint"
        }

        result = engine.process_event(event)

        assert result['type'] == 'checkpoint'
        assert result['name'] == "test_checkpoint"

    def test_process_end(self, engine, services):
        """Test scenario end"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        event = {
            "type": "end",
            "outcome": "success",
            "message": "You win!",
            "xp": 200
        }

        result = engine.process_event(event)

        assert result['type'] == 'end'
        assert result['outcome'] == "success"

        # Verify final XP awarded
        total = services['xp'].get_total_xp()
        assert total == 200

    def test_variable_substitution(self, engine, services):
        """Test variable substitution in text"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        services['scenario'].set_variable(session['session_id'], "name", "Alice")
        services['scenario'].set_variable(session['session_id'], "score", 100)

        text = "Hello {name}, your score is {score}!"
        result = engine._substitute_variables(text)

        assert result == "Hello Alice, your score is 100!"

    def test_evaluate_condition_equals(self, engine, services):
        """Test condition evaluation with =="""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        services['scenario'].set_variable(session['session_id'], "choice", "yes")

        assert engine._evaluate_condition("{choice} == yes") is True
        assert engine._evaluate_condition("{choice} == no") is False

    def test_evaluate_condition_greater(self, engine, services):
        """Test condition evaluation with >"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']

        services['scenario'].set_variable(session['session_id'], "score", 50)

        assert engine._evaluate_condition("{score} > 25") is True
        assert engine._evaluate_condition("{score} > 100") is False

    def test_save_and_restore_progress(self, engine, services):
        """Test saving and restoring scenario progress"""
        services['scenario'].register_scenario("test", ScenarioType.TUTORIAL, "Test")
        session = services['scenario'].start_scenario("test")
        engine.current_session_id = session['session_id']
        engine.event_index = 10

        # Save
        save_result = engine.save_progress()
        assert save_result['saved'] is True

        # Reset
        engine.event_index = 0

        # Restore
        restore_result = engine.restore_progress(session['session_id'])
        assert restore_result['restored'] is True
        assert engine.event_index == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
