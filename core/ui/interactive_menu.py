"""
Interactive Menu System for uDOS TUI

Provides:
- Single-select menus with numeric/arrow navigation
- Multi-select menus for bulk operations
- Hierarchical submenus
- Input validation and guided selection
- Terminal-agnostic (fallback to numeric if arrows fail)
"""

import sys
from typing import List, Dict, Optional, Tuple, Callable, Any
from core.utils.tty import interactive_tty_status
from dataclasses import dataclass
from enum import Enum


class MenuStyle(Enum):
    """Menu display styles."""
    NUMBERED = "numbered"  # 1-9 numeric selection
    ARROW = "arrow"        # Arrow keys + Enter
    HYBRID = "hybrid"      # Numeric + Arrow keys


@dataclass
class MenuItem:
    """Single menu item."""
    label: str
    value: Optional[str] = None  # Return value if selected
    help_text: str = ""
    enabled: bool = True
    submenu: Optional['InteractiveMenu'] = None
    action: Optional[Callable] = None  # Direct action on selection


class InteractiveMenu:
    """
    Interactive menu for terminal UIs.
    
    Usage:
        menu = InteractiveMenu("Choose action", items=[
            MenuItem("Start Server", value="start", help_text="Launch the wizard server"),
            MenuItem("Stop Server", value="stop", help_text="Gracefully shutdown"),
            MenuItem("View Logs", value="logs", help_text="Show recent logs"),
        ])
        selected = menu.show()
    """
    
    def __init__(
        self,
        title: str,
        items: List[MenuItem],
        style: MenuStyle = MenuStyle.HYBRID,
        allow_cancel: bool = True,
        show_help: bool = True,
    ):
        """
        Initialize menu.
        
        Args:
            title: Menu header text
            items: List of MenuItem objects
            style: Menu selection style
            allow_cancel: Allow user to cancel selection
            show_help: Show help text for each item
        """
        self.title = title
        self.items = items
        self.style = style
        self.allow_cancel = allow_cancel
        self.show_help = show_help
        self.selected_index = 0
        self.logger = None
        
        try:
            from core.services.logging_service import get_logger
            self.logger = get_logger("interactive-menu")
        except Exception:
            pass

    def show(self) -> Optional[str]:
        """
        Display menu and get user selection.
        
        Returns:
            Selected item's value, or None if cancelled
        """
        while True:
            self._display()
            
            choice = self._get_choice()
            if choice is None:
                return None
            
            if choice < 0 or choice >= len(self.items):
                if choice == -1 and self.allow_cancel:
                    return None
                print("  ❌ Invalid choice")
                continue
            
            item = self.items[choice]
            if not item.enabled:
                print("  ❌ That option is not available")
                continue
            
            # Handle submenus
            if item.submenu:
                result = item.submenu.show()
                if result is not None:
                    return result
                continue
            
            # Handle direct actions
            if item.action:
                try:
                    item.action()
                except Exception as e:
                    print(f"  ❌ Action failed: {e}")
                    if self.logger:
                        self.logger.error(f"Menu action failed: {e}")
                    continue
            
            # Return value
            return item.value or item.label

    def _display(self) -> None:
        """Display menu on screen."""
        print("\n" + "╔" + "═" * (len(self.title) + 2) + "╗")
        print(f"║ {self.title} ║")
        print("╚" + "═" * (len(self.title) + 2) + "╝\n")
        
        # Display items
        for idx, item in enumerate(self.items):
            num = idx + 1
            indicator = "▶ " if idx == self.selected_index else "  "
            status = "✅" if item.enabled else "⊘"
            
            print(f"{indicator}{status} {num}. {item.label}")
            
            if self.show_help and item.help_text:
                print(f"      {item.help_text}")
        
        # Display cancel option
        if self.allow_cancel:
            cancel_idx = len(self.items)
            indicator = "▶ " if cancel_idx == self.selected_index else "  "
            print(f"{indicator}  0. Cancel")
        
        print()
        self._show_instructions()

    def _show_instructions(self) -> None:
        """Show input instructions."""
        if self.style == MenuStyle.NUMBERED:
            print("  Enter number and press Enter (0-9)")
        elif self.style == MenuStyle.ARROW:
            print("  Use ↑↓ arrows, then press Enter")
        else:  # HYBRID
            print("  Use 1-9 or ↑↓ arrows, then press Enter")

    def _get_choice(self) -> Optional[int]:
        """
        Get user choice from input.
        
        Returns:
            Index of selected item, -1 to cancel, or None for error
        """
        try:
            if self.style == MenuStyle.ARROW or self.style == MenuStyle.HYBRID:
                if not self._is_interactive():
                    if self.logger:
                        self.logger.info("[LOCAL] Non-interactive terminal detected, using numeric menu input")
                    return self._get_choice_numeric()
                return self._get_choice_arrow()
            else:
                return self._get_choice_numeric()
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error getting choice: {e}")
            return self._get_choice_numeric()  # Fallback

    def _get_choice_numeric(self) -> Optional[int]:
        """Get numeric input (1-9, 0 for cancel)."""
        try:
            response = input("  Choice: ").strip()
            
            if not response:
                return None
            
            if response.lower() in ('q', 'quit', 'exit', 'cancel', 'x'):
                return -1
            
            try:
                choice = int(response)
                if choice == 0:
                    return -1 if self.allow_cancel else None
                return choice - 1  # Convert to 0-indexed
            except ValueError:
                return None
        except (KeyboardInterrupt, EOFError):
            return -1

    def _get_choice_arrow(self) -> Optional[int]:
        """Get input with arrow key support."""
        if not self._is_interactive():
            return self._get_choice_numeric()
        try:
            # Try to use readline for arrow key support
            import tty
            import termios
            
            original_settings = termios.tcgetattr(sys.stdin)
            
            try:
                tty.setraw(sys.stdin.fileno())
                
                while True:
                    char = sys.stdin.read(1)
                    
                    # Escape sequence detected
                    if char == '\x1b':
                        next_char = sys.stdin.read(1)
                        if next_char == '[':
                            direction = sys.stdin.read(1)
                            if direction == 'A':  # Up arrow
                                self.selected_index = (self.selected_index - 1) % len(self.items)
                                self._display()
                            elif direction == 'B':  # Down arrow
                                self.selected_index = (self.selected_index + 1) % len(self.items)
                                self._display()
                            continue
                    
                    # Enter key
                    elif char == '\r':
                        return self.selected_index
                    
                    # Numeric input (1-9)
                    elif char.isdigit():
                        try:
                            choice = int(char)
                            if choice == 0:
                                return -1 if self.allow_cancel else None
                            return choice - 1
                        except ValueError:
                            continue
                    
                    # Cancel keys
                    elif char in ('q', 'Q', 'x', 'X'):
                        return -1 if self.allow_cancel else None
                    
                    # Ctrl+C
                    elif char == '\x03':
                        return -1
                        
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
                
        except Exception:
            # Fallback to numeric
            return self._get_choice_numeric()

    def _is_interactive(self) -> bool:
        """Check if running in interactive menu mode."""
        interactive, reason = interactive_tty_status()
        if not interactive and reason and self.logger:
            self.logger.debug("[LOCAL] Interactive menu check failed: %s", reason)
        return interactive


