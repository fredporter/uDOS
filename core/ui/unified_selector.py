"""
uDOS v1.1.0 - Unified Selector System
Cross-platform selector using prompt_toolkit with teletext graphics and numbered fallback

Features:
- Arrow-key navigation via prompt_toolkit (works on macOS/Linux/Windows)
- Retro teletext graphics for visual appeal
- Graceful degradation to numbered menus (SSH, minimal TTY)
- Support for single-select, multi-select, and file picker
- Search/filter capabilities
- Session analytics integration

Author: uDOS Development Team
Version: 1.1.0
Phase: TUI Reliability & Input System (Feature 1.1.0.8)
Date: November 24, 2025
"""

import sys
from typing import List, Optional, Union, Callable, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class SelectorMode(Enum):
    """Selector operation modes."""
    SINGLE_SELECT = "single"
    MULTI_SELECT = "multi"
    FILE_PICKER = "file"
    SEARCH = "search"


@dataclass
class SelectorConfig:
    """Configuration for selector behavior and appearance."""
    title: str
    items: List[str]
    mode: SelectorMode = SelectorMode.SINGLE_SELECT
    descriptions: Optional[List[str]] = None
    icons: Optional[List[str]] = None
    default_index: int = 0
    default_selected: Optional[List[int]] = None  # For multi-select
    allow_cancel: bool = True
    show_numbers: bool = True
    max_display: int = 10
    category: Optional[str] = None
    # File picker specific
    file_extensions: Optional[List[str]] = None
    show_preview: bool = False
    preview_lines: int = 5
    # Search specific
    search_placeholder: str = "Type to filter..."
    min_search_chars: int = 1


