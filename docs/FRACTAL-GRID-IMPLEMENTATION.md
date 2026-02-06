# Fractal Grid + Universe Mapping — Implementation Guide

**Status:** ✅ COMPLETE (v1.3.4)  
**Date:** 2026-02-05  
**Author:** uDOS Development

---

## Overview

This document describes the completed implementation of the **Anchor Registry** and **LocId Parser** systems for uDOS v1.3.4, as specified in [docs/v1-3 UNIVERSE.md](../v1-3%20UNIVERSE.md) and [docs/ROADMAP-STATUS.md](../ROADMAP-STATUS.md).

The system provides:
- **Canonical coordinate identity** via LocId (e.g., `L305-DA11`)
- **Place references** linking anchors, spaces, and locations (e.g., `EARTH:SUR:L305-DA11:D7:Iwinterhoff`)
- **Anchor registry** managing coordinate frame definitions and transforms
- **Layer validation** and band semantics (terrestrial, regional, stellar, etc.)
- **Cross-platform consistency** (TypeScript + Python implementations)

---

## Architecture

### Core Modules

```
core/src/spatial/
  ├── types.ts              # TypeScript interfaces
  ├── anchors.ts            # Anchor type definitions & stubs
  ├── parse.ts              # LocId, PlaceRef, AddressPath parsers
  ├── registry.ts           # AnchorRegistry + JSON loader (NEW)
  ├── validation.ts         # Layer bands, place validation (NEW)
  ├── grid_canvas.ts        # Grid rendering stubs
  ├── schema.sql            # SQLite schema for persistence
  ├── anchors.default.json  # Default anchor definitions
  ├── README.md             # Spatial module guide
  ├── tests.ts              # Comprehensive test suite (NEW)
  └── index.ts              # Module exports (UPDATED)

wizard/services/
  ├── spatial_parser.py     # Python parsing helpers
  └── anchor_registry.py    # Python AnchorRegistry implementation (NEW)
```

---

## Key Components

### 1. LocId Parser

**Purpose:** Parse and validate canonical location identifiers.

**Format:** `L###-CELL` where:
- `###` = effective layer (300-899)
- `CELL` = grid cell (2 letters + 2 digits, rows 10-39)

**Examples:**
```
L305-DA11   (layer 305, cell DA11)
L610-AB22   (layer 610, cell AB22)
L899-ZZ39   (layer 899, cell ZZ39)
```

