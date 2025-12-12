"""
Workspace-Aware File Browser (v1.2.13)

Provides filtered file navigation for:
- /knowledge (read-only knowledge base)
- /memory/docs (user documentation)
- /memory/drafts (work in progress)
- /memory/ucode/sandbox (experimental scripts)
- /memory/ucode/scripts (user scripts)

Features:
- Filtered views (.upy, .md, .json only)
- Workspace switcher
- Recursive subdirectory navigation
- Breadcrumb paths
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Callable
from pathlib import Path
from enum import Enum
from core.utils.column_formatter import ColumnFormatter, ColumnConfig


class Workspace(Enum):
    """Available workspace locations"""
    KNOWLEDGE = "knowledge"
    DOCS = "memory/docs"
    DRAFTS = "memory/drafts"
    SANDBOX = "memory/ucode/sandbox"
    SCRIPTS = "memory/ucode/scripts"


@dataclass
class FileEntry:
    """File or directory entry"""
    path: Path
    name: str
    is_dir: bool
    extension: str = ""
    size: int = 0
    
    def __post_init__(self):
        if not self.is_dir and not self.extension:
            self.extension = self.path.suffix
        if self.path.exists() and not self.is_dir:
            self.size = self.path.stat().st_size


@dataclass
class BrowserState:
    """Current browser state"""
    workspace: Workspace = Workspace.SCRIPTS
    current_path: Path = None
    entries: List[FileEntry] = None
    selection_index: int = 0
    scroll_offset: int = 0
    filter_extensions: List[str] = None
    show_hidden: bool = False
    recent_files: List[str] = None  # v1.2.16 - Recent file paths
    bookmarks: List[str] = None     # v1.2.16 - Bookmarked paths
    workspace_paths: Dict[str, str] = None  # v1.2.16 - Last path per workspace
    column_mode: bool = False       # v1.2.16 - Use 3-column layout
    show_preview: bool = True       # v1.2.16 - Show file preview in column mode
    
    def __post_init__(self):
        if self.entries is None:
            self.entries = []
        if self.filter_extensions is None:
            self.filter_extensions = ['.upy', '.md', '.json']
        if self.recent_files is None:
            self.recent_files = []
        if self.bookmarks is None:
            self.bookmarks = []
        if self.workspace_paths is None:
            self.workspace_paths = {}


class FileBrowser:
    """
    Workspace-aware file browser with filtering.
    
    Workspaces:
    - knowledge: Core distributable knowledge base (read-only)
    - docs: User documentation and guides
    - drafts: Work in progress documents
    - sandbox: Experimental uPY scripts
    - scripts: User uPY scripts
    
    Navigation:
    - 8/2: Move selection up/down
    - 4: Go to parent directory
    - 6: Enter directory
    - 5: Select file
    - 0: Switch workspace
    """
    
    def __init__(self, root_path: Path = None):
        from core.utils.paths import PATHS
        self.root = root_path or PATHS.ROOT
        self.state = BrowserState()
        self.formatter = ColumnFormatter(ColumnConfig(width=60))
        
        # Workspace paths
        self.workspaces = {
            Workspace.KNOWLEDGE: self.root / "knowledge",
            Workspace.DOCS: self.root / "memory" / "docs",
            Workspace.DRAFTS: self.root / "memory" / "drafts",
            Workspace.SANDBOX: self.root / "memory" / "ucode" / "sandbox",
            Workspace.SCRIPTS: self.root / "memory" / "ucode" / "scripts",
        }
        
        # Load saved state (v1.2.16)
        self._load_state()
        
        # Initialize to scripts workspace
        self.set_workspace(Workspace.SCRIPTS)
    
    def set_workspace(self, workspace: Workspace):
        """Switch to a different workspace"""
        # Remember current path before switching (v1.2.16)
        if self.state.current_path:
            self.remember_workspace_path()
        
        self.state.workspace = workspace
        
        # Try to restore last path for this workspace (v1.2.16)
        restored_path = self.restore_workspace_path(workspace)
        if restored_path:
            self.state.current_path = restored_path
            self._refresh_entries()
        else:
            # Use workspace root
            workspace_path = self.workspaces.get(workspace)
            
            if workspace_path and workspace_path.exists():
                self.state.current_path = workspace_path
                self._refresh_entries()
            else:
                # Create workspace if it doesn't exist (except knowledge)
                if workspace != Workspace.KNOWLEDGE:
                    workspace_path.mkdir(parents=True, exist_ok=True)
                    self.state.current_path = workspace_path
                    self._refresh_entries()
    
    def _refresh_entries(self):
        """Scan current directory and populate entries"""
        if not self.state.current_path or not self.state.current_path.exists():
            self.state.entries = []
            return
        
        entries = []
        
        try:
            # Get all items in current directory
            items = sorted(self.state.current_path.iterdir(), 
                          key=lambda p: (not p.is_dir(), p.name.lower()))
            
            for item in items:
                # Skip hidden files unless enabled
                if item.name.startswith('.') and not self.state.show_hidden:
                    continue
                
                if item.is_dir():
                    # Always show directories
                    entries.append(FileEntry(
                        path=item,
                        name=item.name,
                        is_dir=True
                    ))
                else:
                    # Filter files by extension
                    if self.state.filter_extensions:
                        if item.suffix in self.state.filter_extensions:
                            entries.append(FileEntry(
                                path=item,
                                name=item.name,
                                is_dir=False,
                                extension=item.suffix,
                                size=item.stat().st_size
                            ))
                    else:
                        # No filter, show all files
                        entries.append(FileEntry(
                            path=item,
                            name=item.name,
                            is_dir=False,
                            extension=item.suffix,
                            size=item.stat().st_size
                        ))
            
            self.state.entries = entries
            
            # Reset selection if out of bounds
            if self.state.selection_index >= len(entries):
                self.state.selection_index = max(0, len(entries) - 1)
        
        except PermissionError:
            self.state.entries = []
    
    def navigate_up(self) -> bool:
        """Move selection up"""
        if self.state.selection_index > 0:
            self.state.selection_index -= 1
            # Adjust scroll
            if self.state.selection_index < self.state.scroll_offset:
                self.state.scroll_offset = self.state.selection_index
            return True
        return False
    
    def navigate_down(self) -> bool:
        """Move selection down"""
        if self.state.selection_index < len(self.state.entries) - 1:
            self.state.selection_index += 1
            # Adjust scroll (assume 10 visible items)
            if self.state.selection_index >= self.state.scroll_offset + 10:
                self.state.scroll_offset += 1
            return True
        return False
    
    def navigate_parent(self) -> bool:
        """Go to parent directory"""
        if self.state.current_path:
            workspace_root = self.workspaces[self.state.workspace]
            # Don't go above workspace root
            if self.state.current_path != workspace_root:
                self.state.current_path = self.state.current_path.parent
                self._refresh_entries()
                self.state.selection_index = 0
                self.state.scroll_offset = 0
                return True
        return False
    
    def navigate_into(self) -> Optional[Path]:
        """
        Enter selected directory.
        
        Returns:
            New path if entered directory, None otherwise
        """
        if not self.state.entries:
            return None
        
        if 0 <= self.state.selection_index < len(self.state.entries):
            entry = self.state.entries[self.state.selection_index]
            if entry.is_dir:
                self.state.current_path = entry.path
                self._refresh_entries()
                self.state.selection_index = 0
                self.state.scroll_offset = 0
                return entry.path
        return None
    
    def select_current(self) -> Optional[FileEntry]:
        """
        Select current entry.
        
        Returns:
            Selected FileEntry or None
        """
        if not self.state.entries:
            return None
        
        if 0 <= self.state.selection_index < len(self.state.entries):
            return self.state.entries[self.state.selection_index]
        return None
    
    def get_breadcrumb(self) -> str:
        """Get breadcrumb path from workspace root"""
        if not self.state.current_path:
            return ""
        
        workspace_root = self.workspaces[self.state.workspace]
        try:
            relative = self.state.current_path.relative_to(workspace_root)
            parts = [self.state.workspace.value] + list(relative.parts)
            return " > ".join(parts)
        except ValueError:
            return str(self.state.current_path)
    
    def render(self, viewport_height: int = 10) -> List[str]:
        """
        Render browser view.
        
        Args:
            viewport_height: Number of visible entries
            
        Returns:
            List of formatted lines
        """
        lines = []
        
        # Header
        breadcrumb = f"📁 {self.get_breadcrumb()}"
        lines.append(self.formatter.box_top("File Browser"))
        lines.append(self.formatter.box_line(breadcrumb, align="left"))
        lines.append(self.formatter.box_separator())
        lines.append("─" * 60)
        
        # Entries
        if not self.state.entries:
            lines.append("  (empty directory)")
        else:
            start = self.state.scroll_offset
            end = min(start + viewport_height, len(self.state.entries))
            
            for i in range(start, end):
                entry = self.state.entries[i]
                
                # Selection indicator
                marker = "▶" if i == self.state.selection_index else " "
                
                # Icon based on type
                if entry.is_dir:
                    icon = "📁"
                    size_str = "<DIR>"
                else:
                    # Icon by extension
                    if entry.extension == '.upy':
                        icon = "🐍"
                    elif entry.extension == '.md':
                        icon = "📄"
                    elif entry.extension == '.json':
                        icon = "📊"
                    else:
                        icon = "📄"
                    
                    # Format size
                    if entry.size < 1024:
                        size_str = f"{entry.size}B"
                    elif entry.size < 1024 * 1024:
                        size_str = f"{entry.size / 1024:.1f}KB"
                    else:
                        size_str = f"{entry.size / (1024 * 1024):.1f}MB"
                
                # Format line
                line = f"{marker} {icon} {entry.name:<40} {size_str:>10}"
                lines.append(line)
            
            # Scroll indicators
            if start > 0:
                lines.insert(3, "  ▲ More above")
            if end < len(self.state.entries):
                lines.append("  ▼ More below")
        
        # Footer
        lines.append("─" * 60)
        total = len(self.state.entries)
        filtered = len([e for e in self.state.entries if not e.is_dir])
        lines.append(f"Total: {total} items ({filtered} files) | "
                    f"Filter: {', '.join(self.state.filter_extensions)}")
        lines.append("8/2: Navigate | 4: Parent | 6: Enter | 5: Select | 0: Switch Workspace")
        
        return lines
    
    def render_columns(self, terminal_width: int = 120) -> List[str]:
        """
        Render 3-column layout: workspaces | files | preview.
        
        Args:
            terminal_width: Terminal width in characters
            
        Returns:
            List of formatted lines
        """
        import shutil
        
        # Get actual terminal width if not provided
        if terminal_width == 120:
            try:
                terminal_width = shutil.get_terminal_size().columns
            except:
                pass
        
        # Calculate column widths (responsive)
        if terminal_width < 80:
            # Narrow: just files (fall back to normal render)
            return self.render()
        elif terminal_width < 120:
            # Medium: workspaces + files
            ws_width = 20
            file_width = terminal_width - ws_width - 3
            preview_width = 0
        else:
            # Wide: all 3 columns
            ws_width = 20
            preview_width = 40
            file_width = terminal_width - ws_width - preview_width - 6
        
        lines = []
        viewport_height = 15  # Fixed height for consistency
        
        # Header
        header = "═" * terminal_width
        lines.append(header)
        
        # Title row
        title = f"📁 {self.get_breadcrumb()}"
        lines.append(title[:terminal_width])
        lines.append("─" * terminal_width)
        
        # Build columns
        workspace_lines = self._render_workspace_column(ws_width, viewport_height)
        file_lines = self._render_file_column(file_width, viewport_height)
        preview_lines = self._render_preview_column(preview_width, viewport_height) if preview_width > 0 else []
        
        # Combine columns side-by-side
        for i in range(viewport_height):
            ws_line = workspace_lines[i] if i < len(workspace_lines) else " " * ws_width
            file_line = file_lines[i] if i < len(file_lines) else " " * file_width
            
            if preview_width > 0:
                preview_line = preview_lines[i] if i < len(preview_lines) else " " * preview_width
                combined = f"{ws_line} │ {file_line} │ {preview_line}"
            else:
                combined = f"{ws_line} │ {file_line}"
            
            lines.append(combined[:terminal_width])
        
        # Footer
        lines.append("─" * terminal_width)
        total = len(self.state.entries)
        filtered = len([e for e in self.state.entries if not e.is_dir])
        footer = f"Total: {total} items ({filtered} files) | Filter: {', '.join(self.state.filter_extensions)}"
        lines.append(footer[:terminal_width])
        
        controls = "8/2: Navigate | 4: Parent | 6: Enter | 5: Select | 0: Workspace | V: Toggle View"
        lines.append(controls[:terminal_width])
        
        return lines
    
    def _render_workspace_column(self, width: int, height: int) -> List[str]:
        """Render workspace selector column"""
        lines = []
        lines.append("WORKSPACES".center(width))
        lines.append("─" * width)
        
        for ws in Workspace:
            marker = "▶" if ws == self.state.workspace else " "
            name = ws.value.split('/')[-1][:width-3]  # Last part of path
            line = f"{marker} {name}"
            lines.append(line.ljust(width)[:width])
        
        # Pad to height
        while len(lines) < height:
            lines.append(" " * width)
        
        return lines[:height]
    
    def _render_file_column(self, width: int, height: int) -> List[str]:
        """Render file list column"""
        lines = []
        lines.append("FILES".center(width))
        lines.append("─" * width)
        
        if not self.state.entries:
            lines.append("(empty)".center(width))
        else:
            start = self.state.scroll_offset
            end = min(start + height - 4, len(self.state.entries))  # Leave room for header
            
            if start > 0:
                lines.append("▲ More above".center(width))
            
            for i in range(start, end):
                entry = self.state.entries[i]
                
                # Selection marker
                marker = "▶" if i == self.state.selection_index else " "
                
                # Icon
                if entry.is_dir:
                    icon = "📁"
                elif entry.extension == '.upy':
                    icon = "🐍"
                elif entry.extension == '.md':
                    icon = "📄"
                elif entry.extension == '.json':
                    icon = "📊"
                else:
                    icon = "📄"
                
                # Bookmark indicator
                bookmark = "★" if self.is_bookmarked(entry.path) else " "
                
                # Format name to fit
                max_name = width - 6  # marker + icon + bookmark + spaces
                name = entry.name[:max_name]
                
                line = f"{marker}{icon}{bookmark} {name}"
                lines.append(line.ljust(width)[:width])
            
            if end < len(self.state.entries):
                lines.append("▼ More below".center(width))
        
        # Pad to height
        while len(lines) < height:
            lines.append(" " * width)
        
        return lines[:height]
    
    def _render_preview_column(self, width: int, height: int) -> List[str]:
        """Render file preview column"""
        lines = []
        lines.append("PREVIEW".center(width))
        lines.append("─" * width)
        
        # Get selected file
        selected = self.select_current()
        
        if selected and not selected.is_dir and selected.path.exists():
            try:
                # Show file info
                size_kb = selected.size / 1024
                lines.append(f"Size: {size_kb:.1f}KB".ljust(width)[:width])
                lines.append(f"Type: {selected.extension}".ljust(width)[:width])
                lines.append("─" * width)
                
                # Show preview content
                if selected.size < 10240:  # Only preview files < 10KB
                    content = selected.path.read_text(errors='ignore')
                    preview_lines = content.split('\n')[:height - 6]
                    
                    for line in preview_lines:
                        # Truncate to fit
                        display_line = line.replace('\t', '  ')[:width]
                        lines.append(display_line.ljust(width)[:width])
                else:
                    lines.append("(file too large)".center(width))
            except Exception as e:
                lines.append("(preview error)".center(width))
        elif selected and selected.is_dir:
            # Show directory info
            try:
                items = list(selected.path.iterdir())
                lines.append(f"Items: {len(items)}".ljust(width)[:width])
                lines.append("─" * width)
                
                for item in items[:height - 5]:
                    icon = "📁" if item.is_dir() else "📄"
                    name = item.name[:width - 3]
                    lines.append(f"{icon} {name}".ljust(width)[:width])
            except:
                lines.append("(no access)".center(width))
        else:
            lines.append("(no selection)".center(width))
        
        # Pad to height
        while len(lines) < height:
            lines.append(" " * width)
        
        return lines[:height]
    
    def toggle_column_mode(self) -> bool:
        """
        Toggle between single-column and 3-column view.
        
        Returns:
            New column_mode state
        """
        self.state.column_mode = not self.state.column_mode
        self._save_state()
        return self.state.column_mode
    
    def set_column_mode(self, enabled: bool) -> None:
        """Set column mode explicitly"""
        self.state.column_mode = enabled
        self._save_state()
    
    def cycle_workspace(self) -> Workspace:
        """Cycle to next workspace"""
        workspaces = list(Workspace)
        current_idx = workspaces.index(self.state.workspace)
        next_idx = (current_idx + 1) % len(workspaces)
        next_workspace = workspaces[next_idx]
        self.set_workspace(next_workspace)
        return next_workspace
    
    def search(self, query: str) -> Optional[FileEntry]:
        """
        Search for file/folder by name.
        
        Returns:
            First matching entry or None
        """
        query_lower = query.lower()
        for i, entry in enumerate(self.state.entries):
            if query_lower in entry.name.lower():
                self.state.selection_index = i
                # Adjust scroll to show selection
                if i < self.state.scroll_offset:
                    self.state.scroll_offset = i
                elif i >= self.state.scroll_offset + 10:
                    self.state.scroll_offset = max(0, i - 9)
                return entry
        return None
    
    def set_filter(self, extensions: List[str]):
        """Update file extension filter"""
        self.state.filter_extensions = extensions
        self._refresh_entries()
    
    def toggle_hidden(self):
        """Toggle showing hidden files"""
        self.state.show_hidden = not self.state.show_hidden
        self._refresh_entries()
    
    def get_stats(self) -> Dict:
        """Get statistics about current workspace"""
        stats = {
            "workspace": self.state.workspace.value,
            "path": str(self.state.current_path),
            "total_entries": len(self.state.entries),
            "directories": len([e for e in self.state.entries if e.is_dir]),
            "files": len([e for e in self.state.entries if not e.is_dir]),
        }
        
        # Count by extension
        ext_counts = {}
        for entry in self.state.entries:
            if not entry.is_dir:
                ext = entry.extension or "(no ext)"
                ext_counts[ext] = ext_counts.get(ext, 0) + 1
        stats["by_extension"] = ext_counts
        
        return stats
    
    # ====== File Operations (v1.2.16) ======
    
    def open_file(self, entry: FileEntry = None) -> Optional[Dict]:
        """
        Open selected file for viewing/editing.
        
        Args:
            entry: FileEntry to open (uses current selection if None)
            
        Returns:
            Dict with action details or None if failed
        """
        if entry is None:
            entry = self.select_current()
        
        if entry is None or entry.is_dir:
            return None
        
        # Add to recent files (v1.2.16)
        self.add_recent_file(entry.path)
        
        return {
            "action": "open_file",
            "path": str(entry.path),
            "name": entry.name,
            "extension": entry.extension,
            "size": entry.size
        }
    
    def copy_file(self, source: FileEntry = None, dest_path: Path = None) -> Optional[Dict]:
        """
        Copy selected file.
        
        Args:
            source: FileEntry to copy (uses current selection if None)
            dest_path: Destination path (prompts if None)
            
        Returns:
            Dict with action details or None if failed
        """
        import shutil
        
        if source is None:
            source = self.select_current()
        
        if source is None or source.is_dir:
            return {"error": "Cannot copy directories (use recursive copy)"}
        
        if dest_path is None:
            # Return request for destination
            return {
                "action": "copy_file",
                "source": str(source.path),
                "name": source.name,
                "needs_destination": True
            }
        
        try:
            shutil.copy2(source.path, dest_path)
            return {
                "action": "copy_file",
                "source": str(source.path),
                "destination": str(dest_path),
                "success": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def move_file(self, source: FileEntry = None, dest_path: Path = None) -> Optional[Dict]:
        """
        Move/rename selected file.
        
        Args:
            source: FileEntry to move (uses current selection if None)
            dest_path: Destination path (prompts if None)
            
        Returns:
            Dict with action details or None if failed
        """
        import shutil
        
        if source is None:
            source = self.select_current()
        
        if source is None:
            return {"error": "No file selected"}
        
        if dest_path is None:
            # Return request for destination
            return {
                "action": "move_file",
                "source": str(source.path),
                "name": source.name,
                "is_dir": source.is_dir,
                "needs_destination": True
            }
        
        try:
            shutil.move(source.path, dest_path)
            self._refresh_entries()
            return {
                "action": "move_file",
                "source": str(source.path),
                "destination": str(dest_path),
                "success": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def delete_file(self, entry: FileEntry = None, confirm: bool = False) -> Optional[Dict]:
        """
        Delete selected file (with confirmation).
        
        Args:
            entry: FileEntry to delete (uses current selection if None)
            confirm: Confirmation flag (prompts if False)
            
        Returns:
            Dict with action details or None if failed
        """
        if entry is None:
            entry = self.select_current()
        
        if entry is None:
            return {"error": "No file selected"}
        
        if not confirm:
            # Return request for confirmation
            return {
                "action": "delete_file",
                "path": str(entry.path),
                "name": entry.name,
                "is_dir": entry.is_dir,
                "size": entry.size if not entry.is_dir else None,
                "needs_confirmation": True
            }
        
        try:
            if entry.is_dir:
                import shutil
                shutil.rmtree(entry.path)
            else:
                entry.path.unlink()
            
            self._refresh_entries()
            return {
                "action": "delete_file",
                "path": str(entry.path),
                "name": entry.name,
                "success": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    def create_from_template(self, template_name: str, filename: str) -> Optional[Dict]:
        """
        Create new file from template.
        
        Args:
            template_name: Template identifier (e.g., "mission", "script", "guide")
            filename: Name for new file
            
        Returns:
            Dict with action details or None if failed
        """
        templates = {
            "mission": {
                "extension": ".upy",
                "content": '''# Mission: {name}
# Created: {date}
# Status: DRAFT

META(
    id="${{MISSION.ID}}",
    name="{name}",
    objective="TODO: Define mission objective"
)

# TODO: Add mission steps
PRINT("Mission started!")
'''
            },
            "script": {
                "extension": ".upy",
                "content": '''# uPY Script: {name}
# Created: {date}

# TODO: Add script logic
PRINT("Script executed!")
'''
            },
            "guide": {
                "extension": ".md",
                "content": '''# {name}

## Overview

TODO: Add guide content

## Steps

1. Step 1
2. Step 2
3. Step 3

## Notes

- Note 1
- Note 2
'''
            },
            "note": {
                "extension": ".md",
                "content": '''# {name}

Created: {date}

## Content

TODO: Add note content
'''
            }
        }
        
        if template_name not in templates:
            return {"error": f"Unknown template: {template_name}"}
        
        template = templates[template_name]
        
        # Add extension if not present
        if not filename.endswith(template["extension"]):
            filename += template["extension"]
        
        # Generate content
        from datetime import datetime
        content = template["content"].format(
            name=filename.replace(template["extension"], ""),
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Create file in current directory
        new_path = self.state.current_path / filename
        
        if new_path.exists():
            return {"error": f"File already exists: {filename}"}
        
        try:
            new_path.write_text(content)
            self._refresh_entries()
            
            # Select newly created file
            for i, entry in enumerate(self.state.entries):
                if entry.path == new_path:
                    self.state.selection_index = i
                    break
            
            return {
                "action": "create_from_template",
                "template": template_name,
                "path": str(new_path),
                "name": filename,
                "success": True
            }
        except Exception as e:
            return {"error": str(e)}
    
    # ====== Workspace Management (v1.2.16) ======
    
    def add_recent_file(self, file_path: Path) -> None:
        """
        Add file to recent files list (max 10).
        
        Args:
            file_path: Path to file to add to recents
        """
        path_str = str(file_path)
        
        # Remove if already in list
        if path_str in self.state.recent_files:
            self.state.recent_files.remove(path_str)
        
        # Add to front
        self.state.recent_files.insert(0, path_str)
        
        # Keep only last 10
        self.state.recent_files = self.state.recent_files[:10]
        
        # Save state
        self._save_state()
    
    def get_recent_files(self) -> List[Dict]:
        """
        Get recent files with existence check.
        
        Returns:
            List of dicts with file info (path, name, exists)
        """
        recents = []
        for path_str in self.state.recent_files:
            path = Path(path_str)
            recents.append({
                "path": str(path),
                "name": path.name,
                "exists": path.exists(),
                "extension": path.suffix if path.exists() and not path.is_dir() else ""
            })
        return recents
    
    def add_bookmark(self, path: Path) -> bool:
        """
        Add path to bookmarks.
        
        Args:
            path: Path to bookmark (file or directory)
            
        Returns:
            True if added, False if already bookmarked
        """
        path_str = str(path)
        
        if path_str in self.state.bookmarks:
            return False
        
        self.state.bookmarks.append(path_str)
        self._save_state()
        return True
    
    def remove_bookmark(self, path: Path) -> bool:
        """
        Remove path from bookmarks.
        
        Args:
            path: Path to remove
            
        Returns:
            True if removed, False if not found
        """
        path_str = str(path)
        
        if path_str in self.state.bookmarks:
            self.state.bookmarks.remove(path_str)
            self._save_state()
            return True
        return False
    
    def get_bookmarks(self) -> List[Dict]:
        """
        Get bookmarks with existence check.
        
        Returns:
            List of dicts with bookmark info
        """
        bookmarks = []
        for path_str in self.state.bookmarks:
            path = Path(path_str)
            bookmarks.append({
                "path": str(path),
                "name": path.name,
                "exists": path.exists(),
                "is_dir": path.is_dir() if path.exists() else None
            })
        return bookmarks
    
    def is_bookmarked(self, path: Path) -> bool:
        """Check if path is bookmarked."""
        return str(path) in self.state.bookmarks
    
    def remember_workspace_path(self) -> None:
        """Remember current path for current workspace."""
        workspace_key = self.state.workspace.value
        self.state.workspace_paths[workspace_key] = str(self.state.current_path)
        self._save_state()
    
    def restore_workspace_path(self, workspace: Workspace) -> Optional[Path]:
        """Restore last path for workspace.
        
        Args:
            workspace: Workspace to restore
            
        Returns:
            Restored path or None if not saved
        """
        workspace_key = workspace.value
        path_str = self.state.workspace_paths.get(workspace_key)
        
        if path_str:
            path = Path(path_str)
            if path.exists():
                return path
        
        return None
    
    def _save_state(self) -> None:
        """Save browser state to disk."""
        try:
            from core.utils.paths import PATHS
            import json
            
            state_dir = PATHS.MEMORY_SYSTEM_USER
            state_dir.mkdir(parents=True, exist_ok=True)
            state_file = state_dir / "browser_state.json"
            
            state_data = {
                "recent_files": self.state.recent_files,
                "bookmarks": self.state.bookmarks,
                "workspace_paths": self.state.workspace_paths,
                "last_workspace": self.state.workspace.value,
                "filter_extensions": self.state.filter_extensions,
                "show_hidden": self.state.show_hidden,
                "column_mode": self.state.column_mode,
                "show_preview": self.state.show_preview
            }
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        
        except Exception as e:
            # Silent fail - don't break browser if save fails
            pass
    
    def _load_state(self) -> None:
        """Load browser state from disk."""
        try:
            from core.utils.paths import PATHS
            import json
            
            state_file = PATHS.MEMORY_SYSTEM_USER / "browser_state.json"
            
            if not state_file.exists():
                return
            
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            # Restore state
            self.state.recent_files = state_data.get("recent_files", [])
            self.state.bookmarks = state_data.get("bookmarks", [])
            self.state.workspace_paths = state_data.get("workspace_paths", {})
            self.state.filter_extensions = state_data.get("filter_extensions", ['.upy', '.md', '.json'])
            self.state.show_hidden = state_data.get("show_hidden", False)
            self.state.column_mode = state_data.get("column_mode", False)
            self.state.show_preview = state_data.get("show_preview", True)
            
            # Optionally restore last workspace
            # last_workspace = state_data.get("last_workspace")
            # if last_workspace:
            #     try:
            #         self.state.workspace = Workspace(last_workspace)
            #     except ValueError:
            #         pass
        
        except Exception as e:
            # Silent fail - use defaults if load fails
            pass

# Syntax fix: balanced quotes
