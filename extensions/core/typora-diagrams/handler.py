"""
uDOS v1.1.15 - Typora Diagram Support Handler

Extended diagram syntax support for Typora markdown editor.

Supports:
- Mermaid: flowchart, sequence, gantt, class, state, pie, mindmap, gitgraph,
           timeline, quadrant, sankey, xychart
- js-sequence: Simple and hand-drawn sequence diagrams
- Flowchart.js: Traditional flowchart syntax
- C4/PlantUML: Component and architecture diagrams

Commands:
- TYPORA CREATE: Create new diagram file
- TYPORA CONVERT: Convert existing diagrams
- TYPORA EXPORT: Export to PDF/HTML/PNG/SVG
- TYPORA VALIDATE: Validate diagram syntax
- TYPORA LIST: List templates and examples
- TYPORA EXAMPLES: Show example diagrams

Author: uDOS Development Team
Version: 1.0.0
"""

from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import subprocess
import shutil


class TyporaHandler:
    """Handle Typora diagram integration."""

    def __init__(self, viewport=None, logger=None):
        """
        Initialize Typora handler.

        Args:
            viewport: Viewport instance for output
            logger: Logger instance
        """
        self.viewport = viewport
        self.logger = logger

        # Output directories
        self.output_base = Path("memory/drafts/typora")
        self.output_dirs = {
            'flowchart': self.output_base / 'flowcharts',
            'sequence': self.output_base / 'sequence',
            'gantt': self.output_base / 'gantt',
            'class': self.output_base / 'class',
            'state': self.output_base / 'state',
            'pie': self.output_base / 'pie',
            'mindmap': self.output_base / 'mindmap',
            'gitgraph': self.output_base / 'gitgraph',
            'timeline': self.output_base / 'timeline',
            'quadrant': self.output_base / 'quadrant',
            'sankey': self.output_base / 'sankey',
            'xychart': self.output_base / 'xychart',
            'exports': self.output_base / 'exports'
        }

        # Create directories
        for dir_path in self.output_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Templates directory
        self.templates_dir = Path(__file__).parent / 'templates'
        self.examples_dir = Path(__file__).parent / 'examples'

    def handle_command(self, params):
        """
        Handle TYPORA command routing.

        Args:
            params: Command parameters [subcommand, ...]

        Returns:
            Command result message
        """
        if not params:
            return self._show_help()

        subcommand = params[0].upper()

        if subcommand == "CREATE":
            return self._create_diagram(params[1:])
        elif subcommand == "CONVERT":
            return self._convert_diagram(params[1:])
        elif subcommand == "EXPORT":
            return self._export_diagram(params[1:])
        elif subcommand == "VALIDATE":
            return self._validate_diagram(params[1:])
        elif subcommand == "LIST":
            return self._list_diagrams(params[1:])
        elif subcommand == "EXAMPLES":
            return self._show_examples(params[1:])
        elif subcommand == "HELP":
            return self._show_help()
        else:
            return f"❌ Unknown subcommand: {subcommand}\nUse: TYPORA HELP"

    def _create_diagram(self, params):
        """
        Create new diagram file for Typora.

        Args:
            params: [type, title, --style, --save]

        Returns:
            Success message with file path
        """
        if not params:
            return self._create_help()

        diagram_type = params[0].lower()
        title_parts = []
        style = "default"
        filename = None

        # Parse parameters
        i = 1
        while i < len(params):
            if params[i] == "--style" and i + 1 < len(params):
                style = params[i + 1]
                i += 2
            elif params[i] == "--save" and i + 1 < len(params):
                filename = params[i + 1]
                i += 2
            else:
                title_parts.append(params[i])
                i += 1

        title = " ".join(title_parts) if title_parts else "Untitled Diagram"

        # Get template
        template = self._get_template(diagram_type, title, style)
        if template.startswith("❌"):
            return template

        # Generate filename if not provided
        if not filename:
            clean_title = "".join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in title.lower())
            clean_title = clean_title.replace(' ', '_')
            filename = f"{clean_title}.md"

        # Determine output directory
        output_dir = self.output_dirs.get(diagram_type, self.output_base)
        output_path = output_dir / filename

        # Write file
        output_path.write_text(template, encoding='utf-8')

        response = f"✅ Created Typora diagram: {output_path}\n\n"
        response += f"📝 Type: {diagram_type}\n"
        response += f"📄 Title: {title}\n"
        response += f"🎨 Style: {style}\n\n"
        response += "Next steps:\n"
        response += f"  1. Open in Typora: open -a Typora {output_path}\n"
        response += f"  2. Edit diagram content\n"
        response += f"  3. Export: TYPORA EXPORT {filename} --format pdf\n"

        return response

    def _get_template(self, diagram_type: str, title: str, style: str) -> str:
        """
        Get template for diagram type.

        Args:
            diagram_type: Type of diagram
            title: Diagram title
            style: Style variant

        Returns:
            Template markdown content
        """
        # Metadata header
        metadata = f"""---
title: {title}
author: uDOS
date: {datetime.now().strftime('%Y-%m-%d')}
tags: [diagram, {diagram_type}, survival]
---

# {title}

"""

        # Diagram templates
        templates = {
            'flowchart': """```mermaid
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```
""",
            'sequence': """```mermaid
sequenceDiagram
    participant User
    participant System
    participant Service

    User->>System: Request
    System->>Service: Process
    Service-->>System: Response
    System-->>User: Result
```
""",
            'gantt': """```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD

    section Phase 1
    Task 1 :a1, 2025-01-01, 7d
    Task 2 :a2, after a1, 5d

    section Phase 2
    Task 3 :b1, 2025-01-08, 10d
    Task 4 :b2, after b1, 7d
```
""",
            'class': """```mermaid
classDiagram
    class Item {
        +String name
        +int quantity
        +use()
    }

    class Storage {
        +List items
        +add(Item)
        +remove(Item)
    }

    Storage --> Item : contains
```
""",
            'state': """```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Active: Start
    Active --> Processing: Begin
    Processing --> Complete: Finish
    Processing --> Error: Fail
    Error --> Active: Retry
    Complete --> [*]
```
""",
            'pie': """```mermaid
pie title Resource Distribution
    "Water" : 40
    "Shelter" : 30
    "Fire" : 20
    "Food" : 10
```
""",
            'mindmap': """```mermaid
mindmap
  root((Central Topic))
    Branch 1
      Sub-topic 1a
      Sub-topic 1b
    Branch 2
      Sub-topic 2a
      Sub-topic 2b
    Branch 3
      Sub-topic 3a
```
""",
            'gitgraph': """```mermaid
gitGraph
    commit id: "Initial"
    branch feature
    checkout feature
    commit id: "Add feature"
    commit id: "Test feature"
    checkout main
    merge feature
    commit id: "Release"
```
""",
            'timeline': """```mermaid
timeline
    title Event Timeline
    section Morning
        06:00 : Wake up
        08:00 : Start work
    section Afternoon
        12:00 : Lunch
        14:00 : Continue
    section Evening
        18:00 : Finish
        20:00 : Rest
```
""",
            'quadrant': """```mermaid
quadrantChart
    title Priority Matrix
    x-axis Low Urgency --> High Urgency
    y-axis Low Importance --> High Importance

    quadrant-1 Do First
    quadrant-2 Schedule
    quadrant-3 Delegate
    quadrant-4 Eliminate

    Task A: [0.8, 0.9]
    Task B: [0.6, 0.7]
    Task C: [0.3, 0.5]
    Task D: [0.2, 0.3]
```
""",
            'sankey': """```mermaid
sankey-beta

Source A,Process 1,50
Source A,Process 2,30
Source B,Process 1,40
Process 1,Output X,60
Process 1,Output Y,30
Process 2,Output X,30
```
""",
            'xychart': """```mermaid
xychart-beta
    title "Performance Over Time"
    x-axis [Mon, Tue, Wed, Thu, Fri]
    y-axis "Value" 0 --> 100
    line [20, 35, 45, 60, 75]
    bar [15, 30, 40, 55, 70]
```
""",
            'js-sequence': """```sequence
Title: Process Flow

Actor->System: Request
System->Database: Query
Database-->System: Data
System-->Actor: Response
```
""",
            'flow': """```flow
st=>start: Start
op=>operation: Process
cond=>condition: Success?
e=>end: End

st->op->cond
cond(yes)->e
cond(no)->op
```
"""
        }

        template_content = templates.get(diagram_type)
        if not template_content:
            return f"❌ Unknown diagram type: {diagram_type}\n\nSupported types: {', '.join(templates.keys())}"

        return metadata + template_content

    def _validate_diagram(self, params):
        """Validate diagram syntax."""
        if not params:
            return "❌ No file specified\nUsage: TYPORA VALIDATE <file>"

        file_path = Path(params[0])
        if not file_path.exists():
            # Try in output directories
            for dir_path in self.output_dirs.values():
                test_path = dir_path / file_path.name
                if test_path.exists():
                    file_path = test_path
                    break

        if not file_path.exists():
            return f"❌ File not found: {file_path}"

        content = file_path.read_text(encoding='utf-8')

        # Basic validation
        issues = []
        warnings = []

        # Check for diagram blocks
        if '```mermaid' not in content and '```sequence' not in content and '```flow' not in content:
            issues.append("No diagram code blocks found")

        # Check for unclosed code blocks
        if content.count('```') % 2 != 0:
            issues.append("Unclosed code block (odd number of ```)")

        # Check for very long labels (might wrap)
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '-->' in line or '|' in line:
                # Extract labels
                if len(line) > 80:
                    warnings.append(f"Line {i}: Long label may wrap in diagram")

        # Build response
        if issues:
            response = "❌ Validation failed:\n"
            for issue in issues:
                response += f"  - {issue}\n"
        else:
            response = "✅ Diagram syntax valid\n"

        if warnings:
            response += "\n⚠️  Warnings:\n"
            for warning in warnings:
                response += f"  - {warning}\n"

        # Stats
        diagram_count = content.count('```mermaid') + content.count('```sequence') + content.count('```flow')
        response += f"\n📊 Diagrams found: {diagram_count}\n"
        response += f"📄 Lines: {len(lines)}\n"
        response += f"📝 File: {file_path}\n"

        return response

    def _list_diagrams(self, params):
        """List available diagrams."""
        response = "📋 Typora Diagrams\n"
        response += "=" * 60 + "\n\n"

        for diagram_type, dir_path in sorted(self.output_dirs.items()):
            if diagram_type == 'exports':
                continue

            files = list(dir_path.glob("*.md"))
            if files:
                response += f"**{diagram_type.upper()}** ({len(files)} files):\n"
                for file_path in sorted(files)[:5]:  # Show first 5
                    response += f"  - {file_path.name}\n"
                if len(files) > 5:
                    response += f"  ... and {len(files) - 5} more\n"
                response += "\n"

        return response

    def _show_examples(self, params):
        """Show example diagrams."""
        if params and params[0].lower() != 'all':
            diagram_type = params[0].lower()
            return self._get_template(diagram_type, f"Example {diagram_type}", "default")

        response = "📚 Typora Diagram Examples\n"
        response += "=" * 60 + "\n\n"
        response += "Available types:\n"
        response += "  - flowchart, sequence, gantt, class, state, pie\n"
        response += "  - mindmap, gitgraph, timeline, quadrant, sankey, xychart\n"
        response += "  - js-sequence, flow\n\n"
        response += "Usage: TYPORA EXAMPLES <type>\n"
        response += "Example: TYPORA EXAMPLES flowchart\n"

        return response

    def _create_help(self):
        """Show CREATE command help."""
        return """
TYPORA CREATE - Create New Diagram

SYNTAX:
  TYPORA CREATE <type> <title> [--style <style>] [--save <filename>]

TYPES:
  flowchart    - Flowchart diagram
  sequence     - Sequence diagram
  gantt        - Gantt chart
  class        - Class diagram
  state        - State diagram
  pie          - Pie chart
  mindmap      - Mind map
  gitgraph     - Git commit graph
  timeline     - Timeline chart
  quadrant     - Quadrant chart
  sankey       - Sankey diagram
  xychart      - XY chart
  js-sequence  - js-sequence diagram
  flow         - Flowchart.js diagram

EXAMPLES:
  TYPORA CREATE flowchart "Water System"
  TYPORA CREATE sequence "Mission Timeline"
  TYPORA CREATE gantt "Build Schedule" --save plan.md
"""

    def _show_help(self):
        """Show comprehensive help."""
        return """
┌──────────────────────────────────────────────────────────────────┐
│  TYPORA - Extended Diagram Support for Typora Editor            │
└──────────────────────────────────────────────────────────────────┘

COMMANDS:
  TYPORA CREATE <type> <title>     Create new diagram
  TYPORA CONVERT <file>             Convert existing diagram
  TYPORA EXPORT <file> --format     Export diagram
  TYPORA VALIDATE <file>            Validate syntax
  TYPORA LIST                       List diagrams
  TYPORA EXAMPLES [<type>]          Show examples

DIAGRAM TYPES:
  Mermaid (12 types):
    flowchart, sequence, gantt, class, state, pie
    mindmap, gitgraph, timeline, quadrant, sankey, xychart

  Other formats:
    js-sequence   - Simple sequence diagrams
    flow          - Flowchart.js diagrams

OUTPUT:
  memory/drafts/typora/
    ├── flowcharts/
    ├── sequence/
    ├── gantt/
    └── ... (organized by type)

EXAMPLES:
  TYPORA CREATE flowchart "Water Purification"
  TYPORA CREATE sequence "Emergency Response"
  TYPORA CREATE gantt "Mission Timeline"
  TYPORA VALIDATE water_system.md
  TYPORA LIST

INTEGRATION:
  - Open diagrams in Typora for visual editing
  - Export to PDF, HTML, PNG, SVG
  - Fully offline capable
  - Version control friendly (text-based)

See: extensions/cloned/typora-diagrams/README.md
"""

    def _convert_diagram(self, params):
        """Placeholder for conversion."""
        return "⚠️  TYPORA CONVERT not yet implemented\nUse: TYPORA CREATE to create new diagrams"

    def _export_diagram(self, params):
        """Placeholder for export."""
        return "⚠️  TYPORA EXPORT not yet implemented\nManually export from Typora: File → Export"


def get_handler(viewport=None, logger=None):
    """Get Typora handler instance."""
    return TyporaHandler(viewport=viewport, logger=logger)
