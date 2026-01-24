# uDOS Spatial & Text Graphics — Complete Brief

This document consolidates and locks the spatial addressing, layer model, text graphics model, and rendering principles for uDOS, based on the current project state.

---

## 1. Core Design Principles

- **Text-first**: All primary representations must work in plain text and Markdown.
- **Sparse world**: The address space is vast, but only explicitly authored or discovered locations exist.
- **Fractal addressing**: Precision increases by subdivision, not by plotting finer grids.
- **Human + machine harmony**: Readable paths for humans, compressed canonical IDs for machines.
- **Retro-correct**: Embrace chunky graphics, grid snapping, and terminal realities.

---

## 2. Character & Graphics Model

### 2.1 Canonical Graphics Encoding

- Canonical format uses **Unicode BLOCK SEXTANT characters** (2×3 mosaics).
- Stored and displayed inside Markdown fenced code blocks.
- Each sextant cell represents **2×3 square subpixels** in the frontend renderer.

### 2.2 Fallback Ladder

```
Sextant → Quadrant → Shades → ASCII
```

- **Quadrant**: Unicode quadrant/half blocks (preferred pretty skin)
- **Shades**: ░ ▒ ▓ █ (density-based)
- **ASCII**: . : # @ (last resort)

### 2.3 Tile Pixel Geometry

- Canonical Tile size: `16 × 24` pixels
- Pixel = 5-bit palette index (0–31)
- Pixels exist only *inside* a tile

### 2.4 Wide Glyphs / Emoji

- Glyph display width is defined by terminal `wcwidth` (1 or 2)
- Width-2 glyphs (emoji) occupy **2×1 tiles**
- Emoji/Object/Sprite wide footprint:
  - `32 × 24` pixels (2 tiles × 1 tile)

---

## 3. Viewports, Layers & Columns

### 3.1 Viewports

- **Standard Viewport / Layer Grid**: `80 × 30`
- **Mini Viewport**: `40 × 15`

Layers always use `80 × 30`; viewports may be smaller windows into them.

### 3.2 Margins & Columns

- Right margin: **2 characters**
- Content width (standard): `78`

Allowed column widths:
- `12` chars
- `24` chars (default)

Typical layouts:
- `3 × 24`
- `2 × 24 + 2 × 12`
- `6 × 12`

---

## 4. Finite Real-World Layer Bands

uDOS uses a **finite collection** of real-world precision layers, expressed as `L###`.

### 4.1 Surface (SUR)

```
SUR: L300–L305
```

- Precision increases as L increases
- 6 layers total
- `L305` provides ~front-door (~3m) accuracy

### 4.2 Upside Down (UDN)

```
UDN: L299–L294
```

- Precision increases as L decreases ("upside down")
- Same number of precision steps as SUR
- Anchored to the same real-world locations

### 4.3 Subterranean (SUB)

- Uses lower L ranges (e.g. `L293` and below)
- Infinite depth expressed via suffixes (not new layers)

---

## 5. Grid Geometry & Cell Encoding

### 5.1 Grid Size

```
LayerGrid = 80 × 30   (Columns × Rows)
```

### 5.2 Cell Format

```
Cell := Col Row
Example: AA10
```

### 5.3 Columns (Strict Pairs)

- Two uppercase letters
- Fixed-width, no Excel rollover

Mapping:
```
AA = 0
AB = 1
...
DC = 79
```

### 5.4 Rows (Offset Decimal)

- Two-digit decimal
- Rows start at **10**

```
10–39  → 30 rows total
```

Internal normalisation:
```
rowIndex = rowValue - 10
```

---

## 6. Fractal Addressing & Zoom

### 6.1 Address Grammar

```
Address := L{BaseLayer}-{Cell}(-{Cell})*
```

Each additional `-Cell` represents a zoom into a child 80×30 grid.

### 6.2 Canonical Identity (Compressed)

All addresses normalise to:

```
L{EffectiveLayer}-{FinalCell}
```

Where:
```
EffectiveLayer = BaseLayer + Depth
Depth = number of Cell segments
```

