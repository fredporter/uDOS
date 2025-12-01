# Command Registry System - Architecture Guide

Complete guide to the new command registry system in uDOS v1.1.9 (Round 3).

## Overview

The **Command Registry System** provides a Python-first architecture for uDOS commands with:

- **Decorator-based registration** - Clean, declarative command definitions
- **Rich metadata** - Categories, descriptions, usage, examples
- **Alias support** - Multiple names for same command
- **Argument validation** - Min/max arguments, type checking
- **Dynamic discovery** - Auto-load commands from extensions
- **UPPERCASE-HYPHEN naming** - Consistent command naming conventions

---

## Quick Start

### Basic Command Registration

```python
from core.utils.command_registry import command

@command(
    "HELLO",
    description="Greet the user",
    usage="HELLO [name]"
)
def hello_handler(args: List[str]) -> bool:
    """Handle HELLO command."""
    name = args[0] if args else "World"
    print(f"Hello, {name}!")
    return True
```

### Command with Aliases

```python
@command(
    "STORY",
    aliases=["ADVENTURE", "QUEST"],
    category="play",
    description="Manage adventures"
)
def story_handler(args: List[str]) -> bool:
    # All work the same: STORY, ADVENTURE, QUEST
    return True
```

### Command with Validation

```python
@command(
    "MOVE",
    min_args=1,
    max_args=2,
    requires_args=True,
    description="Move to a location"
)
def move_handler(args: List[str]) -> bool:
    # Guaranteed to have 1-2 arguments
    direction = args[0]
    distance = int(args[1]) if len(args) > 1 else 1
    return True
```

---

## Naming Conventions

### UPPERCASE-HYPHEN Format

All commands use **UPPERCASE-HYPHEN** naming:

```python
# ✅ Good
STORY-RUN
MAP-SHOW
SPRITE-CREATE
VARIABLE-SET

# ❌ Bad
story_run     # Lowercase with underscores
StoryRun      # CamelCase
story run     # Spaces
```

### Automatic Normalization

The registry auto-normalizes names:

```python
@command("story_run")  # → STORY-RUN
@command("StoryRun")   # → STORY-RUN
@command("story run")  # → STORY-RUN
```

---

## Command Metadata

### Full Metadata Example

```python
@command(
    name="STORY",
    aliases=["ADVENTURE", "QUEST"],
    category="play",
    description="Manage and run interactive text adventures",
    usage="STORY [LIST|RUN <name>|CREATE <name>|STATUS]",
    examples=[
        "STORY LIST",
        "STORY RUN water_quest",
        "STORY CREATE my_adventure"
    ],
    requires_args=False,
    min_args=0,
    max_args=2,
    extension="play",
    version="1.1.9",
    deprecated=False,
    hidden=False
)
def story_handler(args: List[str]) -> bool:
    """Handler implementation."""
    return True
```

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Command name (UPPERCASE-HYPHEN) |
| `handler` | Callable | Handler function |
| `aliases` | List[str] | Alternative names |
| `category` | str | Command category |
| `description` | str | Short description |
| `usage` | str | Usage syntax |
| `examples` | List[str] | Example commands |
| `requires_args` | bool | Requires arguments |
| `min_args` | int | Minimum arguments |
| `max_args` | int | Maximum arguments (None = unlimited) |
| `extension` | str | Extension name |
| `version` | str | Command version |
| `deprecated` | bool | Deprecated flag |
| `hidden` | bool | Hidden from HELP |

---

## Categories

### Built-in Categories

```python
# System commands
@command("CONFIG", category="system")

# File operations
@command("SAVE", category="file")

# Adventure/gameplay
@command("STORY", category="play")

# Knowledge/guides
@command("KNOWLEDGE", category="reference")

# Development tools
@command("DEBUG", category="dev")

# General utilities
@command("HELP", category="general")  # Default
```

### Custom Categories

```python
@command("MY-TOOL", category="custom-tools")
```

---

## Argument Validation

