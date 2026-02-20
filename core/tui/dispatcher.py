"""
Command Dispatcher

Routes user commands to appropriate handlers.
Manages command handlers including system, NPC, and dev mode.
"""

from typing import Dict, List, Any, Optional

from core.services.error_contract import CommandError
from core.services.logging_manager import get_logger
from core.commands import (
    MapHandler,
    GridHandler,
    AnchorHandler,
    PanelHandler,
    GotoHandler,
    FindHandler,
    TellHandler,
    BagHandler,
    GrabHandler,
    SpawnHandler,
    SaveHandler,
    LoadHandler,
    HelpHandler,
    HealthHandler,
    VerifyHandler,
    RepairHandler,
    DevModeHandler,
    NPCHandler,
    DialogueEngine,
    TalkHandler,
    ConfigHandler,
    WizardHandler,
    EmpireHandler,
    SonicHandler,
    MusicHandler,
    BinderHandler,
    RunHandler,
    FileEditorHandler,
    MaintenanceHandler,
    StoryHandler,
    ReadHandler,
    SetupHandler,
    UIDHandler,
    TokenHandler,
    GhostHandler,
    LogsHandler,
    RestartHandler,
    DestroyHandler,
    UserHandler,
    PlayHandler,
    RuleHandler,
    UndoHandler,
    MigrateHandler,
    SeedHandler,
    SchedulerHandler,
    ScriptHandler,
    ThemeHandler,
    SkinHandler,
    ViewportHandler,
    DrawHandler,
    WorkspaceHandler,
)


