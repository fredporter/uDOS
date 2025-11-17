"""
DOCS Unified Command Handler - v1.0.23
Consolidates DOC, MANUAL, HANDBOOK, and EXAMPLE into one smart command

Smart Features:
- Interactive picker when no args
- Intelligent content detection
- Cross-source search
- Backwards compatible aliases

Commands:
  DOCS                    Interactive picker
  DOCS <query>            Smart search all sources
  DOCS --manual <cmd>     Direct manual access
  DOCS --handbook <vol>   Direct handbook access
  DOCS --example <name>   Direct example access
  DOCS --search <query>   Explicit search

Author: uDOS Development Team
Version: 1.0.23
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import sys

# Import the original handlers
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.commands.doc_handler import DocHandler
from core.commands.manual_handler import ManualHandler
from core.commands.handbook_handler import HandbookHandler
from core.commands.example_handler import ExampleHandler


class DocsUnifiedHandler:
    """Unified documentation access - consolidates 4 commands into one smart interface"""

    def __init__(self, viewport=None, logger=None):
        """Initialize with all sub-handlers"""
        self.viewport = viewport
        self.logger = logger

        # Initialize sub-handlers (backwards compatibility)
        self.doc_handler = DocHandler(viewport=viewport, logger=logger)
        self.manual_handler = ManualHandler(viewport=viewport, logger=logger)
        self.handbook_handler = HandbookHandler(viewport=viewport, logger=logger)
        self.example_handler = ExampleHandler(viewport=viewport, logger=logger)

        # Unified search index
        self._build_unified_index()

    def _build_unified_index(self) -> Dict[str, List[Dict]]:
        """Build unified search index across all sources"""
        self.unified_index = {
            'documentation': [],
            'manual': [],
            'handbook': [],
            'examples': []
        }

        # Index documentation
        for topic, path in self.doc_handler.doc_index.items():
            self.unified_index['documentation'].append({
                'name': topic,
                'path': path,
                'source': 'documentation',
                'priority': 3
            })

        # Index manual entries
        for cmd, data in self.manual_handler.manuals.items():
            self.unified_index['manual'].append({
                'name': cmd.lower(),
                'data': data,
                'source': 'manual',
                'priority': 5  # Highest priority - command reference
            })

        # Index handbook volumes
        for vol_name, vol_data in self.handbook_handler.volumes.items():
            for chapter in vol_data['chapters']:
                self.unified_index['handbook'].append({
                    'name': chapter['name'],
                    'title': chapter['title'],
                    'volume': vol_name,
                    'source': 'handbook',
                    'priority': 4
                })

        # Index examples
        for ex_name, ex_data in self.example_handler.examples.items():
            self.unified_index['examples'].append({
                'name': ex_name,
                'data': ex_data,
                'source': 'examples',
                'priority': 2
            })

        return self.unified_index

    def handle(self, command: str, args: List[str]) -> str:
        """Route DOCS commands intelligently"""

        # No command = interactive picker
        if not command:
            return self._show_picker()

        # Help
        if command == "HELP" or command == "--help":
            return self._show_help()

        # Direct access flags
        if command == "--manual":
            cmd = args[0] if args else ""
            return self.manual_handler.handle(cmd, args[1:])

        if command == "--handbook":
            vol = args[0] if args else ""
            return self.handbook_handler.handle(vol, args[1:])

        if command == "--example":
            name = args[0] if args else ""
            return self.example_handler.handle(name, args[1:])

        # Explicit search
        if command == "--search":
            query = " ".join(args) if args else ""
            return self._unified_search(query)

        # Smart search (default behavior)
        query = command + " " + " ".join(args) if args else command
        return self._smart_search(query.strip())

    def _show_picker(self) -> str:
        """Show interactive source picker"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  DOCS - What would you like to access?                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 📚 Browse Documentation    Browse wiki documentation       │
│  2. 📖 Command Manual           Quick command reference         │
│  3. 📕 Handbook                 Structured learning (4 volumes) │
│  4. 💡 Code Examples            Runnable code examples          │
│  5. 🔍 Search Everything        Search all documentation        │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Quick Access:                                                  │
│    DOCS <query>          Smart search across all sources       │
│    DOCS --manual <cmd>   Jump to command manual                │
│    DOCS --handbook VOL1  Open specific handbook volume         │
│    DOCS --example <name> View code example                     │
│                                                                 │
│  Statistics:                                                    │
│    Documentation:  {doc_count} topics                          │
│    Manual:         {manual_count} commands                     │
│    Handbook:       {handbook_count} chapters (4 volumes)       │
│    Examples:       {example_count} code samples                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [1-5] Select | [S] Search | [H] Help | [Q] Quit               │
└─────────────────────────────────────────────────────────────────┘

