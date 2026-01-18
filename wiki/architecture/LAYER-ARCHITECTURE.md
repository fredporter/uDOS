# uDOS Layer Architecture (v1.0.0.56)

## Overview

uDOS uses a **fractal grid system** where each 60×20 tile layer represents a different realm of existence. Layers connect seamlessly (top↔bottom, left↔right) creating a toroidal topology - not flat, but wrapped.

All layers **vertically align**: a tile at coordinate `BD14` on Earth Surface (layer 300) directly corresponds to `BD14` on Subterranean (200), Dimensions (400), etc. This enables coherent traversal between realms.

**Zoom Depth**: SUBTERRANEAN, EARTH, and DIMENSIONS all support 3-level zoom for front-door precision (3.1m). Other realms support 1-level zoom (11km).

---

## Universe Layer Map (000-799)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        uDOS UNIVERSE LAYERS                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  700-799  GALAXY           Deep space, stars, frontiers            │
│           └── 700: Milky Way overview                              │
│           └── 710-719: Major star systems                          │
│           └── 750-799: Other galaxies, cosmic frontiers            │
│           └── Zoom: 1 level (11 km precision)                      │
│                                                                     │
│  600-699  SOLAR_SYSTEM     Moon, planets, orbit, stations          │
│           └── 600: Earth orbit overview                            │
│           └── 610: Low Earth Orbit, satellites                     │
│           └── 620: Geostationary orbit                             │
│           └── 650-659: Moon surface                                │
│           └── 660-680: Inner planets (Mercury, Venus, Mars)        │
│           └── 690-699: Outer planets, asteroids                    │
│           └── Zoom: 1 level (11 km precision)                      │
│                                                                     │
│  500-599  ATMOSPHERE       Sky, aerial, high altitude              │
│           └── 500: Ground level air                                │
│           └── 510: Low altitude (drones, birds)                    │
│           └── 530: Commercial flight altitude                      │
│           └── 550: High altitude (weather balloons)                │
│           └── 590: Edge of space (Kármán line)                     │
│           └── Zoom: 1 level (11 km precision)                      │
│                                                                     │
│  ══════════════════════════════════════════════════════════════    │
│  400-499  DIMENSIONS       ★ AR/VIRTUAL OVERLAY ★                  │
│           └── 400: Base virtual dimension                          │
│           └── 410-419: Augmented reality layers                    │
│           └── 450-499: Parallel dimensions (gameplay)              │
│           └── Zoom: 3 levels (3.1 m precision) ★                   │
│  ══════════════════════════════════════════════════════════════    │
│                                                                     │
│  ══════════════════════════════════════════════════════════════    │
│  300-399  EARTH            ★ BASE REALITY - REAL WORLD ★           │
│           └── 300: World overview (1 tile ≈ 668 km)                │
│           └── 310: Continental (zoom level 1)                      │
│           └── 320-390: Reserved for layer-based zoom               │
│           └── Zoom: 3 levels (3.1 m precision) ★                   │
│           └── Address: L300:BD14:AA10:BB15:CC20 = front door       │
│  ══════════════════════════════════════════════════════════════    │
│                                                                     │
│  ══════════════════════════════════════════════════════════════    │
│  200-299  SUBTERRANEAN     ★ UNDERGROUND ★                         │
│           └── 200: Shallow underground (basements, tunnels)        │
│           └── 220: Metro systems, sewers                           │
│           └── 250: Deep mines                                      │
│           └── 280: Deep geological                                 │
│           └── Zoom: 3 levels (3.1 m precision) ★                   │
│  ══════════════════════════════════════════════════════════════    │
│                                                                     │
│  100-199  DUNGEONS         Tutorial/learning (procedural)          │
│           └── 100-109: Tutorial levels (very easy)                 │
│           └── 110-129: Beginner dungeons (easy)                    │
│           └── 130-149: Intermediate dungeons (medium)              │
│           └── 150-169: Advanced dungeons (hard)                    │
│           └── 170-189: Expert dungeons (very hard)                 │
│           └── 190-199: Legendary dungeons (extreme)                │
│           └── Zoom: 1 level (11 km precision)                      │
│                                                                     │
│  000-099  SYSTEM           Reserved for system operations          │
│           └── 000: System root/boot                                │
│           └── 010-019: Memory/cache                                │
│           └── 050-099: Debug/diagnostic layers                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Precision Trio (Vertical Alignment)

The same address in SUBTERRANEAN, EARTH, and DIMENSIONS refers to the
same physical Earth location:

