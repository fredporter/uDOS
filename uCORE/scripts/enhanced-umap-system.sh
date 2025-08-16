#!/usr/bin/env bash
# [20-95-01] Enhanced uMAP System with Multi-Map Support
# Location: uCORE/scripts/enhanced-umap-system.sh
# Purpose: Implement 100-map system with 00 = Planet Earth base template

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌍 Enhanced uMAP System v2.0${NC}"
echo "================================="

# Step 1: Create the enhanced tile format (00 + original tile)
echo -e "\n${YELLOW}🗺️ Implementing Multi-Map System...${NC}"

# Create base system map template in uCORE
mkdir -p "$UDOS_ROOT/uCORE/datasets/mapping/maps"
mkdir -p "$UDOS_ROOT/uCORE/templates/mapping"

# Create Map 00 - Planet Earth (System Map - Dev/Wizard only)
cat > "$UDOS_ROOT/uCORE/datasets/mapping/maps/map-00-earth.json" << 'EOF'
{
  "metadata": {
    "map_id": "00",
    "name": "Planet Earth",
    "description": "Base system map - Planet Earth with real geographic coordinates",
    "type": "system",
    "editable_by": ["dev", "wizard"],
    "version": "2.0.0",
    "created": "2025-08-16",
    "base_template": true,
    "grid_size": {
      "width": 120,
      "height": 60
    },
    "depth_layers": {
      "surface": "1m",
      "max_depth": "1000m",
      "layer_increment": "1m"
    },
    "coordinate_system": "geographic",
    "projection": "mercator"
  },
  "schema": {
    "tile": {
      "format": "00[A-Z]{2}[0-9]{2}",
      "description": "Map 00 + two letters + two numbers (e.g., 00CQ43)",
      "map_prefix": "00"
    },
    "depth": {
      "format": "[0-9]{1,4}m",
      "description": "Depth in meters from 1m to 1000m",
      "default": "1m"
    }
  },
  "access_control": {
    "read": ["dev", "wizard", "sorcerer", "ghost", "imp"],
    "write": ["dev", "wizard"],
    "create_derived": ["wizard", "sorcerer"]
  },
  "features": {
    "cities": true,
    "terrain": true,
    "climate": true,
    "population": true,
    "economic_data": true,
    "timezone_mapping": true
  }
}
EOF

echo -e "${GREEN}✅ Created Map 00 - Planet Earth system template${NC}"

# Step 2: Update location detection to use enhanced format
echo -e "\n${YELLOW}📍 Updating location detection system...${NC}"

cat > "$UDOS_ROOT/uMEMORY/scripts/explicit/detect-location-enhanced.sh" << 'EOF'
#!/usr/bin/env bash
# Enhanced uDOS Location Detection with Multi-Map Support
# Format: MMTTNN where MM=map, TT=letters, NN=numbers

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../" && pwd)"
LOCATION_MAP="$UDOS_ROOT/uCORE/datasets/mapping/datasets/locationMap.json"
USER_CONFIG="$UDOS_ROOT/sandbox/user.md"

# Get system timezone
SYSTEM_TZ=$(date +%Z 2>/dev/null || echo "UTC")

# Check if running interactively
if [[ -t 0 ]]; then
    echo "🌍 Enhanced uDOS Location Detection"
    echo "===================================="
    echo ""
    echo "System Timezone: $SYSTEM_TZ"
    INTERACTIVE=true
else
    INTERACTIVE=false
fi

# Get current user location and custom name
get_current_location() {
    local current_tile=""
    local custom_name=""
    
    # Check user identity for location
    if [[ -f "$UDOS_ROOT/uMEMORY/user/explicit/identity.md" ]]; then
        current_tile=$(grep "location:" "$UDOS_ROOT/uMEMORY/user/explicit/identity.md" | cut -d: -f2 | xargs 2>/dev/null || echo "")
    fi
    
    # Check sandbox for custom location name
    if [[ -f "$USER_CONFIG" ]]; then
        custom_name=$(grep "LOCATION=" "$USER_CONFIG" | cut -d= -f2 | tr -d '"' 2>/dev/null || echo "")
    fi
    
    echo "${current_tile}|${custom_name}"
}

