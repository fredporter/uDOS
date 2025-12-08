"""
Command Registry System - Python-First Architecture
Decorator-based command registration with metadata and dynamic discovery.

Version: v1.1.9 Round 3
"""

from typing import Callable, Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
import importlib.util
import inspect
import re


@dataclass
class CommandMetadata:
    """Metadata for a registered command."""

    name: str                           # Command name (UPPERCASE-HYPHEN)
    handler: Callable                   # Handler function
    aliases: List[str] = field(default_factory=list)  # Alternative names
    category: str = "general"           # Command category
    description: str = ""               # Short description
    usage: str = ""                     # Usage syntax
    examples: List[str] = field(default_factory=list)  # Example commands
    requires_args: bool = False         # Requires arguments
    min_args: int = 0                   # Minimum arguments
    max_args: Optional[int] = None      # Maximum arguments (None = unlimited)
    extension: Optional[str] = None     # Extension name (if from extension)
    version: str = "1.0.0"             # Command version
    deprecated: bool = False            # Deprecated flag
    hidden: bool = False                # Hidden from HELP

    def matches(self, command: str) -> bool:
        """Check if command matches this registration."""
        cmd = command.upper()
        return cmd == self.name or cmd in [a.upper() for a in self.aliases]


class CommandRegistry:
    """
    Central registry for all uDOS commands.

    Supports:
    - Decorator-based registration
    - Command metadata and documentation
    - Alias resolution
    - Category organization
    - Extension command loading
    - Backward compatibility
    """

    def __init__(self):
        self._commands: Dict[str, CommandMetadata] = {}
        self._categories: Dict[str, List[str]] = {}
        self._aliases: Dict[str, str] = {}  # alias -> primary name

    def register(
        self,
        name: str,
        handler: Optional[Callable] = None,
        aliases: Optional[List[str]] = None,
        category: str = "general",
        description: str = "",
        usage: str = "",
        examples: Optional[List[str]] = None,
        requires_args: bool = False,
        min_args: int = 0,
        max_args: Optional[int] = None,
        extension: Optional[str] = None,
        version: str = "1.0.0",
        deprecated: bool = False,
        hidden: bool = False
    ) -> Callable:
        """
        Register a command handler.

        Can be used as decorator or direct registration:

        @registry.register("STORY", aliases=["ADVENTURE"])
        def story_handler(args):
            pass

        Or:
        registry.register("STORY", story_handler, aliases=["ADVENTURE"])
        """
        def decorator(func: Callable) -> Callable:
            # Normalize name to UPPERCASE-HYPHEN
            normalized_name = self._normalize_name(name)

            # Create metadata
            metadata = CommandMetadata(
                name=normalized_name,
                handler=func,
                aliases=aliases or [],
                category=category,
                description=description,
                usage=usage or f"{normalized_name} [args]",
                examples=examples or [],
                requires_args=requires_args,
                min_args=min_args,
                max_args=max_args,
                extension=extension,
                version=version,
                deprecated=deprecated,
                hidden=hidden
            )

            # Register command
            self._commands[normalized_name] = metadata

            # Register category
            if category not in self._categories:
                self._categories[category] = []
            if normalized_name not in self._categories[category]:
                self._categories[category].append(normalized_name)

            # Register aliases
            for alias in (aliases or []):
                normalized_alias = self._normalize_name(alias)
                self._aliases[normalized_alias] = normalized_name

            return func

        # Support both @decorator and direct call
        if handler is not None:
            return decorator(handler)
        return decorator

    def get_handler(self, command: str) -> Optional[Callable]:
        """Get handler function for a command."""
        metadata = self.get_metadata(command)
        return metadata.handler if metadata else None

    def get_metadata(self, command: str) -> Optional[CommandMetadata]:
        """Get metadata for a command (resolves aliases)."""
        normalized = self._normalize_name(command)

        # Check direct match
        if normalized in self._commands:
            return self._commands[normalized]

        # Check aliases
        if normalized in self._aliases:
            primary = self._aliases[normalized]
            return self._commands.get(primary)

        return None

    def list_commands(
        self,
        category: Optional[str] = None,
        include_hidden: bool = False,
        include_deprecated: bool = True
    ) -> List[str]:
        """List all registered commands."""
        commands = []

        if category:
            commands = self._categories.get(category, [])
        else:
            commands = list(self._commands.keys())

        # Filter hidden/deprecated
        filtered = []
        for cmd in commands:
            metadata = self._commands[cmd]
            if metadata.hidden and not include_hidden:
                continue
            if metadata.deprecated and not include_deprecated:
                continue
            filtered.append(cmd)

        return sorted(filtered)

    def get_categories(self) -> List[str]:
        """Get all command categories."""
        return sorted(self._categories.keys())

    def find_commands(self, pattern: str) -> List[str]:
        """Find commands matching pattern (regex)."""
        regex = re.compile(pattern, re.IGNORECASE)
        matches = []

        for cmd in self._commands.keys():
            if regex.search(cmd):
                matches.append(cmd)

        return sorted(matches)

    def unregister(self, command: str) -> bool:
        """Unregister a command."""
        normalized = self._normalize_name(command)

        if normalized in self._commands:
            metadata = self._commands[normalized]

            # Remove from commands
            del self._commands[normalized]

            # Remove from category
            if metadata.category in self._categories:
                if normalized in self._categories[metadata.category]:
                    self._categories[metadata.category].remove(normalized)

            # Remove aliases
            aliases_to_remove = [
                alias for alias, primary in self._aliases.items()
                if primary == normalized
            ]
            for alias in aliases_to_remove:
                del self._aliases[alias]

            return True

        return False

    def validate_args(self, command: str, args: List[str]) -> tuple[bool, str]:
        """
        Validate command arguments.

        Returns:
            (valid, error_message)
        """
        metadata = self.get_metadata(command)
        if not metadata:
            return False, f"Unknown command: {command}"

        arg_count = len(args)

        # Check minimum
        if arg_count < metadata.min_args:
            return False, f"{metadata.name} requires at least {metadata.min_args} argument(s)"

        # Check maximum
        if metadata.max_args is not None and arg_count > metadata.max_args:
            return False, f"{metadata.name} accepts at most {metadata.max_args} argument(s)"

        # Check requires_args
        if metadata.requires_args and arg_count == 0:
            return False, f"{metadata.name} requires arguments"

        return True, ""

    def get_help(self, command: Optional[str] = None) -> str:
        """Get help text for command or all commands."""
        if command:
            return self._get_command_help(command)
        else:
            return self._get_all_help()

    def _get_command_help(self, command: str) -> str:
        """Get help for specific command."""
        metadata = self.get_metadata(command)
        if not metadata:
            return f"Unknown command: {command}"

        help_text = []
        help_text.append(f"\n{metadata.name}")
        help_text.append("=" * len(metadata.name))

        if metadata.description:
            help_text.append(f"\n{metadata.description}")

        if metadata.deprecated:
            help_text.append("\n⚠️  DEPRECATED - This command may be removed in future versions")

        help_text.append(f"\nUsage: {metadata.usage}")

        if metadata.aliases:
            help_text.append(f"Aliases: {', '.join(metadata.aliases)}")

        if metadata.examples:
            help_text.append("\nExamples:")
            for example in metadata.examples:
                help_text.append(f"  {example}")

        if metadata.extension:
            help_text.append(f"\nExtension: {metadata.extension} (v{metadata.version})")

        return "\n".join(help_text)

    def _get_all_help(self) -> str:
        """Get help for all commands."""
        help_text = []
        help_text.append("\n" + "=" * 50)
        help_text.append("uDOS COMMAND REFERENCE")
        help_text.append("=" * 50)

        for category in self.get_categories():
            commands = self.list_commands(category=category)
            if not commands:
                continue

            help_text.append(f"\n{category.upper()}")
            help_text.append("-" * 30)

            for cmd in commands:
                metadata = self._commands[cmd]
                desc = metadata.description or "No description"
                help_text.append(f"  {cmd:20} {desc}")

        help_text.append("\nUse HELP <command> for detailed information")
        help_text.append("")

        return "\n".join(help_text)

    def load_extension_commands(self, extension_path: Path) -> int:
        """
        Load commands from an extension directory.

        Returns:
            Number of commands loaded
        """
        commands_loaded = 0
        extension_name = extension_path.name

        # Look for command handlers
        commands_dir = extension_path / "commands"
        if not commands_dir.exists():
            return 0

        # Import all Python files
        for py_file in commands_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                # Import module
                spec = importlib.util.spec_from_file_location(
                    f"{extension_name}.commands.{py_file.stem}",
                    py_file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for register_command function
                    if hasattr(module, 'register_command'):
                        handler = module.register_command()
                        if handler:
                            # Auto-register with extension info
                            cmd_name = py_file.stem.replace("_handler", "").replace("_", "-").upper()
                            self.register(
                                name=cmd_name,
                                handler=handler,
                                extension=extension_name
                            )
                            commands_loaded += 1

            except Exception as e:
                print(f"⚠️  Failed to load {py_file.name}: {e}")

        return commands_loaded

    def _normalize_name(self, name: str) -> str:
        """Normalize command name to UPPERCASE-HYPHEN format."""
        # Convert to uppercase
        normalized = name.upper()

        # Replace underscores with hyphens
        normalized = normalized.replace("_", "-")

        # Remove spaces
        normalized = normalized.replace(" ", "-")

        return normalized

    def export_schema(self) -> Dict[str, Any]:
        """Export registry as JSON schema."""
        schema = {
            "version": "1.1.9",
            "commands": {},
            "categories": self._categories,
            "aliases": self._aliases
        }

        for name, metadata in self._commands.items():
            schema["commands"][name] = {
                "name": metadata.name,
                "category": metadata.category,
                "description": metadata.description,
                "usage": metadata.usage,
                "examples": metadata.examples,
                "aliases": metadata.aliases,
                "requires_args": metadata.requires_args,
                "min_args": metadata.min_args,
                "max_args": metadata.max_args,
                "extension": metadata.extension,
                "version": metadata.version,
                "deprecated": metadata.deprecated,
                "hidden": metadata.hidden
            }

        return schema


# Global registry instance
_registry: Optional[CommandRegistry] = None


def get_registry() -> CommandRegistry:
    """Get global command registry (singleton)."""
    global _registry
    if _registry is None:
        _registry = CommandRegistry()
    return _registry


def reset_registry():
    """Reset global registry (for testing)."""
    global _registry
    _registry = None


# Convenience decorator using global registry
def command(
    name: str,
    aliases: Optional[List[str]] = None,
    category: str = "general",
    description: str = "",
    usage: str = "",
    examples: Optional[List[str]] = None,
    requires_args: bool = False,
    min_args: int = 0,
    max_args: Optional[int] = None,
    extension: Optional[str] = None,
    version: str = "1.0.0",
    deprecated: bool = False,
    hidden: bool = False
):
    """
    Decorator to register a command in the global registry.

    Example:
        @command("STORY", aliases=["ADVENTURE"], category="play")
        def story_handler(args: List[str]) -> bool:
            # Handle STORY command
            return True
    """
    return get_registry().register(
        name=name,
        aliases=aliases,
        category=category,
        description=description,
        usage=usage,
        examples=examples,
        requires_args=requires_args,
        min_args=min_args,
        max_args=max_args,
        extension=extension,
        version=version,
        deprecated=deprecated,
        hidden=hidden
    )