class UnifiedSelector:
    """
    Cross-platform unified selector using prompt_toolkit.

    This replaces the fragmented selector implementations with a single,
    robust system that works reliably across all terminal types.
    """

    def __init__(self, use_analytics: bool = True):
        """
        Initialize unified selector.

        Args:
            use_analytics: Whether to log interactions to session analytics
        """
        self.use_analytics = use_analytics
        self.analytics = None

        # Detect capabilities
        self.advanced_mode = self._detect_advanced_mode()

        # Load session analytics if available
        if use_analytics:
            try:
                from core.services.session_analytics import SessionAnalytics
                self.analytics = SessionAnalytics()
            except ImportError:
                pass

    def _detect_advanced_mode(self) -> bool:
        """
        Detect if terminal supports advanced interactive features.

        Returns:
            True if prompt_toolkit available and running in TTY
        """
        # Check for TTY
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return False

        # Check for prompt_toolkit
        try:
            import prompt_toolkit
            return True
        except ImportError:
            return False

    def select(self, config: SelectorConfig) -> Union[str, List[str], None]:
        """
        Main selector entry point with automatic mode detection.

        Args:
            config: Selector configuration

        Returns:
            Selected item(s) or None if cancelled
        """
        if not config.items:
            print("⚠️  No items available for selection")
            return None if config.mode != SelectorMode.MULTI_SELECT else []

        # Log selector start
        start_time = None
        if self.analytics:
            import time
            start_time = time.time()

        # Check terminal size for advanced mode
        use_advanced = self.advanced_mode
        if use_advanced:
            try:
                import shutil
                cols, rows = shutil.get_terminal_size()
                # Need minimum size for prompt_toolkit to render properly
                # Menu needs at least 10 rows for display
                min_rows_needed = min(len(config.items) + 5, config.max_display + 5)
                if rows < min_rows_needed or cols < 40:
                    print(f"⚠️  Terminal too small for interactive menu ({cols}x{rows})")
                    print(f"   Using numbered menu instead (needs {min_rows_needed}+ rows, 40+ cols)")
                    use_advanced = False
            except Exception:
                # If we can't detect size, try advanced mode anyway
                pass

        # Choose implementation based on capabilities
        if use_advanced:
            result = self._select_advanced(config)
        else:
            result = self._select_fallback(config)

        # Log completion
        if self.analytics and start_time:
            import time
            duration_ms = (time.time() - start_time) * 1000
            success = result is not None and result != [] and result != ""
            self.analytics.track_command(
                command=f"SELECTOR:{config.mode.value}",
                params=[config.title, str(len(config.items))],
                duration_ms=duration_ms,
                success=success,
                context={
                    "advanced_mode": self.advanced_mode,
                    "item_count": len(config.items),
                    "result_type": type(result).__name__
                }
            )

        return result

    def _select_advanced(self, config: SelectorConfig) -> Union[str, List[str], None]:
        """
        Advanced selector using prompt_toolkit Application API.

        This provides full keyboard control with arrow keys, maintains
        the retro aesthetic, and works across platforms.
        """
        try:
            import sys
            import io
            from prompt_toolkit import Application
            from prompt_toolkit.key_binding import KeyBindings
            from prompt_toolkit.keys import Keys
            from prompt_toolkit.layout import Layout, HSplit, Window
            from prompt_toolkit.layout.controls import FormattedTextControl
            from prompt_toolkit.formatted_text import HTML
            from core.ui.visual_selector import VisualSelector

            # State
            current_index = config.default_index
            selected_indices = set(config.default_selected or [])
            search_query = ""
            filtered_items = list(range(len(config.items)))
            result_holder = {"value": None}

            # Visual renderer
            renderer = VisualSelector(width=78)

            def get_display_text():
                """Generate the display content."""
                # Apply search filter if in search mode
                if config.mode == SelectorMode.SEARCH and search_query:
                    nonlocal filtered_items
                    filtered_items = [
                        i for i, item in enumerate(config.items)
                        if search_query.lower() in item.lower()
                    ]
                    if filtered_items and current_index >= len(filtered_items):
                        # Adjust current index if out of range
                        pass

                # Determine which items to display
                display_items = (
                    [config.items[i] for i in filtered_items]
                    if config.mode == SelectorMode.SEARCH
                    else config.items
                )

                # Adjust current index for display
                display_current = current_index
                if config.mode == SelectorMode.SEARCH and filtered_items:
                    # Map current_index to filtered list
                    if current_index < len(filtered_items):
                        display_current = current_index
                    else:
                        display_current = 0

                # Generate visual menu
                if config.mode == SelectorMode.MULTI_SELECT:
                    menu = renderer.render_checkbox_menu(
                        title=config.title,
                        items=display_items[:config.max_display],
                        selected_indices=list(selected_indices),
                        descriptions=config.descriptions
                    )
                else:
                    menu = renderer.render_numbered_menu(
                        title=config.title,
                        items=display_items[:config.max_display],
                        selected_index=display_current,
                        descriptions=config.descriptions,
                        icons=config.icons
                    )

                # Add instructions
                if config.mode == SelectorMode.MULTI_SELECT:
                    instructions = "\n↑/↓: Navigate  SPACE: Toggle  ENTER: Confirm  Q/ESC: Cancel"
                elif config.mode == SelectorMode.SEARCH:
                    instructions = f"\nSearch: {search_query}_\n↑/↓: Navigate  ENTER: Select  Q/ESC: Cancel"
                else:
                    instructions = "\n↑/↓: Navigate  ENTER: Select  1-9: Quick Jump  Q/ESC: Cancel"

                if config.show_numbers and len(display_items) <= 9:
                    instructions += "\n(Or press 1-9 for quick selection)"

                return menu + instructions

            # Key bindings
            kb = KeyBindings()

            @kb.add(Keys.Up)
            def move_up(event):
                nonlocal current_index
                items_count = len(filtered_items) if config.mode == SelectorMode.SEARCH else len(config.items)
                current_index = (current_index - 1) % items_count
                event.app.invalidate()

            @kb.add(Keys.Down)
            def move_down(event):
                nonlocal current_index
                items_count = len(filtered_items) if config.mode == SelectorMode.SEARCH else len(config.items)
                current_index = (current_index + 1) % items_count
                event.app.invalidate()

            @kb.add(Keys.Enter)
            def confirm(event):
                nonlocal result_holder
                if config.mode == SelectorMode.MULTI_SELECT:
                    # Return selected items or current if none selected
                    if selected_indices:
                        result_holder["value"] = sorted([config.items[i] for i in selected_indices])
                    else:
                        result_holder["value"] = [config.items[current_index]]
                else:
                    # Single select
                    if config.mode == SelectorMode.SEARCH and filtered_items:
                        result_holder["value"] = config.items[filtered_items[current_index]]
                    else:
                        result_holder["value"] = config.items[current_index]
                event.app.exit()

            @kb.add(' ')
            def toggle_selection(event):
                """Toggle selection in multi-select mode."""
                if config.mode == SelectorMode.MULTI_SELECT:
                    if current_index in selected_indices:
                        selected_indices.remove(current_index)
                    else:
                        selected_indices.add(current_index)
                    event.app.invalidate()

            @kb.add('q')
            @kb.add(Keys.Escape)
            def cancel(event):
                nonlocal result_holder
                if config.allow_cancel:
                    result_holder["value"] = None
                    event.app.exit()

            @kb.add(Keys.ControlC)
            def ctrl_c(event):
                nonlocal result_holder
                result_holder["value"] = None
                event.app.exit()

            # Quick jump with numbers 1-9
            if config.show_numbers and len(config.items) <= 9:
                for i in range(min(9, len(config.items))):
                    def make_jump_handler(idx):
                        def jump_handler(event):
                            nonlocal result_holder
                            result_holder["value"] = config.items[idx]
                            event.app.exit()
                        return jump_handler

                    kb.add(str(i + 1))(make_jump_handler(i))

            # Search mode: capture typed characters
            if config.mode == SelectorMode.SEARCH:
                @kb.add(Keys.Any)
                def handle_search_input(event):
                    nonlocal search_query, current_index
                    char = event.data
                    if char and char.isprintable():
                        search_query += char
                        current_index = 0  # Reset to top of filtered results
                        event.app.invalidate()

                @kb.add(Keys.Backspace)
                def handle_backspace(event):
                    nonlocal search_query
                    if search_query:
                        search_query = search_query[:-1]
                        event.app.invalidate()

            # Create layout
            content_control = FormattedTextControl(
                text=get_display_text,
                focusable=True
            )

            layout = Layout(
                HSplit([
                    Window(content=content_control, height=len(config.items) + 10)
                ])
            )

            # Create application
            app = Application(
                layout=layout,
                key_bindings=kb,
                full_screen=False,
                mouse_support=False
            )

            # Run application - suppress "Window too small" messages
            # Capture stderr to prevent prompt_toolkit's error messages
            old_stderr = sys.stderr
            try:
                # Redirect stderr to suppress "Window too small..." message
                sys.stderr = io.StringIO()
                app.run()
            except Exception as run_error:
                # Restore stderr before handling error
                sys.stderr = old_stderr
                # Check if it's a size-related error
                error_msg = str(run_error).lower()
                if 'too small' in error_msg or 'size' in error_msg or 'window' in error_msg:
                    raise Exception("Terminal too small for interactive mode")
                raise  # Re-raise other errors
            finally:
                # Always restore stderr
                sys.stderr = old_stderr

            return result_holder["value"]

        except Exception as e:
            # Fallback on any error (including terminal size issues)
            error_msg = str(e).lower()
            if 'too small' in error_msg or 'size' in error_msg or 'window' in error_msg:
                print(f"⚠️  Terminal too small for interactive menu")
                print(f"   Using numbered menu instead...")
            else:
                print(f"⚠️  Interactive mode unavailable, using numbered menu")
            if self.analytics:
                self.analytics.track_error(
                    error=e,
                    context={"fallback": "numbered_menu", "mode": config.mode.value}
                )
            return self._select_fallback(config)

    def _select_fallback(self, config: SelectorConfig) -> Union[str, List[str], None]:
        """
        Fallback numbered menu for degraded terminals.

        This works reliably in any environment: SSH, tmux, screen, minimal TTY.
        """
        from core.ui.visual_selector import VisualSelector

        renderer = VisualSelector(width=78)

        # For multi-select, use checkbox rendering
        if config.mode == SelectorMode.MULTI_SELECT:
            selected_indices = set(config.default_selected or [])

            while True:
                # Render menu
                menu = renderer.render_checkbox_menu(
                    title=config.title,
                    items=config.items,
                    selected_indices=list(selected_indices),
                    descriptions=config.descriptions
                )
                print("\n" + menu)
                print("\nEnter numbers to toggle (e.g., '1 3 5'), 'done' to confirm, 'q' to cancel:")

                try:
                    choice = input("> ").strip().lower()

                    if choice == 'done':
                        if selected_indices:
                            return sorted([config.items[i] for i in selected_indices])
                        else:
                            print("⚠️  No items selected. Select at least one or type 'q' to cancel.")
                            continue

                    if choice == 'q' and config.allow_cancel:
                        return []

                    # Parse numbers
                    for part in choice.split():
                        if part.isdigit():
                            idx = int(part) - 1
                            if 0 <= idx < len(config.items):
                                if idx in selected_indices:
                                    selected_indices.remove(idx)
                                else:
                                    selected_indices.add(idx)
                            else:
                                print(f"⚠️  {part} is out of range (1-{len(config.items)})")
                        else:
                            print(f"⚠️  '{part}' is not a valid number")

                except (KeyboardInterrupt, EOFError):
                    if config.allow_cancel:
                        print("\n⚠️  Selection cancelled")
                        return []
                    else:
                        continue

        else:
            # Single select
            menu = renderer.render_numbered_menu(
                title=config.title,
                items=config.items,
                selected_index=config.default_index,
                descriptions=config.descriptions,
                icons=config.icons
            )

            print("\n" + menu)
            print("\nEnter number (1-{}) or 'q' to cancel:".format(len(config.items)))

            while True:
                try:
                    choice = input("> ").strip().lower()

                    if choice == 'q' and config.allow_cancel:
                        return None

                    if choice.isdigit():
                        idx = int(choice) - 1
                        if 0 <= idx < len(config.items):
                            return config.items[idx]
                        else:
                            print(f"⚠️  Enter a number between 1 and {len(config.items)}")
                    else:
                        # Try name match
                        for item in config.items:
                            if choice in item.lower():
                                return item
                        print(f"⚠️  '{choice}' doesn't match any item")

                except (KeyboardInterrupt, EOFError):
                    if config.allow_cancel:
                        print("\n⚠️  Selection cancelled")
                        return None


