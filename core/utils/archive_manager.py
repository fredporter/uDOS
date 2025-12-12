"""
uDOS Archive Manager - Universal .archive/ folder system

Version: v1.1.16
Purpose: Manage version history, backups, and soft-deleted files across workspace
Location: Any directory can have a .archive/ subfolder

Archive Structure:
  .archive/
  ├── versions/        # File version history (old/working versions)
  ├── backups/         # Timestamped backup snapshots
  ├── deleted/         # Soft-deleted files (7-day recovery window)
  ├── completed/       # Archived work (completed missions, workflows)
  └── metadata.json    # Archive tracking metadata

Features:
- Auto-creation of .archive/ folders on demand
- Version tracking (keep last 5-10 versions per file)
- Backup snapshots (timestamped: YYYYMMDD_HHMMSS_filename.ext)
- Soft-delete (7-day recovery window)
- Retention policies (auto-cleanup old files)
- Health metrics (space usage, file counts, age distribution)
"""

import os
import json
import shutil
import gzip
import tarfile
import hashlib
import difflib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import time
from core.utils.filename_generator import FilenameGenerator


class ArchiveManager:
    """Manage .archive/ folders across workspace."""

    # Default retention policies (days)
    RETENTION_DELETED = 7      # Soft-deleted files: 7 days
    RETENTION_BACKUPS = 30     # Backup snapshots: 30 days
    RETENTION_VERSIONS = 90    # Version history: 90 days
    MAX_VERSIONS = 10          # Keep last 10 versions per file

    # Archive subdirectories
    SUBDIR_VERSIONS = "versions"
    SUBDIR_BACKUPS = "backups"
    SUBDIR_DELETED = "deleted"
    SUBDIR_COMPLETED = "completed"

    # Performance optimization: Cache health metrics
    _health_cache: Optional[Dict[str, Any]] = None
    _health_cache_time: float = 0
    HEALTH_CACHE_TTL = 300  # 5 minutes

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize archive manager.

        Args:
            root_path: Root workspace path (defaults to current directory)
        """
        if root_path is None:
            root_path = Path.cwd()
        self.root = Path(root_path)
        
        # Initialize filename generator for consistent timestamp formatting (v1.2.23)
        try:
            from core.config import Config
            config = Config()
            self.filename_gen = FilenameGenerator(config=config)
        except:
            # Fallback if config not available
            self.filename_gen = FilenameGenerator()

    def get_archive_path(self, directory: Path) -> Path:
        """Get .archive/ path for a directory.

        Args:
            directory: Target directory

        Returns:
            Path to .archive/ folder
        """
        return directory / ".archive"

    def create_archive(self, directory: Path, subdirs: Optional[List[str]] = None) -> Path:
        """Create .archive/ folder with subdirectories.

        Args:
            directory: Target directory
            subdirs: List of subdirectories to create (default: all)

        Returns:
            Path to created .archive/ folder
        """
        archive_path = self.get_archive_path(directory)
        archive_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        if subdirs is None:
            subdirs = [
                self.SUBDIR_VERSIONS,
                self.SUBDIR_BACKUPS,
                self.SUBDIR_DELETED,
                self.SUBDIR_COMPLETED
            ]

        for subdir in subdirs:
            (archive_path / subdir).mkdir(exist_ok=True)

        # Create metadata file if it doesn't exist
        metadata_path = archive_path / "metadata.json"
        if not metadata_path.exists():
            metadata = {
                "created": datetime.now().isoformat(),
                "version": "1.1.16",
                "retention_policies": {
                    "deleted_days": self.RETENTION_DELETED,
                    "backups_days": self.RETENTION_BACKUPS,
                    "versions_days": self.RETENTION_VERSIONS,
                    "max_versions": self.MAX_VERSIONS
                }
            }
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

        return archive_path

    def add_version(self, file_path: Path, archive_dir: Optional[Path] = None) -> Path:
        """Add a file version to archive.

        Args:
            file_path: File to archive
            archive_dir: Archive directory (defaults to file's parent .archive/)

        Returns:
            Path to archived version
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get or create archive
        if archive_dir is None:
            archive_dir = self.create_archive(file_path.parent)

        versions_dir = archive_dir / self.SUBDIR_VERSIONS
        versions_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped version name (v1.2.23 - using FilenameGenerator)
        version_name = self.filename_gen.generate(
            base_name=file_path.stem,
            extension=file_path.suffix,
            include_date=True,
            include_time=True
        )
        version_path = versions_dir / version_name

        # Copy file to versions
        shutil.copy2(file_path, version_path)

        # Cleanup old versions (keep last MAX_VERSIONS)
        self._cleanup_old_versions(file_path.name, versions_dir)

        return version_path

    def _cleanup_old_versions(self, filename: str, versions_dir: Path):
        """Remove old versions beyond MAX_VERSIONS limit.

        Args:
            filename: Original filename
            versions_dir: Versions directory
        """
        # Find all versions of this file
        pattern = f"*_{filename}"
        versions = sorted(versions_dir.glob(pattern), key=os.path.getmtime, reverse=True)

        # Remove old versions
        for old_version in versions[self.MAX_VERSIONS:]:
            old_version.unlink()

    def add_backup(self, file_path: Path, archive_dir: Optional[Path] = None) -> Path:
        """Create timestamped backup of file.

        Args:
            file_path: File to backup
            archive_dir: Archive directory (defaults to file's parent .archive/)

        Returns:
            Path to backup file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get or create archive
        if archive_dir is None:
            archive_dir = self.create_archive(file_path.parent)

        backups_dir = archive_dir / self.SUBDIR_BACKUPS
        backups_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped backup name (v1.2.23 - using FilenameGenerator)
        backup_name = self.filename_gen.generate(
            base_name=file_path.stem,
            extension=file_path.suffix,
            include_date=True,
            include_time=True
        )
        backup_path = backups_dir / backup_name

        # Copy file to backups
        shutil.copy2(file_path, backup_path)

        return backup_path

    def soft_delete(self, file_path: Path, archive_dir: Optional[Path] = None) -> Path:
        """Move file to .archive/deleted/ (soft delete with recovery window).

        Args:
            file_path: File to soft-delete
            archive_dir: Archive directory (defaults to file's parent .archive/)

        Returns:
            Path to deleted file in archive
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get or create archive
        if archive_dir is None:
            archive_dir = self.create_archive(file_path.parent)

        deleted_dir = archive_dir / self.SUBDIR_DELETED
        deleted_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped deleted name (v1.2.23 - using FilenameGenerator)
        deleted_name = self.filename_gen.generate(
            base_name=file_path.stem,
            extension=file_path.suffix,
            include_date=True,
            include_time=True
        )
        deleted_path = deleted_dir / deleted_name

        # Move file to deleted
        shutil.move(str(file_path), str(deleted_path))

        return deleted_path

    def restore_deleted(self, deleted_path: Path, restore_path: Optional[Path] = None) -> Path:
        """Restore soft-deleted file.

        Args:
            deleted_path: Path to deleted file in archive
            restore_path: Destination path (defaults to original location)

        Returns:
            Path to restored file
        """
        if not deleted_path.exists():
            raise FileNotFoundError(f"Deleted file not found: {deleted_path}")

        # Extract original filename (remove timestamp prefix)
        original_name = "_".join(deleted_path.name.split("_")[2:])

        # Determine restore path
        if restore_path is None:
            restore_path = deleted_path.parent.parent.parent / original_name

        # Move file back
        shutil.move(str(deleted_path), str(restore_path))

        return restore_path

    def scan_archives(self, root_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Scan workspace for all .archive/ folders.

        Args:
            root_dir: Root directory to scan (defaults to self.root)

        Returns:
            List of archive metadata dicts
        """
        if root_dir is None:
            root_dir = self.root

        archives = []

        for archive_path in root_dir.rglob(".archive"):
            if not archive_path.is_dir():
                continue

            # Get archive stats
            stats = self.get_archive_stats(archive_path)
            archives.append(stats)

        return archives

    def get_archive_stats(self, archive_path: Path) -> Dict[str, Any]:
        """Get statistics for an archive folder.

        Args:
            archive_path: Path to .archive/ folder

        Returns:
            Dictionary with archive statistics
        """
        stats = {
            "path": str(archive_path),
            "created": None,
            "total_files": 0,
            "total_size_bytes": 0,
            "subdirs": {}
        }

        # Read metadata
        metadata_path = archive_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path) as f:
                metadata = json.load(f)
                stats["created"] = metadata.get("created")

        # Count files and sizes in each subdirectory
        for subdir in [self.SUBDIR_VERSIONS, self.SUBDIR_BACKUPS,
                       self.SUBDIR_DELETED, self.SUBDIR_COMPLETED]:
            subdir_path = archive_path / subdir
            if subdir_path.exists():
                files = list(subdir_path.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                total_size = sum(f.stat().st_size for f in files if f.is_file())

                stats["subdirs"][subdir] = {
                    "file_count": file_count,
                    "size_bytes": total_size,
                    "size_mb": round(total_size / (1024 * 1024), 2)
                }

                stats["total_files"] += file_count
                stats["total_size_bytes"] += total_size

        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)

        return stats

    def purge_old_files(self, archive_path: Path, dry_run: bool = False) -> Dict[str, List[str]]:
        """Purge old files from archive based on retention policies.

        Args:
            archive_path: Path to .archive/ folder
            dry_run: If True, only report what would be deleted

        Returns:
            Dictionary of files to delete/deleted by category
        """
        now = datetime.now()
        purged = {
            "deleted": [],
            "backups": [],
            "versions": []
        }

        # Purge soft-deleted files older than RETENTION_DELETED days
        deleted_dir = archive_path / self.SUBDIR_DELETED
        if deleted_dir.exists():
            cutoff = now - timedelta(days=self.RETENTION_DELETED)
            for file in deleted_dir.rglob("*"):
                if file.is_file() and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                    purged["deleted"].append(str(file))
                    if not dry_run:
                        file.unlink()

        # Purge backups older than RETENTION_BACKUPS days
        backups_dir = archive_path / self.SUBDIR_BACKUPS
        if backups_dir.exists():
            cutoff = now - timedelta(days=self.RETENTION_BACKUPS)
            for file in backups_dir.rglob("*"):
                if file.is_file() and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                    purged["backups"].append(str(file))
                    if not dry_run:
                        file.unlink()

        # Purge versions older than RETENTION_VERSIONS days
        versions_dir = archive_path / self.SUBDIR_VERSIONS
        if versions_dir.exists():
            cutoff = now - timedelta(days=self.RETENTION_VERSIONS)
            for file in versions_dir.rglob("*"):
                if file.is_file() and datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
                    purged["versions"].append(str(file))
                    if not dry_run:
                        file.unlink()

        return purged

    def get_health_metrics(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get health metrics for all archives in workspace.

        Uses caching to avoid expensive filesystem scans on every call.

        Args:
            force_refresh: Force refresh cache even if valid

        Returns:
            Dictionary with overall archive health metrics
        """
        # Check cache validity
        now = time.time()
        if not force_refresh and self._health_cache is not None:
            cache_age = now - self._health_cache_time
            if cache_age < self.HEALTH_CACHE_TTL:
                return self._health_cache

        # Cache miss or expired - recalculate
        archives = self.scan_archives()

        metrics = {
            "total_archives": len(archives),
            "total_files": sum(a["total_files"] for a in archives),
            "total_size_mb": sum(a["total_size_mb"] for a in archives),
            "archives": archives,
            "warnings": [],
            "cached_at": datetime.now().isoformat(),
            "cache_ttl": self.HEALTH_CACHE_TTL
        }

        # Check for warnings
        for archive in archives:
            # Warn if archive > 100MB
            if archive["total_size_mb"] > 100:
                metrics["warnings"].append(
                    f"Large archive: {archive['path']} ({archive['total_size_mb']:.1f} MB)"
                )

            # Warn if deleted files exist (should be purged)
            deleted_count = archive["subdirs"].get(self.SUBDIR_DELETED, {}).get("file_count", 0)
            if deleted_count > 0:
                metrics["warnings"].append(
                    f"Unpurged deleted files: {archive['path']} ({deleted_count} files)"
                )

        # Update cache
        self._health_cache = metrics
        self._health_cache_time = now

        return metrics

    def clear_health_cache(self):
        """Clear health metrics cache to force refresh on next call."""
        self._health_cache = None
        self._health_cache_time = 0

    # ========== Compression Methods (v1.1.18) ==========

    def compress_file(self, file_path: Path, output_path: Optional[Path] = None) -> Path:
        """Compress a file using gzip.

        Args:
            file_path: Path to file to compress
            output_path: Optional output path (default: {file_path}.gz)

        Returns:
            Path to compressed file
        """
        if output_path is None:
            output_path = Path(str(file_path) + '.gz')

        with open(file_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        return output_path

    def decompress_file(self, compressed_path: Path, output_path: Optional[Path] = None) -> Path:
        """Decompress a gzipped file.

        Args:
            compressed_path: Path to compressed file (.gz)
            output_path: Optional output path (default: remove .gz extension)

        Returns:
            Path to decompressed file
        """
        if output_path is None:
            if compressed_path.suffix == '.gz':
                output_path = compressed_path.with_suffix('')
            else:
                output_path = compressed_path.parent / f"{compressed_path.stem}_decompressed"

        with gzip.open(compressed_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        return output_path

    def compress_archive_directory(self, archive_path: Path, subdir: str = "backups") -> Dict[str, Any]:
        """Compress all files in an archive subdirectory.

        Args:
            archive_path: Path to .archive/ folder
            subdir: Subdirectory to compress (backups, versions, etc.)

        Returns:
            Statistics: files compressed, space saved, errors
        """
        target_dir = archive_path / subdir
        if not target_dir.exists():
            return {"error": f"Directory not found: {target_dir}"}

        stats = {
            "files_processed": 0,
            "files_compressed": 0,
            "original_size_mb": 0,
            "compressed_size_mb": 0,
            "space_saved_mb": 0,
            "errors": []
        }

        for file_path in target_dir.rglob('*'):
            if not file_path.is_file():
                continue

            # Skip already compressed files
            if file_path.suffix == '.gz':
                continue

            stats["files_processed"] += 1
            original_size = file_path.stat().st_size

            try:
                compressed_path = self.compress_file(file_path)
                compressed_size = compressed_path.stat().st_size

                # Only keep compressed if it's actually smaller
                if compressed_size < original_size:
                    file_path.unlink()  # Remove original
                    stats["files_compressed"] += 1
                    stats["original_size_mb"] += original_size / (1024 * 1024)
                    stats["compressed_size_mb"] += compressed_size / (1024 * 1024)
                else:
                    compressed_path.unlink()  # Remove compressed, keep original

            except Exception as e:
                stats["errors"].append(f"{file_path.name}: {str(e)}")

        stats["space_saved_mb"] = stats["original_size_mb"] - stats["compressed_size_mb"]
        stats["compression_ratio"] = (
            (1 - stats["compressed_size_mb"] / stats["original_size_mb"]) * 100
            if stats["original_size_mb"] > 0 else 0
        )

        return stats

    def get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of SHA256 hash
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    # ========== Incremental Backup Methods (v1.1.18 Part 2) ==========

    def create_incremental_backup(self, file_path: Path, archive_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Create incremental backup using diffs.

        Instead of storing full file copies, stores unified diffs from previous version.
        Expected 80-90% storage reduction for text files.

        Args:
            file_path: File to backup
            archive_dir: Archive directory (defaults to file's parent .archive/)

        Returns:
            Dictionary with backup info: {
                'backup_path': Path to backup (full or diff),
                'backup_type': 'full' or 'incremental',
                'base_backup': Path to base backup (for incremental),
                'size_original': Original file size,
                'size_backup': Backup file size,
                'savings_percent': Storage savings percentage
            }
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get or create archive
        if archive_dir is None:
            archive_dir = self.create_archive(file_path.parent)

        backups_dir = archive_dir / self.SUBDIR_BACKUPS
        backups_dir.mkdir(parents=True, exist_ok=True)

        # Find most recent backup
        pattern = f"*_{file_path.name}"
        existing_backups = sorted(
            [b for b in backups_dir.glob(pattern) if not b.name.endswith('.diff')],
            key=os.path.getmtime,
            reverse=True
        )

        original_size = file_path.stat().st_size

        # If no previous backup exists, create full backup
        if not existing_backups:
            # Generate timestamped backup name (v1.2.23 - using FilenameGenerator)
            backup_name = self.filename_gen.generate(
                base_name=file_path.stem,
                extension=file_path.suffix,
                include_date=True,
                include_time=True
            )
            backup_path = backups_dir / backup_name
            shutil.copy2(file_path, backup_path)

            return {
                'backup_path': backup_path,
                'backup_type': 'full',
                'base_backup': None,
                'size_original': original_size,
                'size_backup': backup_path.stat().st_size,
                'savings_percent': 0.0
            }

        # Create incremental backup (diff)
        base_backup = existing_backups[0]

        # Read files as text lines
        try:
            with open(base_backup, 'r', encoding='utf-8') as f:
                base_lines = f.readlines()
            with open(file_path, 'r', encoding='utf-8') as f:
                current_lines = f.readlines()
        except UnicodeDecodeError:
            # Binary file - fall back to full backup (v1.2.23 - using FilenameGenerator)
            backup_name = self.filename_gen.generate(
                base_name=file_path.stem,
                extension=file_path.suffix,
                include_date=True,
                include_time=True
            )
            backup_path = backups_dir / backup_name
            shutil.copy2(file_path, backup_path)

            return {
                'backup_path': backup_path,
                'backup_type': 'full',
                'base_backup': None,
                'size_original': original_size,
                'size_backup': backup_path.stat().st_size,
                'savings_percent': 0.0
            }

        # Generate unified diff
        diff = difflib.unified_diff(
            base_lines,
            current_lines,
            fromfile=str(base_backup),
            tofile=str(file_path),
            lineterm=''
        )
        diff_lines = list(diff)

        # If diff is empty (no changes), skip backup
        if not diff_lines:
            return {
                'backup_path': base_backup,
                'backup_type': 'unchanged',
                'base_backup': base_backup,
                'size_original': original_size,
                'size_backup': 0,
                'savings_percent': 100.0
            }

        # Save diff file (v1.2.23 - using FilenameGenerator)
        diff_name = self.filename_gen.generate(
            base_name=file_path.stem,
            extension=".diff",
            include_date=True,
            include_time=True
        )
        diff_path = backups_dir / diff_name

        with open(diff_path, 'w', encoding='utf-8') as f:
            # Store metadata in first line
            metadata = {
                'base_backup': base_backup.name,
                'timestamp': timestamp,
                'original_size': original_size
            }
            f.write(f"# DIFF_METADATA: {json.dumps(metadata)}\n")
            f.write('\n'.join(diff_lines))

        diff_size = diff_path.stat().st_size
        savings = (1 - diff_size / original_size) * 100 if original_size > 0 else 0

        return {
            'backup_path': diff_path,
            'backup_type': 'incremental',
            'base_backup': base_backup,
            'size_original': original_size,
            'size_backup': diff_size,
            'savings_percent': savings
        }

    def apply_incremental_backup(self, diff_path: Path, output_path: Optional[Path] = None) -> Path:
        """Restore file from incremental backup by applying diff.

        Args:
            diff_path: Path to .diff file
            output_path: Optional output path (default: extract from metadata)

        Returns:
            Path to restored file
        """
        if not diff_path.exists():
            raise FileNotFoundError(f"Diff file not found: {diff_path}")

        # Read diff file
        with open(diff_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Extract metadata from first line
        if not lines or not lines[0].startswith('# DIFF_METADATA:'):
            raise ValueError(f"Invalid diff file (missing metadata): {diff_path}")

        metadata_str = lines[0].replace('# DIFF_METADATA:', '').strip()
        metadata = json.loads(metadata_str)

        base_backup_name = metadata['base_backup']
        base_backup = diff_path.parent / base_backup_name

        if not base_backup.exists():
            raise FileNotFoundError(f"Base backup not found: {base_backup}")

        # Read base file
        with open(base_backup, 'r', encoding='utf-8') as f:
            base_lines = f.readlines()

        # Parse diff (skip metadata line)
        diff_lines = lines[1:]

        # Apply diff using difflib
        # Parse the diff to extract changes
        patched_lines = self._apply_unified_diff(base_lines, diff_lines)

        # Determine output path
        if output_path is None:
            # Extract original filename from diff file name
            # Format: YYYYMMDD_HHMMSS_filename.ext.diff
            original_name = '_'.join(diff_path.stem.split('_')[2:])
            output_path = diff_path.parent.parent.parent / original_name

        # Write restored file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(patched_lines)

        return output_path

    def _apply_unified_diff(self, base_lines: List[str], diff_lines: List[str]) -> List[str]:
        """Apply unified diff to base content.

        Args:
            base_lines: Original file lines
            diff_lines: Unified diff lines

        Returns:
            Patched file lines
        """
        # Simple diff application (works for most cases)
        # For production, consider using patch library

        result = []
        base_idx = 0
        i = 0

        while i < len(diff_lines):
            line = diff_lines[i]

            # Skip diff headers
            if line.startswith('---') or line.startswith('+++'):
                i += 1
                continue

            # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
            if line.startswith('@@'):
                # Extract line numbers
                parts = line.split()
                if len(parts) >= 3:
                    old_range = parts[1].lstrip('-').split(',')
                    old_start = int(old_range[0]) - 1  # Convert to 0-indexed

                    # Copy unchanged lines before this hunk
                    while base_idx < old_start and base_idx < len(base_lines):
                        result.append(base_lines[base_idx])
                        base_idx += 1

                i += 1
                continue

            # Process diff lines
            if line.startswith('-'):
                # Removed line - skip in base
                base_idx += 1
            elif line.startswith('+'):
                # Added line - add to result
                result.append(line[1:])
            elif line.startswith(' '):
                # Context line - copy from base
                if base_idx < len(base_lines):
                    result.append(base_lines[base_idx])
                    base_idx += 1

            i += 1

        # Append remaining base lines
        while base_idx < len(base_lines):
            result.append(base_lines[base_idx])
            base_idx += 1

        return result

    def get_backup_chain(self, file_name: str, archive_dir: Path) -> List[Dict[str, Any]]:
        """Get the backup chain for a file (full backup + incremental diffs).

        Args:
            file_name: Name of the file
            archive_dir: Archive directory containing backups

        Returns:
            List of backup info dicts in chronological order
        """
        backups_dir = archive_dir / self.SUBDIR_BACKUPS
        if not backups_dir.exists():
            return []

        # Find all backups (full + diffs) - use two patterns
        full_pattern = f"*_{file_name}"
        diff_pattern = f"*_{file_name}.diff"

        full_backups = list(backups_dir.glob(full_pattern))
        diff_backups = list(backups_dir.glob(diff_pattern))

        # Combine and sort by modification time
        all_backups = sorted(
            full_backups + diff_backups,
            key=os.path.getmtime
        )

        chain = []
        for backup_path in all_backups:
            is_diff = backup_path.suffix == '.diff'

            info = {
                'path': backup_path,
                'name': backup_path.name,
                'type': 'incremental' if is_diff else 'full',
                'size': backup_path.stat().st_size,
                'timestamp': datetime.fromtimestamp(backup_path.stat().st_mtime)
            }

            # Extract base backup for diffs
            if is_diff:
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        first_line = f.readline()
                    if first_line.startswith('# DIFF_METADATA:'):
                        metadata_str = first_line.replace('# DIFF_METADATA:', '').strip()
                        metadata = json.loads(metadata_str)
                        info['base_backup'] = metadata['base_backup']
                except Exception:
                    pass

            chain.append(info)

        return chain