### 6.3 Spatial Equivalence

```
L300-AC10-EA12-BB21-AB32-DA11
≡ L305-DA11
```

Paths are narrative; canonical IDs are destinations.

---

## 7. Sparse World Model

- The address space is infinite; storage is sparse
- If no data exists at a location, it is implicitly EMPTY
- Tiles/objects are allocated only when:
  - authored
  - discovered
  - resolved from a code
  - created by a script

No pre-generation of tiles ever occurs.

---

## 8. GPS & Flat Map Integration

### 8.1 Projection

- Uses **Web Mercator** (flat map)
- Lat/long is internal only; users never see it

### 8.2 Mapping Rule

- Earth is subdivided recursively into 80×30 grids
- SUR/UDN precision depth determines subdivision level
- Conversion:
  - `lat/long → L{EffectiveLayer}-{Cell}`
  - `L{EffectiveLayer}-{Cell} → lat/long bounds`

This enables GPS, BLE, NFC, and mesh proximity integration without changing the grid model.

---

## 9. Computed Sky View

Sky is **not** a stored space or layer.

```
SKY( SURF:L{EffectiveLayer}-{Cell}, time )
```

- Derived from location + time
- Produces:
  - sextant/ASCII sky tiles
  - visible stars/planets
  - rise/set metadata

---

## 10. Transport & Compression (Summary)

- **PrettyPath**: Human-readable, narrative
- **Canonical ID**: `L{EffectiveLayer}-{Cell}`
- **@P**: Packed, reversible
- **@S**: Sealed, offline-decryptable
- **@R**: Resolved, online lookup

All ultimately resolve to the canonical ID.

---

## Status

This brief represents the **current locked design baseline** for uDOS spatial computing and text graphics. Future work builds on this without altering core geometry or semantics.


---

## 11. Tile Taxonomy

A **Tile** is the smallest addressable unit of authored content in uDOS. Tiles exist at **grid-cell resolution** and are anchored to a canonical location:

```
LocId := L{EffectiveLayer}-{Cell}
```

Tiles may exist in one or more **spaces**:

```
Space ∈ { SUR, UDN, SUB }
```

Pixels, palettes, sprites, and emoji are **internal to the Tile** and do not affect world coordinates.

---

### 11.1 Common Tile Properties (All Tile Types)

```yaml
tile:
  id:        <string>           # stable identifier
  loc:       <LocId>            # canonical location
  space:     SUR | UDN | SUB
  footprint: WxH                # in grid cells (default 1x1)
  tilePx:    16x24               # internal pixel resolution
  palette:   5bit (0–31)
```

**Footprint rules**
- Default footprint: `1x1`
- Wide footprint (emoji, hero sprites, objects): `2x1`
- Future expansion allowed (`2x2`, etc.)
- Footprints are always integer-aligned to the grid

---

### 11.2 Object Tile (Static)

**Purpose**: Represents a static thing at a location.

Examples:
- chest
- sign
- landmark
- terminal
- doorway
- buried artefact (UDN)

```yaml
type: object
static: true
```

**Placement rules**
- Exists at exactly one `LocId`
- Does not animate
- May be interacted with
- Valid in `SUR`, `UDN`, and `SUB`

**Optional metadata**
```yaml
object:
  solid: true | false
  interact: true | false
  state: <string|enum>
```

**UDN extension (buried objects)**
```yaml
udn:
  depthMm: 0..3000
```

---

### 11.3 Sprite Tile (Dynamic)

**Purpose**: Represents animated or state-changing entities.

Examples:
- characters
- creatures
- animated effects
- NPCs

```yaml
type: sprite
static: false
```

```yaml
sprite:
  frames: <int>
  tickRate: <ms>
  facing: N|E|S|W|NE|...
```

**Placement rules**
- Anchored to a `LocId`
- May move between adjacent cells
- May change footprint dynamically
- Valid in `SUR` and `SUB` (rare in `UDN`)

---

### 11.4 Marker / Waypoint Tile

**Purpose**: Mapping anchors and semantic reference points.

