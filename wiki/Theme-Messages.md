# Theme-Aware Messaging System

**Version:** v1.2.22  
**Status:** Production Ready

The Theme-Aware Messaging System provides consistent, contextual messaging across all uDOS interfaces with emoji stripping for plaintext mode.

## Overview

uDOS v1.2.22 introduces universal theme-aware messaging that adapts system messages to your current theme (galaxy, foundation, desert, urban, neon, aurora, ocean).

## Features

- 📝 **Consistent Vocabulary** - Messages match theme language
- 🎨 **7 Built-in Themes** - Galaxy, Foundation, Desert, Urban, Neon, Aurora, Ocean
- 🔄 **Dynamic Formatting** - F-string interpolation with context variables
- 🎭 **Emoji Handling** - Automatic stripping for plaintext mode
- 🔧 **Extensible** - Easy to add custom themes

## Quick Start

### Check Current Theme

```bash
CONFIG
# View [Interface] tab → Theme setting
```

### Set Theme

```bash
THEME SET galaxy
```

**Available themes:**
- `galaxy` - Space exploration (🌌 cosmic, starships, sectors)
- `foundation` - Survival first (🏕️ settlements, resources, missions)
- `desert` - Nomadic travel (🏜️ outposts, caravans, oases)
- `urban` - City living (🏙️ districts, metro, networks)
- `neon` - Cyberpunk (⚡ grids, nodes, cyberspace)
- `aurora` - Natural world (🌿 havens, ecosystems, journeys)
- `ocean` - Maritime (🌊 ports, fleets, tides)

### Test Message Formatting

```python
from core.services.theme_messenger import get_theme_messenger

messenger = get_theme_messenger()
msg = messenger.format_message(
    "success_operation",
    operation="file created",
    target="data.json"
)
print(msg)
```

**Output (galaxy theme):**
```
✅ Mission complete: file created → data.json
```

**Output (foundation theme):**
```
✅ Task complete: file created → data.json
```

## Message Templates

### Default Vocabulary

Each theme has a unique vocabulary:

```python
DEFAULT_VOCAB = {
    'galaxy': {
        'location': 'sector',
        'user': 'commander',
        'action': 'mission',
        'system': 'starship',
        'data': 'archive'
    },
    'foundation': {
        'location': 'settlement',
        'user': 'survivor',
        'action': 'task',
        'system': 'base',
        'data': 'resource'
    },
    'desert': {
        'location': 'outpost',
        'user': 'nomad',
        'action': 'trek',
        'system': 'caravan',
        'data': 'supply'
    },
    'urban': {
        'location': 'district',
        'user': 'citizen',
        'action': 'operation',
        'system': 'network',
        'data': 'cache'
    },
    'neon': {
        'location': 'grid',
        'user': 'netrunner',
        'action': 'hack',
        'system': 'node',
        'data': 'datachunk'
    },
    'aurora': {
        'location': 'haven',
        'user': 'wanderer',
        'action': 'journey',
        'system': 'sanctuary',
        'data': 'knowledge'
    },
    'ocean': {
        'location': 'port',
        'user': 'sailor',
        'action': 'voyage',
        'system': 'fleet',
        'data': 'cargo'
    }
}
```

### Common Message Types

#### success_operation
```python
msg = messenger.format_message(
    "success_operation",
    operation="backup",
    target="user.json"
)
# ✅ Mission complete: backup → user.json (galaxy)
# ✅ Task complete: backup → user.json (foundation)
```

#### error_permission
```python
msg = messenger.format_message(
    "error_permission",
    action="modify config",
    required_role="admin"
)
# ❌ Access denied, Commander. Mission requires ADMIN clearance. (galaxy)
# ❌ Permission denied, Survivor. Task requires ADMIN role. (foundation)
```

#### warning_limit
```python
msg = messenger.format_message(
    "warning_limit",
    resource="disk",
    usage="85%",
    threshold="75%"
)
# ⚠️ Archive capacity at 85% (threshold: 75%) (galaxy)
# ⚠️ Resource usage at 85% (threshold: 75%) (foundation)
```

#### info_status
```python
msg = messenger.format_message(
    "info_status",
    component="error interceptor",
    status="active"
)
# ℹ️ Starship system: error interceptor - active (galaxy)
# ℹ️ Base system: error interceptor - active (foundation)
```

## F-String Interpolation

Messages support full Python f-string syntax:

```python
# Template with variables
template = "{user}, your {action} '{name}' is {status}."

# Format with context
msg = messenger.format_message(
    template,
    name="backup_system",
    status="complete"
)

# Galaxy theme output:
# "Commander, your mission 'backup_system' is complete."

# Foundation theme output:
# "Survivor, your task 'backup_system' is complete."
```

