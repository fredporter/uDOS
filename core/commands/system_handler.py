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

    @property
    def output_handler(self):
        """Lazy load output handler."""
        if not hasattr(self, '_output_handler') or self._output_handler is None:
            from .output_handler import OutputHandler
            self._output_handler = OutputHandler(**self.__dict__)
        return self._output_handler

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
            'HISTORY': self.handle_history,
            'SESSION': self.handle_session,
            'RESTORE': self.handle_restore,
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
        Restart the uDOS system or reload extensions.

        Variants:
            REBOOT                  - Full system restart
            REBOOT --extensions     - Reload all extensions (no core restart)
            REBOOT --extension <id> - Reload single extension
            REBOOT --validate       - Dry-run validation (no actual reload)

        Args:
            params: List with optional flags and extension ID
            grid: Grid instance (unused)
            parser: Parser instance (unused)

        Returns:
            Reboot status message or reload results
        """
        # Parse flags
        flags = [p for p in params if p.startswith('--')]
        args = [p for p in params if not p.startswith('--')]

        # Hot reload variants (v1.2.4+)
        if '--extensions' in flags or '--extension' in flags or '--validate' in flags:
            return self._handle_hot_reload(flags, args)

        # Original full system reboot
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
        output += "Welcome back to uDOS v1.2.4\n\n"

        # Set the reboot flag to trigger restart in main loop
        self.reboot_requested = True

        return output

    def _handle_hot_reload(self, flags, args):
        """
        Handle extension hot reload (REBOOT --extensions/--extension/--validate).

        Args:
            flags: List of flags (--extensions, --extension, --validate)
            args: List of arguments (extension ID for --extension)

        Returns:
            Reload result message
        """
        try:
            from core.services.extension_lifecycle import ExtensionLifecycleManager
            from core.services.extension_manager import ExtensionManager
        except ImportError as e:
            return f"❌ Hot reload not available: {e}\n💡 Falling back to full REBOOT\n"

        # Get extension manager instance
        try:
            ext_manager = ExtensionManager()
        except:
            ext_manager = None

        # Create lifecycle manager
        lifecycle = ExtensionLifecycleManager(ext_manager)

        # Determine mode
        validate_only = '--validate' in flags
        single_extension = '--extension' in flags
        all_extensions = '--extensions' in flags

        output = "\n"

        # Single extension reload
        if single_extension:
            if not args:
                return "❌ Error: --extension requires extension ID\n💡 Usage: REBOOT --extension <id>\n"

            ext_id = args[0]
            output += f"🔄 {'VALIDATING' if validate_only else 'RELOADING'} EXTENSION: {ext_id}\n\n"

            result = lifecycle.reload_extension(ext_id, validate_only)
            output += self._format_reload_result(result, validate_only)

        # All extensions reload
        elif all_extensions:
            output += f"🔄 {'VALIDATING' if validate_only else 'RELOADING'} ALL EXTENSIONS\n\n"

            results = lifecycle.reload_all_extensions(validate_only)
            for result in results:
                output += self._format_reload_result(result, validate_only)
                output += "\n"

        else:
            # Just --validate without --extension/--extensions
            return "❌ Error: --validate requires --extension <id> or --extensions\n💡 Usage: REBOOT --validate --extension <id>\n"

        return output

    def _format_reload_result(self, result, validate_only=False):
        """
        Format reload result for display.

        Args:
            result: ReloadResult object
            validate_only: Whether this was a validation-only run

        Returns:
            Formatted result string
        """
        from core.services.extension_lifecycle import ReloadResult

        if not isinstance(result, ReloadResult):
            return "❌ Invalid result format\n"

        output = ""

        if result.success:
            if validate_only:
                output += f"✅ Validation passed for '{result.extension_id}'\n"
                output += f"   📋 Extension is ready for reload\n"
            else:
                output += f"✅ Extension '{result.extension_id}' reloaded successfully!\n"
                if result.state_preserved:
                    output += f"   💾 State preserved\n"
                if result.modules_reloaded > 0:
                    output += f"   🔄 Modules reloaded: {result.modules_reloaded}\n"
                if result.commands_registered > 0:
                    output += f"   ⚡ Commands registered: {result.commands_registered}\n"
                output += f"   🚀 Changes are now active (no full restart needed)\n"
        else:
            output += f"❌ {result.message}\n"
            if result.errors:
                output += f"   📋 Errors:\n"
                for error in result.errors[:3]:  # Limit to 3 errors
                    # Shorten error messages
                    error_line = error.split('\n')[0][:80]
                    output += f"      • {error_line}\n"

        if result.warnings:
            output += f"   ⚠️  Warnings:\n"
            for warning in result.warnings[:3]:  # Limit to 3 warnings
                output += f"      • {warning}\n"

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
        """Manage web servers and extensions - delegates to OutputHandler."""
        return self.output_handler.handle_output(params, grid, parser)

    def handle_get(self, params, grid, parser):
        """GET field value - delegates to VariableHandler."""
        return self.variable_handler.handle_get(params, grid, parser)

    def handle_set(self, params, grid, parser):
        """SET field value - delegates to VariableHandler."""
        return self.variable_handler.handle_set(params, grid, parser)

    def handle_history(self, params, grid, parser):
        """HISTORY command - show variable change history - delegates to VariableHandler."""
        return self.variable_handler.handle_history(params, grid, parser)

    def handle_session(self, params, grid, parser):
        """SESSION command - session management - delegates to SessionHandler."""
        from .session_handler import SessionHandler
        session_handler = SessionHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )
        return session_handler.handle_session(params, grid, parser)

    def handle_restore(self, params, grid, parser):
        """RESTORE command - restore to previous session - delegates to SessionHandler."""
        from .session_handler import SessionHandler
        session_handler = SessionHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )
        return session_handler.handle_restore(params, grid, parser)

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