Examples:
- navigation nodes
- region labels
- spawn points
- teleport anchors
- GPS / BLE / NFC reference points

```yaml
type: marker
visible: false   # default
```

```yaml
marker:
  name: <string>
  category: <string>
  tags: [ ... ]
```

Markers may be invisible or rendered with minimal glyphs and are often resolved by scripts rather than rendered visually.

---

### 11.5 UI Tile (Document-Linked, Deep Tile)

**Purpose**: Links spatial location to documents, data, and executable logic.

Examples:
- information panels
- terminals
- QR / NFC unlock points
- location-aware documents
- interactive maps

```yaml
type: ui
```

**Core behaviour**
- Links to a `.md` document
- Document may include:
  - front matter
  - tables
  - JSON
  - executable `.ts` code blocks

**Example front matter**
```yaml
---
tile: ui
id: INFO-DA11
loc: L305-DA11
space: SUR
footprint: 2x1
---
```

**Execution model**
- Code blocks execute in the context of the tile’s location
- APIs may query:
  - current `LocId`
  - space (`SUR`, `UDN`, `SUB`)
  - proximity
  - time
  - discovery state

This is the convergence point for QR, NFC, beacons, unlocking, and data persistence.

---

### 11.6 Tile Existence & Sparsity

- Tiles do not exist unless authored or created
- Empty cells are implicit and cost nothing
- Multiple tiles may exist at the same `LocId` across different spaces

Example:
```text
SUR:L305-DA11 → UI Tile (sign)
UDN:L305-DA11 → Object Tile (buried cache)
SUB:L305-DA11 → Marker Tile (dungeon entrance)
```

---

### 11.7 Rendering Summary

- World grid uses **cells**
- Tile internals use **pixels**
- Canonical art uses **sextant mosaics**
- Emoji and wide glyphs use **2x1 tile footprints (32x24 px)**
- ASCII is always a valid fallback


---

## 12. Worked Example — One Location, Multiple Spaces

This example demonstrates how a **single real-world location** is represented across multiple spaces using the same canonical identity.

### Canonical Location

```text
L305-DA11
```

This is the compressed, canonical identity for the location. All examples below refer to this same place.

---

## 12.1 Surface (SUR) — UI Tile (Information Panel)

**Purpose**: A public information sign at the location.

```yaml
---
tile: ui
id: INFO-DA11
loc: L305-DA11
space: SUR
footprint: 2x1
---
```

### Visual (ASCII fallback)

```
+------------------------+
|  🛈  LOCATION INFO     |
|  You are here          |
+------------------------+
```

### Visual (sextant canonical, schematic)

```
🬂🬂🬂🬂🬂🬂🬂🬂
🬂🬀🬁🬁🬁🬁🬀🬂
🬂🬁🬁🬁🬁🬁🬁🬂
🬂🬂🬂🬂🬂🬂🬂🬂
```

### Embedded logic (example)

```ts
if (LOCATION.verify("L305-DA11")) {
  OUTPUT("Welcome to DA11");
}
```

---

## 12.2 Surface (SUR) — Object Tile (Landmark)

**Purpose**: A visible, static landmark.

```yaml
tile:
  id: LANDMARK-DA11
  loc: L305-DA11
  space: SUR
  footprint: 1x1

type: object
static: true
object:
  solid: true
  interact: false
```

### Visual (ASCII)

```
  ^
 /|\
/_|_\
```

---

## 12.3 Upside Down (UDN) — Object Tile (Buried Cache)

**Purpose**: A hidden object buried below the surface, discoverable via excavation.

```yaml
tile:
  id: CACHE-DA11
  loc: L305-DA11
  space: UDN
  footprint: 1x1

type: object
static: true
udn:
  depthMm: 1200
```

### Behaviour

- Not visible from `SUR`
- Discoverable only when excavation depth ≥ 1200mm
- Shares the same canonical location as the surface tiles

---

## 12.4 Subterranean (SUB) — Marker Tile (Dungeon Entrance)

**Purpose**: A semantic anchor for a virtual dungeon level.

