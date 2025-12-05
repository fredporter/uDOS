"""
Color UI Utilities for uDOS TUI
Provides colored page breaks, progress bars, status indicators, and themed dividers.
"""

from typing import Optional, Literal
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


class ColorUI:
    """Enhanced color UI utilities for terminal display."""

    def __init__(self):
        # Force color output even if terminal detection fails
        self.console = Console(force_terminal=True, force_interactive=True)
        self.themes = {
            'foundation': {'primary': 'cyan', 'secondary': 'blue', 'accent': 'white'},
            'galaxy': {'primary': 'magenta', 'secondary': 'purple', 'accent': 'cyan'},
            'neon': {'primary': 'bright_green', 'secondary': 'bright_yellow', 'accent': 'bright_magenta'},
            'retro': {'primary': 'yellow', 'secondary': 'orange1', 'accent': 'red'}
        }

    def page_break(self,
                   theme: str = 'foundation',
                   style: Literal['simple', 'double', 'dotted', 'decorative'] = 'simple',
                   width: Optional[int] = None) -> None:
        """
        Print a colored page break/horizontal rule.

        Args:
            theme: Color theme (foundation/galaxy/neon/retro)
            style: Line style (simple/double/dotted/decorative)
            width: Width in characters (None = console width)
        """
        if width is None:
            width = self.console.width

        colors = self.themes.get(theme, self.themes['foundation'])

        if style == 'simple':
            line = "─" * width
            self.console.print(line, style=f"bold {colors['primary']}")

        elif style == 'double':
            line = "═" * width
            self.console.print(line, style=f"bold {colors['primary']}")

        elif style == 'dotted':
            line = "┈" * width
            self.console.print(line, style=f"{colors['secondary']}")

        elif style == 'decorative':
            # Alternating pattern with colors
            pattern = "═─═─" * (width // 4)
            text = Text(pattern[:width])
            # Gradient effect
            for i in range(0, len(text), 2):
                if i % 4 == 0:
                    text.stylize(f"bold {colors['primary']}", i, i+1)
                else:
                    text.stylize(f"{colors['secondary']}", i, i+1)
            self.console.print(text)

    def section_divider(self, title: str, theme: str = 'foundation', width: Optional[int] = None) -> None:
        """
        Print a section divider with centered title.

        Args:
            title: Section title
            theme: Color theme
            width: Width in characters (None = console width)
        """
        if width is None:
            width = self.console.width

        colors = self.themes.get(theme, self.themes['foundation'])

        # Calculate padding
        title_len = len(title) + 4  # Add spaces around title
        line_len = (width - title_len) // 2

        text = Text()
        text.append("─" * line_len, style=f"{colors['secondary']}")
        text.append(f"  {title}  ", style=f"bold {colors['primary']}")
        text.append("─" * (width - line_len - title_len), style=f"{colors['secondary']}")

        self.console.print(text)

    def progress_bar(self,
                    description: str,
                    total: int = 100,
                    theme: str = 'foundation') -> Progress:
        """
        Create a colored progress bar.

        Args:
            description: Task description
            total: Total steps
            theme: Color theme

        Returns:
            Progress object (use with context manager)
        """
        colors = self.themes.get(theme, self.themes['foundation'])

        progress = Progress(
            TextColumn("[bold {color}]{task.description}".format(color=colors['primary'])),
            BarColumn(complete_style=colors['primary'], finished_style=colors['accent']),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console
        )

        return progress

    def status_indicator(self,
                        message: str,
                        status: Literal['success', 'error', 'warning', 'info']) -> None:
        """
        Print a status message with colored indicator.

        Args:
            message: Status message
            status: Status type (success/error/warning/info)
        """
        indicators = {
            'success': ('✓', 'bold green'),
            'error': ('✗', 'bold red'),
            'warning': ('⚠', 'bold yellow'),
            'info': ('ℹ', 'bold cyan')
        }

        icon, style = indicators[status]

        text = Text()
        text.append(f"{icon} ", style=style)
        text.append(message)

        self.console.print(text)

    def meter(self,
             label: str,
             value: float,
             max_value: float = 100,
             theme: str = 'foundation',
             width: int = 40) -> None:
        """
        Display a horizontal meter/gauge.

        Args:
            label: Meter label
            value: Current value
            max_value: Maximum value
            theme: Color theme
            width: Meter width in characters
        """
        colors = self.themes.get(theme, self.themes['foundation'])
        percentage = min(100, (value / max_value) * 100)
        filled = int((percentage / 100) * width)

        # Gradient color based on percentage
        if percentage >= 80:
            bar_color = 'green'
        elif percentage >= 50:
            bar_color = colors['primary']
        elif percentage >= 30:
            bar_color = 'yellow'
        else:
            bar_color = 'red'

        text = Text()
        text.append(f"{label}: ", style="bold")
        text.append("█" * filled, style=f"bold {bar_color}")
        text.append("░" * (width - filled), style="dim")
        text.append(f" {percentage:.1f}%", style="bold")

        self.console.print(text)

    def panel(self,
             content: str,
             title: Optional[str] = None,
             theme: str = 'foundation',
             box_style: str = 'ROUNDED') -> None:
        """
        Display content in a colored panel.

        Args:
            content: Panel content
            title: Optional panel title
            theme: Color theme
            box_style: Box style (ROUNDED/DOUBLE/SQUARE/etc)
        """
        colors = self.themes.get(theme, self.themes['foundation'])

        # Get box style
        box_map = {
            'ROUNDED': box.ROUNDED,
            'DOUBLE': box.DOUBLE,
            'SQUARE': box.SQUARE,
            'MINIMAL': box.MINIMAL,
            'HEAVY': box.HEAVY
        }
        box_obj = box_map.get(box_style, box.ROUNDED)

        panel = Panel(
            content,
            title=title,
            border_style=f"bold {colors['primary']}",
            box=box_obj
        )

        self.console.print(panel)

    def table(self,
             headers: list[str],
             rows: list[list[str]],
             title: Optional[str] = None,
             theme: str = 'foundation') -> None:
        """
        Display a colored table.

        Args:
            headers: Column headers
            rows: Table rows
            title: Optional table title
            theme: Color theme
        """
        colors = self.themes.get(theme, self.themes['foundation'])

        table = Table(
            title=title,
            header_style=f"bold {colors['primary']}",
            border_style=colors['secondary'],
            show_lines=True
        )

        # Add columns
        for header in headers:
            table.add_column(header)

        # Add rows
        for row in rows:
            table.add_row(*row)

        self.console.print(table)

    def rainbow_text(self, text: str, bold: bool = True) -> None:
        """
        Print text with rainbow gradient colors.

        Args:
            text: Text to colorize
            bold: Use bold styling
        """
        colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'magenta']

        rich_text = Text()
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            style = f"bold {color}" if bold else color
            rich_text.append(char, style=style)

        self.console.print(rich_text)

    def gradient_text(self,
                     text: str,
                     start_color: str = 'cyan',
                     end_color: str = 'magenta',
                     bold: bool = True) -> None:
        """
        Print text with two-color gradient (simplified).

        Args:
            text: Text to colorize
            start_color: Starting color
            end_color: Ending color
            bold: Use bold styling
        """
        # Simplified gradient (alternates between two colors)
        rich_text = Text()
        for i, char in enumerate(text):
            color = start_color if i % 2 == 0 else end_color
            style = f"bold {color}" if bold else color
            rich_text.append(char, style=style)

        self.console.print(rich_text)


# Global instance for easy access
_color_ui = None

def get_color_ui() -> ColorUI:
    """Get global ColorUI instance."""
    global _color_ui
    if _color_ui is None:
        _color_ui = ColorUI()
    return _color_ui
