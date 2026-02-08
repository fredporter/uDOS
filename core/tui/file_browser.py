"""
Core TUI File Browser

Interactive file picker for terminal use. Designed for simple, mac/unix-friendly
key controls without overriding standard hotkeys.
"""

import os
from pathlib import Path
from typing import List, Optional

from core.ui.selector_framework import (
    SelectorFramework,
    SelectableItem,
    SelectorConfig,
    SelectionMode,
)
from core.input.keypad_handler import KeypadHandler, KeypadMode
from core.services.viewport_service import ViewportService
from core.utils.text_width import truncate_to_width


_CONTINUE = object()


class FileBrowser:
    """Interactive file browser with selector and keypad support."""

    def __init__(self, start_dir: str = ".", pick_directories: bool = True):
        self.current_dir = Path(start_dir).resolve()
        self.pick_directories = pick_directories
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,
                show_numbers=True,
            )
        )
        self.keypad = KeypadHandler()
        self.keypad.set_mode(KeypadMode.SELECTION)
        self.load_directory()

    def load_directory(self) -> None:
        try:
            entries = sorted(self.current_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            items: List[SelectableItem] = []

            if self.current_dir.parent != self.current_dir:
                items.append(
                    SelectableItem(
                        id="..",
                        label=".. (parent)",
                        metadata={"path": self.current_dir.parent, "is_dir": True},
                    )
                )

            for entry in entries:
                if entry.is_dir():
                    items.append(
                        SelectableItem(
                            id=entry.name,
                            label=f"{entry.name}/",
                            metadata={"path": entry, "is_dir": True},
                        )
                    )

            for entry in entries:
                if entry.is_file():
                    items.append(
                        SelectableItem(
                            id=entry.name,
                            label=entry.name,
                            metadata={"path": entry, "is_dir": False},
                        )
                    )

            self.selector.set_items(items)
            self.keypad.set_items([item.label for item in items])
        except PermissionError:
            print(f"[WARN] Permission denied: {self.current_dir}")

    def display(self) -> None:
        width = ViewportService().get_cols()
        print("\033[2J\033[H", end="")
        print("=" * 70)
        print(f"FILE BROWSER - {self.current_dir}")
        print("=" * 70)
        for line in self.selector.get_display_lines():
            print(truncate_to_width(line, width))
        print("-" * 70)
        print("Controls:")
        print("  j/k or 2/8   Move down/up")
        print("  enter/5      Open/select")
        print("  n/p or 0     Next/prev page")
        print("  /            Search")
        print("  c            Choose current directory")
        print("  q            Quit")
        print()

    def handle_input(self, key: str):
        if key == "q":
            return None
        if key == "/":
            self.search()
            return _CONTINUE
        if key == "c":
            return self.current_dir

        if key in "123456789":
            result = self.keypad.handle_key(key)
            if result and result != "next_page":
                return self.select_by_label(result)
            if result == "next_page":
                self.selector.next_page()
                self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
            return _CONTINUE

        if key in ("0", "n"):
            self.selector.next_page()
            self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
            return _CONTINUE

        if key in ("p",):
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
            return self.select_current()

        return _CONTINUE

    def select_by_label(self, label: str):
        for item in self.selector.items:
            if item.label == label:
                return self._handle_item_selection(item)
        return _CONTINUE

    def select_current(self):
        item = self.selector.get_current_item()
        if not item:
            return _CONTINUE
        return self._handle_item_selection(item)

    def _handle_item_selection(self, item: SelectableItem):
        path = item.metadata.get("path")
        is_dir = item.metadata.get("is_dir")
        if is_dir:
            self.current_dir = path
            self.load_directory()
            return _CONTINUE
        if not self.pick_directories:
            return path
        return _CONTINUE

    def search(self) -> None:
        query = input("Search: ").strip()
        if query:
            self.selector.filter_items(query)
        else:
            self.selector.clear_filter()
        self.keypad.set_items([item.label for item in self.selector.get_visible_items()])

    def pick(self) -> Optional[Path]:
        while True:
            self.display()
            key = input("Command: ").strip().lower()
            if key == "":
                key = "5"
            result = self.handle_input(key[0] if key else "")
            if result is None:
                return None
            if isinstance(result, Path):
                return result
