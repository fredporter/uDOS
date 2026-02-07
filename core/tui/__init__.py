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

__all__ = [
    "uCODETUI",
    "TUIRepl",
    "CommandDispatcher",
    "GridRenderer",
    "Renderer",
    "GameState",
]

def __getattr__(name):
    """Lazy imports to avoid circular dependencies at module import time."""
    if name == "uCODETUI":
        from .ucode import uCODETUI

        return uCODETUI
    if name == "TUIRepl":
        from .ucode import uCODETUI

        return uCODETUI
    if name == "CommandDispatcher":
        from .dispatcher import CommandDispatcher

        return CommandDispatcher
    if name == "GridRenderer":
        from .renderer import GridRenderer

        return GridRenderer
    if name == "Renderer":
        from .renderer import Renderer

        return Renderer
    if name == "GameState":
        from .state import GameState

        return GameState
    raise AttributeError(name)

# Legacy alias expected by older tests (resolved lazily)
def __dir__():
    return sorted(__all__)

__version__ = "1.0.0"