### Context Variables

Automatically available in all messages:

- `{user}` - Theme-specific user term (commander, survivor, nomad, etc.)
- `{location}` - Theme-specific location term (sector, settlement, outpost, etc.)
- `{action}` - Theme-specific action term (mission, task, trek, etc.)
- `{system}` - Theme-specific system term (starship, base, caravan, etc.)
- `{data}` - Theme-specific data term (archive, resource, supply, etc.)

### Custom Variables

Pass any variables via kwargs:

```python
msg = messenger.format_message(
    "Mission: {action_name} at {location_name}",
    action_name="establish camp",
    location_name="Pine Ridge"
)
# Galaxy: "Mission: establish camp at Pine Ridge"
```

## Emoji Handling

### Automatic Stripping

Emojis are automatically removed in plaintext mode:

```python
# With emoji mode enabled
msg = messenger.format_message("success", icon="✅")
# Output: "✅ Mission complete"

# With emoji mode disabled (CONFIG → Interface → Emoji: off)
# Output: "Mission complete"
```

### Emoji Patterns

System removes:
- Standard emoji (🌌, 🏕️, ❌, ✅, etc.)
- Emoji with modifiers (👍🏻, etc.)
- Regional indicators (🇺🇸, etc.)
- Keycap sequences (#️⃣, etc.)
- Zero-width joiners

**Regex Pattern:**
```python
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "]+",
    flags=re.UNICODE
)
```

## Integration Examples

### In Command Handlers

```python
from core.services.theme_messenger import get_theme_messenger

class BackupHandler:
    def __init__(self):
        self.messenger = get_theme_messenger()
    
    def handle_backup(self, filename):
        try:
            # Perform backup...
            return self.messenger.format_message(
                "success_operation",
                operation="backup",
                target=filename
            )
        except Exception as e:
            return self.messenger.format_message(
                "error_failed",
                operation="backup",
                reason=str(e)
            )
```

### In Error Messages

```python
# Permission denied
if not has_permission:
    return messenger.format_message(
        "error_permission",
        action="delete files",
        required_role="admin"
    )

# Resource limit warning
if disk_usage > 0.75:
    return messenger.format_message(
        "warning_limit",
        resource="disk",
        usage=f"{disk_usage*100:.1f}%",
        threshold="75%"
    )
```

### In Status Displays

```python
# Component status
msg = messenger.format_message(
    "info_status",
    component="pattern learner",
    status="15 patterns learned"
)

# Progress update
msg = messenger.format_message(
    "{action} in progress: {progress}",
    progress=f"{current}/{total} ({percent}%)"
)
```

### In uPY Scripts

```upy
# Get theme-aware message
GET (theme_message|success_operation|operation=backup|target=data.json) → {$msg}
PRINT ({$msg})

# Theme-aware error
IF {$error_occurred}
  GET (theme_message|error_failed|operation=save|reason={$error}) → {$msg}
  PRINT ({$msg})
END IF
```

## Custom Themes

### Create Theme Vocabulary

```python
# In memory/bank/system/themes/custom.json
{
  "name": "custom",
  "vocabulary": {
    "location": "zone",
    "user": "operative",
    "action": "operation",
    "system": "mainframe",
    "data": "intel"
  },
  "messages": {
    "success_operation": "✅ Operation complete: {operation} → {target}",
    "error_permission": "❌ Access denied. Operation requires {required_role}."
  }
}
```

### Load Custom Theme

```python
from core.services.theme_messenger import get_theme_messenger

messenger = get_theme_messenger()
messenger.load_theme('custom')

msg = messenger.format_message(
    "success_operation",
    operation="infiltrate",
    target="mainframe"
)
# Output: "✅ Operation complete: infiltrate → mainframe"
```

## Message Categories

### Success Messages

- `success_operation` - Operation completed successfully
- `success_created` - Resource created
- `success_updated` - Resource updated
- `success_deleted` - Resource deleted

### Error Messages

- `error_permission` - Permission denied
- `error_not_found` - Resource not found
- `error_invalid` - Invalid input
- `error_failed` - Operation failed

### Warning Messages

- `warning_limit` - Resource limit approaching
- `warning_deprecated` - Feature deprecated
- `warning_conflict` - Conflict detected

### Info Messages

- `info_status` - Status update
- `info_progress` - Progress update
- `info_reminder` - Reminder or tip

## Configuration

### Enable/Disable Emoji

```bash
CONFIG
# Navigate to [Interface] tab
# Toggle: Emoji mode (on/off)
```

Or via Python:

```python
from core.config import Config

config = Config()
config.set('emoji_mode', False)  # Disable emoji
config.save()
```

### Set Default Theme

```bash
THEME SET foundation
```

Or via Python:

```python
config.set('theme', 'foundation')
config.save()
```

### Theme Persistence

Theme settings stored in `memory/bank/user/user.json`:

```json
{
  "interface": {
    "theme": "foundation",
    "emoji_mode": true
  }
}
```

## Best Practices

### 1. Use Vocabulary Variables

```python
# ✅ Good - Uses theme vocabulary
msg = f"{user}, {action} complete at {location}"

# ❌ Bad - Hardcoded terms
msg = "User, command complete at sector"
```

### 2. Provide All Required Variables

```python
# ✅ Good - All variables provided
msg = messenger.format_message(
    "success_operation",
    operation="backup",
    target="data.json"
)

# ❌ Bad - Missing 'target'
msg = messenger.format_message(
    "success_operation",
    operation="backup"
)
# Raises KeyError
```

### 3. Use Standard Message Types

```python
# ✅ Good - Standard type
msg = messenger.format_message("success_operation", ...)

# ⚠️ OK - Custom template (but less consistent)
msg = messenger.format_message("Custom: {var}", var="value")
```

### 4. Handle Emoji Mode

```python
# ✅ Good - Emoji added by messenger
msg = messenger.format_message("success_operation", ...)

# ❌ Bad - Hardcoded emoji (won't be stripped in plaintext)
msg = f"✅ {messenger.format_message(...)}"
```

### 5. Test Across Themes

```bash
# Test with different themes
THEME SET galaxy
MY_COMMAND

THEME SET foundation
MY_COMMAND

THEME SET plaintext
MY_COMMAND
```

## Troubleshooting

### "KeyError: variable name"

Missing variable in format_message call:

```python
# Error
msg = messenger.format_message(
    "success_operation",
    operation="backup"
    # Missing 'target' variable
)

# Fix
msg = messenger.format_message(
    "success_operation",
    operation="backup",
    target="data.json"
)
```

### "Emoji not stripped in plaintext"

Emoji mode still enabled:

```bash
CONFIG
# Set: Emoji mode → off
```

### "Custom theme not loading"

Check theme file:
1. File exists: `memory/bank/system/themes/custom.json`
2. Valid JSON syntax
3. Contains "vocabulary" and "messages" keys

### "Message not themed"

Using hardcoded strings instead of messenger:

```python
# ❌ Wrong
return "✅ Operation complete"

# ✅ Correct
return messenger.format_message("success_operation", ...)
```

## Technical Details

### Message Resolution Order

1. Load theme vocabulary (or fallback to 'foundation')
2. Load message template (or use provided string)
3. Inject context variables (`{user}`, `{location}`, etc.)
4. Format with f-string interpolation
5. Strip emoji if plaintext mode enabled
6. Return final message

### Vocabulary Inheritance

Themes can extend other themes:

```json
{
  "name": "custom",
  "extends": "galaxy",
  "vocabulary": {
    "user": "captain"  // Override galaxy's "commander"
    // Other terms inherited from galaxy
  }
}
```

### Performance

- Theme loaded once at startup
- Messages formatted on-demand (minimal overhead)
- Emoji stripping via compiled regex (fast)
- No caching needed (format time < 1ms)

## API Reference

### get_theme_messenger()

Factory function, returns singleton instance:

```python
from core.services.theme_messenger import get_theme_messenger

messenger = get_theme_messenger()
```

### format_message(template, **kwargs)

Format message with theme vocabulary:

```python
msg = messenger.format_message(
    "success_operation",
    operation="backup",
    target="data.json"
)
```

**Parameters:**
- `template` (str): Message template or standard type
- `**kwargs`: Variables for f-string interpolation

**Returns:** Formatted message string

### load_theme(theme_name)

Load theme vocabulary:

```python
messenger.load_theme('galaxy')
```

### get_vocabulary()

Get current theme vocabulary:

```python
vocab = messenger.get_vocabulary()
# {'location': 'sector', 'user': 'commander', ...}
```

## See Also

- [Theme System](Theme-System.md) - Complete theme documentation
- [Configuration Guide](Getting-Started.md#configuration) - System configuration
- [Style Guide](Style-Guide.md) - UI/UX guidelines
- [Extension Development](Extension-Development.md) - Custom themes in extensions

## Version History

- **v1.2.22** (Dec 2025) - Initial release
  - Universal theme-aware messaging
  - 7 built-in themes with unique vocabularies
  - F-string interpolation with context variables
  - Emoji stripping for plaintext mode
  - Extensible theme system
