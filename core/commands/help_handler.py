"""
uDOS v1.2.9+ - Enhanced Help System

Provides comprehensive, navigable help with:
- Section selector (quick jump to categories)
- Complete command reference with all v1.2.x additions
- Syntax highlighting for examples
- Usage patterns and common workflows
- Interactive navigation

Version: 1.2.9
Author: uDOS Development Team
"""

from typing import List, Dict, Optional
from core.output.syntax_highlighter import highlight_syntax
import re

# ANSI color codes for command highlighting
CMD_COLOR = '\033[1;32m'  # Bright green for commands
RESET = '\033[0m'


def colorize_command(text: str) -> str:
    """Colorize command names in text (e.g., 'HELP FILES' -> colored 'HELP' and 'FILES')."""
    # Match uppercase words (commands)
    return re.sub(r'\b([A-Z][A-Z0-9_]+)\b', f'{CMD_COLOR}\\1{RESET}', text)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text for length calculation."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


def pad_to_border(text: str, total_width: int = 79) -> str:
    """Pad text to fit border width, accounting for ANSI codes."""
    visible_len = len(strip_ansi(text))
    padding_needed = total_width - visible_len
    return text + ' ' * padding_needed


class HelpHandler:
    """Enhanced help system with section navigation and comprehensive docs."""

    def __init__(self):
        """Initialize help system with all command categories."""
        self.sections = self._build_sections()

    def handle(self, params: List[str]) -> str:
        """
        Handle HELP command with enhanced features.

        Usage:
            HELP                    - Show main menu with section selector
            HELP <section>          - Jump to specific section
            HELP SEARCH <query>     - Search all commands
            HELP QUICK              - Quick reference card
            HELP <command>          - Detailed help for specific command

        Args:
            params: Command parameters

        Returns:
            Formatted help output
        """
        if not params:
            return self._show_main_menu()

        subcommand = params[0].upper()

        # Section shortcuts
        section_map = {
            'FILES': 'file',
            'FILE': 'file',
            'SYSTEM': 'system',
            'KNOWLEDGE': 'knowledge',
            'KB': 'knowledge',
            'MEMORY': 'memory',
            'GRAPHICS': 'graphics',
            'DIAGRAM': 'graphics',
            'SVG': 'graphics',
            'MAP': 'mapping',
            'MAPPING': 'mapping',
            'TILE': 'mapping',
            'CLOUD': 'cloud',
            'GMAIL': 'cloud',
            'SYNC': 'cloud',
            'AUTOMATION': 'automation',
            'MISSIONS': 'automation',
            'WORKFLOW': 'automation',
            'DISPLAY': 'display',
            'THEME': 'display',
            'DEV': 'advanced',
            'DEBUG': 'advanced',
            'RESOURCE': 'advanced',
        }

        # Check for section shortcuts
        if subcommand in section_map:
            return self._show_section(section_map[subcommand])

        # Special commands
        if subcommand == 'SEARCH':
            if len(params) < 2:
                return "Usage: HELP SEARCH <query>\nExample: HELP SEARCH workflow"
            query = ' '.join(params[1:]).lower()
            return self._search_commands(query)

        if subcommand == 'QUICK':
            return self._show_quick_reference()

        # Try to find specific command
        return self._show_command_help(subcommand)

    def _show_main_menu(self) -> str:
        """Show main help menu with section selector."""
        lines = []

        # Header
        lines.append("╔" + "═"*78 + "╗")
        lines.append("║" + " "*26 + "uDOS HELP SYSTEM" + " "*34 + "║")
        lines.append("╠" + "═"*78 + "╣")
        lines.append("║" + " "*78 + "║")

        # Section Selector
        lines.append("║  QUICK NAVIGATION:".ljust(79) + "║")
        lines.append("║  " + "─"*76 + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP FILES") + "         - File operations (NEW, EDIT, DELETE, COPY, etc.)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP SYSTEM") + "        - System commands (STATUS, REPAIR, BACKUP, etc.)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP KNOWLEDGE") + "     - Knowledge bank & guides (GUIDE, SEARCH)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP MEMORY") + "        - Memory system (MEMORY, SHARED, PRIVATE)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP GRAPHICS") + "      - Graphics & diagrams (SVG, DIAGRAM, PANEL)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP MAPPING") + "       - Map & grid system (TILE, LAYER, LOCATE)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP CLOUD") + "         - Cloud sync (GMAIL, SYNC, EMAIL, IMPORT)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP AUTOMATION") + "    - Missions & workflows (MISSION, SCHEDULE)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP DISPLAY") + "       - Display & themes (PANEL, THEME, LAYOUT)", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP ADVANCED") + "      - Advanced tools (DEV MODE, RESOURCE, LOGS)", 76) + "║")
        lines.append("║" + " "*78 + "║")

        # Special Features
        lines.append("║  SPECIAL FEATURES:".ljust(79) + "║")
        lines.append("║  " + "─"*76 + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP SEARCH") + " <query>       - Search all commands", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP QUICK") + "                - One-page quick reference", 76) + "║")
        lines.append("║  " + pad_to_border(colorize_command("HELP") + " <command>            - Detailed help for specific command", 76) + "║")
        lines.append("║" + " "*78 + "║")

        # Footer
        lines.append("╠" + "═"*78 + "╣")
        lines.append("║  Full documentation: https://github.com/fredporter/uDOS/wiki".ljust(79) + "║")
        lines.append("║  Get support: File an issue on GitHub".ljust(79) + "║")
        lines.append("║  uDOS version: 1.2.9 (Gmail Cloud Sync)".ljust(79) + "║")
        lines.append("╚" + "═"*78 + "╝")

        return '\n'.join(lines)

    def _show_section(self, section: str) -> str:
        """Show commands for a specific section."""
        if section not in self.sections:
            return f"Unknown section: {section}\nTry: HELP for all sections"

        section_data = self.sections[section]
        lines = []

        # Header
        lines.append("╔" + "═"*78 + "╗")
        header_text = f"{section_data['icon']} {section_data['title']}"
        lines.append("║  " + pad_to_border(header_text, 76) + "║")
        lines.append("╠" + "═"*78 + "╣")
        lines.append("║" + " "*78 + "║")

        # Commands
        for cmd in section_data['commands']:
            cmd_name_colored = colorize_command(cmd['name'])
            lines.append("║  " + pad_to_border(cmd_name_colored, 76) + "║")
            lines.append(f"║    {cmd['desc']:<73} ║")
            lines.append("║" + " "*78 + "║")

            # Syntax with highlighting
            lines.append("║    Syntax:".ljust(79) + "║")
            for syntax in cmd['syntax']:
                highlighted = highlight_syntax(syntax)
                lines.append("║      " + pad_to_border(highlighted, 72) + "║")

            lines.append("║" + " "*78 + "║")

            # Examples
            if cmd.get('examples'):
                lines.append("║    Examples:".ljust(79) + "║")
                for example in cmd['examples']:
                    highlighted = highlight_syntax(example)
                    lines.append("║      " + pad_to_border(highlighted, 72) + "║")
                lines.append("║" + " "*78 + "║")

        # Footer
        lines.append("╠" + "═"*78 + "╣")
        lines.append("║  " + pad_to_border("Tip: Use " + colorize_command("HELP") + " <command> for more details", 76) + "║")
        lines.append("║  " + pad_to_border("Try: " + colorize_command("HELP SEARCH") + " <keyword> to find related commands", 76) + "║")
        lines.append("╚" + "═"*78 + "╝")

        return '\n'.join(lines)

    def _show_quick_reference(self) -> str:
        """Show one-page quick reference card."""
        lines = []

        lines.append("╔" + "═"*78 + "╗")
        lines.append("║" + " "*25 + "QUICK REFERENCE CARD" + " "*33 + "║")
        lines.append("╠" + "═"*78 + "╣")
        lines.append("║" + " "*78 + "║")

        # Most used commands by category
        quick_cmds = [
            ("Files", [
                ("NEW <file>", "Create new file"),
                ("EDIT <file>", "Edit file"),
                ("DELETE <file>", "Delete file"),
                ("SHOW <file>", "Display file"),
            ]),
            ("System", [
                ("STATUS", "System overview"),
                ("REPAIR", "Fix system issues"),
                ("BACKUP <file>", "Create backup"),
                ("CLEAN", "Clean workspace"),
            ]),
            ("Knowledge", [
                ("GUIDE <topic>", "Interactive guide"),
                ("SEARCH <query>", "Search knowledge"),
            ]),
            ("Cloud", [
                ("LOGIN GMAIL", "Authenticate"),
                ("SYNC GMAIL", "Sync files"),
                ("EMAIL LIST", "List emails"),
                ("IMPORT GMAIL", "Import emails"),
            ]),
            ("Automation", [
                ("MISSION CREATE", "New mission"),
                ("WORKFLOW RUN", "Run workflow"),
                ("SCHEDULE ADD", "Schedule task"),
            ]),
            ("Graphics", [
                ("SVG <name>", "Generate SVG"),
                ("DIAGRAM <topic>", "Create diagram"),
                ("PANEL <content>", "Display panel"),
            ]),
        ]

        for category, commands in quick_cmds:
            category_colored = colorize_command(category)
            lines.append("║  " + pad_to_border(category_colored, 76) + "║")
            lines.append("║  " + "─"*76 + "║")
            for cmd, desc in commands:
                cmd_colored = colorize_command(cmd)
                line_text = f"{cmd_colored:<25} {desc}"
                lines.append("║    " + pad_to_border(line_text, 74) + "║")
            lines.append("║" + " "*78 + "║")

        # Common patterns
        lines.append("║  Common Patterns:".ljust(79) + "║")
        lines.append("║  " + "─"*76 + "║")
        lines.append("║    " + pad_to_border("$VARIABLE                   Use environment variables", 74) + "║")
        lines.append("║    " + pad_to_border("COMMAND --flag              Add options to commands", 74) + "║")
        lines.append("║    " + pad_to_border("COMMAND < input > output    Redirect input/output", 74) + "║")
        lines.append("║" + " "*78 + "║")

        lines.append("╠" + "═"*78 + "╣")
        lines.append("║  " + pad_to_border("For detailed help: " + colorize_command("HELP") + " <section> or " + colorize_command("HELP") + " <command>", 76) + "║")
        lines.append("╚" + "═"*78 + "╝")

        return '\n'.join(lines)

    def _search_commands(self, query: str) -> str:
        """Search commands by name, description, or category."""
        results = []

        for section_name, section_data in self.sections.items():
            for cmd in section_data['commands']:
                # Search in name, description, and syntax
                searchable = f"{cmd['name']} {cmd['desc']} {' '.join(cmd['syntax'])}".lower()
                if query in searchable:
                    results.append({
                        'section': section_data['title'],
                        'icon': section_data['icon'],
                        'name': cmd['name'],
                        'desc': cmd['desc']
                    })

        if not results:
            return f"No commands found matching '{query}'\nTry broader search terms or HELP for all sections"

        # Format results
        lines = []
        lines.append("╔" + "═"*78 + "╗")
        lines.append("║  🔍 " + pad_to_border(f"Search Results for: {query}", 74) + "║")
        lines.append("╠" + "═"*78 + "╣")
        lines.append("║" + " "*78 + "║")

        for result in results:
            result_line = f"{result['icon']} {colorize_command(result['name']):<25} ({result['section']})"
            lines.append("║  " + pad_to_border(result_line, 76) + "║")
            lines.append(f"║    {result['desc']:<73} ║")
            lines.append("║" + " "*78 + "║")

        lines.append("╠" + "═"*78 + "╣")
        lines.append("║  " + pad_to_border(f"Found {len(results)} command(s). Use " + colorize_command("HELP") + " <command> for details.", 76) + "║")
        lines.append("╚" + "═"*78 + "╝")

        return '\n'.join(lines)

    def _show_command_help(self, command: str) -> str:
        """Show detailed help for a specific command."""
        # Search all sections for the command
        for section_name, section_data in self.sections.items():
            for cmd in section_data['commands']:
                if cmd['name'].upper() == command.upper():
                    return self._format_command_detail(cmd, section_data)

        return f"Unknown command: {command}\nTry: HELP SEARCH {command.lower()}"

    def _format_command_detail(self, cmd: Dict, section: Dict) -> str:
        """Format detailed help for a single command."""
        lines = []

        lines.append("╔" + "═"*78 + "╗")
        cmd_header = f"{section['icon']} {colorize_command(cmd['name'])}"
        lines.append("║  " + pad_to_border(cmd_header, 76) + "║")
        lines.append("╠" + "═"*78 + "╣")
        lines.append("║" + " "*78 + "║")

        # Description
        lines.append(f"║  {cmd['desc']:<75} ║")
        lines.append("║" + " "*78 + "║")

        # Syntax
        lines.append("║  Syntax:".ljust(79) + "║")
        lines.append("║  " + "─"*76 + "║")
        for syntax in cmd['syntax']:
            highlighted = highlight_syntax(syntax)
            lines.append("║    " + pad_to_border(highlighted, 74) + "║")
        lines.append("║" + " "*78 + "║")

        # Examples
        if cmd.get('examples'):
            lines.append("║  Examples:".ljust(79) + "║")
            lines.append("║  " + "─"*76 + "║")
            for example in cmd['examples']:
                highlighted = highlight_syntax(example)
                lines.append("║    " + pad_to_border(highlighted, 74) + "║")
            lines.append("║" + " "*78 + "║")

        # Related commands
        if cmd.get('related'):
            lines.append("║  Related Commands:".ljust(79) + "║")
            lines.append("║  " + "─"*76 + "║")
            related_str = ", ".join(cmd['related'])
            lines.append(f"║    {related_str:<73} ║")
            lines.append("║" + " "*78 + "║")

        # Notes
        if cmd.get('notes'):
            lines.append("║  Notes:".ljust(79) + "║")
            lines.append("║  " + "─"*76 + "║")
            for note in cmd['notes']:
                # Wrap long notes
                while len(note) > 73:
                    break_point = note[:73].rfind(' ')
                    if break_point == -1:
                        break_point = 73
                    lines.append(f"║    {note[:break_point]:<73} ║")
                    note = note[break_point:].lstrip()
                if note:
                    lines.append(f"║    {note:<73} ║")
            lines.append("║" + " "*78 + "║")

        lines.append("╠" + "═"*78 + "╣")
        lines.append("║  " + pad_to_border("See also: " + colorize_command("HELP") + f" {section['title'][:20]}", 76) + "║")
        lines.append("╚" + "═"*78 + "╝")

        return '\n'.join(lines)

    def _build_sections(self) -> Dict:
        """Build comprehensive command reference with all v1.2.x commands."""
        return {
            'file': {
                'icon': '📝',
                'title': 'File Operations',
                'commands': [
                    {
                        'name': 'NEW',
                        'desc': 'Create a new file',
                        'syntax': ['NEW <filename>', 'NEW <filename> --template=<type>'],
                        'examples': [
                            'NEW shopping_list.txt',
                            'NEW mission.upy --template=mission',
                            'NEW notes.md --template=markdown',
                        ],
                        'related': ['EDIT', 'DELETE', 'COPY'],
                        'notes': ['Templates available: mission, workflow, checklist, markdown, python']
                    },
                    {
                        'name': 'EDIT',
                        'desc': 'Edit an existing file in your system editor',
                        'syntax': ['EDIT <filename>'],
                        'examples': ['EDIT config.json', 'EDIT memory/missions/current.upy'],
                        'related': ['NEW', 'SHOW', 'SAVE'],
                    },
                    {
                        'name': 'DELETE',
                        'desc': 'Delete a file (soft-delete to .archive/ for 7 days)',
                        'syntax': ['DELETE <filename>', 'DELETE <filename> --permanent'],
                        'examples': ['DELETE old_notes.txt', 'DELETE temp.log --permanent'],
                        'related': ['REPAIR RECOVER', 'CLEAN'],
                        'notes': ['Deleted files go to .archive/deleted/ for 7-day recovery window']
                    },
                    {
                        'name': 'COPY',
                        'desc': 'Copy a file to new location',
                        'syntax': ['COPY <source> <destination>'],
                        'examples': ['COPY template.upy my_mission.upy', 'COPY config.json config.backup'],
                        'related': ['MOVE', 'RENAME'],
                    },
                    {
                        'name': 'MOVE',
                        'desc': 'Move a file to new location',
                        'syntax': ['MOVE <source> <destination>'],
                        'examples': ['MOVE draft.txt memory/docs/', 'MOVE temp.log memory/logs/'],
                        'related': ['COPY', 'RENAME'],
                    },
                    {
                        'name': 'SHOW',
                        'desc': 'Display file contents',
                        'syntax': ['SHOW <filename>', 'SHOW <filename> --lines=N'],
                        'examples': ['SHOW README.md', 'SHOW memory/logs/system.log --lines=50'],
                        'related': ['EDIT', 'SEARCH'],
                    },
                ]
            },
            'system': {
                'icon': '🔧',
                'title': 'System Commands',
                'commands': [
                    {
                        'name': 'STATUS',
                        'desc': 'Show system status overview (disk, resources, health)',
                        'syntax': ['STATUS', 'STATUS --detailed', 'STATUS --health'],
                        'examples': ['STATUS', 'STATUS --health'],
                        'related': ['REPAIR', 'RESOURCE', 'CLEAN'],
                    },
                    {
                        'name': 'REPAIR',
                        'desc': 'Diagnose and fix system issues',
                        'syntax': ['REPAIR', 'REPAIR RECOVER <file>', 'REPAIR --auto'],
                        'examples': ['REPAIR', 'REPAIR RECOVER deleted_file.txt', 'REPAIR --auto'],
                        'related': ['STATUS', 'BACKUP', 'CLEAN'],
                        'notes': ['RECOVER restores files from .archive/deleted/ within 7-day window']
                    },
                    {
                        'name': 'BACKUP',
                        'desc': 'Create, list, restore, or clean file backups',
                        'syntax': [
                            'BACKUP <file>',
                            'BACKUP LIST <file>',
                            'BACKUP RESTORE <file> <timestamp>',
                            'BACKUP CLEAN <file>',
                        ],
                        'examples': [
                            'BACKUP config.json',
                            'BACKUP LIST config.json',
                            'BACKUP RESTORE config.json 20251205_143022',
                            'BACKUP CLEAN config.json',
                        ],
                        'related': ['UNDO', 'REDO', 'REPAIR'],
                        'notes': ['Backups stored in .archive/backups/ with 30-day retention']
                    },
                    {
                        'name': 'UNDO',
                        'desc': 'Revert file to previous version',
                        'syntax': ['UNDO <file>', 'UNDO <file> --steps=N'],
                        'examples': ['UNDO config.json', 'UNDO mission.upy --steps=3'],
                        'related': ['REDO', 'BACKUP'],
                        'notes': ['Uses .archive/versions/ with 90-day retention, keeps last 5 versions']
                    },
                    {
                        'name': 'REDO',
                        'desc': 'Re-apply undone changes to file',
                        'syntax': ['REDO <file>', 'REDO <file> --steps=N'],
                        'examples': ['REDO config.json', 'REDO mission.upy --steps=2'],
                        'related': ['UNDO', 'BACKUP'],
                    },
                    {
                        'name': 'CLEAN',
                        'desc': 'Clean workspace and manage archives',
                        'syntax': [
                            'CLEAN',
                            'CLEAN --scan',
                            'CLEAN --purge [days]',
                            'CLEAN --dry-run',
                        ],
                        'examples': [
                            'CLEAN',
                            'CLEAN --scan',
                            'CLEAN --purge 60',
                            'CLEAN --dry-run --purge 30',
                        ],
                        'related': ['REPAIR', 'BACKUP'],
                        'notes': ['--scan shows archive health metrics, --purge removes old archives']
                    },
                ]
            },
            'knowledge': {
                'icon': '📚',
                'title': 'Knowledge & Guides',
                'commands': [
                    {
                        'name': 'GUIDE',
                        'desc': 'Interactive survival guides with progress tracking',
                        'syntax': [
                            'GUIDE',
                            'GUIDE <category>',
                            'GUIDE <category>/<topic>',
                            'GUIDE LIST',
                        ],
                        'examples': [
                            'GUIDE water',
                            'GUIDE fire/friction',
                            'GUIDE shelter/debris-hut',
                            'GUIDE LIST',
                        ],
                        'related': ['SEARCH', 'DIAGRAM'],
                        'notes': ['Categories: water, fire, shelter, food, navigation, medical']
                    },
                    {
                        'name': 'SEARCH',
                        'desc': 'Search knowledge bank content',
                        'syntax': ['SEARCH <query>', 'SEARCH <query> --category=<cat>'],
                        'examples': [
                            'SEARCH water purification',
                            'SEARCH fire --category=fire',
                            'SEARCH navigation stars',
                        ],
                        'related': ['GUIDE', 'MEMORY'],
                    },
                ]
            },
            'memory': {
                'icon': '💾',
                'title': 'Memory System',
                'commands': [
                    {
                        'name': 'MEMORY',
                        'desc': '4-tier memory system (public knowledge, shared, private, community)',
                        'syntax': [
                            'MEMORY LIST',
                            'MEMORY SEARCH <query>',
                            'MEMORY ADD <content>',
                            'MEMORY GET <id>',
                        ],
                        'examples': [
                            'MEMORY LIST',
                            'MEMORY SEARCH survival',
                            'MEMORY ADD "Important note about water"',
                        ],
                        'related': ['SHARED', 'PRIVATE', 'COMMUNITY'],
                    },
                    {
                        'name': 'PRIVATE',
                        'desc': 'Private memory tier (encrypted, local-only)',
                        'syntax': ['PRIVATE LIST', 'PRIVATE ADD <content>', 'PRIVATE GET <id>'],
                        'examples': ['PRIVATE ADD "Personal reminder"', 'PRIVATE LIST'],
                        'related': ['MEMORY', 'SHARED'],
                    },
                    {
                        'name': 'SHARED',
                        'desc': 'Shared memory tier (cloud-synced groups)',
                        'syntax': ['SHARED LIST', 'SHARED ADD <content>', 'SHARED SYNC'],
                        'examples': ['SHARED LIST', 'SHARED SYNC'],
                        'related': ['MEMORY', 'COMMUNITY'],
                    },
                ]
            },
            'graphics': {
                'icon': '🎨',
                'title': 'Graphics & Diagrams',
                'commands': [
                    {
                        'name': 'SVG',
                        'desc': 'Generate SVG diagrams using Gemini AI',
                        'syntax': ['SVG <description>', 'SVG <description> --category=<cat>'],
                        'examples': [
                            'SVG water filter diagram',
                            'SVG fire teepee structure --category=fire',
                            'SVG shelter debris hut --category=shelter',
                        ],
                        'related': ['DIAGRAM', 'PANEL'],
                        'notes': ['Requires GEMINI_API_KEY in .env file']
                    },
                    {
                        'name': 'DIAGRAM',
                        'desc': 'Generate Mermaid diagrams',
                        'syntax': ['DIAGRAM <type> <description>'],
                        'examples': [
                            'DIAGRAM flowchart "Water purification process"',
                            'DIAGRAM sequence "Mission workflow"',
                        ],
                        'related': ['SVG', 'PANEL'],
                    },
                    {
                        'name': 'PANEL',
                        'desc': 'Display teletext-style panels',
                        'syntax': ['PANEL <content>', 'PANEL <file>'],
                        'examples': ['PANEL "Status update"', 'PANEL memory/docs/status.txt'],
                        'related': ['DIAGRAM', 'THEME'],
                    },
                ]
            },
            'mapping': {
                'icon': '🗺️',
                'title': 'Mapping & Grid System',
                'commands': [
                    {
                        'name': 'TILE',
                        'desc': 'Grid tile commands (2-letter TILE codes)',
                        'syntax': [
                            'TILE INFO <code>',
                            'TILE LOCATE <name>',
                            'TILE LAYER <layer>',
                            'TILE CONVERT <coords>',
                        ],
                        'examples': [
                            'TILE INFO AA340',
                            'TILE LOCATE Sydney',
                            'TILE LAYER 100',
                            'TILE CONVERT -33.87,151.21',
                        ],
                        'related': ['LOCATE', 'LAYER'],
                        'notes': ['Format: AA-RL (columns) + 0-269 (rows), Layers: 100-500']
                    },
                    {
                        'name': 'LOCATE',
                        'desc': 'Find locations on the grid',
                        'syntax': ['LOCATE <name>', 'LOCATE <tile_code>'],
                        'examples': ['LOCATE London', 'LOCATE AA340'],
                        'related': ['TILE', 'LAYER'],
                    },
                ]
            },
            'cloud': {
                'icon': '☁️',
                'title': 'Gmail Cloud Integration',
                'commands': [
                    {
                        'name': 'LOGIN',
                        'desc': 'Authenticate with Gmail (OAuth2)',
                        'syntax': ['LOGIN GMAIL'],
                        'examples': ['LOGIN GMAIL'],
                        'related': ['LOGOUT', 'STATUS'],
                        'notes': ['Opens browser for OAuth2 authentication, tokens stored encrypted']
                    },
                    {
                        'name': 'LOGOUT',
                        'desc': 'Revoke Gmail authentication',
                        'syntax': ['LOGOUT GMAIL'],
                        'examples': ['LOGOUT GMAIL'],
                        'related': ['LOGIN', 'STATUS'],
                    },
                    {
                        'name': 'SYNC',
                        'desc': 'Sync files with Google Drive',
                        'syntax': [
                            'SYNC GMAIL',
                            'SYNC GMAIL STATUS',
                            'SYNC GMAIL ENABLE [mode]',
                            'SYNC GMAIL DISABLE',
                            'SYNC GMAIL CHANGES',
                        ],
                        'examples': [
                            'SYNC GMAIL',
                            'SYNC GMAIL STATUS',
                            'SYNC GMAIL ENABLE auto --interval=300',
                            'SYNC GMAIL CHANGES',
                        ],
                        'related': ['LOGIN', 'CONFIG'],
                        'notes': ['Syncs: missions, workflows, checklists, user config, docs, drafts']
                    },
                    {
                        'name': 'EMAIL',
                        'desc': 'Email operations (list, send, download, tasks)',
                        'syntax': [
                            'EMAIL LIST [query]',
                            'EMAIL SEND <to> <subject>',
                            'EMAIL DOWNLOAD <id>',
                            'EMAIL TASKS [query]',
                        ],
                        'examples': [
                            'EMAIL LIST is:unread',
                            'EMAIL LIST from:boss subject:urgent',
                            'EMAIL TASKS is:unread',
                            'EMAIL DOWNLOAD msg_abc123',
                        ],
                        'related': ['IMPORT', 'SYNC'],
                    },
                    {
                        'name': 'IMPORT',
                        'desc': 'Import emails as notes/checklists/missions (auto-detect)',
                        'syntax': [
                            'IMPORT GMAIL [query]',
                            'IMPORT GMAIL --preview [query]',
                            'IMPORT GMAIL --type=<type> [query]',
                            'IMPORT GMAIL --limit=<n> [query]',
                        ],
                        'examples': [
                            'IMPORT GMAIL is:starred',
                            'IMPORT GMAIL --preview is:unread',
                            'IMPORT GMAIL --type=mission from:boss',
                            'IMPORT GMAIL --limit=5 is:unread',
                        ],
                        'related': ['EMAIL', 'SYNC'],
                        'notes': ['Auto-detect: 3+ tasks=mission, 1-2 tasks=checklist, 0 tasks=note']
                    },
                    {
                        'name': 'QUOTA',
                        'desc': 'Show Gmail/Drive quota usage',
                        'syntax': ['QUOTA GMAIL'],
                        'examples': ['QUOTA GMAIL'],
                        'related': ['STATUS', 'RESOURCE'],
                    },
                    {
                        'name': 'CONFIG',
                        'desc': 'Show or update Gmail sync configuration',
                        'syntax': ['CONFIG GMAIL', 'CONFIG GMAIL SET <key> <value>'],
                        'examples': [
                            'CONFIG GMAIL',
                            'CONFIG GMAIL SET interval 600',
                            'CONFIG GMAIL SET strategy local-wins',
                        ],
                        'related': ['SYNC', 'SETTINGS'],
                        'notes': ['Strategies: newest-wins, local-wins, cloud-wins, manual']
                    },
                ]
            },
            'automation': {
                'icon': '⚙️',
                'title': 'Missions & Automation',
                'commands': [
                    {
                        'name': 'MISSION',
                        'desc': 'Mission control system',
                        'syntax': [
                            'MISSION CREATE <name>',
                            'MISSION LIST',
                            'MISSION START <id>',
                            'MISSION STATUS <id>',
                            'MISSION COMPLETE <id>',
                        ],
                        'examples': [
                            'MISSION CREATE water-collection',
                            'MISSION LIST',
                            'MISSION START mission-001',
                            'MISSION STATUS mission-001',
                        ],
                        'related': ['WORKFLOW', 'SCHEDULE'],
                    },
                    {
                        'name': 'WORKFLOW',
                        'desc': 'Workflow automation (.upy scripts)',
                        'syntax': [
                            'WORKFLOW RUN <file>',
                            'WORKFLOW LIST',
                            'WORKFLOW STATUS',
                            'WORKFLOW STOP <id>',
                        ],
                        'examples': [
                            'WORKFLOW RUN memory/workflows/missions/daily.upy',
                            'WORKFLOW LIST',
                            'WORKFLOW STATUS',
                        ],
                        'related': ['MISSION', 'SCHEDULE'],
                    },
                    {
                        'name': 'SCHEDULE',
                        'desc': 'Task scheduling system',
                        'syntax': [
                            'SCHEDULE ADD <task> --at <time>',
                            'SCHEDULE LIST',
                            'SCHEDULE REMOVE <id>',
                        ],
                        'examples': [
                            'SCHEDULE ADD "SYNC GMAIL" --at 09:00',
                            'SCHEDULE LIST',
                            'SCHEDULE REMOVE task-001',
                        ],
                        'related': ['MISSION', 'WORKFLOW'],
                    },
                ]
            },
            'display': {
                'icon': '🖥️',
                'title': 'Display & Themes',
                'commands': [
                    {
                        'name': 'THEME',
                        'desc': 'Change display theme',
                        'syntax': ['THEME <name>', 'THEME LIST'],
                        'examples': ['THEME foundation', 'THEME galaxy', 'THEME LIST'],
                        'related': ['PANEL', 'COLOR'],
                    },
                    {
                        'name': 'LAYOUT',
                        'desc': 'Screen layout management',
                        'syntax': [
                            'LAYOUT INFO',
                            'LAYOUT MODE <mode>',
                            'LAYOUT RESIZE',
                        ],
                        'examples': [
                            'LAYOUT INFO',
                            'LAYOUT MODE compact',
                            'LAYOUT MODE dashboard',
                        ],
                        'related': ['THEME', 'PANEL'],
                    },
                    {
                        'name': 'COLOR',
                        'desc': 'Color and syntax highlighting settings',
                        'syntax': ['COLOR <preset>', 'COLOR DEMO'],
                        'examples': ['COLOR rainbow', 'COLOR DEMO'],
                        'related': ['THEME', 'LAYOUT'],
                    },
                ]
            },
            'advanced': {
                'icon': '🔬',
                'title': 'Advanced Tools',
                'commands': [
                    {
                        'name': 'DEV',
                        'desc': 'Developer mode (interactive debugging)',
                        'syntax': [
                            'DEV MODE ON',
                            'DEV MODE OFF',
                            'DEV MODE STATUS',
                        ],
                        'examples': ['DEV MODE ON', 'DEV MODE STATUS'],
                        'related': ['LOGS', 'RESOURCE'],
                    },
                    {
                        'name': 'RESOURCE',
                        'desc': 'Resource monitoring (quotas, disk, CPU, memory)',
                        'syntax': [
                            'RESOURCE STATUS',
                            'RESOURCE QUOTA [provider]',
                            'RESOURCE SUMMARY',
                        ],
                        'examples': [
                            'RESOURCE STATUS',
                            'RESOURCE QUOTA gemini',
                            'RESOURCE SUMMARY',
                        ],
                        'related': ['STATUS', 'QUOTA'],
                    },
                    {
                        'name': 'LOGS',
                        'desc': 'View system logs',
                        'syntax': [
                            'LOGS TAIL [lines]',
                            'LOGS SEARCH <query>',
                            'LOGS CLEAR',
                        ],
                        'examples': [
                            'LOGS TAIL 50',
                            'LOGS SEARCH ERROR',
                            'LOGS CLEAR',
                        ],
                        'related': ['DEV', 'STATUS'],
                    },
                ]
            },
        }


# Factory function for easy import
def create_help_handler() -> HelpHandler:
    """Create and return a HelpHandler instance."""
    return HelpHandler()
