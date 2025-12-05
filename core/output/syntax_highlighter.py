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


# ANSI-based syntax highlighting for terminal output (no rich dependency)
class ANSISyntaxHighlighter:
    """ANSI-based syntax highlighter for uPY/uCODE commands."""

    # ANSI color codes
    COMMAND = '\033[1;32m'      # Bright green
    PARAM = '\033[36m'          # Cyan
    VARIABLE = '\033[1;33m'     # Bright yellow
    FLAG = '\033[35m'           # Magenta
    STRING = '\033[37m'         # White
    PIPE = '\033[36m'           # Cyan
    BRACKET = '\033[90m'        # Dim gray
    RESET = '\033[0m'

    # Text formatting
    CYAN = '\033[1;36m'
    YELLOW = '\033[1;33m'
    GREEN = '\033[1;32m'
    BLUE = '\033[34m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'

    @classmethod
    def highlight(cls, text: str) -> str:
        """
        Apply syntax highlighting to uPY/uCODE command syntax.

        Supports:
        - COMMAND(params)
        - [MODULE|COMMAND*PARAM]
        - $VARIABLES
        - --flags
        - 'strings'

        Args:
            text: Command text to highlight

        Returns:
            Text with ANSI color codes
        """
        if not text or not any(char in text for char in '()[]|$'):
            return text

        result = text
        result = cls._highlight_command_parens(result)
        result = cls._highlight_ucode_brackets(result)
        result = cls._highlight_variables(result)
        result = cls._highlight_flags(result)
        result = cls._highlight_strings(result)

        return result

    @classmethod
    def _highlight_command_parens(cls, text: str) -> str:
        """Highlight COMMAND(params) syntax."""
        pattern = r'\b([A-Z][A-Z0-9_]*)\(([^)]*)\)'

        def replace_match(match):
            command = match.group(1)
            params = match.group(2)

            result = f"{cls.COMMAND}{command}{cls.RESET}{cls.BRACKET}({cls.RESET}"

            if params:
                parts = params.split('|')
                highlighted_parts = []

                for part in parts:
                    part = part.strip()
                    if not part:
                        continue

                    if part.startswith('$'):
                        highlighted_parts.append(f"{cls.VARIABLE}{part}{cls.RESET}")
                    elif part.startswith('--'):
                        highlighted_parts.append(f"{cls.FLAG}{part}{cls.RESET}")
                    elif part.startswith("'") and part.endswith("'"):
                        highlighted_parts.append(f"{cls.STRING}{part}{cls.RESET}")
                    else:
                        highlighted_parts.append(f"{cls.PARAM}{part}{cls.RESET}")

                result += f"{cls.PIPE}|{cls.RESET}".join(highlighted_parts)

            result += f"{cls.BRACKET}){cls.RESET}"
            return result

        return re.sub(pattern, replace_match, text)

    @classmethod
    def _highlight_ucode_brackets(cls, text: str) -> str:
        """Highlight [MODULE|COMMAND*PARAM] uCODE syntax."""
        pattern = r'\[([A-Z][A-Z0-9_]*)\|([A-Z][A-Z0-9_]*)(?:\*([^\]]*))?\]'

        def replace_match(match):
            module = match.group(1)
            command = match.group(2)
            params = match.group(3) or ''

            result = f"{cls.BRACKET}[{cls.RESET}"
            result += f"{cls.COMMAND}{module}{cls.RESET}"
            result += f"{cls.PIPE}|{cls.RESET}"
            result += f"{cls.PARAM}{command}{cls.RESET}"

            if params:
                result += f"{cls.PIPE}*{cls.RESET}"
                result += f"{cls.PARAM}{params}{cls.RESET}"

            result += f"{cls.BRACKET}]{cls.RESET}"
            return result

        return re.sub(pattern, replace_match, text)

    @classmethod
    def _highlight_variables(cls, text: str) -> str:
        """Highlight $VARIABLES."""
        # Simple pattern without lookbehind - just match $VAR and check if already colored
        pattern = r'(\$[A-Z_][A-Z0-9_]*)'

        def replace_var(match):
            var = match.group(1)
            # Check if already inside ANSI codes
            start_pos = match.start()
            if start_pos > 0:
                preceding = text[max(0, start_pos-10):start_pos]
                if '\033[' in preceding and '\033[0m' not in preceding:
                    return var  # Already colored
            return f"{cls.VARIABLE}{var}{cls.RESET}"

        return re.sub(pattern, replace_var, text)

    @classmethod
    def _highlight_flags(cls, text: str) -> str:
        """Highlight --flags."""
        # Simple pattern without lookbehind
        pattern = r'(--[a-z][a-z0-9-]*)'

        def replace_flag(match):
            flag = match.group(1)
            # Check if already inside ANSI codes
            start_pos = match.start()
            if start_pos > 0:
                preceding = text[max(0, start_pos-10):start_pos]
                if '\033[' in preceding and '\033[0m' not in preceding:
                    return flag  # Already colored
            return f"{cls.FLAG}{flag}{cls.RESET}"

        return re.sub(pattern, replace_flag, text)

    @classmethod
    def _highlight_strings(cls, text: str) -> str:
        """Highlight 'strings'."""
        # Simple pattern without lookbehind
        pattern = r"('([^']*)')"

        def replace_str(match):
            string = match.group(1)
            # Check if already inside ANSI codes
            start_pos = match.start()
            if start_pos > 0:
                preceding = text[max(0, start_pos-10):start_pos]
                if '\033[' in preceding and '\033[0m' not in preceding:
                    return string  # Already colored
            return f"{cls.STRING}{string}{cls.RESET}"

        return re.sub(pattern, replace_str, text)

    @classmethod
    def format_error(cls, title: str, reason: str, hint: Optional[str] = None) -> str:
        """Format a colored error message."""
        lines = []
        lines.append(f"{cls.RED}💀 {title}{cls.RESET}")
        lines.append(f"   {cls.YELLOW}Reason:{cls.RESET} {cls.highlight(reason)}")

        if hint:
            lines.append(f"   {cls.CYAN}💡 {cls.highlight(hint)}{cls.RESET}")

        return '\n'.join(lines)


# Convenience functions for ANSI highlighting
def highlight_syntax(text: str) -> str:
    """Highlight uPY/uCODE syntax in text with ANSI colors."""
    return ANSISyntaxHighlighter.highlight(text)


def format_error(title: str, reason: str, hint: Optional[str] = None) -> str:
    """Format a colored error message with syntax highlighting."""
    return ANSISyntaxHighlighter.format_error(title, reason, hint)

