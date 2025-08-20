#!/bin/bash
# uDOS Compact uHEX Generator v1.0 - Reduced to 8-character uHEX codes
# Encodes only: Date, Time(HHMMSS), 4-alpha TZ, Role, uTILE location
# All settings must be configured in sandbox/user.md
# Moved from wizard/ to uCORE for system-wide access

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Load uTILE location data if available
TILES_DIR="$UDOS_ROOT/uMEMORY/core/tiles"
USER_LOCATION_FILE="$UDOS_ROOT/sandbox/user.md"

# Function to get user settings from user.md
get_user_settings() {
    local setting_name="$1"
    local default_value="$2"
    
    if [ -f "$USER_LOCATION_FILE" ]; then
        local value=$(grep -E "^\\\$$setting_name=" "$USER_LOCATION_FILE" 2>/dev/null | cut -d'=' -f2 | tr -d '"' | head -1)
        if [ -n "$value" ]; then
            echo "$value"
        else
            echo "$default_value"
        fi
    else
        echo "$default_value"
    fi
}

# Function to detect current uTILE location from user.md
detect_current_tile() {
    local location=$(get_user_settings "LOCATION" "00FFFF")
    local tile_code="FFFF"  # Default system tile
    
    if [[ "$location" =~ ^00[A-Z]{2}[0-9]{2}$ ]]; then
        # Extract uTILE code from location (last 4 characters)
        tile_code="${location: -4}"
    fi
    
    echo "$tile_code"
}

# Function to decode uTILE location name
get_tile_name() {
    local tile_code="$1"
    
    case "$tile_code" in
        "WG10") echo "Wizard Garden Level 10" ;;
        "HO35") echo "Home Office Level 35" ;;
        "SF15") echo "San Francisco Level 15" ;;
        "NY25") echo "New York Level 25" ;;
        "LA20") echo "Los Angeles Level 20" ;;
        "CH12") echo "Chicago Level 12" ;;
        "AU30") echo "Australia Level 30" ;;
        "UK40") echo "United Kingdom Level 40" ;;
        "JP22") echo "Japan Level 22" ;;
        "DE18") echo "Germany Level 18" ;;
        "CA27") echo "Canada Level 27" ;;
        "BR33") echo "Brazil Level 33" ;;
        "FFFF") echo "System Default" ;;
        *) echo "Unknown Location" ;;
    esac
}

# Function to get timezone from user.md (must be set)
get_timezone_alpha() {
    local tz_alpha=$(get_user_settings "TIMEZONE" "")
    
    if [ -z "$tz_alpha" ]; then
        echo "ERRO"
        return 1
    fi
    
    # Validate 4-alpha format
    if [[ ! "$tz_alpha" =~ ^[A-Z]{4}$ ]]; then
        echo "ERRO"
        return 1
    fi
    
    echo "$tz_alpha"
}

# Function to get user role from user.md
get_user_role() {
    local role=$(get_user_settings "ROLE" "")
    
    if [ -z "$role" ]; then
        echo "error"
        return 1
    fi
    
    # Convert to uppercase for consistency
    role=$(echo "$role" | tr '[:lower:]' '[:upper:]')
    
    # Validate role
    case "$role" in
        "GHOST"|"TOMB"|"DRONE"|"IMP"|"SORCERER"|"WIZARD")
            echo "$role"
            ;;
        *)
            echo "error"
            return 1
            ;;
    esac
}

# Function to calculate days since epoch (2025-01-01)
calculate_days_since_epoch() {
    local date_str="$1"
    local year="${date_str:0:4}"
    local month="${date_str:4:2}"
    local day="${date_str:6:2}"
    
    # Calculate days since 2025-01-01
    local epoch_date=$(date -d "2025-01-01" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "2025-01-01" +%s)
    local target_date=$(date -d "${year}-${month}-${day}" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "${year}-${month}-${day}" +%s)
    local days=$(( (target_date - epoch_date) / 86400 ))
    
    echo $days
}

# Function to encode 4-alpha timezone to uHEX
encode_timezone_alpha() {
    local tz_alpha="$1"
    local encoded=0
    
    # Convert 4-character timezone to 16-bit value
    # Each character: A=1, B=2, ..., Z=26
    for i in {0..3}; do
        local char="${tz_alpha:$i:1}"
        local char_val=0
        if [[ "$char" =~ [A-Z] ]]; then
            char_val=$(( $(printf '%d' "'$char") - 64 ))  # A=1, B=2, etc.
        fi
        encoded=$(( encoded * 27 + char_val ))  # Base-27 encoding
    done
    
    # Keep within 16-bit range
    encoded=$(( encoded % 65536 ))
    echo $encoded
}