# Validate enhanced tile format
validate_enhanced_tile() {
    local tile="$1"
    
    # Check format: MMTTNN (e.g., 00CQ43)
    if [[ "$tile" =~ ^[0-9]{2}[A-Z]{2}[0-9]{2}$ ]]; then
        local map_num="${tile:0:2}"
        local base_tile="${tile:2:4}"
        
        # Map 00 must exist in uMAP database
        if [[ "$map_num" == "00" ]]; then
            if command -v jq >/dev/null 2>&1 && [[ -f "$LOCATION_MAP" ]]; then
                if jq -e ".data[] | select(.tile == \"$base_tile\")" "$LOCATION_MAP" >/dev/null 2>&1; then
                    return 0
                else
                    if [[ "$INTERACTIVE" == true ]]; then
                        echo "Base tile $base_tile not found in Map 00 database"
                    fi
                    return 1
                fi
            fi
        else
            # Maps 01-99 are user-created, basic format validation
            return 0
        fi
    else
        if [[ "$INTERACTIVE" == true ]]; then
            echo "Invalid tile format: $tile (should be MMTTNN, e.g., 00CQ43)"
        fi
        return 1
    fi
}

# Get city name from tile
get_city_name() {
    local tile="$1"
    local map_num="${tile:0:2}"
    local base_tile="${tile:2:4}"
    
    if [[ "$map_num" == "00" ]] && command -v jq >/dev/null 2>&1 && [[ -f "$LOCATION_MAP" ]]; then
        jq -r ".data[] | select(.tile == \"$base_tile\") | .city" "$LOCATION_MAP" 2>/dev/null || echo "Unknown"
    else
        echo "Custom Map $map_num"
    fi
}

# Main location detection logic
current_data=$(get_current_location)
current_tile="${current_data%|*}"
custom_name="${current_data#*|}"

if [[ -n "$current_tile" && "$INTERACTIVE" == true ]]; then
    city_name=$(get_city_name "$current_tile")
    display_name="${custom_name:-$city_name}"
    
    echo "Current location: $current_tile ($display_name)"
    echo ""
    echo "Options:"
    echo "  1) Keep current location ($current_tile - $display_name)"
    echo "  2) Select new location"
    echo "  3) Change location display name"
    echo ""
    read -p "Selection [1-3, default: 1]: " choice
    
    case "$choice" in
        "2")
            echo ""
            echo "Map Selection:"
            echo "  00) Planet Earth (system map with real cities)"
            echo "  01-99) Custom user maps (if created)"
            echo ""
            read -p "Select map [00-99, default: 00]: " map_choice
            map_choice=$(printf "%02d" "${map_choice:-0}" 2>/dev/null || echo "00")
            
            if [[ "$map_choice" == "00" ]]; then
                echo ""
                echo "Available Planet Earth locations:"
                if command -v jq >/dev/null 2>&1 && [[ -f "$LOCATION_MAP" ]]; then
                    jq -r '.data[] | "00\(.tile) - \(.city), \(.country)"' "$LOCATION_MAP" | head -20
                else
                    echo "00CQ43 - Sydney, Australia (default)"
                fi
                echo ""
                read -p "Enter enhanced tile code (e.g., 00CQ43): " new_tile
            else
                echo ""
                echo "Custom map $map_choice selected"
                read -p "Enter tile code for map $map_choice (format: ${map_choice}AA##): " base_tile
                new_tile="$map_choice$base_tile"
            fi
            
            new_tile=$(echo "$new_tile" | tr '[:lower:]' '[:upper:]')
            if validate_enhanced_tile "$new_tile"; then
                echo "$new_tile"
            else
                echo "Invalid tile, keeping current: $current_tile"
                echo "$current_tile"
            fi
            ;;
        "3")
            city_name=$(get_city_name "$current_tile")
            echo ""
            echo "Current: $current_tile ($city_name)"
            echo "Custom name: ${custom_name:-$city_name}"
            echo ""
            read -p "Enter new display name (or press enter to use city name): " new_name
            
            # Update sandbox user.md with new location name
            if [[ -n "$new_name" ]]; then
                mkdir -p "$(dirname "$USER_CONFIG")"
                if [[ -f "$USER_CONFIG" ]]; then
                    # Update existing LOCATION variable
                    if grep -q "LOCATION=" "$USER_CONFIG"; then
                        sed -i.bak "s/LOCATION=.*/LOCATION=\"$new_name\"/" "$USER_CONFIG"
                    else
                        echo "LOCATION=\"$new_name\"" >> "$USER_CONFIG"
                    fi
                else
                    # Create new user.md
                    cat > "$USER_CONFIG" << EOL
