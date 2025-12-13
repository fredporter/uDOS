#!/usr/bin/env python3
"""
File Browser Example - Universal Input Device System (v1.2.25)

Demonstrates:
- SelectorFramework for file listing
- KeypadHandler for number-based selection
- MouseHandler for click selection
- Pagination for large directories
- Search/filter functionality

Usage:
    python examples/input_system/file_browser_example.py [directory]
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ui.selector_framework import (
    SelectorFramework,
    SelectableItem,
    SelectorConfig,
    SelectionMode
)
from core.input.keypad_handler import KeypadHandler, KeypadMode
from core.input.mouse_handler import MouseHandler, ClickableRegion
from core.services.device_manager import DeviceManager


class FileBrowser:
    """Interactive file browser with multi-input support."""
    
    def __init__(self, start_dir: str = "."):
        """Initialize file browser.
        
        Args:
            start_dir: Starting directory path
        """
        self.current_dir = Path(start_dir).resolve()
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,  # Match keypad 1-9
                show_numbers=True,
                show_icons=True
            )
        )
        
        # Initialize input handlers
        self.keypad = KeypadHandler()
        self.keypad.set_mode(KeypadMode.SELECTION)
        
        self.mouse = MouseHandler()
        self.device_manager = DeviceManager()
        
        # Check capabilities
        self.caps = self.device_manager.detect_input_capabilities()
        self.mouse_enabled = self.caps["mouse"]["available"]
        
        # Load initial directory
        self.load_directory()
    
    def load_directory(self) -> None:
        """Load files from current directory into selector."""
        try:
            entries = sorted(self.current_dir.iterdir())
            items = []
            
            # Add parent directory option
            if self.current_dir.parent != self.current_dir:
                items.append(SelectableItem(
                    id="..",
                    label=".. (Parent Directory)",
                    icon="📁",
                    metadata={"path": self.current_dir.parent, "is_dir": True}
                ))
            
            # Add directories first
            for entry in entries:
                if entry.is_dir():
                    items.append(SelectableItem(
                        id=entry.name,
                        label=entry.name,
                        icon="📁",
                        metadata={"path": entry, "is_dir": True}
                    ))
            
            # Add files
            for entry in entries:
                if entry.is_file():
                    icon = self._get_file_icon(entry.suffix)
                    items.append(SelectableItem(
                        id=entry.name,
                        label=f"{entry.name} ({self._format_size(entry.stat().st_size)})",
                        icon=icon,
                        metadata={"path": entry, "is_dir": False}
                    ))
            
            self.selector.set_items(items)
            self.keypad.set_items([item.label for item in items])
            
        except PermissionError:
            print(f"⚠️  Permission denied: {self.current_dir}")
    
    def _get_file_icon(self, suffix: str) -> str:
        """Get icon for file type."""
        icons = {
            ".py": "🐍",
            ".md": "📝",
            ".txt": "📄",
            ".json": "📋",
            ".yaml": "⚙️",
            ".yml": "⚙️",
            ".sh": "🔧",
            ".png": "🖼️",
            ".jpg": "🖼️",
            ".gif": "🖼️",
        }
        return icons.get(suffix.lower(), "📄")
    
    def _format_size(self, size: int) -> str:
        """Format file size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def display(self) -> None:
        """Display current directory and file list."""
        # Clear screen
        print("\033[2J\033[H")
        
        # Header
        print("=" * 70)
        print(f"📂 FILE BROWSER - {self.current_dir}")
        print("=" * 70)
        print()
        
        # File list
        lines = self.selector.display()
        for line in lines:
            print(line)
        
        print()
        print("-" * 70)
        
        # Show pagination info
        stats = self.selector.get_stats()
        if stats["total"] > stats["visible"]:
            print(f"Showing {stats['visible']} of {stats['total']} items "
                  f"(Page {stats['current_page']}/{stats['total_pages']})")
        
        # Input hints
        print()
        print("Controls:")
        print("  1-9      Select item by number")
        print("  0        Next page (if available)")
        print("  ↑/↓      Navigate (8/2 on keypad)")
        print("  Enter    Open/Select (5 on keypad)")
        print("  /        Search/Filter")
        print("  q        Quit")
        
        if self.mouse_enabled:
            print("  Mouse    Click to select")
        
        print()
    
    def handle_input(self, key: str) -> bool:
        """Handle user input.
        
        Args:
            key: Input key
            
        Returns:
            True to continue, False to quit
        """
        if key == 'q':
            return False
        
        elif key == '/':
            self.search()
        
        elif key in '123456789':
            # Number selection via keypad
            result = self.keypad.handle_key(key)
            if result and result != "next_page":
                self.select_by_label(result)
        
        elif key == '0':
            # Next page
            if self.selector.stats["has_more"]:
                self.selector.next_page()
                self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
        
        elif key in ['8', 'w']:  # Up
            self.selector.navigate_up()
        
        elif key in ['2', 's']:  # Down
            self.selector.navigate_down()
        
        elif key in ['5', '\r', '\n']:  # Select
            self.select_current()
        
        return True
    
    def select_by_label(self, label: str) -> None:
        """Select item by label (from keypad selection).
        
        Args:
            label: Item label to select
        """
        # Find item by label
        for item in self.selector.items:
            if item.label == label:
                if item.metadata["is_dir"]:
                    self.current_dir = item.metadata["path"]
                    self.load_directory()
                else:
                    print(f"\n✓ Selected file: {item.metadata['path']}")
                    input("Press Enter to continue...")
                break
    
    def select_current(self) -> None:
        """Select currently highlighted item."""
        item = self.selector.get_current_item()
        if item:
            if item.metadata["is_dir"]:
                self.current_dir = item.metadata["path"]
                self.load_directory()
            else:
                print(f"\n✓ Selected file: {item.metadata['path']}")
                input("Press Enter to continue...")
    
    def search(self) -> None:
        """Search/filter files."""
        print("\nSearch: ", end="", flush=True)
        query = input().strip()
        
        if query:
            self.selector.filter_items(query)
            self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
        else:
            self.selector.clear_filter()
            self.keypad.set_items([item.label for item in self.selector.get_visible_items()])
    
    def run(self) -> None:
        """Run file browser main loop."""
        print("🚀 Starting File Browser...")
        print(f"Input capabilities: Keypad=✓, Mouse={'✓' if self.mouse_enabled else '✗'}")
        input("Press Enter to continue...")
        
        while True:
            self.display()
            
            # Get input (simplified for example)
            try:
                key = input("Command: ").strip().lower()
                if not key:
                    continue
                
                if not self.handle_input(key[0]):
                    break
                    
            except KeyboardInterrupt:
                break
        
        print("\n👋 Goodbye!")


def main():
    """Main entry point."""
    start_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    try:
        browser = FileBrowser(start_dir)
        browser.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
