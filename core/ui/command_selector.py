"""
Command Selector for uDOS TUI

Interactive command palette for the terminal. Opens on TAB key and provides
scrollable command selection with help, syntax, and examples.

Part of Phase 3 TUI Enhancement — CommandSelector (TAB menu)
"""

from typing import Optional, List

from core.ui.selector_framework import (
    SelectorFramework,
    SelectableItem,
    SelectorConfig,
    SelectionMode,
)
from core.input.keypad_handler import KeypadHandler, KeypadMode
from core.input.command_prompt import CommandRegistry, CommandMetadata
from core.services.logging_api import get_logger


_CONTINUE = object()


class CommandSelector:
    """Interactive command palette using SelectorFramework."""

    def __init__(self, registry: CommandRegistry, page_size: int = 9):
        self.registry = registry
        self.logger = get_logger("core", category="command-selector", name="command-selector")

        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=page_size,
                show_numbers=True,
            )
        )
        self.keypad = KeypadHandler()
        self.keypad.set_mode(KeypadMode.SELECTION)

        self._load_items()

    def _load_items(self) -> None:
        """Load registry commands into selector items."""
        items: List[SelectableItem] = []
        for cmd in self.registry.list_all():
            label = f"{cmd.icon} {cmd.name:<10} — {cmd.help_text}"
            items.append(
                SelectableItem(
                    id=cmd.name,
                    label=label,
                    value=cmd.name,
                    icon=cmd.icon,
                    metadata={
                        "command": cmd,
                        "syntax": cmd.syntax,
                        "examples": cmd.examples,
                        "options": cmd.options,
                        "category": cmd.category,
                    },
                )
            )

        self.selector.set_items(items)
        self.keypad.set_items([item.label for item in items])

    def display(self) -> None:
        """Display command selector UI."""
        print("\033[2J\033[H", end="")
        print("=" * 70)
        print("COMMAND SELECTOR (TAB)")
        print("=" * 70)

        for line in self.selector.get_display_lines():
            print(line)

        current = self.selector.get_current_item()
        if current:
            cmd: CommandMetadata = current.metadata.get("command")
            print(f"  → {cmd.icon} {cmd.name}  [{cmd.category}]")
            if cmd.syntax:
                print(f"    Syntax: {cmd.syntax}")
            if cmd.examples:
                print(f"    Example: {cmd.examples[0]}")

        print("-" * 70)
        print("Controls:")
        print("  j/k or 2/8   Move down/up")
        print("  enter/5      Select command")
        print("  n/p or 0     Next/prev page")
        print("  /            Search")
        print("  h/?          Help")
        print("  q            Cancel")
        print()

    def handle_input(self, key: str):
        if key == "q":
            return None

        if key in ("h", "?"):
            self._show_help()
            return _CONTINUE

        if key == "/":
            self.search()
            return _CONTINUE

        if key in "123456789":
            result = self.keypad.handle_key(key)
            if result and result != "next_page":
                return self._select_by_label(result)
            if result == "next_page":
                self.selector.next_page()
                self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
            return _CONTINUE

        if key in ("0", "n"):
            self.selector.next_page()
            self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
            return _CONTINUE

        if key == "p":
            self.selector.prev_page()
            self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
            return _CONTINUE

        if key in ("k", "8"):
            self.selector.navigate_up()
            return _CONTINUE

        if key in ("j", "2"):
            self.selector.navigate_down()
            return _CONTINUE

        if key in ("5", ""):
            return self._select_current()

        return _CONTINUE

    def _select_by_label(self, label: str):
        for item in self.selector.items:
            if item.label == label:
                return item.value
        return _CONTINUE

    def _select_current(self):
        item = self.selector.get_current_item()
        if not item:
            return _CONTINUE
        return item.value

    def search(self) -> None:
        try:
            query = input("Search: ").strip()
        except (KeyboardInterrupt, EOFError):
            # User cancelled search
            return

        if query:
            self.selector.filter_items(query)
        else:
            self.selector.clear_filter()
        self.keypad.set_items([item.label for item in self.selector.get_visible_items()])

    def _show_help(self) -> None:
        print("\033[2J\033[H", end="")
        print("=" * 70)
        print("COMMAND SELECTOR HELP")
        print("=" * 70)
        print()
        print("Use this menu to insert a command into the prompt.")
        print()
        print("Navigation:")
        print("  j/k or 2/8     Move up/down")
        print("  1-9            Quick select by number")
        print("  Enter or 5     Select command")
        print("  n/p or 0       Next/prev page")
        print("  /              Search commands")
        print("  q              Cancel")
        print()
        try:
            input("Press Enter to continue...")
        except (KeyboardInterrupt, EOFError):
            pass  # User cancelled, just return

    def pick(self) -> Optional[str]:
        """Open command selector and return selected command or None."""
        try:
            while True:
                self.display()
                try:
                    key = input("Command: ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    # User cancelled with Ctrl+C or Ctrl+D
                    return None

                if key == "":
                    key = "5"

                # Safely get first character
                first_char = key[0] if key else ""
                result = self.handle_input(first_char)

                if result is None:
                    return None
                if result is not _CONTINUE and isinstance(result, str):
                    return f"{result} "
        except Exception as e:
            self.logger.error(f"Command selector error: {e}")
            return None
