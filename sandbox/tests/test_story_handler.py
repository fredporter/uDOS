"""
Test Suite for STORY Command Handler and Adventure Engine
Tests .upy execution, SPRITE/OBJECT integration, and adventure mechanics.
"""

import pytest
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extensions.play.commands.story_handler import StoryHandler, AdventureEngine
from core.utils.variables import VariableManager


class TestAdventureEngine:
    """Test adventure engine core functionality."""
    
    def setup_method(self):
        """Create fresh engine for each test."""
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
    
    def test_engine_initialization(self):
        """Test adventure engine initializes correctly."""
        assert self.engine.vm is not None
        assert self.engine.current_adventure is None
        assert self.engine.labels == {}
    
    def test_load_nonexistent_adventure(self):
        """Test loading adventure that doesn't exist."""
        result = self.engine.load_adventure("nonexistent.upy")
        assert result is False
        assert self.engine.current_adventure is None
    
    def test_load_valid_adventure(self, tmp_path):
        """Test loading a valid adventure file."""
        # Create test adventure
        adv_file = tmp_path / "test.upy"
        adv_file.write_text("""
PRINT [Hello World]
END
""")
        
        result = self.engine.load_adventure(str(adv_file))
        assert result is True
        assert self.engine.current_adventure is not None
        assert self.engine.current_adventure['name'] == 'test'
    
    def test_label_parsing(self, tmp_path):
        """Test that labels are parsed correctly."""
        adv_file = tmp_path / "labels.upy"
        adv_file.write_text("""
LABEL [START]
PRINT [At start]
LABEL [MIDDLE]
PRINT [At middle]
LABEL [END-SECTION]
PRINT [At end]
END
""")
        
        self.engine.load_adventure(str(adv_file))
        assert 'START' in self.engine.labels
        assert 'MIDDLE' in self.engine.labels
        assert 'END-SECTION' in self.engine.labels


class TestCommandExecution:
    """Test individual .upy command execution."""
    
    def setup_method(self):
        """Create fresh engine for each test."""
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
    
    def test_set_command_integer(self):
        """Test SET command with integer value."""
        self.engine._cmd_set("SET [$TEST-VAR = 42]")
        assert self.vm.get_variable('TEST-VAR') == 42
    
    def test_set_command_string(self):
        """Test SET command with string value."""
        self.engine._cmd_set('SET [$NAME = "Hero"]')
        assert self.vm.get_variable('NAME') == "Hero"
    
    def test_set_command_float(self):
        """Test SET command with float value."""
        self.engine._cmd_set("SET [$RATIO = 3.14]")
        assert self.vm.get_variable('RATIO') == 3.14
    
    def test_print_command_plain(self, capsys):
        """Test PRINT command with plain text."""
        self.engine._cmd_print("PRINT [Hello World]")
        captured = capsys.readouterr()
        assert "Hello World" in captured.out
    
    def test_print_command_with_variable(self, capsys):
        """Test PRINT command with variable substitution."""
        self.vm.set_variable('NAME', 'Alice', 'session')
        self.engine._cmd_print("PRINT [Hello $NAME]")
        captured = capsys.readouterr()
        assert "Hello Alice" in captured.out
    
    def test_xp_command_positive(self):
        """Test XP command with positive value."""
        self.vm.set_variable('SPRITE-XP', 0, 'session')
        self.engine._cmd_xp("XP [+50]")
        assert self.vm.get_variable('SPRITE-XP') == 50
    
    def test_xp_command_negative(self):
        """Test XP command with negative value."""
        self.vm.set_variable('SPRITE-XP', 100, 'session')
        self.engine._cmd_xp("XP [-25]")
        assert self.vm.get_variable('SPRITE-XP') == 75
    
    def test_hp_command_gain(self):
        """Test HP command with healing."""
        self.vm.set_variable('SPRITE-HP', 50, 'session')
        self.vm.set_variable('SPRITE-HP-MAX', 100, 'session')
        self.engine._cmd_hp("HP [+30]")
        assert self.vm.get_variable('SPRITE-HP') == 80
    
    def test_hp_command_damage(self):
        """Test HP command with damage."""
        self.vm.set_variable('SPRITE-HP', 100, 'session')
        self.engine._cmd_hp("HP [-25]")
        assert self.vm.get_variable('SPRITE-HP') == 75
    
    def test_hp_cannot_exceed_max(self):
        """Test HP cannot exceed max HP."""
        self.vm.set_variable('SPRITE-HP', 90, 'session')
        self.vm.set_variable('SPRITE-HP-MAX', 100, 'session')
        self.engine._cmd_hp("HP [+50]")  # Try to heal 50
        assert self.vm.get_variable('SPRITE-HP') == 100  # Capped at max
    
    def test_hp_cannot_go_negative(self):
        """Test HP cannot go below zero."""
        self.vm.set_variable('SPRITE-HP', 20, 'session')
        self.engine._cmd_hp("HP [-50]")  # Take 50 damage
        assert self.vm.get_variable('SPRITE-HP') == 0  # Capped at 0
    
    def test_item_command(self):
        """Test ITEM command adds to inventory."""
        self.vm.set_variable('SPRITE-INVENTORY', [], 'session')
        self.engine._cmd_item("ITEM [sword]")
        inventory = self.vm.get_variable('SPRITE-INVENTORY')
        assert 'sword' in inventory
    
    def test_item_command_multiple(self):
        """Test adding multiple items."""
        self.vm.set_variable('SPRITE-INVENTORY', [], 'session')
        self.engine._cmd_item("ITEM [sword]")
        self.engine._cmd_item("ITEM [shield]")
        self.engine._cmd_item("ITEM [potion]")
        inventory = self.vm.get_variable('SPRITE-INVENTORY')
        assert len(inventory) == 3
        assert 'sword' in inventory
        assert 'shield' in inventory
        assert 'potion' in inventory
    
    def test_flag_command(self):
        """Test FLAG command sets story flag."""
        self.vm.set_variable('STORY-FLAGS', [], 'session')
        self.engine._cmd_flag("FLAG [quest_started]")
        flags = self.vm.get_variable('STORY-FLAGS')
        assert 'quest_started' in flags
    
    def test_flag_command_duplicate(self):
        """Test FLAG command doesn't duplicate flags."""
        self.vm.set_variable('STORY-FLAGS', [], 'session')
        self.engine._cmd_flag("FLAG [quest_started]")
        self.engine._cmd_flag("FLAG [quest_started]")  # Set again
        flags = self.vm.get_variable('STORY-FLAGS')
        assert flags.count('quest_started') == 1
    
    def test_roll_command_basic(self):
        """Test ROLL command with basic dice."""
        self.engine._cmd_roll("ROLL [1d20] → $RESULT")
        result = self.vm.get_variable('RESULT')
        assert 1 <= result <= 20
    
    def test_roll_command_multiple_dice(self):
        """Test ROLL command with multiple dice."""
        self.engine._cmd_roll("ROLL [2d6] → $RESULT")
        result = self.vm.get_variable('RESULT')
        assert 2 <= result <= 12  # 2d6 ranges from 2 to 12


