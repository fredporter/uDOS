# Location System Quick Start Guide

**Fast Reference for uDOS Location System**  
**Status:** Phase 5D Complete, Ready for Integration  
**Version:** 1.0.0

---

## 30-Second Overview

The location system provides 46 playable locations across Earth and beyond, with timezone-aware operations, tile-based grids, and connection graph for navigation.

```python
from core.locations import load_locations

# Load all locations
db = load_locations()

# Get a specific location
tokyo = db.get("L300-BJ10")

# Query by region
asia_locations = db.find_by_region("asia_east")

# Get location info
print(tokyo.info())
```

---

## Quick Usage Examples

### 1. Basic Location Access

```python
from core.locations import load_locations, get_location

# Option 1: Load database once
db = load_locations()
location = db.get("L300-BJ10")

# Option 2: Quick access
location = get_location("L300-BJ10")

# Access location properties
print(location.name)          # "Tokyo - Shibuya Crossing"
print(location.timezone)      # "UTC+9"
print(location.region)        # "asia_east"
print(location.type)          # "major-city"
print(location.scale)         # "terrestrial"
print(location.coordinates)   # Coordinate(lat=35.6595, lon=139.7004)
```

### 2. Regional Queries

```python
from core.locations import load_locations

db = load_locations()

# Find all locations in a region
asia_east = db.find_by_region("asia_east")      # 11 locations
asia_south = db.find_by_region("asia_south")    # 11 locations

# Find all in a continent
asia = db.find_by_continent("Asia")

# Find by type
cities = db.find_by_type("major-city")

# Find by scale
terrestrial = db.find_by_scale("terrestrial")   # 41 locations
cosmic = db.find_by_scale("cosmic")             # 5 locations
```

### 3. Location Information

```python
location = db.get("L300-BJ10")

# Get formatted info
info = location.info()
print(info)
# Output:
# 📍 Tokyo - Shibuya Crossing
#    Region: asia_east
#    Type: major-city (metropolis)
#    Layer: 300 (terrestrial)
#    ...

# Get summary
summary = location.summary()
print(summary)
# Output: "Tokyo - Shibuya Crossing (L300-BJ10)"

# Display as string
str(location)
```

### 4. Connections and Navigation

```python
location = db.get("L300-BJ10")

# Get all connections
for conn in location.connections:
    print(f"{conn.direction}: {conn.label} → {conn.to}")

# Check if connection exists
if location.has_connection_to("L300-BK10"):
    conn = location.get_connection("L300-BK10")
    print(f"Go {conn.direction} to {conn.label}")

# Get specific connection
connection = location.get_connection("L300-BK10")
if connection:
    print(f"Direction: {connection.direction}")
    print(f"Label: {connection.label}")
```

### 5. Tiles and Grid Content

```python
location = db.get("L300-BJ10")

# Get tile at specific cell
tile = location.get_tile("AA10")
if tile:
    print(f"Objects: {len(tile.objects)}")
    print(f"Sprites: {len(tile.sprites)}")
    print(f"Markers: {len(tile.markers)}")

    # Iterate objects
    for obj in tile.objects:
        print(f"  {obj.char} {obj.label} (z={obj.z})")

    # Iterate sprites
    for sprite in tile.sprites:
        print(f"  {sprite.char} {sprite.label} (id={sprite.id})")

    # Iterate markers
    for marker in tile.markers:
        print(f"  {marker.type}: {marker.label}")

# Get all tiles
for cell_id, tile in location.tiles.items():
    print(f"{cell_id}: {len(tile.sprites)} sprites")
```

### 6. Timezone Operations

```python
from core.location_service import LocationService

service = LocationService()

# Get local time
local_time = service.get_local_time("L300-BJ10")
print(local_time)  # datetime in UTC+9

# Get formatted time
time_str = service.get_local_time_str("L300-BJ10")
print(time_str)  # "2026-01-18 15:45:32"

# Get time difference
diff = service.get_time_difference("L300-BJ10", "L300-AA10")
print(diff)  # 17 hours (Tokyo to NYC)
```

### 7. Pathfinding

