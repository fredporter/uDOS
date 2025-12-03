"""
uDOS v1.0.12 - Help Manager Service

Manages interactive help content, search functionality, and tutorials.
Provides enhanced help experience with examples, search, and categorization.

Features:
- Help content search with fuzzy matching
- Category filtering
- Command usage tracking integration
- Template-based help rendering
- Interactive tutorials
- Example generation

Version: 1.0.12
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from core.utils.pager import page_output


class HelpManager:
    """Manages help content and interactive help features."""

    def __init__(self, commands_file: str = "core/data/commands.json"):
        """
        Initialize Help Manager.

        Args:
            commands_file: Path to commands JSON file
        """
        self.commands_file = commands_file
        self.commands_data = self._load_commands()
        self.categories = self._categorize_commands()
        self.usage_tracker = None  # Will be injected if available

    def _load_commands(self) -> List[Dict]:
        """Load commands from JSON file, excluding deferred commands."""
        try:
            with open(self.commands_file, 'r') as f:
                data = json.load(f)
                all_commands = data.get('COMMANDS', [])
                # Filter out deferred commands (v1.1+)
                active_commands = [
                    cmd for cmd in all_commands
                    if not cmd.get('DEFERRED')
                ]
                return active_commands
        except Exception as e:
            print(f"Error loading commands: {e}")
            return []

    def _categorize_commands(self) -> Dict[str, List[str]]:
        """Auto-categorize active commands (excludes deferred and extensions)."""
        categories = {
            "📊 System & Info": [],
            "🔧 System Control": [],
            "📝 File Operations": [],
            "💾 Knowledge & Memory": [],
            "🎨 Display & Themes": [],
            "🔍 Search & Navigation": [],
            "⚙️  Configuration": [],
            "🎮 Automation & Missions": [],
            "⚡ Other": []
        }

        for cmd_data in self.commands_data:
            cmd_name = cmd_data.get('NAME', '')
            ucode = cmd_data.get('UCODE_TEMPLATE', '')

            # Skip deferred and extension commands
            if cmd_data.get('DEFERRED') or cmd_data.get('EXTENSION'):
                continue

            # Auto-categorize based on name and uCODE template
            if cmd_name in ['STATUS', 'DASH', 'DASHBOARD', 'HELP', 'HISTORY', 'LOGS', 'RESOURCE']:
                categories["📊 System & Info"].append(cmd_name)
            elif cmd_name in ['BLANK', 'SPLASH', 'REBOOT', 'REPAIR', 'DESTROY', 'UNDO', 'REDO', 'RESTORE']:
                categories["🔧 System Control"].append(cmd_name)
            elif 'FILE|' in ucode or cmd_name in ['EDIT', 'SHOW', 'RUN', 'NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME', 'FILE']:
                categories["📝 File Operations"].append(cmd_name)
            elif cmd_name in ['BANK', 'MEMORY', 'KNOWLEDGE']:
                categories["💾 Knowledge & Memory"].append(cmd_name)
            elif cmd_name in ['PANEL', 'GUIDE', 'DIAGRAM', 'TILE', 'VIEWPORT', 'PALETTE', 'THEME', 'DRAW', 'SVG']:
                categories["🎨 Display & Themes"].append(cmd_name)
            elif cmd_name in ['SEARCH', 'FIND', 'LOCATE', 'WHERE']:
                categories["🔍 Search & Navigation"].append(cmd_name)
            elif cmd_name in ['CONFIG', 'SETTINGS', 'SETUP', 'GET', 'SET', 'WORKSPACE']:
                categories["⚙️  Configuration"].append(cmd_name)
            elif cmd_name in ['MISSION', 'SCHEDULE', 'WORKFLOW']:
                categories["🎮 Automation & Missions"].append(cmd_name)
            else:
                categories["⚡ Other"].append(cmd_name)

        return categories

    def search_help(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search help content with fuzzy matching.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching commands with relevance scores
        """
        query_lower = query.lower()
        results = []

        for cmd_data in self.commands_data:
            cmd_name = cmd_data.get('NAME', '')
            desc = cmd_data.get('DESCRIPTION', '')
            syntax = cmd_data.get('SYNTAX', '')

            # Calculate relevance score
            score = 0.0

            # Exact name match (highest priority)
            if cmd_name.lower() == query_lower:
                score = 100.0
            # Name starts with query
            elif cmd_name.lower().startswith(query_lower):
                score = 90.0
            # Name contains query
            elif query_lower in cmd_name.lower():
                score = 80.0
            # Description contains query
            elif query_lower in desc.lower():
                score = 60.0
            # Fuzzy match on name
            else:
                ratio = SequenceMatcher(None, query_lower, cmd_name.lower()).ratio()
                if ratio > 0.6:
                    score = ratio * 50

            if score > 0:
                results.append({
                    'command': cmd_name,
                    'description': desc,
                    'syntax': syntax,
                    'score': score,
                    'data': cmd_data
                })

        # Sort by score (descending) and return top N
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def get_help_by_category(self, category_name: str) -> List[str]:
        """
        Get commands in a specific category.

        Args:
            category_name: Category identifier (can be partial match)

        Returns:
            List of command names in category
        """
        category_name_lower = category_name.lower()

        for cat_key, commands in self.categories.items():
            if category_name_lower in cat_key.lower():
                return sorted(commands)

        return []

    def get_command_details(self, command_name: str) -> Optional[Dict]:
        """
        Get detailed information for a specific command.

        Args:
            command_name: Command name (case-insensitive)

        Returns:
            Command data dictionary or None if not found
        """
        cmd_upper = command_name.upper()

        for cmd_data in self.commands_data:
            if cmd_data.get('NAME') == cmd_upper:
                return cmd_data

        return None

    def get_related_commands(self, command_name: str, limit: int = 5) -> List[str]:
        """
        Find commands related to a given command.

        Args:
            command_name: Reference command name
            limit: Maximum number of related commands

        Returns:
            List of related command names
        """
        cmd_data = self.get_command_details(command_name)
        if not cmd_data:
            return []

        # Find category of reference command
        ref_category = None
        for cat_name, commands in self.categories.items():
            if command_name.upper() in commands:
                ref_category = cat_name
                break

        if not ref_category:
            return []

        # Get other commands in same category
        related = [cmd for cmd in self.categories[ref_category]
                  if cmd != command_name.upper()]

        return related[:limit]

    def format_help_detailed(self, command_name: str) -> str:
        """
        Format detailed help for a command with enhanced layout.

        Args:
            command_name: Command to display help for

        Returns:
            Formatted help text
        """
        cmd_data = self.get_command_details(command_name)
        if not cmd_data:
            return f"❌ Command '{command_name}' not found."

        cmd_name = cmd_data.get('NAME', '')
        desc = cmd_data.get('DESCRIPTION', 'No description')
        syntax = cmd_data.get('SYNTAX', 'No syntax')
        ucode = cmd_data.get('UCODE_TEMPLATE', '')

        # Build help text
        help_text = "╔" + "═"*78 + "╗\n"
        help_text += f"║  📖 {cmd_name}".ljust(79) + "║\n"
        help_text += "╠" + "═"*78 + "╣\n"

        # Description
        help_text += "║  Description:".ljust(79) + "║\n"
        help_text += self._wrap_text(desc, 4)

        help_text += "║".ljust(79) + "║\n"

        # Syntax
        help_text += "║  Syntax:".ljust(79) + "║\n"
        help_text += f"║    {syntax}".ljust(79) + "║\n"

        # uCODE template if available
        if ucode:
            help_text += "║".ljust(79) + "║\n"
            help_text += "║  uCODE Format:".ljust(79) + "║\n"
            help_text += f"║    {ucode}".ljust(79) + "║\n"

        # Related commands
        related = self.get_related_commands(cmd_name)
        if related:
            help_text += "║".ljust(79) + "║\n"
            help_text += "║  Related Commands:".ljust(79) + "║\n"
            help_text += f"║    {', '.join(related[:5])}".ljust(79) + "║\n"

        help_text += "╚" + "═"*78 + "╝\n"
        return help_text

    def format_help_category(self, category_name: str) -> str:
        """
        Format help for a category.

        Args:
            category_name: Category to display

        Returns:
            Formatted category help
        """
        commands = self.get_help_by_category(category_name)
        if not commands:
            return f"❌ Category '{category_name}' not found."

        # Find full category name
        full_cat_name = None
        for cat_key in self.categories.keys():
            if category_name.lower() in cat_key.lower():
                full_cat_name = cat_key
                break

        help_text = "╔" + "═"*78 + "╗\n"
        help_text += f"║  {full_cat_name}".ljust(79) + "║\n"
        help_text += "╠" + "═"*78 + "╣\n"

        for cmd_name in commands:
            cmd_data = self.get_command_details(cmd_name)
            if cmd_data:
                desc = cmd_data.get('DESCRIPTION', '')[:56]
                help_text += f"║  {cmd_name:<18} - {desc.ljust(56)}║\n"

        help_text += "╚" + "═"*78 + "╝\n"
        
        # Use pager for long output
        if help_text.count('\n') > 20:
            page_output(help_text, title=full_cat_name or category_name)
            return ""  # Already displayed via pager
        
        return help_text

    def format_search_results(self, query: str, limit: int = 10) -> str:
        """
        Format search results.

        Args:
            query: Search query
            limit: Maximum results to display

        Returns:
            Formatted search results
        """
        results = self.search_help(query, limit)

        if not results:
            return f"🔍 No commands found matching '{query}'"

        help_text = "╔" + "═"*78 + "╗\n"
        help_text += f"║  🔍 Search Results for '{query}'".ljust(79) + "║\n"
        help_text += "╠" + "═"*78 + "╣\n"
        help_text += f"║  Found {len(results)} command(s)".ljust(79) + "║\n"
        help_text += "║".ljust(79) + "║\n"

        for result in results:
            cmd_name = result['command']
            desc = result['description'][:56]
            score = result['score']
            help_text += f"║  {cmd_name:<18} - {desc.ljust(56)}║\n"

        help_text += "║".ljust(79) + "║\n"
        help_text += "║  💡 Use 'HELP <command>' for details".ljust(79) + "║\n"
        help_text += "╚" + "═"*78 + "╝\n"
        
        # Use pager for long output
        if help_text.count('\n') > 20:
            page_output(help_text, title=f"Search: {query}")
            return ""  # Already displayed via pager
        
        return help_text

    def _wrap_text(self, text: str, indent: int = 4) -> str:
        """
        Wrap text to fit within help box.

        Args:
            text: Text to wrap
            indent: Number of spaces to indent

        Returns:
            Wrapped text lines
        """
        words = text.split()
        lines = []
        line = "║" + " " * indent

        for word in words:
            if len(line) + len(word) + 1 > 77:
                lines.append(line.ljust(79) + "║\n")
                line = "║" + " " * indent + word
            else:
                line += (" " if len(line) > indent + 1 else "") + word

        if len(line) > indent + 1:
            lines.append(line.ljust(79) + "║\n")

        return "".join(lines)

    def get_all_commands(self) -> List[str]:
        """Get list of all command names."""
        return [cmd.get('NAME', '') for cmd in self.commands_data]

    def get_categories(self) -> List[str]:
        """Get list of all category names."""
        return list(self.categories.keys())
