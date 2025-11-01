"""
uDOS Variable Resolution System v1.0.2
Provides dynamic variable replacement for templates, commands, and help text.
Now includes Character and Object variable types for Stories integration.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, Optional, List, Union


class VariableManager:
    """
    Manages system and user variables for template resolution.
    Variables can be static values or dynamic callables.
    """

    def __init__(self, components: Optional[Dict[str, Any]] = None):
        """
        Initialize the variable manager with system components.

        Args:
            components: Dictionary of system components (grid, env, theme, etc.)
        """
        self.components = components or {}
        self._init_system_vars()
        self._init_user_vars()
        self._init_path_vars()

    def _init_system_vars(self):
        """Initialize static and dynamic system variables."""
        self.system_vars = {
            # Version info
            'VERSION': '1.0.0',
            'PYTHON_VERSION': sys.version.split()[0],

            # Paths
            'INSTALL_DIR': os.getcwd(),
            'DATA_DIR': os.path.join(os.getcwd(), 'data'),
            'CORE_DIR': os.path.join(os.getcwd(), 'core'),
            'SANDBOX_DIR': os.path.join(os.getcwd(), 'sandbox'),
            'MEMORY_DIR': os.path.join(os.getcwd(), 'memory'),
            'KNOWLEDGE_DIR': os.path.join(os.getcwd(), 'knowledge'),

            # Time (dynamic - evaluated on each call)
            'TIMESTAMP': lambda: datetime.now().isoformat(),
            'DATE': lambda: datetime.now().strftime('%Y-%m-%d'),
            'TIME': lambda: datetime.now().strftime('%H:%M:%S'),
            'YEAR': lambda: str(datetime.now().year),
            'MONTH': lambda: datetime.now().strftime('%B'),
            'DAY': lambda: str(datetime.now().day),

            # System info
            'OS': sys.platform,
            'HOSTNAME': lambda: os.uname().nodename if hasattr(os, 'uname') else 'unknown',
        }

    def _init_user_vars(self):
        """Initialize user-specific variables from STORY.UDO."""
        self.user_vars = {
            'USERNAME': lambda: self._get_story_value('USER_PROFILE', 'NAME', 'Adventurer'),
            'USER_ROLE': lambda: self._get_story_value('USER_PROFILE', 'ROLE', 'Explorer'),
            'PROJECT': lambda: self._get_story_value('PROJECT', 'NAME', 'Unknown'),
            'PROJECT_DESC': lambda: self._get_story_value('PROJECT', 'DESCRIPTION', ''),
            'THEME': lambda: self._get_active_theme_name(),
            'THEME_ICON': lambda: self._get_theme_icon(),
            'SESSION': lambda: self._get_story_value('SESSION_STATS', 'CURRENT_SESSION', '1'),
            'TOTAL_SESSIONS': lambda: self._get_story_value('SESSION_STATS', 'TOTAL_SESSIONS', '0'),
            'ACTIVE_PANEL': lambda: self._get_active_panel(),
        }

    def _init_path_vars(self):
        """Initialize path template variables for common folders."""
        self.path_vars = {
            'FOLDER_SANDBOX': 'sandbox',
            'FOLDER_MEMORY': 'memory',
            'FOLDER_KNOWLEDGE': 'knowledge',
            'FOLDER_HISTORY': 'history',
            'FOLDER_CORE': 'core',
            'FOLDER_WIKI': 'wiki',
            'FOLDER_EXTENSIONS': 'extensions',
            'FOLDER_EXAMPLES': 'examples',
            'FOLDER_DATA': 'data',
        }

    def _get_story_value(self, section: str, key: str, default: str = '') -> str:
        """
        Retrieve value from STORY.UDO data.

        Args:
            section: Top-level section (e.g., 'USER_PROFILE')
            key: Key within section (e.g., 'NAME')
            default: Default value if not found

        Returns:
            String value or default
        """
        try:
            if 'env' in self.components:
                env = self.components['env']
                if hasattr(env, 'story_data') and env.story_data:
                    if section in env.story_data:
                        return str(env.story_data[section].get(key, default))
        except Exception:
            pass
        return default

    def _get_active_theme_name(self) -> str:
        """Get the currently active theme name."""
        try:
            if 'env' in self.components:
                env = self.components['env']
                if hasattr(env, 'story_data') and env.story_data:
                    system_opts = env.story_data.get('SYSTEM_OPTIONS', {})
                    return system_opts.get('THEME', 'DUNGEON')
        except Exception:
            pass
        return 'DUNGEON'

    def _get_theme_icon(self) -> str:
        """Get the icon for the active theme."""
        theme = self._get_active_theme_name()
        icons = {
            'DUNGEON': '⚔️',
            'GALAXY': '🚀',
            'FOUNDATION': '📊'
        }
        return icons.get(theme.upper(), '⚔️')

    def _get_active_panel(self) -> str:
        """Get the currently active panel name."""
        try:
            if 'grid' in self.components:
                grid = self.components['grid']
                if hasattr(grid, 'active_panel_name'):
                    return grid.active_panel_name
        except Exception:
            pass
        return 'main'

    def resolve(self, template: str, extra_vars: Optional[Dict[str, Any]] = None) -> str:
        """
        Replace {VAR} placeholders with actual values.

        Args:
            template: String containing {VAR} placeholders
            extra_vars: Additional variables to include (override defaults)

        Returns:
            String with all variables resolved

        Example:
            >>> vm = VariableManager()
            >>> vm.resolve("User: {USERNAME}, Date: {DATE}")
            "User: Adventurer, Date: 2025-10-31"
        """
        # Combine all variable sources
        all_vars = {
            **self.system_vars,
            **self.user_vars,
            **self.path_vars,
            **(extra_vars or {})
        }

        result = template

        # Replace each variable
        for var_name, value in all_vars.items():
            placeholder = f'{{{var_name}}}'
            if placeholder in result:
                # Evaluate if callable
                if callable(value):
                    try:
                        value = value()
                    except Exception as e:
                        value = f'[ERROR:{var_name}]'

                result = result.replace(placeholder, str(value))

        return result

    def resolve_dict(self, template_dict: Dict[str, Any],
                    extra_vars: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recursively resolve variables in a dictionary.

        Args:
            template_dict: Dictionary with string values containing {VAR}
            extra_vars: Additional variables to include

        Returns:
            Dictionary with all string values resolved
        """
        result = {}
        for key, value in template_dict.items():
            if isinstance(value, str):
                result[key] = self.resolve(value, extra_vars)
            elif isinstance(value, dict):
                result[key] = self.resolve_dict(value, extra_vars)
            elif isinstance(value, list):
                result[key] = [
                    self.resolve(item, extra_vars) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def get_all_vars(self) -> Dict[str, str]:
        """
        Get a snapshot of all current variable values.
        Useful for debugging or displaying available variables.

        Returns:
            Dictionary of all variables with resolved values
        """
        result = {}
        all_vars = {
            **self.system_vars,
            **self.user_vars,
            **self.path_vars
        }

        for var_name, value in all_vars.items():
            if callable(value):
                try:
                    result[var_name] = str(value())
                except Exception:
                    result[var_name] = '[UNAVAILABLE]'
            else:
                result[var_name] = str(value)

        return result

    def add_custom_var(self, name: str, value: Any):
        """
        Add a custom variable at runtime.

        Args:
            name: Variable name (without braces)
            value: Variable value (can be callable)
        """
        self.user_vars[name] = value


def create_variable_manager(components: Optional[Dict[str, Any]] = None) -> VariableManager:
    """
    Factory function to create a VariableManager instance.

    Args:
        components: System components dictionary

    Returns:
        Configured VariableManager instance
    """
    return VariableManager(components)


# Example usage and testing
if __name__ == "__main__":
    print("🔧 uDOS Variable Manager Test\n")

    # Create instance
    vm = VariableManager()

    # Test basic resolution
    template = "Welcome {USERNAME}! Today is {DATE} at {TIME}."
    print(f"Template: {template}")
    print(f"Resolved: {vm.resolve(template)}\n")

    # Test path variables
    path_template = "Load file from {FOLDER_SANDBOX}/test.txt"
    print(f"Path Template: {path_template}")
    print(f"Resolved: {vm.resolve(path_template)}\n")

    # Test extra variables
    extra = {"FILE_NAME": "example.md", "AUTHOR": "Test User"}
    doc_template = "File: {FILE_NAME} by {AUTHOR}, created {DATE}"
    print(f"Extra Vars Template: {doc_template}")
    print(f"Resolved: {vm.resolve(doc_template, extra)}\n")

    # Test Character and Object types
    char_mgr = CharacterObjectManager()
    hero = char_mgr.create_character("Frodo", "Archaeologist")
    ring = char_mgr.create_object("One Ring", "ring", rarity="artifact")

    print(f"Character: {hero.get_status_string()}")
    print(f"Object: {ring.get_status_string()}")
    print(f"Timestamp: {generate_udos_timestamp()}")

    # Display all available variables
    print("📋 Available Variables:")


# Character and Object Variable Types for Stories Integration
# =========================================================

@dataclass
class CharacterStats:
    """NetHack-style character statistics."""
    strength: int = 10
    intelligence: int = 10
    dexterity: int = 10
    constitution: int = 10
    wisdom: int = 10
    charisma: int = 10

    def total_stats(self) -> int:
        return self.strength + self.intelligence + self.dexterity + \
               self.constitution + self.wisdom + self.charisma

    def modifier(self, stat_value: int) -> int:
        """Calculate D&D-style ability modifier."""
        return (stat_value - 10) // 2


@dataclass
class CharacterVitals:
    """Character health and experience tracking."""
    level: int = 1
    hp: int = 10
    max_hp: int = 10
    xp: int = 0
    xp_to_next: int = 100
    gold: int = 0
    food: int = 5

    def gain_xp(self, amount: int) -> bool:
        """Gain experience, return True if leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            return self.level_up()
        return False

    def level_up(self) -> bool:
        """Level up character."""
        if self.xp >= self.xp_to_next:
            self.level += 1
            self.xp -= self.xp_to_next
            self.xp_to_next = int(self.xp_to_next * 1.5)
            hp_gain = max(1, (self.level + 2) // 3)
            self.max_hp += hp_gain
            self.hp = self.max_hp
            return True
        return False


@dataclass
class Character:
    """uDOS Character variable type with NetHack-inspired properties."""
    name: str = "Unnamed"
    char_class: str = "Adventurer"
    race: str = "Human"
    alignment: str = "Neutral"
    background: str = "Wanderer"

    stats: CharacterStats = field(default_factory=CharacterStats)
    vitals: CharacterVitals = field(default_factory=CharacterVitals)

    weapon: str = "bare hands"
    armor: str = "clothes"
    inventory: List[str] = field(default_factory=list)
    status_effects: List[str] = field(default_factory=list)
    location: str = "Unknown"
    story_flags: Dict[str, Any] = field(default_factory=dict)

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_armor_class(self) -> int:
        """Calculate armor class."""
        base_ac = 10
        dex_mod = self.stats.modifier(self.stats.dexterity)
        armor_bonuses = {"leather jacket": 1, "chain mail": 3, "plate mail": 6}
        armor_bonus = armor_bonuses.get(self.armor.lower(), 0)
        return base_ac + armor_bonus + dex_mod

    def get_status_string(self) -> str:
        """Get formatted status string."""
        return f"{self.name} the {self.char_class}: Lvl {self.vitals.level}, " \
               f"HP {self.vitals.hp}/{self.vitals.max_hp}, XP {self.vitals.xp}"


@dataclass
class ObjectProperties:
    """Object properties and enchantments."""
    enchantment: int = 0
    durability: int = 100
    max_durability: int = 100
    magical: bool = False
    cursed: bool = False
    blessed: bool = False

    def get_condition(self) -> str:
        """Get condition based on durability."""
        if self.durability <= 0:
            return "broken"
        elif self.durability < 20:
            return "poor"
        elif self.durability < 50:
            return "fair"
        elif self.durability < 80:
            return "good"
        else:
            return "excellent"


@dataclass
class GameObject:
    """uDOS Object variable type for items and artifacts."""
    name: str = "Unknown Object"
    object_type: str = "misc"
    category: str = "item"
    rarity: str = "common"
    weight: float = 1.0
    value: int = 1

    properties: ObjectProperties = field(default_factory=ObjectProperties)
    description: str = ""
    location_found: str = "Unknown"

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_full_name(self) -> str:
        """Get full descriptive name including enchantment."""
        base_name = self.name
        if self.properties.enchantment > 0:
            base_name = f"+{self.properties.enchantment} {base_name}"
        elif self.properties.enchantment < 0:
            base_name = f"{self.properties.enchantment} {base_name}"
        if self.properties.cursed:
            base_name = f"cursed {base_name}"
        elif self.properties.blessed:
            base_name = f"blessed {base_name}"
        return base_name

    def get_status_string(self) -> str:
        """Get formatted status string."""
        condition = self.properties.get_condition()
        return f"{self.get_full_name()}: {condition}, Value {self.value}g"


class CharacterObjectManager:
    """Manager for Character and Object variables."""

    def __init__(self, data_dir: str = "memory/variables"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.characters: Dict[str, Character] = {}
        self.objects: Dict[str, GameObject] = {}

    def create_character(self, name: str, char_class: str = "Adventurer", **kwargs) -> Character:
        """Create a new character."""
        character = Character(name=name, char_class=char_class, **kwargs)
        self.characters[name] = character
        return character

    def create_object(self, name: str, object_type: str = "misc", **kwargs) -> GameObject:
        """Create a new object."""
        obj = GameObject(name=name, object_type=object_type, **kwargs)
        self.objects[name] = obj
        return obj

    def get_character(self, name: str) -> Optional[Character]:
        """Get character by name."""
        return self.characters.get(name)

    def get_object(self, name: str) -> Optional[GameObject]:
        """Get object by name."""
        return self.objects.get(name)

    def list_characters(self) -> List[str]:
        """List all character names."""
        return list(self.characters.keys())

    def list_objects(self) -> List[str]:
        """List all object names."""
        return list(self.objects.keys())


def generate_udos_timestamp(location_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate uDOS timestamp in format: udos-YYMMDD-HHSS-TMZO-MAPTILE-ZOOM

    Args:
        location_data: Optional dict with location information

    Returns:
        Formatted timestamp string
    """
    now = datetime.now()

    # Date and time components
    date_part = now.strftime("%y%m%d")
    time_part = now.strftime("%H%M")

    # Timezone offset (simplified)
    tz_offset = now.strftime("%z")
    if tz_offset:
        tz_part = tz_offset[:3] if len(tz_offset) >= 3 else "+00"
    else:
        tz_part = "+00"

    # Location components (default if not provided)
    if location_data:
        map_tile = location_data.get("map_tile", "000000")[:6].ljust(6, "0")
        zoom = str(location_data.get("zoom_level", 1))[:2].ljust(2, "0")
    else:
        map_tile = "000000"
        zoom = "01"

    return f"udos-{date_part}-{time_part}-{tz_part}-{map_tile}-{zoom}"
    all_vars = vm.get_all_vars()
    for var, val in sorted(all_vars.items()):
        print(f"  {{{var}}}: {val}")
