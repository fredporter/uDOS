"""
Test suite for uDOS Variable Schema System (v1.1.9)
Tests schema loading, validation, scope management, and SPRITE/OBJECT variables.
"""

import pytest
import json
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.utils.variables import VariableManager


class TestSchemaLoading:
    """Test JSON schema loading functionality."""

    def test_schemas_loaded(self):
        """Test that all 5 schemas are loaded successfully."""
        vm = VariableManager()
        expected_schemas = ['system', 'user', 'sprite', 'object', 'story']

        for schema_name in expected_schemas:
            assert schema_name in vm.schemas, f"Schema {schema_name} not loaded"

    def test_schema_structure(self):
        """Test that schemas have required structure."""
        vm = VariableManager()

        for schema_name, schema in vm.schemas.items():
            assert 'variables' in schema, f"{schema_name} missing 'variables' key"
            assert 'meta' in schema, f"{schema_name} missing 'meta' key"
            assert isinstance(schema['variables'], dict)

    def test_system_schema_variables(self):
        """Test system schema contains expected variables."""
        vm = VariableManager()
        system_vars = vm.schemas['system']['variables']

        expected_vars = ['CURRENT-PATH', 'CURRENT-MODE', 'USER-NAME',
                        'SYSTEM-VERSION', 'THEME-CURRENT', 'LOG-LEVEL']

        for var in expected_vars:
            assert var in system_vars, f"System variable {var} not found"

    def test_sprite_schema_variables(self):
        """Test sprite schema contains gameplay variables."""
        vm = VariableManager()
        sprite_vars = vm.schemas['sprite']['variables']

        expected_vars = ['SPRITE-NAME', 'SPRITE-HP', 'SPRITE-XP',
                        'SPRITE-LEVEL', 'SPRITE-INVENTORY']

        for var in expected_vars:
            assert var in sprite_vars, f"Sprite variable {var} not found"

    def test_object_schema_variables(self):
        """Test object schema contains item variables."""
        vm = VariableManager()
        object_vars = vm.schemas['object']['variables']

        expected_vars = ['OBJECT-ID', 'OBJECT-NAME', 'OBJECT-TYPE',
                        'OBJECT-DAMAGE', 'OBJECT-DEFENSE']

        for var in expected_vars:
            assert var in object_vars, f"Object variable {var} not found"


class TestVariableValidation:
    """Test variable validation against schemas."""

    def test_valid_integer(self):
        """Test validating valid integer values."""
        vm = VariableManager()
        is_valid, error = vm.validate_variable('SPRITE-HP', 100)
        assert is_valid, f"Valid integer rejected: {error}"

    def test_invalid_integer_type(self):
        """Test rejecting non-integer for integer field."""
        vm = VariableManager()
        is_valid, error = vm.validate_variable('SPRITE-HP', "not a number")
        assert not is_valid, "String accepted for integer field"
        assert "must be an integer" in error

    def test_integer_minimum_validation(self):
        """Test minimum value validation for integers."""
        vm = VariableManager()
        is_valid, error = vm.validate_variable('SPRITE-HP', -10)
        assert not is_valid, "Negative HP accepted"
        assert "at least" in error

    def test_integer_maximum_validation(self):
        """Test maximum value validation for integers."""
        vm = VariableManager()
        is_valid, error = vm.validate_variable('SPRITE-HP', 10000)
        assert not is_valid, "HP over maximum accepted"
        assert "at most" in error

    def test_valid_string(self):
        """Test validating valid string values."""
        vm = VariableManager()
        is_valid, error = vm.validate_variable('SPRITE-NAME', 'Aragorn')
        assert is_valid, f"Valid string rejected: {error}"

    def test_string_pattern_validation(self):
        """Test regex pattern validation for strings."""
        vm = VariableManager()
        is_valid, error = vm.validate_variable('USER-NAME', 'test_user-123')
        assert is_valid, f"Valid username rejected: {error}"

        is_valid, error = vm.validate_variable('USER-NAME', 'invalid@user')
        assert not is_valid, "Invalid username pattern accepted"

    def test_string_length_validation(self):
        """Test string length validation."""
        vm = VariableManager()

        # Too long
        long_name = 'a' * 100
        is_valid, error = vm.validate_variable('SPRITE-NAME', long_name)
        assert not is_valid, "Overly long string accepted"
        assert "at most" in error

    def test_enum_validation(self):
        """Test enum value validation."""
        vm = VariableManager()

        is_valid, error = vm.validate_variable('CURRENT-MODE', 'DEV')
        assert is_valid, f"Valid enum rejected: {error}"

        is_valid, error = vm.validate_variable('CURRENT-MODE', 'INVALID')
        assert not is_valid, "Invalid enum value accepted"
        assert "must be one of" in error

    def test_array_validation(self):
        """Test array/list validation."""
        vm = VariableManager()

        is_valid, error = vm.validate_variable('SPRITE-INVENTORY', ['sword', 'shield'])
        assert is_valid, f"Valid array rejected: {error}"

        is_valid, error = vm.validate_variable('SPRITE-INVENTORY', "not an array")
        assert not is_valid, "String accepted for array field"

    def test_array_max_items(self):
        """Test array maximum items validation."""
        vm = VariableManager()

        # SPRITE-INVENTORY has maxItems: 50
        large_inventory = ['item' + str(i) for i in range(100)]
        is_valid, error = vm.validate_variable('SPRITE-INVENTORY', large_inventory)
        assert not is_valid, "Array over max items accepted"
        assert "at most" in error

    def test_readonly_validation(self):
        """Test readonly variable protection."""
        vm = VariableManager()

        is_valid, error = vm.validate_variable('SYSTEM-VERSION', '2.0.0')
        assert not is_valid, "Readonly variable accepted modification"
        assert "read-only" in error