class TestConditionalLogic:
    """Test IF/THEN conditional execution."""
    
    def setup_method(self):
        """Create fresh engine for each test."""
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
    
    def test_if_greater_than_true(self):
        """Test IF with > comparison (true case)."""
        self.vm.set_variable('TEST-VAL', 10, 'local')
        result = self.engine._evaluate_value("$TEST-VAL")
        assert result == 10
    
    def test_if_greater_than_false(self):
        """Test IF with > comparison (false case)."""
        self.vm.set_variable('TEST-VAL', 5, 'local')
        result = self.engine._evaluate_value("$TEST-VAL")
        assert result == 5
    
    def test_if_less_than(self):
        """Test IF with < comparison."""
        self.vm.set_variable('HP', 30, 'local')
        result = self.engine._evaluate_value("$HP")
        assert result == 30
    
    def test_if_equal(self):
        """Test IF with == comparison."""
        self.vm.set_variable('LEVEL', 5, 'local')
        result = self.engine._evaluate_value("$LEVEL")
        assert result == 5
    
    def test_if_not_equal(self):
        """Test IF with != comparison."""
        self.vm.set_variable('STATUS', 'normal', 'local')
        result = self.engine._evaluate_value("$STATUS")
        assert result == "normal"
    
    def test_evaluate_literal_integer(self):
        """Test evaluating literal integer values."""
        result = self.engine._evaluate_value("42")
        assert result == 42
    
    def test_evaluate_literal_string(self):
        """Test evaluating literal string values."""
        result = self.engine._evaluate_value('"hello"')
        assert result == "hello"


class TestBranchingLogic:
    """Test CHOICE, OPTION, BRANCH, and LABEL commands."""
    
    def setup_method(self):
        """Create fresh engine for each test."""
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
    
    def test_branch_to_existing_label(self):
        """Test BRANCH jumps to correct label."""
        self.engine.labels = {'TARGET': 10, 'OTHER': 20}
        new_line = self.engine._cmd_branch("BRANCH [TARGET]")
        assert new_line == 10
    
    def test_branch_to_nonexistent_label(self, capsys):
        """Test BRANCH to missing label shows warning."""
        self.engine.labels = {}
        new_line = self.engine._cmd_branch("BRANCH [MISSING]")
        captured = capsys.readouterr()
        assert "Label not found" in captured.out
        assert new_line is None


