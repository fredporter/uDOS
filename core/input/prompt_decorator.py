"""
uDOS v1.0.31 - Prompt Decorator
Generates themed prompt strings and context hints

Provides:
- Dynamic prompt generation with assist mode
- Panel-aware prompts
- Context hints for user guidance
"""

from typing import Optional


class PromptDecorator:
    """Generates themed prompt strings for the REPL"""

    def __init__(self, theme: str = 'dungeon'):
        """Initialize with theme"""
        self.theme = theme
        self.themes = {
            'dungeon': {
                'assist_prompt': '🤖 OK> ',
                'normal_prompt': '🌀> ',
            },
            'science': {
                'assist_prompt': '🤖 OK> ',
                'normal_prompt': '⚗️> ',
            },
            'cyberpunk': {
                'assist_prompt': '🤖 OK> ',
                'normal_prompt': '🔮> ',
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
        Generate prompt string.

        Args:
            is_assist_mode: Whether in assist mode
            panel_name: DEPRECATED - no longer used (kept for compatibility)
            flash: Whether to add flash effect (deprecated, kept for compatibility)
            dev_mode: Whether DEV MODE is active (v1.5.0)

        Returns:
            Formatted prompt string
        """
        theme_config = self.themes.get(self.theme, self.themes['dungeon'])

        # Build prompt parts
        parts = []

        # Panel/workspace display deprecated in v1.1.1
        # uDOS environments are managed via folder structure, not displayed in prompt

        # Add DEV MODE indicator if active (v1.5.0)
        if dev_mode:
            parts.append('🔧 DEV> ')
        # Add main prompt
        elif is_assist_mode:
            parts.append(theme_config['assist_prompt'])
        else:
            parts.append(theme_config['normal_prompt'])

        return ''.join(parts)

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
