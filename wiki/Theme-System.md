# Theme System

**Version**: 1.0.13
**Last Updated**: 8 November 2025

The uDOS Theme System provides comprehensive customization of the user interface, terminology, and experience. Create, share, and switch between themes to match your workflow, aesthetic preferences, or accessibility needs.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Available Themes](#available-themes)
4. [Theme Commands](#theme-commands)
5. [Creating Custom Themes](#creating-custom-themes)
6. [Theme Structure](#theme-structure)
7. [Sharing Themes](#sharing-themes)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is a Theme?

A uDOS theme controls:
- **Command terminology** (e.g., "LIST" vs "SCAN" vs "INDEX")
- **System prompts** (e.g., `>` vs `❯` vs `QUEST>`)
- **User defaults** (name, title, location)
- **Message styles** (success/error prefixes and formatting)
- **Character attributes** (for RPG-style themes)
- **Object categorization** (file types, rarities)
- **Location tracking** (coordinate systems)

### Why Use Themes?

- **Personalization**: Match your style and workflow
- **Context switching**: Different themes for different tasks
- **Accessibility**: High-contrast and screen-reader friendly options
- **Fun**: Transform uDOS into a game, sci-fi console, or professional tool
- **Sharing**: Export and share themes with others

---

## Quick Start

### View Current Theme
```
THEME
```

### List Available Themes
```
THEME LIST
THEME LIST DETAILED
```

### Preview a Theme
```
THEME PREVIEW foundation
THEME PREVIEW galaxy
```

### Switch Theme
```
THEME foundation
THEME galaxy
```

### Create Your Own
```
THEME CREATE INTERACTIVE
```

---

## Available Themes

### Built-in Themes

#### 🏛️ Foundation
**Style**: Isaac Asimov / Apple TV Foundation series
**Best For**: Knowledge work, encyclopedia building, sci-fi fans
**Prompt**: `TERMINUS>`
**Notable Commands**: RETRIEVE, ARCHIVE, REGISTRY

#### 🌌 Galaxy
**Style**: Space exploration and galactic operations
**Best For**: Space-themed workflows, exploration tasks
**Prompt**: `GALAXY>`
**Notable Commands**: SCAN, NAVIGATE, TRANSMIT

#### ⚔️ Dungeon
**Style**: Fantasy RPG and dungeon crawling
**Best For**: Creative writing, game design, adventure themes
**Prompt**: `QUEST>`
**Notable Commands**: INVENTORY, EXAMINE, CAST

#### 🔬 Science
**Style**: Scientific research and laboratory work
**Best For**: Research tasks, data analysis, academic work
**Prompt**: `LAB>`
**Notable Commands**: OBSERVE, MEASURE, ANALYZE

#### 🎯 Project
**Style**: Project management and task tracking
**Best For**: Project-based work, team coordination
**Prompt**: `PROJECT>`
**Notable Commands**: TASKS, SCHEDULE, TRACK

### Template Themes

Located in `data/themes/templates/`:

#### 🎨 Minimal
Basic template with only required fields. Perfect starting point for custom themes.

#### 🌙 Dark Modern
Developer-focused dark theme with modern terminology (LS, EXEC, CD).

#### ☀️ Light Professional
Business-oriented light theme with corporate terminology (INDEX, OVERVIEW).

#### ♿ High Contrast
Accessibility-optimized theme with maximum contrast and clear labels.

---

## Theme Commands

### Basic Commands

#### THEME
Show current theme information
```
THEME
```

#### THEME LIST [DETAILED]
List all available themes
```
THEME LIST
THEME LIST DETAILED
```

#### THEME <name>
Switch to a different theme
```
THEME foundation
THEME galaxy
```

### Preview & Information

#### THEME PREVIEW <name>
Preview a theme without applying it
```
THEME PREVIEW foundation
```
Shows:
- System prompt and name
- User configuration
- Command terminology examples
- Message styles
- Character/object themes

#### THEME DETAILS <name>
Show detailed theme information
```
THEME DETAILS foundation
```
Shows:
- Metadata (author, version, description)
- Validation status
- Available sections
- Sample terminology

#### THEME STATS
Show theme statistics
```
THEME STATS
```
Shows:
- Total themes available
- Themes by style category
- Cache information

### Creating Themes

#### THEME CREATE INTERACTIVE
Step-by-step theme creation wizard
```
THEME CREATE INTERACTIVE
```
Guides you through:
1. Choosing a base template
2. Setting basic information
3. Customizing system configuration
4. Customizing user settings
5. Customizing command terminology

#### THEME CREATE FROM <template>
Create from a template quickly
```
THEME CREATE FROM minimal
THEME CREATE FROM dark-modern
THEME CREATE FROM light-professional
THEME CREATE FROM high-contrast
```

#### THEME COPY <source> <new_name>
Copy and modify an existing theme
```
THEME COPY foundation my-foundation
THEME COPY galaxy custom-space
```

#### THEME TEMPLATES
List available templates
```
THEME TEMPLATES
```

### Sharing Themes

#### THEME EXPORT <name> [path]
Export theme to shareable file
```
THEME EXPORT my-theme
THEME EXPORT my-theme my-theme.udostheme
THEME EXPORT foundation foundation-v1.udostheme
```
Creates a `.udostheme` file that can be shared.

#### THEME IMPORT <path> [name]
Import a theme from file
```
THEME IMPORT downloaded-theme.udostheme
THEME IMPORT downloaded-theme.udostheme custom-name
```

### Validation

#### THEME VALIDATE <name>
Check theme structure and completeness
```
THEME VALIDATE my-theme
```
Shows:
- Validation status (VALID/INVALID)
- Missing fields or sections
- Structural errors

### Backup & Restore

#### THEME BACKUP
Backup current theme settings
```
THEME BACKUP
```

#### THEME RESTORE
Restore theme from backup
```
THEME RESTORE
```

---

## Creating Custom Themes

### Method 1: Interactive Wizard (Recommended)

```
THEME CREATE INTERACTIVE
```

**Step 1: Choose Template**
- Minimal: Start from scratch
- Sci-Fi: Space/technology theme
- Fantasy: RPG/adventure theme
- Corporate: Professional/business theme

**Step 2: Basic Information**
- Theme name (e.g., `CYBERPUNK`)
- Display name (e.g., "Cyberpunk 2077")
- Style (e.g., "Cyberpunk/Sci-Fi")
- Description
- Icon (emoji)

**Step 3: System Configuration**
- Command prompt (e.g., `NEURO>`)
- System name

**Step 4: User Configuration**
- User name, title, location
- Default project settings

**Step 5: Command Terminology**
- Customize command names
- Examples: LIST → SCAN, LOAD → JACK_IN

**Result**: Theme saved and ready to use!

### Method 2: Template-Based

```
THEME CREATE FROM dark-modern
```

Then customize specific fields when prompted:
- Theme name
- Display name
- Description

Fast way to create themes with pre-configured structure.

### Method 3: Copy Existing

```
THEME COPY foundation my-foundation
```

Clone an existing theme and modify specific elements:
- Change description
- Change icon
- Adjust terminology

Perfect for making variations of themes you like.

### Method 4: Manual Creation

Create a JSON file in `data/themes/`:

```json
{
  "THEME_NAME": "MY_THEME",
  "VERSION": "1.0.0",
  "NAME": "My Custom Theme",
  "STYLE": "Custom",
  "DESCRIPTION": "My personalized theme",
  "ICON": "🎨",
  "CORE_SYSTEM": { ... },
  "CORE_USER": { ... },
  "TERMINOLOGY": { ... }
}
```

See [Theme Structure](#theme-structure) for complete format.

---

## Theme Structure

### Required Fields

```json
{
  "THEME_NAME": "UNIQUE_NAME",
  "VERSION": "1.0.0",
  "NAME": "Display Name",
  "STYLE": "Theme Style",
  "DESCRIPTION": "Brief description",
  "ICON": "🎨"
}
```

### Core Sections

#### CORE_SYSTEM
System-level configuration:
```json
{
  "CORE_SYSTEM": {
    "PROMPT_BASE": ">",
    "SYSTEM_NAME": "SYSTEM",
    "SYSTEM_STATUS": "OPERATIONAL",
    "SYSTEM_VERSION": "1.0.0"
  }
}
```

#### CORE_USER
User defaults:
```json
{
  "CORE_USER": {
    "USER_NAME": "User",
    "USER_TITLE": "Operator",
    "USER_LOCATION": "Terminal",
    "USER_TIMEZONE": "UTC",
    "USER_PROJECT": "Default Project",
    "USER_PROJECT_TYPE": "General",
    "USER_MODE": "Standard",
    "USER_LEVEL": "User",
    "USER_EXPERIENCE": 0
  }
}
```

#### TERMINOLOGY
Command name mappings:
```json
{
  "TERMINOLOGY": {
    "PROMPT_BASE": ">",
    "CMD_CATALOG": "LIST",
    "CMD_LOAD": "LOAD",
    "CMD_SAVE": "SAVE",
    "CMD_RUN": "RUN",
    "CMD_CLS": "CLEAR",
    "CMD_HELP": "HELP",
    "CMD_MAP": "MAP",
    "CMD_EDIT": "EDIT"
  }
}
```

### Optional Sections

#### MESSAGE_STYLES
Message formatting:
```json
{
  "MESSAGE_STYLES": {
    "ACTION_SUCCESS": {
      "PREFIX": "✓",
      "SUFFIX": "",
      "STYLE": "Success"
    },
    "ERROR": {
      "PREFIX": "❌",
      "SUFFIX": "",
      "STYLE": "Error"
    }
  }
}
```

#### CHARACTER_TYPES
RPG-style character attributes:
```json
{
  "CHARACTER_TYPES": {
    "CHARACTER_NAME": "Adventurer",
    "CHARACTER_CLASS": "Explorer",
    "CHARACTER_LEVEL": 1,
    "CHARACTER_HP": 100,
    "CHARACTER_MAX_HP": 100
  }
}
```

#### OBJECT_TYPES
Object categorization:
```json
{
  "OBJECT_TYPES": {
    "OBJECT_CATEGORIES": {
      "FILE": "Standard file",
      "FOLDER": "Directory"
    }
  }
}
```

#### LOCATION_TRACKING
Coordinate systems:
```json
{
  "LOCATION_TRACKING": {
    "LOCATION_SYSTEM": "File System",
    "LOCATION_PRECISION": "Directory-Level",
    "COORDINATE_SYSTEM": "ABSOLUTE_PATH"
  }
}
```

### Complete Example

See `data/themes/templates/minimal.json` for a complete minimal theme.
See `data/themes/foundation.json` for a full-featured theme.

---

## Sharing Themes

### Exporting Themes

**Export your theme:**
```
THEME EXPORT my-awesome-theme
```

**Result**: `my-awesome-theme.udostheme` file created.

**Share the file** via:
- Email
- GitHub
- Cloud storage
- uDOS community forums

### Importing Themes

**Import a shared theme:**
```
THEME IMPORT awesome-theme.udostheme
```

**Import with custom name:**
```
THEME IMPORT awesome-theme.udostheme my-custom-name
```

### .udostheme Format

The `.udostheme` format includes:
- Complete theme JSON structure
- Export metadata (date, uDOS version)
- Format version for compatibility

### Theme Validation on Import

All imported themes are automatically validated:
- ✅ Required fields checked
- ✅ Structure validated
- ✅ Safety checks applied
- ❌ Invalid themes rejected with error details

---

## Best Practices

### 1. Start Simple
- Use `THEME CREATE FROM minimal` for maximum control
- Use themed templates for faster setup
- Preview before applying: `THEME PREVIEW <name>`

### 2. Stay Consistent
- Match terminology to your theme's style
- Use consistent message prefixes
- Keep naming conventions uniform
- Group related commands with similar names

### 3. Test Thoroughly
- Validate: `THEME VALIDATE <name>`
- Preview: `THEME PREVIEW <name>`
- Test with actual commands
- Get feedback from others

### 4. Consider Accessibility
- Ensure sufficient contrast
- Use clear, descriptive labels
- Test with screen readers if possible
- Consider color-blind users
- Add accessibility metadata for high-contrast themes

### 5. Document Your Theme
- Write clear descriptions
- Include usage examples
- List notable features
- Credit inspiration sources
- Add version history

### 6. Organize Terminology
**File Operations**:
- CMD_CATALOG (list files)
- CMD_LOAD (open)
- CMD_SAVE (save)

**Navigation**:
- CMD_MAP (overview)
- CMD_GOTO (navigate)
- CMD_WHERE (location)

**System**:
- CMD_HELP (help)
- CMD_RESTART (restart)
- CMD_REPAIR (repair)

### 7. Version Your Themes
Use semantic versioning:
- `1.0.0` - Initial release
- `1.1.0` - New features
- `1.0.1` - Bug fixes

---

## Troubleshooting

### Theme Not Found
**Error**: `Theme 'xyz' not found`

**Solutions**:
1. Check spelling: `THEME LIST`
2. Ensure file exists in `data/themes/`
3. Check file extension is `.json`
4. Validate JSON syntax

### Invalid Theme
**Error**: `Theme is INVALID`

**Solutions**:
1. Run: `THEME VALIDATE <name>`
2. Check error messages
3. Compare with working theme
4. Use auto-fix: Theme Builder does this automatically
5. Start from template

### Import Failed
**Error**: `Failed to import theme`

**Solutions**:
1. Check file extension (`.udostheme`)
2. Validate file is not corrupted
3. Ensure file contains valid JSON
4. Check for name conflicts
5. Try importing with different name

### Commands Not Working
**Issue**: Commands use old terminology after theme switch

**Solutions**:
1. Restart uDOS (if dynamic switching not enabled)
2. Check TERMINOLOGY section in theme
3. Verify theme was actually applied: `THEME`
4. Try: `THEME BACKUP` then `THEME RESTORE`

### Preview Looks Wrong
**Issue**: Preview doesn't match expectations

**Solutions**:
1. This is just a preview - actual appearance may vary
2. Check MESSAGE_STYLES section
3. Validate theme structure
4. Compare with similar theme

---

## Examples

### Creating a Cyberpunk Theme

```
THEME CREATE FROM dark-modern
```

Customize:
- **THEME_NAME**: "CYBERPUNK"
- **NAME**: "Cyberpunk 2077"
- **DESCRIPTION**: "Dystopian future hacking theme"
- **ICON**: "🌃"
- **PROMPT_BASE**: "NEURO>"
- **CMD_CATALOG**: "SCAN"
- **CMD_LOAD**: "JACK_IN"
- **CMD_SAVE**: "UPLOAD"
- **CMD_RUN**: "EXECUTE"
- **CMD_HELP**: "MATRIX"

### Creating a Fantasy Theme

```
THEME CREATE FROM minimal
```

Customize:
- **THEME_NAME**: "FANTASY"
- **NAME**: "Fantasy Quest"
- **DESCRIPTION**: "Medieval fantasy adventure"
- **ICON**: "⚔️"
- **PROMPT_BASE**: "QUEST>"
- **CMD_CATALOG**: "INVENTORY"
- **CMD_LOAD**: "EXAMINE"
- **CMD_SAVE**: "CHRONICLE"
- **CMD_RUN**: "CAST"
- **CMD_HELP**: "GUIDE"

### Creating an Accessible Theme

```
THEME COPY high-contrast my-accessible
```

Then adjust:
- Increase contrast ratios
- Add verbose labels
- Clear message prefixes
- Test with screen readers

---

## Advanced Topics

### Theme Inheritance
Build on existing themes:
```
THEME COPY foundation foundation-custom
```
Modify specific aspects while keeping the base.

### Context-Aware Theming
(Planned for v1.0.14+)
- Different themes for different commands
- Automatic theme switching based on context
- Per-workspace themes

### Theme Collections
Organize related themes:
- Create theme families (light/dark variants)
- Group by style (sci-fi collection)
- Share as bundles

---

## Resources

### Files & Directories
- **Themes**: `data/themes/*.json`
- **Templates**: `data/themes/templates/*.json`
- **Template Documentation**: `data/themes/templates/README.md`
- **Theme Schema**: `data/themes/_schema.json`

### Commands Reference
See: [[Command-Reference#theme-commands]]

### Related Documentation
- [[Customization]] - General customization options
- [[Configuration]] - System configuration
- [[Extensions-System]] - Extending uDOS

### Community
- Share themes on GitHub
- uDOS community forums
- Theme showcase gallery (coming soon)

---

## Version History

**v1.0.13** (November 2025)
- Complete theme system overhaul
- Interactive theme creation wizard
- 4 starter templates
- Import/export functionality
- Validation system
- Preview system
- 10+ new THEME commands

**v1.0.10** (October 2025)
- Typography system integration
- 8 themed fonts
- NES.css framework

**v1.0.0** (September 2025)
- Initial theme system
- Basic theme switching
- 5 built-in themes

---

## See Also

- [[Quick-Start]] - Getting started with uDOS
- [[Command-Reference]] - Complete command reference
- [[Customization]] - Other customization options
- [[Style-Guide]] - uDOS style guidelines

