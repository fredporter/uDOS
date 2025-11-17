"""
HANDBOOK Command Handler - v1.0.22
Structured documentation reader for the uDOS Handbook

Commands:
  HANDBOOK
  HANDBOOK VOL1|VOL2|VOL3|VOL4
  HANDBOOK <chapter>
  HANDBOOK BOOKMARK
  HANDBOOK PROGRESS

Author: uDOS Development Team
Version: 1.0.22
"""

from pathlib import Path
from typing import List, Dict, Optional
import json


class HandbookHandler:
    """Handler for HANDBOOK commands - structured reader"""

    def __init__(self, viewport=None, logger=None):
        """Initialize HandbookHandler"""
        self.viewport = viewport
        self.logger = logger
        self.wiki_path = Path("wiki")
        self.memory_path = Path("memory/modules")

        # Handbook structure
        self.volumes = self._define_volumes()

        # Load reading progress
        self.progress = self._load_progress()

    def handle(self, command: str, args: List[str]) -> str:
        """Route HANDBOOK commands to appropriate handlers"""

        if not command or command == "HELP":
            return self._show_help()

        if command == "PROGRESS":
            return self._show_progress()

        if command == "BOOKMARK":
            return self._show_bookmark()

        if command.startswith("VOL"):
            return self._show_volume(command)

        # Show specific chapter
        chapter = command.lower()
        return self._show_chapter(chapter)

    def _define_volumes(self) -> Dict:
        """Define handbook volume structure"""
        return {
            "VOL1": {
                "title": "Volume 1: System & Commands",
                "chapters": [
                    {"name": "getting-started", "title": "Getting Started"},
                    {"name": "command-reference", "title": "Command Reference"},
                    {"name": "architecture", "title": "System Architecture"},
                    {"name": "configuration", "title": "Configuration"},
                    {"name": "troubleshooting", "title": "Troubleshooting"}
                ]
            },
            "VOL2": {
                "title": "Volume 2: Knowledge Library",
                "chapters": [
                    {"name": "knowledge-system", "title": "Knowledge System Overview"},
                    {"name": "quickref-v1.0.20-knowledge", "title": "Quick Reference"},
                    {"name": "skill-trees", "title": "Skill Trees"},
                    {"name": "cross-references", "title": "Cross-References"}
                ]
            },
            "VOL3": {
                "title": "Volume 3: Development & Scripting",
                "chapters": [
                    {"name": "ucode-language", "title": "uCODE Language Guide"},
                    {"name": "extensions-system", "title": "Extensions System"},
                    {"name": "adventure-creation", "title": "Adventure Creation"},
                    {"name": "api-documentation", "title": "API Documentation"}
                ]
            },
            "VOL4": {
                "title": "Volume 4: Practical Applications",
                "chapters": [
                    {"name": "workflows", "title": "Common Workflows"},
                    {"name": "examples", "title": "Example Projects"},
                    {"name": "project-templates", "title": "Project Templates"},
                    {"name": "community", "title": "Community Resources"}
                ]
            }
        }

    def _load_progress(self) -> Dict:
        """Load reading progress from memory"""
        progress_file = self.memory_path / "handbook_progress.json"

        if progress_file.exists():
            try:
                return json.loads(progress_file.read_text())
            except Exception:
                pass

        return {
            "current_volume": "VOL1",
            "current_chapter": "getting-started",
            "bookmarks": [],
            "completed": []
        }

    def _save_progress(self):
        """Save reading progress to memory"""
        progress_file = self.memory_path / "handbook_progress.json"

        try:
            self.memory_path.mkdir(parents=True, exist_ok=True)
            progress_file.write_text(json.dumps(self.progress, indent=2))
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save handbook progress: {e}")

    def _show_help(self) -> str:
        """Display HANDBOOK command help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  HANDBOOK - Structured Documentation Reader                    │
└─────────────────────────────────────────────────────────────────┘

📕 Navigate the complete uDOS Handbook

USAGE:
  HANDBOOK               Show handbook home
  HANDBOOK VOL1          Show Volume 1 (System & Commands)
  HANDBOOK VOL2          Show Volume 2 (Knowledge Library)
  HANDBOOK VOL3          Show Volume 3 (Development)
  HANDBOOK VOL4          Show Volume 4 (Applications)
  HANDBOOK <chapter>     Jump to specific chapter
  HANDBOOK PROGRESS      Show reading progress
  HANDBOOK BOOKMARK      Show bookmarks

VOLUMES:
  📘 Volume 1: System & Commands (250 pages)
     Getting Started, Commands, Architecture, Configuration

  📗 Volume 2: Knowledge Library (250 pages)
     Knowledge System, Skills, Guides, Cross-References

  📙 Volume 3: Development & Scripting (250 pages)
     uCODE Language, Extensions, Adventures, API

  📕 Volume 4: Practical Applications (250 pages)
     Workflows, Examples, Templates, Community

EXAMPLES:
  HANDBOOK VOL1              Browse Volume 1
  HANDBOOK getting-started   Jump to chapter
  HANDBOOK PROGRESS          View progress
  HANDBOOK BOOKMARK          View bookmarks

NAVIGATION:
  HANDBOOK NEXT          Next chapter
  HANDBOOK PREV          Previous chapter
  HANDBOOK BOOKMARK ADD  Bookmark current page

PROGRESS TRACKING:
  • Reading progress saved automatically
  • Bookmark important sections
  • Track completed chapters

See also: DOC, MANUAL, GUIDE
"""

    def _show_volume(self, volume: str) -> str:
        """Show volume table of contents"""

        if volume not in self.volumes:
            return f"\n❌ Unknown volume '{volume}'\n\nAvailable: VOL1, VOL2, VOL3, VOL4\n"

        vol_data = self.volumes[volume]
        output = ["", "═" * 60]
        output.append(f"  {vol_data['title']}")
        output.append("═" * 60)
        output.append("")

        output.append("TABLE OF CONTENTS:")
        output.append("")

        for i, chapter in enumerate(vol_data['chapters'], 1):
            status = "✅" if chapter['name'] in self.progress.get('completed', []) else "  "
            output.append(f"{status} {i}. {chapter['title']}")

        output.append("")
        output.append("─" * 60)
        output.append(f"Usage: HANDBOOK <chapter-name> to read")
        output.append("")

        return "\n".join(output)

    def _show_chapter(self, chapter: str) -> str:
        """Show specific chapter content"""

        # Find chapter in volumes
        chapter_file = None
        for vol_name, vol_data in self.volumes.items():
            for chap in vol_data['chapters']:
                if chapter in chap['name'].lower():
                    chapter_file = chap['name']
                    break
            if chapter_file:
                break

        if not chapter_file:
            return f"\n❌ Chapter '{chapter}' not found\n\nUse 'HANDBOOK VOL1' to see chapters\n"

        # Find and read chapter file
        possible_paths = [
            self.wiki_path / f"{chapter_file}.md",
            self.wiki_path / f"{chapter_file.replace('-', ' ').title().replace(' ', '-')}.md",
            Path("docs") / f"{chapter_file}.md"
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    content = path.read_text()

                    # Update progress
                    self.progress['current_chapter'] = chapter_file
                    if chapter_file not in self.progress.get('completed', []):
                        self.progress['completed'].append(chapter_file)
                    self._save_progress()

                    return content
                except Exception as e:
                    return f"\n❌ Error reading chapter: {e}\n"

        return f"\n❌ Chapter file not found: {chapter_file}\n"

    def _show_progress(self) -> str:
        """Show reading progress"""
        output = ["", "📊 Handbook Reading Progress", "═" * 60, ""]

        total_chapters = sum(len(v['chapters']) for v in self.volumes.values())
        completed = len(self.progress.get('completed', []))
        percent = int((completed / total_chapters) * 100) if total_chapters > 0 else 0

        output.append(f"Progress: {completed}/{total_chapters} chapters ({percent}%)")
        output.append("")

        # Progress bar
        bar_width = 40
        filled = int((completed / total_chapters) * bar_width) if total_chapters > 0 else 0
        bar = "█" * filled + "░" * (bar_width - filled)
        output.append(f"[{bar}]")
        output.append("")

        # Current position
        output.append(f"Current: {self.progress.get('current_chapter', 'N/A')}")
        output.append("")

        # Volume breakdown
        output.append("BY VOLUME:")
        for vol_name, vol_data in self.volumes.items():
            vol_completed = sum(
                1 for ch in vol_data['chapters']
                if ch['name'] in self.progress.get('completed', [])
            )
            vol_total = len(vol_data['chapters'])
            output.append(f"  {vol_name}: {vol_completed}/{vol_total} chapters")

        output.append("")

        # Bookmarks
        if self.progress.get('bookmarks'):
            output.append(f"Bookmarks: {len(self.progress['bookmarks'])}")
            output.append("")

        return "\n".join(output)

    def _show_bookmark(self) -> str:
        """Show bookmarks"""
        bookmarks = self.progress.get('bookmarks', [])

        if not bookmarks:
            return "\n📑 No bookmarks yet\n\nUse 'HANDBOOK BOOKMARK ADD' to add\n"

        output = ["", "📑 Bookmarks", "═" * 60, ""]

        for i, bookmark in enumerate(bookmarks, 1):
            output.append(f"{i}. {bookmark.get('title', 'Untitled')}")
            output.append(f"   Chapter: {bookmark.get('chapter', 'Unknown')}")
            output.append("")

        return "\n".join(output)


def create_handler(viewport=None, logger=None):
    """Factory function to create handler"""
    return HandbookHandler(viewport=viewport, logger=logger)
