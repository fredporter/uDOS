"""
Spatial Filesystem for uDOS v1.0.7+

Integrates filesystem paths with grid locations, Binders, content-tagging, and role-based access.

Architecture:
- Workspace hierarchy (vault/* for content, memory/* for runtime state)
- Grid location tagging (L###-Cell mappings)
- Content-tag indexing (front-matter extraction, metadata)
- Role-based access control (RBAC) — admin-only folders
- Binder integration (subfolders as chapters)

Example:
    fs = SpatialFilesystem(user_role='user')
    
    # Workspace operations
    fs.list_workspace('@sandbox')      # vault/sandbox
    fs.write_to_workspace('@bank', 'story.md', content)
    
    # Grid location tagging
    fs.tag_location('story.md', 'L300-AB15')
    locations = fs.find_by_location('L300-AB15')
    
    # Content discovery
    tags = fs.extract_tags('story.md')
    docs = fs.find_by_tags(['forest', 'adventure'])
    
    # Binder operations
    binder = fs.open_binder('@sandbox/my-project')
    chapters = binder.list_chapters()

Author: uDOS Development Team
Version: 1.0.7.0
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import re
from collections import defaultdict

from core.services.logging_api import get_logger

logger = get_logger('spatial-filesystem')


# =============================================================================
# Enums & Constants
# =============================================================================

class UserRole(Enum):
    """User role levels for access control."""
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'


class WorkspaceType(Enum):
    """Workspace types and their access requirements."""
    SANDBOX = 'sandbox'        # vault/sandbox — user writable
    BANK = 'bank'              # vault/bank — user writable
    INBOX = 'inbox'            # vault/inbox-dropbox — intake
    PUBLIC = 'public'          # vault/public-open-published — published/open
    SUBMISSIONS = 'submissions'  # vault/public-open-published/submissions — intake
    PRIVATE = 'private'        # vault/private-explicit — explicit/private share
    SHARED = 'shared'          # vault/private-shared — proximity verified share
    WIZARD = 'wizard'          # memory/wizard — wizard service only
    KNOWLEDGE = 'knowledge'    # /knowledge — admin only
    DEV = 'dev'                # /dev — admin only


# Workspace configuration
WORKSPACE_CONFIG = {
    WorkspaceType.SANDBOX: {
        'path': 'vault/sandbox',
        'roles': [UserRole.ADMIN, UserRole.USER],
        'description': 'Vault sandbox for experimentation'
    },
    WorkspaceType.BANK: {
        'path': 'vault/bank',
        'roles': [UserRole.ADMIN, UserRole.USER],
        'description': 'Vault bank (primary knowledge store)'
    },
    WorkspaceType.INBOX: {
        'path': 'vault/inbox-dropbox',
        'roles': [UserRole.ADMIN, UserRole.USER],
        'description': 'Inbox/Dropbox intake (raw notes, imports)'
    },
    WorkspaceType.PUBLIC: {
        'path': 'vault/public-open-published',
        'roles': [UserRole.ADMIN, UserRole.USER],
        'description': 'Public/open/published content'
    },
    WorkspaceType.SUBMISSIONS: {
        'path': 'vault/public-open-published/submissions',
        'roles': [UserRole.ADMIN, UserRole.USER],
        'description': 'Submission intake (pending/submitted/wiki-update-submitted)'
    },
    WorkspaceType.PRIVATE: {
        'path': 'vault/private-explicit',
        'roles': [UserRole.ADMIN, UserRole.USER],
        'description': 'Private explicit sharing (proximity verified)'
    },
    WorkspaceType.SHARED: {
        'path': 'vault/private-shared',
        'roles': [UserRole.ADMIN, UserRole.USER],
        'description': 'Shared vault space (verified proximity)'
    },
    WorkspaceType.WIZARD: {
        'path': 'memory/wizard',
        'roles': [UserRole.ADMIN],
        'description': 'Wizard service workspace (internal)'
    },
    WorkspaceType.KNOWLEDGE: {
        'path': 'knowledge',
        'roles': [UserRole.ADMIN],
        'description': 'Knowledge base (admin only)'
    },
    WorkspaceType.DEV: {
        'path': 'dev',
        'roles': [UserRole.ADMIN],
        'description': 'Development workspace (admin only)'
    }
}


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ContentMetadata:
    """Extracted content metadata from front-matter."""
    title: str = ''
    description: str = ''
    tags: List[str] = field(default_factory=list)
    grid_locations: List[str] = field(default_factory=list)  # L###-Cell
    binder_id: Optional[str] = None
    chapter: Optional[int] = None
    created_at: str = ''
    updated_at: str = ''
    author: str = ''
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileLocation:
    """Physical and logical location of a file."""
    workspace: WorkspaceType
    relative_path: str  # path relative to workspace
    absolute_path: Path
    grid_locations: List[str] = field(default_factory=list)
    metadata: Optional[ContentMetadata] = None
    last_indexed: str = ''


@dataclass
class GridLocation:
    """Grid location reference."""
    layer: int  # L###
    cell: str   # AA10
    
    def __str__(self) -> str:
        return f'L{self.layer}-{self.cell}'
    
    @classmethod
    def parse(cls, location_str: str) -> Optional['GridLocation']:
        """Parse 'L300-AA10' format."""
        match = re.match(r'^L(\d+)-([A-Z]{2}\d{2})$', location_str)
        if match:
            return cls(layer=int(match.group(1)), cell=match.group(2))
        return None


# =============================================================================
# Spatial Filesystem
# =============================================================================

class SpatialFilesystem:
    """
    Integrates filesystem with spatial grid, content-tagging, and role-based access.
    """
    
    def __init__(self, root_dir: Path = Path.cwd(), user_role: UserRole = UserRole.USER):
        """
        Initialize spatial filesystem.
        
        Args:
            root_dir: Root directory (typically uDOS root)
            user_role: User's access level
        """
        self.root_dir = Path(root_dir)
        self.user_role = user_role if isinstance(user_role, UserRole) else UserRole(user_role)

        # Metadata indexes
        self.location_index: Dict[str, Set[str]] = defaultdict(set)  # L###-Cell → file paths
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)       # tag → file paths
        self.binder_index: Dict[str, List[str]] = defaultdict(list)  # binder_id → chapters
        self.metadata_cache: Dict[str, ContentMetadata] = {}         # path → metadata
        
        # Ensure vault workspace folders exist (open-box layout)
        for config in WORKSPACE_CONFIG.values():
            path = config.get('path', '')
            if isinstance(path, str) and path.startswith('vault/'):
                (self.root_dir / path).mkdir(parents=True, exist_ok=True)

        logger.info(f'[LOCAL] Spatial filesystem initialized (role: {self.user_role.value})')
    
    # =========================================================================
    # Access Control
    # =========================================================================
    
    def has_access(self, workspace: WorkspaceType) -> bool:
        """Check if user has access to workspace."""
        required_roles = WORKSPACE_CONFIG[workspace]['roles']
        return self.user_role in required_roles
    
    def ensure_access(self, workspace: WorkspaceType) -> None:
        """Raise error if user doesn't have access."""
        if not self.has_access(workspace):
            raise PermissionError(
                f'Access denied: {self.user_role.value} cannot access {workspace.value}'
            )
    
    # =========================================================================
    # Workspace Operations
    # =========================================================================
    
    def get_workspace_path(self, workspace: WorkspaceType) -> Path:
        """Get absolute path for workspace."""
        config = WORKSPACE_CONFIG[workspace]
        path = self.root_dir / config['path']
        return path
    
    def resolve_workspace_reference(self, ref: str) -> Tuple[WorkspaceType, str]:
        """
        Resolve @workspace syntax.
        
        Args:
            ref: '@sandbox/story.md' or 'memory/sandbox/story.md'
        
        Returns:
            (WorkspaceType, relative_path)
        """
        if ref.startswith('@'):
            # @workspace/path syntax
            parts = ref[1:].split('/', 1)
            workspace_name = parts[0]
            relative_path = parts[1] if len(parts) > 1 else ''
            
            # Find workspace by name
            for ws_type, config in WORKSPACE_CONFIG.items():
                if ws_type.value == workspace_name or config['path'].endswith(workspace_name):
                    return ws_type, relative_path
            
            raise ValueError(f'Unknown workspace: @{workspace_name}')
        else:
            raise ValueError(f'Invalid workspace reference (must start with @): {ref}')
    
    def list_workspace(self, workspace_ref: str) -> List[FileLocation]:
        """List files in workspace."""
        ws_type, _ = self.resolve_workspace_reference(workspace_ref)
        self.ensure_access(ws_type)
        
        ws_path = self.get_workspace_path(ws_type)
        files = []
        
        if ws_path.exists():
            for item in ws_path.rglob('*'):
                if item.is_file():
                    relative_path = str(item.relative_to(ws_path))
                    metadata = self._extract_metadata(item)
                    files.append(FileLocation(
                        workspace=ws_type,
                        relative_path=relative_path,
                        absolute_path=item,
                        metadata=metadata
                    ))
        
        return files
    
    # =========================================================================
    # File Operations
    # =========================================================================
    
    def read_file(self, workspace_ref: str) -> str:
        """Read file from workspace."""
        ws_type, relative_path = self.resolve_workspace_reference(workspace_ref)
        self.ensure_access(ws_type)
        
        file_path = self.get_workspace_path(ws_type) / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')
        
        logger.info(f'[LOCAL] Read file: {workspace_ref}')
        return file_path.read_text(encoding='utf-8')
    
    def write_file(self, workspace_ref: str, content: str) -> FileLocation:
        """Write file to workspace."""
        from core.services.user_service import is_ghost_mode

        if is_ghost_mode():
            raise PermissionError("Ghost Mode is read-only (write blocked)")

        ws_type, relative_path = self.resolve_workspace_reference(workspace_ref)
        self.ensure_access(ws_type)
        
        ws_path = self.get_workspace_path(ws_type)
        file_path = ws_path / relative_path
        
        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_text(content, encoding='utf-8')
        logger.info(f'[LOCAL] Wrote file: {workspace_ref}')
        
        # Update indexes
        self._index_file(file_path, ws_type, relative_path)
        
        return FileLocation(
            workspace=ws_type,
            relative_path=relative_path,
            absolute_path=file_path,
            metadata=self._extract_metadata(file_path)
        )
    
    def delete_file(self, workspace_ref: str) -> None:
        """Delete file from workspace."""
        from core.services.user_service import is_ghost_mode

        if is_ghost_mode():
            raise PermissionError("Ghost Mode is read-only (delete blocked)")

        ws_type, relative_path = self.resolve_workspace_reference(workspace_ref)
        self.ensure_access(ws_type)
        
        file_path = self.get_workspace_path(ws_type) / relative_path
        if file_path.exists():
            file_path.unlink()
            logger.info(f'[LOCAL] Deleted file: {workspace_ref}')
    
    # =========================================================================
    # Metadata & Front-Matter
    # =========================================================================
    
    def _extract_metadata(self, file_path: Path) -> Optional[ContentMetadata]:
        """Extract front-matter metadata from markdown file."""
        if not file_path.suffix in ['.md', '.yaml', '.yml', '.json']:
            return None
        
        cache_key = str(file_path)
        if cache_key in self.metadata_cache:
            return self.metadata_cache[cache_key]
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            frontmatter_str = ''
            body = content

            # Extract YAML front-matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_str = parts[1]
                    body = parts[2]

            metadata_dict = yaml.safe_load(frontmatter_str) or {}

            tags = metadata_dict.get('tags', [])
            if isinstance(tags, str):
                tags = [t.strip().lstrip('#') for t in re.split(r'[ ,]+', tags) if t.strip()]
            elif tags is None:
                tags = []

            inline_tags = self._extract_inline_tags(body)
            merged_tags: List[str] = []
            seen: Set[str] = set()
            for tag in tags + inline_tags:
                tag_clean = str(tag).strip().lstrip('#')
                if not tag_clean:
                    continue
                key = tag_clean.lower()
                if key not in seen:
                    seen.add(key)
                    merged_tags.append(tag_clean)

            metadata = ContentMetadata(
                title=metadata_dict.get('title', ''),
                description=metadata_dict.get('description', ''),
                tags=merged_tags,
                grid_locations=metadata_dict.get('grid_locations', []),
                binder_id=metadata_dict.get('binder_id'),
                chapter=metadata_dict.get('chapter'),
                created_at=metadata_dict.get('created_at', ''),
                updated_at=metadata_dict.get('updated_at', str(datetime.now().isoformat())),
                author=metadata_dict.get('author', ''),
                custom_fields={
                    k: v for k, v in metadata_dict.items()
                    if k not in [
                        'title', 'description', 'tags', 'grid_locations',
                        'binder_id', 'chapter', 'created_at', 'updated_at', 'author'
                    ]
                }
            )

            self.metadata_cache[cache_key] = metadata
            return metadata
        except Exception as e:
            logger.warning(f'[LOCAL] Failed to extract metadata from {file_path}: {e}')
        
        return None

    def _extract_inline_tags(self, body: str) -> List[str]:
        """Extract Obsidian-style inline tags (#tag) from content body."""
        tags: List[str] = []
        in_code = False
        for line in body.splitlines():
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            for match in re.finditer(r'(?<!\w)#([A-Za-z0-9_-]+)', line):
                tags.append(match.group(1))
        return tags
    
    def _index_file(self, file_path: Path, workspace: WorkspaceType, relative_path: str) -> None:
        """Index file in location/tag indexes."""
        metadata = self._extract_metadata(file_path)
        if not metadata:
            return
        
        file_key = str(file_path)
        
        # Index by grid locations
        for location_str in metadata.grid_locations:
            if GridLocation.parse(location_str):
                self.location_index[location_str].add(file_key)
        
        # Index by tags
        for tag in metadata.tags:
            self.tag_index[tag.lower()].add(file_key)
        
        # Index by binder
        if metadata.binder_id:
            self.binder_index[metadata.binder_id].append(file_key)
        
        logger.info(f'[LOCAL] Indexed file: {relative_path} (tags: {metadata.tags})')
    
    # =========================================================================
    # Grid Location Operations
    # =========================================================================
    
    def tag_location(self, workspace_ref: str, location_str: str) -> None:
        """Tag file with grid location."""
        ws_type, relative_path = self.resolve_workspace_reference(workspace_ref)
        self.ensure_access(ws_type)
        
        file_path = self.get_workspace_path(ws_type) / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f'File not found: {file_path}')
        
        # Parse location
        location = GridLocation.parse(location_str)
        if not location:
            raise ValueError(f'Invalid grid location format: {location_str}')
        
        # Update front-matter
        content = file_path.read_text(encoding='utf-8')
        metadata = self._extract_metadata(file_path) or ContentMetadata()
        
        if str(location_str) not in metadata.grid_locations:
            metadata.grid_locations.append(str(location_str))
        
        # Write updated front-matter
        content_updated = self._update_frontmatter(content, metadata)
        file_path.write_text(content_updated, encoding='utf-8')
        
        # Update cache
        self.metadata_cache[str(file_path)] = metadata
        self.location_index[str(location_str)].add(str(file_path))
        
        logger.info(f'[LOCAL] Tagged {workspace_ref} with location: {location_str}')
    
    def find_by_location(self, location_str: str) -> List[FileLocation]:
        """Find files at grid location."""
        location = GridLocation.parse(location_str)
        if not location:
            raise ValueError(f'Invalid grid location format: {location_str}')
        
        file_keys = self.location_index.get(location_str, set())
        results = []
        
        for file_key in file_keys:
            file_path = Path(file_key)
            if file_path.exists():
                # Determine workspace
                for ws_type in WorkspaceType:
                    ws_path = self.get_workspace_path(ws_type)
                    try:
                        relative_path = str(file_path.relative_to(ws_path))
                        results.append(FileLocation(
                            workspace=ws_type,
                            relative_path=relative_path,
                            absolute_path=file_path,
                            grid_locations=[location_str],
                            metadata=self._extract_metadata(file_path)
                        ))
                        break
                    except ValueError:
                        continue
        
        return results
    
    # =========================================================================
    # Content Tagging
    # =========================================================================
    
    def extract_tags(self, workspace_ref: str) -> List[str]:
        """Extract tags from file."""
        ws_type, relative_path = self.resolve_workspace_reference(workspace_ref)
        self.ensure_access(ws_type)
        
        file_path = self.get_workspace_path(ws_type) / relative_path
        metadata = self._extract_metadata(file_path)
        
        return metadata.tags if metadata else []
    
    def find_by_tags(self, tags: List[str]) -> List[FileLocation]:
        """Find files matching any of the given tags."""
        tags_lower = [t.lower() for t in tags]
        file_keys: Set[str] = set()
        
        for tag in tags_lower:
            file_keys.update(self.tag_index.get(tag, set()))
        
        results = []
        for file_key in file_keys:
            file_path = Path(file_key)
            if file_path.exists():
                for ws_type in WorkspaceType:
                    ws_path = self.get_workspace_path(ws_type)
                    try:
                        relative_path = str(file_path.relative_to(ws_path))
                        results.append(FileLocation(
                            workspace=ws_type,
                            relative_path=relative_path,
                            absolute_path=file_path,
                            metadata=self._extract_metadata(file_path)
                        ))
                        break
                    except ValueError:
                        continue
        
        return results
    
    # =========================================================================
    # Binder Operations
    # =========================================================================
    
    def open_binder(self, workspace_ref: str) -> 'Binder':
        """Open binder from workspace."""
        ws_type, relative_path = self.resolve_workspace_reference(workspace_ref)
        self.ensure_access(ws_type)
        
        binder_path = self.get_workspace_path(ws_type) / relative_path
        return Binder(binder_path, self)
    
    def _update_frontmatter(self, content: str, metadata: ContentMetadata) -> str:
        """Update or create front-matter in markdown content."""
        frontmatter = {
            'title': metadata.title,
            'description': metadata.description,
            'tags': metadata.tags,
            'grid_locations': metadata.grid_locations,
            'binder_id': metadata.binder_id,
            'chapter': metadata.chapter,
            'created_at': metadata.created_at,
            'updated_at': metadata.updated_at or str(datetime.now().isoformat()),
            'author': metadata.author,
            **metadata.custom_fields
        }
        
        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)
        
        # Remove old front-matter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        return f'---\n{frontmatter_yaml}---\n{content}'


