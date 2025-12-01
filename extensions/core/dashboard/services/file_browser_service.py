"""
File Browser Service for Advanced Dashboard
Handles file operations, preview generation, and Git integration
"""

import os
import git
import mimetypes
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class FileBrowserService:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self._setup_git_repo()

    def _setup_git_repo(self):
        """Initialize Git repository access if available"""
        try:
            self.repo = git.Repo(self.root_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            self.repo = None

    def list_directory(self, path: str = "") -> List[Dict]:
        """List contents of a directory with metadata"""
        target_path = (self.root_path / path).resolve()
        if not str(target_path).startswith(str(self.root_path)):
            raise ValueError("Access denied: Path outside root directory")

        items = []
        for item in target_path.iterdir():
            try:
                stat = item.stat()
                item_info = {
                    'name': item.name,
                    'path': str(item.relative_to(self.root_path)),
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': stat.st_size if item.is_file() else None,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'git_status': self._get_git_status(str(item.relative_to(self.root_path))) if self.repo else None
                }
                if item.is_file():
                    item_info.update({
                        'mime_type': mimetypes.guess_type(item.name)[0],
                        'preview_available': self._can_preview(item)
                    })
                items.append(item_info)
            except (PermissionError, FileNotFoundError):
                continue

        return sorted(items, key=lambda x: (x['type'] != 'directory', x['name'].lower()))

    def get_file_content(self, path: str, max_size: int = 1024 * 1024) -> Optional[Dict]:
        """Get file content with preview if available"""
        target_path = (self.root_path / path).resolve()
        if not str(target_path).startswith(str(self.root_path)):
            raise ValueError("Access denied: Path outside root directory")

        if not target_path.is_file():
            return None

        stat = target_path.stat()
        if stat.st_size > max_size:
            return {
                'error': 'File too large for preview',
                'size': stat.st_size
            }

        mime_type = mimetypes.guess_type(target_path.name)[0]
        content = None

        try:
            if self._is_text_file(target_path):
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif self._is_binary_preview_supported(mime_type):
                content = self._generate_binary_preview(target_path)
        except UnicodeDecodeError:
            return {
                'error': 'Unable to decode file content',
                'mime_type': mime_type
            }

        return {
            'content': content,
            'mime_type': mime_type,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'git_status': self._get_git_status(path) if self.repo else None
        }

    def _get_git_status(self, path: str) -> Optional[Dict]:
        """Get Git status for a file"""
        if not self.repo:
            return None

        try:
            status = []
            diff_index = self.repo.index.diff(None)
            untracked_files = self.repo.untracked_files

            if path in untracked_files:
                status.append('untracked')

            for diff in diff_index:
                if diff.a_path == path or diff.b_path == path:
                    if diff.change_type == 'M':
                        status.append('modified')
                    elif diff.change_type == 'D':
                        status.append('deleted')
                    elif diff.change_type == 'A':
                        status.append('added')

            return {
                'status': status,
                'branch': self.repo.active_branch.name if not self.repo.head.is_detached else 'DETACHED'
            }
        except Exception:
            return None

    def _can_preview(self, path: Path) -> bool:
        """Check if file can be previewed"""
        mime_type = mimetypes.guess_type(path.name)[0]
        return self._is_text_file(path) or self._is_binary_preview_supported(mime_type)

    def _is_text_file(self, path: Path) -> bool:
        """Check if file is text-based"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                f.read(1024)
            return True
        except UnicodeDecodeError:
            return False

    def _is_binary_preview_supported(self, mime_type: Optional[str]) -> bool:
        """Check if binary file type is supported for preview"""
        if not mime_type:
            return False
        return mime_type.startswith(('image/', 'application/pdf'))
