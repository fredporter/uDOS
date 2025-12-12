"""
uDOS v1.2.22 - Smart Interactive Prompt
Dynamic real-time autocomplete with visual feedback.
Features:
- Auto-show completions as you type
- Multi-word command support (POKE START, CLOUD GENERATE, etc.)
- Smart selection with arrow keys
- Tab/Right-Arrow to accept suggestion
- Syntax highlighting for commands/options/variables
"""

from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText, HTML
from prompt_toolkit.layout import Float, FloatContainer, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.shortcuts import print_formatted_text, CompleteStyle
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.validation import Validator
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.document import Document
from typing import List, Iterable, Optional
import sys
import os

from core.utils.autocomplete import AutocompleteService


class ImprovedCompleter(Completer):
    """Dynamic autocomplete with real-time suggestions as you type."""

    def __init__(self, autocomplete_service: AutocompleteService):
        self.autocomplete = autocomplete_service
        self.multi_word_commands = self._build_multi_word_index()

    def _build_multi_word_index(self) -> dict:
        """Build index of multi-word commands for smart matching."""
        multi_word = {}
        
        # Known multi-word command patterns
        patterns = {
            'POKE': ['START', 'STOP', 'STATUS', 'EXPORT', 'IMPORT'],
            'CLOUD': ['GENERATE', 'RESOLVE', 'BUSINESS', 'EMAIL', 'CONTACTS', 'WEBSITE', 
                     'SOCIAL', 'ENRICH', 'LINK', 'PRUNE', 'EXPORT', 'STATS'],
            'CONFIG': ['GET', 'SET', 'LIST', 'CHECK', 'FIX', 'BACKUP', 'RESTORE'],
            'WORKFLOW': ['NEW', 'LIST', 'RUN', 'PAUSE', 'RESUME', 'STOP', 'STATUS'],
            'MISSION': ['NEW', 'LIST', 'START', 'PAUSE', 'RESUME', 'COMPLETE', 'FAIL'],
            'TUI': ['ENABLE', 'DISABLE', 'STATUS'],
            'GUIDE': ['WATER', 'FIRE', 'SHELTER', 'FOOD', 'MEDICAL', 'NAVIGATION'],
        }
        
        for base_cmd, subcmds in patterns.items():
            multi_word[base_cmd] = subcmds
        
        return multi_word

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        """Generate completions with real-time feedback."""
        text = document.text_before_cursor
        words = text.split()

        # Empty input - show common commands
        if not words:
            for sug in self.autocomplete.get_command_suggestions('', max_results=20):
                yield Completion(sug['command'], start_position=0, 
                               display=sug['command'], display_meta=self._build_meta(sug))
            return
        
        # Space after command - show subcommands
        if len(words) == 1 and text.endswith(' '):
            base_cmd = words[0].upper()
            if base_cmd in self.multi_word_commands:
                for subcmd in self.multi_word_commands[base_cmd]:
                    desc = f"{base_cmd} {subcmd} - {self._get_subcmd_desc(base_cmd, subcmd)}"
                    yield Completion(subcmd, start_position=0, display=subcmd, display_meta=desc[:80])
                return

        # First word - command suggestions
        if len(words) == 1 and not text.endswith(' '):
            partial = words[0].upper()
            for sug in self.autocomplete.get_command_suggestions(partial, max_results=30):
                yield Completion(sug['command'], start_position=-len(partial), 
                               display=sug['command'], display_meta=self._build_meta(sug))
            return

        # Multi-word command detection (POKE START, CLOUD GENERATE, etc.)
        if len(words) >= 2 and (base_cmd := words[0].upper()) in self.multi_word_commands:
            second_word = words[1] if not text.endswith(' ') else ''
            
            # Match second-word completions (even single characters!)
            if len(words) == 2 and not text.endswith(' '):
                second_upper = second_word.upper()
                
                for subcmd in self.multi_word_commands[base_cmd]:
                    if not second_word or subcmd.startswith(second_upper):
                        desc = f"{base_cmd} {subcmd} - {self._get_subcmd_desc(base_cmd, subcmd)}"
                        yield Completion(
                            subcmd,
                            start_position=-len(second_word) if second_word else 0,
                            display=subcmd,
                            display_meta=desc[:80]
                        )
                return  # Early return after multi-word matches
            
            # After multi-word command, show options/parameters
            if len(words) > 2 or (len(words) == 2 and text.endswith(' ')):
                current_word = words[-1] if not text.endswith(' ') else ''
                full_cmd = f"{base_cmd} {words[1].upper()}"
                
                # Get options for the full multi-word command
                for sug in self.autocomplete.get_option_suggestions(full_cmd, partial=current_word, max_results=20):
                    option_text = sug.get('option', '')
                    desc = sug.get('description', f"{full_cmd} {option_text}")
                    yield Completion(option_text, start_position=-len(current_word) if current_word else 0,
                                   display=option_text, display_meta=desc[:80])
                return

        # Default: option/parameter suggestions
        current_word = words[-1] if not text.endswith(' ') else ''
        for sug in self.autocomplete.get_option_suggestions(words[0], partial=current_word, max_results=20):
            option_text = sug.get('option', '')
            desc = sug.get('description', f"{words[0]} {option_text}")
            yield Completion(option_text, start_position=-len(current_word) if current_word else 0,
                           display=option_text, display_meta=desc[:80])

    @staticmethod
    def _extract_meta_text(meta) -> str:
        """Extract plain text from FormattedText or return as-is."""
        if isinstance(meta, str):
            return meta
        if hasattr(meta, '__iter__'):
            try:
                return ''.join(part[1] for part in meta)
            except:
                pass
        return str(meta)
    
    def _build_meta(self, sug: dict) -> str:
        """Build rich metadata display for suggestions."""
        meta_parts = [sug['description'][:50]]
        
        if sug.get('options') and len(sug['options']) > 0:
            opts = ', '.join(sug['options'][:3])
            if len(sug['options']) > 3:
                opts += f" +{len(sug['options'])-3}"
            meta_parts.append(f"→ {opts}")
        
        return ' | '.join(meta_parts)
    
    # Subcommand descriptions - centralized data
    SUBCOMMAND_DESCRIPTIONS = {
        'CLOUD': {
            'GENERATE': 'Generate keywords with AI', 'RESOLVE': 'Convert address to TILE code',
            'BUSINESS': 'Search for businesses', 'EMAIL': 'Email operations',
            'CONTACTS': 'Contact management', 'WEBSITE': 'Parse website data',
            'SOCIAL': 'Social media enrichment', 'ENRICH': 'Enrich data with APIs',
            'LINK': 'Link messages/data', 'PRUNE': 'Archive old data',
            'EXPORT': 'Export data (CSV/JSON)', 'STATS': 'Show statistics'
        },
        'POKE': {
            'START': 'Start Pokémon battle', 'STOP': 'Stop current battle',
            'STATUS': 'Show battle status', 'EXPORT': 'Export battle data',
            'IMPORT': 'Import Pokémon data'
        },
        'CONFIG': {
            'GET': 'Get configuration value', 'SET': 'Set configuration value',
            'LIST': 'List all configurations', 'CHECK': 'Check configuration validity',
            'FIX': 'Fix configuration issues', 'BACKUP': 'Backup configurations',
            'RESTORE': 'Restore from backup'
        }
    }
    
    def _get_subcmd_desc(self, base_cmd: str, subcmd: str) -> str:
        """Get description for any subcommand."""
        return self.SUBCOMMAND_DESCRIPTIONS.get(base_cmd, {}).get(subcmd, f'{subcmd.lower()} operation')


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

        # Create key bindings
        if not use_fallback:
            self.key_bindings = self._create_key_bindings()
            self.style = Style.from_dict({
                # Prompt styling
                'prompt': 'ansigreen bold',
                '': '',
                
                # Auto-suggest from history (gray ghost text)
                'auto-suggestion': 'fg:#666666',
                
                # Completion menu - HIGH CONTRAST with clear selection
                'completion-menu': 'bg:#001100 #00ff00',
                'completion-menu.completion': 'bg:#000000 #00ff00',
                'completion-menu.completion.current': 'bg:#00ff00 #000000 bold',
                
                # Metadata (description) styling
                'completion-menu.meta': 'bg:#000000 #00aa00 italic',
                'completion-menu.meta.completion': 'bg:#000000 #888888 italic',
                'completion-menu.meta.completion.current': 'bg:#00ff00 #000000',
                
                # Multi-column layout
                'completion-menu.multi-column-meta': 'bg:#000000 #00aa00',
                
                # Scrollbar
                'scrollbar.background': 'bg:#000000',
                'scrollbar.button': 'bg:#00ff00',
            })

        # Test prompt_toolkit
        if not use_fallback:
            self._test_prompt_toolkit()

    def _create_key_bindings(self) -> KeyBindings:
        """Create intuitive key bindings for smart input."""
        kb = KeyBindings()

        @kb.add('tab')
        def _(event):
            """Tab: Accept current completion or complete first match."""
            buffer = event.current_buffer
            
            # If completions are visible, accept the current one
            if buffer.complete_state:
                current_completion = buffer.complete_state.current_completion
                if current_completion:
                    buffer.apply_completion(current_completion)
            else:
                # Start completion and auto-accept first match if only one
                buffer.start_completion(select_first=True)
                
                # If exactly one completion, auto-accept it
                if buffer.complete_state and len(buffer.complete_state.completions) == 1:
                    buffer.apply_completion(buffer.complete_state.current_completion)
        
        @kb.add('c-space')
        def _(event):
            """Ctrl+Space: Force show all completions."""
            buffer = event.current_buffer
            buffer.start_completion(select_first=True)
        
        @kb.add('enter')
        def _(event):
            """Enter: Execute command (no auto-accept)."""
            buffer = event.current_buffer
            
            # Close completion menu if open
            if buffer.complete_state:
                buffer.complete_state = None
            
            # Submit the actual typed text
            buffer.validate_and_handle()
        
        @kb.add('escape')
        def _(event):
            """Escape: Close completion menu or clear buffer."""
            buffer = event.current_buffer
            if buffer.complete_state:
                buffer.complete_state = None
            elif buffer.text:
                # Clear the input
                buffer.reset()
            else:
                # Exit gracefully
                event.app.exit(result='EXIT')
        
        @kb.add('right')
        def _(event):
            """Right arrow: Accept completion or move cursor."""
            buffer = event.current_buffer
            
            # If at end of line and completion available, accept it
            if buffer.cursor_position == len(buffer.text) and buffer.complete_state:
                buffer.apply_completion(buffer.complete_state.current_completion)
            else:
                # Normal cursor movement
                buffer.cursor_right()
        
        @kb.add('left')
        def _(event):
            """Left arrow: Move cursor (close completion if at start)."""
            buffer = event.current_buffer
            if buffer.cursor_position == 0 and buffer.complete_state:
                buffer.complete_state = None
            else:
                buffer.cursor_left()
        
        @kb.add('up')
        def _(event):
            """Up: Navigate completions or history."""
            buffer = event.current_buffer
            if buffer.complete_state:
                buffer.complete_previous()
            else:
                buffer.history_backward()
        
        @kb.add('down')
        def _(event):
            """Down: Navigate completions or history."""
            buffer = event.current_buffer
            if buffer.complete_state:
                buffer.complete_next()
            else:
                buffer.history_forward()
        
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
            # Initialize session on first use
            if self.session is None:
                def get_bottom_toolbar():
                    """Show completions in bottom toolbar (up to 3 lines)."""
                    from prompt_toolkit.application.current import get_app
                    
                    app = get_app()
                    if not app or not hasattr(app, 'current_buffer'):
                        return FormattedText([('', '🔍 Ready...')])  # Show we're active
                    
                    buffer = app.current_buffer
                    
                    # Show current text length as debug
                    text = buffer.text if buffer else ''
                    
                    if not buffer or not buffer.complete_state:
                        # Show that we're waiting for completions
                        if text:
                            return FormattedText([('class:completion-menu.completion', f' 🔍 Typing: "{text}" (press TAB for options)')])
                        return FormattedText([('class:completion-menu.completion', ' 🔍 Type a command...')])
                    
                    # Get completions from current state
                    completions = buffer.complete_state.completions
                    if not completions:
                        return FormattedText([('class:completion-menu.completion', ' ⚠️ No matches')])
                    
                    # Format up to 9 completions (3 lines × 3 per line)
                    items = []
                    for i, comp in enumerate(completions[:9]):
                        if i > 0 and i % 3 == 0:
                            items.append(('', '\n'))  # New line every 3 items
                        
                        # Get display text
                        display = comp.display_text if hasattr(comp, 'display_text') else comp.text
                        meta = comp.display_meta_text if hasattr(comp, 'display_meta_text') else ''
                        
                        # Format: [display] meta
                        if meta:
                            items.append(('class:completion-menu.completion', f' [{display}] '))
                            items.append(('class:completion-menu.meta', meta[:40]))  # Truncate meta
                        else:
                            items.append(('class:completion-menu.completion', f' [{display}] '))
                        
                        # Add separator if not last
                        if i < len(completions) - 1 and (i + 1) % 3 != 0:
                            items.append(('', '  '))
                    
                    return FormattedText(items)
                
                self.session = PromptSession(
                    completer=self.completer,
                    complete_while_typing=True,  # Show completions as you type!
                    history=self.pt_history,
                    key_bindings=self.key_bindings,
                    style=self.style,
                    enable_history_search=True,
                    mouse_support=False,
                    complete_in_thread=True,  # Allow async completion
                    validate_while_typing=False,
                    auto_suggest=AutoSuggestFromHistory(),
                    editing_mode=EditingMode.EMACS,
                    bottom_toolbar=get_bottom_toolbar,  # Dynamic toolbar
                    reserve_space_for_menu=0,  # Don't reserve - let toolbar handle it
                    refresh_interval=0.1,  # Refresh every 100ms for live updates
                )
            
            # Simple formatted prompt
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
