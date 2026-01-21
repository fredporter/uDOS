---
tier: 2
category: places
title: "Geographic Knowledge & City Guides"
complexity: reference
last_updated: 2026-01-07
author: uDOS
version: 1.0.0
---

# Geographic Knowledge & City Guides

**Progress: 6 placeholder guides | Foundation Phase**

Geographic knowledge linking the uDOS map layer system (TILE coordinates) to survival knowledge, navigation guides, and location-specific information.

---

## 📚 Directory Structure

```text
places/
├── README.md                 # This file
├── planets/                  # Planetary guides (Solar System)
│   ├── earth.md             # Home planet overview
│   ├── moon.md              # Lunar guide
│   └── mars.md              # Mars exploration
├── regions/                  # Continental guides
│   ├── oceania.md           # Australia, NZ, Pacific
│   └── europe.md            # European overview
├── cities/                   # City GUIDEs with grid references
│   ├── sydney.md            # EARTH-OC-L100-AB34-CD15
│   ├── tokyo.md             # EARTH-AS-L100-PK68-AA20
│   ├── london.md            # EARTH-EU-L100-JF57-CD15
│   └── new-york.md          # EARTH-NA-L100-FP71-AB30
├── landmarks/                # Major landmarks (POIs)
│   └── [future]
└── celestial/                # Space locations
    └── [future]
```

---

## 🌍 Hierarchy Levels

| Level | Scope | Precision | Knowledge Type |
|-------|-------|-----------|----------------|
| 0 | Universe | Galaxy | Overview article |
| 1 | Planet | ~333 km/cell | Planet guide |
| 2 | Continent | ~2.77 km/cell | Regional guide |
| 3 | City | ~23 m/cell | **City GUIDE** |
| 4 | District | ~0.19 m/cell | Section in GUIDE |
| 5 | Location | ~1.6 mm/cell | POI entry |

---

## 🏙️ City GUIDEs

City GUIDEs are comprehensive location references that link to:

- **Grid coordinates** for map navigation
- **Climate** → survival knowledge
- **Terrain** → navigation techniques
- **Local hazards** → safety information
- **Resources** → water, food, shelter

### Guide Structure

Each city GUIDE contains:

1. **Quick Facts** - Population, timezone, emergency numbers
2. **Districts** - Major areas with sub-grid coordinates
3. **Points of Interest** - Landmarks, resources, hazards
4. **Survival Notes** - Climate-specific information
5. **Transport** - Getting around
6. **Related Knowledge** - Links to /knowledge articles

---

## 🏷️ Tag System

### Geographic Scope

- `universe` - Cosmic scale
- `galaxy` - Galactic scale
- `solar-system` - Solar system
- `planet` - Planet level
- `continent` - Continental
- `country` - Country level
- `city` - City level
- `district` - Neighbourhood
- `poi` - Point of interest

### Climate Types

- `tropical` `subtropical` `mediterranean`
- `oceanic` `continental` `arid`
- `semi-arid` `polar` `alpine` `monsoon`

### Terrain Types

- `coastal` `mountain` `desert` `forest`
- `urban` `rural` `river` `lake` `island` `plains`

---

## 🔗 Knowledge Cross-References

City GUIDEs automatically link to related knowledge:

| City Climate | Links To |
|--------------|----------|
| tropical | `/knowledge/survival/tropical_survival.md` |
| arid | `/knowledge/survival/desert_survival.md` |
| coastal | `/knowledge/navigation/coastal_navigation.md` |
| alpine | `/knowledge/survival/cold_weather_survival.md` |

| City Region | Links To |
|-------------|----------|
| Australia | `/knowledge/reference/edible-plants-australia.md` |
| Australia | `/knowledge/reference/seasonal-calendar-australia.md` |

---

## 📍 Grid Reference Format

All locations display their grid reference:

```text
📍 Grid: AB34 | Layer: 100 | Coord: EARTH-OC-L100-AB34-CD15
```

### Coordinate Structure

```text
[REALM]-[REGION]-L[LAYER]-[CELL1]-[CELL2]-[CELL3]...
  │        │       │        │       │       │
  │        │       │        │       │       └── District/POI
  │        │       │        │       └────────── City level
  │        │       │        └────────────────── Region cell
  │        │       └─────────────────────────── Layer (100=surface)
  │        └─────────────────────────────────── Region code (OC=Oceania)
  └──────────────────────────────────────────── Realm (EARTH/SPACE)
```

---

## 🚀 Getting Started

### View a City Guide

```text
KNOW sydney
```

### Navigate to a City

```text
MAP GOTO sydney
```

### Show Grid Reference

```text
WHERE
→ EARTH-OC-L100-AB34-CD15 (Sydney, Australia)
```

---

## 📖 Related Knowledge

- [Navigation & Wayfinding](../navigation/README.md)
- [Reference Materials](../reference/README.md)
- [Survival Guides](../survival/README.md)
- [Celestial Mechanics](../reference/celestial-mechanics.md)

---

*Version: 1.0.0 | Last Updated: 2026-01-07*
