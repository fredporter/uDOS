# uDOS Font Collection

**Location:** `/public/wizard/static/fonts/`
**API:** `http://localhost:8765/api/v1/fonts/`
**Management:** Wizard Font Manager dashboard

---

## 📁 Directory Structure

```
fonts/
├── NotoColorEmoji.ttf       # Color emoji (symlink to goblin)
├── NotoEmoji-Regular.ttf    # Monochrome emoji (symlink to goblin)
└── retro/                   # Retro computing fonts
    ├── PressStart2P-Regular.ttf
    ├── apple/               # Classic Mac fonts
    │   ├── Chicago.ttf
    │   ├── ChicagoFLF.ttf
    │   ├── monaco.ttf
    │   ├── Sanfrisco.ttf
    │   ├── Los Altos.ttf
    │   └── UnifrakturCook-Bold.ttf
    ├── c64/                 # Commodore 64
    │   └── PetMe64.ttf
    ├── gaming/              # Arcade/gaming
    │   └── PressStart2P-Regular.ttf
    └── teletext/            # UK Teletext
        └── Teletext50.otf
```

---

## 🎨 Font Collections

### Modern Fonts

| Collection | Family           | Style   | Characters | Purpose                     |
| ---------- | ---------------- | ------- | ---------- | --------------------------- |
| `emoji`    | Noto Color Emoji | Regular | 50         | Smileys, animals, food      |
| `symbols`  | Unicode Symbols  | Regular | 33         | Math, arrows, shapes        |
| `box`      | Box Drawing      | Regular | 25         | Box drawing, block elements |

### Retro Computing Fonts

| Collection       | Family           | Style        | Era   | Purpose                       |
| ---------------- | ---------------- | ------------ | ----- | ----------------------------- |
| `retro-apple`    | Chicago / Monaco | Classic Mac  | 1984  | System 1-9, Mac OS Classic UI |
| `retro-c64`      | PetMe64          | Commodore 64 | 1982  | PETSCII graphics, C64 games   |
| `retro-gaming`   | Press Start 2P   | 8-bit Arcade | 1980s | Arcade games, retro UI        |
| `retro-teletext` | Teletext50       | UK Teletext  | 1974  | BBC Ceefax, mosaic graphics   |

---

## 🔧 API Usage

### List all collections

```bash
curl http://localhost:8765/api/v1/fonts/collections
```

### Get characters from a collection

```bash
curl 'http://localhost:8765/api/v1/fonts/characters/retro-apple?limit=20'
```

### Search characters

```bash
curl 'http://localhost:8765/api/v1/fonts/search?q=heart'
```

### Export collection

```bash
curl 'http://localhost:8765/api/v1/fonts/retro-c64/export?format=json'
```

---

## 📝 Character Categories

### Emoji

- `smileys` - 😀 😁 😂 😃 😄 😅 😆 😇 😉 😊
- `animals` - 🐶 🐱 🐭 🐰 🦊 🐻 🐼 🐨 🐯 🦁
- `food` - 🍎 🍊 🍌 🍇 🍓 🍉 🍑 🍒 🥝 🍅
- `activities` - ⚽ 🏀 🏈 ⚾ 🎾 🏐 🏉 🥎 🎱 🎮

### Symbols

- `math` - + - × ÷ = ≠ < > ≤ ≥
- `arrows` - ← ↑ → ↓ ↔ ↕ ⇐ ⇒ ⇔
- `shapes` - ■ □ ▲ ▼ ◆ ◇ ● ○ ★ ☆
- `symbols` - ✓ ✔ ✗ ✘

### Box Drawing

- `box` - ─ ━ │ ┃ ┌ ┏ ┐ ┓ └ ┗ ┘ ┛ ├ ┤ ┬ ┴ ┼
- `blocks` - ▀ ▄ █ ▌ ▐ ░ ▒ ▓

### Retro Computing

- `mac-symbols` - ⌘ ⌥ ⇧ ⌃ (Command, Option, Shift, Control)
- `petscii` - █ ▚ ▖ ▗ ▘ ▝ ♥ (C64 graphics)
- `gaming` - ♥ ♦ ♣ ♠ ▲ ▼ (Arcade symbols)
- `teletext` - █ ▀ ▄ ▌ ▐ ▖ ▗ (Mosaic graphics)

---

## 🎯 Use Cases

### Pixel Editor

- Use `retro-gaming` or `retro-c64` for 8-bit pixel art
- Use `box` for ASCII art frames
- Use `symbols` for UI icons

### Terminal UI

- Use `box` for borders and panels
- Use `symbols` for status indicators
- Use `retro-apple` for Classic Mac aesthetic

### Teletext Graphics

- Use `retro-teletext` for BBC Ceefax-style pages
- Combine with `box` for mosaic art
- 7-segment inspired display

### Vintage Theming

- **Classic Mac**: `retro-apple` (Chicago, Monaco)
- **C64 Nostalgia**: `retro-c64` (PetMe64)
- **Arcade**: `retro-gaming` (Press Start 2P)
- **Teletext**: `retro-teletext` (Teletext50)

---

## 📦 Font Sources

- **Noto Emoji**: Google Fonts (Apache 2.0)
- **Chicago/Monaco**: Classic Mac system fonts
- **PetMe64**: C64 PETSCII recreation
- **Press Start 2P**: Google Fonts (OFL)
- **Teletext50**: UK Teletext recreation

---

## 🔄 Migration from Goblin

**Previous location:** `/dev/goblin/public/fonts/`
**New location:** `/public/wizard/static/fonts/`
**Migration date:** 2026-01-18

Emoji fonts remain symlinked to Goblin for development compatibility.
All retro fonts copied to Wizard for production stability.

---

**Last Updated:** 2026-01-18
**Maintained by:** Wizard Server Font Manager
