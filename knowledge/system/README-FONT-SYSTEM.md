# uDOS Font System Integration

**Version:** 1.0.24
**Date:** 2024
**Status:** Active

## Overview

The uDOS Font System provides comprehensive font and color management through centralized JSON configuration, enabling consistent typography and theming across all extensions and core functionality.

## Architecture

### Core Components

1. **font-system.json** (`knowledge/system/font-system.json`)
   - Central configuration for fonts, colors, and character sets
   - Defines Synthwave DOS VGA 16-color palette
   - Specifies font families with licensing and fallback stacks
   - Provides block graphics character sets (PETSCII, Unicode, Teletext, ASCII)
   - Includes extension integration mappings

2. **FontSystemManager** (`core/uDOS_settings.py`)
   - Singleton class for font system access
   - Loads and caches font-system.json
   - Provides methods for color palette, font families, block graphics retrieval
   - Integrated into SettingsManager

3. **FontGraphicsHelper** (`core/uDOS_graphics.py`)
   - Helper class for font-based terminal graphics
   - ANSI color code generation from Synthwave DOS palette
   - Block character retrieval from multiple charsets
   - Text colorization utilities
   - Retro banner generation

4. **Character Editor Integration** (`extensions/core/character-editor/`)
   - Profile management UI (Load/Save Profile buttons)
   - Template duplication from `font-profile-template.json`
   - Custom font profile editing and export
   - Color scheme application

## Configuration Files

### System Configuration

**`knowledge/system/font-system.json`** (400+ lines)
```json
{
  "color_palette": {
    "black": { "hex": "#000000", "rgb": [0,0,0], "ansi": "\\033[30m", "tput": "setaf 0" },
    // ... 16 VGA colors with brightness variants and transparency levels
  },
  "font_families": {
    "chicago": {
      "variants": ["Chicago", "ChicagoFLF"],
      "fallback_stack": "'Chicago', 'Chicago FLF', -apple-system, BlinkMacSystemFont, monospace",
      "licensing": "Public Domain, CC BY-SA 3.0"
    }
    // ... mallard, petme, mode7gx3
  },
  "block_graphics": {
    "unicode": { /* box drawing, blocks */ },
    "petscii": { /* C64 graphics */ },
    "teletext": { /* Teletext mosaics */ },
    "ascii": { /* ASCII extended */ }
  },
  "extensions_integration": {
    "c64-terminal": { "font": "PetMe64", "charset": "petscii" },
    "teletext": { "font": "MODE7GX3", "charset": "teletext" }
    // ... per-extension font recommendations
  }
}
```

### User Templates

**`data/templates/font-profile-template.json`** (200+ lines)
```json
{
  "metadata": {
    "name": "Custom Font Profile",
    "version": "1.0.0",
    "author": "",
    "based_on": "Synthwave DOS v1.0.24"
  },
  "font_settings": {
    "primary_font": "Chicago",
    "fallback_fonts": ["Monaco", "Courier New", "monospace"],
    "font_size": { "base": "16px", "small": "12px", "large": "24px" }
  },
  "color_scheme": {
    "custom_colors": {
      "primary": { "hex": "#8ECAE6", "name": "Cyan Bright" },
      // ... customizable color mappings
    }
  },
  "character_mappings": {
    "custom_chars": {
      "logo": "🌀",
      // ... user-defined character assignments
    }
  }
}
```

## Python API

### FontSystemManager

```python
from core.uDOS_settings import FontSystemManager

# Get singleton instance
font_sys = FontSystemManager.get_instance()

# Access color palette
palette = font_sys.get_color_palette()
cyan_bright = palette['cyan_bright']['hex']  # "#8ECAE6"

# Get font families
families = font_sys.get_font_families()
chicago_stack = font_sys.get_fallback_stack('chicago')
# "'Chicago', 'Chicago FLF', -apple-system, BlinkMacSystemFont, monospace"

# Get extension-specific fonts
teletext_font = font_sys.get_font_for_extension('teletext')  # "MODE7GX3"

# Get block graphics
unicode_blocks = font_sys.get_block_graphics('unicode')
full_block = unicode_blocks['full_block']  # "█"
```

### SettingsManager Integration

```python
from core.uDOS_settings import SettingsManager

settings = SettingsManager()

# Access font system through settings
font_system = settings.get_font_system()

# Get current user font preference
current_font = settings.get_current_font()  # "chicago"

# Get CSS fallback stack for current font
fallback_stack = settings.get_font_fallback_stack()

# Load custom user font profile
profile = settings.load_user_font_profile('memory/user/my-profile.json')
```

### FontGraphicsHelper

```python
from core.uDOS_graphics import FontGraphicsHelper

# Get block characters
full = FontGraphicsHelper.get_block_char('full')  # "█"
top_half = FontGraphicsHelper.get_block_char('top_half')  # "▀"

# Get ANSI colors
cyan_ansi = FontGraphicsHelper.get_ansi_color('cyan', 'bright')  # "\033[96m"

# Colorize text
colored_text = FontGraphicsHelper.colorize("SUCCESS", "green", "bright")
print(colored_text)  # Prints in bright green

# Create retro banner
banner = FontGraphicsHelper.make_retro_banner("uDOS v1.0.24", width=60)
print(banner)
# ████████████████████████████████████████████████████████████
# █▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
# █           uDOS v1.0.24                                    █
# █▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█
# ████████████████████████████████████████████████████████████
```

