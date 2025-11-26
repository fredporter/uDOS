# Desktop Extension Structure

**Version**: 1.0.24
**Type**: Self-contained extension with shared pattern support
**Port**: 8887

## Directory Structure

```
desktop/
├── index.html              # Main HTML interface
├── desktop.css             # All styles (self-contained)
├── static/
│   └── desktop.js          # All JavaScript logic
├── fonts/                  # Local font symlinks
│   ├── ChicagoFLF.woff     → ../../../assets/fonts/ChicagoFLF.woff
│   ├── ChicagoFLF.woff2    → ../../../assets/fonts/ChicagoFLF.woff2
│   ├── Roboto-Regular.ttf  → ../../../assets/fonts/roboto/Roboto-Regular.ttf
│   ├── Roboto-Bold.ttf     → ../../../assets/fonts/roboto/Roboto-Bold.ttf
│   └── Roboto-Italic.ttf   → ../../../assets/fonts/roboto/Roboto-Italic.ttf
├── icons/                  # All icons (local copies)
│   ├── apple.svg           # System.css icons
│   ├── button.svg
│   ├── button-default.svg
│   ├── checkmark.svg
│   ├── radio-*.svg
│   ├── scrollbar-*.svg
│   ├── select-button.svg
│   ├── cil-terminal.svg    # CoreUI app icons (local copies)
│   ├── cil-book.svg
│   ├── cil-tv.svg
│   ├── cil-text.svg
│   ├── cil-apps.svg
│   └── cil-folder.svg
└── docs/                   # Documentation files
```

## Shared Assets Integration

### Patterns CSS (Linked)
- **Source**: `/extensions/assets/css/classic-patterns.css`
- **Purpose**: Classic Mac desktop patterns
- **Usage**: Background pattern selector
- **Reference**: `<link rel="stylesheet" href="../../assets/css/classic-patterns.css">`

### Available Patterns
1. Checkerboard (Default) - Classic Mac grid
2. Fine Dots - Small dot pattern
3. Grid Small - 10px grid
4. Grid Medium - 20px grid
5. Diagonal Lines - 45° stripes
6. Crosshatch - Perpendicular lines
7. Dense Dots - Tight dot pattern
8. Sparse Dots - Wide dot pattern
9. Solid Light - #c0c0c0
10. Solid Black - #000000## Font Strategy

### Chicago (Menus, Titles, Filenames)
- **Usage**: Menu bar, window titles, desktop icon labels, headings
- **Source**: `/extensions/assets/fonts/ChicagoFLF.woff2`
- **Symlinked**: Yes

### Roboto (Body Text, Articles, Viewports)
- **Usage**: Window content, articles, general body text
- **Source**: `/extensions/assets/fonts/roboto/`
- **Variants**: Regular (400), Bold (700), Italic (400)
- **Symlinked**: Yes

## Icon Strategy

### All Icons Local (Self-Contained)
- **System.css UI Icons**: Buttons, scrollbars, form controls
  - Source: Copied from `/extensions/assets/icons/`
  - Location: `desktop/icons/`

- **CoreUI Application Icons**: Desktop shortcuts
  - Source: Copied from `/extensions/assets/icons/coreui/`
  - Location: `desktop/icons/cil-*.svg`

- **Referenced**: All via relative paths `icons/*.svg`
- **No external dependencies**: Fully self-contained

## New Features

### Desktop Pattern Selector
- **Icon**: Apple logo (7th desktop icon)
- **Action**: Click to open pattern selector
- **Storage**: LocalStorage saves preference
- **Patterns**: 10 classic Mac-inspired backgrounds

### Auto-Fullscreen Windows
- **Behavior**: All windows open in fullscreen mode
- **Hidden Elements**: Menu bar, about window, desktop icons
- **Restore**: Click close button to return to desktop
- **Purpose**: Clean, focused workspace for each tool

### Pattern Persistence
```javascript
// Saved to localStorage
localStorage.setItem('desktop-pattern-index', currentPatternIndex);

// Loaded on startup
loadPatternPreference();
```

