#!/usr/bin/env bash
# [20-90-01] uDOS Memory Restructure Script
# Location: uCORE/scripts/memory-restructure.sh
# Purpose: Fix uMEMORY structure and implement proper uMAP tile system

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HIDDEN_MEMORY="$HOME/.uDOS/uMEMORY"
ROOT_MEMORY="$UDOS_ROOT/uMEMORY"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 uDOS Memory Restructure${NC}"
echo "============================="

# Step 1: Move uMEMORY back to root and remove hidden folder
echo -e "\n${YELLOW}📁 Moving uMEMORY back to root...${NC}"

if [[ -d "$HIDDEN_MEMORY" ]]; then
    echo -e "${BLUE}Found hidden uMEMORY at: $HIDDEN_MEMORY${NC}"
    
    # Remove symlink if it exists
    if [[ -L "$ROOT_MEMORY" ]]; then
        rm "$ROOT_MEMORY"
        echo -e "${GREEN}✅ Removed symlink${NC}"
    fi
    
    # Move the actual data back to root
    mv "$HIDDEN_MEMORY" "$ROOT_MEMORY"
    echo -e "${GREEN}✅ Moved uMEMORY back to root${NC}"
    
    # Remove the hidden directory structure
    rm -rf "$HOME/.uDOS"
    echo -e "${GREEN}✅ Removed hidden .uDOS directory${NC}"
fi

# Step 2: Remove sandbox from uMEMORY structure (sandbox is separate)
echo -e "\n${YELLOW}🗑️ Removing sandbox from uMEMORY...${NC}"
if [[ -d "$ROOT_MEMORY/sandbox" ]]; then
    rm -rf "$ROOT_MEMORY/sandbox"
    echo -e "${GREEN}✅ Removed uMEMORY/sandbox${NC}"
fi

# Step 3: Move system data to uCORE
echo -e "\n${YELLOW}📦 Moving system data to uCORE...${NC}"

# Create uCORE/datasets structure if needed
mkdir -p "$UDOS_ROOT/uCORE/datasets/location"
mkdir -p "$UDOS_ROOT/uCORE/templates/location"

# Move cities.json to uCORE/datasets (it's system data)
if [[ -f "$ROOT_MEMORY/generated/explicit/cities.json" ]]; then
    mv "$ROOT_MEMORY/generated/explicit/cities.json" "$UDOS_ROOT/uCORE/datasets/location/legacy-cities.json"
    echo -e "${GREEN}✅ Moved legacy cities.json to uCORE/datasets/location/${NC}"
fi

# Step 4: Update directory structure (remove sandbox, organize by data sovereignty)
echo -e "\n${YELLOW}🏗️ Updating uMEMORY structure...${NC}"

# Create proper structure without sandbox
mkdir -p "$ROOT_MEMORY"/{user,state,logs,missions,moves,milestones,scripts,templates,generated}/{explicit,public}

echo -e "${GREEN}✅ Updated uMEMORY structure${NC}"

# Step 5: Update .gitignore to exclude uMEMORY (but not hide it)
echo -e "\n${YELLOW}📝 Updating .gitignore...${NC}"

# Remove old entries and add clean uMEMORY exclusion
grep -v "uMEMORY" "$UDOS_ROOT/.gitignore" > "$UDOS_ROOT/.gitignore.tmp" || true
echo "" >> "$UDOS_ROOT/.gitignore.tmp"
echo "# uMEMORY - Private User Data (excluded from repository)" >> "$UDOS_ROOT/.gitignore.tmp"
echo "uMEMORY/" >> "$UDOS_ROOT/.gitignore.tmp"

mv "$UDOS_ROOT/.gitignore.tmp" "$UDOS_ROOT/.gitignore"
echo -e "${GREEN}✅ Updated .gitignore${NC}"

# Step 6: Create location system integration with uMAP
echo -e "\n${YELLOW}🗺️ Setting up uMAP integration...${NC}"

# Check if uMapping system exists
if [[ -f "$UDOS_ROOT/uCORE/datasets/mapping/datasets/locationMap.json" ]]; then
    echo -e "${GREEN}✅ Found existing uMAP system${NC}"
    
    # Create location detection script that uses proper uMAP tiles
    cat > "$ROOT_MEMORY/scripts/explicit/detect-location-umap.sh" << 'EOF'
#!/usr/bin/env bash
# uDOS Location Detection with uMAP Integration
# Uses proper AA24 format tiles from uMapping system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
LOCATION_MAP="$UDOS_ROOT/uCORE/datasets/mapping/datasets/locationMap.json"

# Get system timezone
SYSTEM_TZ=$(date +%Z 2>/dev/null || echo "UTC")

echo "🗺️  uDOS Location Detection (uMAP)"
echo "==================================="
echo ""
echo "System Timezone: $SYSTEM_TZ"

