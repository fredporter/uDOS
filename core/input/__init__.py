"""
uDOS Core Input System

Smart interactive prompt with autocomplete and command prediction.
"""

from .smart_prompt import SmartPrompt
from .enhanced_prompt import EnhancedPrompt
from .autocomplete import AutocompleteService
from .command_predictor import CommandPredictor, Prediction, Token
from .keypad_handler import KeypadHandler, KeypadMode, get_keypad_handler
from .mouse_handler import (
    MouseHandler,
    MouseButton,
    MouseEvent,
    MouseEventType,
    MousePosition,
    ClickableRegion,
)
from .command_prompt import (
    CommandRegistry,
    CommandMetadata,
    ContextualCommandPrompt,
    create_default_registry,
)

__all__ = [
    "SmartPrompt",
    "EnhancedPrompt",
    "AutocompleteService",
    "CommandPredictor",
    "Prediction",
    "Token",
    "KeypadHandler",
    "KeypadMode",
    "get_keypad_handler",
    "MouseHandler",
    "MouseButton",
    "MouseEvent",
    "MouseEventType",
    "MousePosition",
    "ClickableRegion",
    "CommandRegistry",
    "CommandMetadata",
    "ContextualCommandPrompt",
    "create_default_registry",
]
