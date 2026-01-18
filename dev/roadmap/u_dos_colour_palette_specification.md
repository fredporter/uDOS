# uDOS Colour Palette Specification
**Version:** 2.0.0  
**Format:** Markdown  
**Purpose:** Terminal, editor UI, emoji, pixel art, retro desktop theming

---

## 1. Design Principles

- **Index-stable**: colours are referenced by numeric index first, name second  
- **Semantic**: colour meaning matters more than hue  
- **Emoji-safe**: core set works at ≤16×16  
- **Terminal-safe**: 16-colour subset maps cleanly to ANSI  
- **Extended-capable**: 32-colour set for modern UIs

---

## 2. Core 16-Colour Palette (Emoji / ANSI)

> This is the **canonical fallback palette**.  
> Use this for:
> - emojis  
> - terminal ANSI colours  
> - pixel icons  
> - low-colour displays

| Index | Name | Hex |
|------:|------|-----|
| 0 | Black | `#000000` |
| 1 | Dark Grey | `#333333` |
| 2 | Light Grey | `#cccccc` |
| 3 | White | `#ffffff` |
| 4 | Red (Danger) | `#dc2626` |
| 5 | Orange (Alert) | `#ff7a1a` |
| 6 | Yellow (Waypoint) | `#ffd23f` |
| 7 | Green (Grass) | `#4c9a2a` |
| 8 | Cyan (Objective) | `#00bfe6` |
| 9 | Blue (Deep Water) | `#1b4965` |
| 10 | Purple | `#6f2ed6` |
| 11 | Pink | `#ff006e` |
| 12 | Brown (Earth) | `#6b4423` |
| 13 | Sand | `#e0b984` |
| 14 | Toxic | `#2ee312` |
| 15 | Lava | `#ff4500` |

---

## 3. Extended 32-Colour Palette

> Indices **0–15** are identical to the Core palette.  
> Indices **16–31** extend the system for modern UIs.

---

### 3.1 Terrain Colours (0–7)

| Index | Name | Hex |
|------:|------|-----|
| 0 | Forest | `#2d5016` |
| 1 | Grass | `#4c9a2a` |
| 2 | Deep Water | `#1b4965` |
| 3 | Water | `#3377dd` |
| 4 | Earth | `#6b4423` |
| 5 | Sand | `#e0b984` |
| 6 | Mountain | `#4f646f` |
| 7 | Snow | `#f2f6f9` |

---

### 3.2 Marker / Signal Colours (8–15)

| Index | Name | Hex |
|------:|------|-----|
| 8 | Danger | `#dc2626` |
| 9 | Alert | `#ff7a1a` |
| 10 | Waypoint | `#ffd23f` |
| 11 | Safe | `#00e89a` |
| 12 | Objective | `#00bfe6` |
| 13 | Purple | `#6f2ed6` |
| 14 | Pink | `#ff006e` |
| 15 | Magenta | `#e91fa0` |

---

### 3.3 Greyscale Ramp (16–23)

| Index | Name | Hex |
|------:|------|-----|
| 16 | Black | `#000000` |
| 17 | Dark Grey | `#1a1a1a` |
| 18 | Charcoal | `#333333` |
| 19 | Medium Grey | `#666666` |
| 20 | Steel Grey | `#999999` |
| 21 | Light Grey | `#cccccc` |
| 22 | Off-White | `#e6e6e6` |
| 23 | White | `#ffffff` |

---

### 3.4 Accent / Special Colours (24–31)

| Index | Name | Hex | Notes |
|------:|------|-----|------|
| 24 | Skin Light | `#ffe0bd` | Extended only |
| 25 | Skin Medium | `#ffcd94` | Extended only |
| 26 | Skin Tan | `#d2a679` | Extended only |
| 27 | Skin Dark | `#8d5524` | Extended only |
| 28 | Lava | `#ff4500` | High-energy |
| 29 | Ice | `#a7c7e7` | Cool highlight |
| 30 | Toxic | `#2ee312` | Warning / hazard |
| 31 | Deep Sea | `#003366` | Depth / void |

---

## 4. Usage Rules

### Emoji & Pixel Art
- Use **Core 16 only**  
- Prefer **solid fills**  
- Optional 1px outline: `#000000` or `#333333`

### Terminal / ANSI
- Map ANSI 0–15 → Core 16 indices  
- Allow 256-colour / true-colour to access full 32

### UI / Editor Backgrounds
- Prefer **Terrain + Greyscale**  
- Use **Markers sparingly** for focus and alerts

### Accessibility
- Do not rely on colour alone for meaning  
- Core 16 is colour-blind safe by design

---

## 5. Stability Guarantees

- Index numbers are **API-stable**  
- Hex values may be refined **without changing index**  
- New colours must be added **only beyond index 31**

