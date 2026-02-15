"""
uDOS Core Autocomplete Service

Intelligent command suggestion engine for the active v1.3.16 command set.
"""

from typing import List, Dict, Optional


class AutocompleteService:
    """Autocomplete service for Core TUI commands"""

    def __init__(self):
        """Initialize with Core's command set"""
        self.core_commands = {
            "MAP": {
                "description": "Display map of current area",
                "options": [],
            },
            "PANEL": {
                "description": "Manage display panels",
                "options": ["MAIN", "LEFT", "RIGHT", "TOP", "BOTTOM"],
            },
            "GOTO": {
                "description": "Navigate to a location",
                "options": [],
            },
            "FIND": {
                "description": "Search for something",
                "options": [],
            },
            "TELL": {
                "description": "Display information",
                "options": [],
            },
            "HELP": {
                "description": "Show command help",
                "options": ["SEARCH", "COMMANDS"],
            },
            "BAG": {
                "description": "View inventory",
                "options": ["LIST", "ADD", "REMOVE"],
            },
            "GRAB": {
                "description": "Pick up item",
                "options": [],
            },
            "SPAWN": {
                "description": "Create new item",
                "options": [],
            },
            "SAVE": {
                "description": "Save file or state slot",
                "options": ["--state"],
            },
            "LOAD": {
                "description": "Load file or state slot",
                "options": ["--state"],
            },
            "HEALTH": {
                "description": "Run offline stdlib health checks",
                "options": ["CHECK", "release-gates", "--format", "json", "text"],
            },
            "VERIFY": {
                "description": "Run TS/runtime verification checks",
                "options": [],
            },
            "OK": {
                "description": "Local Vibe helpers",
                "options": ["LOCAL", "EXPLAIN", "DIFF", "PATCH", "ROUTE", "VIBE", "FALLBACK"],
            },
            "SCHEDULER": {
                "description": "Manage scheduled tasks",
                "options": ["LIST", "RUN", "LOG"],
            },
            "SCRIPT": {
                "description": "Manage system scripts",
                "options": ["LIST", "RUN", "LOG"],
            },
            "REPAIR": {
                "description": "Fix system issues",
                "options": ["--pull", "--upgrade-all"],
            },
            "NPC": {
                "description": "NPC management",
                "options": ["LIST", "CREATE", "EDIT", "DELETE"],
            },
            "SEND": {
                "description": "Unified dialogue command",
                "options": [],
            },
            "PLACE": {
                "description": "Unified workspace/tag/location command",
                "options": ["LIST", "READ", "WRITE", "DELETE", "INFO", "TAG", "FIND", "TAGS", "SEARCH"],
            },
            "READ": {
                "description": "Parse TS markdown runtime files",
                "options": ["--ts"],
            },
            "TOKEN": {
                "description": "Generate local tokens",
                "options": ["GEN", "--len"],
            },
            "GHOST": {
                "description": "Show Ghost Mode status",
                "options": [],
            },
            "WIZARD": {
                "description": "Wizard server management",
                "options": ["START", "STOP", "STATUS", "REBUILD", "CHECK", "PROV", "INTEG"],
            },
        }

        # Common global options
        self.common_options = ["--help", "--verbose", "--quiet", "--debug"]

    def get_completions(self, text: str, max_results: int = 10) -> List[str]:
        """
        Get command completions for partial input.

        Args:
            text: Partial command text
            max_results: Max suggestions to return

        Returns:
            List of completion suggestions
        """
        if not text:
            # Return all commands
            return sorted(self.core_commands.keys())[:max_results]

        text_upper = text.upper()
        suggestions = []

        # Exact prefix matches first
        for cmd in sorted(self.core_commands.keys()):
            if cmd.startswith(text_upper):
                suggestions.append(cmd)
                if len(suggestions) >= max_results:
                    break

        # Fuzzy matches if needed
        if len(suggestions) < max_results:
            for cmd in sorted(self.core_commands.keys()):
                if cmd not in suggestions and text_upper in cmd:
                    suggestions.append(cmd)
                    if len(suggestions) >= max_results:
                        break

        return suggestions

    def get_options(self, command: str) -> List[str]:
        """Get available options for a command"""
        cmd_upper = command.upper()
        cmd_data = self.core_commands.get(cmd_upper, {})
        return cmd_data.get("options", []) + self.common_options

    def get_description(self, command: str) -> Optional[str]:
        """Get command description"""
        cmd_data = self.core_commands.get(command.upper())
        return cmd_data.get("description") if cmd_data else None
