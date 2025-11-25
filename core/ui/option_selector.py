"""
uDOS v1.0.19 - Option Selector Service
Arrow-key navigable option selector for CLI with visual feedback
Similar to file picker but for command options, themes, maps, etc.
"""

import sys
import tty
import termios
from typing import List, Optional, Dict, Tuple, Callable, Union


class OptionSelector:
    """
    Interactive option selector with arrow key navigation.
    Similar to file picker but optimized for option lists.
    """

    def __init__(self):
        """Initialize option selector."""
        self.selected_index = 0
        self.display_start = 0
        self.max_display_items = 10

    def select(
        self,
        prompt: str,
        options: List[str],
        descriptions: Optional[List[str]] = None,
        default: Optional[str] = None,
        allow_multi: bool = False,
        category: Optional[str] = None
    ) -> Union[str, List[str]]:
        """
        Display interactive option selector with arrow key navigation.

        Args:
            prompt: Question/instruction to display
            options: List of option strings
            descriptions: Optional list of descriptions for each option
            default: Default option to highlight
            allow_multi: Allow multiple selections (spacebar to toggle)
            category: Optional category label (e.g., "Theme", "Command")

        Returns:
            Selected option string, or list of strings if allow_multi=True
        """
        if not options:
            print("❌ No options available")
            return [] if allow_multi else ""

        # Initialize state
        self.selected_index = 0
        if default and default in options:
            self.selected_index = options.index(default)

        selected_items = set()
        if default and allow_multi:
            selected_items.add(default)

        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)

        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())

            while True:
                # Clear screen and display
                self._render_options(
                    prompt=prompt,
                    options=options,
                    descriptions=descriptions,
                    selected_index=self.selected_index,
                    selected_items=selected_items if allow_multi else None,
                    category=category
                )

                # Read single character
                char = sys.stdin.read(1)

                # Handle escape sequences (arrow keys)
                if char == '\x1b':
                    next1 = sys.stdin.read(1)
                    next2 = sys.stdin.read(1)

                    if next1 == '[':
                        if next2 == 'A':  # Up arrow
                            self.selected_index = max(0, self.selected_index - 1)
                        elif next2 == 'B':  # Down arrow
                            self.selected_index = min(len(options) - 1, self.selected_index + 1)
                        elif next2 == 'C':  # Right arrow
                            pass  # Could use for expansion
                        elif next2 == 'D':  # Left arrow
                            pass  # Could use for collapse

                # Handle regular keys
                elif char == '\r' or char == '\n':  # Enter
                    break
                elif char == ' ' and allow_multi:  # Spacebar (multi-select)
                    current = options[self.selected_index]
                    if current in selected_items:
                        selected_items.remove(current)
                    else:
                        selected_items.add(current)
                elif char == 'q' or char == '\x03':  # q or Ctrl+C
                    return [] if allow_multi else ""
                elif char.isdigit():
                    # Quick jump to numbered option
                    idx = int(char) - 1
                    if 0 <= idx < len(options):
                        self.selected_index = idx
                        if not allow_multi:
                            break

            # Return result
            if allow_multi:
                # Return selected items or current if none selected
                if selected_items:
                    return sorted(list(selected_items), key=lambda x: options.index(x))
                else:
                    return [options[self.selected_index]]
            else:
                return options[self.selected_index]

        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            # Clear and show final selection
            print("\r\033[K", end="")

    def _render_options(
        self,
        prompt: str,
        options: List[str],
        descriptions: Optional[List[str]],
        selected_index: int,
        selected_items: Optional[set],
        category: Optional[str]
    ):
        """
        Render option list with highlighting.

        Args:
            prompt: Instruction text
            options: List of options
            descriptions: Optional descriptions
            selected_index: Currently highlighted index
            selected_items: Set of selected items (multi-select mode)
            category: Optional category label
        """
        # Move cursor to top of screen
        print("\033[H\033[J", end="")

        # Print header
        print("╔" + "═" * 78 + "╗")
        if category:
            print(f"║ {category.upper():^76} ║")
            print("╠" + "═" * 78 + "╣")
        print(f"║ {prompt:76} ║")
        print("╠" + "═" * 78 + "╣")

        # Calculate display window
        if len(options) > self.max_display_items:
            # Ensure selected item is visible
            if selected_index < self.display_start:
                self.display_start = selected_index
            elif selected_index >= self.display_start + self.max_display_items:
                self.display_start = selected_index - self.max_display_items + 1

            display_options = options[self.display_start:self.display_start + self.max_display_items]
            display_offset = self.display_start
        else:
            display_options = options
            display_offset = 0

        # Print options
        for i, option in enumerate(display_options):
            actual_index = i + display_offset
            is_selected = actual_index == selected_index
            is_checked = selected_items and option in selected_items

            # Format option line
            if is_selected:
                marker = "→"
                style = "\033[1;32m"  # Bold green
            else:
                marker = " "
                style = ""

            checkbox = "☑" if is_checked else "☐" if selected_items is not None else " "
            number = f"{actual_index + 1:2d}"

            # Build line
            desc = ""
            if descriptions and actual_index < len(descriptions):
                desc = f" - {descriptions[actual_index]}"

            line = f"{marker} {checkbox} {number}. {option}{desc}"

            # Truncate if too long
            if len(line) > 76:
                line = line[:73] + "..."

            print(f"║ {style}{line:76}\033[0m ║")

        # Fill remaining space
        remaining = self.max_display_items - len(display_options)
        for _ in range(remaining):
            print("║" + " " * 78 + "║")

        # Print footer with instructions
        print("╠" + "═" * 78 + "╣")
        if selected_items is not None:
            print("║ ↑/↓: Navigate  SPACE: Toggle  ENTER: Confirm  Q: Cancel" + " " * 18 + "║")
        else:
            print("║ ↑/↓: Navigate  ENTER: Select  1-9: Quick Jump  Q: Cancel" + " " * 16 + "║")
        print("╚" + "═" * 78 + "╝")

        # Show scroll indicator if needed
        if len(options) > self.max_display_items:
            total = len(options)
            shown = f"{self.display_start + 1}-{min(self.display_start + self.max_display_items, total)}"
            print(f"\n  Showing {shown} of {total} options")

    def select_with_search(
        self,
        prompt: str,
        options: List[str],
        descriptions: Optional[List[str]] = None,
        default: Optional[str] = None,
        search_placeholder: str = "Type to search..."
    ) -> str:
        """
        Option selector with live search/filter capability.

        Args:
            prompt: Question to display
            options: Full list of options
            descriptions: Optional descriptions
            default: Default option
            search_placeholder: Placeholder text for search

        Returns:
            Selected option string
        """
        # For now, fall back to basic select
        # TODO: Implement live search in future version
        return self.select(prompt, options, descriptions, default)


