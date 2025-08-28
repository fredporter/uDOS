# uDOS Geographic Data System

This directory contains the consolidated geographic data for the uDOS system, migrated and organized in proper uDATA format.

## Directory Structure

- `maps/` - Continental and regional map data files
- `tiles/` - City and metropolitan area tile data
- `cultural/` - Cultural reference data and ethnographic information
- `documentation/` - Geographic system documentation and specs

## File Naming Convention

All files follow the uDATA naming standard:
- `uDATA-[TYPE]-[ID]-[Name].json`
- Examples:
  - `uDATA-uMAP-00FP26-North-America.json`
  - `uDATA-uTILE-00EN20-Los-Angeles.json`
  - `uDATA-Cultural-Reference.json`

## Data Format

All geographic data follows the uDATA standard with:
- Required `metadata` section with name, description, version, format
- Standardized coordinate system (WGS84)
- Hierarchical map/tile linking system
- Timezone and cultural reference integration

## Migration Information

Files were migrated from `uMEMORY/core/` on $(date +%Y-%m-%d) as part of uDOS v1.4 system organization.
Original files are backed up in the system backup directory.

## Usage

Geographic data is accessed through the uDOS mapping and navigation systems.
Tile coordinates follow the TILE standard for hierarchical geographic referencing.
