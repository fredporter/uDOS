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

    def handle(self, args: list) -> bool:
        """
        Handle STORY commands.

        Args:
            args: Command arguments

        Returns:
            True if command handled successfully
        """
        if not args:
            self._show_help()
            return True

        command = args[0].upper()

        if command == 'START':
            return self._start_adventure(args[1:])
        elif command == 'LOAD':
            return self._load_save(args[1:])
        elif command == 'SAVE':
            return self._save_progress(args[1:])
        elif command == 'STATUS':
            return self._show_status()
        elif command == 'LIST':
            return self._list_adventures()
        elif command == 'CONTINUE':
            return self._continue_adventure()
        elif command == 'CHOICE':
            return self._make_choice(args[1:])
        elif command == 'ROLLBACK':
            return self._rollback()
        elif command == 'QUIT':
            return self._quit_adventure()
        else:
            self.output.print(f"❌ Unknown STORY command: {command}")
            self._show_help()
            return False

    def _show_help(self):
        """Display STORY command help."""
        self.output.print("""
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
""")

    def _start_adventure(self, args: list) -> bool:
        """Start a new adventure."""
        if not args:
            self.output.print("❌ Usage: STORY START <adventure_name>")
            return False

        adventure_name = args[0]
        adventure_file = self.adventure_dir / f"{adventure_name}.upy"

        if not adventure_file.exists():
            # Try .json extension
            adventure_file = self.adventure_dir / f"{adventure_name}.json"
            if not adventure_file.exists():
                self.output.print(f"❌ Adventure not found: {adventure_name}")
                self.output.print(f"   Looking in: {self.adventure_dir}")
                self.output.print(f"\n💡 Use 'STORY LIST' to see available adventures")
                return False

        self.output.print(f"📖 Starting adventure: {adventure_name}")
        self.output.print(f"   File: {adventure_file}")

        # Load adventure script
        try:
            result = self.scenario_engine.start_scenario_from_script(str(adventure_file))
            if "error" in result:
                self.output.print(f"❌ Error loading adventure: {result['error']}")
                return False

            self.current_adventure = adventure_name
            self.current_session_id = result.get("session_id")

            self.output.print(f"✅ Adventure started!")
            self.output.print(f"   Session ID: {self.current_session_id}")
            self.output.print(f"\n💡 Use 'STORY CONTINUE' to begin")

            return True

        except Exception as e:
            self.output.print(f"❌ Failed to start adventure: {e}")
            if self.logger:
                self.logger.error(f"Adventure start error: {e}")
            return False

    def _load_save(self, args: list) -> bool:
        """Load saved adventure progress."""
        if not args:
            self.output.print("❌ Usage: STORY LOAD <save_name>")
            return False

        save_name = args[0]
        if not save_name.endswith('.json'):
            save_name += '.json'

        save_file = self.save_dir / save_name

        if not save_file.exists():
            self.output.print(f"❌ Save file not found: {save_name}")
            self.output.print(f"   Looking in: {self.save_dir}")
            return False

        try:
            with open(save_file, 'r') as f:
                save_data = json.load(f)

            self.current_adventure = save_data.get('adventure')
            self.current_session_id = save_data.get('session_id')

            # TODO: Restore scenario engine state
            # self.scenario_engine.load_state(save_data['engine_state'])

            self.output.print(f"✅ Loaded save: {save_name}")
            self.output.print(f"   Adventure: {self.current_adventure}")
            self.output.print(f"   Session: {self.current_session_id}")
            self.output.print(f"\n💡 Use 'STORY CONTINUE' to resume")

            return True

        except Exception as e:
            self.output.print(f"❌ Failed to load save: {e}")
            if self.logger:
                self.logger.error(f"Save load error: {e}")
            return False

    def _save_progress(self, args: list) -> bool:
        """Save current adventure progress."""
        if not self.current_adventure:
            self.output.print("❌ No active adventure to save")
            return False

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

            self.output.print(f"✅ Progress saved: {save_name}")
            self.output.print(f"   Location: {save_file}")

            return True

        except Exception as e:
            self.output.print(f"❌ Failed to save: {e}")
            if self.logger:
                self.logger.error(f"Save error: {e}")
            return False

    def _show_status(self) -> bool:
        """Show current adventure status."""
        if not self.current_adventure:
            self.output.print("📖 No active adventure")
            self.output.print("💡 Use 'STORY START <name>' to begin")
            return True

        self.output.print(f"📖 Current Adventure: {self.current_adventure}")
        self.output.print(f"   Session ID: {self.current_session_id}")

        # Show scenario progress
        if self.scenario_engine.current_events:
            total = len(self.scenario_engine.current_events)
            current = self.scenario_engine.event_index
            self.output.print(f"   Progress: {current}/{total} events")

        # TODO: Show sprite stats, inventory, etc.
        self.output.print(f"\n💡 Use 'STORY CONTINUE' to proceed")

        return True

    def _list_adventures(self) -> bool:
        """List available adventures."""
        if not self.adventure_dir.exists():
            self.output.print(f"📖 No adventures directory: {self.adventure_dir}")
            return True

        adventures = []
        for ext in ['*.upy', '*.json']:
            adventures.extend(self.adventure_dir.glob(ext))

        if not adventures:
            self.output.print(f"📖 No adventures found in {self.adventure_dir}")
            self.output.print(f"\n💡 Create adventure scripts (.upy or .json files)")
            return True

        self.output.print(f"📖 Available Adventures ({len(adventures)}):\n")

        for adventure in sorted(adventures):
            name = adventure.stem
            size = adventure.stat().st_size
            modified = datetime.fromtimestamp(adventure.stat().st_mtime)

            self.output.print(f"  • {name}")
            self.output.print(f"    File: {adventure.name}")
            self.output.print(f"    Size: {size} bytes")
            self.output.print(f"    Modified: {modified.strftime('%Y-%m-%d %H:%M')}")
            self.output.print()

        self.output.print(f"💡 Start with: STORY START <name>")

        return True

    def _continue_adventure(self) -> bool:
        """Continue current adventure."""
        if not self.current_adventure:
            self.output.print("❌ No active adventure")
            self.output.print("💡 Use 'STORY START <name>' to begin")
            return False

        # TODO: Process next event from scenario engine
        self.output.print(f"📖 Continuing: {self.current_adventure}")
        self.output.print("⚠️  Adventure engine integration in progress...")
        self.output.print("💡 Full event processing coming soon")

        return True

    def _make_choice(self, args: list) -> bool:
        """Make a choice in the adventure."""
        if not self.current_adventure:
            self.output.print("❌ No active adventure")
            return False

        if not args:
            self.output.print("❌ Usage: STORY CHOICE <number>")
            return False

        try:
            choice_num = int(args[0])
            # TODO: Process choice through scenario engine
            self.output.print(f"📖 Choice {choice_num} selected")
            self.output.print("⚠️  Choice processing in progress...")
            return True

        except ValueError:
            self.output.print(f"❌ Invalid choice number: {args[0]}")
            return False

    def _rollback(self) -> bool:
        """Rollback last choice."""
        if not self.current_adventure:
            self.output.print("❌ No active adventure")
            return False

        # TODO: Implement rollback through scenario engine
        self.output.print("📖 Rolling back last choice...")
        self.output.print("⚠️  Rollback feature in progress...")

        return True

    def _quit_adventure(self) -> bool:
        """Exit current adventure."""
        if not self.current_adventure:
            self.output.print("❌ No active adventure")
            return False

        self.output.print(f"📖 Exiting adventure: {self.current_adventure}")

        # Prompt to save
        self.output.print("💾 Would you like to save before quitting? (Use STORY SAVE)")

        self.current_adventure = None
        self.current_session_id = None

        self.output.print("✅ Adventure exited")

        return True


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
