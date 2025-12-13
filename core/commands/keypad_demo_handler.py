"""
KEYPAD Demo Handler - v1.2.25

Demonstrates the Universal KEYPAD Handler and Selector system.
Shows how to integrate standardized selectors into any command.

Usage:
    KEYPAD DEMO              - Show selector demo
    KEYPAD MENU              - Show menu selector example
    KEYPAD LIST              - Show list selector example
    KEYPAD TEST              - Interactive keypad test

Version: 1.0.0 (v1.2.25)
"""

from typing import List, Optional, Any
from core.commands.base_handler import BaseCommandHandler
from core.input.keypad_handler import get_keypad_handler, KeypadMode
from core.ui.selector_base import MenuSelector, ListSelector, create_menu


class KeypadDemoHandler(BaseCommandHandler):
    """Demonstrates keypad and selector system."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keypad = get_keypad_handler()
    
    def handle_command(self, params: List[str]) -> str:
        """Handle KEYPAD command.
        
        Args:
            params: Command parameters (either ["KEYPAD", "DEMO"] or ["DEMO"])
            
        Returns:
            Command output
        """
        if not params:
            return self._show_usage()
        
        # Handle both routing patterns: ["KEYPAD", "DEMO"] or ["DEMO"]
        first_param = params[0].upper()
        
        if first_param == "KEYPAD":
            # Full command: KEYPAD DEMO
            if len(params) < 2:
                return self._show_usage()
            subcommand = params[1].upper()
        else:
            # Direct subcommand: DEMO (routed from uDOS_commands.py)
            subcommand = first_param
        
        if subcommand == "DEMO":
            return self._show_demo()
        elif subcommand == "MENU":
            return self._show_menu_example()
        elif subcommand == "LIST":
            return self._show_list_example()
        elif subcommand == "TEST":
            return self._show_test()
        elif subcommand == "KEYS":
            return self._show_key_reference()
        elif subcommand == "":
            return self._show_usage()
        else:
            return self._show_usage()
    
    def _show_usage(self) -> str:
        """Show KEYPAD command usage."""
        return """
🎮 KEYPAD Command - Universal Input System Demo

Commands:
  KEYPAD DEMO              Show selector demonstrations
  KEYPAD MENU              Menu selector example
  KEYPAD LIST              List selector example
  KEYPAD TEST              Interactive keypad test
  KEYPAD KEYS              Show key reference

Examples:
  KEYPAD DEMO              # See all selector types
  KEYPAD MENU              # Simple menu example
  KEYPAD LIST              # List with custom labels

