# Enhanced SETUP Command - v1.0.12

## Overview

The Enhanced SETUP command provides guided configuration for new users and targeted component setup for advanced users through an interactive wizard system.

## Syntax

```bash
SETUP [mode]
```

## Modes

### 1. Full Interactive Wizard
```bash
SETUP
# or
SETUP WIZARD
```

**4-Step Guided Process:**
1. **Theme Selection** - Choose from 5 themes
2. **Viewport Configuration** - Select screen size preset
3. **Extension Setup** - Enable/disable web extensions
4. **Advanced Settings** - Developer mode, debug logging, experimental features

**Best for**: First-time setup, complete reconfiguration

### 2. Quick Setup
```bash
SETUP QUICK
```

**Instant Configuration:**
- Theme: dungeon (default)
- Viewport: auto (adaptive)
- Extensions: All enabled
- Advanced: All disabled

**Best for**: Getting started quickly, restoring defaults

### 3. Theme Selection Only
```bash
SETUP THEME
```

**Interactive Theme Picker:**
- dungeon - Dark fantasy aesthetic
- foundation - Clean minimalist
- galaxy - Space-inspired colors
- project - Professional workspace
- science - Technical blue/green

**Best for**: Changing look without affecting functionality

### 4. Viewport Configuration Only
```bash
SETUP VIEWPORT
```

**5 Viewport Presets:**
- **Watch** (13×13) - Tiny displays, smartwatches
- **Mobile** (30×20) - Phone screens
- **Tablet** (60×40) - Tablet displays
- **Desktop** (120×80) - Standard monitors
- **Cinema** (360×150) - Ultrawide displays

**Best for**: Optimizing for your screen size

### 5. Extension Management Only
```bash
SETUP EXTENSIONS
```

**Toggle Extensions:**
- **Web Extensions** - Dashboard, markdown viewer, font editor
- **Teletext** - Retro mosaic rendering
- **Dashboard** - Web control panel

**Best for**: Managing optional features

### 6. Help Information
```bash
SETUP HELP
```

**Shows:**
- Available setup modes
- Theme descriptions
- Viewport preset details
- Extension information

**Best for**: Learning about options before configuring

## Features

### Interactive Wizards

Each setup mode provides:
- **Clear Instructions** - Step-by-step guidance
- **Visual Previews** - See options before selecting
- **Validation** - Ensures valid configuration
- **Configuration Summary** - Review before saving
- **Confirmation** - Verify changes before applying

### Theme System

**5 Built-in Themes:**

1. **dungeon** - Dark fantasy (default)
   - Deep colors, atmospheric
   - Best for: Long sessions, low light

2. **foundation** - Clean minimal
   - Simple, clear, professional
   - Best for: Focus, documentation

3. **galaxy** - Space-inspired
   - Blues, purples, stars
   - Best for: Creative work

4. **project** - Professional
   - Balanced, productive
   - Best for: Business use

5. **science** - Technical
   - Blue/green, data-focused
   - Best for: Analysis, coding

### Viewport Presets

**Watch** (13×13 cells)
- 208×208 pixels
- Smartwatch displays
- Minimal UI

**Mobile** (30×20 cells)
- 480×320 pixels
- Phone screens
- Touch-optimized

**Tablet** (60×40 cells)
- 960×640 pixels
- Tablet displays
- Balanced layout

**Desktop** (120×80 cells)
- 1920×1280 pixels
- Standard monitors
- Full features

**Cinema** (360×150 cells)
- 5760×2400 pixels
- Ultrawide displays
- Maximum workspace

### Configuration Validation

SetupWizard validates:
- ✅ Theme exists in `data/themes/`
- ✅ Viewport dimensions are reasonable
- ✅ Extension paths are valid
- ✅ No conflicting settings
- ✅ All required fields present

## Workflow Examples

### New User Setup
```bash
# First time running uDOS
SETUP

# Step 1: Choose theme
# > Options: dungeon, foundation, galaxy, project, science
# > Select: galaxy

# Step 2: Choose viewport
# > Options: watch, mobile, tablet, desktop, cinema
# > Select: desktop

# Step 3: Enable extensions
# > Web extensions? (y/n): y
# > Teletext? (y/n): y
# > Dashboard? (y/n): y

# Step 4: Advanced settings
# > Developer mode? (y/n): n
# > Debug logging? (y/n): n
# > Experimental features? (y/n): n

# Configuration Summary shown
# Confirm? (y/n): y
# ✅ Setup complete!
```

