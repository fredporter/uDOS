"""
LEARN Unified Command Handler - v1.0.23
Consolidates GUIDE and DIAGRAM into one smart learning interface

Smart Features:
- Auto-detect content type (guide vs diagram)
- Unified progress tracking
- Smart recommendations
- Interactive picker

Commands:
  LEARN                   Interactive picker
  LEARN <name>            Smart content detection
  LEARN --guides          List all guides
  LEARN --diagrams        List all diagrams
  LEARN --continue        Resume last session

Author: uDOS Development Team
Version: 1.0.23
"""

from pathlib import Path
from typing import List, Dict, Optional
import sys

# Import the original handlers
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.commands.guide_handler import GuideHandler
from core.commands.diagram_handler import DiagramHandler


class LearnUnifiedHandler:
    """Unified learning interface - consolidates GUIDE and DIAGRAM"""

    def __init__(self, viewport=None, logger=None):
        """Initialize with guide and diagram handlers"""
        self.viewport = viewport
        self.logger = logger

        # Initialize sub-handlers
        self.guide_handler = GuideHandler(viewport=viewport, logger=logger)
        self.diagram_handler = DiagramHandler(viewport=viewport, logger=logger)

        # Build unified content index
        self._build_content_index()

    def _build_content_index(self) -> Dict:
        """Build unified index of all learning content"""
        self.content_index = {
            'guides': {},
            'diagrams': {}
        }

        # Index guides
        guides_path = Path("knowledge")
        if guides_path.exists():
            for guide_file in guides_path.rglob("*.md"):
                if "README" not in guide_file.name:
                    name = guide_file.stem.lower()
                    self.content_index['guides'][name] = {
                        'name': guide_file.stem,
                        'path': guide_file,
                        'type': 'guide'
                    }

        # Index diagrams
        diagrams_path = Path("wiki/diagrams")
        if diagrams_path.exists():
            for diagram_file in diagrams_path.rglob("README.md"):
                category = diagram_file.parent.name
                self.content_index['diagrams'][category] = {
                    'name': category,
                    'path': diagram_file,
                    'type': 'diagram'
                }

        return self.content_index

    def handle(self, command: str, args: List[str]) -> str:
        """Route LEARN commands intelligently"""

        # No command = interactive picker
        if not command:
            return self._show_picker()

        # Help
        if command == "HELP" or command == "--help":
            return self._show_help()

        # List commands
        if command == "--guides" or command == "--list-guides":
            return self.guide_handler.handle("LIST", [])

        if command == "--diagrams" or command == "--list-diagrams":
            return self.diagram_handler.handle("LIST", [])

        if command == "--list" or command == "LIST":
            return self._list_all()

        # Continue learning
        if command == "--continue" or command == "CONTINUE":
            return self._continue_learning()

        # Progress tracking
        if command == "--progress" or command == "PROGRESS":
            return self._show_progress()

        # Smart content detection
        query = command + " " + " ".join(args) if args else command
        return self._smart_content_access(query.strip())

    def _show_picker(self) -> str:
        """Show interactive learning content picker"""
        guides_count = len(self.content_index['guides'])
        diagrams_count = len(self.content_index['diagrams'])

        # Get progress from guide handler
        progress = self.guide_handler.progress
        completed = len(progress.get('completed', []))
        total_guides = guides_count
        percent = int((completed / total_guides) * 100) if total_guides > 0 else 0

        return f"""
┌─────────────────────────────────────────────────────────────────┐
│  LEARN - Choose learning content:                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 📖 Interactive Guides      {guides_count} step-by-step tutorials       │
│  2. 📊 ASCII Diagrams          {diagrams_count} visual references           │
│  3. 🎯 Skill Trees             Progression paths                │
│  4. 🚀 Project Tutorials       Complete projects                │
│  5. 🔍 Search All Content      Find anything                    │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Your Progress:                                                 │
│    Guides completed: {completed}/{total_guides} ({percent}%)                        │
│    Last session: {progress.get('current_guide', 'None')}                    │
│                                                                 │
│  Quick Actions:                                                 │
│    LEARN --continue         Resume last guide                   │
│    LEARN --progress         View detailed progress              │
│    LEARN <name>             Smart search (auto-detect type)     │
│                                                                 │
│  Popular Content:                                               │
│    • Water Purification     (Guide - Survival)                  │
│    • Knot Types             (Diagram - Skills)                  │
│    • System Architecture    (Diagram - Technical)               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [1-5] Select | [C] Continue | [P] Progress | [H] Help         │
└─────────────────────────────────────────────────────────────────┘

Enter choice: """

    def _show_help(self) -> str:
        """Show LEARN command help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  LEARN - Unified Learning Interface                            │
└─────────────────────────────────────────────────────────────────┘

🎓 Smart learning access consolidating GUIDE and DIAGRAM

USAGE:
  LEARN                     Interactive picker
  LEARN <name>              Smart content detection
  LEARN --guides            List all guides
  LEARN --diagrams          List all diagrams
  LEARN --continue          Resume last session
  LEARN --progress          View learning progress

SMART CONTENT DETECTION:
  LEARN automatically detects whether you want a guide or diagram:

  LEARN water      → Finds "water-purification" guide
  LEARN knots      → Finds "knot-types" diagram
  LEARN system     → Shows picker if multiple matches

EXAMPLES:
  LEARN                          # Interactive picker
  LEARN water-purification       # Start guide
  LEARN knot-types               # View diagram
  LEARN --continue               # Resume last guide
  LEARN --guides                 # List all guides
  LEARN --diagrams               # List all diagrams
  LEARN --progress               # View completion stats

PROGRESS TRACKING:
  • Automatic progress saving
  • Completion percentage
  • Resume where you left off
  • Achievement tracking

BACKWARDS COMPATIBILITY:
  GUIDE    → LEARN (guides only)
  DIAGRAM  → LEARN (diagrams only)

All old commands still work with deprecation notices.

See also: DOCS (for documentation), HANDBOOK (for structured reading)
"""

    def _smart_content_access(self, query: str) -> str:
        """Smart content detection and access"""
        query_lower = query.lower()

        # Search guides first (priority)
        guide_matches = [k for k in self.content_index['guides'].keys()
                        if query_lower in k]

        # Search diagrams
        diagram_matches = [k for k in self.content_index['diagrams'].keys()
                          if query_lower in k]

        # No matches
        if not guide_matches and not diagram_matches:
            return f"\n❌ No learning content found for '{query}'\n\nTry: LEARN --list to see all content\n"

        # Single guide match - show it
        if len(guide_matches) == 1 and not diagram_matches:
            guide_name = self.content_index['guides'][guide_matches[0]]['name']
            return self.guide_handler.handle("SHOW", [guide_name])

        # Single diagram match - show it
        if len(diagram_matches) == 1 and not guide_matches:
            diagram_name = diagram_matches[0]
            return self.diagram_handler.handle("SHOW", [diagram_name])

        # Multiple matches - show picker
        return self._show_matches(query, guide_matches, diagram_matches)

    def _show_matches(self, query: str, guide_matches: List, diagram_matches: List) -> str:
        """Show multiple matches with type indicators"""
        output = [f"\n📚 Learning content matching '{query}':", "═" * 60, ""]

        if guide_matches:
            output.append("📖 GUIDES:")
            for match in guide_matches:
                guide = self.content_index['guides'][match]
                output.append(f"  • {guide['name']}")
            output.append("")

        if diagram_matches:
            output.append("📊 DIAGRAMS:")
            for match in diagram_matches:
                diagram = self.content_index['diagrams'][match]
                output.append(f"  • {diagram['name']}")
            output.append("")

        output.append("─" * 60)
        output.append("Access: LEARN <name> (exact match needed)")
        output.append("")

        return "\n".join(output)

    def _list_all(self) -> str:
        """List all learning content"""
        output = ["\n📚 All Learning Content", "═" * 60, ""]

        output.append("📖 INTERACTIVE GUIDES:")
        for name, data in sorted(self.content_index['guides'].items()):
            output.append(f"  • {data['name']}")
        output.append("")

        output.append("📊 ASCII DIAGRAMS:")
        for name, data in sorted(self.content_index['diagrams'].items()):
            output.append(f"  • {data['name']}")
        output.append("")

        total = len(self.content_index['guides']) + len(self.content_index['diagrams'])
        output.append(f"Total: {total} learning resources")
        output.append("")
        output.append("Usage: LEARN <name> to access")
        output.append("")

        return "\n".join(output)

    def _continue_learning(self) -> str:
        """Continue last learning session"""
        progress = self.guide_handler.progress
        current = progress.get('current_guide')

        if not current:
            return "\n❌ No active learning session\n\nStart a guide: LEARN <name>\n"

        return self.guide_handler.handle("SHOW", [current])

    def _show_progress(self) -> str:
        """Show detailed learning progress"""
        progress = self.guide_handler.progress
        completed = progress.get('completed', [])
        total = len(self.content_index['guides'])
        percent = int((len(completed) / total) * 100) if total > 0 else 0

        output = ["\n📊 Learning Progress", "═" * 60, ""]

        # Overall stats
        output.append(f"Guides completed: {len(completed)}/{total} ({percent}%)")
        output.append("")

        # Progress bar
        bar_width = 40
        filled = int((len(completed) / total) * bar_width) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        output.append(f"[{bar}]")
        output.append("")

        # Current session
        if progress.get('current_guide'):
            output.append(f"Current: {progress['current_guide']}")
            current_step = progress.get('current_step', 0)
            output.append(f"Progress: Step {current_step}")
            output.append("")

        # Completed guides
        if completed:
            output.append("✅ Completed guides:")
            for guide in completed[:5]:  # Show first 5
                output.append(f"  • {guide}")
            if len(completed) > 5:
                output.append(f"  ... and {len(completed) - 5} more")
            output.append("")

        # Recommendations
        if len(completed) < total:
            output.append("💡 Recommended next:")
            # Simple logic: show first uncompleted
            for name, data in list(self.content_index['guides'].items())[:3]:
                if name not in completed:
                    output.append(f"  • {data['name']}")

        output.append("")
        output.append("Continue: LEARN --continue")
        output.append("")

        return "\n".join(output)


def create_handler(viewport=None, logger=None):
    """Factory function to create unified handler"""
    return LearnUnifiedHandler(viewport=viewport, logger=logger)
