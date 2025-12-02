"""
DIAGRAM Command Handler - v1.0.21
ASCII art library browser and renderer

Commands:
  DIAGRAM LIST [type]
  DIAGRAM SEARCH <query>
  DIAGRAM SHOW <name>
  DIAGRAM RENDER <name> [width]
  DIAGRAM COPY <name> <panel>
  DIAGRAM EXPORT <name> <file>
  DIAGRAM TYPES

Author: uDOS Development Team
Version: 1.0.21
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
import json
from core.services.gemini_generator import get_gemini_generator
from core.services.citation_manager import get_citation_manager


class DiagramHandler:
    """Handler for DIAGRAM commands - ASCII art library"""

    def __init__(self, viewport=None, logger=None):
        """Initialize DiagramHandler"""
        self.viewport = viewport
        self.logger = logger
        self.diagrams_path = Path("core/data/diagrams")
        self.diagrams_path.mkdir(parents=True, exist_ok=True)
        self.knowledge_path = Path("knowledge")

        # Diagram type categories
        self.diagram_types = {
            'knot': 'Knot diagrams and tying instructions',
            'shelter': 'Shelter construction blueprints',
            'chart': 'Charts, graphs, and comparison matrices',
            'map': 'Maps and navigation diagrams',
            'flow': 'Flowcharts and decision trees',
            'circuit': 'Circuit and wiring diagrams',
            'anatomy': 'Anatomical and medical diagrams',
            'plant': 'Plant identification and diagrams',
            'tool': 'Tool usage and maintenance diagrams',
            'symbol': 'Symbols and reference charts',
            'timeline': 'Timelines and progress indicators',
            'table': 'Tables and data structures',
            'ascii': 'General ASCII art and decorative',
        }

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route DIAGRAM commands to appropriate handlers

        Args:
            command: Subcommand (LIST, SEARCH, SHOW, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        handlers = {
            'LIST': self._list,
            'LS': self._list,
            'SEARCH': self._search,
            'FIND': self._search,
            'SHOW': self._show,
            'VIEW': self._show,
            'DISPLAY': self._show,
            'RENDER': self._render,
            'DRAW': self._render,
            'COPY': self._copy,
            'EXPORT': self._export,
            'SAVE': self._export,
            'TYPES': self._types,
            'CATEGORIES': self._types,
        }

        # Deprecation notice for removed GENERATE command
        if command in ['GENERATE', 'GEN']:
            return """❌ DIAGRAM GENERATE has been deprecated in v1.1.15

Use the improved GENERATE command instead:

  GENERATE SVG --survival <category>/<prompt> [--pro|--strict]
  GENERATE ASCII <type> <content>

Examples:
  GENERATE SVG --survival water/purification_flow --pro
  GENERATE ASCII box "Water Sources" 40 5
  GENERATE --survival-help  # Show all survival diagram options

See: GENERATE --help
"""

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown DIAGRAM command: {command}\n\nType 'DIAGRAM HELP' for usage."

    def _help(self) -> str:
        """Display DIAGRAM command help"""
        return """
📐 DIAGRAM - ASCII Art Library Browser & Content Generator

DIAGRAM SYSTEM:
  • Search and browse ASCII diagrams
  • Render in current viewport tier
  • Copy to grid for customization
  • Export to file or panel
  • Extract from knowledge base
  • ✨ GENERATE content with Gemini API (v1.6.0)

COMMANDS:
  DIAGRAM LIST [type]           List diagrams by type
  DIAGRAM SEARCH <query>         Search diagram library
  DIAGRAM SHOW <name>            Display diagram
  DIAGRAM RENDER <name> [width]  Render with custom width
  DIAGRAM COPY <name> <panel>    Copy to grid panel
  DIAGRAM EXPORT <name> <file>   Export to file
  DIAGRAM TYPES                  Show diagram categories
  DIAGRAM GENERATE <source> ...  Generate content + diagrams (v1.6.0)

GENERATE (v1.6.0):
  DIAGRAM GENERATE <source_file> [options]
    Generate Markdown guides and diagrams in multiple formats
    with mandatory citation tracking using Gemini API.

    Options:
      --crawl                  Use PEEK for web enrichment
      --style technical        SVG style (technical/kinetic/hybrid)
      --format md,svg,ascii,teletext  Output formats (comma-separated)
      --output <dir>           Output directory
      --citations-strict       Require 100% citation coverage
      --batch                  Process entire directory

    Formats:
      md        Markdown guide with citations
      svg       Technical-Kinetic vector diagrams
      ascii     C64 PETSCII terminal art (80x24)
      teletext  WST mosaic block graphics (40x25)

    Examples:
      DIAGRAM GENERATE guide.md --crawl
      DIAGRAM GENERATE guide.md --format md,svg,ascii
      DIAGRAM GENERATE knowledge/water/ --batch