### Quick Theme Change
```bash
# Want different aesthetics
SETUP THEME

# > Current: dungeon
# > Available themes:
# >   1. dungeon - Dark fantasy
# >   2. foundation - Clean minimal
# >   3. galaxy - Space-inspired
# >   4. project - Professional
# >   5. science - Technical
# > Select (1-5): 3

# ✅ Theme changed to galaxy
# Restart to see changes
```

### Optimize for New Display
```bash
# Got ultrawide monitor
SETUP VIEWPORT

# > Current: desktop (120×80)
# > Available presets:
# >   1. Watch (13×13)
# >   2. Mobile (30×20)
# >   3. Tablet (60×40)
# >   4. Desktop (120×80)
# >   5. Cinema (360×150)
# > Select (1-5): 5

# ✅ Viewport set to cinema
# REBOOT to apply
```

### Reset to Defaults
```bash
# Something broken, need defaults
SETUP QUICK

# ✅ Configuration reset:
# - Theme: dungeon
# - Viewport: auto
# - Extensions: all enabled
# - Advanced: all disabled
```

## Configuration Files

### Where Settings Are Stored

**user.json**
```json
{
  "theme": "galaxy",
  "viewport": {
    "width": 120,
    "height": 80,
    "preset": "desktop"
  }
}
```

**data/system/config.json**
```json
{
  "extensions": {
    "enable_web": true,
    "enable_teletext": true,
    "enable_dashboard": true
  },
  "advanced": {
    "developer_mode": false,
    "debug_logging": false,
    "experimental_features": false
  }
}
```

## Tips

### When to Use Each Mode

- **SETUP** - First time or major changes
- **SETUP QUICK** - Need defaults fast
- **SETUP THEME** - Just want different colors
- **SETUP VIEWPORT** - New monitor or device
- **SETUP EXTENSIONS** - Managing optional features
- **SETUP HELP** - Learning about options

### Theme Selection Tips

Choose based on:
- **Session length**: Darker for longer
- **Lighting**: Match your environment
- **Purpose**: Professional vs creative
- **Personal preference**: Test each one

### Viewport Tips

- Start with auto, adjust if needed
- Match your terminal size
- Consider readability
- Bigger isn't always better
- Test before committing

### Extension Management

Enable extensions you'll actually use:
- **Web**: If you use dashboard/editors
- **Teletext**: For retro visualization
- **Dashboard**: For GUI control

Disable unused ones to:
- Reduce startup time
- Save memory
- Simplify interface

## Behind the Scenes

### SetupWizard Service

The SetupWizard (`core/services/setup_wizard.py`) provides:
- Interactive prompts with validation
- Theme loading from `data/themes/_index.json`
- Viewport preset management
- Configuration preview
- Safe configuration saving

### Integration

SETUP integrates with:
- **ConfigManager**: Persistent settings
- **ThemeManager**: Theme loading
- **ViewportManager**: Screen adaptation
- **ExtensionManager**: Feature toggles

## Troubleshooting

### Setup Not Saving

1. Check file permissions
2. Verify paths exist
3. Check for JSON syntax errors
4. Use REPAIR to fix corruption

### Theme Not Loading

1. Run `SETUP THEME` again
2. Check `data/themes/<theme>.json` exists
3. Use REPAIR to restore defaults
4. Try SETUP QUICK to reset

### Viewport Issues

1. Terminal size might override
2. Try `SETUP VIEWPORT` to reselect
3. Use `STATUS` to check current size
4. REBOOT to apply changes

## Related Commands

- **CONFIG** - Configuration management
- **SETTINGS** - User preferences
- **STATUS** - Current configuration
- **REBOOT** - Apply viewport changes

## Version History

- **v1.0.0**: Basic SETUP command
- **v1.0.12**: Complete wizard system with 6 modes

## See Also

- [v1.0.12 Release Notes](../../docs/releases/v1.0.12-RELEASE-NOTES.md)
- [SetupWizard Service](../../core/services/setup_wizard.py)
- [Theme System](../../data/themes/README.md)
