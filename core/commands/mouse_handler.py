"""
MOUSE Command Handler (v1.2.25)

Handles MOUSE command for mouse input configuration and testing.

Commands:
- MOUSE ENABLE - Enable mouse input
- MOUSE DISABLE - Disable mouse input  
- MOUSE STATUS - Show mouse state and statistics
- MOUSE DEMO - Interactive mouse demo
- MOUSE REGION ADD <name> <x1> <y1> <x2> <y2> - Add clickable region
- MOUSE REGION LIST - List all regions
- MOUSE REGION REMOVE <name> - Remove region
- MOUSE RESET - Reset statistics

Part of v1.2.25 Universal Input Device System
"""

from core.commands.base_handler import BaseCommandHandler
from core.input.mouse_handler import MouseHandler, MousePosition, ClickableRegion, MouseEvent


class MouseCommandHandler(BaseCommandHandler):
    """Handler for MOUSE commands."""
    
    def __init__(self, **kwargs):
        """Initialize mouse command handler."""
        super().__init__(**kwargs)
        
        # Get or create mouse handler
        if hasattr(self, 'tui_controller') and self.tui_controller:
            self.mouse_handler = getattr(self.tui_controller, 'mouse_handler', None)
        
        if not hasattr(self, 'mouse_handler') or not self.mouse_handler:
            self.mouse_handler = MouseHandler(
                viewport=kwargs.get('viewport'),
                config=kwargs.get('config')
            )
    
    def handle_command(self, params):
        """
        Handle MOUSE command.
        
        Args:
            params: Command parameters [MOUSE, <subcommand>, ...] or [<subcommand>, ...]
            
        Returns:
            Command output
        """
        if not params:
            return self._show_usage()
        
        # Handle both routing patterns:
        # 1. ["MOUSE", "STATUS"] from direct call
        # 2. ["STATUS"] from module router where command=""
        if params[0].upper() == "MOUSE":
            if len(params) < 2:
                return self._show_usage()
            subcommand = params[1].upper()
            extra_params = params[2:]
        else:
            subcommand = params[0].upper()
            extra_params = params[1:]
        
        if subcommand == "ENABLE":
            return self._enable_mouse()
        elif subcommand == "DISABLE":
            return self._disable_mouse()
        elif subcommand == "STATUS":
            return self._show_status()
        elif subcommand == "DEMO":
            return self._run_demo()
        elif subcommand == "REGION":
            return self._handle_region(extra_params)
        elif subcommand == "RESET":
            return self._reset_stats()
        else:
            return f"❌ Unknown MOUSE subcommand: {subcommand}"
    
    def _show_usage(self):
        """Show MOUSE command usage."""
        return """
🖱️  MOUSE Command Usage
═══════════════════════════════════════════════════════════

Basic Commands:
  MOUSE ENABLE              Enable mouse input
  MOUSE DISABLE             Disable mouse input
  MOUSE STATUS              Show mouse state and statistics
  MOUSE DEMO                Interactive mouse demonstration
  MOUSE RESET               Reset statistics

Region Management:
  MOUSE REGION ADD <name> <x1> <y1> <x2> <y2>
                           Add clickable region
  MOUSE REGION LIST         List all regions
  MOUSE REGION REMOVE <name>
                           Remove region
  MOUSE REGION ENABLE <name>
                           Enable region
  MOUSE REGION DISABLE <name>
                           Disable region

Examples:
  MOUSE ENABLE             # Turn on mouse support
  MOUSE STATUS             # Check current state
  MOUSE DEMO               # Try interactive demo
  MOUSE REGION ADD menu 0 0 20 5
                           # Add clickable menu region
"""
    
    def _enable_mouse(self):
        """Enable mouse input."""
        result = self.mouse_handler.enable()
        
        return f"""
✅ {result}

Mouse features enabled:
  • Click detection (left, right, middle)
  • Double-click detection
  • Drag and drop support
  • Scroll wheel events
  • Clickable regions
  • Position tracking

Use MOUSE DEMO to test mouse input
"""
    
    def _disable_mouse(self):
        """Disable mouse input."""
        result = self.mouse_handler.disable()
        return f"✅ {result}"
    
    def _show_status(self):
        """Show mouse status and statistics."""
        stats = self.mouse_handler.get_stats()
        
        status = "🟢 Enabled" if stats['enabled'] else "🔴 Disabled"
        drag_status = "🎯 Dragging" if stats['is_dragging'] else "⚪ Idle"
        
        output = [
            "\n🖱️  Mouse Status",
            "═" * 60,
            f"Status:          {status}",
            f"Current State:   {drag_status}",
            f"Position:        {stats['current_position']}",
            f"Regions:         {stats['active_regions']}/{stats['regions']} active",
            "",
            "📊 Statistics:",
            f"  Clicks:        {stats['statistics']['clicks']}",
            f"  Double-clicks: {stats['statistics']['double_clicks']}",
            f"  Drags:         {stats['statistics']['drags']}",
            f"  Scrolls:       {stats['statistics']['scrolls']}",
            f"  Moves:         {stats['statistics']['moves']}",
        ]
        
        # List regions
        if self.mouse_handler.regions:
            output.append("\n📍 Clickable Regions:")
            for region in self.mouse_handler.regions:
                status_icon = "✓" if region.enabled else "✗"
                output.append(f"  [{status_icon}] {region}")
        
        return "\n".join(output)
    
    def _run_demo(self):
        """Run interactive mouse demo."""
        if not self.mouse_handler.is_enabled():
            return """
❌ Mouse input is disabled

Enable it first with: MOUSE ENABLE
"""
        
        return """
🖱️  Mouse Input Demo
═══════════════════════════════════════════════════════════

Mouse input is now active! Try:

  🖱️  Left Click:       Standard selection
  🖱️  Right Click:      Context menu (if supported)
  🖱️  Double Click:     Quick action
  🖱️  Drag:             Click and hold, then move
  🖱️  Scroll:           Mouse wheel up/down
  🖱️  Hover:            Move cursor over regions

Current active regions: {regions}

Move your mouse around and click to test!
Press Ctrl+C to exit demo mode.

Note: Mouse events will be logged in real-time.
Check statistics with: MOUSE STATUS
""".format(regions=len(self.mouse_handler.regions))
    
    def _handle_region(self, params):
        """Handle MOUSE REGION subcommands."""
        if not params:
            return "❌ Missing REGION subcommand (ADD, LIST, REMOVE, ENABLE, DISABLE)"
        
        action = params[0].upper()
        
        if action == "ADD":
            return self._add_region(params[1:])
        elif action == "LIST":
            return self._list_regions()
        elif action == "REMOVE":
            return self._remove_region(params[1:])
        elif action == "ENABLE":
            return self._enable_region(params[1:])
        elif action == "DISABLE":
            return self._disable_region(params[1:])
        else:
            return f"❌ Unknown REGION action: {action}"
    
    def _add_region(self, params):
        """Add a clickable region."""
        if len(params) < 5:
            return """
❌ Usage: MOUSE REGION ADD <name> <x1> <y1> <x2> <y2>

Example: MOUSE REGION ADD menu 0 0 20 5
"""
        
        try:
            name = params[0]
            x1 = int(params[1])
            y1 = int(params[2])
            x2 = int(params[3])
            y2 = int(params[4])
            
            # Check if region already exists
            if self.mouse_handler.get_region(name):
                return f"❌ Region '{name}' already exists"
            
            # Create dummy callback
            def region_callback(event: MouseEvent):
                print(f"🖱️  Clicked region '{name}' at {event.position}")
            
            region = ClickableRegion(
                name=name,
                x1=x1, y1=y1,
                x2=x2, y2=y2,
                callback=region_callback
            )
            
            self.mouse_handler.add_region(region)
            
            return f"""
✅ Added clickable region: {region}

Region will trigger callback when clicked.
Test it with: MOUSE DEMO
"""
        except ValueError:
            return "❌ Invalid coordinates (must be integers)"
    
    def _list_regions(self):
        """List all clickable regions."""
        if not self.mouse_handler.regions:
            return "📍 No clickable regions defined"
        
        output = ["\n📍 Clickable Regions", "═" * 60]
        
        for i, region in enumerate(self.mouse_handler.regions, 1):
            status = "✓ Enabled" if region.enabled else "✗ Disabled"
            output.append(f"{i}. {region.name:20s} {status}")
            output.append(f"   Area: [{region.x1},{region.y1}] to [{region.x2},{region.y2}]")
            output.append(f"   Size: {region.x2 - region.x1 + 1}×{region.y2 - region.y1 + 1}")
        
        return "\n".join(output)
    
    def _remove_region(self, params):
        """Remove a clickable region."""
        if not params:
            return "❌ Usage: MOUSE REGION REMOVE <name>"
        
        name = params[0]
        if self.mouse_handler.remove_region(name):
            return f"✅ Removed region: {name}"
        else:
            return f"❌ Region not found: {name}"
    
    def _enable_region(self, params):
        """Enable a clickable region."""
        if not params:
            return "❌ Usage: MOUSE REGION ENABLE <name>"
        
        name = params[0]
        region = self.mouse_handler.get_region(name)
        if region:
            self.mouse_handler.enable_region(name)
            return f"✅ Enabled region: {name}"
        else:
            return f"❌ Region not found: {name}"
    
    def _disable_region(self, params):
        """Disable a clickable region."""
        if not params:
            return "❌ Usage: MOUSE REGION DISABLE <name>"
        
        name = params[0]
        region = self.mouse_handler.get_region(name)
        if region:
            self.mouse_handler.disable_region(name)
            return f"✅ Disabled region: {name}"
        else:
            return f"❌ Region not found: {name}"
    
    def _reset_stats(self):
        """Reset mouse statistics."""
        self.mouse_handler.reset_stats()
        return "✅ Mouse statistics reset"