```yaml
tile:
  id: DUNGEON-ENTRY-DA11
  loc: L305-DA11
  space: SUB
  footprint: 1x1

type: marker
visible: false
marker:
  name: "Dungeon Entrance"
  category: "entry"
```

### Dungeon Depth Example

```text
SUB:L305-DA11:D0   # Entry level
SUB:L305-DA11:D1   # First dungeon level
SUB:L305-DA11:D7   # Deep dungeon
```

---

## 12.5 Spatial Relationship Summary

```text
SUR:L305-DA11 → UI Tile (info panel)
SUR:L305-DA11 → Object Tile (landmark)
UDN:L305-DA11 → Object Tile (buried cache @1200mm)
SUB:L305-DA11 → Marker Tile (dungeon entry)
```

All tiles:
- Share the same canonical location
- Differ only by space and metadata
- Require no additional coordinates

---

## 12.6 Key Takeaways

- One location supports multiple meanings and interactions
- Depth, not precision layers, handles burial and dungeons
- UI Tiles unify documents, logic, and place
- Sextant graphics are canonical; ASCII always works

This example should be treated as the reference pattern for future content.


---

## 13. Completion Brief — System Summary Sections

The following sections provide concise, high-level briefs for the remaining core areas of uDOS. These are intended to *complete* the conceptual `.md` document and act as orientation points for implementers, contributors, and reviewers.

---

### 13.1 Formal Schema Definitions

uDOS defines a **small, explicit set of tile schemas** that describe how content exists in space. Schemas are intentionally minimal and extensible.

- Schemas describe **structure**, not behaviour
- All schemas are serialisable (YAML/JSON)
- Behaviour is attached via scripts, not schema expansion

Each tile schema:
- declares its type (object, sprite, marker, ui)
- anchors to a canonical `LocId`
- specifies footprint and space
- allows optional, type-specific metadata

Schemas are stable contracts between:
- authored content
- runtime systems
- transport mechanisms (QR, NFC, resolved codes)

---

### 13.2 Rendering Rules & Composition

Rendering in uDOS is **cell-first, tile-based**, and deterministic.

- Layers are always rendered as `80×30` grids
- Tiles snap to integer grid cells
- Overlap is resolved by:
  1. space (SUR over UDN over SUB when viewed together)
  2. tile type (UI > Sprite > Object > Marker)
  3. explicit z-order (optional override)

Visual rules:
- Sextant mosaics are canonical
- Quadrant blocks provide the preferred pretty skin
- ASCII is always a valid fallback
- Wide glyphs (emoji) occupy `2×1` tile footprints

No rendering rule introduces new spatial coordinates.

---

### 13.3 Authoring Workflow

Authoring in uDOS is **Markdown-native** and location-aware.

Typical workflow:
1. Author creates a `.md` file
2. Front matter declares tile identity and location
3. Content is written using text, tables, and diagrams
4. Optional `.ts` blocks add executable behaviour
5. Tile is placed implicitly by its `LocId`

Key properties:
- No separate "map editor" is required
- Content and location live together
- Unplaced locations remain empty by default
- Authors can reason about space without rendering it

---

### 13.4 Runtime API Contracts

The runtime exposes a **small set of spatially-aware APIs**.

Core concepts:
- Location is always resolved to `L{EffectiveLayer}-{Cell}`
- Space (`SUR`, `UDN`, `SUB`) is contextual
- Time and proximity are first-class inputs

APIs are designed to:
- query where you are
- verify presence
- resolve nearby tiles
- react to discovery or excavation

All APIs operate on canonical identities, never raw lat/long.

---

### 13.5 Diagram & ASCII Conventions

Diagrams and flowcharts in uDOS are **text-first and transferable**.

Rules:
- Canonical diagrams must be expressible in strict ASCII
- Unicode box drawing and sextant graphics are optional skins
- All diagrams live inside fenced code blocks

Allowed primitives:
- lines: `- | +`
- arrows: `-> <- ^ v`
- boxes: `+---+`

This ensures:
- diagrams survive copy/paste
- docs render correctly everywhere
- visual meaning degrades gracefully

---

## Status: Document Complete