class CommandDispatcher:
    """Route commands to handlers"""

    def __init__(self):
        """Initialize command dispatcher with all handlers including NPC system"""
        self.logger = get_logger("command-dispatcher")

        # Initialize NPC system (shared instances)
        self.npc_handler = NPCHandler()
        self.dialogue_engine = DialogueEngine()
        self.talk_handler = TalkHandler(self.npc_handler, self.dialogue_engine)

        file_editor = FileEditorHandler()
        maintenance = MaintenanceHandler()
        workspace = WorkspaceHandler()

        # Import FileHandler here to avoid circular import
        # (FileHandler → OutputToolkit → ucode → dispatcher → FileHandler)
        from core.commands.file_handler import FileHandler
        from core.commands.library_handler import LibraryHandler

        play = PlayHandler()
        self.handlers: Dict[str, Any] = {
            # Navigation (5)
            "MAP": MapHandler(),
            "ANCHOR": AnchorHandler(),
            "GRID": GridHandler(),
            "PANEL": PanelHandler(),
            "GOTO": GotoHandler(),
            "FIND": FindHandler(),
            # Information (2)
            "TELL": TellHandler(),
            "HELP": HelpHandler(),
            # Game State (5)
            "BAG": BagHandler(),
            "GRAB": GrabHandler(),
            "SPAWN": SpawnHandler(),
            "SAVE": SaveHandler(),
            "LOAD": LoadHandler(),
            # System (9)
            "HEALTH": HealthHandler(),
            "VERIFY": VerifyHandler(),
            "REPAIR": RepairHandler(),
            "REBOOT": RestartHandler(),  # Hot reload + TUI restart
            "SETUP": SetupHandler(),
            "UID": UIDHandler(),  # User ID management
            "TOKEN": TokenHandler(),  # Token generation utilities
            "GHOST": GhostHandler(),  # Ghost mode status/policy
            "SONIC": SonicHandler(),
            "MUSIC": MusicHandler(),
            "DEV": DevModeHandler(),  # Shortcut for DEV MODE
            "LOGS": LogsHandler(),  # View unified logs
            "SCHEDULER": SchedulerHandler(),  # Wizard task scheduler
            "SCRIPT": ScriptHandler(),  # System script runner
            "THEME": ThemeHandler(),  # TUI message theme manager
            "SKIN": SkinHandler(),  # Wizard GUI skin manager
            "VIEWPORT": ViewportHandler(),  # Measure viewport size
            "DRAW": DrawHandler(),  # Viewport-aware ASCII demo panels
            # User Management (2)
            "USER": UserHandler(),  # User profiles and permissions
            "PLAY": play,  # Unified gameplay + conditional play options
            "RULE": RuleHandler(),  # Conditional IF/THEN gameplay automation rules
            # Cleanup/Reset (2)
            "DESTROY": DestroyHandler(),  # System cleanup with data wipe options
            "UNDO": UndoHandler(),  # Simple undo via restore from backup
            # Data Migration (1)
            "MIGRATE": MigrateHandler(),  # SQLite migration for location data
            # Seed Installation (1)
            "SEED": SeedHandler(),  # Framework seed data installer
            # NPC & Dialogue (3)
            "NPC": self.npc_handler,
            "SEND": self.talk_handler,
            # Wizard Management (3)
            "CONFIG": ConfigHandler(),
            "WIZARD": WizardHandler(),
            "EMPIRE": EmpireHandler(),
            # Binder (Core)
            "BINDER": BinderHandler(),
            # Workspace-aware file operations
            "PLACE": workspace,
            # Runtime (Story format)
            "STORY": StoryHandler(),
            "RUN": RunHandler(),
            "READ": ReadHandler(),
            # File operations
            "FILE": FileHandler(file_editor=file_editor),  # Phase 2: Workspace picker integration
            # Maintenance
            "BACKUP": maintenance,
            "RESTORE": maintenance,
            "TIDY": maintenance,
            "CLEAN": maintenance,
            "COMPOST": maintenance,
            # Library management
            "LIBRARY": LibraryHandler(),
        }

        self.file_handler = file_editor
        self.save_handler = SaveHandler()
        self.load_handler = LoadHandler()

    def dispatch(
        self,
        command_text: str,
        grid: Any = None,
        parser: Any = None,
        game_state: Any = None,
    ) -> Dict[str, Any]:
        """
        Parse command and route to handler

        Args:
            command_text: User input command (e.g., "FIND tokyo")
            grid: TUI Grid object (can be None for now)
            parser: SmartPrompt parser (can be None for now)

        Returns:
            Dict with status, message, and command-specific data
        """
        # Parse command
        parts = command_text.strip().split()
        if not parts:
            raise CommandError(
                code="ERR_COMMAND_EMPTY",
                message="Empty command",
                recovery_hint="Type HELP to see available commands",
                level="INFO",
            )

        cmd_name = parts[0].upper()
        cmd_params = parts[1:]

        if cmd_name in {"NEW", "EDIT"}:
            cmd_params = [cmd_name] + cmd_params
            cmd_name = "FILE"

        # Get handler
        handler = self.handlers.get(cmd_name)
        if cmd_name in {"SAVE", "LOAD"}:
            if cmd_params and cmd_params[0].lower() == "--state":
                handler = self.save_handler if cmd_name == "SAVE" else self.load_handler
                cmd_params = cmd_params[1:]
            else:
                handler = self.file_handler
        if not handler:
            raise CommandError(
                code="ERR_COMMAND_NOT_FOUND",
                message=f"Unknown command: {cmd_name}",
                recovery_hint="Type HELP for command list",
                level="INFO",
            )

        # Ghost Mode guard for destructive commands
        try:
            from core.commands.ghost_mode_guard import ghost_mode_block

            block = ghost_mode_block(cmd_name, cmd_params)
            if block:
                return block
        except Exception:
            pass

        # Sync handler state from shared game state
        if game_state is not None:
            self._tick_gameplay_state(game_state)
            self._sync_handler_state(handler, game_state)

        # Execute handler
        try:
            result = handler.handle(cmd_name, cmd_params, grid, parser)
            if game_state is not None:
                self._sync_game_state_from_handler(handler, game_state)
            return result
        except CommandError as exc:
            exc.log(self.logger)
            return {
                "status": "error",
                "code": exc.code,
                "message": exc.message,
                "recovery_hint": exc.recovery_hint,
                "command": cmd_name,
            }
        except Exception as exc:
            error = CommandError(
                code="ERR_RUNTIME_UNEXPECTED",
                message=f"Command failed: {str(exc)}",
                recovery_hint="Run HEALTH to diagnose or retry the command",
                cause=exc,
                level="ERROR",
            )
            error.log(self.logger)
            return {
                "status": "error",
                "code": error.code,
                "message": error.message,
                "recovery_hint": error.recovery_hint,
                "command": cmd_name,
            }

    def _sync_handler_state(self, handler: Any, game_state: Any) -> None:
        """Push shared game state into a handler."""
        if not hasattr(handler, "set_state"):
            return
        handler.set_state("current_location", getattr(game_state, "current_location", None))
        handler.set_state("inventory", getattr(game_state, "inventory", None))
        handler.set_state("discovered_locations", getattr(game_state, "discovered_locations", None))
        handler.set_state("player_stats", getattr(game_state, "player_stats", None))
        handler.set_state("player_id", getattr(game_state, "player_id", None))

    def _tick_gameplay_state(self, game_state: Any) -> None:
        """Apply external gameplay events before command execution."""
        try:
            from core.services.gameplay_service import get_gameplay_service
            from core.services.user_service import get_user_manager

            current_user = get_user_manager().current()
            if not current_user:
                return
            tick = get_gameplay_service().tick(current_user.username)
            stats = tick.get("stats")
            if isinstance(stats, dict):
                merged = dict(getattr(game_state, "player_stats", {}) or {})
                merged.update(stats)
                game_state.player_stats = merged
        except Exception:
            return

    def _sync_game_state_from_handler(self, handler: Any, game_state: Any) -> None:
        """Pull updated state from a handler into shared game state."""
        if not hasattr(handler, "get_state"):
            return
        current_location = handler.get_state("current_location")
        if current_location:
            game_state.current_location = current_location
        inventory = handler.get_state("inventory")
        if inventory is not None:
            game_state.inventory = inventory
        discovered = handler.get_state("discovered_locations")
        if discovered is not None:
            game_state.discovered_locations = discovered
        player_stats = handler.get_state("player_stats")
        if player_stats is not None:
            game_state.player_stats = player_stats
        player_id = handler.get_state("player_id")
        if player_id:
            game_state.player_id = player_id

    def get_command_list(self) -> List[str]:
        """Get list of available commands"""
        return sorted(self.handlers.keys())

    def get_command_help(self, cmd_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get help for specific command or all commands

        Args:
            cmd_name: Command name (optional)

        Returns:
            Dict with help information
        """
        if cmd_name:
            # Show specific command help
            handler = self.handlers.get(cmd_name.upper())
            if handler:
                return {
                    "status": "success",
                    "command": cmd_name.upper(),
                    "help": handler.__doc__ or "No help available",
                }
            else:
                return {"status": "error", "message": f"Unknown command: {cmd_name}"}
        else:
            # Show all commands
            commands = self.get_command_list()
            return {"status": "success", "commands": commands, "count": len(commands)}


# Module-level singleton and helper functions for easier access
_dispatcher_instance: Optional[CommandDispatcher] = None


def get_dispatcher() -> CommandDispatcher:
    """Get or create the global dispatcher instance."""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = CommandDispatcher()
    return _dispatcher_instance


def create_handlers() -> Dict[str, Any]:
    """Create and return all command handlers dict."""
    return get_dispatcher().handlers


def get_handler(cmd_name: str) -> Optional[Any]:
    """Get a specific handler by command name."""
    return get_dispatcher().handlers.get(cmd_name.upper())