# Convenience functions for common use cases

def select_single(
    title: str,
    items: List[str],
    descriptions: Optional[List[str]] = None,
    default_index: int = 0,
    category: Optional[str] = None
) -> Optional[str]:
    """
    Quick single-select interface.

    Args:
        title: Menu title
        items: List of items to choose from
        descriptions: Optional descriptions
        default_index: Default selection
        category: Optional category label

    Returns:
        Selected item or None if cancelled
    """
    config = SelectorConfig(
        title=title,
        items=items,
        mode=SelectorMode.SINGLE_SELECT,
        descriptions=descriptions,
        default_index=default_index,
        category=category
    )

    selector = UnifiedSelector()
    return selector.select(config)


def select_multiple(
    title: str,
    items: List[str],
    descriptions: Optional[List[str]] = None,
    default_selected: Optional[List[int]] = None,
    category: Optional[str] = None
) -> List[str]:
    """
    Quick multi-select interface.

    Args:
        title: Menu title
        items: List of items to choose from
        descriptions: Optional descriptions
        default_selected: Indices of pre-selected items
        category: Optional category label

    Returns:
        List of selected items (empty if cancelled)
    """
    config = SelectorConfig(
        title=title,
        items=items,
        mode=SelectorMode.MULTI_SELECT,
        descriptions=descriptions,
        default_selected=default_selected,
        category=category
    )

    selector = UnifiedSelector()
    result = selector.select(config)
    return result if result is not None else []