# Try to find closest city based on timezone
if command -v jq >/dev/null 2>&1 && [[ -f "$LOCATION_MAP" ]]; then
    echo "📍 Searching uMAP database..."
    
    # Get user's current location choice or detect
    if [[ -f "$UDOS_ROOT/uMEMORY/user/explicit/identity.md" ]]; then
        CURRENT_TILE=$(grep "location:" "$UDOS_ROOT/uMEMORY/user/explicit/identity.md" | cut -d: -f2 | xargs 2>/dev/null || echo "")
    fi
    
    if [[ -n "$CURRENT_TILE" ]]; then
        echo "Current location: $CURRENT_TILE"
        echo ""
        echo "Options:"
        echo "  1) Keep current location ($CURRENT_TILE)"
        echo "  2) Select new location from uMAP"
        echo ""
        read -p "Selection [1-2, default: 1]: " choice
        
        if [[ "$choice" == "2" ]]; then
            # Show available cities from uMAP
            echo ""
            echo "Available locations from uMAP:"
            jq -r '.data[] | "\(.tile) - \(.city), \(.country)"' "$LOCATION_MAP" | head -20
            echo ""
            read -p "Enter tile code (e.g., AA24): " new_tile
            
            # Validate tile exists
            if jq -e ".data[] | select(.tile == \"$new_tile\")" "$LOCATION_MAP" >/dev/null 2>&1; then
                echo "$new_tile"
            else
                echo "Invalid tile code, keeping current: $CURRENT_TILE"
                echo "$CURRENT_TILE"
            fi
        else
            echo "$CURRENT_TILE"
        fi
    else
        # First time setup - show available options
        echo "First time setup - select your location:"
        echo ""
        jq -r '.data[] | "\(.tile) - \(.city), \(.country)"' "$LOCATION_MAP" | head -20
        echo ""
        read -p "Enter tile code (e.g., AA24): " chosen_tile
        
        # Validate and return
        if jq -e ".data[] | select(.tile == \"$chosen_tile\")" "$LOCATION_MAP" >/dev/null 2>&1; then
            echo "$chosen_tile"
        else
            echo "Invalid tile code, using default: AA24"
            echo "AA24"
        fi
    fi
else
    echo "⚠️  uMAP database not found, using default"
    echo "AA24"
fi
EOF
    
    chmod +x "$ROOT_MEMORY/scripts/explicit/detect-location-umap.sh"
    echo -e "${GREEN}✅ Created uMAP location detection script${NC}"
    
else
    echo -e "${RED}❌ uMAP system not found at expected location${NC}"
fi

# Step 7: Create user template for location mapping
echo -e "\n${YELLOW}📋 Creating user location templates...${NC}"

cat > "$ROOT_MEMORY/templates/explicit/user-location-template.md" << 'EOF'
# User Location Template
[20-90-01] user-location-template.md

## Personal Location Configuration

### Current Location
**Tile**: {{LOCATION_TILE}}
**City**: {{LOCATION_CITY}}
**Country**: {{LOCATION_COUNTRY}}
**Coordinates**: {{LOCATION_COORDS}}

### Location History
- Previous locations used
- Travel and work locations
- Time zone preferences

### Location Preferences
- Default location for new files
- Privacy settings for location sharing
- Location-based automation preferences

## Integration with uMAP

This template integrates with the uDOS uMAP system which provides:
- Global 120×60 tile coordinate system
- Standardized tile format (AA24, CQ43, etc.)
- Integration with timezone data
- Geographic datasets for 50+ cities worldwide

To change location, use:
```bash
./uMEMORY/scripts/explicit/detect-location-umap.sh
```
EOF

echo -e "${GREEN}✅ Created user location template${NC}"

# Step 8: Update file validation to use uMAP tiles
echo -e "\n${YELLOW}🔍 Updating file validation for uMAP tiles...${NC}"

if [[ -f "$ROOT_MEMORY/scripts/explicit/validate-files.sh" ]]; then
    # Update the tile validation pattern
    sed -i.bak 's/\[A-Z\]{3}\[0-9\]{3}/[A-Z]{2}[0-9]{2}/g' "$ROOT_MEMORY/scripts/explicit/validate-files.sh"
    echo -e "${GREEN}✅ Updated validation for uMAP tile format${NC}"
fi

echo -e "\n${GREEN}🎉 uMEMORY Restructure Complete!${NC}"
echo "=================================="
echo -e "${BLUE}📍 uMEMORY Location:${NC} $ROOT_MEMORY (root level, not hidden)"
echo -e "${BLUE}🗺️ Location System:${NC} uMAP integration with AA24 format tiles"
echo -e "${BLUE}🔒 Data Structure:${NC} explicit (private) / public (shared)"
echo -e "${BLUE}📁 Sandbox:${NC} Separate from uMEMORY (as intended)"
echo -e "${BLUE}🎯 System Data:${NC} Moved to uCORE/datasets and uCORE/templates"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test location detection with uMAP integration"
echo "2. Update file creation to use AA24 format tiles"
echo "3. Validate uMAP system is working correctly"
