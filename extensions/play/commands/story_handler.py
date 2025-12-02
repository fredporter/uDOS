"""
STORY Command Handler - Adventure Scripting System
Integrates scenario engine, sprites, objects, and gameplay systems.

Commands:
    STORY START <adventure>         - Start a new adventure
    STORY LOAD <save_file>          - Load saved adventure progress
    STORY SAVE <save_file>          - Save current progress
    STORY STATUS                    - Show current adventure status
    STORY LIST                      - List available adventures
    STORY CONTINUE                  - Continue current adventure
    STORY CHOICE <number>           - Make a choice
    STORY ROLLBACK                  - Undo last choice
    STORY QUIT                      - Exit current adventure

Round 2 Integration:
- Leverages scenario_engine from core.services.game
- Integrates with SPRITE system (character HP/XP tracking)
- Integrates with OBJECT system (inventory/equipment)
- Supports .upy adventure scripts with advanced flow control
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from extensions.play.services.game_mechanics.scenario_engine import ScenarioEngine, EventType
from extensions.play.services.game_mechanics.scenario_service import ScenarioService, ScenarioType
from extensions.play.services.game_mechanics.xp_service import XPService, XPCategory
from extensions.play.services.game_mechanics.inventory_service import InventoryService
from extensions.play.services.game_mechanics.survival_service import SurvivalService
from extensions.play.services.game_mechanics.upy_adventure_parser import parse_upy_adventure


class StoryHandler:
    """Handler for STORY commands (adventure management)."""

    def __init__(self, components: Dict[str, Any]):
        """Initialize story handler with system components."""
        self.components = components
        self.config = components.get('config')
        self.logger = components.get('logger')
        self.output = components.get('output')

        # Initialize game services
        self.scenario_service = ScenarioService()
        self.xp_service = XPService()
        self.inventory_service = InventoryService()
        self.survival_service = SurvivalService()

        # Initialize scenario engine with all services
        self.scenario_engine = ScenarioEngine(
            scenario_service=self.scenario_service,
            xp_service=self.xp_service,
            inventory_service=self.inventory_service,
            survival_service=self.survival_service
        )

        # Adventure state
        self.current_adventure = None
        self.current_session_id = None
        self.current_choice_options = None  # Store current choice options
        self.adventure_dir = Path("sandbox/ucode/adventures")
        self.save_dir = Path("sandbox/user/saves")
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def handle(self, command: str, params: list) -> str:
        """
        Handle STORY commands.

        Args:
            command: STORY subcommand (START, LIST, etc.)
            params: Command parameters

        Returns:
            Result message string
        """
        command = command.upper()

        if command == 'START':
            return self._start_adventure(params)
        elif command == 'LOAD':
            return self._load_save(params)
        elif command == 'SAVE':
            return self._save_progress(params)
        elif command == 'STATUS':
            return self._show_status()
        elif command == 'LIST':
            return self._list_adventures()
        elif command == 'CONTINUE':
            return self._continue_adventure()
        elif command == 'CHOICE':
            return self._make_choice(params)
        elif command == 'ROLLBACK':
            return self._rollback()
        elif command == 'QUIT':
            return self._quit_adventure()
        elif command == 'HELP' or not command:
            return self._show_help()
        else:
            return f"❌ Unknown STORY command: {command}\n\n" + self._show_help()

    def _show_help(self) -> str:
        """Display STORY command help."""
        return """
📖 STORY Command - Adventure System

Commands:
  STORY START <adventure>    - Start new adventure
  STORY LOAD <save>          - Load saved progress
  STORY SAVE <save>          - Save current progress
  STORY STATUS               - Show adventure status
  STORY LIST                 - List available adventures
  STORY CONTINUE             - Continue current adventure
  STORY CHOICE <number>      - Make a choice (1, 2, 3, etc.)
  STORY ROLLBACK             - Undo last choice
  STORY QUIT                 - Exit adventure

Examples:
  STORY START first-steps              # Start "first-steps" adventure
  STORY CONTINUE                       # Continue story
  STORY CHOICE 1                       # Choose option 1
  STORY SAVE my-progress               # Save to my-progress.json
  STORY LOAD my-progress               # Load from my-progress.json

Integration:
  - Uses SPRITE for character stats (HP, XP)
  - Uses OBJECT for inventory/equipment
  - Tracks survival stats (hunger, thirst, health)
  - Awards XP for choices and actions
  - Persistent save/load system
