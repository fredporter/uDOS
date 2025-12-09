"""
uDOS v1.2.21 - Smart Interactive Prompt
Enhanced CLI with TRUE predictive text (non-intrusive suggestions)

FIXES FROM v1:
- No auto-complete on single keypress (was inserting full commands)
- Proper suggestion box with cursor navigation
- Arrow keys + numpad support for selection
- Tab to accept suggestion
- Esc to dismiss suggestions

Features:
- Non-intrusive prediction box (suggestions shown, not inserted)
- Multi-line suggestion display with cursor
- Tab/Enter to accept selected suggestion
- Arrow keys (↑↓) + numpad (8/2) for navigation
- Fuzzy matching from command history
- Graceful degradation to plain text input (no hotkeys in fallback mode)

Version: 1.2.21 (Geography Consolidation)
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText, HTML
from prompt_toolkit.layout import Float, FloatContainer, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from typing import List, Iterable, Optional
import sys
import os

from core.utils.autocomplete import AutocompleteService


class ImprovedCompleter(Completer):
    """
    Improved completer that ONLY shows suggestions, never auto-inserts.
    
    Changes from v1:
    - Completions require explicit Tab/Enter to accept
    - No auto-insertion on keypress
    - Clear visual distinction between input and suggestions
    """

    def __init__(self, autocomplete_service: AutocompleteService):
        """Initialize with autocomplete service."""
        self.autocomplete = autocomplete_service
        self.last_suggestions = []

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        """
        Generate completions WITHOUT auto-inserting.
        
        User must press Tab or select with arrows to accept.
        """
        text = document.text_before_cursor
        words = text.split()

        # Don't show completions unless user explicitly requests (Tab key)
        if not complete_event.completion_requested:
            return

        if not words:
            # Empty input - suggest common commands
            suggestions = self.autocomplete.get_command_suggestions('', max_results=10)
            for sug in suggestions:
                yield Completion(
                    sug['command'],
                    start_position=0,
                    display=f"  {sug['command']:<12} │ {sug['description'][:45]}"
                )

        elif len(words) == 1 and not text.endswith(' '):
            # First word - command suggestions
            partial = words[0]
            suggestions = self.autocomplete.get_command_suggestions(partial, max_results=10)

            for sug in suggestions:
                # Only complete the command part
                remaining = sug['command'][len(partial):]
                
                yield Completion(
                    remaining,
                    start_position=0,
                    display=f"  {sug['command']:<12} │ {sug['description'][:45]}"
                )

        else:
            # Subsequent words - parameter suggestions
            current_word = words[-1] if not text.endswith(' ') else ''
            suggestions = self.autocomplete.get_parameter_suggestions(
                command=words[0],
                partial_param=current_word,
                position=len(words) - 1
            )

            for sug in suggestions:
                remaining = sug['value'][len(current_word):] if current_word else sug['value']
                
                icon = {
                    'path': '📁',
                    'file': '📄',
                    'flag': '🚩',
                    'value': '💡',
                    'param': '⚙️'
                }.get(sug['type'], '·')
                
                yield Completion(
                    remaining,
                    start_position=0,
                    display=f"  {icon} {sug['value']:<12} │ {sug.get('description', sug['type'])[:40]}"
                )


class SmartPrompt:
    """
    Enhanced interactive prompt with PROPER predictive text.
    
    KEY CHANGES FROM v1:
    - Suggestions shown in dropdown (not auto-inserted)
    - Arrow keys navigate suggestions
    - Tab/Enter accepts selected suggestion
    - Single letter keypresses type normally (NO auto-complete)
    - Esc dismisses suggestion box
    - Numpad 8/2 also navigate when enabled
    """

    def __init__(self, command_history=None, theme='dungeon', use_fallback=False):
        """
        Initialize smart prompt v2.

        Args:
            command_history: CommandHistory instance
            theme: Theme name for styling
            use_fallback: Force fallback mode (simple input)
        """
        # Check TUI config for smart input setting
        try:
            from core.ui.tui_config import get_tui_config
            tui_config = get_tui_config()
            smart_input_enabled = tui_config.get('smart_input_enabled', True)
            
            # Override use_fallback if smart input is disabled
            if not smart_input_enabled and not use_fallback:
                use_fallback = True
                self.fallback_reason = "Smart input disabled in TUI config"
        except Exception:
            # If config fails, proceed with original setting
            pass
        
        self.autocomplete = AutocompleteService()
        self.completer = ImprovedCompleter(self.autocomplete)
        self.command_history = command_history
        self.pt_history = InMemoryHistory()
        self.use_fallback = use_fallback
        self.fallback_reason = getattr(self, 'fallback_reason', None)
        self.tui = None  # TUI controller
        
        # Load history
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
                pass

        # Create key bindings (NO auto-complete on single key)
        if not use_fallback:
            self.key_bindings = self._create_key_bindings()
            self.style = Style.from_dict({
                'prompt': 'ansigreen bold',
                '': '',
                'completion-menu.completion': 'bg:#1a1a1a #00ff00',
                'completion-menu.completion.current': 'bg:#00ff00 #000000 bold',
                'scrollbar.background': 'bg:#333333',
                'scrollbar.button': 'bg:#00ff00',
            })

        # Test prompt_toolkit
        if not use_fallback:
            self._test_prompt_toolkit()

    def _create_key_bindings(self) -> KeyBindings:
        """
        Create key bindings with PROPER navigation support.
        
        CRITICAL CHANGES:
        - NO auto-complete on letter keys
        - Tab opens/navigates completion menu
        - Arrow keys (↑↓) navigate completions
        - Enter accepts selected completion
        - Esc closes completion menu
        - Numpad 8/2 navigate when TUI enabled
        """
        kb = KeyBindings()

        # ===== COMPLETION NAVIGATION =====
        # (prompt_toolkit handles Tab, Enter, arrows by default)
        
        # ===== NUMPAD SUPPORT (TUI mode) =====
        @kb.add('8')  # Numpad 8 = Up
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                current_text = event.current_buffer.text
                
                # If no text typed yet, scroll pager up
                if not current_text.strip():
                    if hasattr(self.tui, 'pager') and self.tui.pager:
                        from core.ui.pager import ScrollDirection
                        scrolled = self.tui.pager.scroll(ScrollDirection.UP)
                        if scrolled:
                            # Show scroll indicator briefly
                            pass  # Pager handles display
                    return
                
                # If text typed, navigate completion menu or history
                if event.current_buffer.complete_state:
                    event.current_buffer.complete_previous()
                else:
                    # History backward
                    event.current_buffer.history_backward()
            else:
                # Insert '8' normally when keypad disabled
                event.current_buffer.insert_text('8')

        @kb.add('2')  # Numpad 2 = Down
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                current_text = event.current_buffer.text
                
                # If no text typed yet, scroll pager down
                if not current_text.strip():
                    if hasattr(self.tui, 'pager') and self.tui.pager:
                        from core.ui.pager import ScrollDirection
                        scrolled = self.tui.pager.scroll(ScrollDirection.DOWN)
                        if scrolled:
                            # Show scroll indicator briefly
                            pass  # Pager handles display
                    return
                
                # If text typed, navigate completion menu or history
                if event.current_buffer.complete_state:
                    event.current_buffer.complete_next()
                else:
                    # History forward
                    event.current_buffer.history_forward()
            else:
                # Insert '2' normally when keypad disabled
                event.current_buffer.insert_text('2')

        @kb.add('4')  # Numpad 4 = Left
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                current_text = event.current_buffer.text
                
                # If no text typed yet, page up in pager
                if not current_text.strip():
                    if hasattr(self.tui, 'pager') and self.tui.pager:
                        from core.ui.pager import ScrollDirection
                        scrolled = self.tui.pager.scroll(ScrollDirection.PAGE_UP)
                        if scrolled:
                            pass  # Pager handles display
                    return
                
                # If text typed, move cursor left
                event.current_buffer.cursor_left()
            else:
                event.current_buffer.insert_text('4')

        @kb.add('6')  # Numpad 6 = Right  
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                current_text = event.current_buffer.text
                
                # If no text typed yet, page down in pager
                if not current_text.strip():
                    if hasattr(self.tui, 'pager') and self.tui.pager:
                        from core.ui.pager import ScrollDirection
                        scrolled = self.tui.pager.scroll(ScrollDirection.PAGE_DOWN)
                        if scrolled:
                            pass  # Pager handles display
                    return
                
                # If text typed and completion available, accept suggestion
                if event.current_buffer.complete_state:
                    # Accept current completion
                    event.current_buffer.apply_completion(event.current_buffer.complete_state.current_completion)
                    event.current_buffer.complete_state = None
                else:
                    # Move cursor right normally
                    event.current_buffer.cursor_right()
            else:
                event.current_buffer.insert_text('6')

        @kb.add('5')  # Numpad 5 = Select/Enter
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                # Accept current completion or submit line
                if event.current_buffer.complete_state:
                    event.current_buffer.complete_next()
                    event.current_buffer.complete_state = None
                else:
                    event.current_buffer.validate_and_handle()
            else:
                event.current_buffer.insert_text('5')

        # ===== CURSOR MOVEMENT =====
        @kb.add('c-a')  # Ctrl+A = Start of line
        def _(event):
            event.current_buffer.cursor_position = 0

        @kb.add('c-e')  # Ctrl+E = End of line
        def _(event):
            event.current_buffer.cursor_position = len(event.current_buffer.text)

        @kb.add('c-k')  # Ctrl+K = Delete to end of line
        def _(event):
            event.current_buffer.delete(count=len(event.current_buffer.text) - event.current_buffer.cursor_position)

        @kb.add('c-u')  # Ctrl+U = Delete to start of line
        def _(event):
            event.current_buffer.delete_before_cursor(count=event.current_buffer.cursor_position)

        # ===== HISTORY SEARCH =====
        # (Ctrl+R is built-in to prompt_toolkit)

        return kb

    def _test_prompt_toolkit(self):
        """Test if prompt_toolkit works, switch to fallback if not."""
        try:
            if not sys.stdin.isatty():
                self.use_fallback = True
                self.fallback_reason = "Non-interactive terminal"
                return

            term = os.environ.get('TERM', '')
            if term in ['dumb', 'unknown']:
                self.use_fallback = True
                self.fallback_reason = f"Unsupported terminal: {term}"
                return

        except Exception as e:
            self.use_fallback = True
            self.fallback_reason = f"Terminal test failed: {e}"

    def set_tui_controller(self, tui_controller):
        """Set TUI controller for enhanced features."""
        self.tui = tui_controller

    def ask(self, prompt_text: str = "> ", multiline: bool = False) -> str:
        """
        Display prompt and get user input with PROPER suggestions.
        
        CRITICAL: Suggestions are SHOWN, not auto-inserted.
        User must Tab to open menu, arrows to navigate, Enter to accept.

        Args:
            prompt_text: Prompt string
            multiline: Allow multiline input

        Returns:
            User input string
        """
        # Show hints if TUI enabled
        if self.tui and self.tui.keypad.enabled:
            print("┌─ Keypad: 8↑ 2↓ 4← 6→ 5✓ | Tab=suggest Enter=accept Esc=cancel ─┐")

        # Use fallback if needed
        if self.use_fallback:
            return self._ask_fallback(prompt_text)

        try:
            formatted_prompt = FormattedText([('class:prompt', prompt_text)])

            user_input = prompt(
                formatted_prompt,
                completer=self.completer,
                complete_while_typing=False,  # CRITICAL: Don't auto-show (user presses Tab)
                history=self.pt_history,
                key_bindings=self.key_bindings,
                style=self.style,
                multiline=multiline,
                enable_history_search=True,
                mouse_support=False,
                # Completion menu style
                reserve_space_for_menu=5,  # Reserve space for suggestions
            )

            # Add to history
            if self.command_history and user_input.strip():
                try:
                    self.command_history.append_string(user_input.strip())
                except Exception:
                    pass

            return user_input.strip()

        except (KeyboardInterrupt, EOFError):
            return ''
        except Exception as e:
            if not self.use_fallback:
                self.use_fallback = True
                self.fallback_reason = f"Prompt error: {e}"
                print(f"\n⚠️  Fallback mode: {self.fallback_reason}")
            return self._ask_fallback(prompt_text)

    def _ask_fallback(self, prompt_text: str = "uDOS> ") -> str:
        """Fallback using plain standard input() - no autocomplete, no hotkeys."""
        try:
            # Plain text input only - no special key handling
            user_input = input(prompt_text).strip()

            if self.command_history and user_input:
                try:
                    self.command_history.append_string(user_input)
                except Exception:
                    pass

            return user_input
        except (KeyboardInterrupt, EOFError):
            return ''
        except Exception:
            # If even basic input fails, return empty
            return ''

    def ask_with_default(self, prompt_text: str, default: str = '') -> str:
        """Ask for input with default value."""
        if self.use_fallback:
            full_prompt = f"{prompt_text} [{default}]: " if default else prompt_text
            result = input(full_prompt).strip()
            return result if result else default

        try:
            user_input = prompt(
                prompt_text,
                default=default,
                completer=self.completer,
                complete_while_typing=False,
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