class EnhancedFilePicker(OptionSelector):
    """
    Enhanced file picker with arrow key navigation, multi-select, and preview.
    Extends OptionSelector for file-specific features.
    """

    def __init__(self, workspace_manager=None):
        """
        Initialize enhanced file picker.

        Args:
            workspace_manager: WorkspaceManager instance
        """
        super().__init__()
        from core.utils.files import WorkspaceManager
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.preview_enabled = True
        self.preview_lines = 5

    def select_file(
        self,
        prompt: str = "Select a file",
        directory: Optional[str] = None,
        extension: Optional[str] = None,
        allow_multi: bool = False,
        show_preview: bool = True
    ) -> Union[str, List[str]]:
        """
        Interactive file selector with preview and navigation.

        Args:
            prompt: Question to display
            directory: Starting directory
            extension: Filter by extension
            allow_multi: Allow multiple selections
            show_preview: Show file preview pane

        Returns:
            Selected file path(s)
        """
        from pathlib import Path

        current_dir = Path(directory) if directory else Path.cwd()

        # Get file list
        files = []
        for item in sorted(current_dir.iterdir()):
            if item.is_file():
                if extension and not item.name.endswith(extension):
                    continue
                if item.name.startswith('.'):
                    continue
                files.append(str(item.name))

        if not files:
            print(f"❌ No files found in {current_dir}")
            return [] if allow_multi else ""

        # Use parent selector with file names
        result = self.select(
            prompt=f"{prompt} ({current_dir})",
            options=files,
            descriptions=None,
            allow_multi=allow_multi,
            category="File Selector"
        )

        # Convert back to full paths
        if allow_multi and isinstance(result, list):
            return [str(current_dir / f) for f in result]
        elif result:
            return str(current_dir / result)
        else:
            return [] if allow_multi else ""


