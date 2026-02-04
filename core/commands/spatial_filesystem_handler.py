"""
Spatial Filesystem Handler for uDOS TUI

Commands:
    WORKSPACE list @sandbox              # List files in workspace
    WORKSPACE read @sandbox/story.md     # Read file
    WORKSPACE write @sandbox/file.md     # Write file
    WORKSPACE delete @sandbox/file.md    # Delete file
    
    LOCATION tag @sandbox/story.md L300-AB15   # Tag file with grid location
    LOCATION find L300-AB15                    # Find files at location
    
    TAG list @sandbox                    # List tags in workspace
    TAG find forest adventure            # Find files with tags
    
    BINDER open @sandbox/my-project      # Open binder
    BINDER list @sandbox/my-project      # List chapters
    BINDER add @sandbox/my-project chapter1.md "Chapter 1"

Author: uDOS Development Team
Version: 1.0.7.0
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

from core.services.spatial_filesystem import (
    SpatialFilesystem,
    UserRole,
    WorkspaceType,
    GridLocation
)
from core.services.logging_service import get_logger
from core.tui.renderer import Renderer

logger = get_logger('spatial-filesystem-handler')


class SpatialFilesystemHandler:
    """Handle spatial filesystem commands in TUI."""
    
    def __init__(self, fs: Optional[SpatialFilesystem] = None):
        """
        Initialize handler.
        
        Args:
            fs: SpatialFilesystem instance (created if None)
        """
        self.fs = fs or SpatialFilesystem(user_role=UserRole.USER)
        self.renderer = Renderer()
    
    # =========================================================================
    # Workspace Commands
    # =========================================================================
    
    def workspace_list(self, workspace_ref: str) -> str:
        """List files in workspace."""
        try:
            files = self.fs.list_workspace(workspace_ref)
            
            lines = [f'📁 Files in {workspace_ref}:']
            lines.append('')
            
            for file in files:
                tags = f" [{', '.join(file.metadata.tags)}]" if file.metadata and file.metadata.tags else ""
                locations = f" @ {file.metadata.grid_locations[0]}" if file.metadata and file.metadata.grid_locations else ""
                lines.append(f"  📄 {file.relative_path}{tags}{locations}")
            
            if not files:
                lines.append('  (empty)')
            
            return '\n'.join(lines)
        
        except PermissionError as e:
            return f'❌ Access denied: {e}'
        except Exception as e:
            return f'❌ Error: {e}'
    
    def workspace_read(self, workspace_ref: str) -> str:
        """Read file from workspace."""
        try:
            content = self.fs.read_file(workspace_ref)
            return content
        
        except FileNotFoundError:
            return f'❌ File not found: {workspace_ref}'
        except PermissionError as e:
            return f'❌ Access denied: {e}'
        except Exception as e:
            return f'❌ Error: {e}'
    
    def workspace_write(self, workspace_ref: str, content: str) -> str:
        """Write file to workspace."""
        try:
            location = self.fs.write_file(workspace_ref, content)
            return f'✅ Wrote: {workspace_ref}'
        
        except PermissionError as e:
            return f'❌ Access denied: {e}'
        except Exception as e:
            return f'❌ Error: {e}'
    
    def workspace_delete(self, workspace_ref: str) -> str:
        """Delete file from workspace."""
        try:
            self.fs.delete_file(workspace_ref)
            return f'✅ Deleted: {workspace_ref}'
        
        except PermissionError as e:
            return f'❌ Access denied: {e}'
        except Exception as e:
            return f'❌ Error: {e}'
    
    # =========================================================================
    # Location Commands
    # =========================================================================
    
    def location_tag(self, workspace_ref: str, location_str: str) -> str:
        """Tag file with grid location."""
        try:
            self.fs.tag_location(workspace_ref, location_str)
            return f'✅ Tagged {workspace_ref} → {location_str}'
        
        except ValueError as e:
            return f'❌ Invalid location: {e}'
        except FileNotFoundError:
            return f'❌ File not found: {workspace_ref}'
        except PermissionError as e:
            return f'❌ Access denied: {e}'
        except Exception as e:
            return f'❌ Error: {e}'
    
    def location_find(self, location_str: str) -> str:
        """Find files at grid location."""
        try:
            files = self.fs.find_by_location(location_str)
            
            lines = [f'📍 Files at {location_str}:']
            lines.append('')
            
            for file in files:
                lines.append(f"  📄 @{file.workspace.value}/{file.relative_path}")
                if file.metadata and file.metadata.title:
                    lines.append(f"     Title: {file.metadata.title}")
            
            if not files:
                lines.append('  (no files found)')
            
            return '\n'.join(lines)
        
        except ValueError as e:
            return f'❌ Invalid location: {e}'
        except Exception as e:
            return f'❌ Error: {e}'
    
    # =========================================================================
    # Tag Commands
    # =========================================================================
    
    def tag_list(self, workspace_ref: str) -> str:
        """List tags used in workspace."""
        try:
            files = self.fs.list_workspace(workspace_ref)
            
            all_tags: Dict[str, int] = {}
            for file in files:
                if file.metadata:
                    for tag in file.metadata.tags:
                        all_tags[tag] = all_tags.get(tag, 0) + 1
            
            lines = [f'🏷️  Tags in {workspace_ref}:']
            lines.append('')
            
            for tag, count in sorted(all_tags.items(), key=lambda x: -x[1]):
                lines.append(f"  {tag} ({count})")
            
            if not all_tags:
                lines.append('  (no tags)')
            
            return '\n'.join(lines)
        
        except Exception as e:
            return f'❌ Error: {e}'
    
    def tag_find(self, *tags: str) -> str:
        """Find files with any of the given tags."""
        try:
            files = self.fs.find_by_tags(list(tags))
            
            lines = [f'🔍 Files tagged with: {", ".join(tags)}']
            lines.append('')
            
            for file in files:
                lines.append(f"  📄 @{file.workspace.value}/{file.relative_path}")
                if file.metadata and file.metadata.title:
                    lines.append(f"     {file.metadata.title}")
                if file.metadata and file.metadata.tags:
                    matching = [t for t in file.metadata.tags if t.lower() in [x.lower() for x in tags]]
                    if matching:
                        lines.append(f"     Tags: {', '.join(matching)}")
            
            if not files:
                lines.append('  (no matches)')
            
            return '\n'.join(lines)
        
        except Exception as e:
            return f'❌ Error: {e}'
    
    # =========================================================================
    # Binder Commands
    # =========================================================================
    
    def binder_open(self, workspace_ref: str) -> str:
        """Open binder."""
        try:
            binder = self.fs.open_binder(workspace_ref)
            chapters = binder.list_chapters()
            
            lines = [f'📚 Binder: {workspace_ref}']
            lines.append(f'   Chapters: {len(chapters)}')
            lines.append('')
            
            for chapter in chapters:
                ch_num = f"Ch {chapter['chapter']}" if chapter['chapter'] is not None else "   "
                lines.append(f"  {ch_num}: {chapter['title']}")
            
            return '\n'.join(lines)
        
        except Exception as e:
            return f'❌ Error: {e}'
    
    def binder_list(self, workspace_ref: str) -> str:
        """Alias for binder_open."""
        return self.binder_open(workspace_ref)
    
    def binder_add(self, workspace_ref: str, filename: str, content: str = '', title: str = '') -> str:
        """Add chapter to binder."""
        try:
            binder = self.fs.open_binder(workspace_ref)
            chapter_num = len(binder.list_chapters()) + 1
            binder.add_chapter(filename, content, chapter_num, title)
            return f'✅ Added chapter: {filename}'
        
        except Exception as e:
            return f'❌ Error: {e}'
    
    # =========================================================================
    # Utility
    # =========================================================================
    
    def get_workspace_info(self) -> str:
        """Show workspace configuration and access levels."""
        lines = ['📊 Workspace Configuration:']
        lines.append(f'   User Role: {self.fs.user_role.value}')
        lines.append('')
        
        from core.services.spatial_filesystem import WORKSPACE_CONFIG
        
        for ws_type, config in WORKSPACE_CONFIG.items():
            can_access = self.fs.has_access(ws_type)
            access_str = '✅' if can_access else '❌'
            lines.append(f'  {access_str} @{ws_type.value}  ({config["path"]})')
            lines.append(f'      {config["description"]}')
        
        return '\n'.join(lines)
    
    def help(self) -> str:
        """Show help for spatial filesystem commands."""
        return """
