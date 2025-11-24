"""
uDOS v1.0.8 - Data Bank Command Handler

Manages local data bank for offline-first information storage and retrieval.
Provides search, indexing, and content management for markdown data files.

Commands:
- BANK SEARCH <query> - Search data bank
- BANK LIST [category] - List data bank items
- BANK SHOW <item> - Display data bank content
- BANK INDEX - Reindex data bank
- BANK STATS - Show data bank statistics
- BANK CATEGORIES - List all categories

Version: 1.0.8
"""

from .base_handler import BaseCommandHandler
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))


class BankCommandHandler(BaseCommandHandler):
    """Data bank management commands."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bank_manager = None

    @property
    def bank_manager(self):
        """Lazy load bank manager."""
        if self._bank_manager is None:
            from core.knowledge import get_knowledge_manager
            self._bank_manager = get_knowledge_manager()
        return self._bank_manager

    def handle(self, command, params, grid):
        """
        Handle KNOWLEDGE commands.

        Args:
            command: The subcommand (SEARCH, LIST, SHOW, etc.)
            params: Command parameters
            grid: Grid system for panel management
        """
        if command == "SEARCH":
            return self._handle_search(params, grid)
        elif command == "LIST":
            return self._handle_list(params, grid)
        elif command == "SHOW":
            return self._handle_show(params, grid)
        elif command == "INDEX":
            return self._handle_index(params)
        elif command == "STATS":
            return self._handle_stats()
        elif command == "CATEGORIES":
            return self._handle_categories()
        elif command == "HELP":
            return self._handle_help()
        else:
            return self.get_message("ERROR_UNKNOWN_KNOWLEDGE_COMMAND", command=command)

    def _handle_search(self, params, grid):
        """Search knowledge base."""
        if not params:
            return """❌ Usage: KNOWLEDGE SEARCH <query> [category] [limit]

Examples:
  BANK SEARCH "OK command"
  KNOWLEDGE SEARCH mapping commands 5
  KNOWLEDGE SEARCH python concepts"""

        query = params[0]
        category = params[1] if len(params) > 1 and not params[1].isdigit() else None
        limit = 10

        # Parse limit if provided
        for param in params[1:]:
            if param.isdigit():
                limit = int(param)
                break

        # Perform search
        results = self.bank_manager.search(query, limit=limit, category=category)

        if not results:
            category_text = f" in category '{category}'" if category else ""
            return f"🔍 No results found for '{query}'{category_text}"

        # Format results
        output = [f"🔍 Knowledge Search: '{query}' ({len(results)} results)\n"]

        for i, result in enumerate(results, 1):
            score_indicator = "🎯" if result['score'] < -5 else "📄"
            output.append(f"{score_indicator} {i}. **{result['title']}** ({result['category']})")
            output.append(f"   📝 {result['word_count']} words")

            # Show snippet
            snippet = result['snippet'].strip()
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            output.append(f"   💡 {snippet}")

            # Show tags if available
            if result['tags']:
                tags = " ".join([f"#{tag}" for tag in result['tags'][:5]])
                output.append(f"   🏷️  {tags}")

            output.append("")

        # Add search tips
        output.append("💡 **Tips:**")
        output.append("   • Use BANK SHOW <title> to view full content")
        output.append("   • Add category filter: BANK SEARCH <query> <category>")
        output.append("   • Use quotes for exact phrases")

        return "\n".join(output)

    def _handle_list(self, params, grid):
        """List knowledge items."""
        category = params[0] if params else None

        if category:
            # List items in specific category
            items = self.bank_manager.get_by_category(category)
            if not items:
                return f"📂 No items found in category '{category}'"

            output = [f"📂 Knowledge Items in '{category}' ({len(items)} items)\n"]

            for item in items:
                output.append(f"📄 **{item['title']}**")
                output.append(f"   📝 {item['word_count']} words")

                if item['tags']:
                    tags = " ".join([f"#{tag}" for tag in item['tags'][:5]])
                    output.append(f"   🏷️  {tags}")

                output.append("")
        else:
            # List all categories
            categories = self.bank_manager.get_categories()
            if not categories:
                return "📂 No knowledge categories found. Use KNOWLEDGE INDEX to scan for files."

            output = ["📂 Knowledge Categories\n"]

            for cat in categories:
                output.append(f"📁 **{cat['category']}**")
                output.append(f"   📄 {cat['count']} items")
                output.append(f"   📝 {cat['total_words']} total words")
                output.append("")

            output.append("💡 Use BANK LIST <category> to see items in a category")

        return "\n".join(output)

    def _handle_show(self, params, grid):
        """Show full content of a knowledge item."""
        if not params:
            return """❌ Usage: KNOWLEDGE SHOW <title|file_path>