```python
from core.location_service import LocationService

service = LocationService()

# Find path between locations
path = service.find_path("L300-AA10", "L300-BJ10")
if path:
    print(f"Path found: {' → '.join(path)}")
else:
    print("No path exists")

# Get connections from location
connections = service.get_connections("L300-BJ10")
for conn in connections:
    print(f"{conn['direction']}: {conn['label']} → {conn['to']}")
```

### 8. Statistics and Exploration

```python
from core.location_service import LocationService

service = LocationService()

# Get all statistics
stats = service.get_statistics()
print(f"Total locations: {stats['total']}")
print(f"Terrestrial: {stats['by_scale']['terrestrial']}")
print(f"Cosmic: {stats['by_scale']['cosmic']}")

# Count locations
total = service.count_locations()
print(f"Locations loaded: {total}")

# Get location info
info = service.get_location_info("L300-BJ10")
print(info)
```

---

## Available Locations by Region

| Region             | Count | Locations Example          |
| ------------------ | ----- | -------------------------- |
| **asia_east**      | 11    | Tokyo, Seoul, Mount Fuji   |
| **asia_south**     | 11    | Bangkok, Mumbai, Phuket    |
| **americas_north** | 11    | NYC, Toronto, Niagara      |
| **europe_north**   | 2     | London, Scottish Highlands |
| **europe_central** | 1     | Swiss Alps                 |
| **europe_south**   | 2     | Athens, Mediterranean      |
| **africa_north**   | 1     | Cairo                      |
| **africa_central** | 1     | Nairobi                    |
| **africa_south**   | 1     | Cape Town                  |
| **oceania**        | 5     | Sydney, Great Barrier Reef |
| **Cosmic**         | 5     | LEO, Mars, Alpha Centauri  |

---

## Location ID Format

```
L{layer}-{cell}

Examples:
L300-AA10      # Layer 300 (Terrestrial), cell AA10
L300-BJ10      # Layer 300 (Terrestrial), cell BJ10
L306-AA01      # Layer 306 (Low Earth Orbit)
L350-AA01      # Layer 350 (Mars)
```

### Layer Reference

| Layer | Name             | Type   | Locations |
| ----- | ---------------- | ------ | --------- |
| 300   | Terrestrial      | Earth  | 41        |
| 306   | Low Earth Orbit  | Cosmic | 1         |
| 325   | Mars             | Cosmic | 1         |
| 350   | Alpha Centauri   | Cosmic | 1         |
| 375   | Sagittarius A\*  | Cosmic | 1         |
| 401   | Andromeda Galaxy | Cosmic | 1         |

---

## Timezone Reference

All timezones represented (UTC offset from UTC):

```
UTC+0   - London, Earth Orbit
UTC+1   - Central Europe
UTC+2   - Southern Europe
UTC+5:30 - India
UTC+7   - Thailand
UTC+9   - Japan, Korea, East Australia (30 min)
UTC+10  - Sydney, East Australia
UTC+11  - Sydney (some)
UTC-5   - New York, Toronto
UTC-6   - Chicago
```

**Special Note:** UTC+5:30 (India) and UTC+9:30 (Central Australia) are fractional timezones and are fully supported.

---

## Common Patterns

### Pattern 1: Display Location Info

```python
from core.locations import load_locations

db = load_locations()
location = db.get("L300-BJ10")
print(location.info())
```

### Pattern 2: List All Regions

```python
from core.locations import load_locations

db = load_locations()
all_locations = db.get_all()
regions = set(loc.region for loc in all_locations)
print(sorted(regions))
```

### Pattern 3: Find Nearby Locations

```python
from core.locations import load_locations
from core.location_service import LocationService

db = load_locations()
location = db.get("L300-BJ10")

# Get directly connected locations
nearby = []
for conn in location.connections:
    target = db.get(conn.to)
    nearby.append(target)

print(f"Connected to: {[loc.name for loc in nearby]}")
```

### Pattern 4: Calculate Time Differences

