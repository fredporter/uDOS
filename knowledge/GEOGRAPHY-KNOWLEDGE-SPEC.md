---
title: "Geography-Knowledge Linking System v1.0.0"
id: GEOGRAPHY-KNOWLEDGE-SPEC
type: reference
category: knowledge
tags: [knowledge, knowledge]
difficulty: intermediate
last_updated: 2026-01-29
---

# Geography-Knowledge Linking System v1.0.0

**uDOS Alpha v1.0.0.67+ | Date: 2026-01-07**

## Overview

This specification defines how geographic map data (TILE system, layers, POIs) links to `/knowledge` articles. The system creates a hierarchical GUIDE structure:

```
🌌 Universe
└── 🌍 Planet (Earth, Mars, etc.)
    └── 🌎 Continent/Region
        └── 🏙️ City
            └── 🏘️ Neighbourhood/District
                └── 📍 Location (front door)
```

---

## 1. Hierarchy Levels

### Level 0: Universe
- **Coordinate Format**: `SPACE-[GALAXY]-L[LAYER]`
- **Knowledge Path**: `/knowledge/places/universe/`
- **Example**: `SPACE-MILKYWAY-L800`

### Level 1: Planet
- **Coordinate Format**: `SPACE-SOL-L[LAYER]` or `EARTH-L[LAYER]`
- **Knowledge Path**: `/knowledge/places/planets/[planet].md`
- **Example**: `SPACE-SOL-L605` (Mars)

### Level 2: Continent/Region
- **Coordinate Format**: `EARTH-[REGION]-L100-[CELL]`
- **Knowledge Path**: `/knowledge/places/regions/[region].md`
- **Example**: `EARTH-OC-L100-AB34` (Oceania-Australia)

### Level 3: City (GUIDE)
- **Coordinate Format**: `EARTH-[REGION]-L100-[CELL1]-[CELL2]`
- **Knowledge Path**: `/knowledge/places/cities/[city-slug].md`
- **Example**: `EARTH-OC-L100-AB34-CD15` (Sydney)

### Level 4: Neighbourhood/District
- **Coordinate Format**: `EARTH-[REGION]-L100-[CELL1]-[CELL2]-[CELL3]`
- **Knowledge Path**: Within city GUIDE as section
- **Example**: `EARTH-OC-L100-AB34-CD15-AA20` (Sydney CBD)

### Level 5: Location (Front Door)
- **Coordinate Format**: `EARTH-[REGION]-L100-[...]-[CELL4]`
- **Knowledge Path**: POI within district section
- **Example**: `EARTH-OC-L100-AB34-CD15-AA20-BC10` (Sydney Opera House entrance)

---

## 2. Knowledge Article Structure

### City GUIDE Template

```markdown
---
tier: 2
category: places
type: city-guide
title: "[City Name] City Guide"
coordinate: "EARTH-[REGION]-L100-[CELL1]-[CELL2]"
grid_cell: "[CELL]"
country: "[Country]"
continent: "[Continent]"
timezone: "[IANA Timezone]"
climate: "[climate_type]"
tags: [city, guide, [continent], [country], [climate]]
related_knowledge:
  - navigation/compass_use.md
  - reference/first-aid-quick-reference.md
last_updated: YYYY-MM-DD
---

# [City Name] City Guide

📍 **Grid Reference**: `[CELL]` at Layer 100
🌐 **Coordinate**: `[Full Coordinate]`
⏰ **Timezone**: [TIMEZONE]
🌡️ **Climate**: [Climate Description]

## Quick Facts
- Population: [X million]
- Languages: [languages]
- Currency: [currency]
- Emergency: [emergency number]

## Districts

### [District 1] `[CELL3]`
**Coordinate**: `[Full District Coordinate]`
[Description]

#### Points of Interest
- **[POI Name]** `[CELL4]` - [description]
- **[POI Name]** `[CELL4]` - [description]

### [District 2] `[CELL3]`
...

## Survival Notes
[Climate-specific survival info linked to /knowledge]

## Transport
[Getting around]

## Related Knowledge
- [Link to navigation article]
- [Link to climate article]
- [Link to local hazards]
```

