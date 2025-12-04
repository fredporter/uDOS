"""
Syntax Highlighter for uPY Scripts
Provides colorized output for .upy code with COMMAND(args) syntax.
"""

from typing import Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
import re


class UPYHighlighter:
    """Syntax highlighter for uPY script language."""

    def __init__(self):
        self.console = Console()

        # uPY syntax patterns
        self.patterns = {
            'command': r'\b([A-Z][A-Z_]*)\s*\(',  # COMMAND(
            'function': r'\b([a-z_][a-z0-9_]*)\s*\(',  # function(
            'string': r'(["\'])(?:(?=(\\?))\2.)*?\1',  # "string" or 'string'
            'comment': r'#.*$',  # # comment
            'number': r'\b\d+\.?\d*\b',  # 123 or 123.45
            'variable': r'\$[A-Z_][A-Z0-9_.]*',  # $VARIABLE or $VAR.PROP
            'operator': r'[+\-*/=<>!&|]+',  # operators
            'bracket': r'[\(\)\[\]\{\}]',  # brackets
            'separator': r'[,;:]',  # separators
        }

        # Color scheme for each pattern type
        self.colors = {
            'command': 'bold cyan',
            'function': 'bold green',
            'string': 'yellow',
            'comment': 'dim italic',
            'number': 'magenta',
            'variable': 'bold blue',
            'operator': 'red',
            'bracket': 'white',
            'separator': 'dim'
        }

    def highlight_line(self, line: str) -> Text:
        """
        Highlight a single line of uPY code.

        Args:
            line: Line of code to highlight

        Returns:
            Rich Text object with syntax highlighting
        """
        text = Text()
        pos = 0

        while pos < len(line):
            matched = False

            # Try each pattern
            for pattern_name, pattern in self.patterns.items():
                regex = re.compile(pattern, re.MULTILINE)
                match = regex.match(line, pos)

                if match:
                    # Add matched text with color
                    matched_text = match.group(0)
                    text.append(matched_text, style=self.colors[pattern_name])
                    pos = match.end()
                    matched = True
                    break

            if not matched:
                # No pattern matched, add character as-is
                text.append(line[pos])
                pos += 1

        return text

    def highlight_code(self, code: str, line_numbers: bool = False) -> None:
        """
        Highlight and print multi-line uPY code.

        Args:
            code: Multi-line code string
            line_numbers: Show line numbers
        """
        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            if line_numbers:
                line_num = Text(f"{i:3d} │ ", style="dim")
                highlighted = self.highlight_line(line)
                self.console.print(line_num + highlighted)
            else:
                self.console.print(self.highlight_line(line))

    def highlight_file(self, filepath: str, line_numbers: bool = True) -> None:
        """
        Highlight and print an entire .upy file.

        Args:
            filepath: Path to .upy file
            line_numbers: Show line numbers
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()

            # Print file header
            from rich.panel import Panel
            header = Panel(
                f"📄 {filepath}",
                border_style="bold cyan",
                padding=(0, 1)
            )
            self.console.print(header)

            # Highlight code
            self.highlight_code(code, line_numbers=line_numbers)

        except FileNotFoundError:
            self.console.print(f"[bold red]Error:[/] File not found: {filepath}")
        except Exception as e:
            self.console.print(f"[bold red]Error:[/] {str(e)}")

    def highlight_command(self, command: str) -> Text:
        """
        Highlight a single command string (for REPL display).

        Args:
            command: Command string to highlight

        Returns:
            Rich Text object with syntax highlighting
        """
        return self.highlight_line(command)


class SimpleSyntaxHighlighter:
    """Simplified syntax highlighter using pygments (fallback)."""

    def __init__(self):
        self.console = Console()

    def highlight_code(self, code: str, language: str = 'python',
                      line_numbers: bool = False, theme: str = 'monokai') -> None:
        """
        Highlight code using pygments.

        Args:
            code: Code string
            language: Language name (python, javascript, etc.)
            line_numbers: Show line numbers
            theme: Color theme
        """
        try:
            syntax = Syntax(
                code,
                language,
                theme=theme,
                line_numbers=line_numbers,
                word_wrap=False
            )
            self.console.print(syntax)
        except Exception as e:
            # Fallback to plain text
            self.console.print(code)

    def highlight_file(self, filepath: str, language: Optional[str] = None,
                      line_numbers: bool = True, theme: str = 'monokai') -> None:
        """
        Highlight a file using pygments.

        Args:
            filepath: Path to file
            language: Language name (auto-detected if None)
            line_numbers: Show line numbers
            theme: Color theme
        """
        try:
            # Auto-detect language from extension
            if language is None:
                ext_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.json': 'json',
                    '.md': 'markdown',
                    '.sh': 'bash',
                    '.upy': 'python',  # Treat .upy as Python-like
                    '.yaml': 'yaml',
                    '.yml': 'yaml'
                }
                import os
                _, ext = os.path.splitext(filepath)
                language = ext_map.get(ext.lower(), 'text')

            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()

            self.highlight_code(code, language, line_numbers, theme)

        except FileNotFoundError:
            self.console.print(f"[bold red]Error:[/] File not found: {filepath}")
        except Exception as e:
            self.console.print(f"[bold red]Error:[/] {str(e)}")


# Global instances
_upy_highlighter = None
_simple_highlighter = None

def get_upy_highlighter() -> UPYHighlighter:
    """Get global UPYHighlighter instance."""
    global _upy_highlighter
    if _upy_highlighter is None:
        _upy_highlighter = UPYHighlighter()
    return _upy_highlighter

def get_simple_highlighter() -> SimpleSyntaxHighlighter:
    """Get global SimpleSyntaxHighlighter instance."""
    global _simple_highlighter
    if _simple_highlighter is None:
        _simple_highlighter = SimpleSyntaxHighlighter()
    return _simple_highlighter


# Convenience functions
def highlight_upy(code: str, line_numbers: bool = False) -> None:
    """Highlight uPY code."""
    get_upy_highlighter().highlight_code(code, line_numbers)

def highlight_upy_file(filepath: str, line_numbers: bool = True) -> None:
    """Highlight uPY file."""
    get_upy_highlighter().highlight_file(filepath, line_numbers)

def highlight_code(code: str, language: str = 'python',
                  line_numbers: bool = False, theme: str = 'monokai') -> None:
    """Highlight code in any language."""
    get_simple_highlighter().highlight_code(code, language, line_numbers, theme)

def highlight_file(filepath: str, language: Optional[str] = None,
                  line_numbers: bool = True, theme: str = 'monokai') -> None:
    """Highlight file in any language."""
    get_simple_highlighter().highlight_file(filepath, language, line_numbers, theme)