# User Configuration
LOCATION="$new_name"
USER="$USER"
CREATED="$(date +"%Y-%m-%d")"
EOL
                fi
                echo "Location name updated to: $new_name"
            fi
            echo "$current_tile"
            ;;
        *)
            echo "$current_tile"
            ;;
    esac
elif [[ -n "$current_tile" ]]; then
    # Non-interactive mode with existing location
    echo "$current_tile"
else
    # First time setup
    if [[ "$INTERACTIVE" == true ]]; then
        echo "First time setup - select your location:"
        echo ""
        echo "Available Planet Earth locations (Map 00):"
        if command -v jq >/dev/null 2>&1 && [[ -f "$LOCATION_MAP" ]]; then
            jq -r '.data[] | "00\(.tile) - \(.city), \(.country)"' "$LOCATION_MAP" | head -20
        else
            echo "00CQ43 - Sydney, Australia (default)"
        fi
        echo ""
        read -p "Enter enhanced tile code (e.g., 00CQ43): " chosen_tile
        
        # Get city name and ask for custom name
        chosen_tile=$(echo "$chosen_tile" | tr '[:lower:]' '[:upper:]')
        if validate_enhanced_tile "$chosen_tile"; then
            city_name=$(get_city_name "$chosen_tile")
            echo ""
            read -p "Custom name for $city_name (or press enter to use city name): " custom_name
            
            # Save to sandbox user.md
            mkdir -p "$(dirname "$USER_CONFIG")"
            cat > "$USER_CONFIG" << EOL
# User Configuration
LOCATION="${custom_name:-$city_name}"
USER="$USER"
CREATED="$(date +"%Y-%m-%d")"
EOL
            echo "$chosen_tile"
        else
            echo "00CQ43"
        fi
    else
        echo "00CQ43"
    fi
fi
EOF

chmod +x "$UDOS_ROOT/uMEMORY/scripts/explicit/detect-location-enhanced.sh"
echo -e "${GREEN}✅ Created enhanced location detection script${NC}"

# Step 3: Update file validation for enhanced format
echo -e "\n${YELLOW}🔍 Updating validation for enhanced tiles...${NC}"

# Backup and update validation script
if [[ -f "$UDOS_ROOT/uMEMORY/scripts/explicit/validate-files.sh" ]]; then
    cp "$UDOS_ROOT/uMEMORY/scripts/explicit/validate-files.sh" "$UDOS_ROOT/uMEMORY/scripts/explicit/validate-files.sh.bak"
    
    # Update the tile validation pattern
    sed -i 's/\[A-Z\]{2}\[0-9\]{2}/[0-9]{2}[A-Z]{2}[0-9]{2}/g' "$UDOS_ROOT/uMEMORY/scripts/explicit/validate-files.sh"
    
    # Update the regex in validate_filename function
    sed -i 's/CODE-\[0-9\]{4}-\[0-9\]{2}-\[0-9\]{2}-\[0-9\]{4}-\[A-Z\]{2}\[0-9\]{2}/CODE-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{4}-[0-9]{2}[A-Z]{2}[0-9]{2}/g' "$UDOS_ROOT/uMEMORY/scripts/explicit/validate-files.sh"
    
    echo -e "${GREEN}✅ Updated file validation for enhanced tile format${NC}"
fi

# Step 4: Create map management system
echo -e "\n${YELLOW}🗺️ Creating map management system...${NC}"

