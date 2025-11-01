"""
uDOS File Operations System
Handles NEW, DELETE, COPY, MOVE, RENAME commands with workspace isolation

Workspaces: sandbox (experiments), memory (storage), data (config)
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple


class WorkspaceManager:
    """Manages siloed workspaces with file operations"""

    WORKSPACES = {
        'sandbox': {
            'path': 'sandbox',
            'description': 'Temporary workspace for experiments',
            'emoji': '🧪'
        },
        'memory': {
            'path': 'memory',
            'description': 'Long-term storage for completed work',
            'emoji': '💾'
        },
        'data': {
            'path': 'data',
            'description': 'System data and configurations',
            'emoji': '⚙️'
        }
    }

    TEMPLATES = {
        'blank': {
            'name': 'Blank Document',
            'extension': '.md',
            'content': '# New Document\n\n'
        },
        'note': {
            'name': 'Quick Note',
            'extension': '.md',
            'content': '''# Quick Note

**Date:** {date}
**Author:** {username}

## Notes

'''
        },
        'quest': {
            'name': 'Quest Log',
            'extension': '.md',
            'content': '''# Quest: {title}

**Status:** 🎯 Active
**Created:** {date}

## Objective

## Tasks

- [ ] Task 1
- [ ] Task 2

## Progress

'''
        },
        'config': {
            'name': 'Configuration',
            'extension': '.udo',
            'content': '''{{
  "VERSION": "1.0",
  "CREATED": "{date}",
  "AUTHOR": "{username}",
  "DESCRIPTION": ""
}}
'''
        },
        'script': {
            'name': 'uCODE Script',
            'extension': '.uscript',
            'content': '''# {title}
# Created: {date}
# Author: {username}

# Your commands here
HELP
'''
        }
    }

    def __init__(self, current_workspace: str = 'sandbox'):
        self.current_workspace = current_workspace
        self.udos_root = Path(os.getcwd())
        self._ensure_workspaces()

    def _ensure_workspaces(self):
        """Create workspace directories if they don't exist"""
        for ws_name, ws_config in self.WORKSPACES.items():
            ws_path = self.udos_root / ws_config['path']
            ws_path.mkdir(exist_ok=True)

    def get_workspace_path(self, workspace: Optional[str] = None) -> Path:
        """Get path for workspace"""
        ws = workspace or self.current_workspace
        if ws not in self.WORKSPACES:
            raise ValueError(f"Unknown workspace: {ws}")
        return self.udos_root / self.WORKSPACES[ws]['path']

    def list_workspaces(self) -> Dict[str, dict]:
        """Get all workspaces with file counts"""
        result = {}
        for ws_name, ws_config in self.WORKSPACES.items():
            ws_path = self.get_workspace_path(ws_name)
            files = list(ws_path.glob('*'))
            result[ws_name] = {
                **ws_config,
                'file_count': len([f for f in files if f.is_file()]),
                'current': ws_name == self.current_workspace
            }
        return result

    def switch_workspace(self, workspace: str) -> bool:
        """Switch to a different workspace"""
        if workspace not in self.WORKSPACES:
            return False
        self.current_workspace = workspace
        return True

    def list_files(self, workspace: Optional[str] = None,
                   pattern: str = '*') -> List[Path]:
        """List files in workspace"""
        ws_path = self.get_workspace_path(workspace)
        return sorted([f for f in ws_path.glob(pattern) if f.is_file()])

    def new_file(self, filename: str, template: str = 'blank',
                 workspace: Optional[str] = None,
                 variables: Optional[Dict] = None) -> Path:
        """Create new file from template"""
        if template not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template}")

        ws_path = self.get_workspace_path(workspace)
        template_config = self.TEMPLATES[template]

        # Add extension if not present
        if not any(filename.endswith(ext) for ext in ['.md', '.udo', '.txt', '.uscript']):
            filename += template_config['extension']

        filepath = ws_path / filename

        # Check if exists
        if filepath.exists():
            raise FileExistsError(f"File already exists: {filename}")

        # Prepare variables
        vars_dict = variables or {}
        vars_dict.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
        vars_dict.setdefault('username', os.getenv('USER', 'user'))
        vars_dict.setdefault('title', Path(filename).stem.replace('_', ' ').title())

        # Render template
        content = template_config['content'].format(**vars_dict)

        # Write file
        filepath.write_text(content)
        return filepath

    def delete_file(self, filename: str, workspace: Optional[str] = None) -> bool:
        """Delete file from workspace"""
        ws_path = self.get_workspace_path(workspace)
        filepath = ws_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        filepath.unlink()
        return True

    def copy_file(self, source: str, destination: str,
                  source_workspace: Optional[str] = None,
                  dest_workspace: Optional[str] = None) -> Path:
        """Copy file within or between workspaces"""
        src_path = self.get_workspace_path(source_workspace) / source
        dest_path = self.get_workspace_path(dest_workspace) / destination

        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        if dest_path.exists():
            raise FileExistsError(f"Destination exists: {destination}")

        shutil.copy2(src_path, dest_path)
        return dest_path

    def move_file(self, source: str, destination: str,
                  source_workspace: Optional[str] = None,
                  dest_workspace: Optional[str] = None) -> Path:
        """Move file within or between workspaces"""
        src_path = self.get_workspace_path(source_workspace) / source
        dest_path = self.get_workspace_path(dest_workspace) / destination

        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {source}")

        if dest_path.exists():
            raise FileExistsError(f"Destination exists: {destination}")

        shutil.move(str(src_path), str(dest_path))
        return dest_path

    def rename_file(self, old_name: str, new_name: str,
                   workspace: Optional[str] = None) -> Path:
        """Rename file in workspace"""
        ws_path = self.get_workspace_path(workspace)
        old_path = ws_path / old_name
        new_path = ws_path / new_name

        if not old_path.exists():
            raise FileNotFoundError(f"File not found: {old_name}")

        if new_path.exists():
            raise FileExistsError(f"File already exists: {new_name}")

        old_path.rename(new_path)
        return new_path
