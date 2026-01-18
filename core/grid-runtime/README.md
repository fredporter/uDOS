# uDOS Grid Runtime

**Version:** v1.0.0.0 (Alpha)  
**Status:** Planning (v1.0.7.0)  
**Component:** core/grid-runtime/

---

## Purpose

TypeScript runtime for **teletext grid-based spatial rendering** in uDOS.

Enables:

- Spatial addressing (L{Layer}-{Cell})
- Grid viewport rendering (80×30, 40×15)
- Sextant/fallback graphics (sextant → quadrant → shade → ASCII)
- Code block parsing (`\`\`\`teletext`, `\`\`\`grid`, `\`\`\`tiles`)
- Tile taxonomy (Object, Sprite, Marker)
- Variable interpolation in markdown scripts

---

## Architecture

```
grid-runtime/
├── src/
│   ├── geometry.ts      # Constants and tile/viewport specs
│   ├── address.ts       # Cell parsing (AA10), layer bands, addresses
│   ├── viewport.ts      # Viewport management (standard/mini)
│   ├── renderer.ts      # Sextant/fallback rendering pipeline
│   ├── parser.ts        # Code block parsing (teletext/grid/tiles)
│   ├── sprite.ts        # Sprite animation and state
│   ├── sky.ts           # Sky view computation (time + location)
│   └── index.ts         # Main exports
├── __tests__/
│   ├── geometry.test.ts
│   ├── address.test.ts
│   ├── renderer.test.ts
│   └── ...
├── package.json
├── tsconfig.json
└── README.md (this file)
```

---

## Specifications

**Locked:** [u_dos_spatial_text_graphics_brief.md](../../dev/roadmap/u_dos_spatial_text_graphics_brief.md)

### Tile Geometry

- Tile size: 16×24 pixels
- Palette: 5-bit (32 colors)
- Footprints: 1×1 (standard), 2×1 (wide/emoji)

### Viewports

- Standard: 80×30 columns × rows
- Mini: 40×15
- Content width: 78 (with 2-char margin)

### Layer Bands

- **SUR** (Surface): L300–L305 (precision increases with L)
- **UDN** (Upside Down): L299–L294 (reversed precision)
- **SUB** (Subterranean): L293+ (infinite depth)

### Grid Addressing

- Format: `AA10` (2 uppercase letters + 2 digits)
- Columns: AA (0)–DC (79)
- Rows: 10–39 (internally 0–29, offset by 10)
- Canonical: `L{BaseLayer}-{Cell}` (e.g., `L300-AA10`)
- Fractal: `L{BaseLayer}-{Cell}-{Cell}-...` (zoom levels)

### Graphics Fallback

```
Sextant (16 symbols) → Quadrant → Shade (░▒▓█) → ASCII (.:@#)
```

### Tile Types

- **Object:** Static (chest, sign, landmark)
- **Sprite:** Dynamic, animated (NPCs, creatures)
- **Marker:** Waypoint/reference (navigation nodes, spawn points)

---

## API Examples

### Parsing Addresses

```typescript
import {
  parseCell,
  parseCanonicalAddress,
  formatCanonicalAddress,
} from "@udos/grid-runtime";

// Parse cell
const cell = parseCell("AA10"); // { col: 0, row: 0 }

// Parse canonical address
const addr = parseCanonicalAddress("L300-AC15");
// { baseLayer: 300, depth: 0, cell: { col: 2, row: 5 }, band: "SUR" }

// Format back
const str = formatCanonicalAddress(addr); // "L300-AC15"
```

### Code Block Types

```typescript
interface TeletextBlock {
  type: "teletext";
  content: string; // raw sextant/ASCII grid
  variables?: Record<string, any>;
}

interface GridBlock {
  type: "grid";
  definition: any; // YAML/JSON structure
  variables?: Record<string, any>;
}

interface TilesBlock {
  type: "tiles";
  tiles: Tile[];
  manifest?: Record<string, any>;
}
```

### Tile Definition

```typescript
interface Tile {
  id: string;
  type: "object" | "sprite" | "marker";
  static: boolean;
  palette?: number[]; // 5-bit indices
}

interface SpriteTile extends Tile {
  frames: number;
  currentFrame?: number;
  facing?: "N" | "E" | "S" | "W" | ...;
}
```

---

## Integration Points

### Markdown Code Blocks

````markdown
```teletext
████████████████████████████
█ L300-AA10: Town Square     █
█                            █
█ @  M  G                    █
█                            █
████████████████████████████
```
````

````markdown
```grid
layer: 300
center: AA10
viewport: 80x30
terrain: true
sprites: true
```
````

### Variable Interpolation

````markdown
# You are at $player.pos.tile

```set
set $player.pos.tile "AA11"
```
````

Current layer: $world.layer

````

---

## Development

```bash
# Install
npm install

# Build
npm run build

# Test
npm test

# Watch
npm run dev
````

---

## Next Phases

- **Phase 2:** Sextant/fallback rendering engine
- **Phase 3:** Code block parsing in markdown
- **Phase 4:** Location parser and sparse world model
- **Phase 5:** Integration with uDOS runtime (map blocks, movement)

---

## References

- [u_dos_spatial_text_graphics_brief.md](../../dev/roadmap/u_dos_spatial_text_graphics_brief.md) — Locked specifications
- [example-script.md](../../dev/roadmap/example-script.md) — Usage examples
- [example-sqlite.db.md](../../dev/roadmap/example-sqlite.db.md) — Tile data examples

---

**Last Updated:** 2026-01-18  
**Status:** Scaffold (Phase 1 planning)
