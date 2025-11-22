"""
uDOS v1.0.30 - Smart Interactive Prompt
Enhanced CLI with autocomplete, history search, and intelligent suggestions
Now with teletext block styling for visual feedback

Robustness Features:
- Fallback mode for terminals with scrollback issues
- Safe input handling (no ANSI interference)
- Copy-paste friendly
- Graceful degradation

Version: 1.0.30
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from typing import List, Iterable, Optional
import sys
import os

from core.services.autocomplete import AutocompleteService


# Teletext block characters for enhanced visual feedback (v1.0.30)
class TeletextIndicators:
    """Simple teletext-style indicators for autocomplete"""
    FULL_BLOCK = '█'
    LIGHT_BLOCK = '░'
    ARROW = '►'
    FILE = '📄'
    FOLDER = '📁'
    VALUE = '💡'
    COMMAND = '⚡'

    @staticmethod
    def score_bar(score: float, length: int = 10) -> str:
        """Create visual score bar using blocks"""
        filled = int(score * length)
        return TeletextIndicators.FULL_BLOCK * filled + TeletextIndicators.LIGHT_BLOCK * (length - filled)


class uDOSCompleter(Completer):
    """
    Custom completer for uDOS commands using AutocompleteService.
    Provides real-time suggestions as you type.
    """

    def __init__(self, autocomplete_service: AutocompleteService):
        """
        Initialize completer with autocomplete service.

        Args:
            autocomplete_service: AutocompleteService instance
        """
        self.autocomplete = autocomplete_service

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        """
        Generate completions based on current input.

        Args:
            document: Current document (input text)
            complete_event: Completion event

        Yields:
            Completion objects for prompt_toolkit
        """
        text = document.text_before_cursor
        words = text.split()

        if not words:
            # Empty input - suggest common commands
            suggestions = self.autocomplete.get_command_suggestions('', max_results=10)
            for sug in suggestions:
                yield Completion(
                    sug['command'],
                    start_position=0,
                    display=f"{sug['command']:<15} - {sug['description']}"
                )

        elif len(words) == 1:
            # First word - command suggestions
            partial = words[0]
            suggestions = self.autocomplete.get_command_suggestions(partial, max_results=10)

            for sug in suggestions:
                # Calculate start position (replace partial command)
                start_pos = -len(partial)

                # v1.0.30: Enhanced visual feedback with teletext blocks
                score_bar = TeletextIndicators.score_bar(sug['score'], length=10)
                icon = TeletextIndicators.COMMAND

                yield Completion(
                    sug['command'],
                    start_position=start_pos,
                    display=f"{icon} {sug['command']:<15} {score_bar} {sug['description'][:35]}"
                )

        elif len(words) == 2:
            # Second word - option/subcommand suggestions
            command = words[0].upper()
            partial = words[1]
            suggestions = self.autocomplete.get_option_suggestions(command, partial, max_results=10)

            if suggestions:
                for sug in suggestions:
                    start_pos = -len(partial)
                    yield Completion(
                        sug['option'],
                        start_position=start_pos,
                        display=f"{sug['command']} {sug['option']}"
                    )
            else:
                # No options available, try argument suggestions
                arg_suggestions = self.autocomplete.get_argument_suggestions(command, '', partial)
                for sug in arg_suggestions:
                    start_pos = -len(partial)
                    arg_type = sug.get('type', 'value')
                    icon = '📁' if arg_type == 'directory' else '📄' if arg_type == 'file' else '💡'
                    desc = sug.get('description', '')
                    display = f"{icon} {sug['argument']}"
                    if desc:
                        display += f" - {desc}"

                    yield Completion(
                        sug['argument'],
                        start_position=start_pos,
                        display=display
                    )

        elif len(words) >= 3:
            # Third word and beyond - argument suggestions
            command = words[0].upper()
            option = words[1].upper() if len(words) > 1 else ''
            partial = words[-1]

            suggestions = self.autocomplete.get_argument_suggestions(command, option, partial)

            for sug in suggestions:
                start_pos = -len(partial)
                arg_type = sug.get('type', 'value')
                icon = '📁' if arg_type == 'directory' else '📄' if arg_type == 'file' else '💡'
                desc = sug.get('description', '')
                display = f"{icon} {sug['argument']}"
                if desc:
                    display += f" - {desc}"

                yield Completion(
                    sug['argument'],
                    start_position=start_pos,
                    display=display
                )


class SmartPrompt:
    """
    Enhanced interactive prompt for uDOS with autocomplete and smart features.

    Features:
    - Autocomplete with fuzzy matching
    - Command history (Ctrl+R)
    - Fallback mode for problematic terminals
    - Copy-paste friendly
    """

    def __init__(self, command_history=None, theme='dungeon', use_fallback=False):
        """
        Initialize smart prompt.

        Args:
            command_history: CommandHistory instance for persistent history
            theme: Theme name for styling
            use_fallback: Force fallback mode (simple input, no autocomplete)
        """
        self.autocomplete = AutocompleteService()
        self.completer = uDOSCompleter(self.autocomplete)
        self.command_history = command_history
        self.pt_history = InMemoryHistory()
        self.use_fallback = use_fallback
        self.fallback_reason = None

        # Load history from command_history if available
        if command_history and not use_fallback:
            try:
                recent = command_history.get_recent(count=100)
                for cmd_data in recent:
                    if isinstance(cmd_data, dict):
                        cmd_text = cmd_data.get('command', '')
                    else:
                        cmd_text = str(cmd_data)
                    if cmd_text:
                        self.pt_history.append_string(cmd_text)
            except Exception:
                pass  # Fallback to empty history

        # Define custom key bindings
        if not use_fallback:
            self.key_bindings = self._create_key_bindings()

            # Define prompt style
            self.style = Style.from_dict({
                'prompt': '#00ff00 bold',  # Green prompt
                'completion-menu.completion': 'bg:#008888 #ffffff',
                'completion-menu.completion.current': 'bg:#00aaaa #000000 bold',
                'scrollbar.background': 'bg:#88aaaa',
                'scrollbar.button': 'bg:#222222',
            })

        # Test if prompt_toolkit works correctly
        if not use_fallback:
            self._test_prompt_toolkit()

    def _create_key_bindings(self) -> KeyBindings:
        """
        Create custom key bindings for enhanced navigation.

        Returns:
            KeyBindings instance
        """
        kb = KeyBindings()

        # Ctrl+R for reverse history search (built-in to prompt_toolkit)
        # Ctrl+C to cancel (built-in)
        # Tab for completion (built-in)
        # Arrow keys for history/completion navigation (built-in)

        return kb

    def _test_prompt_toolkit(self):
        """
        Test if prompt_toolkit works correctly in this terminal.
        Switches to fallback mode if issues detected.
        """
        try:
            # Check if stdin is a TTY
            if not sys.stdin.isatty():
                self.use_fallback = True
                self.fallback_reason = "Non-interactive terminal detected"
                return

            # Check for problematic terminal environments
            term = os.environ.get('TERM', '')
            if term in ['dumb', 'unknown']:
                self.use_fallback = True
                self.fallback_reason = f"Unsupported terminal type: {term}"
                return

            # Test basic prompt_toolkit functionality
            # (skipping actual test for now, can be enabled if needed)

        except Exception as e:
            self.use_fallback = True
            self.fallback_reason = f"Prompt test failed: {str(e)}"

    def ask(self, prompt_text: str = "uDOS> ", multiline: bool = False) -> str:
        """
        Display prompt and get user input with autocomplete.
        Uses fallback mode if prompt_toolkit has issues.

        Args:
            prompt_text: Prompt string to display
            multiline: Whether to allow multiline input

        Returns:
            User input string
        """
        # Use fallback mode if enabled
        if self.use_fallback:
            return self._ask_fallback(prompt_text)

        try:
            user_input = prompt(
                prompt_text,
                completer=self.completer,
                complete_while_typing=True,
                history=self.pt_history,
                key_bindings=self.key_bindings,
                style=self.style,
                multiline=multiline,
                enable_history_search=True,  # Enables Ctrl+R
                mouse_support=False,  # Disable mouse for better terminal compatibility
            )

            # Add to persistent history if available
            if self.command_history and user_input.strip():
                try:
                    self.command_history.append_string(user_input.strip())
                except Exception:
                    pass  # Don't fail if history add fails

            return user_input.strip()

        except (KeyboardInterrupt, EOFError):
            return ''
        except Exception as e:
            # If prompt_toolkit fails, switch to fallback
            if not self.use_fallback:
                self.use_fallback = True
                self.fallback_reason = f"Prompt error: {str(e)}"
                print(f"\n⚠️  Switching to fallback input mode: {self.fallback_reason}")
            return self._ask_fallback(prompt_text)

    def _ask_fallback(self, prompt_text: str = "uDOS> ") -> str:
        """
        Fallback input method using standard input().
        No autocomplete, but more robust and copy-paste friendly.

        Args:
            prompt_text: Prompt string

        Returns:
            User input string
        """
        try:
            user_input = input(prompt_text).strip()

            # Add to persistent history if available
            if self.command_history and user_input:
                try:
                    self.command_history.append_string(user_input)
                except Exception:
                    pass

            return user_input
        except (KeyboardInterrupt, EOFError):
            return ''

    def ask_with_default(self, prompt_text: str, default: str = '') -> str:
        """
        Ask for input with a default value.

        Args:
            prompt_text: Prompt string
            default: Default value

        Returns:
            User input or default
        """
        try:
            user_input = prompt(
                prompt_text,
                default=default,
                completer=self.completer,
                complete_while_typing=True,
                history=self.pt_history,
                style=self.style,
            )
            return user_input.strip()
        except (KeyboardInterrupt, EOFError):
            return default

    def format_command_chain_hint(self, command: str) -> str:
        """
        Suggest command chains based on what user just typed.

        Args:
            command: Command that was executed

        Returns:
            Suggestion for next command in chain
        """
        chains = {
            'LOAD': '→ SHOW → ANALYZE',
            'CATALOG': '→ LOAD → EDIT',
            'ASK': '→ SHOW → SAVE',
            'GRID PANEL CREATE': '→ LOAD → SAVE',
            'UNDO': '→ REDO (if needed)',
            'RESTORE': '→ LIST first to see sessions',
        }

        command_upper = command.upper().strip()
        for cmd, chain in chains.items():
            if command_upper.startswith(cmd):
                return f"\n   Chain: {cmd} {chain}"

        return ""


def create_smart_prompt(command_history=None, theme='dungeon') -> SmartPrompt:
    """
    Factory function to create SmartPrompt instance.

    Args:
        command_history: CommandHistory instance
        theme: Theme name

    Returns:
        SmartPrompt instance
    """
    return SmartPrompt(command_history=command_history, theme=theme)
