"""
uDOS v1.0.31 - Standardized Input System
Unified, reliable CLI input with visual feedback and terminal compatibility

Features:
- Single, consistent interface for all user input
- Visual menus using teletext block characters
- Numbered selection (1-9) with arrow key support
- Automatic fallback for terminal compatibility
- File picker with tree visualization
- Progress bars and status indicators
- Smart autocomplete integration

Author: uDOS Development Team
Version: 1.0.31
Date: November 22, 2025
"""

import sys
import os
from typing import List, Optional, Tuple, Callable, Any, Dict
from pathlib import Path


class StandardizedInput:
    """
    Unified input system with visual feedback and reliable fallback.

    All uDOS components should use this for user input to ensure:
    - Consistent UX across the application
    - Terminal compatibility (works on all platforms)
    - Visual feedback using teletext blocks
    - Graceful degradation when advanced features unavailable
    """

    def __init__(self, use_advanced: Optional[bool] = None):
        """
        Initialize standardized input system.

        Args:
            use_advanced: Force advanced/basic mode, or None for auto-detect
        """
        self.advanced_mode = self._detect_capabilities() if use_advanced is None else use_advanced
        self.visual_renderer = None

        # Load visual renderer if in advanced mode
        if self.advanced_mode:
            try:
                from core.ui.visual_selector import VisualSelector
                self.visual_renderer = VisualSelector()
            except ImportError:
                self.advanced_mode = False

    def _detect_capabilities(self) -> bool:
        """
        Detect if terminal supports advanced features.

        Returns:
            True if advanced features available, False for basic mode
        """
        # Check if running in a real terminal
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return False

        # Check if prompt_toolkit is available
        try:
            import prompt_toolkit
            return True
        except ImportError:
            return False

    def select_option(
        self,
        title: str,
        options: List[str],
        descriptions: Optional[List[str]] = None,
        default_index: int = 0,
        show_numbers: bool = True,
        allow_filter: bool = False,
        icons: Optional[List[str]] = None
    ) -> Tuple[int, str]:
        """
        Single option selector with visual menu.

        Args:
            title: Menu title
            options: List of option strings
            descriptions: Optional descriptions for each option
            default_index: Initially selected option (0-based)
            show_numbers: Show 1-9 numbers for quick selection
            allow_filter: Allow typing to filter options
            icons: Optional icons for each option

        Returns:
            Tuple of (selected_index, selected_option)

        Example:
            idx, choice = si.select_option(
                "Select Theme",
                ["Dungeon", "Science", "Cyberpunk"]
            )
        """
        if not options:
            raise ValueError("Options list cannot be empty")

        # Limit to 9 options for numbered selection
        display_options = options[:9] if show_numbers else options

        if self.advanced_mode and self.visual_renderer:
            try:
                return self._select_with_visual_menu(
                    title, display_options, descriptions, default_index, icons
                )
            except Exception as e:
                # Fallback on any error
                self.advanced_mode = False

        # Basic mode: numbered menu
        return self._select_with_numbers(
            title, display_options, descriptions, default_index, icons
        )

    def _select_with_numbers(
        self,
        title: str,
        options: List[str],
        descriptions: Optional[List[str]],
        default_index: int,
        icons: Optional[List[str]]
    ) -> Tuple[int, str]:
        """Basic numbered selection (always works)."""
        from core.ui.visual_selector import VisualSelector

        renderer = VisualSelector()
        menu = renderer.render_numbered_menu(
            title, options, default_index, descriptions, icons
        )

        print(menu)

        while True:
            try:
                choice = input("\n> ").strip()

                # Try parsing as number
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(options):
                        return index, options[index]
                    print(f"⚠️  Enter 1-{len(options)}")
                    continue

                # Try exact match
                for i, option in enumerate(options):
                    if option.lower() == choice.lower():
                        return i, option

                # Try partial match
                matches = [
                    (i, opt) for i, opt in enumerate(options)
                    if choice.lower() in opt.lower()
                ]

                if len(matches) == 1:
                    return matches[0]
                elif len(matches) > 1:
                    print(f"⚠️  Ambiguous: {', '.join(m[1] for m in matches)}")
                else:
                    print(f"⚠️  Invalid option. Enter 1-{len(options)}")

            except (KeyboardInterrupt, EOFError):
                print("\n⚠️  Selection cancelled")
                return -1, ""

    def _select_with_visual_menu(
        self,
        title: str,
        options: List[str],
        descriptions: Optional[List[str]],
        default_index: int,
        icons: Optional[List[str]]
    ) -> Tuple[int, str]:
        """Advanced selection with arrow keys (when supported)."""
        try:
            from prompt_toolkit import prompt
            from prompt_toolkit.key_binding import KeyBindings
            from prompt_toolkit.keys import Keys
            from prompt_toolkit.formatted_text import ANSI
            from core.ui.visual_selector import VisualSelector

            renderer = VisualSelector()
            current_index = default_index

            bindings = KeyBindings()

            @bindings.add(Keys.Up)
            def _(event):
                nonlocal current_index
                current_index = (current_index - 1) % len(options)
                event.app.exit(result='update')

            @bindings.add(Keys.Down)
            def _(event):
                nonlocal current_index
                current_index = (current_index + 1) % len(options)
                event.app.exit(result='update')

            @bindings.add(Keys.Enter)
            def _(event):
                event.app.exit(result='select')

            @bindings.add('q')
            def _(event):
                event.app.exit(result='quit')

            @bindings.add(Keys.ControlC)
            def _(event):
                event.app.exit(result='quit')

            # Allow number keys 1-9
            for i in range(min(9, len(options))):
                num_key = str(i + 1)
                @bindings.add(num_key)
                def _(event, idx=i):
                    nonlocal current_index
                    current_index = idx
                    event.app.exit(result='select')

            while True:
                # Render menu with current selection
                menu = renderer.render_numbered_menu(
                    title, options, current_index, descriptions, icons
                )
                print("\033[2J\033[H" + menu)  # Clear screen and show menu
                print("\nUse ↑↓ arrows, numbers 1-9, or 'q' to quit")

                try:
                    result = prompt("", key_bindings=bindings)

                    if result == 'select':
                        return current_index, options[current_index]
                    elif result == 'quit':
                        print("\n⚠️  Selection cancelled")
                        return -1, ""
                    # 'update' continues loop with new index

                except (KeyboardInterrupt, EOFError):
                    print("\n⚠️  Selection cancelled")
                    return -1, ""

        except Exception as e:
            # Fallback to numbered selection on any error
            return self._select_with_numbers(title, options, descriptions, default_index, icons)

    def select_multiple(
        self,
        title: str,
        options: List[str],
        default_selected: Optional[List[int]] = None,
        min_select: int = 0,
        max_select: Optional[int] = None,
        descriptions: Optional[List[str]] = None
    ) -> List[int]:
        """
        Multiple option selector with checkboxes.

        Args:
            title: Menu title
            options: List of option strings
            default_selected: List of initially selected indices
            min_select: Minimum number of selections required
            max_select: Maximum number of selections allowed
            descriptions: Optional descriptions

        Returns:
            List of selected indices
        """
        if not options:
            raise ValueError("Options list cannot be empty")

        selected = set(default_selected or [])
        from core.ui.visual_selector import VisualSelector
        renderer = VisualSelector()

        while True:
            menu = renderer.render_checkbox_menu(
                title, options, list(selected), descriptions
            )
            print(menu)

            print("\nCommands: [number] toggle, 'a' all, 'n' none, 'd' done")
            choice = input("> ").strip().lower()

            if choice == 'd' or choice == 'done':
                if len(selected) >= min_select:
                    if max_select is None or len(selected) <= max_select:
                        return sorted(list(selected))
                    else:
                        print(f"⚠️  Maximum {max_select} selections allowed")
                else:
                    print(f"⚠️  Minimum {min_select} selections required")

            elif choice == 'a' or choice == 'all':
                selected = set(range(len(options)))

            elif choice == 'n' or choice == 'none':
                selected.clear()

            elif choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(options):
                    if index in selected:
                        selected.remove(index)
                    else:
                        if max_select is None or len(selected) < max_select:
                            selected.add(index)
                        else:
                            print(f"⚠️  Maximum {max_select} selections reached")

    def select_file(
        self,
        title: str = "Select File",
        start_path: str = ".",
        file_types: Optional[List[str]] = None,
        allow_directories: bool = True,
        show_tree: bool = True
    ) -> Optional[str]:
        """
        File/directory picker with tree visualization.

        Args:
            title: Picker title
            start_path: Starting directory
            file_types: List of allowed extensions (e.g., ['.md', '.json'])
            allow_directories: Allow selecting directories
            show_tree: Show directory tree visualization

        Returns:
            Selected file path or None if cancelled
        """
        from core.ui.file_picker import FilePicker

        picker = FilePicker()
        return picker.pick_file(
            start_path=start_path,
            file_types=file_types,
            allow_directories=allow_directories,
            title=title
        )

    def input_text(
        self,
        prompt: str,
        default: str = "",
        validate: Optional[Callable[[str], bool]] = None,
        suggestions: Optional[List[str]] = None,
        multiline: bool = False,
        required: bool = False
    ) -> str:
        """
        Text input with validation and suggestions.

        Args:
            prompt: Input prompt text
            default: Default value
            validate: Validation function (returns True if valid)
            suggestions: List of suggested values
            multiline: Allow multiple lines
            required: Require non-empty input

        Returns:
            User input string
        """
        if suggestions:
            print(f"\n{prompt}")
            print(f"Suggestions: {', '.join(suggestions[:5])}")
            if default:
                prompt_text = f"[{default}] > "
            else:
                prompt_text = "> "
        else:
            prompt_text = f"{prompt} [{default}] > " if default else f"{prompt} > "

        while True:
            try:
                value = input(prompt_text).strip()

                # Use default if empty
                if not value and default:
                    value = default

                # Check required
                if required and not value:
                    print("⚠️  This field is required")
                    continue

                # Validate
                if validate and value:
                    if not validate(value):
                        print("⚠️  Invalid input")
                        continue

                return value

            except (KeyboardInterrupt, EOFError):
                print("\n⚠️  Input cancelled")
                return default if default else ""

    def confirm(
        self,
        message: str,
        default: bool = False
    ) -> bool:
        """
        Yes/No confirmation dialog.

        Args:
            message: Confirmation message
            default: Default response if user presses Enter

        Returns:
            True for yes, False for no
        """
        default_text = "Y/n" if default else "y/N"
        prompt = f"{message} [{default_text}] > "

        try:
            response = input(prompt).strip().lower()

            if not response:
                return default

            return response in ['y', 'yes', 'true', '1']

        except (KeyboardInterrupt, EOFError):
            print("\n⚠️  Cancelled")
            return False

    def show_progress(
        self,
        current: int,
        total: int,
        label: str = "",
        width: int = 40
    ) -> str:
        """
        Show progress bar.

        Args:
            current: Current progress value
            total: Total value
            label: Optional label
            width: Width of progress bar in characters

        Returns:
            Formatted progress bar string
        """
        from core.ui.visual_selector import VisualSelector

        renderer = VisualSelector()
        return renderer.render_progress(current, total, label, width)

    def show_status(
        self,
        message: str,
        status: str = "info",
        details: Optional[str] = None
    ):
        """
        Show status message with icon.

        Args:
            message: Status message
            status: Status type (info, success, warning, error)
            details: Optional details text
        """
        from core.ui.visual_selector import VisualSelector

        renderer = VisualSelector()
        status_msg = renderer.render_status(message, status, details)
        print(status_msg)

    def text_input(
        self,
        prompt: str,
        default: str = "",
        required: bool = False,
        validator: Optional[callable] = None
    ) -> str:
        """
        Get text input from user with optional validation.

        Args:
            prompt: Prompt message
            default: Default value (shown in prompt)
            required: Whether input is required (can't be empty)
            validator: Optional validation function (str) -> bool

        Returns:
            User input string
        """
        try:
            from prompt_toolkit import prompt as pt_prompt
            from prompt_toolkit.styles import Style

            # Build prompt text
            prompt_text = f"{prompt}"
            if default:
                prompt_text += f" [{default}]"
            prompt_text += ": "

            # Visual style matching teletext theme
            style = Style.from_dict({
                'prompt': '#00ffff bold',
            })

            while True:
                try:
                    result = pt_prompt(
                        prompt_text,
                        style=style,
                        default=default if default else ""
                    )
                except KeyboardInterrupt:
                    raise
                except Exception:
                    # Fallback to basic input
                    result = input(prompt_text)

                # Use default if empty and default provided
                if not result and default:
                    result = default

                # Check required constraint
                if required and not result:
                    self.show_status("Input is required", "error")
                    continue

                # Run validator if provided
                if validator and result:
                    if not validator(result):
                        self.show_status("Invalid input", "error")
                        continue

                return result

        except KeyboardInterrupt:
            self.show_status("\nInput cancelled", "warning")
            return ""
