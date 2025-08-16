#!/bin/bash
# uDOS v1.3 Filename Generator
# Generates compliant filenames with timezone and location integration using existing cityMap dataset

# Source timezone dataset path
TIMEZONE_DATASET="/Users/agentdigital/uDOS/uCORE/datasets/mapping/datasets/timezoneMap.json"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

generate_udos_filename() {
    local file_type="$1"
    local description="$2"
    local custom_location="$3"
    
    echo -e "${CYAN}🏗️ uDOS v1.3 Filename Generator${NC}"
    echo "=================================="
    
    # Get current date/time
    local date_stamp=$(date +%Y%m%d)
    local time_stamp=$(date +%H%M)
    
    # Get timezone code
    local tz_code=$(get_current_timezone_code)
    
    # Get location code
    local location_code
    if [ -n "$custom_location" ]; then
        location_code="$custom_location"
    else
        location_code=$(get_current_location_code)
    fi
    
    # Validate inputs
    if ! validate_file_type "$file_type"; then
        echo -e "${RED}❌ Invalid file type: $file_type${NC}"
        show_valid_file_types
        return 1
    fi
    
    if ! validate_location_code "$location_code"; then
        echo -e "${RED}❌ Invalid location code: $location_code${NC}"
        return 1
    fi
    
    # Generate filename
    local filename="u${file_type}-${date_stamp}-${time_stamp}-${tz_code}-${location_code}.md"
    
    echo -e "${GREEN}✅ Generated filename:${NC} ${YELLOW}$filename${NC}"
    echo ""
    echo "📄 File Details:"
    echo "  Type: u$file_type"
    echo "  Date: $date_stamp"
    echo "  Time: $time_stamp"
    echo "  Timezone: $(get_timezone_name_by_code "$tz_code") (TZ:$tz_code)"
    echo "  Location: $location_code"
    echo "  Description: $description"
    
    # Create the file if requested
    if [ "$4" = "--create" ]; then
        create_file_with_template "$filename" "$file_type" "$description" "$location_code" "$tz_code"
    else
        echo ""
        echo "To create this file, run:"
        echo "${BLUE}$0 \"$file_type\" \"$description\" \"$location_code\" --create${NC}"
    fi
    
    echo "$filename"
}

get_current_timezone_code() {
    # Use the timezone mapper script for proper conversion
    local timezone_mapper="/Users/agentdigital/uDOS/uCORE/scripts/timezone-mapper-v13.sh"
    
    if [ -f "$timezone_mapper" ]; then
        local system_tz=$(date +%Z)
        "$timezone_mapper" map "$system_tz" 2>/dev/null || echo "38"
    else
        # Fallback mapping for common timezones
        local system_tz=$(date +%Z)
        
        case "$system_tz" in
            "AEDT"|"AEST") echo "28" ;;  # Australian Eastern
            "UTC"|"GMT") echo "38" ;;    # UTC/GMT
            "EST"|"EDT") echo "02" ;;    # US Eastern
            "CET"|"CEST") echo "08" ;;   # Central European
            "JST") echo "23" ;;          # Japan
            "PST"|"PDT") echo "34" ;;    # US Pacific
            "CST"|"CDT") echo "01" ;;    # US Central
            "MST"|"MDT") echo "35" ;;    # US Mountain
            *) echo "38" ;;              # Default to UTC
        esac
    fi
}

get_current_location_code() {
    # Try to get from user config first
    if [ -f "/Users/agentdigital/uDOS/sandbox/user.md" ]; then
        local location=$(grep "^Location:" /Users/agentdigital/uDOS/sandbox/user.md | cut -d' ' -f2 | tr -d '[]')
        if [ -n "$location" ] && [[ "$location" =~ ^[0-9]{2}[A-Z]{2}[0-9]{2}$ ]]; then
            echo "$location"
            return
        fi
    fi
    
    # Try enhanced location detection
    if [ -f "/Users/agentdigital/uDOS/uMEMORY/scripts/explicit/detect-location-enhanced.sh" ]; then
        local detected=$(/Users/agentdigital/uDOS/uMEMORY/scripts/explicit/detect-location-enhanced.sh 2>/dev/null | tail -1)
        if [[ "$detected" =~ ^[0-9]{2}[A-Z]{2}[0-9]{2}$ ]]; then
            echo "$detected"
            return
        fi
    fi
    
    # Default fallback
    echo "00SY43"  # Sydney, Australia default
}