## JavaScript API

### Character Editor Profile Management

```javascript
// Load font system configuration
async loadFontSystemConfig() {
    const response = await fetch('../../knowledge/system/font-system.json');
    this.fontSystemConfig = await response.json();
}

// Load user profile template
async loadUserProfile() {
    // Try memory/user/ first, fall back to data/templates/
    let response = await fetch('../../memory/user/font-profile-template.json');
    if (!response.ok) {
        response = await fetch('../../data/templates/font-profile-template.json');
    }
    this.userProfile = await response.json();
    this.applyUserProfile();
}

// Save customized profile
async saveUserProfile() {
    this.userProfile.metadata.modified_date = new Date().toISOString();
    const blob = new Blob([JSON.stringify(this.userProfile, null, 2)], {
        type: 'application/json'
    });
    // Download as JSON file
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `font-profile-${this.userProfile.metadata.name}.json`;
    a.click();
}
```

## Usage Workflows

### 1. Extension Developer: Use Recommended Font

```python
# In your extension initialization
from core.uDOS_settings import FontSystemManager

font_sys = FontSystemManager.get_instance()
recommended_font = font_sys.get_font_for_extension('c64-terminal')
# Returns: "PetMe64"

# Get CSS fallback stack
font_stack = font_sys.get_fallback_stack('petme')
# Returns: "'PetMe64', 'PetMe', 'Courier New', monospace"
```

```css
/* In your extension CSS */
@font-face {
    font-family: 'PetMe64';
    src: url('../fonts/petme/PetMe64.ttf');
}

.c64-terminal {
    font-family: 'PetMe64', 'PetMe', 'Courier New', monospace;
}
```

### 2. User: Create Custom Font Profile

1. **Open Character Editor**: `http://localhost:8888/extensions/core/character-editor/`

2. **Load Template**: Click "Load Profile" button
   - Loads `data/templates/font-profile-template.json`

3. **Customize Settings**:
   - Edit `metadata.name` (e.g., "My Retro Setup")
   - Change `font_settings.primary_font` (e.g., "Mallard")
   - Modify `color_scheme.custom_colors` (adjust hex values)
   - Add `character_mappings.custom_chars` (custom emoji/symbols)

4. **Save Profile**: Click "Save Profile" button
   - Downloads as `font-profile-my-retro-setup.json`
   - Move to `memory/user/` directory

5. **Apply Profile**: Update `memory/user/USER.UDT`:
   ```json
   {
       "system": {
           "font_profile": "memory/user/font-profile-my-retro-setup.json"
       }
   }
   ```

### 3. Core Developer: Add Color Support

```python
# Get Synthwave DOS colors for status messages
from core.uDOS_graphics import FontGraphicsHelper

def print_status(message, status_type='info'):
    color_map = {
        'success': ('green', 'bright'),
        'error': ('red', 'bright'),
        'warning': ('orange', 'dark'),
        'info': ('cyan', 'bright')
    }

    color, brightness = color_map.get(status_type, ('white', 'bright'))
    colored = FontGraphicsHelper.colorize(message, color, brightness)
    print(colored)

# Usage
print_status("✅ Font system loaded", "success")
print_status("⚠️ Profile not found", "warning")
print_status("❌ Invalid JSON", "error")
```

## Extension Integration Guide

### Recommended Font Mappings

| Extension | Font | Charset | Fallback Stack |
|-----------|------|---------|----------------|
| C64 Terminal | PetMe64 | PETSCII | `'PetMe64', 'PetMe', 'Courier New', monospace` |
| Teletext | MODE7GX3 | Teletext | `'MODE7GX3', 'Mallard', 'Courier New', monospace` |
| Desktop | Chicago | Unicode | `'Chicago', 'Chicago FLF', -apple-system, monospace` |
| Dashboard | Mallard | Unicode | `'Mallard', 'MODE7GX3', 'Courier New', monospace` |
| Character Editor | Monaco | Unicode | `'Monaco', 'Courier New', 'Courier', monospace` |
| Markdown | System | Unicode | `-apple-system, BlinkMacSystemFont, monospace` |

### Color Palette Usage

**Synthwave DOS VGA 16-Color Standard:**

| Color | Dark Hex | Bright Hex | ANSI Dark | ANSI Bright |
|-------|----------|------------|-----------|-------------|
| Black | `#000000` | `#5A5A5A` | `\033[30m` | `\033[90m` |
| Red | `#AA0000` | `#FF5555` | `\033[31m` | `\033[91m` |
| Green | `#00AA00` | `#55FF55` | `\033[32m` | `\033[92m` |
| Blue | `#0000AA` | `#5555FF` | `\033[34m` | `\033[94m` |
| Cyan | `#00AAAA` | `#8ECAE6` | `\033[36m` | `\033[96m` |
| Magenta | `#AA00AA` | `#FF55FF` | `\033[35m` | `\033[95m` |
| Orange | `#FF9500` | `#FFD166` | `\033[33m` | `\033[93m` |
| Gray | `#5A5A5A` | `#AAAAAA` | `\033[90m` | `\033[37m` |
| White | `#AAAAAA` | `#FFFFFF` | `\033[37m` | `\033[97m` |