"""

    def _start_adventure(self, params: list) -> str:
        """Start a new adventure."""
        if not params:
            return "❌ Usage: STORY START <adventure_name>"

        adventure_name = params[0]
        adventure_file = self.adventure_dir / f"{adventure_name}.upy"
        is_upy = True

        if not adventure_file.exists():
            # Try .json extension
            adventure_file = self.adventure_dir / f"{adventure_name}.json"
            is_upy = False
            if not adventure_file.exists():
                return (f"❌ Adventure not found: {adventure_name}\n"
                       f"   Looking in: {self.adventure_dir}\n\n"
                       f"💡 Use 'STORY LIST' to see available adventures")

        # Load adventure script
        try:
            # If .upy file, parse it first
            if is_upy:
                if self.logger:
                    self.logger.info(f"Parsing .upy adventure: {adventure_file}")

                # Parse .upy to scenario structure
                parsed_scenario = parse_upy_adventure(str(adventure_file))

                # Register scenario with metadata from parsed data
                metadata = parsed_scenario.get('metadata', {})
                scenario_name = metadata.get('name', adventure_name)

                # Register if not already exists
                self.scenario_service.register_scenario(
                    name=scenario_name,
                    scenario_type=ScenarioType.STORY,
                    title=metadata.get('name', adventure_name),
                    description=metadata.get('description', ''),
                    difficulty=1,
                    estimated_minutes=30,
                    xp_reward=100
                )

                # Save parsed scenario as temp JSON for ScenarioEngine
                temp_json = self.adventure_dir / f".{adventure_name}_parsed.json"
                with open(temp_json, 'w') as f:
                    json.dump(parsed_scenario, f, indent=2)

                adventure_file = temp_json

                if self.logger:
                    self.logger.info(f"Parsed {len(parsed_scenario['events'])} events, "
                                   f"{len(parsed_scenario['labels'])} labels")
            else:
                # For JSON files, load and register
                with open(adventure_file, 'r') as f:
                    scenario_data = json.load(f)
                    metadata = scenario_data.get('metadata', {})
                    scenario_name = metadata.get('name', adventure_name)

                    self.scenario_service.register_scenario(
                        name=scenario_name,
                        scenario_type=ScenarioType.STORY,
                        title=metadata.get('title', adventure_name),
                        description=metadata.get('description', ''),
                        difficulty=metadata.get('difficulty', 1),
                        estimated_minutes=metadata.get('estimated_time', 30),
                        xp_reward=metadata.get('xp_reward', 100)
                    )

            result = self.scenario_engine.start_scenario_from_script(str(adventure_file))
            if "error" in result:
                return f"❌ Error loading adventure: {result['error']}"

            self.current_adventure = adventure_name
            self.current_session_id = result.get("session_id")

            # Initialize player stats for new adventure
            self._initialize_player_stats()

            return (f"✅ Adventure started: {adventure_name}\n"
                   f"   Format: {'.upy' if is_upy else '.json'}\n"
                   f"   Session ID: {self.current_session_id}\n\n"
                   f"📊 Player stats initialized\n"
                   f"💡 Use 'STORY CONTINUE' to begin")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Adventure start error: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
            return f"❌ Failed to start adventure: {e}"

    def _load_save(self, args: list) -> str:
        """Load saved adventure progress."""
        if not args:
            return "❌ Usage: STORY LOAD <save_name>"

        save_name = args[0]
        if not save_name.endswith('.json'):
            save_name += '.json'

        save_file = self.save_dir / save_name

        if not save_file.exists():
            return (f"❌ Save file not found: {save_name}\n"
                   f"   Looking in: {self.save_dir}")

        try:
            with open(save_file, 'r') as f:
                save_data = json.load(f)

            adventure_name = save_data.get('adventure')

            # Restart the adventure
            adventure_file = self.adventure_dir / f"{adventure_name}.upy"
            is_upy = adventure_file.exists()

            if not is_upy:
                adventure_file = self.adventure_dir / f"{adventure_name}.json"
                if not adventure_file.exists():
                    return f"❌ Adventure file not found: {adventure_name}"

            # Load and parse adventure
            if is_upy:
                from extensions.play.services.game_mechanics.upy_adventure_parser import parse_upy_adventure
                parsed_scenario = parse_upy_adventure(str(adventure_file))

                # Save parsed scenario as temp JSON for ScenarioEngine
                temp_json = self.adventure_dir / f".{adventure_name}_loaded.json"
                with open(temp_json, 'w') as f:
                    json.dump(parsed_scenario, f, indent=2)

                adventure_file = temp_json

            # Start scenario
            result = self.scenario_engine.start_scenario_from_script(str(adventure_file))

            if "error" in result:
                return f"❌ Failed to load adventure: {result['error']}"

            self.current_adventure = adventure_name
            self.current_session_id = result.get("session_id")

            # Restore game state
            from extensions.play.services.game_mechanics.survival_service import SurvivalStat
            from extensions.play.services.game_mechanics.inventory_service import ItemCategory

            # Restore stats
            stats = save_data.get('stats', {})
            for stat_name, value in stats.items():
                if stat_name == 'health':
                    self.survival_service.set_stat(SurvivalStat.HEALTH, value, "Load save")
                elif stat_name == 'thirst':
                    self.survival_service.set_stat(SurvivalStat.THIRST, value, "Load save")
                elif stat_name == 'hunger':
                    self.survival_service.set_stat(SurvivalStat.HUNGER, value, "Load save")
                elif stat_name == 'fatigue':
                    self.survival_service.set_stat(SurvivalStat.FATIGUE, value, "Load save")

            # Restore XP (approximate by awarding difference)
            saved_xp = save_data.get('xp', 0)
            current_xp = self.xp_service.get_total_xp()
            if saved_xp > current_xp:
                from extensions.play.services.game_mechanics.xp_service import XPCategory
                self.xp_service.award_xp(XPCategory.INFORMATION, saved_xp - current_xp, "Load save")

            # Restore inventory
            inventory_data = save_data.get('inventory', [])
            for item in inventory_data:
                try:
                    cat = ItemCategory[item['category'].upper()]
                except KeyError:
                    cat = ItemCategory.MISC

                self.inventory_service.add_item(
                    name=item['name'],
                    category=cat,
                    quantity=item['quantity'],
                    weight=item.get('weight', 0.5)
                )

            # Restore scenario position
            scenario_state = save_data.get('scenario', {})
            event_index = scenario_state.get('event_index', 0)
            self.scenario_engine.event_index = event_index

            timestamp = save_data.get('timestamp', 'Unknown')
            total_events = scenario_state.get('total_events', 0)

            return (f"📂 Loaded save: {save_name}\n"
                   f"   Adventure: {adventure_name}\n"
                   f"   Saved: {timestamp[:19]}\n"
                   f"   Progress: {event_index}/{total_events} events\n\n"
                   f"💡 Use 'STORY STATUS' to check state\n"
                   f"💡 Use 'STORY CONTINUE' to resume")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Save load error: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
            return f"❌ Failed to load save: {e}"

    def _save_progress(self, args: list) -> str:
        """Save current adventure progress."""
        if not self.current_adventure:
            return "❌ No active adventure to save"

        if not args:
            # Auto-generate save name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"{self.current_adventure}_{timestamp}"
        else:
            save_name = args[0]

        # Ensure .json extension
        if not save_name.endswith('.json'):
            save_name += '.json'

        save_file = self.save_dir / save_name

        try:
            # Collect game state
            from extensions.play.services.game_mechanics.survival_service import SurvivalStat

            # Get survival stats
            stats = {}
            for stat in [SurvivalStat.HEALTH, SurvivalStat.THIRST,
                        SurvivalStat.HUNGER, SurvivalStat.FATIGUE]:
                stat_data = self.survival_service.get_stat(stat)
                stats[stat.value] = stat_data.get('current', 0)

            # Get XP
            total_xp = self.xp_service.get_total_xp()

            # Get inventory
            inventory = self.inventory_service.get_inventory("Personal Inventory")
            inventory_data = []
            for item in inventory:
                inventory_data.append({
                    'name': item['name'],
                    'category': item['category'],
                    'quantity': item['quantity'],
                    'weight': item['weight']
                })

            # Get scenario state
            scenario_state = {
                'event_index': self.scenario_engine.event_index,
                'total_events': len(self.scenario_engine.current_events),
                'has_choice': self.current_choice_options is not None
            }

            save_data = {
                'adventure': self.current_adventure,
                'session_id': self.current_session_id,
                'timestamp': datetime.now().isoformat(),
                'stats': stats,
                'xp': total_xp,
                'inventory': inventory_data,
                'scenario': scenario_state,
                'version': '2.0.0'
            }

            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=2)

            return (f"💾 Progress saved: {save_name}\n"
                   f"   Location: {save_file}\n"
                   f"   Adventure: {self.current_adventure}\n"
                   f"   Progress: {scenario_state['event_index']}/{scenario_state['total_events']} events")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Save error: {e}")
            return f"❌ Failed to save: {e}"

    def _show_status(self) -> str:
        """Show current adventure status with SPRITE stats and inventory."""
        if not self.current_adventure:
            return ("📖 No active adventure\n"
                   "💡 Use 'STORY START <name>' to begin")

        output = "=" * 60 + "\n"
        output += f"📖 ADVENTURE STATUS\n"
        output += "=" * 60 + "\n\n"

        output += f"Adventure: {self.current_adventure}\n"
        output += f"Session ID: {self.current_session_id}\n"

        # Show scenario progress
        if self.scenario_engine.current_events:
            total = len(self.scenario_engine.current_events)
            current = self.scenario_engine.event_index
            output += f"Progress: {current}/{total} events ({int(current/total*100)}%)\n"

        output += "\n" + "-" * 60 + "\n"
        output += "CHARACTER STATS\n"
        output += "-" * 60 + "\n\n"

        # Get survival stats
        try:
            from extensions.play.services.game_mechanics.survival_service import SurvivalStat

            # Health/HP
            health_data = self.survival_service.get_stat(SurvivalStat.HEALTH)
            if 'current' in health_data:
                hp = int(health_data['current'])
                output += f"❤️  Health: {hp}/100"
                if health_data['status'] == "critical":
                    output += " (CRITICAL!)"
                elif health_data['status'] == "warning":
                    output += " (Low)"
                output += "\n"

            # Thirst
            thirst_data = self.survival_service.get_stat(SurvivalStat.THIRST)
            if 'current' in thirst_data:
                thirst = int(thirst_data['current'])
                output += f"💧 Thirst: {thirst}/100"
                if thirst_data['status'] == "critical":
                    output += " (CRITICAL!)"
                elif thirst_data['status'] == "warning":
                    output += " (High)"
                output += "\n"

            # Hunger
            hunger_data = self.survival_service.get_stat(SurvivalStat.HUNGER)
            if 'current' in hunger_data:
                hunger = int(hunger_data['current'])
                output += f"🍖 Hunger: {hunger}/100"
                if hunger_data['status'] == "critical":
                    output += " (CRITICAL!)"
                elif hunger_data['status'] == "warning":
                    output += " (High)"
                output += "\n"

            # Fatigue (stamina)
            fatigue_data = self.survival_service.get_stat(SurvivalStat.FATIGUE)
            if 'current' in fatigue_data:
                fatigue = int(fatigue_data['current'])
                stamina = 100 - fatigue  # Invert fatigue to stamina
                output += f"⚡ Stamina: {stamina}/100"
                if fatigue_data['status'] == "critical":
                    output += " (Exhausted)"
                elif fatigue_data['status'] == "warning":
                    output += " (Tired)"
                output += "\n"
        except Exception as e:
            output += f"Stats unavailable: {e}\n"

        # Get XP/Level
        output += "\n" + "-" * 60 + "\n"
        output += "EXPERIENCE & LEVEL\n"
        output += "-" * 60 + "\n\n"

        try:
            total_xp = self.xp_service.get_total_xp()

            # Calculate overall level from total XP
            # Using same formula as skills: Level N starts at (N-1)^2 * 100 XP
            level = 1
            while level ** 2 * 100 <= total_xp:
                level += 1

            # Calculate XP for current and next level
            current_level_base = (level - 1) ** 2 * 100
            next_level_total = level ** 2 * 100
            xp_in_level = total_xp - current_level_base
            xp_needed = next_level_total - current_level_base

            # Progress bar (20 chars)
            if xp_needed > 0:
                progress = int((xp_in_level / xp_needed) * 20)
                bar = "█" * progress + "░" * (20 - progress)
            else:
                bar = "█" * 20

            output += f"🌟 Level: {level}\n"
            output += f"✨ XP: {total_xp} ({xp_in_level}/{xp_needed} to next level)\n"
            output += f"   [{bar}] {int((xp_in_level/xp_needed)*100) if xp_needed > 0 else 100}%\n"
        except Exception as e:
            output += f"XP unavailable: {e}\n"

        # Get inventory
        output += "\n" + "-" * 60 + "\n"
        output += "INVENTORY\n"
        output += "-" * 60 + "\n\n"

        try:
            inventory = self.inventory_service.get_inventory("Personal Inventory")
            if inventory and len(inventory) > 0:
                # Show first 10 items
                for item in inventory[:10]:
                    item_name = item.get('name', 'Unknown')
                    quantity = item.get('quantity', 1)
                    condition = item.get('condition_state', '')

                    output += f"  • {item_name}"
                    if quantity > 1:
                        output += f" x{quantity}"
                    if condition and condition != 'pristine':
                        output += f" ({condition})"
                    output += "\n"

                if len(inventory) > 10:
                    output += f"  ... and {len(inventory) - 10} more items\n"

                # Show inventory stats
                stats = self.inventory_service.get_inventory_stats("Personal Inventory")
                if stats:
                    total_weight = stats.get('total_weight', 0)
                    item_count = stats.get('item_count', 0)
                    # Calculate total quantity from inventory list
                    total_quantity = sum(item.get('quantity', 1) for item in inventory)
                    output += f"\n  Total: {total_quantity} items ({item_count} unique), {total_weight:.1f} kg\n"
            else:
                output += "  (Empty)\n"
        except Exception as e:
            output += f"  Inventory unavailable: {e}\n"

        output += "\n" + "=" * 60 + "\n"
        output += "💡 Use 'STORY CONTINUE' to proceed\n"
        output += "=" * 60 + "\n"

        return output

    def _list_adventures(self) -> str:
        """List available adventures."""
        if not self.adventure_dir.exists():
            return f"📖 No adventures directory: {self.adventure_dir}"

        adventures = []
        for ext in ['*.upy', '*.json']:
            adventures.extend(self.adventure_dir.glob(ext))

        if not adventures:
            return (f"📖 No adventures found in {self.adventure_dir}\n\n"
                   f"💡 Create adventure scripts (.upy or .json files)")

        output = f"📖 Available Adventures ({len(adventures)}):\n\n"

        for adventure in sorted(adventures):
            name = adventure.stem
            size = adventure.stat().st_size
            modified = datetime.fromtimestamp(adventure.stat().st_mtime)

            output += f"  • {name}\n"
            output += f"    File: {adventure.name}\n"
            output += f"    Size: {size} bytes\n"
            output += f"    Modified: {modified.strftime('%Y-%m-%d %H:%M')}\n\n"

        output += "💡 Start with: STORY START <name>"

        return output

    def _initialize_player_stats(self):
        """Initialize player stats at adventure start."""
        try:
            # Initialize with default healthy starting values
            from extensions.play.services.game_mechanics.survival_service import SurvivalStat

            self.survival_service.set_stat(SurvivalStat.HEALTH, 100, "Adventure start")
            self.survival_service.set_stat(SurvivalStat.THIRST, 0, "Adventure start")
            self.survival_service.set_stat(SurvivalStat.HUNGER, 0, "Adventure start")
            self.survival_service.set_stat(SurvivalStat.FATIGUE, 0, "Adventure start")

            if self.logger:
                self.logger.info("Player stats initialized for adventure")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize player stats: {e}")

    def _continue_adventure(self) -> str:
        """Continue current adventure by processing next event(s)."""
        if not self.current_adventure:
            return ("❌ No active adventure\n"
                   "💡 Use 'STORY START <name>' to begin")

        if not self.scenario_engine.has_more_events():
            return ("✅ Adventure complete!\n\n"
                   f"📖 You finished: {self.current_adventure}\n"
                   "💡 Use 'STORY LIST' to see other adventures")

        output = ""

        # Process events until we hit a CHOICE or run out
        while self.scenario_engine.has_more_events():
            event = self.scenario_engine.get_next_event()
            if not event:
                break

            # Process the event
            result = self._process_event(event)

            if result:
                output += result

            # Stop at choice points to wait for player input
            event_type = event.get("type")
            if event_type == "choice":
                break

        return output if output else "📖 No events to display"

    def _process_event(self, event: dict) -> str:
        """Process a single adventure event and return display text.

        Args:
            event: Event dict from .upy parser

        Returns:
            String to display to user (or empty string for silent events)
        """
        event_type = event.get("type")

        if event_type == "narrative":
            return self._process_narrative_upy(event)
        elif event_type == "choice":
            return self._process_choice_upy(event)
        elif event_type == "checkpoint":
            return ""  # Silent checkpoint
        else:
            # Process effects attached to event
            output = ""
            effects = event.get("effects", [])
            for effect in effects:
                effect_result = self._process_effect(effect)
                if effect_result:
                    output += effect_result
            return output

    def _process_narrative_upy(self, event: dict) -> str:
        """Process narrative text event from .upy parser."""
        content = event.get("content", "")

        # Process any effects first
        effects_output = ""
        effects = event.get("effects", [])
        for effect in effects:
            effect_result = self._process_effect(effect)
            if effect_result:
                effects_output += effect_result

        # Display narrative text
        output = "\n" + content + "\n\n"

        # Add effects output after narrative
        if effects_output:
            output += effects_output

        return output

    def _process_choice_upy(self, event: dict) -> str:
        """Process choice event from .upy parser - display options and wait."""
        content = event.get("content", "What do you do?")
        choices = event.get("choices", [])

        output = "\n" + "=" * 60 + "\n"
        output += f"🤔 {content}\n"
        output += "=" * 60 + "\n\n"

        # Convert .upy choices to option format for handler
        options = []
        for choice in choices:
            option_text = choice.get("text", "Option")
            next_event = choice.get("next_event", "")
            options.append({
                "text": option_text,
                "jump_to": next_event,
                "consequences": []
            })

        for i, option in enumerate(options, 1):
            output += f"  {i}. {option['text']}\n"

        output += "\n💡 Use 'STORY CHOICE <number>' to decide\n"

        # Store current choice options for validation
        self.current_choice_options = options

        return output

    def _process_effect(self, effect: dict) -> str:
        """Process an effect from event effects list."""
        effect_type = effect.get("type")

        if effect_type == "stat_change":
            return self._process_stat_effect(effect)
        elif effect_type == "xp_award":
            return self._process_xp_effect(effect)
        elif effect_type == "item_give":
            return self._process_item_give_effect(effect)
        elif effect_type == "item_take":
            return self._process_item_take_effect(effect)
        elif effect_type == "flag_set":
            return self._process_flag_effect(effect)
        elif effect_type == "dice_roll":
            # Dice rolls are silent (result stored in variable)
            return ""
        else:
            return ""

    def _process_stat_effect(self, effect: dict) -> str:
        """Process stat modification effect."""
        target = effect.get("target", "").lower()
        change = effect.get("value", 0)

        from extensions.play.services.game_mechanics.survival_service import SurvivalStat

        # Map target names to SurvivalStat enum
        stat_map = {
            "health": SurvivalStat.HEALTH,
            "thirst": SurvivalStat.THIRST,
            "hunger": SurvivalStat.HUNGER,
            "stamina": SurvivalStat.FATIGUE,  # Invert: stamina decrease = fatigue increase
            "fatigue": SurvivalStat.FATIGUE
        }

        if target not in stat_map:
            return ""

        stat = stat_map[target]

        # Invert stamina changes (stamina +10 = fatigue -10)
        if target == "stamina":
            change = -change

        try:
            self.survival_service.update_stat(stat, change, "adventure event")

            # Display notification
            if change > 0:
                symbol = "⬆️"
                direction = "increased"
            else:
                symbol = "⬇️"
                direction = "decreased"

            display_name = target.capitalize()

            return f"{symbol} {display_name} {direction} by {abs(change)}\n"

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to update stat {target}: {e}")
            return ""

    def _process_xp_effect(self, effect: dict) -> str:
        """Process XP award effect."""
        amount = effect.get("value", 0)

        from extensions.play.services.game_mechanics.xp_service import XPCategory

        try:
            # Award to INFORMATION category by default
            self.xp_service.award_xp(XPCategory.INFORMATION, amount, "adventure progress")
            return f"✨ Gained {amount} XP\n"
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to award XP: {e}")
            return ""

    def _process_item_give_effect(self, effect: dict) -> str:
        """Process item acquisition effect."""
        item_name = effect.get("item", "Unknown Item")
        quantity = effect.get("quantity", 1)
        category = effect.get("category", "misc")
        weight = effect.get("weight", 0.5)

        from extensions.play.services.game_mechanics.inventory_service import ItemCategory

        # Map category string to enum
        try:
            item_category = ItemCategory[category.upper()]
        except KeyError:
            item_category = ItemCategory.MISC

        try:
            self.inventory_service.add_item(
                name=item_name,
                category=item_category,
                quantity=quantity,
                weight=weight
            )

            if quantity > 1:
                return f"📦 Received {quantity}x {item_name}\n"
            else:
                return f"📦 Received {item_name}\n"

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to add item {item_name}: {e}")
            return ""

    def _process_item_take_effect(self, effect: dict) -> str:
        """Process item removal effect."""
        item_name = effect.get("item", "Unknown Item")
        quantity = effect.get("quantity", 1)

        try:
            # Find item in inventory
            inventory = self.inventory_service.get_inventory("Personal Inventory")
            item = next((i for i in inventory if i['name'] == item_name), None)

            if not item:
                return f"⚠️  You don't have: {item_name}\n"

            self.inventory_service.remove_item(item['id'], quantity)

            if quantity > 1:
                return f"📤 Lost {quantity}x {item_name}\n"
            else:
                return f"📤 Lost {item_name}\n"

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to remove item {item_name}: {e}")
            return ""

    def _process_flag_effect(self, effect: dict) -> str:
        """Process flag setting effect."""
        flag_name = effect.get("flag", "")

        # Store flag in scenario service
        if self.current_session_id and flag_name:
            self.scenario_service.set_variable(
                self.current_session_id,
                f"FLAG:{flag_name}",
                True
            )
            return f"🏁 Achievement: {flag_name}\n"

        return ""
    def _make_choice(self, args: list) -> str:
        """Make a choice in the adventure."""
        if not self.current_adventure:
            return "❌ No active adventure"

        if not self.current_choice_options:
            return ("❌ No active choice\n"
                   "💡 Use 'STORY CONTINUE' to proceed")

        if not args:
            return "❌ Usage: STORY CHOICE <number>"

        try:
            choice_num = int(args[0])

            # Validate choice number
            if choice_num < 1 or choice_num > len(self.current_choice_options):
                return (f"❌ Invalid choice: {choice_num}\n"
                       f"💡 Choose between 1 and {len(self.current_choice_options)}")

            # Get the chosen option
            chosen_option = self.current_choice_options[choice_num - 1]
            option_text = chosen_option.get("text", f"Option {choice_num}")

            output = f"\n✅ You chose: {option_text}\n\n"

            # Clear current choice
            self.current_choice_options = None

            # Execute the choice's consequences
            consequences = chosen_option.get("consequences", [])
            for consequence in consequences:
                result = self._process_event(consequence)
                if result:
                    output += result

            # Check for jump target
            jump_to = chosen_option.get("jump_to")
            if jump_to:
                # Find the event with this label
                for i, event in enumerate(self.scenario_engine.current_events):
                    if event.get("label") == jump_to:
                        self.scenario_engine.event_index = i
                        break

            # Continue processing after choice
            output += "\n" + self._continue_adventure()

            return output

        except ValueError:
            return f"❌ Invalid choice number: {args[0]}"

    def _rollback(self) -> str:
        """Rollback last choice."""
        if not self.current_adventure:
            return "❌ No active adventure"

        # TODO: Implement rollback through scenario engine
        return ("📖 Rolling back last choice...\n"
               "⚠️  Rollback feature in progress...")

    def _quit_adventure(self) -> str:
        """Exit current adventure."""
        if not self.current_adventure:
            return "❌ No active adventure"

        adventure_name = self.current_adventure

        # Prompt to save
        output = f"📖 Exiting adventure: {adventure_name}\n\n"
        output += "💾 Would you like to save before quitting? (Use STORY SAVE)\n\n"

        self.current_adventure = None
        self.current_session_id = None

        output += "✅ Adventure exited"

        return output


# Register command
def register_command(registry):
    """Register the STORY command."""
    registry.register(
        name='STORY',
        handler=StoryHandler,
        category='gameplay',
        description='Adventure scripting and story management',
        aliases=['ADVENTURE', 'QUEST'],
        help_text="""
STORY - Adventure System

Manage interactive adventures with branching narratives,
character progression, inventory, and survival mechanics.

Commands:
  START <name>     - Begin new adventure
  LOAD <save>      - Load saved progress
  SAVE <save>      - Save current progress
  STATUS           - Show adventure status
  LIST             - List available adventures
  CONTINUE         - Continue story
  CHOICE <num>     - Make a choice
  ROLLBACK         - Undo last choice
  QUIT             - Exit adventure

Example:
  STORY START first-steps
  STORY CONTINUE
  STORY CHOICE 1
  STORY SAVE my-progress
"""
    )
