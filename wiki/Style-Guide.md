# uDOS v1.0.0 Style Guide

This document outlines the design and style conventions for uDOS v1.0.0, ensuring a consistent and intuitive user experience across CLI, web interfaces, maps, and data formats. The core principle is a "human-readable," minimal-touch interface with authentic retro computing aesthetics.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Retro CSS Frameworks](#2-retro-css-frameworks)
3. [Command and uCODE Syntax](#3-command-and-ucode-syntax)
4. [UI and Interaction](#4-ui-and-interaction)
5. [File Naming and Structure](#5-file-naming-and-structure)
6. [Theming System](#6-theming-lexiconudo)
7. [Typography and Fonts](#7-typography-and-fonts)
8. [Color Palette and Viewport](#8-color-palette--viewport-visualization)
9. [Web Viewport Grid Styles](#9-web-viewport-grid-styles)
10. [Map Tile Coordinate System](#10-map-tile-coordinate-system)
11. [Date, Time, and Location Formats](#11-date-time-and-location-formats)
12. [Command Reference](#12-command-reference)

---

## 1. Core Principles

- **Clarity over cleverness**: The system should be easy to understand and learn. All commands and outputs prioritize readability.
- **Minimalism**: Reduce unnecessary keystrokes and visual noise. Prompts and commands are concise.
- **Thematic Consistency**: The "8-bit retro" or "dungeon master" theme, defined in `LEXICON.UDO`, is applied consistently to system terminology.
- **Authentic Retro Aesthetics**: Web extensions use period-accurate CSS frameworks to recreate vintage computing experiences from the 1980s and 1990s.

---

## 2. Retro CSS Frameworks

uDOS v1.0.0 integrates multiple retro-themed CSS frameworks to create authentic vintage computing experiences across all web extensions. Each framework is carefully chosen to match the extension's purpose and aesthetic.

### Framework Implementation Matrix

| Extension | CSS Framework | Theme | Era |
|-----------|---------------|-------|-----|
| Font Editor | system.css | Mac System 6 | 1984-1991 |
| Markdown Viewer | system.css | Mac System 6 | 1984-1991 |
| Terminal | NES.css | 8-bit Gaming | 1983-1990 |
| Dashboard | classic.css + After Dark CSS | Mac OS 8.1 + Screensavers | 1989-1997 |

### system.css - Mac System 6 Aesthetic

**Used in:** Font Editor, Markdown Viewer
**Repository:** https://github.com/sakofchit/system.css
**Style:** Apple System 6 monochrome interface (1984-1991)

Features:
- Pure black & white design
- Pixel-perfect window components (`.window`, `.title-bar`)
- Authentic bitmap scrollbars
- Classic Mac fonts: Chicago_12, Monaco, Geneva_9
- Menu bars and dropdowns
- No JavaScript dependencies

**Example Components:**
```html
<div class="window">
  <div class="title-bar">
    <button aria-label="Close"></button>
    <h1 class="title">Font Editor</h1>
    <button aria-label="Resize"></button>
  </div>
  <div class="separator"></div>
  <div class="window-pane">
    <!-- Content here -->
  </div>
</div>
```

### NES.css - 8-bit Gaming Aesthetic

**Used in:** Terminal
**Repository:** https://github.com/nostalgic-css/NES.css
**Style:** Nintendo Entertainment System retro gaming (1983-1990)

Features:
- Pixelated borders and containers
- 8-bit color palette
- Press Start 2P font
- Gaming-style badges and buttons
- Dark and light theme variants
- Retro progress bars

**Example Components:**
```html
<div class="nes-container is-dark with-title">
  <p class="title">Terminal Output</p>
  <!-- Output content -->
</div>
<input type="text" class="nes-input is-dark">
<button class="nes-btn is-primary">Execute</button>
<span class="nes-badge is-success">v1.0.0</span>
```

### classic.css - Mac OS 8.1 Interface

**Used in:** Dashboard
**Repository:** https://github.com/npjg/classic.css
**Style:** Apple Mac OS 8.1 (System 7.1.1) interface

Features:
- Classic window chrome with beveled edges
- Authentic button shadows (multi-layer CSS)
- System 7.1.1 background patterns
- ChicagoFLF typography
- Hover and focus states
- Classic scrollbars

### After Dark CSS - Screensaver Effects

**Used in:** Dashboard (screensaver mode)
**Repository:** https://github.com/bryanbraun/after-dark-css
**Style:** Berkeley Systems After Dark™ screensavers (1989)

Features:
- Flying Toasters animation
- Starfield effects
- Pure CSS animations (no JavaScript)
- Multiple screensaver modes
- Authentic 1989 aesthetics

### Design Guidelines

When creating or modifying web extensions:

1. **Choose the appropriate framework** based on the extension's purpose
2. **Include framework CDN** in the `<head>` section
3. **Use framework components** instead of custom HTML
4. **Add minimal custom styles** only when necessary
5. **Test across browsers** (especially scrollbar compatibility)
6. **Document customizations** in component README

### Font Loading Best Practices

All frameworks rely on custom fonts:
- Load fonts before rendering content
- Specify fallback fonts (e.g., `monospace`, `sans-serif`)
- Use `font-display: swap` for better performance
- Test with slow network conditions

### Browser Compatibility

- **system.css:** Modern browsers; custom scrollbars in Chromium only
- **NES.css:** IE11+ and all modern browsers
- **classic.css:** Modern browsers with flexbox support
- **After Dark CSS:** Requires CSS3 animations

### Attribution

All CSS frameworks are used under MIT/OFL licenses. See `/docs/CSS-FRAMEWORK-ATTRIBUTION.md` for complete attribution, licensing, and acknowledgements.

**Framework Creators:**
- **system.css** by [@sakofchit](https://github.com/sakofchit)
- **NES.css** by [Black Everyday Company](https://kuroeveryday.blogspot.com/)
- **classic.css** by [@npjg](https://github.com/npjg)
- **After Dark CSS** by [@bryanbraun](https://github.com/bryanbraun)

### Quick References

- `/extensions/web/shared/SYSTEM-CSS-REFERENCE.md` - system.css component guide
- `/docs/SYSTEM-CSS-INTEGRATION.md` - Integration guide for Font Editor/Markdown Viewer
- `/docs/CSS-FRAMEWORK-ATTRIBUTION.md` - Complete attribution and licensing

---

## 3. Command and `uCODE` Syntax

uDOS uses a hybrid system: a friendly user-facing command set and a structured internal language called `uCODE`.

### User Command Syntax

User-facing commands are simple, memorable, and case-insensitive. They follow a `COMMAND [ARGUMENT] [OPTION]` pattern.

- **Commands**: Always single, uppercase words (e.g., `CATALOG`, `LOAD`, `ASK`).
- **Arguments**: Typically quoted strings for paths or text (e.g., `"my_file.txt"`).
- **Options**: Use prepositions for clarity (e.g., `TO "panel_2"`).

**Example:**
```
> load "README.MD" to "docs"
```

### Internal `uCODE` Syntax

`uCODE` is the structured language the parser generates. It is **always** uppercase and follows a strict format for internal processing.

- **Format**: `[MODULE|COMMAND*PARAMETER_1*PARAMETER_2]`
- **`MODULE`**: The core system responsible (eg., `FILE`, `GRID`, `AI`).
- **`COMMAND`**: The specific action to perform (e.g., `LOAD`, `LIST`, `ASK`).
- **`PARAMETERS`**: Star-separated values passed to the command handler.

**Example Translation:**
- User: `load "README.MD" to "docs"`
- `uCODE`: `[FILE|LOAD*README.MD*docs]`

---

## 4. UI and Interaction

### Emoji Prompts

The system prompt uses emojis to indicate the current context or expected input, providing a "smart" minimal-touch experience.

| Emoji | Prompt | Context |
| :--- | :--- | :--- |
| `🟢` | `🟢 >` | **Ready**: System is idle and awaiting a standard command. |
| `📝` | `📝 >` | **Text Input**: System is in multi-line input mode (e.g., for saving a new file). |
| `🤖` | `🤖 >` | **AI Interaction**: System is awaiting a prompt for the `ASK` command. |
| `⏳` | | **Busy**: A spinner or hourglass emoji indicates a background process is running. |
| `🔴` | `🔴 >` | **Error**: Indicates the previous command resulted in an error. |

### System Output

- **Success**: `✅ SUCCESS: File loaded into 'main'.`
- **Error**: `❌ ERROR: File not found at 'path/to/file'.`
- **Information**: `ℹ️ INFO: 3 files found.`
- **AI Response**: The AI's output is presented cleanly, without a prefix.

---

## 5. File Naming and Structure

The "cleverly flat" architecture keeps the core logic accessible.

- **Core Modules**: `uDOS_*.py` (e.g., `uDOS_main.py`, `uDOS_parser.py`). All lowercase with underscores.
- **Configuration**: `.UDO` files in the `/data` directory (e.g., `COMMANDS.UDO`, `LEXICON.UDO`). All uppercase.
- **Documentation**: `.MD` files. All uppercase (e.g., `README.MD`, `ROADMAP.MD`).
- **Legacy Code**: All v1.0 files are moved to the `/legacy` directory.

---

## 6. Theming (`LEXICON.UDO`)

The `LEXICON.UDO` file in the `/data` directory defines the thematic "skin" of the interface. It allows users to swap out the default command names and system messages for a custom theme (e.g., "Dungeon Master").

- The parser will use the lexicon to map themed commands (e.g., `ZAP`) back to their standard equivalents (`LOAD`) before generating `uCODE`.
- All system output messages should be defined in the lexicon to support theming.

---

## 6. Typography and Fonts

### Monaspace Font System

uDOS uses the **Monaspace** font superfamily for web-based interfaces (typo editor, cmd.js terminal, browser views). Monaspace provides five distinct variants optimized for coding, developed by GitHub Next.

**Official Site:** [monaspace.githubnext.com](https://monaspace.githubnext.com)

**Font Variants:**

| Variant | Style | Description | Use Case |
|---------|-------|-------------|----------|
| **Neon** | Neo-grotesque sans | Clean and modern | Default, general editing |
| **Argon** | Humanist sans | Warm and readable | Long-form documentation |
| **Xenon** | Slab serif | Editorial and strong | Headers, emphasis |
| **Radon** | Handwriting | Casual and personal | Comments, notes |
| **Krypton** | Mechanical sans | Technical and precise | Code, data tables |

**Font Features:**
- **Texture Healing™**: Advanced character spacing for improved readability
- **Coding Ligatures**: Enhanced symbol combinations (→, ===, !=, etc.)
- **Powerline Symbols**: Terminal integration glyphs
- **Variable Font Technology**: Flexible weight and width control

**Web Typography System:**

```css
/* Font Families */
--font-neon: 'Monaspace Neon', 'Courier New', Consolas, Monaco, monospace;
--font-argon: 'Monaspace Argon', 'Courier New', Consolas, Monaco, monospace;
--font-xenon: 'Monaspace Xenon', 'Courier New', Consolas, Monaco, monospace;
--font-radon: 'Monaspace Radon', 'Courier New', Consolas, Monaco, monospace;
--font-krypton: 'Monaspace Krypton', 'Courier New', Consolas, Monaco, monospace;

/* Serif headings for readability */
--font-serif: 'Georgia', 'Times New Roman', Times, serif;

/* Sans-serif for UI elements */
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;

/* Font Sizes - Larger and more readable */
--font-size-xs: 12px;   /* Metadata, footnotes */
--font-size-sm: 14px;   /* Secondary text */
--font-size-md: 16px;   /* Body text (default) */
--font-size-lg: 20px;   /* Subheadings */
--font-size-xl: 28px;   /* Headings */
--font-size-xxl: 36px;  /* Page titles */

/* Line Heights - Generous spacing */
--line-height-tight: 1.3;   /* Headers */
--line-height-normal: 1.6;  /* Body text */
--line-height-loose: 1.8;   /* Code blocks */
```

**Button Styling:**

Large, flat buttons with clear affordances:

```css
/* Primary action buttons */
.btn-primary {
  font-size: 16px;
  padding: 1rem 2rem;
  min-height: 48px;
  border-radius: 6px;
  font-weight: 600;
  background: var(--gh-accent-fg);
  color: white;
  border: 2px solid var(--gh-accent-emphasis);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

/* Button variants: .btn-success, .btn-danger, .btn-warning */
/* Button sizes: .btn-sm (36px), .btn-lg (56px) */
```

**Heading Styles:**

Serif fonts for better readability and hierarchy:

```css
h1, h2, h3 {
  font-family: var(--font-serif);
  font-weight: 700;
  line-height: 1.3;
  color: var(--gh-fg-default);
}

h1 {
  font-size: 36px;
  border-bottom: 2px solid var(--gh-border-default);
  padding-bottom: 0.75rem;
  margin-bottom: 2rem;
}

h2 {
  font-size: 28px;
  margin-top: 3rem;
}

h3 {
  font-size: 20px;
  margin-top: 2rem;
}
```

**Configuration:**
```json
{
  "DEFAULT_VARIANT": "NEON",
  "FONT_SIZE": "16px",
  "LINE_HEIGHT": "1.6",
  "HEADING_FONT": "serif",
  "BODY_FONT": "sans-serif",
  "CODE_FONT": "monaspace-neon",
  "FEATURES": {
    "TEXTURE_HEALING": true,
    "LIGATURES": true,
    "POWERLINE": true,
    "VARIABLE_FONT": true
  }
}
```

**Fallback Stack:**
```css
/* Code blocks - Monaspace preferred */
font-family: "Monaspace Neon", monospace, Consolas, Monaco, "Courier New";

/* Headings - Serif */
font-family: Georgia, "Times New Roman", Times, serif;

/* Body text - System sans */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
```

**Installation:**
- **Web fonts**: Installed via `bash extensions/setup_monaspace.sh`
- **Format**: WOFF2 (web), OTF (system)
- **Location**: `extensions/fonts/monaspace/`

**CLI Terminal Use:**
- macOS: Install via Font Book or system preferences
- Linux: Copy OTF files to `~/.local/share/fonts/`
- Windows: Install OTF files to `C:\Windows\Fonts\`

**Commands:**
```
FONT LIST              # View all variants
FONT SET ARGON         # Switch to Argon variant
FONT INFO              # Current configuration
```

---

## 7. Color Palette & Viewport Visualization

### Polaroid Color System

uDOS v1.0.0 uses the **Polaroid** color palette as its default system theme. This palette is inspired by high-contrast instant photography and optimized for terminal visibility.

**Primary Color Reference:**

| Color | Name | tput | Hex | RGB | Usage |
|:------|:-----|:----:|:---:|:---:|:------|
| 🔴 | Polaroid Red | 196 | #FF1744 | 255,23,68 | Errors, alerts, critical warnings, danger zones |
| 🟢 | Polaroid Green | 46 | #00E676 | 0,230,118 | Success, confirmations, growth, positive status |
| 🟡 | Polaroid Yellow | 226 | #FFEB3B | 255,235,59 | Warnings, caution, highlights, notifications |
| 🔵 | Polaroid Blue | 21 | #2196F3 | 33,150,243 | Information, links, system messages, cold tones |
| 🟣 | Polaroid Purple | 201 | #E91E63 | 233,30,99 | Magic, spells, special events, fantasy elements |
| 🔷 | Polaroid Cyan | 51 | #00E5FF | 0,229,255 | Technology, data, navigation, cool highlights |
| ⚪ | Pure White | 15 | #FFFFFF | 255,255,255 | Default text, headings, high emphasis |
| ⚫ | Pure Black | 16 | #000000 | 0,0,0 | Background (light themes), dark accents |

**Grayscale Gradient:**

| Level | tput | Hex | RGB | Usage |
|:------|:----:|:---:|:---:|:------|
| Gray 0 | 232 | #080808 | 8,8,8 | Darkest - borders, shadows |
| Gray 1 | 236 | #303030 | 48,48,48 | Dark - inactive elements |
| Gray 2 | 240 | #585858 | 88,88,88 | Medium-dark - separators |
| Gray 3 | 244 | #808080 | 128,128,128 | Medium - walls, neutral |
| Gray 4 | 248 | #A8A8A8 | 168,168,168 | Light - subtle text |
| Gray 5 | 252 | #D0D0D0 | 208,208,208 | Lightest - highlights |

**Shading Blocks:**

Unicode characters for visual effects:
- `█` Full block (100%) - U+2588
- `▓` Dark shade (75%) - U+2593
- `▒` Medium shade (50%) - U+2592
- `░` Light shade (25%) - U+2591

ASCII fallbacks for limited terminals:
- `#` Full (100%)
- `@` Dark (75%)
- `+` Medium (50%)
- `.` Light (25%)

**Box Drawing Characters:**

For borders and grid layouts:
```
┌─┬─┐  ╔═╦═╗  ┏━┳━┓
│ │ │  ║ ║ ║  ┃ ┃ ┃
├─┼─┤  ╠═╬═╣  ┣━╋━┫
│ │ │  ║ ║ ║  ┃ ┃ ┃
└─┴─┘  ╚═╩═╝  ┗━┻━┛
```

### Viewport Testing and Capabilities

**Terminal Detection:**
- **Dimensions**: Automatically detected (e.g., 80×24, 120×40)
- **Unicode Support**: Tests rendering of special characters
- **Color Depth**: Detects 256-color, 16-color, or monochrome
- **Font Type**: Verifies monospace font rendering

**ViewportVisualizer System:**

Features implemented in `core/uDOS_viewport_viz.py`:
- Color palette visual display
- Grayscale gradient test
- Shading blocks demonstration
- ASCII art logo rendering
- Dimension and boundary testing
- Font spacing verification
- Capability detection and reporting

**Commands:**
```
PALETTE                # Display full color palette
REBOOT                 # Includes viewport splash screen
VIEWPORT               # Show current viewport specs
```

### Accessibility

- ✅ **Colorblind Safe**: Tested for protanopia and deuteranopia
- ✅ **High Contrast**: Optimized for visibility on light/dark terminals
- ✅ **Monochrome Fallback**: Works on non-color terminals
- ✅ **Pattern Distinction**: Does not rely solely on color for critical information
- ✅ **ANSI Support**: Compatible with standard terminal escape sequences

### Theme Mappings

**Dungeon Master (NetHack-inspired):**
- Player: White (15)
- Enemy: Red (196)
- Treasure: Yellow (226)
- Magic: Purple (201)
- Exit: Green (46)
- Water: Cyan (51)
- Wall: Gray 3 (244)
- Floor: Gray 1 (236)

**Cyberpunk (Neon aesthetic):**
- System: Cyan (51)
- Warning: Yellow (226)
- Error: Red (196)
- Success: Green (46)
- Data: Blue (21)
- Special: Purple (201)
- Background: Black (16)
- Text: White (15)

**Terminal Classic (Retro):**
- Primary: Green (46)
- Background: Black (16)
- Highlight: Cyan (51)
- Status: Yellow (226)

---

## 8. Web Viewport Grid Styles

### Grid Layout System

For web-based interfaces (typo editor, cmd.js terminal, future web views), uDOS uses a responsive grid system based on character cells.

**Base Grid Specifications:**

```css
.viewport-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(1ch, 1fr));
  grid-template-rows: repeat(auto-fit, minmax(1.5em, 1fr));
  font-family: "Monaspace Neon", monospace;
  font-size: 14px;
  line-height: 1.5;
  gap: 0;
  padding: 0;
}
```

**Cell Addressing:**

Cells use alphanumeric coordinates: `[Column][Row]`
- Columns: A-Z, AA-AZ, BA-BZ, etc. (base-26)
- Rows: 00-99 (zero-padded decimal)
- Example: `A01`, `Z25`, `AA00`, `BZ99`

**Standard Viewport Sizes:**

| Name | Columns | Rows | Total Cells | Use Case |
|------|---------|------|-------------|----------|
| Compact | 40 | 20 | 800 | Mobile, small terminals |
| Standard | 80 | 24 | 1,920 | Classic terminal, default |
| Wide | 120 | 40 | 4,800 | Modern displays, split views |
| Ultra | 160 | 60 | 9,600 | Large monitors, grid editing |

**Responsive Breakpoints:**

```css
/* Compact: Mobile and small screens */
@media (max-width: 640px) {
  .viewport-grid {
    grid-template-columns: repeat(40, 1ch);
    grid-template-rows: repeat(20, 1.5em);
  }
}

/* Standard: Tablets and medium screens */
@media (min-width: 641px) and (max-width: 1024px) {
  .viewport-grid {
    grid-template-columns: repeat(80, 1ch);
    grid-template-rows: repeat(24, 1.5em);
  }
}

/* Wide: Desktop screens */
@media (min-width: 1025px) and (max-width: 1920px) {
  .viewport-grid {
    grid-template-columns: repeat(120, 1ch);
    grid-template-rows: repeat(40, 1.5em);
  }
}

/* Ultra: Large displays */
@media (min-width: 1921px) {
  .viewport-grid {
    grid-template-columns: repeat(160, 1ch);
    grid-template-rows: repeat(60, 1.5em);
  }
}
```

**Color Classes:**

Apply Polaroid palette colors via CSS classes:

```css
.color-red { color: #FF1744; }
.color-green { color: #00E676; }
.color-yellow { color: #FFEB3B; }
.color-blue { color: #2196F3; }
.color-purple { color: #E91E63; }
.color-cyan { color: #00E5FF; }
.color-white { color: #FFFFFF; }
.color-black { color: #000000; }

.bg-red { background-color: #FF1744; }
.bg-green { background-color: #00E676; }
/* ... etc ... */

.shade-100 { opacity: 1.0; }    /* █ Full */
.shade-75 { opacity: 0.75; }   /* ▓ Dark */
.shade-50 { opacity: 0.5; }    /* ▒ Medium */
.shade-25 { opacity: 0.25; }   /* ░ Light */
```

**Grid Panel Layers:**

For advanced map and overlay systems:

```css
.viewport-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.layer-background {
  z-index: 1;  /* Terrain, floor tiles */
}

.layer-midground {
  z-index: 10; /* Objects, items, NPCs */
}

.layer-foreground {
  z-index: 20; /* Player, UI overlays */
}

.layer-ui {
  z-index: 100; /* HUD, menus, tooltips */
}
```

---

## 9. Map Tile Coordinate System

### Alphanumeric Coordinate Format

uDOS uses a hierarchical coordinate system that encodes both local grid position and global world coordinates.

**Format:** `[LEVEL]-[LAT]-[LONG]-[LOCAL]`

**Components:**

1. **LEVEL**: Vertical layer (-99 to +99)
   - `00`: Default ground level (sea level equivalent)
   - `+01` to `+99`: Above ground (floors, sky, space)
   - `-01` to `-99`: Below ground (basement, caves, depths)

2. **LAT**: Latitude sector (AA-ZZ, base-26)
   - AA = Northernmost (-90°)
   - MZ = Equator (0°)
   - ZZ = Southernmost (+90°)
   - Each letter increment ≈ 3.46° latitude

3. **LONG**: Longitude sector (AA-ZZ, base-26)
   - AA = -180° (International Date Line)
   - MZ = 0° (Prime Meridian)
   - ZZ = +180° (International Date Line)
   - Each letter increment ≈ 6.92° longitude

4. **LOCAL**: Local tile within sector (00-99)
   - 2-digit base-10 for fine positioning
   - 00-99 provides 100×100 grid per sector

**Examples:**

```
00-MZ-MZ-50    # Ground level, Prime Meridian & Equator, center tile
+05-NA-PB-23   # 5th floor, northern hemisphere, tile 23
-12-SA-AA-00   # 12 levels underground, southern/western, corner tile
+50-AA-ZZ-99   # 50 levels up, north pole area, edge tile
```

**Coordinate Translation:**

Base-26 to Degrees (Latitude):
```
Degrees = ((Letter1 * 26 + Letter2) / 676) * 180 - 90
Example: MZ = ((12 * 26 + 25) / 676) * 180 - 90 ≈ 0°
```

Base-26 to Degrees (Longitude):
```
Degrees = ((Letter1 * 26 + Letter2) / 676) * 360 - 180
Example: MZ = ((12 * 26 + 25) / 676) * 360 - 180 ≈ 0°
```

**Tile Resolution:**

Each sector (LAT-LONG pair) represents approximately:
- Latitude span: ~3.46° × ~6.92° ≈ 24 sq. degrees
- With 100×100 local tiles: ~0.0346° × ~0.0692° per tile
- At equator: ~3.8 km × ~7.7 km per tile

**Compact Format:**

For space-constrained displays: `L:LAT-LONG-LOC`
```
0:MZ-MZ-50     # Ground level
+5:NA-PB-23    # 5th floor
-12:SA-AA-00   # 12 underground
```

**Sortable Format:**

For database/file storage (lexicographic sorting):
```
[LEVEL_3][LAT_2][LONG_2][LOCAL_2]
  ↓        ↓      ↓        ↓
+05      NA     PB       23
```
Stored as: `+05NAPB23` (9 characters, zero-padded, sortable)

**Map Data Structure:**

```json
{
  "tile": {
    "coord": "00-MZ-MZ-50",
    "level": 0,
    "lat": "MZ",
    "long": "MZ",
    "local": 50,
    "real_lat": 0.0,
    "real_long": 0.0,
    "type": "floor",
    "char": ".",
    "color": "gray_1",
    "walkable": true
  }
}
```

---

## 10. Date, Time, and Location Formats

### Timestamp Format

uDOS uses **ISO 8601** extended format with timezone and optional map coordinates for complete spatiotemporal referencing.

**Standard Format:**
```
YYYY-MM-DDTHH:MM:SS.sss±HH:MM[@COORD]
```

**Components:**

- `YYYY-MM-DD`: Date (zero-padded)
- `T`: Separator (literal)
- `HH:MM:SS.sss`: Time with milliseconds
- `±HH:MM`: Timezone offset from UTC
- `@COORD`: Optional map coordinate suffix

**Examples:**

**Basic Timestamp:**
```
2025-10-31T14:32:45.123-07:00
```
- Date: October 31, 2025
- Time: 2:32:45.123 PM
- Timezone: UTC-7 (Pacific Daylight Time)

**With Map Location:**
```
2025-10-31T14:32:45.123-07:00@00-MZ-MZ-50
```
- Timestamp: October 31, 2025, 2:32 PM PDT
- Location: Ground level, equator/prime meridian, tile 50

**Underground Event:**
```
2025-11-15T09:15:30.000+00:00@-05-NA-PB-12
```
- Timestamp: November 15, 2025, 9:15 AM UTC
- Location: 5 levels underground, northern sector, tile 12

**Compact Display Format:**

For UI/logs where space is limited:
```
2025-10-31 14:32:45 -07@00-MZ-MZ-50
```
Removes milliseconds and colons in timezone.

**Readable Format:**

For human-friendly display:
```
Oct 31, 2025 at 2:32 PM PDT (00-MZ-MZ-50)
```

**Sortable Filename Format:**

For log files and data storage:
```
20251031_143245_UTC-07_00-MZ-MZ-50.log
```
- Lexicographically sortable
- Filesystem-safe (no colons)
- Includes all spatiotemporal data

**Timezone Codes:**

Support both offset and IANA zone names:
```
2025-10-31T14:32:45-07:00           # UTC offset
2025-10-31T14:32:45[America/Los_Angeles]  # IANA timezone
```

**Relative Timestamps:**

For recent events:
```
just now
2 minutes ago
1 hour ago
yesterday at 2:32 PM
Oct 30 at 9:15 AM
```

**Duration Format:**

For time spans:
```
HH:MM:SS       # 01:23:45 (1 hour, 23 min, 45 sec)
DDd HHh MMm    # 2d 5h 30m (2 days, 5 hours, 30 minutes)
```

**Location-Tagged Log Entry:**

```json
{
  "timestamp": "2025-10-31T14:32:45.123-07:00",
  "location": "00-MZ-MZ-50",
  "event": "player_moved",
  "data": {
    "from": "00-MZ-MZ-49",
    "to": "00-MZ-MZ-50",
    "direction": "east"
  }
}
```

**Command Examples:**

```
LOG "Event occurred" @00-MZ-MZ-50
# Logs with current timestamp and specified location

STATUS
# Shows: 2025-10-31 14:32:45 -07:00 @ 00-MZ-MZ-50

MAP GOTO 00-MZ-MZ-50
# Navigate to coordinate with timestamp logged
```

**Parsing Rules:**

1. Always use ISO 8601 for machine-readable data
2. Store timestamps in UTC when possible
3. Display in user's local timezone
4. Include timezone info in all exports
5. Map coordinates are optional but recommended for location-aware events
6. Use compact format for logs, full format for APIs
7. Milliseconds optional (default to .000)

---

## 11. Command Reference

### Color and Display Commands

View the complete palette system:
```
> PALETTE
```

Test viewport rendering during system reboot:
```
> REBOOT
```

Display current viewport specifications:
```
> VIEWPORT
```

### Font Management Commands

List available font variants:
```
> FONT LIST
```

Switch to a different font variant:
```
> FONT SET ARGON
> FONT SET NEON
```

Show current font configuration:
```
> FONT INFO
```

### Map Coordinate Commands

Navigate to specific coordinates:
```
> MAP GOTO 00-MZ-MZ-50
```

Show current location:
```
> MAP WHERE
```

Set spawn point:
```
> MAP SPAWN 00-MZ-MZ-25
```

### Timestamp and Logging

Log event with location:
```
> LOG "Player found treasure" @00-NA-PB-42
```

Show current time and location:
```
> STATUS
```

Export log with timestamps:
```
> EXPORT LOG sandbox/session_20251031.log
```

---

## 12. Implementation Notes

### File Locations

**Configuration Files:**
- Color palette: `data/PALETTE.UDO`
- Font settings: `data/FONTS.UDO`
- Map data: `data/MAP.UDO`
- User preferences: `data/USER.UDT`

**Web Assets:**
- Fonts: `extensions/fonts/monaspace/`
- CSS stylesheets: `extensions/web/styles/`
- Grid templates: `extensions/web/templates/`

**Python Modules:**
- Viewport system: `core/uDOS_viewport_viz.py`
- Map engine: `core/uDOS_map.py`
- Color utilities: `core/uDOS_colors.py`

### Browser Compatibility

**Supported Browsers:**
- ✅ Chrome/Edge 90+ (Chromium-based)
- ✅ Firefox 88+
- ✅ Safari 14+
- ⚠️ Mobile browsers (limited grid support)

**Required Features:**
- CSS Grid Layout
- CSS Custom Properties (variables)
- @font-face with WOFF2
- Unicode character support
- 256-color palette support

### Performance Considerations

**Grid Rendering:**
- Recommended maximum: 120×40 cells (4,800 total)
- Use virtualization for larger grids
- Limit animation to 60fps
- Lazy-load off-screen content

**Font Loading:**
- Preload default variant (Neon)
- Load additional variants on demand
- Use `font-display: swap` for FOUT mitigation
- Fallback to system monospace immediately

**Color Performance:**
- Use CSS classes instead of inline styles
- Batch DOM updates
- Avoid excessive repaints
- Use `will-change` sparingly

---

## 13. Examples and Best Practices

### Creating a Styled Web Panel

```html
<div class="viewport-grid standard">
  <div class="cell color-green bg-black" data-coord="A00">@</div>
  <div class="cell color-gray-3 bg-black" data-coord="A01">.</div>
  <div class="cell color-yellow bg-black" data-coord="A02">$</div>
  <!-- ... more cells ... -->
</div>
```

### Map Data with Timestamp

```json
{
  "event": "treasure_found",
  "timestamp": "2025-10-31T14:32:45.123-07:00",
  "location": "00-NA-PB-42",
  "player": "fredbook",
  "item": "golden_key",
  "metadata": {
    "level": 0,
    "sector": "NA-PB",
    "tile": 42,
    "biome": "dungeon"
  }
}
```

### Color Theme Switching

```python
# In core/uDOS_commands.py
def set_theme(theme_name):
    themes = {
        "dungeon": DUNGEON_CRAWLER_THEME,
        "cyber": CYBERPUNK_THEME,
        "classic": TERMINAL_CLASSIC_THEME
    }
    active_theme = themes.get(theme_name, POLAROID_DEFAULT)
    save_user_preference("COLOR_THEME", theme_name)
    return f"✓ Theme set to: {theme_name}"
```

### Responsive Grid Adaptation

```javascript
// Detect viewport size and adjust grid
function adaptGrid() {
  const width = window.innerWidth;
  const container = document.querySelector('.viewport-grid');

  if (width < 640) {
    container.classList.add('compact');  // 40×20
  } else if (width < 1024) {
    container.classList.add('standard'); // 80×24
  } else if (width < 1920) {
    container.classList.add('wide');     // 120×40
  } else {
    container.classList.add('ultra');    // 160×60
  }
}
```

---

## 14. Quick Reference Tables

### Coordinate Format Quick Lookup

| Component | Format | Range | Example | Meaning |
|-----------|--------|-------|---------|---------|
| Level | ±NN | -99 to +99 | `00` | Ground level |
| Latitude | AA-ZZ | AA to ZZ | `MZ` | Equator (0°) |
| Longitude | AA-ZZ | AA to ZZ | `MZ` | Prime Meridian (0°) |
| Local Tile | NN | 00-99 | `50` | Center tile |

### Timestamp Format Quick Lookup

| Format | Example | Use Case |
|--------|---------|----------|
| Full ISO | `2025-10-31T14:32:45.123-07:00` | APIs, exports |
| With Location | `2025-10-31T14:32:45.123-07:00@00-MZ-MZ-50` | Location-aware logs |
| Compact | `2025-10-31 14:32:45 -07` | UI display |
| Filename | `20251031_143245_UTC-07` | File naming |
| Relative | `2 minutes ago` | Recent events |

### Font Variant Quick Lookup

| Variant | Character | Best For |
|---------|-----------|----------|
| Neon | Modern, clean | Default editing, UI |
| Argon | Warm, humanist | Documentation, prose |
| Xenon | Slab serif | Headers, emphasis |
| Radon | Handwritten | Comments, notes |
| Krypton | Mechanical | Code, data tables |

### Color Usage Quick Lookup

| Color | Hex | Terminal | Web | Maps |
|-------|-----|----------|-----|------|
| Red | #FF1744 | Errors | Alerts | Lava, danger |
| Green | #00E676 | Success | Confirm | Grass, safe |
| Yellow | #FFEB3B | Warnings | Highlights | Gold, treasure |
| Blue | #2196F3 | Info | Links | Water, ice |
| Purple | #E91E63 | Magic | Special | Portals, magic |
| Cyan | #00E5FF | Tech | Data | Tech, energy |

---

## 15. Versioning and Updates

**Current Style Guide Version:** 1.1.4 (2025-10-31)

**Changelog:**
- 1.1.4: Added map tile coordinates, timestamps with location, web grid styles
- 1.1.3: Integrated Monaspace font system
- 1.1.2: Consolidated viewport colors from separate document
- 1.1.1: Added Polaroid palette and viewport visualization
- 1.1.0: Initial comprehensive style guide

**Contributing:**

For updates to this style guide, see the [Contributing Guide](https://github.com/fredporter/uDOS/wiki/Contributing) on the wiki.

**Related Documentation:**
- [Command Reference](https://github.com/fredporter/uDOS/wiki/Command-Reference)
- [Mapping System](https://github.com/fredporter/uDOS/wiki/Mapping-System)
- [Architecture](https://github.com/fredporter/uDOS/wiki/Architecture)
- [Viewport Colors](https://github.com/fredporter/uDOS/wiki/Viewport-Colors) *(deprecated - content merged into Style Guide)*

---

**Last Updated:** October 31, 2025
**Maintainer:** Fred Porter
**License:** GNU GPL v3.0
