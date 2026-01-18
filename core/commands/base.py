"""
Base command handler - Abstract base class for all command handlers.

Provides common functionality and interface for command handlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseCommandHandler(ABC):
    """Abstract base class for command handlers."""

    def __init__(self):
        """Initialize base handler."""
        self._state = {}

    @abstractmethod
    def handle(self, command: str, params: List[str], grid, parser) -> Dict:
        """
        Handle a command.

        Args:
            command: Command name (e.g., "MAP", "PANEL", "GOTO")
            params: Command parameters
            grid: TUI grid for rendering
            parser: Command parser

        Returns:
            Dict with status and command-specific data
        """
        pass

    def get_state(self, key: str, default=None):
        """Get state value."""
        return self._state.get(key, default)

    def set_state(self, key: str, value):
        """Set state value."""
        self._state[key] = value

    def clear_state(self):
        """Clear all state."""
        self._state = {}
