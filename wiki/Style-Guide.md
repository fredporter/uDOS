# uDOS Style Guide

**Version:** v1.2.21 (December 2025)

This document outlines design and style conventions for uDOS, ensuring consistent user experience across CLI, TUI, graphics, and data formats. Core principles: human-readable, minimal-touch, offline-first, authentic retro computing aesthetics.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Command Syntax](#2-command-syntax)
3. [TUI Key Bindings](#3-tui-key-bindings)
4. [uPY Scripting Conventions](#4-upy-scripting-conventions)
5. [Typography and Fonts](#5-typography-and-fonts)
6. [Color System](#6-color-system)
7. [Graphics and Diagrams](#7-graphics-and-diagrams)
8. [TILE Code Format](#8-tile-code-format)
9. [File Naming](#9-file-naming)
10. [Quick Reference](#10-quick-reference)

---

## 1. Core Principles

- **Clarity over cleverness**: Commands and outputs prioritize readability
- **Minimalism**: Reduce unnecessary keystrokes and visual noise
- **Offline-first**: Full functionality without internet/API keys
- **Text-first**: Terminal-based, ASCII graphics, minimal dependencies
- **Modular**: Clean separation (core → services → extensions)
- **Human-centric**: Natural language commands, practical focus

---

## 2. Command Syntax

### User Commands

Commands are simple, memorable, uppercase words following `COMMAND [ARGUMENT] [--FLAG]` pattern.

**Examples:**
```bash
GUIDE water
MAP CENTER AA340-100
MAKE --format ascii --template flowchart --source "Process Flow"
CONFIG SET theme foundation
STATUS --health
```

### Command Conventions

- **Commands**: Single uppercase words (GUIDE, MAP, MAKE, CONFIG)
- **Arguments**: Quoted strings or TILE codes
- **Flags**: Double-dash prefix (--format, --template, --ai-assisted)
- **Options**: Key-value pairs (--width 80, --palette classic)

### Output Formatting

- **Success**: `✅ File saved to memory/drafts/ascii/diagram.txt`
- **Error**: `❌ ERROR: Template not found: invalid_template`
- **Info**: `ℹ️ Renderer service running on port 5555`
- **Warning**: `⚠️ WARNING: Size limit exceeded (5KB max)`

---

## 3. TUI Key Bindings

### Panel Keys (v1.2.21)

Single-key shortcuts for TUI panels:

| Key | Panel | Purpose | Version |
|-----|-------|---------|---------|
| **W** | Workflow Manager | Missions, checkpoints, templates | v1.2.20 |
| **O** | OK Assistant | AI-powered content generation | v1.2.21 |
| **C** | Config & Settings | Browse/edit settings | v1.2.18 |
| **D** | Dev Browser | System files, dev logs | v1.2.19 |
| **L** | Debug Panel | Live logs, error tracking | v1.2.19 |
| **T** | Testing | SHAKEDOWN, unit tests | v1.2.19 |
| **S** | Server Panel | Extensions, health status | v1.2.16 |
| **0** | File Browser | 5 workspaces (knowledge, docs, drafts, sandbox, scripts) | v1.2.15 |
| **ESC** | Close Panel | Exit current panel | v1.2.15 |

### Panel Navigation

```bash
# Open workflow manager
W

# Select workflow with arrow keys
↑↓ Select workflow
→ View details
← Back to list
ENTER Start workflow

# Close panel
ESC
```

### Panel State

- **Active panel**: Renders above command prompt
- **Single panel limit**: Only one panel open at a time
- **ESC closes**: Always returns to command mode
- **Persistent state**: Panel position/selection saved in `memory/system/user/`

---

## 4. uPY Scripting Conventions

### Variable Naming (v1.2.x)

**System Variables** (read-only):
```python
$MISSION.ID              # Unique mission identifier
$MISSION.NAME            # Mission name
$MISSION.STATUS          # DRAFT|ACTIVE|PAUSED|COMPLETED|FAILED
$MISSION.PROGRESS        # "3/5" or "60%"
$WORKFLOW.NAME           # Current workflow script
$WORKFLOW.PHASE          # INIT|SETUP|EXECUTE|MONITOR|COMPLETE
$LOCATION.TILE_CODE      # Current TILE location (e.g., "AA340")
```

**User Variables** (read/write):
```python
SET WATER_SOURCE="river"
SET STEPS_REMAINING=5
SET DESTINATION="AB340-100"
```

### Flow Control

```python
# Conditionals
IF $LOCATION.TILE_CODE == "AA340" THEN
    PRINT "At Sydney location"
ELIF $LOCATION.TILE_CODE CONTAINS "AA" THEN
    PRINT "In Australian region"
ELSE
    PRINT "Outside region"
END

# Loops
FOR STEP IN RANGE(1, 6):
    PRINT "Step $STEP of 5"
    CHECKPOINT "Step $STEP complete"
END

WHILE $STEPS_REMAINING > 0:
    PRINT "Steps remaining: $STEPS_REMAINING"
    SET STEPS_REMAINING=$STEPS_REMAINING - 1
END
```

### Checkpoint Syntax

```python
# Create checkpoint
CHECKPOINT "Location Assessment"

# Conditional checkpoint
IF $MISSION.PROGRESS > 50% THEN
    CHECKPOINT "Halfway complete"
END
```

### File Structure

```python
# mission_template.upy
MISSION_NAME="Mission Title"
STEP=1
TOTAL_STEPS=5

# Step 1
PRINT "=== Step 1: Description ==="
# ... step logic ...
CHECKPOINT "Step 1 complete"

# Step 2
PRINT "=== Step 2: Description ==="
# ... step logic ...
CHECKPOINT "Step 2 complete"

# ... continue for all steps ...
```

---

## 5. Typography and Fonts

### Font System (v1.2.15)

uDOS uses retro fonts stored in `extensions/assets/fonts/` with comprehensive fallbacks.

**Primary Fonts:**

| Font | Variants | Use Case |
|------|----------|----------|
| Chicago | 2 | System UI, Mac Classic theme |
| Mallard | 6 | Teletext rendering, BBC Micro |
| PetMe | 7 | C64 Terminal, Commodore theme |
| MODE7GX3 | 1 | Teletext fallback |

**Font Stacks:**

```css
/* System (Chicago) */
font-family: 'Chicago', 'Chicago FLF', -apple-system, monospace;

/* Teletext (Mallard) */
font-family: 'Mallard', 'MODE7GX3', 'Courier New', monospace;

/* Terminal (PetMe) */
font-family: 'PetMe64', 'PetMe', 'Courier New', monospace;

/* Monospace fallback */
font-family: 'Monaco', 'Courier New', monospace;
```

**Loading:**
- Use `font-display: swap` for performance
- Relative paths from extension root
- Include generic fallbacks (monospace, sans-serif)

---

## 4. Color System

### Synthwave DOS Palette

8-color ANSI palette optimized for terminal visibility:

| Color | Hex | RGB | Use Case |
|-------|-----|-----|----------|
| 🔴 Red | #FF1744 | 255,23,68 | Errors, alerts, danger |
| 🟢 Green | #00E676 | 0,230,118 | Success, confirmations |
| 🟡 Yellow | #FFEB3B | 255,235,59 | Warnings, highlights |
| 🔵 Blue | #2196F3 | 33,150,243 | Information, links |
| 🟣 Purple | #E91E63 | 233,30,99 | Special events, magic |
| 🔷 Cyan | #00E5FF | 0,229,255 | Technology, data |
| ⚪ White | #FFFFFF | 255,255,255 | Default text |
| ⚫ Black | #000000 | 0,0,0 | Background |

### Box Drawing Characters

**Double-line:**
```
╔═══╦═══╗
║   ║   ║
╠═══╬═══╣
║   ║   ║
╚═══╩═══╝
```

**Single-line:**
```
┌───┬───┐
│   │   │
├───┼───┤
│   │   │
└───┴───┘
```

**Blocks:**
- █ Full (100%)
- ▓ Dark (75%)
- ▒ Medium (50%)
- ░ Light (25%)

---

## 5. Graphics and Diagrams

### 5-Format Graphics System (v1.2.15)

**Format Overview:**

| Format | Templates | Renderer | Output | Max Size |
|--------|-----------|----------|--------|----------|
| ASCII | 25 | ascii.js | .txt | 5KB |
| Teletext | 4 | teletext.js | .ans | 10KB |
| SVG | 3 | svg.js | .svg | 50KB |
| Sequence | 5 | sequence.js | .svg | 5KB |
| Flow | 5 | flow.js | .svg | 5KB |

### MAKE Command

Unified command for all graphics formats:

```bash
# ASCII diagrams
MAKE --format ascii --template flowchart --source "Process" --width 80

# Teletext pages
MAKE --format teletext --palette classic --source "{2}╔═══╗{/}"

# SVG diagrams
MAKE --format svg --style technical --source "Architecture"

# Sequence diagrams
MAKE --format sequence --template login_flow --source "User->App: Login"

# Flowcharts
MAKE --format flow --template simple_decision --source "st=>start: Begin"
```

### Template Categories

**ASCII (25 templates):**
- Flowcharts (5): basic, decision, process, swim_lanes, multi_branch
- Architecture (3): layered, microservices, network_topology
- Progress (3): progress_bar, status_table, metrics_grid
- Data viz (4): funnel_chart, timeline, comparison_table, data_tree
- Decision trees (2): binary_tree, weighted_tree
- Org charts (2): org_chart, hierarchy
- Network (2): network_map, dependency_graph
- Misc (2): gantt_chart, kanban_board

**Teletext (4 palettes):**
- classic: Standard ANSI colors
- earth: Brown/green natural tones
- terminal: Green monochrome
- amber: Orange monochrome

**SVG (3 styles):**
- technical: Blueprint/engineering with grid
- simple: Minimalist flat colors
- detailed: Gradients, shadows, full color

**Sequence (5 templates):**
- login_flow: 3-actor authentication
- error_handling: Retry/fallback patterns
- multi_system: 4+ actors microservices
- async_process: Queue/webhook patterns
- survival_guide: Step-by-step procedures

**Flow (5 templates):**
- simple_decision: Basic yes/no (5 nodes)
- login_process: Authentication with retry (10+ nodes)
- data_pipeline: Validation/transformation
- error_recovery: Retry/fallback/circuit breaker
- business_logic: Complex workflows (15+ nodes)

### Graphics Service

**Node.js Renderer:**
- Port: 5555
- Health: GET /health
- Endpoints: POST /render/{ascii,teletext,svg,sequence,flow}

**Start Service:**
```bash
node extensions/core/renderers/server.js
# Or via extension manager:
EXTENSION START graphics-renderer
```

---

## 6. TILE Code Format

**Strict Format:** `[COLUMN][ROW][-LAYER]`

### Components

- **COLUMN**: 2-letter code (AA-RL = 0-479)
- **ROW**: Numeric (0-269)
- **LAYER**: Optional (100/200/300/400/500)

### Examples

```
AA340           # Sydney (layer unspecified)
AA340-100       # Sydney at world layer (~83km/cell)
JF57-300        # London at city layer (~93m/cell)
BZ42-200        # Custom position at region layer
```

### Invalid Formats (Deprecated)

```
❌ AS-JP-TYO         # Old hierarchical (removed v1.1.12)
❌ [-33.87, 151.21]  # Lat/long coordinates
❌ A340              # Single-letter column
❌ AA340-50          # Invalid layer
```

---

## 7. File Naming

### Conventions

- **Python modules**: `lowercase_with_underscores.py`
- **uPY scripts**: `descriptive_name.upy`
- **Documentation**: `Title-Case-With-Dashes.md`
- **Config files**: `lowercase.json`, `lowercase.yaml`
- **Graphics output**: `descriptive_name.{txt,ans,svg}`

### Directory Structure

```
core/                   # Core system (tracked)
├── commands/           # Command handlers
├── data/              # Templates, configs
├── services/          # Core services
└── ui/                # TUI components

memory/                # User workspace (gitignored except ucode/)
├── ucode/             # Scripts and tests
│   ├── scripts/       # User .upy scripts
│   ├── tests/         # Test suites
│   ├── stdlib/        # Standard library
│   ├── examples/      # Example scripts
│   └── adventures/    # Adventure scripts
├── workflows/         # Workflow automation
└── drafts/            # Generated graphics
    ├── ascii/         # ASCII diagrams
    ├── teletext/      # Teletext pages
    ├── svg/           # SVG graphics
    ├── sequence/      # Sequence diagrams
    └── flow/          # Flowcharts

extensions/            # Extension system
├── assets/            # Shared assets (fonts, icons)
├── core/              # Core extensions
└── play/              # Gameplay extensions

knowledge/             # Knowledge bank (read-only)
├── water/             # Water guides (26 files)
├── fire/              # Fire guides (20 files)
└── shelter/           # Shelter guides (20 files)
```

---

## 8. Quick Reference

### Command Cheat Sheet

```bash
# Knowledge
GUIDE water                 # Load water guide
GUIDE fire boiling          # Search fire guides

# Graphics
MAKE --format ascii --template flowchart --source "Process"
MAKE --format teletext --palette classic --source "{2}Text{/}"
MAKE --format svg --style technical --source "Architecture"
MAKE --format sequence --template login_flow --source "User->App"
MAKE --format flow --template simple_decision --source "st=>start"

# Map
MAP CENTER AA340-100        # Sydney world layer
MAP LAYER 300               # City layer
STATUS location             # Current position

# Config
CONFIG GET theme            # View setting
CONFIG SET theme foundation # Update setting
CONFIG CHECK                # Validate structure
CONFIG FIX                  # Create missing folders

# System
STATUS                      # System health
STATUS --health             # Detailed metrics
CLEAN                       # Remove temp files
TREE                        # Show folder structure
```

### Graphics Format Summary

| Need | Use | Command |
|------|-----|---------|
| Flowchart | ASCII | `MAKE --format ascii --template flowchart` |
| Colored page | Teletext | `MAKE --format teletext --palette classic` |
| Detailed diagram | SVG | `MAKE --format svg --style detailed` |
| Process flow | Sequence | `MAKE --format sequence --template login_flow` |
| Decision tree | Flow | `MAKE --format flow --template simple_decision` |

### TILE Code Reference

| City | TILE Code | Layer 100 |
|------|-----------|-----------|
| Sydney | AA340-100 | World |
| London | JF57-100 | World |
| Tokyo | QR68-100 | World |
| New York | KL82-100 | World |

### Layer Sizes

| Layer | Resolution | Use |
|-------|------------|-----|
| 100 | ~83 km/cell | Continental |
| 200 | ~2.78 km/cell | Regional |
| 300 | ~93 m/cell | Urban |
| 400 | ~3 m/cell | Building |
| 500 | ~10 cm/cell | Detail |

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
<span class="nes-badge is-success">v1.1.15</span>
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

## 7. Typography and Fonts

### uDOS Core Font System

uDOS v1.1.15 uses a curated collection of retro fonts stored in `extensions/assets/fonts/` with comprehensive fallback stacks for reliability. The font system is managed by the Asset Manager and integrated across all extensions.

**Font Management:** See [ASSETS-GUIDE](ASSETS-GUIDE.md) for programmatic font loading and the complete font catalog.

**Retro Font Families:**

| Font Family | Variants | Description | Use Case |
|-------------|----------|-------------|----------|
| **Chicago** | 2 | Apple System font recreations | System 7 Desktop, classic Mac interfaces |
| **Mallard** | 6 | BBC Teletext rendering fonts | Teletext extension, broadcast interfaces |
| **PetMe** | 7 | Commodore PET/CBM fonts | C64 Terminal, Commodore-themed interfaces |
| **MODE7GX3** | 1 | BBC Micro Mode 7 Teletext | Teletext fallback |

**Font Fallback Stacks:**

```css
/* Chicago (System 7 Desktop) */
font-family: 'Chicago', 'Chicago FLF', -apple-system, BlinkMacSystemFont, monospace;

/* Mallard (Teletext) */
font-family: 'Mallard', 'MODE7GX3', 'Courier New', monospace;

/* PetMe (C64 Terminal) */
font-family: 'PetMe64', 'PetMe', 'Courier New', monospace;

/* Generic Monospace */
font-family: 'Monaco', 'Courier New', 'Courier', monospace;
```

**Font Loading Best Practices:**
- All fonts use `font-display: swap` to prevent invisible text
- Relative paths from extension root (e.g., `fonts/chicago/ChicagoFLF.ttf`)
- Include generic fallbacks (`monospace`, `sans-serif`)
- Test with fonts disabled to verify fallbacks work

**Font Licensing:**
- ✅ Chicago (ChicagoFLF): Public domain
- ✅ Chicago (12-1): CC BY-SA 3.0
- ✅ Mallard: CC BY-SA 3.0 (gid/FontStruct.com)
- ✅ PetMe: Kreative Software Free Use License v1.2f

**Font Documentation:** See `extensions/core/fonts/README.md` for complete usage guide and licensing information.

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
- **Web fonts**: Installed via `bash extensions/archive/old-setup-scripts/setup_monaspace.sh`
- **Format**: WOFF2 (web), OTF (system)
- **Location**: `extensions/archive/old-clones/monaspace-fonts/`

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

### Synthwave DOS Color System

uDOS v1.1.15 uses the **Synthwave DOS** color palette as its default system theme. This palette is inspired by high-contrast instant photography and optimized for terminal visibility.

**Primary Color Reference:**

| Color | Name | tput | Hex | RGB | Usage |
|:------|:-----|:----:|:---:|:---:|:------|
| 🔴 | Synthwave DOS Red | 196 | #FF1744 | 255,23,68 | Errors, alerts, critical warnings, danger zones |
| 🟢 | Synthwave DOS Green | 46 | #00E676 | 0,230,118 | Success, confirmations, growth, positive status |
| 🟡 | Synthwave DOS Yellow | 226 | #FFEB3B | 255,235,59 | Warnings, caution, highlights, notifications |
| 🔵 | Synthwave DOS Blue | 21 | #2196F3 | 33,150,243 | Information, links, system messages, cold tones |
| 🟣 | Synthwave DOS Purple | 201 | #E91E63 | 233,30,99 | Magic, spells, special events, fantasy elements |
| 🔷 | Synthwave DOS Cyan | 51 | #00E5FF | 0,229,255 | Technology, data, navigation, cool highlights |
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

### Viewport System & Screen Size Reference

**Character Block System:**
uDOS operates using a **16×16 character block grid system** where each cell represents 16×16 pixels. All dimensions are specified in both **cells** and **pixels** for precise viewport management.

**Screen Size Tiers (14 standard sizes):**

| Tier | Label          | Description        | Width (cells) | Height (cells) | Width (px) | Height (px) | Aspect |
|------|----------------|--------------------|---------------|----------------|-------------|--------------|---------|
| 0    | Watch          | Wearable display   | 13            | 13             | 208         | 208          | 1:1     |
| 1    | Mini Phone     | Small smartphone   | 20            | 11             | 320         | 176          | 16:9    |
| 2    | Phone          | Standard smartphone| 23            | 11             | 368         | 176          | 19:9    |
| 3    | Big Phone      | Large smartphone   | 27            | 12             | 432         | 192          | 20:9    |
| 4    | Compact Tab    | Small tablet       | 38            | 25             | 608         | 400          | 3:2     |
| 5    | Wide Tab       | Full-size tablet   | 48            | 36             | 768         | 576          | 4:3     |
| 6    | Small Notebook | Compact laptop     | 64            | 40             | 1024        | 640          | 16:10   |
| 7    | Notebook       | Standard laptop    | 80            | 45             | 1280        | 720          | 16:9    |
| 8    | HD Display     | Desktop monitor    | 120           | 68             | 1920        | 1088         | 16:9    |
| 9    | Wide Display   | WQHD monitor       | 160           | 90             | 2560        | 1440         | 16:9    |
| 10   | Ultra Display  | Ultrawide screen   | 215           | 92             | 3440        | 1472         | 21:9    |
| 11   | 4K Screen      | UHD display        | 240           | 135            | 3840        | 2160         | 16:9    |
| 12   | 5K Screen      | Retina display     | 320           | 180            | 5120        | 2880         | 16:9    |
| 13   | 8K Wall        | Large LED panel    | 480           | 270            | 7680        | 4320         | 16:9    |
| 14   | Cinema Scope   | Projection stage   | 360           | 150            | 5760        | 2400         | 2.39:1  |

**Visual Size Comparison (relative width):**
```
Watch:          █
Mini Phone:     ██
Phone:          ███
Big Phone:      ████
Compact Tab:    ██████
Wide Tab:       ███████
Small Notebook: █████████
Notebook:       ██████████
HD Display:     ███████████████
Wide Display:   ██████████████████
Ultra Display:  ██████████████████████
4K Screen:      ██████████████████████████
5K Screen:      ███████████████████████████████
8K Wall:        ██████████████████████████████████████
Cinema Scope:   ████████████████████████████
```

**Viewport Configuration:**
- **Automatic Detection**: System calculates nearest screen size tier at startup/reboot
- **Manual Override**: Use `CONFIG VIEWPORT <width> <height>` or `SETUP VIEWPORT`
- **Responsive Design**: Grid panels and layout adapt to viewport dimensions
- **Cross-Platform**: Works consistently across CLI, web, and terminal environments

**Terminal Detection:**
- **Dimensions**: Automatically detected (e.g., 80×24, 120×40)
- **Unicode Support**: Tests rendering of special characters
- **Color Depth**: Detects 256-color, 16-color, or monochrome
- **Font Type**: Verifies monospace font rendering
- **Grid Calculation**: Maps terminal size to nearest screen size tier

**ViewportVisualizer System:**

Features implemented in `core/uDOS_viewport_viz.py`:
- Color palette visual display
- Grayscale gradient test
- Shading blocks demonstration
- ASCII art logo rendering
- Dimension and boundary testing
- Font spacing verification
- Capability detection and reporting
- Screen size tier identification

**Commands:**
```
PALETTE                # Display full color palette
REBOOT                 # Includes viewport splash screen with tier detection
VIEWPORT               # Show current viewport specs and screen size tier
CONFIG VIEWPORT <w> <h># Set custom viewport dimensions (in cells)
SETUP VIEWPORT         # Interactive viewport configuration
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

Apply Synthwave DOS palette colors via CSS classes:

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
- Fonts: `extensions/archive/old-clones/monaspace-fonts/`
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

## 13. Graphics and Diagrams

**Version:** v1.2.20 (Workflow Management System - December 2025)
**Philosophy:** Text-first, offline-compatible, chunky teletext aesthetic

### Core Principles

1. **ASCII/Teletext Only** - All diagrams use text characters, no images
2. **Embedded in Markdown** - Diagrams live in guide files, not separate
3. **Offline Rendering** - Full functionality without internet
4. **Chunky Aesthetic** - Retro teletext blocks (▐ ▀ ▄) preferred
5. **Terminal Compatible** - Renders correctly in all terminals

### Diagram Types

#### Flow Diagrams (Process Steps)

**Use For:** Sequential processes, step-by-step instructions, workflows

**Example:**
```
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐        Pre-Filter (if needed)        ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐               Boiling                ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
                   ┃
                   ▼
▐▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▌
▐          Cooling & Storage           ▌
▐▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▌
```

**Code:**
```python
from core.services.graphics_compositor import create_flow

diagram = create_flow(
    steps=['Pre-Filter (if needed)', 'Boiling', 'Cooling & Storage'],
    style='chunky',
    width=40
)
```

#### Tree Diagrams (Hierarchies)

**Use For:** Categories, taxonomies, decision trees, organizational structures

**Example:**
```
                Shelter Types
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     Natural     Constructed    Improvised
        │             │             │
    ┌───┼───┐     ┌───┼───┐     ┌───┼───┐
    ▼   ▼   ▼     ▼   ▼   ▼     ▼   ▼   ▼
  Cave Rock Tree  Lean A-frame  Tarp Snow
              Hollow -to   Debris  Shelter Cave
                          Hut
```

**Code:**
```python
from core.services.graphics_compositor import create_tree

diagram = create_tree(
    root='Shelter Types',
    branches={
        'Natural': ['Cave', 'Rock', 'Tree Hollow'],
        'Constructed': ['Lean-to', 'A-frame', 'Debris Hut'],
        'Improvised': ['Tarp Shelter', 'Snow Cave']
    },
    style='chunky'
)
```

#### Grid Diagrams (Comparisons)

**Use For:** Feature comparisons, specifications, checklists, ratings

**Example:**
```
╔════════════╦════════╦════════════╦═══════════╗
║ Method     ║  Time  ║ Difficulty ║   Tools   ║
╠════════════╬════════╬════════════╬═══════════╣
║ Boiling    ║ 10 min ║    Easy    ║ Pot, fire ║
║ Chemical   ║ 30 min ║    Easy    ║  Tablets  ║
║ UV Light   ║ 15 min ║   Medium   ║ UV device ║
║ Filter     ║  5 min ║    Easy    ║   Filter  ║
╚════════════╩════════╩════════════╩═══════════╝
```

**Code:**
```python
from core.services.graphics_compositor import create_grid

diagram = create_grid(
    headers=['Method', 'Time', 'Difficulty', 'Tools'],
    rows=[
        ['Boiling', '10 min', 'Easy', 'Pot, fire'],
        ['Chemical', '30 min', 'Easy', 'Tablets'],
        ['UV Light', '15 min', 'Medium', 'UV device'],
        ['Filter', '5 min', 'Easy', 'Filter']
    ],
    style='chunky'
)
```

### Teletext Block Character Set

**Core Blocks:**
```
█ ▓ ▒ ░    Solid blocks (dark to light)
▐ ▀ ▄      Chunky teletext blocks
▌ ▐        Half blocks (left/right)
▀ ▄        Half blocks (top/bottom)
```

**Box Drawing:**
```
┌─┐        Light borders
│ │
└─┘

╔═╗        Heavy/double borders
║ ║
╚═╝

╭─╮        Rounded borders
│ │
╰─╯
```

**Arrows & Connectors:**
```
↑ ↓ ← →    Thin arrows
▲ ▼ ◄ ►    Solid arrows
┃ ━        Heavy lines
│ ─        Light lines
```

**Terrain & Icons:**
```
≈          Water/waves
∩          Hills
▲          Mountains
♠ ♣        Trees/forest
∴          Desert/sand
· ∙        Dots/points
● ○        Circles (filled/hollow)
■ □        Squares (filled/hollow)
```

### Embedding Diagrams in Guides

**Markdown Structure:**
```markdown
# Guide Title

## Overview
Brief description...

## Step-by-Step Instructions
1. Step one
2. Step two
3. Step three

## Diagram

```
[ASCII diagram here - no code markers inside]
```

## Key Points
- Point 1
- Point 2

## Sources
- Source citation
```

**Best Practices:**
1. Place diagram after instructions, before key points
2. Use triple backticks (```) around diagram
3. No syntax highlighting language (just ```)
4. Ensure diagram is 80 chars wide max for terminal compatibility
5. Test rendering in actual terminal

### Style Guidelines

#### Box Styles

| Style | Characters | Use Case |
|-------|-----------|----------|
| `chunky` | ▐ ▀ ▄ | Default, teletext aesthetic |
| `heavy` | ╔ ═ ╗ | Emphasis, warnings |
| `light` | ┌ ─ ┐ | Subtle, minimal |
| `double` | ╔ ═ ╗ | Tables, grids |
| `rounded` | ╭ ─ ╮ | Friendly, modern |

#### Width Standards

- **Narrow:** 30 chars - Mobile/small terminals
- **Standard:** 40 chars - Default for most diagrams
- **Wide:** 60 chars - Detailed comparisons
- **Max:** 80 chars - Terminal compatibility limit

#### Spacing

- **Compact:** No spacing between elements
- **Standard:** 1 line between boxes (default)
- **Spacious:** 2+ lines for readability

### Tools & Scripts

**Generate New Guide with Diagram:**
```bash
.venv/bin/python sandbox/scripts/generate_knowledge_guide.py \
    --category water \
    --title "Water Purification Methods" \
    --type flow \
    --complexity beginner
```

**Add Diagrams to Existing Guides:**
```bash
# Refresh single category
.venv/bin/python sandbox/scripts/refresh_knowledge_diagrams.py knowledge/water/

# Refresh all categories
.venv/bin/python sandbox/scripts/refresh_knowledge_diagrams.py --all
```

**Validate Content:**
```bash
.venv/bin/python sandbox/scripts/validate_knowledge_content.py --all
```

**Generate Custom Diagram:**
```python
from core.services.graphics_compositor import GraphicsCompositor

gc = GraphicsCompositor()

# Flow diagram
flow = gc.create_flow(['Step 1', 'Step 2', 'Step 3'], style='chunky', width=40)
print(flow)

# Save to file
with open('diagram.txt', 'w') as f:
    f.write(flow)
```

### Block Library Reference

**Location:** `core/data/graphics/blocks/`

```
teletext.json       Core teletext blocks
├── solid_blocks    █, ▓, ▒, ░
├── box_drawing     ┌─┐ ╔═╗ ╭─╮
├── arrows          ↑ ↓ ← → ▲ ▼
├── icons           ● ○ ■ □ ▪ ▫
├── geometric       △ ▽ ◇ ◆
├── terrain         ≈ ∩ ▲ ♠ ♣
└── mosaic_2x3      ▐ ▀ ▄ (chunky)

borders.json        Border styles
├── heavy           ▐ ▀ ▄
├── double          ╔ ═ ╗
├── light           ┌ ─ ┐
├── rounded         ╭ ─ ╮
└── chunky          ▐ ▀ ▄ (default)

patterns.json       Fill patterns
├── solid           Full blocks
├── gradient        █ ▓ ▒ ░
├── checkerboard    Alternating
└── dots            Sparse

maps.json           Map terrain
├── terrain_chars   Ocean, land, mountains
├── biome_patterns  Forest, desert, etc.
└── gradients       Elevation transitions
```

### Examples in Knowledge Bank

**Current Coverage (v1.1.15):**
- Water guides: 17/25 have diagrams (68%)
- Fire guides: 12/20 have diagrams (60%)
- Shelter guides: 13/20 have diagrams (65%)
- Food guides: 12/22 have diagrams (55%)
- Medical guides: 12/26 have diagrams (46%)
- Navigation guides: 10/20 have diagrams (50%)

**Example Files:**
- `knowledge/water/boiling-purification.md` - Flow diagram
- `knowledge/fire/bow_drill_technique.md` - Flow diagram
- `knowledge/shelter/lean-to_construction.md` - Flow diagram

### SVG Graphics Evolution

**Status:** Replaced by Nano Banana integration in v1.1.15 (December 2025)

**Graphics System Evolution:**
- **ASCII/Teletext graphics**: Core system (always available, offline)
- **SVG generation**: Nano Banana pipeline - `GENERATE SVG --survival <category>/<prompt>`
- **MERMAID, GEOJSON, STL, TYPORA**: GitHub diagrams integration (v1.1.14+)

**Historical:**
- v1.1.1: Removed 135 static SVG files, embedded diagrams as ASCII/teletext
- v1.1.6: Added Nano Banana AI-powered SVG generation
- v1.1.14: Integrated GitHub diagrams (Mermaid, GeoJSON, STL)
- v1.1.15: Graphics infrastructure complete with survival prompts

**Current Approach:**
- Offline-first: ASCII/Teletext for core content
- AI-powered: SVG generation via Nano Banana when API available
- GitHub integration: Mermaid/GeoJSON/STL for technical diagrams

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

**Current Style Guide Version:** v1.2.20 (December 2025)

**Changelog:**
- **v1.2.20**: Added TUI key bindings, uPY scripting conventions, workflow system standards
- **v1.2.15**: Graphics and diagrams system (ASCII/teletext)
- **v1.1.4**: Map tile coordinates, timestamps with location, web grid styles
- **v1.1.3**: Integrated Monaspace font system
- **v1.1.2**: Consolidated viewport colors from separate document
- **v1.1.1**: Added Synthwave DOS palette and viewport visualization
- **v1.1.0**: Initial comprehensive style guide

**Contributing:**

For updates to this style guide, see [Contributing Guide](CONTRIBUTING.md).

**Related Documentation:**
- [Command Reference](Command-Reference.md)
- [TUI Guide](TUI-Guide.md) - Keyboard navigation
- [Workflow Management](Workflow-Management.md) - Mission system
- [Mapping System](Mapping-System.md) - TILE grid
- [uPY Scripting](uPY-Scripting-Guide.md) - Mission scripts
- [Architecture](Architecture.md)

---

**Last Updated:** December 8, 2025  
**Maintainer:** Fred Porter  
**License:** MIT License
