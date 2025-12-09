# Geography Data (v2.2.0 - TILE-Based)

**Last Updated:** December 8, 2025  
**uDOS Version:** v1.2.21  
**Coordinate System:** uDOS TILE Grid (480×270, no lat/long)

## Overview

The uDOS geography system uses **TILE codes** exclusively for all location references. No latitude/longitude coordinates are stored - all positions use the TILE grid system.

## Data Files

### ✅ Active Files

| File | Version | Purpose | Records |
|------|---------|---------|---------|
| **cities.json** | 2.2.0 | Complete city/country/timezone database | 55 cities |
| **climate.json** | 2.0.0 | Climate zone definitions | 18 zones |
| **terrain.json** | 2.0.0 | Terrain type classifications | 24 types |

### 📦 Archived Files

| File | Status | Reason |
|------|--------|--------|
| **countries.json** | Deprecated | Country data now in cities.json |
| **timezones.json** | Deprecated | Timezone data now in cities.json |

**Location:** `.archive/*.deprecated`

## File Structures

### cities.json

**Primary location database** - All city and country data in one file.

```json
{
  "metadata": {
    "version": "2.2.0",
    "total_cities": 55,
    "coordinate_system": "uDOS TILE grid (480x270, 83km @ layer 100)",
    "data_structure": "TILE-based geography (no lat/long stored)",
    "timezone_data": "Integrated (no separate timezones.json)"
  },
  "cities": [
    {
      "name": "Sydney",
      "country": "Australia",
      "country_code": "AU",
      "tile_code": "AA340-100",
      "grid_cell": "AA340",
      "layer": 100,
      "timezone": {
        "iana": "Australia/Sydney",
        "utc_offset": "+10:00",
        "utc_offset_dst": "+11:00",
        "dst_active": true,
        "abbr": "AEST/AEDT"
      },
      "climate": "subtropical",
      "languages": ["en"],
      "region": "Oceania",
      "continent": "Australia",
      "type": "city",
      "population_class": "major"
    }
  ]
}
```

**Key Fields:**
- `grid_cell` - TILE code (e.g., "AA340")
- `tile_code` - Full TILE with layer (e.g., "AA340-100")
- `country` - Country name (embedded, no separate file)
- `country_code` - ISO 2-letter code
- `timezone` - Complete timezone data (embedded, no separate file)
  - `iana` - IANA timezone name
  - `utc_offset` - Standard UTC offset
  - `utc_offset_dst` - Daylight saving offset
  - `dst_active` - Has daylight saving
  - `abbr` - Timezone abbreviation
- **NO** `latitude` or `longitude` fields

### climate.json

**Climate zone classifications** for world generation.

```json
{
  "metadata": {
    "version": "2.0.0",
    "coordinate_system": "TILE-based (no lat/long)",
    "usage": "Climate zones mapped to TILE grid for world generation"
  },
  "climate_zones": [
    {
      "id": "tropical_rainforest",
      "name": "Tropical Rainforest",
      "koppen_code": "Af",
      "temp_range_c": {"min": 18, "max": 35},
      "annual_rainfall_mm": {"min": 2000, "max": 10000},
      "description": "Hot and humid year-round with heavy rainfall",
      "vegetation": "Dense rainforest",
      "example_tiles": [],
      "season_count": 1,
      "color_code": "dark_green"
    }
  ]
}
```

**Key Changes:**
- Removed `example_locations` field
- Added `example_tiles` (empty, ready for TILE mapping)
- No geographic coordinates

### terrain.json

**Terrain type definitions** for map rendering.

```json
{
  "metadata": {
    "version": "2.0.0",
    "coordinate_system": "TILE-based (elevation derived from layer)",
    "note": "Elevation calculated from TILE layer (100-899)"
  },
  "terrain_types": [
    {
      "id": "ocean",
      "name": "Ocean",
      "ascii_char": "≈",
      "color_code": "blue",
      "traversable": false,
      "water_source": true,
      "description": "Deep ocean waters",
      "map_symbol": "~",
      "teletext_block": "░"
    }
  ],
  "tile_layers": {
    "100": {"name": "world", "scale_km": 83},
    "200": {"name": "region", "scale_km": 2.78},
    "300": {"name": "city", "scale_km": 0.093},
    "400": {"name": "district", "scale_km": 0.003},
    "500": {"name": "block", "scale_km": 0.0001}
  }
}
```