### Minimum Arguments

```python
@command("MOVE", min_args=1)
def move_handler(args: List[str]) -> bool:
    # Will never be called with 0 args
    direction = args[0]  # Safe - guaranteed to exist
    return True
```

### Maximum Arguments

```python
@command("GREET", max_args=1)
def greet_handler(args: List[str]) -> bool:
    # Will never get > 1 argument
    name = args[0] if args else "World"
    return True
```

### Argument Range

```python
@command("ROLL", min_args=1, max_args=2)
def roll_handler(args: List[str]) -> bool:
    # Always 1 or 2 arguments
    dice = args[0]           # Required
    modifier = args[1] if len(args) > 1 else "0"  # Optional
    return True
```

### Requires Arguments

```python
@command("DELETE", requires_args=True)
def delete_handler(args: List[str]) -> bool:
    # Will never be called with empty args
    target = args[0]
    return True
```

---

## Registry Usage

### Getting the Registry

```python
from core.utils.command_registry import get_registry

registry = get_registry()  # Singleton
```

### Finding Commands

```python
# Get handler
handler = registry.get_handler("STORY")
if handler:
    handler(["LIST"])

# Get metadata
metadata = registry.get_metadata("STORY")
print(metadata.description)

# List all commands
all_commands = registry.list_commands()

# List by category
play_commands = registry.list_commands(category="play")

# Search by pattern
story_commands = registry.find_commands("STORY.*")
```

### Validation

```python
# Validate arguments before calling
valid, msg = registry.validate_args("STORY", ["LIST"])
if valid:
    handler = registry.get_handler("STORY")
    handler(["LIST"])
else:
    print(f"Error: {msg}")
```

---

## Extension Commands

### Auto-Loading from Extensions

```python
# In extensions/my-extension/commands/my_handler.py

from core.utils.command_registry import command

@command(
    "MY-COMMAND",
    category="custom",
    extension="my-extension"
)
def my_handler(args: List[str]) -> bool:
    print("Custom command!")
    return True

# Auto-discovered by registry.load_extension_commands()
```

### Manual Extension Loading

```python
from pathlib import Path

extension_path = Path("extensions/my-extension")
count = registry.load_extension_commands(extension_path)
print(f"Loaded {count} commands")
```

---

## Help System

### Command Help

```python
# Get help for specific command
help_text = registry.get_help("STORY")
print(help_text)

# Output:
# STORY
# =====
#
# Manage and run interactive text adventures
#
# Usage: STORY [LIST|RUN <name>|CREATE <name>|STATUS]
# Aliases: ADVENTURE, QUEST
#
# Examples:
#   STORY LIST
#   STORY RUN water_quest
#
# Extension: play (v1.1.9)
```

### All Commands Help

```python
# Get help for all commands
help_text = registry.get_help()
print(help_text)

# Output:
# ==================================================
# uDOS COMMAND REFERENCE
# ==================================================
#
# PLAY
# ------------------------------
#   STORY                Manage and run adventures
#
# SYSTEM
# ------------------------------
#   CONFIG               System configuration
#   ...
```

---

## Advanced Features

### Deprecated Commands

```python
@command("OLD-COMMAND", deprecated=True)
def old_handler(args: List[str]) -> bool:
    print("⚠️  This command is deprecated!")
    return True

# Still works, but marked in help
```

### Hidden Commands

```python
@command("DEBUG-INTERNAL", hidden=True)
def debug_handler(args: List[str]) -> bool:
    # Not shown in HELP, but works
    return True
```

### Unregistering Commands

```python
# Remove a command
registry.unregister("OLD-COMMAND")

# Command and all aliases removed
```

### Schema Export

```python
# Export registry as JSON schema
schema = registry.export_schema()

# Schema includes:
# - All commands with metadata
# - Categories
# - Aliases
# - Version info
```

---

## Migration Guide

### Old Style (v1.x)

```python
# Old command registration
def register_command():
    return my_handler

def my_handler(args):
    return True
```

