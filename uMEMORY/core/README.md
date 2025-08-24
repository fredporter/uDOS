# uMEMORY Core Data v3.0

This directory contains core geographical and reference data for the uDOS system using enhanced hex naming and TILE integration.

## 🗺️ Geographic Data (uMAP/uTILE Format)

### Continental Maps (uMAP)
- `uMAP-00MK60-Earth.json` - Planet Earth base map
- `uMAP-00FP26-North-America.json` - North American continent
- `uMAP-00MP63-Europe.json` - European continent  
- `uMAP-00UH04-Oceania.json` - Oceanic region
- `uMAP-00SO94-Asia.json` - Asian continent
- `uMAP-00NH68-Africa.json` - African continent
- `uMAP-00II44-South-America.json` - South American continent
- `uMAP-03MAN-Manhattan.json` - Manhattan borough (example street-level)

### TILE Location Data (uTILE)
- `tiles/` directory - 28 uTILE files with real geographic coordinates
- **Maintains full Earth-00 map depth** - from planet level to street level
- **Real TILE codes** - based on actual WGS84 coordinates
- **Hierarchical navigation** - Planet→Continent→Country→City→Street

### Reference Data (uDATA Format)

#### Enhanced Cultural Reference
- `uDATA-00E78515A0000FFFF-Cultural-Reference.json` - Consolidated currencies and languages
  - **Replaces**: `currencyMap.json`, `languageMap.json` 
  - **Benefits**: Single source, proper hex naming, unified schema

### Legacy Geographic Data
- `cityMap.json` - Global city mappings and metadata
- `countryMap.json` - Country codes and geographical information
- `locationMap.json` - Location coordinate mappings
- `global-cities-timezones.json` - City-timezone associations  
- `timezoneMap.json` - Comprehensive timezone mappings

### Documentation & Validation
- `geographic-validation-rules.md` - Rules for validating geographical data
- `global-cities-expanded.md` - Extended city information and documentation
- `timezone-location-validation.md` - Timezone validation rules
- `location-timezone-templates.md` - Templates for location-timezone associations
- `map-layers.md` - Map layer definitions and documentation
- `mission-locations.geojson` - GeoJSON data for mission locations

## 🔧 Enhanced Hex Generator (uCORE Integration)

### System-Wide Access
- **Location**: `/uCORE/bin/hex-generator.sh`
- **Alias**: `/uCORE/bin/uhex` for quick access
- **Features**: TILE integration, 4-alpha timezone codes, role detection

### 4-Alpha Timezone Support
- **Format**: USPT, EUCE, JPST, AUET, etc.
- **No conversion datasets needed** - direct encoding in hex
- **TILE-aware** - timezone detection from uTILE files
- **System fallback** - automatic system timezone detection

### Usage Examples
```bash
# Generate uDATA file
uhex generate uDATA "Global reference data" json

# Generate uMAP file  
uhex generate uMAP "New city map" json

# Check current TILE location
uhex tile

# Decode existing filename
uhex decode uDATA-00E78515A0000FFFF-Cultural-Reference.json
```

## 📊 File Organization Benefits

### Before Consolidation
- **16 separate reference files** - scattered data
- **No hex naming** - breaks uDOS v1.3 standards  
- **Data redundancy** - timezone/currency duplicates
- **Poor TILE integration** - no geographic awareness

### After Enhancement  
- ✅ **uDATA for reference data** - currencies, languages consolidated
- ✅ **uMAP/uTILE preserved** - maintains full geographic depth
- ✅ **Proper hex naming** - system-wide compliance
- ✅ **TILE integration** - geographic-aware hex generation
- ✅ **4-alpha timezones** - eliminates conversion datasets

## 🌍 Geographic Capabilities Preserved

### Earth-00 Map Depth Maintained
- **Planet Level**: `uMAP-00MK60-Earth.json`
- **Continental Level**: `uMAP-00FP26-North-America.json` 
- **Country Level**: `uTILE-00US01-United-States.json`
- **City Level**: `uTILE-00HO35-New-York-City.json`
- **Street Level**: `uMAP-03MAN-Manhattan.json`

### TILE Navigation System
- **Real coordinates** - WGS84 geographic positioning
- **Hierarchical relationships** - proper parent-child linking  
- **Street-level detail** - full urban navigation support
- **Global coverage** - 28 major world cities with real TILE codes
