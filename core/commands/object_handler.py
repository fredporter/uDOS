"""
OBJECT Command Handler - Item/Object Management
Handles loading, querying, and managing OBJECT variables (items, equipment, consumables).
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from core.commands.base_handler import BaseCommandHandler
from core.utils.paths import PATHS

try:
    from jsonschema import validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class ObjectHandler(BaseCommandHandler):
    """Handler for OBJECT commands (item/object management)."""

    def __init__(self, components: Dict[str, Any]):
        """Initialize object handler with system components."""
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

        # Load object schema
        self.schema = self._load_schema()

        # Item catalog (loaded from files)
        self.catalog = {}

    def _load_schema(self) -> Optional[Dict]:
        """Load object.schema.json."""
        schema_path = Path(__file__).parent.parent / 'data' / 'variables' / 'object.schema.json'
        if schema_path.exists():
            try:
                with open(schema_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Failed to load object schema: {e}")
        return None

    def handle(self, args: list) -> bool:
        """
        Handle OBJECT commands.

        Commands:
            OBJECT LOAD <file>              - Load objects catalog from JSON
            OBJECT LIST [category]          - List all objects (optionally by category)
            OBJECT INFO <name>              - Show object details
            OBJECT SEARCH <query>           - Search objects by name/description
            OBJECT FILTER <key>=<value>     - Filter objects by property

        Args:
            args: Command arguments

        Returns:
            True if command handled successfully
        """
        if not args:
            self._show_help()
            return True

        command = args[0].upper()

        if command == 'LOAD':
            return self._load_catalog(args[1:])
        elif command == 'LIST':
            return self._list_objects(args[1:])
        elif command == 'INFO':
            return self._show_info(args[1:])
        elif command == 'SEARCH':
            return self._search_objects(args[1:])
        elif command == 'FILTER':
            return self._filter_objects(args[1:])
        else:
            print(f"❌ Unknown OBJECT command: {command}")
            self._show_help()
            return False

    def _load_catalog(self, args: list) -> bool:
        """Load objects catalog from JSON file."""
        if not args:
            print("❌ Usage: OBJECT LOAD <file>")
            return False

        filepath = args[0]

        # Resolve path
        path = Path(filepath)
        if not path.is_absolute():
            # Try sandbox/user/ first
            user_path = Path(str(PATHS.MEMORY_SYSTEM_USER)) / filepath
            if user_path.exists():
                path = user_path
            else:
                path = Path(filepath)

        if not path.exists():
            print(f"❌ File not found: {filepath}")
            return False

        try:
            with open(path, 'r') as f:
                data = json.load(f)

            # Handle both array and {items: [...]} format
            items = data if isinstance(data, list) else data.get('items', [])

            if not isinstance(items, list):
                print(f"❌ Invalid catalog format (expected array or {{items: []}})")
                return False

            # Validate each item against schema if available
            validated_count = 0
            for item in items:
                if JSONSCHEMA_AVAILABLE and self.schema:
                    try:
                        validate(instance=item, schema=self.schema)
                    except ValidationError as e:
                        print(f"⚠️  Validation warning for {item.get('name', 'UNNAMED')}: {e.message}")
                        continue

                # Add to catalog
                name = item.get('name')
                if name:
                    self.catalog[name] = item
                    validated_count += 1

            print(f"✅ Loaded {validated_count} objects from {path.name}")
            return True

        except Exception as e:
            print(f"❌ Error loading catalog: {e}")
            return False

    def _list_objects(self, args: list) -> bool:
        """List all objects, optionally filtered by category."""
        if not self.catalog:
            print("No objects loaded. Use: OBJECT LOAD <file>")
            return True

        # Filter by category if provided
        category_filter = args[0].lower() if args else None

        items = []
        for name, obj in self.catalog.items():
            if category_filter and obj.get('category', '').lower() != category_filter:
                continue

            items.append({
                'name': name,
                'category': obj.get('category', 'unknown'),
                'rarity': obj.get('properties', {}).get('rarity', 'common'),
                'value': obj.get('properties', {}).get('value', 0)
            })

        if not items:
            if category_filter:
                print(f"No {category_filter} objects found")
            else:
                print("No objects found")
            return True

        # Sort by category, then name
        items.sort(key=lambda x: (x['category'], x['name']))

        print(f"\n{'Name':<20} {'Category':<12} {'Rarity':<10} {'Value'}")
        print("-" * 60)
        for item in items:
            print(f"{item['name']:<20} {item['category']:<12} {item['rarity']:<10} {item['value']}")

        print(f"\nTotal: {len(items)} objects")
        if category_filter:
            print(f"Category: {category_filter}")

        return True

    def _show_info(self, args: list) -> bool:
        """Show detailed object information."""
        if not args:
            print("❌ Usage: OBJECT INFO <name>")
            return False

        name = args[0].upper()

        if name not in self.catalog:
            print(f"❌ Object not found: {name}")
            print("   Use OBJECT LIST to see available objects")
            return False

        obj = self.catalog[name]

        # Display object info
        display = obj.get('display', {})
        properties = obj.get('properties', {})
        stats = obj.get('stats', {})
        effects = obj.get('effects', {})
        requirements = obj.get('requirements', {})
        crafting = obj.get('crafting', {})

        print(f"\n=== {display.get('display_name', name)} {display.get('icon', '')} ===")

        if display.get('description'):
            print(f"\n{display.get('description')}")

        if display.get('flavor_text'):
            print(f'"{display.get("flavor_text")}"')

        print(f"\nCategory: {obj.get('category', 'unknown').upper()}")
        print(f"Rarity: {properties.get('rarity', 'common').upper()}")
        print(f"Value: {properties.get('value', 0)} gold")

        # Properties
        if properties:
            print(f"\nProperties:")
            print(f"  Weight: {properties.get('weight', 0)} kg")
            if properties.get('stackable'):
                print(f"  Stackable: Yes (max {properties.get('max_stack', 1)})")
            print(f"  Tradeable: {'Yes' if properties.get('tradeable') else 'No'}")
            print(f"  Droppable: {'Yes' if properties.get('droppable') else 'No'}")

        # Stats (for equipment)
        if stats and any(stats.values()):
            print(f"\nStats:")
            if stats.get('attack'):
                print(f"  Attack: +{stats.get('attack')}")
            if stats.get('defense'):
                print(f"  Defense: +{stats.get('defense')}")
            if stats.get('speed'):
                sign = '+' if stats.get('speed') > 0 else ''
                print(f"  Speed: {sign}{stats.get('speed')}")
            if stats.get('hp_bonus'):
                print(f"  HP: +{stats.get('hp_bonus')}")
            if stats.get('mp_bonus'):
                print(f"  MP: +{stats.get('mp_bonus')}")
            if stats.get('luck'):
                print(f"  Luck: +{stats.get('luck')}")

        # Effects (for consumables)
        if effects and (effects.get('consumable') or effects.get('hp_restore') or effects.get('mp_restore')):
            print(f"\nEffects:")
            if effects.get('hp_restore'):
                print(f"  Restores {effects.get('hp_restore')} HP")
            if effects.get('mp_restore'):
                print(f"  Restores {effects.get('mp_restore')} MP")
            if effects.get('status_cure'):
                print(f"  Cures: {', '.join(effects.get('status_cure'))}")
            if effects.get('status_apply'):
                print(f"  Applies: {', '.join(effects.get('status_apply'))}")
            if effects.get('consumable'):
                print(f"  Consumed on use: Yes")

        # Requirements
        if requirements and (requirements.get('level') or requirements.get('stats') or requirements.get('class')):
            print(f"\nRequirements:")
            if requirements.get('level'):
                print(f"  Level: {requirements.get('level')}")
            if requirements.get('stats'):
                for stat, value in requirements.get('stats', {}).items():
                    print(f"  {stat.capitalize()}: {value}")
            if requirements.get('class'):
                print(f"  Class: {', '.join(requirements.get('class'))}")

        # Crafting
        if crafting and crafting.get('craftable'):
            print(f"\nCrafting:")
            if crafting.get('recipe'):
                print(f"  Recipe:")
                for ingredient in crafting.get('recipe', []):
                    print(f"    - {ingredient.get('quantity')}x {ingredient.get('item')}")
            if crafting.get('skill_required'):
                skill_level = crafting.get('level_required', 1)
                print(f"  Requires: {crafting.get('skill_required')} (level {skill_level})")

        return True

    def _search_objects(self, args: list) -> bool:
        """Search objects by name or description."""
        if not args:
            print("❌ Usage: OBJECT SEARCH <query>")
            return False

        query = ' '.join(args).lower()

        if not self.catalog:
            print("No objects loaded. Use: OBJECT LOAD <file>")
            return True

        results = []
        for name, obj in self.catalog.items():
            # Search in name, display name, description
            display = obj.get('display', {})
            if (query in name.lower() or
                query in display.get('display_name', '').lower() or
                query in display.get('description', '').lower()):
                results.append({
                    'name': name,
                    'display_name': display.get('display_name', name),
                    'category': obj.get('category', 'unknown')
                })

        if not results:
            print(f"No objects found matching: {query}")
            return True

        print(f"\nSearch results for '{query}':")
        print(f"{'Name':<20} {'Display Name':<25} {'Category'}")
        print("-" * 60)
        for item in results:
            print(f"{item['name']:<20} {item['display_name']:<25} {item['category']}")

        print(f"\nFound: {len(results)} objects")
        return True

    def _filter_objects(self, args: list) -> bool:
        """Filter objects by property."""
        if not args:
            print("❌ Usage: OBJECT FILTER <key>=<value>")
            print("   Examples:")
            print("     OBJECT FILTER category=weapon")
            print("     OBJECT FILTER rarity=legendary")
            print("     OBJECT FILTER stackable=true")
            return False

        if not self.catalog:
            print("No objects loaded. Use: OBJECT LOAD <file>")
            return True

        # Parse filter
        filter_str = ' '.join(args)
        if '=' not in filter_str:
            print("❌ Invalid filter (use key=value format)")
            return False

        key, value = filter_str.split('=', 1)
        key = key.strip()
        value = value.strip().lower()

        # Convert value to appropriate type
        if value in ['true', 'yes']:
            filter_value = True
        elif value in ['false', 'no']:
            filter_value = False
        elif value == 'null' or value == 'none':
            filter_value = None
        else:
            try:
                filter_value = int(value)
            except ValueError:
                try:
                    filter_value = float(value)
                except ValueError:
                    filter_value = value

        # Filter objects
        results = []
        for name, obj in self.catalog.items():
            # Navigate to property
            current = obj
            found = False

            # Try direct property
            if key in current:
                if str(current[key]).lower() == value:
                    found = True
            # Try nested in properties
            elif key in current.get('properties', {}):
                if str(current['properties'][key]).lower() == value:
                    found = True
            # Try nested in stats
            elif key in current.get('stats', {}):
                if str(current['stats'][key]).lower() == value:
                    found = True

            if found:
                results.append({
                    'name': name,
                    'category': obj.get('category', 'unknown'),
                    'rarity': obj.get('properties', {}).get('rarity', 'common')
                })

        if not results:
            print(f"No objects found with {key}={value}")
            return True

        print(f"\nFiltered results ({key}={value}):")
        print(f"{'Name':<20} {'Category':<12} {'Rarity'}")
        print("-" * 50)
        for item in results:
            print(f"{item['name']:<20} {item['category']:<12} {item['rarity']}")

        print(f"\nFound: {len(results)} objects")
        return True

    def _show_help(self):
        """Show OBJECT command help."""
        print("\n=== OBJECT Commands ===")
        print("\nManage item/object catalog:")
        print("  OBJECT LOAD <file>                - Load objects from JSON")
        print("  OBJECT LIST [category]            - List all objects")
        print("  OBJECT INFO <name>                - Show object details")
        print("  OBJECT SEARCH <query>             - Search by name/description")
        print("  OBJECT FILTER <key>=<value>       - Filter by property")
        print("\nExamples:")
        print("  OBJECT LOAD sandbox/user/items.json")
        print("  OBJECT LIST weapon")
        print("  OBJECT INFO SWORD-IRON")
        print("  OBJECT SEARCH potion")
        print("  OBJECT FILTER rarity=legendary")
