"""
Tests for v1.0.18 Scenario System
Tests scenarios, quests, variables, and adventure commands
"""

import os
import sys
import pytest
import tempfile
import shutil

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.services.scenario_service import (
    ScenarioService, ScenarioType, QuestStatus
)
from core.commands.scenario_handler import ScenarioCommandHandler


class TestScenarioService:
    """Test ScenarioService functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def scenario_service(self, temp_dir):
        """Create ScenarioService instance"""
        return ScenarioService(data_dir=temp_dir)

    def test_init_creates_database(self, scenario_service):
        """Test database initialization"""
        assert os.path.exists(scenario_service.db_path)

    def test_register_scenario(self, scenario_service):
        """Test registering a new scenario"""
        result = scenario_service.register_scenario(
            name="test_scenario",
            scenario_type=ScenarioType.TUTORIAL,
            title="Test Scenario",
            description="A test scenario",
            difficulty=1,
            estimated_minutes=15,
            xp_reward=50
        )

        assert result['name'] == "test_scenario"
        assert result['type'] == "tutorial"

    def test_start_scenario(self, scenario_service):
        """Test starting a scenario"""
        # Register first
        scenario_service.register_scenario(
            "intro", ScenarioType.TUTORIAL, "Introduction"
        )

        # Start
        result = scenario_service.start_scenario("intro")

        assert result['started'] is True
        assert 'session_id' in result

    def test_start_nonexistent_scenario(self, scenario_service):
        """Test starting scenario that doesn't exist"""
        result = scenario_service.start_scenario("nonexistent")

        assert 'error' in result

    def test_save_and_load_state(self, scenario_service):
        """Test saving and loading game state"""
        # Create session
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        # Save state
        state = {"player_position": [10, 5], "health": 100}
        save_result = scenario_service.save_state(session_id, state)
        assert save_result['saved'] is True

        # Load state
        loaded = scenario_service.load_state(session_id)
        assert loaded == state

    def test_create_checkpoint(self, scenario_service):
        """Test creating named checkpoint"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        state = {"checkpoint_data": "test"}
        result = scenario_service.create_checkpoint(session_id, "save1", state)

        assert result['created'] is True
        assert result['checkpoint'] == "save1"

    def test_restore_checkpoint(self, scenario_service):
        """Test restoring from checkpoint"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        # Create checkpoint
        original_state = {"value": 42}
        scenario_service.create_checkpoint(session_id, "checkpoint1", original_state)

        # Change state
        scenario_service.save_state(session_id, {"value": 99})

        # Restore
        restored = scenario_service.restore_checkpoint(session_id, "checkpoint1")
        assert restored == original_state

    def test_set_and_get_variable(self, scenario_service):
        """Test setting and getting scenario variables"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        # Set variable
        result = scenario_service.set_variable(session_id, "player_name", "Hero")
        assert result['variable'] == "player_name"
        assert result['value'] == "Hero"

        # Get variable
        value = scenario_service.get_variable(session_id, "player_name")
        assert value == "Hero"

    def test_get_variable_default(self, scenario_service):
        """Test getting variable with default"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        value = scenario_service.get_variable(session_id, "nonexistent", "default")
        assert value == "default"

    def test_get_all_variables(self, scenario_service):
        """Test getting all variables"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        scenario_service.set_variable(session_id, "var1", "value1")
        scenario_service.set_variable(session_id, "var2", 42)
        scenario_service.set_variable(session_id, "var3", True)

        variables = scenario_service.get_all_variables(session_id)

        assert len(variables) == 3
        assert variables['var1'] == "value1"
        assert variables['var2'] == 42
        assert variables['var3'] is True

    def test_add_quest(self, scenario_service):
        """Test adding quest to scenario"""
        result = scenario_service.register_scenario(
            "quest_test", ScenarioType.STORY, "Quest Test"
        )
        scenario_id = result['scenario_id']

        quest = scenario_service.add_quest(
            scenario_id=scenario_id,
            quest_name="main_quest",
            title="Find the Cure",
            description="Locate medical supplies",
            objectives=["Find hospital", "Search pharmacy", "Return to base"],
            quest_type="main",
            rewards={"xp": 100, "items": ["medicine"]}
        )

        assert quest['quest_name'] == "main_quest"
        assert quest['title'] == "Find the Cure"

    def test_start_quest(self, scenario_service):
        """Test starting a quest"""
        # Setup
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        # Get scenario ID
        info = scenario_service.get_session_info(session_id)
        scenario_id = info['scenario_id']

        # Add quest
        quest = scenario_service.add_quest(
            scenario_id, "quest1", "Test Quest",
            objectives=["Objective 1", "Objective 2"]
        )
        quest_id = quest['quest_id']

        # Start quest
        result = scenario_service.start_quest(session_id, quest_id)

        assert result['status'] == 'in_progress'
        assert result['objectives_total'] == 2

    def test_update_quest_objective(self, scenario_service):
        """Test completing quest objectives"""
        # Setup quest
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']
        info = scenario_service.get_session_info(session_id)

        quest = scenario_service.add_quest(
            info['scenario_id'], "quest1", "Test",
            objectives=["Step 1", "Step 2", "Step 3"]
        )
        scenario_service.start_quest(session_id, quest['quest_id'])

        # Complete first objective
        result = scenario_service.update_quest_objective(
            session_id, quest['quest_id'], 0, True
        )

        assert result['completed'] is True
        assert result['all_complete'] is False

    def test_quest_completion(self, scenario_service):
        """Test quest marked complete when all objectives done"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']
        info = scenario_service.get_session_info(session_id)

        quest = scenario_service.add_quest(
            info['scenario_id'], "quest1", "Test",
            objectives=["Step 1", "Step 2"]
        )
        scenario_service.start_quest(session_id, quest['quest_id'])

        # Complete all objectives
        scenario_service.update_quest_objective(session_id, quest['quest_id'], 0, True)
        result = scenario_service.update_quest_objective(session_id, quest['quest_id'], 1, True)

        assert result['all_complete'] is True
        assert result['status'] == 'completed'

    def test_get_quest_progress(self, scenario_service):
        """Test getting quest progress"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']
        info = scenario_service.get_session_info(session_id)

        quest = scenario_service.add_quest(
            info['scenario_id'], "quest1", "Test Quest",
            objectives=["A", "B", "C"]
        )
        scenario_service.start_quest(session_id, quest['quest_id'])
        scenario_service.update_quest_objective(session_id, quest['quest_id'], 0, True)

        progress = scenario_service.get_quest_progress(session_id, quest['quest_id'])

        assert progress is not None
        assert progress['status'] == 'in_progress'
        assert progress['progress_percent'] == 33  # 1 of 3

    def test_get_active_quests(self, scenario_service):
        """Test listing active quests"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']
        info = scenario_service.get_session_info(session_id)

        # Add multiple quests
        quest1 = scenario_service.add_quest(
            info['scenario_id'], "quest1", "Quest 1", objectives=["A"]
        )
        quest2 = scenario_service.add_quest(
            info['scenario_id'], "quest2", "Quest 2", objectives=["B"]
        )

        scenario_service.start_quest(session_id, quest1['quest_id'])
        scenario_service.start_quest(session_id, quest2['quest_id'])

        active = scenario_service.get_active_quests(session_id)

        assert len(active) == 2

    def test_list_scenarios(self, scenario_service):
        """Test listing all scenarios"""
        scenario_service.register_scenario("s1", ScenarioType.TUTORIAL, "Scenario 1")
        scenario_service.register_scenario("s2", ScenarioType.STORY, "Scenario 2")
        scenario_service.register_scenario("s3", ScenarioType.SURVIVAL, "Scenario 3")

        scenarios = scenario_service.list_scenarios()

        assert len(scenarios) == 3

    def test_get_session_info(self, scenario_service):
        """Test getting session information"""
        scenario_service.register_scenario("test", ScenarioType.STORY, "Test Scenario")
        session = scenario_service.start_scenario("test")
        session_id = session['session_id']

        info = scenario_service.get_session_info(session_id)

        assert info is not None
        assert info['scenario_name'] == "test"
        assert info['title'] == "Test Scenario"
        assert info['completed'] is False


