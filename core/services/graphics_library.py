"""
Graphics Library for ASCII/Teletext Diagrams

Provides tools for creating and rendering ASCII diagrams using box-drawing
characters, shapes, and connectors. Supports flowcharts, trees, grids, and
hierarchical diagrams.

Version: 1.0.0 (v1.1.4 Move 1)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum


class BoxStyle(Enum):
    """Box drawing styles"""
    SIMPLE = "simple"
    DOUBLE = "double"
    HEAVY = "heavy"
    ROUNDED = "rounded"
    BLOCK = "block"


class Alignment(Enum):
    """Text alignment options"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass
class Point:
    """2D point for diagram positioning"""
    x: int
    y: int


@dataclass
class Size:
    """Dimensions for diagram elements"""
    width: int
    height: int


class GraphicsLibrary:
    """Main graphics library for loading and managing diagram resources"""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize graphics library

        Args:
            data_dir: Path to graphics data directory (defaults to core/data/graphics)
        """
        if data_dir is None:
            # Default to core/data/graphics from project root
            # __file__ is in core/services/, so go up 2 levels to project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "core" / "data" / "graphics"

        self.data_dir = Path(data_dir)
        self.box_drawing = self._load_json("blocks/box_drawing.json")
        self.components = self._load_json("components.json")
        self.templates = self._load_templates()

    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from graphics directory"""
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Graphics file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_templates(self) -> Dict[str, Dict]:
        """Load all diagram templates"""
        templates = {}
        template_dir = self.data_dir / "templates"

        if not template_dir.exists():
            return templates

        for template_file in template_dir.glob("*.json"):
            with open(template_file, 'r', encoding='utf-8') as f:
                template = json.load(f)
                templates[template['type']] = template

        return templates

    def get_box_chars(self, style: str = "simple") -> Dict[str, str]:
        """Get box-drawing characters for a style

        Args:
            style: Box style (simple, double, heavy, rounded, block)

        Returns:
            Dictionary with corners, edges, junctions
        """
        if style not in self.components['boxes']:
            raise ValueError(f"Unknown box style: {style}")

        return self.components['boxes'][style]

    def get_template(self, diagram_type: str) -> Dict:
        """Get diagram template by type

        Args:
            diagram_type: Type of diagram (flow, tree, grid, hierarchy)

        Returns:
            Template configuration dictionary
        """
        if diagram_type not in self.templates:
            raise ValueError(f"Unknown diagram type: {diagram_type}")

        return self.templates[diagram_type]

    def get_color_code(self, color: str, foreground: bool = True) -> str:
        """Get ANSI color code

        Args:
            color: Color name (black, red, green, yellow, blue, magenta, cyan, white)
            foreground: True for foreground color, False for background

        Returns:
            ANSI escape code string
        """
        prefix = "fg_" if foreground else "bg_"
        key = f"{prefix}{color}"

        if key not in self.components['color_mapping']['ansi_codes']:
            raise ValueError(f"Unknown color: {color}")

        return self.components['color_mapping']['ansi_codes'][key]

    def get_arrow(self, direction: str) -> str:
        """Get arrow character for direction

        Args:
            direction: Direction (up, down, left, right)

        Returns:
            Arrow character
        """
        arrows = self.components['connectors']['arrows']

        if direction not in arrows:
            raise ValueError(f"Unknown direction: {direction}")

        return arrows[direction]


