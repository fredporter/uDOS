# uMAP System - Complete Geographic Mapping Framework

## Overview
The uMAP system provides a hierarchical geographic mapping framework with TILE-based location coding and multi-level zoom navigation from global to street level.

## Core Components

### Engine Files (renamed from MAP-00)
- `umap-engine.sh` - Core tile creation and management engine
- `utile-location.sh` - Advanced coordinate conversion and spatial operations

### Map Hierarchy

#### Level 0: Planet Earth (00)
- **File**: `uMAP-00MK60-Earth.json`
- **Coverage**: Global (entire planet)
- **TILE Format**: `00[A-Z]{2}[0-9]{2}-[depth]m`

#### Level 1: Continents (01XX)
- **01NA**: North America (`uMAP-01NA-North-America.json`)
- **01EU**: Europe (`uMAP-01EU-Europe.json`)
- **01AS**: Asia (`uMAP-01AS-Asia.json`)
- **01AF**: Africa (`uMAP-01AF-Africa.json`)
- **01SA**: South America (`uMAP-01SA-South-America.json`)
- **01OC**: Oceania (`uMAP-01OC-Oceania.json`)

#### Level 2: Metropolitan Areas (02XXX)
- **02NYC**: New York City Metropolitan Area
- **02LON**: London Metropolitan Area
- **02PAR**: Paris Metropolitan Area
- And many more regional submaps...

#### Level 3: Cities/Boroughs (03XXXX)
- **03MAN**: Manhattan Borough
- **03BRO**: Brooklyn Borough
- And detailed city districts...

#### Level 4: Districts/Neighborhoods (04XXXXX)
- **04TSQ**: Times Square District
- **04CPK**: Central Park Area
- And specific neighborhood maps...

#### Level 5: Landmarks/Streets (05XXXXXX)
- **05BWY**: Broadway Corridor
- **05WST**: Wall Street Area
- And detailed landmark maps...

## Major Cities with TILE Codes

### North America
- New York City: `00HO35-1m` (40.7589, -73.9851)
- Washington DC: `00GO34-1m` (38.9072, -77.0369)
- Los Angeles: `00EN20-1m` (34.0522, -118.2437)
- Ottawa: `00GP34-1m` (45.4215, -75.6972)
- Mexico City: `00FM26-1m` (19.4326, -99.1332)

### Europe
- London: `00LP59-1m` (51.5074, -0.1278)
- Paris: `00MP60-1m` (48.8566, 2.3522)
- Berlin: `00MP64-1m` (52.5200, 13.4050)
- Rome: `00MO64-1m` (41.9028, 12.4964)
- Madrid: `00LO58-1m` (40.4168, -3.7038)

### Asia
- Tokyo: `00VN06-1m` (35.6762, 139.6503)
- Beijing: `00TO98-1m` (39.9042, 116.4074)
- New Delhi: `00RN85-1m` (28.6139, 77.2090)
- Moscow: `00OQ72-1m` (55.7558, 37.6176)

### Africa
- Cairo: `00ON70-1m` (30.0444, 31.2357)
- Johannesburg: `00NH69-1m` (-26.2041, 28.0473)

### South America
- Brasilia: `00II44-1m` (-15.7975, -47.8919)
- Buenos Aires: `00IG40-1m` (-34.6118, -58.3960)

### Oceania
- Sydney: `00WG10-1m` (-33.8688, 151.2093)

## Navigation System

### Hierarchical Linking
Each map level contains:
- **parent**: Link to higher level map
- **zoom_in**: Array of detailed submaps
- **zoom_out**: Link to broader map
- **adjacent**: Links to neighboring areas at same level

### Submap References
Maps include `submap_links` sections that define what each submap ID represents, enabling seamless navigation between different zoom levels.

## TILE Code Generation

### Format Structure
- **Map ID**: `00` (Earth), `01XX` (Continents), `02XXX` (Metro), etc.
- **Grid Letters**: Two letters based on longitude/latitude bands
- **Grid Numbers**: Two digits for fine-grained positioning
- **Depth**: Depth level (1m for surface, up to 1000m)

### Example: New York City
- **Coordinates**: 40.7589°N, 73.9851°W
- **TILE Code**: `00HO35-1m`
- **Breakdown**:
  - `00`: Earth map
  - `HO`: Grid letters for longitude/latitude bands
  - `35`: Fine-grained grid position
  - `1m`: Surface level

## Usage Commands

### Create Tiles
```bash
./umap-engine.sh create-tile <lat> <lon> [depth] [type] [description]
```

### Initialize System
```bash
./umap-engine.sh init
```

### View Statistics
```bash
./umap-engine.sh stats
```

### Find Tiles
```bash
./umap-engine.sh find-tile <lat> <lon>
```

## File Organization

```
uMEMORY/core/
├── uMAP-00MK60-Earth.json              # Level 0: Planet
├── uMAP-01NA-North-America.json        # Level 1: Continental
├── uMAP-01EU-Europe.json
├── uMAP-01AS-Asia.json
├── uMAP-01AF-Africa.json
├── uMAP-01SA-South-America.json
├── uMAP-01OC-Oceania.json
├── uMAP-02NYC-New-York-City.json       # Level 2: Metropolitan
├── uMAP-03MAN-Manhattan.json           # Level 3: Borough/City
└── tiles/                              # Individual TILE files
    ├── uTILE-00HO35-New-York-City.json
    ├── uTILE-00GO34-Washington-DC.json
    └── ...

uCORE/mapping/
├── umap-engine.sh                      # Core engine
├── utile-location.sh                   # Location utilities
└── tile-index.json                     # Spatial index
```

## System Statistics
- **Total Tiles Created**: 33
- **Coverage**: Global with detailed urban areas
- **Depth Levels**: Surface (1m) focus
- **Types**: Continental, capital cities, boroughs, metropolitan areas

## Integration Features
- **WGS84 Coordinate System**: Standard geographic coordinates
- **Mercator Projection**: Web mapping standard
- **Spatial Indexing**: Fast tile lookup and spatial queries
- **Hierarchical Navigation**: Seamless zoom in/out capabilities
- **Real TILE Codes**: Generated from actual geographic coordinates

This system provides complete geographic coverage from planetary level down to individual landmarks and streets, with each level containing proper TILE codes and navigation links for seamless exploration.
