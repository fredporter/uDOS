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

    def __init__(self, theme='dungeon', commands_file='data/system/commands.json',
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
        theme_file = f'data/themes/{theme.lower()}.json'
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

        self.assistant_handler = AssistantCommandHandler(**handler_kwargs)
        self.file_handler = FileCommandHandler(**handler_kwargs)
        self.grid_handler = GridCommandHandler(**handler_kwargs)
        self.map_handler = MapCommandHandler(**handler_kwargs)
        self.system_handler = SystemCommandHandler(**handler_kwargs)
        self.bank_handler = BankCommandHandler(**handler_kwargs)

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
