# uDOS Character Editor

**Version:** 1.0.24  
**Status:** Active Development  
**Location:** `/extensions/core/font-tools/`

## Overview

The uDOS Character Editor is a comprehensive pixel-art tool for creating, editing, and managing character sets and emoji for the uDOS terminal environment. Supports multiple resolutions, monochrome and multicolor modes, and seamless integration with uDOS fonts and block graphics.

## Features

### Multi-Resolution Support
- **8×8 pixels** - Classic 8-bit character size
- **16×16 pixels** - Standard uDOS character size (default)
- **32×32 pixels** - Enhanced detail characters
- **64×64 pixels** - High-resolution icons
- **128×128 pixels** - Maximum detail graphics

### Font Picker
Comprehensive font library with instant preview and grid population:

#### System Fonts (Monaco Priority Stack)
```
Monaco → Courier New → Courier → monospace
```
- **Monaco** - Classic Mac monospace (primary)
- **Courier New** - Ubiquitous, retro-terminal style
- **Courier** - PostScript core font (guaranteed)
- **monospace** - Generic fallback

#### uDOS Fonts
- **PetMe64** - Authentic C64 PETSCII font
- **PetMe128** - High-res C64 font variant
- **Mallard Blocky** - Teletext-style block font
- **Mallard Blockier** - Extra-bold blocks
- **Mallard Smooth** - Anti-aliased variant
- **Mallard Smoother** - Smoother anti-aliasing
- **Mallard Tiny** - Compact teletext font
- **Chicago** - Classic Mac system font

#### Block Graphics Sets
- **C64 PETSCII Blocks** - Commodore 64 graphics characters
- **Unicode Box Drawing** - Standard box-drawing characters
- **Teletext Graphics** - BBC Teletext block graphics
- **ASCII Extended** - Extended ASCII character set

#### Emoji Sets
- **Noto Emoji Mono** - Google's monospaced emoji
- **Twemoji** - Twitter's multicolor emoji set
- **Custom Emoji** - User-created emoji library

### Color Modes

#### Monochrome Mode (Default)
- Single-color pixel art (black/white or custom)
- Optimized for terminal character sets
- Clean, crisp bitmap output

#### Multicolor Mode
- Full Synthwave DOS 16-color palette
- Support for emoji and icons
- Per-pixel color selection
- Custom color addition

### Editing Tools

- **Draw** - Freehand pixel drawing (D)
- **Erase** - Remove individual pixels (E)
- **Fill** - Flood-fill regions (F)
- **Line** - Draw straight lines (L)
- **Rectangle** - Draw rectangles (R)
- **Circle** - Draw circles (C)

### Transform Operations

- **Flip Horizontal** - Mirror character left-right
- **Flip Vertical** - Mirror character top-bottom
- **Rotate CW** - Rotate 90° clockwise
- **Rotate CCW** - Rotate 90° counter-clockwise
- **Invert** - Swap black/white pixels
- **Shift Up/Down/Left/Right** - Move pixels by 1px

## System Font Stack Rationale

The uDOS Character Editor uses a carefully designed font stack that prioritizes aesthetics while ensuring universal compatibility:

$$\\text{Font Stack} = \\text{Monaco}, \\text{Courier New}, \\text{Courier}, \\text{monospace}$$

### Monaco (Priority 1)
- **Why:** Recognizable and beloved classic Mac monospace font
- **Aesthetic:** Clean, professional, nostalgic
- **Availability:** macOS (built-in), some Linux distributions

### Courier New (Priority 2)
- **Why:** Balance of ubiquity and clear retro-terminal style
- **Aesthetic:** Classic typewriter monospace
- **Availability:** Universal (Windows, macOS, Linux)

### Courier (Priority 3)
- **Why:** Guaranteed PostScript core font
- **Aesthetic:** Original typewriter font
- **Availability:** All platforms (PostScript standard)

### monospace (Priority 4)
- **Why:** Generic fallback ensures monospace rendering
- **Aesthetic:** System-dependent
- **Availability:** Universal (CSS generic family)

This cascading stack ensures optimal aesthetics while maintaining universal compatibility across all platforms.

## Credits

- **Original Concept:** uDOS Font Manager v1.0.23
- **Redesign:** Character Editor v1.0.24
- **Color Palette:** Synthwave DOS 16-color standard
- **Fonts:** 
  - PetMe by Style (C64 font)
  - Mallard by Elias Steurer (Teletext font family)
  - Chicago by Susan Kare (Classic Mac font)

## Version History

### v1.0.24 (Current)
- Renamed from Font Manager to Character Editor
- Added multi-resolution support (8×8 to 128×128)
- Implemented Font Picker with System/uDOS/Block/Emoji categories
- Added Synthwave DOS 16-color palette
- Multicolor mode for emoji design
- Monospaced emoji support (Noto Emoji Mono)
- System font stack (Monaco priority)
- Enhanced transform tools (shift operations)
- Character Set grid view
- /memory integration for saved sets

### v1.0.23 (Previous)
- Original Font Manager implementation
- 16×16 bitmap editor
- Basic TTF viewer
- Polaroid color palette
