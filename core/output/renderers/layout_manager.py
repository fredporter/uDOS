"""
uDOS Layout Manager - Responsive terminal layouts and adaptive content formatting.

This module provides dynamic layout management that adapts to different screen
sizes, supports window resizing, split-pane layouts, and optimal content formatting.

Author: uDOS Development Team
Version: 1.0.6
"""

import os
import shutil
import threading
import time
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum


class LayoutMode(Enum):
    """Layout modes for different screen configurations."""
    COMPACT = "compact"      # Small screens, minimal decorations
    STANDARD = "standard"    # Normal screens, balanced layout
    EXPANDED = "expanded"    # Large screens, maximum information
    SPLIT = "split"          # Split-pane layout
    DASHBOARD = "dashboard"  # Dashboard-style layout


class ContentType(Enum):
    """Types of content for adaptive formatting."""
    TEXT = "text"
    TABLE = "table"
    TREE = "tree"
    LIST = "list"
    GRID = "grid"
    STATUS = "status"
    HELP = "help"
    ERROR = "error"


@dataclass
class TerminalDimensions:
    """Terminal dimensions and characteristics."""
    width: int
    height: int
    is_wide: bool = False      # Width > 120 columns
    is_tall: bool = False      # Height > 30 rows
    is_mobile: bool = False    # Very small screen
    is_ultra_wide: bool = False # Ultra-wide display
    aspect_ratio: float = 0.0

    def __post_init__(self):
        self.is_wide = self.width > 120
        self.is_tall = self.height > 30
        self.is_mobile = self.width < 60 or self.height < 15
        self.is_ultra_wide = self.width > 200
        self.aspect_ratio = self.width / self.height if self.height > 0 else 0.0


@dataclass
class LayoutConfig:
    """Configuration for layout management."""
    auto_adapt: bool = True
    min_width: int = 40
    max_width: int = 200
    preferred_width: int = 80
    content_margin: int = 2
    use_unicode: bool = True
    compact_mode: bool = False
    show_borders: bool = True
    responsive_tables: bool = True
    adaptive_columns: bool = True


