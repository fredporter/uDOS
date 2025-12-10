"""
uDOS v1.2.22 - Modern Help System

Integrated with smart prompt and pager:
- Clean, borderless output
- Syntax highlighting for commands and examples
- Command options and subcommands clearly displayed
- Minimal blank lines
- Pager integration for long content
- Hotkey support in smart prompt

Version: 1.2.22
Author: uDOS Development Team
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
import re


class HelpHandler:
    """Modern help system with smart prompt integration."""

    def __init__(self, viewport=None, logger=None):
        """Initialize help handler."""
        self.viewport = viewport
        self.logger = logger
        self.commands = self._load_commands()
        
        # ANSI colors for syntax highlighting
        self.colors = {
            'command': '\033[1;36m',      # Cyan for commands
            'option': '\033[1;33m',       # Yellow for options
            'param': '\033[1;35m',        # Magenta for parameters
            'value': '\033[0;32m',        # Green for values
            'comment': '\033[0;90m',      # Gray for comments
            'highlight': '\033[1;37m',    # Bright white for emphasis
            'reset': '\033[0m'
        }

    def _load_commands(self) -> Dict:
        """Load commands from commands.json."""
        commands_file = Path(__file__).parent.parent / 'data' / 'commands.json'
        with open(commands_file) as f:
            data = json.load(f)
        return {cmd['NAME']: cmd for cmd in data['COMMANDS']}

    def handle(self, params: List[str]) -> str:
        """
        Handle HELP command.

        Usage:
            HELP                - Show available commands by category
            HELP <command>      - Show detailed help for command
            HELP SEARCH <term>  - Search commands

        Args:
            params: Command parameters

        Returns:
            Formatted help output
        """
        if not params:
            return self._show_command_list()

        command = params[0].upper()

        if command == 'SEARCH':
            query = ' '.join(params[1:]).lower() if len(params) > 1 else ''
            return self._search_commands(query)

        # Show specific command help
        if command in self.commands:
            return self._show_command_help(command)
        
        # Try fuzzy match
        matches = self._fuzzy_match(command)
        if matches:
            if len(matches) == 1:
                return self._show_command_help(matches[0])
            else:
                return self._show_matches(command, matches)
        
        return f"❌ Unknown command: {command}\n💡 Type HELP to see all commands"

    def _show_command_list(self) -> str:
        """Show categorized list of all commands."""
        c = self.colors
        lines = []
        
        # Header
        lines.append(f"{c['highlight']}📚 uDOS Command Reference{c['reset']}")
        lines.append(f"{c['comment']}Complete guide to all available commands organized by category{c['reset']}\n")
        
        # Group commands by category with descriptions
        categories = {
            '🗂️  File Operations': {
                'description': 'Create, edit, delete, and manage files and directories',
                'commands': ['FILE', 'NEW', 'DELETE', 'COPY', 'MOVE', 'EDIT', 'SHOW', 'LIST', 'TREE']
            },
            '⚙️  System': {
                'description': 'System maintenance, configuration, and status monitoring',
                'commands': ['STATUS', 'REPAIR', 'CONFIG', 'BACKUP', 'CLEAN', 'REBOOT', 'THEME']
            },
            '📖 Knowledge': {
                'description': 'Access survival guides and knowledge bank resources',
                'commands': ['GUIDE', 'SEARCH', 'INDEX']
            },
            '💾 Memory': {
                'description': 'Personal, shared, and community memory management',
                'commands': ['MEMORY', 'PRIVATE', 'SHARED', 'COMMUNITY']
            },
            '🎨 Graphics': {
                'description': 'Create and display ASCII art, diagrams, and visual content',
                'commands': ['SVG', 'DIAGRAM', 'PANEL', 'SPRITE']
            },
            '🗺️  Mapping': {
                'description': 'Navigate grid system, layers, and spatial coordinates',
                'commands': ['MAP', 'TILE', 'LAYER', 'LOCATE', 'ASCEND', 'DESCEND']
            },
            '☁️  Cloud': {
                'description': 'Cloud synchronization and external data integration',
                'commands': ['GMAIL', 'SYNC', 'EMAIL', 'IMPORT', 'EXPORT']
            },
            '🤖 AI & Automation': {
                'description': 'AI-powered content generation and workflow automation',
                'commands': ['OK', 'MAKE', 'MISSION', 'WORKFLOW', 'SCHEDULE']
            },
            '🎮 Gameplay': {
                'description': 'Experience points, items, quests, and achievements',
                'commands': ['XP', 'ITEM', 'QUEST', 'ACHIEVEMENT']
            },
            '🔧 Advanced': {
                'description': 'Development tools, debugging, and system extensions',
                'commands': ['DEV', 'DEBUG', 'RESOURCE', 'EXTENSION']
            },
        }
        
        for category, data in categories.items():
            lines.append(f"{c['highlight']}{category}{c['reset']}")
            lines.append(f"{c['comment']}{data['description']}{c['reset']}")
            
            available_cmds = [cmd for cmd in data['commands'] if cmd in self.commands]
            if available_cmds:
                # Format in columns with descriptions
                cols = 3
                for i in range(0, len(available_cmds), cols):
                    row = available_cmds[i:i+cols]
                    formatted_cmds = []
                    for cmd in row:
                        desc = self.commands[cmd].get('DESCRIPTION', '')[:30]
                        formatted_cmds.append(f"{c['command']}{cmd:12}{c['reset']} {c['comment']}{desc}{c['reset']}")
                    lines.append("  " + "  ".join(formatted_cmds))
            lines.append("")  # Single blank line between categories
        
        # Usage hints section
        lines.append(f"{c['highlight']}Quick Start Guide{c['reset']}")
        lines.append(f"{c['comment']}Getting help and finding commands:{c['reset']}")
        lines.append(f"  {c['command']}HELP <command>{c['reset']}        Show detailed help for any command")
        lines.append(f"  {c['command']}HELP SEARCH <term>{c['reset']}    Search all commands by keyword")
        lines.append(f"  {c['command']}Press F1{c['reset']}               Get help while typing a command")
        lines.append(f"  {c['command']}↑/↓ arrows{c['reset']}             Navigate command completions")
        lines.append(f"  {c['command']}Tab or Enter{c['reset']}           Accept selected completion\n")
        
        # Common workflows
        lines.append(f"{c['highlight']}Common Workflows{c['reset']}")
        lines.append(f"  {c['option']}File Management:{c['reset']}    FILE → Pick operation → Select file")
        lines.append(f"  {c['option']}Knowledge Lookup:{c['reset']}  GUIDE water → Browse survival guides")
        lines.append(f"  {c['option']}AI Generation:{c['reset']}     OK MAKE SVG \"water filter diagram\"")
        lines.append(f"  {c['option']}System Check:{c['reset']}      STATUS → View system health")
        
        return "\n".join(lines)

    def _show_command_help(self, command: str) -> str:
        """Show detailed help for a specific command."""
        c = self.colors
        cmd_data = self.commands[command]
        lines = []
        
        # Command name and description (more detailed)
        lines.append(f"{c['highlight']}━━━ {command} ━━━{c['reset']}")
        description = cmd_data.get('DESCRIPTION', 'No description available')
        lines.append(f"{description}\n")
        
        # Syntax with explanation
        syntax = cmd_data.get('SYNTAX', command)
        lines.append(f"{c['comment']}Syntax:{c['reset']}")
        lines.append(f"  {self._highlight_syntax(syntax)}")
        lines.append(f"{c['comment']}  Legend: {c['command']}COMMAND{c['reset']} {c['option']}[optional]{c['reset']} {c['param']}<required>{c['reset']} {c['comment']}|{c['reset']} {c['comment']}choices{c['reset']}\n")
        
        # Subcommands/Options (with more detail)
        subcommands = cmd_data.get('SUBCOMMANDS', {})
        if subcommands:
            lines.append(f"{c['comment']}Available Options:{c['reset']}")
            for subcmd, desc in subcommands.items():
                # Clean up subcmd display
                clean_subcmd = subcmd.strip('<>')
                lines.append(f"  {c['option']}{clean_subcmd:18}{c['reset']} {desc}")
            lines.append("")
        
        # Examples (show all with context)
        examples = cmd_data.get('EXAMPLES', [])
        if examples:
            lines.append(f"{c['comment']}Usage Examples:{c['reset']}")
            for i, example in enumerate(examples[:8], 1):  # Show up to 8 examples
                lines.append(f"  {c['comment']}{i}.{c['reset']} {c['command']}{example}{c['reset']}")
            if len(examples) > 8:
                lines.append(f"{c['comment']}  ... and {len(examples) - 8} more examples{c['reset']}")
            lines.append("")
        
        # Flags (with full descriptions)
        flags = cmd_data.get('FLAGS', {})
        if flags:
            lines.append(f"{c['comment']}Command Flags:{c['reset']}")
            for flag, desc in flags.items():
                lines.append(f"  {c['option']}{flag:18}{c['reset']} {desc}")
            lines.append("")
        
        # Notes (show all)
        notes = cmd_data.get('NOTES', [])
        if notes:
            lines.append(f"{c['comment']}Important Notes:{c['reset']}")
            for note in notes:  # Show all notes
                # Remove emoji if present at start
                clean_note = re.sub(r'^[^\w\s]+\s*', '', note)
                lines.append(f"  • {clean_note}")
            lines.append("")
        
        # Related commands (if we can infer them)
        related = self._get_related_commands(command)
        if related:
            lines.append(f"{c['comment']}Related Commands:{c['reset']}")
            for rel_cmd in related[:5]:
                rel_desc = self.commands[rel_cmd].get('DESCRIPTION', '')[:50]
                lines.append(f"  {c['command']}{rel_cmd:15}{c['reset']} {c['comment']}{rel_desc}{c['reset']}")
            lines.append("")
        
        # Footer with helpful hints
        lines.append(f"{c['comment']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{c['reset']}")
        lines.append(f"{c['comment']}💡 Tips:{c['reset']}")
        lines.append(f"  • Press {c['option']}F1{c['reset']} while typing to see this help")
        lines.append(f"  • Use {c['command']}↑/↓{c['reset']} arrows to browse command completions")
        lines.append(f"  • Type {c['command']}HELP SEARCH <keyword>{c['reset']} to find related commands")
        
        return "\n".join(lines)

    def _highlight_syntax(self, syntax: str) -> str:
        """Apply syntax highlighting to command syntax."""
        c = self.colors
        
        # Highlight command name (first word)
        parts = syntax.split(None, 1)
        if not parts:
            return syntax
        
        result = f"{c['command']}{parts[0]}{c['reset']}"
        
        if len(parts) > 1:
            rest = parts[1]
            # Highlight options in brackets
            rest = re.sub(r'\[([^\]]+)\]', f"{c['comment']}[{c['option']}\\1{c['comment']}]{c['reset']}", rest)
            # Highlight required params in <>
            rest = re.sub(r'<([^>]+)>', f"{c['param']}<\\1>{c['reset']}", rest)
            # Highlight pipe separator
            rest = re.sub(r'\|', f"{c['comment']}|{c['reset']}", rest)
            result += " " + rest
        
        return result

    def _search_commands(self, query: str) -> str:
        """Search commands by name or description."""
        c = self.colors
        
        if not query:
            return "❌ Usage: HELP SEARCH <term>\nExample: HELP SEARCH file"
        
        matches = []
        query_lower = query.lower()
        
        for name, cmd_data in self.commands.items():
            desc = cmd_data.get('DESCRIPTION', '').lower()
            syntax = cmd_data.get('SYNTAX', '').lower()
            
            if (query_lower in name.lower() or 
                query_lower in desc or 
                query_lower in syntax):
                matches.append((name, cmd_data))
        
        if not matches:
            return f"❌ No commands found matching '{query}'\n💡 Try HELP to see all commands"
        
        lines = []
        lines.append(f"{c['highlight']}🔍 Search results for '{query}'{c['reset']}\n")
        
        for name, cmd_data in matches[:15]:  # Show max 15 results
            desc = cmd_data.get('DESCRIPTION', '')[:60]
            lines.append(f"{c['command']}{name:15}{c['reset']} {desc}")
        
        if len(matches) > 15:
            lines.append(f"\n{c['comment']}... and {len(matches) - 15} more results{c['reset']}")
        
        lines.append(f"\n{c['comment']}💡 Type {c['command']}HELP <command>{c['reset']}{c['comment']} for details{c['reset']}")
        
        return "\n".join(lines)

    def _fuzzy_match(self, query: str) -> List[str]:
        """Find commands that partially match query."""
        query_lower = query.lower()
        matches = []
        
        for name in self.commands.keys():
            if query_lower in name.lower():
                matches.append(name)
        
        return matches
    
    def _get_related_commands(self, command: str) -> List[str]:
        """Find commands related to the given command."""
        cmd_data = self.commands[command]
        desc_lower = cmd_data.get('DESCRIPTION', '').lower()
        syntax_lower = cmd_data.get('SYNTAX', '').lower()
        
        # Keywords to look for relationships
        keywords = set()
        for word in desc_lower.split():
            if len(word) > 4:  # Only meaningful words
                keywords.add(word)
        
        related = []
        for name, data in self.commands.items():
            if name == command:
                continue
            
            other_desc = data.get('DESCRIPTION', '').lower()
            other_syntax = data.get('SYNTAX', '').lower()
            
            # Check for keyword overlap
            for keyword in keywords:
                if keyword in other_desc or keyword in other_syntax:
                    related.append(name)
                    break
        
        return related[:5]
    
    def get_quick_help_for_prompt(self, command: str) -> str:
        """Get one-line quick help for smart prompt display."""
        if command not in self.commands:
            return ""
        
        cmd_data = self.commands[command]
        syntax = cmd_data.get('SYNTAX', command)
        desc = cmd_data.get('DESCRIPTION', '')[:60]
        
        return f"{syntax} - {desc}"
