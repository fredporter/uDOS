"""
Diagram Generation Service

Generates diagrams using AI (Gemini) based on text descriptions.
Integrates graphics library and compositor with AI content generation.

Version: 1.0.0 (v1.1.4 Move 3)
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from core.services.diagram_compositor import (
    DiagramCompositor,
    create_flowchart,
    create_tree,
    create_grid
)


class DiagramGenerator:
    """Generates diagrams from text descriptions using AI"""

    def __init__(self, ai_service: Optional[Any] = None):
        """Initialize diagram generator

        Args:
            ai_service: AI service instance (optional, for AI-assisted generation)
        """
        self.ai_service = ai_service
        self.compositor = DiagramCompositor()

    def generate_from_description(self, description: str,
                                  diagram_type: str = "auto") -> str:
        """Generate diagram from natural language description

        Args:
            description: Text description of what to diagram
            diagram_type: Type of diagram (auto, flow, tree, grid, hierarchy)

        Returns:
            ASCII diagram as string
        """
        # Normalize and validate diagram type
        diagram_type = diagram_type.lower()

        if diagram_type == "auto":
            diagram_type = self._detect_diagram_type(description)

        # Validate type - default to flow if invalid
        valid_types = ['flow', 'tree', 'grid', 'hierarchy']
        if diagram_type not in valid_types:
            diagram_type = 'flow'  # Default to flowchart

        # Parse description into structured data
        data = self._parse_description(description, diagram_type)

        # Create diagram
        compositor = DiagramCompositor()
        compositor.create_from_template(diagram_type, data)

        return compositor.render()

    def _detect_diagram_type(self, description: str) -> str:
        """Detect appropriate diagram type from description

        Args:
            description: Text description

        Returns:
            Diagram type (flow, tree, grid, hierarchy)
        """
        desc_lower = description.lower()

        # Flow indicators
        if any(word in desc_lower for word in
               ['process', 'workflow', 'steps', 'decision', 'if', 'then']):
            return 'flow'

        # Tree indicators
        if any(word in desc_lower for word in
               ['tree', 'hierarchy', 'parent', 'child', 'branch']):
            return 'tree'

        # Grid/table indicators
        if any(word in desc_lower for word in
               ['table', 'grid', 'rows', 'columns', 'matrix']):
            return 'grid'

        # Hierarchy indicators
        if any(word in desc_lower for word in
               ['organization', 'org chart', 'levels', 'manager', 'team']):
            return 'hierarchy'

        # Default to flowchart
        return 'flow'

    def _parse_description(self, description: str,
                          diagram_type: str) -> Dict[str, Any]:
        """Parse text description into diagram data structure

        Args:
            description: Text description
            diagram_type: Type of diagram

        Returns:
            Data dictionary for diagram creation
        """
        if diagram_type == 'flow':
            return self._parse_flowchart(description)
        elif diagram_type == 'tree':
            return self._parse_tree(description)
        elif diagram_type == 'grid':
            return self._parse_grid(description)
        elif diagram_type == 'hierarchy':
            return self._parse_hierarchy(description)
        else:
            # Unknown type - default to flowchart (most flexible)
            return self._parse_flowchart(description)

    def _parse_flowchart(self, description: str) -> Dict[str, Any]:
        """Parse flowchart from description

        Simple parser that extracts steps and decisions.
        For production, would use AI service.
        """
        lines = [line.strip() for line in description.split('\n') if line.strip()]

        nodes = []
        connections = []

        # Add start node
        nodes.append({
            'id': 'start',
            'type': 'start_end',
            'text': 'Start'
        })

        prev_id = 'start'

        # Parse each line as a step
        for i, line in enumerate(lines):
            node_id = f'step{i+1}'

            # Detect node type
            if '?' in line or 'if' in line.lower():
                node_type = 'decision'
            else:
                node_type = 'process'

            nodes.append({
                'id': node_id,
                'type': node_type,
                'text': line[:30]  # Truncate long text
            })

            # Connect to previous
            connections.append({
                'from': prev_id,
                'to': node_id
            })

            prev_id = node_id

        # Add end node
        nodes.append({
            'id': 'end',
            'type': 'start_end',
            'text': 'End'
        })

        connections.append({
            'from': prev_id,
            'to': 'end'
        })

        return {'nodes': nodes, 'connections': connections}

    def _parse_tree(self, description: str) -> Dict[str, Any]:
        """Parse tree diagram from description"""
        lines = [line.strip() for line in description.split('\n') if line.strip()]

        if not lines:
            return {'root': {'id': 'root', 'text': 'Root'}, 'children': []}

        # First line is root
        root = {'id': 'root', 'text': lines[0][:30]}

        # Remaining lines are children
        children = []
        for i, line in enumerate(lines[1:], 1):
            children.append({
                'id': f'child{i}',
                'text': line[:30]
            })

        return {'root': root, 'children': children}

    def _parse_grid(self, description: str) -> Dict[str, Any]:
        """Parse grid/table from description"""
        lines = [line.strip() for line in description.split('\n') if line.strip()]

        if not lines:
            return {'headers': ['Col1', 'Col2'], 'rows': []}

        # First line is headers (split by comma, pipe, or tab)
        header_line = lines[0]
        headers = re.split(r'[,|\t]+', header_line)
        headers = [h.strip() for h in headers if h.strip()]

        # Remaining lines are rows
        rows = []
        for line in lines[1:]:
            cells = re.split(r'[,|\t]+', line)
            cells = [c.strip() for c in cells if c.strip()]
            if cells:
                rows.append(cells)

        return {'headers': headers, 'rows': rows}

    def _parse_hierarchy(self, description: str) -> Dict[str, Any]:
        """Parse hierarchy diagram from description"""
        lines = [line.strip() for line in description.split('\n') if line.strip()]

        levels = []
        current_level = 1

        for i, line in enumerate(lines):
            # Detect level by indentation or numbering
            indent = len(line) - len(line.lstrip())
            level = (indent // 2) + 1

            if level > current_level:
                current_level = level

            # Find or create level
            level_data = None
            for l in levels:
                if l['level'] == current_level:
                    level_data = l
                    break

            if level_data is None:
                level_data = {'level': current_level, 'nodes': []}
                levels.append(level_data)

            # Add node
            node_id = f'node{i+1}'
            node_type = 'executive' if current_level == 1 else \
                       'manager' if current_level == 2 else 'worker'

            level_data['nodes'].append({
                'id': node_id,
                'type': node_type,
                'text': line.lstrip()[:30]
            })

        return {'levels': levels}

    def generate_with_ai(self, prompt: str, diagram_type: str = "auto") -> str:
        """Generate diagram using AI service

        Args:
            prompt: Natural language description
            diagram_type: Type of diagram to generate

        Returns:
            ASCII diagram string
        """
        if self.ai_service is None:
            # Fallback to simple parsing
            return self.generate_from_description(prompt, diagram_type)

        # Use AI to generate structured data
        ai_prompt = self._build_ai_prompt(prompt, diagram_type)

        try:
            # Get AI response (would call actual AI service)
            ai_response = self._call_ai_service(ai_prompt)

            # Parse AI response to diagram data
            data = self._parse_ai_response(ai_response, diagram_type)

            # Generate diagram
            compositor = DiagramCompositor()
            compositor.create_from_template(diagram_type, data)

            return compositor.render()

        except Exception as e:
            # Fallback to simple parsing on AI error
            return self.generate_from_description(prompt, diagram_type)

    def _build_ai_prompt(self, user_prompt: str, diagram_type: str) -> str:
        """Build prompt for AI service"""

        if diagram_type == "flow":
            template = """
            Create a flowchart for: {prompt}

            Return JSON with this structure:
            {{
                "nodes": [
                    {{"id": "node1", "type": "start_end|process|decision", "text": "Node text"}},
                    ...
                ],
                "connections": [
                    {{"from": "node1", "to": "node2", "label": "optional"}},
                    ...
                ]
            }}
            """
        elif diagram_type == "tree":
            template = """
            Create a tree diagram for: {prompt}

            Return JSON with this structure:
            {{
                "root": {{"id": "root", "text": "Root node"}},
                "children": [
                    {{"id": "child1", "text": "Child text", "children": [...]}},
                    ...
                ]
            }}
            """
        elif diagram_type == "grid":
            template = """
            Create a table/grid for: {prompt}

            Return JSON with this structure:
            {{
                "headers": ["Col1", "Col2", ...],
                "rows": [
                    ["cell1", "cell2", ...],
                    ...
                ]
            }}
            """
        else:  # hierarchy
            template = """
            Create an org chart for: {prompt}

            Return JSON with this structure:
            {{
                "levels": [
                    {{
                        "level": 1,
                        "nodes": [
                            {{"id": "ceo", "type": "executive|manager|worker", "text": "Title"}}
                        ]
                    }},
                    ...
                ]
            }}
            """

        return template.format(prompt=user_prompt)

    def _call_ai_service(self, prompt: str) -> str:
        """Call AI service (placeholder for actual implementation)"""
        if self.ai_service and hasattr(self.ai_service, 'generate'):
            return self.ai_service.generate(prompt)

        # Return empty response if no AI service
        return "{}"

    def _parse_ai_response(self, response: str, diagram_type: str) -> Dict[str, Any]:
        """Parse AI JSON response to diagram data"""
        try:
            # Extract JSON from response (AI might wrap in markdown)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass

        # Return empty structure on parse error
        if diagram_type == 'flow':
            return {'nodes': [], 'connections': []}
        elif diagram_type == 'tree':
            return {'root': {'id': 'root', 'text': 'Root'}, 'children': []}
        elif diagram_type == 'grid':
            return {'headers': [], 'rows': []}
        else:  # hierarchy
            return {'levels': []}


def quick_diagram(description: str, diagram_type: str = "auto") -> str:
    """Quick helper to generate diagram from description

    Args:
        description: What to diagram
        diagram_type: Type (auto, flow, tree, grid, hierarchy)

    Returns:
        ASCII diagram
    """
    generator = DiagramGenerator()
    return generator.generate_from_description(description, diagram_type)


def flowchart(description: str) -> str:
    """Generate flowchart from description"""
    return quick_diagram(description, "flow")


def tree(description: str) -> str:
    """Generate tree diagram from description"""
    return quick_diagram(description, "tree")


def table(description: str) -> str:
    """Generate table/grid from description"""
    return quick_diagram(description, "grid")