class ContentFormatter:
    """Adaptive content formatter for different screen sizes."""

    def __init__(self, dimensions: TerminalDimensions, config: LayoutConfig):
        self.dimensions = dimensions
        self.config = config

    def format_content(self, content: str, content_type: ContentType,
                      title: str = "", metadata: Dict[str, Any] = None) -> str:
        """
        Format content adaptively based on screen size and content type.

        Args:
            content: Raw content to format
            content_type: Type of content
            title: Optional title
            metadata: Additional formatting metadata

        Returns:
            Formatted content string
        """
        metadata = metadata or {}

        if content_type == ContentType.TABLE:
            return self._format_table(content, title, metadata)
        elif content_type == ContentType.TREE:
            return self._format_tree(content, title, metadata)
        elif content_type == ContentType.LIST:
            return self._format_list(content, title, metadata)
        elif content_type == ContentType.GRID:
            return self._format_grid(content, title, metadata)
        elif content_type == ContentType.STATUS:
            return self._format_status(content, title, metadata)
        elif content_type == ContentType.HELP:
            return self._format_help(content, title, metadata)
        elif content_type == ContentType.ERROR:
            return self._format_error(content, title, metadata)
        else:  # TEXT
            return self._format_text(content, title, metadata)

    def _format_table(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format table content adaptively."""
        lines = content.strip().split('\n')
        if not lines:
            return content

        # Parse table data
        if '|' in lines[0]:
            # Pipe-separated table
            rows = [line.split('|') for line in lines]
        else:
            # Space-separated table (try to detect columns)
            rows = [line.split() for line in lines]

        if not rows:
            return content

        # Adaptive column sizing
        if self.dimensions.is_mobile:
            return self._format_mobile_table(rows, title)
        elif self.dimensions.is_wide:
            return self._format_wide_table(rows, title)
        else:
            return self._format_standard_table(rows, title)

    def _format_mobile_table(self, rows: List[List[str]], title: str) -> str:
        """Format table for mobile/small screens."""
        if not rows:
            return ""

        result = []
        if title:
            result.append(f"📱 {title}")
            result.append("─" * min(30, self.dimensions.width - 2))

        # For mobile, show data vertically
        headers = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []

        for i, row in enumerate(data_rows[:5]):  # Limit to 5 items on mobile
            if i > 0:
                result.append("")

            result.append(f"Item {i + 1}:")
            for j, (header, value) in enumerate(zip(headers, row)):
                if j < 3:  # Show only first 3 columns on mobile
                    result.append(f"  {header}: {value}")

            if len(row) > 3:
                result.append(f"  ... and {len(row) - 3} more fields")

        if len(data_rows) > 5:
            result.append(f"\n... and {len(data_rows) - 5} more items")

        return '\n'.join(result)

    def _format_wide_table(self, rows: List[List[str]], title: str) -> str:
        """Format table for wide screens."""
        if not rows:
            return ""

        result = []
        if title:
            title_width = min(self.dimensions.width - 4, 100)
            result.append(f"{'🖥️ ' + title:^{title_width}}")
            result.append("═" * title_width)

        # Calculate column widths
        max_cols = len(max(rows, key=len)) if rows else 0
        available_width = self.dimensions.width - 4

        # Give more space to columns on wide screens
        col_widths = []
        for col in range(max_cols):
            col_data = [row[col] if col < len(row) else "" for row in rows]
            max_content = max(len(str(item)) for item in col_data) if col_data else 0
            # Allow wider columns on wide screens
            col_width = min(max_content + 2, available_width // max(max_cols, 1))
            col_widths.append(max(col_width, 8))

        # Format rows with borders
        for i, row in enumerate(rows):
            if i == 0:  # Header
                result.append("┌" + "┬".join("─" * w for w in col_widths) + "┐")
            elif i == 1:  # After header
                result.append("├" + "┼".join("─" * w for w in col_widths) + "┤")

            formatted_row = "│"
            for j, cell in enumerate(row):
                if j < len(col_widths):
                    cell_str = str(cell)[:col_widths[j]-2]
                    formatted_row += f" {cell_str:<{col_widths[j]-2}} │"
            result.append(formatted_row)

        if rows:
            result.append("└" + "┴".join("─" * w for w in col_widths) + "┘")

        return '\n'.join(result)

    def _format_standard_table(self, rows: List[List[str]], title: str) -> str:
        """Format table for standard screens."""
        if not rows:
            return ""

        result = []
        if title:
            result.append(f"📊 {title}")
            result.append("─" * min(self.dimensions.width - 2, 60))

        # Simple table format for standard screens
        max_cols = len(max(rows, key=len)) if rows else 0
        available_width = self.dimensions.width - 4

        # Calculate balanced column widths
        col_widths = []
        base_width = max(available_width // max_cols, 8) if max_cols > 0 else 8

        for col in range(max_cols):
            col_data = [row[col] if col < len(row) else "" for row in rows]
            max_content = max(len(str(item)) for item in col_data) if col_data else 0
            col_width = min(max_content + 1, base_width)
            col_widths.append(max(col_width, 6))

        # Format rows
        for i, row in enumerate(rows):
            if i == 0:  # Header
                formatted_row = ""
                for j, cell in enumerate(row):
                    if j < len(col_widths):
                        cell_str = str(cell)[:col_widths[j]]
                        formatted_row += f"{cell_str:<{col_widths[j]}} "
                result.append(formatted_row.rstrip())
                result.append("─" * min(len(formatted_row), self.dimensions.width - 2))
            else:  # Data rows
                formatted_row = ""
                for j, cell in enumerate(row):
                    if j < len(col_widths):
                        cell_str = str(cell)[:col_widths[j]]
                        formatted_row += f"{cell_str:<{col_widths[j]}} "
                result.append(formatted_row.rstrip())

        return '\n'.join(result)

    def _format_tree(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format tree content adaptively."""
        lines = content.strip().split('\n')
        if not lines:
            return content

        result = []
        if title:
            if self.dimensions.is_mobile:
                result.append(f"📱🌳 {title}")
            else:
                result.append(f"🌳 {title}")
            result.append("─" * min(self.dimensions.width - 2, 50))

        # Adjust indentation based on screen width
        if self.dimensions.is_mobile:
            # Reduce indentation for mobile
            for line in lines:
                # Convert tree characters for mobile
                mobile_line = line.replace('├──', '├─').replace('└──', '└─')
                mobile_line = mobile_line.replace('│   ', '│ ')
                result.append(mobile_line[:self.dimensions.width - 2])
        elif self.dimensions.is_wide:
            # Enhanced tree for wide screens
            for line in lines:
                enhanced_line = line.replace('├──', '├───').replace('└──', '└───')
                result.append(enhanced_line)
        else:
            # Standard tree formatting
            result.extend(lines)

        return '\n'.join(result)

    def _format_list(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format list content adaptively."""
        lines = content.strip().split('\n')
        if not lines:
            return content

        result = []
        if title:
            result.append(f"📋 {title}")
            result.append("─" * min(self.dimensions.width - 2, 40))

        # Adaptive list formatting
        for i, line in enumerate(lines):
            if self.dimensions.is_mobile:
                # Simplified bullets for mobile
                if line.strip().startswith('•') or line.strip().startswith('-'):
                    result.append(f"{i+1}. {line.strip()[1:].strip()}")
                else:
                    result.append(f"{i+1}. {line.strip()}")
            elif self.dimensions.is_wide:
                # Enhanced bullets for wide screens
                if not line.strip().startswith(('•', '-', '*')):
                    result.append(f"▶ {line.strip()}")
                else:
                    result.append(line)
            else:
                # Standard list formatting
                result.append(line)

        return '\n'.join(result)

    def _format_grid(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format grid content adaptively."""
        # Grid formatting based on terminal dimensions
        grid_width = metadata.get('grid_width', 3)

        if self.dimensions.is_mobile:
            grid_width = 1  # Single column on mobile
        elif self.dimensions.is_wide:
            grid_width = min(grid_width * 2, 6)  # More columns on wide screens

        lines = content.strip().split('\n')
        items = [line.strip() for line in lines if line.strip()]

        result = []
        if title:
            result.append(f"⊞ {title}")
            result.append("─" * min(self.dimensions.width - 2, 40))

        # Format items in grid
        for i in range(0, len(items), grid_width):
            row_items = items[i:i + grid_width]
            if self.dimensions.is_mobile:
                result.extend(row_items)
            else:
                row = "  ".join(f"{item:<15}" for item in row_items)
                result.append(row[:self.dimensions.width - 2])

        return '\n'.join(result)

    def _format_status(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format status content adaptively."""
        lines = content.strip().split('\n')

        result = []
        if title:
            status_icon = "📊" if not self.dimensions.is_mobile else "📱"
            result.append(f"{status_icon} {title}")

            if not self.dimensions.is_mobile:
                result.append("═" * min(self.dimensions.width - 2, 50))

        # Adaptive status formatting
        for line in lines:
            if self.dimensions.is_mobile:
                # Compact status for mobile
                if ':' in line:
                    key, value = line.split(':', 1)
                    result.append(f"{key.strip()}: {value.strip()}")
                else:
                    result.append(line)
            else:
                # Full status for larger screens
                result.append(line)

        return '\n'.join(result)

    def _format_help(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format help content adaptively."""
        lines = content.strip().split('\n')

        result = []
        if title:
            help_icon = "❓" if self.dimensions.is_mobile else "📖"
            result.append(f"{help_icon} {title}")
            result.append("─" * min(self.dimensions.width - 2, 60))

        # Adaptive help formatting
        current_section = []
        for line in lines:
            if self.dimensions.is_mobile:
                # Simplified help for mobile
                if line.strip().startswith('#'):
                    if current_section:
                        result.extend(current_section[:3])  # Show only first 3 lines
                        if len(current_section) > 3:
                            result.append("  ...")
                        current_section = []
                    result.append(line.replace('#', '').strip())
                else:
                    current_section.append(line)
            else:
                # Full help for larger screens
                result.append(line)

        if self.dimensions.is_mobile and current_section:
            result.extend(current_section[:3])
            if len(current_section) > 3:
                result.append("  ...")

        return '\n'.join(result)

    def _format_error(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format error content adaptively."""
        lines = content.strip().split('\n')

        result = []
        if title:
            result.append(f"❌ {title}")
            if not self.dimensions.is_mobile:
                result.append("!" * min(self.dimensions.width - 2, 40))

        # Error formatting
        for line in lines:
            if self.dimensions.is_mobile:
                # Wrap long error messages on mobile
                if len(line) > self.dimensions.width - 2:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        if len(current_line + word) < self.dimensions.width - 2:
                            current_line += word + " "
                        else:
                            if current_line:
                                result.append(current_line.strip())
                            current_line = word + " "
                    if current_line:
                        result.append(current_line.strip())
                else:
                    result.append(line)
            else:
                result.append(line)

        return '\n'.join(result)

    def _format_text(self, content: str, title: str, metadata: Dict[str, Any]) -> str:
        """Format text content adaptively."""
        lines = content.strip().split('\n')

        result = []
        if title:
            result.append(f"📄 {title}")
            result.append("─" * min(self.dimensions.width - 2, 50))

        # Adaptive text wrapping
        for line in lines:
            if len(line) <= self.dimensions.width - self.config.content_margin:
                result.append(line)
            else:
                # Wrap long lines
                words = line.split()
                current_line = ""

                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if len(test_line) <= self.dimensions.width - self.config.content_margin:
                        current_line = test_line
                    else:
                        if current_line:
                            result.append(current_line)
                        current_line = word

                if current_line:
                    result.append(current_line)

        return '\n'.join(result)


class LayoutManager:
    """Responsive layout manager for uDOS terminal interface."""

    def __init__(self):
        """Initialize layout manager."""
        self.current_dimensions = self._get_terminal_dimensions()
        self.current_mode = self._determine_layout_mode()
        self.config = LayoutConfig()
        self.formatter = ContentFormatter(self.current_dimensions, self.config)

        # Layout state
        self.split_panes = []
        self.current_pane = 0
        self.layout_stack = []

        # Auto-detection
        self.auto_resize_enabled = True
        self._last_resize_check = time.time()
        self._resize_thread = None

        if self.auto_resize_enabled:
            self._start_resize_monitoring()

    def _get_terminal_dimensions(self) -> TerminalDimensions:
        """Get current terminal dimensions."""
        try:
            size = shutil.get_terminal_size()
            return TerminalDimensions(
                width=size.columns,
                height=size.lines
            )
        except:
            # Fallback dimensions
            return TerminalDimensions(width=80, height=24)

    def _determine_layout_mode(self) -> LayoutMode:
        """Determine appropriate layout mode based on terminal size."""
        dims = self.current_dimensions

        if dims.is_mobile:
            return LayoutMode.COMPACT
        elif dims.is_ultra_wide:
            return LayoutMode.EXPANDED
        elif dims.is_wide and dims.is_tall:
            return LayoutMode.SPLIT
        else:
            return LayoutMode.STANDARD

    def _start_resize_monitoring(self):
        """Start background thread to monitor terminal resize."""
        def monitor_resize():
            while self.auto_resize_enabled:
                time.sleep(1)  # Check every second
                new_dimensions = self._get_terminal_dimensions()

                if (new_dimensions.width != self.current_dimensions.width or
                    new_dimensions.height != self.current_dimensions.height):

                    self._handle_resize(new_dimensions)

                self._last_resize_check = time.time()

        self._resize_thread = threading.Thread(target=monitor_resize, daemon=True)
        self._resize_thread.start()

    def _handle_resize(self, new_dimensions: TerminalDimensions):
        """Handle terminal resize event."""
        old_mode = self.current_mode
        self.current_dimensions = new_dimensions
        self.current_mode = self._determine_layout_mode()

        # Update formatter
        self.formatter = ContentFormatter(self.current_dimensions, self.config)

        # Trigger layout update if mode changed
        if old_mode != self.current_mode:
            self._trigger_layout_update()

    def _trigger_layout_update(self):
        """Trigger layout update callback (would integrate with main UI)."""
        # This would be called to refresh the current display
        pass

    def format_content(self, content: str, content_type: ContentType = ContentType.TEXT,
                      title: str = "", metadata: Dict[str, Any] = None) -> str:
        """
        Format content using adaptive layout.

        Args:
            content: Content to format
            content_type: Type of content
            title: Optional title
            metadata: Additional formatting metadata

        Returns:
            Formatted content
        """
        return self.formatter.format_content(content, content_type, title, metadata)

    def create_split_layout(self, pane_configs: List[Dict[str, Any]]) -> str:
        """
        Create a split-pane layout.

        Args:
            pane_configs: List of pane configurations

        Returns:
            Formatted split layout
        """
        if not self.current_dimensions.is_wide:
            # Fall back to vertical stacking on narrow screens
            return self._create_stacked_layout(pane_configs)

        pane_width = self.current_dimensions.width // len(pane_configs)
        result = []

        # Create horizontal split
        for i, config in enumerate(pane_configs):
            content = config.get('content', '')
            title = config.get('title', f'Pane {i+1}')
            content_type = config.get('content_type', ContentType.TEXT)

            # Format content for this pane
            pane_formatter = ContentFormatter(
                TerminalDimensions(pane_width - 2, self.current_dimensions.height - 4),
                self.config
            )

            formatted_content = pane_formatter.format_content(content, content_type, title)

            # Add pane borders
            pane_lines = formatted_content.split('\n')
            bordered_pane = []

            for j, line in enumerate(pane_lines):
                if j == 0:
                    bordered_pane.append(f"┌{'─' * (pane_width - 2)}┐")
                    bordered_pane.append(f"│{line[:pane_width-2]:<{pane_width-2}}│")
                elif j == len(pane_lines) - 1:
                    bordered_pane.append(f"│{line[:pane_width-2]:<{pane_width-2}}│")
                    bordered_pane.append(f"└{'─' * (pane_width - 2)}┘")
                else:
                    bordered_pane.append(f"│{line[:pane_width-2]:<{pane_width-2}}│")

            if i == 0:
                result = bordered_pane
            else:
                # Merge panes horizontally
                for k, line in enumerate(bordered_pane):
                    if k < len(result):
                        result[k] += line
                    else:
                        result.append(line)

        return '\n'.join(result)

    def _create_stacked_layout(self, pane_configs: List[Dict[str, Any]]) -> str:
        """Create a vertical stacked layout for narrow screens."""
        result = []

        for i, config in enumerate(pane_configs):
            if i > 0:
                result.append("─" * self.current_dimensions.width)

            content = config.get('content', '')
            title = config.get('title', f'Section {i+1}')
            content_type = config.get('content_type', ContentType.TEXT)

            formatted_content = self.format_content(content, content_type, title)
            result.append(formatted_content)

        return '\n'.join(result)

    def create_dashboard_layout(self, sections: Dict[str, Any]) -> str:
        """
        Create a dashboard-style layout.

        Args:
            sections: Dictionary of dashboard sections

        Returns:
            Formatted dashboard layout
        """
        if self.current_dimensions.is_mobile:
            return self._create_mobile_dashboard(sections)
        elif self.current_dimensions.is_wide:
            return self._create_wide_dashboard(sections)
        else:
            return self._create_standard_dashboard(sections)

    def _create_mobile_dashboard(self, sections: Dict[str, Any]) -> str:
        """Create mobile-optimized dashboard."""
        result = []
        result.append("📱 Dashboard")
        result.append("=" * min(self.current_dimensions.width - 2, 30))

        # Show only essential sections on mobile
        priority_sections = ['status', 'alerts', 'recent']

        for section_name in priority_sections:
            if section_name in sections:
                section_data = sections[section_name]
                content = section_data.get('content', '')
                title = section_data.get('title', section_name.title())

                result.append("")
                formatted = self.format_content(content, ContentType.STATUS, title)
                result.append(formatted)

        # Show count of remaining sections
        remaining = len(sections) - len([s for s in priority_sections if s in sections])
        if remaining > 0:
            result.append(f"\n... and {remaining} more sections")
            result.append("💡 Use larger screen for full dashboard")

        return '\n'.join(result)

    def _create_wide_dashboard(self, sections: Dict[str, Any]) -> str:
        """Create wide-screen dashboard with multiple columns."""
        # Split sections into columns
        section_items = list(sections.items())
        cols = 3 if self.current_dimensions.is_ultra_wide else 2
        col_width = self.current_dimensions.width // cols

        columns = [[] for _ in range(cols)]

        # Distribute sections across columns
        for i, (section_name, section_data) in enumerate(section_items):
            col_index = i % cols
            content = section_data.get('content', '')
            title = section_data.get('title', section_name.title())
            content_type = section_data.get('content_type', ContentType.STATUS)

            # Format content for column width
            col_formatter = ContentFormatter(
                TerminalDimensions(col_width - 4, self.current_dimensions.height),
                self.config
            )

            formatted = col_formatter.format_content(content, content_type, title)
            columns[col_index].extend(formatted.split('\n'))

        # Merge columns
        result = []
        max_lines = max(len(col) for col in columns)

        for line_num in range(max_lines):
            line_parts = []
            for col in columns:
                if line_num < len(col):
                    line_parts.append(f"{col[line_num]:<{col_width-2}}")
                else:
                    line_parts.append(" " * (col_width - 2))
            result.append("  ".join(line_parts))

        return '\n'.join(result)

    def _create_standard_dashboard(self, sections: Dict[str, Any]) -> str:
        """Create standard dashboard layout."""
        result = []
        result.append("📊 uDOS Dashboard")
        result.append("═" * min(self.current_dimensions.width - 2, 60))

        for section_name, section_data in sections.items():
            content = section_data.get('content', '')
            title = section_data.get('title', section_name.title())
            content_type = section_data.get('content_type', ContentType.STATUS)

            result.append("")
            formatted = self.format_content(content, content_type, title)
            result.append(formatted)

        return '\n'.join(result)

    def get_layout_info(self) -> Dict[str, Any]:
        """Get current layout information."""
        return {
            'dimensions': {
                'width': self.current_dimensions.width,
                'height': self.current_dimensions.height,
                'is_wide': self.current_dimensions.is_wide,
                'is_tall': self.current_dimensions.is_tall,
                'is_mobile': self.current_dimensions.is_mobile,
                'is_ultra_wide': self.current_dimensions.is_ultra_wide,
                'aspect_ratio': self.current_dimensions.aspect_ratio
            },
            'layout_mode': self.current_mode.value,
            'config': {
                'auto_adapt': self.config.auto_adapt,
                'responsive_tables': self.config.responsive_tables,
                'adaptive_columns': self.config.adaptive_columns,
                'compact_mode': self.config.compact_mode
            },
            'auto_resize_enabled': self.auto_resize_enabled
        }

    def set_layout_mode(self, mode: LayoutMode):
        """Manually set layout mode."""
        self.current_mode = mode
        self.formatter = ContentFormatter(self.current_dimensions, self.config)

    def update_config(self, **kwargs):
        """Update layout configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # Update formatter with new config
        self.formatter = ContentFormatter(self.current_dimensions, self.config)


# Global layout manager instance
layout_manager = LayoutManager()
