"""
uDOS v1.0.29 - Base Command Handler

Provides the foundation for all command handlers in uDOS.
All specific handlers (SystemHandler, AssistantHandler, etc.) inherit from this.

v1.0.29 adds smart input and output services for all commands.
"""

import json
from pathlib import Path
from core.theme_loader import load_theme


class BaseCommandHandler:
    """Base class for all command handlers."""

    def __init__(self, theme='dungeon', **kwargs):
        """
        Initialize base handler with common dependencies.

        Args:
            theme: Theme name (default: 'dungeon') - loads from data/themes/{theme}.json
            **kwargs: Additional dependencies passed from main CommandHandler
        """
        # Store theme name
        self.theme = theme

        # Load merged theme (bundled + memory overrides)
        # root_path should be the uDOS root directory (parent.parent.parent from this file)
        theme_data = load_theme(theme, root_path=Path(__file__).parent.parent.parent)
        self.lexicon = theme_data.get('TERMINOLOGY', {})
        self.messages = theme_data.get('MESSAGES', {})

        # Store common dependencies
        self.connection = kwargs.get('connection')
        self.viewport = kwargs.get('viewport')
        self.user_manager = kwargs.get('user_manager')
        self.history = kwargs.get('history')
        self.command_history = kwargs.get('command_history')
        self.logger = kwargs.get('logger')

        # v1.0.29: Smart input and output services (lazy-loaded)
        self._input_manager = None
        self._story_manager = None
        self._output_formatter = None

    def get_message(self, key, **kwargs):
        """
        Retrieve a themed message from the lexicon.

        Args:
            key: Message key
            **kwargs: Format arguments for the message

        Returns:
            Formatted message string
        """
        # Prefer MESSAGES, then TERMINOLOGY, then fallback
        template = None
        if hasattr(self, 'messages') and key in self.messages:
            template = self.messages.get(key)
        elif key in self.lexicon:
            template = self.lexicon.get(key)
        else:
            # Fallback: create a readable error message
            if kwargs:
                # Try to create a simple error with provided context
                context_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())
                return f"⚠️ {key}: {context_str}"
            else:
                return f"⚠️ {key}"

        try:
            return template.format(**kwargs)
        except (KeyError, AttributeError, ValueError) as e:
            # If formatting fails, return template with error note
            return f"{template} (format error: {e})"

    def get_root_path(self):
        """Get the root path of the uDOS installation."""
        return Path(__file__).parent.parent.parent

    # v1.0.29: Lazy-loaded service properties

    @property
    def input_manager(self):
        """Get or create InputManager instance"""
        if self._input_manager is None:
            from core.services.input_manager import create_input_manager
            self._input_manager = create_input_manager(theme=self.theme)
        return self._input_manager

    @property
    def story_manager(self):
        """Get or create StoryManager instance"""
        if self._story_manager is None:
            from core.output.story_manager import create_story_manager
            self._story_manager = create_story_manager()
        return self._story_manager

    @property
    def output_formatter(self):
        """Get or create OutputFormatter instance"""
        if self._output_formatter is None:
            from core.output.output_formatter import create_output_formatter
            # Use viewport width if available
            width = self.viewport.width if self.viewport else 80
            self._output_formatter = create_output_formatter(
                theme=self.theme,
                width=width
            )
        return self._output_formatter