🗂️  SPATIAL FILESYSTEM COMMANDS

📁 WORKSPACE Operations:
  WORKSPACE list @workspace              - List files
  WORKSPACE read @workspace/file.md      - Read file
  WORKSPACE write @workspace/file.md     - Write file
  WORKSPACE delete @workspace/file.md    - Delete file

📍 LOCATION Tagging:
  LOCATION tag @ws/file.md L300-AB15     - Tag with grid location
  LOCATION find L300-AB15                - Find files at location

🏷️  TAG Discovery:
  TAG list @workspace                    - List tags in workspace
  TAG find forest adventure              - Find files with tags

📚 BINDER Management:
  BINDER open @ws/project                - Open binder
  BINDER list @ws/project                - List chapters
  BINDER add @ws/project file.md         - Add chapter

✨ INFO:
  WORKSPACE INFO                         - Show config & access levels
  WORKSPACE HELP                         - Show this help

Workspaces (vault-first):
  @sandbox     - Vault sandbox (vault/sandbox)
  @bank        - Vault bank (vault/bank)
  @inbox       - Inbox/Dropbox intake (vault/inbox-dropbox)
  @public      - Public/open/published (vault/public-open-published)
  @submissions - Submissions intake (vault/public-open-published/submissions)
  @private     - Private explicit share (vault/private-explicit)
  @shared      - Private shared (vault/private-shared)
  @wizard      - Wizard service (memory/wizard) [admin only]
  @knowledge   - Knowledge base (/knowledge) [admin only]
  @dev         - Development (/dev) [admin only]
