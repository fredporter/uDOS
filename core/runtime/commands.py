"""
Central Command Registry for uDOS

Manages all system commands with UPPERCASE-HYPHEN naming convention.
Provides command discovery, validation, and execution routing.
"""

import re
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class CommandCategory(Enum):
    """Command categories for organization"""
    SYSTEM = "system"
    FILE = "file"
    KNOWLEDGE = "knowledge"
    DISPLAY = "display"
    NAVIGATION = "navigation"
    ADVENTURE = "adventure"
    GAME = "game"
    CONTENT = "content"
    GRAPHICS = "graphics"
    EXTENSION = "extension"


@dataclass
class CommandMetadata:
    """Metadata for a registered command"""
    name: str  # UPPERCASE-HYPHEN format (e.g., SYSTEM-STATUS)
    category: CommandCategory
    handler: Callable
    description: str
    usage: str = ""
    aliases: List[str] = field(default_factory=list)
    requires_args: bool = False
    min_args: int = 0
    max_args: Optional[int] = None
    examples: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate command name format"""
        if not self.is_valid_command_name(self.name):
            raise ValueError(
                f"Invalid command name '{self.name}'. "
                f"Must be UPPERCASE-HYPHEN format (e.g., SYSTEM-STATUS)"
            )

    @staticmethod
    def is_valid_command_name(name: str) -> bool:
        """Validate UPPERCASE-HYPHEN format"""
        # Must be UPPERCASE letters and hyphens only
        # Must have at least one hyphen (no single-word commands)
        # Must start and end with letter
        pattern = r'^[A-Z]+(-[A-Z]+)+$'
        return bool(re.match(pattern, name))


class CommandRegistry:
    """
    Central registry for all uDOS commands.

    Manages command registration, discovery, and routing with
    UPPERCASE-HYPHEN naming convention.
    """

    _instance: Optional['CommandRegistry'] = None
    _commands: Dict[str, CommandMetadata] = {}
    _aliases: Dict[str, str] = {}  # alias -> command_name mapping

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._commands = {}
            cls._aliases = {}
        return cls._instance

    def register(
        self,
        name: str,
        category: CommandCategory,
        handler: Callable,
        description: str,
        usage: str = "",
        aliases: Optional[List[str]] = None,
        requires_args: bool = False,
        min_args: int = 0,
        max_args: Optional[int] = None,
        examples: Optional[List[str]] = None
    ) -> None:
        """
        Register a command in the central registry.

        Args:
            name: Command name in UPPERCASE-HYPHEN format
            category: Command category
            handler: Callable that handles the command
            description: Brief description
            usage: Usage string (e.g., "SYSTEM-STATUS [--verbose]")
            aliases: Alternative names (can be legacy names)
            requires_args: Whether command requires arguments
            min_args: Minimum number of arguments
            max_args: Maximum number of arguments (None = unlimited)
            examples: Usage examples

        Raises:
            ValueError: If command name invalid or already registered
        """
        # Validate name format
        if not CommandMetadata.is_valid_command_name(name):
            raise ValueError(
                f"Invalid command name '{name}'. "
                f"Must be UPPERCASE-HYPHEN format (e.g., SYSTEM-STATUS)"
            )

        # Check for duplicates
        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")

        # Create metadata
        metadata = CommandMetadata(
            name=name,
            category=category,
            handler=handler,
            description=description,
            usage=usage or name,
            aliases=aliases or [],
            requires_args=requires_args,
            min_args=min_args,
            max_args=max_args,
            examples=examples or []
        )

        # Register command
        self._commands[name] = metadata

        # Register aliases
        for alias in metadata.aliases:
            if alias in self._aliases:
                raise ValueError(
                    f"Alias '{alias}' already registered for '{self._aliases[alias]}'"
                )
            self._aliases[alias] = name

    def get(self, name: str) -> Optional[CommandMetadata]:
        """
        Get command metadata by name or alias.

        Args:
            name: Command name or alias

        Returns:
            CommandMetadata if found, None otherwise
        """
        # Direct lookup
        if name in self._commands:
            return self._commands[name]

        # Alias lookup
        if name in self._aliases:
            return self._commands[self._aliases[name]]

        return None

    def resolve_name(self, name: str) -> Optional[str]:
        """
        Resolve command name from name or alias.

        Args:
            name: Command name or alias

        Returns:
            Canonical command name if found, None otherwise
        """
        if name in self._commands:
            return name
        if name in self._aliases:
            return self._aliases[name]
        return None

    def execute(self, name: str, args: List[str], context: Any = None) -> Any:
        """
        Execute a command by name or alias.

        Args:
            name: Command name or alias
            args: Command arguments
            context: Execution context (e.g., CommandHandler instance)

        Returns:
            Command execution result

        Raises:
            ValueError: If command not found or invalid arguments
        """
        metadata = self.get(name)
        if not metadata:
            raise ValueError(f"Unknown command: {name}")

        # Validate arguments
        arg_count = len(args)
        if metadata.requires_args and arg_count == 0:
            raise ValueError(f"Command '{metadata.name}' requires arguments")

        if arg_count < metadata.min_args:
            raise ValueError(
                f"Command '{metadata.name}' requires at least {metadata.min_args} arguments"
            )

        if metadata.max_args is not None and arg_count > metadata.max_args:
            raise ValueError(
                f"Command '{metadata.name}' accepts at most {metadata.max_args} arguments"
            )

        # Execute handler
        return metadata.handler(args, context)

    def list_commands(
        self,
        category: Optional[CommandCategory] = None
    ) -> List[CommandMetadata]:
        """
        List all registered commands.

        Args:
            category: Filter by category (None = all)

        Returns:
            List of command metadata
        """
        commands = list(self._commands.values())

        if category:
            commands = [c for c in commands if c.category == category]

        return sorted(commands, key=lambda c: c.name)

    def list_categories(self) -> List[str]:
        """Get list of all command categories"""
        categories = set(cmd.category.value for cmd in self._commands.values())
        return sorted(categories)

    def search(self, query: str) -> List[CommandMetadata]:
        """
        Search commands by name or description.

        Args:
            query: Search query (case-insensitive)

        Returns:
            Matching commands
        """
        query = query.lower()
        results = []

        for cmd in self._commands.values():
            if (query in cmd.name.lower() or
                query in cmd.description.lower() or
                any(query in alias.lower() for alias in cmd.aliases)):
                results.append(cmd)

        return sorted(results, key=lambda c: c.name)

    def get_help(self, name: str) -> str:
        """
        Get formatted help text for a command.

        Args:
            name: Command name or alias

        Returns:
            Formatted help text
        """
        metadata = self.get(name)
        if not metadata:
            return f"Unknown command: {name}"

        help_text = [
            f"Command: {metadata.name}",
            f"Category: {metadata.category.value}",
            f"Description: {metadata.description}",
            f"",
            f"Usage: {metadata.usage}",
        ]

        if metadata.aliases:
            help_text.append(f"Aliases: {', '.join(metadata.aliases)}")

        if metadata.examples:
            help_text.append("")
            help_text.append("Examples:")
            for example in metadata.examples:
                help_text.append(f"  {example}")

        return "\n".join(help_text)

    def clear(self) -> None:
        """Clear all registered commands (for testing)"""
        self._commands.clear()
        self._aliases.clear()


# Global registry instance
_registry = CommandRegistry()


def register_command(
    name: str,
    category: CommandCategory,
    description: str,
    usage: str = "",
    aliases: Optional[List[str]] = None,
    requires_args: bool = False,
    min_args: int = 0,
    max_args: Optional[int] = None,
    examples: Optional[List[str]] = None
):
    """
    Decorator for registering commands.

    Usage:
        @register_command(
            name="SYSTEM-STATUS",
            category=CommandCategory.SYSTEM,
            description="Display system status",
            aliases=["STATUS", "STAT"]
        )
        def handle_system_status(args, context):
            return "System OK"
    """
    def decorator(handler: Callable):
        _registry.register(
            name=name,
            category=category,
            handler=handler,
            description=description,
            usage=usage,
            aliases=aliases,
            requires_args=requires_args,
            min_args=min_args,
            max_args=max_args,
            examples=examples
        )
        return handler
    return decorator


def get_registry() -> CommandRegistry:
    """Get the global command registry instance"""
    return _registry
