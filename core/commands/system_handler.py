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

    def _get_display_handler(self):
        """Helper to create DisplayHandler with current context."""
        from .display_handler import DisplayHandler
        return DisplayHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_dashboard_handler(self):
        """Helper to create DashboardHandler with current context."""
        from .dashboard_handler import DashboardHandler
        return DashboardHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_config_handler(self):
        """Helper to create ConfigurationHandler with current context."""
        from .configuration_handler import ConfigurationHandler
        return ConfigurationHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_repair_handler(self):
        """Helper to create RepairHandler with current context."""
        from .repair_handler import RepairHandler
        return RepairHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

    def _get_shakedown_handler(self):
        """Helper to create ShakedownHandler with current context."""
        from .shakedown_handler import ShakedownHandler
        return ShakedownHandler(
            connection=self.connection,
            viewport=self.viewport,
            user_manager=self.user_manager,
            history=self.history,
            theme=self.theme,
            logger=self.logger
        )

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
        """Enhanced help system with section navigation (v1.2.9+)."""
        from .help_v2_handler import create_help_handler

        # Use new HelpV2Handler for comprehensive, navigable help
        help_handler = create_help_handler()
        return help_handler.handle(params)

    def handle_blank(self, params, grid, parser):
        """Clear screen (BLANK) - delegates to DisplayHandler."""
        return self._get_display_handler().handle_blank(params, grid, parser)

    def handle_splash(self, params, grid, parser):
        """Show splash screen - delegates to DisplayHandler."""
        return self._get_display_handler().handle_splash(params, grid, parser)

    def handle_layout(self, params, grid, parser):
        """Screen layout management - delegates to DisplayHandler."""
        return self._get_display_handler().handle_layout(params, grid, parser)

    def handle_progress(self, params, grid, parser):
        """Show progress indicators - delegates to DisplayHandler."""
        return self._get_display_handler().handle_progress(params, grid, parser)

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
            'TREE': self.handle_tree,
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
        """System diagnostics and repair - delegates to RepairHandler."""
        return self._get_repair_handler().handle_repair(params, grid, parser)

    def handle_shakedown(self, params, grid, parser):
        """Comprehensive system validation test suite - delegates to ShakedownHandler."""
        return self._get_shakedown_handler().handle(params)

    def handle_tree(self, params, grid, parser):
        """Display folder structure tree (v1.2.12)."""
        from pathlib import Path
        
        # Parse options
        show_full = '--full' in params
        show_memory_only = '--memory' in params
        
        output = []
        output.append("═" * 70)
        output.append("📁 uDOS FOLDER STRUCTURE (v1.2.12)")
        output.append("═" * 70)
        
        root = Path.cwd()
        
        # Define v1.2.x structure with expected state
        structure = {
            'core/': {'required': True, 'description': 'Core system files'},
            'extensions/': {'required': True, 'description': 'Extension system'},
            'knowledge/': {'required': True, 'description': 'Knowledge library'},
            'memory/': {'required': True, 'description': 'User workspace'},
            'memory/ucode/': {'required': True, 'description': 'Distributable scripts'},
            'memory/ucode/tests/': {'required': True, 'description': 'Test suites (tracked)'},
            'memory/ucode/stdlib/': {'required': True, 'description': 'Standard library (tracked)'},
            'memory/ucode/examples/': {'required': True, 'description': 'Example scripts (tracked)'},
            'memory/ucode/adventures/': {'required': True, 'description': 'Adventure scripts (tracked)'},
            'memory/ucode/scripts/': {'required': True, 'description': 'User scripts (ignored)'},
            'memory/ucode/sandbox/': {'required': True, 'description': 'Experimental (ignored)'},
            'memory/workflows/': {'required': True, 'description': 'Workflow automation (ignored)'},
            'memory/system/': {'required': True, 'description': 'System config (ignored)'},
            'memory/bank/': {'required': True, 'description': 'Banking data (ignored)'},
            'memory/shared/': {'required': True, 'description': 'Community content (ignored)'},
            'memory/logs/': {'required': True, 'description': 'Session logs (ignored)'},
            'wiki/': {'required': True, 'description': 'Documentation'},
            'dev/': {'required': True, 'description': 'Development files'},
        }
        
        if show_memory_only:
            # Filter to only memory/ structure
            structure = {k: v for k, v in structure.items() if k.startswith('memory/')}
        
        # Display tree
        for folder_path, info in sorted(structure.items()):
            full_path = root / folder_path
            exists = full_path.exists()
            
            # Determine status and color
            if exists:
                if info['required']:
                    status = "🟢"
                    status_text = "OK"
                else:
                    status = "🟡"
                    status_text = "EXTRA"
            else:
                status = "🔴"
                status_text = "MISSING"
            
            # Count files if exists
            file_count = ""
            if exists and show_full:
                files = list(full_path.rglob('*'))
                file_count = f" ({len([f for f in files if f.is_file()])} files)"
            
            # Format indentation
            indent_level = folder_path.count('/')
            indent = "  " * indent_level
            
            output.append(f"{indent}{status} {folder_path:<40} {status_text:>10}{file_count}")
            
            if show_full and info.get('description'):
                output.append(f"{indent}   {info['description']}")
        
        output.append("")
        output.append("Legend:")
        output.append("  🟢 OK      - Folder exists and is required")
        output.append("  🔴 MISSING - Required folder not found")
        output.append("  🟡 EXTRA   - Non-required folder present")
        output.append("")
        output.append("Options:")
        output.append("  TREE --full    - Show file counts and descriptions")
        output.append("  TREE --memory  - Show only memory/ structure")
        output.append("")
        
        return "\n".join(output)

    def handle_status(self, params, grid, parser):
        """Display comprehensive system status - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_status(params, grid, parser)

    def handle_dashboard(self, params, grid, parser):
        """Display system dashboard - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_dashboard(params, grid, parser)

    def handle_viewport(self, params, grid, parser):
        """Display viewport visualization - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_viewport(params, grid, parser)

    def handle_palette(self, params, grid, parser):
        """Display color palette - delegates to DashboardHandler."""
        return self._get_dashboard_handler().handle_palette(params, grid, parser)

    def handle_settings(self, params, grid, parser):
        """Manage system settings - delegates to EnvironmentHandler."""
        return self.environment_handler.handle_settings(params, grid, parser)

    def handle_config(self, params, grid, parser):
        """Manage configuration files - supports CONFIG ROLE and delegates to ConfigurationHandler."""
        if params and params[0].upper() == 'ROLE':
            return self._handle_config_role(params[1:] if len(params) > 1 else [])
        return self._get_config_handler().handle_config(params, grid, parser)

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
        if flags:
            return self._handle_hot_reload(flags, args)

        # Animated progress bar reboot (matches start_udos.sh)
        import time

        steps = [
            ("Saving state", "saved"),
            ("Clearing buffers", "cleared"),
            ("Viewport detection", None),  # Special handling
            ("Configuration", "ready"),
        ]

        # Show progress for each step
        for i, (step_name, completion_msg) in enumerate(steps, 1):
            print(self._show_progress(i, len(steps), f"{step_name}..."), end="", flush=True)
            time.sleep(0.15)

            # Clear line and show completion
            if i == 3:  # Viewport detection
                try:
                    from core.services.viewport_manager import ViewportManager
                    vp = ViewportManager()
                    tier = vp.refresh_viewport()["screen_tier"]
                    size = f"{tier['actual_width_cells']}×{tier['actual_height_cells']}"
                except:
                    size = "cached"
                print(f"\r{' ' * 80}\r\033[1;32m[✓]\033[0m {step_name:<20} ({size})  ", flush=True)
            else:
                print(f"\r{' ' * 80}\r\033[1;32m[✓]\033[0m {step_name:<20} ({completion_msg})  ", flush=True)

        # Final progress bar
        print(f"\r{' ' * 80}\r{self._show_progress(len(steps), len(steps), 'System ready!')}")
        print("\n\033[1;32m[✓]\033[0m All checks passed - restarting uDOS...\n")

        self.reboot_requested = True
        return ""

    def _show_progress(self, current, total, message):
        """Show animated progress bar matching startup style."""
        width = 35
        percentage = (current * 100) // total
        filled = (current * width) // total
        bar = "┌─ " + ("█" * filled) + ("░" * (width - filled)) + " ─┐"
        return f"\r{bar} \033[1;32m{percentage:3d}%\033[0m {message}"

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
        """Destructive reset command with safety confirmations."""
        from core.commands.sandbox_handler import SandboxHandler

        destruction_type = params[0] if params else None

        # Map valid flags to modes
        mode_map = {"--reset": "reset", "--env": "env", "--all": "all"}

        if not destruction_type or destruction_type not in mode_map:
            return ("❌ DESTROY requires a flag\n\n"
                   "Available options:\n"
                   "  DESTROY --reset    Reset sandbox (safe - preserves user/tests)\n"
                   "  DESTROY --env      Clean environment files\n"
                   "  DESTROY --all      Delete all sandbox data (DANGER!)\n\n"
                   "⚠️  All DESTROY operations require confirmation")

        # Execute via sandbox handler
        return SandboxHandler().destroy_sandbox(mode=mode_map[destruction_type])

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
        return self._get_session_handler().handle_session(params, grid, parser)

    def handle_restore(self, params, grid, parser):
        """RESTORE command - restore to previous session - delegates to SessionHandler."""
        return self._get_session_handler().handle_restore(params, grid, parser)

    def _get_user_data(self):
        """Helper to get user data dictionary."""
        return {'username': getattr(self.user_manager, 'current_user', 'user') if self.user_manager else 'user'}

    def _format_cmd_result(self, result):
        """Helper to format command result with success/error prefix."""
        return result['message'] if result['success'] else f"❌ {result['message']}"

    # ═══════════════════════════════════════════════════════════════════════════
    # v1.0.32: PLANET SYSTEM COMMANDS
    # ═══════════════════════════════════════════════════════════════════════════

    def handle_config_planet(self, params, grid, parser):
        """Handle CONFIG PLANET commands - delegates to cmd_config_planet."""
        from core.commands.cmd_config_planet import cmd_config_planet
        return self._format_cmd_result(cmd_config_planet(self._get_user_data(), params))

    def handle_locate(self, params, grid, parser):
        """Handle LOCATE command - delegates to cmd_locate."""
        from core.commands.cmd_locate import cmd_locate
        return self._format_cmd_result(cmd_locate(self._get_user_data(), params))

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

