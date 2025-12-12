"""
Universal Column Formatter for uDOS TUI

Provides consistent column-style output formatting across all TUI components.
Uses box-drawing characters for clean, professional output.

Part of v1.2.23 - Time-Space Integration + TUI Enhancement
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class ColumnConfig:
    """Configuration for column display."""
    width: int = 61  # Default width for single column box
    padding: int = 2   # Padding inside box
    use_unicode: bool = True  # Use Unicode box characters
    
    # Box drawing characters
    top_left: str = "╔"
    top_right: str = "╗"
    bottom_left: str = "╚"
    bottom_right: str = "╝"
    horizontal: str = "═"
    vertical: str = "║"
    left_join: str = "╠"
    right_join: str = "╣"
    cross: str = "╬"
    
    def __post_init__(self):
        """Fallback to ASCII if Unicode disabled."""
        if not self.use_unicode:
            self.top_left = "+"
            self.top_right = "+"
            self.bottom_left = "+"
            self.bottom_right = "+"
            self.horizontal = "="
            self.vertical = "|"
            self.left_join = "+"
            self.right_join = "+"
            self.cross = "+"


class ColumnFormatter:
    """Universal column formatter for uDOS TUI components."""
    
    def __init__(self, config: Optional[ColumnConfig] = None):
        """
        Initialize column formatter.
        
        Args:
            config: Optional ColumnConfig instance
        """
        self.config = config or ColumnConfig()
    
    def box_top(self, title: Optional[str] = None) -> str:
        """
        Create top border with optional title.
        
        Args:
            title: Optional centered title
            
        Returns:
            Formatted top border line
        """
        width = self.config.width
        
        if title:
            # Center title in border
            padding_total = width - len(title) - 4  # 4 for spaces around title
            left_pad = padding_total // 2
            right_pad = padding_total - left_pad
            
            return (
                f"{self.config.top_left}"
                f"{self.config.horizontal * left_pad}"
                f" {title} "
                f"{self.config.horizontal * right_pad}"
                f"{self.config.top_right}"
            )
        else:
            return (
                f"{self.config.top_left}"
                f"{self.config.horizontal * width}"
                f"{self.config.top_right}"
            )
    
    def box_bottom(self) -> str:
        """Create bottom border."""
        return (
            f"{self.config.bottom_left}"
            f"{self.config.horizontal * self.config.width}"
            f"{self.config.bottom_right}"
        )
    
    def box_separator(self) -> str:
        """Create middle separator line."""
        return (
            f"{self.config.left_join}"
            f"{self.config.horizontal * self.config.width}"
            f"{self.config.right_join}"
        )
    
    def box_line(self, content: str, align: str = "left") -> str:
        """
        Create a single line inside box.
        
        Args:
            content: Text content
            align: Alignment ('left', 'center', 'right')
            
        Returns:
            Formatted line with borders
        """
        width = self.config.width
        content_width = width - 2 * self.config.padding
        
        # Truncate if too long
        if len(content) > content_width:
            content = content[:content_width - 3] + "..."
        
        # Align content
        if align == "center":
            content = content.center(content_width)
        elif align == "right":
            content = content.rjust(content_width)
        else:  # left
            content = content.ljust(content_width)
        
        return (
            f"{self.config.vertical}"
            f"{' ' * self.config.padding}"
            f"{content}"
            f"{' ' * self.config.padding}"
            f"{self.config.vertical}"
        )
    
    def box_kv_line(self, key: str, value: str, key_width: int = 20) -> str:
        """
        Create a key-value line.
        
        Args:
            key: Key label
            value: Value content
            key_width: Width for key column
            
        Returns:
            Formatted key-value line
        """
        width = self.config.width
        content_width = width - 2 * self.config.padding
        value_width = content_width - key_width - 2  # 2 for ": "
        
        # Truncate value if needed
        if len(value) > value_width:
            value = value[:value_width - 3] + "..."
        
        # Format line
        key_part = f"{key}:".ljust(key_width)
        value_part = value.ljust(value_width)
        
        return (
            f"{self.config.vertical}"
            f"{' ' * self.config.padding}"
            f"{key_part} {value_part}"
            f"{' ' * self.config.padding}"
            f"{self.config.vertical}"
        )
    
    def box_multi_column(self, columns: List[str], widths: Optional[List[int]] = None) -> str:
        """
        Create line with multiple columns.
        
        Args:
            columns: List of column values
            widths: Optional list of column widths (auto-divide if None)
            
        Returns:
            Formatted multi-column line
        """
        width = self.config.width
        content_width = width - 2 * self.config.padding
        
        # Auto-calculate widths if not provided
        if widths is None:
            col_width = content_width // len(columns)
            widths = [col_width] * len(columns)
        
        # Truncate and pad columns
        formatted_cols = []
        for col, w in zip(columns, widths):
            if len(col) > w:
                col = col[:w - 3] + "..."
            formatted_cols.append(col.ljust(w))
        
        content = " ".join(formatted_cols)
        
        return (
            f"{self.config.vertical}"
            f"{' ' * self.config.padding}"
            f"{content[:content_width].ljust(content_width)}"
            f"{' ' * self.config.padding}"
            f"{self.config.vertical}"
        )
    
    def box_progress_bar(self, label: str, current: int, total: int, width: int = 20) -> str:
        """
        Create progress bar line.
        
        Args:
            label: Progress bar label
            current: Current progress value
            total: Total/max value
            width: Width of progress bar in characters
            
        Returns:
            Formatted progress bar line
        """
        if total == 0:
            percent = 0
        else:
            percent = min(100, int((current / total) * 100))
        
        # Build progress bar
        filled = int((percent / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        
        # Format line
        label_part = f"{label}:".ljust(20)
        percent_part = f"{percent}%".rjust(4)
        
        content = f"{label_part} {bar} {percent_part} ({current}/{total})"
        
        return self.box_line(content)
    
    def box_list_item(self, marker: str, text: str, indent: int = 0) -> str:
        """
        Create list item line.
        
        Args:
            marker: List marker (•, -, 1., etc.)
            text: Item text
            indent: Indentation level
            
        Returns:
            Formatted list item line
        """
        width = self.config.width
        content_width = width - 2 * self.config.padding
        
        indent_str = "  " * indent
        item = f"{indent_str}{marker} {text}"
        
        # Truncate if too long
        if len(item) > content_width:
            item = item[:content_width - 3] + "..."
        
        return self.box_line(item)
    
    def box_section_header(self, title: str, subtitle: Optional[str] = None) -> List[str]:
        """
        Create section header lines.
        
        Args:
            title: Section title
            subtitle: Optional subtitle
            
        Returns:
            List of formatted lines
        """
        lines = [self.box_line(title, align="center")]
        
        if subtitle:
            lines.append(self.box_line(subtitle, align="center"))
        
        return lines
    
    def format_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        title: Optional[str] = None,
        footer: Optional[str] = None
    ) -> str:
        """
        Format complete table with headers and rows.
        
        Args:
            headers: Column headers
            rows: List of row data (each row is list of column values)
            title: Optional table title
            footer: Optional footer message
            
        Returns:
            Complete formatted table as string
        """
        lines = []
        
        # Top border
        lines.append(self.box_top(title))
        
        # Headers
        if headers:
            lines.append(self.box_multi_column(headers))
            lines.append(self.box_separator())
        
        # Rows
        for row in rows:
            lines.append(self.box_multi_column(row))
        
        # Footer
        if footer:
            lines.append(self.box_separator())
            lines.append(self.box_line(footer))
        
        # Bottom border
        lines.append(self.box_bottom())
        
        return "\n".join(lines)
    
    def format_info_panel(
        self,
        title: str,
        data: Dict[str, Any],
        footer: Optional[str] = None
    ) -> str:
        """
        Format information panel with key-value pairs.
        
        Args:
            title: Panel title
            data: Dictionary of key-value pairs
            footer: Optional footer message
            
        Returns:
            Complete formatted panel as string
        """
        lines = []
        
        # Top border
        lines.append(self.box_top(title))
        lines.append(self.box_separator())
        
        # Data rows
        for key, value in data.items():
            lines.append(self.box_kv_line(key, str(value)))
        
        # Footer
        if footer:
            lines.append(self.box_separator())
            lines.append(self.box_line(footer))
        
        # Bottom border
        lines.append(self.box_bottom())
        
        return "\n".join(lines)
    
    def format_list(
        self,
        title: str,
        items: List[str],
        numbered: bool = False,
        footer: Optional[str] = None
    ) -> str:
        """
        Format list with items.
        
        Args:
            title: List title
            items: List of item strings
            numbered: Use numbered list (1., 2., etc.)
            footer: Optional footer message
            
        Returns:
            Complete formatted list as string
        """
        lines = []
        
        # Top border
        lines.append(self.box_top(title))
        lines.append(self.box_separator())
        
        # Items
        for i, item in enumerate(items, 1):
            marker = f"{i}." if numbered else "•"
            lines.append(self.box_list_item(marker, item))
        
        # Footer
        if footer:
            lines.append(self.box_separator())
            lines.append(self.box_line(footer))
        
        # Bottom border
        lines.append(self.box_bottom())
        
        return "\n".join(lines)


# Convenience function for quick formatting
def format_box(
    content: List[str],
    title: Optional[str] = None,
    footer: Optional[str] = None,
    width: int = 61
) -> str:
    """
    Quick format content in a box.
    
    Args:
        content: List of content lines
        title: Optional title
        footer: Optional footer
        width: Box width
        
    Returns:
        Formatted box as string
    """
    config = ColumnConfig(width=width)
    formatter = ColumnFormatter(config)
    
    lines = []
    lines.append(formatter.box_top(title))
    
    if title:
        lines.append(formatter.box_separator())
    
    for line in content:
        lines.append(formatter.box_line(line))
    
    if footer:
        lines.append(formatter.box_separator())
        lines.append(formatter.box_line(footer))
    
    lines.append(formatter.box_bottom())
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo usage
    formatter = ColumnFormatter()
    
    print("=== Info Panel Demo ===")
    print(formatter.format_info_panel(
        title="System Status",
        data={
            "Version": "v1.2.22",
            "Tests": "45/45 passing",
            "Status": "Production Ready",
            "Memory": "52M"
        },
        footer="💡 Use STATUS for full details"
    ))
    
    print("\n=== List Demo ===")
    print(formatter.format_list(
        title="Available Commands",
        items=[
            "TIME - Show current time",
            "CLOCK - ASCII clock display",
            "CALENDAR - View calendar",
            "JSON VIEW - Interactive JSON editor"
        ],
        numbered=True,
        footer="💡 Use HELP <command> for details"
    ))
    
    print("\n=== Progress Bar Demo ===")
    print(formatter.box_top("Download Progress"))
    print(formatter.box_separator())
    print(formatter.box_progress_bar("Files", 7, 10))
    print(formatter.box_progress_bar("Size", 42, 100))
    print(formatter.box_bottom())