cat > "$UDOS_ROOT/uCORE/scripts/map-manager.sh" << 'EOF'
#!/usr/bin/env bash
# uMAP Management System - Create and manage custom maps
# Location: uCORE/scripts/map-manager.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MAPS_DIR="$UDOS_ROOT/uCORE/datasets/mapping/maps"

show_help() {
    echo "uMAP Management System"
    echo "====================="
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  list                    List all available maps"
    echo "  create <id> <name>      Create new map (01-99)"
    echo "  info <id>               Show map information"
    echo "  template                Show base template info (Map 00)"
    echo "  validate <id>           Validate map structure"
    echo ""
    echo "Examples:"
    echo "  $0 list                 # List all maps"
    echo "  $0 create 01 \"Fantasy World\"  # Create Map 01"
    echo "  $0 info 00              # Show Planet Earth info"
}

list_maps() {
    echo "Available uMAPs:"
    echo "================"
    echo ""
    
    # Show Map 00 (always present)
    echo "00 - Planet Earth (System Map)"
    echo "   Type: System Template"
    echo "   Access: Read-only (dev/wizard write)"
    echo "   Features: Real geographic coordinates"
    echo ""
    
    # Show user maps
    for map_file in "$MAPS_DIR"/map-*.json; do
        if [[ -f "$map_file" && "$map_file" != *"map-00-earth.json" ]]; then
            local map_id=$(basename "$map_file" | sed 's/map-\([0-9]*\)-.*/\1/')
            local map_name=$(jq -r '.metadata.name' "$map_file" 2>/dev/null || echo "Unknown")
            local map_type=$(jq -r '.metadata.type' "$map_file" 2>/dev/null || echo "user")
            echo "$map_id - $map_name"
            echo "   Type: $map_type"
            echo "   Created: $(jq -r '.metadata.created' "$map_file" 2>/dev/null || echo "Unknown")"
            echo ""
        fi
    done
}

create_map() {
    local map_id="$1"
    local map_name="$2"
    
    if [[ ! "$map_id" =~ ^[0-9]{2}$ ]] || [[ "$map_id" == "00" ]]; then
        echo "Error: Map ID must be 01-99"
        return 1
    fi
    
    if [[ -z "$map_name" ]]; then
        echo "Error: Map name required"
        return 1
    fi
    
    local map_file="$MAPS_DIR/map-$map_id-$(echo "$map_name" | tr ' ' '-' | tr '[:upper:]' '[:lower:]').json"
    
    if [[ -f "$map_file" ]]; then
        echo "Error: Map $map_id already exists"
        return 1
    fi
    
    # Create new map based on template
    cat > "$map_file" << EOL
{
  "metadata": {
    "map_id": "$map_id",
    "name": "$map_name",
    "description": "User-created map derived from Planet Earth template",
    "type": "user",
    "editable_by": ["wizard", "sorcerer"],
    "version": "1.0.0",
    "created": "$(date +%Y-%m-%d)",
    "base_template": false,
    "parent_map": "00",
    "grid_size": {
      "width": 120,
      "height": 60
    },
    "depth_layers": {
      "surface": "1m",
      "max_depth": "1000m",
      "layer_increment": "1m"
    },
    "coordinate_system": "custom",
    "projection": "custom"
  },
  "schema": {
    "tile": {
      "format": "${map_id}[A-Z]{2}[0-9]{2}",
      "description": "Map $map_id + two letters + two numbers",
      "map_prefix": "$map_id"
    },
    "depth": {
      "format": "[0-9]{1,4}m",
      "description": "Depth in meters from 1m to 1000m",
      "default": "1m"
    }
  },
  "access_control": {
    "read": ["wizard", "sorcerer", "ghost", "imp"],
    "write": ["wizard", "sorcerer"],
    "create_derived": ["wizard"]
  },
  "features": {
    "cities": true,
    "terrain": true,
    "climate": false,
    "population": false,
    "economic_data": false,
    "timezone_mapping": false,
    "custom_features": true
  },
  "data": []
}
EOL
    
    echo "Created Map $map_id: $map_name"
    echo "File: $map_file"
}