class TestScopeManagement:
    """Test variable scope management."""

    def test_default_scopes_exist(self):
        """Test that all scopes are initialized."""
        vm = VariableManager()
        expected_scopes = ['global', 'session', 'script', 'local']

        for scope in expected_scopes:
            assert scope in vm.variables, f"Scope {scope} not initialized"

    def test_set_global_variable(self):
        """Test setting a global scope variable."""
        vm = VariableManager()
        success = vm.set_variable('USER-NAME', 'testuser', 'global')
        assert success, "Failed to set global variable"
        assert vm.variables['global']['USER-NAME'] == 'testuser'

    def test_set_session_variable(self):
        """Test setting a session scope variable."""
        vm = VariableManager()
        success = vm.set_variable('SPRITE-HP', 75, 'session')
        assert success, "Failed to set session variable"
        assert vm.variables['session']['SPRITE-HP'] == 75

    def test_scope_priority(self):
        """Test that local scope overrides other scopes."""
        vm = VariableManager()

        vm.set_variable('TEST-VAR', 'global', 'global')
        vm.set_variable('TEST-VAR', 'session', 'session')
        vm.set_variable('TEST-VAR', 'local', 'local')

        # get_variable should return local (highest priority)
        assert vm.get_variable('TEST-VAR') == 'local'

    def test_scope_priority_without_local(self):
        """Test scope priority without local scope."""
        vm = VariableManager()

        vm.set_variable('TEST-VAR', 'global', 'global')
        vm.set_variable('TEST-VAR', 'session', 'session')

        # Should return session (higher than global)
        assert vm.get_variable('TEST-VAR') == 'session'

    def test_clear_scope(self):
        """Test clearing a specific scope."""
        vm = VariableManager()

        vm.set_variable('TEST-VAR', 'value', 'session')
        assert 'TEST-VAR' in vm.variables['session']

        vm.clear_scope('session')
        assert 'TEST-VAR' not in vm.variables['session']

    def test_get_scope_variables(self):
        """Test retrieving all variables from a scope."""
        vm = VariableManager()

        vm.set_variable('VAR1', 'value1', 'script')
        vm.set_variable('VAR2', 'value2', 'script')

        script_vars = vm.get_scope_variables('script')
        assert 'VAR1' in script_vars
        assert 'VAR2' in script_vars
        assert script_vars['VAR1'] == 'value1'


