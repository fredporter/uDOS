"""
uDOS v1.2.22 - Smart Interactive Prompt
Predictive autocomplete with multi-column suggestions.
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText, HTML
from prompt_toolkit.layout import Float, FloatContainer, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.shortcuts import print_formatted_text
from typing import List, Iterable, Optional
import sys
import os

from core.utils.autocomplete import AutocompleteService


class ImprovedCompleter(Completer):
    """Autocomplete provider for command and parameter suggestions."""

    def __init__(self, autocomplete_service: AutocompleteService):
        self.autocomplete = autocomplete_service

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        """Generate command and parameter completions."""
        text = document.text_before_cursor
        words = text.split()

        if not words:
            # Empty input - suggest common/recent commands
            suggestions = self.autocomplete.get_command_suggestions('', max_results=15)
            for sug in suggestions:
                # Build rich meta with syntax and options
                meta_parts = [sug['description'][:40]]
                if sug.get('usage'):
                    meta_parts.append(f"Usage: {sug['usage'][:50]}")
                if sug.get('options'):
                    opts = ', '.join(sug['options'][:4])
                    if len(sug['options']) > 4:
                        opts += f" +{len(sug['options'])-4} more"
                    meta_parts.append(f"Options: {opts}")
                
                yield Completion(
                    sug['command'],
                    start_position=0,
                    display=sug['command'],
                    display_meta=' | '.join(meta_parts)
                )

        elif len(words) == 1 and not text.endswith(' '):
            # First word - command suggestions (show ALL matches, not just top 10)
            partial = words[0]
            suggestions = self.autocomplete.get_command_suggestions(partial, max_results=25)

            for sug in suggestions:
                # Build rich meta with syntax and options
                meta_parts = [sug['description'][:40]]
                if sug.get('usage'):
                    meta_parts.append(f"Usage: {sug['usage'][:50]}")
                if sug.get('options'):
                    opts = ', '.join(sug['options'][:4])
                    if len(sug['options']) > 4:
                        opts += f" +{len(sug['options'])-4} more"
                    meta_parts.append(f"Options: {opts}")
                
                # Replace the partial text with the full command
                yield Completion(
                    sug['command'],
                    start_position=-len(partial),
                    display=sug['command'],
                    display_meta=' | '.join(meta_parts)
                )

        else:
            # Subsequent words - option/parameter suggestions
            current_word = words[-1] if not text.endswith(' ') else ''
            suggestions = self.autocomplete.get_option_suggestions(
                command=words[0],
                partial=current_word,
                max_results=15
            )

            for sug in suggestions:
                option_text = sug.get('option', '')
                cmd_name = sug.get('command', '')
                
                # Build description - NO display_meta, just text
                desc = sug.get('description', '')
                if not desc:
                    desc = f"{cmd_name} {option_text}"
                
                # Create completion with FormattedText (prevents auto-wrapping)
                display_text = FormattedText([('', f"{option_text:<15} - {desc[:60]}")])
                yield Completion(
                    option_text,
                    start_position=-len(current_word) if current_word else 0,
                    display=display_text
                )


class SmartPrompt:
    """Interactive prompt with autocomplete and history."""

    def __init__(self, command_history=None, theme='dungeon', use_fallback=False):
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
        self.tui = None
        self.session = None
        self.selected_completion_index = 0
        
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
                # Completion menu - HIGH CONTRAST
                'completion-menu': 'bg:#000000 #00ff00',
                'completion-menu.completion': 'bg:#000000 #00ff00',
                'completion-menu.completion.current': 'bg:#00ff00 #000000 bold',
                'completion-menu.meta.completion': 'bg:#000000 #888888 italic',
                'completion-menu.meta.completion.current': 'bg:#00ff00 #000000',
                'completion-menu.multi-column-meta': 'bg:#000000 #888888',
            })

        # Test prompt_toolkit
        if not use_fallback:
            self._test_prompt_toolkit()

    def _create_key_bindings(self) -> KeyBindings:
        """Create key bindings for navigation, editing, and completion."""
        kb = KeyBindings()

        @kb.add('tab')
        def _(event):
            if event.current_buffer.complete_state:
                event.current_buffer.complete_next()
            else:
                # Check if we have completions to accept
                text = event.current_buffer.text
                if text:
                    from prompt_toolkit.document import Document
                    doc = Document(text, cursor_position=len(text))
                    comps = list(self.completer.get_completions(doc, None))
                    if comps and self.selected_completion_index < len(comps):
                        selected = comps[self.selected_completion_index]
                        event.current_buffer.text = selected.text
                        event.current_buffer.cursor_position = len(selected.text)
                        self.selected_completion_index = 0
                        event.app.invalidate()
                        return
                event.current_buffer.start_completion()
        
        @kb.add('enter')
        def _(event):
            # If we have completions visible, accept the selected one before executing
            text = event.current_buffer.text
            if text:
                from prompt_toolkit.document import Document
                doc = Document(text, cursor_position=len(text))
                comps = list(self.completer.get_completions(doc, None))
                if comps and self.selected_completion_index < len(comps):
                    selected = comps[self.selected_completion_index]
                    event.current_buffer.text = selected.text
                    event.current_buffer.cursor_position = len(selected.text)
                    self.selected_completion_index = 0
                    event.app.invalidate()
            # Now submit the command
            event.current_buffer.validate_and_handle()
        
        @kb.add('escape')
        def _(event):
            if event.current_buffer.complete_state:
                event.current_buffer.complete_state = None
        
        @kb.add('f1')
        def _(event):
            """Show help for current command (F1 hotkey)."""
            buffer = event.current_buffer
            text = buffer.text.strip()
            
            if text:
                # Extract command name (first word)
                command = text.split()[0].upper()
                
                # Load help handler and show help
                try:
                    from core.commands.help_handler import HelpHandler
                    help_handler = HelpHandler()
                    help_text = help_handler.handle([command])
                    
                    # Print help output
                    print(f"\n{help_text}\n")
                    
                    # Refresh prompt
                    event.app.invalidate()
                except Exception as e:
                    print(f"\n❌ Error loading help: {e}\n")
            else:
                # Show general help
                try:
                    from core.commands.help_handler import HelpHandler
                    help_handler = HelpHandler()
                    help_text = help_handler.handle([])
                    print(f"\n{help_text}\n")
                    event.app.invalidate()
                except Exception as e:
                    print(f"\n❌ Error loading help: {e}\n")
        
        @kb.add('up')
        def _(event):
            if event.current_buffer.complete_state:
                event.current_buffer.complete_previous()
            else:
                # Check if we have completions in toolbar
                text = event.current_buffer.text
                if text:
                    from prompt_toolkit.document import Document
                    doc = Document(text, cursor_position=len(text))
                    comps = list(self.completer.get_completions(doc, None))
                    if comps:
                        self.selected_completion_index = max(0, self.selected_completion_index - 1)
                        event.app.invalidate()
                        return
                event.current_buffer.history_backward()
        
        @kb.add('down')
        def _(event):
            if event.current_buffer.complete_state:
                event.current_buffer.complete_next()
            else:
                # Check if we have completions in toolbar
                text = event.current_buffer.text
                if text:
                    from prompt_toolkit.document import Document
                    doc = Document(text, cursor_position=len(text))
                    comps = list(self.completer.get_completions(doc, None))
                    if comps:
                        self.selected_completion_index = min(len(comps) - 1, self.selected_completion_index + 1)
                        event.app.invalidate()
                        return
                event.current_buffer.history_forward()
        
        @kb.add('right')
        def _(event):
            if event.current_buffer.complete_state:
                event.current_buffer.complete_state = None
            else:
                event.current_buffer.cursor_right()
        
        @kb.add('8')
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                # Priority 1: If completion menu is open, ALWAYS navigate
                if event.current_buffer.complete_state:
                    event.current_buffer.complete_previous()
                # Priority 2: If buffer is empty, navigate history/pager
                elif len(event.current_buffer.text) == 0:
                    if hasattr(self.tui, 'pager') and self.tui.pager:
                        from core.ui.pager import ScrollDirection
                        self.tui.pager.scroll(ScrollDirection.UP)
                    else:
                        event.current_buffer.history_backward()
                # Priority 3: Text present and no menu = insert digit
                else:
                    event.current_buffer.insert_text('8')
            else:
                # Insert '8' normally when keypad disabled
                event.current_buffer.insert_text('8')

        @kb.add('2')
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                if event.current_buffer.complete_state:
                    event.current_buffer.complete_next()
                elif len(event.current_buffer.text) == 0:
                    if hasattr(self.tui, 'pager') and self.tui.pager:
                        from core.ui.pager import ScrollDirection
                        self.tui.pager.scroll(ScrollDirection.DOWN)
                    else:
                        event.current_buffer.history_forward()
                else:
                    event.current_buffer.insert_text('2')
            else:
                event.current_buffer.insert_text('2')

        @kb.add('4')
        def _(event):
            if self.tui and self.tui.keypad.enabled and len(event.current_buffer.text) == 0:
                if hasattr(self.tui, 'pager') and self.tui.pager:
                    from core.ui.pager import ScrollDirection
                    self.tui.pager.scroll(ScrollDirection.PAGE_UP)
            else:
                event.current_buffer.insert_text('4')

        @kb.add('6')
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                if event.current_buffer.complete_state:
                    event.current_buffer.complete_state = None
                elif len(event.current_buffer.text) == 0:
                    if hasattr(self.tui, 'pager') and self.tui.pager:
                        from core.ui.pager import ScrollDirection
                        self.tui.pager.scroll(ScrollDirection.PAGE_DOWN)
                else:
                    event.current_buffer.insert_text('6')
            else:
                event.current_buffer.insert_text('6')

        @kb.add('5')
        def _(event):
            if self.tui and self.tui.keypad.enabled:
                if event.current_buffer.complete_state:
                    event.current_buffer.complete_state = None
                elif len(event.current_buffer.text) == 0:
                    event.current_buffer.validate_and_handle()
                else:
                    event.current_buffer.insert_text('5')
            else:
                event.current_buffer.insert_text('5')

        @kb.add('1')
        def _(event):
            if self.tui and self.tui.keypad.enabled and len(event.current_buffer.text) == 0:
                event.current_buffer.history_backward()
            else:
                event.current_buffer.insert_text('1')

        @kb.add('3')
        def _(event):
            if self.tui and self.tui.keypad.enabled and len(event.current_buffer.text) == 0:
                event.current_buffer.history_forward()
            else:
                event.current_buffer.insert_text('3')

        @kb.add('7')
        def _(event):
            if self.tui and self.tui.keypad.enabled and len(event.current_buffer.text) == 0:
                event.current_buffer.undo()
            else:
                event.current_buffer.insert_text('7')

        @kb.add('9')
        def _(event):
            if self.tui and self.tui.keypad.enabled and len(event.current_buffer.text) == 0:
                if hasattr(event.current_buffer, '_redo_stack') and event.current_buffer._redo_stack:
                    event.current_buffer.redo()
            else:
                event.current_buffer.insert_text('9')

        @kb.add('0')
        def _(event):
            if not (self.tui and self.tui.keypad.enabled and len(event.current_buffer.text) == 0):
                event.current_buffer.insert_text('0')

        @kb.add('c-a')
        def _(event):
            event.current_buffer.cursor_position = 0

        @kb.add('c-e')
        def _(event):
            event.current_buffer.cursor_position = len(event.current_buffer.text)

        @kb.add('c-b')
        def _(event):
            event.current_buffer.cursor_left()

        @kb.add('c-f')
        def _(event):
            event.current_buffer.cursor_right()

        @kb.add('c-k')
        def _(event):
            event.current_buffer.delete(count=len(event.current_buffer.text) - event.current_buffer.cursor_position)

        @kb.add('c-u')
        def _(event):
            event.current_buffer.delete_before_cursor(count=event.current_buffer.cursor_position)

        @kb.add('c-w')
        def _(event):
            event.current_buffer.delete_before_cursor(count=event.current_buffer.document.find_start_of_previous_word())

        @kb.add('c-d')
        def _(event):
            event.current_buffer.delete()

        @kb.add('c-l')
        def _(event):
            event.app.renderer.clear()

        @kb.add('c-p')
        def _(event):
            if event.current_buffer.complete_state:
                event.current_buffer.complete_previous()
            else:
                event.current_buffer.history_backward()

        @kb.add('c-n')
        def _(event):
            if event.current_buffer.complete_state:
                event.current_buffer.complete_next()
            else:
                event.current_buffer.history_forward()

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
    
    def _show_ready_cursor(self):
        """Show blinking white block cursor after prompt (3 blinks)."""
        import time
        import sys
        
        for _ in range(3):
            sys.stdout.write('\033[97m█\033[0m')  # White block
            sys.stdout.flush()
            time.sleep(0.15)
            sys.stdout.write('\b \b')  # Backspace, space, backspace
            sys.stdout.flush()
            time.sleep(0.15)

    def ask(self, prompt_text: str = "🌀 ", multiline: bool = False, show_shortcuts: bool = True) -> str:
        """Display prompt and get user input with autocomplete."""
        if self.tui and self.tui.keypad.enabled:
            print("┌─ Nav: 8↑ 2↓ 4← 6→ 5✓ | Help: F1 | History: Ctrl+R ↑/↓ | Edit: Ctrl+A/E/K/U/W ─┐")

        if self.use_fallback:
            return self._ask_fallback(prompt_text)

        try:
            if self.session is None:
                from prompt_toolkit import PromptSession
                from prompt_toolkit.shortcuts import CompleteStyle
                from prompt_toolkit.document import Document
                
                # Bottom toolbar showing completions OR pager
                def get_bottom_toolbar():
                    if not hasattr(self.session, 'app') or not self.session.app:
                        return ""
                    
                    try:
                        # Priority 1: Check if pager has content to show
                        if self.tui and hasattr(self.tui, 'pager') and self.tui.pager:
                            pager = self.tui.pager
                            if pager.state.total_lines > 0:
                                # Show pager status bar
                                current_page = (pager.state.scroll_offset // pager.state.viewport_height) + 1
                                total_pages = (pager.state.total_lines // pager.state.viewport_height) + 1
                                progress_pct = int(pager.state.scroll_percentage * 100)
                                
                                # Progress bar (60 chars wide)
                                filled = int(60 * pager.state.scroll_percentage)
                                bar = '█' * filled + '░' * (60 - filled)
                                
                                return f"{bar} Page {current_page}/{total_pages} [↓→/ENTER|↑←|ESC]"
                        
                        # Priority 2: Show completions if typing
                        buffer = self.session.app.current_buffer
                        text = buffer.text
                        
                        if not text:
                            self.selected_completion_index = 0
                            return ""
                        
                        # Get completions for current text
                        doc = Document(text, cursor_position=len(text))
                        completions = list(self.completer.get_completions(doc, None))
                        
                        if not completions:
                            self.selected_completion_index = 0
                            return ""
                        
                        # Ensure index is valid
                        self.selected_completion_index = min(self.selected_completion_index, len(completions) - 1)
                        
                        # Show first 5 completions
                        lines = []
                        for i, comp in enumerate(completions[:5]):
                            marker = "►" if i == self.selected_completion_index else " "
                            lines.append(f"{marker} {comp.text:<12} │ {comp.display_meta}")
                        
                        return "\n".join(lines)
                    except:
                        return ""
                
                self.session = PromptSession(
                    completer=self.completer,
                    complete_while_typing=True,
                    complete_style=CompleteStyle.COLUMN,
                    history=self.pt_history,
                    key_bindings=self.key_bindings,
                    style=self.style,
                    enable_history_search=True,
                    mouse_support=False,
                    reserve_space_for_menu=10,
                    complete_in_thread=False,
                    validate_while_typing=False,
                    bottom_toolbar=get_bottom_toolbar,
                )
            
            # Show keyboard shortcuts header if enabled
            import sys
            if show_shortcuts:
                # Get terminal width
                try:
                    import shutil
                    term_width = shutil.get_terminal_size().columns
                except:
                    term_width = 80
                
                # Right-aligned shortcuts line
                shortcuts = "Ctrl+A/E/K/U/W ─┐"
                padding = " " * (term_width - len(shortcuts))
                sys.stdout.write(f"\n{padding}{shortcuts}\n")
                sys.stdout.flush()
            
            # Show prompt with blinking cursor
            sys.stdout.write(prompt_text)
            sys.stdout.flush()
            self._show_ready_cursor()
            
            formatted_prompt = FormattedText([('class:prompt', prompt_text)])
            user_input = self.session.prompt(formatted_prompt, multiline=multiline)

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
        """Fallback using plain input()."""
        try:
            user_input = input(prompt_text).strip()
            if self.command_history and user_input:
                try:
                    self.command_history.append_string(user_input)
                except Exception:
                    pass
            return user_input
        except (KeyboardInterrupt, EOFError):
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