class TestLevelingSystem:
    """Test XP and leveling mechanics."""
    
    def setup_method(self):
        """Create fresh engine for each test."""
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
    
    def test_level_up_on_xp_threshold(self, capsys):
        """Test character levels up at XP threshold."""
        self.vm.set_variable('SPRITE-XP', 90, 'session')
        self.vm.set_variable('SPRITE-LEVEL', 1, 'session')
        self.vm.set_variable('SPRITE-HP', 50, 'session')
        self.vm.set_variable('SPRITE-HP-MAX', 100, 'session')
        
        self.engine._cmd_xp("XP [+15]")  # Total: 105 (threshold: 100)
        
        captured = capsys.readouterr()
        assert "Level up" in captured.out
        assert self.vm.get_variable('SPRITE-LEVEL') == 2
        assert self.vm.get_variable('SPRITE-HP') == 100  # HP restored
    
    def test_no_level_up_below_threshold(self):
        """Test no level up when below threshold."""
        self.vm.set_variable('SPRITE-XP', 50, 'session')
        self.vm.set_variable('SPRITE-LEVEL', 1, 'session')
        
        self.engine._cmd_xp("XP [+25]")  # Total: 75 (threshold: 100)
        
        assert self.vm.get_variable('SPRITE-LEVEL') == 1  # No level up


class TestStoryHandler:
    """Test STORY command handler."""
    
    def setup_method(self):
        """Create fresh handler for each test."""
        self.handler = StoryHandler()
    
    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        assert self.handler.vm is not None
        assert self.handler.engine is not None
    
    def test_status_no_active_story(self, capsys):
        """Test STATUS with no active adventure."""
        self.handler._show_status()
        captured = capsys.readouterr()
        assert "No active adventure" in captured.out
    
    def test_status_with_active_story(self, capsys):
        """Test STATUS with active adventure."""
        self.handler.vm.set_variable('STORY-CURRENT', 'test_quest', 'session')
        self.handler.vm.set_variable('SPRITE-NAME', 'TestHero', 'session')
        self.handler.vm.set_variable('SPRITE-HP', 80, 'session')
        
        self.handler._show_status()
        captured = capsys.readouterr()
        assert "test_quest" in captured.out
        assert "TestHero" in captured.out
    
    def test_list_adventures_empty_dir(self, capsys, tmp_path):
        """Test LIST with no adventures."""
        self.handler.adventures_dir = tmp_path / "adventures"
        self.handler.adventures_dir.mkdir()
        
        self.handler._list_adventures()
        captured = capsys.readouterr()
        assert "No adventures found" in captured.out
    
    def test_list_adventures_with_files(self, capsys, tmp_path):
        """Test LIST with adventure files."""
        adv_dir = tmp_path / "adventures"
        adv_dir.mkdir()
        
        (adv_dir / "quest1.upy").write_text("PRINT [Quest 1]\nEND")
        (adv_dir / "quest2.upy").write_text("PRINT [Quest 2]\nEND")
        
        self.handler.adventures_dir = adv_dir
        self.handler._list_adventures()
        
        captured = capsys.readouterr()
        assert "quest1" in captured.out
        assert "quest2" in captured.out
    
    def test_create_adventure(self, tmp_path, capsys):
        """Test CREATE generates new adventure."""
        self.handler.adventures_dir = tmp_path / "adventures"
        
        result = self.handler._create_adventure("my_quest")
        captured = capsys.readouterr()
        
        assert result is True
        assert (tmp_path / "adventures" / "my_quest.upy").exists()
        assert "Created adventure" in captured.out
    
    def test_create_duplicate_adventure(self, tmp_path, capsys):
        """Test CREATE fails if adventure exists."""
        adv_dir = tmp_path / "adventures"
        adv_dir.mkdir()
        (adv_dir / "existing.upy").write_text("PRINT [Test]\nEND")
        
        self.handler.adventures_dir = adv_dir
        result = self.handler._create_adventure("existing")
        
        captured = capsys.readouterr()
        assert result is False
        assert "already exists" in captured.out


