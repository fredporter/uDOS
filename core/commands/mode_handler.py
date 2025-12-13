"""
uDOS v1.3 - Mode Handler
Handles prompt mode switching: COMMAND, DEV, ASSIST, GHOST, TOMB, CRYPT.
"""

from .base_handler import BaseCommandHandler
from .handler_utils import HandlerUtils


class ModeCommandHandler(BaseCommandHandler):
    """Handle prompt mode switching commands."""

    @property
    def config_manager(self):
        """Get shared config manager instance."""
        return HandlerUtils.get_config()

    def handle(self, command, params):
        """Route mode commands."""
        if command == 'MODE':
            return self.handle_mode(params)
        elif command == 'GHOST':
            return self.handle_ghost(params)
        elif command == 'TOMB':
            return self.handle_tomb(params)
        elif command == 'CRYPT':
            return self.handle_crypt(params)
        return f"Unknown mode command: {command}"

    def handle_mode(self, params):
        """
        MODE command - Show or change prompt mode.
        Usage:
          MODE               - Show current mode
          MODE STATUS        - Show mode details
          MODE COMMAND       - Switch to command mode (🌀)
          MODE DEV           - Switch to dev mode (⚙️)
          MODE ASSIST        - Switch to assist mode (❤️)
          MODE GHOST         - Switch to ghost mode (👻)
          MODE TOMB          - Switch to tomb mode (🔒)
          MODE CRYPT         - Switch to crypt mode (🛜)
        """
        if not params:
            # Show current mode
            mode = self.config_manager.get('prompt_mode', 'command')
            symbols = {
                'command': '🌀',
                'dev': '⚙️',
                'assist': '❤️',
                'ghost': '👻',
                'tomb': '🔒',
                'crypt': '🛜'
            }
            symbol = symbols.get(mode, '🌀')
            return f"{symbol} Current mode: {mode.upper()}"

        subcommand = params[0].upper()

        if subcommand == 'STATUS':
            return self._show_mode_status()

        # Mode switching
        mode_map = {
            'COMMAND': 'command',
            'DEV': 'dev',
            'ASSIST': 'assist',
            'GHOST': 'ghost',
            'TOMB': 'tomb',
            'CRYPT': 'crypt'
        }

        if subcommand in mode_map:
            new_mode = mode_map[subcommand]
            self.config_manager.set('prompt_mode', new_mode)
            symbols = {
                'command': '🌀',
                'dev': '⚙️',
                'assist': '❤️',
                'ghost': '👻',
                'tomb': '🔒',
                'crypt': '🛜'
            }
            symbol = symbols[new_mode]
            return f"{symbol} Switched to {subcommand} mode"

        return f"Unknown MODE subcommand: {subcommand}"

    def _show_mode_status(self):
        """Show detailed mode information."""
        mode = self.config_manager.get('prompt_mode', 'command')
        
        modes_info = {
            'command': ('🌀', 'COMMAND', 'Standard operations'),
            'dev': ('⚙️', 'DEV', 'Developer/admin access'),
            'assist': ('❤️', 'ASSIST', 'AI-powered assistance'),
            'ghost': ('👻', 'GHOST', 'Demo/sandbox/offline-testing'),
            'tomb': ('🔒', 'TOMB', 'Archival local/private'),
            'crypt': ('🛜', 'CRYPT', 'Archival with networking')
        }
        
        output = ["MODE STATUS\n"]
        for mode_key, (symbol, name, desc) in modes_info.items():
            marker = '●' if mode == mode_key else '○'
            output.append(f"  {marker} {symbol} {name:8} - {desc}")
        
        output.append("\nPriority: DEV > GHOST > TOMB > CRYPT > ASSIST > COMMAND")
        return '\n'.join(output)

    def handle_ghost(self, params):
        """GHOST - Switch to ghost mode (demo/sandbox/offline-testing)."""
        self.config_manager.set('prompt_mode', 'ghost')
        return "👻 Switched to GHOST mode (demo/sandbox/offline-testing)"

    def handle_tomb(self, params):
        """TOMB - Switch to tomb mode (archival local/private)."""
        self.config_manager.set('prompt_mode', 'tomb')
        return "🔒 Switched to TOMB mode (archival local/private)"

    def handle_crypt(self, params):
        """CRYPT - Switch to crypt mode (archival with networking)."""
        self.config_manager.set('prompt_mode', 'crypt')
        return "🛜 Switched to CRYPT mode (archival with networking)"
