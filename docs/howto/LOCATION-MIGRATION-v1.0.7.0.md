# Location System v1.0.7.0 Migration Guide

**Status:** v1.0.7.0 canonical format locked  
**Old Format:** v2.2.0 (480×270, 100-899 layers, various coordinate formats)  
**New Format:** v1.0.7.0 (80×30 viewport, finite layers L300-L305, AA-DC × 10-39)

---

## 🎯 Key Changes

### Grid System

| Aspect        | v2.2.0 (Old)               | v1.0.7.0 (New)                                | Notes                           |
| ------------- | -------------------------- | --------------------------------------------- | ------------------------------- |
| **Grid Size** | 480×270 cells              | 80×30 tiles                                   | Viewport-based, not world-based |
| **Columns**   | AA-RL (480)                | AA-DC (80)                                    | Letter pair encoding            |
| **Rows**      | 0-269                      | 10-39 (offset)                                | Always 2 digits                 |
| **Layers**    | 100-899 (800 layers)       | L300-L305 (SUR), L299-L294 (UDN), L293+ (SUB) | Finite, precision-based         |
| **ID Format** | `AA000-100` or `TILE CODE` | `L300-AA10`                                   | Layer-Cell always               |

### Layer Bands

| Band                   | v1.0.7.0  | Purpose                                      |
| ---------------------- | --------- | -------------------------------------------- |
| **SUR** (Surface)      | L300-L305 | Above-ground, real-world precision 3-5m      |
| **UDN** (Upside Down)  | L299-L294 | Mirror of SUR, alternate precision           |
| **SUB** (Subterranean) | L293+     | Dungeons, mines, infinite depth via suffixes |

### Address Format

```
Old:  AA000-300        (column + row + layer)
      TILE-CODE-LAYER
      L100-AA10

New:  L300-AA10        (strict: L{LAYER}-{CELL})
      L305-DC39        (max: layer 305, cell DC39)
      L293-AB20        (subterranean: unlimited layers below 293)
```

---

## 🔄 Migration Steps

### Step 1: Identify Old Format

**Old location file characteristics:**

- Uses layers 100-899 (Earth=100-399, Space=600-899, Virtual=400-599)
- Grid size 480×270
- Columns: AA-RL (or similar base-26)
- Rows: 0-269 (single digit possible)
- Multiple coordinate systems in same file

**New location file characteristics:**

- Uses only L300-L305 (SUR) + L299-L294 (UDN) + L293+ (SUB)
- Grid size 80×30 (viewport)
- Columns: AA-DC (strict)
- Rows: 10-39 (always 2 digits)
- Single unified ID format: `L{LAYER}-{CELL}`

### Step 2: Convert Coordinates

**Algorithm:**

1. **Determine base layer:**
   - If original layer 100-399 (Earth surface/near) → Use L300 (default)
   - If original layer 400-499 (Atmosphere/virtual) → Use L301-L305 (precision levels)
   - If original layer 500+ (Space/dungeons) → Document separately or move to SUB

2. **Scale coordinates (480→80, 270→30):**

   ```
   new_col = floor(old_col * 80 / 480)      # Scale from 480 to 80
   new_row = floor(old_row * 30 / 270) + 10 # Scale to 10-39 range

   Clamp to valid:
   new_col = clamp(new_col, 0, 79)
   new_row = clamp(new_row, 10, 39)
   ```

3. **Convert column to AA-DC format:**

   ```
   col_index = new_col
   first_letter = chr(ord('A') + (col_index // 26) % 26)
   second_letter = chr(ord('A') + col_index % 26)
   cell = f"{first_letter}{second_letter}{new_row:02d}"
   ```

4. **Build new ID:**
   ```
   new_id = f"L{new_layer:03d}-{cell}"
   Example: old=AA000-100 → new=L300-AA10
   ```

### Step 3: Update Location Objects

**Old format example:**

```json
{
  "name": "Sydney",
  "grid_cell": "AB340",
  "tile_code": "AB340-100",
  "layer": 100
}
```

**New format example:**

```json
{
  "id": "L300-AB10",
  "name": "Sydney",
  "kind": "landmark",
  "layer": 300,
  "cell": "AB10",
  "terrain": "stone",
  "connections": {
    "N": "L300-AB11",
    "E": "L300-AC10",
    ...
  }
}
```

**Required fields:**

- `id` — Canonical location ID (L{LAYER}-{CELL})
- `name` — Human-readable name
- `layer` — Layer number (300-305 for SUR)
- `cell` — Grid cell (AA10-DC39)

**Optional fields:**

- `kind` — Location type (landmark, town, poi, dungeon, etc.)
- `terrain` — Terrain type (grass, stone, water, forest, mountain)
- `connections` — Adjacent locations {direction → id}
- `objects` — Static objects (furniture, doors, chests)
- `sprites` — NPCs, creatures, entities
- `markers` — Quest markers, waypoints, treasures
- `metadata` — Custom data

