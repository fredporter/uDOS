"""
uDOS v1.2.22 - Prompt Decorator
Themed prompt strings with mode indicators.
"""

from typing import Optional


class Colors:
    """ANSI color codes."""
    RESET = '\033[0m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_CYAN = '\033[96m'


class PromptDecorator:
    """Themed prompt generator."""

    def __init__(self, theme: str = 'dungeon', use_colors: bool = True):
        self.theme = theme
        self.use_colors = use_colors
        self.themes = {
            'dungeon': {
                'regular_prompt': '🌀 ',
                'regular_color': '',  # No color for regular
                'dev_prompt': '🔧 ',
                'dev_color': Colors.YELLOW if use_colors else '',
                'assist_prompt': '🤖 ',
                'assist_color': Colors.CYAN if use_colors else '',
            },
            'science': {
                'regular_prompt': '🌀 ',
                'regular_color': '',
                'dev_prompt': '🔬 ',
                'dev_color': Colors.YELLOW if use_colors else '',
                'assist_prompt': '🤖 ',
                'assist_color': Colors.CYAN if use_colors else '',
            },
            'cyberpunk': {
                'regular_prompt': '🌀 ',
                'regular_color': '',
                'dev_prompt': '⚡ ',
                'dev_color': Colors.YELLOW if use_colors else '',
                'assist_prompt': '🤖 ',
                'assist_color': Colors.CYAN if use_colors else '',
            }
        }

    def get_prompt(
        self,
        is_assist_mode: bool = False,
        panel_name: Optional[str] = None,
        flash: bool = False,
        dev_mode: bool = False,
        for_prompt_toolkit: bool = True
    ) -> str:
        """Generate prompt string. Priority: dev_mode > assist_mode > regular."""
        theme_config = self.themes.get(self.theme, self.themes['dungeon'])
        if dev_mode:
            prompt_text = theme_config['dev_prompt']
        elif is_assist_mode:
            prompt_text = theme_config['assist_prompt']
        else:
            prompt_text = theme_config['regular_prompt']

        # Return plain text - let prompt_toolkit handle styling
        return prompt_text

    def get_mode_status(self, dev_mode: bool = False, is_assist_mode: bool = False) -> str:
        """Get mode status string."""
        if dev_mode:
            return f"{Colors.BRIGHT_YELLOW if self.use_colors else ''}🔧 DEV MODE{Colors.RESET if self.use_colors else ''}"
        elif is_assist_mode:
            return f"{Colors.BRIGHT_CYAN if self.use_colors else ''}🤖 ASSIST MODE{Colors.RESET if self.use_colors else ''}"
        else:
            return "› REGULAR MODE"

    def get_context_hint(self, last_command: Optional[str] = None, panel_content_length: int = 0) -> Optional[str]:
        """Get contextual hint (currently disabled)."""
        return None


# Global instance
_prompt_decorator = None


def get_prompt_decorator(theme: str = 'dungeon') -> PromptDecorator:
    """Get or create global prompt decorator"""
    global _prompt_decorator
    if _prompt_decorator is None:
        _prompt_decorator = PromptDecorator(theme)
    return _prompt_decorator
