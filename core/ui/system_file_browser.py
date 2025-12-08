"""
System File Browser (v1.2.19)

Browse and edit system files (core/, extensions/, wiki/) with warnings.
D-key access for developers.
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import subprocess


class SystemFileBrowser:
    """
    TUI browser for system files.
    
    Features:
    - Navigate core/, extensions/, wiki/
    - Edit system files with warnings
    - Syntax highlighting preview
    - Git status indicators
    - Safety confirmations
    """
    
    # System workspaces
    WORKSPACES = {
        'core': 'core/',
        'extensions': 'extensions/',
        'wiki': 'wiki/',
        'dev': 'dev/',
        'tests': 'memory/ucode/tests/'
    }
    
    def __init__(self):
        """Initialize system file browser"""
        from core.utils.paths import PATHS
        self.project_root = PATHS.PROJECT_ROOT
        
        # Current state
        self.current_workspace = 'core'
        self.current_path = self.project_root / self.WORKSPACES['core']
        self.files: List[Path] = []
        self.selected_index = 0
        self.git_status = {}
        
        # Load initial workspace
        self._load_workspace()
        self._load_git_status()
        
    def _load_workspace(self):
        """Load files from current workspace"""
        self.files = []
        
        if not self.current_path.exists():
            return
        
        # Add parent directory entry if not at workspace root
        workspace_root = self.project_root / self.WORKSPACES[self.current_workspace]
        if self.current_path != workspace_root:
            self.files.append(self.current_path.parent)
        
        # Add directories first
        try:
            for item in sorted(self.current_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    self.files.append(item)
        except PermissionError:
            pass
        
        # Add files (Python, Markdown, JSON, config)
        try:
            for item in sorted(self.current_path.iterdir()):
                if item.is_file():
                    # Filter to relevant file types
                    if item.suffix in ['.py', '.md', '.json', '.yaml', '.yml', '.txt', '.sh']:
                        self.files.append(item)
        except PermissionError:
            pass
        
        # Reset selection
        self.selected_index = 0
    
    def _load_git_status(self):
        """Load git status for current files"""
        self.git_status = {}
        
        try:
            # Run git status --short
            result = subprocess.run(
                ['git', 'status', '--short'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if len(line) < 4:
                        continue
                    
                    status = line[:2]
                    filepath = line[3:]
                    
                    # Map status codes
                    if status[0] == 'M' or status[1] == 'M':
                        self.git_status[filepath] = 'modified'
                    elif status[0] == 'A':
                        self.git_status[filepath] = 'added'
                    elif status == '??':
                        self.git_status[filepath] = 'untracked'
                    elif status[0] == 'D':
                        self.git_status[filepath] = 'deleted'
        except Exception:
            pass
    
    def render(self) -> str:
        """Render system file browser"""
        output = []
        
        # Header
        output.append("╔══ SYSTEM FILE BROWSER ══╗")
        output.append("")
        
        # Workspace tabs
        output.append(self._render_workspace_tabs())
        output.append("=" * 70)
        output.append("")
        
        # Current path
        relative_path = self.current_path.relative_to(self.project_root)
        output.append(f"📂 {relative_path}")
        output.append("")
        
        # Files list
        output.extend(self._render_files())
        
        # Footer
        output.append("")
        output.append(self._render_footer())
        
        return "\n".join(output)
    
    def _render_workspace_tabs(self) -> str:
        """Render workspace tabs"""
        tabs = []
        for workspace in self.WORKSPACES.keys():
            if workspace == self.current_workspace:
                tabs.append(f"[{workspace.upper()}]")
            else:
                tabs.append(f" {workspace} ")
        
        return "  |  ".join(tabs)
    
    def _render_files(self) -> List[str]:
        """Render files list"""
        output = []
        
        if not self.files:
            output.append("  (empty directory)")
            return output
        
        # Render each file
        for i, file_path in enumerate(self.files):
            # Highlight selected
            prefix = "→ " if i == self.selected_index else "  "
            
            # Icon
            if file_path.is_dir():
                icon = "📁"
            elif file_path.suffix == '.py':
                icon = "🐍"
            elif file_path.suffix == '.md':
                icon = "📝"
            elif file_path.suffix == '.json':
                icon = "📋"
            else:
                icon = "📄"
            
            # Git status indicator
            relative = str(file_path.relative_to(self.project_root))
            git_indicator = self._get_git_indicator(relative)
            
            # File name
            if file_path == self.current_path.parent:
                name = ".."
            else:
                name = file_path.name
            
            # File size (if file)
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    size_str = self._format_size(size)
                    output.append(f"{prefix}{git_indicator}{icon} {name} ({size_str})")
                except:
                    output.append(f"{prefix}{git_indicator}{icon} {name}")
            else:
                output.append(f"{prefix}{git_indicator}{icon} {name}/")
        
        return output
    
    def _get_git_indicator(self, relative_path: str) -> str:
        """Get git status indicator for file"""
        status = self.git_status.get(relative_path, '')
        
        if status == 'modified':
            return "M "
        elif status == 'added':
            return "A "
        elif status == 'untracked':
            return "? "
        elif status == 'deleted':
            return "D "
        else:
            return "  "
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        else:
            return f"{size / (1024 * 1024):.1f}MB"
    
    def _render_footer(self) -> str:
        """Render footer with controls"""
        controls = [
            "↑↓ Navigate",
            "[ENTER] Open",
            "[E]dit",
            "[V]iew",
            "[G]it Status",
            "[ESC] Close"
        ]
        return "  ".join(controls)
    
    def switch_workspace(self, workspace: str):
        """Switch to a different workspace"""
        if workspace in self.WORKSPACES:
            self.current_workspace = workspace
            self.current_path = self.project_root / self.WORKSPACES[workspace]
            self._load_workspace()
            self._load_git_status()
    
    def move_selection(self, delta: int):
        """Move selection up/down"""
        if not self.files:
            return
        
        self.selected_index = (self.selected_index + delta) % len(self.files)
    
    def enter_selected(self) -> Dict[str, Any]:
        """Enter selected directory or open file"""
        if not self.files or self.selected_index >= len(self.files):
            return {'success': False, 'error': 'No file selected'}
        
        selected = self.files[self.selected_index]
        
        if selected.is_dir():
            # Navigate into directory
            self.current_path = selected
            self._load_workspace()
            self._load_git_status()
            return {'success': True, 'action': 'navigate', 'path': str(selected)}
        else:
            # File selected - return for external handling
            return {
                'success': True,
                'action': 'file_selected',
                'path': str(selected),
                'type': selected.suffix
            }
    
    def get_selected_file(self) -> Optional[Path]:
        """Get currently selected file"""
        if not self.files or self.selected_index >= len(self.files):
            return None
        
        selected = self.files[self.selected_index]
        return selected if selected.is_file() else None
    
    def view_file(self) -> Dict[str, Any]:
        """View selected file content"""
        file_path = self.get_selected_file()
        if not file_path:
            return {'success': False, 'error': 'No file selected'}
        
        try:
            content = file_path.read_text()
            return {
                'success': True,
                'path': str(file_path),
                'content': content,
                'lines': len(content.splitlines())
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def edit_file(self) -> Dict[str, Any]:
        """
        Edit selected file.
        Returns path and warning if system file.
        """
        file_path = self.get_selected_file()
        if not file_path:
            return {'success': False, 'error': 'No file selected'}
        
        # Check if it's a critical system file
        critical_files = [
            'core/config.py',
            'core/uDOS_main.py',
            'core/uDOS_commands.py'
        ]
        
        relative = str(file_path.relative_to(self.project_root))
        is_critical = any(relative.startswith(cf) for cf in critical_files)
        
        return {
            'success': True,
            'path': str(file_path),
            'relative': relative,
            'is_critical': is_critical,
            'warning': 'This is a critical system file. Edit with caution!' if is_critical else None
        }
    
    def get_git_diff(self, file_path: Optional[Path] = None) -> Dict[str, Any]:
        """Get git diff for file"""
        if file_path is None:
            file_path = self.get_selected_file()
        
        if not file_path:
            return {'success': False, 'error': 'No file selected'}
        
        try:
            result = subprocess.run(
                ['git', 'diff', str(file_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'success': True,
                'path': str(file_path),
                'diff': result.stdout,
                'has_changes': bool(result.stdout.strip())
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get browser summary"""
        return {
            'workspace': self.current_workspace,
            'path': str(self.current_path),
            'files_count': len([f for f in self.files if f.is_file()]),
            'dirs_count': len([f for f in self.files if f.is_dir()]),
            'git_modified': len([f for f, s in self.git_status.items() if s == 'modified'])
        }


# Global instance
_system_file_browser: Optional[SystemFileBrowser] = None


def get_system_file_browser() -> SystemFileBrowser:
    """Get global SystemFileBrowser instance"""
    global _system_file_browser
    if _system_file_browser is None:
        _system_file_browser = SystemFileBrowser()
    return _system_file_browser