# Convenience functions for common use cases
def select_theme(current_theme: Optional[str] = None) -> str:
    """
    Select a uDOS theme.

    Args:
        current_theme: Current theme to highlight as default

    Returns:
        Selected theme name
    """
    selector = OptionSelector()

    themes = [
        "midnight", "forest", "ocean", "desert", "arctic",
        "volcano", "neon", "retro", "minimal", "cyberpunk",
        "dungeon", "crystal", "sunset", "aurora", "matrix"
    ]

    descriptions = [
        "Dark blue with purple accents",
        "Deep greens and earth tones",
        "Blues and aqua",
        "Warm oranges and yellows",
        "Ice blues and whites",
        "Reds and oranges",
        "Bright pinks and cyans",
        "Amber and sepia",
        "Black and white",
        "Purple and cyan",
        "Dark grays and reds",
        "Light purples and blues",
        "Orange and pink gradients",
        "Green and blue lights",
        "Green on black classic"
    ]

    return selector.select(
        prompt="Select a theme",
        options=themes,
        descriptions=descriptions,
        default=current_theme,
        category="Themes"
    )


def select_command(category: Optional[str] = None) -> str:
    """
    Select a uDOS command.

    Args:
        category: Filter by category (FILE, MAP, SYSTEM, etc.)

    Returns:
        Selected command name
    """
    selector = OptionSelector()

    # Common commands by category
    all_commands = {
        "FILE": ["LIST", "EDIT", "RUN", "CREATE", "DELETE", "COPY", "MOVE"],
        "MAP": ["SHOW", "ZOOM", "FIND", "SAVE", "LEGEND"],
        "THEME": ["SET", "LIST", "INFO", "PREVIEW"],
        "SYSTEM": ["HELP", "STATUS", "CONFIG", "REPAIR", "REBOOT"],
        "GRID": ["VIEW", "FOCUS", "SPLIT", "MERGE"],
        "ASSIST": ["OK", "ASK", "EXPLAIN", "DEBUG"]
    }

    if category:
        commands = all_commands.get(category.upper(), [])
        if not commands:
            return ""
    else:
        # Flatten all commands
        commands = []
        for cat_commands in all_commands.values():
            commands.extend(cat_commands)
        commands = sorted(set(commands))

    return selector.select(
        prompt=f"Select a command{' in ' + category if category else ''}",
        options=commands,
        category=f"{category} Commands" if category else "Commands"
    )


def select_map_cell(current_cell: Optional[str] = None) -> str:
    """
    Select a map cell reference (e.g., 'A1', 'B3').

    Args:
        current_cell: Current cell to highlight

    Returns:
        Selected cell reference
    """
    selector = OptionSelector()

    # Generate common cell references (A-J, 1-10)
    cells = []
    for row in range(1, 11):
        for col in 'ABCDEFGHIJ':
            cells.append(f"{col}{row}")

    return selector.select(
        prompt="Select a map cell",
        options=cells,
        default=current_cell,
        category="Map Navigation"
    )