Examples:
  BANK SHOW "OK Command Reference"
  BANK SHOW commands/OK.md"""

        identifier = params[0]

        # Try to find by title first
        results = self.bank_manager.search(identifier, limit=5)

        # Look for exact title match
        exact_match = None
        for result in results:
            if result['title'].lower() == identifier.lower():
                exact_match = result
                break

        # If no exact match, try first result or file path
        if exact_match:
            content = self.bank_manager.get_content(exact_match['file_path'])
            title = exact_match['title']
            file_path = exact_match['file_path']
        else:
            # Try as file path
            if identifier.endswith('.md'):
                content = self.bank_manager.get_content(identifier)
                title = identifier
                file_path = identifier
            elif results:
                # Use first search result
                content = self.bank_manager.get_content(results[0]['file_path'])
                title = results[0]['title']
                file_path = results[0]['file_path']
            else:
                content = None
                title = identifier
                file_path = None

        if not content:
            return f"❌ Knowledge item '{identifier}' not found"

        # Format content for display
        output = [f"📖 **{title}**"]
        if file_path:
            output.append(f"📁 {file_path}")
        output.append("─" * 60)
        output.append("")
        output.append(content)

        # Create panel if grid available
        if grid:
            panel_name = f"knowledge_{title.lower().replace(' ', '_')}"
            grid.create_panel(panel_name, "\n".join(output), 0, 0, 80, 30)
            return f"📖 Knowledge content displayed in panel '{panel_name}'"

        return "\n".join(output)

    def _handle_index(self, params):
        """Reindex knowledge base."""
        force_reindex = "--force" in params or "-f" in params

        output = ["🔄 Indexing knowledge base..."]

        stats = self.bank_manager.index_knowledge_base(force_reindex=force_reindex)

        output.append("")
        output.append("📊 **Indexing Results:**")
        output.append(f"   📁 Total files scanned: {stats['total_files']}")
        output.append(f"   ✅ New files indexed: {stats['new_files']}")
        output.append(f"   🔄 Files updated: {stats['updated_files']}")
        output.append(f"   🗑️  Files removed: {stats['deleted_files']}")
        output.append(f"   ❌ Errors encountered: {stats['errors']}")

        if stats['total_files'] == 0:
            output.append("")
            output.append("💡 **Tip:** Add .md files to the /knowledge folder to build your knowledge base")

        return "\n".join(output)

    def _handle_stats(self):
        """Show knowledge base statistics."""
        stats = self.bank_manager.get_statistics()

        output = ["📊 **Knowledge Base Statistics**\n"]

        output.append(f"📄 **Total Items:** {stats['total_items']}")
        output.append(f"📝 **Total Words:** {stats['total_words']:,}")
        output.append(f"📂 **Categories:** {stats['total_categories']}")

        if stats['last_updated']:
            output.append(f"🕒 **Last Updated:** {stats['last_updated']}")

        # Database info
        db_size_mb = stats['database_size'] / (1024 * 1024)
        output.append(f"💾 **Database Size:** {db_size_mb:.2f} MB")

        # Category breakdown
        categories = self.bank_manager.get_categories()
        if categories:
            output.append("\n📂 **Category Breakdown:**")
            for cat in categories:
                percentage = (cat['total_words'] / stats['total_words'] * 100) if stats['total_words'] > 0 else 0
                output.append(f"   {cat['category']}: {cat['count']} items ({percentage:.1f}%)")

        return "\n".join(output)

    def _handle_categories(self):
        """List all categories with details."""
        categories = self.bank_manager.get_categories()

        if not categories:
            return "📂 No categories found. Use KNOWLEDGE INDEX to scan for files."

        output = ["📂 **Knowledge Categories**\n"]

        for cat in categories:
            output.append(f"📁 **{cat['category']}**")
            output.append(f"   📄 {cat['count']} items")
            output.append(f"   📝 {cat['total_words']:,} words")

            # Get sample items
            items = self.bank_manager.get_by_category(cat['category'])
            if items:
                sample_titles = [item['title'] for item in items[:3]]
                output.append(f"   📋 Examples: {', '.join(sample_titles)}")
                if len(items) > 3:
                    output.append(f"   📋 ... and {len(items) - 3} more")

            output.append("")

        output.append("💡 Use KNOWLEDGE LIST <category> to see all items in a category")

        return "\n".join(output)

    def _handle_help(self):
        """Show KNOWLEDGE command help."""
        return """📚 **KNOWLEDGE Command Reference**

**Search & Discovery:**
  KNOWLEDGE SEARCH <query> [category] [limit]  - Search knowledge base
  KNOWLEDGE LIST [category]                     - List knowledge items
  KNOWLEDGE CATEGORIES                          - Show all categories
  KNOWLEDGE STATS                              - Show knowledge statistics

**Content Management:**
  KNOWLEDGE SHOW <title|path>                  - Display full content
  KNOWLEDGE INDEX [--force]                    - Reindex knowledge base

**Examples:**
  KNOWLEDGE SEARCH "command architecture"      - Search for content
  KNOWLEDGE LIST commands                      - List command docs
  KNOWLEDGE SHOW "ASK Command Reference"       - View full document
  KNOWLEDGE INDEX --force                      - Force reindex all files

**Tips:**
• Knowledge files are stored in /knowledge folder
• Files are automatically indexed when changed
• Use categories to organize content (folders become categories)
• Search supports full-text search with ranking
• Content is displayed in panels when possible

**Categories:**
• commands/ - Command reference documentation
• concepts/ - System architecture and design concepts
• faq/ - Frequently asked questions
• maps/ - Geographical and navigation data
• personal/ - User-specific knowledge (git-ignored)"""

    def get_message(self, template_key, **kwargs):
        """Get formatted message from template."""
        templates = {
            'ERROR_UNKNOWN_KNOWLEDGE_COMMAND': "❌ Unknown KNOWLEDGE command: {command}\n\nUse KNOWLEDGE HELP for available commands.",
        }
        return templates.get(template_key, f"Unknown template: {template_key}").format(**kwargs)
