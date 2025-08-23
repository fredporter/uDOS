#!/bin/bash
# uDOS Filename Generator v2.0
# Generates filenames following the new v2.0 convention

#!/bin/bash
# uDOS Filename Generator v2.0
# Generates filenames following the new v2.0 convention with timezone alpha codes

# Function to get 2-letter timezone alpha code from the timezone dataset
get_timezone_alpha() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local ucore_dir="$(dirname "$(dirname "$script_dir")")/uCORE"
    local tz_mapping_file="$ucore_dir/datasets/timezone-alpha-codes.json"
    
    # Get current timezone (try multiple methods)
    local current_tz=""
    if command -v timedatectl >/dev/null 2>&1; then
        current_tz=$(timedatectl show --property=Timezone --value 2>/dev/null)
    elif [ -n "$TZ" ]; then
        current_tz="$TZ"
    else
        # Fallback: get from system
        current_tz=$(date +%Z 2>/dev/null)
    fi
    
    # Map common timezone names to our 2-letter alpha codes
    case "$current_tz" in
        "AEST"|"Australia/Sydney"|"Australia/Melbourne"|"AEDT") echo "AE" ;;
        "AWST"|"Australia/Perth") echo "AW" ;;
        "ACST"|"Australia/Adelaide") echo "AT" ;;
        "UTC"|"GMT") echo "UT" ;;
        "EST"|"US/Eastern") echo "ES" ;;
        "PST"|"US/Pacific") echo "PS" ;;
        "CST"|"US/Central") echo "CS" ;;
        "MST"|"US/Mountain") echo "MS" ;;
        "JST"|"Asia/Tokyo") echo "JS" ;;
        "CET"|"Europe/Berlin"|"Europe/Paris") echo "CE" ;;
        "EET"|"Europe/Athens") echo "EE" ;;
        "IST"|"Asia/Kolkata") echo "IS" ;;
        "BST"|"Asia/Dhaka") echo "BS" ;;
        "NZST"|"Pacific/Auckland") echo "NZ" ;;
        *) 
            # Default fallback - try to extract from mapping file if it exists
            if [ -f "$tz_mapping_file" ] && command -v jq >/dev/null 2>&1; then
                local alpha_code=$(jq -r ".mappings[\"$current_tz\"] // \"AE\"" "$tz_mapping_file" 2>/dev/null)
                echo "$alpha_code"
            else
                echo "AE"  # Default to Australian Eastern (original system timezone)
            fi
            ;;
    esac
}

# Function to generate filename
generate_filename() {
    local file_type=$1
    local title=$2
    local is_memory_file=${3:-false}
    local tile=${4:-""}
    
    # Get current local time
    local date=$(date +%Y%m%d)
    local time=$(date +%H%M%S)
    
    # Get timezone alpha code from the dataset
    local tz_code=$(get_timezone_alpha)
    
    # Build filename
    local filename
    if [ "$is_memory_file" = "true" ] && [ -n "$tile" ]; then
        # uMEMORY file with TILE
        filename="${file_type}-${date}-${time}${tz_code}-${tile}-${title}.md"
    else
        # General system file
        filename="${file_type}-${date}-${time}${tz_code}-${title}.md"
    fi
    
    # Check 40 character limit
    local basename=$(basename "$filename" .md)
    if [ ${#basename} -gt 40 ]; then
        echo "WARNING: Filename too long (${#basename} chars): $filename"
        echo "Consider shortening the title."
    fi
    
    echo "$filename"
}

# Function to show usage
show_usage() {
    echo "uDOS Filename Generator v2.0"
    echo ""
    echo "Usage:"
    echo "  $0 <file_type> <title> [memory_file] [tile]"
    echo ""
    echo "Examples:"
    echo "  $0 uLOG System-Startup"
    echo "  $0 uDEV Dev-Session"
    echo "  $0 uNOTE Personal-Notes true 05"
    echo "  $0 uTASK Daily-Goals true 05"
    echo ""
    echo "File Types: uLOG, uDEV, uDATA, uDOC, uTASK, uNOTE, uREP, uCONF, uSCRIPT, uTEMP"
}

# Main execution
if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

generate_filename "$@"