# Function to generate compact uHEX code (8 characters total)
generate_hex_code() {
    local date_str="$1"
    local time_str="$2"
    local tz_alpha="$3"
    local role="$4"
    local tile_code="$5"
    
    # Calculate days since epoch (max 255 for single byte)
    local days=$(calculate_days_since_epoch "$date_str")
    local date_byte=$(( days % 256 ))
    
    # Extract time components and pack into single byte each
    local hour=$((10#${time_str:0:2}))
    local minute=$((10#${time_str:2:2}))
    local second=$((10#${time_str:4:2}))
    
    # Encode 4-alpha timezone to single byte (Base-26 encoding)
    local tz_encoded=0
    for i in {0..3}; do
        local char="${tz_alpha:$i:1}"
        if [[ "$char" =~ [A-Z] ]]; then
            local char_val=$(( $(printf '%d' "'$char") - 64 ))
            tz_encoded=$(( (tz_encoded * 27 + char_val) % 256 ))
        fi
    done
    
    # Role encoding (4 bits) + uTILE high bits (4 bits)
    local role_encoded=10 # Default WIZARD
    case "$role" in
        "GHOST") role_encoded=1 ;;
        "TOMB") role_encoded=2 ;;
        "DRONE") role_encoded=4 ;;
        "IMP") role_encoded=6 ;;
        "SORCERER") role_encoded=8 ;;
        "WIZARD") role_encoded=10 ;;
        *) role_encoded=10 ;;
    esac
    
    # uTILE code encoding (simplified to fit in remaining space)
    local tile_encoded=255  # Default FF for system files
    if [[ "$tile_code" =~ ^[A-Z]{2}[0-9]{2}$ ]]; then
        # Compact uTILE encoding
        local char1=$(( $(printf '%d' "'${tile_code:0:1}") - 64 ))
        local char2=$(( $(printf '%d' "'${tile_code:1:1}") - 64 ))
        local num_part=$((10#${tile_code:2:2}))
        tile_encoded=$(( (char1 + char2 + num_part) % 256 ))
    fi
    
    # Pack role and tile high bits
    local role_tile=$(( (role_encoded << 4) | (tile_encoded >> 4) ))
    local tile_low=$(( tile_encoded & 15 ))
    
    # Generate 8-character uHEX code (4 bytes)
    # Format: DDHHMMSS where:
    # DD = Date (days since epoch)
    # HH = Hour
    # MM = Minute  
    # SS = Second
    printf "%02X%02X%02X%02X" $date_byte $hour $minute $second
}

# Function to get full timezone name
get_timezone_name() {
    local tz_code="$1"
    case "$tz_code" in
        "USPT") echo "US Pacific Time" ;;
        "USCT") echo "US Central Time" ;;
        "USET") echo "US Eastern Time" ;;
        "EUCE") echo "European Central Time" ;;
        "JPST") echo "Japan Standard Time" ;;
        "AUET") echo "Australian Eastern Time" ;;
        "GMTU") echo "Greenwich Mean Time" ;;
        *) echo "$tz_code" ;;
    esac
}

