# TILE Commands - Geographic Reference System

Complete guide to the TILE geographic data and mapping system (v1.0.20b)

---

## 🗺️ Overview

The **TILE System** provides comprehensive offline geographic reference data including 250 world cities, 50 countries, 120 timezones, terrain types, and climate zones. All data ships with uDOS and requires no internet connection.

### Key Features
- **250 Cities** with TIZO codes and coordinates
- **50 Countries** with ISO codes and demographics
- **120 Timezones** with DST rules
- **24 Terrain Types** with elevation data
- **18 Climate Zones** (Köppen classification)
- **Unit Conversions** (temperature, distance, mass)
- **Route Planning** with Haversine distance calculations

---

## 📍 Location Commands

### TILE INFO
Get comprehensive information about any city or country

**Usage**:
```bash
TILE INFO <location>
```

**Examples**:
```bash
🔮 > TILE INFO Tokyo
🏙️  Tokyo, JP
================================================
📍 Location:
   Coordinates: 35.6762°, 139.6503°
   TIZO Code: T001
   Elevation: 40 meters

🌍 Demographics:
   Population: 37,400,000
   Region: Asia-Pacific

🌡️  Climate: subtropical
🕐 Time: Asia/Tokyo

🔮 > TILE INFO France
🌏 France
================================================
🏛️  Basic Info:
   ISO Code: FR / FRA
   Capital: Paris
   Region: Western Europe

📍 Geography:
   Coordinates: 46.2276°, 2.2137°
   Area: 551,695 km²

🌍 Demographics:
   Population: 67,391,582

💬 Languages: French
💰 Currency: EUR
🕐 Timezone: Europe/Paris
```

---

### TILE SEARCH
Search for cities or countries by name

**Usage**:
```bash
TILE SEARCH <query>
```

**Examples**:
```bash
🔮 > TILE SEARCH Paris
🔍 Search Results (3):
🏙️  Paris, FR (TIZO: T023)
🏙️  Paris, US (TIZO: T145)
🌏 Paraguay (PY)

🔮 > TILE SEARCH New
🔍 Search Results (8):
🏙️  New York, US (TIZO: T087)
🏙️  New Delhi, IN (TIZO: T002)
🌏 New Zealand (NZ)
...
```

---

### TILE NEARBY
Find cities within a specified radius

**Usage**:
```bash
TILE NEARBY <location> [radius_km]
```

**Default radius**: 500km

**Examples**:
```bash
🔮 > TILE NEARBY London 500
🗺️  Cities near London (within 500km):
==================================================
  109.2km - Birmingham, GB
  212.5km - Amsterdam, NL
  344.0km - Paris, FR
  410.8km - Frankfurt, DE
  491.3km - Brussels, BE

🔮 > TILE NEARBY Tokyo 1000
🗺️  Cities near Tokyo (within 1000km):
==================================================
  397.5km - Osaka, JP
  514.2km - Nagoya, JP
  751.8km - Seoul, KR
  892.1km - Shanghai, CN
```

**How it works**: Uses Haversine formula to calculate great-circle distances between coordinates with accuracy to within a few meters.

---

## 🌍 Geographic Data Commands

### TILE WEATHER
Get climate zone information for any location

**Usage**:
```bash
TILE WEATHER <location>
```

**Examples**:
```bash
🔮 > TILE WEATHER Sydney
🌡️  Climate: Sydney, AU
==================================================
🌍 Climate Type: Temperate (Cfb)

🌡️  Temperature Range: 8°C to 26°C
🌧️  Annual Rainfall: 1200-1500mm

📝 Description: Mild temperatures year-round, frequent rain
🌿 Vegetation: Temperate rainforest
📅 Seasons: 4

📍 Similar Locations: Western Europe, New Zealand, Pacific Northwest

🔮 > TILE WEATHER Cairo
🌡️  Climate: Cairo, EG
==================================================
🌍 Climate Type: Hot Desert (BWh)

🌡️  Temperature Range: 5°C to 50°C
🌧️  Annual Rainfall: 0-250mm

📝 Description: Extremely hot and dry
🌿 Vegetation: Sparse desert plants
📅 Seasons: 2

📍 Similar Locations: Sahara, Arabian Desert, Death Valley
```