Enter choice (1-5) or search query: """.format(
            doc_count=len(self.doc_handler.doc_index),
            manual_count=len(self.manual_handler.manuals),
            handbook_count=sum(len(v['chapters']) for v in self.handbook_handler.volumes.values()),
            example_count=len(self.example_handler.examples)
        )

    def _show_help(self) -> str:
        """Show DOCS command help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  DOCS - Unified Documentation Access                           │
└─────────────────────────────────────────────────────────────────┘

🎯 Smart documentation access consolidating DOC, MANUAL, HANDBOOK, and EXAMPLE

USAGE:
  DOCS                       Interactive picker
  DOCS <query>               Smart search all sources
  DOCS --manual <command>    View command manual
  DOCS --handbook <volume>   Open handbook volume
  DOCS --example <name>      View code example
  DOCS --search <query>      Explicit search

SMART SEARCH:
  DOCS knows what you're looking for and prioritizes results:
  1. Command reference (MANUAL) - Highest priority
  2. Handbook chapters - High priority
  3. Documentation - Medium priority
  4. Examples - Lower priority (code-focused)

EXAMPLES:
  DOCS                           # Interactive picker
  DOCS getting started           # Smart search
  DOCS LOAD                      # Finds LOAD command manual
  DOCS --manual SAVE             # Direct manual access
  DOCS --handbook VOL1           # Open Volume 1
  DOCS --example hello           # View hello example
  DOCS --search "file operations" # Search everything

BACKWARDS COMPATIBILITY:
  DOC        → DOCS (documentation only)
  MANUAL     → DOCS --manual
  HANDBOOK   → DOCS --handbook
  EXAMPLE    → DOCS --example

All old commands still work with deprecation notices.

See also: LEARN (for guides/diagrams), HELP
"""

    def _smart_search(self, query: str) -> str:
        """Smart search with relevance ranking"""
        query_lower = query.lower()
        results = []

        # Search all sources
        for source_name, items in self.unified_index.items():
            for item in items:
                score = 0
                name = item.get('name', '').lower()

                # Exact match
                if name == query_lower:
                    score = 100 + item['priority']
                # Starts with query
                elif name.startswith(query_lower):
                    score = 50 + item['priority']
                # Contains query
                elif query_lower in name:
                    score = 25 + item['priority']
                # Word match
                elif any(word in name for word in query_lower.split()):
                    score = 10 + item['priority']

                if score > 0:
                    results.append({
                        'score': score,
                        'item': item,
                        'source': source_name
                    })

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)

        if not results:
            return f"\n❌ No results found for '{query}'\n\nTry: DOCS --search <query> for explicit search\n"

        # Top result: show directly if high confidence
        top_result = results[0]
        if top_result['score'] >= 100:
            return self._show_result(top_result)

        # Multiple results: show picker
        return self._show_search_results(query, results[:10])

    def _show_search_results(self, query: str, results: List[Dict]) -> str:
        """Show search results with source indicators"""
        output = [f"\n🔍 Results for '{query}' ({len(results)} found)", "═" * 60, ""]

        for i, result in enumerate(results, 1):
            item = result['item']
            source = result['source']

            # Source emoji
            source_emoji = {
                'manual': '📖',
                'handbook': '📕',
                'documentation': '📚',
                'examples': '💡'
            }

            emoji = source_emoji.get(source, '📄')
            name = item.get('name', 'Unknown')

            # Additional info based on source
            if source == 'manual':
                desc = item['data'].get('description', '')
                output.append(f"{i}. {emoji} {name.upper()}")
                output.append(f"   Command: {desc}")
            elif source == 'handbook':
                title = item.get('title', name)
                vol = item.get('volume', '')
                output.append(f"{i}. {emoji} {title}")
                output.append(f"   Handbook {vol}")
            elif source == 'examples':
                ex_type = item['data'].get('type', '')
                output.append(f"{i}. {emoji} {name}")
                output.append(f"   Example: {ex_type}")
            else:
                output.append(f"{i}. {emoji} {name.title()}")

            output.append("")

        output.append("─" * 60)
        output.append("View result: DOCS <name> or use number (DOCS --result <n>)")
        output.append("")

        return "\n".join(output)

    def _show_result(self, result: Dict) -> str:
        """Show specific result content"""
        source = result['source']
        item = result['item']

        if source == 'manual':
            cmd = item['name'].upper()
            return self.manual_handler._show_manual(cmd)
        elif source == 'handbook':
            chapter = item['name']
            return self.handbook_handler._show_chapter(chapter)
        elif source == 'documentation':
            topic = item['name']
            return self.doc_handler._show_topic(topic)
        elif source == 'examples':
            name = item['name']
            return self.example_handler._show_example(name)

        return f"\n❌ Unable to display result from {source}\n"

    def _unified_search(self, query: str) -> str:
        """Explicit unified search across all sources"""
        if not query:
            return "❌ Usage: DOCS --search <query>"

        return self._smart_search(query)


def create_handler(viewport=None, logger=None):
    """Factory function to create unified handler"""
    return DocsUnifiedHandler(viewport=viewport, logger=logger)
