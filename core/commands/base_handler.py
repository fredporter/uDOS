"""
uDOS v1.1.13 - Base Command Handler

Provides the foundation for all command handlers in uDOS.
All specific handlers (SystemHandler, AssistantHandler, etc.) inherit from this.

v1.0.29: Added smart input and output services for all commands.
v1.1.13: Added utility methods (validate_file_path, parse_key_value_params, format helpers).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from core.services.theme.theme_loader import load_theme
from core.utils.common import (
    validate_path,
    resolve_path,
    load_json_safe,
    save_json_atomic,
    parse_key_value_args,
    parse_flags,
    is_valid_filename,
    is_valid_extension
)


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

    # ========================================================================
    # v1.1.13: UTILITY METHODS
    # ========================================================================

    def validate_file_path(self, path: str, must_exist: bool = False) -> Tuple[bool, Optional[Path], str]:
        """
        Validate a file path using common utilities.

        Args:
            path: Path string to validate
            must_exist: Whether path must exist on filesystem

        Returns:
            Tuple of (is_valid, resolved_path, error_message)

        Examples:
            >>> success, path_obj, error = self.validate_file_path("core/data/themes/galaxy.json", must_exist=True)
        """
        return validate_path(path, must_exist=must_exist, base_dir=self.get_root_path())

    def parse_key_value_params(self, args: List[str]) -> Dict[str, str]:
        """
        Parse key=value argument pairs.

        Args:
            args: List of argument strings

        Returns:
            Dictionary of key-value pairs

        Examples:
            >>> params = self.parse_key_value_params(["name=test", "type=water"])
            {'name': 'test', 'type': 'water'}
        """
        return parse_key_value_args(args)

    def parse_command_flags(self, args: List[str]) -> Tuple[List[str], Dict[str, bool]]:
        """
        Parse flag arguments (--flag) from argument list.

        Args:
            args: List of argument strings

        Returns:
            Tuple of (non_flag_args, flag_dict)

        Examples:
            >>> args, flags = self.parse_command_flags(["file.txt", "--verbose"])
            (['file.txt'], {'verbose': True})
        """
        return parse_flags(args)

    def load_json_file(self, path: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Load JSON file safely.

        Args:
            path: Path to JSON file (relative to root or absolute)

        Returns:
            Tuple of (success, data, error_message)

        Examples:
            >>> success, data, error = self.load_json_file("core/data/themes/galaxy.json")
        """
        is_valid, path_obj, error = self.validate_file_path(path, must_exist=True)
        if not is_valid:
            return False, None, error
        return load_json_safe(path_obj)

    def save_json_file(self, path: str, data: Dict, indent: int = 2) -> Tuple[bool, str]:
        """
        Save JSON file atomically.

        Args:
            path: Path to JSON file (relative to root or absolute)
            data: Dictionary to save
            indent: JSON indentation (default: 2)

        Returns:
            Tuple of (success, error_message)

        Examples:
            >>> success, error = self.save_json_file("sandbox/config.json", {"key": "value"})
        """
        is_valid, path_obj, error = self.validate_file_path(path, must_exist=False)
        if not is_valid:
            return False, error
        return save_json_atomic(path_obj, data, indent=indent)

    # Format helpers (delegate to output_formatter)

    def format_success(self, message: str) -> str:
        """Format success message using output formatter."""
        return self.output_formatter.format_success(message)

    def format_error(self, message: str) -> str:
        """Format error message using output formatter."""
        return self.output_formatter.format_error(message)

    def format_info(self, message: str) -> str:
        """Format info message using output formatter."""
        return self.output_formatter.format_info(message)

    def format_warning(self, message: str) -> str:
        """Format warning message using output formatter."""
        return self.output_formatter.format_warning(message)