**Köppen Climate Codes**:
- **Af**: Tropical Rainforest
- **Am**: Tropical Monsoon
- **Aw**: Tropical Savanna
- **BWh**: Hot Desert
- **BWk**: Cold Desert
- **BS**: Semi-Arid Steppe
- **Cs**: Mediterranean
- **Cfa**: Humid Subtropical
- **Cfb**: Oceanic
- **Dfa**: Warm Continental
- **Dfb**: Cool Continental
- **Dfc**: Subarctic
- **ET**: Tundra
- **EF**: Ice Cap
- **H**: Highland/Alpine

---

### TILE TIMEZONE
Detailed timezone information with DST rules

**Usage**:
```bash
TILE TIMEZONE <location>
```

**Examples**:
```bash
🔮 > TILE TIMEZONE New_York
🕐 America/New_York
==================================================
⏰ Time Offsets:
   Standard: UTC-05:00
   DST: UTC-04:00
   Zone: EST/EDT

🌍 DST Information:
   Active: Yes
   Starts: 2nd Sunday March 2:00 AM
   Ends: 1st Sunday November 2:00 AM

🏙️  Major Cities: New York, Washington DC, Miami, Detroit, Boston
🌏 Countries: US

🔮 > TILE TIMEZONE Tokyo
🕐 Asia/Tokyo
==================================================
⏰ Time Offsets:
   Standard: UTC+09:00
   DST: UTC+09:00
   Zone: JST

🌍 DST Information:
   Active: No

🏙️  Major Cities: Tokyo, Osaka, Yokohama, Nagoya, Sapporo
🌏 Countries: JP
```

**Features**:
- 120 IANA timezone definitions
- UTC offset ranges from UTC-12 to UTC+14
- DST start/end rules by region
- Major cities per timezone
- No-DST zones clearly marked

---

### TILE TERRAIN
Terrain type definitions and characteristics

**Usage**:
```bash
TILE TERRAIN [type]     # Specific type or list all
```

**Examples**:
```bash
🔮 > TILE TERRAIN ocean
🗺️  Ocean Terrain
==================================================
🎨 Visuals:
   ASCII: ≈
   Symbol: ~
   Color: blue

📐 Elevation Range: -11000m to 0m
🚶 Traversable: No
💧 Water Source: Yes

📝 Description: Deep ocean waters

🔮 > TILE TERRAIN mountains
🗺️  Mountains Terrain
==================================================
🎨 Visuals:
   ASCII: ▲
   Symbol: ^
   Color: brown

📐 Elevation Range: 1000m to 5000m
🚶 Traversable: Yes
💧 Water Source: No

📝 Description: Mountain ranges

🔮 > TILE TERRAIN
🗺️  Terrain Types:
==================================================
≈ Ocean - Deep ocean waters
∼ Coastal Water - Shallow coastal waters and seas
○ Lake - Freshwater lakes
~ River - Flowing rivers and streams
· Beach - Sandy coastal beaches
∴ Desert - Arid desert terrain
─ Plains - Flat grasslands and plains
" Grassland - Grassy savanna
♣ Forest - Dense woodland forest
♠ Jungle - Tropical rainforest
∩ Hills - Rolling hills
▲ Mountains - Mountain ranges
△ High Mountains - High altitude peaks with snow
≡ Glacier - Permanent ice fields
∙ Tundra - Arctic/alpine tundra
█ Ice Sheet - Polar ice sheets
≋ Swamp - Wetlands and marshes
≈ Wetland - Seasonal wetlands
║ Canyon - Deep canyons and gorges
═ Plateau - High elevation plateaus
Δ Volcanic - Active or dormant volcanoes
▪ Urban - Cities and urban areas
≡ Farmland - Agricultural land
≈ Badlands - Eroded badlands terrain
```

