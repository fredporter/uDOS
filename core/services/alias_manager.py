"""
Command Alias Manager - v1.0.23
Smart command aliasing system with built-in shortcuts and custom aliases

Features:
- Built-in shortcuts (?, !!, @, #)
- Custom user aliases
- Persistent storage
- Smart suggestions
- Usage tracking

Author: uDOS Development Team
Version: 1.0.23
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import re


class AliasManager:
    """Manage command aliases and shortcuts"""

    # Built-in shortcuts
    BUILTIN_ALIASES = {
        '?': 'HELP',
        '??': 'HELP --all',
        '!': 'HISTORY',
        '!!': 'HISTORY --last',
        '@': 'MEMORY',
        '@@': 'MEMORY --list',
        '#': 'COMMENT',
        'q': 'QUIT',
        'x': 'EXIT',
        'cls': 'CLEAR',
        'h': 'HELP',
        'l': 'LIST',
        'ls': 'LIST',
        'cd': 'DIRECTORY',
        'pwd': 'DIRECTORY --current',

        # Documentation shortcuts
        'd': 'DOCS',
        'doc': 'DOCS',
        'm': 'DOCS --manual',
        'man': 'DOCS --manual',
        'hb': 'DOCS --handbook',
        'ex': 'DOCS --example',

        # Learning shortcuts
        'learn': 'LEARN',
        'guide': 'LEARN --guides',
        'diag': 'LEARN --diagrams',

        # Memory shortcuts
        'priv': 'MEMORY --private',
        'share': 'MEMORY --shared',
        'comm': 'MEMORY --community',
        'kb': 'MEMORY --public',

        # File operations
        'e': 'EDIT',
        'v': 'VIEW',
        'cat': 'VIEW',
        's': 'SAVE',
        'w': 'SAVE',

        # System shortcuts
        'env': 'ENV',
        'set': 'SETTINGS',
        'cfg': 'CONFIG',
        'stat': 'STATUS',
    }

    def __init__(self, user_data_path: str = "data/USER.UDT", logger=None):
        """Initialize alias manager"""
        self.user_data_path = Path(user_data_path)
        self.logger = logger
        self.custom_aliases: Dict[str, str] = {}
        self.alias_usage: Dict[str, int] = {}
        self.command_patterns: Dict[str, int] = {}  # Track repeated commands

        # Load custom aliases
        self._load_aliases()

    def resolve_alias(self, command: str) -> str:
        """
        Resolve alias to full command

        Args:
            command: Raw command string (may be alias)

        Returns:
            Resolved command string
        """
        # Parse command (handle multi-word aliases)
        parts = command.split(maxsplit=1)
        alias = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Check custom aliases first (higher priority)
        if alias in self.custom_aliases:
            resolved = self.custom_aliases[alias]
            self._track_usage(alias)

            # If alias has parameters, append args
            if args:
                return f"{resolved} {args}"
            return resolved

        # Check built-in aliases
        if alias in self.BUILTIN_ALIASES:
            resolved = self.BUILTIN_ALIASES[alias]
            self._track_usage(alias)

            if args:
                return f"{resolved} {args}"
            return resolved

        # Not an alias - track as potential alias candidate
        self._track_command_pattern(command)

        return command

    def add_alias(self, alias: str, command: str, force: bool = False) -> Tuple[bool, str]:
        """
        Add custom alias

        Args:
            alias: Short alias name
            command: Full command to execute
            force: Overwrite existing alias

        Returns:
            (success, message)
        """
        # Validate alias name
        if not self._is_valid_alias_name(alias):
            return False, f"Invalid alias name '{alias}'. Use letters, numbers, - and _ only."

        # Check if conflicts with built-in
        if alias in self.BUILTIN_ALIASES and not force:
            return False, f"Alias '{alias}' conflicts with built-in. Use --force to override."

        # Check if already exists
        if alias in self.custom_aliases and not force:
            existing = self.custom_aliases[alias]
            return False, f"Alias '{alias}' already exists: {existing}\nUse --force to override."

        # Add alias
        self.custom_aliases[alias] = command
        self._save_aliases()

        return True, f"✅ Alias created: {alias} → {command}"

    def remove_alias(self, alias: str) -> Tuple[bool, str]:
        """
        Remove custom alias

        Args:
            alias: Alias to remove

        Returns:
            (success, message)
        """
        if alias not in self.custom_aliases:
            return False, f"Alias '{alias}' not found"

        command = self.custom_aliases[alias]
        del self.custom_aliases[alias]
        self._save_aliases()

        return True, f"✅ Removed alias: {alias} (was: {command})"

    def list_aliases(self, show_builtin: bool = True, show_custom: bool = True) -> str:
        """
        List all aliases

        Args:
            show_builtin: Include built-in aliases
            show_custom: Include custom aliases

        Returns:
            Formatted alias list
        """
        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│  COMMAND ALIASES                                               │",
            "└─────────────────────────────────────────────────────────────────┘",
            ""
        ]

        if show_custom and self.custom_aliases:
            output.append("📝 CUSTOM ALIASES:")
            output.append("─" * 65)
            for alias, command in sorted(self.custom_aliases.items()):
                usage = self.alias_usage.get(alias, 0)
                output.append(f"  {alias:<15} → {command:<35} ({usage} uses)")
            output.append("")

        if show_builtin:
            output.append("⚡ BUILT-IN SHORTCUTS:")
            output.append("─" * 65)

            # Group by category
            categories = {
                'Help & Info': ['?', '??', 'h'],
                'History': ['!', '!!'],
                'Memory': ['@', '@@', 'priv', 'share', 'comm', 'kb'],
                'Documentation': ['d', 'doc', 'm', 'man', 'hb', 'ex'],
                'Learning': ['learn', 'guide', 'diag'],
                'File Ops': ['e', 'v', 'cat', 's', 'w', 'l', 'ls'],
                'Navigation': ['cd', 'pwd'],
                'System': ['env', 'set', 'cfg', 'stat', 'q', 'x', 'cls'],
            }

            for category, aliases in categories.items():
                output.append(f"\n  {category}:")
                for alias in aliases:
                    if alias in self.BUILTIN_ALIASES:
                        command = self.BUILTIN_ALIASES[alias]
                        output.append(f"    {alias:<12} → {command}")

        output.append("")
        output.append("Add alias: ALIAS <name>=\"<command>\"")
        output.append("Remove: ALIAS --remove <name>")
        output.append("")

        return "\n".join(output)

    def get_suggestions(self, command_history: List[str], min_count: int = 5) -> List[Tuple[str, str, int]]:
        """
        Suggest aliases for repeated commands

        Args:
            command_history: List of recent commands
            min_count: Minimum repetitions to suggest

        Returns:
            List of (command, suggested_alias, count) tuples
        """
        # Count command frequency
        frequency: Dict[str, int] = {}
        for cmd in command_history:
            # Normalize (remove args for pattern matching)
            base_cmd = cmd.split()[0] if cmd else ""
            if base_cmd and len(base_cmd) > 3:  # Skip very short commands
                frequency[cmd] = frequency.get(cmd, 0) + 1

        # Generate suggestions
        suggestions = []
        for command, count in frequency.items():
            if count >= min_count:
                # Skip if already has alias
                if command in self.custom_aliases.values():
                    continue

                # Generate suggested alias name
                suggested = self._generate_alias_name(command)
                suggestions.append((command, suggested, count))

        # Sort by frequency
        suggestions.sort(key=lambda x: x[2], reverse=True)

        return suggestions

    def _is_valid_alias_name(self, alias: str) -> bool:
        """Validate alias name"""
        # Allow letters, numbers, hyphens, underscores
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', alias))

    def _generate_alias_name(self, command: str) -> str:
        """Generate suggested alias name from command"""
        # Take first word
        base = command.split()[0].lower()

        # If long, create abbreviation
        if len(base) > 8:
            # Take first letter of each capital or first 3 chars
            if any(c.isupper() for c in base):
                abbr = ''.join(c for c in base if c.isupper()).lower()
            else:
                abbr = base[:3]
            return abbr

        return base

    def _track_usage(self, alias: str):
        """Track alias usage"""
        self.alias_usage[alias] = self.alias_usage.get(alias, 0) + 1

    def _track_command_pattern(self, command: str):
        """Track command patterns for suggestions"""
        self.command_patterns[command] = self.command_patterns.get(command, 0) + 1

    def _load_aliases(self):
        """Load custom aliases from user data"""
        try:
            if self.user_data_path.exists():
                with open(self.user_data_path, 'r') as f:
                    data = json.load(f)
                    self.custom_aliases = data.get('aliases', {})
                    self.alias_usage = data.get('alias_usage', {})
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Error loading aliases: {e}")
            self.custom_aliases = {}
            self.alias_usage = {}

    def _save_aliases(self):
        """Save custom aliases to user data"""
        try:
            # Load existing data
            data = {}
            if self.user_data_path.exists():
                with open(self.user_data_path, 'r') as f:
                    data = json.load(f)

            # Update aliases
            data['aliases'] = self.custom_aliases
            data['alias_usage'] = self.alias_usage
            data['last_updated'] = datetime.now().isoformat()

            # Save
            self.user_data_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.user_data_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            if self.logger:
                self.logger.error(f"Error saving aliases: {e}")

    def export_aliases(self, output_path: str) -> Tuple[bool, str]:
        """Export aliases to file"""
        try:
            export_data = {
                'custom_aliases': self.custom_aliases,
                'exported_at': datetime.now().isoformat(),
                'total_aliases': len(self.custom_aliases)
            }

            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            return True, f"✅ Exported {len(self.custom_aliases)} aliases to {output_path}"

        except Exception as e:
            return False, f"❌ Export failed: {e}"

    def import_aliases(self, input_path: str, merge: bool = True) -> Tuple[bool, str]:
        """Import aliases from file"""
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)

            imported_aliases = data.get('custom_aliases', {})

            if not merge:
                # Replace all
                self.custom_aliases = imported_aliases
                count = len(imported_aliases)
            else:
                # Merge (imported takes precedence)
                before = len(self.custom_aliases)
                self.custom_aliases.update(imported_aliases)
                count = len(self.custom_aliases) - before

            self._save_aliases()

            return True, f"✅ Imported {count} aliases from {input_path}"

        except Exception as e:
            return False, f"❌ Import failed: {e}"


class AliasCommandHandler:
    """Handler for ALIAS command"""

    def __init__(self, alias_manager: AliasManager, viewport=None):
        """Initialize handler"""
        self.manager = alias_manager
        self.viewport = viewport

    def handle(self, command: str, args: List[str]) -> str:
        """Handle ALIAS commands"""

        # No args = list aliases
        if not command:
            return self.manager.list_aliases()

        # Help
        if command in ["HELP", "--help"]:
            return self._show_help()

        # List custom only
        if command == "--custom":
            return self.manager.list_aliases(show_builtin=False)

        # List builtin only
        if command == "--builtin":
            return self.manager.list_aliases(show_custom=False)

        # Remove alias
        if command == "--remove" or command == "-r":
            if not args:
                return "\n❌ Usage: ALIAS --remove <name>\n"

            success, msg = self.manager.remove_alias(args[0])
            return f"\n{msg}\n"

        # Export aliases
        if command == "--export":
            if not args:
                return "\n❌ Usage: ALIAS --export <file>\n"

            success, msg = self.manager.export_aliases(args[0])
            return f"\n{msg}\n"

        # Import aliases
        if command == "--import":
            if not args:
                return "\n❌ Usage: ALIAS --import <file> [--merge]\n"

            merge = "--merge" in args
            success, msg = self.manager.import_aliases(args[0], merge=merge)
            return f"\n{msg}\n"

        # Add alias: ALIAS name="command"
        if "=" in command:
            parts = command.split("=", 1)
            alias_name = parts[0].strip()
            alias_command = parts[1].strip().strip('"').strip("'")

            force = "--force" in args or "-f" in args
            success, msg = self.manager.add_alias(alias_name, alias_command, force=force)
            return f"\n{msg}\n"

        # Show specific alias
        if command in self.manager.custom_aliases:
            target = self.manager.custom_aliases[command]
            usage = self.manager.alias_usage.get(command, 0)
            return f"\n{command} → {target}\nUsed {usage} times\n"

        if command in self.manager.BUILTIN_ALIASES:
            target = self.manager.BUILTIN_ALIASES[command]
            return f"\n{command} → {target} (built-in)\n"

        return f"\n❌ Unknown alias '{command}'\n"

    def _show_help(self) -> str:
        """Show ALIAS help"""
        return """
