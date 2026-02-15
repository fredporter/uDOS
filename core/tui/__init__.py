"""
uDOS Lightweight TUI Package

Modern, clean CLI interface for the refined uDOS core.
Leverages Phase 5F command handlers and TypeScript runtime.
All heavy lifting delegated to Wizard Server.

Components:
- ucode: Unified Terminal TUI (uCLI)
- dispatcher: Command routing
- renderer: Output formatting
- state: Game state management
"""

__all__ = [
    "UCLI",
    "TUIRepl",
    "CommandDispatcher",
    "GridRenderer",
    "Renderer",
    "GameState",
]

def __getattr__(name):
    """Lazy imports to avoid circular dependencies at module import time."""
    if name == "UCLI":
        from .ucode import UCLI

        return UCLI
    if name == "TUIRepl":
        from .ucode import UCLI

        return UCLI
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

def __dir__():
    return sorted(__all__)

__version__ = "1.0.0"