class Box:
    """Drawable box element"""

    def __init__(self, text: str, style: str = "simple",
                 width: Optional[int] = None, height: int = 3,
                 alignment: str = "center", color: Optional[str] = None):
        """Create a box element

        Args:
            text: Text content
            style: Box style (simple, double, heavy, rounded, block)
            width: Box width (auto-calculated if None)
            height: Box height
            alignment: Text alignment (left, center, right)
            color: Optional color name
        """
        self.text = text
        self.style = style
        self.width = width or (len(text) + 4)  # Auto-size with padding
        self.height = height
        self.alignment = alignment
        self.color = color
        self.position = Point(0, 0)

    def render(self, graphics: GraphicsLibrary) -> List[str]:
        """Render box to list of strings (one per line)

        Args:
            graphics: Graphics library instance

        Returns:
            List of rendered lines
        """
        chars = graphics.get_box_chars(self.style)
        lines = []

        # Top border
        top = chars['corners'][0] + chars['edges'][0] * (self.width - 2) + chars['corners'][1]
        lines.append(top)

        # Middle lines with text
        text_line_idx = self.height // 2  # Center vertically

        for i in range(1, self.height - 1):
            if i == text_line_idx:
                # Line with text
                content = self._format_text(self.text, self.width - 2, self.alignment)
                line = chars['edges'][1] + content + chars['edges'][1]
            else:
                # Empty line
                line = chars['edges'][1] + ' ' * (self.width - 2) + chars['edges'][1]

            lines.append(line)

        # Bottom border
        bottom = chars['corners'][2] + chars['edges'][0] * (self.width - 2) + chars['corners'][3]
        lines.append(bottom)

        # Apply color if specified
        if self.color:
            color_code = graphics.get_color_code(self.color)
            reset = graphics.components['color_mapping']['ansi_codes']['reset']
            lines = [color_code + line + reset for line in lines]

        return lines

    def _format_text(self, text: str, width: int, alignment: str) -> str:
        """Format text within specified width

        Args:
            text: Text to format
            width: Available width
            alignment: left, center, or right

        Returns:
            Formatted text string
        """
        if len(text) > width:
            # Truncate with ellipsis
            text = text[:width-3] + "..."

        if alignment == "center":
            padding = width - len(text)
            left_pad = padding // 2
            right_pad = padding - left_pad
            return ' ' * left_pad + text + ' ' * right_pad
        elif alignment == "right":
            return text.rjust(width)
        else:  # left
            return text.ljust(width)


class Connector:
    """Drawable connector line between boxes"""

    def __init__(self, start: Point, end: Point,
                 arrow: Optional[str] = None, style: str = "light"):
        """Create a connector

        Args:
            start: Starting point
            end: Ending point
            arrow: Optional arrow direction (up, down, left, right)
            style: Line style
        """
        self.start = start
        self.end = end
        self.arrow = arrow
        self.style = style

    def render(self, graphics: GraphicsLibrary) -> List[Tuple[Point, str]]:
        """Render connector as list of (position, character) tuples

        Args:
            graphics: Graphics library instance

        Returns:
            List of positioned characters
        """
        chars = []

        # Simple straight line rendering
        if self.start.x == self.end.x:
            # Vertical line
            char = '│'
            for y in range(min(self.start.y, self.end.y),
                          max(self.start.y, self.end.y) + 1):
                chars.append((Point(self.start.x, y), char))
        elif self.start.y == self.end.y:
            # Horizontal line
            char = '─'
            for x in range(min(self.start.x, self.end.x),
                          max(self.start.x, self.end.x) + 1):
                chars.append((Point(x, self.start.y), char))

        # Add arrow if specified
        if self.arrow and chars:
            arrow_char = graphics.get_arrow(self.arrow)
            chars[-1] = (chars[-1][0], arrow_char)

        return chars


def create_simple_box(text: str, width: int = 20) -> Box:
    """Create a simple box with default styling

    Args:
        text: Box text
        width: Box width

    Returns:
        Box instance
    """
    return Box(text, style="simple", width=width, height=3, alignment="center")


def create_flowchart_node(text: str, node_type: str = "process") -> Box:
    """Create a flowchart node

    Args:
        text: Node text
        node_type: Type (process, decision, start_end, data)

    Returns:
        Box instance with appropriate style
    """
    style_map = {
        "process": "simple",
        "decision": "simple",  # Would use diamond shape in full implementation
        "start_end": "rounded",
        "data": "simple"  # Would use parallelogram in full implementation
    }

    style = style_map.get(node_type, "simple")
    return Box(text, style=style, width=20, height=3, alignment="center")
