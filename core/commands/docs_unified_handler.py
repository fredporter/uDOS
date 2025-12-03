"""
DOCS Unified Command Handler - v1.1.17
Consolidates GUIDE, DIAGRAM, and LEARN into single documentation system

Smart Features:
- Auto-detect content type (guide/diagram/reference)
- Unified progress tracking across all doc types
- Content quality assessment (REVIEW)
- AI-powered content regeneration (REGEN)
- Interactive picker with recommendations
- Backward compatibility with legacy commands

Commands:
  DOCS                        Interactive picker
  DOCS LIST [type] [category] List content by type/category
  DOCS SHOW <name>            Smart content display
  DOCS SEARCH <query>         Search all documentation
  DOCS START <name>           Begin interactive learning
  DOCS NEXT|PREV              Navigate steps
  DOCS COMPLETE [step]        Mark step complete
  DOCS PROGRESS               View learning progress
  DOCS REVIEW <name>          Assess content quality
  DOCS REGEN <name> [opts]    Regenerate with improvements
  DOCS HISTORY <name>         View content version history

Author: uDOS Development Team
Version: 1.1.17 (December 2025)
"""

from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
import json
import re
from datetime import datetime
from core.commands.base_handler import BaseCommandHandler
from core.utils.pager import page_output


class DocsUnifiedHandler(BaseCommandHandler):
    """Unified handler for all documentation access (GUIDE + DIAGRAM + LEARN)"""

    def __init__(self, viewport=None, logger=None, **kwargs):
        """Initialize unified docs handler"""
        # Initialize base handler (provides shared utilities)
        super().__init__(viewport=viewport, logger=logger, **kwargs)

        # Store viewport and logger explicitly for backward compatibility
        self.viewport = viewport
        self.logger = logger

        # Paths
        self.knowledge_path = Path("knowledge")
        self.diagrams_path = Path("core/data/diagrams")
        self.progress_file = Path("memory/modules/.docs_progress.json")
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        # Content types
        self.content_types = {
            'guide': 'Interactive step-by-step tutorials',
            'diagram': 'ASCII art and visual references',
            'reference': 'Quick reference cards and checklists',
            'manual': 'Comprehensive documentation',
        }

        # Diagram type categories (from legacy diagram_handler)
        self.diagram_types = {
            'knot': 'Knot diagrams and tying instructions',
            'shelter': 'Shelter construction blueprints',
            'chart': 'Charts, graphs, and comparison matrices',
            'map': 'Maps and navigation diagrams',
            'flow': 'Flowcharts and decision trees',
            'circuit': 'Circuit and wiring diagrams',
            'anatomy': 'Anatomical and medical diagrams',
            'plant': 'Plant identification diagrams',
            'tool': 'Tool usage and maintenance diagrams',
            'symbol': 'Symbols and reference charts',
            'timeline': 'Timelines and progress indicators',
            'table': 'Tables and data structures',
            'ascii': 'General ASCII art and decorative',
        }

        # Current session state
        self.current_content = None
        self.current_step = 0
        self.content_steps = []
        self.completed_steps: Set[int] = set()

        # Load saved progress
        self._load_progress()

        # Build content index
        self._build_content_index()

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route DOCS commands to appropriate handlers

        Args:
            command: Subcommand (LIST, SHOW, SEARCH, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        # Command routing
        handlers = {
            # Listing and discovery
            'LIST': self._list,
            'LS': self._list,
            'SEARCH': self._search,
            'FIND': self._search,
            'TYPES': self._types,
            'CATEGORIES': self._types,

            # Content display
            'SHOW': self._show,
            'VIEW': self._show,
            'DISPLAY': self._show,

            # Interactive learning
            'START': self._start,
            'BEGIN': self._start,
            'NEXT': self._next,
            'PREV': self._prev,
            'PREVIOUS': self._prev,
            'BACK': self._prev,
            'JUMP': self._jump,
            'GOTO': self._jump,

            # Progress tracking
            'COMPLETE': self._complete,
            'DONE': self._complete,
            'CHECK': self._complete,
            'RESET': self._reset,
            'RESTART': self._reset,
            'PROGRESS': self._progress,
            'STATUS': self._progress,

            # Session management
            'CONTINUE': self._continue,
            'RESUME': self._continue,

            # v1.1.17: Content quality (NEW)
            'REVIEW': self._review,
            'ASSESS': self._review,
            'REGEN': self._regen,
            'REGENERATE': self._regen,
            'HISTORY': self._history,
            'VERSIONS': self._history,
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            # Try smart content access
            query = command + " " + " ".join(args) if args else command
            return self._smart_content_access(query.strip())

    def _help(self) -> str:
        """Display DOCS command help"""
        return """
📚 DOCS - Unified Documentation System (v1.1.17)

Consolidates GUIDE, DIAGRAM, and LEARN into one smart interface.

CONTENT ACCESS:
  DOCS                        Interactive picker with recommendations
  DOCS LIST [type] [cat]      List content (guide/diagram/reference/manual)
  DOCS SHOW <name>            Smart display (auto-detects type)
  DOCS SEARCH <query>         Search all documentation
  DOCS TYPES                  Show content categories

INTERACTIVE LEARNING:
  DOCS START <name>           Begin step-by-step tutorial
  DOCS NEXT | PREV            Navigate steps
  DOCS JUMP <step>            Jump to specific step
  DOCS COMPLETE [step]        Mark step as complete
  DOCS PROGRESS               View learning progress
  DOCS CONTINUE               Resume last session

CONTENT QUALITY (v1.1.17 NEW):
  DOCS REVIEW <name>          Assess content quality & completeness
  DOCS REGEN <name> [opts]    Regenerate with AI improvements
  DOCS HISTORY <name>         View content version history

SMART FEATURES:
  • Auto-detect content type (guide vs diagram vs reference)
  • Unified progress tracking across all content
  • Resume from last position
  • Content quality scoring
  • AI-powered regeneration with citations
  • Version history and rollback

EXAMPLES:
  DOCS                                # Interactive picker
  DOCS LIST guide survival            # Survival guides
  DOCS LIST diagram knot              # Knot diagrams
  DOCS SHOW water-purification        # View guide
  DOCS START bushfire-survival        # Begin tutorial
  DOCS NEXT                           # Next step
  DOCS COMPLETE                       # Mark step done
  DOCS REVIEW water-purification      # Check quality
  DOCS REGEN water-purification --pro # Improve with AI

BACKWARD COMPATIBILITY:
  GUIDE <cmd>   → DOCS <cmd>  (guides only)
  DIAGRAM <cmd> → DOCS <cmd>  (diagrams only)
  LEARN <name>  → DOCS <name> (smart detection)

All legacy commands still work with deprecation notices.
"""

    def _list(self, args: List[str]) -> str:
        """List content by type and category"""
        content_type = args[0].lower() if args else None
        category = args[1].lower() if len(args) > 1 else None

        # Filter content
        content = []
        for item in self.content_index:
            if content_type and item['content_type'] != content_type:
                continue
            if category and item['category'] != category:
                continue
            content.append(item)

        if not content:
            msg = f"type '{content_type}'" if content_type else "all content"
            if category:
                msg += f" in category '{category}'"
            return f"❌ No content found for {msg}\n\nTry 'DOCS TYPES' to see categories."

        # Group by type and category
        by_type_cat = {}
        for item in content:
            key = (item['content_type'], item['category'])
            if key not in by_type_cat:
                by_type_cat[key] = []
            by_type_cat[key].append(item)

        # Build output
        output = ["", "📚 Documentation Library", "═" * 60]

        for (ctype, cat), items in sorted(by_type_cat.items()):
            type_icon = self._get_type_icon(ctype)
            output.append(f"\n{type_icon} {ctype.upper()} / {cat.upper()} ({len(items)} items)")
            output.append("─" * 60)

            for item in items:
                # Progress indicator
                progress = self._get_content_progress(item['id'])
                if progress['total'] > 0:
                    pct = int(progress['completed'] / progress['total'] * 100)
                    bar = self._progress_bar(pct, 10)
                    prog_text = f"{bar} {progress['completed']}/{progress['total']}"
                else:
                    prog_text = "No steps tracked"

                output.append(f"  • {item['title']}")
                output.append(f"    {item['description']}")
                if progress['total'] > 0:
                    output.append(f"    Progress: {prog_text}")
                output.append("")

        output.append("─" * 60)
        output.append(f"Total: {len(content)} items")
        output.append(f"💡 Tip: DOCS SHOW <name> to view")
        output.append("")

        result = "\n".join(output)

        # Use pager for long output
        if len(output) > 20:
            page_output(result, title="Documentation Library")
            return ""  # Already displayed via pager

        return result

    def _search(self, args: List[str]) -> str:
        """Search all documentation"""
        if not args:
            return "❌ Usage: DOCS SEARCH <query>"

        query = " ".join(args).lower()

        # Search content index
        results = []
        for item in self.content_index:
            # Search in name, title, description, content
            if (query in item['id'].lower() or
                query in item['title'].lower() or
                query in item['description'].lower() or
                query in item.get('tags', '').lower()):
                results.append(item)

        if not results:
            return f"❌ No content found matching: {query}\n\nTry 'DOCS LIST' to browse all content."

        # Build output
        output = ["", f"🔍 Search Results: '{query}'", "═" * 60]
        output.append(f"Found {len(results)} matching items\n")

        # Group by type
        by_type = {}
        for item in results:
            ctype = item['content_type']
            if ctype not in by_type:
                by_type[ctype] = []
            by_type[ctype].append(item)

        for ctype, items in sorted(by_type.items()):
            icon = self._get_type_icon(ctype)
            output.append(f"{icon} {ctype.upper()} ({len(items)}):")
            for item in items:
                output.append(f"  • {item['title']} ({item['category']})")
                output.append(f"    {item['description']}")
            output.append("")

        output.append("─" * 60)
        output.append(f"💡 Tip: DOCS SHOW <name> to view")
        output.append("")

        result = "\n".join(output)

        # Use pager for long output
        if len(output) > 20:
            page_output(result, title=f"Search: {query}")
            return ""  # Already displayed via pager

        return result

    def _show(self, args: List[str]) -> str:
        """Display content with smart type detection"""
        if not args:
            return "❌ Usage: DOCS SHOW <name>"

        content_name = " ".join(args)
        item = self._find_content(content_name)

        if not item:
            return f"❌ Content not found: {content_name}\n\nTry 'DOCS SEARCH {content_name}' to find similar."

        # Load content
        content_data = self._load_content(item)
        if not content_data:
            return f"❌ Error loading content: {content_name}"

        # Render based on type
        if item['content_type'] == 'guide':
            return self._show_guide(item, content_data)
        elif item['content_type'] == 'diagram':
            return self._show_diagram(item, content_data)
        else:
            return self._show_generic(item, content_data)

    def _show_guide(self, item: Dict, content_data: Dict) -> str:
        """Display guide overview"""
        steps = content_data.get('steps', [])

        output = ["", f"📖 {item['title']}", "═" * 60]
        output.append(f"Type: Guide | Category: {item['category']}")
        output.append(f"Location: {item.get('location', 'Global')}")
        output.append("")
        output.append(f"📖 Description:")
        output.append(f"   {item['description']}")
        output.append("")

        if steps:
            output.append(f"📋 Steps ({len(steps)} total):")
            output.append("─" * 60)

            progress = self._get_content_progress(item['id'])
            completed = progress['completed_steps']

            for i, step in enumerate(steps, 1):
                status = "✓" if i in completed else " "
                output.append(f"  [{status}] Step {i}: {step['title']}")

            output.append("")
            pct = int(len(completed) / len(steps) * 100) if steps else 0
            bar = self._progress_bar(pct, 20)
            output.append(f"Progress: {bar} {len(completed)}/{len(steps)} ({pct}%)")

        output.append("")
        output.append(f"💡 Commands:")
        output.append(f"   DOCS START {item['id']}  - Begin interactive tutorial")
        output.append(f"   DOCS REVIEW {item['id']} - Assess content quality")
        output.append("")

        result = "\n".join(output)

        # Use pager for long output
        if len(output) > 20:
            page_output(result, title=item['title'])
            return ""  # Already displayed via pager

        return result

    def _show_diagram(self, item: Dict, content_data: Dict) -> str:
        """Display diagram"""
        ascii_content = content_data.get('content', '')

        output = ["", f"📐 {item['title']}", "═" * 60]
        output.append(f"Type: Diagram ({item['category']}) | Size: {content_data.get('width', 0)}×{content_data.get('height', 0)}")
        output.append(f"Description: {item['description']}")
        output.append("")
        output.append("─" * 60)
        output.append(ascii_content)
        output.append("─" * 60)
        output.append("")
        output.append(f"💡 Tip: DOCS REVIEW {item['id']} to assess quality")
        output.append("")

        result = "\n".join(output)

        # Use pager for long output
        if len(output) > 20:
            page_output(result, title=item['title'])
            return ""  # Already displayed via pager

        return result

    def _show_generic(self, item: Dict, content_data: Dict) -> str:
        """Display generic content"""
        output = ["", f"📄 {item['title']}", "═" * 60]
        output.append(f"Type: {item['content_type']} | Category: {item['category']}")
        output.append(f"Description: {item['description']}")
        output.append("")
        output.append(content_data.get('content', ''))
        output.append("")

        result = "\n".join(output)

        # Use pager for long output
        if len(output) > 20:
            page_output(result, title=item['title'])
            return ""  # Already displayed via pager

        return result

    def _start(self, args: List[str]) -> str:
        """Start interactive learning session"""
        if not args:
            return "❌ Usage: DOCS START <name>"

        content_name = " ".join(args)
        item = self._find_content(content_name)

        if not item:
            return f"❌ Content not found: {content_name}"

        # Only guides support interactive mode
        if item['content_type'] != 'guide':
            return f"❌ Content type '{item['content_type']}' doesn't support interactive mode. Use 'DOCS SHOW {item['id']}' instead."

        # Load content
        content_data = self._load_content(item)
        if not content_data:
            return f"❌ Error loading content: {content_name}"

        steps = content_data.get('steps', [])
        if not steps:
            return f"❌ Guide has no interactive steps: {content_name}"

        # Set current session
        self.current_content = item['id']
        self.content_steps = steps

        # Resume from last position or start fresh
        progress = self._get_content_progress(item['id'])
        self.completed_steps = progress['completed_steps']

        # Find first incomplete step
        self.current_step = 1
        for i in range(1, len(steps) + 1):
            if i not in self.completed_steps:
                self.current_step = i
                break

        self._save_progress()

        # Show first step
        output = ["", f"📚 Starting Guide: {item['title']}", "═" * 60]
        output.append(f"Total Steps: {len(steps)}")
        output.append(f"Completed: {len(self.completed_steps)}/{len(steps)}")
        output.append("")
        output.append(self._render_current_step())
        output.append("")
        output.append("💡 Commands: DOCS NEXT | DOCS PREV | DOCS COMPLETE | DOCS PROGRESS")
        output.append("")

        return "\n".join(output)

    def _next(self, args: List[str]) -> str:
        """Move to next step"""
        if not self.current_content:
            return "❌ No active session. Use 'DOCS START <name>' first."

        if self.current_step >= len(self.content_steps):
            return "✓ You're at the last step! Use 'DOCS PROGRESS' to see completion."

        self.current_step += 1
        self._save_progress()

        return self._render_current_step()

    def _prev(self, args: List[str]) -> str:
        """Move to previous step"""
        if not self.current_content:
            return "❌ No active session. Use 'DOCS START <name>' first."

        if self.current_step <= 1:
            return "❌ Already at first step."

        self.current_step -= 1
        self._save_progress()

        return self._render_current_step()

    def _jump(self, args: List[str]) -> str:
        """Jump to specific step"""
        if not self.current_content:
            return "❌ No active session. Use 'DOCS START <name>' first."

        if not args:
            return "❌ Usage: DOCS JUMP <step-number>"

        try:
            step_num = int(args[0])
        except ValueError:
            return f"❌ Invalid step number: {args[0]}"

        if step_num < 1 or step_num > len(self.content_steps):
            return f"❌ Step {step_num} out of range (1-{len(self.content_steps)})"

        self.current_step = step_num
        self._save_progress()

        return self._render_current_step()

    def _complete(self, args: List[str]) -> str:
        """Mark step as complete"""
        if not self.current_content:
            return "❌ No active session. Use 'DOCS START <name>' first."

        # Determine which step to mark complete
        if args:
            try:
                step_num = int(args[0])
            except ValueError:
                return f"❌ Invalid step number: {args[0]}"
        else:
            step_num = self.current_step

        if step_num < 1 or step_num > len(self.content_steps):
            return f"❌ Step {step_num} out of range (1-{len(self.content_steps)})"

        # Mark complete
        self.completed_steps.add(step_num)
        self._save_progress()

        # Check if all steps complete
        if len(self.completed_steps) == len(self.content_steps):
            output = ["", "🎉 Congratulations! Guide Complete!", "═" * 60]
            output.append(f"You've completed all {len(self.content_steps)} steps!")
            output.append("")
            output.append("💡 Tip: Use 'DOCS RESET' to start over, or 'DOCS LIST' for more content.")
            output.append("")
            return "\n".join(output)
        else:
            completed = len(self.completed_steps)
            total = len(self.content_steps)
            pct = int(completed / total * 100)
            bar = self._progress_bar(pct, 20)

            return f"✓ Step {step_num} marked complete!\n\nProgress: {bar} {completed}/{total} ({pct}%)\n"

    def _reset(self, args: List[str]) -> str:
        """Reset progress for content"""
        if args:
            content_name = " ".join(args)
            item = self._find_content(content_name)
            if not item:
                return f"❌ Content not found: {content_name}"
            content_id = item['id']
        elif self.current_content:
            content_id = self.current_content
        else:
            return "❌ Usage: DOCS RESET <name>"

        # Reset progress
        if content_id in self.progress_data:
            del self.progress_data[content_id]
            self._save_progress()

        # Clear current if it's the active session
        if content_id == self.current_content:
            self.completed_steps = set()
            self.current_step = 1

        return f"✓ Progress reset for: {content_id}\n"

    def _progress(self, args: List[str]) -> str:
        """Show current session progress"""
        if not self.current_content:
            return "❌ No active session. Use 'DOCS START <name>' first."

        total = len(self.content_steps)
        completed = len(self.completed_steps)
        pct = int(completed / total * 100) if total > 0 else 0

        output = ["", f"📊 Progress: {self.current_content}", "═" * 60]
        output.append(f"Current Step: {self.current_step}/{total}")
        output.append(f"Completed: {completed}/{total} steps ({pct}%)")
        output.append("")
        output.append(self._progress_bar(pct, 30))
        output.append("")

        # Show step checklist
        output.append("Checklist:")
        output.append("─" * 60)
        for i, step in enumerate(self.content_steps, 1):
            status = "✓" if i in self.completed_steps else " "
            current = "→" if i == self.current_step else " "
            output.append(f"{current} [{status}] Step {i}: {step['title']}")

        output.append("")
        return "\n".join(output)

    def _continue(self, args: List[str]) -> str:
        """Continue last learning session"""
        # Find most recent content with incomplete progress
        recent = None
        recent_time = None

        for content_id, progress in self.progress_data.items():
            if progress['completed'] < progress['total']:
                updated = datetime.fromisoformat(progress.get('last_updated', '2000-01-01'))
                if recent_time is None or updated > recent_time:
                    recent = content_id
                    recent_time = updated

        if not recent:
            return "❌ No active learning session\n\nStart content: DOCS START <name>\n"

        return self._start([recent])

    def _types(self, args: List[str]) -> str:
        """Show content type categories"""
        output = ["", "📊 Content Type Categories", "═" * 60, ""]

        # Count by type
        by_type = {}
        for item in self.content_index:
            ctype = item['content_type']
            if ctype not in by_type:
                by_type[ctype] = []
            by_type[ctype].append(item)

        # Display categories
        for ctype, desc in sorted(self.content_types.items()):
            items = by_type.get(ctype, [])
            count = len(items)
            icon = self._get_type_icon(ctype)
            bar = "█" * min(count, 30)
            output.append(f"  {icon} {ctype:12} {bar} ({count})")
            output.append(f"               {desc}")
            output.append("")

        # Diagram subcategories
        output.append("📐 Diagram Subcategories:")
        output.append("─" * 60)
        diagram_items = by_type.get('diagram', [])
        diagram_counts = {}
        for item in diagram_items:
            cat = item['category']
            diagram_counts[cat] = diagram_counts.get(cat, 0) + 1

        for dtype, desc in sorted(self.diagram_types.items()):
            count = diagram_counts.get(dtype, 0)
            bar = "░" * min(count, 20)
            if count > 0:
                output.append(f"  {dtype:12} {bar} ({count})")

        output.append("")
        output.append("─" * 60)
        output.append(f"Total: {len(self.content_index)} items across {len(self.content_types)} types")
        output.append("")
        output.append("💡 Tip: DOCS LIST <type> to browse category")
        output.append("")

        return "\n".join(output)

    def _review(self, args: List[str]) -> str:
        """
        v1.1.17 NEW: Assess content quality and completeness

        Scores content on:
        - Completeness (all sections present)
        - Clarity (readable, well-structured)
        - Accuracy (citations, references)
        - Usefulness (practical, actionable)
        """
        if not args:
            return "❌ Usage: DOCS REVIEW <name>"

        content_name = " ".join(args)
        item = self._find_content(content_name)

        if not item:
            return f"❌ Content not found: {content_name}"

        # Load content
        content_data = self._load_content(item)
        if not content_data:
            return f"❌ Error loading content: {content_name}"

        # Run quality assessment
        quality_scores = self._assess_quality(item, content_data)

        # Build output
        output = ["", f"📋 Content Quality Review: {item['title']}", "═" * 60]
        output.append(f"Type: {item['content_type']} | Category: {item['category']}")
        output.append("")

        # Overall score
        overall = sum(quality_scores.values()) / len(quality_scores)
        overall_pct = int(overall * 100)
        bar = self._progress_bar(overall_pct, 30)
        output.append(f"Overall Quality: {bar} {overall_pct}%")
        output.append("")

        # Individual scores
        output.append("Quality Dimensions:")
        output.append("─" * 60)
        for dimension, score in quality_scores.items():
            pct = int(score * 100)
            status = "✓" if score >= 0.8 else "⚠" if score >= 0.6 else "✗"
            bar = self._progress_bar(pct, 20)
            output.append(f"{status} {dimension:15} {bar} {pct}%")

        output.append("")

        # Recommendations
        if overall < 0.8:
            output.append("💡 Recommendations:")
            output.append("─" * 60)
            for dimension, score in quality_scores.items():
                if score < 0.8:
                    output.append(f"  • Improve {dimension}: {self._get_improvement_tip(dimension, item['content_type'])}")
            output.append("")
            output.append(f"Try: DOCS REGEN {item['id']} to improve with AI")
        else:
            output.append("✅ Content quality is excellent!")

        output.append("")

        return "\n".join(output)

    def _regen(self, args: List[str]) -> str:
        """
        v1.1.17 NEW: Regenerate content with AI improvements

        Uses Gemini API to enhance content based on quality assessment.
        Maintains version history for rollback.
        """
        if not args:
            return """❌ Usage: DOCS REGEN <name> [options]

Options:
  --pro              Use Gemini Pro for better quality
  --strict           Require 100% citation coverage
  --preview          Show changes without saving
  --rollback         Revert to previous version

Examples:
  DOCS REGEN water-purification
  DOCS REGEN bushfire-survival --pro
  DOCS REGEN shelter-building --preview
"""

        # Parse args
        content_name = []
        options = {'pro': False, 'strict': False, 'preview': False, 'rollback': False}

        for arg in args:
            if arg.startswith('--'):
                opt = arg[2:]
                if opt in options:
                    options[opt] = True
            else:
                content_name.append(arg)

        content_name = " ".join(content_name)

        if not content_name:
            return "❌ Content name required"

        item = self._find_content(content_name)
        if not item:
            return f"❌ Content not found: {content_name}"

        # Handle rollback
        if options['rollback']:
            return self._rollback_content(item)

        # Load content
        content_data = self._load_content(item)
        if not content_data:
            return f"❌ Error loading content: {content_name}"

        # Check for Gemini API
        try:
            from core.services.gemini_generator import get_gemini_generator
            generator = get_gemini_generator()
        except ImportError:
            return "❌ Gemini generator not available. Install required dependencies."
        except ValueError as e:
            return f"❌ {str(e)}\n\nSet GEMINI_API_KEY in .env file to enable content regeneration."

        # Assess current quality (before)
        quality_before = self._assess_quality(item, content_data)
        overall_before = sum(quality_before.values()) / len(quality_before)

        # Run regeneration
        output = ["", f"🔄 Regenerating: {item['title']}", "═" * 60]
        output.append(f"Mode: {'Pro' if options['pro'] else 'Standard'} | Citations: {'Strict' if options['strict'] else 'Standard'}")
        output.append("")
        output.append(f"Current Quality: {self._progress_bar(int(overall_before * 100))} {overall_before:.1%}")
        output.append("")

        # Get quality recommendations
        weak_areas = [dim for dim, score in quality_before.items() if score < 0.8]
        if weak_areas:
            output.append("Areas for improvement:")
            for dim in weak_areas:
                output.append(f"  • {dim.capitalize()}: {self._get_improvement_tip(dim, item['type'])}")
            output.append("")

        output.append("⏳ Generating improved content with AI...")
        output.append("")

        try:
            # Generate enhanced content
            enhanced_content = self._generate_enhanced_content(
                item, content_data, quality_before, options
            )

            # Preview mode - show changes without saving
            if options['preview']:
                output.append("📋 Preview Mode (changes not saved):")
                output.append("")
                output.append(enhanced_content[:500] + "..." if len(enhanced_content) > 500 else enhanced_content)
                output.append("")
                output.append("Run without --preview to apply changes")
                return "\n".join(output)

            # Save version to archive
            archive_path = self._save_version(item, content_data)
            output.append(f"✅ Previous version archived: {archive_path.name}")
            output.append("")

            # Apply enhanced content
            self._save_enhanced_content(item, enhanced_content)

            # Assess new quality (after)
            new_content_data = self._load_content(item)
            quality_after = self._assess_quality(item, new_content_data)
            overall_after = sum(quality_after.values()) / len(quality_after)

            # Show improvements
            output.append(f"New Quality: {self._progress_bar(int(overall_after * 100))} {overall_after:.1%}")
            output.append("")
            output.append("Quality Changes:")
            for dim in quality_before.keys():
                before_pct = int(quality_before[dim] * 100)
                after_pct = int(quality_after[dim] * 100)
                delta = after_pct - before_pct
                icon = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
                output.append(f"  {icon} {dim.capitalize()}: {before_pct}% → {after_pct}% ({delta:+d}%)")

            output.append("")
            output.append(f"✅ Content regenerated successfully")
            output.append(f"   Use 'DOCS HISTORY {content_name}' to view version history")
            output.append(f"   Use 'DOCS REGEN {content_name} --rollback' to revert")

        except Exception as e:
            output.append(f"❌ Regeneration failed: {str(e)}")
            output.append("")
            output.append("Please check:")
            output.append("  • GEMINI_API_KEY is set in .env")
            output.append("  • API key has valid permissions")
            output.append("  • Network connection is available")

        return "\n".join(output)

    def _history(self, args: List[str]) -> str:
        """
        v1.1.17 NEW: View content version history

        Shows all versions with timestamps and quality scores.
        """
        if not args:
            return "❌ Usage: DOCS HISTORY <name>"

        content_name = " ".join(args)
        item = self._find_content(content_name)

        if not item:
            return f"❌ Content not found: {content_name}"

        # Check for version history
        content_path = Path(item['path'])
        archive_dir = content_path.parent / ".archive" / "versions"
        metadata_path = archive_dir / "metadata.json"

        if not metadata_path.exists():
            return f"❌ No version history found for: {item['title']}\n\nContent has not been regenerated yet."

        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        versions = metadata.get("versions", [])
        if not versions:
            return f"❌ Version history empty for: {item['title']}"

        # Build output
        output = ["", f"📜 Version History: {item['title']}", "═" * 60]
        output.append(f"Total versions: {len(versions)}")
        output.append("")

        # Show versions in reverse chronological order (newest first)
        for i, version in enumerate(reversed(versions), 1):
            version_num = len(versions) - i + 1
            is_current = (i == 1)
            icon = "📍" if is_current else "📝"

            output.append(f"{icon} Version {version_num} {' (CURRENT)' if is_current else ''}")
            output.append(f"   File: {version['file']}")
            output.append(f"   Date: {version['timestamp'][:19].replace('T', ' ')}")
            output.append(f"   Overall Quality: {self._progress_bar(int(version['overall'] * 100))} {version['overall']:.1%}")
            output.append("")

            # Show quality breakdown
            output.append("   Quality Breakdown:")
            scores = version.get('quality_scores', {})
            for dim, score in scores.items():
                pct = int(score * 100)
                status = "✓" if score >= 0.8 else "⚠" if score >= 0.7 else "✗"
                output.append(f"     {status} {dim.capitalize()}: {self._progress_bar(pct, 15)} {score:.1%}")

            # Show improvement from previous version
            if i < len(versions):
                prev_idx = len(versions) - i
                prev_overall = versions[prev_idx - 1]['overall']
                delta = version['overall'] - prev_overall
                if delta > 0:
                    output.append(f"     📈 +{delta:.1%} improvement from v{version_num - 1}")
                elif delta < 0:
                    output.append(f"     📉 {delta:.1%} decline from v{version_num - 1}")

            output.append("")

        # Add usage tips
        output.append("═" * 60)
        output.append("Commands:")
        output.append(f"  DOCS REVIEW {content_name}")
        output.append(f"  DOCS REGEN {content_name} [--pro] [--strict]")
        output.append(f"  DOCS REGEN {content_name} --rollback")
        output.append("")

        return "\n".join(output)

    # === Smart content access ===

    def _smart_content_access(self, query: str) -> str:
        """Smart content detection and access"""
        query_lower = query.lower()

        # Search for matches
        matches = []
        for item in self.content_index:
            if (query_lower in item['id'].lower() or
                query_lower in item['title'].lower()):
                matches.append(item)

        # No matches
        if not matches:
            return f"\n❌ No content found for '{query}'\n\nTry: DOCS SEARCH {query}\n"

        # Single match - show it
        if len(matches) == 1:
            return self._show([matches[0]['id']])

        # Multiple matches - show picker
        return self._show_matches(query, matches)

    def _show_matches(self, query: str, matches: List[Dict]) -> str:
        """Show multiple matches with type indicators"""
        output = [f"\n📚 Content matching '{query}':", "═" * 60, ""]

        # Group by type
        by_type = {}
        for item in matches:
            ctype = item['content_type']
            if ctype not in by_type:
                by_type[ctype] = []
            by_type[ctype].append(item)

        for ctype, items in sorted(by_type.items()):
            icon = self._get_type_icon(ctype)
            output.append(f"{icon} {ctype.upper()}:")
            for item in items:
                output.append(f"  • {item['title']} ({item['category']})")
            output.append("")

        output.append("─" * 60)
        output.append("Access: DOCS SHOW <name> (exact match needed)")
        output.append("")

        return "\n".join(output)

    # === Content indexing and loading ===

    def _build_content_index(self):
        """Build unified index of all documentation content"""
        self.content_index = []

        # Index guides
        self._index_guides()

        # Index diagrams
        self._index_diagrams()

        # Index reference docs
        self._index_references()

    def _index_guides(self):
        """Index all guides from knowledge directory"""
        # Define guide categories
        categories = ['water', 'fire', 'shelter', 'food', 'navigation',
                     'medical', 'skills', 'tools', 'survival', 'making']

        for category in categories:
            cat_path = self.knowledge_path / category
            if not cat_path.exists():
                continue

            for md_file in cat_path.rglob("*.md"):
                if md_file.name.startswith('.') or 'README' in md_file.name:
                    continue

                metadata = self._parse_markdown_metadata(md_file)
                if metadata:
                    self.content_index.append({
                        'id': md_file.stem,
                        'title': metadata['title'],
                        'description': metadata['description'],
                        'content_type': 'guide',
                        'category': category,
                        'path': md_file,
                        'location': metadata.get('location'),
                        'doc_id': metadata.get('doc_id'),
                        'tags': metadata.get('tags', ''),
                    })

    def _index_diagrams(self):
        """Index all diagrams from knowledge and diagrams directory"""
        # Scan knowledge for ASCII diagrams
        for md_file in self.knowledge_path.rglob("*.md"):
            if md_file.name.startswith('.'):
                continue

            content = md_file.read_text()
            blocks = re.finditer(r'```(?:ascii)?\n(.+?)```', content, re.DOTALL)

            for i, match in enumerate(blocks, 1):
                diagram_content = match.group(1)

                # Analyze diagram
                lines = diagram_content.split('\n')
                height = len(lines)
                width = max(len(line) for line in lines) if lines else 0

                # Skip small diagrams
                if height < 3 or width < 10:
                    continue

                # Classify diagram type
                dtype = self._classify_diagram(diagram_content, md_file)

                # Extract context
                context = self._extract_context(content, match.start())

                self.content_index.append({
                    'id': f"{md_file.stem}-diagram-{i}",
                    'title': f"{md_file.stem.title()} Diagram {i}",
                    'description': context or f"Diagram from {md_file.name}",
                    'content_type': 'diagram',
                    'category': dtype,
                    'path': md_file,
                    'width': width,
                    'height': height,
                    'tags': dtype,
                })

        # Scan dedicated diagrams directory
        if self.diagrams_path.exists():
            for diagram_file in self.diagrams_path.rglob("*.txt"):
                content = diagram_file.read_text()
                metadata = self._parse_diagram_metadata(content)

                lines = content.split('\n')
                height = len(lines)
                width = max(len(line) for line in lines) if lines else 0

                dtype = metadata.get('type', 'ascii')

                self.content_index.append({
                    'id': diagram_file.stem,
                    'title': metadata.get('name', diagram_file.stem.title()),
                    'description': metadata.get('description', ''),
                    'content_type': 'diagram',
                    'category': dtype,
                    'path': diagram_file,
                    'width': width,
                    'height': height,
                    'tags': dtype,
                })

    def _index_references(self):
        """Index reference documentation"""
        # Reference docs in knowledge/reference/
        ref_path = self.knowledge_path / "reference"
        if not ref_path.exists():
            return

        for md_file in ref_path.rglob("*.md"):
            if md_file.name.startswith('.') or 'README' in md_file.name:
                continue

            metadata = self._parse_markdown_metadata(md_file)
            if metadata:
                self.content_index.append({
                    'id': md_file.stem,
                    'title': metadata['title'],
                    'description': metadata['description'],
                    'content_type': 'reference',
                    'category': md_file.parent.name,
                    'path': md_file,
                    'tags': metadata.get('tags', ''),
                })

    def _find_content(self, content_name: str) -> Optional[Dict]:
        """Find content by name or ID"""
        # Try exact ID match
        for item in self.content_index:
            if item['id'] == content_name:
                return item

        # Try fuzzy match
        name_lower = content_name.lower()
        for item in self.content_index:
            if (name_lower in item['title'].lower() or
                name_lower in item['id'].lower()):
                return item

        return None

    def _load_content(self, item: Dict) -> Optional[Dict]:
        """Load content from file"""
        try:
            path = item['path']

            if item['content_type'] == 'guide':
                content = path.read_text()
                steps = self._extract_steps(content)
                return {'content': content, 'steps': steps}

            elif item['content_type'] == 'diagram':
                if path.suffix == '.md':
                    # Extract diagram from markdown code block
                    content = path.read_text()
                    match = re.search(r'```(?:ascii)?\n(.+?)```', content, re.DOTALL)
                    if match:
                        diagram = match.group(1)
                    else:
                        diagram = content
                else:
                    diagram = path.read_text()

                lines = diagram.split('\n')
                return {
                    'content': diagram,
                    'width': item['width'],
                    'height': item['height']
                }

            else:
                # Generic content
                return {'content': path.read_text()}

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading content {item['id']}: {e}")
            return None

    def _parse_markdown_metadata(self, file_path: Path) -> Optional[Dict]:
        """Parse guide metadata from markdown file"""
        try:
            content = file_path.read_text()

            # Extract title (first H1)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem

            # Extract description (first paragraph after title)
            desc_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|\n#)', content, re.MULTILINE | re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else "No description"
            description = description[:100] + "..." if len(description) > 100 else description

            # Extract metadata fields
            location_match = re.search(r'\*\*Location:\*\*\s+(.+)', content)
            doc_id_match = re.search(r'\*\*Document ID:\*\*\s+(.+)', content)
            tags_match = re.search(r'\*\*Tags:\*\*\s+(.+)', content)

            return {
                'title': title,
                'description': description,
                'location': location_match.group(1) if location_match else None,
                'doc_id': doc_id_match.group(1) if doc_id_match else None,
                'tags': tags_match.group(1) if tags_match else '',
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing metadata from {file_path}: {e}")
            return None

    def _extract_steps(self, content: str) -> List[Dict]:
        """Extract interactive steps from guide content"""
        steps = []

        # Look for numbered sections (## 1., ## 2., etc.)
        pattern = r'^##\s+(\d+)\.\s+(.+?)$\n\n(.+?)(?=\n##|\Z)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            step_num = int(match.group(1))
            step_title = match.group(2).strip()
            step_content = match.group(3).strip()

            steps.append({
                'number': step_num,
                'title': step_title,
                'content': step_content
            })

        return sorted(steps, key=lambda x: x['number'])

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
        if re.search(r'(\|.*\|.*\|)', content):
            return 'table'

        return 'ascii'

    def _extract_context(self, content: str, diagram_pos: int) -> Optional[str]:
        """Extract description from text before diagram"""
        before = content[:diagram_pos]
        paragraphs = before.split('\n\n')

        if paragraphs:
            last_para = paragraphs[-1].strip()
            last_para = re.sub(r'[*_#`]', '', last_para)
            if len(last_para) > 100:
                last_para = last_para[:97] + "..."
            return last_para

        return None

    def _parse_diagram_metadata(self, content: str) -> Dict:
        """Parse metadata from diagram file header"""
        metadata = {}

        lines = content.split('\n')
        for line in lines[:10]:
            if line.startswith('#'):
                metadata['name'] = line.lstrip('# ').strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                metadata[key] = value

        return metadata

    # === Progress tracking ===

    def _get_content_progress(self, content_id: str) -> Dict:
        """Get progress for specific content"""
        if content_id in self.progress_data:
            data = self.progress_data[content_id]
            return {
                'completed': data.get('completed', 0),
                'total': data.get('total', 0),
                'completed_steps': set(data.get('completed_steps', [])),
                'last_step': data.get('last_step', 1),
            }
        else:
            return {
                'completed': 0,
                'total': 0,
                'completed_steps': set(),
                'last_step': 1,
            }

    def _load_progress(self):
        """Load saved progress from file"""
        if not self.progress_file.exists():
            self.progress_data = {}
            return

        # Use shared utility for safe JSON loading
        success, data, error = self.load_json_file(str(self.progress_file))
        if success:
            self.progress_data = data
        else:
            if self.logger:
                self.logger.error(f"Error loading progress: {error}")
            self.progress_data = {}

    def _save_progress(self):
        """Save progress to file"""
        if self.current_content:
            self.progress_data[self.current_content] = {
                'completed': len(self.completed_steps),
                'total': len(self.content_steps),
                'completed_steps': list(self.completed_steps),
                'last_step': self.current_step,
                'last_updated': datetime.now().isoformat()
            }

        # Use shared utility for atomic JSON save
        success, error = self.save_json_file(str(self.progress_file), self.progress_data)
        if not success and self.logger:
            self.logger.error(f"Error saving progress: {error}")

    def _render_current_step(self) -> str:
        """Render the current step content"""
        if not self.current_content or not self.content_steps:
            return "❌ No active session."

        step = self.content_steps[self.current_step - 1]
        total = len(self.content_steps)
        completed = len(self.completed_steps)
        is_complete = self.current_step in self.completed_steps

        output = ["", f"Step {self.current_step}/{total}: {step['title']}", "═" * 60]

        if is_complete:
            output.append("✓ COMPLETED")
            output.append("")

        output.append(step['content'])
        output.append("")
        output.append("─" * 60)

        # Progress bar
        pct = int(completed / total * 100)
        bar = self._progress_bar(pct, 30)
        output.append(f"Progress: {bar} {completed}/{total}")
        output.append("")

        return "\n".join(output)

    # === Quality assessment (v1.1.17 NEW) ===

    def _assess_quality(self, item: Dict, content_data: Dict) -> Dict[str, float]:
        """
        Assess content quality across multiple dimensions

        Returns scores (0.0-1.0) for:
        - Completeness
        - Clarity
        - Accuracy
        - Usefulness
        """
        content = content_data.get('content', '')

        scores = {
            'Completeness': self._score_completeness(item, content),
            'Clarity': self._score_clarity(content),
            'Accuracy': self._score_accuracy(content),
            'Usefulness': self._score_usefulness(item, content),
        }

        return scores

    def _score_completeness(self, item: Dict, content: str) -> float:
        """Score content completeness"""
        score = 0.0

        # Has title
        if re.search(r'^#\s+.+', content, re.MULTILINE):
            score += 0.2

        # Has description
        if len(content) > 200:
            score += 0.2

        # Has sections (guides)
        if item['content_type'] == 'guide':
            sections = re.findall(r'^##\s+', content, re.MULTILINE)
            if len(sections) >= 3:
                score += 0.3
            elif len(sections) > 0:
                score += 0.15

        # Has code blocks/diagrams (if applicable)
        if item['content_type'] in ['guide', 'reference']:
            if re.search(r'```', content):
                score += 0.15

        # Has examples
        if 'example' in content.lower():
            score += 0.15

        return min(score, 1.0)

    def _score_clarity(self, content: str) -> float:
        """Score content clarity"""
        score = 0.0

        # Reasonable length (not too short, not too long)
        word_count = len(content.split())
        if 100 < word_count < 5000:
            score += 0.3
        elif word_count >= 100:
            score += 0.15

        # Has lists
        if re.search(r'(^\s*[-*+]\s+|\d+\.)', content, re.MULTILINE):
            score += 0.2

        # Well-structured (headers)
        headers = re.findall(r'^#+\s+', content, re.MULTILINE)
        if len(headers) >= 2:
            score += 0.2

        # Has formatting (bold, italic)
        if re.search(r'(\*\*|__|\*|_)', content):
            score += 0.15

        # Readable sentences (not too long)
        sentences = re.split(r'[.!?]\s+', content)
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        if avg_words < 30:
            score += 0.15

        return min(score, 1.0)

    def _score_accuracy(self, content: str) -> float:
        """Score content accuracy"""
        score = 0.5  # Base score (assume accurate unless proven otherwise)

        # Has citations/references
        if re.search(r'(source:|reference:|citation:|cited)', content, re.IGNORECASE):
            score += 0.2

        # Has links
        if re.search(r'\[.+\]\(.+\)', content):
            score += 0.15

        # Has metadata (location, doc ID)
        if re.search(r'\*\*(Location|Document ID):\*\*', content):
            score += 0.15

        return min(score, 1.0)

    def _score_usefulness(self, item: Dict, content: str) -> float:
        """Score content usefulness"""
        score = 0.0

        # Has practical steps (guides)
        if item['content_type'] == 'guide':
            steps = re.findall(r'^##\s+\d+\.', content, re.MULTILINE)
            if len(steps) >= 3:
                score += 0.3
            elif len(steps) > 0:
                score += 0.15

        # Has warnings/cautions
        if re.search(r'(⚠️|warning|caution|important|danger)', content, re.IGNORECASE):
            score += 0.2

        # Has tips/recommendations
        if re.search(r'(💡|tip|recommendation|note|pro tip)', content, re.IGNORECASE):
            score += 0.2

        # Has visual aids (diagrams)
        if item['content_type'] == 'guide' and re.search(r'```', content):
            score += 0.15

        # Has troubleshooting
        if re.search(r'(troubleshoot|problem|issue|fix|solution)', content, re.IGNORECASE):
            score += 0.15

        return min(score, 1.0)

    def _get_improvement_tip(self, dimension: str, content_type: str) -> str:
        """Get improvement tip for quality dimension"""
        tips = {
            'Completeness': {
                'guide': 'Add more sections covering setup, execution, and troubleshooting',
                'diagram': 'Include description, legend, and usage examples',
                'reference': 'Add comprehensive coverage of all key concepts',
            },
            'Clarity': {
                'guide': 'Break down complex steps, add numbered lists',
                'diagram': 'Add labels, annotations, and context',
                'reference': 'Organize with clear headings and structure',
            },
            'Accuracy': {
                'guide': 'Add citations, references, and source attribution',
                'diagram': 'Include technical specifications and accuracy notes',
                'reference': 'Add authoritative sources and verification',
            },
            'Usefulness': {
                'guide': 'Add practical examples, warnings, and tips',
                'diagram': 'Include usage context and common applications',
                'reference': 'Add quick-start examples and common scenarios',
            },
        }

        return tips.get(dimension, {}).get(content_type, 'Review and enhance content')

    # === Content regeneration helpers (v1.1.17+) ===

    def _generate_enhanced_content(self, item: Dict, content_data: Dict,
                                   quality_scores: Dict[str, float],
                                   options: Dict[str, bool]) -> str:
        """
        Generate enhanced content using Gemini API.

        Args:
            item: Content metadata
            content_data: Current content
            quality_scores: Quality assessment scores
            options: Regeneration options (pro, strict, etc.)

        Returns:
            Enhanced content string
        """
        from core.services.gemini_generator import get_gemini_generator

        # Get Gemini generator
        generator = get_gemini_generator()

        # Build enhancement prompt
        prompt_parts = []
        prompt_parts.append(f"# Content Enhancement Task")
        prompt_parts.append(f"")
        prompt_parts.append(f"**Original Content:** {item['title']}")
        prompt_parts.append(f"**Type:** {item['type']}")
        prompt_parts.append(f"**Category:** {item.get('category', 'general')}")
        prompt_parts.append(f"")
        prompt_parts.append(f"## Current Quality Scores")
        for dim, score in quality_scores.items():
            status = "✓ Good" if score >= 0.8 else "⚠ Needs improvement"
            prompt_parts.append(f"- {dim.capitalize()}: {score:.1%} {status}")
        prompt_parts.append(f"")

        # Identify weak areas
        weak_areas = [dim for dim, score in quality_scores.items() if score < 0.8]
        if weak_areas:
            prompt_parts.append(f"## Areas Requiring Improvement")
            for dim in weak_areas:
                tip = self._get_improvement_tip(dim, item['type'])
                prompt_parts.append(f"- **{dim.capitalize()}:** {tip}")
            prompt_parts.append(f"")

        # Mode-specific instructions
        if options['pro']:
            prompt_parts.append(f"## Enhancement Mode: PRO")
            prompt_parts.append(f"- Provide expert-level analysis and depth")
            prompt_parts.append(f"- Include advanced techniques and nuances")
            prompt_parts.append(f"- Add practical warnings and edge cases")
            prompt_parts.append(f"- Cross-reference related topics")
        else:
            prompt_parts.append(f"## Enhancement Mode: STANDARD")
            prompt_parts.append(f"- Maintain clear, accessible language")
            prompt_parts.append(f"- Focus on practical application")
            prompt_parts.append(f"- Include beginner-friendly explanations")

        prompt_parts.append(f"")

        if options['strict']:
            prompt_parts.append(f"## Citation Requirements: STRICT")
            prompt_parts.append(f"- Include citations for all factual claims")
            prompt_parts.append(f"- Use Markdown reference format: [source_name](URL)")
            prompt_parts.append(f"- Add 'References' section at end")
            prompt_parts.append(f"- Prefer authoritative sources (WHO, CDC, scientific papers)")
        else:
            prompt_parts.append(f"## Citation Requirements: STANDARD")
            prompt_parts.append(f"- Add citations for key facts and figures")
            prompt_parts.append(f"- Include references section if using external sources")

        prompt_parts.append(f"")
        prompt_parts.append(f"## Original Content")
        prompt_parts.append(f"```markdown")
        prompt_parts.append(content_data.get('content', ''))
        prompt_parts.append(f"```")
        prompt_parts.append(f"")
        prompt_parts.append(f"## Task")
        prompt_parts.append(f"Enhance the above content addressing the quality issues identified.")
        prompt_parts.append(f"Maintain the same Markdown format and structure.")
        prompt_parts.append(f"Return ONLY the enhanced Markdown content, no explanations.")

        prompt = "\n".join(prompt_parts)

        # Generate enhanced content
        enhanced_text, citations = generator.generate_text(
            source_content=content_data.get('content', ''),
            topic=item['title']
        )

        return enhanced_text

    def _save_version(self, item: Dict, content_data: Dict) -> Path:
        """
        Save current version to .archive/versions/.

        Args:
            item: Content metadata
            content_data: Current content

        Returns:
            Path to archived version
        """
        from datetime import datetime

        # Determine archive directory
        content_path = Path(item['path'])
        archive_dir = content_path.parent / ".archive" / "versions"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Generate version filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"{content_path.stem}_v{timestamp}{content_path.suffix}"
        archive_path = archive_dir / version_name

        # Save content
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(content_data.get('content', ''))

        # Update metadata
        metadata_path = archive_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            metadata = {"versions": []}

        # Add version record
        quality_scores = self._assess_quality(item, content_data)
        metadata["versions"].append({
            "file": version_name,
            "timestamp": datetime.now().isoformat(),
            "quality_scores": quality_scores,
            "overall": sum(quality_scores.values()) / len(quality_scores)
        })

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

        return archive_path

    def _save_enhanced_content(self, item: Dict, content: str) -> None:
        """
        Save enhanced content to file.

        Args:
            item: Content metadata
            content: Enhanced content string
        """
        content_path = Path(item['path'])
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _rollback_content(self, item: Dict) -> str:
        """
        Rollback content to previous version.

        Args:
            item: Content metadata

        Returns:
            Status message
        """
        content_path = Path(item['path'])
        archive_dir = content_path.parent / ".archive" / "versions"
        metadata_path = archive_dir / "metadata.json"

        if not metadata_path.exists():
            return "❌ No version history found"

        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        versions = metadata.get("versions", [])
        if len(versions) < 2:
            return "❌ No previous version available"

        # Get previous version (second to last)
        prev_version = versions[-2]
        version_path = archive_dir / prev_version["file"]

        if not version_path.exists():
            return f"❌ Version file not found: {prev_version['file']}"

        # Load previous content
        with open(version_path, 'r', encoding='utf-8') as f:
            prev_content = f.read()

        # Save current as new version before rollback
        current_data = self._load_content(item)
        self._save_version(item, current_data)

        # Restore previous content
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(prev_content)

        # Show quality comparison
        output = ["", f"⏪ Rolled back: {item['title']}", "═" * 60]
        output.append(f"Restored version: {prev_version['file']}")
        output.append(f"Previous quality: {prev_version['overall']:.1%}")
        output.append("")
        output.append("✅ Rollback complete")

        return "\n".join(output)

    # === Utility methods ===

    def _progress_bar(self, percent: int, width: int = 20) -> str:
        """Generate ASCII progress bar"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percent}%"

    def _get_type_icon(self, content_type: str) -> str:
        """Get emoji icon for content type"""
        icons = {
            'guide': '📖',
            'diagram': '📐',
            'reference': '📋',
            'manual': '📚',
        }
        return icons.get(content_type, '📄')


def create_handler(viewport=None, logger=None):
    """Factory function to create unified handler"""
    return DocsUnifiedHandler(viewport=viewport, logger=logger)
