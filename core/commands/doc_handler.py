"""
DOC Command Handler - v1.0.22
Browse and search uDOS documentation

Commands:
  DOC
  DOC <topic>
  DOC SEARCH <query>
  DOC INDEX
  DOC LIST

Author: uDOS Development Team
Version: 1.0.22
"""

from pathlib import Path
from typing import List, Dict, Optional
import re


class DocHandler:
    """Handler for DOC commands - documentation browser"""

    def __init__(self, viewport=None, logger=None):
        """Initialize DocHandler"""
        self.viewport = viewport
        self.logger = logger
        self.wiki_path = Path("wiki")
        self.docs_path = Path("docs")

        # Documentation index
        self.doc_index = self._build_index()

    def handle(self, command: str, args: List[str]) -> str:
        """Route DOC commands to appropriate handlers"""

        if not command or command == "HELP":
            return self._show_help()

        if command == "INDEX":
            return self._show_index()

        if command == "LIST":
            return self._list_docs()

        if command == "SEARCH":
            if not args:
                return "❌ Usage: DOC SEARCH <query>"
            query = " ".join(args)
            return self._search_docs(query)

        # Default: show specific topic
        topic = command.lower()
        return self._show_topic(topic)

    def _build_index(self) -> Dict[str, Path]:
        """Build searchable index of all documentation"""
        index = {}

        # Index wiki pages
        if self.wiki_path.exists():
            for md_file in self.wiki_path.rglob("*.md"):
                if md_file.name not in ["_Footer.md", "_Sidebar.md", "README.md"]:
                    # Use filename without extension as key
                    key = md_file.stem.lower().replace("-", " ")
                    index[key] = md_file

        # Index docs
        if self.docs_path.exists():
            for md_file in self.docs_path.rglob("*.md"):
                if "archive" not in str(md_file):
                    key = md_file.stem.lower().replace("-", " ")
                    index[key] = md_file

        return index

    def _show_help(self) -> str:
        """Display DOC command help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  DOC - Documentation Browser                                    │
└─────────────────────────────────────────────────────────────────┘

📚 Browse and search uDOS documentation

USAGE:
  DOC                    Show documentation home
  DOC <topic>            Show specific topic
  DOC SEARCH <query>     Full-text search
  DOC INDEX              Show complete index
  DOC LIST               List all documents

EXAMPLES:
  DOC getting started    Show getting started guide
  DOC configuration      Show configuration docs
  DOC SEARCH "commands"  Search for "commands"
  DOC INDEX              Browse all topics

TOPICS:
  • getting started      Installation and first steps
  • command reference    All commands documented
  • configuration        Settings and customization
  • troubleshooting      Problem solving
  • architecture         System design
  • ucode language       Scripting guide
  • theme system         Themes and styling
  • extensions           Building extensions
  • knowledge            Knowledge bank system

See also: MANUAL, HANDBOOK, GUIDE
"""

    def _show_index(self) -> str:
        """Display complete documentation index"""
        output = ["", "📚 Documentation Index", "═" * 60, ""]

        # Group by category
        categories = {
            "Getting Started": [],
            "System": [],
            "Commands": [],
            "Development": [],
            "Knowledge": [],
            "Other": []
        }

        for topic, path in sorted(self.doc_index.items()):
            if any(x in topic for x in ["getting", "start", "quick"]):
                categories["Getting Started"].append((topic, path))
            elif any(x in topic for x in ["command", "reference"]):
                categories["Commands"].append((topic, path))
            elif any(x in topic for x in ["knowledge", "guide", "diagram"]):
                categories["Knowledge"].append((topic, path))
            elif any(x in topic for x in ["dev", "extension", "ucode", "architecture"]):
                categories["Development"].append((topic, path))
            elif any(x in topic for x in ["config", "theme", "viewport", "troubleshoot"]):
                categories["System"].append((topic, path))
            else:
                categories["Other"].append((topic, path))

        for category, docs in categories.items():
            if docs:
                output.append(f"▸ {category}")
                output.append("─" * 60)
                for topic, path in sorted(docs):
                    output.append(f"  • {topic.title()}")
                output.append("")

        output.append(f"Total: {len(self.doc_index)} documents")
        output.append("")
        output.append("Usage: DOC <topic> to view")

        return "\n".join(output)

    def _list_docs(self) -> str:
        """List all available documentation"""
        output = ["", "📄 Available Documentation", "═" * 60, ""]

        for topic in sorted(self.doc_index.keys()):
            output.append(f"  • {topic.title()}")

        output.append("")
        output.append(f"Total: {len(self.doc_index)} documents")
        output.append("")
        output.append("Usage: DOC <topic> to view")

        return "\n".join(output)

    def _search_docs(self, query: str) -> str:
        """Search documentation for query"""
        query_lower = query.lower()
        results = []

        # Search in indexed documents
        for topic, path in self.doc_index.items():
            try:
                content = path.read_text()
                content_lower = content.lower()

                # Check if query appears in title or content
                if query_lower in topic or query_lower in content_lower:
                    # Count occurrences
                    count = content_lower.count(query_lower)

                    # Extract context (first occurrence)
                    lines = content.split('\n')
                    context = ""
                    for i, line in enumerate(lines):
                        if query_lower in line.lower():
                            context = line.strip()[:80]
                            break

                    results.append({
                        'topic': topic,
                        'path': path,
                        'count': count,
                        'context': context
                    })
            except Exception:
                continue

        if not results:
            return f"\n❌ No results found for '{query}'\n"

        # Sort by relevance (count)
        results.sort(key=lambda x: x['count'], reverse=True)

        output = ["", f"🔍 Search Results for '{query}'", "═" * 60, ""]

        for i, result in enumerate(results[:10], 1):
            output.append(f"{i}. {result['topic'].title()} ({result['count']} matches)")
            if result['context']:
                output.append(f"   {result['context']}...")
            output.append("")

        if len(results) > 10:
            output.append(f"... and {len(results) - 10} more results")
            output.append("")

        output.append(f"✅ Found {len(results)} documents")
        output.append("")
        output.append("Usage: DOC <topic> to view")

        return "\n".join(output)

    def _show_topic(self, topic: str) -> str:
        """Display specific documentation topic"""

        # Try exact match first
        if topic in self.doc_index:
            return self._render_doc(self.doc_index[topic])

        # Try partial match
        matches = [k for k in self.doc_index.keys() if topic in k]

        if not matches:
            return f"\n❌ Topic '{topic}' not found\n\nUse 'DOC INDEX' to see all topics\n"

        if len(matches) == 1:
            return self._render_doc(self.doc_index[matches[0]])

        # Multiple matches - show list
        output = ["", f"📚 Multiple matches for '{topic}':", ""]
        for match in matches:
            output.append(f"  • {match.title()}")
        output.append("")
        output.append("Please be more specific")

        return "\n".join(output)

    def _render_doc(self, path: Path) -> str:
        """Render documentation file for display"""
        try:
            content = path.read_text()

            # Adapt to viewport tier if available
            if self.viewport and hasattr(self.viewport, 'tier'):
                tier = self.viewport.tier
                if tier < 5:
                    # Simplify for small screens
                    content = self._simplify_for_small_screen(content)

            return content

        except Exception as e:
            return f"\n❌ Error reading documentation: {e}\n"

    def _simplify_for_small_screen(self, content: str) -> str:
        """Simplify content for small viewport tiers"""
        lines = content.split('\n')
        simplified = []

        skip_table = False
        for line in lines:
            # Skip complex tables
            if '|' in line and line.count('|') > 3:
                if not skip_table:
                    simplified.append("[Table - use larger screen to view]")
                    skip_table = True
                continue
            else:
                skip_table = False

            # Keep headers and important content
            if line.strip().startswith('#') or not line.strip().startswith('│'):
                simplified.append(line)

        return '\n'.join(simplified)


def create_handler(viewport=None, logger=None):
    """Factory function to create handler"""
    return DocHandler(viewport=viewport, logger=logger)