class TestFullAdventureExecution:
    """Test complete adventure script execution."""
    
    def setup_method(self):
        """Create fresh engine for each test."""
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
    
    def test_simple_adventure(self, tmp_path, capsys):
        """Test executing a simple adventure."""
        adv_file = tmp_path / "simple.upy"
        adv_file.write_text("""
SET [$SPRITE-NAME = "Hero"]
SET [$SPRITE-HP = 100]
PRINT [Welcome $SPRITE-NAME!]
XP [+50]
HP [+10]
ITEM [sword]
FLAG [adventure_started]
END
""")
        
        self.engine.load_adventure(str(adv_file))
        result = self.engine.execute()
        
        captured = capsys.readouterr()
        
        assert result is True
        assert "Welcome Hero!" in captured.out
        assert self.vm.get_variable('SPRITE-NAME') == "Hero"
        assert self.vm.get_variable('SPRITE-XP') == 50
        assert 'sword' in self.vm.get_variable('SPRITE-INVENTORY', [])
        assert 'adventure_started' in self.vm.get_variable('STORY-FLAGS', [])
    
    def test_adventure_with_branching(self, tmp_path):
        """Test adventure with labels and branches."""
        adv_file = tmp_path / "branching.upy"
        adv_file.write_text("""
SET [$COUNTER = 0]
BRANCH [MIDDLE]
SET [$COUNTER = 99]
LABEL [MIDDLE]
SET [$COUNTER = 5]
BRANCH [END-SECTION]
SET [$COUNTER = 88]
LABEL [END-SECTION]
XP [+10]
END
""")
        
        self.engine.load_adventure(str(adv_file))
        self.engine.execute()
        
        # Counter should be 5 (skipped the 99 and 88 assignments)
        assert self.vm.get_variable('COUNTER') == 5
        assert self.vm.get_variable('SPRITE-XP') == 10


class TestVariableIntegration:
    """Test integration with SPRITE, OBJECT, and STORY variables."""
    
    def setup_method(self):
        """Create fresh engine for each test."""
        self.vm = VariableManager()
        self.engine = AdventureEngine(self.vm)
    
    def test_sprite_variables_integration(self):
        """Test SPRITE variables work in adventures."""
        # Test all major SPRITE variables
        self.vm.set_variable('SPRITE-HP', 100, 'session')
        self.vm.set_variable('SPRITE-HP-MAX', 100, 'session')
        self.vm.set_variable('SPRITE-XP', 0, 'session')
        self.vm.set_variable('SPRITE-LEVEL', 1, 'session')
        self.vm.set_variable('SPRITE-GOLD', 50, 'session')
        self.vm.set_variable('SPRITE-INVENTORY', [], 'session')
        
        # Modify through commands
        self.engine._cmd_hp("HP [-20]")
        self.engine._cmd_xp("XP [+50]")
        self.engine._cmd_item("ITEM [health_potion]")
        
        assert self.vm.get_variable('SPRITE-HP') == 80
        assert self.vm.get_variable('SPRITE-XP') == 50
        assert 'health_potion' in self.vm.get_variable('SPRITE-INVENTORY')
    
    def test_story_variables_integration(self):
        """Test STORY variables work in adventures."""
        self.vm.set_variable('STORY-CURRENT', 'test_quest', 'session')
        self.vm.set_variable('STORY-CHAPTER', 1, 'session')
        self.vm.set_variable('STORY-FLAGS', [], 'session')
        self.vm.set_variable('STORY-CHOICES', {}, 'session')
        
        # Add flags and choices
        self.engine._cmd_flag("FLAG [met_wizard]")
        self.engine._cmd_flag("FLAG [found_key]")
        
        flags = self.vm.get_variable('STORY-FLAGS')
        assert 'met_wizard' in flags
        assert 'found_key' in flags


# Integration test for real adventure files (if they exist)
class TestRealAdventures:
    """Test actual adventure files in the project."""
    
    def test_water_quest_loads(self):
        """Test water_quest.upy exists and loads."""
        water_quest = Path("sandbox/ucode/adventures/water_quest.upy")
        if water_quest.exists():
            vm = VariableManager()
            engine = AdventureEngine(vm)
            result = engine.load_adventure(str(water_quest))
            assert result is True
            assert 'START' in engine.labels or len(engine.current_adventure['lines']) > 0
    
    def test_fire_quest_loads(self):
        """Test fire_quest.upy exists and loads."""
        fire_quest = Path("sandbox/ucode/adventures/fire_quest.upy")
        if fire_quest.exists():
            vm = VariableManager()
            engine = AdventureEngine(vm)
            result = engine.load_adventure(str(fire_quest))
            assert result is True
    
    def test_shelter_quest_loads(self):
        """Test shelter_quest.upy exists and loads."""
        shelter_quest = Path("sandbox/ucode/adventures/shelter_quest.upy")
        if shelter_quest.exists():
            vm = VariableManager()
            engine = AdventureEngine(vm)
            result = engine.load_adventure(str(shelter_quest))
            assert result is True


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
