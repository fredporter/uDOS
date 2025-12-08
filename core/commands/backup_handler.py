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
from typing import List, Optional, Dict, Any
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
        elif subcommand == 'STATS':
            return self._show_backup_stats(params[1:])
        elif subcommand == 'BATCH':
            return self._batch_backup(params[1:])
        elif subcommand == 'DEDUPE':
            return self._dedupe_backups(params[1:])
        elif subcommand == 'RETENTION':
            return self._retention_policy(params[1:])
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
            count_str = str(detail['count'])
            size_str = f"{detail['size_mb']:.2f}"
            padding = ' ' * (40 - len(count_str) - len(size_str))
            lines.append(f"║  • {path_short:<55} ║")
            lines.append(f"║    {count_str} backup(s), {size_str} MB{padding} ║")

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
            space_saved_str = f"{stats['space_saved_mb']:.2f}"
            compression_str = f"{stats['compression_ratio']:.1f}"
            space_padding = ' ' * (34 - len(space_saved_str))
            compression_padding = ' ' * (36 - len(compression_str))
            
            return (
                "╔═══════════════════════════════════════════════════════════╗\n"
                "║  Backup Compression Complete                              ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                f"║  Files compressed:  {stats['files_compressed']:<38} ║\n"
                f"║  Space saved:       {space_saved_str} MB{space_padding} ║\n"
                f"║  Compression ratio: {compression_str}%{compression_padding} ║\n"
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

            size_mb = stats['total_size'] / (1024*1024)
            size_str = f"{size_mb:.2f} MB"
            padding = ' ' * (45 - len(size_str))

            return (
                "╔═══════════════════════════════════════════════════════════╗\n"
                "║  Index Rebuild Complete                                   ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                f"║  Files indexed:     {stats['file_count']:<37} ║\n"
                f"║  Backups indexed:   {stats['backup_count']:<37} ║\n"
                f"║  Total size:        {size_str}{padding} ║\n"
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

            size_mb = stats['total_size'] / (1024*1024)
            size_str = f"{size_mb:.2f} MB"
            padding = ' ' * (45 - len(size_str))

            lines = [
                "╔═══════════════════════════════════════════════════════════╗",
                "║  Backup Index Statistics                                  ║",
                "╠═══════════════════════════════════════════════════════════╣",
                f"║  Files tracked:     {stats['file_count']:<37} ║",
                f"║  Backups tracked:   {stats['backup_count']:<37} ║",
                f"║  Total size:        {size_str}{padding} ║",
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

    def _show_backup_stats(self, params: List[str]) -> str:
        """Show comprehensive backup statistics dashboard."""
        from core.utils.archive_index import get_archive_index
        from core.utils.archive_manager import ArchiveManager

        try:
            index = get_archive_index()
            stats = index.get_stats()
            archive_mgr = ArchiveManager()

            # Get all archives for additional stats
            archives = archive_mgr.scan_archives()

            # Calculate totals
            total_files = stats['file_count']
            total_backups = stats['backup_count']
            total_size_mb = stats['total_size'] / (1024 * 1024)
            total_archives = len(archives)

            # Calculate savings (estimate based on backup types)
            type_breakdown = stats.get('type_breakdown', {})
            full_size = type_breakdown.get('full', {}).get('size', 0)
            incremental_size = type_breakdown.get('incremental', {}).get('size', 0)
            compressed_size = type_breakdown.get('compressed', {}).get('size', 0)

            # Estimate original size for savings calculation
            # Full backups = actual size
            # Incremental = ~10% of full (assume 90% savings)
            # Compressed = ~40% of full (assume 60% savings)
            incremental_count = type_breakdown.get('incremental', {}).get('count', 0)
            compressed_count = type_breakdown.get('compressed', {}).get('count', 0)

            estimated_full_size = full_size
            if incremental_count > 0:
                estimated_full_size += incremental_size * 10  # Assume diffs are 10% of full
            if compressed_count > 0:
                estimated_full_size += compressed_size * 2.5  # Assume compression is 40% of original

            total_savings = 0
            if estimated_full_size > 0:
                total_savings = ((estimated_full_size - stats['total_size']) / estimated_full_size) * 100

            # Build output
            lines = [
                "╔═══════════════════════════════════════════════════════════╗",
                "║              BACKUP SYSTEM STATISTICS                     ║",
                "╠═══════════════════════════════════════════════════════════╣",
                "║  Overview                                                 ║",
                "╠═══════════════════════════════════════════════════════════╣",
                f"║  Files tracked:        {total_files:>6}                            ║",
                f"║  Total backups:        {total_backups:>6}                            ║",
                f"║  Archive directories:  {total_archives:>6}                            ║",
                f"║  Total storage:        {total_size_mb:>8.2f} MB                    ║",
            ]

            if total_savings > 0:
                lines.append(f"║  Space savings:        {total_savings:>6.1f}%                          ║")

            lines.extend([
                "╠═══════════════════════════════════════════════════════════╣",
                "║  Backup Types                                             ║",
                "╠═══════════════════════════════════════════════════════════╣"
            ])

            # Show breakdown by type with ASCII bars
            if type_breakdown:
                max_count = max((t.get('count', 0) for t in type_breakdown.values()), default=1)

                for backup_type in ['full', 'incremental', 'compressed']:
                    if backup_type in type_breakdown:
                        type_stats = type_breakdown[backup_type]
                        count = type_stats['count']
                        size_mb = type_stats['size'] / (1024 * 1024)
                        percent = (count / total_backups * 100) if total_backups > 0 else 0

                        # ASCII bar (max 20 characters)
                        bar_length = int((count / max_count) * 20)
                        bar = '█' * bar_length + '░' * (20 - bar_length)

                        type_label = backup_type.capitalize()[:12].ljust(12)
                        lines.append(f"║  {type_label} {bar} {count:>5} ({percent:>5.1f}%) ║")
                        lines.append(f"║    Size: {size_mb:>8.2f} MB                                  ║")

            lines.extend([
                "╠═══════════════════════════════════════════════════════════╣",
                "║  Top 5 Most Backed Up Files                               ║",
                "╠═══════════════════════════════════════════════════════════╣"
            ])

            # Get top files by backup count
            top_files = self._get_top_backed_up_files(index, limit=5)
            if top_files:
                for i, file_info in enumerate(top_files, 1):
                    name = file_info['file_name'][:35]
                    count = file_info['backup_count']
                    size_mb = file_info['total_backup_size'] / (1024 * 1024)
                    lines.append(f"║  {i}. {name:<35} {count:>3} backups ║")
                    lines.append(f"║     {size_mb:>6.2f} MB total                                  ║")
            else:
                lines.append("║  No files with backups found                              ║")

            lines.extend([
                "╠═══════════════════════════════════════════════════════════╣",
                "║  Storage Efficiency                                       ║",
                "╠═══════════════════════════════════════════════════════════╣"
            ])

            # Calculate average backup size
            avg_backup_size = (stats['total_size'] / total_backups) if total_backups > 0 else 0
            avg_backup_kb = avg_backup_size / 1024

            lines.append(f"║  Average backup size:  {avg_backup_kb:>8.2f} KB                    ║")
            lines.append(f"║  Backups per file:     {total_backups / total_files if total_files > 0 else 0:>8.2f}                      ║")

            # Show compression and incremental effectiveness
            if incremental_count > 0:
                inc_avg_kb = (incremental_size / incremental_count / 1024) if incremental_count > 0 else 0
                lines.append(f"║  Avg incremental size: {inc_avg_kb:>8.2f} KB (vs ~{inc_avg_kb*10:.0f} KB full) ║")

            if compressed_count > 0:
                comp_avg_kb = (compressed_size / compressed_count / 1024) if compressed_count > 0 else 0
                full_avg_kb = (full_size / type_breakdown.get('full', {}).get('count', 1) / 1024)
                comp_ratio = (comp_avg_kb / full_avg_kb * 100) if full_avg_kb > 0 else 0
                lines.append(f"║  Avg compressed size:  {comp_avg_kb:>8.2f} KB ({comp_ratio:.0f}% of full)      ║")

            lines.extend([
                "╠═══════════════════════════════════════════════════════════╣",
                f"║  Last updated: {stats['last_updated'][:19]:<37} ║",
                "╠═══════════════════════════════════════════════════════════╣",
                "║  💡 Use BACKUP SEARCH to find specific backups            ║",
                "║  💡 Use BACKUP INDEX REBUILD to refresh stats             ║",
                "╚═══════════════════════════════════════════════════════════╝"
            ])

            return '\n'.join(lines)

        except Exception as e:
            return f"❌ Failed to generate stats: {str(e)}"

    def _get_top_backed_up_files(self, index, limit: int = 5) -> List[Dict[str, Any]]:
        """Get files with most backups."""
        import sqlite3

        conn = sqlite3.connect(str(index.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                f.id as file_id,
                f.name as file_name,
                COUNT(b.id) as backup_count,
                SUM(b.size) as total_backup_size
            FROM files f
            LEFT JOIN backups b ON f.id = b.file_id
            GROUP BY f.id
            HAVING backup_count > 0
            ORDER BY backup_count DESC, total_backup_size DESC
            LIMIT ?
        ''', (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'file_id': row['file_id'],
                'file_name': row['file_name'],
                'backup_count': row['backup_count'],
                'total_backup_size': row['total_backup_size'] or 0
            })

        conn.close()
        return results

    def _batch_backup(self, params: List[str]) -> str:
        """Create backups for multiple files matching pattern.

        Args:
            params: Command parameters - pattern or --list <file>

        Returns:
            Summary of batch backup operation
        """
        import glob
        from core.utils.archive_manager import ArchiveManager

        if not params:
            return "❌ No pattern specified\nUsage: BACKUP BATCH <pattern> [--compress] [--incremental]"

        # Check if using --list option for file list
        use_list = False
        list_file = None
        pattern = None
        flags = []

        i = 0
        while i < len(params):
            if params[i] == '--list' and i + 1 < len(params):
                use_list = True
                list_file = params[i + 1]
                i += 2
            elif params[i].startswith('--'):
                flags.append(params[i])
                i += 1
            else:
                pattern = params[i]
                i += 1

        # Get file list
        files_to_backup = []

        if use_list:
            # Read files from list file
            list_path = Path(list_file)
            if not list_path.exists():
                return f"❌ List file not found: {list_file}"

            try:
                with open(list_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            file_path = Path(line)
                            if file_path.exists():
                                files_to_backup.append(file_path)
            except Exception as e:
                return f"❌ Error reading list file: {str(e)}"

        elif pattern:
            # Use glob pattern
            matches = glob.glob(pattern, recursive=True)
            for match in matches:
                file_path = Path(match)
                if file_path.is_file():  # Only backup files, not directories
                    files_to_backup.append(file_path)
        else:
            return "❌ No pattern or --list option specified"

        if not files_to_backup:
            return f"❌ No files found matching pattern: {pattern or list_file}"

        # Determine backup options
        compress = '--compress' in flags or '--gz' in flags
        incremental = '--incremental' in flags

        # Initialize counters
        total_files = len(files_to_backup)
        successful = 0
        failed = 0
        skipped = 0
        total_size = 0
        total_backup_size = 0
        failures = []

        # Create archive manager
        workspace_root = Path.cwd()
        archive_mgr = ArchiveManager(workspace_root)

        # Progress header
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            "║  Batch Backup Progress                                    ║",
            "╠═══════════════════════════════════════════════════════════╣"
        ]

        # Process each file
        for idx, file_path in enumerate(files_to_backup, 1):
            try:
                # Get file size
                file_size = file_path.stat().st_size
                total_size += file_size

                # Create backup based on flags
                if incremental:
                    result = archive_mgr.create_incremental_backup(file_path)
                    if result.get('skipped'):
                        skipped += 1
                        continue
                    backup_path = Path(result['backup_path'])
                else:
                    backup_path = archive_mgr.add_backup(file_path)

                    # Compress if requested
                    if compress:
                        original_backup_path = backup_path
                        backup_path = archive_mgr.compress_file(backup_path)

                        # Only keep compressed if smaller
                        if backup_path.stat().st_size >= original_backup_path.stat().st_size:
                            backup_path.unlink()
                            backup_path = original_backup_path
                        else:
                            original_backup_path.unlink()

                # Track backup size
                backup_size = backup_path.stat().st_size
                total_backup_size += backup_size

                # Index the backup
                backup_type = 'incremental' if incremental else 'compressed' if compress else 'full'
                compression_type = 'gzip' if compress and backup_path.suffix == '.gz' else None
                self._index_backup(file_path, backup_path, backup_type, backup_size, compression_type)

                successful += 1

            except Exception as e:
                failed += 1
                failures.append(f"{file_path.name}: {str(e)}")

        # Calculate savings
        if total_size > 0:
            savings_pct = round((1 - total_backup_size / total_size) * 100, 1)
        else:
            savings_pct = 0

        # Calculate string sizes for padding
        orig_size_str = f"{total_size / (1024*1024):.2f}"
        backup_size_str = f"{total_backup_size / (1024*1024):.2f}"
        savings_str = str(savings_pct)
        
        orig_padding = ' ' * (35 - len(orig_size_str))
        backup_padding = ' ' * (35 - len(backup_size_str))
        savings_padding = ' ' * (41 - len(savings_str))

        # Build summary
        lines.extend([
            f"║  Files processed: {total_files:<41} ║",
            f"║  Successful:      {successful:<41} ║",
            f"║  Failed:          {failed:<41} ║",
            f"║  Skipped:         {skipped:<41} ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Original size:   {orig_size_str} MB{orig_padding} ║",
            f"║  Backup size:     {backup_size_str} MB{backup_padding} ║",
            f"║  Space savings:   {savings_str}%{savings_padding} ║"
        ])

        # Add failure details if any
        if failures:
            lines.extend([
                "╠═══════════════════════════════════════════════════════════╣",
                "║  Failures:                                                ║"
            ])
            for failure in failures[:5]:  # Show first 5 failures
                failure_line = failure[:55]  # Truncate long lines
                lines.append(f"║  {failure_line:<57} ║")
            if len(failures) > 5:
                lines.append(f"║  ... and {len(failures) - 5} more{' ' * (37 - len(str(len(failures) - 5)))} ║")

        lines.append("╚═══════════════════════════════════════════════════════════╝")

        return "\n".join(lines)

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file.

        Args:
            file_path: Path to file

        Returns:
            Hexadecimal hash string
        """
        import hashlib

        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in 64KB chunks for memory efficiency
            for chunk in iter(lambda: f.read(65536), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _dedupe_backups(self, params: List[str]) -> str:
        """Find and optionally remove duplicate backups based on content hash.

        Args:
            params: Command parameters - optional flags (--remove, --dry-run)

        Returns:
            Report of duplicate backups found
        """
        import glob
        from collections import defaultdict

        # Parse flags
        remove_duplicates = '--remove' in params
        dry_run = '--dry-run' in params or not remove_duplicates

        # Find all backup files in workspace
        workspace_root = Path.cwd()
        backup_files = []

        # Search for backups in .archive directories
        for archive_dir in workspace_root.rglob('.archive'):
            if archive_dir.is_dir():
                for backup_file in archive_dir.rglob('*'):
                    if backup_file.is_file() and not backup_file.name.startswith('.'):
                        backup_files.append(backup_file)

        if not backup_files:
            return "❌ No backup files found"

        # Calculate hashes and group duplicates
        hash_to_files = defaultdict(list)
        total_files = len(backup_files)
        processed = 0

        for backup_file in backup_files:
            try:
                file_hash = self._calculate_file_hash(backup_file)
                hash_to_files[file_hash].append(backup_file)
                processed += 1
            except Exception as e:
                # Skip files that can't be read
                continue

        # Find duplicates (hashes with multiple files)
        # Sort files in each group to ensure consistent ordering (oldest first by path)
        duplicates = {}
        for h, files in hash_to_files.items():
            if len(files) > 1:
                duplicates[h] = sorted(files, key=lambda f: str(f))

        if not duplicates:
            return (
                "╔═══════════════════════════════════════════════════════════╗\n"
                "║  Deduplication Scan Complete                              ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                f"║  Files scanned:     {total_files:<37} ║\n"
                f"║  Duplicates found:  0{' ' * 37} ║\n"
                "╠═══════════════════════════════════════════════════════════╣\n"
                "║  ✅ No duplicate backups found                            ║\n"
                "╚═══════════════════════════════════════════════════════════╝"
            )

        # Count duplicate files and calculate savings
        duplicate_count = sum(len(files) - 1 for files in duplicates.values())
        duplicate_size = 0

        for files in duplicates.values():
            # Keep first file, count others as duplicates
            for duplicate_file in files[1:]:
                try:
                    duplicate_size += duplicate_file.stat().st_size
                except:
                    pass

        # Build report
        dup_size_str = f"{duplicate_size / (1024*1024):.2f}"
        dup_padding = ' ' * (27 - len(dup_size_str))
        
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            "║  Deduplication Scan Results                               ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  Files scanned:        {total_files:<34} ║",
            f"║  Unique content:       {len(hash_to_files):<34} ║",
            f"║  Duplicate groups:     {len(duplicates):<34} ║",
            f"║  Duplicate files:      {duplicate_count:<34} ║",
            f"║  Potential savings:    {dup_size_str} MB{dup_padding} ║",
            "╠═══════════════════════════════════════════════════════════╣"
        ]

        # Show sample duplicates (first 5 groups)
        lines.append("║  Duplicate Groups (showing first 5):                      ║")
        lines.append("╠═══════════════════════════════════════════════════════════╣")

        for idx, (file_hash, files) in enumerate(list(duplicates.items())[:5], 1):
            # Show hash prefix and file count
            hash_prefix = file_hash[:12]
            lines.append(f"║  Group {idx}: {hash_prefix}... ({len(files)} files){' ' * (26 - len(str(len(files))) - len(str(idx)))} ║")

            # Show first file (to keep) and duplicates
            for file_idx, file_path in enumerate(files[:3]):  # Show max 3 files per group
                rel_path = str(file_path.relative_to(workspace_root))
                if len(rel_path) > 53:
                    rel_path = "..." + rel_path[-50:]
                marker = "[KEEP]" if file_idx == 0 else "[DUP] "
                lines.append(f"║    {marker} {rel_path:<48} ║")

            if len(files) > 3:
                lines.append(f"║    ... and {len(files) - 3} more{' ' * (42 - len(str(len(files) - 3)))} ║")

        if len(duplicates) > 5:
            lines.append(f"║  ... and {len(duplicates) - 5} more groups{' ' * (33 - len(str(len(duplicates) - 5)))} ║")

        # Add action section
        lines.append("╠═══════════════════════════════════════════════════════════╣")

        if dry_run and not remove_duplicates:
            lines.extend([
                "║  Mode: DRY RUN (no changes made)                          ║",
                "║  💡 Run with --remove to delete duplicates                ║"
            ])
        elif remove_duplicates:
            # Remove duplicates (keep first file in each group)
            removed_count = 0
            removed_size = 0

            for files in duplicates.values():
                for duplicate_file in files[1:]:
                    try:
                        file_size = duplicate_file.stat().st_size
                        duplicate_file.unlink()
                        removed_count += 1
                        removed_size += file_size
                    except Exception as e:
                        # Skip files that can't be deleted
                        continue

            reclaimed_str = f"{removed_size / (1024*1024):.2f}"
            reclaimed_padding = ' ' * (31 - len(reclaimed_str))
            
            lines.extend([
                f"║  Mode: REMOVE                                             ║",
                f"║  Files removed:     {removed_count:<37} ║",
                f"║  Space reclaimed:   {reclaimed_str} MB{reclaimed_padding} ║",
                "║  ✅ Deduplication complete                                ║"
            ])

        lines.append("╚═══════════════════════════════════════════════════════════╝")

        return "\n".join(lines)

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

    def _retention_policy(self, params: List[str]) -> str:
        """Manage backup retention policies.

        Commands:
        - BACKUP RETENTION SHOW - Display current policies
        - BACKUP RETENTION SET <rule> <count> - Set retention rule
        - BACKUP RETENTION CLEAR - Clear all policies
        - BACKUP RETENTION APPLY - Apply policies now

        Rules:
        - daily <N> - Keep last N daily backups (one per day)
        - weekly <N> - Keep last N weekly backups (one per week)
        - monthly <N> - Keep last N monthly backups (one per month)
        - minimum <N> - Always keep at least N most recent backups
        """
        if not params:
            return self._show_retention_policy()

        action = params[0].upper()

        if action == 'SHOW':
            return self._show_retention_policy()
        elif action == 'SET':
            return self._set_retention_policy(params[1:])
        elif action == 'CLEAR':
            return self._clear_retention_policy()
        elif action == 'APPLY':
            return self._apply_retention_policy(params[1:])
        else:
            return "❌ Unknown retention command\nUsage: BACKUP RETENTION [SHOW|SET|CLEAR|APPLY]"

    def _load_retention_config(self) -> Dict[str, Any]:
        """Load retention policy configuration."""
        import json

        config_path = Path(__file__).parent.parent / 'memory' / 'system' / '.backup_retention.json'

        if not config_path.exists():
            # Default policies
            return {
                'daily': 7,      # Keep 7 daily backups
                'weekly': 4,     # Keep 4 weekly backups
                'monthly': 6,    # Keep 6 monthly backups
                'minimum': 3     # Always keep at least 3 most recent
            }

        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {'error': str(e)}

    def _save_retention_config(self, config: Dict[str, Any]) -> bool:
        """Save retention policy configuration."""
        import json

        config_path = Path(__file__).parent.parent / 'memory' / 'system' / '.backup_retention.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            return False

    def _show_retention_policy(self) -> str:
        """Display current retention policies."""
        config = self._load_retention_config()

        if 'error' in config:
            return f"❌ Error loading retention config: {config['error']}"

        output = []
        output.append("╔═══════════════════════════════════════╗")
        output.append("║   BACKUP RETENTION POLICIES          ║")
        output.append("╠═══════════════════════════════════════╣")

        # Show each policy
        output.append(f"║ Daily backups:    {str(config.get('daily', 'None')).ljust(19)}║")
        output.append(f"║ Weekly backups:   {str(config.get('weekly', 'None')).ljust(19)}║")
        output.append(f"║ Monthly backups:  {str(config.get('monthly', 'None')).ljust(19)}║")
        output.append(f"║ Minimum kept:     {str(config.get('minimum', 'None')).ljust(19)}║")

        output.append("╠═══════════════════════════════════════╣")
        output.append("║ Commands:                            ║")
        output.append("║ SET <rule> <count> - Update policy   ║")
        output.append("║ CLEAR - Remove all policies          ║")
        output.append("║ APPLY - Apply policies now           ║")
        output.append("╚═══════════════════════════════════════╝")

        return "\n".join(output)

    def _set_retention_policy(self, params: List[str]) -> str:
        """Set a retention policy rule."""
        if len(params) < 2:
            return "❌ Missing parameters\nUsage: BACKUP RETENTION SET <rule> <count>\nRules: daily, weekly, monthly, minimum"

        rule = params[0].lower()

        if rule not in ['daily', 'weekly', 'monthly', 'minimum']:
            return f"❌ Invalid rule '{rule}'\nValid rules: daily, weekly, monthly, minimum"

        try:
            count = int(params[1])
            if count < 0:
                return "❌ Count must be non-negative"
        except ValueError:
            return f"❌ Invalid count '{params[1]}' - must be a number"

        # Load current config
        config = self._load_retention_config()
        if 'error' in config:
            config = {}  # Start fresh if error

        # Update rule
        config[rule] = count

        # Save config
        if not self._save_retention_config(config):
            return "❌ Failed to save retention policy"

        return f"✅ Retention policy updated: {rule} = {count}"

    def _clear_retention_policy(self) -> str:
        """Clear all retention policies."""
        import json

        config_path = Path(__file__).parent.parent / 'memory' / 'system' / '.backup_retention.json'

        if config_path.exists():
            try:
                config_path.unlink()
                return "✅ All retention policies cleared"
            except Exception as e:
                return f"❌ Failed to clear policies: {e}"
        else:
            return "ℹ️  No retention policies configured"

    def _apply_retention_policy(self, params: List[str]) -> str:
        """Apply retention policies to existing backups."""
        from collections import defaultdict

        # Load retention config
        config = self._load_retention_config()
        if 'error' in config:
            return f"❌ Error loading retention config: {config['error']}"

        # Get all backup files across workspace
        root = Path(__file__).parent.parent
        archive_dirs = list(root.rglob('.archive'))

        if not archive_dirs:
            return "ℹ️  No .archive directories found"

        # Collect all backups
        all_backups = []
        for archive_dir in archive_dirs:
            backups_dir = archive_dir / 'backups'
            if backups_dir.exists():
                for backup_file in backups_dir.iterdir():
                    if backup_file.is_file():
                        all_backups.append(backup_file)

        if not all_backups:
            return "ℹ️  No backups found"

        # Group backups by original file
        file_backups = defaultdict(list)
        for backup in all_backups:
            # Extract original filename from backup name
            # Format: YYYYMMDD_HHMMSS_originalname or YYYYMMDD_HHMMSS_originalname.diff/gz
            name = backup.name
            parts = name.split('_', 2)
            if len(parts) >= 3:
                original = parts[2]
                # Remove .diff or .gz extensions
                if original.endswith('.diff'):
                    original = original[:-5]
                if original.endswith('.gz'):
                    original = original[:-3]
                file_backups[original].append(backup)

        # Apply retention policy to each file's backups
        total_removed = 0
        total_kept = 0
        total_size_freed = 0

        dry_run = '--dry-run' in params

        for original_file, backups in file_backups.items():
            # Sort by modification time (newest first)
            backups_sorted = sorted(backups, key=lambda f: f.stat().st_mtime, reverse=True)

            # Determine which backups to keep
            to_keep = set()

            # Always keep minimum most recent
            minimum = config.get('minimum', 3)
            for i in range(min(minimum, len(backups_sorted))):
                to_keep.add(backups_sorted[i])

            # Keep daily backups
            daily_count = config.get('daily', 0)
            if daily_count > 0:
                kept_days = set()
                for backup in backups_sorted:
                    backup_date = datetime.fromtimestamp(backup.stat().st_mtime).date()
                    if backup_date not in kept_days:
                        to_keep.add(backup)
                        kept_days.add(backup_date)
                        if len(kept_days) >= daily_count:
                            break

            # Keep weekly backups
            weekly_count = config.get('weekly', 0)
            if weekly_count > 0:
                kept_weeks = set()
                for backup in backups_sorted:
                    backup_date = datetime.fromtimestamp(backup.stat().st_mtime).date()
                    week_key = (backup_date.year, backup_date.isocalendar()[1])
                    if week_key not in kept_weeks:
                        to_keep.add(backup)
                        kept_weeks.add(week_key)
                        if len(kept_weeks) >= weekly_count:
                            break

            # Keep monthly backups
            monthly_count = config.get('monthly', 0)
            if monthly_count > 0:
                kept_months = set()
                for backup in backups_sorted:
                    backup_date = datetime.fromtimestamp(backup.stat().st_mtime).date()
                    month_key = (backup_date.year, backup_date.month)
                    if month_key not in kept_months:
                        to_keep.add(backup)
                        kept_months.add(month_key)
                        if len(kept_months) >= monthly_count:
                            break

            # Remove backups not in keep set
            for backup in backups_sorted:
                if backup not in to_keep:
                    size = backup.stat().st_size
                    total_size_freed += size
                    total_removed += 1
                    if not dry_run:
                        try:
                            backup.unlink()
                        except Exception:
                            pass  # Ignore errors
                else:
                    total_kept += 1

        # Format output
        output = []
        output.append("╔═══════════════════════════════════════╗")
        output.append("║   RETENTION POLICY APPLICATION       ║")
        output.append("╠═══════════════════════════════════════╣")

        mode = "DRY RUN" if dry_run else "APPLIED"
        output.append(f"║ Mode: {mode.ljust(30)}║")
        output.append("╟───────────────────────────────────────╢")
        output.append(f"║ Backups kept:     {str(total_kept).ljust(19)}║")
        output.append(f"║ Backups removed:  {str(total_removed).ljust(19)}║")

        if total_size_freed > 0:
            size_mb = total_size_freed / (1024 * 1024)
            output.append(f"║ Space freed:      {f'{size_mb:.2f} MB'.ljust(19)}║")

        output.append("╠═══════════════════════════════════════╣")
        output.append("║ Policies applied:                    ║")
        output.append(f"║ Daily: {str(config.get('daily', 0)).ljust(31)}║")
        output.append(f"║ Weekly: {str(config.get('weekly', 0)).ljust(30)}║")
        output.append(f"║ Monthly: {str(config.get('monthly', 0)).ljust(29)}║")
        output.append(f"║ Minimum: {str(config.get('minimum', 0)).ljust(29)}║")
        output.append("╚═══════════════════════════════════════╝")

        if dry_run:
            output.append("\nℹ️  Use BACKUP RETENTION APPLY (without --dry-run) to remove files")

        return "\n".join(output)

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
║  BACKUP STATS                                             ║
║    Show comprehensive backup statistics dashboard         ║
║    Displays: file/backup counts, storage usage, savings   ║
║    Includes: backup type breakdown, top files, efficiency ║
║    Example: BACKUP STATS                                  ║
║                                                           ║
║  BACKUP BATCH <pattern> [--compress] [--incremental]      ║
║    Create backups for multiple files matching pattern     ║
║    Supports glob patterns (*, **, ?) and --list option    ║
║    Example: BACKUP BATCH "*.py"                            ║
║              BACKUP BATCH "src/**/*.txt" --compress        ║
║              BACKUP BATCH --list files.txt                ║
║                                                           ║
║  BACKUP DEDUPE [--remove] [--dry-run]                      ║
║    Find and remove duplicate backups (same content)       ║
║    Uses SHA-256 hashing for content comparison            ║
║    --dry-run: Show duplicates without removing (default)  ║
║    --remove:  Delete duplicate files, keep first copy     ║
║    Example: BACKUP DEDUPE                                 ║
║              BACKUP DEDUPE --remove                       ║
║                                                           ║
║  BACKUP RETENTION [SHOW|SET|CLEAR|APPLY]                  ║
║    Manage automated backup retention policies             ║
║    SHOW - Display current policies                        ║
║    SET <rule> <count> - Update policy                     ║
║         Rules: daily, weekly, monthly, minimum            ║
║    CLEAR - Remove all policies                            ║
║    APPLY [--dry-run] - Apply policies to existing backups ║
║    Example: BACKUP RETENTION SET daily 7                  ║
║              BACKUP RETENTION SET weekly 4                ║
║              BACKUP RETENTION APPLY                       ║
║              BACKUP RETENTION APPLY --dry-run             ║
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