**Terrain Categories**:
- **Water**: Ocean, coastal water, lake, river
- **Land**: Beach, desert, plains, grassland
- **Vegetation**: Forest, jungle, farmland
- **Elevation**: Hills, mountains, high mountains, plateau
- **Cold**: Glacier, ice sheet, tundra
- **Special**: Swamp, wetland, canyon, volcanic, urban, badlands

---

## 🧭 Navigation Commands

### TILE ROUTE
Calculate routes between locations with distance and bearing

**Usage**:
```bash
TILE ROUTE <from> <to>
```

**Examples**:
```bash
🔮 > TILE ROUTE Tokyo London
🧭 Route: Tokyo → London
==================================================
📍 From: Tokyo, JP
   TIZO: T001
   Timezone: Asia/Tokyo
   Climate: subtropical

📍 To: London, GB
   TIZO: T045
   Timezone: Europe/London
   Climate: temperate

📏 Distance: 9584.5 km (5954.7 miles)
🧭 Bearing: 312.4° (NW)

🔮 > TILE ROUTE Sydney Melbourne
🧭 Route: Sydney → Melbourne
==================================================
📍 From: Sydney, AU
   TIZO: T025
   Timezone: Australia/Sydney
   Climate: temperate

📍 To: Melbourne, AU
   TIZO: T024
   Timezone: Australia/Melbourne
   Climate: temperate

📏 Distance: 713.4 km (443.2 miles)
🧭 Bearing: 232.1° (SW)
```

**Features**:
- **Haversine Formula**: Accurate great-circle distance calculations
- **Bearing Calculation**: 8-point compass directions (N, NE, E, SE, S, SW, W, NW)
- **Climate Comparison**: See climate differences between locations
- **Timezone Info**: Time zone details for both endpoints
- **Dual Units**: Displays both metric (km) and imperial (miles)

---

## 🔧 Utility Commands

### TILE CONVERT
Convert between measurement units

**Usage**:
```bash
TILE CONVERT <value> <from_unit> <to_unit>
```

**Supported Conversions**:

#### Temperature
- **C** (Celsius) ↔ **F** (Fahrenheit) ↔ **K** (Kelvin)

#### Distance
- **km** (kilometers) ↔ **mi** (miles)
- **m** (meters) ↔ **ft** (feet)

#### Mass
- **kg** (kilograms) ↔ **lb** (pounds)

**Examples**:
```bash
# Temperature
🔮 > TILE CONVERT 100 C F
100°C = 212.00°F

🔮 > TILE CONVERT 32 F C
32°F = 0.00°C

🔮 > TILE CONVERT 0 C K
0°C = 273.15K

# Distance
🔮 > TILE CONVERT 100 km mi
100 km = 62.14 miles

🔮 > TILE CONVERT 10 mi km
10 miles = 16.09 km

🔮 > TILE CONVERT 100 m ft
100 m = 328.08 feet

# Mass
🔮 > TILE CONVERT 50 kg lb
50 kg = 110.23 lbs

🔮 > TILE CONVERT 150 lb kg
150 lbs = 68.04 kg
```

**Conversion Formulas**:
- C to F: `F = (C × 9/5) + 32`
- F to C: `C = (F - 32) × 5/9`
- C to K: `K = C + 273.15`
- km to mi: `mi = km × 0.621371`
- m to ft: `ft = m × 3.28084`
- kg to lb: `lb = kg × 2.20462`

---

## 📊 Data Coverage

### Geographic Database Statistics

| Category | Count | Coverage |
|:---------|------:|:---------|
| **Cities** | 250 | All continents, major metropolitan areas |
| **Countries** | 50 | Major nations, 50+ million population or significant |
| **Timezones** | 120 | All IANA zones, UTC-12 to UTC+14 |
| **Terrain Types** | 24 | Land, water, vegetation, elevation, climate |
| **Climate Zones** | 18 | Complete Köppen classification |

### Regional Coverage

| Region | Cities | Countries |
|:-------|-------:|----------:|
| **Asia** | 85 | 15 |
| **Europe** | 65 | 20 |
| **Americas** | 55 | 10 |
| **Africa** | 25 | 3 |
| **Oceania** | 20 | 2 |