class TestSpriteVariables:
    """Test SPRITE variable system."""

    def test_sprite_hp_system(self):
        """Test SPRITE HP tracking."""
        vm = VariableManager()

        vm.set_variable('SPRITE-HP', 100, 'session')
        vm.set_variable('SPRITE-HP-MAX', 100, 'session')

        assert vm.get_variable('SPRITE-HP') == 100

        # Take damage
        vm.set_variable('SPRITE-HP', 75, 'session')
        assert vm.get_variable('SPRITE-HP') == 75

    def test_sprite_xp_system(self):
        """Test SPRITE XP and leveling."""
        vm = VariableManager()

        vm.set_variable('SPRITE-XP', 0, 'session')
        vm.set_variable('SPRITE-LEVEL', 1, 'session')

        # Gain XP
        vm.set_variable('SPRITE-XP', 150, 'session')
        assert vm.get_variable('SPRITE-XP') == 150

        # Level up logic would be handled by game code
        vm.set_variable('SPRITE-LEVEL', 2, 'session')
        assert vm.get_variable('SPRITE-LEVEL') == 2

    def test_sprite_stats(self):
        """Test SPRITE stat system."""
        vm = VariableManager()

        vm.set_variable('SPRITE-STRENGTH', 15, 'session')
        vm.set_variable('SPRITE-DEXTERITY', 12, 'session')
        vm.set_variable('SPRITE-INTELLIGENCE', 14, 'session')

        assert vm.get_variable('SPRITE-STRENGTH') == 15
        assert vm.get_variable('SPRITE-DEXTERITY') == 12
        assert vm.get_variable('SPRITE-INTELLIGENCE') == 14

    def test_sprite_inventory(self):
        """Test SPRITE inventory system."""
        vm = VariableManager()

        inventory = ['sword', 'shield', 'potion']
        vm.set_variable('SPRITE-INVENTORY', inventory, 'session')

        retrieved = vm.get_variable('SPRITE-INVENTORY')
        assert retrieved == inventory
        assert 'sword' in retrieved

    def test_sprite_equipped_items(self):
        """Test SPRITE equipped items."""
        vm = VariableManager()

        vm.set_variable('SPRITE-EQUIPPED-WEAPON', 'longsword', 'session')
        vm.set_variable('SPRITE-EQUIPPED-ARMOR', 'chainmail', 'session')

        assert vm.get_variable('SPRITE-EQUIPPED-WEAPON') == 'longsword'
        assert vm.get_variable('SPRITE-EQUIPPED-ARMOR') == 'chainmail'

    def test_sprite_status_effects(self):
        """Test SPRITE status system."""
        vm = VariableManager()

        is_valid, error = vm.validate_variable('SPRITE-STATUS', 'poisoned')
        assert is_valid, f"Valid status rejected: {error}"

        is_valid, error = vm.validate_variable('SPRITE-STATUS', 'invalid_status')
        assert not is_valid, "Invalid status accepted"


class TestObjectVariables:
    """Test OBJECT variable system."""

    def test_object_creation(self):
        """Test creating an object with variables."""
        vm = VariableManager()

        vm.set_variable('OBJECT-ID', 'sword_001', 'local')
        vm.set_variable('OBJECT-NAME', 'Iron Sword', 'local')
        vm.set_variable('OBJECT-TYPE', 'weapon', 'local')

        assert vm.get_variable('OBJECT-ID') == 'sword_001'
        assert vm.get_variable('OBJECT-NAME') == 'Iron Sword'
        assert vm.get_variable('OBJECT-TYPE') == 'weapon'

    def test_object_stats(self):
        """Test object stat tracking."""
        vm = VariableManager()

        vm.set_variable('OBJECT-DAMAGE', 25, 'local')
        vm.set_variable('OBJECT-DEFENSE', 0, 'local')
        vm.set_variable('OBJECT-VALUE', 150, 'local')

        assert vm.get_variable('OBJECT-DAMAGE') == 25
        assert vm.get_variable('OBJECT-VALUE') == 150

    def test_object_durability(self):
        """Test object durability system."""
        vm = VariableManager()

        vm.set_variable('OBJECT-DURABILITY', 100, 'local')
        assert vm.get_variable('OBJECT-DURABILITY') == 100

        # Wear down
        vm.set_variable('OBJECT-DURABILITY', 75, 'local')
        assert vm.get_variable('OBJECT-DURABILITY') == 75

    def test_object_type_validation(self):
        """Test object type enum validation."""
        vm = VariableManager()

        valid_types = ['weapon', 'armor', 'consumable', 'quest', 'tool', 'item', 'resource']

        for obj_type in valid_types:
            is_valid, error = vm.validate_variable('OBJECT-TYPE', obj_type)
            assert is_valid, f"Valid type {obj_type} rejected: {error}"

        is_valid, error = vm.validate_variable('OBJECT-TYPE', 'invalid_type')
        assert not is_valid, "Invalid object type accepted"

    def test_object_effects(self):
        """Test object effect system."""
        vm = VariableManager()

        vm.set_variable('OBJECT-EFFECT', 'heal', 'local')
        vm.set_variable('OBJECT-EFFECT-VALUE', 50, 'local')

        assert vm.get_variable('OBJECT-EFFECT') == 'heal'
        assert vm.get_variable('OBJECT-EFFECT-VALUE') == 50


