"""
Command Dispatcher

Routes user commands to appropriate handlers.
Manages command handlers including system, NPC, and dev mode.
"""

from typing import Dict, List, Any, Optional
from core.commands import (
    MapHandler,
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
    ShakedownHandler,
    RepairHandler,
    DevModeHandler,
    NPCHandler,
    DialogueEngine,
    TalkHandler,
    ConfigHandler,
    ProviderHandler,
    PatternHandler,
    BinderHandler,
    RunHandler,
    DatasetHandler,
    FileEditorHandler,
    MaintenanceHandler,
    StoryHandler,
    SetupHandler,
    UIDHandler,
    LogsHandler,
    HotkeyHandler,
    ReloadHandler,
    RestartHandler,
    DestroyHandler,
    UserHandler,
    UndoHandler,
    MigrateHandler,
    SeedHandler,
    HotkeyHandler,
    IntegrationHandler,
)


class CommandDispatcher:
    """Route commands to handlers"""

    def __init__(self):
        """Initialize command dispatcher with all handlers including NPC system"""
        # Initialize NPC system (shared instances)
        self.npc_handler = NPCHandler()
        self.dialogue_engine = DialogueEngine()
        self.talk_handler = TalkHandler(self.npc_handler, self.dialogue_engine)

        file_editor = FileEditorHandler()
        maintenance = MaintenanceHandler()
        
        # Import FileHandler here to avoid circular import
        # (FileHandler → OutputToolkit → ucode → dispatcher → FileHandler)
        from core.commands.file_handler import FileHandler

        self.handlers: Dict[str, Any] = {
            # Navigation (4)
            "MAP": MapHandler(),
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
            "SHAKEDOWN": ShakedownHandler(),
            "REPAIR": RepairHandler(),
            "RESTART": RestartHandler(),  # Unified restart/reboot
            "REBOOT": RestartHandler(),  # Alias for RESTART --repair
            "RELOAD": ReloadHandler(),  # Control hot reload watcher
            "SETUP": SetupHandler(),
            "UID": UIDHandler(),  # User ID management
            "PATTERN": PatternHandler(),
            "DEV MODE": DevModeHandler(),
            "DEV": DevModeHandler(),  # Shortcut for DEV MODE
            "LOGS": LogsHandler(),  # View unified logs
            "HOTKEYS": HotkeyHandler(),
            "HOTKEY": HotkeyHandler(),
            # User Management (2)
            "USER": UserHandler(),  # User profiles and permissions
            # Cleanup/Reset (2)
            "DESTROY": DestroyHandler(),  # System cleanup with data wipe options
            "UNDO": UndoHandler(),  # Simple undo via restore from backup
            # Data Migration (1)
            "MIGRATE": MigrateHandler(),  # SQLite migration for location data
            # Seed Installation (1)
            "SEED": SeedHandler(),  # Framework seed data installer
            # NPC & Dialogue (3)
            "NPC": self.npc_handler,
            "TALK": self.talk_handler,
            "REPLY": self.talk_handler,
            # Wizard Management (2)
            "CONFIG": ConfigHandler(),
            "PROVIDER": ProviderHandler(),
            "INTEGRATION": IntegrationHandler(),
            # Binder (Core)
            "BINDER": BinderHandler(),
            # Runtime (Story format)
            "STORY": StoryHandler(),
            "RUN": RunHandler(),
            # Data
            "DATASET": DatasetHandler(),
            # File operations
            "FILE": FileHandler(),  # Phase 2: Workspace picker integration
            "NEW": file_editor,
            "EDIT": file_editor,
            # Maintenance
            "BACKUP": maintenance,
            "RESTORE": maintenance,
            "TIDY": maintenance,
            "CLEAN": maintenance,
            "COMPOST": maintenance,
        }

        self.file_handler = file_editor
        self.save_handler = SaveHandler()
        self.load_handler = LoadHandler()

    def dispatch(
        self, command_text: str, grid: Any = None, parser: Any = None
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
            return {"status": "error", "message": "Empty command"}

        cmd_name = parts[0].upper()
        cmd_params = parts[1:]

        # Get handler
        handler = self.handlers.get(cmd_name)
        if cmd_name in {"SAVE", "LOAD"}:
            if cmd_params and cmd_params[0].lower() in {"game", "state"}:
                handler = self.save_handler if cmd_name == "SAVE" else self.load_handler
                cmd_params = cmd_params[1:]
            else:
                handler = self.file_handler
        if not handler:
            return {
                "status": "error",
                "message": f"Unknown command: {cmd_name}",
                "suggestion": "Type HELP for command list",
            }

        # Execute handler
        try:
            result = handler.handle(cmd_name, cmd_params, grid, parser)
            return result
        except Exception as e:
            return {
                "status": "error",
                "message": f"Command failed: {str(e)}",
                "command": cmd_name,
            }

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
