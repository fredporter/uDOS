# 🗺️ uDOS Template System - Source Code v1.7.1

This directory contains the TypeScript source code for the uDOS Template System with integrated map generation and dataset processing capabilities.

## 📁 Directory Structure

```
src/
├── README.md              # This file - documentation
├── index.ts               # Main map generator and CLI entry point
├── templates/             # Template processing utilities
└── utils/                 # Shared utility functions
    └── parser.ts          # Template parsing and validation
```

## 🎯 Core Components

### 🗺️ Map Generator (`index.ts`)
Primary TypeScript class for generating world maps using our comprehensive dataset system.

**Features:**
- 120×60 tile coordinate system (AX14 format)
- Full integration with locationMap, timezoneMap, mapTerrain datasets
- ASCII/emoji map rendering with proper coordinate placement
- Region-specific map generation
- City lookup by coordinates
- TypeScript type safety with proper interfaces

**Usage:**
```bash
npm run map generate          # Generate full world map
npm run map region Europe     # Generate European map
npm run map city AX14         # Get city info at coordinates
```

### 🧰 Template Utilities (`utils/parser.ts`)
TypeScript utilities for parsing and processing uDOS template files.

**Features:**
- YAML front matter parsing
- Template variable extraction ({{variable}} format)
- Dataset reference detection
- Template validation and error reporting
- Coordinate extraction from content
- Template rendering with variable substitution

## 🔗 Dataset Integration

The source code integrates with all uDOS datasets:

### 📍 Core Map Data
- **locationMap.json** - 52 cities with tile coordinates
- **mapTerrain.json** - 15 terrain symbols with priorities  
- **timezoneMap.json** - 38 global timezones

### 🌐 Supporting Data
- **countryMap.json** - Country codes and details
- **languageMap.json** - Language references
- **currencyMap.json** - Currency information
- **And 5 more specialized datasets**

## 🏗️ Build Process

### Prerequisites
```bash
# Install dependencies (when available)
npm install

# Dependencies needed:
# - @types/node: Node.js type definitions
# - typescript: TypeScript compiler
# - ts-node: Development runner
```

### Build Commands
```bash
npm run build        # Compile TypeScript to JavaScript
npm run dev          # Run in development mode
npm run start        # Run compiled JavaScript
```

## 🎨 Map Generation

### Coordinate System
- **Format:** Letter-Letter-Number-Number (e.g., AX14, CJ28)
- **Range:** A-DU columns (120 total), 01-60 rows
- **Resolution:** 7,200 total tiles
- **Symbols:** Unicode emoji for terrain and cities

### Rendering Priority
1. **Base Layer:** Ocean tiles (🟦) as default
2. **Terrain:** Applied based on priority in mapTerrain dataset
3. **Cities:** Override terrain with location-specific symbols
4. **Landmarks:** World wonders have highest priority

### Symbol Legend
- 🏙️ **Cities** - Population centers
- ✈️ **Airports** - International hubs
- 🗿 **World Wonders** - Historic landmarks
- 🏝️ **Islands** - Island territories
- ⛰️ **Mountains** - Mountain ranges
- 🟦 **Ocean** - Default background

## 🔧 Integration Points

### uCode Shell Integration
The map generator integrates with uCode shell commands:

```bash
# From ucode.sh
CHECK MAP <coordinates>     # Get location info
TIMEZONE <location>         # Get timezone data
LOCATION <query>           # Search locations
```

### Template System Integration
- Template variables automatically populated from datasets
- Dynamic coordinate validation
- Real-time location data in templates
- Cross-dataset referencing (location → timezone → country)

## 🧪 Development Notes

### TypeScript Configuration
- Target: ES2020 with Node.js types
- Strict mode enabled for type safety
- JSON module resolution for dataset loading
- Source maps for debugging

### Error Handling
- Graceful dataset loading failures
- Coordinate validation with bounds checking
- Template parsing error recovery
- File I/O error management

### Performance Considerations
- Lazy loading of large datasets
- Efficient grid initialization
- Minimal memory footprint for map storage
- Fast coordinate conversion algorithms

## 🚀 Future Enhancements

### Planned Features
- Interactive map rendering
- Real-time location tracking
- Dynamic terrain updates
- Multi-layer map support
- Export to multiple formats (SVG, PNG, PDF)

### Integration Targets
- VS Code extension for map viewing
- Web-based map interface
- CLI-based map exploration
- Template-driven map generation

---

*Generated for uDOS Template System v1.7.1 with comprehensive dataset integration*
