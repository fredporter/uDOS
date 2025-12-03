"""
uDOS Simple Pager - Page breaks for long output

Displays content page-by-page when it exceeds viewport height.
Uses block graphics for progress bar and arrow key navigation.

Author: uDOS Development Team
Date: December 3, 2025
"""

import sys
import shutil
import termios
import tty
from typing import List, Optional


class SimplePager:
    """Simple text pager with block graphics progress bar."""

    def __init__(self, viewport_height: Optional[int] = None, viewport_width: Optional[int] = None):
        """
        Initialize pager.

        Args:
            viewport_height: Height in lines (auto-detected if None)
            viewport_width: Width in columns (auto-detected if None)
        """
        if viewport_height is None or viewport_width is None:
            try:
                width, height = shutil.get_terminal_size()
                if viewport_height is None:
                    # Reserve line for progress bar
                    viewport_height = max(10, height - 2)
                if viewport_width is None:
                    viewport_width = width
            except Exception:
                viewport_height = viewport_height or 20
                viewport_width = viewport_width or 80

        self.viewport_height = viewport_height
        self.viewport_width = viewport_width

    def _get_key(self) -> str:
        """
        Get a single keypress from user (cross-platform).

        Returns:
            Key code as string ('up', 'down', 'esc', 'enter', or character)
        """
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)

                # Handle escape sequences (arrow keys)
                if ch == '\x1b':  # ESC
                    # Check if this is an escape sequence or just ESC key
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':  # Arrow key sequence
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'A':  # Up arrow
                            return 'up'
                        elif ch3 == 'B':  # Down arrow
                            return 'down'
                        elif ch3 == 'C':  # Right arrow
                            return 'down'  # Treat right as down (next page)
                        elif ch3 == 'D':  # Left arrow
                            return 'up'  # Treat left as up (prev page)
                        else:
                            return 'esc'
                    else:
                        return 'esc'
                elif ch == '\r' or ch == '\n':
                    return 'enter'
                else:
                    return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            # Fallback for non-Unix systems
            return input().strip().lower() or 'enter'

    def _draw_progress_bar(self, page_num: int, total_pages: int, at_end: bool = False) -> str:
        """
        Draw block graphics progress bar with navigation hints.

        Args:
            page_num: Current page number
            total_pages: Total number of pages
            at_end: Whether this is the last page

        Returns:
            Formatted progress bar string
        """
        # Block graphics characters
        FULL_BLOCK = '█'
        EMPTY_BLOCK = '░'

        # Calculate progress percentage
        progress_pct = page_num / total_pages

        # Determine available width for progress bar
        # Format: "█████░░░ Page 3/7 [↓→/ENTER|↑←|ESC]"
        info_text = f" Page {page_num}/{total_pages} "

        if at_end:
            options_text = "[ENTER=OK|ESC]"
        else:
            options_text = "[↓→/ENTER|↑←|ESC]"

        # Reserve space for info and options
        reserved_width = len(info_text) + len(options_text) + 2
        bar_width = max(10, self.viewport_width - reserved_width)

        # Calculate filled blocks
        filled_blocks = int(bar_width * progress_pct)
        empty_blocks = bar_width - filled_blocks

        # Build progress bar
        bar = FULL_BLOCK * filled_blocks + EMPTY_BLOCK * empty_blocks

        # Combine all elements
        progress_line = f"{bar}{info_text}{options_text}"

        # Ensure it doesn't exceed viewport width
        if len(progress_line) > self.viewport_width:
            progress_line = progress_line[:self.viewport_width]

        return progress_line

    def page(self, text: str, title: Optional[str] = None) -> None:
        """
        Display text with page breaks and arrow key navigation.

        Navigation:
            Down Arrow/ENTER - Next page
            Up Arrow - Previous page
            ESC - Quit paging

        Args:
            text: Text to display
            title: Optional title to show at top of each page
        """
        lines = text.split('\n')

        # If content fits on screen, just print it
        if len(lines) <= self.viewport_height:
            print(text)
            return

        # Paginate
        page_num = 1
        total_pages = (len(lines) + self.viewport_height - 1) // self.viewport_height

        while True:
            # Calculate line range for current page
            start_idx = (page_num - 1) * self.viewport_height
            end_idx = min(start_idx + self.viewport_height, len(lines))

            # Clear screen (optional - can be disabled for accessibility)
            # print('\033[2J\033[H', end='')

            # Show title if provided
            if title:
                print(f"╔{'═' * (len(title) + 2)}╗")
                print(f"║ {title} ║")
                print(f"╚{'═' * (len(title) + 2)}╝")
                print()

            # Show page content
            for line in lines[start_idx:end_idx]:
                print(line)

            # Show block graphics progress bar
            is_last_page = page_num >= total_pages
            progress_bar = self._draw_progress_bar(page_num, total_pages, at_end=is_last_page)
            print(f"\n{progress_bar}", flush=True)

            # Get user input
            try:
                key = self._get_key()

                if key == 'esc':
                    print("\n⚠️  Paging cancelled")
                    break
                elif key == 'down' or key == 'enter':
                    if is_last_page:
                        # On last page, ENTER exits
                        break
                    else:
                        # Move to next page
                        page_num += 1
                elif key == 'up':
                    if page_num > 1:
                        # Move to previous page
                        page_num -= 1
                    # If already on first page, do nothing

            except (KeyboardInterrupt, EOFError):
                print("\n\n⚠️  Paging cancelled")
                break

    def page_lines(self, lines: List[str], title: Optional[str] = None) -> None:
        """
        Display list of lines with page breaks.

        Args:
            lines: List of lines to display
            title: Optional title
        """
        self.page('\n'.join(lines), title=title)


def page_output(text: str, viewport_height: Optional[int] = None, title: Optional[str] = None) -> None:
    """
    Convenience function to page text output.

    Args:
        text: Text to page
        viewport_height: Viewport height (auto-detected if None)
        title: Optional title for pages

    Example:
        from core.utils.pager import page_output
        page_output(long_text, title="Help Information")
    """
    pager = SimplePager(viewport_height=viewport_height)
    pager.page(text, title=title)


# Example usage
if __name__ == '__main__':
    # Generate sample long content
    sample_lines = []
    for i in range(100):
        sample_lines.append(f"Line {i + 1}: This is sample content to demonstrate paging.")

    sample_text = '\n'.join(sample_lines)

    print("Testing SimplePager with 100 lines of content...\n")
    page_output(sample_text, title="Sample Content")
