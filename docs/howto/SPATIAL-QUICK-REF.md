# uDOS Spatial Quick Reference — v1.3

## LocId Format
```
L###-CELL[-Zz]
 └ L300-DA11 = Layer 300, cell DA11 (z=0 implied)
 └ L300-DA11-Z2 = Layer 300, cell DA11, z offset +2
```
- **Layer:** 300-899 (see bands below)
- **Cell:** 2 letters (A-Z) + 2 digits (10-39)
- **Optional z-axis:** -99..99 (`-Z0` optional, omitted means `z=0`)

## PlaceRef Format
```
<ANCHOR>:<SPACE>:<LOCID>[:D<depth>][:I<instance>]
 └ EARTH:SUR:L305-DA11:D7:Iwinterhoff
```

### Anchors
- `EARTH` — Real-world surface
- `BODY:<name>` — Planets/moons (e.g., `BODY:MOON`, `BODY:MARS`)
- `GAME:<name>` — Virtual worlds (e.g., `GAME:skyrim`)
- `CATALOG:<name>` — Astronomical catalogues
- `SKY` — Computed sky (read-only)

### Spaces
- `SUR` — Surface/overworld
- `UDN` — Inverted/hidden layer
- `SUB` — Dungeons/interiors (supports depth D0-D99)

### Optional Tags
- `D<n>` — Depth (for SUB only, 0-99)
- `I<id>` — Instance name (any string)

## Layer Bands (v1.3)

| Band | Range | Meaning |
|------|-------|---------|
| TERRESTRIAL | L300–L305 | Human-scale surface |
| REGIONAL | L306–L399 | Local regions |
| CITIES | L400–L499 | City/metro overlays |
| NATIONS | L500–L599 | Nation/continent |
| PLANETARY | L600–L699 | Planets, moons |
| ORBITAL | L700–L799 | Solar system |
| STELLAR | L800–L899 | Stars, exoplanets |

## TypeScript API

### Parse LocId
```typescript
import { parseLocId } from "@udos/spatial";

const loc = parseLocId("L305-DA11");
// { locId: "L305-DA11", effectiveLayer: 305, finalCell: "DA11" }

const locWithZ = parseLocId("L305-DA11-Z2");
// { locId: "L305-DA11-Z2", effectiveLayer: 305, finalCell: "DA11", z: 2 }
```

### Parse PlaceRef
```typescript
import { parsePlaceRef } from "@udos/spatial";

const place = parsePlaceRef("EARTH:SUB:L305-DA11:D7");
// { anchorId: "EARTH", space: "SUB", locId: "L305-DA11", depth: 7 }
```

### Registry
```typescript
import { AnchorRegistry } from "@udos/spatial";

const registry = new AnchorRegistry();
registry.registerAnchor({ id: "EARTH", title: "Earth" });

if (registry.hasAnchor("EARTH")) {
  const anchor = registry.getAnchor("EARTH");
}
```

### Validate Place
```typescript
import { validatePlaceRef } from "@udos/spatial";

const result = validatePlaceRef("EARTH:SUR:L305-DA11");
// { valid: true } or { valid: false, error: "..." }
```

### Layer Bands
```typescript
import { getLayerBand, LayerBand } from "@udos/spatial";

const band = getLayerBand(305);
// LayerBand.TERRESTRIAL
```

## Python API

Similar to TypeScript, available in `wizard/services/anchor_registry.py`:

```python
from wizard.services.anchor_registry import (
    AnchorRegistry,
    parse_place_ref,
    validate_place_ref,
)

registry = AnchorRegistry()
registry.register_anchor("EARTH", "Earth (Web Mercator)")

place = parse_place_ref("EARTH:SUR:L305-DA11")
result = validate_place_ref("GAME:skyrim:SUB:L402-CC18")
```

## Common Patterns

### Frontmatter (Markdown)
```yaml
---
title: My Note
places:
  - EARTH:SUR:L305-DA11
  - GAME:skyrim:SUB:L402-CC18:D3:Iwhiterun
---
```

### Feature Location
```
BODY:MARS:SUR:L610-AB22
```

### Game Instance
```
GAME:skyrim:SUB:L402-CC18:D5:Iblackreach
```

### Migration (Legacy)
```yaml
# Old format
grid_locations:
  - L305-DA11
  - L305-DA11-Z2

# New format
places:
  - EARTH:SUR:L305-DA11
  - EARTH:SUR:L305-DA11-Z2
```

## Constraints

| Item | Min | Max | Rules |
|------|-----|-----|-------|
| Layer | 300 | 899 | Integer only |
| Depth (SUB) | 0 | 99 | Integer only |
| Cell | — | — | 2 letters (A-Z), 2 digits (10-39) |
| Rows | 10 | 39 | Forms 80×30 grid |
| Z-axis | -99 | 99 | Optional vertical offset (`-Zz`) |

## Files

| File | Purpose |
|------|---------|
| `core/src/spatial/parse.ts` | LocId/PlaceRef parsers |
| `core/src/spatial/registry.ts` | AnchorRegistry implementation |
| `core/src/spatial/validation.ts` | Layer bands, place validation |
| `core/src/spatial/types.ts` | TypeScript interfaces |
| `core/src/spatial/schema.sql` | SQLite schema |
| `core/src/spatial/anchors.default.json` | Default anchor definitions |
| `wizard/services/anchor_registry.py` | Python implementation |

## See Also

- [FRACTAL-GRID-IMPLEMENTATION.md](FRACTAL-GRID-IMPLEMENTATION.md) — Full guide
- [v1-3 UNIVERSE.md](v1-3%20UNIVERSE.md) — Design specification
- [core/src/spatial/README.md](../core/src/spatial/README.md) — Spatial module guide

## TUI Z-Layer Messaging Convention

Spatial z/elevation fields are independent from TUI message theming.

- Spatial signals:
  - `LocId` optional `-Zz`
  - seed fields `z`, `z_min`, `z_max`, `stairs`, `ramps`, `portals`
- TUI message routing signals:
  - `UDOS_TUI_MAP_LEVEL=dungeon|foundation|galaxy`
  - `UDOS_TUI_MESSAGE_THEME=<theme>`

Recommended mapping:

| Spatial context | Map level |
|------|------|
| `SUB` / underground / negative z | `dungeon` |
| surface/regional traversal near base elevation | `foundation` |
| orbital/stellar traversal or high layer bands | `galaxy` |
