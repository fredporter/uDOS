#!/bin/bash

# Migration Script: Geographic Data to uMEMORY/system/geo
# Version: 1.4.0
# Purpose: Migrate map data files from uMEMORY/core to proper uDATA format in uMEMORY/system/geo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_DIR="$UDOS_ROOT/uMEMORY/core"
TARGET_DIR="$UDOS_ROOT/uMEMORY/system/geo"
BACKUP_DIR="$UDOS_ROOT/backup/geo-migration-$(date +%Y%m%d-%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🗺️  uDOS Geographic Data Migration v1.4${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create backup directory
echo -e "${YELLOW}📦 Creating backup directory...${NC}"
mkdir -p "$BACKUP_DIR"
echo "   Backup location: $BACKUP_DIR"
echo ""

# Create target directories
echo -e "${YELLOW}📁 Setting up target directories...${NC}"
mkdir -p "$TARGET_DIR/maps"
mkdir -p "$TARGET_DIR/tiles"
mkdir -p "$TARGET_DIR/cultural"
mkdir -p "$TARGET_DIR/documentation"
echo "   ✅ Created: $TARGET_DIR/maps"
echo "   ✅ Created: $TARGET_DIR/tiles"
echo "   ✅ Created: $TARGET_DIR/cultural"
echo "   ✅ Created: $TARGET_DIR/documentation"
echo ""

# Initialize migration counters
map_count=0
tile_count=0
cultural_count=0
doc_count=0
empty_count=0
skipped_count=0

echo -e "${YELLOW}🔄 Starting file migration and format validation...${NC}"
echo ""

# Function to convert filename to proper uDATA format
convert_filename() {
    local filename="$1"
    local target_dir="$2"

    # Handle different file types
    case "$filename" in
        "MAP-"*)
            # Convert MAP-XX-Name.json to uDATA-MAP-XX-Name.json
            echo "uDATA-${filename}"
            ;;
        "uMAP-"*)
            # Already has u prefix, just add uDATA
            echo "uDATA-${filename}"
            ;;
        "uTILE-"*)
            # Already has proper format, just add uDATA prefix
            echo "uDATA-${filename}"
            ;;
        "uDATA-"*)
            # Already in correct format
            echo "$filename"
            ;;
        "map-"*)
            # Convert lowercase map to uppercase
            new_name=$(echo "$filename" | sed 's/map-/MAP-/')
            echo "uDATA-${new_name}"
            ;;
        *)
            # Default case
            echo "uDATA-${filename}"
            ;;
    esac
}

# Function to determine target subdirectory
get_target_subdir() {
    local filename="$1"

    case "$filename" in
        *"Cultural"* | *"cultural"*)
            echo "cultural"
            ;;
        *".md")
            echo "documentation"
            ;;
        "uTILE-"* | "TILE-"*)
            echo "tiles"
            ;;
        "uMAP-"* | "MAP-"* | "map-"*)
            echo "maps"
            ;;
        *)
            echo "maps"  # Default to maps
            ;;
    esac
}