class TestScenarioCommandHandler:
    """Test ScenarioCommandHandler functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test databases"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    @pytest.fixture
    def scenario_handler(self, temp_dir):
        """Create ScenarioCommandHandler instance"""
        return ScenarioCommandHandler(data_dir=temp_dir)

    def test_scenario_list(self, scenario_handler):
        """Test SCENARIO LIST command"""
        # Register some scenarios
        scenario_handler.scenario_service.register_scenario(
            "test1", ScenarioType.TUTORIAL, "Test 1"
        )

        result = scenario_handler.handle_command("SCENARIO", ["list"])

        assert result['type'] == 'scenario_list'
        assert result['total'] >= 1

    def test_scenario_start(self, scenario_handler):
        """Test SCENARIO START command"""
        scenario_handler.scenario_service.register_scenario(
            "intro", ScenarioType.TUTORIAL, "Introduction"
        )

        result = scenario_handler.handle_command("SCENARIO", ["start", "intro"])

        assert result['type'] == 'scenario_started'
        assert scenario_handler.current_session_id is not None

    def test_scenario_info(self, scenario_handler):
        """Test SCENARIO INFO command"""
        scenario_handler.scenario_service.register_scenario(
            "test", ScenarioType.STORY, "Test"
        )
        scenario_handler.handle_command("SCENARIO", ["start", "test"])

        result = scenario_handler.handle_command("SCENARIO", ["info"])

        assert result['type'] == 'scenario_info'
        assert 'info' in result

    def test_quest_list(self, scenario_handler):
        """Test QUEST LIST command"""
        scenario_handler.scenario_service.register_scenario(
            "test", ScenarioType.STORY, "Test"
        )
        scenario_handler.handle_command("SCENARIO", ["start", "test"])

        result = scenario_handler.handle_command("QUEST", ["list"])

        assert result['type'] == 'quest_list'

    def test_set_and_get_variable(self, scenario_handler):
        """Test variable set and get"""
        scenario_handler.scenario_service.register_scenario(
            "test", ScenarioType.STORY, "Test"
        )
        scenario_handler.handle_command("SCENARIO", ["start", "test"])

        scenario_handler.set_variable("test_var", "test_value")
        value = scenario_handler.get_variable("test_var")

        assert value == "test_value"

    def test_evaluate_condition_equals(self, scenario_handler):
        """Test condition evaluation =="""
        scenario_handler.scenario_service.register_scenario(
            "test", ScenarioType.STORY, "Test"
        )
        scenario_handler.handle_command("SCENARIO", ["start", "test"])

        scenario_handler.set_variable("score", 100)

        assert scenario_handler.evaluate_condition("{score} == 100") is True
        assert scenario_handler.evaluate_condition("{score} == 50") is False

    def test_evaluate_condition_greater(self, scenario_handler):
        """Test condition evaluation >"""
        scenario_handler.scenario_service.register_scenario(
            "test", ScenarioType.STORY, "Test"
        )
        scenario_handler.handle_command("SCENARIO", ["start", "test"])

        scenario_handler.set_variable("level", 5)

        assert scenario_handler.evaluate_condition("{level} > 3") is True
        assert scenario_handler.evaluate_condition("{level} > 10") is False

    def test_evaluate_condition_less(self, scenario_handler):
        """Test condition evaluation <"""
        scenario_handler.scenario_service.register_scenario(
            "test", ScenarioType.STORY, "Test"
        )
        scenario_handler.handle_command("SCENARIO", ["start", "test"])

        scenario_handler.set_variable("health", 50)

        assert scenario_handler.evaluate_condition("{health} < 100") is True
        assert scenario_handler.evaluate_condition("{health} < 10") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
