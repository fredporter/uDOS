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
import os
from typing import List, Dict, Optional, Tuple, Callable, Any
from core.input.keymap import decode_key_input
from core.utils.tty import interactive_tty_status
from core.services.viewport_service import ViewportService
from core.utils.text_width import pad_to_width, truncate_to_width
from core.tui.stdout_guard import atomic_print, atomic_stdout_write
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
        style: MenuStyle = MenuStyle.NUMBERED,
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
        self.style = self._resolve_style(style)
        self.allow_cancel = allow_cancel
        self.show_help = show_help
        self.selected_index = 0
        self.logger = None
        self._raw_mode = False
        self._alt_screen = False
        self._use_alt_screen = os.getenv("UDOS_MENU_ALT_SCREEN", "0").lower() in ("1", "true", "yes", "on")
        self._raw_nav_enabled = os.getenv("UDOS_MENU_ENABLE_RAW_NAV", "0").lower() in ("1", "true", "yes", "on")
        self._ascii_only = self._should_use_ascii()
        
        try:
            from core.services.logging_api import get_logger
            self.logger = get_logger("interactive-menu")
        except Exception:
            pass

    def _resolve_style(self, style: MenuStyle) -> MenuStyle:
        """Apply env overrides for menu style."""
        env_style = os.getenv("UDOS_MENU_STYLE", "").strip().lower()
        if env_style in ("numbered", "numeric"):
            return MenuStyle.NUMBERED
        if env_style == "arrow":
            return MenuStyle.ARROW
        if env_style == "hybrid":
            return MenuStyle.HYBRID
        if os.getenv("UDOS_MENU_NO_ARROWS", "").strip().lower() in ("1", "true", "yes"):
            return MenuStyle.NUMBERED
        return style

    def _should_use_ascii(self) -> bool:
        """Return True if we should avoid emoji/box-drawing glyphs."""
        ascii_only = os.getenv("UDOS_ASCII_ONLY", "").strip().lower() in ("1", "true", "yes")
        encoding = (getattr(sys.stdout, "encoding", "") or "").lower()
        return ascii_only or not encoding.startswith("utf")

    def _enter_alt_screen(self) -> None:
        """Switch to alternate screen buffer for stable redraws."""
        if self._alt_screen or not self._use_alt_screen:
            return
        atomic_stdout_write("\033[?1049h\033[H")
        self._alt_screen = True

    def _exit_alt_screen(self) -> None:
        """Return from alternate screen buffer."""
        if not self._alt_screen:
            return
        # Do not force cursor-home on exit; restoring alt-screen already
        # restores cursor/screen state and forcing \033[H can overwrite
        # prior content in the primary buffer.
        atomic_stdout_write("\033[?1049l")
        self._alt_screen = False

    def _clear_screen(self) -> None:
        """Clear visible screen area."""
        atomic_stdout_write("\033[2J\033[H")

    def show(self) -> Optional[str]:
        """
        Display menu and get user selection.
        
        Returns:
            Selected item's value, or None if cancelled
        """
        try:
            interactive, reason = interactive_tty_status()
            if not interactive:
                if self.logger:
                    self.logger.info(
                        "[LOCAL] Non-interactive terminal detected, skipping menu (%s)",
                        reason,
                    )
                return None
        except Exception:
            # If detection fails, proceed with default behavior
            pass

        if self.style in (MenuStyle.ARROW, MenuStyle.HYBRID):
            self._enter_alt_screen()

        try:
            while True:
                self._display()

                choice = self._get_choice()
                if choice is None:
                    return None

                if choice < 0 or choice >= len(self.items):
                    if choice == -1 and self.allow_cancel:
                        return None
                    atomic_print("  ❌ Invalid choice")
                    continue

                item = self.items[choice]
                if not item.enabled:
                    atomic_print("  ❌ That option is not available")
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
                        atomic_print(f"  ❌ Action failed: {e}")
                        if self.logger:
                            self.logger.error(f"Menu action failed: {e}")
                        continue

                # Return value
                return item.value or item.label
        finally:
            self._exit_alt_screen()

    def _display(self) -> None:
        """Display menu on screen."""
        # For arrow/hybrid menus we re-render on navigation; clear the screen
        # to avoid stacked/garbled layouts when handling arrow keys.
        if self.style in (MenuStyle.ARROW, MenuStyle.HYBRID):
            self._clear_screen()
        lines: List[str] = []
        width = ViewportService().get_cols()
        inner_width = max(10, width - 2)
        if self._ascii_only:
            tl, tr, bl, br = "+", "+", "+", "+"
            hline, vline = "-", "|"
        else:
            tl, tr, bl, br = "╔", "╗", "╚", "╝"
            hline, vline = "═", "║"
        lines.append(tl + hline * (len(self.title) + 2) + tr)
        lines.append(f"{vline} {self.title} {vline}")
        lines.append(bl + hline * (len(self.title) + 2) + br)

        # Options box
        opt_top = tl + hline * inner_width + tr
        opt_bottom = bl + hline * inner_width + br
        lines.append(opt_top)

        # Display items
        for idx, item in enumerate(self.items):
            num = idx + 1
            if self._ascii_only:
                indicator = "> " if idx == self.selected_index else "  "
                status = "[x]" if item.enabled else "[ ]"
            else:
                indicator = "▶ " if idx == self.selected_index else "  "
                status = "✅" if item.enabled else "⊘"
            label = f"{indicator}{status} {num}. {item.label}"
            if self.show_help and item.help_text:
                label = f"{label} — {item.help_text}"
            label = truncate_to_width(label, inner_width)
            lines.append(f"{vline}{pad_to_width(label, inner_width)}{vline}")

        # Display cancel option
        if self.allow_cancel:
            cancel_idx = len(self.items)
            indicator = "> " if (self._ascii_only and cancel_idx == self.selected_index) else (
                "▶ " if cancel_idx == self.selected_index else "  "
            )
            cancel_line = f"{indicator}  0. Cancel"
            cancel_line = truncate_to_width(cancel_line, inner_width)
            lines.append(f"{vline}{pad_to_width(cancel_line, inner_width)}{vline}")

        lines.append(opt_bottom)
        lines.extend(self._get_instructions_lines())
        self._emit_lines(lines)

    def _get_instructions_lines(self) -> List[str]:
        """Get input instructions."""
        if self.style == MenuStyle.NUMBERED:
            return ["  Enter number and press Enter (0-9)"]
        elif self.style == MenuStyle.ARROW:
            return ["  Use up/down arrows, then press Enter" if self._ascii_only else "  Use ↑↓ arrows, then press Enter"]
        # HYBRID
        return ["  Use 1-9 or up/down arrows, then press Enter" if self._ascii_only else "  Use 1-9 or ↑↓ arrows, then press Enter"]

    def _emit_lines(self, lines: List[str]) -> None:
        """Write menu output with correct newlines for raw mode."""
        newline = "\r\n" if self._raw_mode else "\n"
        width = ViewportService().get_cols()
        padded = [pad_to_width(line, width) for line in lines]
        atomic_stdout_write(newline.join(padded) + newline)

    def _get_choice(self) -> Optional[int]:
        """
        Get user choice from input.
        
        Returns:
            Index of selected item, -1 to cancel, or None for error
        """
        try:
            if (self.style == MenuStyle.ARROW or self.style == MenuStyle.HYBRID) and not self._raw_nav_enabled:
                if self.logger:
                    self.logger.info("[LOCAL] Raw arrow menu input disabled; using numeric input")
                return self._get_choice_numeric()
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
                self._raw_mode = True
                
                while True:
                    char = sys.stdin.read(1)
                    
                    # Escape sequence detected
                    if char == '\x1b':
                        next_char = sys.stdin.read(1)
                        if next_char in ('[', 'O'):
                            seq = ""
                            while True:
                                part = sys.stdin.read(1)
                                if not part:
                                    break
                                seq += part
                                if part.isalpha() or part == '~':
                                    break
                            decoded = decode_key_input("\x1b" + next_char + seq, env=os.environ)
                            if decoded.action == "NAV_UP":
                                self.selected_index = (self.selected_index - 1) % len(self.items)
                                self._display()
                            elif decoded.action == "NAV_DOWN":
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
                self._raw_mode = False
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
    try:
        from core.input.confirmation_utils import format_prompt, parse_confirmation
        prompt = format_prompt(title, "yes", "ok")
        if help_text:
            atomic_print(f"  {help_text}")
        response = input(prompt)
        choice = parse_confirmation(response, "yes", "ok")
        return choice in {"yes", "ok"}
    except Exception:
        # Fallback to simple yes/no input
        response = input(f"{title}? [Yes|No|OK] ").strip().lower()
        return response in {"", "1", "y", "yes", "ok"}
