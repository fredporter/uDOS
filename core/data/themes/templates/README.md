# Theme Templates

Templates for creating custom uDOS themes are **defined in-memory** in `core/theme_builder.py` for performance. JSON reference files archived to `core/data/themes/archive/templates/`.

## Available Templates

### 1. minimal
**Purpose**: Bare-bones template with only required fields
**Best For**: Starting from scratch, maximum customization
**Source**: `theme_builder._get_minimal_template()`
**Features**:
- Clean, simple structure
- Standard command terminology (LIST, LOAD, SAVE, etc.)
- Basic message styles
- No extra sections

### 2. sci-fi
**Purpose**: Space/technology themed template
**Best For**: Science fiction aesthetics, tech-focused projects
**Source**: `theme_builder._get_scifi_template()`
**Features**:
- Tech terminology (SCAN, ACCESS, EXECUTE, etc.)
- CONSOLE> prompt style
- MAINFRAME system naming
- Officer/technician user roles

### 3. fantasy
**Purpose**: RPG/adventure themed template
**Best For**: Gaming, medieval/fantasy aesthetics
**Source**: `theme_builder._get_fantasy_template()`
**Features**:
- Fantasy terminology (INVENTORY, EXAMINE, CHRONICLE, etc.)
- QUEST> prompt style
- Adventure-focused system naming
- Hero/adventurer user roles

### 4. corporate
**Purpose**: Professional business theme
**Best For**: Corporate users, business analysts, office work
**Source**: `theme_builder._get_corporate_template()`
**Features**:
- Professional terminology (OPEN, SAVE, EXECUTE, etc.)
- TERMINAL> prompt style
- Business-oriented system naming
- Clear, formal message styles

## Using Templates

### Command Line (Interactive)
```
THEME CREATE INTERACTIVE
```
Select a template when prompted (minimal, sci-fi, fantasy, corporate).

### Command Line (From Template)
```
THEME CREATE FROM minimal
THEME CREATE FROM sci-fi
THEME CREATE FROM fantasy
THEME CREATE FROM corporate
```

### Programmatic (Python)
```python
from core.theme_builder import ThemeBuilder

builder = ThemeBuilder()
theme = builder.create_from_template("minimal", {
    "THEME_NAME": "MY_THEME",
    "NAME": "My Custom Theme",
    "DESCRIPTION": "My theme description"
})
builder.save_theme(theme)
```

## Theme Structure

### Required Fields (All Templates Have These)
- **THEME_NAME**: Unique uppercase identifier
- **VERSION**: Theme version (e.g., "1.0.0")
- **NAME**: Display name
- **STYLE**: Theme style/category
- **DESCRIPTION**: Brief description
- **ICON**: Emoji icon
- **CORE_SYSTEM**: System configuration
- **CORE_USER**: User defaults
- **TERMINOLOGY**: Command name mappings

### Optional Sections
- **CHARACTER_TYPES**: RPG-style character attributes
- **OBJECT_TYPES**: Object categorization system
- **LOCATION_TRACKING**: Location/coordinate system
- **MESSAGE_STYLES**: Message formatting preferences
- **ACCESSIBILITY**: Accessibility features (high-contrast only)

## Customization Guide

### 1. Basic Information
Edit these fields to personalize your theme:
```json
{
  "THEME_NAME": "YOUR_THEME",
  "NAME": "Your Theme Display Name",
  "DESCRIPTION": "What makes this theme unique",
  "ICON": "🎨",
  "STYLE": "Your theme style category"
}
```

### 2. System Prompt
Customize the command prompt:
```json
{
  "CORE_SYSTEM": {
    "PROMPT_BASE": ">",      // Change to: ❯, $, >, CMD>, etc.
    "SYSTEM_NAME": "SYSTEM"  // Your system's name
  }
}
```

### 3. Command Terminology
Rename commands to match your theme:
```json
{
  "TERMINOLOGY": {
    "CMD_CATALOG": "LIST",   // or: LS, INDEX, DIR, SCAN
    "CMD_LOAD": "LOAD",      // or: OPEN, READ, ACCESS
    "CMD_SAVE": "SAVE",      // or: WRITE, STORE, ARCHIVE
    "CMD_HELP": "HELP"       // or: MANUAL, GUIDE, INFO
  }
}
```

### 4. Message Styles
Customize how messages appear:
```json
{
  "MESSAGE_STYLES": {
    "ACTION_SUCCESS": {
      "PREFIX": "✓",         // Symbol before success messages
      "SUFFIX": "",          // Text after (optional)
      "STYLE": "Success"     // Style hint
    }
  }
}
```

## Tips for Creating Themes

### 1. Start Simple
- Use **minimal.json** for maximum control
- Use themed templates (dark-modern, light-professional) for faster setup

### 2. Stay Consistent
- Match terminology to your theme's style
- Use consistent message prefixes
- Keep naming conventions uniform

### 3. Test Thoroughly
- Use `THEME VALIDATE <name>` to check structure
- Use `THEME PREVIEW <name>` before applying
- Test with different commands

### 4. Consider Accessibility
- Ensure sufficient contrast
- Use clear, descriptive labels
- Test with screen readers if possible
- Consider color-blind users

### 5. Share Your Themes
- Export with `THEME EXPORT <name>`
- Share .udostheme files
- Document special features
- Include usage examples

## Examples

### Creating a Cyberpunk Theme
```
THEME CREATE FROM sci-fi
```
Then customize:
- THEME_NAME: "CYBERPUNK"
- PROMPT_BASE: "NEURO>"
- CMD_CATALOG: "SCAN"
- CMD_LOAD: "JACK_IN"
- CMD_SAVE: "UPLOAD"
- ICON: "🌃"

### Creating a Medieval Theme
```
THEME CREATE FROM fantasy
```
Then customize:
- THEME_NAME: "MEDIEVAL"
- PROMPT_BASE: "QUEST>"
- CMD_CATALOG: "INVENTORY"
- CMD_LOAD: "EXAMINE"
- CMD_SAVE: "CHRONICLE"
- ICON: "⚔️"

### Creating a Business Theme
```
THEME CREATE FROM corporate
```
Then customize:
- THEME_NAME: "BUSINESS"
- PROMPT_BASE: "WORK>"
- CMD_CATALOG: "INDEX"
- CMD_LOAD: "REVIEW"
- CMD_SAVE: "FILE"
- ICON: "💼"

## Validation

All templates pass validation by default. When customizing:

1. Check syntax: `THEME VALIDATE <name>`
2. Preview: `THEME PREVIEW <name>`
3. Test: `THEME <name>` (switch to it)
4. Refine based on experience

## Support

For help with theme creation:
- `THEME TEMPLATES` - List available templates
- `THEME CREATE INTERACTIVE` - Step-by-step wizard
- `THEME DETAILS <name>` - See theme structure
- See `knowledge/customization/THEME-SYSTEM.md` for full documentation

## Version History

- v1.0.0 (Nov 2025) - Initial template library
  - 4 starter templates
  - Complete documentation
  - Full theme builder integration