### New Style (v1.1.9+)

```python
# New decorator-based registration
@command(
    "MY-COMMAND",
    description="My command",
    category="custom"
)
def my_handler(args: List[str]) -> bool:
    return True

# Backward compatibility wrapper
def register_command():
    handler = StoryHandler()
    return handler.handle
```

---

## Best Practices

### 1. Use Descriptive Names

```python
# ✅ Good
@command("STORY-RUN", description="Run an adventure")
@command("MAP-SHOW", description="Display map")

# ❌ Bad
@command("SR", description="???")
@command("CMD1", description="Command")
```

### 2. Provide Usage Examples

```python
@command(
    "ROLL",
    examples=[
        "ROLL 1d20",
        "ROLL 2d6+3",
        "ROLL 1d100"
    ]
)
```

### 3. Set Argument Limits

```python
# Prevent misuse
@command("DELETE", min_args=1, max_args=1)  # Exactly 1 arg
@command("MOVE", min_args=1)                # At least 1
@command("SEARCH", max_args=3)              # At most 3
```

### 4. Use Categories

```python
# Organize related commands
@command("STORY-RUN", category="play")
@command("STORY-LIST", category="play")
@command("STORY-CREATE", category="play")
```

### 5. Add Aliases for Convenience

```python
@command(
    "STORY",
    aliases=["ADVENTURE", "QUEST", "S"]  # Include short form
)
```

---

## Testing

### Test Command Registration

```python
def test_command_registration():
    from core.utils.command_registry import CommandRegistry

    registry = CommandRegistry()

    @registry.register("TEST")
    def handler(args):
        return True

    assert "TEST" in registry.list_commands()
    assert registry.get_handler("TEST") == handler
```

### Test Argument Validation

```python
def test_validation():
    @registry.register("TEST", min_args=1, max_args=2)
    def handler(args):
        return True

    valid, _ = registry.validate_args("TEST", ["arg1"])
    assert valid is True

    invalid, msg = registry.validate_args("TEST", [])
    assert invalid is False
```

---

## Examples

### Complete Command Example

```python
from typing import List
from core.utils.command_registry import command
from core.utils.variables import VariableManager

@command(
    "SPRITE-CREATE",
    aliases=["CREATE-SPRITE", "NEW-SPRITE"],
    category="play",
    description="Create a new character sprite",
    usage="SPRITE-CREATE <name> [class]",
    examples=[
        "SPRITE-CREATE Hero",
        "SPRITE-CREATE Warrior fighter",
        "SPRITE-CREATE Gandalf wizard"
    ],
    min_args=1,
    max_args=2,
    extension="play",
    version="1.1.9"
)
def sprite_create_handler(args: List[str]) -> bool:
    """
    Create a new character sprite.

    Args:
        args[0]: Character name (required)
        args[1]: Character class (optional, default: adventurer)
    """
    vm = VariableManager()

    name = args[0]
    char_class = args[1] if len(args) > 1 else "adventurer"

    # Set SPRITE variables
    vm.set_variable('SPRITE-NAME', name, 'session')
    vm.set_variable('SPRITE-CLASS', char_class, 'session')
    vm.set_variable('SPRITE-HP', 100, 'session')
    vm.set_variable('SPRITE-HP-MAX', 100, 'session')
    vm.set_variable('SPRITE-LEVEL', 1, 'session')
    vm.set_variable('SPRITE-XP', 0, 'session')

    print(f"✨ Created {char_class} '{name}'")
    print(f"   HP: 100/100 | Level: 1 | XP: 0")

    return True
```

---

## See Also

- [Variable System](Variable-System.md) - Variable management
- [Adventure Scripting](Adventure-Scripting.md) - .upy adventures
- [Developers Guide](Developers-Guide.md) - Extension development
- [Command Reference](Command-Reference.md) - All commands

---

**Version:** v1.1.9 Round 3
**Last Updated:** December 2025
**Status:** Active Development
