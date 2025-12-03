"""
SPRITE Command Handler - Character/Entity Management
Handles creation, loading, saving, and manipulation of SPRITE variables.
"""

import json
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, Any, Optional
from core.commands.base_handler import BaseCommandHandler

try:
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class SpriteHandler(BaseCommandHandler):
    """Handler for SPRITE commands (character/entity management)."""

    def __init__(self, components: Dict[str, Any]):
        """Initialize sprite handler with system components."""
        # Initialize base handler
        super().__init__(
            theme=components.get('theme', 'default'),
            connection=components.get('connection'),
            viewport=components.get('viewport'),
            user_manager=components.get('user_manager'),
            history=components.get('history'),
            command_history=components.get('command_history'),
            logger=components.get('logger'),
            main_handler=components.get('main_handler')
        )

        self.components = components
        self.config = components.get('config')
        self.var_manager = components.get('variable_manager')

        # Load sprite schema
        self.schema = self._load_schema()

    def _load_schema(self) -> Optional[Dict]:
        """Load sprite.schema.json."""
        schema_path = 'core/data/variables/sprite.schema.json'

        # Use base handler method for safe JSON loading
        success, data, error = self.load_json_file(schema_path)
        if not success:
            if self.logger:
                self.logger.error(f"Failed to load sprite schema: {error}")
            return None

        return data

    def handle(self, args: list) -> bool:
        """
        Handle SPRITE commands.

        Commands:
            SPRITE CREATE <name>                    - Create new sprite with defaults
            SPRITE LOAD <name> <file>               - Load sprite from JSON file
            SPRITE SAVE <name> <file>               - Save sprite to JSON file
            SPRITE SET <name>.<path> = <value>      - Set sprite property
            SPRITE GET <name>.<path>                - Get sprite property
            SPRITE LIST                             - List all sprites
            SPRITE DELETE <name>                    - Delete sprite
            SPRITE INFO <name>                      - Show sprite details

        Args:
            args: Command arguments

        Returns:
            True if command handled successfully
        """
        if not args:
            self._show_help()
            return True

        command = args[0].upper()

        if command == 'CREATE':
            return self._create_sprite(args[1:])
        elif command == 'LOAD':
            return self._load_sprite(args[1:])
        elif command == 'SAVE':
            return self._save_sprite(args[1:])
        elif command == 'SET':
            return self._set_property(args[1:])
        elif command == 'GET':
            return self._get_property(args[1:])
        elif command == 'LIST':
            return self._list_sprites()
        elif command == 'DELETE':
            return self._delete_sprite(args[1:])
        elif command == 'INFO':
            return self._show_info(args[1:])
        else:
            print(f"❌ Unknown SPRITE command: {command}")
            self._show_help()
            return False

    def _create_sprite(self, args: list) -> bool:
        """Create new sprite with default values."""
        if not args:
            print("❌ Usage: SPRITE CREATE <name>")
            return False

        name = args[0].upper()

        # Validate name format (UPPERCASE-HYPHEN)
        if not name.replace('-', '').replace('_', '').isalnum():
            print(f"❌ Invalid sprite name: {name}")
            print("   Names must be UPPERCASE-HYPHEN format (e.g., HERO, WARRIOR-KNIGHT)")
            return False

        # Create default sprite structure
        sprite = {
            "type": "sprite",
            "name": name,
            "stats": {
                "hp": 100,
                "hp_max": 100,
                "mp": 50,
                "mp_max": 50,
                "level": 1,
                "xp": 0,
                "xp_next": 100,
                "attack": 10,
                "defense": 10,
                "speed": 10,
                "luck": 5
            },
            "inventory": {
                "gold": 0,
                "items": [],
                "equipment": {
                    "weapon": None,
                    "armor": None,
                    "shield": None,
                    "accessory": None
                },
                "capacity": 20
            },
            "status": {
                "state": "alive",
                "effects": [],
                "buffs": {}
            },
            "skills": [],
            "meta": {
                "created": datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
                "modified": datetime.now(UTC).isoformat().replace('+00:00', 'Z'),
                "scope": "session",
                "description": f"Sprite created: {name}",
                "tags": ["sprite"]
            }
        }

        # Validate against schema if available
        if JSONSCHEMA_AVAILABLE and self.schema:
            try:
                validate(instance=sprite, schema=self.schema)
            except ValidationError as e:
                print(f"❌ Schema validation failed: {e.message}")
                return False

        # Store in variable manager
        if self.var_manager:
            self.var_manager.set_variable(name, sprite, scope='session')
            print(f"✅ Created sprite: {name}")
            print(f"   HP: {sprite['stats']['hp']}/{sprite['stats']['hp_max']}")
            print(f"   Level: {sprite['stats']['level']}")
            print(f"   Scope: {sprite['meta']['scope']}")
            return True

        print("❌ Variable manager not available")
        print("💡 The SPRITE system requires variable manager initialization")
        print("   This feature is under development - coming soon!")
        return False

    def _load_sprite(self, args: list) -> bool:
        """Load sprite from JSON file."""
        if len(args) < 2:
            print("❌ Usage: SPRITE LOAD <name> <file>")
            return False

        name = args[0].upper()
        filepath = args[1]

        # Resolve path
        path = Path(filepath)
        if not path.is_absolute():
            # Try sandbox/user/ first
            user_path = 'sandbox/user/' + filepath
            is_valid, path, error = self.validate_file_path(user_path, must_exist=True)
            if not is_valid:
                # Try filepath as-is
                is_valid, path, error = self.validate_file_path(filepath, must_exist=True)

        if not is_valid:
            print(self.format_error(f"File not found: {filepath}"))
            return False

        # Use base handler method for safe JSON loading
        success, sprite, load_error = self.load_json_file(str(path))
        if not success:
            print(self.format_error(f"Failed to load sprite: {load_error}"))
            return False

        # Validate structure
        if sprite.get('type') != 'sprite':
            print(self.format_error("Invalid sprite file: missing or wrong 'type' field"))
            return False

        # Validate against schema if available
        if JSONSCHEMA_AVAILABLE and self.schema:
            try:
                validate(instance=sprite, schema=self.schema)
            except ValidationError as e:
                print(f"❌ Schema validation failed: {e.message}")
                return False

        # Update name if different
        sprite['name'] = name
        sprite['meta']['modified'] = datetime.now(UTC).isoformat().replace('+00:00', 'Z')

        # Store in variable manager
        if self.var_manager:
            scope = sprite['meta'].get('scope', 'session')
            self.var_manager.set_variable(name, sprite, scope=scope)
            print(f"✅ Loaded sprite: {name}")
            print(f"   HP: {sprite['stats']['hp']}/{sprite['stats']['hp_max']}")
            print(f"   Level: {sprite['stats']['level']}")
            print(f"   Gold: {sprite['inventory']['gold']}")
            return True

        print("❌ Variable manager not available")
        return False

    def _save_sprite(self, args: list) -> bool:
        """Save sprite to JSON file."""
        if len(args) < 2:
            print("❌ Usage: SPRITE SAVE <name> <file>")
            return False

        name = args[0].upper()
        filepath = args[1]

        # Get sprite from variable manager
        if not self.var_manager:
            print("❌ Variable manager not available")
            return False

        sprite = self.var_manager.get_variable(name)
        if not sprite or not isinstance(sprite, dict) or sprite.get('type') != 'sprite':
            print(f"❌ Sprite not found: {name}")
            return False

        # Update modified timestamp
        sprite['meta']['modified'] = datetime.now(UTC).isoformat().replace('+00:00', 'Z')

        # Resolve path
        path = Path(filepath)
        if not path.is_absolute():
            # Default to sandbox/user/
            path = Path('sandbox/user') / filepath

        # Create directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, 'w') as f:
                json.dump(sprite, f, indent=2)

            print(f"✅ Saved sprite: {name}")
            print(f"   File: {path}")
            return True

        except Exception as e:
            print(f"❌ Error saving sprite: {e}")
            return False

    def _set_property(self, args: list) -> bool:
        """Set sprite property using dot notation."""
        if not args:
            print("❌ Usage: SPRITE SET <name>.<path> = <value>")
            print("   Example: SPRITE SET HERO.stats.hp = 50")
            return False

        # Parse assignment
        arg_str = ' '.join(args)
        if '=' not in arg_str:
            print("❌ Missing '=' in assignment")
            return False

        left, right = arg_str.split('=', 1)
        left = left.strip()
        value_str = right.strip()

        # Parse dot notation
        if '.' not in left:
            print("❌ Invalid property path (use dot notation)")
            return False

        parts = left.split('.')
        name = parts[0].upper()
        path = parts[1:]

        # Get sprite
        if not self.var_manager:
            print("❌ Variable manager not available")
            return False

        sprite = self.var_manager.get_variable(name)
        if not sprite or not isinstance(sprite, dict) or sprite.get('type') != 'sprite':
            print(f"❌ Sprite not found: {name}")
            return False

        # Parse value
        try:
            # Try JSON parse first (handles numbers, booleans, null, arrays, objects)
            value = json.loads(value_str)
        except json.JSONDecodeError:
            # Fall back to string
            value = value_str.strip('"\'')

        # Navigate to property and set value
        current = sprite
        for i, key in enumerate(path[:-1]):
            if key not in current:
                current[key] = {}
            current = current[key]

        final_key = path[-1]
        current[final_key] = value

        # Update modified timestamp
        sprite['meta']['modified'] = datetime.now(UTC).isoformat().replace('+00:00', 'Z')

        # Save back to variable manager
        scope = sprite['meta'].get('scope', 'session')
        self.var_manager.set_variable(name, sprite, scope=scope)

        print(f"✅ Set {name}.{'.'.join(path)} = {value}")
        return True

    def _get_property(self, args: list) -> bool:
        """Get sprite property using dot notation."""
        if not args:
            print("❌ Usage: SPRITE GET <name>.<path>")
            print("   Example: SPRITE GET HERO.stats.hp")
            return False

        # Parse dot notation
        path_str = args[0]
        if '.' not in path_str:
            print("❌ Invalid property path (use dot notation)")
            return False

        parts = path_str.split('.')
        name = parts[0].upper()
        path = parts[1:]

        # Get sprite
        if not self.var_manager:
            print("❌ Variable manager not available")
            return False

        sprite = self.var_manager.get_variable(name)
        if not sprite or not isinstance(sprite, dict) or sprite.get('type') != 'sprite':
            print(f"❌ Sprite not found: {name}")
            return False

        # Navigate to property
        current = sprite
        try:
            for key in path:
                current = current[key]

            # Pretty print result
            if isinstance(current, (dict, list)):
                print(json.dumps(current, indent=2))
            else:
                print(current)
            return True

        except (KeyError, TypeError):
            print(f"❌ Property not found: {'.'.join(path)}")
            return False

    def _list_sprites(self) -> bool:
        """List all sprites in all scopes."""
        if not self.var_manager:
            print("❌ Variable manager not available")
            return False

        found_sprites = []

        # Check all scopes
        for scope in ['global', 'session', 'script', 'local']:
            scope_vars = self.var_manager.variables.get(scope, {})
            for var_name, value in scope_vars.items():
                if isinstance(value, dict) and value.get('type') == 'sprite':
                    found_sprites.append({
                        'name': var_name,
                        'scope': scope,
                        'level': value.get('stats', {}).get('level', '?'),
                        'hp': value.get('stats', {}).get('hp', '?'),
                        'hp_max': value.get('stats', {}).get('hp_max', '?')
                    })

        if not found_sprites:
            print("No sprites found")
            return True

        print(f"\n{'Name':<15} {'Scope':<10} {'Level':<7} {'HP'}")
        print("-" * 50)
        for sprite in found_sprites:
            hp_str = f"{sprite['hp']}/{sprite['hp_max']}"
            print(f"{sprite['name']:<15} {sprite['scope']:<10} {sprite['level']:<7} {hp_str}")

        return True

    def _delete_sprite(self, args: list) -> bool:
        """Delete sprite from variable manager."""
        if not args:
            print("❌ Usage: SPRITE DELETE <name>")
            return False

        name = args[0].upper()

        if not self.var_manager:
            print("❌ Variable manager not available")
            return False

        # Find and delete from all scopes
        deleted = False
        for scope in ['global', 'session', 'script', 'local']:
            scope_vars = self.var_manager.variables.get(scope, {})
            if name in scope_vars:
                value = scope_vars[name]
                if isinstance(value, dict) and value.get('type') == 'sprite':
                    del scope_vars[name]
                    deleted = True
                    print(f"✅ Deleted sprite: {name} (scope: {scope})")
                    break

        if not deleted:
            print(f"❌ Sprite not found: {name}")
            return False

        return True

    def _show_info(self, args: list) -> bool:
        """Show detailed sprite information."""
        if not args:
            print("❌ Usage: SPRITE INFO <name>")
            return False

        name = args[0].upper()

        if not self.var_manager:
            print("❌ Variable manager not available")
            return False

        sprite = self.var_manager.get_variable(name)
        if not sprite or not isinstance(sprite, dict) or sprite.get('type') != 'sprite':
            print(f"❌ Sprite not found: {name}")
            return False

        # Display sprite info
        stats = sprite.get('stats', {})
        inventory = sprite.get('inventory', {})
        status = sprite.get('status', {})
        meta = sprite.get('meta', {})

        print(f"\n=== {name} ===")
        print(f"\nStats:")
        print(f"  HP: {stats.get('hp')}/{stats.get('hp_max')}")
        print(f"  MP: {stats.get('mp')}/{stats.get('mp_max')}")
        print(f"  Level: {stats.get('level')} (XP: {stats.get('xp')}/{stats.get('xp_next')})")
        print(f"  Attack: {stats.get('attack')}  Defense: {stats.get('defense')}  Speed: {stats.get('speed')}  Luck: {stats.get('luck')}")

        print(f"\nInventory:")
        print(f"  Gold: {inventory.get('gold')}")
        print(f"  Items: {len(inventory.get('items', []))}/{inventory.get('capacity')}")

        equipment = inventory.get('equipment', {})
        print(f"  Equipment:")
        for slot, item in equipment.items():
            print(f"    {slot.capitalize()}: {item or '(empty)'}")

        print(f"\nStatus:")
        print(f"  State: {status.get('state')}")
        if status.get('effects'):
            print(f"  Effects: {', '.join(status.get('effects'))}")

        print(f"\nMeta:")
        print(f"  Scope: {meta.get('scope')}")
        print(f"  Created: {meta.get('created')}")
        print(f"  Modified: {meta.get('modified')}")
        if meta.get('tags'):
            print(f"  Tags: {', '.join(meta.get('tags'))}")

        return True

    def _show_help(self):
        """Show SPRITE command help."""
        print("\n=== SPRITE Commands ===")
        print("\nCreate and manage character sprites:")
        print("  SPRITE CREATE <name>              - Create new sprite")
        print("  SPRITE LOAD <name> <file>         - Load sprite from JSON")
        print("  SPRITE SAVE <name> <file>         - Save sprite to JSON")
        print("  SPRITE SET <name>.<path> = <val>  - Set property (dot notation)")
        print("  SPRITE GET <name>.<path>          - Get property (dot notation)")
        print("  SPRITE LIST                       - List all sprites")
        print("  SPRITE DELETE <name>              - Delete sprite")
        print("  SPRITE INFO <name>                - Show sprite details")
        print("\nExamples:")
        print("  SPRITE CREATE HERO")
        print("  SPRITE SET HERO.stats.hp = 50")
        print("  SPRITE GET HERO.stats.level")
        print("  SPRITE LOAD WARRIOR sandbox/user/warrior.json")
        print("  SPRITE SAVE HERO hero.json")
