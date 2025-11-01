# uDOS v1.0.0 - Enhanced Prompt System

import time
import sys
from prompt_toolkit.formatted_text import FormattedText, ANSI

class SmartPrompt:
    """
    Enhanced prompt system with emoji, flash effect, and smart context.
    """

    def __init__(self):
        # Emoji options for different states
        self.ready_emoji = "🌀"  # Ready for input (Cyclone - dynamic, fluid)
        self.assist_emoji = "🧙"  # Assist mode
        self.working_emoji = "⚙️"  # Processing
        self.error_emoji = "⚠️"   # Error state

        # ANSI escape codes
        self.HIDE_CURSOR = '\033[?25l'
        self.SHOW_CURSOR = '\033[?25h'
        self.CLEAR_LINE = '\033[2K\r'

    def flash_prompt(self, emoji, times=3, delay=0.1):
        """
        Flash the prompt emoji to indicate ready state.

        Args:
            emoji (str): The emoji to flash
            times (int): Number of flashes
            delay (float): Delay between flashes in seconds
        """
        try:
            # Hide cursor during flash
            sys.stdout.write(self.HIDE_CURSOR)
            sys.stdout.flush()

            for _ in range(times):
                # Show emoji
                sys.stdout.write(f"\r{emoji} ")
                sys.stdout.flush()
                time.sleep(delay)

                # Clear
                sys.stdout.write(self.CLEAR_LINE)
                sys.stdout.flush()
                time.sleep(delay * 0.5)

            # Show cursor again
            sys.stdout.write(self.SHOW_CURSOR)
            sys.stdout.flush()
        except:
            # If flash fails, just continue
            pass

    def get_prompt(self, is_assist_mode=False, panel_name="main", flash=True):
        """
        Get the formatted prompt string.

        Args:
            is_assist_mode (bool): Whether assist mode is active
            panel_name (str): Current active panel
            flash (bool): Whether to flash before showing prompt

        Returns:
            str: Formatted prompt string
        """
        # Choose emoji based on mode
        emoji = self.assist_emoji if is_assist_mode else self.ready_emoji

        # Flash if enabled
        if flash:
            self.flash_prompt(emoji, times=3, delay=0.08)

        # Simple emoji prompt with minimal context
        return f"{emoji} "

    def get_rich_prompt(self, project_name, panel_name, is_assist_mode=False):
        """
        Get a richer prompt with more context (optional mode).

        Returns:
            FormattedText: Formatted text for prompt_toolkit
        """
        emoji = self.assist_emoji if is_assist_mode else self.ready_emoji
        assist_tag = "[ASSIST]" if is_assist_mode else ""

        # Create formatted text with colors
        return FormattedText([
            ('class:emoji', emoji),
            ('', ' '),
            ('class:project', f'[{project_name}]'),
            ('', ' '),
            ('class:panel', f'({panel_name})'),
            ('', ' '),
            ('class:assist', assist_tag),
            ('', ' '),
        ])

    def get_context_hint(self, last_command=None, panel_content_length=0):
        """
        Generate smart context hints based on current state.

        Args:
            last_command (str): The last executed command
            panel_content_length (int): Length of current panel content

        Returns:
            str: Context hint or empty string
        """
        hints = []

        # Suggest based on last command
        if last_command:
            if last_command.startswith('LOAD'):
                hints.append("💡 Try: SHOW to view content")
            elif last_command.startswith('CATALOG'):
                hints.append("💡 Try: LOAD \"<file>\" to open a file")
            elif last_command.startswith('GRID PANEL CREATE'):
                hints.append("💡 Try: SHOW \"<panel>\" to view it")
            elif last_command.startswith('ASK'):
                hints.append("💡 Try: SHOW to see the response")

        # Suggest based on panel state
        if panel_content_length > 100:
            hints.append("💡 Panel has content - try SAVE or ANALYZE")

        return "\n".join(hints) if hints else ""

    def format_command_chain_hint(self, command):
        """
        Suggest command chains based on what user just typed.

        Args:
            command (str): Command being typed

        Returns:
            str: Suggestion for next command in chain
        """
        chains = {
            'LOAD': '→ SHOW → ANALYZE',
            'CATALOG': '→ LOAD → EDIT',
            'ASK': '→ SHOW → SAVE',
            'GRID PANEL CREATE': '→ LOAD → SAVE',
            'UNDO': '→ REDO (if needed)',
            'RESTORE': '→ LIST first to see sessions',
        }

        for cmd, chain in chains.items():
            if command.upper().startswith(cmd):
                return f"\n   Chain: {cmd} {chain}"

        return ""
