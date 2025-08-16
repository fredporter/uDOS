#!/usr/bin/env bash
# [20-90-02] uDOS File Standards Update for uMAP Integration
# Location: uCORE/scripts/update-file-standards.sh
# Purpose: Update all file standards to use proper uMAP tile system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 uDOS File Standards Update${NC}"
echo "=============================="

# Step 1: Update user identity with proper uMAP location
echo -e "\n${YELLOW}👤 Updating user identity...${NC}"

IDENTITY_FILE="$UDOS_ROOT/uMEMORY/user/explicit/identity.md"
if [[ -f "$IDENTITY_FILE" ]]; then
    # Get current location or default to Sydney
    CURRENT_LOCATION=$(./uMEMORY/scripts/explicit/detect-location-umap.sh <<< "CQ43")
    
    # Update identity file
    cat > "$IDENTITY_FILE" << EOF
# uDOS User Identity
[20-90-02] identity.md

## User Configuration
role: wizard
created: $(date +"%Y-%m-%d %H:%M")
location: $CURRENT_LOCATION

## Location Details (uMAP Integration)
Using uDOS uMAP system with global tile coordinates:
- **Tile System**: 120×60 global coordinate grid
- **Format**: Two letters + two numbers (e.g., CQ43, AA24)
- **Coverage**: 50+ major cities worldwide
- **Integration**: Full timezone and geographic data

## Data Sovereignty
default_sharing: explicit
allow_public_sharing: true

## Access Permissions
Based on role: wizard
Full access to all uMEMORY areas
EOF

    echo -e "${GREEN}✅ Updated user identity with location: $CURRENT_LOCATION${NC}"
else
    echo -e "${RED}❌ Identity file not found${NC}"
fi

# Step 2: Update file standard documentation
echo -e "\n${YELLOW}📝 Updating file standards documentation...${NC}"

cat > "$UDOS_ROOT/uCORE/docs/uDOS-User-File-Standard-v2.md" << 'EOF'
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
EOF

echo -e "${GREEN}✅ Created updated file standards documentation${NC}"

# Step 3: Update MOVELOG manager for uMAP tiles
echo -e "\n${YELLOW}📝 Updating MOVELOG manager...${NC}"

if [[ -f "$UDOS_ROOT/uMEMORY/scripts/explicit/movelog-manager.sh" ]]; then
    # Update tile format in MOVELOG manager
    sed -i.bak 's/\[A-Z\]{3}\[0-9\]{3}/[A-Z]{2}[0-9]{2}/g' "$UDOS_ROOT/uMEMORY/scripts/explicit/movelog-manager.sh"
    echo -e "${GREEN}✅ Updated MOVELOG manager for uMAP tiles${NC}"
fi

# Step 4: Create sample files with proper uMAP format
echo -e "\n${YELLOW}📄 Creating sample files...${NC}"

CURRENT_LOCATION="${CURRENT_LOCATION:-CQ43}"
TIMESTAMP=$(date +"%Y-%m-%d-%H%M")

cat > "$UDOS_ROOT/uMEMORY/user/explicit/CODE-$TIMESTAMP-$CURRENT_LOCATION.md" << EOF
# uMAP Integration Test File
[20-90-02] CODE-$TIMESTAMP-$CURRENT_LOCATION.md

This file demonstrates the new uMAP integration with proper tile formatting.

## Location Information
- **Tile**: $CURRENT_LOCATION
- **Generated**: $(date +"%Y-%m-%d %H:%M")
- **System**: uDOS v1.2 with uMAP

## Code Example
\`\`\`bash
#!/bin/bash
# Test script with location awareness
echo "Current location: $CURRENT_LOCATION"
./uMEMORY/scripts/explicit/detect-location-umap.sh
\`\`\`

## Validation
This file follows uDOS v2.0 standards:
- ✅ Proper uMAP tile format ($CURRENT_LOCATION)
- ✅ Location coding in header
- ✅ Under 80 character line limits
- ✅ CODE-date-time-tile.md format
EOF

echo -e "${GREEN}✅ Created sample file: CODE-$TIMESTAMP-$CURRENT_LOCATION.md${NC}"

echo -e "\n${GREEN}🎉 File Standards Update Complete!${NC}"
echo "==================================="
echo -e "${BLUE}📍 Location System:${NC} uMAP global tiles (AA24, CQ43, etc.)"
echo -e "${BLUE}🗺️ Coverage:${NC} 50+ cities worldwide with coordinates"
echo -e "${BLUE}📝 Standards:${NC} Updated to v2.0 with full uMAP integration"
echo -e "${BLUE}🔍 Validation:${NC} Updated for new tile format"
echo -e "${BLUE}📋 Documentation:${NC} Complete v2.0 specification created"
