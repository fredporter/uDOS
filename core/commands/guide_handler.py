"""
GUIDE Command Handler - v1.0.21
Interactive guide viewer with step-through tutorials

Commands:
  GUIDE LIST [category]
  GUIDE SHOW <guide>
  GUIDE START <guide>
  GUIDE NEXT
  GUIDE PREV
  GUIDE JUMP <step>
  GUIDE COMPLETE [step]
  GUIDE RESET <guide>
  GUIDE PROGRESS

Author: uDOS Development Team
Version: 1.0.21
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json
import re
from datetime import datetime


class GuideHandler:
    """Handler for interactive GUIDE commands"""

    def __init__(self, viewport=None, logger=None):
        """Initialize GuideHandler"""
        self.viewport = viewport
        self.logger = logger
        self.guides_path = Path("knowledge")
        self.progress_file = Path("memory/modules/.guide_progress.json")
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        # Current guide state
        self.current_guide = None
        self.current_step = 0
        self.guide_content = None
        self.guide_steps = []
        self.completed_steps = set()

        # Load saved progress
        self._load_progress()

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route GUIDE commands to appropriate handlers

        Args:
            command: Subcommand (LIST, SHOW, START, etc.)
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
            'SHOW': self._show,
            'VIEW': self._show,
            'START': self._start,
            'BEGIN': self._start,
            'NEXT': self._next,
            'PREV': self._prev,
            'PREVIOUS': self._prev,
            'BACK': self._prev,
            'JUMP': self._jump,
            'GOTO': self._jump,
            'COMPLETE': self._complete,
            'DONE': self._complete,
            'CHECK': self._complete,
            'RESET': self._reset,
            'RESTART': self._reset,
            'PROGRESS': self._progress,
            'STATUS': self._progress,
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown GUIDE command: {command}\n\nType 'GUIDE HELP' for usage."

    def _help(self) -> str:
        """Display GUIDE command help"""
        return """
📚 GUIDE - Interactive Knowledge Viewer

GUIDE SYSTEM:
  • Step-through tutorials with progress tracking
  • Checklist integration (mark steps complete)
  • ASCII diagram display in viewport
  • TZONE location context awareness
  • Resume from last position

COMMANDS:
  GUIDE LIST [category]         List available guides
  GUIDE SHOW <guide>            View guide overview
  GUIDE START <guide>           Begin interactive guide
  GUIDE NEXT                    Next step in current guide
  GUIDE PREV                    Previous step
  GUIDE JUMP <step>             Jump to specific step
  GUIDE COMPLETE [step]         Mark step as complete
  GUIDE RESET <guide>           Reset guide progress
  GUIDE PROGRESS                Show current progress

WORKFLOW:
  1. GUIDE LIST survival        # Find guides in category
  2. GUIDE START bushfire       # Start interactive mode
  3. GUIDE NEXT                 # Step through tutorial
  4. GUIDE COMPLETE             # Mark step done
  5. GUIDE PROGRESS             # Check completion

EXAMPLES:
  GUIDE LIST                    # All categories
  GUIDE LIST survival           # Survival guides only
  GUIDE START water-purification # Begin guide
  GUIDE NEXT                    # Next step
  GUIDE COMPLETE 3              # Mark step 3 done
  GUIDE PROGRESS                # See progress (5/12 steps)

FEATURES:
  ✓ Progress saved between sessions
  ✓ Visual step indicators (█▓▒░)
  ✓ Checklist tracking
  ✓ Diagram rendering
  ✓ Context-aware tips

CATEGORIES:
  • survival     - Emergency preparedness, first aid, shelter
  • skills       - Programming, knot-tying, navigation
  • productivity - Workflows, automation, tools
  • well-being   - Health, fitness, mental wellness
  • environment  - Sustainability, conservation
  • community    - Collaboration, sharing, support
  • tools        - Equipment, maintenance, DIY
  • building     - Construction, repair, making

