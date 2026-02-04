"""
uDOS Lightweight TUI Package

Modern, clean CLI interface for the refined uDOS core.
Leverages Phase 5F command handlers and TypeScript runtime.
All heavy lifting delegated to Wizard Server.

Components:
- ucode: Unified Terminal TUI (main entry point)
- dispatcher: Command routing
- renderer: Output formatting
- state: Game state management
"""

from .ucode import uCODETUI
from .dispatcher import CommandDispatcher
from .renderer import GridRenderer, Renderer
from .state import GameState

# Legacy alias expected by older tests
TUIRepl = uCODETUI

__all__ = [
    "uCODETUI",
    "TUIRepl",
    "CommandDispatcher",
    "GridRenderer",
    "Renderer",
    "GameState",
]

__version__ = "1.0.0"