class MenuBuilder:
    """Builder pattern for creating menus."""
    
    def __init__(self, title: str):
        self.title = title
        self.items: List[MenuItem] = []
        self.style = MenuStyle.HYBRID
        self.allow_cancel = True
        self.show_help = True
    
    def add_item(
        self,
        label: str,
        value: Optional[str] = None,
        help_text: str = "",
        enabled: bool = True
    ) -> 'MenuBuilder':
        """Add menu item."""
        self.items.append(MenuItem(
            label=label,
            value=value,
            help_text=help_text,
            enabled=enabled
        ))
        return self
    
    def add_action(
        self,
        label: str,
        action: Callable,
        help_text: str = "",
    ) -> 'MenuBuilder':
        """Add item with direct action callback."""
        self.items.append(MenuItem(
            label=label,
            action=action,
            help_text=help_text
        ))
        return self
    
    def add_submenu(
        self,
        label: str,
        submenu: 'InteractiveMenu',
        help_text: str = "",
    ) -> 'MenuBuilder':
        """Add submenu."""
        self.items.append(MenuItem(
            label=label,
            submenu=submenu,
            help_text=help_text
        ))
        return self
    
    def with_style(self, style: MenuStyle) -> 'MenuBuilder':
        """Set menu style."""
        self.style = style
        return self
    
    def with_cancel(self, allow: bool) -> 'MenuBuilder':
        """Allow/disallow cancel."""
        self.allow_cancel = allow
        return self
    
    def with_help(self, show: bool) -> 'MenuBuilder':
        """Show/hide help text."""
        self.show_help = show
        return self
    
    def build(self) -> InteractiveMenu:
        """Build menu."""
        return InteractiveMenu(
            title=self.title,
            items=self.items,
            style=self.style,
            allow_cancel=self.allow_cancel,
            show_help=self.show_help
        )


# Quick helpers

def show_menu(
    title: str,
    options: List[Tuple[str, str, str]],
    allow_cancel: bool = True,
) -> Optional[str]:
    """
    Quick menu display.
    
    Args:
        title: Menu title
        options: List of (label, value, help_text) tuples
        allow_cancel: Allow cancellation
    
    Returns:
        Selected value or None
    
    Example:
        result = show_menu(
            "Choose action",
            [
                ("Start", "start", "Launch the server"),
                ("Stop", "stop", "Shutdown gracefully"),
            ]
        )
    """
    items = [
        MenuItem(label=label, value=value, help_text=help_text)
        for label, value, help_text in options
    ]
    menu = InteractiveMenu(title, items, allow_cancel=allow_cancel)
    return menu.show()


def show_confirm(title: str, help_text: str = "") -> bool:
    """
    Quick confirmation menu.
    
    Args:
        title: Question text
        help_text: Optional help
    
    Returns:
        True if confirmed
    """
    menu = InteractiveMenu(
        title,
        items=[
            MenuItem("Yes", value="yes", help_text=help_text or "Proceed"),
            MenuItem("No", value="no", help_text="Cancel"),
        ],
        allow_cancel=True
    )
    return menu.show() == "yes"
