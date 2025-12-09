# Location Data Structure (v1.2.21)

## Overview
User location data is stored across two main sources:
1. **user.json** - User's current location (city name + TILE code)
2. **cities.json** - Complete city/country reference data (55 cities)

## Data Storage Schema

### user.json Fields

```json
{
  "USER_PROFILE": {
    "NAME": "Fredrick",
    "LOCATION": "Sydney",          // City NAME
    "TILE": "AA340",                // Grid position (TILE code)
    "GALAXY": "Milky Way",          // Auto-linked to planet
    "PLANET": "Earth",              // Conditionally sets galaxy
    "TIMEZONE": "Australia/Sydney"
  }
}
```

**Note:** 
- No `LOCATION_DATA` section needed - all location fields in `USER_PROFILE`
- Lat/long can be derived from TILE code when needed (not stored)
- City/country data lives in cities.json for reference

### cities.json Structure

```json
{
  "metadata": {
    "version": "2.0.0",
    "total_cities": 55,
    "coordinate_system": "uDOS TILE grid (480x270, 83km @ layer 100)"
  },
  "cities": [
    {
      "name": "Sydney",
      "country": "Australia",
      "country_code": "AU",
      "tile_code": "AA340-100",     // Full TILE code with layer
      "grid_cell": "AA340",          // Grid position only
      "layer": 100,                  // World layer
      "latitude": -33.8688,
      "longitude": 151.2093,
      "timezone": {
        "name": "Australia/Sydney",
        "offset": "+10:00"
      },
      "climate": "subtropical",
      "languages": ["en"],
      "region": "Oceania",
      "continent": "Australia",
      "type": "city"
    }
  ]
}
```

## Planet → Galaxy Conditional Linking

Planets are automatically linked to their parent galaxy:

| Planet | Galaxy | Notes |
|--------|--------|-------|
| Earth | Milky Way | Sol system |
| Mars | Milky Way | Sol system |
| Jupiter | Milky Way | Sol system |
| Proxima b | Alpha Centauri System | Exoplanet |

**Implementation:** Setup wizard auto-sets `USER_PROFILE.GALAXY` based on `USER_PROFILE.PLANET` selection.

## Field Usage Guide
## Field Usage Guide

### Reading User Location
```python
from core.config import get_config

config = get_config()

# Get city name
city = config.get_user('USER_PROFILE.LOCATION', 'Unknown')  # "Sydney"

# Get TILE code
tile = config.get_user('USER_PROFILE.TILE', 'N/A')          # "AA340"

# Get planet/galaxy
planet = config.get_user('USER_PROFILE.PLANET', 'Earth')    # "Earth"
galaxy = config.get_user('USER_PROFILE.GALAXY', 'Milky Way') # "Milky Way"
```

### Looking Up City/Country Data
```python
import json
from pathlib import Path

# Load cities.json
cities_path = Path('core/data/geography/cities.json')
with open(cities_path) as f:
    data = json.load(f)

# Find city by name
city_name = config.get_user('USER_PROFILE.LOCATION')
for city in data['cities']:
    if city['name'] == city_name:
        country = city['country']         # "Australia"
        country_code = city['country_code'] # "AU"
        climate = city['climate']         # "subtropical"
        languages = city['languages']     # ["en"]
        # Lat/long available if needed
        lat = city['latitude']            # -33.8688
        lon = city['longitude']           # 151.2093
        break
```
## Setup Wizard Workflow
3. **Wizard stores:**
   - `USER_PROFILE.LOCATION` = City name
   - `USER_PROFILE.TILE` = Grid position from cities.json
   - `USER_PROFILE.PLANET` = Planet name
   - `USER_PROFILE.GALAXY` = Auto-linked galaxy

4. **NOT stored in user.json:**
   - City metadata (country, languages, climate, etc.)
   - Country data
   - Latitude/longitude (can be derived from TILE or looked up in cities.json)
   - Timezone offsets (only timezone name stored)
   - City metadata (country, languages, climate, etc.)
## Deprecated Fields (v1.2.21)

The following fields are **deprecated** and should not be used:

- ❌ `SYSTEM.GALAXY` → Use `USER_PROFILE.GALAXY`
- ❌ `SYSTEM.PLANET` → Use `USER_PROFILE.PLANET`
- ❌ `SYSTEM.CITY` → Use `USER_PROFILE.LOCATION`
- ❌ `SYSTEM.CITY_GRID` → Use `USER_PROFILE.TILE`
- ❌ `SYSTEM.CITY_LAYER` → Removed (always layer 100)
- ❌ `LOCATION_DATA.*` → All fields moved to `USER_PROFILE`
- ❌ `LOCATION_DATA.CITY` → Use `USER_PROFILE.LOCATION`
- ❌ `LOCATION_DATA.COUNTRY` → Lookup in cities.json
- ❌ `LOCATION_DATA.COUNTRY_CODE` → Lookup in cities.json

## Migration Notes

### From v1.2.20 → v1.2.21

**Old Structure:**
```json
{
  "SYSTEM": {
    "GALAXY": "Milky Way",
    "PLANET": "Earth",
    "CITY": "Sydney",
    "CITY_GRID": "AA340",
    "CITY_LAYER": 100
  }
}
```
**New Structure:**
```json
{
  "USER_PROFILE": {
    "LOCATION": "Sydney",
    "TILE": "AA340",
    "PLANET": "Earth",
    "GALAXY": "Milky Way"
  }
}
```
```

**Migration Script:** Setup wizard automatically converts old format to new format on first run.

## Benefits of This Structure
## Benefits of This Structure

✅ **No Data Duplication:** City/country data stored once in cities.json  
✅ **Simple User Config:** user.json only stores current location (city name + TILE)  
✅ **Easy Reference:** All city metadata available in cities.json  
✅ **Conditional Linking:** Planet automatically sets correct galaxy  
✅ **TILE Grid Ready:** Grid position stored for mapping system  
✅ **Extensible:** Easy to add new cities to cities.json without schema changes  
✅ **Centralized:** All location fields in USER_PROFILE (no LOCATION_DATA section)  
✅ **Derived Data:** Lat/long calculated from TILE when needed (not stored)
## Related Files

- **Setup Wizard:** `core/services/setup_wizard.py`
- **Config Manager:** `core/config.py`
- **Planet Manager:** `core/services/planet_manager.py`
- **Cities Database:** `core/data/geography/cities.json`
- **User Config:** `memory/bank/user/user.json`
- **CONFIG Panel:** `core/commands/configuration_handler.py`
- **Test Script:** `memory/ucode/tests/test_location_fields.upy`