┌─────────────────────────────────────────────────────────────────┐
│  ALIAS - Command Aliasing System                               │
└─────────────────────────────────────────────────────────────────┘

⚡ Create shortcuts for frequently used commands

USAGE:
  ALIAS                       List all aliases
  ALIAS <name>="<command>"    Create custom alias
  ALIAS --remove <name>       Remove alias
  ALIAS --custom              List custom aliases only
  ALIAS --builtin             List built-in shortcuts
  ALIAS --export <file>       Export aliases
  ALIAS --import <file>       Import aliases

BUILT-IN SHORTCUTS:
  ?   → HELP              Quick help
  ??  → HELP --all        Full help
  !   → HISTORY           Command history
  !!  → HISTORY --last    Last command
  @   → MEMORY            Memory system
  d   → DOCS              Documentation
  m   → DOCS --manual     Manual
  e   → EDIT              Edit file
  v   → VIEW              View file
  q   → QUIT              Exit uDOS

EXAMPLES:
  ALIAS gm="DOCS --manual git"              # Git manual shortcut
  ALIAS pk="MEMORY --private --save"        # Quick private save
  ALIAS todo="EDIT tasks.md"                # Edit todo list
  ALIAS backup="SAVE --tier=private backup" # Backup shortcut

  ALIAS --remove gm                          # Remove alias
  ALIAS --export my_aliases.json            # Export to file
  ALIAS --import team_aliases.json --merge  # Import and merge

SMART SUGGESTIONS:
  uDOS tracks command patterns and suggests aliases after 5+ uses
  Use 'ALIAS --suggestions' to see recommendations

ALIAS CHAINING:
  Aliases can reference other aliases:
  ALIAS gm="DOCS --manual git"
  ALIAS gc="gm commit"    # Chains to DOCS --manual git commit

FORCE OVERRIDE:
  ALIAS q="QUIT --save" --force    # Override built-in 'q'

See also: HISTORY (command history), DOCS (documentation)
"""


# Convenience function
def create_alias_manager(user_data_path: str = "data/USER.UDT", logger=None):
    """Create alias manager instance"""
    return AliasManager(user_data_path=user_data_path, logger=logger)