# Function to validate and enhance uDATA format
validate_udata_format() {
    local filepath="$1"
    local filename="$(basename "$filepath")"

    # Check if file is empty
    if [ ! -s "$filepath" ]; then
        echo "EMPTY"
        return 1
    fi

    # Check if file is valid JSON
    if ! python3 -m json.tool "$filepath" > /dev/null 2>&1; then
        echo "INVALID_JSON"
        return 1
    fi

    # Check if it has basic uDATA structure
    if python3 -c "
import json, sys
try:
    with open('$filepath', 'r') as f:
        data = json.load(f)
    if 'metadata' in data:
        print('VALID_UDATA')
        sys.exit(0)
    else:
        print('NEEDS_METADATA')
        sys.exit(0)
except:
    print('INVALID')
    sys.exit(1)
" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Process all files in source directory
for file in "$SOURCE_DIR"/*.json "$SOURCE_DIR"/*.md; do
    if [ -f "$file" ]; then
        filename="$(basename "$file")"

        # Skip README.md
        if [ "$filename" = "README.md" ]; then
            continue
        fi

        echo -e "${BLUE}Processing: $filename${NC}"

        # Backup original file
        cp "$file" "$BACKUP_DIR/"

        # Validate file format
        validation_result=$(validate_udata_format "$file")

        if [ "$validation_result" = "EMPTY" ]; then
            echo "   ⚠️  File is empty - moving to backup only"
            ((empty_count++))
            continue
        fi

        # Determine target subdirectory and new filename
        target_subdir=$(get_target_subdir "$filename")
        new_filename=$(convert_filename "$filename" "$target_subdir")
        target_path="$TARGET_DIR/$target_subdir/$new_filename"

        # Copy and potentially enhance the file
        if [ "$validation_result" = "VALID_UDATA" ]; then
            cp "$file" "$target_path"
            echo "   ✅ Migrated to: $target_subdir/$new_filename"
        elif [ "$validation_result" = "NEEDS_METADATA" ]; then
            # Add basic metadata structure
            echo "   🔧 Adding metadata structure..."
            python3 << EOF
import json
import datetime

try:
    with open('$file', 'r') as f:
        data = json.load(f)

    # Add metadata if missing
    if 'metadata' not in data:
        data['metadata'] = {
            'name': '${filename%.*}',
            'description': 'Geographic data migrated from uMEMORY/core',
            'version': '1.4.0',
            'format': 'uDATA',
            'migrated': datetime.datetime.now().isoformat(),
            'original_file': '$filename'
        }

    with open('$target_path', 'w') as f:
        json.dump(data, f, indent=2)

    print('   ✅ Enhanced and migrated to: $target_subdir/$new_filename')
except Exception as e:
    print(f'   ❌ Error processing file: {e}')
EOF
        else
            echo "   ❌ Invalid file format - skipped"
            ((skipped_count++))
            continue
        fi

        # Update counters
        case "$target_subdir" in
            "maps") ((map_count++)) ;;
            "tiles") ((tile_count++)) ;;
            "cultural") ((cultural_count++)) ;;
            "documentation") ((doc_count++)) ;;
        esac
    fi
done

# Process tiles subdirectory
echo ""
echo -e "${YELLOW}🔄 Processing tiles subdirectory...${NC}"

for file in "$SOURCE_DIR/tiles"/*.json; do
    if [ -f "$file" ]; then
        filename="$(basename "$file")"

        echo -e "${BLUE}Processing tile: $filename${NC}"

        # Backup original file
        cp "$file" "$BACKUP_DIR/"

        # Validate file format
        validation_result=$(validate_udata_format "$file")

        if [ "$validation_result" = "EMPTY" ]; then
            echo "   ⚠️  File is empty - moving to backup only"
            ((empty_count++))
            continue
        fi

        # Convert filename and set target
        new_filename=$(convert_filename "$filename" "tiles")
        target_path="$TARGET_DIR/tiles/$new_filename"

        # Copy and potentially enhance the file
        if [ "$validation_result" = "VALID_UDATA" ]; then
            cp "$file" "$target_path"
            echo "   ✅ Migrated to: tiles/$new_filename"
        elif [ "$validation_result" = "NEEDS_METADATA" ]; then
            # Add basic metadata structure
            echo "   🔧 Adding metadata structure..."
            python3 << EOF
import json
import datetime

try:
    with open('$file', 'r') as f:
        data = json.load(f)

    # Add metadata if missing
    if 'metadata' not in data:
        data['metadata'] = {
            'name': '${filename%.*}',
            'description': 'Geographic tile data migrated from uMEMORY/core/tiles',
            'version': '1.4.0',
            'format': 'uDATA',
            'migrated': datetime.datetime.now().isoformat(),
            'original_file': '$filename'
        }

    with open('$target_path', 'w') as f:
        json.dump(data, f, indent=2)

    print('   ✅ Enhanced and migrated to: tiles/$new_filename')
except Exception as e:
    print(f'   ❌ Error processing tile: {e}')
EOF
        else
            echo "   ❌ Invalid tile format - skipped"
            ((skipped_count++))
            continue
        fi

        ((tile_count++))
    fi
done

# Create README for the new geo directory
echo ""
echo -e "${YELLOW}📝 Creating documentation...${NC}"

cat > "$TARGET_DIR/README.md" << 'EOF'
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
EOF

# Move deprecated source files to backup/legacy
echo ""
echo -e "${YELLOW}🗂️  Moving source files to deprecated location...${NC}"

mkdir -p "$UDOS_ROOT/uMEMORY/system/deprecated/geo-core-legacy"

# Move the original files to deprecated location
cp -r "$SOURCE_DIR"/* "$UDOS_ROOT/uMEMORY/system/deprecated/geo-core-legacy/"

# Clean up original location (keeping README)
for file in "$SOURCE_DIR"/*.json "$SOURCE_DIR"/*.md; do
    if [ -f "$file" ] && [ "$(basename "$file")" != "README.md" ]; then
        rm "$file"
    fi
done

# Clean up tiles directory
if [ -d "$SOURCE_DIR/tiles" ]; then
    rm -rf "$SOURCE_DIR/tiles"
fi

# Update the core README to reflect the migration
cat > "$SOURCE_DIR/README.md" << 'EOF'
# uMEMORY Core Directory

This directory previously contained geographic map data which has been migrated to the proper location:

**New Location:** `uMEMORY/system/geo/`

The geographic data has been reorganized into:
- `uMEMORY/system/geo/maps/` - Continental and regional maps
- `uMEMORY/system/geo/tiles/` - City and metropolitan tiles
- `uMEMORY/system/geo/cultural/` - Cultural reference data
- `uMEMORY/system/geo/documentation/` - Geographic documentation

All files have been converted to proper uDATA format with consistent naming conventions.

Original files are preserved in `uMEMORY/system/deprecated/geo-core-legacy/`
EOF

# Generate final report
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Geographic Data Migration Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Migration Summary:${NC}"
echo "  📍 Maps migrated: $map_count"
echo "  🗺️  Tiles migrated: $tile_count"
echo "  🏛️  Cultural files: $cultural_count"
echo "  📚 Documentation: $doc_count"
echo "  ⚠️  Empty files: $empty_count"
echo "  ❌ Skipped files: $skipped_count"
echo ""
echo -e "${BLUE}Directories Created:${NC}"
echo "  📂 $TARGET_DIR/maps/"
echo "  📂 $TARGET_DIR/tiles/"
echo "  📂 $TARGET_DIR/cultural/"
echo "  📂 $TARGET_DIR/documentation/"
echo ""
echo -e "${BLUE}Backup Location:${NC}"
echo "  💾 $BACKUP_DIR"
echo ""
echo -e "${BLUE}Legacy Location:${NC}"
echo "  🗃️  $UDOS_ROOT/uMEMORY/system/deprecated/geo-core-legacy/"
echo ""
echo -e "${GREEN}Geographic data is now properly organized and ready for uDOS v1.4!${NC}"
echo ""
