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
/wizard/font-manager/fonts/
├── manifest.json          # Central registry with credits, settings
├── README.md             # This file
├── distribute.sh         # Optional distribution script (legacy)
├── retro/               # Retro computing fonts
│   ├── c64/            # Commodore 64
│   ├── teletext/       # BBC Micro Teletext
│   ├── apple/          # Classic Mac fonts
│   └── gaming/         # Arcade/gaming fonts
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

### Retro Fonts

#### C64 Collection

- **PetMe64** - Commodore 64 PETSCII font (Style64.org)

#### Teletext Collection

- **Teletext50** - BBC Micro Teletext with block graphics (Simon Rawles, OFL)

#### Apple Collection

- **Chicago** - Classic Mac System 7 font (Susan Kare)
- **Monaco** - Mac monospace terminal font (Susan Kare)
- **ChicagoFLF** - Chicago recreation (Robin Casady)
- **Los Altos** - Classic Mac-inspired UI sans
- **Sanfrisco** - Modern Mac-style UI sans

#### Gaming Collection

- **Press Start 2P** - Arcade pixel font (CodeMan38, OFL)

### Emoji Fonts

- **Noto Color Emoji** - Full-color emoji (Google, OFL)
- **Noto Emoji** - Monochrome emoji (Google, OFL)

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
