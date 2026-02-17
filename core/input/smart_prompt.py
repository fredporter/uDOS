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
import re
from typing import Optional, List, Iterable, Tuple, Dict

from .autocomplete import AutocompleteService
from .command_predictor import CommandPredictor
from core.input.confirmation_utils import (
    normalize_default,
    parse_confirmation,
    format_prompt,
    format_error,
)
from core.services.logging_api import get_logger
from core.input.keymap import decode_key_input
from core.utils.tty import (
    interactive_tty_status,
    normalize_terminal_input,
    strip_ansi_sequences,
    strip_literal_escape_sequences,
)

# Setup debug logging (silent by default, enable with DEBUG env var)

debug_logger = logging.getLogger("smartprompt")
if os.environ.get("DEBUG_SMARTPROMPT"):
    debug_logger.setLevel(logging.DEBUG)
    if not debug_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[SmartPrompt DEBUG] %(message)s"))
        debug_logger.addHandler(handler)
else:
    debug_logger.setLevel(logging.CRITICAL)  # Silent unless DEBUG_SMARTPROMPT=1

logger = get_logger("core", category="smartprompt", name="smartprompt")


class CoreCompleter(Completer):
    """Dynamic autocomplete for Core TUI commands with syntax hints"""

    def __init__(self, autocomplete_service: AutocompleteService, registry=None):
        """
        Initialize completer.

        Args:
            autocomplete_service: AutocompleteService instance
            registry: Optional CommandRegistry for enhanced completions
        """
        self.autocomplete = autocomplete_service
        self.registry = registry
        self._command_cache = {}

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        """
        Provide completions based on cursor position with enhanced help text.

        Args:
            document: Current document
            complete_event: Completion event

        Yields:
            Completion objects with syntax hints
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

            # Use registry if available, otherwise fall back to autocomplete service
            if self.registry:
                suggestions = self.registry.get_suggestions(partial_cmd, limit=10)
                debug_logger.debug(f"  Got {len(suggestions)} suggestions from registry")

                for suggestion in suggestions:
                    completion_text = suggestion.name[len(partial_cmd):]
                    display_meta = f"{suggestion.icon} {suggestion.help_text}"
                    debug_logger.debug(
                        f"    Yielding registry completion: {suggestion.name}, meta={display_meta}"
                    )
                    yield Completion(
                        completion_text,
                        start_position=-len(partial_cmd),
                        display=suggestion.name,
                        display_meta=display_meta,
                    )
            else:
                completions_list = self.autocomplete.get_completions(partial_cmd)
                debug_logger.debug(
                    f"  Got {len(completions_list)} completions from autocomplete: {completions_list}"
                )

                for completion in completions_list:
                    debug_logger.debug(
                        f"    Yielding completion: {completion}, start_position=-{len(partial_cmd)}"
                    )

                # Get help text for the command
                help_text = self._get_command_help(completion)

                yield Completion(
                    completion,
                    start_position=-len(partial_cmd),
                    display=completion,
                    display_meta=help_text,
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

                    # Add context-specific help for options
                    option_hint = self._get_option_hint(cmd, option)

                    yield Completion(
                        option,
                        start_position=-len(partial),
                        display=option,
                        display_meta=option_hint,
                    )

    def _get_command_help(self, command: str) -> str:
        """
        Get quick help text for a command.

        Args:
            command: Command name (e.g., "GOTO")

        Returns:
            Short description for display
        """
        if command in self._command_cache:
            return self._command_cache[command]

        try:
            from core.commands.help_handler import HelpHandler

            help_handler = HelpHandler()
            if command in help_handler.COMMANDS:
                cmd_info = help_handler.COMMANDS[command]
                desc = cmd_info.get("description", "")
                category = cmd_info.get("category", "")

                # Format: "Description | Category"
                help_text = f"{desc} | {category}" if category else desc

                self._command_cache[command] = help_text
                return help_text
        except Exception:
            pass

        return ""

    def _get_option_hint(self, command: str, option: str) -> str:
        """
        Get hint text for an option.

        Args:
            command: Command name
            option: Option name

        Returns:
            Hint text for display
        """
        # Common option hints
        hints = {
            "--help": "Show help for this command",
            "--verbose": "Verbose output",
            "--force": "Force operation without confirmation",
            "--dry-run": "Show what would be done without doing it",
            "--limit": "Limit results to N items",
            "--offset": "Start results at offset",
            "--type": "Filter by type",
            "--region": "Filter by region",
            "--filter": "Filter results",
            "--compress": "Apply compression",
            "--aggressive": "Aggressive mode (more changes)",
            "--confirm": "Require confirmation",
            "--date": "Specify date (YYYY-MM-DD)",
            "--template": "Use template",
            "--readonly": "Read-only mode",
            "--no-edit": "Do not open editor",
            "--validate": "Validate before proceeding",
            "--test": "Test mode (dry run)",
            "--details": "Show detailed information",
            "--focus": "Focus on specific module/area",
            "--check": "Check for issues",
            "--install": "Install dependencies",
            "--pull": "Pull from remote",
            "--skip-intro": "Skip introduction",
        }

        return hints.get(option.lower(), "")


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

    def __init__(self, use_fallback: bool = False, registry=None):
        """
        Initialize SmartPrompt.

        Args:
            use_fallback: Force fallback to basic input() (default: auto-detect)
            registry: Optional CommandRegistry for enhanced completions
        """
        debug_logger.debug(
            f"SmartPrompt.__init__() called, use_fallback={use_fallback}"
        )

        # Check if terminal is interactive
        self.interactive_reason: Optional[str] = None
        is_tty = self._is_interactive()
        debug_logger.debug(
            f"  is_tty={is_tty}, HAS_PROMPT_TOOLKIT={HAS_PROMPT_TOOLKIT}"
        )

        self.use_fallback = use_fallback or not HAS_PROMPT_TOOLKIT or not is_tty
        self.fallback_reason = None
        self.tab_handler = None
        self.registry = registry
        self.fkey_handler = None
        self.bottom_toolbar_provider = None
        self.input_history: List[str] = []
        self.logger = logger

        if self.use_fallback and not HAS_PROMPT_TOOLKIT:
            self.fallback_reason = "prompt_toolkit not installed"
        elif self.use_fallback and not is_tty:
            reason = self.interactive_reason or "stdin/stdout not a TTY or TERM=dumb"
            self.fallback_reason = f"Non-interactive terminal ({reason})"
            self.logger.info("[LOCAL] SmartPrompt fallback: %s", self.fallback_reason)

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
        self.completer = CoreCompleter(self.autocomplete_service, registry=self.registry)
        self.history = InMemoryHistory()

        # Create key bindings
        self.key_bindings = self._create_key_bindings()

        # Create style with improved syntax highlighting
        self.style = Style.from_dict(
            {
                "prompt": "ansigreen bold",           # Bold green prompt
                "completion": "ansiwhite",             # White completions
                "completion.meta": "ansiyellow",       # Yellow hints
                "scrollbar": "ansicyan",               # Cyan scrollbar
                "scrollbar.background": "ansiblack",   # Dark background
                # Keep high contrast so toolbar remains visible across terminals/themes.
                "bottom-toolbar": "ansiwhite bg:ansiblack",
                "bottom-toolbar.suggestion": "ansibrightblue",
                "bottom-toolbar.help": "ansiyellow",
                "bottom-toolbar.tip": "ansicyan",
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

    def _is_interactive(self) -> bool:
        """Check if running in an interactive terminal session."""
        interactive, reason = interactive_tty_status()
        self.interactive_reason = reason
        if not interactive and reason:
            debug_logger.debug("Interactive check failed: %s", reason)
        return interactive

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

        function_key_names = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]

        def _bind_function_key(key_name: str):
            @bindings.add(getattr(Keys, key_name))
            def _handle(event, _key=key_name):
                self._trigger_function_key(_key)

        for key_name in function_key_names:
            _bind_function_key(key_name)

        # macOS/Linux compatibility: allow Meta+1..8 as soft aliases for F1..F8.
        for index, key_name in enumerate(function_key_names, start=1):
            @bindings.add("escape", str(index))
            def _handle_meta_digit(event, _key=key_name):
                self._trigger_function_key(_key)

        @bindings.add(Keys.Tab)
        def _(event):
            """Handle Tab for command selector"""
            if not self.tab_handler:
                return

            try:
                # Try to use run_in_terminal if available
                if hasattr(event.app, 'run_in_terminal'):
                    selection = {"value": None}

                    def run_selector():
                        selection["value"] = self.tab_handler()

                    event.app.run_in_terminal(run_selector)
                    if selection["value"]:
                        event.app.current_buffer.insert_text(selection["value"])
                else:
                    # Fallback: run directly in current context
                    selection = self.tab_handler()
                    if selection:
                        event.app.current_buffer.insert_text(selection)
            except Exception as e:
                # On any error, just suppress tab handling
                debug_logger.debug(f"Tab handler error: {e}")

        return bindings

    def set_tab_handler(self, handler) -> None:
        """Register a callback for Tab key in advanced prompt mode."""
        self.tab_handler = handler

    def set_function_key_handler(self, handler) -> None:
        """Register a handler that responds to F1-F8 presses."""
        self.fkey_handler = handler

    def set_bottom_toolbar_provider(self, provider) -> None:
        """
        Register a callable that returns dynamic bottom toolbar lines.

        Provider signature: provider(text: str) -> Iterable[str] | str
        """
        self.bottom_toolbar_provider = provider

    def _get_bottom_toolbar(self):
        """Build bottom toolbar text for prompt_toolkit."""
        if not self.bottom_toolbar_provider:
            return ""

        try:
            buffer = None
            if self.session:
                app = getattr(self.session, "app", None)
                if app and getattr(app, "current_buffer", None):
                    buffer = app.current_buffer
                else:
                    buffer = self.session.default_buffer
            doc = buffer.document if buffer else None
            text = doc.text if doc else ""
            lines = self.bottom_toolbar_provider(text)
            if lines is None:
                return ""
            if isinstance(lines, str):
                return lines
            # Join multiple lines for a multi-line toolbar
            return "\n".join([str(line) for line in lines if line is not None])
        except Exception as exc:
            debug_logger.debug(f"Bottom toolbar provider failed: {exc}")
            return ""


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

    def ask_yes_no_ok(
        self,
        question: str,
        default: str = "yes",
    ) -> str:
        """
        Ask a standardized Yes/No/OK question.

        Format: "Question? [Yes/No/OK]"
        Accepts: Y/1, N/0, OK (OK maps to Yes). Enter returns default.

        Args:
            question: The question to ask (without punctuation)
        default: Default answer (yes, no, ok)

        Returns:
            'yes', 'no', or 'ok' (ok is equivalent to yes)
        """
        default_choice = normalize_default(default, "ok")
        prompt_text = format_prompt(question, default_choice, "ok")

        response = self.ask(prompt_text, default="")
        choice = parse_confirmation(response, default_choice, "ok")
        if choice is None:
            print(format_error("ok"))
            return self.ask_yes_no_ok(question, default_choice)
        return choice

    def ask_yes_no_choice(
        self,
        question: str,
        default: Optional[str] = None,
        variant: str = "ok",
    ) -> str:
        """Ask a standardized Yes/No/OK or Yes/No/SKIP question."""
        default_choice = normalize_default(default, variant)
        prompt_text = format_prompt(question, default_choice, variant)

        response = self.ask(prompt_text, default="")
        choice = parse_confirmation(response, default_choice, variant)
        if choice is None:
            print(format_error(variant))
            return self.ask_yes_no_choice(question, default_choice, variant)
        return choice

    def ask_yes_no(
        self,
        question: str,
        default: bool = True,
        variant: str = "ok",
    ) -> bool:
        """Ask a standardized confirmation question and return True/False."""
        choice = self.ask_yes_no_choice(question, default, variant)
        return choice in {"yes", "ok"}

    def ask_menu_choice(
        self,
        prompt_text: str,
        num_options: int,
        allow_zero: bool = False,
    ) -> Optional[int]:
        """
        Prompt for a numbered menu choice.

        Format: "Choose an option [1-N] (Enter=0 for cancel): "

        Args:
            prompt_text: Prompt to display (e.g., "Choose an option")
            num_options: Number of valid options (1 to N)
            allow_zero: If True, 0 is a valid choice (cancel/exit)

        Returns:
            Selected number (1-N), or None if cancelled
        """
        valid_range = f"0-{num_options}" if allow_zero else f"1-{num_options}"
        full_prompt = f"{prompt_text} [{valid_range}] "

        response = self.ask(full_prompt, default="")
        response = response.strip()

        # Empty defaults to cancel (0)
        if response == "":
            return 0 if allow_zero else None

        try:
            choice = int(response)

            # Validate range
            if allow_zero:
                if 0 <= choice <= num_options:
                    return choice
            else:
                if 1 <= choice <= num_options:
                    return choice

            # Out of range
            print(f"  ❌ Please enter a number between {valid_range}")
            return self.ask_menu_choice(prompt_text, num_options, allow_zero)

        except ValueError:
            # Not a number
            print(f"  ❌ Please enter a valid number (1-{num_options})")
            return self.ask_menu_choice(prompt_text, num_options, allow_zero)

    def ask_single_key(
        self,
        prompt_text: str,
        valid_keys: List[str],
        default: Optional[str] = None,
    ) -> str:
        """
        Prompt for a single key/choice input (y/n, number selection, etc).
        Accepts the key directly or uses default on Enter.

        Args:
            prompt_text: Prompt to display
            valid_keys: List of acceptable keys (lowercase)
            default: Default key to return on Enter (lowercase)

        Returns:
            The selected key (lowercase), or empty string
        """
        valid = [k.lower() for k in valid_keys]
        default_key = default.lower() if default else None

        try:
            # Use normal input
            response = self.ask(prompt_text, default="")
            response_lower = response.lower().strip()

            # Empty input returns default
            if response_lower == "" and default_key:
                return default_key

            # Valid key
            if response_lower in valid:
                return response_lower

            # Invalid - return empty
            return ""
        except (KeyboardInterrupt, EOFError):
            return ""
        except Exception as e:
            debug_logger.exception(f"Exception in ask_single_key(): {e}")
            return ""

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
            bottom_toolbar = self._get_bottom_toolbar if self.bottom_toolbar_provider else None
            user_input = self.session.prompt(prompt_text, bottom_toolbar=bottom_toolbar)
            debug_logger.debug(f"  Got input: '{user_input}'")

            # Track for history
            if user_input.strip():
                self._record_input(user_input)
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
            while True:
                self._render_fallback_toolbar()
                raw_input = input(prompt_text)
                normalized = normalize_terminal_input(raw_input)
                decoded = decode_key_input(normalized, env=os.environ)
                fallback_fkey = self._parse_fallback_function_key(normalized)
                if fallback_fkey:
                    self._trigger_function_key(fallback_fkey)
                    continue

                if decoded.action == "OPEN_COMMAND":
                    tab_selection = self._handle_tab_shortcut()
                    if tab_selection:
                        return tab_selection.strip()
                    continue

                if decoded.action in {"NAV_UP", "NAV_DOWN", "NAV_LEFT", "NAV_RIGHT", "NAV_HOME", "NAV_END", "NAV_DELETE", "NOISE"}:
                    # Ignore navigation-only input and reprompt.
                    continue

                had_escape = "\x1b" in normalized
                had_literal_escape = bool(re.search(r"(?:\^\[\[[0-9;?]*[A-Za-z~]|\\x1b\[[0-9;?]*[A-Za-z~])", normalized))
                if had_literal_escape:
                    normalized = strip_literal_escape_sequences(normalized)
                if had_escape:
                    # Strip ANSI escape sequences (arrows, colors, etc.)
                    normalized = strip_ansi_sequences(normalized)

                user_input = normalized.strip()
                if (had_escape or had_literal_escape) and self._looks_like_escape_noise(user_input):
                    # Self-heal for terminals that echo raw control keys as text.
                    continue

                if user_input:
                    self._record_input(user_input)

                return user_input
        except (KeyboardInterrupt, EOFError):
            return ""

    def _looks_like_escape_noise(self, text: str) -> bool:
        """Return True for non-semantic control-key residue in fallback mode."""
        if not text:
            return True
        # Keep any meaningful alphanumeric input.
        if re.search(r"[A-Za-z0-9]", text):
            return False
        # Strings of punctuation/symbols (e.g. '· ▶') are usually control-key echo noise.
        return True

    def _render_fallback_toolbar(self) -> None:
        """Best-effort toolbar rendering when prompt_toolkit is unavailable."""
        if not self.bottom_toolbar_provider:
            return
        try:
            lines = self.bottom_toolbar_provider("")
            if lines is None:
                return
            if isinstance(lines, str):
                if lines.strip():
                    print(lines)
                return
            for line in lines:
                if line is None:
                    continue
                s = str(line)
                if s.strip():
                    print(s)
        except Exception as exc:
            debug_logger.debug(f"Fallback toolbar render failed: {exc}")

    def _parse_fallback_function_key(self, raw_input: str) -> Optional[str]:
        """Best-effort F1-F8 parsing in fallback mode across common terminals."""
        decoded = decode_key_input(raw_input, env=os.environ)
        if decoded.action.startswith("FKEY_"):
            return f"F{decoded.action.split('_', 1)[1]}"
        return None

    def _handle_tab_shortcut(self) -> Optional[str]:
        """Invoke command selector via Tab even in fallback mode."""
        if not self.tab_handler:
            return None

        try:
            selection = self.tab_handler()
            if selection:
                print(f"\n  → Selected command: {selection.strip()}")
                return selection
        except Exception as exc:
            debug_logger.debug(f"Tab handler failed in fallback: {exc}")
        return None

    def _trigger_function_key(self, key_name: str) -> None:
        """Run a handler when the user presses F1-F8."""
        if not self.fkey_handler:
            return

        handler = self.fkey_handler.handlers.get(key_name)
        if not handler:
            return

        try:
            result = handler()
        except Exception as exc:
            debug_logger.debug(f"Function key handler {key_name} failed: {exc}")
            return

        if result:
            output = result.get("output") or result.get("message") or ""
            if output:
                print(f"\n{output}")

    def _record_input(self, user_input: str) -> None:
        """Track input for predictions and recent history."""
        self.predictor.record_command(user_input)
        self.input_history.append(user_input)
        self.input_history = self.input_history[-200:]

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

        # ANSI color codes for syntax highlighting
        colors = {
            "command": "\033[1;32m",    # Bold green
            "subcommand": "\033[36m",    # Cyan
            "argument": "\033[37m",      # White
            "option": "\033[33m",        # Yellow
            "path": "\033[35m",          # Magenta
            "reset": "\033[0m",
        }

        if not tokens:
            return command

        highlighted = ""
        for token in tokens:
            token_color = colors.get(token.color, colors["reset"])
            highlighted += f"{token_color}{token.text}{colors['reset']} "

        return highlighted.strip()

    def get_command_help_hint(self, command: str) -> Optional[str]:
        """
        Get a quick help hint for a command.

        Args:
            command: Command string (e.g., "GOTO north" or "SAVE")

        Returns:
            Help hint string or None
        """
        if not command or not command.strip():
            return None

        parts = command.split()
        cmd_name = parts[0].upper() if parts else ""

        # Import help handler to get command metadata
        try:
            from core.commands.help_handler import HelpHandler
            help_handler = HelpHandler()

            if cmd_name in help_handler.COMMANDS:
                cmd_info = help_handler.COMMANDS[cmd_name]
                # Format: "COMMAND (category) → description | syntax"
                category = cmd_info.get("category", "Unknown")
                desc = cmd_info.get("description", "")
                syntax = cmd_info.get("syntax", cmd_info.get("usage", ""))

                # Shorten long syntax for display
                if len(syntax) > 50:
                    syntax = syntax[:47] + "..."

                return f"{cmd_name} ({category}) → {desc}\n              Syntax: {syntax}"

        except Exception:
            # Silently fail if help handler unavailable
            pass

        return None

    def get_syntax_examples(self, command: str, max_examples: int = 3) -> List[str]:
        """
        Get example usages for a command.

        Args:
            command: Command string
            max_examples: Maximum examples to return

        Returns:
            List of example strings
        """
        if not command or not command.strip():
            return []

        cmd_name = command.split()[0].upper()

        try:
            from core.commands.help_handler import HelpHandler
            help_handler = HelpHandler()

            if cmd_name in help_handler.COMMANDS:
                cmd_info = help_handler.COMMANDS[cmd_name]
                example = cmd_info.get("example", "")

                if example:
                    # Split multiple examples by "or"
                    examples = [e.strip() for e in example.split(" or ")]
                    return examples[:max_examples]

        except Exception:
            pass

        return []

    def ask_story_field(self, field: Dict, previous_value: Optional[str] = None) -> Optional[str]:
        """
        Basic story field input (fallback method).

        Used when AdvancedFormField is not available or fails.
        Provides simple labeled input for story forms.

        Args:
            field: Field definition with name, label, type, required, etc.
            previous_value: Previous value if editing

        Returns:
            User input string or None if skipped
        """
        label = field.get('label', field.get('name', 'Field'))
        required = field.get('required', False)
        field_type = field.get('type', 'text')
        placeholder = field.get('placeholder', '')

        # Build prompt
        req_marker = " *" if required else ""
        prompt_text = f"{label}{req_marker}"

        # Show previous value if available
        if previous_value:
            prompt_text += f" [{previous_value}]"
        elif placeholder:
            prompt_text += f" ({placeholder})"

        prompt_text += ": "

        # Get input
        value = self.ask(prompt_text)

        # Handle empty input
        if not value:
            if previous_value:
                return previous_value
            elif required:
                print("  ⚠️  This field is required")
                return self.ask_story_field(field, previous_value)
            else:
                return None

        return value

    def __repr__(self) -> str:
        """String representation"""
        mode = "advanced" if not self.use_fallback else "fallback"
        reason = f" ({self.fallback_reason})" if self.fallback_reason else ""
        return f"<SmartPrompt mode={mode}{reason}>"
