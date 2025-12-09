"""
uDOS v1.1.15 - MERMAID Command Handler

Mermaid diagram generation and management for text-to-diagram workflows.

Commands:
- MERMAID RENDER <type> <code|file>  # Generate diagram from Mermaid code
- MERMAID EXPORT <format>            # Export last diagram to SVG/PNG
- MERMAID LIST                       # List supported diagram types
- MERMAID VALIDATE <code>            # Syntax check Mermaid code
- MERMAID TEMPLATE <type>            # Show template for diagram type
- MERMAID EXAMPLES                   # Show example diagrams

Supported Mermaid Types (Typora/GitHub compatible):
- flowchart: Flowcharts and process diagrams
- sequence: Sequence diagrams (interactions)
- gantt: Gantt charts (project timelines)
- class: Class diagrams (UML)
- state: State diagrams (state machines)
- pie: Pie charts
- gitgraph: Git branching diagrams
- mindmap: Mind maps
- timeline: Timeline diagrams
- quadrant: Quadrant charts
- sankey: Sankey diagrams
- xychart: XY charts

Rendering Approach: Hybrid (Server-side mermaid-cli for offline, client-side for dashboard)

Output: memory/drafts/mermaid/

Author: uDOS Development Team
Version: 1.1.15
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import subprocess
import tempfile


class MermaidHandler:
    """Handle all MERMAID commands for diagram generation."""

    def __init__(self, viewport=None, logger=None):
        """
        Initialize MERMAID handler.

        Args:
            viewport: Viewport instance for output display
            logger: Logger instance for logging
        """
        self.viewport = viewport
        self.logger = logger
        
        # Get dashboard URL from config
        try:
            from core.config import Config
            config = Config()
            host = config.get('dashboard_host', 'localhost')
            port = config.get('dashboard_port', 5050)
            self.dashboard_url = f'http://{host}:{port}'
        except:
            self.dashboard_url = 'http://localhost:5050'

        # Output directories
        self.mermaid_output = Path("memory/drafts/mermaid")
        self.template_dir = Path("core/data/diagrams/mermaid")

        # Ensure directories exist
        self.mermaid_output.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        # Track last rendered diagram
        self.last_diagram = None
        self.last_diagram_path = None

        # Mermaid diagram types with descriptions
        self.diagram_types = {
            'flowchart': {
                'desc': 'Flowcharts and process diagrams',
                'keywords': ['TD', 'LR', 'BT', 'RL'],
                'use_cases': ['decision trees', 'workflows', 'processes']
            },
            'sequence': {
                'desc': 'Sequence diagrams for interactions',
                'keywords': ['participant', 'activate', 'deactivate'],
                'use_cases': ['communication flows', 'API interactions', 'protocols']
            },
            'gantt': {
                'desc': 'Gantt charts for project timelines',
                'keywords': ['dateFormat', 'section', 'task'],
                'use_cases': ['project planning', 'schedules', 'milestones']
            },
            'class': {
                'desc': 'Class diagrams (UML)',
                'keywords': ['class', 'relationship', 'inheritance'],
                'use_cases': ['data models', 'system structure', 'relationships']
            },
            'state': {
                'desc': 'State diagrams for state machines',
                'keywords': ['state', 'transition', '[*]'],
                'use_cases': ['workflows', 'status tracking', 'conditions']
            },
            'pie': {
                'desc': 'Pie charts for proportions',
                'keywords': ['title', 'data labels'],
                'use_cases': ['resource allocation', 'statistics', 'distributions']
            },
            'gitgraph': {
                'desc': 'Git branching diagrams',
                'keywords': ['commit', 'branch', 'merge'],
                'use_cases': ['version control', 'development flows', 'releases']
            },
            'mindmap': {
                'desc': 'Mind maps for brainstorming',
                'keywords': ['root', 'branches', 'nodes'],
                'use_cases': ['planning', 'brainstorming', 'knowledge maps']
            },
            'timeline': {
                'desc': 'Timeline diagrams',
                'keywords': ['title', 'period', 'events'],
                'use_cases': ['history', 'schedules', 'event sequences']
            },
            'quadrant': {
                'desc': 'Quadrant charts for prioritization',
                'keywords': ['x-axis', 'y-axis', 'quadrant'],
                'use_cases': ['priority matrix', 'risk assessment', 'decision making']
            },
            'sankey': {
                'desc': 'Sankey diagrams for flows',
                'keywords': ['source', 'target', 'value'],
                'use_cases': ['resource flows', 'energy diagrams', 'migration']
            },
            'xychart': {
                'desc': 'XY charts for data visualization',
                'keywords': ['x-axis', 'y-axis', 'line', 'bar'],
                'use_cases': ['trends', 'comparisons', 'analytics']
            }
        }

        # Check for mermaid-cli availability
        self._mmdc_available = self._check_mermaid_cli()

    def _check_mermaid_cli(self) -> bool:
        """
        Check if mermaid-cli (mmdc) is installed.

        Returns:
            bool: True if mmdc is available, False otherwise
        """
        try:
            result = subprocess.run(
                ['mmdc', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                if self.logger:
                    self.logger.log('EVENT', f"mermaid-cli available: {result.stdout.strip()}")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if self.logger:
            self.logger.log('WARNING', "mermaid-cli (mmdc) not found. Install: npm install -g @mermaid-js/mermaid-cli")
        return False

    def handle_command(self, params):
        """
        Handle MERMAID command routing.

        Args:
            params: Command parameters [subcommand, type, code/file, options...]

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()

        # Route to handlers
        handlers = {
            'RENDER': self._render,
            'EXPORT': self._export,
            'LIST': self._list_types,
            'TYPES': self._list_types,
            'VALIDATE': self._validate,
            'CHECK': self._validate,
            'TEMPLATE': self._show_template,
            'EXAMPLES': self._show_examples,
            'HELP': self._show_help,
        }

        handler = handlers.get(subcommand)
        if handler:
            return handler(params[1:])
        else:
            return self._show_help()

    def _show_help(self) -> str:
        """Display MERMAID command help."""
        return """
╔════════════════════════════════════════════════════════════════════════╗
║                    🌊 MERMAID DIAGRAM SYSTEM                          ║
╚════════════════════════════════════════════════════════════════════════╝

Text-to-diagram generation using Mermaid syntax (GitHub/Typora compatible)

COMMANDS:
  MERMAID RENDER <type> <code|file>  Generate diagram from Mermaid code
  MERMAID EXPORT <format>            Export last diagram (svg/png/pdf)
  MERMAID LIST                       List supported diagram types
  MERMAID VALIDATE <code|file>       Syntax check Mermaid code
  MERMAID TEMPLATE <type>            Show template for diagram type
  MERMAID EXAMPLES                   Show example diagrams

DIAGRAM TYPES:
  flowchart    Flowcharts and process diagrams
  sequence     Sequence diagrams (interactions)
  gantt        Gantt charts (project timelines)
  class        Class diagrams (UML)
  state        State diagrams (state machines)
  pie          Pie charts
  gitgraph     Git branching diagrams
  mindmap      Mind maps
  timeline     Timeline diagrams
  quadrant     Quadrant charts
  sankey       Sankey diagrams
  xychart      XY charts

EXAMPLES:
  MERMAID RENDER flowchart "graph TD; A-->B; B-->C;"
  MERMAID RENDER sequence water_purification.mmd
  MERMAID TEMPLATE flowchart
  MERMAID VALIDATE my_diagram.mmd
  MERMAID EXPORT svg

OUTPUT:
  Diagrams saved to: memory/drafts/mermaid/
  Templates stored in: core/data/diagrams/mermaid/

RENDERING:
  • Server-side: Uses mermaid-cli (mmdc) for offline rendering
  • Client-side: Dashboard preview (requires browser)
  • Status: """ + ("✅ mermaid-cli available" if self._mmdc_available else "⚠️  mermaid-cli not installed") + """

INSTALLATION:
  npm install -g @mermaid-js/mermaid-cli

For more info: https://mermaid.js.org/
"""

    def _render(self, params: List[str]) -> str:
        """
        Render Mermaid diagram from code or file.

        Args:
            params: [type, code/file, options...]

        Returns:
            Success/error message
        """
        if len(params) < 2:
            return "❌ Usage: MERMAID RENDER <type> <code|file>"

        diagram_type = params[0].lower()
        code_or_file = params[1]

        # Validate diagram type
        if diagram_type not in self.diagram_types:
            return f"❌ Unknown diagram type: {diagram_type}\n\nUse 'MERMAID LIST' to see available types."

        # Determine if input is file or inline code
        if Path(code_or_file).exists():
            # Load from file
            try:
                with open(code_or_file, 'r') as f:
                    mermaid_code = f.read()
            except Exception as e:
                return f"❌ Failed to read file: {e}"
        else:
            # Treat as inline code
            mermaid_code = code_or_file

        # Validate syntax (basic check)
        validation_result = self._validate_syntax(mermaid_code, diagram_type)
        if not validation_result['valid']:
            return f"❌ Syntax error: {validation_result['error']}"

        # Render diagram
        if self._mmdc_available:
            return self._render_with_cli(mermaid_code, diagram_type)
        else:
            return self._render_fallback(mermaid_code, diagram_type)

    def _render_with_cli(self, code: str, diagram_type: str) -> str:
        """
        Render diagram using mermaid-cli (mmdc).

        Args:
            code: Mermaid code
            diagram_type: Type of diagram

        Returns:
            Success message with output path
        """
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.mermaid_output / f"{diagram_type}_{timestamp}.svg"

        try:
            # Run mermaid-cli
            result = subprocess.run(
                ['mmdc', '-i', tmp_path, '-o', str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.last_diagram = code
                self.last_diagram_path = output_file

                if self.logger:
                    self.logger.log('EVENT', f"Rendered Mermaid diagram: {output_file}")

                return f"""
✅ Diagram rendered successfully!

Type: {diagram_type}
Output: {output_file}
Size: {output_file.stat().st_size} bytes

Use 'MERMAID EXPORT png' to convert to PNG.
"""
            else:
                return f"❌ Rendering failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            return "❌ Rendering timed out (30s limit exceeded)"
        except Exception as e:
            return f"❌ Rendering error: {e}"
        finally:
            # Cleanup temp file
            Path(tmp_path).unlink(missing_ok=True)

    def _render_fallback(self, code: str, diagram_type: str) -> str:
        """
        Fallback rendering when mermaid-cli not available.
        Saves code to .mmd file for manual rendering or dashboard preview.

        Args:
            code: Mermaid code
            diagram_type: Type of diagram

        Returns:
            Instructions for manual rendering
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        mmd_file = self.mermaid_output / f"{diagram_type}_{timestamp}.mmd"

        try:
            with open(mmd_file, 'w') as f:
                f.write(code)

            self.last_diagram = code
            self.last_diagram_path = mmd_file

            return f"""
⚠️  mermaid-cli not installed - saved Mermaid code for preview

Type: {diagram_type}
Saved: {mmd_file}

OPTIONS:
1. Install mermaid-cli: npm install -g @mermaid-js/mermaid-cli
   Then run: mmdc -i {mmd_file} -o {mmd_file.with_suffix('.svg')}

2. Preview in dashboard (if running):
   Visit: {self.dashboard_url}/mermaid/preview

3. Copy code to Typora or GitHub markdown:
   ```mermaid
{code}
   ```

4. Use online editor: https://mermaid.live/
"""
        except Exception as e:
            return f"❌ Failed to save diagram: {e}"

    def _export(self, params: List[str]) -> str:
        """
        Export last rendered diagram to different format.

        Args:
            params: [format] (svg/png/pdf)

        Returns:
            Success/error message
        """
        if not self.last_diagram_path:
            return "❌ No diagram to export. Render a diagram first."

        if not params:
            return "❌ Usage: MERMAID EXPORT <format> (svg/png/pdf)"

        output_format = params[0].lower()
        if output_format not in ['svg', 'png', 'pdf']:
            return "❌ Supported formats: svg, png, pdf"

        if not self._mmdc_available:
            return """
⚠️  mermaid-cli not installed

Install: npm install -g @mermaid-js/mermaid-cli
Then use: mmdc -i input.mmd -o output.{format}
"""

        # Export using mermaid-cli
        output_file = self.last_diagram_path.with_suffix(f'.{output_format}')

        try:
            result = subprocess.run(
                ['mmdc', '-i', str(self.last_diagram_path), '-o', str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return f"✅ Exported to: {output_file}"
            else:
                return f"❌ Export failed: {result.stderr}"

        except Exception as e:
            return f"❌ Export error: {e}"

    def _list_types(self, params: List[str]) -> str:
        """
        List all supported Mermaid diagram types.

        Returns:
            Formatted list of types with descriptions
        """
        output = ["", "🌊 MERMAID DIAGRAM TYPES", "=" * 60, ""]

        for i, (dtype, info) in enumerate(self.diagram_types.items(), 1):
            output.append(f"{i:2d}. {dtype.upper()}")
            output.append(f"    {info['desc']}")
            output.append(f"    Use cases: {', '.join(info['use_cases'])}")
            output.append("")

        output.append(f"Total: {len(self.diagram_types)} types supported")
        output.append("")
        output.append("Use 'MERMAID TEMPLATE <type>' to see example code.")

        return "\n".join(output)

    def _validate(self, params: List[str]) -> str:
        """
        Validate Mermaid syntax.

        Args:
            params: [code|file]

        Returns:
            Validation result
        """
        if not params:
            return "❌ Usage: MERMAID VALIDATE <code|file>"

        code_or_file = params[0]

        # Load code
        if Path(code_or_file).exists():
            try:
                with open(code_or_file, 'r') as f:
                    code = f.read()
            except Exception as e:
                return f"❌ Failed to read file: {e}"
        else:
            code = code_or_file

        # Detect diagram type
        diagram_type = self._detect_diagram_type(code)
        if not diagram_type:
            return "❌ Could not detect diagram type"

        # Validate
        result = self._validate_syntax(code, diagram_type)

        if result['valid']:
            return f"""
✅ Valid Mermaid code

Type: {diagram_type}
Lines: {len(code.splitlines())}

Ready to render: MERMAID RENDER {diagram_type} <code>
"""
        else:
            return f"❌ Syntax error: {result['error']}"

    def _validate_syntax(self, code: str, diagram_type: str) -> Dict[str, Any]:
        """
        Basic syntax validation for Mermaid code.

        Args:
            code: Mermaid code
            diagram_type: Expected diagram type

        Returns:
            {'valid': bool, 'error': str}
        """
        # Basic checks
        if not code.strip():
            return {'valid': False, 'error': 'Empty code'}

        # Check for diagram type declaration
        type_info = self.diagram_types.get(diagram_type)
        if not type_info:
            return {'valid': False, 'error': f'Unknown type: {diagram_type}'}

        # Check for type-specific keywords (basic heuristic)
        keywords = type_info['keywords']
        has_keyword = any(kw in code for kw in keywords)

        if not has_keyword:
            return {
                'valid': False,
                'error': f'Missing {diagram_type} keywords: {", ".join(keywords)}'
            }

        return {'valid': True, 'error': None}

    def _detect_diagram_type(self, code: str) -> Optional[str]:
        """
        Detect Mermaid diagram type from code.

        Args:
            code: Mermaid code

        Returns:
            Detected type or None
        """
        code_lower = code.lower()

        # Check for explicit type declarations
        if code_lower.startswith('graph') or code_lower.startswith('flowchart'):
            return 'flowchart'
        elif code_lower.startswith('sequencediagram'):
            return 'sequence'
        elif code_lower.startswith('gantt'):
            return 'gantt'
        elif code_lower.startswith('classDiagram'):
            return 'class'
        elif code_lower.startswith('stateDiagram'):
            return 'state'
        elif code_lower.startswith('pie'):
            return 'pie'
        elif code_lower.startswith('gitGraph'):
            return 'gitgraph'
        elif code_lower.startswith('mindmap'):
            return 'mindmap'
        elif code_lower.startswith('timeline'):
            return 'timeline'
        elif code_lower.startswith('quadrantChart'):
            return 'quadrant'
        elif code_lower.startswith('sankey-beta'):
            return 'sankey'
        elif code_lower.startswith('xychart-beta'):
            return 'xychart'

        return None

    def _show_template(self, params: List[str]) -> str:
        """
        Show template for diagram type.

        Args:
            params: [type]

        Returns:
            Template code
        """
        if not params:
            return "❌ Usage: MERMAID TEMPLATE <type>"

        diagram_type = params[0].lower()
        if diagram_type not in self.diagram_types:
            return f"❌ Unknown type: {diagram_type}\n\nUse 'MERMAID LIST' for available types."

        # Load or generate template
        template_file = self.template_dir / f"{diagram_type}_template.mmd"

        if template_file.exists():
            with open(template_file, 'r') as f:
                template = f.read()
        else:
            # Generate basic template
            template = self._generate_template(diagram_type)

        return f"""
📋 TEMPLATE: {diagram_type.upper()}

{template}

USAGE:
  1. Copy template above
  2. Modify for your needs
  3. Save to file: {diagram_type}_diagram.mmd
  4. Render: MERMAID RENDER {diagram_type} {diagram_type}_diagram.mmd
"""

    def _generate_template(self, diagram_type: str) -> str:
        """Generate basic template for diagram type."""
        templates = {
            'flowchart': """graph TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E""",

            'sequence': """sequenceDiagram
    participant User
    participant System
    User->>System: Request
    System->>System: Process
    System-->>User: Response""",

            'gantt': """gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
    Task 1: 2025-01-01, 7d
    Task 2: 2025-01-08, 5d
    section Phase 2
    Task 3: 2025-01-13, 10d""",
        }

        return templates.get(diagram_type, f"# {diagram_type} template\n# Add your diagram code here")

    def _show_examples(self, params: List[str]) -> str:
        """
        Show example diagrams.

        Returns:
            List of example diagrams
        """
        return """
🌊 MERMAID EXAMPLES

1. WATER PURIFICATION FLOWCHART:
   graph TD
     A[Found Water Source] --> B{Is water clear?}
     B -->|Yes| C[Boil 1 minute]
     B -->|No| D[Filter through cloth]
     D --> C
     C --> E{Altitude > 2000m?}
     E -->|Yes| F[Boil 3 minutes]
     E -->|No| G[Water ready]
     F --> G

2. FIRE TRIANGLE MINDMAP:
   mindmap
     root((Fire Triangle))
       Heat
         Friction
         Spark
         Sun lens
       Fuel
         Tinder
         Kindling
         Fuel wood
       Oxygen
         Air flow
         Ventilation

3. SHELTER PRIORITY SEQUENCE:
   sequenceDiagram
     participant S as Survivor
     participant E as Environment
     S->>E: Assess weather
     E-->>S: Temperature, wind, rain
     S->>S: Select shelter type
     S->>E: Find location
     E-->>S: Dry, elevated, protected
     S->>S: Build shelter
     S->>E: Test protection
     E-->>S: Feedback
     S->>S: Adjust if needed

Use 'MERMAID RENDER <type> <code>' to generate these diagrams.
"""


def handle_mermaid(params, viewport=None, logger=None):
    """
    Entry point for MERMAID command.

    Args:
        params: Command parameters
        viewport: Viewport instance
        logger: Logger instance

    Returns:
        Command result
    """
    handler = MermaidHandler(viewport=viewport, logger=logger)
    return handler.handle_command(params)
