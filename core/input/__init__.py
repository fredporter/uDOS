"""
Universal Input System - v1.2.25

Core input handling components for device-agnostic operation.

Components:
    - interactive: Interactive prompts (v1.x)
    - keypad_handler: Universal 0-9 keypad system (v1.2.25)
    - (Future) mouse_handler: TUI mouse integration
    - (Future) clipboard_manager: Rolling clipboard system

Version: 1.2.25
"""

from .interactive import InteractivePrompt
from .keypad_handler import (
    KeypadHandler,
    KeypadMode,
    KeypadContext,
    get_keypad_handler
)

__all__ = [
    'InteractivePrompt',
    'KeypadHandler',
    'KeypadMode',
    'KeypadContext',
    'get_keypad_handler'
]
