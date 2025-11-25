# uDOS Theme System Guide

## Overview

The uDOS theme system allows complete customization of command terminology and system messages. Themes are stored as JSON files and support user overrides via the `/memory` directory.

## Architecture

### Directory Structure

```
knowledge/system/themes/     # Bundled themes (read-only)
├── default.json            # Standard uDOS theme
├── teletext.json           # BBC Ceefax style
├── dungeon.json            # RPG dungeon master
├── foundation.json         # Isaac Asimov Foundation
├── galaxy.json             # Hitchhiker's Guide style
└── ...

memory/system/themes/        # User customizations (writable)
├── default.json            # Override default theme
└── custom.json             # User-created themes
```

### Loading Priority

1. **Bundled theme** loaded from `knowledge/system/themes/`
2. **User overrides** from `memory/system/themes/` merged on top
3. **Message precedence**: MESSAGES (full templates) > TERMINOLOGY (tokens)

## Theme File Structure

### Required Keys

Every theme must include:

```json
{
  "THEME_NAME": "theme_name",
  "TERMINOLOGY": { ... },
  "MESSAGES": { ... }
}
```

### Optional Metadata

```json
{
  "VERSION": "1.0.2",
  "NAME": "Human-Readable Theme Name",
  "STYLE": "Aesthetic inspiration",
  "ICON": "📺",
  "DESCRIPTION": "Brief theme description"
}
```

### TERMINOLOGY Section

Maps command names to themed aliases:

```json
{
  "TERMINOLOGY": {
    "PROMPT_BASE": ">",
    "CMD_CATALOG": "CATALOG",
    "CMD_LOAD": "LOAD",
    "CMD_SAVE": "SAVE",
    "CMD_HELP": "HELP",
    "CMD_EXIT": "EXIT"
  }
}
```

### MESSAGES Section

Defines system messages with format placeholders:

```json
{
  "MESSAGES": {
    "ERROR_CRASH": "ERROR: Command '{command}' failed",
    "ERROR_UNKNOWN_MODULE": "Unknown module '{module}'",
    "INFO_EXIT": "Goodbye! Session terminated.",
    "ACTION_SUCCESS": "Operation completed successfully"
  }
}
```

#### Nested Structure (Optional)

Messages can be organized by category:

```json
{
  "MESSAGES": {
    "SUCCESS": {
      "ACTION_SUCCESS": "✓ Operation complete",
      "ACTION_SUCCESS_REPAIR": "✓ System repaired"
    },
    "ERROR": {
      "ERROR_CRASH": "⚠ Failed: {command}",
      "ERROR_GENERIC": "⚠ {error}"
    }
  }
}
```

### Required Messages

All themes must define:

- `ERROR_CRASH` - Command execution failure
- `ERROR_INVALID_UCODE_FORMAT` - Malformed command syntax
- `ERROR_UNKNOWN_MODULE` - Unknown module reference
- `ERROR_UNKNOWN_SYSTEM_COMMAND` - Unrecognized system command
- `ERROR_UNKNOWN_FILE_COMMAND` - Unrecognized file command
- `ERROR_GENERIC` - Generic error fallback
- `INFO_EXIT` - Session termination message

## Creating Themes

### 1. Start with Template

Copy an existing theme as starting point:

```bash
cp knowledge/system/themes/default.json memory/system/themes/mytheme.json
```

### 2. Edit Metadata

```json
{
  "THEME_NAME": "mytheme",
  "NAME": "My Custom Theme",
  "STYLE": "Your aesthetic inspiration",
  "ICON": "🎨",
  "DESCRIPTION": "What makes this theme unique"
}
```

### 3. Customize Terminology

Rename commands to match your theme:

```json
{
  "TERMINOLOGY": {
    "PROMPT_BASE": ">>>",
    "CMD_CATALOG": "INDEX",
    "CMD_LOAD": "OPEN",
    "CMD_HELP": "GUIDE"
  }
}
```

### 4. Customize Messages

Rewrite system messages:

```json
{
  "MESSAGES": {
    "ERROR_CRASH": "🔥 SYSTEM FAULT: {command} crashed",
    "INFO_EXIT": "👋 See you later!"
  }
}
```

### 5. Validate Theme

Run the validator to check for errors:

```bash
python3 core/utils/theme_validator.py
```

Look for your theme in the report:
```
✅ VALID: mytheme
```

Or check specific theme programmatically:

```python
from core.theme_loader import ThemeValidator
from pathlib import Path

validator = ThemeValidator()
is_valid, errors = validator.validate_theme_file(
    Path('memory/system/themes/mytheme.json')
)
print(f"Valid: {is_valid}")
if errors:
    print(f"Errors: {errors}")
```

## User Customization

### Override Bundled Themes

Users can customize bundled themes without modifying core files:

1. Create override file: `memory/system/themes/default.json`
2. Include only the fields you want to change:

```json
{
  "MESSAGES": {
    "INFO_EXIT": "Customized goodbye message!"
  }
}
```

3. The override merges with the bundled theme automatically

### Create Personal Themes

Users can create entirely new themes in `/memory`:

```bash
# Create user theme
nano memory/system/themes/personal.json
```

Theme will be available system-wide once created.

## Validation

### Schema Requirements

The validator checks:

1. **Required keys** - THEME_NAME, TERMINOLOGY, MESSAGES
2. **Required messages** - All critical messages present
3. **Format strings** - Valid Python format placeholders
4. **Type safety** - Messages are strings, not nested objects (unless categorized)

### Running Validation

```bash
# Validate all themes
python3 core/utils/theme_validator.py

# Output:
# ======================================================================
# uDOS THEME VALIDATION REPORT
# ======================================================================
#
# ✅ VALID: default
# ✅ VALID: teletext
# ✅ VALID: dungeon
# ...
# ======================================================================
# Summary: 8/8 themes valid
# ======================================================================
```

### Common Validation Errors

**Missing required keys:**
```
❌ INVALID: mytheme
  └─ Missing required keys: MESSAGES
```
Fix: Add MESSAGES section

**Invalid format string:**
```
❌ INVALID: mytheme
  └─ Message ERROR_CRASH has invalid format string: single '}' encountered in format string
```
Fix: Escape braces or use proper format syntax

**Missing required messages:**
```
❌ INVALID: mytheme
  └─ Missing required messages: ERROR_CRASH, INFO_EXIT
```
Fix: Add required message keys

## Testing

### Unit Tests

Run comprehensive theme tests:

```bash
python3 core/tests/test_themes.py
```

Tests cover:
- Theme loading (bundled + memory)
- Message formatting with placeholders
- User override merging
- Validation edge cases
- Format string safety

### Manual Testing

Load and preview theme in uDOS:

```
uDOS> THEME mytheme
uDOS> THEME PREVIEW mytheme
```

## Format Placeholders

### Common Placeholders

Messages support Python format strings:

| Placeholder | Usage | Example |
|-------------|-------|---------|
| `{command}` | Failed command name | `ERROR: '{command}' not found` |
| `{error}` | Error description | `ERROR: {error}` |
| `{module}` | Module name | `Module '{module}' unavailable` |
| `{ucode}` | uCode command | `Invalid: {ucode}` |
| `{file_path}` | File path | `Loaded: {file_path}` |

### Safe Formatting

The system handles missing placeholders gracefully:

```python
# In code:
try:
    message = template.format(command='HELP')
except KeyError:
    message = template  # Fallback to unformatted
```

## Best Practices

### 1. Consistent Voice

Maintain consistent tone throughout theme:

```json
{
  "MESSAGES": {
    "ERROR_CRASH": "⚠️ SYSTEM MALFUNCTION: {command}",
    "ERROR_GENERIC": "⚠️ DIAGNOSTIC ERROR: {error}",
    "INFO_EXIT": "🔧 SYSTEM SHUTDOWN COMPLETE"
  }
}
```

### 2. Preserve Placeholders

