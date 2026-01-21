"""
uDOS Lightweight TUI Package

Modern, clean CLI interface for the refined uDOS core.
Leverages Phase 5F command handlers and TypeScript runtime.
All heavy lifting delegated to Wizard Server.

Components:
- repl: Main event loop
- dispatcher: Command routing
- renderer: Output formatting
- state: Game state management
"""

from .repl import TUIRepl
from .dispatcher import CommandDispatcher
from .renderer import GridRenderer
from .state import GameState

__all__ = [
    "TUIRepl",
    "CommandDispatcher",
    "GridRenderer",
    "GameState",
]

__version__ = "1.0.0"
