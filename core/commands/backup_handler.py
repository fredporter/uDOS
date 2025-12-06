"""
uDOS v1.1.16 - BACKUP Command Handler

Handles file backup operations with .archive/ integration.

Commands:
- BACKUP <file>                      - Create timestamped backup
- BACKUP <file> --incremental        - Create diff-based incremental backup (80-90% savings)
- BACKUP <file> --compress           - Create compressed backup (50-70% savings)
- BACKUP <file> --to <path>          - Backup to specific archive
- BACKUP LIST [file]                 - List backups for file
- BACKUP RESTORE <backup>            - Restore a backup (handles .diff and .gz)
- BACKUP CLEAN [days]                - Clean old backups (default: 30 days)
- BACKUP HELP                        - Show help

Incremental Backups:
- First backup is always full
- Subsequent --incremental backups store only changes (unified diff)
- Typical savings: 80-90% for text files with minor edits
- Unchanged files are skipped (100% savings)
- RESTORE automatically handles .diff files
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
        elif subcommand == 'COMPRESS':
            return self._compress_archives(params[1:])
        elif subcommand == 'SEARCH':
            return self._search_backups(params[1:])
        elif subcommand == 'INDEX':
            return self._manage_index(params[1:])
        else:
            # Default: create backup
            return self._create_backup(params)

    def _create_backup(self, params: List[str]) -> str:
        """Create timestamped backup of file."""
        from core.utils.archive_manager import ArchiveManager

        if not params:
            return "❌ No file specified\nUsage: BACKUP <file> [--to <archive_path>] [--compress] [--incremental]"

        # Parse file path
        file_path = Path(params[0])
        if not file_path.exists():
            return f"❌ File not found: {file_path}"

        if not file_path.is_file():
            return f"❌ Not a file: {file_path}"

        # Parse flags
        compress = '--compress' in params or '-c' in params
        incremental = '--incremental' in params or '-i' in params
        archive_path = None
        if '--to' in params:
            idx = params.index('--to')
            if idx + 1 < len(params):
                archive_path = Path(params[idx + 1]) / '.archive'

        try:
            archive_mgr = ArchiveManager()

            # Create incremental backup if requested
            if incremental:
                result = archive_mgr.create_incremental_backup(file_path, archive_path)

                if result['backup_type'] == 'unchanged':
                    return (
                        "ℹ️  No changes detected - backup skipped\n\n"
                        f"File:         {file_path.name}\n"
                        f"Last backup:  {result['base_backup'].name}\n"
                        f"Status:       Unchanged\n"
                    )

                # Add to index
                self._index_backup(
                    file_path=file_path,
                    backup_path=result['backup_path'],
                    backup_type=result['backup_type'],
                    backup_size=result['size_backup'],
                    base_backup_path=result.get('base_backup')
                )

                backup_type = "Full" if result['backup_type'] == 'full' else "Incremental (diff)"
                original_kb = round(result['size_original'] / 1024, 2)
                backup_kb = round(result['size_backup'] / 1024, 2)

                output = (
                    f"✅ {backup_type} backup created successfully\n\n"
                    f"File:         {file_path.name}\n"
                    f"Backup:       {result['backup_path'].name}\n"
                    f"Type:         {result['backup_type']}\n"
                    f"Original:     {original_kb} KB\n"
                    f"Backup size:  {backup_kb} KB\n"
                    f"Space saved:  {result['savings_percent']:.1f}%\n"
                )

                if result['base_backup']:
                    output += f"Base backup:  {result['base_backup'].name}\n"

                output += (
                    f"Archive:      {result['backup_path'].parent}\n\n"
                    f"💡 Restore with: BACKUP RESTORE {result['backup_path'].name}"
                )

                return output

            # Create regular backup
            backup_path = archive_mgr.add_backup(file_path, archive_path)

            original_size = backup_path.stat().st_size
            original_size_kb = round(original_size / 1024, 2)

            # Add to index
            self._index_backup(file_path, backup_path, 'full', original_size)

            # Compress if requested
            if compress:
                compressed_path = archive_mgr.compress_file(backup_path)
                compressed_size = compressed_path.stat().st_size
                compressed_size_kb = round(compressed_size / 1024, 2)

                # Only keep compressed if smaller
                if compressed_size < original_size:
                    backup_path.unlink()
                    backup_path = compressed_path
                    savings = round((1 - compressed_size / original_size) * 100, 1)

                    # Update index with compressed version
                    self._index_backup(file_path, backup_path, 'compressed', compressed_size, compression='gzip')

                    return (
                        "✅ Backup created and compressed successfully\n\n"
                        f"File:         {file_path.name}\n"
                        f"Backup:       {backup_path.name}\n"
                        f"Original:     {original_size_kb} KB\n"
                        f"Compressed:   {compressed_size_kb} KB\n"
                        f"Space saved:  {savings}%\n"
                        f"Archive:      {backup_path.parent}\n\n"
                        f"💡 Restore with: BACKUP RESTORE {backup_path.name}"
                    )
                else:
                    compressed_path.unlink()

            return (
                "✅ Backup created successfully\n\n"
                f"File:    {file_path.name}\n"
                f"Backup:  {backup_path.name}\n"
                f"Size:    {original_size_kb} KB\n"
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
            # Check backup type
            is_compressed = backup_file.suffix == '.gz'
            is_incremental = backup_file.suffix == '.diff'

            # Extract original filename (remove timestamp prefix)
            if is_incremental:
                filename_to_process = backup_name.replace('.diff', '')
            elif is_compressed:
                filename_to_process = backup_name.replace('.gz', '')
            else:
                filename_to_process = backup_name

            original_name = "_".join(filename_to_process.split("_")[2:])

            # Determine restore path
            if restore_path is None:
                restore_path = backup_file.parent.parent.parent / original_name

            # Restore file based on type
            if is_incremental:
                # Apply incremental backup (diff)
                restored_file = archive_mgr.apply_incremental_backup(backup_file, restore_path)
                size_kb = round(restored_file.stat().st_size / 1024, 2)

                # Get base backup info for user feedback
                with open(backup_file, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# BASE:'):
                        base_backup = first_line.split('BASE:')[1].split('|')[0].strip()
                        compression_note = f" (incremental from {base_backup})"
                    else:
                        compression_note = " (incremental backup)"

            elif is_compressed:
                # Decompress during restore
                decompressed = archive_mgr.decompress_file(backup_file, restore_path)
                size_kb = round(decompressed.stat().st_size / 1024, 2)
                compression_note = " (decompressed from .gz)"

            else:
                # Direct copy
                import shutil
                shutil.copy2(backup_file, restore_path)
                size_kb = round(restore_path.stat().st_size / 1024, 2)
                compression_note = ""

            return (
                f"✅ Backup restored successfully{compression_note}\n\n"
                f"Backup:   {backup_name}\n"
                f"Restored: {restore_path}\n"
                f"Size:     {size_kb} KB"
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

    def _compress_archives(self, params: List[str]) -> str:
        """Batch compress backups in an archive directory."""
        if not params:
            return "❌ No directory specified\nUsage: BACKUP COMPRESS <directory>"

        from core.utils.archive_manager import ArchiveManager
        archive_mgr = ArchiveManager()

        archive_path = Path(params[0])
        if not archive_path.exists():
            return f"❌ Directory not found: {archive_path}"

        if not (archive_path / '.archive').exists():
            return f"❌ Not an archive directory: {archive_path}"

        try:
            # Compress backups subdirectory
            stats = archive_mgr.compress_archive_directory(
                archive_path / '.archive',
                subdir='backups'
            )

            if stats['files_compressed'] == 0:
                return "No uncompressed backups found to compress"

            # Format output
            return (
                "╔═══════════════════════════════════════════════════════════╗\n"
                "║  Backup Compression Complete                              ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                f"║  Files compressed:  {stats['files_compressed']:<38} ║\n"
                f"║  Space saved:       {stats['space_saved_mb']:.2f} MB{' ' * (34 - len(f'{stats['space_saved_mb']:.2f}'))} ║\n"
                f"║  Compression ratio: {stats['compression_ratio']:.1f}%{' ' * (36 - len(f'{stats['compression_ratio']:.1f}'))} ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                f"║  Archive: {str(archive_path)[-47:]:<49} ║\n"
                "╚═══════════════════════════════════════════════════════════╝"
            )

        except Exception as e:
            return f"❌ Compression failed: {str(e)}"

    def _search_backups(self, params: List[str]) -> str:
        """Search for backups across workspace."""
        from core.utils.archive_index import get_archive_index

        if not params:
            return "❌ No search query specified\nUsage: BACKUP SEARCH <query> [--limit N]"

        query = params[0]
        limit = 50

        # Parse limit flag
        if '--limit' in params:
            try:
                idx = params.index('--limit')
                if idx + 1 < len(params):
                    limit = int(params[idx + 1])
            except (ValueError, IndexError):
                pass

        try:
            index = get_archive_index()
            results = index.search(query, limit=limit)

            if not results:
                return f"No backups found matching: {query}"

            # Format output
            lines = [
                "╔═══════════════════════════════════════════════════════════╗",
                f"║  Backup Search Results: '{query}'                         ║",
                "╠═══════════════════════════════════════════════════════════╣",
                f"║  Found: {len(results)} file(s)                                        ║",
                "╠═══════════════════════════════════════════════════════════╣"
            ]

            for result in results[:10]:  # Show first 10
                file_name = result['file_name'][:45]
                backup_count = result['backup_count']
                latest = result['latest_backup'] or 'N/A'
                size_mb = result['total_backup_size'] / (1024 * 1024) if result['total_backup_size'] else 0

                lines.append(f"║  📁 {file_name:<45}               ║")
                lines.append(f"║     {backup_count} backup(s) | Latest: {latest[:15]} | {size_mb:.2f} MB  ║")

            if len(results) > 10:
                lines.append("╠═══════════════════════════════════════════════════════════╣")
                lines.append(f"║  ... {len(results) - 10} more results (use --limit to see all)     ║")

            lines.extend([
                "╠═══════════════════════════════════════════════════════════╣",
                "║  💡 View details: BACKUP LIST <filename>                  ║",
                "╚═══════════════════════════════════════════════════════════╝"
            ])

            return '\n'.join(lines)

        except Exception as e:
            return f"❌ Search failed: {str(e)}"

    def _manage_index(self, params: List[str]) -> str:
        """Manage backup index (rebuild, stats)."""
        from core.utils.archive_index import get_archive_index
        from core.utils.archive_manager import ArchiveManager

        if not params:
            return self._show_index_stats()

        subcommand = params[0].upper()

        if subcommand == 'REBUILD':
            return self._rebuild_index()
        elif subcommand == 'STATS':
            return self._show_index_stats()
        else:
            return "❌ Unknown INDEX command\nUsage: BACKUP INDEX [REBUILD|STATS]"

    def _rebuild_index(self) -> str:
        """Rebuild index from all .archive directories."""
        from core.utils.archive_index import get_archive_index
        from core.utils.archive_manager import ArchiveManager

        try:
            index = get_archive_index()
            archive_mgr = ArchiveManager()

            # Get all .archive directories
            archives = archive_mgr.scan_archives()
            archive_dirs = [Path(a['path']) for a in archives]

            if not archive_dirs:
                return "No .archive directories found in workspace"

            # Progress tracking
            progress_msgs = []

            def progress_callback(current, total, message):
                if current % 50 == 0 or current == total:
                    progress_msgs.append(f"{current}/{total}: {message}")

            # Rebuild index
            index.rebuild_index(archive_dirs, progress_callback=progress_callback)

            # Get stats
            stats = index.get_stats()

            return (
                "╔═══════════════════════════════════════════════════════════╗\n"
                "║  Index Rebuild Complete                                   ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                f"║  Files indexed:     {stats['file_count']:<37} ║\n"
                f"║  Backups indexed:   {stats['backup_count']:<37} ║\n"
                f"║  Total size:        {stats['total_size'] / (1024*1024):.2f} MB{' ' * (29 - len(f\"{stats['total_size'] / (1024*1024):.2f}\"))} ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                "║  💡 Search backups: BACKUP SEARCH <query>                 ║\n"
                "╚═══════════════════════════════════════════════════════════╝"
            )

        except Exception as e:
            return f"❌ Index rebuild failed: {str(e)}"

    def _show_index_stats(self) -> str:
        """Show index statistics."""
        from core.utils.archive_index import get_archive_index

        try:
            index = get_archive_index()
            stats = index.get_stats()

            lines = [
                "╔═══════════════════════════════════════════════════════════╗",
                "║  Backup Index Statistics                                  ║",
                "╠═══════════════════════════════════════════════════════════╣",
                f"║  Files tracked:     {stats['file_count']:<37} ║",
                f"║  Backups tracked:   {stats['backup_count']:<37} ║",
                f"║  Total size:        {stats['total_size'] / (1024*1024):.2f} MB{' ' * (29 - len(f\"{stats['total_size'] / (1024*1024):.2f}\"))} ║",
                f"║  Last updated:      {stats['last_updated'][:19]:<29} ║",
                "╠═══════════════════════════════════════════════════════════╣"
            ]

            # Breakdown by type
            if stats['type_breakdown']:
                lines.append("║  Backup Types:                                            ║")
                for backup_type, type_stats in stats['type_breakdown'].items():
                    count = type_stats['count']
                    size_mb = type_stats['size'] / (1024 * 1024)
                    lines.append(f"║    {backup_type.capitalize():<15} {count:>5} backups | {size_mb:>8.2f} MB  ║")

            lines.extend([
                "╠═══════════════════════════════════════════════════════════╣",
                "║  💡 Rebuild index: BACKUP INDEX REBUILD                   ║",
                "╚═══════════════════════════════════════════════════════════╝"
            ])

            return '\n'.join(lines)

        except Exception as e:
            return f"❌ Failed to get index stats: {str(e)}"

    def _index_backup(self, file_path: Path, backup_path: Path, backup_type: str,
                      backup_size: int, compression: Optional[str] = None,
                      base_backup_path: Optional[Path] = None):
        """Add backup to search index.

        Args:
            file_path: Original file path
            backup_path: Path to backup file
            backup_type: 'full', 'incremental', or 'compressed'
            backup_size: Size of backup in bytes
            compression: Compression type ('gzip' or None)
            base_backup_path: Base backup for incremental backups
        """
        try:
            from core.utils.archive_index import get_archive_index

            # Extract timestamp from backup filename
            backup_name = backup_path.name
            name_parts = backup_name.split('_', 2)
            if len(name_parts) >= 2:
                timestamp = f"{name_parts[0]}_{name_parts[1]}"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            index = get_archive_index()
            index.add_backup(
                file_path=file_path,
                backup_path=backup_path,
                backup_type=backup_type,
                backup_size=backup_size,
                timestamp=timestamp,
                compression=compression,
                base_backup_path=base_backup_path
            )
        except Exception:
            # Silently fail indexing - don't break backup operation
            pass

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
║  BACKUP <file> --incremental (or -i)                      ║
║    Create diff-based incremental backup (80-90% savings)  ║
║    First backup is full, subsequent are diffs             ║
║    Unchanged files are skipped (100% savings)             ║
║    Example: BACKUP config.json --incremental              ║
║                                                           ║
║  BACKUP <file> --compress (or -c)                         ║
║    Create compressed backup (saves 50-70% space)          ║
║    Example: BACKUP large_file.json --compress             ║
║                                                           ║
║  BACKUP <file> --to <path>                                ║
║    Backup to specific archive directory                   ║
║    Example: BACKUP data.json --to memory/system           ║
║                                                           ║
║  BACKUP LIST [file]                                       ║
║    List all backups or backups for specific file          ║
║    Shows full and incremental (.diff) backups             ║
║    Example: BACKUP LIST config.json                       ║
║                                                           ║
║  BACKUP RESTORE <backup_name>                             ║
║    Restore a backup to original location                  ║
║    (Automatically handles .gz and .diff files)            ║
║    Example: BACKUP RESTORE 20251203_120000_config.json    ║
║              BACKUP RESTORE 20251203_120000_config.diff   ║
║                                                           ║
║  BACKUP RESTORE <backup_name> --to <path>                 ║
║    Restore backup to custom location                      ║
║                                                           ║
║  BACKUP COMPRESS <directory>                              ║
║    Batch compress all backups in archive directory        ║
║    Example: BACKUP COMPRESS memory/workflows/.archive     ║
║                                                           ║
║  BACKUP SEARCH <query> [--limit N]                        ║
║    Search for backups across workspace (fuzzy match)      ║
║    Example: BACKUP SEARCH config                          ║
║              BACKUP SEARCH workflow --limit 100           ║
║                                                           ║
║  BACKUP INDEX [REBUILD|STATS]                             ║
║    Manage backup search index                             ║
║    REBUILD - Scan all .archive directories and rebuild    ║
║    STATS   - Show index statistics                        ║
║    Example: BACKUP INDEX REBUILD                          ║
║              BACKUP INDEX STATS                           ║
║                                                           ║
║  BACKUP CLEAN [days]                                      ║
║    Clean backups older than N days (default: 30)          ║
║    Example: BACKUP CLEAN 60                               ║
║                                                           ║
║  BACKUP CLEAN --dry-run                                   ║
║    Preview what would be deleted                          ║
║                                                           ║
╠═══════════════════════════════════════════════════════════╣
║  Search & Indexing:                                       ║
║    SQLite-based index for fast search across workspace    ║
║    Auto-updates when backups are created                  ║
║    Fuzzy matching on file names and paths                 ║
║    Run BACKUP INDEX REBUILD after restoring from cloud    ║
║                                                           ║
║  Incremental Backups (.diff files):                       ║
║    Uses unified diff format to store only changes         ║
║    80-90% savings for text files with minor edits         ║
║    Binary files automatically use full backup             ║
║    Unchanged files are skipped (100% savings)             ║
║    RESTORE automatically reconstructs original            ║
║                                                           ║
║  Compression (.gz files):                                 ║
║    Uses gzip compression (50-70% savings for text files)  ║
║    Only keeps compressed if smaller than original         ║
║    Decompression is automatic during RESTORE              ║
║                                                           ║
║  Backup Formats:                                          ║
║    Regular:     YYYYMMDD_HHMMSS_original_filename.ext     ║
║    Compressed:  YYYYMMDD_HHMMSS_original_filename.ext.gz  ║
║    Incremental: YYYYMMDD_HHMMSS_original_filename.diff    ║
║                                                           ║
║    Example: 20251203_143022_config.json                   ║
║             20251203_143022_config.json.gz                ║
║             20251203_143022_config.diff                   ║
║                                                           ║
║  Storage Location:                                        ║
║    <file_directory>/.archive/backups/                     ║
║    Index database: ~/.udos/archive_index.db               ║
║                                                           ║
║  Retention Policy:                                        ║
║    Default: 30 days                                       ║
║    Configurable via metadata.json                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝"""


def create_handler(**kwargs) -> BackupHandler:
    """Factory function for handler creation."""
    return BackupHandler(**kwargs)
