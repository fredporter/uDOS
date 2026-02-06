"""
Workspace Selector for uDOS TUI

Interactive workspace picker that presents available workspaces before
opening FileBrowser. Uses the same SelectorFramework pattern as FileBrowser
for consistent UX.

Workspaces:
- memory/sandbox (default workspace)
- memory/bank (data storage)
- memory/shared (collaborative space)
- /knowledge (admin only)
- memory/wizard (admin only)
- /dev (admin only)

Part of Phase 2 TUI Enhancement — Workspace selection layer
"""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass

from core.ui.selector_framework import (
    SelectorFramework,
    SelectableItem,
    SelectorConfig,
    SelectionMode,
)
from core.input.keypad_handler import KeypadHandler, KeypadMode
from core.services.spatial_filesystem import UserRole, WorkspaceType


_CONTINUE = object()


@dataclass
class WorkspaceOption:
    """Represents a selectable workspace."""
    id: str
    name: str
    path: Path
    description: str
    icon: str
    admin_only: bool = False
    
    def to_selectable_item(self) -> SelectableItem:
        """Convert to SelectableItem for SelectorFramework."""
        label = f"{self.icon} {self.name}"
        return SelectableItem(
            id=self.id,
            label=label,
            value=self.path,
            icon=self.icon,
            metadata={
                "path": self.path,
                "description": self.description,
                "admin_only": self.admin_only,
            },
        )