```
L200:BD14:AA10:BB15:CC20  = 3.1m underground at THIS spot
L300:BD14:AA10:BB15:CC20  = 3.1m on surface at THIS spot
L400:BD14:AA10:BB15:CC20  = 3.1m AR marker at THIS spot
```

Use cases:
- Buried time capsule: Mark in SUBTERRANEAN, visible when standing above in EARTH
- AR game: Place virtual item in DIMENSIONS, aligned with physical location
- Underground infrastructure: Map pipes/cables with surface reference

---

## Grid Topology: Wrapped Not Flat

Each layer is a **60×20 torus**:

```
        ┌──────────────────────────────────────────────────────────────┐
        │  CH10 ←────────────────────────────────────────────→ AA10   │
        │    ↑                                                    ↑    │
        │    │        Layer wraps horizontally (left↔right)       │    │
        │    │        Layer wraps vertically (top↔bottom)         │    │
        │    ↓                                                    ↓    │
        │  CH29 ←────────────────────────────────────────────→ AA29   │
        └──────────────────────────────────────────────────────────────┘

Walking off east edge (CH__) → appears on west edge (AA__)
Walking off south edge (__29) → appears on north edge (__10)
```

**Result**: No "edge of the world" - continuous navigation in all directions.

---

## Vertical Alignment (Layer Stacking)

All layers share the same coordinate grid. Tile `BD14` exists on every layer:

```
                    Layer 800 (Galaxy)      BD14 = Our solar system location
                         ↑
                    Layer 700 (Solar)       BD14 = Earth's position
                         ↑
                    Layer 600 (Near Space)  BD14 = Above Earth surface
                         ↑
                    Layer 400 (Atmosphere)  BD14 = Sky above location
                         ↑
             ═══════════════════════════════════════════════════
                    Layer 300 (Earth)       BD14 = Physical location ★
             ═══════════════════════════════════════════════════
                         ↓
                    Layer 200 (Underground) BD14 = Below location
                         ↓
                    Layer 100 (Dungeon)     BD14 = Dungeon entrance
```

**Why this matters**:
- Stairs/elevators connect same coordinate across layers
- Buildings extend from 300 (ground) through 200 (basement) and 360+ (floors)
- Caves discovered at 200 align with surface features at 300
- Space coordinates align with Earth positions for astronomical accuracy

---

## Traversal Mechanics

### 1. Walking (Same Layer)
Standard movement between adjacent tiles on the same layer.

```
L300:BD14 → L300:BD15  (walk east)
L300:BD14 → L300:BC14  (walk west)
```

### 2. Stairs/Elevators (Layer Transition)
Move between layers at the **same coordinate**.

```
L300:BD14 → L200:BD14  (stairs down to underground)
L300:BD14 → L400:BD14  (elevator up to roof/atmosphere)
```

**Stair Types**:
| Type | Layers | Example |
|------|--------|---------|
| Basement stairs | 300↔200 | House basement |
| Cave entrance | 300↔200 | Natural cave |
| Mine shaft | 300↔200-280 | Deep mine |
| Building stairs | 300↔360+ | Multi-story building |
| Dungeon entrance | 300↔100 | Special portal |
| Space elevator | 300↔600 | Mega structure |

### 3. Horizontal Teleport (Same Layer)
Instant transport between two tiles on the **same layer**.

```
L300:BD14 ══════════════════════════> L300:CG28
     (teleport pad A)                (teleport pad B)
```

**Use cases**:
- Fast travel between cities
- Linked portal networks
- Emergency evacuation

### 4. Vertical Teleport / Waypoints (Layer Jump)
Instant transport to **same tile on different layer**.

```
L300:BD14 ══════════════════════════> L500:BD14
  (real world)                    (virtual dimension)
```

**Use cases**:
- Dimensional shift (reality → virtual)
- Orbital ascent (surface → space station)
- Deep dive (surface → deep underground)

---

## Waypoint System (Checkpoints)

Waypoints are **persistent locations** that serve as:
- Save points / checkpoints
- Fast travel destinations
- Community gathering spots

### Linking to Real-World POIs

Like Pokémon GO's PokéStops, waypoints can be anchored to:

| Real-World Feature | Waypoint Type | Benefits |
|--------------------|---------------|----------|
| Monuments/Statues | Heritage Point | History XP, community events |
| Parks | Nature Point | Rest bonus, nature quests |
| Libraries | Knowledge Point | Skill training, knowledge access |
| Community Centers | Social Point | Trading, team activities |
| Transit Hubs | Transit Point | Fast travel network |
| Historic Sites | Quest Point | Special storylines |