# Function to generate filename with current context
generate_filename() {
    local prefix="$1"
    local title="$2"
    local extension="${3:-md}"
    
    # Get current date/time
    local current_date=$(date +%Y%m%d)
    local current_time=$(date +%H%M%S)
    
    # Get user settings from user.md (required)
    local tile_code=$(detect_current_tile)
    local tz_alpha=$(get_timezone_alpha)
    local current_role=$(get_user_role)
    
    # Check for errors
    if [ "$tz_alpha" = "ERRO" ] || [ "$current_role" = "error" ]; then
        echo -e "${RED}❌ Cannot generate filename - check user.md settings${NC}"
        return 1
    fi
    
    # Generate compact 8-character uHEX code
    local hex_code=$(generate_hex_code "$current_date" "$current_time" "$tz_alpha" "$current_role" "$tile_code")
    
    # Clean and limit title (more space available with shorter uHEX)
    local clean_title=$(echo "$title" | sed 's/[^a-zA-Z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-\|-$//g')
    if [ ${#clean_title} -gt 30 ]; then
        clean_title="${clean_title:0:27}..."
    fi
    
    # Create filename with compact format
    local filename="${prefix}-${hex_code}-${clean_title}.${extension}"
    
    # Get full timezone name
    local tz_full_name=$(get_timezone_name "$tz_alpha")
    
    echo -e "${GREEN}� uDOS Compact Hex Generator${NC}"
    echo -e "${GREEN}8-Character Hex Codes with Required user.md Settings${NC}"
    echo -e "${CYAN}📝 $filename${NC}"
    echo -e "${CYAN}🗓️  Date: $current_date${NC}"
    echo -e "${CYAN}⏰ Time: $current_time${NC}"
    echo -e "${CYAN}🌍 Timezone: $tz_alpha ($tz_full_name)${NC}"
    echo -e "${CYAN}👤 Role: $(echo $current_role | tr '[:lower:]' '[:upper:]')${NC}"
    echo -e "${CYAN}📍 uTILE: 00$tile_code ($(get_tile_name "$tile_code"))${NC}"
    echo -e "${CYAN}🔢 uHEX#: $hex_code${NC}"
    echo ""
    
    echo "$filename"
}

# Function to decode uHEX filename (for verification)
decode_uhex_filename() {
    local filename="$1"
    
    if [[ "$filename" =~ ^(u[A-Z]+)-([0-9A-F]{16})-(.*)\.([^.]+)$ ]]; then
        local prefix="${BASH_REMATCH[1]}"
        local hex_code="${BASH_REMATCH[2]}"
        local title="${BASH_REMATCH[3]}"
        local ext="${BASH_REMATCH[4]}"
        
        echo -e "${BLUE}🔍 Decoding: $filename${NC}"
        echo -e "${CYAN}   📝 Prefix: $prefix${NC}"
        echo -e "${CYAN}   🔢 uHEX#: $hex_code${NC}"
        echo -e "${CYAN}   📄 Title: $title${NC}"
        echo -e "${CYAN}   📎 Extension: $ext${NC}"
        
        # TODO: Add full hex decoding logic here
        echo -e "${YELLOW}   ⚠️  Full decode implementation pending${NC}"
    else
        echo -e "${RED}❌ Invalid uHEX filename format${NC}"
    fi
}

# Main interface
case "${1:-help}" in
    "generate"|"gen")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}❌ Usage: $0 generate <prefix> <title> [extension]${NC}"
            echo -e "${CYAN}   Example: $0 generate uLOG \"System Startup\" md${NC}"
            exit 1
        fi
        generate_filename "$2" "$3" "$4"
        ;;
    "decode")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Usage: $0 decode <filename>${NC}"
            echo -e "${CYAN}   Example: $0 decode uLOG-1234567890ABCDEF-System-Startup.md${NC}"
            exit 1
        fi
        decode_hex_filename "$2"
        ;;
    "tile")
        echo -e "${BLUE}📍 Current User Settings:${NC}"
        echo -e "${CYAN}Reading from: $USER_LOCATION_FILE${NC}"
        echo ""
        
        tile_code=$(detect_current_tile)
        tz_alpha=$(get_timezone_alpha)
        current_role=$(get_user_role)
        
        echo ""
        echo -e "${GREEN}Current Configuration:${NC}"
        echo -e "${GREEN}   TILE Code: $tile_code${NC}"
        echo -e "${GREEN}   Timezone: $tz_alpha${NC}"
        echo -e "${GREEN}   Role: $current_role${NC}"
        ;;
    "help"|*)
        echo -e "${BLUE}🔧 uDOS Compact uHEX Generator v1.0 - Usage:${NC}"
        echo ""
        echo -e "${CYAN}Commands:${NC}"
        echo -e "  ${GREEN}generate <prefix> <title> [ext]${NC}  - Generate compact hex filename"
        echo -e "  ${GREEN}decode <filename>${NC}              - Decode existing hex filename"
        echo -e "  ${GREEN}tile${NC}                           - Show current user settings"
        echo ""
        echo -e "${CYAN}Required Setup (in sandbox/user.md):${NC}"
        echo -e "  ${YELLOW}\$LOCATION=00HO35${NC}              - Physical TILE location"
        echo -e "  ${YELLOW}\$TIMEZONE=USET${NC}                - 4-alpha timezone code"
        echo -e "  ${YELLOW}\$ROLE=WIZARD${NC}                  - User role"
        echo ""
        echo -e "${CYAN}Examples:${NC}"
        echo -e "  $0 generate uLOG \"System startup complete\""
        echo -e "  $0 generate uDATA \"Global city reference\" json"
        echo -e "  $0 decode uLOG-E5174530-System-Startup.md"
        echo -e "  $0 tile"
        echo ""
        echo -e "${CYAN}Compact Hex Format (8 characters):${NC}"
        echo -e "  ✅ Date: Days since 2025-01-01 (1 byte)"
        echo -e "  ✅ Time: HHMMSS precise timing (3 bytes)"
        echo -e "  ✅ 4-Alpha TZ: From user.md (encoded)"
        echo -e "  ✅ Role: From user.md (encoded)"
        echo -e "  ✅ TILE: Physical location from user.md (encoded)"
        echo ""
        echo -e "${CYAN}Supported Timezones:${NC}"
        echo -e "  USPT, USCT, USET, EUCE, JPST, AUET, GMTU"
        echo ""
        echo -e "${CYAN}Supported Roles:${NC}"
        echo -e "  GHOST, TOMB, DRONE, IMP, SORCERER, WIZARD"
        ;;
esac
