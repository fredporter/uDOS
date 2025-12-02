"""
uDOS v1.1.16 - BACKUP Command Handler

Handles file backup operations with .archive/ integration.

Commands:
- BACKUP <file>              - Create timestamped backup
- BACKUP <file> --to <path>  - Backup to specific archive
- BACKUP LIST [file]         - List backups for file
- BACKUP RESTORE <backup>    - Restore a backup
- BACKUP CLEAN [days]        - Clean old backups (default: 30 days)
- BACKUP HELP                - Show help
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from .base_handler import BaseCommandHandler


class BackupHandler(BaseCommandHandler):
    """Handler for file backup operations."""

    def handle(self, params: List[str], grid, parser) -> str:
        """
        Route BACKUP commands to appropriate handlers.

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()

        if subcommand == 'HELP':
            return self._show_help()
        elif subcommand == 'LIST':
            return self._list_backups(params[1:])
        elif subcommand == 'RESTORE':
            return self._restore_backup(params[1:])
        elif subcommand == 'CLEAN':
            return self._clean_backups(params[1:])
        else:
            # Default: create backup
            return self._create_backup(params)

    def _create_backup(self, params: List[str]) -> str:
        """Create timestamped backup of file."""
        from core.utils.archive_manager import ArchiveManager

        if not params:
            return "❌ No file specified\nUsage: BACKUP <file> [--to <archive_path>]"

        # Parse file path
        file_path = Path(params[0])
        if not file_path.exists():
            return f"❌ File not found: {file_path}"

        if not file_path.is_file():
            return f"❌ Not a file: {file_path}"

        # Parse custom archive path
        archive_path = None
        if '--to' in params:
            idx = params.index('--to')
            if idx + 1 < len(params):
                archive_path = Path(params[idx + 1]) / '.archive'

        try:
            # Create backup
            archive_mgr = ArchiveManager()
            backup_path = archive_mgr.add_backup(file_path, archive_path)

            # Get backup info
            size = backup_path.stat().st_size
            size_kb = round(size / 1024, 2)

            return (
                "✅ Backup created successfully\n\n"
                f"File:    {file_path.name}\n"
                f"Backup:  {backup_path.name}\n"
                f"Size:    {size_kb} KB\n"
                f"Archive: {backup_path.parent}\n\n"
                f"💡 Restore with: BACKUP RESTORE {backup_path.name}"
            )

        except Exception as e:
            return f"❌ Backup failed: {str(e)}"

    def _list_backups(self, params: List[str]) -> str:
        """List backups for a file or all backups."""
        from core.utils.archive_manager import ArchiveManager

        # Determine what to list
        if params:
            # List backups for specific file
            filename = params[0]
            return self._list_file_backups(filename)
        else:
            # List all backups in workspace
            return self._list_all_backups()

    def _list_file_backups(self, filename: str) -> str:
        """List backups for specific file."""
        from core.utils.archive_manager import ArchiveManager

        archive_mgr = ArchiveManager()

        # Search for backups across workspace
        backups = []
        for archive_stats in archive_mgr.scan_archives():
            archive_path = Path(archive_stats['path'])
            backups_dir = archive_path / 'backups'

            if backups_dir.exists():
                # Find backups matching filename
                pattern = f"*_{filename}"
                for backup in sorted(backups_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True):
                    backups.append({
                        'path': backup,
                        'name': backup.name,
                        'size': backup.stat().st_size,
                        'modified': datetime.fromtimestamp(backup.stat().st_mtime)
                    })

        if not backups:
            return f"No backups found for: {filename}"

        # Format output
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            f"║  Backups for: {filename:<45} ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Found {len(backups)} backup(s):{' ' * (45 - len(str(len(backups))))} ║",
            "╠═══════════════════════════════════════════════════════════╣"
        ]

        for i, backup in enumerate(backups, 1):
            timestamp = backup['modified'].strftime('%Y-%m-%d %H:%M:%S')
            size_kb = round(backup['size'] / 1024, 2)
            lines.append(f"║  {i}. {backup['name'][:50]:<50} ║")
            lines.append(f"║     {timestamp}  {size_kb} KB{' ' * (34 - len(str(size_kb)))} ║")
            if i < len(backups):
                lines.append("║  ─────────────────────────────────────────────────────────  ║")

        lines.extend([
            "╠═══════════════════════════════════════════════════════════╣",
            "║  💡 Restore with: BACKUP RESTORE <backup_name>             ║",
            "╚═══════════════════════════════════════════════════════════╝"
        ])

        return '\n'.join(lines)

    def _list_all_backups(self) -> str:
        """List all backups in workspace."""
        from core.utils.archive_manager import ArchiveManager

        archive_mgr = ArchiveManager()
        archives = archive_mgr.scan_archives()

        total_backups = 0
        archive_details = []

        for archive_stats in archives:
            backup_count = archive_stats['subdirs'].get('backups', {}).get('file_count', 0)
            if backup_count > 0:
                total_backups += backup_count
                archive_details.append({
                    'path': archive_stats['path'],
                    'count': backup_count,
                    'size_mb': archive_stats['subdirs']['backups']['size_mb']
                })

        if total_backups == 0:
            return "No backups found in workspace"

        # Format output
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            "║  All Backups in Workspace                                 ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Total Backups: {total_backups:<42} ║",
            f"║  Archives:      {len(archive_details):<42} ║",
            "╠═══════════════════════════════════════════════════════════╣"
        ]

        for detail in archive_details:
            path_short = str(detail['path'])[-50:]
            lines.append(f"║  • {path_short:<55} ║")
            lines.append(f"║    {detail['count']} backup(s), {detail['size_mb']:.2f} MB{' ' * (40 - len(str(detail['count'])) - len(f'{detail['size_mb']:.2f}'))} ║")

        lines.extend([
            "╠═══════════════════════════════════════════════════════════╣",
            "║  💡 List specific file: BACKUP LIST <filename>             ║",
            "╚═══════════════════════════════════════════════════════════╝"
        ])

        return '\n'.join(lines)

    def _restore_backup(self, params: List[str]) -> str:
        """Restore a backup file."""
        if not params:
            return "❌ No backup specified\nUsage: BACKUP RESTORE <backup_name> [--to <path>]"

        backup_name = params[0]

        # Parse custom restore path
        restore_path = None
        if '--to' in params:
            idx = params.index('--to')
            if idx + 1 < len(params):
                restore_path = Path(params[idx + 1])

        # Find the backup
        from core.utils.archive_manager import ArchiveManager
        archive_mgr = ArchiveManager()

        backup_file = None
        for archive_stats in archive_mgr.scan_archives():
            archive_path = Path(archive_stats['path'])
            backups_dir = archive_path / 'backups'

            if backups_dir.exists():
                candidate = backups_dir / backup_name
                if candidate.exists():
                    backup_file = candidate
                    break

        if not backup_file:
            return f"❌ Backup not found: {backup_name}"

        try:
            # Extract original filename (remove timestamp prefix)
            original_name = "_".join(backup_name.split("_")[2:])

            # Determine restore path
            if restore_path is None:
                restore_path = backup_file.parent.parent.parent / original_name

            # Restore (copy, don't move)
            import shutil
            shutil.copy2(backup_file, restore_path)

            return (
                "✅ Backup restored successfully\n\n"
                f"Backup:   {backup_name}\n"
                f"Restored: {restore_path}\n"
                f"Size:     {round(restore_path.stat().st_size / 1024, 2)} KB"
            )

        except Exception as e:
            return f"❌ Restore failed: {str(e)}"

    def _clean_backups(self, params: List[str]) -> str:
        """Clean old backups beyond retention period."""
        from core.utils.archive_manager import ArchiveManager

        # Parse retention days
        retention_days = 30  # default
        if params and params[0].isdigit():
            retention_days = int(params[0])

        dry_run = '--dry-run' in params

        archive_mgr = ArchiveManager()
        archives = archive_mgr.scan_archives()

        # Clean each archive
        total_cleaned = 0
        details = []

        for archive_stats in archives:
            archive_path = Path(archive_stats['path'])
            purged = archive_mgr.purge_old_files(archive_path, dry_run=dry_run)

            backup_count = len(purged.get('backups', []))
            if backup_count > 0:
                total_cleaned += backup_count
                details.append({
                    'path': str(archive_path),
                    'count': backup_count
                })

        # Format output
        mode_text = "Would clean" if dry_run else "Cleaned"
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            f"║  Backup Cleanup ({mode_text}){' ' * (35 - len(mode_text))} ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Retention: {retention_days} days{' ' * (45 - len(str(retention_days)))} ║",
            f"║  Backups {mode_text.lower()}: {total_cleaned:<36} ║"
        ]

        if details:
            lines.append("╠═══════════════════════════════════════════════════════════╣")
            for detail in details:
                path_short = str(detail['path'])[-50:]
                lines.append(f"║  • {path_short}: {detail['count']} file(s){' ' * (45 - len(path_short) - len(str(detail['count'])))} ║")

        lines.append("╠═══════════════════════════════════════════════════════════╣")
        if dry_run:
            lines.append("║  💡 Run without --dry-run to actually delete              ║")
        else:
            lines.append("║  ✅ Cleanup complete                                      ║")
        lines.append("╚═══════════════════════════════════════════════════════════╝")

        return '\n'.join(lines)

    def _show_help(self) -> str:
        """Show BACKUP command help."""
        return """╔═══════════════════════════════════════════════════════════╗
║                BACKUP Command Reference                   ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  BACKUP <file>                                            ║
║    Create timestamped backup of file                      ║
║    Example: BACKUP config.json                            ║
║                                                           ║
║  BACKUP <file> --to <path>                                ║
║    Backup to specific archive directory                   ║
║    Example: BACKUP data.json --to memory/system           ║
║                                                           ║
║  BACKUP LIST [file]                                       ║
║    List all backups or backups for specific file          ║
║    Example: BACKUP LIST config.json                       ║
║                                                           ║
║  BACKUP RESTORE <backup_name>                             ║
║    Restore a backup to original location                  ║
║    Example: BACKUP RESTORE 20251203_120000_config.json    ║
║                                                           ║
║  BACKUP RESTORE <backup_name> --to <path>                 ║
║    Restore backup to custom location                      ║
║                                                           ║
║  BACKUP CLEAN [days]                                      ║
║    Clean backups older than N days (default: 30)          ║
║    Example: BACKUP CLEAN 60                               ║
║                                                           ║
║  BACKUP CLEAN --dry-run                                   ║
║    Preview what would be deleted                          ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║  Backup Format:                                           ║
║    YYYYMMDD_HHMMSS_original_filename.ext                  ║
║    Example: 20251203_143022_config.json                   ║
║                                                           ║
║  Storage Location:                                        ║
║    <file_directory>/.archive/backups/                     ║
║                                                           ║
║  Retention Policy:                                        ║
║    Default: 30 days                                       ║
║    Configurable via metadata.json                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝"""


def create_handler(**kwargs) -> BackupHandler:
    """Factory function for handler creation."""
    return BackupHandler(**kwargs)
