# uDOS User File Standards v2.0 - uMAP Integration
[20-90-02] uDOS-User-File-Standard-v2.md

## Overview

This document establishes comprehensive standards for uDOS user files with full integration of the uMAP global tile system, providing consistent location-aware file management across the entire uDOS ecosystem.

## File Type Classification

### 1. Natural Language Markdown Files
- **Extension**: `.md`
- **Content**: Pure markdown with no code blocks
- **Usage**: Documentation, notes, planning, communication
- **Location Coding**: Optional header with tile reference

### 2. Code-Containing Files  
- **Format**: `CODE-YYYY-MM-DD-HHMM-TILE.md`
- **Content**: Contains code blocks, scripts, or technical implementations
- **Tile Format**: uMAP tile coordinates (e.g., CQ43, AA24, AX14)
- **Location Coding**: Mandatory in filename

## uMAP Location System Integration

### Global Tile Coordinate System
The uDOS system uses the uMAP global coordinate system:
- **Grid**: 120×60 tiles covering the entire world
- **Format**: `[A-Z]{2}[0-9]{2}` (e.g., CQ43, AA24, AX14)
- **Coverage**: 50+ major cities with precise coordinates
- **Database**: Located at `uCORE/datasets/mapping/datasets/locationMap.json`

### Location Detection
```bash
# Automatic location detection using uMAP
./uMEMORY/scripts/explicit/detect-location-umap.sh

# Example output: CQ43 (Sydney, Australia)
```

### Supported Locations (Sample)
- **CQ43**: Sydney, Australia
- **CQ46**: Melbourne, Australia  
- **AA24**: Mexico City, Mexico
- **AX14**: London, UK
- **AY14**: Paris, France
- **AJ17**: New York, USA
- **CJ28**: Tokyo, Japan
- **BD12**: Moscow, Russia

## File Naming Standards

### Natural Language Files
```
filename.md
user-notes.md
project-documentation.md
```

### Code Files
```
CODE-2025-08-16-1605-CQ43.md
CODE-2025-08-16-1410-AX14.md
CODE-2025-08-16-0930-AA24.md
```

### System Integration Files
```
MOVELOG-001-2025-08-16-1605-CQ43.md
BACKUP-2025-08-16-CQ43.md
CONFIG-2025-08-16-CQ43.md
```

## Format Limits and Standards

### Line Length Limits
- **Maximum**: 80 characters per line
- **Enforcement**: Automatic validation
- **Overflow**: MOVELOG system for longer content

### Column Display
- **Standard**: 10 characters per column for structured data
- **Alignment**: Left-aligned for readability
- **Spacing**: Consistent padding

### Shortcode Format
- **Length**: Maximum 8 characters
- **Pattern**: Alphanumeric only
- **Usage**: Quick reference codes within documents

## Location Coding System

### Header Format
```markdown
# Document Title
[CC-NN-NN] filename.md

Where:
- CC: Category code (20, 10, 30, etc.)
- NN-NN: Sequential numbering
- Location tile embedded in document context
```

### Location Context
```markdown
**Location**: CQ43 (Sydney, Australia)
**Coordinates**: -33.8688°S, 151.2093°E
**Timezone**: Australia/Sydney
**Region**: Oceania
```

## Validation System

### File Format Validation
```bash
# Validate single file
./uMEMORY/scripts/explicit/validate-files.sh filename.md

# Validate multiple files
./uMEMORY/scripts/explicit/validate-files.sh *.md
```

### Validation Checks
- ✅ Filename format compliance
- ✅ uMAP tile format validation
- ✅ Line length limits
- ✅ Shortcode format
- ✅ Content type matching

## MOVELOG Overflow System

### Automatic Overflow Handling
When content exceeds 80 characters per line:
1. Original entry truncated to 80 characters
2. Full content moved to MOVELOG file
3. Reference link created in original location
4. Daily log integration maintained

### MOVELOG Format
```
MOVELOG-001-2025-08-16-1605-CQ43.md
├── Full content preservation
├── Metadata and timestamps
├── Location and tile reference
└── Link back to original context
```

## Integration with uDOS Systems

### uMAP System Integration
- **Database**: Full access to 50+ city coordinates
- **Validation**: Real-time tile verification
- **Timezone**: Automatic timezone mapping
- **Geographic**: Full geographic context

### uMEMORY Structure Integration  
- **Private Files**: `uMEMORY/user/explicit/`
- **Shared Files**: `uMEMORY/user/public/`
- **Scripts**: `uMEMORY/scripts/explicit/`
- **Logs**: `uMEMORY/logs/explicit/`

### Role-Based Access
- **wizard**: Full access to all location data
- **sorcerer**: Development access with location awareness
- **ghost**: Read-only access to public location data
- **imp**: Guided access with automatic location detection

## Migration from Legacy System

### Automatic Migration
Files using legacy location codes (NYC001, LON023, etc.) are automatically detected and migration assistance provided.

### Migration Tools
```bash
# Migrate legacy location codes
./uCORE/scripts/migrate-legacy-locations.sh

# Verify migration
./uMEMORY/scripts/explicit/validate-files.sh --migration-check
```

## Best Practices

### Location Awareness
1. Always include location context in code files
2. Use consistent tile format (uMAP standard)  
3. Validate location codes before file creation
4. Update location when traveling or relocating

### File Organization
1. Group files by location when relevant
2. Use location-aware naming for distributed work
3. Maintain location history in user templates
4. Consider timezone implications for timestamps

### Privacy and Sharing
1. Location data private by default (explicit)
2. Conscious choice required for location sharing
3. Role-based access to location-sensitive data
4. User control over geographic data exposure

---

## Implementation Status

- ✅ uMAP integration complete
- ✅ Global tile system operational  
- ✅ Location detection functional
- ✅ File validation updated
- ✅ MOVELOG system compatible
- ✅ Role-based access implemented
- ✅ Migration tools available

*This standard supersedes all previous location coding systems and provides full integration with the uDOS uMAP global coordinate system.*

---
*Document Version: 2.0*  
*Last Updated: 2025-08-16*  
*Location: CQ43 (Sydney, Australia)*  
*uDOS System: v1.2 with uMAP Integration*