Keep all original placeholders:

```json
// ❌ BAD - Missing {command} placeholder
"ERROR_CRASH": "Something went wrong"

// ✅ GOOD - Preserves {command}
"ERROR_CRASH": "Command '{command}' failed unexpectedly"
```

### 3. Test Format Strings

Verify messages work with real values:

```python
from core.theme import load_theme

theme = load_theme('mytheme')
msg = theme['MESSAGES']['ERROR_CRASH']
print(msg.format(command='TEST'))  # Should not raise KeyError
```

### 4. Keep Metadata Current

Update VERSION and DESCRIPTION when making changes:

```json
{
  "VERSION": "1.0.3",
  "DESCRIPTION": "Updated error messages for clarity"
}
```

## Maintenance Workflow

### Regular Tasks

1. **Validate all themes** after modifications:
   ```bash
   python3 core/utils/theme_validator.py
   ```

2. **Run theme tests** before committing:
   ```bash
   python3 core/tests/test_themes.py
   ```

3. **Update documentation** when adding new messages

4. **Version themes** to track changes over time

### Adding New Messages

When adding a new message key system-wide:

1. Add to `default.json` (reference implementation)
2. Add to validator's `REQUIRED_MESSAGES` if critical
3. Update all existing themes with the new key
4. Run validation to verify completeness
5. Update this guide with placeholder documentation

### Deprecating Messages

When removing messages:

1. Mark as deprecated in documentation
2. Keep in themes for 1-2 versions (backward compatibility)
3. Remove from validator's required list
4. Clean up from all themes in next major version

## Troubleshooting

### Theme Not Loading

**Symptom:** Theme changes don't appear

**Solutions:**
- Check file is in `memory/system/themes/`
- Verify JSON syntax with validator
- Restart uDOS to reload theme cache

### Format Errors

**Symptom:** Messages show `{placeholder}` literally

**Solutions:**
- Ensure placeholder names match code
- Check for typos in placeholder names
- Verify format string syntax

### Validation Failures

**Symptom:** Theme rejected by validator

**Solutions:**
- Read error messages carefully
- Compare with working theme (e.g., `default.json`)
- Check JSON syntax with linter
- Ensure all required keys present

## Examples

### Minimal Theme

```json
{
  "THEME_NAME": "minimal",
  "TERMINOLOGY": {
    "PROMPT_BASE": ">",
    "CMD_HELP": "HELP"
  },
  "MESSAGES": {
    "ERROR_CRASH": "Error: {command}",
    "ERROR_INVALID_UCODE_FORMAT": "Invalid: {ucode}",
    "ERROR_UNKNOWN_MODULE": "Unknown: {module}",
    "ERROR_UNKNOWN_SYSTEM_COMMAND": "Unknown command: {command}",
    "ERROR_UNKNOWN_FILE_COMMAND": "Unknown file command: {command}",
    "ERROR_GENERIC": "{error}",
    "INFO_EXIT": "Goodbye"
  }
}
```

### User Override

Override just the exit message:

```json
{
  "MESSAGES": {
    "INFO_EXIT": "Peace out! ✌️"
  }
}
```

System merges this with bundled theme automatically.

## Reference

### Files

- `core/utils/theme_loader.py` - Theme loading logic
- `core/utils/theme_validator.py` - Validation tool
- `core/tests/test_themes.py` - Unit tests
- `knowledge/system/themes/` - Bundled themes
- `memory/system/themes/` - User themes

### Commands

```bash
# Validate all themes
python3 core/utils/theme_validator.py

# Run theme tests
python3 core/tests/test_themes.py

# List available themes (in uDOS)
THEME LIST

# Switch theme (in uDOS)
THEME <name>

# Preview theme (in uDOS)
THEME PREVIEW <name>
```

## See Also

- [Theme System Wiki](../wiki/Theme-System.md) - User-facing documentation
- [Style Guide](STYLE-GUIDE.md) - Code style conventions
- [Contributing](../CONTRIBUTING.md) - How to contribute themes
