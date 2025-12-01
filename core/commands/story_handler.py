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

from core.services.game.scenario_engine import ScenarioEngine, EventType
from core.services.game.scenario_service import ScenarioService
from core.services.game.xp_service import XPService, XPCategory
from core.services.game.inventory_service import InventoryService
from core.services.game.survival_service import SurvivalService


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

        if not adventure_file.exists():
            # Try .json extension
            adventure_file = self.adventure_dir / f"{adventure_name}.json"
            if not adventure_file.exists():
                return (f"❌ Adventure not found: {adventure_name}\n"
                       f"   Looking in: {self.adventure_dir}\n\n"
                       f"💡 Use 'STORY LIST' to see available adventures")

        # Load adventure script
        try:
            result = self.scenario_engine.start_scenario_from_script(str(adventure_file))
            if "error" in result:
                return f"❌ Error loading adventure: {result['error']}"

            self.current_adventure = adventure_name
            self.current_session_id = result.get("session_id")

            return (f"✅ Adventure started!\n"
                   f"   Session ID: {self.current_session_id}\n\n"
                   f"💡 Use 'STORY CONTINUE' to begin")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Adventure start error: {e}")
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

            self.current_adventure = save_data.get('adventure')
            self.current_session_id = save_data.get('session_id')

            # TODO: Restore scenario engine state
            # self.scenario_engine.load_state(save_data['engine_state'])

            return (f"✅ Loaded save: {save_name}\n"
                   f"   Adventure: {self.current_adventure}\n"
                   f"   Session: {self.current_session_id}\n\n"
                   f"💡 Use 'STORY CONTINUE' to resume")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Save load error: {e}")
            return f"❌ Failed to load save: {e}"

    def _save_progress(self, args: list) -> str:
        """Save current adventure progress."""
        if not self.current_adventure:
            return "❌ No active adventure to save"

        if not args:
            # Auto-generate save name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_name = f"{self.current_adventure}_{timestamp}.json"
        else:
            save_name = args[0]
            if not save_name.endswith('.json'):
                save_name += '.json'

        save_file = self.save_dir / save_name

        try:
            save_data = {
                'adventure': self.current_adventure,
                'session_id': self.current_session_id,
                'timestamp': datetime.now().isoformat(),
                # TODO: Save scenario engine state
                # 'engine_state': self.scenario_engine.get_state(),
            }

            with open(save_file, 'w') as f:
                json.dump(save_data, f, indent=2)

            return (f"✅ Progress saved: {save_name}\n"
                   f"   Location: {save_file}")

        except Exception as e:
            if self.logger:
                self.logger.error(f"Save error: {e}")
            return f"❌ Failed to save: {e}"

    def _show_status(self) -> str:
        """Show current adventure status."""
        if not self.current_adventure:
            return ("📖 No active adventure\n"
                   "💡 Use 'STORY START <name>' to begin")

        output = f"📖 Current Adventure: {self.current_adventure}\n"
        output += f"   Session ID: {self.current_session_id}\n"

        # Show scenario progress
        if self.scenario_engine.current_events:
            total = len(self.scenario_engine.current_events)
            current = self.scenario_engine.event_index
            output += f"   Progress: {current}/{total} events\n"

        # TODO: Show sprite stats, inventory, etc.
        output += "\n💡 Use 'STORY CONTINUE' to proceed"

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

    def _continue_adventure(self) -> str:
        """Continue current adventure."""
        if not self.current_adventure:
            return ("❌ No active adventure\n"
                   "💡 Use 'STORY START <name>' to begin")

        # TODO: Process next event from scenario engine
        return (f"📖 Continuing: {self.current_adventure}\n"
               f"⚠️  Adventure engine integration in progress...\n"
               f"💡 Full event processing coming soon")

    def _make_choice(self, args: list) -> str:
        """Make a choice in the adventure."""
        if not self.current_adventure:
            return "❌ No active adventure"

        if not args:
            return "❌ Usage: STORY CHOICE <number>"

        try:
            choice_num = int(args[0])
            # TODO: Process choice through scenario engine
            return (f"📖 Choice {choice_num} selected\n"
                   f"⚠️  Choice processing in progress...")

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
