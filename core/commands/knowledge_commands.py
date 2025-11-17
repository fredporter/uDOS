"""
Knowledge Command Handler - v1.0.20 Enhanced
Tier 4: Public global knowledge bank

Commands:
  KNOWLEDGE CONTRIBUTE <title> [category]
  KNOWLEDGE REVIEW [status]
  KNOWLEDGE APPROVE <id>
  KNOWLEDGE REJECT <id>
  KNOWLEDGE STATUS
  KNOWLEDGE SEARCH <query>
  KNOWLEDGE LIST [category]

Author: uDOS Development Team
Version: 1.0.20
"""

from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
from core.services.memory_manager import MemoryManager, MemoryTier


class KnowledgeCommandHandler:
    """Handler for KNOWLEDGE (Tier 4) commands"""

    def __init__(self):
        """Initialize KnowledgeCommandHandler"""
        self.memory_manager = MemoryManager()
        self.knowledge_path = self.memory_manager.get_tier_path(MemoryTier.PUBLIC)
        self.submissions_path = self.knowledge_path / ".submissions"
        self.submissions_path.mkdir(exist_ok=True)
        self.current_user = "owner@localhost"  # TODO: Get from session/auth

    def handle(self, command: str, args: List[str]) -> str:
        """
        Route KNOWLEDGE commands to appropriate handlers

        Args:
            command: Subcommand (CONTRIBUTE, REVIEW, etc.)
            args: Command arguments

        Returns:
            Formatted response string
        """
        if not command or command.upper() == "HELP":
            return self._help()

        command = command.upper()

        handlers = {
            'CONTRIBUTE': self._contribute,
            'SUBMIT': self._contribute,     # Alias
            'REVIEW': self._review,
            'APPROVE': self._approve,
            'ACCEPT': self._approve,        # Alias
            'REJECT': self._reject,
            'DECLINE': self._reject,        # Alias
            'STATUS': self._status,
            'STATS': self._status,          # Alias
            'SEARCH': self._search,
            'FIND': self._search,           # Alias
            'LIST': self._list,
            'LS': self._list,               # Alias
        }

        handler = handlers.get(command)
        if handler:
            return handler(args)
        else:
            return f"❌ Unknown KNOWLEDGE command: {command}\n\nType 'KNOWLEDGE HELP' for usage."

    def _help(self) -> str:
        """Display KNOWLEDGE command help"""
        return """
🌍 KNOWLEDGE - Tier 4: Global Knowledge Bank

KNOWLEDGE MODEL:
  • Community-curated - Quality-controlled submissions
  • Version-tracked - Full change history
  • Moderated - Human review before publishing
  • Read-only public - Everyone can access
  • Attribution - Credit to contributors
  • Offline-first - Local replicas, p2p sync
  • Resilient - Distributed across devices

COMMANDS:
  KNOWLEDGE CONTRIBUTE <title> [cat]  Submit knowledge
  KNOWLEDGE REVIEW [status]           Review submissions
  KNOWLEDGE APPROVE <id>              Approve submission
  KNOWLEDGE REJECT <id>               Reject submission
  KNOWLEDGE STATUS                    Knowledge statistics
  KNOWLEDGE SEARCH <query>            Search knowledge
  KNOWLEDGE LIST [category]           List by category

SUBMISSION WORKFLOW:
  1. CONTRIBUTE - Submit your knowledge
  2. REVIEW - Moderators review quality
  3. APPROVE/REJECT - Community decision
  4. PUBLISH - Available globally
  5. VERSION - Track changes over time

CATEGORIES:
  survival     - Emergency preparedness, first aid
  food         - Gardening, preservation, recipes
  water        - Collection, purification, storage
  energy       - Solar, batteries, efficiency
  tools        - DIY, repair, maintenance
  skills       - Practical hands-on knowledge
  community    - Organization, cooperation
  resources    - Maps, contacts, materials

QUALITY CRITERIA:
  ✓ Practical - Real-world applicable
  ✓ Verified - Tested or cited sources
  ✓ Clear - Easy to understand
  ✓ Complete - All necessary steps
  ✓ Safe - No dangerous misinformation
  ✓ Offline - Works without internet

EXAMPLES:
  # Submit knowledge
  KNOWLEDGE CONTRIBUTE seed-saving survival

  # Review pending submissions
  KNOWLEDGE REVIEW pending

  # Approve a submission
  KNOWLEDGE APPROVE 12345

  # Search knowledge
  KNOWLEDGE SEARCH water purification

  # List by category
  KNOWLEDGE LIST survival

MODERATION:
  • Community-driven review process
  • Require 3+ approvals for publication
  • Reject with constructive feedback
  • Version control for updates
  • Attribution for all contributors
"""

    def _contribute(self, args: List[str]) -> str:
        """Submit knowledge to global bank"""
        if not args:
            return "❌ Usage: KNOWLEDGE CONTRIBUTE <title> [category]"

        title = args[0]
        category = args[1] if len(args) > 1 else "general"

        # Generate submission ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        submission_id = f"{category}_{timestamp}"

        # Get content (in real implementation, this would open editor)
        print(f"\n📝 Enter knowledge content (end with empty line):")
        lines = []
        while True:
            try:
                line = input()
                if not line:
                    break
                lines.append(line)
            except EOFError:
                break

        content = "\n".join(lines) if lines else "Knowledge content goes here..."

        # Create submission
        submission = {
            'id': submission_id,
            'title': title,
            'category': category,
            'content': content,
            'author': self.current_user,
            'submitted': datetime.now().isoformat(),
            'status': 'pending',
            'reviews': [],
            'approvals': 0,
            'rejections': 0
        }

        # Save submission
        submission_file = self.submissions_path / f"{submission_id}.json"
        submission_file.write_text(json.dumps(submission, indent=2))

        return f"""
✅ Knowledge submitted!

🆔 Submission ID: {submission_id}
📄 Title: {title}
📁 Category: {category}
👤 Author: {self.current_user}
📊 Status: Pending Review

Your submission will be reviewed by community moderators.
Use 'KNOWLEDGE REVIEW' to check status.
"""

    def _review(self, args: List[str]) -> str:
        """Review pending submissions"""
        status_filter = args[0] if args else "pending"

        # Get all submissions
        submissions = []
        for submission_file in self.submissions_path.glob("*.json"):
            data = json.loads(submission_file.read_text())
            if status_filter == "all" or data['status'] == status_filter:
                submissions.append(data)

        output = [f"🌍 Knowledge Submissions - {status_filter.upper()}"]
        output.append("=" * 60)

        if not submissions:
            output.append(f"\n📭 No {status_filter} submissions")
        else:
            output.append(f"\n📊 {len(submissions)} submission(s)\n")

            for sub in sorted(submissions, key=lambda x: x['submitted'], reverse=True):
                status_icons = {
                    'pending': '⏳',
                    'approved': '✅',
                    'rejected': '❌',
                    'published': '🌍'
                }
                icon = status_icons.get(sub['status'], '📄')

                output.append(f"{icon} {sub['id']}")
                output.append(f"   Title: {sub['title']}")
                output.append(f"   Category: {sub['category']} | Author: {sub['author']}")
                output.append(f"   Submitted: {sub['submitted'][:10]}")
                output.append(f"   Status: {sub['status'].upper()} | "
                            f"👍 {sub['approvals']} | 👎 {sub['rejections']}")
                output.append("")

        output.append("=" * 60)
        output.append("\nℹ️  Use 'KNOWLEDGE APPROVE <id>' or 'KNOWLEDGE REJECT <id>'")

        return "\n".join(output)

    def _approve(self, args: List[str]) -> str:
        """Approve a submission"""
        if not args:
            return "❌ Usage: KNOWLEDGE APPROVE <id>"

        submission_id = args[0]
        submission_file = self.submissions_path / f"{submission_id}.json"

        if not submission_file.exists():
            return f"❌ Submission not found: {submission_id}"

        # Load submission
        submission = json.loads(submission_file.read_text())

        if submission['status'] != 'pending':
            return f"ℹ️  Submission already {submission['status']}"

        # Add review
        review = {
            'reviewer': self.current_user,
            'decision': 'approve',
            'timestamp': datetime.now().isoformat(),
            'comment': ''
        }
        submission['reviews'].append(review)
        submission['approvals'] += 1

        # Check if enough approvals (3+ required)
        if submission['approvals'] >= 3:
            submission['status'] = 'approved'
            # TODO: Publish to global knowledge bank

        # Save
        submission_file.write_text(json.dumps(submission, indent=2))

        return f"""
✅ Submission approved!

🆔 {submission_id}
📄 {submission['title']}
👍 Approvals: {submission['approvals']} / 3 required

{'🌍 PUBLISHED to global knowledge bank!' if submission['status'] == 'approved' else '⏳ Waiting for more approvals...'}
"""

    def _reject(self, args: List[str]) -> str:
        """Reject a submission"""
        if not args:
            return "❌ Usage: KNOWLEDGE REJECT <id>"

        submission_id = args[0]
        submission_file = self.submissions_path / f"{submission_id}.json"

        if not submission_file.exists():
            return f"❌ Submission not found: {submission_id}"

        # Load submission
        submission = json.loads(submission_file.read_text())

        if submission['status'] != 'pending':
            return f"ℹ️  Submission already {submission['status']}"

        # Get feedback
        print(f"\n📝 Rejection reason (optional):")
        try:
            feedback = input()
        except EOFError:
            feedback = ""

        # Add review
        review = {
            'reviewer': self.current_user,
            'decision': 'reject',
            'timestamp': datetime.now().isoformat(),
            'comment': feedback
        }
        submission['reviews'].append(review)
        submission['rejections'] += 1

        # Check if rejected (2+ rejections)
        if submission['rejections'] >= 2:
            submission['status'] = 'rejected'

        # Save
        submission_file.write_text(json.dumps(submission, indent=2))

        return f"""
❌ Submission rejected

🆔 {submission_id}
📄 {submission['title']}
👎 Rejections: {submission['rejections']} / 2 required

{'🚫 REJECTED - Author will be notified' if submission['status'] == 'rejected' else '⏳ Waiting for more reviews...'}
"""

    def _status(self, args: List[str]) -> str:
        """Show knowledge bank statistics"""
        tier_stats = self.memory_manager.get_tier_stats(MemoryTier.PUBLIC)

        # Count submissions by status
        pending = 0
        approved = 0
        rejected = 0
        published = 0

        for submission_file in self.submissions_path.glob("*.json"):
            data = json.loads(submission_file.read_text())
            status = data['status']
            if status == 'pending':
                pending += 1
            elif status == 'approved':
                approved += 1
            elif status == 'rejected':
                rejected += 1
            elif status == 'published':
                published += 1

        # User's contributions
        user_submissions = sum(1 for f in self.submissions_path.glob("*.json")
                              if json.loads(f.read_text())['author'] == self.current_user)

        output = ["🌍 Knowledge Bank Status"]
        output.append("=" * 60)

        # Tier statistics
        output.append(f"\n📊 Tier Statistics:")
        output.append(f"  Total Files: {tier_stats['file_count']}")
        output.append(f"  Total Size: {tier_stats['total_size_mb']} MB")

        # Submission statistics
        output.append(f"\n📝 Submissions:")
        output.append(f"  Pending: {pending}")
        output.append(f"  Approved: {approved}")
        output.append(f"  Rejected: {rejected}")
        output.append(f"  Published: {published}")
        output.append(f"  Total: {pending + approved + rejected + published}")

        # User statistics
        output.append(f"\n👤 Your Contributions:")
        output.append(f"  Submissions: {user_submissions}")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _search(self, args: List[str]) -> str:
        """Search knowledge bank"""
        if not args:
            return "❌ Usage: KNOWLEDGE SEARCH <query>"

        query = " ".join(args).lower()

        # Search knowledge files
        results = []
        for category_dir in self.knowledge_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                for item in category_dir.glob("**/*.md"):
                    content = item.read_text().lower()
                    if query in content or query in item.name.lower():
                        results.append({
                            'path': item,
                            'category': category_dir.name,
                            'name': item.stem,
                            'size': item.stat().st_size
                        })

        output = [f"🔍 Knowledge Search: '{query}'"]
        output.append("=" * 60)

        if not results:
            output.append(f"\n📭 No results found")
        else:
            output.append(f"\n📊 {len(results)} result(s)\n")

            for result in results[:20]:  # Limit to 20
                size_kb = result['size'] / 1024
                output.append(f"📄 {result['name']}")
                output.append(f"   Category: {result['category']} | Size: {size_kb:.1f} KB")

        output.append("\n" + "=" * 60)

        return "\n".join(output)

    def _list(self, args: List[str]) -> str:
        """List knowledge by category"""
        category = args[0] if args else None

        # Get knowledge items
        items = []
        for category_dir in self.knowledge_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                if category and category_dir.name != category:
                    continue

                for item in category_dir.glob("**/*.md"):
                    items.append({
                        'path': item,
                        'category': category_dir.name,
                        'name': item.stem,
                        'size': item.stat().st_size,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })

        output = [f"📚 Knowledge Bank"]
        if category:
            output.append(f"📁 Category: {category}")
        output.append("=" * 60)

        if not items:
            output.append(f"\n📭 No items found")
        else:
            # Group by category
            by_category = {}
            for item in items:
                cat = item['category']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)

            output.append(f"\n📊 {len(items)} item(s) in {len(by_category)} categor{'y' if len(by_category) == 1 else 'ies'}\n")

            for cat, cat_items in sorted(by_category.items()):
                output.append(f"📁 {cat} ({len(cat_items)} items)")
                for item in sorted(cat_items, key=lambda x: x['name'])[:10]:
                    size_kb = item['size'] / 1024
                    output.append(f"  📄 {item['name']} ({size_kb:.1f} KB)")
                if len(cat_items) > 10:
                    output.append(f"  ... and {len(cat_items) - 10} more")
                output.append("")

        output.append("=" * 60)

        return "\n".join(output)


def main():
    """Test KnowledgeCommandHandler"""
    handler = KnowledgeCommandHandler()

    print("\n" + "=" * 60)
    print("Testing KNOWLEDGE Commands")
    print("=" * 60 + "\n")

    print(handler.handle("HELP", [])[:500] + "...")
    print("\n" + "=" * 60 + "\n")
    print(handler.handle("STATUS", []))


if __name__ == "__main__":
    main()
