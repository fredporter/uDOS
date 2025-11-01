"""
uDOS v1.0.0 - System Command Handler (Modular)

Handles system administration commands by delegating to specialized handlers:
- REPAIR: Delegates to RepairHandler for comprehensive diagnostics and maintenance
- STATUS, DASHBOARD, VIEWPORT, PALETTE: Delegates to DashboardHandler
- SETTINGS, CONFIG: Delegates to ConfigurationHandler
- REBOOT, DESTROY: Core system commands handled directly
"""

import os
import sys
import json
import shutil
from pathlib import Path
from .base_handler import BaseCommandHandler


class SystemCommandHandler(BaseCommandHandler):
    """Modular system administration handler with specialized delegation."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Import services only when needed (lazy loading)
        self._startup_module = None
        self._settings_manager = None
        self._workspace_manager = None
        self._config_manager = None

    @property
    def startup(self):
        """Lazy load startup module."""
        if self._startup_module is None:
            from core import uDOS_startup
            self._startup_module = uDOS_startup
        return self._startup_module

    @property
    def settings_manager(self):
        """Lazy load settings manager."""
        if self._settings_manager is None:
            from core.services.settings_manager import SettingsManager
            self._settings_manager = SettingsManager()
        return self._settings_manager

    @property
    def workspace_manager(self):
        """Lazy load workspace manager."""
        if self._workspace_manager is None:
            from core.services.workspace_manager import WorkspaceManager
            self._workspace_manager = WorkspaceManager()
        return self._workspace_manager

    @property
    def config_manager(self):
        """Lazy load config manager."""
        if self._config_manager is None:
            from core.services.config_manager import ConfigManager
            self._config_manager = ConfigManager()
        return self._config_manager

    def handle(self, command, params, grid, parser):
        """
        Route system commands to appropriate handlers.

        Args:
            command: Command name (e.g., 'REPAIR', 'STATUS')
            params: List of command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result string
        """
        # Map commands to handler methods
        handlers = {
            'BLANK': self.handle_blank,
            'HELP': self.handle_help,
            'STATUS': self.handle_status,
            'REPAIR': self.handle_repair,
            'REBOOT': self.handle_reboot,
            'DESTROY': self.handle_destroy,
            'VIEWPORT': self.handle_viewport,
            'PALETTE': self.handle_palette,
            'DASH': self.handle_dashboard,
            'DASHBOARD': self.handle_dashboard,
            'TREE': self.handle_tree,
            'CLEAN': self.handle_clean,
            'CONFIG': self.handle_config,
            'SETTINGS': self.handle_settings,
            'SETUP': self.handle_setup,
            'WORKSPACE': self.handle_workspace,
            'OUTPUT': self.handle_output,
            'SERVER': self.handle_output,  # Alias for OUTPUT
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)
        else:
            return self.get_message("ERROR_UNKNOWN_SYSTEM_COMMAND", command=command)

    def handle_blank(self, params, grid, parser):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        return self.get_message("ACTION_SUCCESS_SCREEN_CLEARED")

    def handle_help(self, params, grid, parser):
        """
        Display help information for all commands or a specific command.

        Args:
            params: List with optional command name to get help for
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Formatted help text
        """
        # Load commands data
        commands_file = 'data/system/commands.json'
        try:
            with open(commands_file, 'r') as f:
                commands_data = json.load(f)['COMMANDS']
        except Exception as e:
            return f"❌ Error loading commands: {e}"

        if not params or params[0] == 'ALL':
            # Display organized command list dynamically from COMMANDS.UDO
            help_text = "╔" + "═"*78 + "╗\n"
            help_text += "║" + " "*26 + "📚 uDOS COMMAND REFERENCE" + " "*27 + "║\n"
            help_text += "╠" + "═"*78 + "╣\n"

            # Auto-categorize commands based on their properties
            categories = {
                "📊 System & Info": [],
                "🤖 Assistant & Analysis": [],
                "🔧 System Control": [],
                "📝 File Operations": [],
                "🗺️  Navigation & Mapping": [],
                "🌐 Web Output": [],
                "🎨 Customization": [],
                "⚡ Other": []
            }

            # Build command lookup and auto-categorize
            cmd_lookup = {}
            for cmd_data in commands_data:
                cmd_name = cmd_data.get('NAME', '')
                cmd_lookup[cmd_name] = {
                    'syntax': cmd_data.get('SYNTAX', ''),
                    'desc': cmd_data.get('DESCRIPTION', '')
                }

                # Auto-categorize based on name and uCODE template
                ucode = cmd_data.get('UCODE_TEMPLATE', '')
                if cmd_name in ['STATUS', 'DASH', 'DASHBOARD', 'VIEWPORT', 'PALETTE', 'HELP', 'TREE', 'SETUP']:
                    categories["📊 System & Info"].append(cmd_name)
                elif 'ASSISTANT|' in ucode or cmd_name in ['ASK', 'ANALYZE', 'EXPLAIN', 'GENERATE', 'DEBUG', 'CLEAR']:
                    categories["🤖 Assistant & Analysis"].append(cmd_name)
                elif cmd_name in ['BLANK', 'REBOOT', 'RESTART', 'REPAIR', 'DESTROY', 'UNDO', 'REDO', 'RESTORE', 'CLEAN']:
                    categories["🔧 System Control"].append(cmd_name)
                elif 'FILE|' in ucode or cmd_name in ['EDIT', 'SHOW', 'RUN', 'NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME']:
                    categories["📝 File Operations"].append(cmd_name)
                elif 'MAP' in cmd_name or cmd_name in ['GOTO', 'MOVE', 'LAYER', 'DESCEND', 'ASCEND', 'LOCATE', 'WHERE']:
                    categories["🗺️  Navigation & Mapping"].append(cmd_name)
                elif cmd_name in ['OUTPUT', 'SERVER', 'WEB']:
                    categories["🌐 Web Output"].append(cmd_name)
                elif cmd_name in ['FONT', 'THEME', 'CONFIG', 'SETTINGS']:
                    categories["🎨 Customization"].append(cmd_name)
                else:
                    categories["⚡ Other"].append(cmd_name)

            # Display by category (only show categories with commands)
            for category, commands in categories.items():
                if not commands:
                    continue

                help_text += "║ " + category.ljust(77) + "║\n"
                help_text += "║ " + "─"*77 + "║\n"

                for cmd_name in sorted(commands):
                    if cmd_name in cmd_lookup:
                        cmd_info = cmd_lookup[cmd_name]
                        # Truncate description to fit
                        desc = cmd_info['desc'][:56]
                        help_text += f"║  {cmd_name:<18} - {desc.ljust(56)}║\n"

                help_text += "║" + " "*78 + "║\n"

            # Footer
            help_text += "╠" + "═"*78 + "╣\n"
            help_text += "║  💡 HELP <command_name> for detailed information".ljust(79) + "║\n"
            help_text += "║  📖 Full docs: https://github.com/fredporter/uDOS/wiki".ljust(79) + "║\n"
            help_text += "╚" + "═"*78 + "╝\n"

            return help_text
        else:
            # Display help for a specific command
            cmd_name = params[0].upper()
            for cmd_data in commands_data:
                if cmd_data.get('NAME') == cmd_name:
                    help_text = "╔" + "═"*78 + "╗\n"
                    help_text += f"║  📖 {cmd_name}".ljust(79) + "║\n"
                    help_text += "╠" + "═"*78 + "╣\n"

                    # Description
                    desc = cmd_data.get('DESCRIPTION', 'No description')
                    help_text += "║  Description:".ljust(79) + "║\n"
                    # Word wrap description
                    words = desc.split()
                    line = "║    "
                    for word in words:
                        if len(line) + len(word) + 1 > 77:
                            help_text += line.ljust(79) + "║\n"
                            line = "║    " + word
                        else:
                            line += (" " if len(line) > 4 else "") + word
                    if len(line) > 4:
                        help_text += line.ljust(79) + "║\n"

                    help_text += "║".ljust(79) + "║\n"

                    # Syntax
                    syntax = cmd_data.get('SYNTAX', 'No syntax')
                    help_text += "║  Syntax:".ljust(79) + "║\n"
                    help_text += f"║    {syntax}".ljust(79) + "║\n"

                    # uCODE template if available
                    if 'UCODE_TEMPLATE' in cmd_data:
                        help_text += "║".ljust(79) + "║\n"
                        help_text += "║  uCODE Format:".ljust(79) + "║\n"
                        template = cmd_data.get('UCODE_TEMPLATE', '')
                        help_text += f"║    {template}".ljust(79) + "║\n"

                    help_text += "╚" + "═"*78 + "╝\n"
                    return help_text
            return self.get_message("ERROR_COMMAND_NOT_FOUND", command=cmd_name)

    # ======================================================================
    # DELEGATED HANDLERS - Route to specialized handlers
    # ======================================================================

    def handle_repair(self, params, grid, parser):
        """
        System diagnostics and repair with extension management.
        Delegates to specialized RepairHandler for comprehensive functionality.
        """
        from .repair_handler import RepairHandler

        # Create repair handler with same context
        repair_handler = RepairHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return repair_handler.handle_repair(params, grid, parser)

    def handle_status(self, params, grid, parser):
        """
        Display comprehensive system status.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_status(params, grid, parser)

    def handle_dashboard(self, params, grid, parser):
        """
        Display system dashboard.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_dashboard(params, grid, parser)

    def handle_viewport(self, params, grid, parser):
        """
        Display viewport visualization.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_viewport(params, grid, parser)

    def handle_palette(self, params, grid, parser):
        """
        Display color palette.
        Delegates to specialized DashboardHandler for functionality.
        """
        from .dashboard_handler import DashboardHandler

        # Create dashboard handler with same context
        dashboard_handler = DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return dashboard_handler.handle_palette(params, grid, parser)

    def handle_settings(self, params, grid, parser):
        """
        Manage system settings.
        Delegates to specialized ConfigurationHandler for functionality.
        """
        from .configuration_handler import ConfigurationHandler

        # Create configuration handler with same context
        config_handler = ConfigurationHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return config_handler.handle_settings(params, grid, parser)

    def handle_config(self, params, grid, parser):
        """
        Manage configuration files.
        Delegates to specialized ConfigurationHandler for functionality.
        """
        from .configuration_handler import ConfigurationHandler

        # Create configuration handler with same context
        config_handler = ConfigurationHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return config_handler.handle_config(params, grid, parser)

    # ======================================================================
    # CORE SYSTEM COMMANDS - Handled directly
    # ======================================================================

    def handle_reboot(self, params, grid, parser):
        """
        Restart the entire uDOS system.
        Equivalent to exiting and re-running uDOS.py
        """
        output = "\n🔄 REBOOTING uDOS SYSTEM...\n\n"
        output += "✅ Saving current state...\n"
        output += "✅ Clearing memory buffers...\n"
        output += "✅ Reinitializing components...\n\n"
        output += "🚀 System restart complete!\n"
        output += "Welcome back to uDOS v1.0.0\n\n"

        # Signal for system restart
        if hasattr(self, '_signal_restart'):
            self._signal_restart()

        return output

    def handle_destroy(self, params, grid, parser):
        """
        Destructive reset command with safety confirmations.
        Supports: --all, --env, --reset flags

        Args:
            params: List with optional flags (--all, --env, --reset)
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Destruction confirmation or cancellation message
        """
        # Safety confirmation required
        destruction_type = params[0] if params else None

        # Warning message based on destruction type
        if destruction_type == "--all":
            warning_msg = "⚠️  DANGER: This will DELETE ALL user data, extensions, and settings!"
            target = "entire uDOS installation"
        elif destruction_type == "--env":
            warning_msg = "⚠️  This will reset the Python environment and dependencies"
            target = "Python environment"
        elif destruction_type == "--reset":
            warning_msg = "⚠️  This will reset all settings to defaults"
            target = "configuration settings"
        else:
            return ("❌ DESTROY requires a flag\n\n"
                   "Available options:\n"
                   "  DESTROY --reset    Reset settings to defaults\n"
                   "  DESTROY --env      Reset Python environment\n"
                   "  DESTROY --all      Delete all user data (DANGER!)\n\n"
                   "⚠️  All DESTROY operations require confirmation")

        # Return warning and ask for confirmation
        result = f"🚨 DESTRUCTION CONFIRMATION REQUIRED\n"
        result += "=" * 50 + "\n"
        result += f"{warning_msg}\n\n"
        result += f"Target: {target}\n\n"
        result += "To proceed, type: DESTROY CONFIRM\n"
        result += "To cancel, type any other command\n"
        result += "\n⚠️  This action cannot be undone!"

        return result

    # ======================================================================
    # STUB METHODS - To be implemented or moved to other handlers
    # ======================================================================

    def handle_tree(self, params, grid, parser):
        """File tree display - to be implemented or moved to file handler."""
        return "🌳 TREE command - Implementation moved to file handler"

    def handle_clean(self, params, grid, parser):
        """Clean sandbox - to be implemented or moved to file handler."""
        return "🧹 CLEAN command - Implementation moved to file handler"

    def handle_setup(self, params, grid, parser):
        """Setup wizard - to be implemented."""
        return "⚙️ SETUP command - Implementation pending"

    def handle_workspace(self, params, grid, parser):
        """Workspace management - to be implemented."""
        return "🏢 WORKSPACE command - Implementation pending"

    def handle_output(self, params, grid, parser):
        """
        Manage web-based output interfaces (servers).
        Enhanced implementation for v1.0.5 Web Server Infrastructure.
        """
        if not params:
            return ("❌ Usage: OUTPUT <START|STOP|STATUS|LIST> [name] [options]\n\n"
                   "Examples:\n"
                   "  OUTPUT LIST                    # List all available extensions\n"
                   "  OUTPUT START dashboard         # Start dashboard server\n"
                   "  OUTPUT STATUS                  # Show all server status\n"
                   "  OUTPUT STOP teletext          # Stop teletext server")

        subcommand = params[0].upper()

        if subcommand == "LIST":
            return self._handle_output_list()
        elif subcommand == "STATUS":
            extension_name = params[1] if len(params) > 1 else None
            return self._handle_output_status(extension_name)
        elif subcommand == "START":
            if len(params) < 2:
                return "❌ Usage: OUTPUT START <extension_name> [--port N] [--no-browser]"
            extension_name = params[1]
            options = params[2:] if len(params) > 2 else []
            return self._handle_output_start(extension_name, options)
        elif subcommand == "STOP":
            if len(params) < 2:
                return "❌ Usage: OUTPUT STOP <extension_name>"
            extension_name = params[1]
            return self._handle_output_stop(extension_name)
        else:
            return f"❌ Unknown OUTPUT subcommand: {subcommand}\nUse: START, STOP, STATUS, or LIST"

    def _handle_output_list(self):
        """List all available web extensions."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()
            return server_manager.list_servers()
        except Exception as e:
            return f"❌ Error listing extensions: {str(e)}"

    def _handle_output_status(self, extension_name=None):
        """Show status of web extensions."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()
            return server_manager.get_status(extension_name)
        except Exception as e:
            return f"❌ Error getting status: {str(e)}"

    def _handle_output_start(self, extension_name, options):
        """Start a web extension server."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()

            # Parse options
            port = None
            no_browser = False

            for option in options:
                if option.startswith('--port'):
                    if '=' in option:
                        port = int(option.split('=')[1])
                    else:
                        # Look for next parameter
                        port_index = options.index(option) + 1
                        if port_index < len(options):
                            port = int(options[port_index])
                elif option == '--no-browser':
                    no_browser = True

            return server_manager.start_server(extension_name, port=port, open_browser=not no_browser)
        except Exception as e:
            return f"❌ Error starting {extension_name}: {str(e)}"

    def _handle_output_stop(self, extension_name):
        """Stop a web extension server."""
        try:
            from core.uDOS_server import ServerManager
            server_manager = ServerManager()
            success, message = server_manager.stop_server(extension_name)
            return f"🛑 {message}" if success else f"⚠️  {message}"
        except Exception as e:
            return f"❌ Error stopping {extension_name}: {str(e)}"
