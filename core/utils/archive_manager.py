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
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import time


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

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize archive manager.

        Args:
            root_path: Root workspace path (defaults to current directory)
        """
        if root_path is None:
            root_path = Path.cwd()
        self.root = Path(root_path)

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

        # Generate timestamped version name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"{timestamp}_{file_path.name}"
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

        # Generate timestamped backup name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{file_path.name}"
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

        # Generate timestamped deleted name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        deleted_name = f"{timestamp}_{file_path.name}"
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

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics for all archives in workspace.

        Returns:
            Dictionary with overall archive health metrics
        """
        archives = self.scan_archives()

        metrics = {
            "total_archives": len(archives),
            "total_files": sum(a["total_files"] for a in archives),
            "total_size_mb": sum(a["total_size_mb"] for a in archives),
            "archives": archives,
            "warnings": []
        }

        # Check for warnings
        for archive in archives:
            # Warn if archive > 100MB
            if archive["total_size_mb"] > 100:
                metrics["warnings"].append(
                    f"Large archive: {archive['path']} ({archive['total_size_mb']} MB)"
                )

            # Warn if deleted files exist (should be purged)
            deleted_count = archive["subdirs"].get(self.SUBDIR_DELETED, {}).get("file_count", 0)
            if deleted_count > 0:
                metrics["warnings"].append(
                    f"Unpurged deleted files: {archive['path']} ({deleted_count} files)"
                )

        return metrics
