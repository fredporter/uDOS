# Wizard Font Manager - Font Repository

**Version:** 1.0.0  
**Part of:** uDOS Alpha v1.0.2.0  
**Last Updated:** 2026-01-25

---

## 📚 Overview

Canonical font repository for Wizard dashboard tooling and typography. This directory contains all fonts used across uDOS with proper attribution and metadata.

---

## 📁 Structure

```
/wizard/fonts/
├── manifest.json          # Central registry with credits, settings
├── README.md             # This file
├── distribute.sh         # Optional distribution script (legacy)
├── bundled/              # Production fonts
│   ├── code/            # Code/programming fonts (Monaspace)
│   ├── prose/           # Prose/body fonts
│   └── retro/           # Retro computing fonts
│       ├── c64/        # Commodore 64
│       ├── teletext/   # BBC Micro Teletext
│       ├── apple/      # Classic Mac fonts
│       └── gaming/     # Arcade/gaming fonts
├── emoji/              # Emoji fonts
│   ├── NotoColorEmoji.ttf
│   └── NotoEmoji-Regular.ttf
└── custom/             # User custom fonts

```

---

## 🎯 Features

### 1. **Monosorts Grid Rendering**

24x24 pixel grid character placement with:

- Centering algorithms (baseline, ink-center)
- Vertical/horizontal offset adjustments
- Per-font tuning for optimal rendering

### 2. **Emoji Library Integration**

- Color emoji (Noto Color Emoji)
- Mono emoji (Noto Emoji)
- GitHub shortcode mapping
- Unicode support

### 3. **Distribution System**

Font delivery is handled by Wizard API routes. Optional distribution targets can be
configured in `manifest.json` if needed.

---

## 📋 Font Collections

### Code Fonts (Monaspace) — Code Blocks Only

Five programming fonts with distinct typographic voices for code rendering:

- **Monaspace Argon** - Neutral, system-like (default code font, `.udos`)
- **Monaspace Xenon** - Mechanical, precise (`.ucode`)
- **Monaspace Krypton** - Experimental, italic accents (`.wizard`)
- **Monaspace Neon** - Human-readable, airy (`.mission`)
- **Monaspace Radon** - Additional programming variant

**Usage:** Code blocks ONLY (not available for prose H/P switchers)

