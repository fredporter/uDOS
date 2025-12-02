"""
uDOS v1.0.0 - System Command Handler (Modular)

Handles system administration commands by delegating to specialized handlers:
- REPAIR: Delegates to RepairHandler for comprehensive diagnostics and maintenance
- STATUS, DASHBOARD, VIEWPORT, PALETTE: Delegates to DashboardHandler
- WIZARD (old SETUP): Setup wizard for first-time configuration
- CONFIG: Delegates to ConfigurationHandler for settings management
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
        self._help_manager = None
        self._screen_manager = None
        self._setup_wizard = None
        self._usage_tracker = None

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
        """Lazy load config manager (v1.5.0: Uses new ConfigManager)."""
        if self._config_manager is None:
            from core.uDOS_main import get_config
            self._config_manager = get_config()
        return self._config_manager

    @property
    def help_manager(self):
        """Lazy load help manager."""
        if self._help_manager is None:
            from core.services.help_manager import HelpManager
            self._help_manager = HelpManager()
        return self._help_manager

    @property
    def screen_manager(self):
        """Lazy load screen manager."""
        if self._screen_manager is None:
            from core.output.screen_manager import ScreenManager
            self._screen_manager = ScreenManager()
        return self._screen_manager

    @property
    def setup_wizard(self):
        """Lazy load setup wizard."""
        if self._setup_wizard is None:
            from core.services.setup_wizard import SetupWizard
            self._setup_wizard = SetupWizard()
        return self._setup_wizard

    @property
    def usage_tracker(self):
        """Lazy load usage tracker."""
        if self._usage_tracker is None:
            from core.utils.usage_tracker import UsageTracker
            self._usage_tracker = UsageTracker()
        return self._usage_tracker

    @property
    def dev_mode_manager(self):
        """Lazy load DEV MODE manager (v1.5.0)."""
        if not hasattr(self, '_dev_mode_manager') or self._dev_mode_manager is None:
            from core.services.dev_mode_manager import get_dev_mode_manager
            self._dev_mode_manager = get_dev_mode_manager(config_manager=self.config_manager)
        return self._dev_mode_manager

    @property
    def variable_handler(self):
        """Lazy load variable handler."""
        if not hasattr(self, '_variable_handler') or self._variable_handler is None:
            from .variable_handler import VariableHandler
            self._variable_handler = VariableHandler(**self.__dict__)
        return self._variable_handler

    @property
    def environment_handler(self):
        """Lazy load environment handler."""
        if not hasattr(self, '_environment_handler') or self._environment_handler is None:
            from .environment_handler import EnvironmentHandler
            self._environment_handler = EnvironmentHandler(**self.__dict__)
        return self._environment_handler

    @property
    def environment_handler(self):
        """Lazy load environment handler."""
        if not hasattr(self, '_environment_handler') or self._environment_handler is None:
            from .environment_handler import EnvironmentHandler
            self._environment_handler = EnvironmentHandler(**self.__dict__)
        return self._environment_handler

    def handle_help(self, params, grid, parser):
        """Quick help - shows essential commands and both syntaxes."""
        from .display_handler import DisplayHandler

        # Delegate to display_handler for full help functionality
        display_handler = DisplayHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )
        return display_handler.handle_help(params, grid, parser)

    def handle_blank(self, params, grid, parser):
        """Clear screen (BLANK) - delegates to DisplayHandler."""
        from .display_handler import DisplayHandler
        display_handler = DisplayHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )
        return display_handler.handle_blank(params, grid, parser)

    def handle_splash(self, params, grid, parser):
        """Show splash screen - delegates to DisplayHandler."""
        from .display_handler import DisplayHandler
        display_handler = DisplayHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )
        return display_handler.handle_splash(params, grid, parser)

    def handle_layout(self, params, grid, parser):
        """Screen layout management - delegates to DisplayHandler."""
        from .display_handler import DisplayHandler
        display_handler = DisplayHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )
        return display_handler.handle_layout(params, grid, parser)

    def handle_progress(self, params, grid, parser):
        """Show progress indicators - delegates to DisplayHandler."""
        from .display_handler import DisplayHandler
        display_handler = DisplayHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )
        return display_handler.handle_progress(params, grid, parser)

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
            'SPLASH': self.handle_splash,
            'HELP': self.handle_help,
            'HISTORY': self.handle_history,
            'PROGRESS': self.handle_progress,
            'LAYOUT': self.handle_layout,
            'STATUS': self.handle_status,
            'REPAIR': self.handle_repair,
            'SHAKEDOWN': self.handle_shakedown,
            'REBOOT': self.handle_reboot,
            'DESTROY': self.handle_destroy,
            'VIEWPORT': self.handle_viewport,
            'PALETTE': self.handle_palette,
            'DASH': self.handle_dashboard,
            'DASHBOARD': self.handle_dashboard,
            'CLEAN': self.handle_clean,
            'CONFIG': self.handle_config,
            'WIZARD': self.handle_wizard,
            'SETUP': self.handle_settings,
            # WORKSPACE command removed - use file pickers
            'OUTPUT': self.handle_output,
            'SERVER': self.handle_output,
            'GET': self.handle_get,
            'SET': self.handle_set,
            'CONFIG_PLANET': self.handle_config_planet,
            'LOCATE': self.handle_locate,
            'DEV': self.handle_dev_mode,
            'ASSETS': self.handle_assets,
        }

        handler = handlers.get(command)
        if handler:
            return handler(params, grid, parser)
        else:
            return self.get_message("ERROR_UNKNOWN_SYSTEM_COMMAND", command=command)

    def _create_custom_theme(self, theme_manager, name):
        """Create a custom theme (simplified for now)."""
        try:
            # For now, create a sample custom theme based on current theme
            current_scheme = theme_manager.get_current_scheme()
            success = theme_manager.create_custom_theme(name, current_scheme)

            if success:
                return theme_manager.format_text(f"🎨 Custom theme created: {name}", "success") + "\n💡 Use 'THEME SET custom-{name}' to activate"
            else:
                return theme_manager.format_text(f"❌ Failed to create theme: {name}", "error")
        except Exception as e:
            return f"❌ Error creating custom theme: {e}"

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

    def handle_shakedown(self, params, grid, parser):
        """
        Comprehensive v1.5.0 system validation test suite.
        Delegates to specialized ShakedownHandler for test execution.
        """
        from .shakedown_handler import ShakedownHandler

        # Create shakedown handler with same context
        shakedown_handler = ShakedownHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

        return shakedown_handler.handle(params)

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
        """Manage system settings - delegates to EnvironmentHandler."""
        return self.environment_handler.handle_settings(params, grid, parser)

    def handle_config(self, params, grid, parser):
        """
        Manage configuration files.
        Supports CONFIG ROLE to assign wizard/dev roles.
        Delegates to specialized ConfigurationHandler for functionality.
        """
        # Handle CONFIG ROLE subcommand
        if params and params[0].upper() == 'ROLE':
            return self._handle_config_role(params[1:] if len(params) > 1 else [])

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

    def _handle_config_role(self, params):
        """Handle CONFIG ROLE subcommand for wizard/dev role assignment."""
        if not params:
            # Show current role
            current_role = self.config_manager.get('USER_ROLE', 'user')
            return (f"📋 Current Role: {current_role}\n\n"
                   f"Available roles:\n"
                   f"  • user    - Standard user (default)\n"
                   f"  • wizard  - Developer access (OK DEV, advanced features)\n\n"
                   f"Usage: CONFIG ROLE <role>\n"
                   f"Example: CONFIG ROLE wizard")

        role = params[0].lower()
        if role not in ['user', 'wizard']:
            return f"❌ Invalid role: {role}\n💡 Available: user, wizard"

        # Set role in config
        self.config_manager.set('USER_ROLE', role)
        self.config_manager.save()

        emoji = "🧙" if role == "wizard" else "👤"
        features = "\n✅ OK DEV enabled\n✅ Advanced system access" if role == "wizard" else ""

        return f"{emoji} Role set to: {role}{features}"

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

        # Refresh viewport detection
        try:
            from core.services.viewport_manager import ViewportManager
            viewport = ViewportManager()
            viewport_info = viewport.refresh_viewport()
            tier = viewport_info["screen_tier"]
            output += f"🖥️  Viewport refreshed: {tier['label']} ({tier['actual_width_cells']}×{tier['actual_height_cells']} cells)\n"
        except Exception as e:
            output += f"⚠️  Viewport refresh warning: {str(e)}\n"

        output += "✅ Reinitializing components...\n\n"
        output += "🚀 System restart initiated!\n"
        output += "Welcome back to uDOS v1.0.0\n\n"

        # Set the reboot flag to trigger restart in main loop
        self.reboot_requested = True

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
        from core.commands.sandbox_handler import SandboxHandler

        # Safety confirmation required
        destruction_type = params[0] if params else None

        # Handle confirmation (if user types DESTROY CONFIRM after warning)
        if destruction_type and destruction_type.upper() == "CONFIRM":
            # This shouldn't be reached normally - confirmation happens via re-entering command
            return "⚠️  Please re-enter DESTROY command with flag (--reset, --env, or --all)"

        # Map destruction types to sandbox modes
        sandbox_mode_map = {
            "--reset": "reset",
            "--env": "env",
            "--all": "all"
        }

        # Warning message based on destruction type
        if destruction_type == "--all":
            warning_msg = "⚠️  DANGER: This will DELETE ALL user data, sandbox, and logs!"
            target = "sandbox (all folders except protected)"
        elif destruction_type == "--env":
            warning_msg = "⚠️  This will clean environment files and cached data"
            target = "environment files (.env, .venv cache)"
        elif destruction_type == "--reset":
            warning_msg = "⚠️  This will reset sandbox to pristine state"
            target = "sandbox (preserving user/ and tests/)"
        else:
            return ("❌ DESTROY requires a flag\n\n"
                   "Available options:\n"
                   "  DESTROY --reset    Reset sandbox (safe - preserves user/tests)\n"
                   "  DESTROY --env      Clean environment files\n"
                   "  DESTROY --all      Delete all sandbox data (DANGER!)\n\n"
                   "⚠️  All DESTROY operations require confirmation")

        # Execute destruction via sandbox handler
        mode = sandbox_mode_map.get(destruction_type)
        if mode:
            sandbox_handler = SandboxHandler()
            result = sandbox_handler.destroy_sandbox(mode=mode)
            return result
        else:
            return f"❌ Unknown destruction mode: {destruction_type}"

    # ======================================================================
    # STUB METHODS - To be implemented or moved to other handlers
    # ======================================================================

    def handle_clean(self, params, grid, parser):
        """Review sandbox files - delegates to EnvironmentHandler."""
        return self.environment_handler.handle_clean(params, grid, parser)

    def handle_wizard(self, params, grid, parser):
        """
        Enhanced setup wizard with multiple modes (renamed from SETUP).

        Modes:
        - WIZARD or WIZARD WIZARD: Full interactive wizard
        - WIZARD QUICK: Quick setup with sensible defaults
        - WIZARD THEME: Theme selection only
        - WIZARD VIEWPORT: Viewport configuration only
        - WIZARD EXTENSIONS: Extension management only
        - WIZARD HELP: Show setup help information
        """
        if not params:
            # Default to full wizard
            return self.setup_wizard.run_full_wizard()

        mode = params[0].upper()

        if mode == "HELP":
            return self.setup_wizard.format_help()

        elif mode == "WIZARD":
            return self.setup_wizard.run_full_wizard()

        elif mode == "QUICK":
            return self.setup_wizard.run_quick_setup()

        elif mode == "THEME":
            return self.setup_wizard.setup_theme_only()

        elif mode == "VIEWPORT":
            return self.setup_wizard.setup_viewport_only()

        elif mode == "EXTENSIONS":
            return self.setup_wizard.setup_extensions_only()

        else:
            return (f"❌ Unknown wizard mode: {mode}\n\n"
                   "📋 Available modes:\n"
                   "  WIZARD or WIZARD WIZARD     # Full interactive setup\n"
                   "  WIZARD QUICK              # Quick setup with defaults\n"
                   "  WIZARD THEME              # Theme selection only\n"
                   "  WIZARD VIEWPORT           # Viewport configuration only\n"
                   "  WIZARD EXTENSIONS         # Extension management only\n"
                   "  WIZARD HELP               # Show detailed help\n\n"
                   "💡 Tip: Use WIZARD HELP for detailed information\n"
                   "💡 Note: For settings, use SETUP or CONFIG commands")

    # WORKSPACE command removed - use file pickers with uDOS subdirectories instead
    # (sandbox, memory, knowledge, etc. act as workspaces)

    def handle_output(self, params, grid, parser):
        """
        Manage web-based output interfaces (servers) and extensions.
        Implementation for v1.0.11 Extension System Formalization.
        """
        if not params:
            return ("❌ Usage: POKE <command> [name] [options]\n\n"
                   "🖥️  Server Management:\n"
                   "  POKE LIST                      # List all available extensions\n"
                   "  POKE START dashboard           # Start dashboard server\n"
                   "  POKE STATUS                    # Show all server status\n"
                   "  POKE HEALTH                    # Check server health\n"
                   "  POKE RESTART dashboard         # Restart specific server\n"
                   "  POKE STOP teletext            # Stop teletext server\n\n"
                   "🔧 Extension Management:\n"
                   "  POKE DISCOVER                  # Scan for new extensions\n"
                   "  POKE INFO <name>               # Detailed extension information\n"
                   "  POKE INSTALL <name>            # Install extension from source\n"
                   "  POKE UNINSTALL <name>          # Remove extension\n"
                   "  POKE MARKETPLACE               # Browse extension marketplace")

        subcommand = params[0].upper()

        if subcommand == "LIST":
            return self._handle_output_list()
        elif subcommand == "STATUS":
            extension_name = params[1] if len(params) > 1 else None
            return self._handle_output_status(extension_name)
        elif subcommand == "HEALTH":
            return self._handle_output_health()
        elif subcommand == "START":
            if len(params) < 2:
                return "❌ Usage: POKE START <extension_name> [--port N] [--no-browser]"
            extension_name = params[1]
            options = params[2:] if len(params) > 2 else []
            return self._handle_output_start(extension_name, options)
        elif subcommand == "STOP":
            if len(params) < 2:
                return "❌ Usage: POKE STOP <extension_name>"
            extension_name = params[1]
            return self._handle_output_stop(extension_name)
        elif subcommand == "RESTART":
            if len(params) < 2:
                return "❌ Usage: POKE RESTART <extension_name>"
            extension_name = params[1]
            return self._handle_output_restart(extension_name)
        # New extension management commands for v1.0.11
        elif subcommand == "DISCOVER":
            return self._handle_extension_discover()
        elif subcommand == "INFO":
            if len(params) < 2:
                return "❌ Usage: POKE INFO <extension_name>"
            extension_name = params[1]
            return self._handle_extension_info(extension_name)
        elif subcommand == "INSTALL":
            if len(params) < 2:
                return "❌ Usage: POKE INSTALL <extension_name>"
            extension_name = params[1]
            return self._handle_extension_install(extension_name)
        elif subcommand == "UNINSTALL":
            if len(params) < 2:
                return "❌ Usage: POKE UNINSTALL <extension_name>"
            extension_name = params[1]
            return self._handle_extension_uninstall(extension_name)
        elif subcommand == "MARKETPLACE":
            return self._handle_extension_marketplace()
        else:
            return f"❌ Unknown POKE subcommand: {subcommand}\nUse: START, STOP, STATUS, LIST, HEALTH, RESTART, DISCOVER, INFO, INSTALL, UNINSTALL, or MARKETPLACE"

    def _handle_output_list(self):
        """List all available web extensions."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()
            return server_manager.list_servers()
        except Exception as e:
            return f"❌ Error listing extensions: {str(e)}"

    def _handle_output_status(self, extension_name=None):
        """Show status of web extensions."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()
            return server_manager.get_status(extension_name)
        except Exception as e:
            return f"❌ Error getting status: {str(e)}"

    def _handle_output_start(self, extension_name, options):
        """Start a web extension server."""
        try:
            from extensions.server_manager import ServerManager
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
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()
            success, message = server_manager.stop_server(extension_name)
            return f"🛑 {message}" if success else f"⚠️  {message}"
        except Exception as e:
            return f"❌ Error stopping {extension_name}: {str(e)}"

    def _handle_output_health(self):
        """Perform health check on all running servers."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()

            # Get current status
            status_result = server_manager.get_status()

            # Count running/stopped servers
            running_count = status_result.count("✅")
            stopped_count = status_result.count("❌")
            total_count = running_count + stopped_count

            health_report = f"🏥 Server Health Report\n"
            health_report += f"{'='*40}\n"
            health_report += f"📊 Summary:\n"
            health_report += f"   ✅ Running: {running_count}\n"
            health_report += f"   ❌ Stopped: {stopped_count}\n"
            health_report += f"   📈 Total: {total_count}\n\n"

            if running_count == 0:
                health_report += "⚠️  No servers currently running\n"
                health_report += "💡 Tip: Use 'OUTPUT START <name>' to start servers\n"
            elif stopped_count == 0:
                health_report += "✅ All servers are running healthy!\n"
            else:
                health_percentage = (running_count / total_count) * 100 if total_count > 0 else 0
                health_report += f"📊 System Health: {health_percentage:.1f}%\n"

                if health_percentage >= 80:
                    health_report += "✅ System health is good\n"
                elif health_percentage >= 50:
                    health_report += "⚠️  System health is moderate\n"
                else:
                    health_report += "❌ System health needs attention\n"

            return health_report

        except Exception as e:
            return f"❌ Error checking health: {str(e)}"

    def _handle_output_restart(self, extension_name):
        """Restart a web extension server."""
        try:
            from extensions.server_manager import ServerManager
            server_manager = ServerManager()

            # Stop the server first
            stop_success, stop_message = server_manager.stop_server(extension_name)

            # Wait a moment for cleanup
            import time
            time.sleep(1)

            # Start the server again
            start_result = server_manager.start_server(extension_name)

            if stop_success or "not running" in stop_message:
                return f"🔄 Restarted {extension_name}:\n🛑 Stop: {stop_message}\n{start_result}"
            else:
                return f"⚠️  Restart {extension_name} (stop failed, attempting start anyway):\n🛑 Stop: {stop_message}\n{start_result}"

        except Exception as e:
            return f"❌ Error restarting {extension_name}: {str(e)}"

    # Extension Management Methods - v1.0.11 Extension System Formalization

    def _handle_extension_discover(self):
        """Discover available extensions in the system and scan for new ones."""
        try:
            import json
            from pathlib import Path

            discovered = []
            report = "🔍 EXTENSION DISCOVERY REPORT\n" + "="*50 + "\n\n"

            # Scan bundled extensions
            bundled_path = Path(__file__).parent.parent.parent / "extensions" / "bundled" / "web"
            if bundled_path.exists():
                manifest_path = bundled_path / "version-manifest.json"
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)

                        report += "🎁 BUNDLED EXTENSIONS:\n"
                        for name, info in manifest.get('extensions', {}).items():
                            status = "🟢 Available" if (bundled_path / name).exists() else "🔴 Missing"
                            report += f"  {status} {name} v{info.get('version', 'unknown')}\n"
                            report += f"    📝 {info.get('description', 'No description')}\n"
                            if info.get('port'):
                                report += f"    🌐 Port: {info['port']}\n"
                            report += "\n"
                            discovered.append(name)
                    except Exception as e:
                        report += f"❌ Error reading manifest: {str(e)}\n"

            # Scan cloned extensions
            cloned_path = Path(__file__).parent.parent.parent / "extensions" / "cloned"
            if cloned_path.exists():
                cloned_dirs = [d for d in cloned_path.iterdir() if d.is_dir()]
                if cloned_dirs:
                    report += "\n🌐 CLONED EXTENSIONS:\n"
                    for ext_dir in cloned_dirs:
                        report += f"  📂 {ext_dir.name}\n"
                        # Check for package.json or README
                        if (ext_dir / "package.json").exists():
                            report += f"    📦 Node.js project detected\n"
                        if (ext_dir / "README.md").exists():
                            report += f"    📖 Documentation available\n"
                        discovered.append(ext_dir.name)

            # Check extension manager status
            from extensions.core.extension_manager import ExtensionManager
            ext_mgr = ExtensionManager()
            status = ext_mgr.get_extension_status()

            report += "\n🔧 INSTALLATION STATUS:\n"
            for ext, installed in status.items():
                symbol = "✅" if installed else "❌"
                report += f"  {symbol} {ext}\n"

            report += f"\n📊 SUMMARY: {len(discovered)} extensions discovered\n"
            return report

        except Exception as e:
            return f"❌ Error during discovery: {str(e)}"

    def _handle_extension_info(self, extension_name):
        """Get detailed information about a specific extension using enhanced metadata."""
        try:
            # Use the enhanced metadata manager for comprehensive information
            from extensions.core.extension_metadata_manager import ExtensionMetadataManager
            metadata_mgr = ExtensionMetadataManager()

            # Generate comprehensive report
            report = metadata_mgr.generate_extension_report(extension_name)
            return report

        except ImportError:
            # Fallback to basic implementation if metadata manager is not available
            return self._handle_extension_info_basic(extension_name)
        except Exception as e:
            return f"❌ Error getting extension info: {str(e)}"

    def _handle_extension_info_basic(self, extension_name):
        """Basic extension info implementation (fallback)."""
        try:
            import json
            from pathlib import Path

            info_report = f"📋 EXTENSION INFO: {extension_name}\n" + "="*50 + "\n\n"

            # Check bundled extensions first
            bundled_path = Path(__file__).parent.parent.parent / "extensions" / "bundled" / "web"
            manifest_path = bundled_path / "version-manifest.json"

            extension_found = False

            if manifest_path.exists():
                try:
                    with open(manifest_path, 'r') as f:
                        manifest = json.load(f)

                    if extension_name in manifest.get('extensions', {}):
                        ext_info = manifest['extensions'][extension_name]
                        extension_found = True

                        info_report += f"📦 NAME: {extension_name}\n"
                        info_report += f"🏷️  VERSION: {ext_info.get('version', 'unknown')}\n"
                        info_report += f"📝 DESCRIPTION: {ext_info.get('description', 'No description')}\n"

                        if ext_info.get('port'):
                            info_report += f"🌐 PORT: {ext_info['port']}\n"

                        if ext_info.get('features'):
                            info_report += f"\n✨ FEATURES:\n"
                            for feature in ext_info['features']:
                                info_report += f"  • {feature}\n"

                        if ext_info.get('dependencies'):
                            info_report += f"\n📦 DEPENDENCIES:\n"
                            for dep in ext_info['dependencies']:
                                info_report += f"  • {dep}\n"

                        # Check if extension files exist
                        ext_path = bundled_path / extension_name
                        if ext_path.exists():
                            info_report += f"\n📂 STATUS: ✅ Installed\n"
                            info_report += f"📍 LOCATION: {ext_path}\n"

                            # Count files
                            try:
                                files = list(ext_path.rglob('*'))
                                file_count = len([f for f in files if f.is_file()])
                                info_report += f"📄 FILES: {file_count}\n"
                            except:
                                pass
                        else:
                            info_report += f"\n📂 STATUS: ❌ Not installed\n"

                except Exception as e:
                    info_report += f"❌ Error reading manifest: {str(e)}\n"

            # Check extension manager
            try:
                from extensions.core.extension_manager import ExtensionManager
                ext_mgr = ExtensionManager()
                ext_details = ext_mgr.get_extension_info(extension_name)

                if ext_details and not extension_found:
                    extension_found = True
                    info_report += f"📦 NAME: {ext_details.get('name', extension_name)}\n"
                    info_report += f"📝 DESCRIPTION: {ext_details.get('description', 'No description')}\n"
                    info_report += f"🔗 REPOSITORY: {ext_details.get('repository', 'Not specified')}\n"
                    info_report += f"⚙️  TYPE: {ext_details.get('type', 'unknown')}\n"

                    if ext_details.get('port'):
                        info_report += f"🌐 PORT: {ext_details['port']}\n"

                    # Check installation status
                    is_installed = ext_mgr.check_extension_installed(extension_name)
                    status = "✅ Installed" if is_installed else "❌ Not installed"
                    info_report += f"\n📂 STATUS: {status}\n"

            except Exception as e:
                info_report += f"\n⚠️  Extension manager error: {str(e)}\n"

            if not extension_found:
                info_report += f"❌ Extension '{extension_name}' not found.\n"
                info_report += f"💡 Use 'POKE DISCOVER' to see available extensions.\n"

            return info_report

        except Exception as e:
            return f"❌ Error getting extension info: {str(e)}"

    def _handle_extension_install(self, extension_name):
        """Install an extension."""
        try:
            from extensions.core.extension_manager import ExtensionManager
            ext_mgr = ExtensionManager()

            install_report = f"📦 INSTALLING EXTENSION: {extension_name}\n" + "="*50 + "\n\n"

            # Check if already installed
            if ext_mgr.check_extension_installed(extension_name):
                return f"✅ Extension '{extension_name}' is already installed.\n💡 Use 'POKE RESTART {extension_name}' to restart if needed."

            install_report += f"🔄 Installing {extension_name}...\n"

            success, message = ext_mgr.install_extension(extension_name, quiet=False)

            if success:
                install_report += f"✅ SUCCESS: {message}\n"
                install_report += f"🚀 Extension '{extension_name}' is now available.\n"
                install_report += f"💡 Use 'POKE START {extension_name}' to launch it."
            else:
                install_report += f"❌ FAILED: {message}\n"
                install_report += f"💡 Use 'POKE DISCOVER' to see available extensions."

            return install_report

        except Exception as e:
            return f"❌ Error installing extension: {str(e)}"

    def _handle_extension_uninstall(self, extension_name):
        """Uninstall an extension (placeholder for future implementation)."""
        return (f"🚧 UNINSTALL FEATURE COMING SOON\n\n"
                f"Extension uninstallation for '{extension_name}' is not yet implemented.\n"
                f"This feature will be added in a future version.\n\n"
                f"📝 For now, you can manually remove extension files from:\n"
                f"   • extensions/bundled/web/{extension_name}/\n"
                f"   • extensions/cloned/{extension_name}/\n\n"
                f"⚠️  CAUTION: Manual removal may affect system stability.")

    def _handle_extension_marketplace(self):
        """Browse the extension marketplace (placeholder for future implementation)."""
        return ("🏪 EXTENSION MARKETPLACE\n" + "="*30 + "\n\n"
                "🚧 COMING SOON: Extension Marketplace\n\n"
                "The extension marketplace will provide:\n"
                "• 🌐 Community-contributed extensions\n"
                "• 🔍 Search and discovery features\n"
                "• ⭐ Ratings and reviews\n"
                "• 🔒 Security verification\n"
                "• 📦 One-click installation\n"
                "• 🔄 Automatic updates\n\n"
                "🎯 CURRENT EXTENSIONS:\n"
                "Use 'POKE DISCOVER' to see available extensions\n"
                "Use 'POKE INFO <name>' for detailed information\n\n"
                "📧 Want to contribute? Contact the uDOS development team!")

    def handle_history(self, params, grid, parser):
        """Show variable change history - delegates to VariableHandler."""
        return self.variable_handler.handle_history(params, grid, parser)


    # ======================================================================
    # v1.0.29: GET/SET SYSTEM - Smart field access
    # ======================================================================

    def handle_get(self, params, grid, parser):
        """GET field value - delegates to VariableHandler."""
        return self.variable_handler.handle_get(params, grid, parser)

    def handle_set(self, params, grid, parser):
        """SET field value - delegates to VariableHandler."""
        return self.variable_handler.handle_set(params, grid, parser)

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.0.32: PLANET SYSTEM COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════

    def handle_config_planet(self, params, grid, parser):
        """
        Handle CONFIG PLANET commands.
        Delegates to cmd_config_planet for all planet management.

        Args:
            params: Command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Command result message
        """
        from core.commands.cmd_config_planet import cmd_config_planet

        user_data = {
            'username': getattr(self.user_manager, 'current_user', 'user') if self.user_manager else 'user'
        }

        result = cmd_config_planet(user_data, params)

        if result['success']:
            return result['message']
        else:
            return f"❌ {result['message']}"

    def handle_locate(self, params, grid, parser):
        """
        Handle LOCATE command.
        Delegates to cmd_locate for location management.

        Args:
            params: Command parameters
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Command result message
        """
        from core.commands.cmd_locate import cmd_locate

        user_data = {
            'username': getattr(self.user_manager, 'current_user', 'user') if self.user_manager else 'user'
        }

        result = cmd_locate(user_data, params)

        if result['success']:
            return result['message']
        else:
            return f"❌ {result['message']}"

    def handle_dev_mode(self, params, grid, parser):
        """Handle DEV MODE commands - delegates to EnvironmentHandler."""
        return self.environment_handler.handle_dev_mode(params, grid, parser)

    def handle_assets(self, params, grid, parser):
        """
        Handle ASSETS commands (v1.5.3+).

        Delegates to AssetsHandler for asset management operations.

        Commands:
        - ASSETS LIST [type] - List available assets
        - ASSETS SEARCH <query> - Search for assets
        - ASSETS INFO <name> - Show asset details
        - ASSETS PREVIEW <name> - Preview asset contents
        - ASSETS LOAD <name> - Load asset into memory
        - ASSETS STATS - Show asset statistics
        - ASSETS RELOAD <name> - Hot-reload asset
        - ASSETS HELP - Show help

        Args:
            params: Command parameters
            grid: Grid object
            parser: Parser object

        Returns:
            Command response
        """
        from core.commands.assets_handler import handle_assets_command
        return handle_assets_command(params, grid, parser)

