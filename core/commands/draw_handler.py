"""
DRAW Command Handler - v1.1.4
Generate ASCII/Teletext diagrams from text descriptions

Creates flowcharts, trees, grids, and hierarchies using the uDOS graphics system.
Supports AI-assisted generation with fallback to simple text parsing.

Commands:
  DRAW FLOW <description>      - Create flowchart diagram
  DRAW TREE <description>      - Create tree diagram
  DRAW GRID <description>      - Create grid/table diagram
  DRAW HIERARCHY <description> - Create org chart/hierarchy
  DRAW <description>           - Auto-detect diagram type

Options:
  --file PATH                  - Read description from file
  --data JSON                  - Use structured JSON data
  --save PATH                  - Save diagram to file
  --format FMT                 - Output format (ascii/ansi/unicode)

Examples:
  DRAW FLOW "User login workflow"
  DRAW TREE "System architecture"
  DRAW GRID "Feature comparison table"
  DRAW "Process checkout: cart → payment → confirm"
  DRAW FLOW --file workflow.txt --save diagram.txt

Author: uDOS Development Team
Version: 1.1.4 (Graphics System)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.config import Config
from core.services.diagram_generator import DiagramGenerator, quick_diagram
from core.services.diagram_compositor import DiagramCompositor


class DrawHandler:
    """Handler for DRAW command - diagram generation"""

    def __init__(self, viewport=None, logger=None):
        """Initialize draw handler

        Args:
            viewport: Optional viewport for output
            logger: Optional logger instance
        """
        self.viewport = viewport
        self.logger = logger
        self.config = Config()
        self.generator = DiagramGenerator()
        self.compositor = DiagramCompositor()

    def handle(self, command: str, params: List[str]) -> Dict[str, Any]:
        """Handle DRAW command

        Args:
            command: The command name (DRAW)
            params: Command parameters

        Returns:
            Result dictionary with diagram output
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()

        # Help commands
        if subcommand in ['HELP', '--HELP', '-H', '?']:
            return self._show_help()

        # List diagram types
        if subcommand in ['LIST', 'TYPES']:
            return self._list_types()

        # Diagram type commands
        if subcommand in ['FLOW', 'TREE', 'GRID', 'HIERARCHY']:
            return self._create_diagram(subcommand.lower(), params[1:])

        # Auto-detect type from description
        return self._create_diagram('auto', params)

    def _show_help(self) -> Dict[str, Any]:
        """Show command help"""
        help_text = """╔═══════════════════════════════════════════════════════════════════════╗
║                    DRAW - Diagram Generation                         ║
╚═══════════════════════════════════════════════════════════════════════╝

USAGE:
  DRAW <type> <description>      Generate diagram from text
  DRAW <type> --file <path>      Read description from file
  DRAW <type> --data <json>      Use structured JSON data

DIAGRAM TYPES:
  FLOW        Flowchart (processes, decisions, workflows)
  TREE        Tree diagram (hierarchies, file systems)
  GRID        Table/grid (data, comparisons, lists)
  HIERARCHY   Org chart (organizations, team structures)

  (Auto)      Omit type to auto-detect from description

OPTIONS:
  --file PATH     Read description from file
  --data JSON     Provide structured data (file or JSON string)
  --save PATH     Save output to file
  --format FMT    Output format: ascii (default), ansi, unicode

EXAMPLES:
  DRAW FLOW "Check credentials, validate token, grant access"
  DRAW TREE "Root: System\\nUsers\\nData\\nConfig"
  DRAW GRID "Name,Age,City\\nAlice,30,NYC\\nBob,25,SF"
  DRAW "Process workflow for checkout"
  DRAW FLOW --file workflow.txt --save output.txt

DESCRIPTION FORMATS:

  FLOW (Flowchart):
    - List steps on separate lines
    - Use "?" or "if" for decisions
    - Use "start" and "end" keywords
    Example: "Start\\nGet input\\nValid?\\nProcess\\nEnd"

  TREE (Tree Diagram):
    - First line is root node
    - Remaining lines are children
    Example: "System\\nUsers\\nData\\nConfig"

  GRID (Table):
    - First line: column headers (comma/pipe separated)
    - Remaining lines: data rows
    Example: "Name,Status,Priority\\nTask 1,Done,High"

  HIERARCHY (Org Chart):
    - Use indentation to show levels
    - First line: top level (CEO, etc.)
    Example: "CEO\\n  CTO\\n    Eng Lead\\n  CFO"

MORE INFO:
  DRAW TYPES              - List all diagram types
  HELP WORKFLOWS          - Diagram workflow examples
  wiki/Command-Reference  - Full documentation

"""
        return {
            'success': True,
            'output': help_text,
            'type': 'help'
        }

    def _list_types(self) -> Dict[str, Any]:
        """List available diagram types"""
        types_info = """╔═══════════════════════════════════════════════════════════════════════╗
║                    Available Diagram Types                           ║
╚═══════════════════════════════════════════════════════════════════════╝

┌─ FLOW (Flowchart) ──────────────────────────────────────────────────┐
│ Process workflows, decision trees, step-by-step procedures          │
│                                                                       │
│ Components:                                                           │
│   • Process boxes (rectangles)                                       │
│   • Decision diamonds (conditions)                                   │
│   • Start/End markers (rounded)                                      │
│   • Arrows and connectors                                            │
│                                                                       │
│ Use for: Login flows, validation, multi-step processes              │
└───────────────────────────────────────────────────────────────────────┘

┌─ TREE (Tree Diagram) ───────────────────────────────────────────────┐
│ Hierarchical structures, file systems, taxonomies                    │
│                                                                       │
│ Components:                                                           │
│   • Root node (top level)                                            │
│   • Parent nodes (branches)                                          │
│   • Child nodes (leaves)                                             │
│   • Tree connectors (├─, └─)                                         │
│                                                                       │
│ Use for: Directory trees, classification, nested data                │
└───────────────────────────────────────────────────────────────────────┘

┌─ GRID (Table/Grid) ─────────────────────────────────────────────────┐
│ Tabular data, comparisons, structured lists                          │
│                                                                       │
│ Components:                                                           │
│   • Header row (bold borders)                                        │
│   • Data rows (content cells)                                        │
│   • Fixed column widths                                              │
│   • Grid borders                                                     │
│                                                                       │
│ Use for: Feature tables, schedules, data matrices                    │
└───────────────────────────────────────────────────────────────────────┘

┌─ HIERARCHY (Org Chart) ─────────────────────────────────────────────┐
│ Organization charts, team structures, reporting lines                │
│                                                                       │
│ Components:                                                           │
│   • Executive level (double border)                                  │
│   • Manager level (single border)                                    │
│   • Worker level (light border)                                      │
│   • Vertical connectors                                              │
│                                                                       │
│ Use for: Org charts, command structures, level systems               │
└───────────────────────────────────────────────────────────────────────┘

TIP: Use DRAW without a type to auto-detect from your description!

Examples:
  DRAW FLOW --help     - Flowchart-specific help
  DRAW TREE "example"  - Quick tree generation
  DRAW TYPES           - This list

"""
        return {
            'success': True,
            'output': types_info,
            'type': 'types'
        }

    def _create_diagram(self, diagram_type: str, args: List[str]) -> Dict[str, Any]:
        """Create diagram from arguments

        Args:
            diagram_type: Type of diagram (flow/tree/grid/hierarchy/auto)
            args: Remaining arguments

        Returns:
            Result dictionary
        """
        try:
            # Parse options
            options = self._parse_options(args)

            # Get description or data
            if options.get('file'):
                description = self._read_file(options['file'])
            elif options.get('data'):
                data = self._read_json(options['data'])
                return self._create_from_data(diagram_type, data, options)
            elif options.get('description'):
                description = options['description']
            else:
                return {
                    'success': False,
                    'error': 'No description provided. Use: DRAW HELP'
                }

            # Generate diagram
            if not description.strip():
                return {
                    'success': False,
                    'error': 'Empty description. Provide text to convert to diagram.'
                }

            # Use generator to create diagram
            if diagram_type == 'auto':
                diagram = self.generator.generate_from_description(description)
            else:
                diagram = self.generator.generate_from_description(
                    description,
                    diagram_type
                )

            # Save if requested
            if options.get('save'):
                self._save_diagram(diagram, options['save'])
                save_msg = f"\n\n✓ Saved to: {options['save']}"
            else:
                save_msg = ""

            # Log if logger available
            if self.logger:
                self.logger.info(f"Generated {diagram_type} diagram")

            return {
                'success': True,
                'output': diagram + save_msg,
                'type': diagram_type,
                'saved': options.get('save')
            }

        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'File not found: {e}'
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON data: {e}'
            }
        except Exception as e:
            error_msg = f'Failed to create diagram: {str(e)}'
            if self.logger:
                self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def _create_from_data(self, diagram_type: str, data: Dict,
                         options: Dict) -> Dict[str, Any]:
        """Create diagram from structured JSON data

        Args:
            diagram_type: Diagram type
            data: Structured diagram data
            options: Command options

        Returns:
            Result dictionary
        """
        try:
            # Use compositor directly for structured data
            if diagram_type == 'auto':
                # Try to infer type from data structure
                if 'nodes' in data or 'steps' in data:
                    diagram_type = 'flow'
                elif 'root' in data or 'children' in data:
                    diagram_type = 'tree'
                elif 'headers' in data or 'rows' in data:
                    diagram_type = 'grid'
                elif 'levels' in data or 'organization' in data:
                    diagram_type = 'hierarchy'
                else:
                    diagram_type = 'flow'  # Default

            self.compositor.create_from_template(diagram_type, data)

            output_format = options.get('format', 'ascii')
            diagram = self.compositor.export(output_format)

            if options.get('save'):
                self._save_diagram(diagram, options['save'])
                save_msg = f"\n\n✓ Saved to: {options['save']}"
            else:
                save_msg = ""

            if self.logger:
                self.logger.info(f"Generated {diagram_type} diagram from data")

            return {
                'success': True,
                'output': diagram + save_msg,
                'type': diagram_type,
                'format': output_format,
                'saved': options.get('save')
            }

        except Exception as e:
            error_msg = f'Failed to create diagram from data: {str(e)}'
            if self.logger:
                self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def _parse_options(self, args: List[str]) -> Dict[str, Any]:
        """Parse command options from arguments

        Args:
            args: Command arguments

        Returns:
            Options dictionary
        """
        options = {
            'description': None,
            'file': None,
            'data': None,
            'save': None,
            'format': 'ascii'
        }

        i = 0
        description_parts = []

        while i < len(args):
            arg = args[i]

            if arg.startswith('--'):
                option = arg[2:].lower()

                if option in ['file', 'data', 'save', 'format']:
                    if i + 1 < len(args):
                        options[option] = args[i + 1]
                        i += 2
                        continue

                i += 1
            else:
                description_parts.append(arg)
                i += 1

        if description_parts:
            options['description'] = ' '.join(description_parts)

        return options

    def _read_file(self, filepath: str) -> str:
        """Read description from file

        Args:
            filepath: Path to file

        Returns:
            File contents

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"{filepath}")

        return path.read_text(encoding='utf-8')

    def _read_json(self, data_input: str) -> Dict:
        """Read JSON data from file or string

        Args:
            data_input: JSON string or filepath

        Returns:
            Parsed JSON data

        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        # Try as file first
        path = Path(data_input)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Try as JSON string
        return json.loads(data_input)

    def _save_diagram(self, diagram: str, filepath: str) -> None:
        """Save diagram to file

        Args:
            diagram: Diagram text
            filepath: Output file path
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(diagram, encoding='utf-8')

        if self.logger:
            self.logger.info(f"Diagram saved to: {filepath}")


# Command info for registration (if using auto-discovery)
COMMAND_INFO = {
    'name': 'DRAW',
    'handler': DrawHandler,
    'description': 'Generate ASCII/teletext diagrams from text',
    'category': 'Graphics',
    'version': '1.1.4',
    'examples': [
        'DRAW FLOW "User login workflow"',
        'DRAW TREE "System architecture"',
        'DRAW GRID "Feature comparison"',
        'DRAW "Process checkout steps"'
    ]
}