---

## 3. Tag Taxonomy

### Geographic Tags
```yaml
scope_tags:
  - universe      # Cosmic scale
  - galaxy        # Galactic scale
  - solar-system  # Solar system
  - planet        # Planet level
  - continent     # Continental
  - country       # Country level
  - city          # City level
  - district      # Neighbourhood
  - poi           # Point of interest

type_tags:
  - guide         # City/region guide
  - landmark      # Notable landmark
  - waypoint      # Navigation waypoint
  - hazard        # Safety hazard
  - resource      # Survival resource
  - transport     # Transport hub
  - shelter       # Shelter location
  - water-source  # Water source
  - historical    # Historical site
  - natural       # Natural feature
```

### Climate Tags
```yaml
climate_tags:
  - tropical
  - subtropical
  - mediterranean
  - oceanic
  - continental
  - arid
  - semi-arid
  - polar
  - alpine
  - monsoon
```

### Terrain Tags
```yaml
terrain_tags:
  - coastal
  - mountain
  - desert
  - forest
  - urban
  - rural
  - river
  - lake
  - island
  - plains
```

---

## 4. Data Structure Extensions

### Enhanced City Entry (cities.json)

```json
{
  "name": "Sydney",
  "country": "Australia",
  "tile_code": "AB34-100",
  "grid_cell": "AB34",
  "layer": 100,
  "coordinate": "EARTH-OC-L100-AB34-CD15",
  
  "knowledge_link": "/knowledge/places/cities/sydney.md",
  
  "tags": ["city", "guide", "oceania", "australia", "coastal", "subtropical"],
  
  "districts": [
    {
      "name": "Sydney CBD",
      "cell": "AA20",
      "coordinate": "EARTH-OC-L100-AB34-CD15-AA20",
      "tags": ["district", "urban", "transport"],
      "pois": [
        {
          "name": "Sydney Opera House",
          "cell": "BC10",
          "coordinate": "EARTH-OC-L100-AB34-CD15-AA20-BC10",
          "type": "landmark",
          "tags": ["landmark", "historical", "cultural"]
        }
      ]
    }
  ],
  
  "related_knowledge": [
    "navigation/coastal_navigation.md",
    "reference/seasonal-calendar-australia.md",
    "survival/heat_emergencies.md"
  ]
}
```

### Enhanced Planet Entry (planets-hierarchical.json)

```json
{
  "name": "Mars",
  "coordinate": "SPACE-SOL-L605",
  "knowledge_link": "/knowledge/places/planets/mars.md",
  
  "tags": ["planet", "terrestrial", "solar-system"],
  
  "notable_locations": [
    {
      "name": "Olympus Mons",
      "coordinate": "SPACE-SOL-L605-AB20-CD15",
      "knowledge_section": "#olympus-mons",
      "type": "geological_feature",
      "tags": ["landmark", "mountain", "volcanic"]
    }
  ],
  
  "related_knowledge": [
    "reference/celestial-mechanics.md",
    "tech/space-navigation.md"
  ]
}
```

---

## 5. Waypoint & POI Types

### Waypoint Categories
```yaml
waypoint_types:
  navigation:
    - compass_point     # Cardinal direction marker
    - trail_marker      # Trail/path marker
    - junction          # Path intersection
    - summit            # Mountain peak
    - pass              # Mountain pass
    
  shelter:
    - building          # Structure
    - cave              # Natural shelter
    - campsite          # Camping area
    - emergency_shelter # Emergency refuge
    
  water:
    - spring            # Natural spring
    - well              # Well/bore
    - river_access      # River/stream access
    - reservoir         # Water storage
    - purification      # Water treatment
    
  transport:
    - airport           # Airport
    - port              # Sea port
    - station           # Train/bus station
    - helipad           # Helicopter landing
    - fuel              # Fuel station
    
  emergency:
    - hospital          # Medical facility
    - police            # Police station
    - fire_station      # Fire service
    - embassy           # Embassy/consulate
    - safe_zone         # Evacuation point
```

---

## 6. Celestial Data Structure

### Solar System Layer Mapping

