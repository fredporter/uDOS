"""
Command Predictor for Core TUI

Provides syntax highlighting and command predictions.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re


@dataclass
class Prediction:
    """A single command prediction"""

    text: str
    confidence: float  # 0.0 - 1.0
    source: str  # "history", "schema", "fuzzy"
    description: Optional[str] = None


@dataclass
class Token:
    """Highlighted token in command"""

    text: str
    type: str  # "command", "arg", "option"
    color: str = "white"


class CommandPredictor:
    """
    Smart command prediction and tokenization for Core.

    Provides:
    - Real-time syntax highlighting
    - Intelligent completions
    - Fuzzy matching for typos
    """

    def __init__(self, autocomplete_service=None):
        """
        Initialize predictor.

        Args:
            autocomplete_service: AutocompleteService instance
        """
        from .autocomplete import AutocompleteService

        self.autocomplete = autocomplete_service or AutocompleteService()
        self.recent_commands: List[str] = []
        self.command_frequency: Dict[str, int] = {}

    def predict(self, partial: str, max_results: int = 5) -> List[Prediction]:
        """
        Generate predictions for partial input.

        Args:
            partial: Current text being typed
            max_results: Max predictions to return

        Returns:
            List of ranked predictions
        """
        if not partial.strip():
            # Return most common commands
            return [
                Prediction(
                    text=cmd,
                    confidence=0.8,
                    source="schema",
                    description=self.autocomplete.get_description(cmd),
                )
                for cmd in ["HELP", "MAP", "GOTO", "FIND"]
            ]

        predictions = []
        words = partial.strip().split()
        cmd_partial = words[0].upper() if words else ""

        # Get completions from autocomplete service
        completions = self.autocomplete.get_completions(cmd_partial, max_results)

        for cmd in completions:
            confidence = 0.9 if cmd.startswith(cmd_partial) else 0.5
            # Boost recent commands
            if cmd in self.recent_commands:
                confidence = min(1.0, confidence + 0.1)

            predictions.append(
                Prediction(
                    text=cmd,
                    confidence=confidence,
                    source="schema",
                    description=self.autocomplete.get_description(cmd),
                )
            )

        return predictions[:max_results]

    def tokenize(self, command: str) -> List[Token]:
        """
        Parse command into syntax-highlighted tokens.

        Args:
            command: Command string to tokenize

        Returns:
            List of highlighted tokens
        """
        if not command.strip():
            return []

        tokens = []
        words = command.strip().split()

        if not words:
            return tokens

        # First word is command
        cmd = words[0].upper()
        valid_commands = self.autocomplete.core_commands

        tokens.append(
            Token(
                text=cmd,
                type="command",
                color="green" if cmd in valid_commands else "yellow",
            )
        )

        # Remaining words are arguments/options
        for word in words[1:]:
            if word.startswith("--"):
                tokens.append(Token(text=word, type="option", color="cyan"))
            elif word.startswith("-"):
                tokens.append(Token(text=word, type="option", color="cyan"))
            else:
                tokens.append(Token(text=word, type="arg", color="white"))

        return tokens

    def record_command(self, command: str) -> None:
        """Track command for frequency analysis"""
        cmd = command.strip().split()[0] if command.strip() else ""
        if cmd:
            self.recent_commands.append(cmd)
            self.recent_commands = self.recent_commands[-100:]  # Keep last 100
            self.command_frequency[cmd] = self.command_frequency.get(cmd, 0) + 1
