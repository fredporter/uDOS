# uDOS 16×16 Grid Reference

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

## 2) Block Graphics & Shading (edge‑to‑edge)

Use Unicode block characters for fills and shading. These **ignore the buffer** so tiled areas have **no visible seams**.

- **░ Light**
- **▒ Medium**
- **▓ Heavy**
- **█ Solid**
- **▀** upper half, **▄** lower half, **▌** left half, **▐** right half
- **▘ ▝ ▖ ▗** quarter blocks (TL/TR/BL/BR)

### 2.1 Palette table (with overlay slot)

```
BASE  │  LAYER L        │  LAYER D        │  LAYER C        │  LAYER T
──────┼─────────────────┼─────────────────┼─────────────────┼────────────────
░     │ [░: ] [░:A]     │ [░: ] [░:5]     │ [░: ] [░:#]     │ [░: ]
▒     │ [▒: ] [▒:A]     │ [▒: ] [▒:5]     │ [▒: ] [▒:#]     │ [▒: ]
▓     │ [▓: ] [▓:A]     │ [▓: ] [▓:5]     │ [▓: ] [▓:#]     │ [▓: ]
█     │ [█: ] [█:A]     │ [█: ] [█:5]     │ [█: ] [█:#]     │ [█: ]
```

> Syntax `[█:X]` means **fill** = `█`, **overlay glyph** = `X` (centred monosort).

### 2.2 Gradients (hierarchy)

```
[░] → [▒] → [▓] → [█]   (Light → Dark emphasis)
[█] → [▓] → [▒] → [░]   (Dark → Light fade)
```

---

## 3) 4× Overlay (64×64 effective) – Icons & detail

Inside one 16×16 cell, enable a **4×4 overlay grid** (each subcell = 16×16 logical px) to draw crisp icons or dithered fills. Text overlay still centres in the 12×12 box.

### 3.1 64×64 heart (ASCII sketch)

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

> Use `.` for empty pixels in sketches. Renderer treats them as transparent/space.

---

## 4) UI Building Blocks (copy‑paste)

### 4.1 Single‑line button (16 px high)

```
┌────────────────────────────────┐
│        C O N T I N U E ▷       │
└────────────────────────────────┘
```

- Height: **1 u‑cell** (16)
- Border: 1–2 px
- Text baseline: row 9

### 4.2 Input field

```
┌──────────────────────────────────┐
│  U s e r n a m e :  _ _ _ _ _    │
└──────────────────────────────────┘
```

### 4.3 Pill badge (rounded corners)

```
╭───────────────────╮
│     O N L I N E   │
╰───────────────────╯
```

---

## 5) Monosort Fonts – Bundled Set & Demos

All fonts below are **fixed‑width** and sit in the **12×12 text box**, centred. Block fills remain edge‑to‑edge.

### 5.1 Bundled pixel/retro fonts

- MODE7GX0.TTF (BBC Teletext clone)
- pot\_noodle.ttf (BBS/retro)
- Pet Me 64 (C64 family)
- Perfect DOS VGA 437
- Pixel Operator
- DotGothic16
- GNU Unifont (wide Unicode)
- Valova (16×16 tileset)

### 5.2 System monospace fallbacks

- **macOS**: Menlo, SF Mono
- **Linux/Ubuntu**: Ubuntu Mono, DejaVu Sans Mono
- **Windows/Chrome**: Consolas, Courier New

### 5.3 Uniform demo string (paste under any font)

```
AaBb CcDd EeFf GgHh IiJj KkLl MmNn
N o w  i s  t h e  t i m e  1 2 3 4 5 ! ? # $ %
```

> When previewing, ensure line height = 16 and letter‑spacing = fixed (no kerning) for consistent results.

---

## 6) Mode 7 Mapping Notes (when exporting)

- Teletext cells are rectangular (2×3 mosaics). To preserve **square‑pixel look**:
  - Option A (columns): duplicate every Nth column when rasterising → widens output
  - Option B (rows): duplicate rows to compensate for tall cells
- Icons: design in 16×16 or 64×64; exporter reduces to mosaics while keeping silhouette.

```
Square (16×16)  →  Mode7 (2×3)  ≈  column/row duplication to keep aspect
```

---

## 7) Implementation Cheat‑Sheet

- **Text overlay**: centre glyph inside 12×12 box (2 px padding).
- **Blocks/gradients**: draw full cell (ignore buffer) to avoid seams.
- **Overlay icons**: enable 4× (64×64) for crisp shapes; text still centres.
- **Contrast**: choose high‑contrast overlay colour against ▓/█.
- **Single‑line UI**: set line height to exactly 16 for tidy buttons.

---

## 8) Test Grid (paste and render)

### 8.1 Fill tiling (seam check)

```
████████████████████
████████████████████
████████████████████
```

### 8.2 Overlay centring check

```
[░:A] [▒:A] [▓:A] [█:A]   [▀:A] [▄:A] [▌:A] [▐:A]
[▘:A] [▝:A] [▖:A] [▗:A]
```

### 8.3 Button stack

```
┌──────────────┐
│   S T A R T  │
└──────────────┘
┌──────────────┐
│   O P T I O N│
└──────────────┘
┌──────────────┐
│      Q U I T │
└──────────────┘
```

---

## 9) Accessibility Notes

- Prefer **▓ / █** fills only when overlay text colour maintains sufficient contrast.
- For icons, provide a **text label** nearby in UI documentation.
- Keep single‑line components to **16 px height** for predictable focus outlines.

---

*End of reference.*

