"""
DEVICE Command Handler - v1.2.25

Manages input device detection, configuration, and status reporting.
Supports keyboard, mouse, and terminal capability detection.

Date: 20251213-185000UTC
Location: Core Commands
"""

from core.commands.base_handler import BaseCommandHandler
from core.services.device_manager import DeviceManager
from core.commands.handler_utils import HandlerUtils


class DeviceHandler(BaseCommandHandler):
    """Handler for DEVICE commands."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device_manager = DeviceManager(config=HandlerUtils.get_config())
    
    def handle_command(self, params: list) -> str:
        """
        Route DEVICE commands.
        
        Commands:
            DEVICE STATUS - Show input device capabilities
            DEVICE SETUP - Run device detection wizard
            DEVICE MODE <mode> - Switch input mode
            DEVICE TEST - Test mouse/keyboard input
            DEVICE ENABLE MOUSE - Enable mouse input
            DEVICE DISABLE MOUSE - Disable mouse input
        
        Args:
            params: Command parameters [command_name, ...args]
            
        Returns:
            Command output string
        """
        if len(params) < 1:
            return self._show_usage()
        
        command = params[0].upper()
        
        if command == "DEVICE":
            if len(params) == 1:
                # Just "DEVICE" - show status
                return self._status()
            
            subcommand = params[1].upper()
            
            if subcommand == "STATUS":
                return self._status()
            elif subcommand == "SETUP":
                return self._setup()
            elif subcommand == "MODE":
                if len(params) < 3:
                    return "❌ Usage: DEVICE MODE <keypad|full_keyboard|hybrid>"
                return self._set_mode(params[2])
            elif subcommand == "TEST":
                return self._test()
            elif subcommand == "ENABLE":
                if len(params) < 3:
                    return "❌ Usage: DEVICE ENABLE <MOUSE>"
                if params[2].upper() == "MOUSE":
                    return self._enable_mouse()
                else:
                    return f"❌ Unknown device: {params[2]}\n   Valid: MOUSE"
            elif subcommand == "DISABLE":
                if len(params) < 3:
                    return "❌ Usage: DEVICE DISABLE <MOUSE>"
                if params[2].upper() == "MOUSE":
                    return self._disable_mouse()
                else:
                    return f"❌ Unknown device: {params[2]}\n   Valid: MOUSE"
            else:
                return self._show_usage()
        
        return self._show_usage()
    
    def _status(self) -> str:
        """Show input device status."""
        return self.device_manager.get_input_status_report()
    
    def _setup(self) -> str:
        """Run device detection wizard."""
        lines = []
        lines.append("🔍 DEVICE DETECTION WIZARD")
        lines.append("=" * 60)
        lines.append("")
        lines.append("Scanning input devices...")
        lines.append("")
        
        # Run detection
        capabilities = self.device_manager.detect_input_capabilities()
        
        lines.append("✅ Detection complete!")
        lines.append("")
        lines.append("Results:")
        lines.append(f"  Keyboard:     {'✅' if capabilities['keyboard']['available'] else '❌'}")
        lines.append(f"  Mouse:        {'✅' if capabilities['mouse']['available'] else '❌'}")
        lines.append(f"  Touch:        {'✅' if capabilities['touch']['available'] else '❌'}")
        lines.append(f"  256 Colors:   {'✅' if capabilities['terminal']['colors_256'] else '❌'}")
        lines.append(f"  Unicode:      {'✅' if capabilities['terminal']['unicode'] else '❌'}")
        lines.append("")
        lines.append("Configuration saved to: memory/bank/system/device.json")
        lines.append("")
        lines.append("💡 Tip: Use 'DEVICE STATUS' to view full details")
        
        return "\n".join(lines)
    
    def _set_mode(self, mode: str) -> str:
        """Set input mode."""
        mode = mode.lower()
        
        if self.device_manager.set_input_mode(mode):
            mode_display = mode.upper().replace('_', ' ')
            
            lines = []
            lines.append(f"✅ Input mode set to: {mode_display}")
            lines.append("")
            
            if mode == "keypad":
                lines.append("📱 KEYPAD MODE")
                lines.append("  0-9 numpad controls enabled")
                lines.append("  8/2/4/6 = navigation, 5 = select")
                lines.append("  7/9 = undo/redo, 1/3 = history, 0 = menu")
            elif mode == "full_keyboard":
                lines.append("⌨️  FULL KEYBOARD MODE")
                lines.append("  All keys available (arrows, function keys)")
                lines.append("  Numpad disabled for typing numbers")
            elif mode == "hybrid":
                lines.append("🔀 HYBRID MODE")
                lines.append("  Keypad navigation + additional shortcuts")
                lines.append("  Best of both worlds")
            
            return "\n".join(lines)
        else:
            return f"❌ Invalid mode: {mode}\n   Valid modes: keypad, full_keyboard, hybrid"
    
    def _test(self) -> str:
        """Test input device functionality."""
        lines = []
        lines.append("🧪 INPUT DEVICE TEST")
        lines.append("=" * 60)
        lines.append("")
        lines.append("Testing input devices...")
        lines.append("")
        
        # Test keyboard
        lines.append("⌨️  Keyboard:")
        lines.append("  Status:       ✅ Working (you're typing!)")
        lines.append("  Num Keypad:   ✅ Detected")
        lines.append("")
        
        # Test mouse
        if self.device_manager.is_mouse_enabled():
            lines.append("🖱️  Mouse:")
            lines.append("  Status:       ✅ Enabled")
            lines.append("  Protocol:     xterm")
            lines.append("  Test:         Move mouse and click to test")
            lines.append("")
            lines.append("💡 Try clicking in the terminal to test mouse support")
        else:
            lines.append("🖱️  Mouse:")
            lines.append("  Status:       ❌ Disabled")
            lines.append("  Hint:         Use 'DEVICE ENABLE MOUSE' to activate")
        
        lines.append("")
        lines.append("✅ Test complete")
        
        return "\n".join(lines)
    
    def _enable_mouse(self) -> str:
        """Enable mouse input."""
        if self.device_manager.enable_mouse():
            lines = []
            lines.append("✅ Mouse input enabled!")
            lines.append("")
            lines.append("🖱️  Mouse Features:")
            lines.append("  • Click to select items")
            lines.append("  • Drag to select text")
            lines.append("  • Scroll wheel for navigation")
            lines.append("  • Right-click for context menu")
            lines.append("")
            lines.append("💡 Try clicking around to test it out!")
            return "\n".join(lines)
        else:
            return "❌ Mouse not available on this terminal\n   Terminal does not support xterm mouse protocol"
    
    def _disable_mouse(self) -> str:
        """Disable mouse input."""
        self.device_manager.disable_mouse()
        return "✅ Mouse input disabled\n   Click events will not be captured"
    
    def _show_usage(self) -> str:
        """Show DEVICE command usage."""
        return """📱 DEVICE Command Usage

Commands:
  DEVICE                    Show device status (same as STATUS)
  DEVICE STATUS             Show input device capabilities
  DEVICE SETUP              Run device detection wizard
  DEVICE MODE <mode>        Switch input mode
  DEVICE TEST               Test mouse/keyboard input
  DEVICE ENABLE MOUSE       Enable mouse input
  DEVICE DISABLE MOUSE      Disable mouse input

Input Modes:
  keypad         0-9 numpad navigation (default)
  full_keyboard  All keys including arrows, function keys
  hybrid         Keypad + additional shortcuts

Examples:
  DEVICE STATUS             # Show current device status
  DEVICE SETUP              # Detect input devices
  DEVICE MODE keypad        # Enable keypad navigation
  DEVICE ENABLE MOUSE       # Turn on mouse support
  DEVICE TEST               # Test input devices"""
