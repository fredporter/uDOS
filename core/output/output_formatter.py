"""
uDOS v1.0.29 - Output Formatter
Unified output formatting with theme-aware styling and consistent layouts
"""

from typing import List, Dict, Any, Optional
from datetime import datetime


class OutputFormatter:
    """
    Formats command output with theme-aware styling.
    Provides consistent formatting for success, error, warning, info messages,
    tables, lists, and panels.
    """

    def __init__(self, theme: str = 'dungeon', width: int = 80):
        """
        Initialize output formatter.

        Args:
            theme: Theme name for styling
            width: Default output width in characters
        """
        self.theme = theme
        self.width = width
        self.icons = self._get_theme_icons()
        self.borders = self._get_theme_borders()

    def _get_theme_icons(self) -> Dict[str, str]:
        """Get theme-specific icons"""
        theme_icons = {
            'dungeon': {
                'success': '✓',
                'error': '✗',
                'warning': '⚠',
                'info': 'ℹ',
                'bullet': '•',
                'arrow': '→',
                'check': '✓',
                'cross': '✗',
            },
            'hacker': {
                'success': '[+]',
                'error': '[!]',
                'warning': '[*]',
                'info': '[i]',
                'bullet': '>',
                'arrow': '>>',
                'check': '[OK]',
                'cross': '[X]',
            },
            'galaxy': {
                'success': '★',
                'error': '⊗',
                'warning': '△',
                'info': '○',
                'bullet': '◆',
                'arrow': '▸',
                'check': '✓',
                'cross': '✗',
            },
        }

        return theme_icons.get(self.theme, theme_icons['dungeon'])

    def _get_theme_borders(self) -> Dict[str, str]:
        """Get theme-specific border characters"""
        return {
            'horizontal': '═',
            'vertical': '║',
            'top_left': '╔',
            'top_right': '╗',
            'bottom_left': '╚',
            'bottom_right': '╝',
            'tee_down': '╦',
            'tee_up': '╩',
            'tee_right': '╠',
            'tee_left': '╣',
            'cross': '╬',
        }

    def format_success(self, message: str, details: Optional[Dict[str, Any]] = None) -> str:
        """
        Format success message.

        Args:
            message: Main success message
            details: Optional dictionary of details to display

        Returns:
            Formatted success message

        Example:
            output = formatter.format_success(
                "Configuration saved",
                details={"File": "user.json", "Fields": 5}
            )
        """
        icon = self.icons['success']
        lines = [f"{icon} {message}"]

        if details:
            for key, value in details.items():
                lines.append(f"  {key}: {value}")

        return '\n'.join(lines)

    def format_error(self, message: str, error_details: Optional[str] = None) -> str:
        """
        Format error message.

        Args:
            message: Main error message
            error_details: Optional detailed error information

        Returns:
            Formatted error message
        """
        icon = self.icons['error']
        lines = [f"{icon} {message}"]

        if error_details:
            lines.append(f"  Details: {error_details}")

        return '\n'.join(lines)

    def format_warning(self, message: str) -> str:
        """Format warning message"""
        icon = self.icons['warning']
        return f"{icon}  {message}"

    def format_info(self, message: str) -> str:
        """Format info message"""
        icon = self.icons['info']
        return f"{icon}  {message}"

    def format_table(self,
                    data: List[Dict[str, Any]],
                    headers: Optional[List[str]] = None,
                    max_width: Optional[int] = None) -> str:
        """
        Format data as ASCII table.

        Args:
            data: List of dictionaries with table data
            headers: Optional list of column headers (uses dict keys if not provided)
            max_width: Maximum table width

        Returns:
            Formatted table string

        Example:
            data = [
                {"Name": "Fred", "Role": "Admin"},
                {"Name": "Alice", "Role": "User"}
            ]
            table = formatter.format_table(data)
        """
        if not data:
            return self.format_info("No data to display")

        # Get headers from first row if not provided
        if not headers:
            headers = list(data[0].keys())

        # Calculate column widths
        col_widths = {}
        for header in headers:
            col_widths[header] = len(header)

        for row in data:
            for header in headers:
                value = str(row.get(header, ''))
                col_widths[header] = max(col_widths[header], len(value))

        # Apply max width if specified
        table_width = sum(col_widths.values()) + len(headers) * 3 + 1
        if max_width and table_width > max_width:
            # Scale down proportionally
            scale = max_width / table_width
            for header in headers:
                col_widths[header] = max(5, int(col_widths[header] * scale))

        # Build table
        b = self.borders
        lines = []

        # Top border
        top_line = b['top_left']
        for i, header in enumerate(headers):
            top_line += b['horizontal'] * (col_widths[header] + 2)
            if i < len(headers) - 1:
                top_line += b['tee_down']
        top_line += b['top_right']
        lines.append(top_line)

        # Headers
        header_line = b['vertical']
        for header in headers:
            header_line += f" {header:<{col_widths[header]}} {b['vertical']}"
        lines.append(header_line)

        # Middle border
        mid_line = b['tee_right']
        for i, header in enumerate(headers):
            mid_line += b['horizontal'] * (col_widths[header] + 2)
            if i < len(headers) - 1:
                mid_line += b['cross']
        mid_line += b['tee_left']
        lines.append(mid_line)

        # Data rows
        for row in data:
            row_line = b['vertical']
            for header in headers:
                value = str(row.get(header, ''))
                # Truncate if too long
                if len(value) > col_widths[header]:
                    value = value[:col_widths[header]-2] + '..'
                row_line += f" {value:<{col_widths[header]}} {b['vertical']}"
            lines.append(row_line)

        # Bottom border
        bottom_line = b['bottom_left']
        for i, header in enumerate(headers):
            bottom_line += b['horizontal'] * (col_widths[header] + 2)
            if i < len(headers) - 1:
                bottom_line += b['tee_up']
        bottom_line += b['bottom_right']
        lines.append(bottom_line)

        return '\n'.join(lines)

    def format_list(self,
                   items: List[str],
                   numbered: bool = False,
                   indent: int = 2) -> str:
        """
        Format list with bullets or numbers.

        Args:
            items: List of items to format
            numbered: Use numbers instead of bullets
            indent: Indentation level

        Returns:
            Formatted list string
        """
        lines = []
        bullet = self.icons['bullet']

        for i, item in enumerate(items, 1):
            prefix = f"{i}." if numbered else bullet
            lines.append(f"{' ' * indent}{prefix} {item}")

        return '\n'.join(lines)

    def format_panel(self,
                    title: str,
                    content: str,
                    width: Optional[int] = None) -> str:
        """
        Format content in a bordered panel.

        Args:
            title: Panel title
            content: Panel content
            width: Panel width (uses default if not specified)

        Returns:
            Formatted panel string
        """
        w = width or self.width
        b = self.borders

        lines = []

        # Top border with title
        title_text = f" {title} "
        title_len = len(title_text)
        left_padding = (w - title_len - 2) // 2
        right_padding = w - title_len - left_padding - 2

        top_line = b['top_left'] + b['horizontal'] * left_padding
        top_line += title_text
        top_line += b['horizontal'] * right_padding + b['top_right']
        lines.append(top_line)

        # Content lines
        content_lines = content.split('\n')
        for line in content_lines:
            # Wrap long lines
            if len(line) > w - 4:
                # Simple wrapping (can be improved)
                while line:
                    chunk = line[:w-4]
                    line = line[w-4:]
                    lines.append(f"{b['vertical']} {chunk:<{w-4}} {b['vertical']}")
            else:
                lines.append(f"{b['vertical']} {line:<{w-4}} {b['vertical']}")

        # Bottom border
        bottom_line = b['bottom_left'] + b['horizontal'] * (w - 2) + b['bottom_right']
        lines.append(bottom_line)

        return '\n'.join(lines)

    def format_key_value(self, data: Dict[str, Any], indent: int = 2) -> str:
        """
        Format dictionary as key-value pairs.

        Args:
            data: Dictionary to format
            indent: Indentation level

        Returns:
            Formatted key-value string
        """
        lines = []
        max_key_len = max(len(str(k)) for k in data.keys()) if data else 0

        for key, value in data.items():
            lines.append(f"{' ' * indent}{str(key):<{max_key_len}} : {value}")

        return '\n'.join(lines)

    def format_progress(self,
                       current: int,
                       total: int,
                       label: str = "",
                       width: int = 40) -> str:
        """
        Format progress bar.

        Args:
            current: Current progress value
            total: Total value
            label: Optional label
            width: Progress bar width

        Returns:
            Formatted progress bar
        """
        if total == 0:
            percent = 0
        else:
            percent = (current / total) * 100

        filled = int((current / total) * width) if total > 0 else 0
        bar = '█' * filled + '░' * (width - filled)

        if label:
            return f"{label}: [{bar}] {percent:.1f}% ({current}/{total})"
        else:
            return f"[{bar}] {percent:.1f}% ({current}/{total})"


def create_output_formatter(theme: str = 'dungeon', width: int = 80) -> OutputFormatter:
    """
    Factory function to create OutputFormatter instance.

    Args:
        theme: Theme name
        width: Default output width

    Returns:
        OutputFormatter instance
    """
    return OutputFormatter(theme=theme, width=width)
