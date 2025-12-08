"""
TUI Command Handler (v1.2.15)

Manages Terminal User Interface components:
- Keypad navigation (numpad controls)
- Command predictions
- Enhanced pager
- File browser

Commands:
- TUI ENABLE [KEYPAD|PREDICTOR|PAGER|BROWSER|ALL]
- TUI DISABLE [KEYPAD|PREDICTOR|PAGER|BROWSER|ALL]
- TUI STATUS
- TUI TOGGLE KEYPAD
"""

from typing import List, Optional
from core.ui.tui_config import get_tui_config


class TUIHandler:
    """Handler for TUI management commands"""
    
    def __init__(self, tui_controller=None):
        """
        Initialize TUI handler.
        
        Args:
            tui_controller: TUIController instance from main loop
        """
        self.tui = tui_controller
        self.config = get_tui_config()
    
    def handle_command(self, args: List[str]) -> str:
        """
        Route TUI commands.
        
        Args:
            args: Command arguments
            
        Returns:
            Result message
        """
        if not args:
            return self._help()
        
        action = args[0].upper()
        
        if action == 'ENABLE':
            return self._enable(args[1] if len(args) > 1 else 'ALL')
        elif action == 'DISABLE':
            return self._disable(args[1] if len(args) > 1 else 'ALL')
        elif action == 'STATUS':
            return self._status()
        elif action == 'TOGGLE':
            component = args[1].upper() if len(args) > 1 else 'KEYPAD'
            return self._toggle(component)
        elif action == 'HELP':
            return self._help()
        else:
            return f"❌ Unknown TUI action: {action}\n\n{self._help()}"
    
    def _enable(self, component: str) -> str:
        """Enable TUI component"""
        component = component.upper()
        
        if component == 'KEYPAD' or component == 'ALL':
            self.config.set('keypad_enabled', True)
            if self.tui:
                self.tui.keypad.enabled = True
            result = "✅ Keypad navigation enabled\n"
            result += "   8↑ 2↓ 4← 6→ (arrows) | 5✓ (select)\n"
            result += "   7↶ 9↷ (undo/redo) | 1◀ 3▶ (history) | 0☰ (menu)"
            
            if component == 'ALL':
                self.config.set('prediction_enabled', True)
                self.config.set('preserve_scroll', True)
                result += "\n✅ All TUI features enabled"
            
            return result
        
        elif component == 'PREDICTOR':
            self.config.set('prediction_enabled', True)
            return "✅ Command predictor enabled"
        
        elif component == 'PAGER':
            self.config.set('preserve_scroll', True)
            return "✅ Enhanced pager enabled"
        
        elif component == 'BROWSER':
            return "✅ File browser available (use FILE BROWSE command)"
        
        else:
            return f"❌ Unknown component: {component}\n   Valid: KEYPAD, PREDICTOR, PAGER, BROWSER, ALL"
    
    def _disable(self, component: str) -> str:
        """Disable TUI component"""
        component = component.upper()
        
        if component == 'KEYPAD' or component == 'ALL':
            self.config.set('keypad_enabled', False)
            if self.tui:
                self.tui.keypad.enabled = False
            result = "✅ Keypad navigation disabled (numpad keys will type normally)"
            
            if component == 'ALL':
                self.config.set('prediction_enabled', False)
                self.config.set('preserve_scroll', False)
                result += "\n✅ All TUI features disabled"
            
            return result
        
        elif component == 'PREDICTOR':
            self.config.set('prediction_enabled', False)
            return "✅ Command predictor disabled"
        
        elif component == 'PAGER':
            self.config.set('preserve_scroll', False)
            return "✅ Enhanced pager disabled"
        
        else:
            return f"❌ Unknown component: {component}\n   Valid: KEYPAD, PREDICTOR, PAGER, BROWSER, ALL"
    
    def _toggle(self, component: str) -> str:
        """Toggle TUI component on/off"""
        if component == 'KEYPAD':
            current = self.config.get('keypad_enabled', False)
            if current:
                return self._disable('KEYPAD')
            else:
                return self._enable('KEYPAD')
        else:
            return f"❌ Toggle only supports KEYPAD currently"
    
    def _status(self) -> str:
        """Show TUI component status"""
        keypad = "✅ ENABLED" if self.config.get('keypad_enabled', False) else "❌ DISABLED"
        predictor = "✅ ENABLED" if self.config.get('prediction_enabled', True) else "❌ DISABLED"
        pager = "✅ ENABLED" if self.config.get('preserve_scroll', True) else "❌ DISABLED"
        
        result = "╔═══════════════════════════════════════╗\n"
        result += "║       TUI COMPONENT STATUS            ║\n"
        result += "╠═══════════════════════════════════════╣\n"
        result += f"║ Keypad Navigator:  {keypad:15s} ║\n"
        result += f"║ Command Predictor: {predictor:15s} ║\n"
        result += f"║ Enhanced Pager:    {pager:15s} ║\n"
        result += "║ File Browser:      ✅ AVAILABLE       ║\n"
        result += "╚═══════════════════════════════════════╝\n"
        
        if self.config.get('keypad_enabled', False):
            result += "\n📋 Keypad Controls:\n"
            result += "   8↑ 2↓ 4← 6→ = Arrow navigation\n"
            result += "   5 = Select/Confirm\n"
            result += "   7/9 = Undo/Redo\n"
            result += "   1/3 = History back/forward\n"
            result += "   0 = Menu/Toggle"
        else:
            result += "\n💡 Enable keypad: TUI ENABLE KEYPAD"
        
        return result
    
    def _help(self) -> str:
        """Show TUI command help"""
        return """╔════════════════════════════════════════════════════════╗
║                    TUI COMMANDS                        ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  TUI ENABLE [component]   Enable TUI feature          ║
║  TUI DISABLE [component]  Disable TUI feature         ║
║  TUI TOGGLE KEYPAD        Toggle keypad on/off        ║
║  TUI STATUS               Show component status       ║
║  TUI HELP                 Show this help              ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║  Components:                                           ║
║    KEYPAD     - Numpad navigation (8↑ 2↓ 4← 6→ 5✓)   ║
║    PREDICTOR  - Command autocomplete predictions      ║
║    PAGER      - Enhanced output scrolling             ║
║    BROWSER    - File browser (FILE BROWSE command)    ║
║    ALL        - All components                        ║
║                                                        ║
╠════════════════════════════════════════════════════════╣
║  Examples:                                             ║
║    TUI ENABLE KEYPAD     Enable numpad navigation     ║
║    TUI DISABLE ALL       Disable all TUI features     ║
║    TUI STATUS            Check what's enabled         ║
║    TUI TOGGLE KEYPAD     Quick keypad on/off          ║
║                                                        ║
╚════════════════════════════════════════════════════════╝

💡 Tip: Keypad is disabled by default to avoid conflicts with
   number input. Enable it when you want keyboard-only navigation."""