def select_file(
    title: str = "Select File",
    directory: Optional[str] = None,
    extensions: Optional[List[str]] = None,
    allow_multi: bool = False
) -> Union[str, List[str], None]:
    """
    Quick file picker interface.

    Args:
        title: Picker title
        directory: Starting directory (default: current)
        extensions: Filter by extensions (e.g., ['.py', '.txt'])
        allow_multi: Allow multiple file selection

    Returns:
        Selected file path(s) or None if cancelled
    """
    start_dir = Path(directory) if directory else Path.cwd()

    # Gather files
    files = []
    for item in sorted(start_dir.iterdir()):
        if item.is_file():
            if extensions and item.suffix not in extensions:
                continue
            if item.name.startswith('.'):
                continue
            files.append(item.name)

    if not files:
        print(f"⚠️  No files found in {start_dir}")
        return [] if allow_multi else None

    config = SelectorConfig(
        title=f"{title} ({start_dir})",
        items=files,
        mode=SelectorMode.MULTI_SELECT if allow_multi else SelectorMode.SINGLE_SELECT,
        file_extensions=extensions,
        category="File Picker"
    )

    selector = UnifiedSelector()
    result = selector.select(config)

    # Convert to full paths
    if result is None:
        return None

    if isinstance(result, list):
        return [str(start_dir / f) for f in result]
    else:
        return str(start_dir / result)


def select_with_search(
    title: str,
    items: List[str],
    descriptions: Optional[List[str]] = None,
    placeholder: str = "Type to filter..."
) -> Optional[str]:
    """
    Quick search/filter interface.

    Args:
        title: Menu title
        items: List of items
        descriptions: Optional descriptions
        placeholder: Search placeholder text

    Returns:
        Selected item or None if cancelled
    """
    config = SelectorConfig(
        title=title,
        items=items,
        mode=SelectorMode.SEARCH,
        descriptions=descriptions,
        search_placeholder=placeholder
    )

    selector = UnifiedSelector()
    return selector.select(config)
