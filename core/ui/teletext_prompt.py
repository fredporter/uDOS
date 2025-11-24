"""
uDOS v1.0.30 - Enhanced Teletext Prompt & Picker System

Improvements:
- Teletext block character selectors for visual navigation
- Enhanced autocomplete with visual cues
- Improved file picker with directory tree visualization
- Option picker with teletext-style selection boxes
- Better keyboard navigation with 1-9 shortcuts
- Visual feedback using mosaic characters

Version: 1.0.30
Date: 22 November 2025
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import sys


class TeletextBlocks:
    """Teletext mosaic block characters for UI elements."""

    # Block characters (standard Unicode)
    FULL = '█'
    LIGHT = '░'
    MEDIUM = '▒'
    DARK = '▓'

    # Box drawing
    TOP_LEFT = '┌'
    TOP_RIGHT = '┐'
    BOTTOM_LEFT = '└'
    BOTTOM_RIGHT = '┘'
    HORIZONTAL = '─'
    VERTICAL = '│'
    VERTICAL_RIGHT = '├'
    VERTICAL_LEFT = '┤'
    HORIZONTAL_DOWN = '┬'
    HORIZONTAL_UP = '┴'
    CROSS = '┼'

    # Double lines
    DOUBLE_H = '═'
    DOUBLE_V = '║'
    DOUBLE_TL = '╔'
    DOUBLE_TR = '╗'
    DOUBLE_BL = '╚'
    DOUBLE_BR = '╝'
    DOUBLE_VR = '╠'
    DOUBLE_VL = '╣'
    DOUBLE_HD = '╦'
    DOUBLE_HU = '╩'

    # Selector blocks
    SELECTED = '◉'
    UNSELECTED = '○'
    CHECKBOX_ON = '☑'
    CHECKBOX_OFF = '☐'
    RADIO_ON = '◉'
    RADIO_OFF = '◯'

    # Arrows and indicators
    ARROW_RIGHT = '→'
    ARROW_LEFT = '←'
    ARROW_UP = '↑'
    ARROW_DOWN = '↓'
    TRIANGLE_RIGHT = '▶'
    TRIANGLE_LEFT = '◀'
    POINTER = '►'

    # Status indicators
    SUCCESS = '✓'
    ERROR = '✗'
    WARNING = '⚠'
    INFO = 'ℹ'

    # File type icons
    FILE = '📄'
    FOLDER = '📁'
    FOLDER_OPEN = '📂'
    CODE = '📝'
    IMAGE = '🖼'
    DATA = '📊'

    # UI elements
    MENU_SEPARATOR = '─' * 60
    DOUBLE_SEPARATOR = '═' * 60


class TeletextPromptStyle:
    """Visual styles for teletext-based prompts."""

    @staticmethod
    def create_selection_box(
        title: str,
        items: List[str],
        selected_index: int = 0,
        show_numbers: bool = True,
        width: int = 60
    ) -> str:
        """
        Create a teletext-style selection box.

        Args:
            title: Box title
            items: List of items to display
            selected_index: Currently selected item index
            show_numbers: Show 1-9 number shortcuts
            width: Box width

        Returns:
            Formatted selection box string
        """
        lines = []

        # Top border
        lines.append(f"{TeletextBlocks.DOUBLE_TL}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_TR}")

        # Title
        title_padded = f" {title} ".center(width - 2, TeletextBlocks.DOUBLE_H)
        lines.append(f"{TeletextBlocks.DOUBLE_V}{title_padded}{TeletextBlocks.DOUBLE_V}")

        # Separator
        lines.append(f"{TeletextBlocks.DOUBLE_VR}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_VL}")

        # Items
        for i, item in enumerate(items):
            if i >= 9 and show_numbers:
                break  # Limit to 9 items for keyboard shortcuts

            # Selection indicator
            if i == selected_index:
                indicator = f"{TeletextBlocks.POINTER} "
                checkbox = TeletextBlocks.SELECTED
            else:
                indicator = "  "
                checkbox = TeletextBlocks.UNSELECTED

            # Number shortcut
            number = f"{i + 1}." if show_numbers else ""

            # Format line
            item_text = f"{indicator}{number:3} {checkbox} {item}"
            padded = item_text.ljust(width - 2)[:width - 2]
            lines.append(f"{TeletextBlocks.DOUBLE_V}{padded}{TeletextBlocks.DOUBLE_V}")

        # More items indicator
        if len(items) > 9 and show_numbers:
            more_text = f"  ... and {len(items) - 9} more items"
            lines.append(f"{TeletextBlocks.DOUBLE_V}{more_text.ljust(width - 2)}{TeletextBlocks.DOUBLE_V}")

        # Bottom border
        lines.append(f"{TeletextBlocks.DOUBLE_BL}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_BR}")

        return "\n".join(lines)

    @staticmethod
    def create_file_tree(
        path: str,
        files: List[Dict[str, Any]],
        selected_index: int = 0,
        max_depth: int = 3,
        width: int = 60
    ) -> str:
        """
        Create a teletext-style file tree visualization.

        Args:
            path: Current directory path
            files: List of file/directory dictionaries
            selected_index: Currently selected item index
            max_depth: Maximum tree depth to display
            width: Display width

        Returns:
            Formatted file tree string
        """
        lines = []

        # Header
        lines.append(f"{TeletextBlocks.DOUBLE_TL}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_TR}")
        header = f" 📁 {path} "
        lines.append(f"{TeletextBlocks.DOUBLE_V}{header.ljust(width - 2)}{TeletextBlocks.DOUBLE_V}")
        lines.append(f"{TeletextBlocks.DOUBLE_VR}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_VL}")

        # Files/directories
        for i, item in enumerate(files[:9]):  # Limit to 9 for shortcuts
            is_dir = item.get('is_dir', False)
            name = item.get('name', '')
            size = item.get('size', 0)

            # Selection indicator
            indicator = TeletextBlocks.POINTER if i == selected_index else " "

            # File type icon
            if is_dir:
                icon = TeletextBlocks.FOLDER
            else:
                # Determine icon by extension
                ext = name.split('.')[-1].lower() if '.' in name else ''
                if ext in ['py', 'js', 'ts', 'cpp', 'h']:
                    icon = TeletextBlocks.CODE
                elif ext in ['png', 'jpg', 'gif', 'svg']:
                    icon = TeletextBlocks.IMAGE
                elif ext in ['json', 'csv', 'xml']:
                    icon = TeletextBlocks.DATA
                else:
                    icon = TeletextBlocks.FILE

            # Format size
            size_str = f"{size:>6}B" if size < 1024 else f"{size//1024:>5}KB"

            # Build line
            line = f"{indicator} {i+1}. {icon} {name}"
            if not is_dir:
                line += f" {TeletextBlocks.LIGHT * (width - len(line) - len(size_str) - 4)} {size_str}"

            padded = line.ljust(width - 2)[:width - 2]
            lines.append(f"{TeletextBlocks.DOUBLE_V}{padded}{TeletextBlocks.DOUBLE_V}")

        # More items indicator
        if len(files) > 9:
            more = f"  ... {len(files) - 9} more items (use arrows to scroll)"
            lines.append(f"{TeletextBlocks.DOUBLE_V}{more.ljust(width - 2)}{TeletextBlocks.DOUBLE_V}")

        # Footer
        lines.append(f"{TeletextBlocks.DOUBLE_BL}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_BR}")

        return "\n".join(lines)

    @staticmethod
    def create_autocomplete_panel(
        current_input: str,
        suggestions: List[Dict[str, Any]],
        selected_index: int = 0,
        width: int = 70
    ) -> str:
        """
        Create autocomplete suggestion panel with teletext styling.

        Args:
            current_input: Current user input
            suggestions: List of suggestion dictionaries
            selected_index: Currently selected suggestion
            width: Panel width

        Returns:
            Formatted autocomplete panel
        """
        if not suggestions:
            return ""

        lines = []

        # Header
        lines.append(f"{TeletextBlocks.TOP_LEFT}{TeletextBlocks.HORIZONTAL * (width - 2)}{TeletextBlocks.TOP_RIGHT}")
        header = f" Suggestions for: {current_input} "
        lines.append(f"{TeletextBlocks.VERTICAL}{header.ljust(width - 2)}{TeletextBlocks.VERTICAL}")
        lines.append(f"{TeletextBlocks.VERTICAL_RIGHT}{TeletextBlocks.HORIZONTAL * (width - 2)}{TeletextBlocks.VERTICAL_LEFT}")

        # Suggestions (max 5)
        for i, sug in enumerate(suggestions[:5]):
            command = sug.get('command', sug.get('option', sug.get('argument', '')))
            description = sug.get('description', '')
            score = sug.get('score', 0)

            # Selection indicator
            indicator = TeletextBlocks.TRIANGLE_RIGHT if i == selected_index else " "

            # Score bar (visual representation)
            score_blocks = int(score * 10)
            score_bar = TeletextBlocks.FULL * score_blocks + TeletextBlocks.LIGHT * (10 - score_blocks)

            # Format line
            cmd_part = f"{indicator} {command}"
            desc_part = description[:30] if description else ""

            # Build complete line
            line = f"{cmd_part:<20} {score_bar} {desc_part}"
            padded = line.ljust(width - 2)[:width - 2]
            lines.append(f"{TeletextBlocks.VERTICAL}{padded}{TeletextBlocks.VERTICAL}")

        # More indicator
        if len(suggestions) > 5:
            more = f"  ... {len(suggestions) - 5} more (↓ to see all)"
            lines.append(f"{TeletextBlocks.VERTICAL}{more.ljust(width - 2)}{TeletextBlocks.VERTICAL}")

        # Footer with help
        lines.append(f"{TeletextBlocks.VERTICAL_RIGHT}{TeletextBlocks.HORIZONTAL * (width - 2)}{TeletextBlocks.VERTICAL_LEFT}")
        help_text = "  ↑↓ Navigate  │  TAB Complete  │  ENTER Execute"
        lines.append(f"{TeletextBlocks.VERTICAL}{help_text.ljust(width - 2)}{TeletextBlocks.VERTICAL}")
        lines.append(f"{TeletextBlocks.BOTTOM_LEFT}{TeletextBlocks.HORIZONTAL * (width - 2)}{TeletextBlocks.BOTTOM_RIGHT}")

        return "\n".join(lines)

    @staticmethod
    def create_multi_select_box(
        title: str,
        items: List[str],
        selected_items: List[int],
        current_index: int = 0,
        width: int = 60
    ) -> str:
        """
        Create multi-select box with checkboxes.

        Args:
            title: Box title
            items: List of items
            selected_items: List of selected item indices
            current_index: Currently highlighted item
            width: Box width

        Returns:
            Formatted multi-select box
        """
        lines = []

        # Top border
        lines.append(f"{TeletextBlocks.DOUBLE_TL}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_TR}")

        # Title
        title_text = f" {title} (SPACE to toggle, ENTER to confirm) "
        title_padded = title_text.center(width - 2, TeletextBlocks.DOUBLE_H)
        lines.append(f"{TeletextBlocks.DOUBLE_V}{title_padded}{TeletextBlocks.DOUBLE_V}")

        # Separator
        lines.append(f"{TeletextBlocks.DOUBLE_VR}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_VL}")

        # Items
        for i, item in enumerate(items[:9]):
            # Current highlight
            indicator = TeletextBlocks.POINTER if i == current_index else " "

            # Checkbox state
            checkbox = TeletextBlocks.CHECKBOX_ON if i in selected_items else TeletextBlocks.CHECKBOX_OFF

            # Number shortcut
            number = f"{i + 1}."

            # Format line
            line = f"{indicator} {number:3} {checkbox} {item}"
            padded = line.ljust(width - 2)[:width - 2]
            lines.append(f"{TeletextBlocks.DOUBLE_V}{padded}{TeletextBlocks.DOUBLE_V}")

        # Selection count
        lines.append(f"{TeletextBlocks.DOUBLE_VR}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_VL}")
        count_text = f"  {len(selected_items)} item(s) selected"
        lines.append(f"{TeletextBlocks.DOUBLE_V}{count_text.ljust(width - 2)}{TeletextBlocks.DOUBLE_V}")

        # Bottom border
        lines.append(f"{TeletextBlocks.DOUBLE_BL}{TeletextBlocks.DOUBLE_H * (width - 2)}{TeletextBlocks.DOUBLE_BR}")

        return "\n".join(lines)


class EnhancedPromptRenderer:
    """Enhanced prompt renderer with teletext styling."""

    def __init__(self, theme: str = 'dungeon', width: int = 70):
        """
        Initialize prompt renderer.

        Args:
            theme: Theme name
            width: Display width
        """
        self.theme = theme
        self.width = width
        self.blocks = TeletextBlocks()
        self.style = TeletextPromptStyle()

    def render_command_prompt(
        self,
        prompt_text: str = "uDOS",
        current_input: str = "",
        suggestions: Optional[List[Dict]] = None
    ) -> str:
        """
        Render enhanced command prompt with suggestions.

        Args:
            prompt_text: Prompt prefix
            current_input: Current user input
            suggestions: Optional autocomplete suggestions

        Returns:
            Formatted prompt display
        """
        output = []

        # Show suggestions if available
        if suggestions:
            output.append(self.style.create_autocomplete_panel(
                current_input, suggestions, width=self.width
            ))
            output.append("")

        # Prompt line
        prompt_line = f"{TeletextBlocks.POINTER} {prompt_text}> {current_input}"
        output.append(prompt_line)

        return "\n".join(output)

    def render_file_picker(
        self,
        current_path: str,
        files: List[Dict],
        selected_index: int = 0
    ) -> str:
        """Render file picker."""
        return self.style.create_file_tree(
            current_path, files, selected_index, width=self.width
        )

    def render_option_picker(
        self,
        title: str,
        options: List[str],
        selected_index: int = 0
    ) -> str:
        """Render option picker."""
        return self.style.create_selection_box(
            title, options, selected_index, width=self.width
        )

    def render_multi_picker(
        self,
        title: str,
        items: List[str],
        selected_items: List[int],
        current_index: int = 0
    ) -> str:
        """Render multi-select picker."""
        return self.style.create_multi_select_box(
            title, items, selected_items, current_index, width=self.width
        )


# Example usage and tests
if __name__ == '__main__':
    print("=" * 70)
    print("uDOS v1.0.30 - Enhanced Teletext Prompt System - Demo")
    print("=" * 70)
    print()

    renderer = EnhancedPromptRenderer()

    # Demo 1: Selection box
    print("1. SELECTION BOX:")
    print()
    items = ["SETUP Wizard", "CONFIG Settings", "THEME Selection", "VIEWPORT Config", "EXIT"]
    print(TeletextPromptStyle.create_selection_box("Main Menu", items, selected_index=1))
    print()

    # Demo 2: File tree
    print("2. FILE PICKER:")
    print()
    files = [
        {'name': 'README.md', 'is_dir': False, 'size': 2048},
        {'name': 'src', 'is_dir': True, 'size': 0},
        {'name': 'main.py', 'is_dir': False, 'size': 5120},
        {'name': 'config.json', 'is_dir': False, 'size': 512},
        {'name': 'tests', 'is_dir': True, 'size': 0},
    ]
    print(TeletextPromptStyle.create_file_tree('/Users/fred/project', files, selected_index=2))
    print()

    # Demo 3: Autocomplete
    print("3. AUTOCOMPLETE SUGGESTIONS:")
    print()
    suggestions = [
        {'command': 'SETUP', 'description': 'Run interactive setup wizard', 'score': 0.95},
        {'command': 'SET', 'description': 'Set configuration value', 'score': 0.75},
        {'command': 'SETTINGS', 'description': 'Manage system settings', 'score': 0.70},
    ]
    print(TeletextPromptStyle.create_autocomplete_panel('SE', suggestions, selected_index=0))
    print()

    # Demo 4: Multi-select
    print("4. MULTI-SELECT BOX:")
    print()
    extensions = ["Dashboard", "Teletext", "Map Viewer", "Data Browser"]
    selected = [0, 2]
    print(TeletextPromptStyle.create_multi_select_box("Select Extensions", extensions, selected, current_index=1))
    print()
