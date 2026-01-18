#!/usr/bin/env python3
"""
Configuration Panel Example - Universal Input Device System (v1.2.25)

Demonstrates:
- Settings management with selector
- Toggle switches with keypad
- Value adjustment controls
- Input validation
- Device capability detection

Usage:
    python examples/input_system/config_panel_example.py
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

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


class Setting:
    """Configuration setting."""
    
    def __init__(
        self,
        id: str,
        label: str,
        value: Any,
        setting_type: str,  # bool, int, str, choice
        options: List[Any] = None,
        min_val: int = None,
        max_val: int = None
    ):
        self.id = id
        self.label = label
        self.value = value
        self.setting_type = setting_type
        self.options = options or []
        self.min_val = min_val
        self.max_val = max_val
    
    def format_value(self) -> str:
        """Format value for display."""
        if self.setting_type == "bool":
            return "✓ ON" if self.value else "✗ OFF"
        elif self.setting_type == "choice":
            return str(self.value)
        else:
            return str(self.value)
    
    def toggle(self) -> None:
        """Toggle boolean setting."""
        if self.setting_type == "bool":
            self.value = not self.value
    
    def increment(self) -> None:
        """Increment numeric setting."""
        if self.setting_type == "int":
            if self.max_val is None or self.value < self.max_val:
                self.value += 1
    
    def decrement(self) -> None:
        """Decrement numeric setting."""
        if self.setting_type == "int":
            if self.min_val is None or self.value > self.min_val:
                self.value -= 1
    
    def next_option(self) -> None:
        """Select next option in choice setting."""
        if self.setting_type == "choice" and self.options:
            current_idx = self.options.index(self.value) if self.value in self.options else 0
            next_idx = (current_idx + 1) % len(self.options)
            self.value = self.options[next_idx]


class ConfigPanel:
    """Configuration panel with multi-input support."""
    
    def __init__(self):
        """Initialize configuration panel."""
        self.settings = self._create_settings()
        self.selector = SelectorFramework(
            config=SelectorConfig(
                mode=SelectionMode.SINGLE,
                page_size=9,
                show_numbers=True,
                show_icons=False
            )
        )
        
        self.keypad = KeypadHandler()
        self.keypad.set_mode(KeypadMode.SELECTION)
        
        self.device_manager = DeviceManager()
        self.caps = self.device_manager.detect_input_capabilities()
        
        self.load_settings()
    
    def _create_settings(self) -> Dict[str, Setting]:
        """Create sample settings."""
        return {
            "mouse_input": Setting(
                "mouse_input",
                "Mouse Input",
                True,
                "bool"
            ),
            "keypad_mode": Setting(
                "keypad_mode",
                "Keypad Mode",
                "navigation",
                "choice",
                options=["navigation", "selection", "editing", "menu"]
            ),
            "page_size": Setting(
                "page_size",
                "Items Per Page",
                9,
                "int",
                min_val=5,
                max_val=20
            ),
            "show_icons": Setting(
                "show_icons",
                "Show Icons",
                True,
                "bool"
            ),
            "theme": Setting(
                "theme",
                "Color Theme",
                "galaxy",
                "choice",
                options=["foundation", "galaxy", "midnight", "dawn"]
            ),
            "sound": Setting(
                "sound",
                "Sound Effects",
                False,
                "bool"
            ),
            "autosave": Setting(
                "autosave",
                "Auto-Save",
                True,
                "bool"
            ),
            "timeout": Setting(
                "timeout",
                "Session Timeout (min)",
                30,
                "int",
                min_val=5,
                max_val=120
            ),
        }
    
    def load_settings(self) -> None:
        """Load settings into selector."""
        items = []
        
        for setting_id, setting in self.settings.items():
            label = f"{setting.label:<30} {setting.format_value():>20}"
            items.append(SelectableItem(
                id=setting_id,
                label=label,
                metadata={"setting": setting}
            ))
        
        self.selector.set_items(items)
        self.keypad.set_items([item.label for item in items])
    
    def display(self) -> None:
        """Display configuration panel."""
        print("\033[2J\033[H")  # Clear screen
        
        # Header
        print("=" * 70)
        print("⚙️  CONFIGURATION PANEL")
        print("=" * 70)
        print()
        
        # Settings list
        lines = self.selector.display()
        for line in lines:
            print(line)
        
        print()
        print("-" * 70)
        
        # Current setting details
        current = self.selector.get_current_item()
        if current:
            setting = current.metadata["setting"]
            print(f"\nCurrent Setting: {setting.label}")
            print(f"Type: {setting.setting_type}")
            print(f"Value: {setting.format_value()}")
            
            if setting.setting_type == "int":
                print(f"Range: {setting.min_val} - {setting.max_val}")
            elif setting.setting_type == "choice":
                print(f"Options: {', '.join(str(o) for o in setting.options)}")
        
        print()
        print("-" * 70)
        
        # Controls
        print()
        print("Controls:")
        print("  1-9      Select setting")
        print("  ↑/↓      Navigate (8/2 on keypad)")
        print("  Enter    Toggle/Next (5 on keypad)")
        print("  ←/→      Decrease/Increase (4/6 on keypad)")
        print("  s        Save configuration")
        print("  r        Reset to defaults")
        print("  q        Quit")
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
        
        elif key == 's':
            self.save_config()
        
        elif key == 'r':
            self.reset_config()
        
        elif key in '123456789':
            result = self.keypad.handle_key(key)
            if result:
                self.select_by_label(result)
        
        elif key in ['8', 'w']:  # Up
            self.selector.navigate_up()
        
        elif key in ['2', 's']:  # Down
            self.selector.navigate_down()
        
        elif key in ['5', '\r', '\n']:  # Toggle/Next
            self.toggle_current()
        
        elif key in ['4', 'a']:  # Decrease/Previous
            self.adjust_current(-1)
        
        elif key in ['6', 'd']:  # Increase/Next
            self.adjust_current(1)
        
        return True
    
    def select_by_label(self, label: str) -> None:
        """Select setting by label.
        
        Args:
            label: Setting label
        """
        for item in self.selector.items:
            if item.label == label:
                self.selector.navigate_to(item.id)
                break
    
    def toggle_current(self) -> None:
        """Toggle or advance current setting."""
        item = self.selector.get_current_item()
        if item:
            setting = item.metadata["setting"]
            
            if setting.setting_type == "bool":
                setting.toggle()
            elif setting.setting_type == "choice":
                setting.next_option()
            elif setting.setting_type == "int":
                setting.increment()
            
            self.load_settings()  # Refresh display
    
    def adjust_current(self, direction: int) -> None:
        """Adjust current setting value.
        
        Args:
            direction: -1 for decrease, 1 for increase
        """
        item = self.selector.get_current_item()
        if item:
            setting = item.metadata["setting"]
            
            if setting.setting_type == "int":
                if direction > 0:
                    setting.increment()
                else:
                    setting.decrement()
                self.load_settings()
    
    def save_config(self) -> None:
        """Save configuration."""
        print("\n💾 Saving configuration...")
        
        # In real application, would save to file
        config_data = {
            setting_id: setting.value
            for setting_id, setting in self.settings.items()
        }
        
        print("✓ Configuration saved successfully!")
        print(f"Settings: {config_data}")
        input("\nPress Enter to continue...")
    
    def reset_config(self) -> None:
        """Reset to default configuration."""
        print("\n⚠️  Reset to defaults?")
        confirm = input("Type 'yes' to confirm: ").strip().lower()
        
        if confirm == 'yes':
            self.settings = self._create_settings()
            self.load_settings()
            print("✓ Configuration reset to defaults")
        else:
            print("✗ Reset cancelled")
        
        input("\nPress Enter to continue...")
    
    def run(self) -> None:
        """Run configuration panel main loop."""
        print("🚀 Starting Configuration Panel...")
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


def main():
    """Main entry point."""
    try:
        panel = ConfigPanel()
        panel.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
