"""
uDOS Simple Pager - Page breaks for long output

Displays content page-by-page when it exceeds viewport height.
Uses block graphics for progress bar and styled options.

Author: uDOS Development Team
Date: December 3, 2025
"""

import sys
import shutil
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

    def _draw_progress_bar(self, page_num: int, total_pages: int, at_end: bool = False) -> str:
        """
        Draw block graphics progress bar with styled options.

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
        # Format: "█████░░░ Page 3/7 [YES|NO|OK]"
        info_text = f" Page {page_num}/{total_pages} "

        if at_end:
            options_text = "[OK]"
        else:
            options_text = "[YES|NO]"

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
        Display text with page breaks.

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
        start_idx = 0

        while start_idx < len(lines):
            # Clear screen (optional - can be disabled for accessibility)
            # print('\033[2J\033[H', end='')

            # Show title if provided
            if title:
                print(f"╔{'═' * (len(title) + 2)}╗")
                print(f"║ {title} ║")
                print(f"╚{'═' * (len(title) + 2)}╝")
                print()

            # Show page content
            end_idx = min(start_idx + self.viewport_height, len(lines))
            for line in lines[start_idx:end_idx]:
                print(line)

            # Show block graphics progress bar
            is_last_page = end_idx >= len(lines)
            progress_bar = self._draw_progress_bar(page_num, total_pages, at_end=is_last_page)
            print(f"\n{progress_bar}", flush=True)

            if not is_last_page:
                # Not the last page - wait for input
                try:
                    response = input().strip().lower()
                    if response in ('n', 'no', 'q'):
                        print("\n⚠️  Paging cancelled")
                        break
                    # Any other input (ENTER, 'y', 'yes', etc.) continues
                except (KeyboardInterrupt, EOFError):
                    print("\n\n⚠️  Paging cancelled")
                    break

                start_idx = end_idx
                page_num += 1
            else:
                # Last page - wait for acknowledgment
                try:
                    input()  # Just wait for ENTER/OK
                except (KeyboardInterrupt, EOFError):
                    pass
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
