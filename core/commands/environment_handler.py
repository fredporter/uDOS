"""
uDOS v1.1.12 - Environment Command Handler

Handles environment and workspace management: CLEAN, SETTINGS, DEV MODE
Manages sandbox cleanup, system configuration, and development mode access.
"""

from pathlib import Path
from .base_handler import BaseCommandHandler


class EnvironmentHandler(BaseCommandHandler):
    """Handler for environment and workspace management commands."""

    def handle_clean(self, params, grid, parser):
        """
        Review sandbox files and prepare for commit to memory.

        Lists all files in sandbox workspace and provides options to:
        - Move to memory/shared
        - Move to memory/private
        - Delete
        - Keep in sandbox

        Returns:
            Interactive review interface
        """
        try:
            sandbox_path = Path("sandbox")
            if not sandbox_path.exists():
                return self.output_formatter.format_warning(
                    "Sandbox is empty",
                    details={"Path": str(sandbox_path)}
                )

            # Get all files in sandbox (excluding subdirectories that are part of memory structure)
            files = []
            for item in sandbox_path.iterdir():
                if item.is_file() and not item.name.startswith('.'):
                    files.append(item)

            if not files:
                return self.output_formatter.format_info(
                    "Sandbox is clean",
                    details={"Message": "No files to review"}
                )

            # Format file list
            file_list = []
            for f in files:
                size = f.stat().st_size
                modified = f.stat().st_mtime
                from datetime import datetime
                mod_time = datetime.fromtimestamp(modified).strftime('%Y-%m-%d %H:%M')
                file_list.append(f"  • {f.name} ({size} bytes, modified {mod_time})")

            files_text = '\n'.join(file_list)

            return self.output_formatter.format_panel(
                "Sandbox Review",
                f"Found {len(files)} file(s) in sandbox:\n\n{files_text}\n\n" +
                "💡 Use FILE BATCH or WORKSPACE commands to manage these files\n" +
                "   - WORKSPACE MOVE <file> TO shared\n" +
                "   - WORKSPACE MOVE <file> TO private\n" +
                "   - DELETE <file>"
            )

        except Exception as e:
            return self.output_formatter.format_error(
                "Clean operation failed",
                details={"Error": str(e)}
            )

    def handle_settings(self, params, grid, parser):
        """
        Manage system settings.
        Delegates to ConfigurationHandler.handle_setup() for settings management.
        SETTINGS is an alias - primary command is now CONFIG.
        """
        from .configuration_handler import ConfigurationHandler

        config_handler = ConfigurationHandler(
            theme=self.theme,
            viewport=self.viewport,
            logger=self.logger,
            input_manager=getattr(self, 'input_manager', None),
            output_formatter=getattr(self, 'output_formatter', None),
            resource_manager=getattr(self, 'resource_manager', None)
        )
        return config_handler.handle_setup(params, grid, parser)

    def handle_dev_mode(self, params, grid, parser):
        """
        Handle DEV MODE commands (v1.5.0 - Master User Only).

        Commands:
        - DEV MODE ON: Enable DEV MODE (requires master password)
        - DEV MODE OFF: Disable DEV MODE
        - DEV MODE STATUS: Show current DEV MODE status
        - DEV MODE HELP: Show DEV MODE help

        Args:
            params: Command parameters ['MODE', 'ON'/'OFF'/'STATUS'/'HELP']
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result message
        """
        # Validate params
        if not params or len(params) < 2:
            return (
                "❌ Invalid DEV MODE command\n\n"
                "Usage:\n"
                "  DEV MODE ON      - Enable DEV MODE (master user only)\n"
                "  DEV MODE OFF     - Disable DEV MODE\n"
                "  DEV MODE STATUS  - Show current status\n"
                "  DEV MODE HELP    - Show detailed help"
            )

        # Parse subcommand
        if params[0].upper() != 'MODE':
            return "❌ Invalid DEV command - did you mean 'DEV MODE'?"

        subcommand = params[1].upper()

        # Route to appropriate handler
        if subcommand == 'ON':
            return self._dev_mode_enable()
        elif subcommand == 'OFF':
            return self._dev_mode_disable()
        elif subcommand == 'STATUS':
            return self._dev_mode_status()
        elif subcommand == 'HELP':
            return self._dev_mode_help()
        else:
            return f"❌ Unknown DEV MODE command: {subcommand}"

    def _dev_mode_enable(self) -> str:
        """Enable DEV MODE with password authentication."""
        success, message = self.dev_mode_manager.enable(interactive=True)
        return message

    def _dev_mode_disable(self) -> str:
        """Disable DEV MODE."""
        success, message = self.dev_mode_manager.disable()
        return message

    def _dev_mode_status(self) -> str:
        """Show current DEV MODE status."""
        status = self.dev_mode_manager.get_status()

        if not status['active']:
            return (
                "╔═══════════════════════════════════════╗\n"
                "║       DEV MODE Status                 ║\n"
                "╠═══════════════════════════════════════╣\n"
                f"║  Status: ❌ INACTIVE                  ║\n"
                f"║  Master User: {status['master_user']:<20} ║\n"
                "╚═══════════════════════════════════════╝\n\n"
                "💡 Enable with: DEV MODE ON"
            )

        return (
            "╔═══════════════════════════════════════╗\n"
            "║       DEV MODE Status                 ║\n"
            "╠═══════════════════════════════════════╣\n"
            f"║  Status: ✅ ACTIVE                    ║\n"
            f"║  User: {status['user']:<27} ║\n"
            f"║  Duration: {status['duration']:<23} ║\n"
            f"║  Commands: {status['commands_executed']:<23} ║\n"
            "╠═══════════════════════════════════════╣\n"
            "║  ⚠️  Unrestricted System Access       ║\n"
            "║  📝 All actions logged                ║\n"
            "╚═══════════════════════════════════════╝\n\n"
            f"📄 Log: {status['log_file']}"
        )

    def _dev_mode_help(self) -> str:
        """Show DEV MODE help information."""
        return (
            "╔═══════════════════════════════════════════════════════════╗\n"
            "║              DEV MODE - Master User Only                  ║\n"
            "╠═══════════════════════════════════════════════════════════╣\n"
            "║                                                           ║\n"
            "║  DEV MODE provides unrestricted access to:               ║\n"
            "║  • Dangerous system operations (DELETE, DESTROY, etc.)    ║\n"
            "║  • Development tools (debugger, profiler, test runner)    ║\n"
            "║  • Live Gemini AI coding assistance                      ║\n"
            "║  • Hot code reloading and system modification            ║\n"
            "║                                                           ║\n"
            "╠═══════════════════════════════════════════════════════════╣\n"
            "║  Commands:                                                ║\n"
            "║                                                           ║\n"
            "║  DEV MODE ON      Enable DEV MODE (password required)     ║\n"
            "║  DEV MODE OFF     Disable DEV MODE                        ║\n"
            "║  DEV MODE STATUS  Show current status                     ║\n"
            "║  DEV MODE HELP    Show this help                          ║\n"
            "║                                                           ║\n"
            "╠═══════════════════════════════════════════════════════════╣\n"
            "║  Security:                                                ║\n"
            "║                                                           ║\n"
            "║  • Requires master user credentials (.env)                ║\n"
            "║  • All operations logged to sandbox/logs/dev_mode.log      ║\n"
            "║  • Session auto-expires after 1 hour of inactivity        ║\n"
            "║  • Never enable on production systems                     ║\n"
            "║                                                           ║\n"
            "╠═══════════════════════════════════════════════════════════╣\n"
            "║  Setup:                                                   ║\n"
            "║                                                           ║\n"
            "║  1. Set UDOS_MASTER_PASSWORD in .env                      ║\n"
            "║  2. Set UDOS_MASTER_USER in .env (must match username)    ║\n"
            "║  3. Run: DEV MODE ON                                      ║\n"
            "║  4. Enter master password when prompted                   ║\n"
            "║                                                           ║\n"
            "╠═══════════════════════════════════════════════════════════╣\n"
            "║  ⚠️  WARNING:                                              ║\n"
            "║                                                           ║\n"
            "║  DEV MODE disables all safety restrictions. Use only      ║\n"
            "║  in controlled development environments. All actions      ║\n"
            "║  are irreversible and logged.                             ║\n"
            "║                                                           ║\n"
            "╚═══════════════════════════════════════════════════════════╝"
        )

    @property
    def dev_mode_manager(self):
        """Lazy load DEV MODE manager."""
        if not hasattr(self, '_dev_mode_manager') or self._dev_mode_manager is None:
            from core.services.dev_mode_manager import get_dev_mode_manager
            from core.uDOS_main import get_config
            self._dev_mode_manager = get_dev_mode_manager(config_manager=get_config())
        return self._dev_mode_manager
