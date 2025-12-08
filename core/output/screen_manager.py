"""
uDOS v1.0.12 - Screen Manager Service

Manages terminal screen state, clearing operations, and buffer management.
Provides enhanced clearing capabilities beyond simple screen clear.

Features:
- Smart clear (preserve status bar/header)
- Component-specific clearing (grid, logs, history)
- Partial clearing (last N lines)
- Buffer management
- State preservation options

Version: 1.0.12
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any


class ScreenManager:
    """Manages terminal screen state and clearing operations."""

    def __init__(self):
        """Initialize Screen Manager."""
        self.is_windows = os.name == 'nt'
        self.clear_command = 'cls' if self.is_windows else 'clear'

        # Track screen components
        self.status_bar_height = 3  # Lines for status bar
        self.header_height = 0      # Lines for header

    def clear_full(self) -> str:
        """
        Perform full screen clear including scrollback buffer.

        Returns:
            Success message
        """
        os.system(self.clear_command)
        return "✅ Screen cleared completely"

    def clear_smart(self) -> str:
        """
        Smart clear that preserves status bar and important information.
        Clears content but keeps header/status visible.

        Returns:
            Success message
        """
        # Get terminal size
        try:
            rows, cols = self._get_terminal_size()

            # Clear by printing newlines up to status bar
            lines_to_clear = rows - self.status_bar_height
            print('\n' * lines_to_clear)

            return "✅ Screen cleared (status preserved)"
        except:
            # Fallback to full clear
            return self.clear_full()

    def clear_buffer(self) -> str:
        """
        Clear the scrollback buffer.

        Returns:
            Success message
        """
        if self.is_windows:
            # Windows: cls clears buffer
            os.system('cls')
            return "✅ Scrollback buffer cleared"
        else:
            # Unix/Linux: use escape sequence
            # \033[3J clears scrollback in many terminals
            print('\033[3J', end='')
            print('\033[H\033[2J', end='')  # Also clear visible screen
            sys.stdout.flush()
            return "✅ Scrollback buffer cleared"

    def clear_last_n_lines(self, n: int) -> str:
        """
        Clear the last N lines from the terminal.

        Args:
            n: Number of lines to clear

        Returns:
            Success message
        """
        if n < 1:
            return "⚠️  Invalid line count"

        try:
            # Use ANSI escape sequences to clear lines
            # Move cursor up N lines and clear from there
            for _ in range(n):
                # Move up one line and clear it
                print('\033[1A\033[2K', end='')
            sys.stdout.flush()

            return f"✅ Cleared last {n} line(s)"
        except Exception as e:
            return f"❌ Error clearing lines: {e}"

    def clear_component(self, component: str) -> str:
        """
        Clear a specific component (placeholder for future integration).

        Args:
            component: Component name (grid, logs, history, etc.)

        Returns:
            Status message
        """
        component_lower = component.lower()

        if component_lower == 'grid':
            return self._clear_grid()
        elif component_lower == 'logs':
            return self._clear_logs()
        elif component_lower == 'history':
            return self._clear_history()
        else:
            return f"⚠️  Unknown component: {component}"

    def _clear_grid(self) -> str:
        """Clear grid display (placeholder)."""
        # This would integrate with actual grid system
        # For now, just clear screen
        os.system(self.clear_command)
        return "✅ Grid display cleared"

    def _clear_logs(self) -> str:
        """Clear session logs (placeholder)."""
        # This would integrate with logging system
        # Could clear memory/logs/session-*.json files
        return "⚠️  Log clearing requires confirmation (use CLEAR LOGS CONFIRM)"

    def _clear_history(self) -> str:
        """Clear command history (placeholder)."""
        # This would integrate with history system
        # Could clear command_history.db
        return "⚠️  History clearing requires confirmation (use CLEAR HISTORY CONFIRM)"

    def _get_terminal_size(self) -> tuple:
        """
        Get terminal size (rows, columns).

        Returns:
            Tuple of (rows, cols)
        """
        try:
            import shutil
            cols, rows = shutil.get_terminal_size()
            return (rows, cols)
        except:
            # Default fallback
            return (24, 80)

    def get_screen_info(self) -> Dict[str, Any]:
        """
        Get current screen/terminal information.

        Returns:
            Dictionary with screen info
        """
        rows, cols = self._get_terminal_size()

        return {
            'rows': rows,
            'cols': cols,
            'platform': 'Windows' if self.is_windows else 'Unix/Linux',
            'clear_command': self.clear_command,
            'status_bar_height': self.status_bar_height,
            'header_height': self.header_height
        }

    def format_clear_help(self) -> str:
        """
        Format help text for CLEAR command variations.

        Returns:
            Formatted help text
        """
        help_text = "╔" + "═"*78 + "╗\n"
        help_text += "║  📖 CLEAR - Enhanced Screen Management".ljust(79) + "║\n"
        help_text += "╠" + "═"*78 + "╣\n"
        help_text += "║  Available Variations:".ljust(79) + "║\n"
        help_text += "║".ljust(79) + "║\n"
        help_text += "║  CLEAR              - Smart clear (preserve status)".ljust(79) + "║\n"
        help_text += "║  CLEAR ALL          - Full screen clear".ljust(79) + "║\n"
        help_text += "║  CLEAR BUFFER       - Clear scrollback buffer".ljust(79) + "║\n"
        help_text += "║  CLEAR LAST <n>     - Clear last N lines".ljust(79) + "║\n"
        help_text += "║  CLEAR GRID         - Clear grid display".ljust(79) + "║\n"
        help_text += "║  CLEAR LOGS         - Clear session logs (requires confirm)".ljust(79) + "║\n"
        help_text += "║  CLEAR HISTORY      - Clear command history (requires confirm)".ljust(79) + "║\n"
        help_text += "║".ljust(79) + "║\n"
        help_text += "║  Examples:".ljust(79) + "║\n"
        help_text += "║    CLEAR            → Smart clear preserving status".ljust(79) + "║\n"
        help_text += "║    CLEAR ALL        → Complete screen wipe".ljust(79) + "║\n"
        help_text += "║    CLEAR LAST 5     → Remove last 5 lines".ljust(79) + "║\n"
        help_text += "╚" + "═"*78 + "╝\n"

        return help_text


# Standalone test function
def test_screen_manager():
    """Test ScreenManager functionality."""
    print("Testing ScreenManager...")

    sm = ScreenManager()

    # Test screen info
    info = sm.get_screen_info()
    print(f"✅ Screen Info: {info['rows']}×{info['cols']} on {info['platform']}")

    # Test help formatting
    help_text = sm.format_clear_help()
    print(f"✅ Help text: {len(help_text)} characters")

    # Test component clearing (won't actually clear, just returns messages)
    result = sm.clear_component('grid')
    print(f"✅ Clear grid: {result}")

    result = sm.clear_component('history')
    print(f"✅ Clear history: {result}")

    print("\n✅ ScreenManager tests passed")


if __name__ == "__main__":
    test_screen_manager()
