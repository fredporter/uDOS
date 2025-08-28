# uCORE JSON Processing System

**TypeScript-based JSON data processing and template system**

## Overview

This directory contains the TypeScript/Node.js system for processing JSON data and generating templates within the uDOS ecosystem.

## Structure

```
uCORE/json/
├── src/                   # TypeScript source code
│   ├── data/             # Data processing modules
│   ├── templates/        # Template processing
│   ├── utils/            # Utility functions
│   └── index.ts          # Main entry point
├── package.json          # Node.js project configuration
├── tsconfig.json         # TypeScript configuration
└── README.md             # This file
```

## Components

### Data Processing (`src/data/`)
- **`worldMap.py`** - Python module for world map data processing
- Geographic coordinate processing
- Data validation and transformation

### Template Processing (`src/templates/`)
- **`baseMap.uTemplate`** - Base template for map generation
- Template variable substitution
- Dynamic content generation

### Utilities (`src/utils/`)
- **`parser.ts`** - JSON parsing and validation utilities
- Data format conversion
- Error handling and validation

## Features

### JSON Data Processing
- **Parse and validate** JSON datasets from uMEMORY
- **Transform data** between different formats
- **Merge datasets** for comprehensive analysis
- **Export capabilities** to CSV, YAML, HTML formats

### Template System
- **Variable substitution** with dynamic data
- **Template inheritance** and composition
- **Validation** of template definitions
- **Batch processing** for multiple templates

### Integration Points
- **uMEMORY Data**: Processes data files from uMEMORY/core, uMEMORY/system
- **Template Output**: Generates content using uMEMORY/templates
- **Configuration**: Uses settings from uCORE/config
- **Processing Scripts**: Integrates with uCORE/code scripts

## Usage

### Development Mode
```bash
cd uCORE/json
npm install
npm run dev
```

### Build and Run
```bash
npm run build
npm start
```

### Template Generation
```bash
npm run map:generate
npm run map:region
npm run map:city
```

## TypeScript Configuration

### Project Setup
- **TypeScript 5.0+**: Modern TypeScript features
- **Node.js 16+**: Minimum runtime requirements
- **ES Modules**: Modern module system
- **Strict typing**: Enhanced type safety

### Build System
- **`tsc`**: TypeScript compiler
- **`ts-node`**: Development execution
- **Source maps**: Debug support
- **Watch mode**: Development workflow

## Data Sources

The JSON processing system works with data from:
- **uMEMORY/core/**: Geographical and location data
- **uMEMORY/system/**: Command definitions and system data
- **uCORE/config/**: Template and system configuration

## Output Formats

Supports generation of:
- **JSON**: Structured data output
- **CSV**: Tabular data export
- **YAML**: Configuration format
- **HTML**: Web-ready content
- **Markdown**: Documentation format

## Integration with uDOS

### Command Integration
Access through uDOS shell commands:
```bash
json process <dataset>
json export <dataset> <format>
json validate <dataset>
template generate <template> <data>
```

### Script Integration
Integrates with uCORE/code scripts for:
- **Automated processing**: Batch data operations
- **Template generation**: Dynamic content creation
- **Data validation**: Quality assurance workflows
- **Export operations**: Multi-format output

## Development

### Local Development
```bash
# Install dependencies
npm install

# Run in development mode
npm run dev

# Build for production
npm run build

# Run tests (when implemented)
npm test
```

### Adding New Features
1. **Data processors**: Add to `src/data/`
2. **Template types**: Add to `src/templates/`
3. **Utilities**: Add to `src/utils/`
4. **Configuration**: Update `package.json` scripts

## Dependencies

### Development Dependencies
- **@types/node**: Node.js type definitions
- **typescript**: TypeScript compiler
- **ts-node**: TypeScript execution engine

### Runtime Dependencies
- **Node.js 16+**: JavaScript runtime
- **Built-in modules**: No external runtime dependencies

---

*uCORE JSON Processing - TypeScript-powered data processing and template generation*
