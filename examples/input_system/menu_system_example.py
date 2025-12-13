#!/usr/bin/env python3
"""
Menu System Example - Universal Input Device System (v1.2.25)

Demonstrates:
- Multi-level menu navigation
- KeypadHandler for quick selection
- MouseHandler for click navigation
- Menu state management
- Keyboard shortcuts

Usage:
    python examples/input_system/menu_system_example.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Callable

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ui.selector_framework import (
    SelectorFramework,
    SelectableItem,
    SelectorConfig,
    SelectionMode
)
from core.input.keypad_handler import KeypadHandler, KeypadMode
from core.services.device_manager import DeviceManager


class MenuItem:
    """Menu item with action or submenu."""
    
    def __init__(
        self,
        id: str,
        label: str,
        icon: str = "",
        action: Optional[Callable] = None,
        submenu: Optional[List['MenuItem']] = None,
        shortcut: str = ""
    ):
        self.id = id
        self.label = label
        self.icon = icon
        self.action = action
        self.submenu = submenu
        self.shortcut = shortcut


class MenuSystem:
    """Multi-level menu system with input device support."""
    
    def __init__(self, root_menu: List[MenuItem]):
        """Initialize menu system.
        
        Args:
            root_menu: Root level menu items
        """
        self.root_menu = root_menu
        self.menu_stack = [root_menu]  # Stack for navigation
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,
                show_numbers=True,
                show_icons=True
            )
        )
        
        self.keypad = KeypadHandler()
        self.keypad.set_mode(KeypadMode.SELECTION)
        
        self.device_manager = DeviceManager()
        self.caps = self.device_manager.detect_input_capabilities()
        
        # Load root menu
        self.load_current_menu()
    
    def load_current_menu(self) -> None:
        """Load current menu level into selector."""
        current_menu = self.menu_stack[-1]
        items = []
        
        # Add back option if not at root
        if len(self.menu_stack) > 1:
            items.append(SelectableItem(
                id="__back__",
                label="← Back",
                icon="◀️",
                metadata={"type": "back"}
            ))
        
        # Add menu items
        for item in current_menu:
            display_label = item.label
            if item.shortcut:
                display_label += f"  [{item.shortcut}]"
            
            items.append(SelectableItem(
                id=item.id,
                label=display_label,
                icon=item.icon,
                metadata={
                    "type": "menu_item",
                    "item": item
                }
            ))
        
        self.selector.set_items(items)
        self.keypad.set_items([item.label for item in items])
    
    def display(self) -> None:
        """Display current menu."""
        print("\033[2J\033[H")  # Clear screen
        
        # Header
        print("=" * 70)
        print("📋 MENU SYSTEM")
        print("=" * 70)
        print()
        
        # Breadcrumb
        depth = len(self.menu_stack)
        if depth > 1:
            print(f"Level {depth} (Root → ... → Current Menu)")
            print()
        
        # Menu items
        lines = self.selector.display()
        for line in lines:
            print(line)
        
        print()
        print("-" * 70)
        
        # Controls
        print()
        print("Controls:")
        print("  1-9      Select menu item")
        print("  ↑/↓      Navigate (8/2 on keypad)")
        print("  Enter    Select (5 on keypad)")
        print("  Esc/b    Back")
        print("  q        Quit")
        
        if self.caps["mouse"]["available"]:
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
        
        elif key in ['b', '\x1b']:  # Back or Escape
            self.go_back()
        
        elif key in '123456789':
            result = self.keypad.handle_key(key)
            if result:
                self.select_by_label(result)
        
        elif key in ['8', 'w']:  # Up
            self.selector.navigate_up()
        
        elif key in ['2', 's']:  # Down
            self.selector.navigate_down()
        
        elif key in ['5', '\r', '\n']:  # Select
            self.select_current()
        
        return True
    
    def select_by_label(self, label: str) -> None:
        """Select menu item by label.
        
        Args:
            label: Item label
        """
        for item in self.selector.items:
            if item.label == label:
                self.activate_item(item)
                break
    
    def select_current(self) -> None:
        """Select currently highlighted item."""
        item = self.selector.get_current_item()
        if item:
            self.activate_item(item)
    
    def activate_item(self, item: SelectableItem) -> None:
        """Activate selected menu item.
        
        Args:
            item: Selected item
        """
        if item.metadata["type"] == "back":
            self.go_back()
        else:
            menu_item = item.metadata["item"]
            
            if menu_item.submenu:
                # Navigate to submenu
                self.menu_stack.append(menu_item.submenu)
                self.load_current_menu()
            elif menu_item.action:
                # Execute action
                print()
                menu_item.action()
                input("\nPress Enter to continue...")
    
    def go_back(self) -> None:
        """Navigate back to previous menu level."""
        if len(self.menu_stack) > 1:
            self.menu_stack.pop()
            self.load_current_menu()
    
    def run(self) -> None:
        """Run menu system main loop."""
        print("🚀 Starting Menu System...")
        print(f"Input capabilities: Keypad=✓, Mouse={'✓' if self.caps['mouse']['available'] else '✗'}")
        input("Press Enter to continue...")
        
        while True:
            self.display()
            
            try:
                key = input("Command: ").strip().lower()
                if not key:
                    continue
                
                if not self.handle_input(key[0]):
                    break
                    
            except KeyboardInterrupt:
                break
        
        print("\n👋 Goodbye!")


# Example menu actions
def action_new_file():
    print("📄 Creating new file...")
    print("✓ New file created successfully!")

def action_open_file():
    print("📂 Opening file...")
    print("✓ File opened successfully!")

def action_save_file():
    print("💾 Saving file...")
    print("✓ File saved successfully!")

def action_exit():
    print("👋 Exiting application...")
    sys.exit(0)

def action_undo():
    print("↩️  Undo last action")

def action_redo():
    print("↪️  Redo action")

def action_cut():
    print("✂️  Cut selection")

def action_copy():
    print("📋 Copy selection")

def action_paste():
    print("📌 Paste from clipboard")

def action_preferences():
    print("⚙️  Opening preferences...")
    print("Settings panel would appear here")

def action_about():
    print("ℹ️  About this application")
    print("Universal Input Device System - v1.2.25")
    print("Demo Menu System Example")


def create_sample_menu() -> List[MenuItem]:
    """Create sample menu structure."""
    return [
        MenuItem(
            id="file",
            label="File",
            icon="📁",
            submenu=[
                MenuItem("new", "New File", "📄", action_new_file, shortcut="Ctrl+N"),
                MenuItem("open", "Open File", "📂", action_open_file, shortcut="Ctrl+O"),
                MenuItem("save", "Save", "💾", action_save_file, shortcut="Ctrl+S"),
                MenuItem("exit", "Exit", "🚪", action_exit, shortcut="Ctrl+Q"),
            ]
        ),
        MenuItem(
            id="edit",
            label="Edit",
            icon="✏️",
            submenu=[
                MenuItem("undo", "Undo", "↩️", action_undo, shortcut="Ctrl+Z"),
                MenuItem("redo", "Redo", "↪️", action_redo, shortcut="Ctrl+Y"),
                MenuItem("cut", "Cut", "✂️", action_cut, shortcut="Ctrl+X"),
                MenuItem("copy", "Copy", "📋", action_copy, shortcut="Ctrl+C"),
                MenuItem("paste", "Paste", "📌", action_paste, shortcut="Ctrl+V"),
            ]
        ),
        MenuItem(
            id="view",
            label="View",
            icon="👁️",
            submenu=[
                MenuItem("zoom_in", "Zoom In", "🔍", lambda: print("🔍 Zooming in...")),
                MenuItem("zoom_out", "Zoom Out", "🔎", lambda: print("🔎 Zooming out...")),
                MenuItem("fullscreen", "Toggle Fullscreen", "⛶", lambda: print("⛶ Toggling fullscreen...")),
            ]
        ),
        MenuItem(
            id="tools",
            label="Tools",
            icon="🔧",
            submenu=[
                MenuItem("preferences", "Preferences", "⚙️", action_preferences),
            ]
        ),
        MenuItem(
            id="help",
            label="Help",
            icon="❓",
            submenu=[
                MenuItem("docs", "Documentation", "📚", lambda: print("📚 Opening documentation...")),
                MenuItem("about", "About", "ℹ️", action_about),
            ]
        ),
    ]


def main():
    """Main entry point."""
    try:
        menu = create_sample_menu()
        system = MenuSystem(menu)
        system.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
