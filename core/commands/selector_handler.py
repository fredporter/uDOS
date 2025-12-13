"""
SELECTOR Command Handler (v1.2.25)

Demonstrates and tests the unified selector framework.

Commands:
- SELECTOR DEMO - Interactive demonstration
- SELECTOR TEST <mode> - Test specific selection mode
- SELECTOR STATUS - Show selector information

Part of v1.2.25 Universal Input Device System - Week 4
"""

from core.commands.base_handler import BaseCommandHandler
from core.ui.selector_framework import (
    SelectorFramework, SelectableItem, SelectorConfig,
    SelectionMode, NavigationMode
)


class SelectorCommandHandler(BaseCommandHandler):
    """Handler for SELECTOR commands."""
    
    def __init__(self, **kwargs):
        """Initialize selector command handler."""
        super().__init__(**kwargs)
        self.selector = None
    
    def handle_command(self, params):
        """
        Handle SELECTOR command.
        
        Args:
            params: Command parameters
            
        Returns:
            Command output
        """
        if not params:
            return self._show_usage()
        
        # Handle both routing patterns
        if params[0].upper() == "SELECTOR":
            if len(params) < 2:
                return self._show_usage()
            subcommand = params[1].upper()
            extra_params = params[2:]
        else:
            subcommand = params[0].upper()
            extra_params = params[1:]
        
        if subcommand == "DEMO":
            return self._run_demo()
        elif subcommand == "TEST":
            mode = extra_params[0].lower() if extra_params else "single"
            return self._run_test(mode)
        elif subcommand == "STATUS":
            return self._show_status()
        else:
            return f"❌ Unknown SELECTOR subcommand: {subcommand}"
    
    def _show_usage(self):
        """Show SELECTOR command usage."""
        return """
📋 SELECTOR Command Usage
═══════════════════════════════════════════════════════════

Commands:
  SELECTOR DEMO             Interactive demonstration
  SELECTOR TEST <mode>      Test specific selection mode
  SELECTOR STATUS           Show selector information

Selection Modes:
  single                    One item at a time (default)
  multi                     Multiple items (checkboxes)
  toggle                    Toggle states on/off
  none                      Display only (no selection)

Navigation:
  8 ↑                       Move up
  2 ↓                       Move down
  5 ⏎                       Select/Confirm
  1-9                       Select by number
  4 ←                       Previous page
  6 →                       Next page

Examples:
  SELECTOR DEMO             # Show all selector types
  SELECTOR TEST single      # Test single-select
  SELECTOR TEST multi       # Test multi-select
  SELECTOR STATUS           # Show statistics
"""
    
    def _run_demo(self):
        """Run interactive selector demonstration."""
        output = [
            "\n📋 Selector Framework Demo",
            "═" * 60,
            "",
            "🔹 Single Selection Mode:",
            self._demo_single_select(),
            "",
            "🔹 Multi-Selection Mode:",
            self._demo_multi_select(),
            "",
            "🔹 Toggle Mode:",
            self._demo_toggle_mode(),
            "",
            "🔹 Number Selection:",
            "  Press 1-9 to select items directly",
            "  ▶ Quick selection without navigation",
            "",
            "🔹 Pagination:",
            "  Press 4 (←) for previous page",
            "  Press 6 (→) for next page",
            "  ▶ Automatic when items > page_size",
            "",
            "🔹 Search/Filter:",
            "  Type to filter items by text",
            "  ▶ Real-time filtering of visible items",
            "",
            "✅ Framework Features:",
            "  • Consistent navigation across all components",
            "  • Keypad and mouse support",
            "  • Visual feedback (highlighting, icons)",
            "  • Pagination for long lists",
            "  • Multi-select with checkboxes",
            "  • Search and filter capability",
        ]
        
        return "\n".join(output)
    
    def _demo_single_select(self):
        """Demonstrate single selection mode."""
        config = SelectorConfig(mode=SelectionMode.SINGLE)
        selector = SelectorFramework(config)
        
        items = [
            SelectableItem("opt1", "Option 1", icon="📄"),
            SelectableItem("opt2", "Option 2", icon="📁"),
            SelectableItem("opt3", "Option 3", icon="🔧", selected=True),
        ]
        selector.set_items(items)
        
        lines = selector.get_display_lines()
        return "\n".join(f"  {line}" for line in lines)
    
    def _demo_multi_select(self):
        """Demonstrate multi-selection mode."""
        config = SelectorConfig(mode=SelectionMode.MULTI)
        selector = SelectorFramework(config)
        
        items = [
            SelectableItem("file1", "document.txt", icon="📄", selected=True),
            SelectableItem("file2", "image.png", icon="🖼️", selected=True),
            SelectableItem("file3", "script.py", icon="🐍"),
        ]
        selector.set_items(items)
        
        lines = selector.get_display_lines()
        return "\n".join(f"  {line}" for line in lines)
    
    def _demo_toggle_mode(self):
        """Demonstrate toggle mode."""
        config = SelectorConfig(mode=SelectionMode.TOGGLE)
        selector = SelectorFramework(config)
        
        items = [
            SelectableItem("feat1", "Mouse Input", icon="🖱️", selected=True),
            SelectableItem("feat2", "Keypad Navigation", icon="🎮", selected=True),
            SelectableItem("feat3", "Voice Commands", icon="🎤"),
        ]
        selector.set_items(items)
        
        lines = selector.get_display_lines()
        return "\n".join(f"  {line}" for line in lines)
    
    def _run_test(self, mode: str):
        """Run interactive test of specific mode."""
        # Map mode strings to enums
        mode_map = {
            'single': SelectionMode.SINGLE,
            'multi': SelectionMode.MULTI,
            'toggle': SelectionMode.TOGGLE,
            'none': SelectionMode.NONE
        }
        
        if mode not in mode_map:
            return f"❌ Unknown mode: {mode}\nUse: single, multi, toggle, none"
        
        config = SelectorConfig(mode=mode_map[mode])
        selector = SelectorFramework(config)
        
        # Create test items
        items = [
            SelectableItem(f"item{i}", f"Item {i}", icon="📦")
            for i in range(1, 16)
        ]
        selector.set_items(items)
        
        output = [
            f"\n🧪 Testing {mode.upper()} Selection Mode",
            "═" * 60,
            "",
            "Test Items (15 total, page size: 10):",
        ]
        
        # Show first page
        lines = selector.get_display_lines()
        output.extend(f"  {line}" for line in lines)
        
        output.extend([
            "",
            "Navigation:",
            "  8 ↑     - Move up",
            "  2 ↓     - Move down",
            "  5 ⏎     - Select item",
            "  1-9     - Select by number",
            "  4 ←     - Previous page",
            "  6 →     - Next page",
            "",
            f"Mode: {mode}",
            f"Total items: {len(items)}",
            f"Page size: {selector.page_size}",
        ])
        
        return "\n".join(output)
    
    def _show_status(self):
        """Show selector framework status."""
        if not self.selector:
            return """
📋 Selector Framework Status
═══════════════════════════════════════════════════════════

Status: No active selector

The selector framework provides:
  • Unified selection API across all TUI components
  • Keypad navigation (8↑ 2↓ 4← 6→ 5=select)
  • Mouse click support
  • Visual feedback and highlighting
  • Pagination for long lists
  • Multi-select with checkboxes
  • Search and filter capability

Components using selector:
  • File browsers (memory/ucode, knowledge/)
  • Configuration panels (CONFIG, OK, TUI)
  • Command history and logs
  • Menu systems
  • List displays

Use SELECTOR DEMO to see examples
"""
        
        stats = self.selector.get_stats()
        
        return f"""
📋 Selector Framework Status
═══════════════════════════════════════════════════════════

Active Selector: {self.selector.config.mode.value} mode

Statistics:
  Total items:    {stats['total_items']}
  Visible items:  {stats['visible_items']}
  Selected items: {stats['selected_items']}
  Current index:  {stats['current_index']}
  Current page:   {stats['page'] + 1}
  Search active:  {stats['search_active']}

Configuration:
  Mode:           {self.selector.config.mode.value}
  Navigation:     {self.selector.config.navigation.value}
  Wrap around:    {self.selector.config.wrap_around}
  Show numbers:   {self.selector.config.show_numbers}
  Page size:      {self.selector.config.page_size}
  Mouse enabled:  {self.selector.config.enable_mouse}
"""