### Elevation Range
- **Lowest**: -11,000m (ocean trenches)
- **Highest**: +9,000m (mountain peaks)
- **Most common**: 0-500m (coastal/lowland)

### Climate Distribution
- **Tropical**: 30% of cities
- **Temperate**: 45% of cities
- **Continental**: 15% of cities
- **Arid**: 7% of cities
- **Polar**: 3% of cities

---

## 🏗️ Data Architecture

### System Data Location
All TILE data is stored in `/data/system/`:

```
/data/system/
  ├── geography/
  │   ├── countries.json     # 50 countries
  │   ├── cities.json        # 250 cities with TIZO codes
  │   ├── timezones.json     # 120 IANA timezones
  │   ├── terrain.json       # 24 terrain types
  │   └── climate.json       # 18 climate zones
  ├── reference/
  │   ├── metric.json        # SI units
  │   └── imperial.json      # Imperial/US units
  └── graphics/
      ├── ascii_blocks.json
      └── teletext_mosaic.json
```

### Data Characteristics
- **Read-only**: System data cannot be modified by users
- **Version controlled**: Part of git repository
- **Offline-first**: All data ships with uDOS
- **JSON format**: Human-readable and parsable
- **Curated**: Quality-controlled reference data

---

## 🔗 Integration

### Works With

#### v1.0.3 MAP System
- Shares TIZO cell infrastructure
- Compatible with MAP commands
- Same coordinate system

#### v1.0.20 Knowledge Bank
- Stores user location preferences in PRIVATE tier
- Shares geographic data with COMMUNITY groups
- References PUBLIC knowledge base for survival info

### uCODE Format
All TILE commands use standard uCODE syntax:

```
[TILE|COMMAND*PARAM1*PARAM2*...]
```

Examples:
```
[TILE|INFO*Tokyo]
[TILE|SEARCH*Paris]
[TILE|NEARBY*London*500]
[TILE|ROUTE*Tokyo*London]
[TILE|CONVERT*100*km*mi]
```

---

## 💡 Use Cases

### Survival Planning
```bash
# Find nearest major cities
TILE NEARBY "Current Location" 1000

# Check climate for destination
TILE WEATHER "Target City"

# Calculate travel distance
TILE ROUTE "Start" "Destination"

# Understand terrain challenges
TILE TERRAIN mountains
```

### Knowledge Reference
```bash
# Look up country information
TILE INFO Germany

# Search for locations
TILE SEARCH water

# Get timezone for coordination
TILE TIMEZONE UTC+8
```

### Unit Calculations
```bash
# Temperature conversions for weather
TILE CONVERT 25 C F

# Distance planning
TILE CONVERT 500 km mi

# Weight/mass conversions
TILE CONVERT 70 kg lb
```

---

## 🎯 Technical Details

### Distance Calculations
Uses **Haversine Formula** for great-circle distances:

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
c = 2 × atan2(√a, √(1-a))
distance = R × c
```

Where:
- R = 6371 km (Earth's radius)
- Δlat = lat2 - lat1
- Δlon = lon2 - lon1

**Accuracy**: Within a few meters for most calculations

### Bearing Calculations
Calculates initial bearing between two points:

```
y = sin(Δlon) × cos(lat2)
x = cos(lat1) × sin(lat2) - sin(lat1) × cos(lat2) × cos(Δlon)
bearing = atan2(y, x)
```

**Output**: 0-360° converted to 8-point compass (N, NE, E, SE, S, SW, W, NW)

---

## 📚 Related Documentation

- [Command Reference](Command-Reference) - All uDOS commands
- [Mapping System](Mapping-System) - v1.0.3 MAP commands and TIZO cells
- [Knowledge Architecture](Knowledge-Architecture) - v1.0.20 4-Tier system
- [Getting Started](Getting-Started) - Basic uDOS usage

---

## 🚀 Future Enhancements

Planned for future versions:
- Expand to all 195 countries
- Add thousands more cities
- Real-time weather integration (when online)
- Interactive map visualization
- Elevation contour data
- Custom location bookmarks

---

*Complete geographic reference in your terminal - no internet required.*
