#!/bin/bash

# Enhanced Migration Script: Geographic Data to uMEMORY/system/geo
# Version: 1.4.1
# Purpose: Migrate map data files from deprecated location back to proper uDATA format in uMEMORY/system/geo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_DIR="$UDOS_ROOT/uMEMORY/system/deprecated/geo-core-legacy"
TARGET_DIR="$UDOS_ROOT/uMEMORY/system/geo"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🗺️  uDOS Geographic Data Recovery v1.4.1${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Initialize migration counters
map_count=0
tile_count=0
cultural_count=0
doc_count=0
empty_count=0
total_count=0

echo -e "${YELLOW}🔄 Processing files with corrected validation...${NC}"
echo ""

# Function to convert filename to proper uDATA format
convert_filename() {
    local filename="$1"

    # Handle different file types
    case "$filename" in
        "MAP-"*)
            # Convert MAP-XX-Name.json to uDATA-MAP-XX-Name.json
            echo "uDATA-${filename}"
            ;;
        "uMAP-"* | "uTILE-"*)
            # Already has u prefix, just add uDATA
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

# Process all files in source directory
for file in "$SOURCE_DIR"/*.json "$SOURCE_DIR"/*.md; do
    if [ -f "$file" ]; then
        filename="$(basename "$file")"

        # Skip README.md
        if [ "$filename" = "README.md" ]; then
            continue
        fi

        echo -e "${BLUE}Processing: $filename${NC}"
        ((total_count++))

        # Check if file is empty
        if [ ! -s "$file" ]; then
            echo "   ⚠️  File is empty - skipping"
            ((empty_count++))
            continue
        fi

        # Quick JSON validation
        if ! python3 -c "import json; json.load(open('$file', 'r'))" 2>/dev/null; then
            echo "   ❌ Invalid JSON format - skipping"
            continue
        fi

        # Determine target subdirectory and new filename
        target_subdir=$(get_target_subdir "$filename")
        new_filename=$(convert_filename "$filename")
        target_path="$TARGET_DIR/$target_subdir/$new_filename"

        # Copy the file
        cp "$file" "$target_path"
        echo "   ✅ Migrated to: $target_subdir/$new_filename"

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
        ((total_count++))

        # Check if file is empty
        if [ ! -s "$file" ]; then
            echo "   ⚠️  File is empty - skipping"
            ((empty_count++))
            continue
        fi

        # Quick JSON validation
        if ! python3 -c "import json; json.load(open('$file', 'r'))" 2>/dev/null; then
            echo "   ❌ Invalid JSON format - skipping"
            continue
        fi

        # Convert filename and set target
        new_filename=$(convert_filename "$filename")
        target_path="$TARGET_DIR/tiles/$new_filename"

        # Copy the file
        cp "$file" "$target_path"
        echo "   ✅ Migrated to: tiles/$new_filename"

        ((tile_count++))
    fi
done

# Generate status report
echo ""
echo -e "${YELLOW}📊 Generating inventory report...${NC}"

cat > "$TARGET_DIR/MIGRATION-REPORT.md" << EOF
# Geographic Data Migration Report

Migration completed: $(date)

## Files Processed

### Maps Directory (${map_count} files)
$(ls -la "$TARGET_DIR/maps/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "No files migrated")

### Tiles Directory (${tile_count} files)
$(ls -la "$TARGET_DIR/tiles/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "No files migrated")

### Cultural Directory (${cultural_count} files)
$(ls -la "$TARGET_DIR/cultural/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "No files migrated")

### Documentation Directory (${doc_count} files)
$(ls -la "$TARGET_DIR/documentation/" 2>/dev/null | grep -v "^total" | grep -v "^d" || echo "No files migrated")

## Migration Summary

- Total files processed: ${total_count}
- Maps migrated: ${map_count}
- Tiles migrated: ${tile_count}
- Cultural files: ${cultural_count}
- Documentation: ${doc_count}
- Empty files skipped: ${empty_count}

## Data Format Validation

All migrated files have been validated as proper JSON format.
Files follow uDATA naming convention: uDATA-[TYPE]-[ID]-[Name].json

## Next Steps

1. Verify all geographic data is accessible through uDOS mapping system
2. Test tile coordinate system and hierarchical navigation
3. Validate cultural reference integration
4. Update system documentation

Source files remain in deprecated location for backup purposes.
EOF

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Geographic Data Recovery Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Migration Summary:${NC}"
echo "  📍 Maps migrated: $map_count"
echo "  🗺️  Tiles migrated: $tile_count"
echo "  🏛️  Cultural files: $cultural_count"
echo "  📚 Documentation: $doc_count"
echo "  ⚠️  Empty files: $empty_count"
echo "  📊 Total processed: $total_count"
echo ""
echo -e "${BLUE}Target Location:${NC}"
echo "  📂 $TARGET_DIR/"
echo ""
echo -e "${BLUE}Report Generated:${NC}"
echo "  📄 $TARGET_DIR/MIGRATION-REPORT.md"
echo ""
echo -e "${GREEN}Geographic data is now properly organized for uDOS v1.4!${NC}"
echo ""