With these sections, the uDOS spatial and text graphics specification is conceptually complete.

- Geometry, addressing, and layers are locked
- Tile taxonomy and examples are defined
- Rendering, authoring, and runtime concerns are scoped

All further work builds *on top of this document*, not inside it.


---

## 14. Spec Sheet — ASCII / Line / Shading / Blocks → Sextant Teletext

This section defines the **character families** used for diagrams and TUI graphics, and a **canonical sextant (2×3) mapping model**. The sextant model is the authoritative bridge for Teletext-style blocks and later SVG generation.

---

### 14.1 Character Families

#### Tier 0 — Strict ASCII (portable everywhere)

**Lines & corners (diagram primitives)**

```
+  -  |  =  _
/  \
( )  [ ]  { }
< >
```

**Arrows / flow**

```
->  <-  ^  v  =>  <=
```

**Shading / density (ASCII)**

```
'  .  :  ;  *  #  @
```

#### Tier 1 — Unicode “pretty skin” (widely supported)

**Box drawing (single + double)**

```
┌ ┐ └ ┘ ─ │ ├ ┤ ┬ ┴ ┼
╔ ╗ ╚ ╝ ═ ║ ╠ ╣ ╦ ╩ ╬
```

**Shades**

```
░ ▒ ▓ █
```

**Quadrant / half blocks (Block tier, preferred)**

```
▀ ▄ ▌ ▐ █
▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟
```

---

### 14.2 Canonical Sextant Model (Teletext 2×3)

A **sextant cell** is a 2×3 occupancy mask. There are **64** possible patterns.

#### Sextant bit layout (canonical)

We number subcells left-to-right, top-to-bottom:

```
[0] [1]
[2] [3]
[4] [5]
```

A sextant pattern is a 6-bit mask:

```
mask = b0 b1 b2 b3 b4 b5
```

Where `bN ∈ {0,1}` indicates the corresponding subcell is filled.

#### Visual notation for sextant masks

We render masks in docs as:
- `█` for filled subcell
- `·` for empty subcell

Example (mask 0b100101):

```
█ ·
· █
█ ·
```

---

### 14.3 ASCII / Block → Sextant Mapping Rules

These rules define how non-sextant glyphs degrade/upgrade into sextant space.

#### 14.3.1 Density mapping (ASCII → sextant)

ASCII glyphs map by **density**, not by semantic line direction.

Suggested density ladder:

| ASCII | Density | Sextant fill count (0–6) |
|------:|:-------:|:------------------------:|
| space |   0%    | 0 |
|   .   |  ~15%   | 1 |
|   :   |  ~35%   | 2 |
|   *   |  ~55%   | 3 |
|   #   |  ~75%   | 5 |
|   @   | ~100%   | 6 |

Fill selection preference (when choosing which bits to set at a given count):
1. centre-weighted (prefer middle row first)
2. symmetric left/right when possible
3. preserve silhouette continuity across neighbours

#### 14.3.2 Line mapping (ASCII/box → sextant)

Lines are represented by setting subcells along an edge:

- Vertical stroke `|`: set left column bits `[0,2,4]` or right column `[1,3,5]` depending on alignment.
- Horizontal stroke `-`: set top row `[0,1]`, mid row `[2,3]`, or bottom row `[4,5]`.
- Corners `+` / `┌┐└┘`: set a minimal corner L-shape (two strokes meeting).

This yields a consistent conversion path:

```
ASCII/Box lines → Sextant masks → Quadrant blocks → Shades → ASCII
```

---

### 14.4 Sextant → Quadrant Downsample (Block tier)

When sextants are not available, downsample 2×3 → 2×2 using:

Sextant bits:

```
a b
c d
e f
```

Quadrant bits:

```
TL = a OR c
TR = b OR d
BL = c OR e
BR = d OR f
```

Then encode using quadrant glyphs if available, otherwise fall back to shades.

---

## 14.5 Complete Sextant Pattern Set (64 masks)

Below are **all 64 sextant masks** required by the system. These are the canonical patterns; rendering may use Unicode sextant glyphs when supported, but the mask table is the source of truth.

