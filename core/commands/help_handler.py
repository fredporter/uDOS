"""HELP command handler - Command reference and system help."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler


class HelpHandler(BaseCommandHandler):
    """Handler for HELP command - display command reference."""

    COMMAND_CATEGORIES = {
        "Navigation": ["MAP", "PANEL", "GOTO", "FIND", "TELL"],
        "Inventory": ["BAG", "GRAB", "SPAWN"],
        "NPCs & Dialogue": ["NPC", "TALK", "REPLY"],
        "Files & State": ["SAVE", "LOAD", "NEW", "EDIT"],
        "System & Maintenance": [
            "SHAKEDOWN",
            "REPAIR",
            "BACKUP",
            "RESTORE",
            "TIDY",
            "CLEAN",
            "COMPOST",
            "DESTROY",
            "DEV",
            "DEV MODE",
            "LOGS",
            "RELOAD",
        ],
        "Advanced": ["BINDER", "RUN", "STORY", "SETUP", "DATASET", "CONFIG", "PROVIDER"],
    }

    COMMANDS = {
        "MAP": {
            "description": "Display location tile grid",
            "usage": "MAP [location_id]",
            "example": "MAP L300-BJ10",
            "notes": "Shows 80x30 grid with tiles, objects, sprites",
            "category": "Navigation",
            "syntax": "MAP [--follow] [--zoom N] [location_id]",
        },
        "PANEL": {
            "description": "Show location information panel",
            "usage": "PANEL [location_id]",
            "example": "PANEL",
            "notes": "Displays metadata, timezone, connections",
            "category": "Navigation",
            "syntax": "PANEL [--details] [location_id]",
        },
        "GOTO": {
            "description": "Navigate to connected location",
            "usage": "GOTO [direction|location_id]",
            "example": "GOTO north or GOTO L300-BK10",
            "notes": "Directions: north/south/east/west/up/down (or n/s/e/w/u/d)",
            "category": "Navigation",
            "syntax": "GOTO <north|south|east|west|up|down|location_id>",
        },
        "FIND": {
            "description": "Search for locations by name/type/region",
            "usage": "FIND [query] [--type TYPE] [--region REGION]",
            "example": "FIND tokyo or FIND --type major-city",
            "notes": "Search is case-insensitive",
            "category": "Navigation",
            "syntax": "FIND <query> [--type <type>] [--region <region>] [--limit N]",
        },
        "TELL": {
            "description": "Show rich location description",
            "usage": "TELL [location_id]",
            "example": "TELL",
            "notes": "Displays full description with connections",
            "category": "Navigation",
            "syntax": "TELL [--verbose] [location_id]",
        },
        "BAG": {
            "description": "Manage character inventory",
            "usage": "BAG [action] [item] [quantity]",
            "example": "BAG list or BAG add sword 1",
            "notes": "Actions: list, add, remove, drop, equip",
            "category": "Inventory",
            "syntax": "BAG <list|add|remove|drop|equip> [item] [quantity]",
        },
        "GRAB": {
            "description": "Pick up objects at current location",
            "usage": "GRAB [object_name]",
            "example": "GRAB sword",
            "notes": "Adds objects to your inventory",
            "category": "Inventory",
            "syntax": "GRAB <object_name> [quantity]",
        },
        "SPAWN": {
            "description": "Create objects/sprites at locations",
            "usage": "SPAWN [type] [char] [name] at [location] [cell]",
            "example": "SPAWN object key at L300-BJ10 AA00",
            "notes": "Types: object, sprite",
            "category": "Inventory",
            "syntax": "SPAWN <object|sprite> <char> <name> at <location_id> <cell>",
        },
        "SAVE": {
            "description": "Save file (editor) or game state",
            "usage": "SAVE [path] | SAVE GAME [slot_name]",
            "example": "SAVE notes.md or SAVE GAME mysave",
            "notes": "Opens editor for files or saves game state when using SAVE GAME",
            "category": "Files & State",
            "syntax": "SAVE [path] | SAVE GAME <slot_name> [--force]",
        },
        "LOAD": {
            "description": "Load file (editor) or game state",
            "usage": "LOAD [path] | LOAD GAME [slot_name]",
            "example": "LOAD notes.md or LOAD GAME mysave",
            "notes": "Opens editor for files or restores game state when using LOAD GAME",
            "category": "Files & State",
            "syntax": "LOAD [path] | LOAD GAME <slot_name> [--force]",
        },
        "NEW": {
            "description": "Create a new markdown file in /memory",
            "usage": "NEW [name]",
            "example": "NEW daily-notes",
            "notes": "Creates/open /memory/<name>.md in editor",
            "category": "Files & State",
            "syntax": "NEW <name> [--no-edit] [--template <type>]",
        },
        "EDIT": {
            "description": "Edit a markdown file in /memory",
            "usage": "EDIT [path]",
            "example": "EDIT notes.md",
            "notes": "Opens editor for /memory/<path>",
            "category": "Files & State",
            "syntax": "EDIT <path> [--readonly]",
        },
        "HELP": {
            "description": "Display command reference",
            "usage": "HELP [command]",
            "example": "HELP GOTO or HELP",
            "notes": "Shows all commands or specific command details",
            "category": "System & Maintenance",
            "syntax": "HELP [<command>] | HELP CATEGORY <category> | HELP SEARCH <query>",
        },
        "SHAKEDOWN": {
            "description": "System validation and diagnostics",
            "usage": "SHAKEDOWN",
            "example": "SHAKEDOWN",
            "notes": "Checks core components, handlers, locations",
            "category": "System & Maintenance",
            "syntax": "SHAKEDOWN [--verbose] [--focus <module>]",
        },
        "REPAIR": {
            "description": "Self-healing and system maintenance",
            "usage": "REPAIR [--pull|--install|--check]",
            "example": "REPAIR --pull",
            "notes": "Git sync, installer check, dependency verification",
            "category": "System & Maintenance",
            "syntax": "REPAIR [--pull] [--install] [--check] [--dry-run]",
        },
        "BACKUP": {
            "description": "Create a workspace snapshot in .backup",
            "usage": "BACKUP [current|+subfolders|workspace|all] [label]",
            "example": "BACKUP workspace pre-clean",
            "notes": "Creates a tar.gz backup in the target .backup folder",
            "category": "System & Maintenance",
            "syntax": "BACKUP <current|+subfolders|workspace|all> [label] [--compress]",
        },
        "RESTORE": {
            "description": "Restore from the latest backup in .backup",
            "usage": "RESTORE [current|+subfolders|workspace|all] [--force]",
            "example": "RESTORE workspace",
            "notes": "Restores the most recent backup (use --force to overwrite)",
            "category": "System & Maintenance",
            "syntax": "RESTORE <current|+subfolders|workspace|all> [--force] [--date YYYY-MM-DD]",
        },
        "TIDY": {
            "description": "Organize junk files into .archive",
            "usage": "TIDY [current|+subfolders|workspace|all]",
            "example": "TIDY workspace",
            "notes": "Moves stray/temporary files into .archive (no deletion)",
            "category": "System & Maintenance",
            "syntax": "TIDY <current|+subfolders|workspace|all> [--dry-run]",
        },
        "CLEAN": {
            "description": "Reset workspace to default state (archive extras)",
            "usage": "CLEAN [current|+subfolders|workspace|all]",
            "example": "CLEAN workspace",
            "notes": "Moves non-default files into .archive (no deletion)",
            "category": "System & Maintenance",
            "syntax": "CLEAN <current|+subfolders|workspace|all> [--aggressive] [--dry-run]",
        },
        "COMPOST": {
            "description": "Collect .archive/.backup/.tmp into /.compost",
            "usage": "COMPOST [current|+subfolders|workspace|all]",
            "example": "COMPOST all",
            "notes": "Moves archive/backup/temp folders into repo /.compost",
            "category": "System & Maintenance",
            "syntax": "COMPOST <current|+subfolders|workspace|all> [--compress]",
        },
        "DESTROY": {
            "description": "Wipe and reinstall (Dev TUI only)",
            "usage": "DESTROY",
            "example": "DESTROY",
            "notes": "Use Dev TUI to run DESTROY with confirmation",
            "category": "System & Maintenance",
            "syntax": "DESTROY [--confirm]",
        },
        "DEV": {
            "description": "Access development mode (Wizard-controlled)",
            "usage": "DEV",
            "example": "DEV",
            "notes": "Shows dev mode status. Start Wizard server to activate dev mode",
            "category": "System & Maintenance",
            "syntax": "DEV | DEV MODE",
        },
        "DEV MODE": {
            "description": "Manage development mode via Wizard Server",
            "usage": "DEV MODE",
            "example": "DEV MODE",
            "notes": "Dev mode is controlled from Wizard Server TUI. Use: WIZARD start → then DEV ON/OFF in Wizard console. Goblin experimental server runs on port 8767 when enabled",
            "category": "System & Maintenance",
            "syntax": "DEV [MODE]",
        },
        "LOGS": {
            "description": "View and search unified system logs",
            "usage": "LOGS [options]",
            "example": "LOGS or LOGS --wizard or LOGS --level ERROR",
            "notes": "View aggregated logs from Core, Wizard, Goblin, Extensions. Files stored in memory/logs/",
            "category": "System & Maintenance",
            "syntax": "LOGS [--last N] [--core|--wizard|--goblin] [--level LEVEL] [--category CATEGORY] [--stats] [--clear] [help]",
        },
        "NPC": {
            "description": "List NPCs at current or specified location",
            "usage": "NPC [location_id]",
            "example": "NPC or NPC L300-BJ10",
            "notes": "Shows NPCs with name, role, disposition, and dialogue state",
            "category": "NPCs & Dialogue",
            "syntax": "NPC [location_id] [--filter <role>]",
        },
        "TALK": {
            "description": "Start conversation with NPC",
            "usage": "TALK [npc_name]",
            "example": "TALK Kenji or TALK Elder Tanaka",
            "notes": "Initiates dialogue tree, presents conversation options",
            "category": "NPCs & Dialogue",
            "syntax": "TALK <npc_name> [--skip-intro]",
        },
        "REPLY": {
            "description": "Select dialogue option during conversation",
            "usage": "REPLY [option_number]",
            "example": "REPLY 1 or REPLY 2",
            "notes": "Continue conversation by choosing numbered option",
            "category": "NPCs & Dialogue",
            "syntax": "REPLY <option_number>",
        },
        "CONFIG": {
            "description": "Manage Wizard configuration",
            "usage": "CONFIG [SHOW|LIST|EDIT <file>|SETUP]",
            "example": "CONFIG SHOW or CONFIG EDIT wizard.json",
            "notes": "Requires Wizard Server running on port 8765",
            "category": "Advanced",
            "syntax": "CONFIG <SHOW|LIST|EDIT|SETUP> [file] [--validate]",
        },
        "PROVIDER": {
            "description": "Manage AI/service providers",
            "usage": "PROVIDER [LIST|STATUS <id>|ENABLE <id>|DISABLE <id>|SETUP <id>]",
            "example": "PROVIDER LIST or PROVIDER ENABLE github",
            "notes": "Requires Wizard Server running on port 8765",
            "category": "Advanced",
            "syntax": "PROVIDER <LIST|STATUS|ENABLE|DISABLE|SETUP> [<id>] [--test]",
        },
        "STORY": {
            "description": "Run story format files",
            "usage": "STORY [file] | STORY PARSE <file> | STORY NEW <name>",
            "example": "STORY new my-onboarding or STORY my-onboarding",
            "notes": "Runs -story.md files from memory/story/ using the TS runtime",
            "category": "Advanced",
            "syntax": "STORY [<file>] | STORY PARSE <file> | STORY NEW <name>",
        },
        "SETUP": {
            "description": "View setup profiles (Wizard-backed)",
            "usage": "SETUP [--story|--wizard]",
            "example": "SETUP or SETUP --story",
            "notes": "Requires Wizard Server running on port 8765",
            "category": "Advanced",
            "syntax": "SETUP [--story|--wizard]",
        },
        "BINDER": {
            "description": "Core binder operations",
            "usage": "BINDER [PICK|COMPILE <id>|CHAPTERS <id>|HELP]",
            "example": "BINDER PICK or BINDER COMPILE my-binder markdown json",
            "notes": "Compile binder outputs and browse files",
            "category": "Advanced",
            "syntax": "BINDER <PICK|COMPILE|CHAPTERS|HELP> [<id>] [--output <dir>]",
        },
        "RUN": {
            "description": "Execute TS markdown runtime script",
            "usage": "RUN <file> [section_id] | RUN PARSE <file>",
            "example": "RUN core/examples/sample.md intro",
            "notes": "Executes a markdown script or lists parsed sections",
            "category": "Advanced",
            "syntax": "RUN <file> [section_id] | RUN PARSE <file> [--verbose]",
        },
        "DATASET": {
            "description": "List and validate datasets",
            "usage": "DATASET [LIST|VALIDATE <id>|BUILD <id>|REGEN <id>]",
            "example": "DATASET LIST or DATASET REGEN locations",
            "notes": "Validates and regenerates datasets for 80x30 layers",
            "category": "Advanced",
            "syntax": "DATASET <LIST|VALIDATE|BUILD|REGEN> [<id>] [--force]",
        },
    }

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle HELP command.

        Args:
            command: Command name (HELP)
            params: [help_topic] (optional: command_name, CATEGORY, SYNTAX, etc.)
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with help text
        """
        if not params:
            return self._show_all_commands()

        main_arg = params[0].upper()

        # Handle HELP CATEGORY <category>
        if main_arg == "CATEGORY" and len(params) > 1:
            return self._show_category(params[1])

        # Handle HELP SYNTAX <command>
        if main_arg == "SYNTAX" and len(params) > 1:
            return self._show_syntax(params[1])

        # Handle HELP <command>
        if main_arg not in self.COMMANDS:
            # Check if it's a partial match
            matching = [c for c in self.COMMANDS.keys() if c.startswith(main_arg)]
            if len(matching) == 1:
                main_arg = matching[0]
            else:
                return {
                    "status": "error",
                    "message": f"Unknown command: {main_arg}",
                    "hint": "Try 'HELP' for all commands or 'HELP CATEGORY Navigation'",
                    "available": list(self.COMMANDS.keys())[:5],
                }

        return self._show_command_help(main_arg)

    def _show_all_commands(self) -> Dict:
        """Show all available commands grouped by category."""
        box_line = "+" + "-" * 69 + "+"
        title = "uDOS Command Reference (v1.1.0)"
        title_line = f"| {title:<67}|"
        
        help_text = f"{box_line}\n{title_line}\n{box_line}\n\n"
        
        # Build output by category
        for category in [
            "Navigation", "Inventory", "NPCs & Dialogue", "Files & State",
            "System & Maintenance", "Advanced"
        ]:
            if category not in self.COMMAND_CATEGORIES:
                continue
            
            commands = self.COMMAND_CATEGORIES[category]
            help_text += f"{category}:\n"
            
            for cmd in commands:
                if cmd in self.COMMANDS:
                    info = self.COMMANDS[cmd]
                    desc = info.get("description", "")
                    # Format: "  COMMAND      - description (usage hint)"
                    usage_hint = info.get("usage", "").split("[")[0].strip()
                    help_text += f"  {cmd:<12} - {desc:<45}\n"
            
            help_text += "\n"
        
        # Add usage instructions
        help_text += (
            "Usage:\n"
            "  HELP [command]              Show detailed help for a command\n"
            "  HELP CATEGORY <category>    List commands in a category\n"
            "  HELP SYNTAX <command>       Show full syntax with options\n"
            "\n"
            "Examples:\n"
            "  HELP GOTO                   Detailed help for GOTO\n"
            "  HELP CATEGORY Navigation    All navigation commands\n"
            "  HELP SYNTAX SAVE            Full SAVE syntax with options\n"
        )

        return {
            "status": "success",
            "message": f"Found {len(self.COMMANDS)} commands",
            "help": help_text.strip(),
            "commands": list(self.COMMANDS.keys()),
            "categories": list(self.COMMAND_CATEGORIES.keys()),
        }

    def _show_command_help(self, cmd_name: str) -> Dict:
        """Show detailed help for a specific command."""
        cmd_info = self.COMMANDS[cmd_name]
        
        box_line = "+" + "-" * 69 + "+"
        title_line = f"| {cmd_name:<67}|"
        
        help_text = (
            f"{box_line}\n"
            f"{title_line}\n"
            f"{box_line}\n\n"
            f"Category:   {cmd_info.get('category', 'Uncategorized')}\n\n"
            f"Description:\n"
            f"  {cmd_info['description']}\n\n"
            f"Syntax:\n"
            f"  {cmd_info.get('syntax', cmd_info['usage'])}\n\n"
            f"Usage:\n"
            f"  {cmd_info['usage']}\n\n"
            f"Example:\n"
            f"  {cmd_info['example']}\n\n"
            f"Notes:\n"
            f"  {cmd_info['notes']}\n"
        )

        return {
            "status": "success",
            "message": f"Help for {cmd_name}",
            "command": cmd_name,
            "help": help_text.strip(),
            "category": cmd_info.get("category", "Uncategorized"),
            "description": cmd_info["description"],
            "syntax": cmd_info.get("syntax", cmd_info["usage"]),
            "usage": cmd_info["usage"],
            "example": cmd_info["example"],
        }

    def _show_category(self, category: str) -> Dict:
        """Show all commands in a specific category."""
        # Find matching category (case-insensitive)
        matching_cat = None
        for cat in self.COMMAND_CATEGORIES.keys():
            if cat.upper() == category.upper():
                matching_cat = cat
                break

        if not matching_cat:
            available = list(self.COMMAND_CATEGORIES.keys())
            return {
                "status": "error",
                "message": f"Unknown category: {category}",
                "available_categories": available,
            }

        commands = self.COMMAND_CATEGORIES[matching_cat]
        
        box_line = "+" + "-" * 69 + "+"
        title = f"{matching_cat} Commands"
        title_line = f"| {title:<67}|"
        
        help_text = f"{box_line}\n{title_line}\n{box_line}\n\n"

        for cmd in commands:
            if cmd in self.COMMANDS:
                info = self.COMMANDS[cmd]
                help_text += f"{cmd}\n"
                help_text += f"  {info['description']}\n"
                help_text += f"  Syntax: {info.get('syntax', info['usage'])}\n\n"

        help_text += (
            "Tip: Use 'HELP <command>' for detailed help on any command\n"
            f"Example: HELP {commands[0] if commands else 'MAP'}\n"
        )

        return {
            "status": "success",
            "message": f"{matching_cat} commands",
            "category": matching_cat,
            "help": help_text.strip(),
            "commands": commands,
        }

    def _show_syntax(self, cmd_name: str) -> Dict:
        """Show syntax reference for a specific command."""
        cmd_upper = cmd_name.upper()
        
        if cmd_upper not in self.COMMANDS:
            # Try partial match
            matching = [c for c in self.COMMANDS.keys() if c.startswith(cmd_upper)]
            if len(matching) == 1:
                cmd_upper = matching[0]
            else:
                return {
                    "status": "error",
                    "message": f"Unknown command: {cmd_name}",
                }

        cmd_info = self.COMMANDS[cmd_upper]
        syntax = cmd_info.get("syntax", cmd_info["usage"])
        
        box_line = "+" + "-" * 69 + "+"
        syntax_line = f"| {syntax:<67}|"
        
        help_text = (
            f"{box_line}\n"
            f"{syntax_line}\n"
            f"{box_line}\n\n"
            f"{cmd_info['description']}\n\n"
            f"Usage: {cmd_info['usage']}\n\n"
            f"Example:\n"
            f"  {cmd_info['example']}\n\n"
            f"Notes:\n"
            f"  {cmd_info['notes']}\n"
        )

        return {
            "status": "success",
            "message": f"Syntax help for {cmd_upper}",
            "command": cmd_upper,
            "syntax": syntax,
            "help": help_text.strip(),
        }