### Step 4: Rebuild Connections

Old format often had no explicit connections. New format requires sparse adjacency graph.

**For each location:**

1. Determine valid adjacent cells (N/E/S/W/diagonals)
2. Check if adjacent cell has a location in the world
3. If yes, add to `connections`:

```json
{
  "id": "L300-AA10",
  "connections": {
    "N": "L300-AA11",
    "E": "L300-AB10",
    "S": "L300-AA09",
    "W": "L300-ZZ10"
  }
}
```

**Valid directions:** N, S, E, W, NE, NW, SE, SW

---

## 🧹 Files to Update/Remove

### Files using old formats (v2.2.0+):

1. **Goblin Dev Server** (dev/goblin):
   - `core/data/geography/cities.json` — Update to v1.0.7.0
   - `core/data/geography/terrain.json` — Update if needed
   - `core/services/location_service.py` — Convert to new grid
   - `core/services/tile_hierarchy.py` — Update layer ranges

2. **Extensions/Empire** (CRM):
   - `extensions/empire/location_resolver.py` — Update grid math
   - `extensions/empire/QUICK-REFERENCE.md` — Update examples

3. **Wizard** (Production):
   - `wizard/tools/bizintel/location_resolver.py` — Update grid math
   - `wizard/docs/` — Update coordinate examples

4. **Knowledge/Places**:
   - `knowledge/places/` — Update grid references in content

### Files that are CORRECT (v1.0.7.0):

- ✅ `/core/location-parser.ts` — Already uses L300-DC39 format
- ✅ `/core/location.schema.json` — NEW canonical schema
- ✅ `/core/location.example.json` — NEW example with correct format

---

## 🔧 Migration Script (Python)

Use this to batch-convert old location files:

```python
def migrate_location_v2_to_v1_0_7(old_location: dict) -> dict:
    """Convert v2.2.0 location to v1.0.7.0."""

    # Extract old coordinates
    old_layer = old_location.get('layer', 100)
    old_cell = old_location.get('grid_cell') or old_location.get('tile_code', '').split('-')[0]

    # Determine new layer (v1.0.7.0)
    if 100 <= old_layer <= 399:
        new_layer = 300  # Default to SUR surface
    else:
        # Document or skip
        new_layer = 300

    # Parse old cell (assume format like "AB340" or similar)
    # Convert from variable format to AA-DC, 10-39
    if len(old_cell) >= 4:
        old_col_str = old_cell[:2]
        old_row_str = old_cell[2:]
    else:
        old_col_str = "AA"
        old_row_str = "00"

    # Convert column letters to index (A=0, Z=25, AA=0, AB=1, etc.)
    col_index = (ord(old_col_str[0]) - ord('A')) * 26 + (ord(old_col_str[1]) - ord('A'))
    col_index = int(col_index * 80 / 480) % 80  # Scale to 0-79

    # Convert row to index and scale
    try:
        old_row = int(old_row_str)
    except:
        old_row = 0
    new_row = int(old_row * 30 / 270) + 10  # Scale to 10-39
    new_row = max(10, min(39, new_row))  # Clamp

    # Convert column index back to AA-DC format
    first_letter = chr(ord('A') + (col_index // 26) % 26)
    second_letter = chr(ord('A') + col_index % 26)
    new_cell = f"{first_letter}{second_letter}{new_row:02d}"

    # Build new location
    new_id = f"L{new_layer:03d}-{new_cell}"

    return {
        "id": new_id,
        "name": old_location.get('name', 'Unknown'),
        "kind": old_location.get('kind') or old_location.get('type'),
        "layer": new_layer,
        "cell": new_cell,
        "terrain": old_location.get('terrain'),
        "description": old_location.get('description'),
        "metadata": {
            "migrated_from": old_location.get('tile_code') or old_location.get('grid_cell')
        }
    }


# Usage
import json
with open('old_locations.json') as f:
    old_data = json.load(f)

new_locations = [migrate_location_v2_to_v1_0_7(loc) for loc in old_data['locations']]

print(json.dumps({"version": "1.0.7.0", "locations": new_locations}, indent=2))
```

---

## ✅ Validation Checklist

After migration:

- [ ] All location IDs match `L\d{3}-[A-Z]{2}\d{2}` pattern
- [ ] All layers in range 300-305 (SUR) or 299-294 (UDN) or ≤293 (SUB)
- [ ] All cells in range AA-DC columns, 10-39 rows
- [ ] All connections point to valid location IDs
- [ ] No duplicate location IDs
- [ ] schema validates against `core/location.schema.json`

---

## 📚 References

- **New Schema:** `core/location.schema.json`
- **Example:** `core/location.example.json`
- **Parser:** `core/location-parser.ts`
- **Brief:** `dev/roadmap/u_dos_spatial_text_graphics_brief.md`

---

_Last Updated: 2026-01-18_  
_v1.0.7.0 Migration Guide_
