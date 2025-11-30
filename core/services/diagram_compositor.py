"""
Diagram Compositor for ASCII/Teletext Diagrams

Assembles diagrams from templates, handles layout, positioning, connectors,
and exports to ASCII/ANSI format.

Version: 1.0.0 (v1.1.4 Move 2)
"""

from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json

from core.services.graphics_library import (
    GraphicsLibrary, Box, Connector, Point, Size,
    create_simple_box, create_flowchart_node
)


@dataclass
class DiagramNode:
    """Represents a node in a diagram"""
    id: str
    text: str
    node_type: str = "default"
    position: Point = field(default_factory=lambda: Point(0, 0))
    size: Size = field(default_factory=lambda: Size(20, 3))
    style: str = "simple"
    color: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DiagramConnection:
    """Represents a connection between nodes"""
    from_id: str
    to_id: str
    label: Optional[str] = None
    style: str = "light"
    arrow: Optional[str] = "down"


class DiagramCompositor:
    """Composes and renders ASCII/teletext diagrams"""

    def __init__(self, graphics: Optional[GraphicsLibrary] = None):
        """Initialize compositor

        Args:
            graphics: Graphics library instance (creates new if None)
        """
        self.graphics = graphics or GraphicsLibrary()
        self.nodes: Dict[str, DiagramNode] = {}
        self.connections: List[DiagramConnection] = []
        self.canvas: List[List[str]] = []
        self.width = 80
        self.height = 40

    def create_from_template(self, template_type: str, data: Dict) -> 'DiagramCompositor':
        """Create diagram from template and data

        Args:
            template_type: Type of diagram (flow, tree, grid, hierarchy)
            data: Dictionary with nodes and connections

        Returns:
            Self for method chaining
        """
        template = self.graphics.get_template(template_type)

        if template_type == "flow":
            return self._create_flowchart(template, data)
        elif template_type == "tree":
            return self._create_tree(template, data)
        elif template_type == "grid":
            return self._create_grid(template, data)
        elif template_type == "hierarchy":
            return self._create_hierarchy(template, data)
        else:
            raise ValueError(f"Unknown template type: {template_type}")

    def _create_flowchart(self, template: Dict, data: Dict) -> 'DiagramCompositor':
        """Create flowchart diagram"""
        nodes = data.get('nodes', [])
        connections = data.get('connections', [])

        # Add nodes
        y_offset = 2
        for node in nodes:
            node_id = node['id']
            node_type = node.get('type', 'process')
            text = node['text']

            # Get component config from template
            component = template['components'].get(node_type, template['components']['process'])

            diagram_node = DiagramNode(
                id=node_id,
                text=text,
                node_type=node_type,
                position=Point(30, y_offset),
                size=Size(component['width'], component['height']),
                style=component['style']
            )

            self.add_node(diagram_node)
            y_offset += component['height'] + template['layout']['spacing']

        # Add connections
        for conn in connections:
            self.add_connection(DiagramConnection(
                from_id=conn['from'],
                to_id=conn['to'],
                label=conn.get('label'),
                arrow='down'
            ))

        return self

    def _create_tree(self, template: Dict, data: Dict) -> 'DiagramCompositor':
        """Create tree diagram"""
        root = data.get('root', {})
        children = data.get('children', [])

        # Add root node
        root_node = DiagramNode(
            id=root['id'],
            text=root['text'],
            node_type='root',
            position=Point(30, 2),
            size=Size(24, 3),
            style='double'
        )
        self.add_node(root_node)

        # Add child branches
        y_offset = 8
        x_start = 10
        for i, child in enumerate(children):
            child_node = DiagramNode(
                id=child['id'],
                text=child['text'],
                node_type='parent',
                position=Point(x_start + i * 25, y_offset),
                size=Size(20, 3),
                style='simple'
            )
            self.add_node(child_node)
            self.add_connection(DiagramConnection(
                from_id=root['id'],
                to_id=child['id'],
                arrow='down'
            ))

            # Add sub-children if any
            if 'children' in child:
                sub_y = y_offset + 6
                for j, sub_child in enumerate(child['children']):
                    sub_node = DiagramNode(
                        id=sub_child['id'],
                        text=sub_child['text'],
                        node_type='leaf',
                        position=Point(x_start + i * 25, sub_y + j * 5),
                        size=Size(16, 3),
                        style='simple'
                    )
                    self.add_node(sub_node)
                    self.add_connection(DiagramConnection(
                        from_id=child['id'],
                        to_id=sub_child['id'],
                        arrow='down'
                    ))

        return self

    def _create_grid(self, template: Dict, data: Dict) -> 'DiagramCompositor':
        """Create grid/table diagram"""
        headers = data.get('headers', [])
        rows = data.get('rows', [])

        cell_width = 15
        cell_height = 3
        x_start = 5
        y_start = 2

        # Add header row
        for i, header in enumerate(headers):
            node = DiagramNode(
                id=f"header_{i}",
                text=header,
                node_type='header',
                position=Point(x_start + i * cell_width, y_start),
                size=Size(cell_width, cell_height),
                style='heavy'
            )
            self.add_node(node)

        # Add data rows
        for row_idx, row in enumerate(rows):
            for col_idx, cell in enumerate(row):
                node = DiagramNode(
                    id=f"cell_{row_idx}_{col_idx}",
                    text=cell,
                    node_type='cell',
                    position=Point(x_start + col_idx * cell_width,
                                 y_start + (row_idx + 1) * cell_height),
                    size=Size(cell_width, cell_height),
                    style='simple'
                )
                self.add_node(node)

        return self

    def _create_hierarchy(self, template: Dict, data: Dict) -> 'DiagramCompositor':
        """Create hierarchy diagram"""
        levels = data.get('levels', [])

        for level_data in levels:
            level_num = level_data['level']
            nodes = level_data['nodes']

            y_pos = 2 + (level_num - 1) * 7
            num_nodes = len(nodes)
            total_width = num_nodes * 25
            x_start = (80 - total_width) // 2

            for i, node in enumerate(nodes):
                node_type = node.get('type', 'worker')
                diagram_node = DiagramNode(
                    id=node['id'],
                    text=node['text'],
                    node_type=node_type,
                    position=Point(x_start + i * 25, y_pos),
                    size=Size(20, 3),
                    style=template['components'][node_type]['style']
                )
                self.add_node(diagram_node)

                # Add connection to parent if specified
                if 'parent' in node:
                    self.add_connection(DiagramConnection(
                        from_id=node['parent'],
                        to_id=node['id'],
                        arrow='down'
                    ))

        return self

    def add_node(self, node: DiagramNode) -> None:
        """Add a node to the diagram"""
        self.nodes[node.id] = node

    def add_connection(self, connection: DiagramConnection) -> None:
        """Add a connection between nodes"""
        self.connections.append(connection)

    def layout(self) -> None:
        """Calculate layout positions for all nodes"""
        # For now, use positions from template creation
        # Future: implement auto-layout algorithms
        pass

    def render(self) -> str:
        """Render diagram to ASCII string

        Returns:
            ASCII diagram as string
        """
        # Initialize canvas
        self._init_canvas()

        # Draw connections first (so nodes appear on top)
        self._draw_connections()

        # Draw nodes
        self._draw_nodes()

        # Convert canvas to string
        return self._canvas_to_string()

    def _init_canvas(self) -> None:
        """Initialize blank canvas"""
        # Calculate required canvas size
        max_x = max_y = 0
        for node in self.nodes.values():
            max_x = max(max_x, node.position.x + node.size.width + 2)
            max_y = max(max_y, node.position.y + node.size.height + 2)

        self.width = max(80, max_x)
        self.height = max(40, max_y)

        # Create blank canvas
        self.canvas = [[' ' for _ in range(self.width)]
                      for _ in range(self.height)]

    def _draw_nodes(self) -> None:
        """Draw all nodes on canvas"""
        for node in self.nodes.values():
            box = Box(
                text=node.text,
                style=node.style,
                width=node.size.width,
                height=node.size.height,
                alignment="center",
                color=node.color
            )

            lines = box.render(self.graphics)
            self._draw_at_position(lines, node.position)

    def _draw_connections(self) -> None:
        """Draw all connections on canvas"""
        for conn in self.connections:
            if conn.from_id not in self.nodes or conn.to_id not in self.nodes:
                continue

            from_node = self.nodes[conn.from_id]
            to_node = self.nodes[conn.to_id]

            # Simple vertical connector for now
            start_x = from_node.position.x + from_node.size.width // 2
            start_y = from_node.position.y + from_node.size.height
            end_x = to_node.position.x + to_node.size.width // 2
            end_y = to_node.position.y

            # Draw vertical line
            if start_x == end_x:
                for y in range(start_y, end_y):
                    if 0 <= y < self.height and 0 <= start_x < self.width:
                        self.canvas[y][start_x] = '│'

                # Add arrow at end
                if conn.arrow and 0 <= end_y - 1 < self.height:
                    self.canvas[end_y - 1][start_x] = '↓'

    def _draw_at_position(self, lines: List[str], position: Point) -> None:
        """Draw text lines at position on canvas

        Args:
            lines: List of text lines to draw
            position: Top-left position to start drawing
        """
        for dy, line in enumerate(lines):
            y = position.y + dy
            if y >= self.height:
                break

            for dx, char in enumerate(line):
                x = position.x + dx
                if x >= self.width:
                    break

                if 0 <= y < self.height and 0 <= x < self.width:
                    # Only overwrite spaces (preserve connections)
                    if self.canvas[y][x] == ' ':
                        self.canvas[y][x] = char
                    # Always draw box-drawing characters
                    elif char in '─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬━┃┏┓┗┛┣┫┳┻╋╭╮╰╯':
                        self.canvas[y][x] = char

    def _canvas_to_string(self) -> str:
        """Convert canvas to string"""
        return '\n'.join(''.join(row).rstrip() for row in self.canvas)

    def export(self, format: str = "ascii") -> str:
        """Export diagram in specified format

        Args:
            format: Export format (ascii, ansi, unicode)

        Returns:
            Formatted diagram string
        """
        if format == "ascii":
            return self.render()
        elif format == "ansi":
            # TODO: Add ANSI color codes
            return self.render()
        elif format == "unicode":
            return self.render()
        else:
            raise ValueError(f"Unknown export format: {format}")

    def save(self, filepath: Path, format: str = "ascii") -> None:
        """Save diagram to file

        Args:
            filepath: Path to save file
            format: Export format
        """
        content = self.export(format)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


def create_flowchart(nodes: List[Dict], connections: List[Dict]) -> str:
    """Quick helper to create flowchart

    Args:
        nodes: List of node dictionaries
        connections: List of connection dictionaries

    Returns:
        ASCII flowchart string
    """
    compositor = DiagramCompositor()
    compositor.create_from_template('flow', {
        'nodes': nodes,
        'connections': connections
    })
    return compositor.render()


def create_tree(root: Dict, children: List[Dict]) -> str:
    """Quick helper to create tree diagram

    Args:
        root: Root node dictionary
        children: List of child node dictionaries

    Returns:
        ASCII tree diagram string
    """
    compositor = DiagramCompositor()
    compositor.create_from_template('tree', {
        'root': root,
        'children': children
    })
    return compositor.render()


def create_grid(headers: List[str], rows: List[List[str]]) -> str:
    """Quick helper to create grid/table

    Args:
        headers: List of header labels
        rows: List of row data (each row is list of cells)

    Returns:
        ASCII grid string
    """
    compositor = DiagramCompositor()
    compositor.create_from_template('grid', {
        'headers': headers,
        'rows': rows
    })
    return compositor.render()