💡 The KEYPAD system provides consistent 0-9 input across all uDOS panels
""".strip()
    
    def _show_demo(self) -> str:
        """Show comprehensive demo."""
        lines = []
        
        lines.append("🎮 UNIVERSAL KEYPAD SYSTEM DEMO")
        lines.append("=" * 60)
        lines.append("")
        lines.append("The keypad system provides consistent navigation using 0-9:")
        lines.append("")
        
        # Key layout
        lines.append("  +------+------+------+")
        lines.append("  |  7   |  8   |  9   |")
        lines.append("  | REDO |  ↑   | UNDO |")
        lines.append("  +------+------+------+")
        lines.append("  |  4   |  5   |  6   |")
        lines.append("  |  ←   |  OK  |  →   |")
        lines.append("  +------+------+------+")
        lines.append("  |  1   |  2   |  3   |")
        lines.append("  | YES  |  ↓   |  NO  |")
        lines.append("  +------+------+------+")
        lines.append("         |  0   |")
        lines.append("         | MENU |")
        lines.append("         +------+")
        lines.append("")
        
        # Menu example
        lines.append("📋 MENU SELECTOR EXAMPLE:")
        lines.append("")
        menu = create_menu(
            ["New File", "Open File", "Save File", "Close"],
            "File Menu",
            ["📄", "📁", "💾", "❌"]
        )
        lines.append(menu.render())
        lines.append("")
        lines.append(f"Key hints: {menu.get_key_hints()}")
        lines.append("")
        
        # List example
        lines.append("─" * 60)
        lines.append("")
        lines.append("📂 LIST SELECTOR EXAMPLE:")
        lines.append("")
        
        files = [
            {"name": "config.json", "size": "2.5 KB", "type": "json"},
            {"name": "readme.md", "size": "8.1 KB", "type": "markdown"},
            {"name": "script.upy", "size": "4.3 KB", "type": "upy"},
        ]
        
        list_selector = ListSelector(
            files,
            "Recent Files",
            label_func=lambda f: f"{f['name']} ({f['size']})",
            emoji_func=lambda f, i: "📄" if f['type'] == 'json' else "📝" if f['type'] == 'markdown' else "⚙️"
        )
        lines.append(list_selector.render())
        lines.append("")
        lines.append(f"Key hints: {list_selector.get_key_hints()}")
        lines.append("")
        
        # Integration info
        lines.append("─" * 60)
        lines.append("")
        lines.append("🔗 INTEGRATION:")
        lines.append("  • Works with DEVICE MODE command")
        lines.append("  • Compatible with existing keypad_navigator.py")
        lines.append("  • Standardized across all panels")
        lines.append("  • Mode-aware (navigation/selection/editing/menu)")
        lines.append("")
        lines.append("💡 Try: KEYPAD MENU or KEYPAD LIST for focused examples")
        
        return "\n".join(lines)
    
    def _show_menu_example(self) -> str:
        """Show simple menu example."""
        lines = []
        
        lines.append("📋 MENU SELECTOR - Simple String Menus")
        lines.append("=" * 60)
        lines.append("")
        
        # Create sample menu
        menu = MenuSelector(
            items=["🔧 Settings", "📁 Files", "⚙️ Tools", "❓ Help"],
            title="Main Menu"
        )
        
        lines.append(menu.render())
        lines.append("")
        lines.append("Key Mapping:")
        for key, hint in menu.get_key_hints().items():
            lines.append(f"  {key} → {hint}")
        lines.append("")
        
        # Code example
        lines.append("Code Example:")
        lines.append("─" * 60)
        lines.append("from core.ui.selector_base import MenuSelector")
        lines.append("")
        lines.append('menu = MenuSelector(')
        lines.append('    items=["Option 1", "Option 2", "Option 3"],')
        lines.append('    title="My Menu",')
        lines.append('    emojis=["🔧", "📁", "⚙️"]')
        lines.append(')')
        lines.append("")
        lines.append('print(menu.render())')
        lines.append('result = menu.handle_key("1")  # Selects first item')
        
        return "\n".join(lines)
    
    def _show_list_example(self) -> str:
        """Show list selector example."""
        lines = []
        
        lines.append("📂 LIST SELECTOR - Custom Objects with Labels")
        lines.append("=" * 60)
        lines.append("")
        
        # Sample data
        guides = [
            {"category": "water", "title": "Water Purification", "pages": 12},
            {"category": "fire", "title": "Fire Starting", "pages": 8},
            {"category": "shelter", "title": "Shelter Building", "pages": 15},
            {"category": "food", "title": "Wild Edibles", "pages": 20},
            {"category": "medical", "title": "First Aid", "pages": 18},
        ]
        
        # Create list selector
        list_selector = ListSelector(
            items=guides,
            title="Survival Guides",
            label_func=lambda g: f"{g['title']} ({g['pages']} pages)",
            emoji_func=lambda g, i: {
                "water": "💧",
                "fire": "🔥",
                "shelter": "🏕️",
                "food": "🍎",
                "medical": "🏥"
            }.get(g['category'], "📖")
        )
        
        lines.append(list_selector.render())
        lines.append("")
        lines.append("Key Mapping:")
        for key, hint in list_selector.get_key_hints().items():
            lines.append(f"  {key} → {hint}")
        lines.append("")
        
        # Code example
        lines.append("Code Example:")
        lines.append("─" * 60)
        lines.append("from core.ui.selector_base import ListSelector")
        lines.append("")
        lines.append("items = [")
        lines.append('    {"name": "File 1", "size": 100},')
        lines.append('    {"name": "File 2", "size": 200}')
        lines.append("]")
        lines.append("")
        lines.append("selector = ListSelector(")
        lines.append("    items=items,")
        lines.append('    title="Files",')
        lines.append('    label_func=lambda f: f"{f[\'name\']} ({f[\'size\']}KB)",')
        lines.append('    emoji_func=lambda f, i: "📄"')
        lines.append(")")
        lines.append("")
        lines.append('print(selector.render())')
        lines.append('selected = selector.handle_key("1")')
        
        return "\n".join(lines)
    
    def _show_test(self) -> str:
        """Show interactive test info."""
        lines = []
        
        lines.append("🧪 KEYPAD INTERACTIVE TEST")
        lines.append("=" * 60)
        lines.append("")
        lines.append("Status:")
        lines.append(f"  Keypad Enabled: {'✅ Yes' if self.keypad.is_enabled() else '❌ No'}")
        lines.append(f"  Current Mode: {self.keypad.context.mode.value}")
        lines.append("")
        
        # Show key hints for current mode
        hints = self.keypad.get_key_hints()
        lines.append("Current Key Mapping:")
        for key, desc in hints.items():
            lines.append(f"  {key} → {desc}")
        lines.append("")
        
        lines.append("💡 To test keypad input:")
        lines.append("  1. Enable TUI keypad: TUI ENABLE KEYPAD")
        lines.append("  2. Use number keys 0-9 in any uDOS panel")
        lines.append("  3. Check DEVICE STATUS for input mode")
        lines.append("")
        lines.append("📋 Keypad works in these contexts:")
        lines.append("  • CONFIG panels (select settings)")
        lines.append("  • HELP command (select topics)")
        lines.append("  • FILE browser (select files)")
        lines.append("  • GUIDE system (select categories)")
        lines.append("  • WORKFLOW missions (select tasks)")
        
        return "\n".join(lines)
    
    def _show_key_reference(self) -> str:
        """Show complete key reference."""
        lines = []
        
        lines.append("🎮 KEYPAD KEY REFERENCE")
        lines.append("=" * 60)
        lines.append("")
        lines.append("Standard Mappings (All Modes):")
        lines.append("─" * 60)
        lines.append("  8 → Up / Scroll Up")
        lines.append("  2 → Down / Scroll Down")
        lines.append("  4 → Left / Previous")
        lines.append("  6 → Right / Next")
        lines.append("  5 → OK / Select / Confirm")
        lines.append("  7 → Redo")
        lines.append("  9 → Undo")
        lines.append("  1 → Yes")
        lines.append("  3 → No")
        lines.append("  0 → Menu / More Options")
        lines.append("")
        
        lines.append("Selection Mode (Menus & Lists):")
        lines.append("─" * 60)
        lines.append("  1-9 → Select item by number")
        lines.append("  0   → Show more items (if available)")
        lines.append("")
        
        lines.append("Navigation Mode (Browsing):")
        lines.append("─" * 60)
        lines.append("  8 → Scroll up one line")
        lines.append("  2 → Scroll down one line")
        lines.append("  4 → Previous page/item")
        lines.append("  6 → Next page/item")
        lines.append("  5 → Select current item")
        lines.append("")
        
        lines.append("Editing Mode (Text Input):")
        lines.append("─" * 60)
        lines.append("  8 → Previous command (history)")
        lines.append("  2 → Next command (history)")
        lines.append("  4 → Cursor left")
        lines.append("  6 → Cursor right")
        lines.append("  5 → Autocomplete")
        lines.append("  7 → Redo edit")
        lines.append("  9 → Undo edit")
        lines.append("  1 → Accept/confirm")
        lines.append("  3 → Cancel")
        lines.append("  0 → Options menu")
        lines.append("")
        
        lines.append("💡 Mode switches automatically based on context")
        lines.append("💡 Full keyboard still works (arrow keys, etc.)")
        
        return "\n".join(lines)


def create_handler(**kwargs) -> KeypadDemoHandler:
    """Factory function for handler creation."""
    return KeypadDemoHandler(**kwargs)
