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
        Clean workspace files and manage archives.

        Commands:
        - CLEAN              - Review sandbox files (legacy behavior)
        - CLEAN --scan       - Scan all .archive/ folders for statistics
        - CLEAN --purge [N]  - Purge old archive files (default: 30 days)
        - CLEAN --dry-run    - Preview what would be purged
        - CLEAN --path <dir> - Clean specific directory's .archive/

        Returns:
            Cleanup results or interactive review
        """
        try:
            # Parse flags
            scan_mode = '--scan' in params
            purge_mode = '--purge' in params
            dry_run = '--dry-run' in params

            # Get custom path if specified
            custom_path = None
            if '--path' in params:
                idx = params.index('--path')
                if idx + 1 < len(params):
                    custom_path = Path(params[idx + 1])

            # Get custom retention days if specified with --purge
            retention_days = 30  # default
            if purge_mode:
                idx = params.index('--purge')
                if idx + 1 < len(params) and params[idx + 1].isdigit():
                    retention_days = int(params[idx + 1])

            # Route to appropriate handler
            if scan_mode:
                return self._clean_scan_archives(custom_path)
            elif purge_mode or dry_run:
                return self._clean_purge_archives(retention_days, dry_run, custom_path)
            else:
                # Legacy behavior: review sandbox files
                return self._clean_review_sandbox()

        except Exception as e:
            return self.output_formatter.format_error(
                "Clean operation failed",
                details={"Error": str(e)}
            )

    def _clean_review_sandbox(self):
        """Legacy CLEAN behavior: review sandbox files."""
        sandbox_path = Path("sandbox")
        if not sandbox_path.exists():
            return self.output_formatter.format_warning(
                "Sandbox is empty",
                details={"Path": str(sandbox_path)}
            )

        # Get all files in sandbox (excluding subdirectories)
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
            "   - DELETE <file>\n\n" +
            "💡 Use CLEAN --scan to check .archive/ folders"
        )

    def _clean_scan_archives(self, custom_path=None):
        """Scan workspace for .archive/ folders and show statistics."""
        from core.utils.archive_manager import ArchiveManager

        # Determine scan path
        scan_path = custom_path if custom_path else Path.cwd()

        archive_mgr = ArchiveManager(scan_path)
        metrics = archive_mgr.get_health_metrics()

        if metrics['total_archives'] == 0:
            return self.output_formatter.format_info(
                "No archives found",
                details={"Path": str(scan_path)}
            )

        # Build output
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            "║         Archive System Health Report (v1.1.16)           ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Total Archives: {metrics['total_archives']:<42} ║",
            f"║  Total Files:    {metrics['total_files']:<42} ║",
            f"║  Total Size:     {metrics['total_size_mb']:.2f} MB{' ' * (42 - len(f'{metrics['total_size_mb']:.2f} MB'))} ║",
            "╠═══════════════════════════════════════════════════════════╣"
        ]

        # Show individual archives
        lines.append("║  Archives:                                                ║")
        for archive in metrics['archives']:
            path_short = str(archive['path'])[-50:]
            lines.append(f"║  • {path_short:<55} ║")
            lines.append(f"║    Files: {archive['total_files']:<3}  Size: {archive['total_size_mb']:.2f} MB{' ' * (35 - len(f'{archive['total_size_mb']:.2f} MB'))} ║")

        # Show warnings
        if metrics['warnings']:
            lines.append("╠═══════════════════════════════════════════════════════════╣")
            lines.append("║  ⚠️  Warnings:                                             ║")
            for warning in metrics['warnings']:
                # Wrap long warnings
                if len(warning) > 55:
                    warning = warning[:52] + "..."
                lines.append(f"║  {warning:<57} ║")

        lines.append("╠═══════════════════════════════════════════════════════════╣")
        lines.append("║  Commands:                                                ║")
        lines.append("║  CLEAN --purge [days]  - Remove old archive files         ║")
        lines.append("║  CLEAN --dry-run       - Preview what would be deleted    ║")
        lines.append("║  CLEAN --path <dir>    - Clean specific directory         ║")
        lines.append("╚═══════════════════════════════════════════════════════════╝")

        return '\n'.join(lines)

    def _clean_purge_archives(self, retention_days=30, dry_run=False, custom_path=None):
        """Purge old files from archives."""
        from core.utils.archive_manager import ArchiveManager
        from datetime import datetime

        # Determine scan path
        scan_path = custom_path if custom_path else Path.cwd()

        archive_mgr = ArchiveManager(scan_path)
        archives = archive_mgr.scan_archives(scan_path)

        if not archives:
            return self.output_formatter.format_info(
                "No archives found to purge",
                details={"Path": str(scan_path)}
            )

        # Purge each archive
        total_purged = {"deleted": 0, "backups": 0, "versions": 0}
        purge_details = []

        for archive_stats in archives:
            archive_path = Path(archive_stats['path'])
            purged = archive_mgr.purge_old_files(archive_path, dry_run=dry_run)

            # Count totals
            for category in purged:
                total_purged[category] += len(purged[category])

            # Record details if files were purged
            if any(purged.values()):
                purge_details.append({
                    'path': str(archive_path),
                    'purged': purged
                })

        # Build output
        mode_text = "DRY RUN - Would purge" if dry_run else "Purged"
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            f"║  Archive Cleanup Report ({mode_text}){' ' * (23 - len(mode_text))} ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Retention Policy: {retention_days} days{' ' * (38 - len(str(retention_days)))} ║",
            f"║  Archives Scanned: {len(archives):<39} ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Deleted Files:  {total_purged['deleted']:<42} ║",
            f"║  Backup Files:   {total_purged['backups']:<42} ║",
            f"║  Version Files:  {total_purged['versions']:<42} ║",
            f"║  Total:          {sum(total_purged.values()):<42} ║"
        ]

        # Show details
        if purge_details:
            lines.append("╠═══════════════════════════════════════════════════════════╣")
            lines.append("║  Details:                                                 ║")
            for detail in purge_details:
                path_short = str(detail['path'])[-50:]
                lines.append(f"║  • {path_short:<55} ║")
                for category, files in detail['purged'].items():
                    if files:
                        lines.append(f"║    {category}: {len(files)} file(s){' ' * (41 - len(category) - len(str(len(files))))} ║")

        lines.append("╠═══════════════════════════════════════════════════════════╣")
        if dry_run:
            lines.append("║  💡 Run without --dry-run to actually delete files        ║")
        else:
            lines.append("║  ✅ Cleanup complete                                      ║")
        lines.append("╚═══════════════════════════════════════════════════════════╝")

        return '\n'.join(lines)

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
