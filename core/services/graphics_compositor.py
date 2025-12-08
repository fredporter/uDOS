"""Graphics Compositor - Generate ASCII/Teletext diagrams from block library.

This service composes diagrams programmatically using the chunky teletext
block library for consistent, retro-aesthetic graphics throughout uDOS.

Usage:
    from core.services.graphics_compositor import GraphicsCompositor

    gc = GraphicsCompositor()

    # Create a flow diagram
    flow = gc.create_flow(['Collect', 'Filter', 'Boil', 'Store'])
    print(flow)

    # Create a tree hierarchy
    tree = gc.create_tree('Shelter', ['Natural', 'Constructed', 'Improvised'])
    print(tree)

    # Create a comparison grid
    grid = gc.create_grid(
        headers=['Method', 'Time', 'Difficulty'],
        rows=[['Friction', '10min', 'Hard'], ['Flint', '2min', 'Easy']]
    )
    print(grid)
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class GraphicsCompositor:
    """Compose ASCII/Teletext diagrams from block library."""

    def __init__(self):
        """Initialize compositor with block library."""
        self.blocks_dir = Path('core/data/graphics/blocks')
        self.templates_dir = Path('core/data/graphics/templates')

        # Load block sets
        self.teletext = self._load_json('teletext.json')
        self.patterns = self._load_json('patterns.json')
        self.borders = self._load_json('borders.json')

        # Load templates
        self.flow_template = self._load_template('flow_diagram.json')
        self.tree_template = self._load_template('tree_diagram.json')
        self.grid_template = self._load_template('grid_diagram.json')

    def _load_json(self, filename: str) -> Dict:
        """Load JSON from blocks directory."""
        path = self.blocks_dir / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_template(self, filename: str) -> Dict:
        """Load template from templates directory."""
        path = self.templates_dir / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    # ═══════════════════════════════════════════════════════════════════
    # Box/Panel Creation
    # ═══════════════════════════════════════════════════════════════════

    def create_box(
        self,
        width: int,
        height: int,
        title: str = "",
        style: str = 'heavy',
        content: List[str] = None
    ) -> str:
        """Create bordered box with optional title and content.

        Args:
            width: Box width in characters
            height: Box height in lines
            title: Optional title (centered on top border)
            style: Border style (heavy, double, light, rounded, block)
            content: Optional list of content lines

        Returns:
            Multi-line string with box
        """
        border = self.borders.get(style, self.borders['heavy'])

        # Top border with optional title
        if title:
            title_pad = (width - len(title) - 4) // 2
            remaining = width - len(title) - title_pad - 4
            top = (
                border['top_left'] +
                (border['horizontal'] * title_pad) +
                f" {title} " +
                (border['horizontal'] * remaining) +
                border['top_right']
            )
        else:
            top = (
                border['top_left'] +
                (border['horizontal'] * (width - 2)) +
                border['top_right']
            )

        # Middle lines
        middle_lines = []
        if content:
            for line in content:
                # Truncate or pad to fit
                padded = line[:width-4].ljust(width-4)
                middle_lines.append(f"{border['vertical']} {padded} {border['vertical']}")
        else:
            empty = ' ' * (width - 2)
            for _ in range(height - 2):
                middle_lines.append(f"{border['vertical']}{empty}{border['vertical']}")

        # Bottom border
        bottom = (
            border['bottom_left'] +
            (border['horizontal'] * (width - 2)) +
            border['bottom_right']
        )

        return '\n'.join([top] + middle_lines + [bottom])

    def create_chunky_box(self, width: int, label: str) -> str:
        """Create chunky teletext-style box for labels/buttons.

        Args:
            width: Box width (must be >= len(label) + 4)
            label: Text to display in box

        Returns:
            3-line chunky box
        """
        # Ensure width fits label
        min_width = len(label) + 4
        if width < min_width:
            width = min_width

        pad = width - 2
        top = "▐" + ("▀" * pad) + "▌"
        middle = f"▐ {label.center(pad-2)} ▌"
        bottom = "▐" + ("▄" * pad) + "▌"

        return '\n'.join([top, middle, bottom])

    # ═══════════════════════════════════════════════════════════════════
    # Flow Diagrams
    # ═══════════════════════════════════════════════════════════════════

    def create_flow(
        self,
        steps: List[str],
        style: str = 'chunky',
        width: int = 30
    ) -> str:
        """Create vertical flow diagram.

        Args:
            steps: List of step labels
            style: Box style (chunky, heavy, light)
            width: Width of each step box

        Returns:
            Multi-line flow diagram
        """
        lines = []
        arrow = self.teletext['arrows']['down']
        connector = self.teletext['box_drawing']['heavy']['vertical']

        for i, step in enumerate(steps):
            # Create step box
            if style == 'chunky':
                box = self.create_chunky_box(width, step)
            else:
                box = self.create_box(width, 3, content=[step], style=style)

            lines.append(box)

            # Add arrow between steps
            if i < len(steps) - 1:
                arrow_padding = ' ' * (width // 2 - 1)
                lines.append(f"{arrow_padding}{connector}")
                lines.append(f"{arrow_padding}{arrow}")

        return '\n'.join(lines)

    def create_branching_flow(
        self,
        root: str,
        branches: List[Tuple[str, List[str]]],
        width: int = 20
    ) -> str:
        """Create flow with branches (decision tree).

        Args:
            root: Root node label
            branches: List of (branch_label, [steps]) tuples
            width: Width of boxes

        Returns:
            Multi-line branching flow diagram
        """
        lines = []

        # Root box
        root_box = self.create_chunky_box(width, root)
        lines.append(root_box)

        # Branch split
        split_char = self.teletext['box_drawing']['heavy']['t_down']
        connector = self.teletext['box_drawing']['heavy']['horizontal']
        vertical = self.teletext['box_drawing']['heavy']['vertical']

        # Center padding for split
        pad = ' ' * (width // 2 - 1)
        lines.append(f"{pad}{vertical}")

        # Create branches side by side (up to 2)
        for i, (branch_label, branch_steps) in enumerate(branches[:2]):
            branch_box = self.create_box(width, 3, content=[branch_label], style='heavy')
            lines.append(branch_box)

        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════
    # Tree Diagrams
    # ═══════════════════════════════════════════════════════════════════

    def create_tree(
        self,
        root: str,
        children: List[str],
        width: int = 20,
        indent: int = 4
    ) -> str:
        """Create tree hierarchy diagram.

        Args:
            root: Root node label
            children: List of child node labels
            width: Width of nodes
            indent: Indentation for children

        Returns:
            Multi-line tree diagram
        """
        lines = []

        # Root node (chunky)
        root_box = self.create_chunky_box(width, root)
        for line in root_box.split('\n'):
            lines.append(line.center(width + indent * 2))

        # Connector
        vertical = self.teletext['box_drawing']['heavy']['vertical']
        lines.append(vertical.center(width + indent * 2))

        # Branch split
        branch = self.teletext['box_drawing']['heavy']['t_down']
        horizontal = self.teletext['box_drawing']['heavy']['horizontal']

        if len(children) > 1:
            # Multi-branch
            branch_line = ' ' * indent + horizontal * (len(children) * indent)
            lines.append(branch_line.center(width + indent * 2))

        # Child nodes
        for child in children:
            child_box = self.create_box(width, 3, content=[child], style='light')
            for line in child_box.split('\n'):
                lines.append(' ' * indent + line)

        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════
    # Grid/Table Diagrams
    # ═══════════════════════════════════════════════════════════════════

    def create_grid(
        self,
        headers: List[str],
        rows: List[List[str]],
        col_width: int = 15
    ) -> str:
        """Create grid/table diagram.

        Args:
            headers: List of column headers
            rows: List of row data (each row is list of cell values)
            col_width: Width of each column

        Returns:
            Multi-line grid diagram
        """
        lines = []

        # Borders
        heavy = self.borders['heavy']
        double = self.borders['double']

        # Header row (chunky style)
        header_top = "▐" + ("▀" * (col_width - 2)) + "▌"
        header_middle_parts = []
        header_bottom = "▐" + ("▄" * (col_width - 2)) + "▌"

        for header in headers:
            header_middle_parts.append(f"▐ {header.center(col_width - 4)} ▌")

        lines.append("".join([header_top] * len(headers)))
        lines.append("".join(header_middle_parts))
        lines.append("".join([header_bottom] * len(headers)))

        # Separator
        sep = double['horizontal'] * (col_width * len(headers))
        lines.append(sep)

        # Data rows
        for row in rows:
            row_parts = []
            for cell in row:
                row_parts.append(f"{heavy['vertical']} {cell.center(col_width - 4)} ")
            lines.append("".join(row_parts) + heavy['vertical'])

        return '\n'.join(lines)

    # ═══════════════════════════════════════════════════════════════════
    # Labels & Annotations
    # ═══════════════════════════════════════════════════════════════════

    def create_label(
        self,
        text: str,
        style: str = 'chunky',
        min_width: int = None
    ) -> str:
        """Create inline label/tag.

        Args:
            text: Label text
            style: chunky, badge, or plain
            min_width: Minimum width (auto if None)

        Returns:
            Single-line label
        """
        if style == 'chunky':
            left = self.teletext['chunky_labels']['button_left']
            right = self.teletext['chunky_labels']['button_right']
            fill = self.teletext['chunky_labels']['button_fill']

            width = min_width or len(text) + 4
            padding = (width - len(text) - 2) // 2

            return f"{left}{fill * padding} {text} {fill * padding}{right}"

        elif style == 'badge':
            return f"▐ {text} ▌"

        else:
            return f"[ {text} ]"

    def create_arrow_connector(
        self,
        length: int,
        direction: str = 'right',
        label: str = ""
    ) -> str:
        """Create arrow connector with optional label.

        Args:
            length: Length of connector
            direction: right, left, up, down
            label: Optional label on connector

        Returns:
            Arrow connector string
        """
        horizontal = self.teletext['box_drawing']['heavy']['horizontal']
        arrows = self.teletext['arrows']

        if direction == 'right':
            arrow_head = arrows['right']
            line = horizontal * (length - 1) + arrow_head
        elif direction == 'left':
            arrow_head = arrows['left']
            line = arrow_head + horizontal * (length - 1)
        elif direction == 'down':
            vertical = self.teletext['box_drawing']['heavy']['vertical']
            arrow_head = arrows['down']
            return '\n'.join([vertical] * (length - 1) + [arrow_head])
        elif direction == 'up':
            vertical = self.teletext['box_drawing']['heavy']['vertical']
            arrow_head = arrows['up']
            return '\n'.join([arrow_head] + [vertical] * (length - 1))
        else:
            line = horizontal * length

        # Add label if provided
        if label:
            mid = length // 2 - len(label) // 2
            line = line[:mid] + f" {label} " + line[mid + len(label) + 2:]

        return line


# ═══════════════════════════════════════════════════════════════════════
# Module-level convenience functions
# ═══════════════════════════════════════════════════════════════════════

_compositor = None

def get_compositor() -> GraphicsCompositor:
    """Get singleton compositor instance."""
    global _compositor
    if _compositor is None:
        _compositor = GraphicsCompositor()
    return _compositor


def create_flow(steps: List[str], **kwargs) -> str:
    """Create flow diagram (convenience function)."""
    return get_compositor().create_flow(steps, **kwargs)


def create_tree(root: str, children: List[str], **kwargs) -> str:
    """Create tree diagram (convenience function)."""
    return get_compositor().create_tree(root, children, **kwargs)


def create_grid(headers: List[str], rows: List[List[str]], **kwargs) -> str:
    """Create grid diagram (convenience function)."""
    return get_compositor().create_grid(headers, rows, **kwargs)


def create_box(width: int, height: int, **kwargs) -> str:
    """Create box (convenience function)."""
    return get_compositor().create_box(width, height, **kwargs)