**Implementation:** [core/src/spatial/parse.ts#parseLocId](../../core/src/spatial/parse.ts)

```typescript
import { parseLocId } from "@udos/spatial";

const locId = parseLocId("L305-DA11");
// { locId: "L305-DA11", effectiveLayer: 305, finalCell: "DA11" }
```

### 2. PlaceRef Parser

**Purpose:** Parse full place references including anchor, space, location, and optional depth/instance.

**Format:** `<ANCHOR>:<SPACE>:<LOCID>[:D<depth>][:I<instance>]`

**Anchors:**
- `EARTH` - Real-world surface
- `BODY:<name>` - Planets/moons (e.g., `BODY:MARS`, `BODY:MOON`)
- `GAME:<name>` - Virtual worlds (e.g., `GAME:SKYRIM`)
- `CATALOG:<name>` - Astronomical catalogues
- `SKY` - Computed sky (no stored locations)

**Spaces:**
- `SUR` - Surface/overworld
- `UDN` - Inverted/hidden layer
- `SUB` - Dungeons/interiors/instances (supports depth)

**Examples:**
```
EARTH:SUR:L305-DA11
EARTH:SUB:L305-DA11:D7
BODY:MARS:SUR:L610-AB22
GAME:skyrim:SUB:L402-CC18:Iwinterhoff
```

**Implementation:** [core/src/spatial/parse.ts#parsePlaceRef](../../core/src/spatial/parse.ts)

```typescript
import { parsePlaceRef } from "@udos/spatial";

const place = parsePlaceRef("EARTH:SUB:L305-DA11:D7");
// { anchorId: "EARTH", space: "SUB", locId: "L305-DA11", depth: 7 }
```

### 3. AddressPath Parser

**Purpose:** Parse narrative paths that compress to canonical LocIds.

**Format:** `L{BaseLayer}-{Cell}(-{Cell})*`

**Example:**
```
L300-AC10-BB20-DA11
→ baseLayer: 300
→ cells: ["AC10", "BB20", "DA11"]
→ effectiveLayer: 302 (300 + 2 steps)
→ canonicalLocId: "L302-DA11"
```

**Implementation:** [core/src/spatial/parse.ts#parseAddressPath](../../core/src/spatial/parse.ts)

### 4. Anchor Registry

**Purpose:** Manage coordinate frame definitions, transforms, and capabilities.

**Features:**
- Register anchors with metadata
- Query by ID, list all, validate existence
- Store and retrieve coordinate transforms
- Load from JSON (e.g., `anchors.default.json`)
- Global singleton for application-wide access

**Implementation:** [core/src/spatial/registry.ts](../../core/src/spatial/registry.ts)

```typescript
import { AnchorRegistry, loadAnchorsFromJSON } from "@udos/spatial";

// Create registry
const registry = new AnchorRegistry();

// Register anchors
registry.registerAnchor({
  id: "EARTH",
  title: "Earth (Web Mercator)",
  description: "Real-world surface",
  capabilities: { locidReverseLookup: true },
});

// Get anchor
const earth = registry.getAnchor("EARTH");

// List all anchors
const all = registry.listAnchors();

// Load from JSON
const data = JSON.parse(fs.readFileSync("anchors.default.json"));
const registry2 = loadAnchorsFromJSON(data);
```

**Python equivalent:** [wizard/services/anchor_registry.py](../../wizard/services/anchor_registry.py)

### 5. Layer Bands & Validation

**Purpose:** Define semantic layer ranges and validate spatial coordinates.

**Bands (v1.3):**

| Band | Range | Description |
|------|-------|-------------|
| TERRESTRIAL | L300–L305 | Human-scale surface precision |
| REGIONAL | L306–L399 | Local regions, overlays |
| CITIES | L400–L499 | City/metro overlays |
| NATIONS | L500–L599 | Nation/continent scales |
| PLANETARY | L600–L699 | Planets, moons, bodies |
| ORBITAL | L700–L799 | Solar system, orbits |
| STELLAR | L800–L899 | Stars, exoplanets, catalogues |

**Implementation:** [core/src/spatial/validation.ts](../../core/src/spatial/validation.ts)

```typescript
import { getLayerBand, LayerBand, validatePlaceRef } from "@udos/spatial";

// Get band for a layer
const band = getLayerBand(305);  // Returns LayerBand.TERRESTRIAL

// Validate place reference
const result = validatePlaceRef("EARTH:SUR:L305-DA11");
// { valid: true }

result = validatePlaceRef("EARTH:SUR:L199-DA11");
// { valid: false, error: "Layer 199 out of range..." }

// Canonicalize place
const canonical = canonicalizePlace("EARTH", "SUR", "L305-DA11", 7);
// Returns: "EARTH:SUR:L305-DA11:D7"
```

---

## Implementation Details

### TypeScript (`core/src/spatial/`)

**New Files:**
- `registry.ts` (250 LOC) — AnchorRegistry class, JSON loader, global singleton
- `validation.ts` (400 LOC) — Layer bands, place validation, utilities
- `tests.ts` (600 LOC) — Comprehensive test suite

**Updated Files:**
- `index.ts` — Export new modules

**Existing Files (no changes needed):**
- `types.ts` — Already complete
- `parse.ts` — Already complete
- `anchors.ts` — Already complete
- `schema.sql` — SQLite schema ready for use

### Python (`wizard/services/`)

**New Files:**
- `anchor_registry.py` (500 LOC) — AnchorRegistry class, validation helpers

**Existing Files (no changes needed):**
- `spatial_parser.py` — Already has parsers

---

## Usage Examples

### Basic LocId Parsing

```typescript
import { parseLocId, parseAddressPath } from "@udos/spatial";

// Parse canonical location
const loc = parseLocId("L305-DA11");
console.log(loc.effectiveLayer, loc.finalCell);  // 305, DA11

// Parse narrative path
const path = parseAddressPath("L300-AC10-BB20-DA11");
console.log(path.effectiveLayer, path.canonicalLocId);  // 302, L302-DA11
```

### PlaceRef Parsing & Validation

```typescript
import { parsePlaceRef, validatePlaceRef, describePlaceRef } from "@udos/spatial";

// Parse place reference
const place = parsePlaceRef("GAME:skyrim:SUB:L402-CC18:D3:Iwhiterun");
console.log(place.anchorId, place.depth, place.instance);
// GAME:skyrim, 3, whiterun

// Validate with anchor registry
const registry = new AnchorRegistry();
registry.registerAnchor({ id: "GAME:skyrim", title: "The Elder Scrolls V" });

const isValid = validatePlaceRef("GAME:skyrim:SUB:L402-CC18", 
  (id) => registry.validateAnchor(id)
);
console.log(isValid.valid);  // true

// Human-readable description
console.log(describePlaceRef("EARTH:SUR:L305-DA11"));
// EARTH/SUR/L305-DA11 [Human-scale surface precision...]
```

### Anchor Registry

```typescript
import { AnchorRegistry, loadAnchorsFromJSON, getGlobalRegistry } from "@udos/spatial";

// Create and populate
const registry = new AnchorRegistry();
registry.registerAnchor({
  id: "EARTH",
  title: "Earth (Web Mercator)",
  capabilities: { locidReverseLookup: true },
  config: { projection: "web_mercator" },
});

// Load from JSON
const data = {
  version: "1.3.0",
  anchors: [
    {
      anchorId: "EARTH",
      kind: "earth",
      title: "Earth",
      status: "active",
      config: { projection: "web_mercator" },
    },
  ],
};
const loaded = loadAnchorsFromJSON(data);

// Use global singleton
const global = getGlobalRegistry();
global.registerAnchor({ ... });
const anchors = global.listAnchors();
```

### Layer Validation

```typescript
import { isValidLayer, getLayerBand, listLayerBands, LayerBand } from "@udos/spatial";

// Check valid range
console.log(isValidLayer(305));   // true
console.log(isValidLayer(199));   // false
console.log(isValidLayer(900));   // false

// Get band
const band = getLayerBand(305);
console.log(band === LayerBand.TERRESTRIAL);  // true

// List all bands
const bands = listLayerBands();
for (const config of bands) {
  console.log(`${config.band}: L${config.minLayer}-L${config.maxLayer}`);
}

// Validate place with registry
const validator = (id: string) => registry.hasAnchor(id);
const result = validatePlaceRef("EARTH:SUR:L305-DA11", validator);
```

---

## Testing

### TypeScript Tests

A comprehensive test suite is included in [core/src/spatial/tests.ts](../../core/src/spatial/tests.ts):

**Test Coverage:**
- LocId parsing (valid/invalid cases)
- Cell validation (ranges, format)
- Address path parsing (single and multi-cell)
- PlaceRef parsing (all anchor types, optional tags)
- Layer validation (bands, constraints)
- Place reference validation (with anchors)
- Place canonicalization
- Anchor registry CRUD
- JSON loading
- Frontmatter normalization

**Usage:**
```bash
# Run tests (requires Node.js + ts-node or esbuild)
ts-node core/src/spatial/tests.ts
```

Expected output:
```
=== uDOS v1.3 Spatial Parsing & Registry Tests ===

Testing LocId Parser...
✓ LocId Parser tests passed
Testing Cell & Row Validation...
✓ Cell Validation tests passed
...
✅ All spatial tests passed!
```

### Python Tests

Python tests can be added to [wizard/services/tests/](../../wizard/services/tests/) following the same pattern.

---

## Migration & Integration

### Frontmatter Normalization

The system includes migration helpers for legacy `grid_locations` frontmatter:

```typescript
import { normaliseFrontmatterPlaces } from "@udos/spatial";

// Legacy format (implicit EARTH:SUR)
const legacy = {
  grid_locations: ["L305-DA11", "L305-BB20"],
};

// Normalize to v1.3 format
const normalized = normaliseFrontmatterPlaces(legacy);
// ["EARTH:SUR:L305-DA11", "EARTH:SUR:L305-BB20"]
```

### Database Integration

The [schema.sql](../../core/src/spatial/schema.sql) file defines tables for persistence:

```sql
-- Anchors: coordinate frames
CREATE TABLE anchors (
  anchor_id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  config_json TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);

-- Places: anchor + space + locid
CREATE TABLE places (
  place_id TEXT PRIMARY KEY,
  anchor_id TEXT NOT NULL,
  space TEXT NOT NULL,
  loc_id TEXT NOT NULL,
  depth INTEGER,
  instance TEXT,
  label TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  FOREIGN KEY(anchor_id) REFERENCES anchors(anchor_id),
  FOREIGN KEY(loc_id) REFERENCES locids(loc_id)
);
```

See [schema.sql](../../core/src/spatial/schema.sql) for full details.

---

## Constraints & Safety

### Layer Constraints
- **Valid range:** 300–899
- **Max depth:** 99 (SUB layers only)

### Cell Constraints
- **Format:** 2 letters + 2 digits (e.g., `DA11`)
- **Letter range:** A–Z (case-sensitive, uppercase required)
- **Digit range:** Rows 10–39 (800×30 grid standard)

### Place Validation
- Anchors must be registered before validation
- Spaces must be `SUR`, `UDN`, or `SUB`
- Depths only valid for `SUB` space
- Instance IDs can be arbitrary strings

---

## Specification References

See the specification documents for full context:

- [docs/v1-3 UNIVERSE.md](../v1-3%20UNIVERSE.md) — Fractal grid & anchor model
- [sonic/docs/specs/uDOS-Gameplay-Anchors-v1.3-Spec.md](../../sonic/docs/specs/uDOS-Gameplay-Anchors-v1.3-Spec.md) — Gameplay anchors & transforms
- [core/src/spatial/README.md](../../core/src/spatial/README.md) — Spatial module guide
- [docs/ROADMAP-STATUS.md](../ROADMAP-STATUS.md) — v1.3.4+ roadmap

---

## Phase 3 Roadmap

With Anchor Registry and LocId Parser now complete, the following tasks are enabled:

1. **UGRID Core** (v1.3.4) — Grid canvas + LocId overlays
2. **Gameplay Anchors** (v1.3.5) — AnchorTransform implementations
3. **Wizard Spatial API** (v1.3.5) — REST endpoints for place queries
4. **World Lenses** (v1.3.4+) — Godot/O3DE adapters

---

## Notes

- All parsers are zero-copy and stateless (safe for concurrent use)
- Layer band constraints are enforced at validation time
- Global registry is optional; applications can create isolated registries
- Python implementation mirrors TypeScript for cross-platform consistency
- No external dependencies required (JSON parsing uses stdlib)

---

**Status: ✅ COMPLETE** — Ready for integration into Phase 2+ systems.
