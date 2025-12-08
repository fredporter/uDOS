"""
Enhanced Pager with Scroll-While-Prompting (v1.2.13)

Provides advanced paging controls:
- Scroll through output while typing new commands
- Preserve scroll position across commands
- Visual scroll indicators
- Immediate command entry without clearing output
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
from enum import Enum
import shutil


class ScrollDirection(Enum):
    """Scroll movement direction"""
    UP = "up"
    DOWN = "down"
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"
    TOP = "top"
    BOTTOM = "bottom"


@dataclass
class PagerState:
    """Current pager state"""
    lines: List[str] = None
    offset: int = 0
    viewport_height: int = 20
    preserve_scroll: bool = True
    show_indicators: bool = True
    
    def __post_init__(self):
        if self.lines is None:
            self.lines = []
    
    @property
    def total_lines(self) -> int:
        return len(self.lines)
    
    @property
    def max_offset(self) -> int:
        return max(0, self.total_lines - self.viewport_height)
    
    @property
    def scroll_percentage(self) -> float:
        """Current scroll position as percentage (0.0 - 1.0)"""
        if self.total_lines <= self.viewport_height:
            return 1.0
        return self.offset / self.max_offset if self.max_offset > 0 else 0.0
    
    @property
    def at_top(self) -> bool:
        return self.offset == 0
    
    @property
    def at_bottom(self) -> bool:
        return self.offset >= self.max_offset


class Pager:
    """
    Enhanced terminal pager with scroll-while-prompting.
    
    Features:
    - Navigate large outputs with space/arrows
    - Keep output visible while typing new command
    - Visual scroll indicators (▲ ▼)
    - Preserve scroll position option
    - Configurable viewport height
    """
    
    def __init__(self, preserve_scroll: bool = True):
        self.state = PagerState(preserve_scroll=preserve_scroll)
        self.command_buffer = ""
        self.in_command_mode = False
        
        # Get terminal size
        try:
            terminal_size = shutil.get_terminal_size()
            self.state.viewport_height = terminal_size.lines - 3  # Leave room for prompt
        except:
            self.state.viewport_height = 20
    
    def set_content(self, lines: List[str], reset_scroll: bool = None):
        """
        Set new content to display.
        
        Args:
            lines: List of output lines
            reset_scroll: Override preserve_scroll setting
        """
        self.state.lines = lines
        
        # Reset scroll if requested or not preserving
        if reset_scroll is True or (reset_scroll is None and not self.state.preserve_scroll):
            self.state.offset = 0
        else:
            # Clamp offset to new content
            self.state.offset = min(self.state.offset, self.state.max_offset)
    
    def scroll(self, direction: ScrollDirection) -> bool:
        """
        Scroll in specified direction.
        
        Returns:
            True if scrolled, False if already at limit
        """
        old_offset = self.state.offset
        
        if direction == ScrollDirection.UP:
            self.state.offset = max(0, self.state.offset - 1)
        elif direction == ScrollDirection.DOWN:
            self.state.offset = min(self.state.max_offset, self.state.offset + 1)
        elif direction == ScrollDirection.PAGE_UP:
            self.state.offset = max(0, self.state.offset - self.state.viewport_height)
        elif direction == ScrollDirection.PAGE_DOWN:
            self.state.offset = min(self.state.max_offset, 
                                   self.state.offset + self.state.viewport_height)
        elif direction == ScrollDirection.TOP:
            self.state.offset = 0
        elif direction == ScrollDirection.BOTTOM:
            self.state.offset = self.state.max_offset
        
        return old_offset != self.state.offset
    
    def get_viewport(self) -> List[str]:
        """Get current viewport of visible lines"""
        start = self.state.offset
        end = start + self.state.viewport_height
        return self.state.lines[start:end]
    
    def render(self, include_indicators: bool = True) -> str:
        """
        Render current viewport with scroll indicators.
        
        Args:
            include_indicators: Show scroll position indicators
            
        Returns:
            Formatted output string
        """
        lines = []
        
        # Add scroll indicator at top
        if include_indicators and self.state.show_indicators:
            if not self.state.at_top:
                lines.append("▲ (More above - Press 8 or PgUp to scroll)")
            else:
                lines.append("─" * 60)
        
        # Add viewport content
        viewport = self.get_viewport()
        lines.extend(viewport)
        
        # Add scroll indicator at bottom
        if include_indicators and self.state.show_indicators:
            if not self.state.at_bottom:
                scroll_pct = int(self.state.scroll_percentage * 100)
                lines.append(f"▼ (More below - {scroll_pct}% - Press 2 or PgDn to scroll)")
            else:
                lines.append("─" * 60)
        
        return "\n".join(lines)
    
    def handle_key(self, key: str) -> Optional[str]:
        """
        Handle keypress for paging control.
        
        Args:
            key: Key character or code
            
        Returns:
            Action taken ("scrolled", "passthrough", etc.) or None
        """
        # Map keys to scroll actions
        scroll_keys = {
            '8': ScrollDirection.UP,
            '2': ScrollDirection.DOWN,
            ' ': ScrollDirection.PAGE_DOWN,  # Space = page down
            'k': ScrollDirection.UP,
            'j': ScrollDirection.DOWN,
            'g': ScrollDirection.TOP,
            'G': ScrollDirection.BOTTOM,
        }
        
        # Check for special keys (terminal codes)
        if key == '\x1b[A':  # Up arrow
            direction = ScrollDirection.UP
        elif key == '\x1b[B':  # Down arrow
            direction = ScrollDirection.DOWN
        elif key == '\x1b[5~':  # Page Up
            direction = ScrollDirection.PAGE_UP
        elif key == '\x1b[6~':  # Page Down
            direction = ScrollDirection.PAGE_DOWN
        elif key in scroll_keys:
            direction = scroll_keys[key]
        else:
            # Not a paging key, pass through
            return "passthrough"
        
        # Attempt scroll
        if self.scroll(direction):
            return "scrolled"
        else:
            return "limit"
    
    def enter_command_mode(self):
        """Switch to command input while keeping output visible"""
        self.in_command_mode = True
    
    def exit_command_mode(self):
        """Exit command mode"""
        self.in_command_mode = False
        self.command_buffer = ""
    
    def is_paging_needed(self) -> bool:
        """Check if content requires paging"""
        return self.state.total_lines > self.state.viewport_height
    
    def get_status_line(self) -> str:
        """Get status line showing scroll position"""
        if not self.is_paging_needed():
            return ""
        
        current_line = self.state.offset + 1
        visible_end = min(self.state.offset + self.state.viewport_height, 
                         self.state.total_lines)
        total = self.state.total_lines
        pct = int(self.state.scroll_percentage * 100)
        
        return f"Lines {current_line}-{visible_end} of {total} ({pct}%)"
    
    def split_output_and_prompt(self, full_output: str, prompt: str) -> Tuple[str, str]:
        """
        Split screen: paged output on top, prompt at bottom.
        
        Args:
            full_output: Complete output text
            prompt: Command prompt text
            
        Returns:
            (viewport_output, prompt_line) tuple
        """
        # Parse output into lines
        output_lines = full_output.split('\n')
        self.set_content(output_lines, reset_scroll=False)
        
        # Render viewport
        viewport = self.render(include_indicators=True)
        
        # Add status line if in command mode
        if self.in_command_mode:
            status = self.get_status_line()
            if status:
                viewport += f"\n{status}"
        
        return viewport, prompt
    
    def clear(self):
        """Clear pager content"""
        self.state.lines = []
        self.state.offset = 0
    
    def auto_scroll_to_bottom(self):
        """Automatically scroll to show latest content"""
        self.state.offset = self.state.max_offset
    
    def search(self, query: str, forward: bool = True) -> bool:
        """
        Search for text and scroll to first match.
        
        Args:
            query: Search string
            forward: Search forward (True) or backward (False)
            
        Returns:
            True if found, False otherwise
        """
        current = self.state.offset
        lines = self.state.lines
        
        if forward:
            # Search from current position forward
            for i in range(current, len(lines)):
                if query.lower() in lines[i].lower():
                    self.state.offset = max(0, i - self.state.viewport_height // 2)
                    return True
        else:
            # Search backward
            for i in range(current, -1, -1):
                if query.lower() in lines[i].lower():
                    self.state.offset = max(0, i - self.state.viewport_height // 2)
                    return True
        
        return False
    
    def get_config(self) -> dict:
        """Get current configuration"""
        return {
            "preserve_scroll": self.state.preserve_scroll,
            "show_indicators": self.state.show_indicators,
            "viewport_height": self.state.viewport_height
        }
    
    def update_config(self, config: dict):
        """Update configuration"""
        if "preserve_scroll" in config:
            self.state.preserve_scroll = config["preserve_scroll"]
        if "show_indicators" in config:
            self.state.show_indicators = config["show_indicators"]
        if "viewport_height" in config:
            self.state.viewport_height = config["viewport_height"]