## CSS Structure

```css
/* Shared patterns (linked) */
@import url('../../assets/css/classic-patterns.css');

/* Font declarations */
@font-face { font-family: Chicago; ... }
@font-face { font-family: Roboto; ... }

/* Base typography */
body {
  font-family: Roboto, sans-serif;
  background: /* pattern from selector */;
}
h1, h2, h3 { font-family: Chicago, sans-serif; }

/* Menu bar */
ul[role="menu-bar"] { font-family: Chicago, sans-serif; }

/* Window titles */
.title-bar .title { font-family: Chicago, sans-serif; }

/* Desktop icons */
.desktop-icon-label { font-family: Chicago, sans-serif; }

/* Window content */
.window-pane { font-family: Roboto, sans-serif; }

/* Fullscreen windows */
.window[data-fullscreened="true"] {
  border: none;
  margin: 0;
  width: 100vw;
  height: 100vh;
}
```

## JavaScript Structure

All JavaScript is contained in `static/desktop.js` with IIFE pattern:

```javascript
(function() {
    'use strict';

    // Private state
    const desktopIcons = [...]; // 7 icons including pattern selector
    const desktopPatterns = [...]; // 10 background patterns
    let draggedWindow = null;
    let currentPatternIndex = 0;

    // Pattern management
    function loadPatternPreference() { ... }
    function applyPattern(index) { ... }

    // Auto-fullscreen
    function autoFullscreenWindow(win) {
        // Hide menu, about, icons
        // Expand window to 100vw x 100vh
    }

    function restoreDesktop() {
        // Show menu, about, icons
    }

    // Public API exposed to window object
    window.toggleWindow = function(windowId) { ... };
    window.openExtension = function(name, port) { ... };
    window.openPatternSelector = function() { ... };
    // ... etc

})();
```## Self-Contained Principles

1. **No external CDNs** - All assets local or symlinked
2. **All icons local** - CoreUI and System.css icons copied locally
3. **Shared patterns** - Link to classic-patterns.css for backgrounds
4. **Relative paths** - CSS/JS use relative paths to local resources
5. **Clean separation** - HTML, CSS, JS in separate files
6. **Font strategy** - Chicago for UI, Roboto for content
7. **Auto-fullscreen** - Windows open fullscreen, hide desktop
8. **Pattern persistence** - Background choice saved in LocalStorage

## Comparison with Other Extensions

| Extension  | CSS          | JS            | Fonts        | Icons        | Patterns | Fullscreen |
|-----------|--------------|---------------|--------------|--------------|----------|------------|
| Terminal  | terminal.css | terminal.js   | PetMe64      | Local copies | No       | No         |
| Teletext  | teletext-*.css | teletext-*.js | Mallard (6)  | N/A          | No       | No         |
| Dashboard | dashboard-*.css | dashboard-*.js | PressStart2P | N/A          | No       | No         |
| **Desktop** | **desktop.css** | **desktop.js** | **Chicago + Roboto** | **All local** | **Yes** | **Yes** |

## Running the Extension

```bash
# Start server
cd /Users/fredbook/Code/uDOS/extensions/core/desktop
python3 -m http.server 8887

# Access
http://localhost:8887
```

## Development Notes

- **All icons are local copies** - Both system UI and application icons
- **Pattern selector** - 7th desktop icon (Apple logo)
- **Auto-fullscreen behavior** - Windows hide desktop until closed
- **Pattern persistence** - Uses LocalStorage for user preference
- **Chicago provides authentic Mac System 6 aesthetic** for UI chrome
- **Roboto provides modern, readable body text** for content
- **All window content** uses Roboto for better readability
- **Menu bar, titles, and filenames** use Chicago for retro aesthetic
- **Shared patterns CSS** linked for classic Mac backgrounds

## Credits

- **system.css**: Sakun Acharige (@sakofchit) - MIT License
- **Chicago Font**: Recreated by @blogmywiki
- **Roboto Font**: Google Fonts - Apache License 2.0
- **CoreUI Icons**: CoreUI Team - MIT License
