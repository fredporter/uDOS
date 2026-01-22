"""
uDOS Core Smart Interactive Prompt

Advanced input handling with:
- Real-time autocomplete
- Multi-word command support
- Syntax highlighting
- Command history tracking
- Graceful fallback to basic input
"""

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.styles import Style
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.document import Document

    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

import sys
import os
import logging
from typing import Optional, List, Iterable

from .autocomplete import AutocompleteService
from .command_predictor import CommandPredictor

# Setup debug logging (silent by default, enable with DEBUG env var)
import os

debug_logger = logging.getLogger("smartprompt")
if os.environ.get("DEBUG_SMARTPROMPT"):
    debug_logger.setLevel(logging.DEBUG)
    if not debug_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[SmartPrompt DEBUG] %(message)s"))
        debug_logger.addHandler(handler)
else:
    debug_logger.setLevel(logging.CRITICAL)  # Silent unless DEBUG_SMARTPROMPT=1


class CoreCompleter(Completer):
    """Dynamic autocomplete for Core TUI commands"""

    def __init__(self, autocomplete_service: AutocompleteService):
        """
        Initialize completer.

        Args:
            autocomplete_service: AutocompleteService instance
        """
        self.autocomplete = autocomplete_service

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        """
        Provide completions based on cursor position.

        Args:
            document: Current document
            complete_event: Completion event

        Yields:
            Completion objects
        """
        text = document.text_before_cursor
        debug_logger.debug(f"get_completions() called: text='{text}'")

        if not text.strip():
            debug_logger.debug(f"  Empty text, returning no completions")
            return

        words = text.split()
        if not words:
            debug_logger.debug(f"  No words, returning")
            return

        debug_logger.debug(f"  Words: {words}, word count: {len(words)}")

        # Completing command (first word)
        if len(words) == 1:
            partial_cmd = words[0].upper()
            debug_logger.debug(f"  Completing command: partial_cmd='{partial_cmd}'")
            completions_list = self.autocomplete.get_completions(partial_cmd)
            debug_logger.debug(
                f"  Got {len(completions_list)} completions: {completions_list}"
            )
            for completion in completions_list:
                debug_logger.debug(
                    f"    Yielding completion: {completion}, start_position=-{len(partial_cmd)}"
                )
                yield Completion(
                    completion,
                    start_position=-len(partial_cmd),
                    display=completion,
                )
        else:
            # Completing arguments/options
            cmd = words[0].upper()
            partial = words[-1] if words[-1] else ""
            debug_logger.debug(f"  Completing args: cmd='{cmd}', partial='{partial}'")

            # Suggest options for known commands
            options = self.autocomplete.get_options(cmd)
            debug_logger.debug(f"  Got {len(options)} options: {options}")
            for option in options:
                if option.upper().startswith(partial.upper()):
                    debug_logger.debug(
                        f"    Yielding option: {option}, start_position=-{len(partial)}"
                    )
                    yield Completion(
                        option,
                        start_position=-len(partial),
                        display=option,
                    )


