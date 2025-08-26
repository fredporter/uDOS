
# uDOS Font Editor – Design Document
*Version: Draft 1.0 • Date: 26 Aug 2025*

The **uDOS Font Editor** is a pixel‑level editor for creating, modifying, and exporting **16×16 monosort bitmap fonts** (uCELL standard). Inspired by Apple’s 1984 **Font Editor** and BBC Teletext design, it provides a minimal, retro‑styled UI that doubles as a powerful font development tool for the uDOS ecosystem.

---

## 🎯 Goals
- Provide a **native tool** for editing uDOS fonts in the **16×16 uCELL grid**.  
- Maintain **monosort alignment** for ASCII art, Unicode box drawing, and system UI.  
- Support **overlay 4× grids (64×64 effective)** for detailed icons.  
- Export to **uDATA JSON** + convert to `.ttf` or `.bdf` for system integration.  
- Retro feel: minimalist UI, block graphics, ASCII‑styled menus.  

---

## 🖥️ Core Features

### 1. Glyph Editing Grid
- **Default size**: 16×16 (uCELL)  
- **Optional overlay**: 4× (64×64 effective) for icons/logos  
- **Tools**: Pencil, Eraser, Fill, FlipH, FlipV, Rotate90  

### 2. Glyph Metadata
- **Codepoint**: Unicode / ASCII value (e.g., `U+0041 A`)  
- **Advance Width**: Default 16 (fixed mono); override if needed  
- **Baseline**: Row 9 of 16 (system standard)  

### 3. Live Preview
- Preview string: `"0123456789 ABCDEFGHIJKLM nopqrstuvwxyz"`  
- UI mock: show character in **Terminal**, **Dashboard**, and **Button** contexts.  
- Switchable **color palettes** for testing.  

### 4. Font Management
- **New / Open / Save** (uDATA JSON format)  
- **Export**: `.ttf` (via converter), `.bdf`, `.json`  
- **Import**: existing uDOS `.json` font packs or standard monospace `.bdf`  

### 5. Sample Strings
- ASCII: `!@#$%^&*()[]{};:'",.<>?/\|`  
- Box drawing: `█ ▓ ▒ ░ ▌ ▐ ▀ ▄ ┌ ┐ └ ┘ ─ │ ┼`  
- UI Layout: `THE QUICK BROWN FOX JUMPS OVER 1234567890`  

---

## 🧩 UI Concept (ASCII Mockup)

```
┌───────────────────────── FONT EDITOR ─────────────────────────┐
│ Glyph: "A" (U+0041)   Grid: 16×16   uCELL Size: 256×256       │
│                                                             │
│   █      ██                                                 │
│   █     █  █                                                │
│   ████  █  █                                                │
│   █  █  ████                                                │
│   █  █  █  █                                                │
│                                                             │
│  [X:Draw] [_:Erase] [FlipH] [FlipV] [Overlay4×] [Export]    │
│                                                             │
│ Preview:  THE QUICK BROWN FOX JUMPS OVER 1234567890         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 File Format – uDATA JSON
Example: `uFONT-20250826-Sample.json`

```json
{
  "fontName": "uDOS Custom",
  "gridSize": "16x16",
  "baseline": 9,
  "glyphs": {
    "U+0041": [
      "00111100",
      "01000010",
      "01111110",
      "01000010",
      "01000010"
    ],
    "U+2588": [
      "11111111",
      "11111111",
      "11111111",
      "11111111",
      "11111111"
    ]
  }
}
```

---

## 🔌 Export Pipeline
1. Save as **uDATA JSON** (`uFONT-YYYYMMDD-Name.json`).  
2. Run `uCORE font export --ttf` → generates `.ttf`.  
3. Optionally export `.bdf` for X11/bitmap systems.  
4. Load into uDOS via `uCORE font install`.  

---

## 🎨 Inspiration Fonts to Support
- **Teletext/Mode 7**: via VT323, DotGothic16 templates.  
- **Apple Macintosh (1984)**: Chicago, Monaco, Geneva (use safe clones).  
- **C64**: C64 Pro Mono grid template.  
- **Block ASCII**: Terminus / box‑drawing extended set.  
- **LCD**: DSEG7 Classic grid overlay.  

---

## 📋 Roadmap

### Phase 1 – Core Editor
- [ ] 16×16 grid UI with draw/erase  
- [ ] JSON save/load  
- [ ] Preview string rendering  

### Phase 2 – Export Tools
- [ ] `.ttf` export via converter  
- [ ] `.bdf` legacy export  
- [ ] Palette testing modes  

### Phase 3 – Advanced Tools
- [ ] Overlay 4× grid (64×64)  
- [ ] Import external `.bdf` fonts  
- [ ] Box‑drawing validation checks  

### Phase 4 – Integration
- [ ] Integrate with uCORE CLI (`font generate`, `font install`)  
- [ ] Bundle with sample templates (Teletext, C64, LCD, Block ASCII)  
- [ ] Add assist‑mode help with [HELP] shortcode  

---

## 📖 References
- Apple Font Editor (1984, Susan Kare & Bill Atkinson)  
- BBC Teletext / Mode 7 (SAA5050 character set)  
- Commodore 64 PETSCII & C64 Pro Mono (OFL clone)  
- GNU Unifont / Terminus (bitmap inspiration)  

---

*uDOS Font Editor v1.0 (Design Doc)*  
*“Pixel Precision for the Post‑Terminal Age”*
