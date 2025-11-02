"""
uDOS v1.0.0 - Base Command Handler

Provides the foundation for all command handlers in uDOS.
All specific handlers (SystemHandler, AssistantHandler, etc.) inherit from this.
"""

import json
from pathlib import Path


class BaseCommandHandler:
    """Base class for all command handlers."""

    def __init__(self, theme='dungeon', **kwargs):
        """
        Initialize base handler with common dependencies.

        Args:
            theme: Theme name (default: 'dungeon') - loads from data/themes/{theme}.json
            **kwargs: Additional dependencies passed from main CommandHandler
        """
        # Load theme lexicon for themed messages
        theme_file = f'data/themes/{theme.lower()}.json'
        with open(theme_file, 'r') as f:
            theme_data = json.load(f)
            self.lexicon = theme_data.get('TERMINOLOGY', {})

        # Store common dependencies
        self.connection = kwargs.get('connection')
        self.viewport = kwargs.get('viewport')
        self.user_manager = kwargs.get('user_manager')
        self.history = kwargs.get('history')
        self.enhanced_history = kwargs.get('enhanced_history')

    def get_message(self, key, **kwargs):
        """
        Retrieve a themed message from the lexicon.

        Args:
            key: Message key
            **kwargs: Format arguments for the message

        Returns:
            Formatted message string
        """
        message = self.lexicon.get(key, f"<{key}>")
        return message.format(**kwargs)

    def get_root_path(self):
        """Get the root path of the uDOS installation."""
        return Path(__file__).parent.parent.parent
