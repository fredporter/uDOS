# uMapping System - v1.2.0

**uMapping** is the specialized geographic and cartographic system for uDOS v1.2, providing TypeScript-based map generation, coordinate systems, and comprehensive geographic datasets.

## 🗺️ System Overview
This system was moved from `uTemplate/` during v1.2 reorganization to create a dedicated mapping and geographic data management system.

## 📁 Directory Structure

```
uMapping/
├── README.md              # This documentation
├── package.json           # TypeScript project configuration
├── tsconfig.json          # TypeScript compiler configuration
├── src/                   # TypeScript source code
├── datasets/              # Geographic and system datasets (JSON)
└── mapping/               # Mapping utilities and scripts
```

## 🎯 Core Components

### 🔧 TypeScript Map Generator (`src/`)
Primary TypeScript application for generating world maps with:
- 120×60 tile coordinate system (AX14 format)
- Full integration with locationMap, timezoneMap, mapTerrain datasets
- ASCII/emoji map rendering with proper coordinate placement
- Region-specific map generation
- City lookup by coordinates
- TypeScript type safety with proper interfaces

### 🗄️ Geographic Datasets (`datasets/`)
Complete dataset collection with 355+ records across 11 categories:

#### Geographic & Location Data
- **locationMap.json** (52 cities) - Global city coordinates with map tile integration
- **mapTerrain.json** (15 symbols) - ASCII terrain symbols for cartography  
- **timezoneMap.json** (38 zones) - Global timezone data with map references
- **countryMap.json** (195 countries) - ISO country codes and regional data
- **cityMap.json** (50 cities) - Major world cities with coordinates

#### Language & Currency Data
- **languageMap.json** (50 languages) - ISO language codes and regional usage
- **currencyMap.json** (168 currencies) - Global currency data with exchange rates

#### System Integration Data
- **ucode-commands.json** (9 commands) - uDOS command definitions
- **template-definitions.json** (9 templates) - Template schema and metadata
- **template-system-config.json** - Template engine configuration
- **dataset-metadata.json** - Dataset versioning and schema definitions
- **shortcode-integration-v2.1.json** - Advanced shortcode system integration
- **shortcodes.json** - Core shortcode definitions
- **variable-system.json** - Template variable system configuration

### 🛠️ Mapping Utilities (`mapping/`)
Operational scripts and tools for map processing:
- **demo-map-integration.sh** - Integration demonstration
- **working-demo.sh** - Working examples and demos
- **process-map-shortcodes.sh** - Shortcode processing for maps
- **mission-locations.geojson** - GeoJSON mission location data
- **mission-mapping-demo.html** - HTML demo interface
- **map-output/** - Generated map files and outputs

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- TypeScript compiler
- uDOS v1.2 system

### Build and Run
```bash
# Install dependencies
npm install

# Compile TypeScript
npm run build

# Generate world map
npm run map

# Generate specific region
npm run map:region

# Generate city lookup
npm run map:city
```

## 📊 Dataset Statistics
- **Total Records**: 355+ entries across 11 datasets
- **Geographic Coverage**: 195 countries, 50+ major cities, 38 time zones
- **Language Support**: 50 languages with regional data
- **Currency Data**: 168 currencies with exchange rates
- **Map Resolution**: 120×60 tile coordinate system

## 🔗 Integration
The uMapping system integrates with:
- **uTemplate** - Geographic data for template variable substitution
- **uCode** - Map generation commands and shortcodes  
- **uMemory** - Location-based data storage and retrieval
- **Mission System** - Geographic mission planning and tracking

## 📋 Version History
- **v1.7.1** - Advanced mapping system with TypeScript implementation
- **v1.2.0** - Reorganized as dedicated uMapping system (July 2025)

---
*Part of uDOS v1.2 - A unified development and operations system*
