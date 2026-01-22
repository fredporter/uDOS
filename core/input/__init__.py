"""
uDOS Core Input System

Smart interactive prompt with autocomplete and command prediction.
"""

from .smart_prompt import SmartPrompt
from .autocomplete import AutocompleteService
from .command_predictor import CommandPredictor, Prediction, Token

__all__ = [
    "SmartPrompt",
    "AutocompleteService",
    "CommandPredictor",
    "Prediction",
    "Token",
]