Type 'GUIDE LIST <category>' to browse guides
"""

    def _list(self, args: List[str]) -> str:
        """List available guides"""
        category = args[0] if args else None

        # Scan knowledge directory for guides
        guides = self._scan_guides(category)

        if not guides:
            if category:
                return f"❌ No guides found in category: {category}\n\nTry 'GUIDE LIST' to see all categories."
            else:
                return "❌ No guides found in knowledge directory."

        # Group by category
        by_category = {}
        for guide in guides:
            cat = guide['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(guide)

        # Build output
        output = [""]
        output.append("📚 Available Guides")
        output.append("═" * 60)

        for cat, cat_guides in sorted(by_category.items()):
            output.append(f"\n📂 {cat.upper()} ({len(cat_guides)} guides)")
            output.append("─" * 60)

            for guide in cat_guides:
                # Progress indicator
                progress = self._get_guide_progress(guide['id'])
                if progress['total'] > 0:
                    pct = int(progress['completed'] / progress['total'] * 100)
                    bar = self._progress_bar(pct, 10)
                    prog_text = f"{bar} {progress['completed']}/{progress['total']} steps"
                else:
                    prog_text = "No steps tracked"

                output.append(f"  • {guide['title']}")
                output.append(f"    {guide['description']}")
                output.append(f"    Progress: {prog_text}")
                output.append("")

        output.append("─" * 60)
        output.append(f"💡 Tip: GUIDE START <guide-name> to begin")
        output.append("")

        return "\n".join(output)

    def _show(self, args: List[str]) -> str:
        """Show guide overview"""
        if not args:
            return "❌ Usage: GUIDE SHOW <guide-name>"

        guide_name = " ".join(args)
        guide_info = self._find_guide(guide_name)

        if not guide_info:
            return f"❌ Guide not found: {guide_name}\n\nTry 'GUIDE LIST' to see available guides."

        # Load and parse guide
        content = self._load_guide_content(guide_info['path'])
        steps = self._extract_steps(content)

        # Build overview
        output = [""]
        output.append(f"📚 {guide_info['title']}")
        output.append("═" * 60)
        output.append(f"Category: {guide_info['category']}")
        output.append(f"Document ID: {guide_info.get('doc_id', 'N/A')}")
        output.append(f"Location: {guide_info.get('location', 'Global')}")
        output.append("")
        output.append(f"📖 Description:")
        output.append(f"   {guide_info['description']}")
        output.append("")

        if steps:
            output.append(f"📋 Steps ({len(steps)} total):")
            output.append("─" * 60)

            progress = self._get_guide_progress(guide_info['id'])
            completed = progress['completed_steps']

            for i, step in enumerate(steps, 1):
                status = "✓" if i in completed else " "
                output.append(f"  [{status}] Step {i}: {step['title']}")

            output.append("")
            output.append(f"Progress: {progress['completed']}/{len(steps)} steps complete")

        # v1.1.14: Show related checklists if any
        related_checklists = self._find_related_checklists(guide_info['id'])
        if related_checklists:
            output.append("")
            output.append("📋 Related Checklists:")
            output.append("─" * 60)
            for checklist in related_checklists:
                output.append(f"  • {checklist}")
            output.append("")
            output.append("💡 Tip: CHECKLIST LOAD <name> to open a checklist")

        output.append("")
        output.append(f"💡 Tip: GUIDE START {guide_info['id']} to begin")
        output.append("")

        return "\n".join(output)

    def _start(self, args: List[str]) -> str:
        """Start interactive guide"""
        if not args:
            return "❌ Usage: GUIDE START <guide-name>"

        guide_name = " ".join(args)
        guide_info = self._find_guide(guide_name)

        if not guide_info:
            return f"❌ Guide not found: {guide_name}\n\nTry 'GUIDE LIST' to see available guides."

        # Load guide content
        content = self._load_guide_content(guide_info['path'])
        steps = self._extract_steps(content)

        if not steps:
            return f"❌ Guide has no interactive steps: {guide_name}"

        # Set current guide
        self.current_guide = guide_info['id']
        self.guide_content = content
        self.guide_steps = steps

        # Resume from last position or start fresh
        progress = self._get_guide_progress(guide_info['id'])
        self.completed_steps = progress['completed_steps']

        # Find first incomplete step
        self.current_step = 1
        for i in range(1, len(steps) + 1):
            if i not in self.completed_steps:
                self.current_step = i
                break

        self._save_progress()

        # Show first step
        output = [""]
        output.append(f"📚 Starting Guide: {guide_info['title']}")
        output.append("═" * 60)
        output.append(f"Total Steps: {len(steps)}")
        output.append(f"Completed: {len(self.completed_steps)}/{len(steps)}")
        output.append("")
        output.append(self._render_current_step())
        output.append("")
        output.append("💡 Commands: GUIDE NEXT | GUIDE PREV | GUIDE COMPLETE | GUIDE PROGRESS")
        output.append("")

        return "\n".join(output)

    def _next(self, args: List[str]) -> str:
        """Move to next step"""
        if not self.current_guide:
            return "❌ No active guide. Use 'GUIDE START <guide-name>' first."

        if self.current_step >= len(self.guide_steps):
            return "✓ You're at the last step! Use 'GUIDE PROGRESS' to see completion."

        self.current_step += 1
        self._save_progress()

        return self._render_current_step()

    def _prev(self, args: List[str]) -> str:
        """Move to previous step"""
        if not self.current_guide:
            return "❌ No active guide. Use 'GUIDE START <guide-name>' first."

        if self.current_step <= 1:
            return "❌ Already at first step."

        self.current_step -= 1
        self._save_progress()

        return self._render_current_step()

    def _jump(self, args: List[str]) -> str:
        """Jump to specific step"""
        if not self.current_guide:
            return "❌ No active guide. Use 'GUIDE START <guide-name>' first."

        if not args:
            return "❌ Usage: GUIDE JUMP <step-number>"

        try:
            step_num = int(args[0])
        except ValueError:
            return f"❌ Invalid step number: {args[0]}"

        if step_num < 1 or step_num > len(self.guide_steps):
            return f"❌ Step {step_num} out of range (1-{len(self.guide_steps)})"

        self.current_step = step_num
        self._save_progress()

        return self._render_current_step()

    def _complete(self, args: List[str]) -> str:
        """Mark step as complete"""
        if not self.current_guide:
            return "❌ No active guide. Use 'GUIDE START <guide-name>' first."

        # Determine which step to mark complete
        if args:
            try:
                step_num = int(args[0])
            except ValueError:
                return f"❌ Invalid step number: {args[0]}"
        else:
            step_num = self.current_step

        if step_num < 1 or step_num > len(self.guide_steps):
            return f"❌ Step {step_num} out of range (1-{len(self.guide_steps)})"

        # Mark complete
        self.completed_steps.add(step_num)
        self._save_progress()

        # Check if all steps complete
        if len(self.completed_steps) == len(self.guide_steps):
            output = [""]
            output.append("🎉 Congratulations! Guide Complete!")
            output.append("═" * 60)
            output.append(f"You've completed all {len(self.guide_steps)} steps!")
            output.append("")
            output.append("💡 Tip: Use 'GUIDE RESET' to start over, or 'GUIDE LIST' for more guides.")
            output.append("")
            return "\n".join(output)
        else:
            completed = len(self.completed_steps)
            total = len(self.guide_steps)
            pct = int(completed / total * 100)
            bar = self._progress_bar(pct, 20)

            return f"✓ Step {step_num} marked complete!\n\nProgress: {bar} {completed}/{total} ({pct}%)\n"

    def _reset(self, args: List[str]) -> str:
        """Reset guide progress"""
        if args:
            guide_name = " ".join(args)
            guide_info = self._find_guide(guide_name)
            if not guide_info:
                return f"❌ Guide not found: {guide_name}"
            guide_id = guide_info['id']
        elif self.current_guide:
            guide_id = self.current_guide
        else:
            return "❌ Usage: GUIDE RESET <guide-name>"

        # Reset progress
        if guide_id in self.progress_data:
            del self.progress_data[guide_id]
            self._save_progress()

        # Clear current if it's the active guide
        if guide_id == self.current_guide:
            self.completed_steps = set()
            self.current_step = 1

        return f"✓ Progress reset for guide: {guide_id}\n"

    def _progress(self, args: List[str]) -> str:
        """Show current guide progress"""
        if not self.current_guide:
            return "❌ No active guide. Use 'GUIDE START <guide-name>' first."

        total = len(self.guide_steps)
        completed = len(self.completed_steps)
        pct = int(completed / total * 100) if total > 0 else 0

        output = [""]
        output.append(f"📊 Guide Progress: {self.current_guide}")
        output.append("═" * 60)
        output.append(f"Current Step: {self.current_step}/{total}")
        output.append(f"Completed: {completed}/{total} steps ({pct}%)")
        output.append("")
        output.append(self._progress_bar(pct, 30))
        output.append("")

        # Show step checklist
        output.append("Checklist:")
        output.append("─" * 60)
        for i, step in enumerate(self.guide_steps, 1):
            status = "✓" if i in self.completed_steps else " "
            current = "→" if i == self.current_step else " "
            output.append(f"{current} [{status}] Step {i}: {step['title']}")

        output.append("")
        return "\n".join(output)

    def _render_current_step(self) -> str:
        """Render the current step content"""
        if not self.current_guide or not self.guide_steps:
            return "❌ No active guide."

        step = self.guide_steps[self.current_step - 1]
        total = len(self.guide_steps)
        completed = len(self.completed_steps)
        is_complete = self.current_step in self.completed_steps

        output = [""]
        output.append(f"Step {self.current_step}/{total}: {step['title']}")
        output.append("═" * 60)

        if is_complete:
            output.append("✓ COMPLETED")
            output.append("")

        # Render step content
        output.append(step['content'])
        output.append("")
        output.append("─" * 60)

        # Progress bar
        pct = int(completed / total * 100)
        bar = self._progress_bar(pct, 30)
        output.append(f"Progress: {bar} {completed}/{total}")
        output.append("")

        return "\n".join(output)

    def _scan_guides(self, category: Optional[str] = None) -> List[Dict]:
        """Scan knowledge directory for guides"""
        guides = []

        # Define guide categories
        categories = ['survival', 'skills', 'productivity', 'well-being',
                     'environment', 'community', 'tools', 'building']

        if category:
            categories = [category] if category in categories else []

        for cat in categories:
            cat_path = self.guides_path / cat
            if not cat_path.exists():
                continue

            # Scan markdown files recursively
            for md_file in cat_path.rglob("*.md"):
                if md_file.name.startswith('.'):
                    continue

                # Extract guide info from file
                guide_info = self._parse_guide_metadata(md_file, cat)
                if guide_info:
                    guides.append(guide_info)

        return guides

    def _parse_guide_metadata(self, file_path: Path, category: str) -> Optional[Dict]:
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

            # Extract location and doc ID if present
            location_match = re.search(r'\*\*Location:\*\*\s+(.+)', content)
            doc_id_match = re.search(r'\*\*Document ID:\*\*\s+(.+)', content)

            return {
                'id': file_path.stem,
                'title': title,
                'description': description,
                'category': category,
                'path': file_path,
                'location': location_match.group(1) if location_match else None,
                'doc_id': doc_id_match.group(1) if doc_id_match else None,
            }
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing guide {file_path}: {e}")
            return None

    def _find_guide(self, guide_name: str) -> Optional[Dict]:
        """Find guide by name or ID"""
        guides = self._scan_guides()

        # Try exact ID match first
        for guide in guides:
            if guide['id'] == guide_name:
                return guide

        # Try fuzzy title match
        guide_lower = guide_name.lower()
        for guide in guides:
            if guide_lower in guide['title'].lower():
                return guide
            if guide_lower in guide['id'].lower():
                return guide

        return None

    def _load_guide_content(self, file_path: Path) -> str:
        """Load guide content from file"""
        try:
            return file_path.read_text()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading guide {file_path}: {e}")
            return ""

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

    def _get_guide_progress(self, guide_id: str) -> Dict:
        """Get progress for a specific guide"""
        if guide_id in self.progress_data:
            data = self.progress_data[guide_id]
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

    def _progress_bar(self, percent: int, width: int = 20) -> str:
        """Generate ASCII progress bar"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percent}%"

    def _load_progress(self):
        """Load saved progress from file"""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r') as f:
                    self.progress_data = json.load(f)
            else:
                self.progress_data = {}
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading guide progress: {e}")
            self.progress_data = {}

    def _save_progress(self):
        """Save progress to file"""
        try:
            # Update current guide progress
            if self.current_guide:
                self.progress_data[self.current_guide] = {
                    'completed': len(self.completed_steps),
                    'total': len(self.guide_steps),
                    'completed_steps': list(self.completed_steps),
                    'last_step': self.current_step,
                    'last_updated': datetime.now().isoformat()
                }

            # Write to file
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error saving guide progress: {e}")

    def _find_related_checklists(self, guide_id: str) -> List[str]:
        """
        Find checklists related to this guide.
        
        v1.1.14: Checks checklist JSON files for related_guides field.
        
        Args:
            guide_id: Guide identifier (e.g., 'water/purification')
            
        Returns:
            List of checklist titles
        """
        checklists_dir = Path("knowledge/checklists")
        if not checklists_dir.exists():
            return []
        
        related = []
        
        # Scan all checklist files
        for checklist_file in checklists_dir.rglob("*.json"):
            try:
                with open(checklist_file, 'r') as f:
                    data = json.load(f)
                    
                # Check if this guide is in the checklist's related_guides
                related_guides = data.get('related_guides', [])
                for guide_ref in related_guides:
                    # Match on partial path (e.g., 'water' matches 'water/purification')
                    if guide_id.startswith(guide_ref) or guide_ref in guide_id:
                        related.append(data.get('title', checklist_file.stem))
                        break
                        
            except (json.JSONDecodeError, IOError):
                continue
        
        return related
                self.progress_data[self.current_guide] = {
                    'completed': len(self.completed_steps),
                    'total': len(self.guide_steps),
                    'completed_steps': list(self.completed_steps),
                    'last_step': self.current_step,
                    'last_accessed': datetime.now().isoformat(),
                }

            # Write to file
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress_data, f, indent=2)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error saving guide progress: {e}")