Legend:
- `█` = filled subcell
- `·` = empty subcell

Format:
```text
mask (hex)  mask (bin)   2×3 pattern
```

### Masks 0x00–0x0F

```
0x00  000000  · ·
              · ·
              · ·

0x01  000001  · ·
              · ·
              · █

0x02  000010  · ·
              · ·
              █ ·

0x03  000011  · ·
              · ·
              █ █

0x04  000100  · ·
              · █
              · ·

0x05  000101  · ·
              · █
              · █

0x06  000110  · ·
              · █
              █ ·

0x07  000111  · ·
              · █
              █ █

0x08  001000  · ·
              █ ·
              · ·

0x09  001001  · ·
              █ ·
              · █

0x0A  001010  · ·
              █ ·
              █ ·

0x0B  001011  · ·
              █ ·
              █ █

0x0C  001100  · ·
              █ █
              · ·

0x0D  001101  · ·
              █ █
              · █

0x0E  001110  · ·
              █ █
              █ ·

0x0F  001111  · ·
              █ █
              █ █
```

### Masks 0x10–0x1F

```
0x10  010000  · █
              · ·
              · ·

0x11  010001  · █
              · ·
              · █

0x12  010010  · █
              · ·
              █ ·

0x13  010011  · █
              · ·
              █ █

0x14  010100  · █
              · █
              · ·

0x15  010101  · █
              · █
              · █

0x16  010110  · █
              · █
              █ ·

0x17  010111  · █
              · █
              █ █

0x18  011000  · █
              █ ·
              · ·

0x19  011001  · █
              █ ·
              · █

0x1A  011010  · █
              █ ·
              █ ·

0x1B  011011  · █
              █ ·
              █ █

0x1C  011100  · █
              █ █
              · ·

0x1D  011101  · █
              █ █
              · █

0x1E  011110  · █
              █ █
              █ ·

0x1F  011111  · █
              █ █
              █ █
```

### Masks 0x20–0x2F

```
0x20  100000  █ ·
              · ·
              · ·

0x21  100001  █ ·
              · ·
              · █

0x22  100010  █ ·
              · ·
              █ ·

0x23  100011  █ ·
              · ·
              █ █

0x24  100100  █ ·
              · █
              · ·

0x25  100101  █ ·
              · █
              · █

0x26  100110  █ ·
              · █
              █ ·

0x27  100111  █ ·
              · █
              █ █

0x28  101000  █ ·
              █ ·
              · ·

0x29  101001  █ ·
              █ ·
              · █

0x2A  101010  █ ·
              █ ·
              █ ·

0x2B  101011  █ ·
              █ ·
              █ █

0x2C  101100  █ ·
              █ █
              · ·

0x2D  101101  █ ·
              █ █
              · █

0x2E  101110  █ ·
              █ █
              █ ·

0x2F  101111  █ ·
              █ █
              █ █
```

### Masks 0x30–0x3F

```
0x30  110000  █ █
              · ·
              · ·

0x31  110001  █ █
              · ·
              · █

0x32  110010  █ █
              · ·
              █ ·

0x33  110011  █ █
              · ·
              █ █

0x34  110100  █ █
              · █
              · ·

0x35  110101  █ █
              · █
              · █

0x36  110110  █ █
              · █
              █ ·

0x37  110111  █ █
              · █
              █ █

0x38  111000  █ █
              █ ·
              · ·

0x39  111001  █ █
              █ ·
              · █

0x3A  111010  █ █
              █ ·
              █ ·

0x3B  111011  █ █
              █ ·
              █ █

0x3C  111100  █ █
              █ █
              · ·

0x3D  111101  █ █
              █ █
              · █

0x3E  111110  █ █
              █ █
              █ ·

0x3F  111111  █ █
              █ █
              █ █
```

---

### 14.6 Optional: Unicode Sextant Glyph Binding

When the host environment supports Unicode sextant glyphs, implementations may provide a lookup:

- `mask (0..63) → glyph`

The mask table above remains canonical; glyph binding is an implementation detail that may vary by font/terminal support.

