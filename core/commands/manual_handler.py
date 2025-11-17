"""
MANUAL Command Handler - v1.0.22
Quick command reference and examples

Commands:
  MANUAL
  MANUAL <command>
  MANUAL --examples
  MANUAL --search <query>

Author: uDOS Development Team
Version: 1.0.22
"""

from typing import List, Dict, Optional


class ManualHandler:
    """Handler for MANUAL commands - quick reference"""

    def __init__(self, viewport=None, logger=None):
        """Initialize ManualHandler"""
        self.viewport = viewport
        self.logger = logger

        # Command manual database
        self.manuals = self._build_manuals()

    def handle(self, command: str, args: List[str]) -> str:
        """Route MANUAL commands to appropriate handlers"""

        if not command or command == "HELP":
            return self._show_help()

        if command == "--examples":
            return self._show_examples()

        if command == "--search":
            if not args:
                return "❌ Usage: MANUAL --search <query>"
            query = " ".join(args)
            return self._search_manual(query)

        # Show manual for specific command
        cmd = command.upper()
        return self._show_manual(cmd)

    def _build_manuals(self) -> Dict[str, Dict]:
        """Build command manual database"""
        return {
            "LOAD": {
                "name": "LOAD",
                "category": "Files",
                "syntax": "LOAD <filename>",
                "description": "Load and display a file",
                "options": [
                    "--raw     Show file without processing",
                    "--hex     Display in hexadecimal format",
                    "--json    Parse and format JSON"
                ],
                "examples": [
                    "LOAD data.txt           # Load text file",
                    "LOAD config.json        # Load JSON",
                    "LOAD --raw binary.dat   # Load as raw data"
                ],
                "related": ["SAVE", "FILES", "CD"]
            },
            "SAVE": {
                "name": "SAVE",
                "category": "Files",
                "syntax": "SAVE <filename>",
                "description": "Save current content to file",
                "options": [
                    "--append  Append to file instead of overwrite",
                    "--backup  Create backup before saving"
                ],
                "examples": [
                    "SAVE output.txt         # Save to file",
                    "SAVE --append log.txt   # Append to log"
                ],
                "related": ["LOAD", "FILES", "EXPORT"]
            },
            "GUIDE": {
                "name": "GUIDE",
                "category": "Knowledge",
                "syntax": "GUIDE [options] [guide-name]",
                "description": "Interactive guide viewer with step-through tutorials",
                "options": [
                    "LIST               List all guides",
                    "SEARCH <query>     Search guides",
                    "START <name>       Start a guide",
                    "NEXT               Next step",
                    "PREV               Previous step",
                    "JUMP <n>           Jump to step n",
                    "COMPLETE           Mark as complete",
                    "PROGRESS           Show progress",
                    "RESET <name>       Reset progress"
                ],
                "examples": [
                    "GUIDE LIST                    # List all guides",
                    "GUIDE START water-purif       # Start guide",
                    "GUIDE NEXT                    # Next step",
                    "GUIDE PROGRESS                # View progress"
                ],
                "related": ["DIAGRAM", "DOC", "HANDBOOK"]
            },
            "DIAGRAM": {
                "name": "DIAGRAM",
                "category": "Knowledge",
                "syntax": "DIAGRAM [options] [diagram-name]",
                "description": "ASCII art library browser",
                "options": [
                    "LIST               List all diagrams",
                    "SEARCH <query>     Search diagrams",
                    "SHOW <name>        Display diagram",
                    "RENDER <name>      Render with effects",
                    "EXTRACT <name>     Extract to clipboard",
                    "VIEWPORT           Show viewport info",
                    "COPY <name>        Copy to memory",
                    "EXPORT <name>      Export to file"
                ],
                "examples": [
                    "DIAGRAM LIST                  # List diagrams",
                    "DIAGRAM SHOW knots            # Show knot diagram",
                    "DIAGRAM RENDER water-cycle    # Render diagram",
                    "DIAGRAM EXPORT shelter        # Export to file"
                ],
                "related": ["GUIDE", "PANEL", "GRID"]
            },
            "DOC": {
                "name": "DOC",
                "category": "Help",
                "syntax": "DOC [topic]",
                "description": "Browse uDOS documentation",
                "options": [
                    "INDEX              Show complete index",
                    "LIST               List all documents",
                    "SEARCH <query>     Search documentation"
                ],
                "examples": [
                    "DOC                          # Documentation home",
                    "DOC getting started          # Show guide",
                    "DOC SEARCH commands          # Search docs"
                ],
                "related": ["MANUAL", "HANDBOOK", "HELP"]
            },
            "GRID": {
                "name": "GRID",
                "category": "Graphics",
                "syntax": "GRID [options]",
                "description": "Manage global grid system",
                "options": [
                    "SHOW               Display current grid",
                    "SET <x> <y>        Set current position",
                    "SAVE <name>        Save grid state",
                    "LOAD <name>        Load grid state"
                ],
                "examples": [
                    "GRID SHOW                    # Show grid",
                    "GRID SET AA 001              # Set position",
                    "GRID SAVE mybuild            # Save state"
                ],
                "related": ["PANEL", "TIZO", "MAP"]
            },
            "PANEL": {
                "name": "PANEL",
                "category": "Graphics",
                "syntax": "PANEL <block-code>",
                "description": "Display teletext graphics blocks",
                "options": [
                    "LIST               List all blocks",
                    "INFO <code>        Block information",
                    "DEMO               Show all blocks"
                ],
                "examples": [
                    "PANEL LIST                   # List blocks",
                    "PANEL ▀                      # Show upper block",
                    "PANEL DEMO                   # Demo all"
                ],
                "related": ["GRID", "DIAGRAM", "THEME"]
            },
            "HELP": {
                "name": "HELP",
                "category": "Help",
                "syntax": "HELP [command]",
                "description": "Display help information",
                "options": [
                    "ALL                Show all commands",
                    "TOPICS             Show help topics"
                ],
                "examples": [
                    "HELP                         # General help",
                    "HELP LOAD                    # Command help",
                    "HELP ALL                     # All commands"
                ],
                "related": ["DOC", "MANUAL", "HANDBOOK"]
            }
        }

    def _show_help(self) -> str:
        """Display MANUAL command help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  MANUAL - Quick Command Reference                              │
└─────────────────────────────────────────────────────────────────┘

📖 Fast reference for uDOS commands

USAGE:
  MANUAL                 Show command categories
  MANUAL <command>       Show command manual page
  MANUAL --examples      Show example commands
  MANUAL --search <q>    Search command reference

EXAMPLES:
  MANUAL LOAD            Show LOAD command manual
  MANUAL GUIDE           Show GUIDE command help
  MANUAL --examples      Browse examples
  MANUAL --search file   Search for 'file'

CATEGORIES:
  • Files       File operations (LOAD, SAVE, FILES, CD)
  • Knowledge   Guides and diagrams (GUIDE, DIAGRAM)
  • Graphics    Grid and panels (GRID, PANEL, TIZO)
  • Help        Documentation (DOC, MANUAL, HANDBOOK)
  • System      Core commands (CONFIG, THEME, REPAIR)

See also: DOC, HANDBOOK, HELP
"""

    def _show_examples(self) -> str:
        """Show example commands"""
        output = ["", "📚 Command Examples", "═" * 60, ""]

        categories = {}
        for cmd_data in self.manuals.values():
            cat = cmd_data.get("category", "Other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cmd_data)

        for category, commands in sorted(categories.items()):
            output.append(f"▸ {category}")
            output.append("─" * 60)
            for cmd_data in commands:
                output.append(f"\n{cmd_data['name']}:")
                for example in cmd_data.get("examples", []):
                    output.append(f"  {example}")
            output.append("")

        return "\n".join(output)

    def _search_manual(self, query: str) -> str:
        """Search command manuals"""
        query_lower = query.lower()
        results = []

        for cmd_name, cmd_data in self.manuals.items():
            # Search in name, description, syntax, examples
            searchable = [
                cmd_name.lower(),
                cmd_data.get("description", "").lower(),
                cmd_data.get("syntax", "").lower(),
                " ".join(cmd_data.get("examples", [])).lower()
            ]

            if any(query_lower in s for s in searchable):
                results.append((cmd_name, cmd_data))

        if not results:
            return f"\n❌ No commands found matching '{query}'\n"

        output = ["", f"🔍 Commands matching '{query}'", "═" * 60, ""]

        for cmd_name, cmd_data in results:
            output.append(f"\n{cmd_name} - {cmd_data.get('description', '')}")
            output.append(f"  Usage: {cmd_data.get('syntax', '')}")

        output.append("")
        output.append(f"✅ Found {len(results)} commands")
        output.append("")
        output.append("Usage: MANUAL <command> for details")

        return "\n".join(output)

    def _show_manual(self, cmd: str) -> str:
        """Show manual page for specific command"""

        if cmd not in self.manuals:
            return f"\n❌ No manual page for '{cmd}'\n\nUse 'MANUAL' to see all commands\n"

        cmd_data = self.manuals[cmd]
        output = ["", "═" * 60]
        output.append(f"  {cmd_data['name']} - {cmd_data.get('description', '')}")
        output.append("═" * 60)
        output.append("")

        # Syntax
        output.append("SYNTAX:")
        output.append(f"  {cmd_data.get('syntax', '')}")
        output.append("")

        # Options
        if cmd_data.get("options"):
            output.append("OPTIONS:")
            for opt in cmd_data["options"]:
                output.append(f"  {opt}")
            output.append("")

        # Examples
        if cmd_data.get("examples"):
            output.append("EXAMPLES:")
            for example in cmd_data["examples"]:
                output.append(f"  {example}")
            output.append("")

        # Related
        if cmd_data.get("related"):
            output.append("SEE ALSO:")
            output.append(f"  {', '.join(cmd_data['related'])}")
            output.append("")

        return "\n".join(output)


def create_handler(viewport=None, logger=None):
    """Factory function to create handler"""
    return ManualHandler(viewport=viewport, logger=logger)
