"""
uDOS v1.0.0 - Command Router

This is a thin routing layer that delegates commands to specialized handlers:
- AssistantHandler: Assistant/Gemini commands (ASK, ANALYZE, EXPLAIN, etc.)
- FileHandler: File operations (NEW, DELETE, COPY, MOVE, RENAME, SHOW, EDIT, RUN)
- GridHandler: Grid/panel operations (deprecated, provides migration messages)
- MapHandler: Map navigation (MOVE, GOTO, LAYER, VIEW, LOCATE, etc.)
- SystemHandler: System commands (REPAIR, STATUS, REBOOT, DESTROY, DASHBOARD, etc.)

This refactored design keeps the main router under 200 lines while maintaining
all functionality through delegation.

Version: 1.0.0
Author: Fred Porter
"""

import json
from pathlib import Path


class CommandHandler:
    """Main command router - delegates to specialized handlers."""

    def __init__(self, theme='dungeon', commands_file='knowledge/system/commands.json',
                 history=None, connection=None, viewport=None, user_manager=None, command_history=None, logger=None):
        """
        Initialize command handler and load specialized handlers.

        Args:
            theme: Theme name (default: 'dungeon')
            commands_file: Path to commands reference
            history: ActionHistory instance
            connection: ConnectionManager instance
            viewport: Viewport instance
            user_manager: UserManager instance
            command_history: CommandHistory instance
            logger: Logger instance
        """
        # Load theme and commands
        theme_file = f'knowledge/system/themes/{theme.lower()}.json'
        with open(theme_file, 'r') as f:
            theme_data = json.load(f)
            self.lexicon = theme_data.get('TERMINOLOGY', {})

        with open(commands_file, 'r') as f:
            self.commands_data = json.load(f)['COMMANDS']

        # Store core dependencies
        self.history = history
        self.connection = connection
        self.viewport = viewport
        self.user_manager = user_manager
        self.command_history = command_history
        self.logger = logger
        self.reboot_requested = False
        self.current_theme = theme

        # Common kwargs for all handlers
        handler_kwargs = {
            'theme': theme,
            'connection': connection,
            'viewport': viewport,
            'user_manager': user_manager,
            'history': history,
            'command_history': command_history,
            'logger': logger,
            'main_handler': None  # Will be set after initialization
        }

        # Initialize specialized handlers (lazy loading in handlers themselves)
        from core.commands.assistant_handler import AssistantCommandHandler
        from core.commands.file_handler import FileCommandHandler
        from core.commands.grid_handler import GridCommandHandler
        from core.commands.map_handler import MapCommandHandler
        from core.commands.system_handler import SystemCommandHandler
        from core.commands.bank_handler import BankCommandHandler
        from core.commands.cmd_knowledge import cmd_knowledge

        # v1.0.20 - 4-Tier Knowledge Bank handlers
        from core.commands.memory_commands import MemoryCommandHandler
        from core.commands.private_commands import PrivateCommandHandler
        from core.commands.shared_commands import SharedCommandHandler
        from core.commands.community_commands import CommunityCommandHandler
        from core.commands.knowledge_commands import KnowledgeCommandHandler

        # v1.0.20b - Enhanced Mapping & Reference Data System
        from core.commands.tile_handler import TILECommandHandler

        # v1.0.21 - Teletext Display System
        from core.commands.panel_handler import PanelCommandHandler
        from core.commands.guide_handler import GuideHandler
        from core.commands.diagram_handler import DiagramHandler

        self.assistant_handler = AssistantCommandHandler(**handler_kwargs)
        self.file_handler = FileCommandHandler(**handler_kwargs)
        self.grid_handler = GridCommandHandler(**handler_kwargs)
        self.map_handler = MapCommandHandler(**handler_kwargs)
        self.system_handler = SystemCommandHandler(**handler_kwargs)
        self.bank_handler = BankCommandHandler(**handler_kwargs)
        self.knowledge_command = cmd_knowledge

        # v1.0.20 - 4-Tier Memory System handlers
        self.memory_handler = MemoryCommandHandler()
        self.private_handler = PrivateCommandHandler()
        self.shared_handler = SharedCommandHandler()
        self.community_handler = CommunityCommandHandler()
        self.knowledge_v2_handler = KnowledgeCommandHandler()

        # v1.0.20b - TILE Enhanced Mapping handler
        self.tile_handler = TILECommandHandler(**handler_kwargs)

        # v1.0.21 - PANEL Teletext Display handler
        self.panel_handler = PanelCommandHandler(**handler_kwargs)

        # v1.0.21 - GUIDE & DIAGRAM Interactive Knowledge handlers
        self.guide_handler = GuideHandler(viewport=viewport, logger=logger)
        self.diagram_handler = DiagramHandler(viewport=viewport, logger=logger)

        # Now set main_handler reference on all handlers
        for handler in [self.assistant_handler, self.file_handler, self.grid_handler,
                       self.map_handler, self.system_handler, self.bank_handler]:
            handler.main_handler = self

    def get_message(self, key, **kwargs):
        """
        Retrieve a themed message from the lexicon.

        Args:
            key: Message key
            **kwargs: Format arguments

        Returns:
            Formatted message string
        """
        message = self.lexicon.get(key, f"<{key}>")
        return message.format(**kwargs)

    def handle_command(self, ucode, grid, parser):
        """
        Route uCODE command to the appropriate specialized handler.

        Format: [MODULE|COMMAND*PARAM1*PARAM2*...]

        Args:
            ucode: uCODE string to parse and execute
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result message
        """
        try:
            # Parse uCODE format: [MODULE|COMMAND*PARAM1*PARAM2]
            parts = ucode.strip('[]').split('|')
            module = parts[0].upper()
            command_parts = parts[1].split('*')
            command = command_parts[0].upper()
            params = command_parts[1:] if len(command_parts) > 1 else []

            # Route to appropriate handler
            if module == "ASSISTANT" or module == "ASSIST":
                return self.assistant_handler.handle(command, params, grid)

            elif module == "FILE":
                return self.file_handler.handle(command, params, grid, parser)

            elif module == "GRID":
                return self.grid_handler.handle(command, params, grid)

            elif module == "MAP":
                return self.map_handler.handle(command, params, grid)

            elif module == "BANK":
                return self.bank_handler.handle(command, params, grid)

            elif module == "KNOWLEDGE":
                # Legacy KNOWLEDGE commands (v1.0.8)
                return self.knowledge_command(self.user_manager, [command] + params)

            # v1.0.20 - 4-Tier Knowledge Bank & Memory System
            elif module == "MEMORY":
                return self.memory_handler.handle(command, params)

            elif module == "PRIVATE":
                return self.private_handler.handle(command, params)

            elif module == "SHARED":
                return self.shared_handler.handle(command, params)

            elif module == "COMMUNITY":
                return self.community_handler.handle(command, params)

            elif module == "KB" or module == "KNOWLEDGEBANK":
                # New v1.0.20 knowledge bank (use KB to distinguish from legacy)
                return self.knowledge_v2_handler.handle(command, params)

            # v1.0.20b - Enhanced Mapping & Reference Data System
            elif module == "TILE":
                return self.tile_handler.handle(command, ' '.join(params) if params else '', grid)

            # v1.0.21 - Teletext Display System
            elif module == "PANEL":
                return self.panel_handler.handle(command, params, grid)

            # v1.0.21 - Interactive Knowledge Viewers
            elif module == "GUIDE":
                return self.guide_handler.handle(command, params)

            elif module == "DIAGRAM":
                return self.diagram_handler.handle(command, params)

            elif module == "SYSTEM":
                # System handler needs access to reboot flag
                result = self.system_handler.handle(command, params, grid, parser)
                # Check if reboot was requested
                if hasattr(self.system_handler, 'reboot_requested'):
                    self.reboot_requested = self.system_handler.reboot_requested
                return result

            else:
                return self.get_message("ERROR_UNKNOWN_MODULE", module=module)

        except IndexError:
            return self.get_message("ERROR_INVALID_UCODE_FORMAT",
                                   ucode=ucode,
                                   error="Missing module or command")
        except Exception as e:
            return self.get_message("ERROR_INVALID_UCODE_FORMAT",
                                   ucode=ucode,
                                   error=str(e))


# Example Usage (for testing)
if __name__ == '__main__':
    from core.uDOS_grid import Grid
    from core.uDOS_parser import Parser

    grid = Grid()
    parser = Parser()
    handler = CommandHandler()

    print("="*60)
    print("uDOS v1.0.0 Command Router Test")
    print("="*60)
    print()

    # Test system commands
    print("--- SYSTEM COMMANDS ---")
    print(handler.handle_command("[SYSTEM|STATUS]", grid, parser))
    print()

    # Test file commands
    print("--- FILE COMMANDS ---")
    print(handler.handle_command("[FILE|SHOW*README.MD]", grid, parser))
    print()

    # Test assistant commands
    print("--- ASSISTANT COMMANDS ---")
    print(handler.handle_command("[ASSISTANT|ASK*What is uDOS?]", grid, parser))
    print()

    # Test map commands
    print("--- MAP COMMANDS ---")
    print(handler.handle_command("[MAP|STATUS]", grid, parser))
    print()

    print("="*60)
    print("✅ Command router test complete")
    print("="*60)