| Layer | Description | Knowledge Path |
|-------|-------------|----------------|
| L600 | Mercury | `/knowledge/places/planets/mercury.md` |
| L601 | Venus | `/knowledge/places/planets/venus.md` |
| L602 | Earth (ref) | Cross-ref to EARTH-L100 |
| L603 | Moon | `/knowledge/places/planets/moon.md` |
| L605 | Mars | `/knowledge/places/planets/mars.md` |
| L610 | Ceres | `/knowledge/places/asteroids/ceres.md` |
| L620 | Jupiter | `/knowledge/places/planets/jupiter.md` |
| L621 | Saturn | `/knowledge/places/planets/saturn.md` |
| L700 | Milky Way Overview | `/knowledge/places/galaxy/milky-way.md` |

### Celestial POI Types
```yaml
celestial_poi_types:
  - landing_site      # Historical/planned landing
  - crater            # Impact crater
  - mountain          # Mons/mountain
  - valley            # Valley/canyon
  - plain             # Planitia/plain
  - volcano           # Volcanic feature
  - ice_deposit       # Water/ice location
  - base_site         # Future base location
  - observation_point # Telescope/observatory
```

---

## 7. Knowledge Cross-References

### Auto-Link Rules

1. **Climate → Survival**: City climate tag links to matching survival articles
   - `tropical` → `/knowledge/survival/tropical_survival.md`
   - `arid` → `/knowledge/survival/desert_survival.md`

2. **Terrain → Navigation**: Terrain tags link to navigation guides
   - `coastal` → `/knowledge/navigation/coastal_navigation.md`
   - `mountain` → `/knowledge/navigation/terrain_features.md`

3. **Region → Flora/Fauna**: Region links to local knowledge
   - `australia` → `/knowledge/reference/edible-plants-australia.md`

4. **Planet → Celestial**: Planet links to astronomical guides
   - `mars` → `/knowledge/reference/celestial-mechanics.md`

---

## 8. Directory Structure

```
/knowledge/places/
├── README.md                    # Places knowledge overview
├── version.json                 # Version tracking
│
├── planets/                     # Planetary guides
│   ├── earth.md                 # Earth overview (links to cities)
│   ├── mars.md                  # Mars exploration guide
│   ├── moon.md                  # Lunar guide
│   ├── venus.md                 # Venus guide
│   └── jupiter.md               # Jupiter system guide
│
├── regions/                     # Continental/regional guides
│   ├── oceania.md               # Oceania overview
│   ├── europe.md                # Europe overview
│   ├── asia.md                  # Asia overview
│   ├── north-america.md         # North America overview
│   └── africa.md                # Africa overview
│
├── cities/                      # City GUIDEs
│   ├── sydney.md                # Sydney comprehensive guide
│   ├── tokyo.md                 # Tokyo comprehensive guide
│   ├── london.md                # London comprehensive guide
│   ├── new-york.md              # NYC comprehensive guide
│   ├── paris.md                 # Paris guide
│   └── [more cities...]
│
├── landmarks/                   # Major landmarks
│   ├── natural/
│   │   ├── grand-canyon.md
│   │   └── great-barrier-reef.md
│   └── cultural/
│       ├── eiffel-tower.md
│       └── pyramids-giza.md
│
└── celestial/                   # Space locations
    ├── milky-way.md             # Galaxy overview
    ├── solar-system.md          # Solar system guide
    └── notable-objects/
        ├── olympus-mons.md      # Mars volcano
        └── europa.md            # Jupiter moon
```

---

## 9. Implementation Notes

### Grid Reference Display
All knowledge articles with geographic links should display:
```
📍 Grid: [CELL] | Layer: [LAYER] | Coord: [FULL_COORDINATE]
```

### Knowledge Lookup Flow
```
User enters TILE code → MapEngine lookup → Knowledge bridge query
                                        → Return linked articles
                                        → Display in sidebar/panel
```

### Offline Priority
All geographic knowledge must be:
- Self-contained (no external links required)
- Cacheable in `.udos.md` tiles
- Accessible via `KNOW` command

---

*Version: 1.0.0 | Author: uDOS System | Last Updated: 2026-01-07*