""".strip()


# =============================================================================
# Command Dispatcher
# =============================================================================

def dispatch_spatial_command(handler: SpatialFilesystemHandler, args: List[str]) -> str:
    """
    Dispatch spatial filesystem command.
    
    Usage:
        dispatch_spatial_command(handler, ['WORKSPACE', 'list', '@sandbox'])
    """
    if not args:
        return handler.help()
    
    command = args[0].upper()
    subcommand = args[1].upper() if len(args) > 1 else ''
    
    try:
        # Workspace commands
        if command == 'WORKSPACE':
            if subcommand == 'LIST':
                return handler.workspace_list(args[2]) if len(args) > 2 else '❌ Usage: WORKSPACE list @workspace'
            elif subcommand == 'READ':
                return handler.workspace_read(args[2]) if len(args) > 2 else '❌ Usage: WORKSPACE read @ws/file'
            elif subcommand == 'WRITE':
                # Would need interactive input for content
                return '❌ WORKSPACE write requires interactive input'
            elif subcommand == 'DELETE':
                return handler.workspace_delete(args[2]) if len(args) > 2 else '❌ Usage: WORKSPACE delete @ws/file'
            elif subcommand == 'INFO':
                return handler.get_workspace_info()
            elif subcommand == 'HELP':
                return handler.help()
        
        # Location commands
        elif command == 'LOCATION':
            if subcommand == 'TAG':
                if len(args) > 3:
                    return handler.location_tag(args[2], args[3])
                return '❌ Usage: LOCATION tag @ws/file.md L300-AB15'
            elif subcommand == 'FIND':
                return handler.location_find(args[2]) if len(args) > 2 else '❌ Usage: LOCATION find L300-AB15'
        
        # Tag commands
        elif command == 'TAG':
            if subcommand == 'LIST':
                return handler.tag_list(args[2]) if len(args) > 2 else '❌ Usage: TAG list @workspace'
            elif subcommand == 'FIND':
                if len(args) > 2:
                    return handler.tag_find(*args[2:])
                return '❌ Usage: TAG find tag1 tag2 ...'
        
        # Binder commands
        elif command == 'BINDER':
            if subcommand in ['OPEN', 'LIST']:
                return handler.binder_open(args[2]) if len(args) > 2 else '❌ Usage: BINDER open @ws/project'
            elif subcommand == 'ADD':
                if len(args) > 3:
                    title = args[4] if len(args) > 4 else ''
                    return handler.binder_add(args[2], args[3], title=title)
                return '❌ Usage: BINDER add @ws/project filename.md "Title"'
        
        # Help
        elif command in ['HELP', '?']:
            return handler.help()
        
        else:
            return f'❌ Unknown command: {command}'
    
    except Exception as e:
        logger.error(f'[LOCAL] Command error: {e}')
        return f'❌ Error: {e}'


__all__ = [
    'SpatialFilesystemHandler',
    'dispatch_spatial_command'
]
