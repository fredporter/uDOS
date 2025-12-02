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
from core.services.theme.theme_loader import load_theme


class CommandHandler:
    """Main command router - delegates to specialized handlers."""

    def __init__(self, theme='dungeon', commands_file='core/data/commands.json',
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
        # Load theme and commands (merged with any user overrides)
        theme_data = load_theme(theme, root_path=Path(__file__).parent.parent)
        self.lexicon = theme_data.get('TERMINOLOGY', {})
        self.messages = theme_data.get('MESSAGES', {})

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
        from core.commands.system_handler import SystemCommandHandler

        # Play extension (optional) - load if available
        try:
            from extensions.play.commands.map_handler import MapCommandHandler
            self._play_available = True
        except ImportError:
            MapCommandHandler = None
            self._play_available = False

        # v1.0.20 - 4-Tier Knowledge Bank handlers
        from core.commands.memory_commands import MemoryCommandHandler
        from core.commands.private_commands import PrivateCommandHandler
        from core.commands.shared_commands import SharedCommandHandler
        from core.commands.community_commands import CommunityCommandHandler
        # Note: KB command now redirects to GUIDE handler (KnowledgeCommandHandler removed in v2.0.0)

        # v1.0.20b - Enhanced Mapping & Reference Data System
        from core.commands.tile_handler import TILECommandHandler

        # v1.0.21 - Teletext Display System
        from core.commands.panel_handler import PanelCommandHandler
        from core.commands.guide_handler import GuideHandler
        from core.commands.diagram_handler import DiagramHandler

        # v1.0.33 - Barter Economy System
        from core.commands.barter_commands import BarterCommandHandler

        # v1.1.0 - User Feedback System
        from core.commands.user_handler import UserCommandHandler

        # v1.0.32 - Tree Structure Generator
        from core.commands.tree_handler import TreeHandler

        # v1.5.0 - PEEK Data Collection System
        from core.commands.peek_handler import PeekHandler

        # v2.0 - Sandbox Management System
        from core.commands.sandbox_handler import SandboxHandler

        # v1.1.2 - Mission Control & Workflow Automation
        from core.commands.mission_handler import handle_mission_command
        from core.commands.schedule_handler import handle_schedule_command
        from core.commands.workflow_handler import handle_workflow_command
        from core.commands.resource_handler import handle_resource_command

        self.assistant_handler = AssistantCommandHandler(**handler_kwargs)
        self.file_handler = FileCommandHandler(**handler_kwargs)
        self.map_handler = MapCommandHandler(**handler_kwargs) if MapCommandHandler else None
        self.system_handler = SystemCommandHandler(**handler_kwargs)
        # Note: bank_handler removed in v2.0.0 - use GUIDE for knowledge access

        # v1.0.20 - 4-Tier Memory System handlers
        self.memory_handler = MemoryCommandHandler()
        self.private_handler = PrivateCommandHandler()
        self.shared_handler = SharedCommandHandler()
        self.community_handler = CommunityCommandHandler()
        # Note: knowledge_v2_handler removed in v2.0.0 - KB commands redirect to GUIDE

        # v1.0.20b - TILE Enhanced Mapping handler
        self.tile_handler = TILECommandHandler(**handler_kwargs)

        # v1.0.21 - PANEL Teletext Display handler
        self.panel_handler = PanelCommandHandler(**handler_kwargs)

        # v1.0.21 - GUIDE & DIAGRAM Interactive Knowledge handlers
        self.guide_handler = GuideHandler(viewport=viewport, logger=logger)
        self.diagram_handler = DiagramHandler(viewport=viewport, logger=logger)

        # v1.1.4 - DRAW Diagram Generation handler (ASCII/Teletext graphics)
        from core.commands.draw_handler import DrawHandler
        self.draw_handler = DrawHandler(viewport=viewport, logger=logger)

        # v1.1.6 - GENERATE handler (unified generation system via Nano Banana)
        from core.commands.generate_handler import GenerateHandler
        self.generate_handler = GenerateHandler(viewport=viewport, logger=logger)

        # v1.1.9 - SPRITE & OBJECT handlers (Round 1 Variable System)
        from core.commands.sprite_handler import SpriteHandler
        from core.commands.object_handler import ObjectHandler

        # v1.1.14 - CHECKLIST handler (Task Management System)
        from core.commands.checklist_handler import ChecklistHandler
        self.checklist_handler = ChecklistHandler(config=config)

        # Get variable_manager from components (if available)
        components = {
            'config': None,
            'variable_manager': None,
            'logger': logger
        }
        self.sprite_handler = SpriteHandler(components)
        self.object_handler = ObjectHandler(components)

        # v1.1.9+ - STORY handler (Round 2 Adventure System)
        from core.commands.story_handler import StoryHandler
        story_components = {
            'config': None,
            'logger': logger,
            'output': viewport
        }
        self.story_handler = StoryHandler(story_components)

        # v1.1.6 - LOGS Command handler (Logging System Management)
        from core.commands.logs_handler import create_logs_handler
        self.logs_handler = create_logs_handler()

        # v1.0.33 - BARTER Economy handler
        self.barter_handler = BarterCommandHandler()

        # v1.1.0 - User Feedback handler
        self.user_handler = UserCommandHandler(**handler_kwargs)

        # v1.0.32 - TREE Structure handler
        self.tree_handler = TreeHandler()

        # v1.5.0 - PEEK Data Collection handler
        self.peek_handler = PeekHandler(**handler_kwargs)

        # v2.0 - Sandbox Management handler
        self.sandbox_handler = SandboxHandler()

        # v1.1.8 - EXTENSION Management handler (Extension Polish)
        from core.commands.extension_handler import create_extension_handler
        self.extension_handler = create_extension_handler(viewport=viewport, logger=logger)

        # Now set main_handler reference on all handlers (v2.0.0: removed bank_handler)
        for handler in [self.assistant_handler, self.file_handler,
                       self.system_handler]:
            handler.main_handler = self

        # Set main_handler on map_handler if available
        if self.map_handler:
            self.map_handler.main_handler = self

    def get_message(self, key, **kwargs):
        """
        Retrieve a themed message from the lexicon.

        Args:
            key: Message key
            **kwargs: Format arguments

        Returns:
            Formatted message string
        """
        # Prefer full message templates, then terminology tokens, then fallback
        template = None
        if hasattr(self, 'messages') and key in self.messages:
            template = self.messages.get(key)
        elif key in self.lexicon:
            template = self.lexicon.get(key)
        else:
            template = f"<{key}>"

        try:
            # Format with provided kwargs
            return template.format(**kwargs)
        except KeyError as e:
            # Missing template variable - provide better error context
            missing_var = str(e).strip("'")
            if self.logger:
                self.logger.warning(f"Template '{key}' missing variable: {missing_var}")
            # Return template with visible placeholder instead of empty
            return template.replace(f"{{{missing_var}}}", f"<{missing_var.upper()}>")
        except Exception as e:
            # Other formatting errors - log and return template as-is
            if self.logger:
                self.logger.warning(f"Error formatting message '{key}': {e}")
            return template

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

            # ROLE shortcut to CONFIG ROLE
            elif module == "ROLE":
                return self.system_handler._handle_config_role([])

            elif module == "GRID":
                return ("❌ GRID commands have been removed in uDOS v1.0.32\n\n"
                       "The panel system has been simplified. Commands now work\n"
                       "directly with files and the terminal output.\n\n"
                       "💡 Alternatives:\n"
                       "   • Use TREE to view repository structure\n"
                       "   • Use EDIT to edit files\n"
                       "   • Use SHOW to view files\n"
                       "   • Use PANEL for teletext UI")

            elif module == "MAP":
                if self.map_handler:
                    return self.map_handler.handle(command, params, grid)
                else:
                    return ("❌ MAP commands require Play extension\n"
                           "💡 Install: POKE START play")

            elif module == "BANK":
                # BANK handler removed in v2.0.0 - redirect to GUIDE
                return self.guide_handler.handle(command, params)

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
                # KB handler removed in v2.0.0 - redirect to GUIDE
                return self.guide_handler.handle(command, params)

            # v1.0.20b - Enhanced Mapping & Reference Data System
            elif module == "TILE":
                return self.tile_handler.handle(command, ' '.join(params) if params else '', grid)

            # v1.0.33 - Barter Economy System
            elif module == "BARTER" or module == "OFFER" or module == "REQUEST" or module == "TRADE":
                # Route OFFER, REQUEST, TRADE directly to barter handler
                if module in ["OFFER", "REQUEST", "TRADE"]:
                    return self.barter_handler.handle(module, params)
                else:
                    return self.barter_handler.handle(command, params)

            # v1.1.9 - SPRITE & OBJECT Variable System (Round 1)
            elif module == "SPRITE":
                success = self.sprite_handler.handle([command] + params)
                return "✅ Command executed" if success else "❌ Command failed"

            elif module == "OBJECT":
                success = self.object_handler.handle([command] + params)
                return "✅ Command executed" if success else "❌ Command failed"

            # v1.1.9+ - STORY Adventure System (Round 2)
            elif module == "STORY":
                return self.story_handler.handle(command, params)

            # v1.0.21 - Teletext Display System
            elif module == "PANEL" or module == "UI":
                return self.panel_handler.handle(command, params, grid)

            # v1.0.21 - Interactive Knowledge Viewers
            elif module == "GUIDE":
                return self.guide_handler.handle(command, params)

            elif module == "DIAGRAM":
                return self.diagram_handler.handle(command, params)

            # v1.1.14 - Checklist Task Management
            elif module == "CHECKLIST":
                return self.checklist_handler.handle(command, params)

            # v1.1.4 - DRAW Diagram Generation (ASCII/Teletext graphics)
            elif module == "DRAW":
                return self.draw_handler.handle(command, params)

            # v1.1.6 - GENERATE Unified Generation System (Nano Banana pipeline)
            elif module == "GENERATE":
                return self.generate_handler.handle_command(params)

            # v1.1.5 - SVG Graphics Extension (REMOVED in v1.1.5.3 - use GENERATE SVG)
            elif module == "SVG":
                return (
                    "❌ SVG command removed in v1.1.5.3\n\n"
                    "Use: GENERATE SVG <description>\n\n"
                    "Examples:\n"
                    "  GENERATE SVG water purification flowchart\n"
                    "  GENERATE SVG solar still diagram\n\n"
                    "The GENERATE command provides better quality via Nano Banana.\n"
                )

            # v1.1.6 - LOGS System Management
            elif module == "LOGS":
                return self.logs_handler.handle(command, params)

            # v1.0.32 & v1.1.7 - POKE Extension Management & Online Features
            elif module == "POKE" or module == "OUTPUT" or module == "SERVER":
                # Check if this is POKE Online extension command
                if params and params[0].upper() in ["TUNNEL", "SHARE", "GROUP"]:
                    # Try to load POKE Online extension
                    try:
                        from extensions.cloud.poke_commands import handle_poke_command
                        return handle_poke_command(params)
                    except ImportError:
                        return ("❌ POKE Online extension not available\n"
                               "💡 Install the extension to use tunnel/sharing features")
                    except Exception as e:
                        return f"❌ POKE Online error: {e}"
                else:
                    # Delegate to system handler for extension management
                    return self.system_handler.handle_output(params, self.grid, self.parser)

            # v1.1.0 - User Feedback System
            elif module == "USER":
                return self.user_handler.handle(command, params, grid)

            # v1.0.32 - TREE Directory Structure Generator
            elif module == "TREE":
                return self.tree_handler.handle(params)

            # v1.5.0 - PEEK Data Collection System
            elif module == "PEEK":
                return self.peek_handler.handle(command, params, grid, parser)

            # v2.0 - Sandbox Management System
            elif module == "SANDBOX":
                return self.sandbox_handler.handle(command, params)

            # v1.1.8 - EXTENSION Management (Extension Polish)
            elif module == "EXTENSION" or module == "EXT":
                return self.extension_handler.handle_command([command] + params)

            # v1.1.2 - Mission Control & Workflow Automation
            elif module == "MISSION":
                # Reconstruct command line for mission handler
                command_line = f"MISSION {command}" + (' ' + ' '.join(params) if params else '')
                return handle_mission_command(command_line)

            # v1.1.2 - Scheduler System
            elif module == "SCHEDULE":
                # Reconstruct command line for schedule handler
                command_line = f"SCHEDULE {command}" + (' ' + ' '.join(params) if params else '')
                return handle_schedule_command(command_line)

            # v1.1.2 - Workflow Automation
            elif module == "WORKFLOW":
                from core.config import Config
                config = Config()
                return handle_workflow_command(command, params, config)

            # v1.1.2 - Resource Management
            elif module == "RESOURCE":
                # If no command provided, show help
                if not command or command.strip() == '':
                    result = handle_resource_command('HELP')
                    return result.get('output', str(result))

                # Parse params into kwargs for resource handler
                kwargs = {'provider': params[0] if params else None}

                # Handle --flag arguments
                i = 0
                while i < len(params):
                    param = params[i]
                    if param.startswith('--'):
                        # Flag with value
                        flag_name = param[2:]  # Remove --
                        if i + 1 < len(params) and not params[i + 1].startswith('--'):
                            kwargs[flag_name] = params[i + 1]
                            i += 2
                        else:
                            kwargs[flag_name] = True
                            i += 1
                    elif not param.startswith('--') and 'mission_id' not in kwargs:
                        # First non-flag param is mission_id
                        kwargs['mission_id'] = param
                        i += 1
                    else:
                        i += 1

                result = handle_resource_command(command, **kwargs)
                return result.get('output', str(result))

            elif module == "SYSTEM":
                # System handler needs access to reboot flag
                result = self.system_handler.handle(command, params, grid, parser)
                # Check if reboot was requested
                if hasattr(self.system_handler, 'reboot_requested'):
                    self.reboot_requested = self.system_handler.reboot_requested
                return result

            else:
                return self.get_message("ERROR_UNKNOWN_MODULE", module=module)

        except IndexError as e:
            return self.get_message("ERROR_INVALID_UCODE_FORMAT",
                                   ucode=ucode,
                                   error=f"Missing module or command: {str(e)}")
        except Exception as e:
            return self.get_message("ERROR_INVALID_UCODE_FORMAT",
                                   ucode=ucode,
                                   error=str(e))


# Example Usage (for testing)
if __name__ == '__main__':
    from core.services.uDOS_grid import Grid
    from core.interpreters.uDOS_parser import Parser

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