```python
from core.location_service import LocationService

service = LocationService()

locations = ["L300-BJ10", "L300-AA10", "L300-AE05"]
print(f"Tokyo: {service.get_local_time_str('L300-BJ10')}")
print(f"NYC: {service.get_local_time_str('L300-AA10')}")

diff = service.get_time_difference("L300-BJ10", "L300-AA10")
print(f"Tokyo is {diff} hours ahead of NYC")
```

### Pattern 5: Explore by Type

```python
from core.locations import load_locations

db = load_locations()

# Get all major cities
cities = db.find_by_type("major-city")
print(f"Major cities: {[loc.name for loc in cities]}")

# Get all geographic landmarks
landmarks = db.find_by_type("geographical-landmark")
print(f"Landmarks: {[loc.name for loc in landmarks]}")
```

---

## Data Types

### Location Object

```python
@dataclass
class Location:
    id: str                              # "L300-BJ10"
    name: str                           # "Tokyo - Shibuya Crossing"
    region: str                         # "asia_east"
    description: str                    # Location description
    layer: int                          # 300-401
    cell: str                           # "BJ10"
    scale: str                          # "terrestrial", "cosmic", etc
    continent: str                      # "Asia", "Europe", etc
    timezone: str                       # "UTC+9", "UTC-5", etc
    coordinates: Coordinate             # {lat, lon}
    type: str                           # "major-city", "temple", etc
    region_type: str                    # "metropolis", "landmark", etc
    connections: List[LocationConnection]
    tiles: Dict[str, Tile]
```

### Coordinate Object

```python
@dataclass
class Coordinate:
    lat: float      # -90 to 90
    lon: float      # -180 to 180

    def distance_to(other: Coordinate) -> float:
        """Return distance in kilometers."""
```

### LocationConnection Object

```python
@dataclass
class LocationConnection:
    to: str                     # Target location ID
    direction: str             # "north", "south", "east", "west"
    label: str                 # Display name
    requires: Optional[str]    # Quest/item requirement (future)
```

### Tile Object

```python
@dataclass
class Tile:
    objects: List[TileObject]      # Static objects
    sprites: List[TileSprite]      # Dynamic sprites
    markers: List[TileMarker]      # Waypoints/POIs
```

---

## Common Errors and Solutions

### Error: Module not found

```python
# ❌ Wrong
from location_service import LocationService

# ✅ Correct
from core.location_service import LocationService
from core.locations import load_locations
```

### Error: Location not found

```python
# Check location ID format (should be L{layer}-{cell})
location = db.get("L300-BJ10")  # Correct
location = db.get("Tokyo")       # ❌ Won't work

# Use query functions instead
tokyo_locs = db.find_by_region("asia_east")
```

### Error: No timezone support

```python
# The system already supports all timezones
# UTC+5:30 and UTC+9:30 work fine
location = service.get_location("L300-AE05")  # Mumbai (UTC+5:30)
local_time = service.get_local_time("L300-AE05")  # Works!
```

---

## Performance Notes

- **Database Load:** ~50ms (first load)
- **Query Time:** <1ms (subsequent queries)
- **Pathfinding:** <5ms for most paths
- **Timezone Calc:** <1ms
- **Memory Usage:** ~2-3MB for full database

The database is singleton-cached, so repeated calls use cached version.

---

## Next Steps

### For Command Handler Implementation

- Refer to `/docs/v1.0.7.0-PHASE-5E-HANDLERS.md`
- Start with `map_handler.py` (simpler grid-based)
- Then implement `panel_handler.py` and `goto_handler.py`

### For TUI Integration

- Import `LocationService` in handlers
- Use `load_locations()` for database access
- Display location info using TUI grid system

### For Testing

- Test with `LocationDatabase.load()`
- Verify timezone calculations
- Test pathfinding with sample locations
- Validate tile rendering

---

## Support

For questions or issues:

1. Check `/docs/v1.0.7.0-PHASE-5E-HANDLERS.md` for handler specs
2. Review `/docs/devlog/2026-01-18-phase-5d-complete.md` for architecture
3. Look at test examples in `/memory/tests/integration/test_location_service.py`
4. See usage patterns in this guide

---

**Last Updated:** 2026-01-18  
**Version:** 1.0.0 - Phase 5D Complete  
**Status:** Ready for Phase 5E Command Handlers
