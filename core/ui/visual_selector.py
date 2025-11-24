"""
uDOS v1.0.31 - Visual Selector & Teletext Graphics
Enhanced ASCII/Unicode visual components for CLI interface

Features:
- Teletext-style block character graphics
- Selection menus with visual indicators
- Progress bars and status indicators
- File tree visualization
- Checkbox and radio button menus
- Consistent styling across all components

Author: uDOS Development Team
Version: 1.0.31
Date: November 22, 2025
"""

from typing import List, Optional, Dict, Any
from enum import Enum


class TeletextChars:
    """Extended teletext block characters for enhanced visuals."""

    # Core blocks
    FULL = '█'
    DARK = '▓'
    MEDIUM = '▒'
    LIGHT = '░'
    EMPTY = ' '

    # Box drawing - single line
    H_LINE = '─'
    V_LINE = '│'
    TOP_LEFT = '┌'
    TOP_RIGHT = '┐'
    BOTTOM_LEFT = '└'
    BOTTOM_RIGHT = '┘'
    CROSS = '┼'
    T_RIGHT = '├'
    T_LEFT = '┤'
    T_DOWN = '┬'
    T_UP = '┴'

    # Box drawing - double line
    H_DBL = '═'
    V_DBL = '║'
    TOP_LEFT_DBL = '╔'
    TOP_RIGHT_DBL = '╗'
    BOTTOM_LEFT_DBL = '╚'
    BOTTOM_RIGHT_DBL = '╝'
    T_RIGHT_DBL = '╠'
    T_LEFT_DBL = '╣'
    T_DOWN_DBL = '╦'
    T_UP_DBL = '╩'
    CROSS_DBL = '╬'

    # Arrows and pointers
    ARROW_RIGHT = '→'
    ARROW_LEFT = '←'
    ARROW_UP = '↑'
    ARROW_DOWN = '↓'
    POINTER = '►'
    BULLET = '•'

    # Selection indicators
    SELECTED = '◉'
    UNSELECTED = '○'
    CHECKBOX_ON = '☑'
    CHECKBOX_OFF = '☐'
    RADIO_ON = '◉'
    RADIO_OFF = '◯'

    # Status icons
    SUCCESS = '✓'
    ERROR = '✗'
    WARNING = '⚠'
    INFO = 'ℹ'
    PENDING = '⋯'

    # File/folder icons
    FILE = '📄'
    FOLDER = '📁'
    FOLDER_OPEN = '📂'
    CODE = '📝'

    # Progress indicators
    SPINNER = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    PROGRESS_FULL = '█'
    PROGRESS_EMPTY = '░'


