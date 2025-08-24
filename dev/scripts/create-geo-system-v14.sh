#!/bin/bash

# uCORE Geographic System Consolidation Script
# Version: 1.4.0
# Purpose: Rebuild mapping as geo system with uMEMORY/system/geo integration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🌍 uCORE Geographic System v1.4${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create backup
BACKUP_DIR="$UDOS_ROOT/backup/mapping-to-geo-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}📦 Creating backup of existing mapping system...${NC}"
if [ -d "$UDOS_ROOT/uCORE/mapping" ]; then
    cp -r "$UDOS_ROOT/uCORE/mapping" "$BACKUP_DIR/"
    echo "   💾 Backup created: $BACKUP_DIR/mapping"
fi
echo ""

# Create new geo system directory structure
echo -e "${YELLOW}🏗️  Creating new geographic system structure...${NC}"

mkdir -p "$UDOS_ROOT/uCORE/geo/engines"
mkdir -p "$UDOS_ROOT/uCORE/geo/processing"
mkdir -p "$UDOS_ROOT/uCORE/geo/visualization"
mkdir -p "$UDOS_ROOT/uCORE/geo/utilities"
mkdir -p "$UDOS_ROOT/uCORE/geo/templates"
mkdir -p "$UDOS_ROOT/uCORE/geo/cache"

echo "   ✅ Created uCORE/geo/engines/"
echo "   ✅ Created uCORE/geo/processing/"
echo "   ✅ Created uCORE/geo/visualization/"
echo "   ✅ Created uCORE/geo/utilities/"
echo "   ✅ Created uCORE/geo/templates/"
echo "   ✅ Created uCORE/geo/cache/"
echo ""

# Analyze and consolidate existing mapping files
echo -e "${YELLOW}🔍 Analyzing existing mapping components...${NC}"

declare -A file_purposes=(
    ["MAP-00-engine.sh"]="engines"
    ["umap-engine.sh"]="engines"
    ["tile-location.sh"]="utilities"
    ["utile-location.sh"]="utilities"
    ["process-map-shortcodes.sh"]="processing"
    ["working-demo.sh"]="utilities"
    ["mission-mapping-demo.html"]="templates"
    ["README.md"]="documentation"
    ["uMAP-SYSTEM-GUIDE.md"]="documentation"
)

# Move and consolidate files
echo -e "${YELLOW}🚚 Moving and consolidating mapping components...${NC}"

for file in "${!file_purposes[@]}"; do
    if [ -f "$UDOS_ROOT/uCORE/mapping/$file" ]; then
        target_dir="${file_purposes[$file]}"

        case "$target_dir" in
            "engines")
                new_name=$(echo "$file" | sed 's/MAP-00-engine/geo-core-engine/' | sed 's/umap-engine/geo-map-engine/')
                cp "$UDOS_ROOT/uCORE/mapping/$file" "$UDOS_ROOT/uCORE/geo/engines/$new_name"
                echo "   ✅ Moved $file → engines/$new_name"
                ;;
            "processing")
                new_name=$(echo "$file" | sed 's/process-map-shortcodes/geo-template-processor/')
                cp "$UDOS_ROOT/uCORE/mapping/$file" "$UDOS_ROOT/uCORE/geo/processing/$new_name"
                echo "   ✅ Moved $file → processing/$new_name"
                ;;
            "utilities")
                new_name=$(echo "$file" | sed 's/tile-location/geo-tile-resolver/' | sed 's/utile-location/geo-location-utils/' | sed 's/working-demo/geo-system-demo/')
                cp "$UDOS_ROOT/uCORE/mapping/$file" "$UDOS_ROOT/uCORE/geo/utilities/$new_name"
                echo "   ✅ Moved $file → utilities/$new_name"
                ;;
            "templates")
                cp "$UDOS_ROOT/uCORE/mapping/$file" "$UDOS_ROOT/uCORE/geo/templates/"
                echo "   ✅ Moved $file → templates/$file"
                ;;
            "documentation")
                cp "$UDOS_ROOT/uCORE/mapping/$file" "$UDOS_ROOT/uCORE/geo/$file"
                echo "   ✅ Moved $file → geo/$file"
                ;;
        esac
    fi
done

# Handle map-output directory
if [ -d "$UDOS_ROOT/uCORE/mapping/map-output" ]; then
    cp -r "$UDOS_ROOT/uCORE/mapping/map-output" "$UDOS_ROOT/uCORE/geo/visualization/"
    echo "   ✅ Moved map-output/ → visualization/map-output/"
fi

echo ""

echo -e "${GREEN}Geographic system structure created successfully!${NC}"
echo ""
echo -e "${BLUE}Next: Creating integrated geo components...${NC}"
echo ""