class WorkspacePicker:
    """
    Interactive workspace selector using SelectorFramework.
    
    Presents workspace options before opening FileBrowser. Respects
    user role (admin vs normal) to show/hide restricted workspaces.
    
    Usage:
        picker = WorkspacePicker(user_role=UserRole.ADMIN)
        workspace_path = picker.pick()
        if workspace_path:
            browser = FileBrowser(start_dir=str(workspace_path))
            selected_file = browser.pick()
    """
    
    def __init__(
        self,
        user_role: UserRole = UserRole.USER,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize workspace picker.
        
        Args:
            user_role: UserRole.USER or UserRole.ADMIN
            project_root: Root of uDOS project (default: auto-detect)
        """
        self.user_role = user_role
        self.project_root = project_root or self._detect_project_root()
        
        # Create selector and keypad
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,
                show_numbers=True,
            )
        )
        self.keypad = KeypadHandler()
        self.keypad.set_mode(KeypadMode.SELECTION)
        
        # Load workspace options
        self.workspaces = self._build_workspace_list()
        self._populate_selector()
    
    def _detect_project_root(self) -> Path:
        """Auto-detect uDOS project root."""
        # Start from this file's location and walk up
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            if (parent / "memory").is_dir() and (parent / "core").is_dir():
                return parent
        # Fallback: cwd
        return Path.cwd()
    
    def _build_workspace_list(self) -> List[WorkspaceOption]:
        """Build list of available workspaces based on user role."""
        memory_dir = self.project_root / "memory"
        knowledge_dir = self.project_root / "knowledge"
        dev_dir = self.project_root / "dev"
        
        workspaces = [
            WorkspaceOption(
                id="sandbox",
                name="Sandbox",
                path=memory_dir / "sandbox",
                description="Personal workspace for experiments and drafts",
                icon="📦",
                admin_only=False,
            ),
            WorkspaceOption(
                id="bank",
                name="Bank",
                path=memory_dir / "bank",
                description="Data vault for important files and backups",
                icon="🏦",
                admin_only=False,
            ),
            WorkspaceOption(
                id="shared",
                name="Shared",
                path=memory_dir / "shared",
                description="Collaborative workspace for shared content",
                icon="🤝",
                admin_only=False,
            ),
        ]
        
        # Admin-only workspaces
        if self.user_role == UserRole.ADMIN:
            workspaces.extend([
                WorkspaceOption(
                    id="wizard",
                    name="Wizard",
                    path=memory_dir / "wizard",
                    description="Wizard service configuration and logs",
                    icon="🧙",
                    admin_only=True,
                ),
                WorkspaceOption(
                    id="knowledge",
                    name="Knowledge",
                    path=knowledge_dir,
                    description="Knowledge base and reference materials",
                    icon="📖",
                    admin_only=True,
                ),
                WorkspaceOption(
                    id="dev",
                    name="Development",
                    path=dev_dir,
                    description="Development tools and private projects",
                    icon="⚙️",
                    admin_only=True,
                ),
            ])
        
        return workspaces
    
    def _populate_selector(self) -> None:
        """Load workspace items into selector."""
        items = [ws.to_selectable_item() for ws in self.workspaces]
        self.selector.set_items(items)
        self.keypad.set_items([item.label for item in items])
    
    def display(self) -> None:
        """Display workspace picker interface."""
        print("\033[2J\033[H", end="")  # Clear screen
        print("=" * 70)
        print("WORKSPACE SELECTOR")
        print("=" * 70)
        print()
        print("Choose a workspace to browse:")
        print()
        
        # Display items with selector framework
        for line in self.selector.get_display_lines():
            print(line)
        
        # Show description for current item
        current = self.selector.get_current_item()
        if current:
            description = current.metadata.get("description", "")
            print()
            print(f"  → {description}")
        
        print()
        print("-" * 70)
        print("Controls:")
        print("  j/k or 2/8   Move down/up")
        print("  enter/5      Select workspace")
        print("  n/p or 0     Next/prev page")
        print("  h/?          Help")
        print("  q            Cancel")
        print()
    
    def handle_input(self, key: str):
        """Handle user input."""
        if key == "q":
            return None
        
        if key in ("h", "?"):
            self._show_help()
            return _CONTINUE
        
        # Number selection (1-9)
        if key in "123456789":
            result = self.keypad.handle_key(key)
            if result and result != "next_page":
                return self._select_by_label(result)
            if result == "next_page":
                self.selector.next_page()
                self.keypad.set_items([
                    item.label for item in self.selector.get_visible_items()
                ])
            return _CONTINUE
        
        # Pagination
        if key in ("0", "n"):
            self.selector.next_page()
            self.keypad.set_items([
                item.label for item in self.selector.get_visible_items()
            ])
            return _CONTINUE
        
        if key == "p":
            self.selector.prev_page()
            self.keypad.set_items([
                item.label for item in self.selector.get_visible_items()
            ])
            return _CONTINUE
        
        # Navigation
        if key in ("k", "8"):
            self.selector.navigate_up()
            return _CONTINUE
        
        if key in ("j", "2"):
            self.selector.navigate_down()
            return _CONTINUE
        
        # Selection
        if key in ("5", ""):
            return self._select_current()
        
        return _CONTINUE
    
    def _select_by_label(self, label: str):
        """Select workspace by label."""
        for item in self.selector.items:
            if item.label == label:
                return item.value  # Returns Path object
        return _CONTINUE
    
    def _select_current(self):
        """Select currently highlighted workspace."""
        item = self.selector.get_current_item()
        if not item:
            return _CONTINUE
        return item.value  # Returns Path object
    
    def _show_help(self) -> None:
        """Show help overlay."""
        print("\033[2J\033[H", end="")
        print("=" * 70)
        print("WORKSPACE SELECTOR HELP")
        print("=" * 70)
        print()
        print("Available Workspaces:")
        print()
        for ws in self.workspaces:
            admin_badge = " [ADMIN]" if ws.admin_only else ""
            print(f"  {ws.icon} {ws.name}{admin_badge}")
            print(f"     {ws.description}")
            print(f"     Path: {ws.path}")
            print()
        print("-" * 70)
        print()
        print("Navigation:")
        print("  • Use arrow keys (j/k or 2/8) to move up/down")
        print("  • Press number (1-9) for quick selection")
        print("  • Press Enter or 5 to select workspace")
        print("  • Press n/p or 0 for pagination")
        print("  • Press q to cancel")
        print()
        print("Workspace Types:")
        print("  📦 Sandbox — Your personal workspace")
        print("  🏦 Bank — Secure storage for important files")
        print("  🤝 Shared — Collaborative workspace")
        if self.user_role == UserRole.ADMIN:
            print("  🧙 Wizard — Service configuration (admin)")
            print("  📖 Knowledge — Reference library (admin)")
            print("  ⚙️  Development — Dev tools (admin)")
        print()
        input("Press Enter to continue...")
    
    def pick(self) -> Optional[Path]:
        """
        Run picker and return selected workspace path.
        
        Returns:
            Path object if workspace selected, None if cancelled
        """
        while True:
            self.display()
            key = input("Command: ").strip().lower()
            if key == "":
                key = "5"  # Enter = select
            result = self.handle_input(key[0] if key else "")
            if result is None:
                return None
            if isinstance(result, Path):
                return result


# ============================================================================
# Convenience Functions
# ============================================================================

def pick_workspace(
    user_role: UserRole = UserRole.USER,
    project_root: Optional[Path] = None,
) -> Optional[Path]:
    """
    Quick function to pick a workspace.
    
    Usage:
        workspace = pick_workspace(user_role=UserRole.ADMIN)
        if workspace:
            print(f"Selected: {workspace}")
    
    Args:
        user_role: UserRole.USER or UserRole.ADMIN
        project_root: Root of uDOS project (default: auto-detect)
    
    Returns:
        Path object if workspace selected, None if cancelled
    """
    picker = WorkspacePicker(user_role=user_role, project_root=project_root)
    return picker.pick()


def pick_workspace_then_file(
    user_role: UserRole = UserRole.USER,
    project_root: Optional[Path] = None,
    pick_directories: bool = False,
) -> Optional[Path]:
    """
    Two-stage picker: workspace selection then file browser.
    
    Usage:
        file_path = pick_workspace_then_file(user_role=UserRole.ADMIN)
        if file_path:
            print(f"Selected file: {file_path}")
    
    Args:
        user_role: UserRole.USER or UserRole.ADMIN
        project_root: Root of uDOS project (default: auto-detect)
        pick_directories: Allow selecting directories (not just files)
    
    Returns:
        Path object of selected file, None if cancelled
    """
    from core.tui.file_browser import FileBrowser
    
    # Stage 1: Pick workspace
    workspace = pick_workspace(user_role=user_role, project_root=project_root)
    if not workspace:
        return None
    
    # Stage 2: Browse files in workspace
    browser = FileBrowser(
        start_dir=str(workspace),
        pick_directories=pick_directories,
    )
    return browser.pick()