**Semantic Aliases:**
- **Terminal**: `terminal-bg` (black), `terminal-fg` (cyan_bright), `terminal-cursor` (orange_bright)
- **Status**: `status-success` (green_bright), `status-error` (red_bright), `status-warning` (orange_dark), `status-info` (cyan_bright)
- **UI**: `ui-border` (gray_dark), `ui-border-active` (cyan_bright), `ui-highlight` (orange_bright), `ui-shadow` (black-50%)

## File Locations

### System Files (Version Controlled)
- `knowledge/system/font-system.json` - Master configuration
- `knowledge/system/palette.json` - Legacy color palette (deprecated in favor of font-system.json)
- `data/templates/font-profile-template.json` - User profile template
- `extensions/core/fonts/` - Bundled retro fonts (Chicago, Mallard, PetMe, MODE7GX3)
- `extensions/core/css/synthwave-dos-colors.css` - CSS color variables

### User Files (Gitignored)
- `memory/user/font-profile-template.json` - Working copy of template
- `memory/user/font-profile-*.json` - Custom user profiles
- `memory/user/USER.UDT` - User settings (includes `font_profile` path)

## Migration Notes

### From v1.0.23 to v1.0.24

1. **Polaroid → Synthwave DOS**: All references to "Polaroid" color system renamed to "Synthwave DOS"

2. **Font Path Changes**: Fonts moved from `extensions/fonts/` to `extensions/core/fonts/`
   - Update any custom CSS: `url('../fonts/...')` → `url('../fonts/...')` (relative to extension root)
   - Update Python imports if accessing fonts directly

3. **Monaspace Removed**: Monaspace fonts archived, no longer bundled
   - If using Monaspace, install separately or use fallback stacks

4. **New Settings Keys**: `system.font_family` and `system.font_profile` added to USER.UDT
   - Default font is "chicago"
   - Custom profiles are optional

## Testing

### Verify Font System Integration

```bash
# Run Python interactive
python3

# Test font system loading
>>> from core.uDOS_settings import FontSystemManager
>>> font_sys = FontSystemManager.get_instance()
>>> palette = font_sys.get_color_palette()
>>> print(palette['cyan_bright']['hex'])
#8ECAE6
>>>
>>> chicago = font_sys.get_fallback_stack('chicago')
>>> print(chicago)
'Chicago', 'Chicago FLF', -apple-system, BlinkMacSystemFont, monospace
>>>
>>> teletext_font = font_sys.get_font_for_extension('teletext')
>>> print(teletext_font)
MODE7GX3
```

### Test Character Editor Profile Management

1. Open: `http://localhost:8888/extensions/core/character-editor/`
2. Click "Load Profile" - should load template
3. Verify console: `✅ Loaded font system configuration`
4. Check profile loaded: inspect `window.fontManagerApp.userProfile`
5. Click "Save Profile" - should download JSON file
6. Verify downloaded file has correct structure and metadata

## Troubleshooting

### Font System Not Loading

**Error:** `⚠️ Font system config not found`

**Solution:** Verify `knowledge/system/font-system.json` exists. Reinstall from git:
```bash
git checkout knowledge/system/font-system.json
```

### Profile Template Missing

**Error:** `Font profile not found. Please ensure template exists in data/templates/`

**Solution:** Create template from git:
```bash
git checkout data/templates/font-profile-template.json
```

### CSS Variables Not Applied

**Error:** Colors not displaying correctly in extensions

**Solution:** Ensure `synthwave-dos-colors.css` is imported:
```css
@import url('../css/synthwave-dos-colors.css');
```

### Font Fallback Issues

**Error:** Fonts not rendering, showing default serif/sans-serif

**Solution:** Verify font files exist in `extensions/core/fonts/` and `@font-face` declarations are correct:
```css
@font-face {
    font-family: 'Chicago';
    src: url('../fonts/chicago/ChicagoFLF.ttf') format('truetype');
    font-display: swap;
}
```

## References

- **Style Guide**: `wiki/Style-Guide.md` (Typography & Color Palette sections)
- **Theme System**: `wiki/Theme-System.md`
- **FAQ**: `wiki/FAQ.md` (Font and color questions)
- **Font Licensing**: `extensions/core/fonts/LICENSE_ASSESSMENT.md`
- **Character Editor Docs**: `extensions/core/character-editor/docs/`

## Support

For issues or questions:
1. Check `wiki/FAQ.md` for common questions
2. Review `wiki/Style-Guide.md` for usage examples
3. See `extensions/core/docs/` for extension-specific documentation
4. Consult `knowledge/system/font-system.json` for configuration details

---

**Last Updated:** 2024
**Version:** 1.0.24
**Status:** Active ✅