WORKFLOW:
  1. DIAGRAM TYPES              # See categories
  2. DIAGRAM LIST knot          # Browse knots
  3. DIAGRAM SHOW bowline       # View diagram
  4. DIAGRAM RENDER bowline 60  # Custom width
  5. DIAGRAM EXPORT bowline knots.txt
  6. DIAGRAM GENERATE guide.md  # Generate new content

Type 'DIAGRAM GENERATE' for detailed generation help.
"""

    def _list(self, args: List[str]) -> str:
        """List diagrams by type"""
        diagram_type = args[0].lower() if args else None

        # Scan for diagrams
        diagrams = self._scan_diagrams(diagram_type)

        if not diagrams:
            if diagram_type:
                return f"❌ No diagrams found for type: {diagram_type}\n\nTry 'DIAGRAM TYPES' to see categories."
            else:
                return "❌ No diagrams found in library."

        # Group by type
        by_type = {}
        for diagram in diagrams:
            dtype = diagram['type']
            if dtype not in by_type:
                by_type[dtype] = []
            by_type[dtype].append(diagram)

        # Build output
        output = [""]
        output.append("📐 Diagram Library")
        output.append("═" * 60)

        for dtype, type_diagrams in sorted(by_type.items()):
            type_desc = self.diagram_types.get(dtype, "Unknown type")
            output.append(f"\n📊 {dtype.upper()} ({len(type_diagrams)} diagrams)")
            output.append(f"   {type_desc}")
            output.append("─" * 60)

            for diagram in type_diagrams:
                output.append(f"  • {diagram['name']}")
                output.append(f"    {diagram['description']}")
                output.append(f"    Size: {diagram['width']}×{diagram['height']} | Source: {diagram['source']}")
                output.append("")

        output.append("─" * 60)
        output.append(f"Total: {len(diagrams)} diagrams")
        output.append(f"💡 Tip: DIAGRAM SHOW <name> to view")
        output.append("")

        return "\n".join(output)

    def _search(self, args: List[str]) -> str:
        """Search diagram library"""
        if not args:
            return "❌ Usage: DIAGRAM SEARCH <query>"

        query = " ".join(args).lower()

        # Scan all diagrams
        diagrams = self._scan_diagrams()

        # Filter by query
        results = []
        for diagram in diagrams:
            # Search in name, description, and content
            if (query in diagram['name'].lower() or
                query in diagram['description'].lower() or
                query in diagram['content'].lower()):
                results.append(diagram)

        if not results:
            return f"❌ No diagrams found matching: {query}\n\nTry 'DIAGRAM LIST' to browse all diagrams."

        # Build output
        output = [""]
        output.append(f"🔍 Search Results: '{query}'")
        output.append("═" * 60)
        output.append(f"Found {len(results)} matching diagrams")
        output.append("")

        for diagram in results:
            output.append(f"📐 {diagram['name']} ({diagram['type']})")
            output.append(f"   {diagram['description']}")
            output.append(f"   Size: {diagram['width']}×{diagram['height']} | Source: {diagram['source']}")
            output.append("")

        output.append("─" * 60)
        output.append(f"💡 Tip: DIAGRAM SHOW <name> to view")
        output.append("")

        return "\n".join(output)

    def _show(self, args: List[str]) -> str:
        """Display diagram"""
        if not args:
            return "❌ Usage: DIAGRAM SHOW <name>"

        diagram_name = " ".join(args)
        diagram = self._find_diagram(diagram_name)

        if not diagram:
            return f"❌ Diagram not found: {diagram_name}\n\nTry 'DIAGRAM SEARCH {diagram_name}' to find similar."

        # Render diagram
        output = [""]
        output.append(f"📐 {diagram['name']}")
        output.append("═" * 60)
        output.append(f"Type: {diagram['type']} | Size: {diagram['width']}×{diagram['height']}")
        output.append(f"Description: {diagram['description']}")
        output.append(f"Source: {diagram['source']}")
        output.append("")
        output.append("─" * 60)
        output.append(diagram['content'])
        output.append("─" * 60)
        output.append("")
        output.append("💡 Commands:")
        output.append("   DIAGRAM RENDER <name> <width>  - Resize diagram")
        output.append("   DIAGRAM EXPORT <name> <file>   - Save to file")
        output.append("")

        return "\n".join(output)

    def _render(self, args: List[str]) -> str:
        """Render diagram with custom width"""
        if not args:
            return "❌ Usage: DIAGRAM RENDER <name> [width]"

        # Parse args
        diagram_name = args[0]
        width = int(args[1]) if len(args) > 1 else None

        # Find diagram
        diagram = self._find_diagram(diagram_name)
        if not diagram:
            return f"❌ Diagram not found: {diagram_name}"

        # Apply width scaling if specified
        content = diagram['content']
        if width and width != diagram['width']:
            content = self._scale_diagram(content, width)

        # Render
        output = [""]
        output.append(f"📐 {diagram['name']} ({diagram['type']})")
        if width:
            output.append(f"Scaled to width: {width}")
        output.append("─" * 60)
        output.append(content)
        output.append("─" * 60)
        output.append("")

        return "\n".join(output)

    def _copy(self, args: List[str]) -> str:
        """Copy diagram to grid panel"""
        if len(args) < 2:
            return "❌ Usage: DIAGRAM COPY <name> <panel>"

        diagram_name = args[0]
        panel_name = args[1]

        # Find diagram
        diagram = self._find_diagram(diagram_name)
        if not diagram:
            return f"❌ Diagram not found: {diagram_name}"

        # TODO: Implement grid panel integration
        return f"✓ Diagram '{diagram['name']}' copied to panel '{panel_name}'\n(Grid integration pending)"

    def _export(self, args: List[str]) -> str:
        """Export diagram to file"""
        if len(args) < 2:
            return "❌ Usage: DIAGRAM EXPORT <name> <file>"

        diagram_name = args[0]
        output_file = args[1]

        # Find diagram
        diagram = self._find_diagram(diagram_name)
        if not diagram:
            return f"❌ Diagram not found: {diagram_name}"

        # Write to file
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w') as f:
                f.write(f"# {diagram['name']}\n")
                f.write(f"Type: {diagram['type']}\n")
                f.write(f"Size: {diagram['width']}×{diagram['height']}\n")
                f.write(f"Description: {diagram['description']}\n")
                f.write(f"Source: {diagram['source']}\n")
                f.write("\n")
                f.write(diagram['content'])

            return f"✓ Diagram exported to: {output_file}\n"
        except Exception as e:
            return f"❌ Export failed: {e}\n"

    def _types(self, args: List[str]) -> str:
        """Show diagram type categories"""
        output = [""]
        output.append("📊 Diagram Type Categories")
        output.append("═" * 60)

        # Get counts per type
        diagrams = self._scan_diagrams()
        type_counts = {}
        for diagram in diagrams:
            dtype = diagram['type']
            type_counts[dtype] = type_counts.get(dtype, 0) + 1

        # Display categories
        for dtype, description in sorted(self.diagram_types.items()):
            count = type_counts.get(dtype, 0)
            bar = "█" * min(count, 20)
            output.append(f"  {dtype:12} {bar} ({count})")
            output.append(f"               {description}")
            output.append("")

        output.append("─" * 60)
        output.append(f"Total: {len(diagrams)} diagrams across {len(self.diagram_types)} types")
        output.append("")
        output.append("💡 Tip: DIAGRAM LIST <type> to browse category")
        output.append("")

        return "\n".join(output)

    def _scan_diagrams(self, diagram_type: Optional[str] = None) -> List[Dict]:
        """Scan for diagrams in library and knowledge base"""
        diagrams = []

        # Scan knowledge base for ASCII diagrams
        diagrams.extend(self._extract_from_knowledge(diagram_type))

        # Scan dedicated diagrams directory
        diagrams.extend(self._scan_diagram_files(diagram_type))

        return diagrams

    def _extract_from_knowledge(self, diagram_type: Optional[str] = None) -> List[Dict]:
        """Extract diagrams from knowledge base markdown files"""
        diagrams = []

        # Scan all markdown files in knowledge
        for md_file in self.knowledge_path.rglob("*.md"):
            if md_file.name.startswith('.'):
                continue

            try:
                content = md_file.read_text()

                # Find code blocks with ASCII art
                # Look for triple backtick blocks or indented blocks
                blocks = re.finditer(r'```(?:ascii)?\n(.+?)```', content, re.DOTALL)

                for i, match in enumerate(blocks, 1):
                    diagram_content = match.group(1)

                    # Analyze diagram
                    lines = diagram_content.split('\n')
                    height = len(lines)
                    width = max(len(line) for line in lines) if lines else 0

                    # Skip small diagrams (likely just code)
                    if height < 3 or width < 10:
                        continue

                    # Classify diagram type
                    dtype = self._classify_diagram(diagram_content, md_file)

                    if diagram_type and dtype != diagram_type:
                        continue

                    # Extract context (paragraph before diagram)
                    context = self._extract_context(content, match.start())

                    diagrams.append({
                        'name': f"{md_file.stem}-{i}",
                        'type': dtype,
                        'description': context or f"Diagram {i} from {md_file.name}",
                        'width': width,
                        'height': height,
                        'content': diagram_content,
                        'source': str(md_file.relative_to(Path.cwd())),
                    })
            except Exception as e:
                if self.logger and hasattr(self.logger, 'error'):
                    self.logger.error(f"Error extracting diagrams from {md_file}: {e}")
                # Silently skip errored files

        return diagrams

    def _scan_diagram_files(self, diagram_type: Optional[str] = None) -> List[Dict]:
        """Scan dedicated diagram files"""
        diagrams = []

        if not self.diagrams_path.exists():
            return diagrams

        # Scan .txt and .ascii files
        for diagram_file in self.diagrams_path.rglob("*.txt"):
            try:
                content = diagram_file.read_text()

                # Parse metadata from first lines (if formatted)
                metadata = self._parse_diagram_metadata(content)

                # Analyze diagram
                lines = content.split('\n')
                height = len(lines)
                width = max(len(line) for line in lines) if lines else 0

                dtype = metadata.get('type', 'ascii')
                if diagram_type and dtype != diagram_type:
                    continue

                diagrams.append({
                    'name': metadata.get('name', diagram_file.stem),
                    'type': dtype,
                    'description': metadata.get('description', ''),
                    'width': width,
                    'height': height,
                    'content': content,
                    'source': str(diagram_file.relative_to(Path.cwd())),
                })
            except Exception as e:
                if self.logger and hasattr(self.logger, 'error'):
                    self.logger.error(f"Error loading diagram {diagram_file}: {e}")
                # Silently skip errored files

        return diagrams

    def _classify_diagram(self, content: str, source_file: Path) -> str:
        """Classify diagram type based on content and source"""
        content_lower = content.lower()
        source_lower = str(source_file).lower()

        # Check source path first
        for dtype in self.diagram_types.keys():
            if dtype in source_lower:
                return dtype

        # Check content patterns
        if re.search(r'(═══|───|╔═╗|╠═╣|╚═╝)', content):
            if 'step' in content_lower or 'then' in content_lower:
                return 'flow'
            elif any(word in content_lower for word in ['vs', 'comparison', 'chart']):
                return 'chart'

        if re.search(r'(loop|knot|rope|line)', content_lower):
            return 'knot'

        if re.search(r'(shelter|roof|wall|structure)', content_lower):
            return 'shelter'

        if re.search(r'(map|grid|coordinate|location)', content_lower):
            return 'map'

        if re.search(r'(circuit|wire|power|voltage)', content_lower):
            return 'circuit'

        if re.search(r'(plant|leaf|root|flower)', content_lower):
            return 'plant'

        if re.search(r'(tool|hammer|knife|saw)', content_lower):
            return 'tool'

        if re.search(r'(timeline|progress|phase|step)', content_lower):
            return 'timeline'

        if re.search(r'(\|.*\|.*\|)', content):  # Table detection
            return 'table'

        return 'ascii'

    def _extract_context(self, content: str, diagram_pos: int) -> Optional[str]:
        """Extract description from text before diagram"""
        # Get text before diagram
        before = content[:diagram_pos]

        # Get last paragraph
        paragraphs = before.split('\n\n')
        if paragraphs:
            last_para = paragraphs[-1].strip()
            # Remove markdown formatting
            last_para = re.sub(r'[*_#`]', '', last_para)
            # Limit length
            if len(last_para) > 100:
                last_para = last_para[:97] + "..."
            return last_para

        return None

    def _parse_diagram_metadata(self, content: str) -> Dict:
        """Parse metadata from diagram file header"""
        metadata = {}

        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.startswith('#'):
                # Title line
                metadata['name'] = line.lstrip('# ').strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                metadata[key] = value

        return metadata

    def _find_diagram(self, diagram_name: str) -> Optional[Dict]:
        """Find diagram by name"""
        diagrams = self._scan_diagrams()

        # Try exact match
        for diagram in diagrams:
            if diagram['name'] == diagram_name:
                return diagram

        # Try fuzzy match
        diagram_lower = diagram_name.lower()
        for diagram in diagrams:
            if diagram_lower in diagram['name'].lower():
                return diagram

        return None

    def _scale_diagram(self, content: str, target_width: int) -> str:
        """Scale diagram to target width (simple character-based scaling)"""
        lines = content.split('\n')
        current_width = max(len(line) for line in lines) if lines else 0

        if current_width == 0 or target_width == current_width:
            return content

        # Simple scaling: truncate or pad
        scaled_lines = []
        for line in lines:
            if len(line) > target_width:
                scaled_lines.append(line[:target_width])
            else:
                scaled_lines.append(line.ljust(target_width))

        return '\n'.join(scaled_lines)
