"""
Google Drive Sync Engine for uDOS v1.2.9

Provides bidirectional synchronization between local uDOS data and Google Drive
App Data folder (15MB quota). Handles conflict resolution, change detection,
and incremental syncing.

Features:
- Bidirectional sync (local ↔ cloud)
- Conflict detection and resolution
- Incremental updates (only changed files)
- MD5 checksum validation
- File metadata tracking
- Sync history and rollback

Conflict Resolution Strategies:
- local-wins: Keep local version
- cloud-wins: Keep cloud version
- newest-wins: Keep most recent version (default)
- manual: Prompt user for decision

Author: @fredporter
Version: 1.2.9
Date: December 2025
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
from enum import Enum

from core.services.gmail_service import get_drive_service


class ConflictStrategy(Enum):
    """Conflict resolution strategies."""
    LOCAL_WINS = "local-wins"
    CLOUD_WINS = "cloud-wins"
    NEWEST_WINS = "newest-wins"
    MANUAL = "manual"


class SyncStatus(Enum):
    """Sync operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"


class SyncEngine:
    """
    Core synchronization engine for Google Drive.

    Handles:
    - Change detection (local vs cloud)
    - Bidirectional sync operations
    - Conflict resolution
    - Incremental updates
    - Metadata management
    """

    # Syncable directories (relative to project root)
    SYNC_DIRS = [
        "memory/missions",
        "memory/workflows",
        "memory/checklists",
        "memory/system/user",
        "memory/docs",
        "memory/drafts"
    ]

    # Files to exclude from sync
    EXCLUDE_PATTERNS = [
        ".archive",
        ".git",
        "__pycache__",
        "*.pyc",
        "*.log",
        "*.tmp",
        ".gmail_token.enc",
        "gmail_credentials.json"
    ]

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize sync engine.

        Args:
            project_root: Project root path (defaults to auto-detect)
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.drive = get_drive_service()

        # Metadata storage
        self.metadata_dir = self.project_root / "memory" / "system" / "sync"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.metadata_dir / "sync_metadata.json"

        # Load metadata
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """
        Load sync metadata from disk.

        Returns:
            Metadata dictionary with file tracking info
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            'files': {},  # {local_path: {cloud_id, md5, modified, synced_at}}
            'last_sync': None,
            'conflict_strategy': ConflictStrategy.NEWEST_WINS.value
        }

    def _save_metadata(self) -> None:
        """Save sync metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Failed to save metadata: {e}")

    def _compute_md5(self, file_path: Path) -> str:
        """
        Compute MD5 hash of file.

        Args:
            file_path: Path to file

        Returns:
            MD5 hash string
        """
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def _should_exclude(self, path: Path) -> bool:
        """
        Check if file should be excluded from sync.

        Args:
            path: File or directory path

        Returns:
            True if should exclude, False otherwise
        """
        path_str = str(path)

        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith('*'):
                # Extension pattern
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True

        return False

    def get_local_files(self) -> List[Path]:
        """
        Get list of all syncable local files.

        Returns:
            List of Path objects for files to sync
        """
        files = []

        for sync_dir in self.SYNC_DIRS:
            dir_path = self.project_root / sync_dir
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and not self._should_exclude(file_path):
                    files.append(file_path)

        return files

    def detect_changes(self) -> Dict[str, List[Path]]:
        """
        Detect changes between local and cloud.

        Returns:
            Dictionary with categorized changes:
            {
                'new_local': [files to upload],
                'modified_local': [files to upload],
                'deleted_local': [files to delete from cloud],
                'new_cloud': [files to download],
                'modified_cloud': [files to download],
                'conflicts': [files with conflicts]
            }
        """
        changes = {
            'new_local': [],
            'modified_local': [],
            'deleted_local': [],
            'new_cloud': [],
            'modified_cloud': [],
            'conflicts': []
        }

        if not self.drive.is_available():
            return changes

        # Get local files
        local_files = self.get_local_files()
        local_paths = {self._get_relative_path(f): f for f in local_files}

        # Get cloud files
        cloud_files = self.drive.list_files()
        cloud_map = {f['name']: f for f in cloud_files}

        # Check local files
        for rel_path, file_path in local_paths.items():
            rel_path_str = str(rel_path)

            if rel_path_str not in cloud_map:
                # New local file
                changes['new_local'].append(file_path)
            else:
                # File exists in cloud - check if modified
                cloud_file = cloud_map[rel_path_str]
                local_md5 = self._compute_md5(file_path)
                cloud_md5 = cloud_file.get('md5Checksum', '')

                if local_md5 != cloud_md5:
                    # File modified - check which is newer
                    local_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    cloud_mtime = datetime.fromisoformat(cloud_file['modifiedTime'].replace('Z', '+00:00'))

                    if local_mtime > cloud_mtime:
                        changes['modified_local'].append(file_path)
                    elif cloud_mtime > local_mtime:
                        changes['modified_cloud'].append(file_path)
                    else:
                        # Same timestamp but different content - conflict
                        changes['conflicts'].append(file_path)

        # Check cloud files (for deletions)
        for cloud_name, cloud_file in cloud_map.items():
            if cloud_name not in local_paths:
                # File exists in cloud but not local
                # Could be deleted or not yet synced
                if cloud_name in self.metadata['files']:
                    # Was previously synced - deleted locally
                    changes['deleted_local'].append(cloud_name)
                else:
                    # Not in metadata - new cloud file
                    changes['new_cloud'].append(cloud_name)

        return changes

    def _get_relative_path(self, file_path: Path) -> Path:
        """
        Get relative path from project root.

        Args:
            file_path: Absolute file path

        Returns:
            Relative path from project root
        """
        return file_path.relative_to(self.project_root)

    def upload_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Upload file to Google Drive.

        Args:
            file_path: Local file path

        Returns:
            Upload result dictionary
        """
        if not self.drive.is_available():
            return {'success': False, 'error': 'Not authenticated'}

        rel_path = self._get_relative_path(file_path)
        cloud_name = str(rel_path)

        # Check if file already exists in cloud
        cloud_files = self.drive.list_files(name_filter=cloud_name)

        if cloud_files:
            # File exists - delete old version first
            for cloud_file in cloud_files:
                if cloud_file['name'] == cloud_name:
                    self.drive.delete_file(cloud_file['id'])

        # Upload new version
        result = self.drive.upload_file(file_path, cloud_name=cloud_name)

        if result['success']:
            # Update metadata
            self.metadata['files'][cloud_name] = {
                'cloud_id': result['file_id'],
                'md5': self._compute_md5(file_path),
                'modified': datetime.now().isoformat(),
                'synced_at': datetime.now().isoformat()
            }
            self._save_metadata()

        return result

    def download_file(self, cloud_name: str, local_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Download file from Google Drive.

        Args:
            cloud_name: Cloud file name (relative path)
            local_path: Optional local destination (defaults to cloud_name)

        Returns:
            Download result dictionary
        """
        if not self.drive.is_available():
            return {'success': False, 'error': 'Not authenticated'}

        # Get cloud file
        cloud_files = self.drive.list_files(name_filter=cloud_name)
        cloud_file = None
        for f in cloud_files:
            if f['name'] == cloud_name:
                cloud_file = f
                break

        if not cloud_file:
            return {'success': False, 'error': f'File not found in cloud: {cloud_name}'}

        # Determine local path
        if local_path is None:
            local_path = self.project_root / cloud_name

        # Ensure directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)

        # Download
        success = self.drive.download_file(cloud_file['id'], local_path)

        if success:
            # Update metadata
            self.metadata['files'][cloud_name] = {
                'cloud_id': cloud_file['id'],
                'md5': cloud_file.get('md5Checksum', ''),
                'modified': cloud_file.get('modifiedTime'),
                'synced_at': datetime.now().isoformat()
            }
            self._save_metadata()

            return {'success': True, 'local_path': str(local_path)}
        else:
            return {'success': False, 'error': 'Download failed'}

    def resolve_conflict(self, file_path: Path, strategy: ConflictStrategy) -> Dict[str, Any]:
        """
        Resolve sync conflict using specified strategy.

        Args:
            file_path: Conflicted file path
            strategy: Conflict resolution strategy

        Returns:
            Resolution result dictionary
        """
        rel_path = str(self._get_relative_path(file_path))

        if strategy == ConflictStrategy.LOCAL_WINS:
            # Upload local version
            return self.upload_file(file_path)

        elif strategy == ConflictStrategy.CLOUD_WINS:
            # Download cloud version
            return self.download_file(rel_path, file_path)

        elif strategy == ConflictStrategy.NEWEST_WINS:
            # Compare timestamps and keep newest
            local_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            cloud_files = self.drive.list_files(name_filter=rel_path)
            cloud_file = None
            for f in cloud_files:
                if f['name'] == rel_path:
                    cloud_file = f
                    break

            if not cloud_file:
                return self.upload_file(file_path)

            cloud_mtime = datetime.fromisoformat(cloud_file['modifiedTime'].replace('Z', '+00:00'))

            if local_mtime >= cloud_mtime:
                return self.upload_file(file_path)
            else:
                return self.download_file(rel_path, file_path)

        elif strategy == ConflictStrategy.MANUAL:
            # Return conflict info for manual resolution
            return {
                'success': False,
                'requires_manual': True,
                'file': str(file_path),
                'message': 'Manual conflict resolution required'
            }

        return {'success': False, 'error': 'Unknown strategy'}

    def sync_all(self, strategy: Optional[ConflictStrategy] = None) -> Dict[str, Any]:
        """
        Perform full bidirectional sync.

        Args:
            strategy: Conflict resolution strategy (defaults to metadata setting)

        Returns:
            Sync result summary
        """
        if not self.drive.is_available():
            return {
                'success': False,
                'error': 'Not authenticated',
                'stats': {}
            }

        # Use provided strategy or default
        if strategy is None:
            strategy = ConflictStrategy(self.metadata.get('conflict_strategy', 'newest-wins'))

        # Detect changes
        changes = self.detect_changes()

        stats = {
            'uploaded': 0,
            'downloaded': 0,
            'deleted': 0,
            'conflicts': 0,
            'errors': 0
        }

        errors = []

        # Upload new files
        for file_path in changes['new_local']:
            result = self.upload_file(file_path)
            if result['success']:
                stats['uploaded'] += 1
            else:
                stats['errors'] += 1
                errors.append(f"Upload failed: {file_path}")

        # Upload modified files
        for file_path in changes['modified_local']:
            result = self.upload_file(file_path)
            if result['success']:
                stats['uploaded'] += 1
            else:
                stats['errors'] += 1
                errors.append(f"Upload failed: {file_path}")

        # Download new files
        for cloud_name in changes['new_cloud']:
            result = self.download_file(cloud_name)
            if result['success']:
                stats['downloaded'] += 1
            else:
                stats['errors'] += 1
                errors.append(f"Download failed: {cloud_name}")

        # Download modified files
        for file_path in changes['modified_cloud']:
            rel_path = str(self._get_relative_path(file_path))
            result = self.download_file(rel_path, file_path)
            if result['success']:
                stats['downloaded'] += 1
            else:
                stats['errors'] += 1
                errors.append(f"Download failed: {rel_path}")

        # Resolve conflicts
        for file_path in changes['conflicts']:
            result = self.resolve_conflict(file_path, strategy)
            if result.get('success'):
                stats['conflicts'] += 1
            elif result.get('requires_manual'):
                stats['conflicts'] += 1
                errors.append(f"Manual resolution needed: {file_path}")
            else:
                stats['errors'] += 1
                errors.append(f"Conflict resolution failed: {file_path}")

        # Delete from cloud (if files deleted locally)
        for cloud_name in changes['deleted_local']:
            cloud_files = self.drive.list_files(name_filter=cloud_name)
            for cloud_file in cloud_files:
                if cloud_file['name'] == cloud_name:
                    if self.drive.delete_file(cloud_file['id']):
                        stats['deleted'] += 1
                        # Remove from metadata
                        if cloud_name in self.metadata['files']:
                            del self.metadata['files'][cloud_name]
                    else:
                        stats['errors'] += 1
                        errors.append(f"Delete failed: {cloud_name}")

        # Update last sync time
        self.metadata['last_sync'] = datetime.now().isoformat()
        self._save_metadata()

        return {
            'success': stats['errors'] == 0,
            'stats': stats,
            'errors': errors,
            'last_sync': self.metadata['last_sync']
        }


# Singleton instance
_sync_engine_instance = None

def get_sync_engine() -> SyncEngine:
    """Get singleton sync engine instance."""
    global _sync_engine_instance
    if _sync_engine_instance is None:
        _sync_engine_instance = SyncEngine()
    return _sync_engine_instance