**Key Changes:**
- Removed `elevation_range` (derived from TILE layer)
- Added `tile_layers` reference system
- Elevation calculated: `layer * scale_km`

### timezones.json

**Timezone reference** linked to cities via TILE codes.

```json
{
  "metadata": {
    "version": "2.0.0",
    "coordinate_system": "TILE-based (city references)",
    "usage": "Lookup timezone by city name, get TILE from cities.json"
  },
  "timezones": [
    {
      "iana_name": "Australia/Sydney",
      "utc_offset": "+10:00",
      "utc_offset_dst": "+11:00",
      "dst_active": true,
      "zone_abbr": "AEST/AEDT",
      "cities": ["Sydney", "Melbourne", "Brisbane"],
      "city_tiles": {
        "Sydney": "AA340",
        "Melbourne": "AB345",
        "Brisbane": "AA330"
      },
      "countries": ["AU"]
    }
  ]
}
```

**Key Changes:**
- Removed `tizo_zones` (outdated system)
- Added `city_tiles` mapping (city name → TILE code)
- Links to cities.json for full city data

## TILE Grid System

### Grid Specifications

- **Dimensions:** 480 columns × 270 rows
- **Format:** 2-letter column (AA-RL) + row number (0-269)
- **Layers:** 100-899 (5 zoom levels)

### Layer Scale

| Layer | Name | Scale (km/cell) | Use Case |
|-------|------|-----------------|----------|
| 100 | World | 83 | Continents, oceans |
| 200 | Region | 2.78 | Countries, states |
| 300 | City | 0.093 | Urban areas |
| 400 | District | 0.003 | Neighborhoods |
| 500 | Block | 0.0001 | Buildings |

### TILE Code Format

```
AA340-100
││ │  └── Layer (100-899)
## Data Integrity

### No Duplication

✅ **Country data:** Stored once in cities.json (no countries.json)  
✅ **Timezone data:** Stored once in cities.json (no timezones.json)  
✅ **Location data:** TILE codes only (no lat/long anywhere)  
✅ **Climate data:** Ready for TILE-based world generation  

### Lookup Pattern

**To get all data for a city:**
1. Load cities.json
2. Find city by name or TILE code
3. Access country, timezone, climate, languages - all in one object

**To find cities in a timezone:**
1. Load cities.json
2. Filter by `timezone.iana` field
3. Get list of matching cities

**To get climate for a TILE:**
1. Load climate.json
2. Match TILE to climate zone (future: use climate mapping)
3. Apply climate rules to TILE

## Migration Notes

### From v2.1.0 → v2.2.0

**cities.json:**
- ✅ Integrated complete timezone data from timezones.json
- ✅ Updated timezone structure: `{iana, utc_offset, utc_offset_dst, dst_active, abbr}`
- ✅ Updated metadata version to 2.2.0

**timezones.json:**
- ❌ **DEPRECATED** - Moved to `.archive/timezones.json.deprecated`
- ✅ Data preserved in cities.json timezone field

### From v1.0.20b → v2.0.0

**cities.json:**
- ❌ Removed `latitude` and `longitude` fields
- ✅ Added country data (country_code, region, continent)
- ✅ Updated metadata with TILE reference

**climate.json:**
- ❌ Removed `example_locations` field
- ✅ Added `example_tiles` (empty array)
- ✅ Updated metadata with TILE reference

**terrain.json:**
- ❌ Removed `elevation_range` field
- ❌ Removed `elevation_categories` section
- ✅ Added `tile_layers` reference system
- ✅ Updated metadata

**countries.json:**
- ❌ **DEPRECATED** - Moved to `.archive/countries.json.deprecated`
- ✅ Data preserved in cities.json

## Benefits

✅ **Single Source of Truth:** All city data in cities.json (country + timezone + climate)  
✅ **TILE-First:** All locations use grid codes  
✅ **No Redundancy:** No separate files for countries or timezones  
✅ **Simplified Lookups:** Single file access for complete city data  
✅ **Smaller Dataset:** Consolidated data, faster loading  
✅ **Future-Ready:** Climate and terrain ready for procedural generation  

## See Also

- [Location Data Structure](../docs/LOCATION-DATA-STRUCTURE.md) - USER_PROFILE location fields
- [Mapping System](../../../../wiki/Mapping-System.md) - TILE grid documentation
- [Grid System](../../../../extensions/play/README.md) - Map engine details
