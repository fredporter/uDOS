"""
uDOS v1.1.16 - UNDO/REDO Command Handler

Handles version history tracking and file restoration.

Commands:
- UNDO [file]               - Revert file to previous version
- UNDO --list [file]        - List available versions
- UNDO --to-version <ver>   - Revert to specific version
- REDO [file]               - Re-apply undone changes
- UNDO HELP                 - Show help
"""

from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from .base_handler import BaseCommandHandler


class UndoHandler(BaseCommandHandler):
    """Handler for undo/redo operations using version history."""

    # Track redo stack per file (in-memory for session)
    _redo_stack: Dict[str, List[str]] = {}

    def handle(self, params: List[str], grid, parser) -> str:
        """
        Route UNDO/REDO commands to appropriate handlers.

        Args:
            params: Command parameters
            grid: Grid instance
            parser: Parser instance

        Returns:
            Command result message
        """
        if not params:
            return "❌ No parameters specified\nUsage: UNDO <file> [--list] [--to-version <version>]"

        # Check for flags
        if '--list' in params:
            filename = params[0] if params[0] != '--list' else None
            return self._list_versions(filename)

        if '--to-version' in params:
            idx = params.index('--to-version')
            if idx + 1 >= len(params):
                return "❌ No version specified\nUsage: UNDO --to-version <version_name> <file>"
            version_name = params[idx + 1]
            # File should be before or after --to-version
            filename = params[0] if params[0] != '--to-version' else params[idx + 2]
            return self._revert_to_version(filename, version_name)

        if params[0].upper() == 'HELP':
            return self._show_help()

        # Default: undo last change
        filename = params[0]
        return self._undo_file(filename)

    def handle_redo(self, params: List[str], grid, parser) -> str:
        """Handle REDO command."""
        if not params:
            return "❌ No file specified\nUsage: REDO <file>"

        filename = params[0]
        return self._redo_file(filename)

    def _is_unified_tasks_file(self, filename: str) -> bool:
        """Check if file is unified_tasks.json (v1.2.23)."""
        return 'unified_tasks.json' in filename
    
    def _undo_file(self, filename: str) -> str:
        """Revert file to previous version."""
        from core.utils.archive_manager import ArchiveManager

        file_path = Path(filename)
        if not file_path.exists():
            return f"❌ File not found: {filename}"
        
        # v1.2.23: Special handling for unified_tasks.json
        if self._is_unified_tasks_file(filename):
            return self._undo_unified_tasks(file_path)

        # Find versions for this file
        archive_mgr = ArchiveManager()
        versions = self._get_file_versions(filename, archive_mgr)

        if not versions:
            return f"❌ No version history found for: {filename}"

        if len(versions) < 2:
            return f"❌ No previous version available for: {filename}\n(Current version is the only one)"

        try:
            # Save current version to redo stack
            import shutil
            current_backup = file_path.with_suffix(file_path.suffix + '.redo_temp')
            shutil.copy2(file_path, current_backup)

            # Get previous version (second in list, since first is current)
            prev_version = versions[1]

            # Restore previous version
            shutil.copy2(prev_version['path'], file_path)

            # Store redo information
            if filename not in self._redo_stack:
                self._redo_stack[filename] = []
            self._redo_stack[filename].append(str(current_backup))

            # Get version timestamp
            version_time = prev_version['modified'].strftime('%Y-%m-%d %H:%M:%S')

            return (
                f"✅ Undone changes to: {filename}\n\n"
                f"Reverted to:  {prev_version['name']}\n"
                f"Version date: {version_time}\n"
                f"File size:    {round(file_path.stat().st_size / 1024, 2)} KB\n\n"
                f"💡 Use REDO {filename} to re-apply changes"
            )

        except Exception as e:
            return f"❌ Undo failed: {str(e)}"

    def _redo_file(self, filename: str) -> str:
        """Re-apply undone changes."""
        file_path = Path(filename)

        if filename not in self._redo_stack or not self._redo_stack[filename]:
            return f"❌ No redo available for: {filename}\n(Nothing has been undone this session)"

        try:
            # Get last undone version
            redo_temp = Path(self._redo_stack[filename].pop())

            if not redo_temp.exists():
                return f"❌ Redo data lost: {filename}\n(Temporary file was removed)"

            # Restore undone version
            import shutil
            shutil.copy2(redo_temp, file_path)

            # Clean up temp file
            redo_temp.unlink()

            return (
                f"✅ Redone changes to: {filename}\n\n"
                f"File size: {round(file_path.stat().st_size / 1024, 2)} KB\n\n"
                f"💡 Use UNDO {filename} to undo again"
            )

        except Exception as e:
            return f"❌ Redo failed: {str(e)}"

    def _revert_to_version(self, filename: str, version_name: str) -> str:
        """Revert to specific version."""
        from core.utils.archive_manager import ArchiveManager

        file_path = Path(filename)
        if not file_path.exists():
            return f"❌ File not found: {filename}"

        # Find the specified version
        archive_mgr = ArchiveManager()
        versions = self._get_file_versions(filename, archive_mgr)

        target_version = None
        for version in versions:
            if version['name'] == version_name:
                target_version = version
                break

        if not target_version:
            return f"❌ Version not found: {version_name}\nUse UNDO --list {filename} to see available versions"

        try:
            # Save current version to redo stack
            import shutil
            current_backup = file_path.with_suffix(file_path.suffix + '.redo_temp')
            shutil.copy2(file_path, current_backup)

            # Restore target version
            shutil.copy2(target_version['path'], file_path)

            # Store redo information
            if filename not in self._redo_stack:
                self._redo_stack[filename] = []
            self._redo_stack[filename].append(str(current_backup))

            version_time = target_version['modified'].strftime('%Y-%m-%d %H:%M:%S')

            return (
                f"✅ Reverted to version: {version_name}\n\n"
                f"File:         {filename}\n"
                f"Version date: {version_time}\n"
                f"File size:    {round(file_path.stat().st_size / 1024, 2)} KB\n\n"
                f"💡 Use REDO {filename} to restore previous state"
            )

        except Exception as e:
            return f"❌ Revert failed: {str(e)}"

    def _list_versions(self, filename: Optional[str]) -> str:
        """List version history for file(s)."""
        from core.utils.archive_manager import ArchiveManager

        if not filename:
            return "❌ No file specified\nUsage: UNDO --list <file>"

        archive_mgr = ArchiveManager()
        versions = self._get_file_versions(filename, archive_mgr)

        if not versions:
            return f"No version history found for: {filename}"

        # Format output
        lines = [
            "╔═══════════════════════════════════════════════════════════╗",
            f"║  Version History: {filename:<41} ║",
            "╠═══════════════════════════════════════════════════════════╣",
            f"║  {len(versions)} version(s) available:{' ' * (39 - len(str(len(versions))))} ║",
            "╠═══════════════════════════════════════════════════════════╣"
        ]

        for i, version in enumerate(versions, 1):
            timestamp = version['modified'].strftime('%Y-%m-%d %H:%M:%S')
            size_kb = round(version['size'] / 1024, 2)
            marker = " (current)" if i == 1 else ""

            lines.append(f"║  {i}. {version['name'][:45]:<45} ║")
            lines.append(f"║     {timestamp}  {size_kb} KB{marker}{' ' * (24 - len(str(size_kb)) - len(marker))} ║")

            if i < len(versions):
                lines.append("  -----------------------------------------------------------")

        lines.extend([
            "==================================================================",
            "  Commands:",
            f"  UNDO {filename}",
            f"  UNDO --to-version <version_name> {filename}",
            f"  REDO {filename}",
            "=================================================================="
        ])

        return '\n'.join(lines)

    def _get_file_versions(self, filename: str, archive_mgr) -> List[Dict]:
        """Get all versions for a file, sorted by modification time (newest first)."""
        file_path = Path(filename)
        versions = []

        # Search in parent directory's archive
        if file_path.parent.exists():
            archive_path = file_path.parent / '.archive' / 'versions'
            if archive_path.exists():
                pattern = f"*_{file_path.name}"
                for version_file in archive_path.glob(pattern):
                    versions.append({
                        'path': version_file,
                        'name': version_file.name,
                        'size': version_file.stat().st_size,
                        'modified': datetime.fromtimestamp(version_file.stat().st_mtime)
                    })

        # Sort by modification time (newest first)
        versions.sort(key=lambda v: v['modified'], reverse=True)

        return versions

    def _show_help(self) -> str:
        """Show UNDO/REDO help."""
        lines = [
            "=" * 66,
            "              UNDO/REDO Command Reference",
            "=" * 66,
            "",
            "  UNDO <file>",
            "    Revert file to previous version",
            "    Example: UNDO config.json",
            "",
            "  UNDO --list <file>",
            "    List all available versions for file",
            "    Example: UNDO --list config.json",
            "",
            "  UNDO --to-version <version_name> <file>",
            "    Revert to specific version",
            "    Example: UNDO --to-version 20251203_120000_config.json",
            "",
            "  REDO <file>",
            "    Re-apply undone changes",
            "    Example: REDO config.json",
            "",
            "=" * 66,
            "  How It Works:",
            "",
            "  1. File versions are automatically saved to .archive/",
            "     when file changes are detected",
            "",
            "  2. UNDO restores previous version from .archive/versions",
            "",
            "  3. Current state is saved for REDO",
            "",
            "  4. Version history kept for 90 days (configurable)",
            "",
            "  5. Maximum 10 versions per file (oldest auto-purged)",
            "",
            "=" * 66,
            "  Version Format:",
            "    YYYYMMDD_HHMMSS_original_filename.ext",
            "    Example: 20251203_143022_config.json",
            "",
            "  Storage Location:",
            "    <file_directory>/.archive/versions/",
            "",
            "=" * 66,
        ]
        return "\n".join(lines)