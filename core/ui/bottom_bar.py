"""
Bottom Bar TUI - Integrated Command Line + Completions + Pager (v1.2.22)

Provides a 2-3 line bottom bar that shows:
- Line 1: Command input with inline completion preview
- Line 2: Top completion suggestion (auto-updating)
- Line 3: Pager scroll indicator (when content scrollable)

Features:
- Auto-updating completions as you type (no Tab needed)
- Visual completion preview in gray
- Seamless pager integration
- Compact 2-3 line footprint
"""

from typing import List, Optional, Tuple
from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style


class BottomBar:
    """
    Integrated bottom bar for command input, completions, and pager.
    
    Layout:
    ┌────────────────────────────────────────────────┐
    │ (scrollable output area)                       │
    │                                                │
    ├────────────────────────────────────────────────┤
    │ > command_here [preview: COMMAND]         ▲ 45%│  ← Input + preview + scroll
    │   COMMAND        - Command description        │  ← Top suggestion
    └────────────────────────────────────────────────┘
    """
    
    def __init__(self, autocomplete_service, pager=None):
        self.autocomplete = autocomplete_service
        self.pager = pager
        self.current_suggestions = []
        self.selected_index = 0
        
    def get_inline_completion(self, text: str) -> str:
        """Get inline completion preview for current text."""
        if not text:
            return ""
        
        suggestions = self.autocomplete.get_command_suggestions(text, max_results=1)
        if suggestions:
            suggestion = suggestions[0]['command']
            # Return the part that completes the current text
            if suggestion.upper().startswith(text.upper()):
                return suggestion[len(text):]
        return ""
    
    def get_suggestions(self, text: str, max_results: int = 3) -> List[dict]:
        """Get completion suggestions for current text."""
        if not text:
            return self.autocomplete.get_command_suggestions('', max_results=5)
        return self.autocomplete.get_command_suggestions(text, max_results=max_results)
    
    def format_suggestion_line(self, suggestion: dict, is_selected: bool = False) -> str:
        """Format a single suggestion for display."""
        cmd = suggestion['command']
        desc = suggestion['description'][:40]
        
        if is_selected:
            return f"  ► {cmd:<12} - {desc}"
        else:
            return f"    {cmd:<12} - {desc}"
    
    def render_bottom_bar(self, current_text: str) -> List[str]:
        """
        Render the bottom bar (2-3 lines).
        
        Returns:
            List of formatted lines to display
        """
        lines = []
        
        # Line 1: Input with inline preview
        inline = self.get_inline_completion(current_text)
        scroll_indicator = ""
        
        if self.pager and self.pager.state.total_lines > self.pager.state.viewport_height:
            pct = int(self.pager.state.scroll_percentage * 100)
            if not self.pager.state.at_bottom:
                scroll_indicator = f"▲ {pct}%"
            else:
                scroll_indicator = "▼ 100%"
        
        # Format: "🌀 text[preview]     indicator"
        preview_text = f"\x1b[90m{inline}\x1b[0m" if inline else ""
        padding = " " * (60 - len(current_text) - len(inline))
        input_line = f"🌀 {current_text}{preview_text}{padding}{scroll_indicator}"
        lines.append(input_line)
        
        # Line 2: Top suggestion (if available)
        suggestions = self.get_suggestions(current_text, max_results=3)
        if suggestions:
            lines.append(self.format_suggestion_line(suggestions[0], is_selected=True))
            
            # Line 3: Second suggestion (optional)
            if len(suggestions) > 1:
                lines.append(self.format_suggestion_line(suggestions[1], is_selected=False))
        
        return lines


def create_bottom_bar(autocomplete_service, pager=None):
    """Factory function to create BottomBar instance."""
    return BottomBar(autocomplete_service, pager)
