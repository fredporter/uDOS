"""
uDOS v1.0.31 - Micro Editor Integration

Provides a lightweight text editor component for FILE EDIT and FILE VIEW commands.
Uses a simple terminal-based editor with syntax highlighting for .md and .uscript files.

Features:
- Line-based editing with navigation
- Basic syntax highlighting
- Read-only mode for VIEW
- Save/Cancel options
- Works within uDOS terminal session
- Standardized input interface (v1.0.31)

Version: 1.0.31
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from core.services.standardized_input import StandardizedInput


class MicroEditor:
    """
    Lightweight terminal-based text editor for uDOS.
    Provides basic editing capabilities without external dependencies.
    """

    def __init__(self, filepath: str, readonly: bool = False):
        """
        Initialize micro editor.

        Args:
            filepath: Path to file to edit/view
            readonly: If True, file is read-only (VIEW mode)
        """
        self.filepath = Path(filepath)
        self.readonly = readonly
        self.lines: List[str] = []
        self.modified = False
        self.current_line = 0
        self.si = StandardizedInput()  # Standardized input v1.0.31

    def load_file(self) -> bool:
        """
        Load file contents into editor.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.filepath.exists():
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.lines = [line.rstrip('\n') for line in f.readlines()]
            else:
                # New file
                self.lines = []
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def save_file(self) -> bool:
        """
        Save editor contents to file.

        Returns:
            True if successful, False otherwise
        """
        if self.readonly:
            print("Cannot save in read-only mode")
            return False

        try:
            # Create parent directories if needed
            self.filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.lines))
                if self.lines:  # Add final newline if file has content
                    f.write('\n')

            self.modified = False
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def display(self, start_line: int = 0, num_lines: int = 20) -> None:
        """
        Display file contents with line numbers.

        Args:
            start_line: First line to display (0-indexed)
            num_lines: Number of lines to display
        """
        print(f"\n{'─' * 70}")
        print(f"File: {self.filepath}")
        print(f"Mode: {'READ-ONLY' if self.readonly else 'EDIT'}")
        print(f"Lines: {len(self.lines)}")
        if self.modified:
            print("Status: MODIFIED")
        print(f"{'─' * 70}\n")

        # Display lines
        end_line = min(start_line + num_lines, len(self.lines))

        if not self.lines:
            print("  (empty file)")
        else:
            for i in range(start_line, end_line):
                line_num = i + 1
                line_content = self.lines[i]

                # Simple syntax highlighting for .md files
                if self.filepath.suffix == '.md':
                    line_content = self._highlight_markdown(line_content)
                elif self.filepath.suffix == '.uscript':
                    line_content = self._highlight_uscript(line_content)

                # Show current line indicator
                indicator = '►' if i == self.current_line else ' '
                print(f"{indicator} {line_num:4} │ {line_content}")

        # Show navigation info if file is longer than display
        if len(self.lines) > num_lines:
            remaining = len(self.lines) - end_line
            if remaining > 0:
                print(f"\n  ... {remaining} more lines (use 'n' for next page)")

        print()

    def _highlight_markdown(self, line: str) -> str:
        """Apply simple markdown syntax highlighting."""
        if line.startswith('# '):
            return f"\033[1;36m{line}\033[0m"  # Cyan bold for H1
        elif line.startswith('## '):
            return f"\033[1;34m{line}\033[0m"  # Blue bold for H2
        elif line.startswith('### '):
            return f"\033[1;35m{line}\033[0m"  # Magenta bold for H3
        elif line.startswith('- ') or line.startswith('* '):
            return f"\033[33m{line}\033[0m"  # Yellow for lists
        elif line.startswith('```'):
            return f"\033[32m{line}\033[0m"  # Green for code blocks
        return line

    def _highlight_uscript(self, line: str) -> str:
        """Apply simple uScript syntax highlighting."""
        if line.strip().startswith('[') and ']' in line:
            # uCODE command
            return f"\033[1;32m{line}\033[0m"  # Green bold
        elif line.strip().startswith('#'):
            # Comment
            return f"\033[90m{line}\033[0m"  # Gray
        return line

    def edit_line(self, line_num: int, new_content: str) -> bool:
        """
        Edit a specific line.

        Args:
            line_num: Line number (1-indexed)
            new_content: New line content

        Returns:
            True if successful
        """
        if self.readonly:
            print("Cannot edit in read-only mode")
            return False

        if line_num < 1 or line_num > len(self.lines) + 1:
            print(f"Invalid line number: {line_num}")
            return False

        if line_num > len(self.lines):
            # Append new line
            self.lines.append(new_content)
        else:
            # Edit existing line
            self.lines[line_num - 1] = new_content

        self.modified = True
        return True

    def insert_line(self, line_num: int, content: str) -> bool:
        """
        Insert a new line at position.

        Args:
            line_num: Position to insert (1-indexed)
            content: Line content

        Returns:
            True if successful
        """
        if self.readonly:
            print("Cannot insert in read-only mode")
            return False

        if line_num < 1 or line_num > len(self.lines) + 1:
            print(f"Invalid line number: {line_num}")
            return False

        self.lines.insert(line_num - 1, content)
        self.modified = True
        return True

    def delete_line(self, line_num: int) -> bool:
        """
        Delete a specific line.

        Args:
            line_num: Line number to delete (1-indexed)

        Returns:
            True if successful
        """
        if self.readonly:
            print("Cannot delete in read-only mode")
            return False

        if line_num < 1 or line_num > len(self.lines):
            print(f"Invalid line number: {line_num}")
            return False

        del self.lines[line_num - 1]
        self.modified = True
        return True

    def run_interactive(self) -> bool:
        """
        Run interactive editor session.

        Returns:
            True if file was saved, False if cancelled
        """
        if not self.load_file():
            return False

        start_line = 0
        lines_per_page = 20

        while True:
            # Clear screen and display
            os.system('clear' if os.name != 'nt' else 'cls')
            self.display(start_line, lines_per_page)

            # Build command options based on mode
            if self.readonly:
                commands = ["Next page", "Previous page", "Go to line", "Quit"]
                command_keys = ['n', 'p', 'g', 'q']
            else:
                commands = ["Edit line", "Insert line", "Delete line", "Next page",
                           "Previous page", "Save", "Quit"]
                command_keys = ['e', 'i', 'd', 'n', 'p', 's', 'q']

            try:
                # Use standardized input for command selection
                cmd_idx, cmd_text = self.si.select_option(
                    "Editor Command",
                    commands,
                    show_numbers=True
                )

                if cmd_idx == -1:  # Cancelled
                    if self.modified and not self.readonly:
                        if self.si.confirm("File modified. Save changes?", default=False):
                            return self.save_file()
                    return False

                cmd = command_keys[cmd_idx]

                if cmd == 'q':
                    if self.modified and not self.readonly:
                        if self.si.confirm("File modified. Save changes?", default=False):
                            return self.save_file()
                    return False

                elif cmd == 's' and not self.readonly:
                    if self.save_file():
                        self.si.show_status("File saved successfully", "success")
                        self.si.input_text("Press ENTER to continue", default="")

                elif cmd == 'n':
                    if start_line + lines_per_page < len(self.lines):
                        start_line += lines_per_page

                elif cmd == 'p':
                    start_line = max(0, start_line - lines_per_page)

                elif cmd == 'g':
                    line_num = self.si.input_text(
                        "Go to line",
                        validate=lambda x: x.isdigit() and 1 <= int(x) <= len(self.lines)
                    )
                    if line_num:
                        start_line = max(0, min(int(line_num) - 1, len(self.lines) - 1))

                elif cmd == 'e' and not self.readonly:
                    line_num = self.si.input_text(
                        "Edit line number",
                        validate=lambda x: x.isdigit() and 1 <= int(x) <= len(self.lines)
                    )
                    if line_num:
                        ln = int(line_num)
                        print(f"Current: {self.lines[ln - 1]}")
                        new_content = self.si.input_text("New content")
                        if new_content is not None:
                            self.edit_line(ln, new_content)

                elif cmd == 'i' and not self.readonly:
                    line_num = self.si.input_text(
                        "Insert at line",
                        validate=lambda x: x.isdigit() and 1 <= int(x) <= len(self.lines) + 1
                    )
                    if line_num:
                        content = self.si.input_text("Content")
                        if content:
                            self.insert_line(int(line_num), content)

                elif cmd == 'd' and not self.readonly:
                    line_num = self.si.input_text(
                        "Delete line number",
                        validate=lambda x: x.isdigit() and 1 <= int(x) <= len(self.lines)
                    )
                    if line_num:
                        if self.si.confirm(f"Delete line {line_num}?", default=False):
                            self.delete_line(int(line_num))

            except (KeyboardInterrupt, EOFError):
                if self.modified and not self.readonly:
                    if self.si.confirm("File modified. Save changes?", default=False):
                        return self.save_file()
                return False

        return False


def edit_file(filepath: str) -> bool:
    """
    Open file in editor.

    Args:
        filepath: Path to file

    Returns:
        True if file was saved
    """
    editor = MicroEditor(filepath, readonly=False)
    return editor.run_interactive()


def view_file(filepath: str) -> bool:
    """
    Open file in read-only viewer.

    Args:
        filepath: Path to file

    Returns:
        True when viewer closes
    """
    editor = MicroEditor(filepath, readonly=True)
    return editor.run_interactive()


# Quick test
if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if '--view' in sys.argv:
            view_file(filepath)
        else:
            edit_file(filepath)
    else:
        print("Usage: python micro_editor.py <filepath> [--view]")
