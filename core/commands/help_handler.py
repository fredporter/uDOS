"""HELP command handler - Command reference and system help."""

from typing import List, Dict
from core.commands.base import BaseCommandHandler


class HelpHandler(BaseCommandHandler):
    """Handler for HELP command - display command reference."""

    COMMANDS = {
        "MAP": {
            "description": "Display location tile grid",
            "usage": "MAP [location_id]",
            "example": "MAP L300-BJ10",
            "notes": "Shows 80×24 grid with tiles, objects, sprites",
        },
        "PANEL": {
            "description": "Show location information panel",
            "usage": "PANEL [location_id]",
            "example": "PANEL",
            "notes": "Displays metadata, coordinates, timezone, connections",
        },
        "GOTO": {
            "description": "Navigate to connected location",
            "usage": "GOTO [direction|location_id]",
            "example": "GOTO north or GOTO L300-BK10",
            "notes": "Directions: north/south/east/west/up/down (or n/s/e/w/u/d)",
        },
        "FIND": {
            "description": "Search for locations by name/type/region",
            "usage": "FIND [query] [--type TYPE] [--region REGION]",
            "example": "FIND tokyo or FIND --type major-city",
            "notes": "Search is case-insensitive",
        },
        "TELL": {
            "description": "Show rich location description",
            "usage": "TELL [location_id]",
            "example": "TELL",
            "notes": "Displays full description with coordinates and connections",
        },
        "BAG": {
            "description": "Manage character inventory",
            "usage": "BAG [action] [item] [quantity]",
            "example": "BAG list or BAG add sword 1",
            "notes": "Actions: list, add, remove, drop, equip",
        },
        "GRAB": {
            "description": "Pick up objects at current location",
            "usage": "GRAB [object_name]",
            "example": "GRAB sword",
            "notes": "Adds objects to your inventory",
        },
        "SPAWN": {
            "description": "Create objects/sprites at locations",
            "usage": "SPAWN [type] [char] [name] at [location] [cell]",
            "example": "SPAWN object 🗝️ key at L300-BJ10 AA00",
            "notes": "Types: object, sprite",
        },
        "SAVE": {
            "description": "Save game state",
            "usage": "SAVE [slot_name]",
            "example": "SAVE mysave or SAVE (quicksave)",
            "notes": "Saves location, inventory, and player stats",
        },
        "LOAD": {
            "description": "Load saved game state",
            "usage": "LOAD [slot_name]",
            "example": "LOAD mysave",
            "notes": "Restores from save file",
        },
        "HELP": {
            "description": "Display command reference",
            "usage": "HELP [command]",
            "example": "HELP GOTO or HELP",
            "notes": "Shows all commands or specific command details",
        },
        "SHAKEDOWN": {
            "description": "System validation and diagnostics",
            "usage": "SHAKEDOWN",
            "example": "SHAKEDOWN",
            "notes": "Checks core components, handlers, locations",
        },
        "REPAIR": {
            "description": "Self-healing and system maintenance",
            "usage": "REPAIR [--pull|--install|--check]",
            "example": "REPAIR --pull",
            "notes": "Git sync, installer check, dependency verification",
        },
        "NPC": {
            "description": "List NPCs at current or specified location",
            "usage": "NPC [location_id]",
            "example": "NPC or NPC L300-BJ10",
            "notes": "Shows NPCs with name, role, disposition, and dialogue state",
        },
        "TALK": {
            "description": "Start conversation with NPC",
            "usage": "TALK [npc_name]",
            "example": "TALK Kenji or TALK Elder Tanaka",
            "notes": "Initiates dialogue tree, presents conversation options",
        },
        "REPLY": {
            "description": "Select dialogue option during conversation",
            "usage": "REPLY [option_number]",
            "example": "REPLY 1 or REPLY 2",
            "notes": "Continue conversation by choosing numbered option",
        },
        "CONFIG": {
            "description": "Manage Wizard configuration",
            "usage": "CONFIG [SHOW|LIST|EDIT <file>|SETUP]",
            "example": "CONFIG SHOW or CONFIG EDIT wizard.json",
            "notes": "View status, list config files, edit configs, run provider setup",
        },
        "PROVIDER": {
            "description": "Manage AI/service providers",
            "usage": "PROVIDER [LIST|STATUS <id>|ENABLE <id>|DISABLE <id>|SETUP <id>]",
            "example": "PROVIDER LIST or PROVIDER ENABLE github",
            "notes": "Configure AI providers (ollama, github, openai, etc.)",
        },
    }

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle HELP command.

        Args:
            command: Command name (HELP)
            params: [command_name] (optional, shows specific command or all)
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with help text
        """
        if not params:
            return self._show_all_commands()

        cmd_name = params[0].upper()

        if cmd_name not in self.COMMANDS:
            return {
                "status": "error",
                "message": f"Unknown command: {cmd_name}",
                "available": list(self.COMMANDS.keys()),
            }

        cmd_info = self.COMMANDS[cmd_name]

        help_text = f"""
╔═══════════════════════════════════════════════════════════╗
║ {cmd_name:<57}║
╚═══════════════════════════════════════════════════════════╝

📖 {cmd_info['description']}

Usage:
  {cmd_info['usage']}

Example:
  {cmd_info['example']}

Notes:
  {cmd_info['notes']}
"""

        return {
            "status": "success",
            "command": cmd_name,
            "help": help_text.strip(),
            "description": cmd_info["description"],
            "usage": cmd_info["usage"],
            "example": cmd_info["example"],
        }

    def _show_all_commands(self) -> Dict:
        """Show all available commands."""
        command_list = []
        for cmd, info in sorted(self.COMMANDS.items()):
            command_list.append(f"  {cmd:<12} - {info['description']}")

        help_text = f"""
╔═══════════════════════════════════════════════════════════╗
║ uDOS Command Reference (v1.1.0)                           ║
╚═══════════════════════════════════════════════════════════╝

Navigation:
  MAP          - Display location tile grid
  PANEL        - Show location information
  GOTO         - Navigate to connected location
  FIND         - Search for locations

Information:
  TELL         - Show rich location description
  HELP         - Display command reference

Inventory:
  BAG          - Manage character inventory
  GRAB         - Pick up objects at location
  SPAWN        - Create objects/sprites

NPCs & Dialogue:
  NPC          - List NPCs at location
  TALK         - Start conversation with NPC
  REPLY        - Select dialogue option

State:
  SAVE         - Save game state
  LOAD         - Load saved game state

System:
  SHAKEDOWN    - System validation
  REPAIR       - Self-healing and maintenance

Type 'HELP [command]' for detailed help.
Example: HELP GOTO or HELP TALK
"""

        return {
            "status": "success",
            "help": help_text.strip(),
            "commands": list(self.COMMANDS.keys()),
        }
