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
                'dev_prompt': '⚙️ ',
                'dev_color': Colors.YELLOW if use_colors else '',
                'assist_prompt': '❤️ ',
                'assist_color': Colors.CYAN if use_colors else '',
                'ghost_prompt': '👻 ',  # Demo/sandbox/offline-testing
                'tomb_prompt': '🔒 ',   # Archival local/private only
                'crypt_prompt': '🛜 ',  # Archival with live/networking/sharing
            },
            'science': {
                'regular_prompt': '🌀 ',
                'regular_color': '',
                'dev_prompt': '⚙️ ',
                'dev_color': Colors.YELLOW if use_colors else '',
                'assist_prompt': '❤️ ',
                'assist_color': Colors.CYAN if use_colors else '',
                'ghost_prompt': '👻 ',
                'tomb_prompt': '🔒 ',
                'crypt_prompt': '🛜 ',
            },
            'cyberpunk': {
                'regular_prompt': '🌀 ',
                'regular_color': '',
                'dev_prompt': '⚙️ ',
                'dev_color': Colors.YELLOW if use_colors else '',
                'assist_prompt': '❤️ ',
                'assist_color': Colors.CYAN if use_colors else '',
                'ghost_prompt': '👻 ',
                'tomb_prompt': '🔒 ',
                'crypt_prompt': '🛜 ',
            }
        }

    def get_prompt(
        self,
        is_assist_mode: bool = False,
        panel_name: Optional[str] = None,
        flash: bool = False,
        dev_mode: bool = False,
        ghost_mode: bool = False,
        tomb_mode: bool = False,
        crypt_mode: bool = False,
        for_prompt_toolkit: bool = True
    ) -> str:
        """Generate prompt string. Priority: dev_mode > ghost > tomb > crypt > assist_mode > regular."""
        theme_config = self.themes.get(self.theme, self.themes['dungeon'])
        if dev_mode:
            prompt_text = theme_config['dev_prompt']
        elif ghost_mode:
            prompt_text = theme_config.get('ghost_prompt', '👻 ')
        elif tomb_mode:
            prompt_text = theme_config.get('tomb_prompt', '🔒 ')
        elif crypt_mode:
            prompt_text = theme_config.get('crypt_prompt', '🛜 ')
        elif is_assist_mode:
            prompt_text = theme_config['assist_prompt']
        else:
            prompt_text = theme_config['regular_prompt']

        # Return plain text - let prompt_toolkit handle styling
        return prompt_text

    def get_mode_status(self, dev_mode: bool = False, is_assist_mode: bool = False, ghost_mode: bool = False, tomb_mode: bool = False, crypt_mode: bool = False) -> str:
        """Get mode status string."""
        if dev_mode:
            return f"{Colors.BRIGHT_YELLOW if self.use_colors else ''}⚙️ DEV MODE{Colors.RESET if self.use_colors else ''}"
        elif is_assist_mode:
            return f"{Colors.BRIGHT_CYAN if self.use_colors else ''}❤️ ASSIST MODE{Colors.RESET if self.use_colors else ''}"
        elif ghost_mode:
            return "👻 GHOST MODE (demo/sandbox/offline-testing)"
        elif tomb_mode:
            return "🔒 TOMB MODE (archival local/private)"
        elif crypt_mode:
            return "🛜 CRYPT MODE (archival with networking)"
        else:
            return "🌀 COMMAND MODE"

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


"""
PROMPT MODE REFERENCE (v1.2.24+)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌀 COMMAND MODE (default)
   • Standard user operations
   • Full command access
   • Production environment
   • Priority: Lowest

⚙️ DEV MODE
   • Developer/admin access
   • Extended debugging tools
   • System modification allowed
   • Priority: Highest (overrides all)

❤️ ASSIST MODE
   • AI-powered assistance
   • Context-aware suggestions
   • OK command integration
   • Priority: Medium

👻 GHOST MODE (demo/sandbox/offline-testing only)
   • Isolated testing environment
   • No persistent changes
   • Safe experimentation
   • Network disabled
   • Priority: High (below DEV)

🔒 TOMB MODE (archival local/private only)
   • Read-only archival access
   • Local storage only
   • No network access
   • No sharing capabilities
   • Priority: High (below GHOST)

🛜 CRYPT MODE (archival with live/networking/sharing)
   • Read-write archival access
   • Network enabled for sync
   • Location/beacon/key sharing
   • Collaborative archival work
   • Priority: High (below TOMB)

PRIORITY ORDER:
DEV > GHOST > TOMB > CRYPT > ASSIST > COMMAND

USAGE:
  decorator = PromptDecorator(theme='dungeon')
  prompt = decorator.get_prompt(dev_mode=True)      # ⚙️ 
  prompt = decorator.get_prompt(ghost_mode=True)    # 👻 
  prompt = decorator.get_prompt(tomb_mode=True)     # 🔒 
  prompt = decorator.get_prompt(crypt_mode=True)    # 🛜 
  prompt = decorator.get_prompt(is_assist_mode=True) # ❤️ 
  prompt = decorator.get_prompt()                    # 🌀 
"""