class SmartPrompt:
    """
    Advanced interactive prompt for Core TUI.

    Features:
    - Autocomplete with Tab key
    - Command history with arrow keys
    - Multi-word command support
    - Syntax highlighting
    - Graceful fallback to basic input()
    """

    def __init__(self, use_fallback: bool = False):
        """
        Initialize SmartPrompt.

        Args:
            use_fallback: Force fallback to basic input() (default: auto-detect)
        """
        debug_logger.debug(
            f"SmartPrompt.__init__() called, use_fallback={use_fallback}"
        )

        # Check if stdin is a TTY (interactive terminal)
        is_tty = sys.stdin.isatty() if hasattr(sys.stdin, "isatty") else False
        debug_logger.debug(
            f"  is_tty={is_tty}, HAS_PROMPT_TOOLKIT={HAS_PROMPT_TOOLKIT}"
        )

        self.use_fallback = use_fallback or not HAS_PROMPT_TOOLKIT or not is_tty
        self.fallback_reason = None

        if self.use_fallback and not HAS_PROMPT_TOOLKIT:
            self.fallback_reason = "prompt_toolkit not installed"
        elif self.use_fallback and not is_tty:
            self.fallback_reason = "Non-interactive terminal (stdin not a TTY)"

        debug_logger.debug(
            f"  use_fallback={self.use_fallback}, reason={self.fallback_reason}"
        )

        if not self.use_fallback:
            debug_logger.debug(f"  Initializing advanced mode")
            self._init_advanced_prompt()
            debug_logger.debug(
                f"  Advanced mode initialized, has session: {hasattr(self, 'session')}"
            )
        else:
            debug_logger.debug(f"  Initializing fallback mode")
            self._init_fallback_prompt()
            debug_logger.debug(f"  Fallback mode initialized")

    def _init_advanced_prompt(self) -> None:
        """Initialize advanced prompt_toolkit features"""
        self.autocomplete_service = AutocompleteService()
        self.predictor = CommandPredictor(self.autocomplete_service)
        self.completer = CoreCompleter(self.autocomplete_service)
        self.history = InMemoryHistory()

        # Create key bindings
        self.key_bindings = self._create_key_bindings()

        # Create style
        self.style = Style.from_dict(
            {
                "prompt": "ansigreen bold",
                "": "",
            }
        )

        # Create session
        try:
            self.session = PromptSession(
                completer=self.completer,
                history=self.history,
                auto_suggest=AutoSuggestFromHistory(),
                key_bindings=self.key_bindings,
                style=self.style,
                complete_while_typing=True,
                enable_history_search=True,
            )
        except Exception as e:
            # Switch to fallback if session creation fails
            self.use_fallback = True
            self.fallback_reason = f"PromptSession creation failed: {str(e)}"
            # Still initialize fallback services
            self.autocomplete_service = AutocompleteService()
            self.predictor = CommandPredictor(self.autocomplete_service)

    def _init_fallback_prompt(self) -> None:
        """Initialize basic fallback prompt"""
        self.autocomplete_service = AutocompleteService()
        self.predictor = CommandPredictor(self.autocomplete_service)

    def _create_key_bindings(self) -> KeyBindings:
        """
        Create key bindings for the prompt.

        Returns:
            KeyBindings instance
        """
        bindings = KeyBindings()

        @bindings.add(Keys.ControlC)
        def _(event):
            """Handle Ctrl+C"""
            raise KeyboardInterrupt()

        @bindings.add(Keys.ControlD)
        def _(event):
            """Handle Ctrl+D (EOF)"""
            raise EOFError()

        return bindings

    def ask(
        self,
        prompt_text: str = "uDOS> ",
        default: str = "",
    ) -> str:
        """
        Display prompt and get user input.

        Args:
            prompt_text: Prompt to display
            default: Default value if user presses Ctrl+C

        Returns:
            User input string
        """
        debug_logger.debug(f"ask() called: prompt_text='{prompt_text}'")
        try:
            if self.use_fallback:
                debug_logger.debug(f"  Using fallback mode")
                return self._ask_fallback(prompt_text)
            else:
                debug_logger.debug(f"  Using advanced mode (prompt_toolkit)")
                return self._ask_advanced(prompt_text)
        except (KeyboardInterrupt, EOFError):
            debug_logger.debug(f"  KeyboardInterrupt/EOFError caught")
            return ""
        except Exception as e:
            # Fallback on any error
            debug_logger.exception(f"  Exception in ask(): {e}")
            if not self.use_fallback:
                self.use_fallback = True
                self.fallback_reason = f"Error in advanced prompt: {e}"
            return self._ask_fallback(prompt_text)

    def _ask_advanced(self, prompt_text: str) -> str:
        """
        Get input using prompt_toolkit.

        Args:
            prompt_text: Prompt to display

        Returns:
            User input
        """
        debug_logger.debug(f"_ask_advanced() called")
        try:
            debug_logger.debug(f"  Calling session.prompt('{prompt_text}')")
            user_input = self.session.prompt(prompt_text)
            debug_logger.debug(f"  Got input: '{user_input}'")

            # Track for history
            if user_input.strip():
                self.predictor.record_command(user_input)
                debug_logger.debug(f"  Recorded command in history")

            return user_input.strip()
        except Exception as e:
            debug_logger.exception(f"  Exception in _ask_advanced: {e}")
            # Fallback to basic input
            return self._ask_fallback(prompt_text)

    def _ask_fallback(self, prompt_text: str = "uDOS> ") -> str:
        """
        Get input using basic input().

        Args:
            prompt_text: Prompt to display

        Returns:
            User input
        """
        try:
            user_input = input(prompt_text).strip()

            # Track for history
            if user_input:
                self.predictor.record_command(user_input)

            return user_input
        except (KeyboardInterrupt, EOFError):
            return ""

    def get_predictions(self, partial: str, max_results: int = 5) -> List:
        """
        Get command predictions for partial input.

        Args:
            partial: Partial command text
            max_results: Max predictions to return

        Returns:
            List of Prediction objects
        """
        return self.predictor.predict(partial, max_results)

    def get_highlighted_command(self, command: str) -> str:
        """
        Get syntax-highlighted version of command.

        Args:
            command: Command string

        Returns:
            Formatted command string (with ANSI codes if available)
        """
        tokens = self.predictor.tokenize(command)

        # Simple ANSI color codes
        color_map = {
            "green": "\033[32m",
            "cyan": "\033[36m",
            "yellow": "\033[33m",
            "white": "\033[37m",
            "reset": "\033[0m",
        }

        if not tokens:
            return command

        highlighted = ""
        for token in tokens:
            color = color_map.get(token.color, "")
            highlighted += f"{color}{token.text}\033[0m "

        return highlighted.strip()

    def __repr__(self) -> str:
        """String representation"""
        mode = "advanced" if not self.use_fallback else "fallback"
        reason = f" ({self.fallback_reason})" if self.fallback_reason else ""
        return f"<SmartPrompt mode={mode}{reason}>"