### Waypoint Data Structure

```json
{
  "waypoint_id": "wp_bd14_monument",
  "name": "Victory Monument",
  "type": "heritage",
  "coordinates": {
    "cascading": "L300:BD14-CG15-BT21",
    "lat": 51.5074,
    "lon": -0.1278
  },
  "layers": [300, 500],  // Available on Earth + Virtual
  "features": {
    "fast_travel": true,
    "checkpoint": true,
    "community_space": true,
    "quest_giver": "monument_guardian"
  },
  "real_world_poi": {
    "osm_id": 123456789,
    "type": "monument",
    "name": "Nelson's Column"
  }
}
```

### Community Contribution

Users can **propose new waypoints** at real-world locations:
1. Visit physical location
2. Submit waypoint proposal with photo/description
3. Community votes on additions
4. Approved waypoints added to global map data

---

## Scale Reference (Earth Layers)

| Layer | Zoom Level | Tile Size | Coverage | Detail |
|-------|------------|-----------|----------|--------|
| 300 | L0 | ~600km | Global | Continents |
| 310 | L1 | ~60km | Continental | Countries/regions |
| 320 | L2 | ~6km | Regional | Cities |
| 330 | L3 | ~600m | City | Districts/blocks |
| 340 | L4 | ~60m | Neighborhood | Streets/buildings |
| 350 | L5 | ~6m | Block | Individual structures |
| 360 | L6 | ~0.6m | Building | Rooms/areas |

**Zoom Factor**: 10× per level (configurable via `EARTH_ZOOM_FACTOR`)

---

## Space Layer Accuracy

Space layers maintain **accurate relative positions**:

### Solar System (700-799)
```
Layer 730 (Mars):
- Tile BD14 on Mars corresponds to the same angular position
  as BD14 on Earth, adjusted for Mars topology
- Mars grid: 60×20 tiles covering 360°×180° of Mars surface

Layer 740 (Jupiter):
- Same coordinate system scaled to Jupiter's dimensions
- Accurate moon positions (Io, Europa, Ganymede, Callisto)
```

### Galaxy (800-899)
```
Layer 800 (Milky Way):
- Tile BD14 = Solar system's position in galaxy
- Each tile represents ~1000 light-years
- Accurate arm positions (Orion Arm for Sol)

Layer 850+ (Other Galaxies):
- Andromeda, Triangulum, etc.
- Same tile-to-coordinate mapping
- Distances accurate to astronomical data
```

---

## Pregenerated Content

### Dungeons (100-199)
| Range | Difficulty | Floors | Features |
|-------|------------|--------|----------|
| 100-109 | Tutorial | 5 | Hand-crafted, teaching mechanics |
| 110-129 | Easy | 10 | Simple layouts, weak enemies |
| 130-149 | Medium | 15 | Branching paths, traps |
| 150-169 | Hard | 20 | Complex puzzles, strong enemies |
| 170-189 | Very Hard | 25 | Labyrinths, boss battles |
| 190-199 | Legendary | 30+ | Epic challenges, rare rewards |

### Earth Data (300-399)
- **L300**: Full world coverage (pregenerated)
- **L310-320**: All continental/regional data
- **L330+**: Major cities pregenerated, rural areas procedural

### Space Data (600-899)
- **L600**: Earth orbital objects (ISS, satellites)
- **L650**: Complete Moon surface mapping
- **L700-780**: All major planets/moons in Sol system
- **L800**: Milky Way structure with accurate arm positions
- **L850+**: Major nearby galaxies

---

## Implementation Notes

### Coordinate Functions (from grid.py)
```python
from core.constants.grid import (
    tile_to_coord,           # (col, row) → "BD14"
    coord_to_tile,           # "BD14" → (col, row)
    latlong_to_cascading,    # (lat, lon, depth) → "L300:BD14-CG15"
    cascading_to_latlong,    # "L300:BD14-CG15" → (lat, lon)
    Realm,                   # Enum of layer realms
    EarthZoom,               # Earth zoom level enum
)
```

### Layer Traversal Helpers (planned)
```python
def can_traverse(from_layer: int, to_layer: int, coord: str) -> bool:
    """Check if traversal exists between layers at coordinate."""
    pass

def find_waypoints(layer: int, coord: str, radius: int = 5) -> List[Waypoint]:
    """Find nearby waypoints on a layer."""
    pass

def teleport_destinations(from_coord: str, layer: int) -> List[str]:
    """Get available teleport destinations from a tile."""
    pass
```

---

*Document Version: 1.0.0.51*
*Last Updated: 2026-01-06*