show_map_info() {
    local map_id="$1"
    
    if [[ "$map_id" == "00" ]]; then
        local map_file="$MAPS_DIR/map-00-earth.json"
    else
        local map_file=$(find "$MAPS_DIR" -name "map-$map_id-*.json" | head -1)
    fi
    
    if [[ ! -f "$map_file" ]]; then
        echo "Error: Map $map_id not found"
        return 1
    fi
    
    echo "Map Information:"
    echo "================"
    jq -r '
    "ID: " + .metadata.map_id + 
    "\nName: " + .metadata.name +
    "\nType: " + .metadata.type +
    "\nCreated: " + .metadata.created +
    "\nGrid: " + (.metadata.grid_size.width|tostring) + "×" + (.metadata.grid_size.height|tostring) +
    "\nDepth: " + .metadata.depth_layers.surface + " to " + .metadata.depth_layers.max_depth +
    "\nEditable by: " + (.metadata.editable_by | join(", "))
    ' "$map_file"
}

# Main command handling
case "${1:-help}" in
    "list") list_maps ;;
    "create") create_map "$2" "$3" ;;
    "info") show_map_info "$2" ;;
    "template") show_map_info "00" ;;
    "help"|*) show_help ;;
esac
EOF

chmod +x "$UDOS_ROOT/uCORE/scripts/map-manager.sh"
echo -e "${GREEN}✅ Created map management system${NC}"

# Step 5: Update user identity with enhanced location
echo -e "\n${YELLOW}👤 Updating user identity for enhanced system...${NC}"

if [[ -f "$UDOS_ROOT/uMEMORY/user/explicit/identity.md" ]]; then
    # Get current location and enhance it
    current_location=$(grep "location:" "$UDOS_ROOT/uMEMORY/user/explicit/identity.md" | cut -d: -f2 | xargs 2>/dev/null || echo "CQ43")
    
    # Add 00 prefix if not already present
    if [[ ! "$current_location" =~ ^[0-9]{2} ]]; then
        enhanced_location="00$current_location"
    else
        enhanced_location="$current_location"
    fi
    
    # Update identity file
    sed -i.bak "s/location:.*/location: $enhanced_location/" "$UDOS_ROOT/uMEMORY/user/explicit/identity.md"
    echo -e "${GREEN}✅ Updated identity with enhanced location: $enhanced_location${NC}"
fi

# Step 6: Create sandbox user.md if it doesn't exist
echo -e "\n${YELLOW}📄 Setting up sandbox user configuration...${NC}"

mkdir -p "$UDOS_ROOT/sandbox"
if [[ ! -f "$UDOS_ROOT/sandbox/user.md" ]]; then
    cat > "$UDOS_ROOT/sandbox/user.md" << EOF
# User Configuration
LOCATION="Sydney"
USER="$USER"
CREATED="$(date +"%Y-%m-%d")"
PASSWORD=""

# Location Settings
# LOCATION can be customized to any name you prefer
# This is stored separately from the technical tile coordinates
# Examples: "Sydney", "Elsewhere", "Home Base", "Dev Station"
EOF
    echo -e "${GREEN}✅ Created sandbox/user.md with location configuration${NC}"
fi

echo -e "\n${GREEN}🎉 Enhanced uMAP System Complete!${NC}"
echo "=================================="
echo -e "${BLUE}📍 Enhanced Format:${NC} MMTTNN (e.g., 00CQ43)"
echo -e "${BLUE}🗺️ Map System:${NC} 100 maps (00-99) with 1m depth layers"
echo -e "${BLUE}🌍 Map 00:${NC} Planet Earth (system template, dev/wizard only)"
echo -e "${BLUE}🎨 Maps 01-99:${NC} User-created custom maps"
echo -e "${BLUE}📝 User Location:${NC} Customizable names in sandbox/user.md"
echo -e "${BLUE}🔧 Management:${NC} Full map creation and management tools"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Test enhanced location detection"
echo "2. Create custom maps using map-manager.sh"
echo "3. Update file naming to use enhanced format"
echo "4. Customize location display name"
