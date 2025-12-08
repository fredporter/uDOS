"""
uDOS v1.1.15 - ASCII Graphics Generator

Enhanced ASCII diagram generation with Unicode box-drawing characters.

Features:
- Two house styles: Plain ASCII (max compatibility) + Block shading (visual hierarchy)
- Unicode box-drawing: ┌─┐ │ └─┘ ├─┤ ┬ ┴ ┼
- Improved flowchart, table, and alignment algorithms
- Template-based generation
- Export to .txt files

House Styles:
1. Plain ASCII (graphics2.md) - Maximum compatibility, no block characters
2. Block Shading (graphics1.md) - Visual hierarchy with █▓▒░

Author: uDOS Development Team
Version: 1.1.15
"""

from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
from core.utils.paths import PATHS


class ASCIIGenerator:
    """Generate refined ASCII diagrams with Unicode box-drawing."""

    def __init__(self, style: str = "plain"):
        """
        Initialize ASCII generator.

        Args:
            style: "plain" (max compatibility) or "blocks" (visual hierarchy)
        """
        self.style = style

        # Unicode box-drawing characters (refined style)
        self.box_chars_unicode = {
            # Corners
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            # Lines
            'h': '─', 'v': '│',
            # Intersections
            'x': '┼',  # Cross
            'lt': '├', 'rt': '┤', 'tt': '┬', 'bt': '┴',
            # Double lines
            'dh': '═', 'dv': '║',
            'dtl': '╔', 'dtr': '╗', 'dbl': '╚', 'dbr': '╝',
        }

        # Plain ASCII characters (maximum compatibility)
        self.box_chars_plain = {
            'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
            'h': '-', 'v': '|',
            'x': '+',
            'lt': '+', 'rt': '+', 'tt': '+', 'bt': '+',
            'dh': '=', 'dv': '|',
            'dtl': '+', 'dtr': '+', 'dbl': '+', 'dbr': '+',
        }

        # Block shading characters
        self.block_chars = {
            'full': '█',    # Full block
            'dark': '▓',    # Dark shade
            'medium': '▒',  # Medium shade
            'light': '░',   # Light shade
        }

        # Select character set based on style
        if style == "unicode":
            self.chars = self.box_chars_unicode
        else:
            self.chars = self.box_chars_plain

    def generate_box(self, width: int, height: int, title: Optional[str] = None,
                     content: Optional[List[str]] = None, style: str = "single") -> str:
        """
        Generate a box with optional title and content.

        Args:
            width: Box width (including borders)
            height: Box height (including borders)
            title: Optional title text (centered)
            content: Optional list of content lines
            style: "single", "double", or "plain"

        Returns:
            ASCII box diagram
        """
        lines = []
        inner_width = width - 2

        # Select characters
        if style == "double":
            tl, tr, bl, br = self.chars['dtl'], self.chars['dtr'], self.chars['dbl'], self.chars['dbr']
            h, v = self.chars['dh'], self.chars['dv']
        else:
            tl, tr, bl, br = self.chars['tl'], self.chars['tr'], self.chars['bl'], self.chars['br']
            h, v = self.chars['h'], self.chars['v']

        # Top border
        if title:
            title_text = f" {title} "
            padding = (inner_width - len(title_text)) // 2
            title_line = tl + h * padding + title_text + h * (inner_width - padding - len(title_text)) + tr
            lines.append(title_line)
        else:
            lines.append(tl + h * inner_width + tr)

        # Content area
        content_lines = content if content else []
        current_height = 1  # Already added top border

        for line in content_lines:
            if current_height >= height - 1:
                break
            padded_line = line.ljust(inner_width)[:inner_width]
            lines.append(v + padded_line + v)
            current_height += 1

        # Fill remaining height with empty lines
        while current_height < height - 1:
            lines.append(v + ' ' * inner_width + v)
            current_height += 1

        # Bottom border
        lines.append(bl + h * inner_width + br)

        return '\n'.join(lines)

    def generate_panel(self, width: int, title: str, style: str = "blocks") -> str:
        """
        Generate a panel header (block style from graphics1.md).

        Args:
            width: Panel width
            title: Panel title (will be centered with [ ])
            style: "blocks" (█▓▒░) or "plain" (text only)

        Returns:
            Panel header (3 lines)
        """
        title_text = f"[{title}]"
        padding = (width - len(title_text)) // 2

        if style == "blocks":
            # Block style (graphics1.md)
            block = self.block_chars['full']
            top = block * width
            middle = block * padding + ' ' * len(title_text) + block * (width - padding - len(title_text))
            # Replace middle section with title
            middle = middle[:padding] + title_text + middle[padding + len(title_text):]
            bottom = block * width
            return f"{top}\n{middle}\n{bottom}"
        else:
            # Plain style (graphics2.md)
            top = f"[ {title.upper()} ]"
            bottom = '-' * len(top)
            return f"{top}\n{bottom}"

    def generate_table(self, headers: List[str], rows: List[List[str]],
                       column_widths: Optional[List[int]] = None) -> str:
        """
        Generate a table with headers and data rows.

        Args:
            headers: Column headers
            rows: Data rows (list of lists)
            column_widths: Optional custom column widths

        Returns:
            ASCII table
        """
        # Calculate column widths if not provided
        if not column_widths:
            column_widths = []
            for i, header in enumerate(headers):
                max_width = len(header)
                for row in rows:
                    if i < len(row):
                        max_width = max(max_width, len(str(row[i])))
                column_widths.append(max_width + 2)  # Add padding

        lines = []
        h, v = self.chars['h'], self.chars['v']
        tl, tr, bl, br = self.chars['tl'], self.chars['tr'], self.chars['bl'], self.chars['br']
        lt, rt, tt, bt, x = self.chars['lt'], self.chars['rt'], self.chars['tt'], self.chars['bt'], self.chars['x']

        # Top border
        top_parts = [tl]
        for width in column_widths:
            top_parts.append(h * width)
            top_parts.append(tt)
        top_parts[-1] = tr  # Replace last tt with tr
        lines.append(''.join(top_parts))

        # Header row
        header_parts = [v]
        for i, header in enumerate(headers):
            header_parts.append(f" {header}".ljust(column_widths[i]))
            header_parts.append(v)
        lines.append(''.join(header_parts))

        # Header separator
        sep_parts = [lt]
        for width in column_widths:
            sep_parts.append(h * width)
            sep_parts.append(x)
        sep_parts[-1] = rt  # Replace last x with rt
        lines.append(''.join(sep_parts))

        # Data rows
        for row in rows:
            row_parts = [v]
            for i, cell in enumerate(row):
                cell_text = f" {cell}".ljust(column_widths[i])
                row_parts.append(cell_text)
                row_parts.append(v)
            lines.append(''.join(row_parts))

        # Bottom border
        bottom_parts = [bl]
        for width in column_widths:
            bottom_parts.append(h * width)
            bottom_parts.append(bt)
        bottom_parts[-1] = br  # Replace last bt with br
        lines.append(''.join(bottom_parts))

        return '\n'.join(lines)

    def generate_flowchart(self, nodes: List[Dict[str, Any]], connections: List[Tuple[str, str]]) -> str:
        """
        Generate a simple flowchart.

        Args:
            nodes: List of node dicts with 'id', 'label', 'shape' ('box', 'diamond', 'circle')
            connections: List of (from_id, to_id) tuples

        Returns:
            ASCII flowchart
        """
        # Simple vertical flowchart layout
        lines = []
        node_map = {node['id']: node for node in nodes}

        for i, node in enumerate(nodes):
            # Draw node based on shape
            label = node['label']
            shape = node.get('shape', 'box')

            if shape == 'box':
                # Rectangle
                lines.append(self.chars['tl'] + self.chars['h'] * (len(label) + 2) + self.chars['tr'])
                lines.append(self.chars['v'] + f" {label} " + self.chars['v'])
                lines.append(self.chars['bl'] + self.chars['h'] * (len(label) + 2) + self.chars['br'])
            elif shape == 'diamond':
                # Diamond (decision)
                lines.append(f"  {self.chars['h']}{label}{self.chars['h']}")
                lines.append(f" {self.chars['v']}   {self.chars['v']}")
                lines.append(f"  {self.chars['h']}{self.chars['h']}{self.chars['h']}")
            else:
                # Circle (simple)
                lines.append(f"( {label} )")

            # Draw connection arrow if not last node
            if i < len(nodes) - 1:
                # Check if there's a connection
                has_connection = any(
                    from_id == node['id'] for from_id, to_id in connections
                )
                if has_connection:
                    lines.append('  ' + self.chars['v'])

        return '\n'.join(lines)

    def generate_progress_bar(self, label: str, percentage: int, width: int = 40,
                             style: str = "blocks") -> str:
        """
        Generate a progress bar.

        Args:
            label: Progress bar label
            percentage: Completion percentage (0-100)
            width: Bar width
            style: "blocks" (█░) or "chars" (=#-)

        Returns:
            Progress bar line
        """
        filled = int(width * percentage / 100)
        empty = width - filled

        if style == "blocks":
            fill_char = self.block_chars['full']
            empty_char = self.block_chars['light']
            bar = fill_char * filled + empty_char * empty
        else:
            bar = '=' * filled + '-' * empty

        return f"{label.ljust(15)} [{bar}] {percentage}%"

    def generate_tree(self, root: str, children: Dict[str, List[str]],
                     indent: str = "  ", prefix: str = "") -> str:
        """
        Generate a tree structure.

        Args:
            root: Root node label
            children: Dict mapping parent to children
            indent: Indentation per level
            prefix: Current line prefix

        Returns:
            ASCII tree diagram
        """
        lines = [prefix + root]

        if root in children:
            child_list = children[root]
            for i, child in enumerate(child_list):
                is_last = (i == len(child_list) - 1)
                connector = self.chars['bl'] + self.chars['h'] if is_last else self.chars['lt'] + self.chars['h']
                new_prefix = prefix + (indent if is_last else self.chars['v'] + ' ')

                child_tree = self.generate_tree(child, children, indent, new_prefix)
                lines.append(prefix + connector + child_tree.split('\n')[0][len(new_prefix):])

                # Add remaining lines from child tree
                for line in child_tree.split('\n')[1:]:
                    lines.append(line)

        return '\n'.join(lines)

    def generate_list(self, items: List[str], style: str = "bullet") -> str:
        """
        Generate a formatted list.

        Args:
            items: List items
            style: "bullet" (•), "number" (1. 2. 3.), "checkbox" ([ ])

        Returns:
            Formatted list
        """
        lines = []

        for i, item in enumerate(items, 1):
            if style == "bullet":
                lines.append(f"• {item}")
            elif style == "number":
                lines.append(f"{i}. {item}")
            elif style == "checkbox":
                lines.append(f"[ ] {item}")
            elif style == "checkbox-checked":
                lines.append(f"[x] {item}")

        return '\n'.join(lines)

    def generate_banner(self, text: str, width: int = 60, style: str = "double") -> str:
        """
        Generate a banner with centered text.

        Args:
            text: Banner text
            width: Banner width
            style: "single", "double", or "blocks"

        Returns:
            ASCII banner
        """
        if style == "blocks":
            # Block style banner (graphics1.md)
            block = self.block_chars['full']
            padding = (width - len(text) - 4) // 2

            top = block * width
            middle = block * padding + f" [{text}] " + block * (width - padding - len(text) - 4)
            bottom = block * width

            return f"{top}\n{middle}\n{bottom}"
        else:
            # Box style banner
            return self.generate_box(width, 3, title=text, style=style)

    def save(self, content: str, filename: str, output_dir: Path = PATHS.MEMORY_DRAFTS_ASCII) -> Path:
        """
        Save ASCII diagram to file.

        Args:
            content: ASCII diagram content
            filename: Output filename
            output_dir: Output directory

        Returns:
            Path to saved file
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename.endswith('.txt'):
            filename += '.txt'

        output_path = output_dir / filename
        output_path.write_text(content, encoding='utf-8')

        return output_path


def get_ascii_generator(style: str = "plain") -> ASCIIGenerator:
    """
    Get ASCII generator instance.

    Args:
        style: "plain" (max compatibility) or "unicode" (refined) or "blocks" (visual hierarchy)

    Returns:
        ASCIIGenerator instance
    """
    return ASCIIGenerator(style=style)