# =============================================================================
# Binder Integration
# =============================================================================

class Binder:
    """
    Represents a Binder (folder-based project with chapters).
    """
    
    def __init__(self, binder_path: Path, fs: SpatialFilesystem):
        """
        Initialize binder.
        
        Args:
            binder_path: Path to binder folder
            fs: Parent SpatialFilesystem instance
        """
        self.path = Path(binder_path)
        self.fs = fs
        self.chapters: List[Dict[str, Any]] = []
        
        self._scan_chapters()
    
    def _scan_chapters(self) -> None:
        """Scan folder for chapter files."""
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)
        
        self.chapters = []
        for item in sorted(self.path.glob('*.md')):
            metadata = self.fs._extract_metadata(item)
            self.chapters.append({
                'path': item,
                'filename': item.name,
                'chapter': metadata.chapter if metadata else None,
                'title': metadata.title if metadata else item.stem,
                'metadata': metadata
            })
        
        # Sort by chapter number
        self.chapters.sort(key=lambda x: x['chapter'] or 999)
    
    def list_chapters(self) -> List[Dict[str, Any]]:
        """List all chapters in binder."""
        return self.chapters
    
    def add_chapter(self, filename: str, content: str, chapter_num: int, title: str = '') -> None:
        """Add chapter to binder."""
        chapter_path = self.path / filename
        
        metadata = ContentMetadata(
            title=title or filename.replace('.md', ''),
            chapter=chapter_num
        )
        
        content_with_fm = self.fs._update_frontmatter(content, metadata)
        chapter_path.write_text(content_with_fm, encoding='utf-8')
        
        self._scan_chapters()
        logger.info(f'[LOCAL] Added chapter to binder: {filename}')


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    'SpatialFilesystem',
    'Binder',
    'UserRole',
    'WorkspaceType',
    'ContentMetadata',
    'FileLocation',
    'GridLocation',
    'WORKSPACE_CONFIG'
]