class TestStoryVariables:
    """Test STORY variable system."""

    def test_story_progression(self):
        """Test story progression tracking."""
        vm = VariableManager()

        vm.set_variable('STORY-CURRENT', 'water_quest', 'session')
        vm.set_variable('STORY-CHAPTER', 3, 'session')

        assert vm.get_variable('STORY-CURRENT') == 'water_quest'
        assert vm.get_variable('STORY-CHAPTER') == 3

    def test_story_flags(self):
        """Test story flag system."""
        vm = VariableManager()

        flags = ['met_elder', 'found_water', 'completed_intro']
        vm.set_variable('STORY-FLAGS', flags, 'session')

        retrieved = vm.get_variable('STORY-FLAGS')
        assert 'met_elder' in retrieved
        assert 'found_water' in retrieved

    def test_story_quests(self):
        """Test quest tracking."""
        vm = VariableManager()

        active_quests = ['find_water', 'gather_supplies']
        completed_quests = ['tutorial', 'first_fire']

        vm.set_variable('STORY-QUEST-ACTIVE', active_quests, 'session')
        vm.set_variable('STORY-QUEST-COMPLETED', completed_quests, 'session')

        assert vm.get_variable('STORY-QUEST-ACTIVE') == active_quests
        assert vm.get_variable('STORY-QUEST-COMPLETED') == completed_quests

    def test_story_difficulty(self):
        """Test difficulty setting."""
        vm = VariableManager()

        difficulties = ['easy', 'normal', 'hard', 'nightmare']

        for diff in difficulties:
            is_valid, error = vm.validate_variable('STORY-DIFFICULTY', diff)
            assert is_valid, f"Valid difficulty {diff} rejected: {error}"


class TestVariableResolution:
    """Test variable resolution in templates."""

    def test_basic_resolution(self):
        """Test basic {VAR} resolution."""
        vm = VariableManager()
        vm.set_variable('USER-NAME', 'testuser')

        template = "Hello, {USER-NAME}!"
        result = vm.resolve(template)
        assert result == "Hello, testuser!"

    def test_dollar_sign_resolution(self):
        """Test $VAR resolution."""
        vm = VariableManager()
        vm.set_variable('SPRITE-HP', 85, 'session')

        template = "HP: $SPRITE-HP"
        result = vm.resolve(template)
        assert result == "HP: 85"

    def test_mixed_resolution(self):
        """Test mixed {VAR} and $VAR resolution."""
        vm = VariableManager()
        vm.set_variable('USER-NAME', 'hero')
        vm.set_variable('SPRITE-LEVEL', 10, 'session')

        template = "{USER-NAME} reached level $SPRITE-LEVEL!"
        result = vm.resolve(template)
        assert result == "hero reached level 10!"

    def test_extra_vars_resolution(self):
        """Test resolution with extra variables."""
        vm = VariableManager()

        extra = {"QUEST": "Find Water", "REWARD": "100 XP"}
        template = "Quest: {QUEST}, Reward: {REWARD}"
        result = vm.resolve(template, extra)

        assert "Find Water" in result
        assert "100 XP" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