class VisualSelector:
    """Renders visual selection interfaces using teletext graphics."""

    def __init__(self, width: int = 60):
        """
        Initialize visual selector.

        Args:
            width: Default width for rendered components
        """
        self.width = width
        self.chars = TeletextChars()

    def render_numbered_menu(
        self,
        title: str,
        items: List[str],
        selected_index: int = 0,
        descriptions: Optional[List[str]] = None,
        icons: Optional[List[str]] = None
    ) -> str:
        """
        Render numbered selection menu.

        Args:
            title: Menu title
            items: List of menu items
            selected_index: Currently selected item (0-based)
            descriptions: Optional descriptions for items
            icons: Optional icons for items

        Returns:
            Formatted menu string
        """
        lines = []

        # Title bar
        lines.append(f"\n{self.chars.TOP_LEFT_DBL}{self.chars.H_DBL * (self.width - 2)}{self.chars.TOP_RIGHT_DBL}")
        title_centered = title.center(self.width - 4)
        lines.append(f"{self.chars.V_DBL} {title_centered} {self.chars.V_DBL}")
        lines.append(f"{self.chars.T_RIGHT_DBL}{self.chars.H_DBL * (self.width - 2)}{self.chars.T_LEFT_DBL}")

        # Menu items
        for i, item in enumerate(items):
            # Selection indicator
            indicator = self.chars.POINTER if i == selected_index else ' '

            # Number
            num = f"{i + 1}."

            # Icon
            icon = icons[i] if icons and i < len(icons) else ''

            # Description
            desc = descriptions[i] if descriptions and i < len(descriptions) else ''

            # Format line
            if desc:
                line_text = f" {num} {indicator} {icon} {item:<20} - {desc}"
            else:
                line_text = f" {num} {indicator} {icon} {item}"

            # Truncate if needed
            if len(line_text) > self.width - 4:
                line_text = line_text[:self.width - 7] + "..."

            lines.append(f"{self.chars.V_DBL}{line_text.ljust(self.width - 2)}{self.chars.V_DBL}")

        # Bottom bar
        lines.append(f"{self.chars.BOTTOM_LEFT_DBL}{self.chars.H_DBL * (self.width - 2)}{self.chars.BOTTOM_RIGHT_DBL}")

        return '\n'.join(lines)

    def render_checkbox_menu(
        self,
        title: str,
        items: List[str],
        selected_indices: List[int],
        descriptions: Optional[List[str]] = None
    ) -> str:
        """
        Render checkbox-style multi-select menu.

        Args:
            title: Menu title
            items: List of menu items
            selected_indices: List of selected item indices
            descriptions: Optional descriptions

        Returns:
            Formatted menu string
        """
        lines = []
        selected_set = set(selected_indices)

        # Title
        lines.append(f"\n{self.chars.TOP_LEFT_DBL}{self.chars.H_DBL * (self.width - 2)}{self.chars.TOP_RIGHT_DBL}")
        lines.append(f"{self.chars.V_DBL} {title.center(self.width - 4)} {self.chars.V_DBL}")
        lines.append(f"{self.chars.T_RIGHT_DBL}{self.chars.H_DBL * (self.width - 2)}{self.chars.T_LEFT_DBL}")

        # Items
        for i, item in enumerate(items):
            checkbox = self.chars.CHECKBOX_ON if i in selected_set else self.chars.CHECKBOX_OFF
            num = f"{i + 1}."

            desc = descriptions[i] if descriptions and i < len(descriptions) else ''

            if desc:
                line_text = f" {num} {checkbox} {item:<20} - {desc}"
            else:
                line_text = f" {num} {checkbox} {item}"

            if len(line_text) > self.width - 4:
                line_text = line_text[:self.width - 7] + "..."

            lines.append(f"{self.chars.V_DBL}{line_text.ljust(self.width - 2)}{self.chars.V_DBL}")

        # Footer
        lines.append(f"{self.chars.BOTTOM_LEFT_DBL}{self.chars.H_DBL * (self.width - 2)}{self.chars.BOTTOM_RIGHT_DBL}")
        lines.append(f"  {self.chars.INFO} Selected: {len(selected_indices)}/{len(items)}")

        return '\n'.join(lines)

    def render_file_tree(
        self,
        path: str,
        items: List[Dict[str, Any]],
        selected_path: str = "",
        max_depth: int = 3
    ) -> str:
        """
        Render file/directory tree visualization.

        Args:
            path: Root path
            items: List of file/directory items with 'name', 'type', 'path'
            selected_path: Currently selected item path
            max_depth: Maximum tree depth to display

        Returns:
            Formatted tree string
        """
        lines = []

        # Title
        lines.append(f"\n{self.chars.TOP_LEFT}{self.chars.H_LINE * (self.width - 2)}{self.chars.TOP_RIGHT}")
        lines.append(f"{self.chars.V_LINE} {path.ljust(self.width - 4)} {self.chars.V_LINE}")
        lines.append(f"{self.chars.T_RIGHT}{self.chars.H_LINE * (self.width - 2)}{self.chars.T_LEFT}")

        # Tree items
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            is_selected = item.get('path') == selected_path

            # Tree structure characters
            prefix = self.chars.BOTTOM_LEFT if is_last else self.chars.T_RIGHT
            connector = self.chars.H_LINE * 2

            # Icon
            if item.get('type') == 'dir':
                icon = self.chars.FOLDER
            else:
                icon = self.chars.FILE

            # Selection indicator
            indicator = self.chars.POINTER if is_selected else ' '

            # Item line
            name = item.get('name', '')
            line_text = f" {prefix}{connector} {indicator} {icon} {name}"

            if len(line_text) > self.width - 4:
                line_text = line_text[:self.width - 7] + "..."

            lines.append(f"{self.chars.V_LINE}{line_text.ljust(self.width - 2)}{self.chars.V_LINE}")

        # Bottom
        lines.append(f"{self.chars.BOTTOM_LEFT}{self.chars.H_LINE * (self.width - 2)}{self.chars.BOTTOM_RIGHT}")

        return '\n'.join(lines)

    def render_progress(
        self,
        current: int,
        total: int,
        label: str = "",
        width: int = 40
    ) -> str:
        """
        Render progress bar.

        Args:
            current: Current progress value
            total: Total value
            label: Optional label
            width: Width of progress bar

        Returns:
            Formatted progress bar
        """
        if total == 0:
            percentage = 0
        else:
            percentage = (current / total) * 100

        filled = int((current / total) * width) if total > 0 else 0
        empty = width - filled

        bar = self.chars.PROGRESS_FULL * filled + self.chars.PROGRESS_EMPTY * empty

        if label:
            return f"{label}: [{bar}] {percentage:.0f}% ({current}/{total})"
        else:
            return f"[{bar}] {percentage:.0f}% ({current}/{total})"

    def render_status(
        self,
        message: str,
        status: str = "info",
        details: Optional[str] = None
    ) -> str:
        """
        Render status message with icon.

        Args:
            message: Status message
            status: Status type (info, success, warning, error, pending)
            details: Optional details text

        Returns:
            Formatted status message
        """
        icons = {
            'info': self.chars.INFO,
            'success': self.chars.SUCCESS,
            'warning': self.chars.WARNING,
            'error': self.chars.ERROR,
            'pending': self.chars.PENDING
        }

        icon = icons.get(status, self.chars.INFO)

        result = f"{icon} {message}"

        if details:
            result += f"\n  {self.chars.BULLET} {details}"

        return result

    def render_separator(self, style: str = "single") -> str:
        """
        Render separator line.

        Args:
            style: Line style (single, double, heavy)

        Returns:
            Separator string
        """
        if style == "double":
            return self.chars.H_DBL * self.width
        elif style == "heavy":
            return self.chars.FULL * self.width
        else:
            return self.chars.H_LINE * self.width

    def render_banner(
        self,
        text: str,
        style: str = "double"
    ) -> str:
        """
        Render banner/header.

        Args:
            text: Banner text
            style: Border style (single, double)

        Returns:
            Formatted banner
        """
        if style == "double":
            top_left = self.chars.TOP_LEFT_DBL
            top_right = self.chars.TOP_RIGHT_DBL
            bottom_left = self.chars.BOTTOM_LEFT_DBL
            bottom_right = self.chars.BOTTOM_RIGHT_DBL
            h_line = self.chars.H_DBL
            v_line = self.chars.V_DBL
        else:
            top_left = self.chars.TOP_LEFT
            top_right = self.chars.TOP_RIGHT
            bottom_left = self.chars.BOTTOM_LEFT
            bottom_right = self.chars.BOTTOM_RIGHT
            h_line = self.chars.H_LINE
            v_line = self.chars.V_LINE

        lines = []
        lines.append(f"{top_left}{h_line * (self.width - 2)}{top_right}")
        lines.append(f"{v_line} {text.center(self.width - 4)} {v_line}")
        lines.append(f"{bottom_left}{h_line * (self.width - 2)}{bottom_right}")

        return '\n'.join(lines)

    def render_info_box(
        self,
        title: str,
        items: Dict[str, str]
    ) -> str:
        """
        Render information box with key-value pairs.

        Args:
            title: Box title
            items: Dictionary of key-value pairs

        Returns:
            Formatted info box
        """
        lines = []

        # Title
        lines.append(f"\n{self.chars.TOP_LEFT}{self.chars.H_LINE * (self.width - 2)}{self.chars.TOP_RIGHT}")
        lines.append(f"{self.chars.V_LINE} {title.ljust(self.width - 4)} {self.chars.V_LINE}")
        lines.append(f"{self.chars.T_RIGHT}{self.chars.H_LINE * (self.width - 2)}{self.chars.T_LEFT}")

        # Items
        for key, value in items.items():
            line_text = f" {key}: {value}"
            if len(line_text) > self.width - 4:
                line_text = line_text[:self.width - 7] + "..."
            lines.append(f"{self.chars.V_LINE}{line_text.ljust(self.width - 2)}{self.chars.V_LINE}")

        # Bottom
        lines.append(f"{self.chars.BOTTOM_LEFT}{self.chars.H_LINE * (self.width - 2)}{self.chars.BOTTOM_RIGHT}")

        return '\n'.join(lines)