Source: [GitHub Next Monaspace](https://monaspace.githubnext.com)  
License: OFL (SIL Open Font License)

### Prose Fonts — H (Heading) & P (Paragraph) Switchers

Available in order of priority:

1. **SF Pro** (Apple) - Default system UI font (macOS)
2. **Iowan Old Style** (Bitstream) - Default serif prose
3. **Monaspace** (all 5) - Programming fonts available for prose
4. **Chicago** (Susan Kare) - Classic Mac System 7
5. **Los Altos** - Mac-inspired UI sans
6. **Sanfrisco** - Modern Mac-style sans
7. **Monaco** (Susan Kare) - Mac monospace terminal
8. **Quicksand** (OFL) - Rounded sans serif
9. **Torrance** - Display/decorative
10. **System Sans** - Fallback system sans
11. **System Serif** - Fallback system serif

### Teletext Fonts — Not Mapped Yet

Reserved for special rendering modes (Monosorts grid, pixel editor, etc.):

- **PetMe64** - Commodore 64 PETSCII graphics
- **Teletext50** - BBC Micro Teletext with block graphics
- **Press Start 2P** - Arcade/gaming pixel font

**Note:** These appear in Font Manager under "Teletext Fonts" tab but are not wired to prose switchers yet.

### Retro Fonts

#### C64 Collection

- **PetMe64** - Commodore 64 PETSCII font (Style64.org)

#### Teletext Collection

- **Teletext50** - BBC Micro Teletext with block graphics (Simon Rawles, OFL)

#### Apple Collection

- **Los Altos** - Classic Mac-inspired UI sans
- **Sanfrisco** - Modern Mac-style UI sans

---

## 📜 Font Credits

See [FONT-CREDITS.md](FONT-CREDITS.md) for complete licensing information and attribution.

**Quick Summary:**

- ✅ **OFL Licensed (Redistributable):** Monaspace, Teletext50, Press Start 2P, Quicksand, UnifrakturCook, Noto Emoji
- ⚠️ **Apple Fonts (Dev Only):** SF Pro, Iowan Old Style, Chicago, Monaco - Not redistributable
- ⚠️ **Free (Check Usage):** Los Altos, Sanfrisco, Torrance
- ⚠️ **Personal Use Only:** PetMe64

---

## 🎯 Font Usage by Type

| Type         | Default       | Code Blocks       | H/P Prose Switchers | Teletext Mode |
| ------------ | ------------- | ----------------- | ------------------- | ------------- |
| **Default**  | SF Pro        | Monaspace Argon   | ✅ All prose fonts  | —             |
| **Code**     | —             | ✅ Monaspace only | ⚠️ Available        | —             |
| **Prose**    | SF Pro, Iowan | —                 | ✅ Primary          | —             |
| **Teletext** | —             | —                 | ❌ Not mapped       | ✅ Reserved   |

---

## 🔧 Usage

### Serving Fonts

Wizard serves fonts via:

```
/api/v1/fonts/manifest
/api/v1/fonts/file?path=retro/apple/ChicagoFLF.ttf
```

Optional distribution targets can still be used via `distribute.sh` if needed.

### Adding New Fonts

1. Add font file to appropriate subdirectory
2. Update `manifest.json` with metadata:
   ```json
   "FontName": {
     "file": "category/subfolder/font.ttf",
     "name": "Display Name",
     "type": "mono" | "color",
     "gridSize": 24,
     "author": "Author Name",
     "license": "License Type",
     "url": "https://source.url",
     "description": "Font description",
     "monosorts": {
       "centering": "baseline" | "ink-center",
       "verticalOffset": 0,
       "horizontalOffset": 0
     }
   }
   ```
3. (Optional) Run `./distribute.sh` to copy to targets
4. Update credits in `manifest.json`

---

## 📜 Credits & Attribution

### Primary Sources

| Source           | URL                                                                              | License             |
| ---------------- | -------------------------------------------------------------------------------- | ------------------- |
| **Google Fonts** | [fonts.google.com](https://fonts.google.com)                                     | OFL, Apache 2.0     |
| **Noto Emoji**   | [github.com/googlefonts/noto-emoji](https://github.com/googlefonts/noto-emoji)   | OFL                 |
| **Teletext50**   | [github.com/simon-rawles/teletext50](https://github.com/simon-rawles/teletext50) | OFL                 |
| **Style64**      | [style64.org](https://style64.org)                                               | Free (personal use) |

### Individual Font Credits

- **PetMe64** - © Style64.org (Free for personal use)
- **Teletext50** - © Simon Rawles (OFL)
- **Chicago / Monaco** - © Susan Kare / Apple (Historical system fonts)
- **ChicagoFLF** - © Robin Casady (Free)
- **Press Start 2P** - © CodeMan38 (OFL)
- **Noto Color Emoji** - © Google (OFL)
- **Noto Emoji** - © Google (OFL)

---

## 🚀 Future: uFont Manager Mac App

This repository serves as the beta foundation for **uFont Manager**, a native Mac app for:

- Google Fonts browser and installer
- Local font management
- Font preview and testing
- System font integration
- Custom font collections

**Target Release:** uDOS v1.1.0.0+

---

## 📝 License Notes

### Open Font License (OFL)

Fonts licensed under OFL can be:

- Used commercially
- Modified and redistributed
- Bundled with software
- **Must retain copyright notice**

### Historical System Fonts

Classic Mac fonts (Chicago, Monaco) are historical system fonts no longer actively distributed by Apple. Usage in retro computing projects is generally accepted.

### Attribution Required

All fonts must maintain their original credits and license information when distributed.

---

## 🔗 Integration Points

### Pixel Editor

- Reads from `/public/fonts/` via `fontLoader.ts`
- Uses `manifest.json` metadata for rendering
- Monosorts grid positioning via `monosorts` settings

### Grid Display

- 24x24 character grid rendering
- Teletext block graphics support
- Custom character sets

### Future Mac App

- Will read from this manifest
- Google Fonts API integration
- System-wide font installation

---

**Part of uDOS Alpha v1.0.2.0**  
**uFont Manager Beta - Font Repository System**
