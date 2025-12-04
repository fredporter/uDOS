"""
uDOS v1.2.4 - Prompt Decorator
Generates themed prompt strings and context hints

Provides:
- Dynamic prompt generation with assist mode
- Panel-aware prompts
- Context hints for user guidance
- Visual mode indicators (v1.2.4: regular/dev/assist)
- Color-coded prompts with distinct symbols

v1.2.4 Changes:
- Added ANSI color codes for mode distinction
- Enhanced symbols: › (regular), 🔧 (dev), 🤖 (assist)
- Color scheme: default (regular), yellow (dev), cyan (assist)
"""

from typing import Optional


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal styling"""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Standard colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class PromptDecorator:
    """Generates themed prompt strings for the REPL"""

    def __init__(self, theme: str = 'dungeon', use_colors: bool = True):
        """
        Initialize with theme.

        Args:
            theme: Theme name (dungeon, science, cyberpunk)
            use_colors: Whether to use ANSI colors (disable for plain terminals)
        """
        self.theme = theme
        self.use_colors = use_colors

        # v1.2.4: Enhanced theme configuration with colors and symbols
        self.themes = {
            'dungeon': {
                'regular_prompt': '› ',
                'regular_color': Colors.RESET,
                'dev_prompt': '🔧 DEV› ',
                'dev_color': Colors.BRIGHT_YELLOW,
                'assist_prompt': '🤖 OK› ',
                'assist_color': Colors.BRIGHT_CYAN,
            },
            'science': {
                'regular_prompt': '⚗️› ',
                'regular_color': Colors.RESET,
                'dev_prompt': '🔧 LAB› ',
                'dev_color': Colors.BRIGHT_YELLOW,
                'assist_prompt': '🤖 AI› ',
                'assist_color': Colors.BRIGHT_CYAN,
            },
            'cyberpunk': {
                'regular_prompt': '🔮› ',
                'regular_color': Colors.RESET,
                'dev_prompt': '🔧 SYS› ',
                'dev_color': Colors.BRIGHT_YELLOW,
                'assist_prompt': '🤖 NET› ',
                'assist_color': Colors.BRIGHT_CYAN,
            }
        }

    def get_prompt(
        self,
        is_assist_mode: bool = False,
        panel_name: Optional[str] = None,  # Deprecated but kept for compatibility
        flash: bool = False,
        dev_mode: bool = False
    ) -> str:
        """
        Generate prompt string with visual mode indicators.

        Args:
            is_assist_mode: Whether in assist mode
            panel_name: DEPRECATED - no longer used (kept for compatibility)
            flash: Whether to add flash effect (deprecated, kept for compatibility)
            dev_mode: Whether DEV MODE is active

        Returns:
            Formatted prompt string with ANSI colors and mode symbols

        Mode Priority (highest to lowest):
            1. DEV MODE (🔧 yellow) - Security-elevated operations
            2. ASSIST MODE (🤖 cyan) - AI assistant active
            3. REGULAR MODE (› default) - Normal operations
        """
        theme_config = self.themes.get(self.theme, self.themes['dungeon'])

        # Determine mode and get prompt configuration
        # Priority: dev_mode > assist_mode > regular
        if dev_mode:
            prompt_text = theme_config['dev_prompt']
            color = theme_config['dev_color'] if self.use_colors else ''
        elif is_assist_mode:
            prompt_text = theme_config['assist_prompt']
            color = theme_config['assist_color'] if self.use_colors else ''
        else:
            prompt_text = theme_config['regular_prompt']
            color = theme_config['regular_color'] if self.use_colors else ''

        # Apply color and reset
        if self.use_colors:
            return f"{color}{prompt_text}{Colors.RESET}"
        else:
            return prompt_text

    def get_mode_status(self, dev_mode: bool = False, is_assist_mode: bool = False) -> str:
        """
        Get current mode status string for display.

        Args:
            dev_mode: Whether DEV MODE is active
            is_assist_mode: Whether ASSIST MODE is active

        Returns:
            Status string describing current mode
        """
        if dev_mode:
            return f"{Colors.BRIGHT_YELLOW if self.use_colors else ''}🔧 DEV MODE{Colors.RESET if self.use_colors else ''}"
        elif is_assist_mode:
            return f"{Colors.BRIGHT_CYAN if self.use_colors else ''}🤖 ASSIST MODE{Colors.RESET if self.use_colors else ''}"
        else:
            return "› REGULAR MODE"

    def get_context_hint(
        self,
        last_command: Optional[str] = None,
        panel_content_length: int = 0
    ) -> Optional[str]:
        """
        Get contextual hints for user.

        Args:
            last_command: Last command executed
            panel_content_length: Length of current panel content

        Returns:
            Hint string or None
        """
        # Could be enhanced with more intelligent hints
        # For now, keep it minimal to avoid clutter
        return None


# Global instance
_prompt_decorator = None


def get_prompt_decorator(theme: str = 'dungeon') -> PromptDecorator:
    """Get or create global prompt decorator"""
    global _prompt_decorator
    if _prompt_decorator is None:
        _prompt_decorator = PromptDecorator(theme)
    return _prompt_decorator