validate_file_type() {
    local type="$1"
    local valid_types=("SCRIPT" "LOG" "DATA" "DOC" "MISSION" "LEGACY" "CONFIG" "TEMPLATE" "REPORT" "TEST" "BACKUP" "TMP")
    
    for valid_type in "${valid_types[@]}"; do
        if [ "$type" = "$valid_type" ]; then
            return 0
        fi
    done
    return 1
}

validate_location_code() {
    local code="$1"
    
    # Check format: MMLLNN (6 characters)
    if [[ ! "$code" =~ ^[0-9]{2}[A-Z]{2}[0-9]{2}$ ]]; then
        return 1
    fi
    
    local map_num=${code:0:2}
    local tile_num=${code:4:2}
    
    # Validate map number (00-99)
    if [ "$map_num" -gt 99 ]; then
        return 1
    fi
    
    # Validate tile number (01-99)
    if [ "$tile_num" -lt 1 ] || [ "$tile_num" -gt 99 ]; then
        return 1
    fi
    
    return 0
}

show_valid_file_types() {
    echo ""
    echo -e "${YELLOW}📋 Valid File Types:${NC}"
    echo "  SCRIPT     - Executable scripts and automation"
    echo "  LOG        - System and user activity logs"
    echo "  DATA       - Data files and datasets"
    echo "  DOC        - Documentation and guides"
    echo "  MISSION    - Mission and project files"
    echo "  LEGACY     - Historical and archived content"
    echo "  CONFIG     - Configuration files"
    echo "  TEMPLATE   - Template definitions"
    echo "  REPORT     - Generated reports"
    echo "  TEST       - Test files and validation"
    echo "  BACKUP     - Backup and recovery files"
    echo "  TMP        - Temporary working files"
}

get_timezone_name_by_code() {
    local code="$1"
    local timezone_mapper="/Users/agentdigital/uDOS/uCORE/scripts/timezone-mapper-v13.sh"
    
    if [ -f "$timezone_mapper" ]; then
        "$timezone_mapper" name "$code" 2>/dev/null || echo "Unknown Timezone"
    else
        # Fallback timezone names
        case "$code" in
            "01") echo "Central Standard Time (CST)" ;;
            "02") echo "Eastern Standard Time (EST)" ;;
            "08") echo "Central European Time (CET)" ;;
            "09") echo "Greenwich Mean Time (GMT)" ;;
            "23") echo "Japan Standard Time (JST)" ;;
            "28") echo "Australian Eastern Time (AEDT)" ;;
            "34") echo "Pacific Standard Time (PST)" ;;
            "35") echo "Mountain Standard Time (MST)" ;;
            "38") echo "Coordinated Universal Time (UTC)" ;;
            *) echo "Unknown Timezone" ;;
        esac
    fi
}

create_file_with_template() {
    local filename="$1"
    local file_type="$2"
    local description="$3"
    local location_code="$4"
    local tz_code="$5"
    
    local full_path="/Users/agentdigital/uDOS/$filename"
    
    cat > "$full_path" << EOF
# $description

**Type**: $filename  
**Version**: 3.0  
**Author**: \$USERNAME  
**Location**: [$location_code] \$(get_location_name "$location_code")  
**Timezone**: $(get_timezone_name_by_code "$tz_code")  
**Created**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")  

---

## Purpose

$description

## Details

[Add your content here]

---

*Generated by uDOS v1.3 Filename Generator*  
*Universal Data Operating System*
EOF
    
    echo -e "${GREEN}✅ File created:${NC} $full_path"
}

# Command line interface
case "$1" in
    "help"|"--help"|"-h")
        echo -e "${CYAN}🏗️ uDOS v1.3 Filename Generator${NC}"
        echo "Usage: $0 FILE_TYPE \"DESCRIPTION\" [LOCATION_CODE] [--create]"
        echo ""
        echo "Examples:"
        echo "  $0 SCRIPT \"Build automation script\""
        echo "  $0 LOG \"System startup log\" 00NY12"
        echo "  $0 DOC \"User manual\" 00SY43 --create"
        echo ""
        show_valid_file_types
        ;;
    "")
        echo -e "${RED}❌ Missing arguments${NC}"
        echo "Usage: $0 FILE_TYPE \"DESCRIPTION\" [LOCATION_CODE] [--create]"
        echo "Run '$0 help' for more information"
        ;;
    *)
        generate_udos_filename "$1" "$2" "$3" "$4"
        ;;
esac
