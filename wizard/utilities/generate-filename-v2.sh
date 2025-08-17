#!/bin/bash
# uDOS Filename Generator v2.0
# Generates filenames following the new v2.0 convention

# Function to get 2-digit timezone code from UTC offset
get_timezone_code() {
    local offset=$1
    case $offset in
        "-12") echo "A0" ;;
        "-11") echo "A1" ;;
        "-10") echo "A2" ;;
        "-9") echo "A3" ;;
        "-8") echo "A4" ;;
        "-7") echo "A5" ;;
        "-6") echo "A6" ;;
        "-5") echo "A7" ;;
        "-4") echo "A8" ;;
        "-3") echo "A9" ;;
        "-2") echo "B0" ;;
        "-1") echo "B1" ;;
        "0") echo "B2" ;;
        "+1") echo "B3" ;;
        "+2") echo "B4" ;;
        "+3") echo "B5" ;;
        "+4") echo "B6" ;;
        "+5") echo "B7" ;;
        "+6") echo "B8" ;;
        "+7") echo "B9" ;;
        "+8") echo "C0" ;;
        "+9") echo "C1" ;;
        "+10") echo "C2" ;;
        "+11") echo "C3" ;;
        "+12") echo "C4" ;;
        "+13") echo "C5" ;;
        "+14") echo "C6" ;;
        *) echo "B2" ;; # Default to UTC
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
    
    # Get timezone offset and convert to code
    local tz_offset=$(date +%z | sed 's/^\([+-]\)\([0-9][0-9]\)\([0-9][0-9]\)$/\1\2/')
    local tz_code=$(get_timezone_code "$tz_offset")
    
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
