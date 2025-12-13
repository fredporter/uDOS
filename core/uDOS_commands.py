"""
uDOS v1.2.21 - Command Router

Thin routing layer that delegates commands to specialized handlers:
- AssistantHandler: AI commands (ASK, ANALYZE)
- FileHandler: File operations (NEW, DELETE, COPY, MOVE, SHOW, EDIT)
- MapHandler: Navigation (MOVE, GOTO, LAYER, VIEW, LOCATE)
- SystemHandler: System commands (REPAIR, STATUS, REBOOT)

Clean modular design with no deprecated patterns or backward compatibility.
"""

import json
from pathlib import Path
from core.services.theme.theme_loader import load_theme

# Import mission/workflow handlers at module level for use in execute_ucode
from core.commands.mission_handler import handle_mission_command
from core.commands.schedule_handler import handle_schedule_command
from core.commands.workflow_handler import handle_workflow_command


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

        # Memory System handlers
        from core.commands.memory_commands import MemoryCommandHandler
        from core.commands.private_commands import PrivateCommandHandler
        from core.commands.shared_commands import SharedCommandHandler
        from core.commands.community_commands import CommunityCommandHandler

        # Core system handlers
        from core.commands.tile_handler import TILECommandHandler
        from core.commands.panel_handler import PanelCommandHandler
        from core.commands.docs_unified_handler import DocsUnifiedHandler
        from core.commands.barter_commands import BarterCommandHandler

        # Core UI & System Imports
        from core.commands.user_handler import UserCommandHandler
        from core.commands.color_handler import handle_color
        from core.commands.tree_handler import TreeHandler
        from core.commands.peek_handler import PeekHandler
        from core.commands.sandbox_handler import SandboxHandler
        from core.commands.cloud_handler import CloudHandler

        self.assistant_handler = AssistantCommandHandler(**handler_kwargs)
        self.file_handler = FileCommandHandler(**handler_kwargs)
        self.map_handler = MapCommandHandler(**handler_kwargs) if MapCommandHandler else None
        self.system_handler = SystemCommandHandler(**handler_kwargs)
        self.cloud_handler = CloudHandler(**handler_kwargs)


        # Memory System Handlers
        self.memory_handler = MemoryCommandHandler()
        self.private_handler = PrivateCommandHandler()
        self.shared_handler = SharedCommandHandler()
        self.community_handler = CommunityCommandHandler()


        # Core System Handlers
        self.tile_handler = TILECommandHandler(**handler_kwargs)
        self.panel_handler = PanelCommandHandler(**handler_kwargs)
        self.docs_handler = DocsUnifiedHandler(viewport=viewport, logger=logger)

        # Content Generation Handlers
        from core.commands.make_handler import MakeHandler
        self.make_handler = MakeHandler(**handler_kwargs)
        
        from core.commands.ok_handler import create_ok_handler
        self.ok_handler = create_ok_handler(**handler_kwargs)
        
        from core.commands.prompt_handler import PromptHandler
        self.prompt_handler = PromptHandler()

        # Diagram & Integration Handlers
        from core.commands.mermaid_handler import MermaidHandler
        self.mermaid_handler = MermaidHandler(viewport=viewport, logger=logger)
        
        try:
            from extensions.core.typora_diagrams.handler import get_handler as get_typora_handler
            self.typora_handler = get_typora_handler(viewport=viewport, logger=logger)
        except ImportError:
            self.typora_handler = None
            if logger:
                logger.log('EVENT', "Typora diagrams extension not available")

        # Game Object Handlers
        from core.commands.sprite_handler import SpriteHandler
        from core.commands.object_handler import ObjectHandler

        # Task Management Handlers
        from core.commands.checklist_handler import ChecklistHandler
        self.checklist_handler = ChecklistHandler(config=None)
        
        # Inbox Processing Handler
        from core.commands.inbox_handler import InboxHandler
        self.inbox_handler = InboxHandler(**handler_kwargs)


        from core.commands.archive_handler import ArchiveHandler
        self.archive_handler = ArchiveHandler(**handler_kwargs)
        
        # Time/Date Handler (v1.2.22)
        from core.commands.time_handler import create_time_handler
        self.time_handler = create_time_handler(**handler_kwargs)

        # JSON Viewer/Editor Handler (v1.2.22)
        from core.commands.json_handler import create_json_handler
        self.json_handler = create_json_handler(**handler_kwargs)

        from core.commands.backup_handler import create_handler as create_backup_handler
        self.backup_handler = create_backup_handler(viewport=viewport, logger=logger)


        from core.commands.undo_handler import create_handler as create_undo_handler
        self.undo_handler = create_undo_handler(viewport=viewport, logger=logger)
        
        
        # Content & Build Handlers
        from core.commands.clone_handler import CloneHandler
        self.clone_handler = CloneHandler(**handler_kwargs)
        

        from core.commands.build_handler import BuildHandler
        self.build_handler = BuildHandler(**handler_kwargs)
        
        # v1.2.15 - TUI Management
        from core.commands.tui_handler import TUIHandler
        self.tui_handler = TUIHandler()  # Will set TUI controller later


        from core.commands.gmail_handler import handle_gmail_command
        self.gmail_handler = handle_gmail_command


        from core.commands.session_handler import SessionHandler
        self.session_handler = SessionHandler(**handler_kwargs)

        # Get variable_manager from components (if available)
        components = {
            'config': None,
            'variable_manager': None,
            'logger': logger
        }
        self.sprite_handler = SpriteHandler(components)
        self.object_handler = ObjectHandler(components)

        # Adventure & Game Handlers
        from core.commands.story_handler import StoryHandler
        story_components = {
            'config': None,
            'logger': logger,
            'output': viewport
        }
        self.story_handler = StoryHandler(story_components)

        
        # System Management Handlers
        from core.commands.logs_handler import create_logs_handler
        self.logs_handler = create_logs_handler()


        self.barter_handler = BarterCommandHandler()


        self.user_handler = UserCommandHandler(**handler_kwargs)


        self.tree_handler = TreeHandler()


        self.peek_handler = PeekHandler(**handler_kwargs)


        self.sandbox_handler = SandboxHandler()


        from core.commands.extension_handler import create_extension_handler
        self.extension_handler = create_extension_handler(viewport=viewport, logger=logger)

        # Calendar System (v1.2.23 Task 4)
        from core.commands.calendar_handler import CalendarHandler
        from core.config import Config
        self.calendar_handler = CalendarHandler(config=Config(), **handler_kwargs)
        
        # Development System Handlers
        from core.commands.dev_mode_handler import DevModeHandler
        self.dev_mode_handler = DevModeHandler()
        
        # Mode Handler (v1.3)
        from core.commands.mode_handler import ModeCommandHandler
        self.mode_handler = ModeCommandHandler(**handler_kwargs)

        # Set main_handler reference on all handlers
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
            # OK Assistant (check before ASSISTANT)
            if module == "OK":
                return self.ok_handler.handle(command, params, grid)

            elif module == "ASSISTANT" or module == "ASSIST":
                return self.assistant_handler.handle(command, params, grid)

            elif module == "FILE":
                return self.file_handler.handle(command, params, grid, parser)

            # ROLE - User role and permission management (v1.2.22)
            elif module == "ROLE":
                return self.system_handler.handle_role([command] + params, grid, parser)

            # PATTERNS - Error pattern learning (v1.2.22)
            elif module == "PATTERNS":
                return self.system_handler.handle_patterns([command] + params, grid, parser)

            # ERROR - Error context management (v1.2.22)
            elif module == "ERROR":
                return self.system_handler.handle_error([command] + params, grid, parser)

            # TIME - Time/date system (v1.2.22)
            elif module in ["TIME", "CLOCK", "TIMER", "EGG", "STOPWATCH", "CALENDAR"]:
                return self.time_handler.handle(command, params, grid)

            # JSON - JSON viewer/editor (v1.2.22)
            elif module == "JSON":
                return self.json_handler.handle_command([command] + params)

            elif module == "MAP":
                if self.map_handler:
                    return self.map_handler.handle(command, params, grid)
                else:
                    return ("❌ MAP commands require Play extension\n"
                           "💡 Install: POKE START play")



            # Memory System
            elif module == "MEMORY":
                return self.memory_handler.handle(command, params)

            elif module == "PRIVATE":
                return self.private_handler.handle(command, params)

            elif module == "SHARED":
                return self.shared_handler.handle(command, params)

            elif module == "COMMUNITY":
                return self.community_handler.handle(command, params)



            # Mapping System
            elif module == "TILE":
                return self.tile_handler.handle(command, ' '.join(params) if params else '', grid)

            # Barter System
            elif module == "BARTER" or module == "OFFER" or module == "REQUEST" or module == "TRADE":
                # Route OFFER, REQUEST, TRADE directly to barter handler
                if module in ["OFFER", "REQUEST", "TRADE"]:
                    return self.barter_handler.handle(module, params)
                else:
                    return self.barter_handler.handle(command, params)

            # Sprite System
            elif module == "SPRITE":
                success = self.sprite_handler.handle([command] + params)
                return "✅ Command executed" if success else "❌ Command failed"

            elif module == "OBJECT":
                success = self.object_handler.handle([command] + params)
                return "✅ Command executed" if success else "❌ Command failed"

            # v1.2.24 - Core Gameplay Commands
            elif module == "CHECKPOINT":
                # Map to WORKFLOW SAVE_CHECKPOINT/LOAD_CHECKPOINT
                from core.config import Config
                config = Config()
                # Convert CHECKPOINT*SAVE → SAVE_CHECKPOINT, CHECKPOINT*LOAD → LOAD_CHECKPOINT
                if command == "SAVE":
                    workflow_command = "SAVE_CHECKPOINT"
                elif command == "LOAD":
                    workflow_command = "LOAD_CHECKPOINT"
                elif command == "LIST":
                    workflow_command = "LIST_CHECKPOINTS"
                else:
                    workflow_command = command
                return handle_workflow_command(workflow_command, params, config)

            elif module == "XP":
                # Map to BARTER XP system
                return self.barter_handler.handle("XP", [command] + params)

            elif module == "ITEM":
                # Map to SPRITE INVENTORY system
                inventory_command = "ADD" if not command or command.startswith('+') else "REMOVE" if command.startswith('-') else command
                sprite_params = ["INVENTORY", inventory_command] + params
                success = self.sprite_handler.handle(sprite_params)
                return "✅ Item updated" if success else "❌ Item operation failed"

            # Story System
            elif module == "STORY":
                return self.story_handler.handle(command, params)

            # Display System
            elif module == "PANEL" or module == "UI":
                return self.panel_handler.handle(command, params, grid)

            # Documentation System
            elif module == "DOCS":
                return self.docs_handler.handle(command, params)
            
            # GUIDE - redirect to DOCS (consolidated in v2.0)
            elif module == "GUIDE":
                return self.docs_handler.handle(command, params)







            # Calendar & Task Management (v1.2.23 Task 4)
            elif module in ["CAL", "CALENDAR"]:
                return self.calendar_handler.handle_command([command] + params if command else [])
            
            # Task Management (v1.2.23 Task 4 - integrated with calendar)
            elif module == "TASK":
                return self.calendar_handler.handle_command([command] + params if command else [])
            
            # Checklist Management (separate from TASK)
            elif module == "CHECKLIST":
                return self.checklist_handler.handle(command, params)
            
            # Inbox Processing
            elif module == "INBOX":
                return self.inbox_handler.handle(command, params, grid)

            # Archive Management
            elif module == "ARCHIVE":
                return self.archive_handler.handle(params, grid, parser)

            # Backup System
            elif module == "BACKUP":
                return self.backup_handler.handle(params, grid, parser)

            # v1.1.16 - UNDO/REDO Version History
            elif module == "UNDO":
                return self.undo_handler.handle(params, grid, parser)

            elif module == "REDO":
                return self.undo_handler.handle_redo(params, grid, parser)

            # Session Management
            elif module in ["SESSION", "HISTORY", "RESTORE"]:
                return self.session_handler.handle(module, params, grid, parser)



            # Unified Generation System
            elif module == "MAKE":
                # MAKE handler expects all params including subcommand
                # Prepend command back to params since it contains the subcommand
                all_params = [command] + params if command else params
                return self.make_handler.handle("MAKE", all_params, grid)

            # OK Assistant Commands
            elif module == "OK":
                return self.ok_handler.handle(command, params, grid)

            # Admin Prompt Management
            elif module == "PROMPT":
                return self.prompt_handler.handle(params)

            # Diagram Systems
            elif module == "MERMAID":
                return self.mermaid_handler.handle_command(params)




            elif module == "TYPORA":
                if self.typora_handler:
                    return self.typora_handler.handle_command(params)
                else:
                    return (
                        "❌ Typora diagrams extension not available\n\n"
                        "The extension is located in:\n"
                        "  extensions/core/typora-diagrams/\n\n"
                        "Make sure the handler.py file exists and is importable.\n"
                    )



            # System Management
            elif module == "LOGS":
                return self.logs_handler.handle(command, params)

            # Extension Management
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

            # User Feedback
            elif module == "USER":
                return self.user_handler.handle(command, params, grid)

            # Feedback Shortcut
            elif module == "FEEDBACK":
                return self.user_handler.handle("FEEDBACK", params, grid)

            # v1.0.32 - TREE Directory Structure Generator
            elif module == "TREE":
                return self.tree_handler.handle(params)
            
            # v1.2.15 - TUI Management (Keypad, Predictor, Pager, Browser)
            elif module == "TUI":
                return self.tui_handler.handle_command([command] + params if command else params)

            # v1.5.0 - PEEK Data Collection System
            elif module == "PEEK":
                return self.peek_handler.handle(command, params, grid, parser)

            # v2.0 - Sandbox Management System
            elif module == "SANDBOX":
                return self.sandbox_handler.handle(command, params)
            
            # v1.2.21 - CLONE User Content Packaging
            elif module == "CLONE":
                return self.clone_handler.handle(params, grid, parser)
            
            # v1.2.21 - CLOUD Business Intelligence (BIZINTEL)
            elif module == "CLOUD":
                return self.cloud_handler.handle_command([module] + [command] + params)
            
            # v1.2.21 - BUILD Offline Installation Packaging  
            elif module == "BUILD":
                return self.build_handler.handle(params, grid, parser)
            
            # v1.1.16 - UNDO/REDO Version History
            elif module == "UNDO":
                return self.undo_handler.handle(params, grid, parser)
            
            elif module == "REDO":
                return self.undo_handler.handle_redo(params, grid, parser)

            # v1.1.8 - EXTENSION Management (Extension Polish)
            elif module == "EXTENSION" or module == "EXT":
                return self.extension_handler.handle_command([command] + params)

            # v1.2.2 - DEV MODE Interactive Debugging
            elif module == "DEV":
                return self.dev_mode_handler.handle([command] + params)

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

            # v1.2.9 - Gmail Cloud Integration
            elif module == "GMAIL" or module == "LOGIN" or module == "LOGOUT" or module == "EMAIL" or module == "SYNC":
                # Route LOGIN GMAIL, LOGOUT GMAIL, STATUS GMAIL, EMAIL LIST, SYNC GMAIL, etc.
                from core.config import Config
                config = Config()
                # Reconstruct command line for gmail handler
                if module == "GMAIL" or module == "SYNC":
                    parts = [module, command] + params
                else:
                    # LOGIN/LOGOUT/EMAIL are shortcuts to GMAIL subcommands
                    parts = [module, command] + params if command else [module] + params
                return self.gmail_handler(parts, config=config)

            # v1.1.2 - Resource Management
            elif module == "RESOURCE":
                from core.commands.resource_handler import handle_resource_command

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

            # v1.2.8+ - COLOR TUI Enhancement (rainbow splash, syntax highlighting, themed UI)
            elif module == "COLOR":
                # Join all params into single string for subcommand
                param_str = ' '.join(params) if params else ''
                return handle_color(param_str)

            # v1.3 - MODE system (prompt mode switching)
            elif module in ["MODE", "GHOST", "TOMB", "CRYPT"]:
                return self.mode_handler.handle(command, params)

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
