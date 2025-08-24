# uDATA Geographic Documentation v4.0
*Consolidated from multiple documentation files*

## 📊 Data Sources Consolidated
- `geographic-validation-rules.md`
- `global-cities-expanded.md`
- `location-timezone-templates.md`
- `timezone-location-validation.md`
- `map-layers.md`

## 🌍 Geographic Validation Rules

### TILE Code Validation
- **Format**: `[A-Z]{2}[0-9]{2}` (2 letters + 2 digits)
- **Examples**: `AA24`, `CF35`, `WG10`
- **Range**: AA00-ZZ99 (valid coordinate space)

### Coordinate Validation
- **Latitude**: -90.0 to +90.0 degrees
- **Longitude**: -180.0 to +180.0 degrees
- **Precision**: 4 decimal places minimum
- **Format**: Decimal degrees (WGS84)

### 4-Alpha Timezone Codes
- **Format**: `[A-Z]{4}` (4 uppercase letters)
- **Standard**: USPT, USCT, USET, EUCE, JPST, AUET, GMTU
- **Custom**: Regional codes following 4-character pattern

## 🏙️ Global Cities Reference

### Population Tiers
- **Megacity**: 10+ million (e.g., Tokyo 37.4M)
- **Large Metro**: 5-10 million (e.g., Sydney 5.4M)
- **Major City**: 2-5 million (e.g., Paris 2.1M)
- **Regional Hub**: 1-2 million (e.g., Barcelona 1.6M)

### Regional Distribution
- **Asia**: 16 cities (44% of dataset)
- **Europe**: 7 cities (19% of dataset)
- **North America**: 6 cities (17% of dataset)
- **South America**: 4 cities (11% of dataset)
- **Africa**: 3 cities (8% of dataset)

## 🗺️ Map Layer System

### Virtual Layer Stack
```
🌌 Space Layer        (+50,000m)  - Satellites, orbital data
🌟 Atmosphere Layer   (+20,000m)  - Weather systems
✈️  Aviation Layer     (+10,000m)  - Flight paths
☁️  Cloud Layer        (+2,000m)   - Precipitation
🌍 Surface Layer      (0m)        - Geography, cities
🚇 Subsurface Layer   (-100m)     - Utilities, tunnels
🌋 Geological Layer   (-1,000m)   - Geology, resources
🔥 Core Layer         (-6,371km)  - Planetary core
```

### Layer Properties
- **Elevation Range**: -6,371km to +50,000m
- **Data Types**: Vector, raster, temporal
- **Update Frequency**: Real-time to historical
- **Coordinate System**: WGS84

## 📍 Location Templates

### City Template
```json
{
  "tile": "XX##",
  "city": "City Name",
  "country": "Country",
  "lat": 00.0000,
  "lon": 000.0000,
  "population": 0000000,
  "timezone": "XXXX",
  "region": "Continental Region"
}
```

### TILE Reference Template
```json
{
  "tile_id": "XX##",
  "coordinates": {
    "latitude": 00.0000,
    "longitude": 000.0000
  },
  "location_type": "city|country|region",
  "parent_tile": "XXXX",
  "child_tiles": ["XX##", "XX##"]
}
```

## ⏰ Timezone Integration

### Timezone Validation Process
1. **Code Format Check**: Must be 4 uppercase letters
2. **UTC Offset Validation**: -12:00 to +14:00 range
3. **DST Rules**: Summer/winter time adjustments
4. **Regional Consistency**: Matches geographic location

### Conversion Examples
```bash
# Old 2-digit → New 4-alpha
C0 → USPT (US Pacific Time)
AE → EUCE (Central European Time)
UT → GMTU (Greenwich Mean Time)
```

## 🔍 Data Quality Standards

### Coordinate Precision
- **Cities**: ±100m accuracy required
- **Countries**: ±1km boundary accuracy
- **Regions**: ±10km center point accuracy

### Population Data
- **Source**: Latest metropolitan area estimates
- **Update Cycle**: Annual review required
- **Verification**: Cross-reference with official statistics

### Timezone Accuracy
- **Current Rules**: Updated for latest DST changes
- **Historical Data**: Maintains timezone history
- **Future Changes**: Monitors timezone legislation

## 🛠️ Usage Guidelines

### File Naming
- **Geographic Data**: Use uDATA format with compact hex
- **Map Files**: Preserve uMAP/uTILE naming for depth
- **Documentation**: Consolidate into uDATA format

### Integration Points
- **Hex Generator**: Reads timezone from user.md
- **TILE System**: Links to geographic coordinates
- **Map Navigation**: Hierarchical parent-child relationships

## 📈 Performance Considerations

### Data Loading
- **Lazy Loading**: Load regions on demand
- **Caching**: Cache frequently accessed cities
- **Compression**: Use efficient JSON structures

### Search Optimization
- **TILE Index**: Fast coordinate-based lookup
- **City Search**: Name-based fuzzy matching
- **Timezone Lookup**: Direct 4-alpha code mapping

---

**Consolidation Complete**: All geographic documentation now unified in single uDATA file with comprehensive validation rules, templates, and integration guidelines.
