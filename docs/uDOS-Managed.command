# uDOS Display Ethos v1.3.1 – 16×16 Grid Reference

A practical, copy‑pasteable reference for building uDOS UIs with **16×16 u‑cells**, **monosort fonts**, **edge‑to‑edge block graphics**, and the **4× overlay (64×64 effective)** system. All examples are plain Markdown/ASCII so they travel cleanly.

---

## 1) Quick Specs

- **u‑cell**: 16×16 (square)
- **Text box**: 12×12, centred in cell (2 px buffer each side)
- **Baseline**: row 9 of 16
- **Block fills**: edge‑to‑edge (ignore buffer) → no gaps between tiles
- **Overlays**: optional high‑detail 64×64 per cell (4× overlay grid)
- **Layers**: Light / Dark / Colour / Transparent (L/D/C/T)
- **Alignment**: monosort glyphs centred in the 12×12 text box

```
16×16 u‑cell (outer)        12×12 text box (overlay zone)
┌────────────────┐          ┌──────────────┐
│                │  buffer  │              │
│                │ ◀─2 px─▶ │              │
│                │          │              │
│                │          │              │
└────────────────┘          └──────────────┘
```

---

## 2) Core Display Sizes

Effective resolution = `(cols × 16) × (rows × 16)`.

| Grid (cols×rows) | Effective px | Device class |
|------------------|--------------|--------------|
| 160×60           | 2560×960     | Wallboard |
| 120×48           | 1920×768     | Large Dashboard |
| 80×30            | 1280×480     | Standard Terminal (16:9) |
| 64×24            | 1024×384     | Small Screen (16:9) |
| 48×20            | 768×320      | Tablet (4:3) |
| 40×16            | 640×256      | Mobile (16:9) |
| 32×24            | 512×384      | Compact 4:3 |
| 16×16            | 256×256      | Wearable (Square) |

### Aspect Ratios
- **16:9** → 80×30, 64×24, 40×16
- **4:3** → 48×20, 32×24
- **Square** → 16×16
- **Ultrawide / Wallboard** → 160×60, 120×48

> Orientation: Horizontal default; Square supported; Vertical not supported (yet – turn your phone!! 😂)

---

## 3) Visual Cheatsheet

### 3.1 ASCII Mini‑Grids

```
160×60 (Wallboard)
[■■■■■■■■■■■■■■■■■■■■■■■■]

120×48 (Large Dashboard)
[■■■■■■■■■■■■■■■■]

80×30 (Standard Terminal)
[■■■■■■■■]

64×24 (Small Screen)
[■■■■■■]

48×20 (Tablet)
[■■■■]

40×16 (Mobile)
[■■■]

32×24 (Compact 4:3)
[■■]

16×16 (Wearable)
[■]
```

Relative proportions are shown schematically. Each block (`■`) is a placeholder for 1 grid unit.

---

## 4) Block Graphics & Shading

Use Unicode block characters for fills and shading. These **ignore the buffer** so tiled areas have **no visible seams**.

- **░ Light**
- **▒ Medium**
- **▓ Heavy**
- **█ Solid**
- **▀** upper half, **▄** lower half, **▌** left half, **▐** right half
- **▘ ▝ ▖ ▗** quarter blocks (TL/TR/BL/BR)

### 4.1 Palette Table
```
BASE  │  LAYER L        │  LAYER D        │  LAYER C        │  LAYER T
──────┼─────────────────┼─────────────────┼─────────────────┼────────────────
░     │ [░: ] [░:A]     │ [░: ] [░:5]     │ [░: ] [░:#]     │ [░: ]
▒     │ [▒: ] [▒:A]     │ [▒: ] [▒:5]     │ [▒: ] [▒:#]     │ [▒: ]
▓     │ [▓: ] [▓:A]     │ [▓: ] [▓:5]     │ [▓: ] [▓:#]     │ [▓: ]
█     │ [█: ] [█:A]     │ [█: ] [█:5]     │ [█: ] [█:#]     │ [█: ]
```

---

## 5) 4× Overlay (64×64 effective)

Inside one 16×16 cell, enable a **4×4 overlay grid** (each subcell = 16×16 logical px) to draw crisp icons or dithered fills.

### Example: 64×64 heart
```
....████....████....
..████████████████..
.██████████████████.
.██████████████████.
..████████████████..
...██████████████...
....████████████....
.....██████████.....
......████████......
.......██████.......
........████........
.........██.........
```

---

## 6) UI Building Blocks

### Button
```
┌────────────────────────────────┐
│        C O N T I N U E ▷       │
└────────────────────────────────┘
```

### Input field
```
┌──────────────────────────────────┐
│  U s e r n a m e :  _ _ _ _ _    │
└──────────────────────────────────┘
```

### Pill badge
```
╭───────────────────╮
│     O N L I N E   │
╰───────────────────╯
```

---

## 7) Fonts

### Bundled pixel/retro fonts
- MODE7GX0.TTF
- pot_noodle.ttf
- Pet Me 64
- Perfect DOS VGA 437
- Pixel Operator
- DotGothic16
- GNU Unifont
- Valova

### System monospace fallbacks
- **macOS**: Menlo, SF Mono
- **Linux/Ubuntu**: Ubuntu Mono, DejaVu Sans Mono
- **Windows/Chrome**: Consolas, Courier New

### Demo string
```
AaBb CcDd EeFf GgHh IiJj KkLl MmNn
N o w  i s  t h e  t i m e  1 2 3 4 5 ! ? # $ %
```

---

## 8) Mode 7 Mapping Notes

- Teletext cells = rectangular (2×3 mosaics).
- To preserve **square look**:
  - Duplicate columns (widen output), or
  - Duplicate rows (shorten aspect).

```
Square (16×16)  →  Mode7 (2×3)  ≈  column/row duplication
```

---

## 9) Accessibility Notes

- Use high contrast overlay text vs. ▓/█.
- Provide labels for icon‑only elements.
- Keep buttons/input to **16 px height** for predictability.

---

**uDOS Display Ethos v1.3.1 establishes a consistent, scalable, and extensible model across wallboards, dashboards, terminals, tablets, mobiles, and wearables.**

