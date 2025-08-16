#!/bin/bash
# uDOS v1.3 Timezone Code Mapper
# Maps 3-4 letter timezone codes to 2-digit codes for filename generation

#!/bin/bash
# uDOS v1.3 Timezone Code Mapper
# Maps 3-4 letter timezone codes to 2-digit codes for filename generation

get_timezone_code() {
    local input_tz="$1"
    
    # Handle special case for Chinese CST
    if [ "$input_tz" = "CST" ]; then
        # Default to North America CST for now
        echo "01"
        return
    fi
    
    # Standard timezone lookup
    case "$input_tz" in
        # North America
        "EST"|"EDT") echo "02" ;;    # Eastern Standard/Daylight Time
        "PST"|"PDT") echo "34" ;;    # Pacific Standard/Daylight Time
        "MST"|"MDT") echo "35" ;;    # Mountain Standard/Daylight Time
        "AKST"|"AKDT") echo "33" ;;  # Alaska Standard/Daylight Time
        "HST") echo "32" ;;          # Hawaii Standard Time
        
        # South America
        "PET") echo "03" ;;          # Peru Time
        "ART") echo "04" ;;          # Argentina Time
        "BRT") echo "05" ;;          # Brazil Time
        "CLT") echo "06" ;;          # Chile Time
        
        # Africa
        "WET") echo "07" ;;          # Western European Time
        "EAT") echo "13" ;;          # East Africa Time
        "CAT") echo "36" ;;          # Central Africa Time
        "WAT") echo "37" ;;          # West Africa Time
        
        # Europe
        "GMT") echo "09" ;;          # Greenwich Mean Time
        "UTC") echo "38" ;;          # Coordinated Universal Time
        "CET"|"CEST") echo "08" ;;   # Central European Time
        "EET"|"EEST") echo "10" ;;   # Eastern European Time
        "TRT") echo "11" ;;          # Turkey Time
        "MSK") echo "12" ;;          # Moscow Time
        
        # Asia
        "AST") echo "14" ;;          # Arabia Standard Time
        "IRST") echo "15" ;;         # Iran Standard Time
        "PKT") echo "16" ;;          # Pakistan Standard Time
        "IST") echo "17" ;;          # India Standard Time
        "BST") echo "18" ;;          # Bangladesh Standard Time
        "ICT") echo "19" ;;          # Indochina Time
        "MYT") echo "20" ;;          # Malaysia Time
        "WIB") echo "21" ;;          # Western Indonesian Time
        "PHT") echo "22" ;;          # Philippines Time
        "JST") echo "23" ;;          # Japan Standard Time
        "KST") echo "24" ;;          # Korea Standard Time
        "HKT") echo "26" ;;          # Hong Kong Time
        "SGT") echo "27" ;;          # Singapore Time
        
        # Oceania
        "AEDT"|"AEST") echo "28" ;;  # Australian Eastern Time
        "AWST") echo "29" ;;         # Australian Western Time
        "ACST"|"ACDT") echo "30" ;;  # Australian Central Time
        "NZST"|"NZDT") echo "31" ;;  # New Zealand Time
        
        # Default
        *) echo "38" ;;              # Default to UTC
    esac
}

get_current_location_from_citymap() {
    local citymap_path="/Users/agentdigital/uDOS/uCORE/datasets/mapping/datasets/cityMap.json"
    
    if [ ! -f "$citymap_path" ]; then
        return 1
    fi
    
    # Get system timezone
    local system_tz=$(date +%Z)
    
    # Find matching city in cityMap.json
    local location_data=$(jq -r ".[] | select(.TIMEZONE == \"$system_tz\") | \"\(.LAT),\(.LON),\(.TILE)\"" "$citymap_path" | head -1)
    
    if [ -n "$location_data" ] && [ "$location_data" != "null" ]; then
        echo "$location_data"
    else
        return 1
    fi
}

get_timezone_name() {
    local code="$1"
    
    case "$code" in
        "01") echo "Central Standard Time (CST)" ;;
        "02") echo "Eastern Standard Time (EST)" ;;
        "03") echo "Peru Time (PET)" ;;
        "04") echo "Argentina Time (ART)" ;;
        "05") echo "Brazil Time (BRT)" ;;
        "06") echo "Chile Time (CLT)" ;;
        "07") echo "Western European Time (WET)" ;;
        "08") echo "Central European Time (CET)" ;;
        "09") echo "Greenwich Mean Time (GMT)" ;;
        "10") echo "Eastern European Time (EET)" ;;
        "11") echo "Turkey Time (TRT)" ;;
        "12") echo "Moscow Time (MSK)" ;;
        "13") echo "East Africa Time (EAT)" ;;
        "14") echo "Arabia Standard Time (AST)" ;;
        "15") echo "Iran Standard Time (IRST)" ;;
        "16") echo "Pakistan Standard Time (PKT)" ;;
        "17") echo "India Standard Time (IST)" ;;
        "18") echo "Bangladesh Standard Time (BST)" ;;
        "19") echo "Indochina Time (ICT)" ;;
        "20") echo "Malaysia Time (MYT)" ;;
        "21") echo "Western Indonesian Time (WIB)" ;;
        "22") echo "Philippines Time (PHT)" ;;
        "23") echo "Japan Standard Time (JST)" ;;
        "24") echo "Korea Standard Time (KST)" ;;
        "25") echo "China Standard Time (CST)" ;;
        "26") echo "Hong Kong Time (HKT)" ;;
        "27") echo "Singapore Time (SGT)" ;;
        "28") echo "Australian Eastern Time (AEDT)" ;;
        "29") echo "Australian Western Time (AWST)" ;;
        "30") echo "Australian Central Time (ACST)" ;;
        "31") echo "New Zealand Time (NZST)" ;;
        "32") echo "Hawaii Standard Time (HST)" ;;
        "33") echo "Alaska Standard Time (AKST)" ;;
        "34") echo "Pacific Standard Time (PST)" ;;
        "35") echo "Mountain Standard Time (MST)" ;;
        "36") echo "Central Africa Time (CAT)" ;;
        "37") echo "West Africa Time (WAT)" ;;
        "38") echo "Coordinated Universal Time (UTC)" ;;
        *) echo "Unknown Timezone ($code)" ;;
    esac
}

validate_timezone_code() {
    local code="$1"
    
    # Check if it's a valid 2-digit code (01-38)
    if [[ "$code" =~ ^[0-9]{2}$ ]] && [ "$code" -ge 1 ] && [ "$code" -le 38 ]; then
        return 0
    else
        return 1
    fi
}

# Main function for command line usage
case "$1" in
    "map")
        if [ -z "$2" ]; then
            echo "Usage: $0 map TIMEZONE_CODE"
            echo "Example: $0 map AEDT"
            exit 1
        fi
        get_timezone_code "$2"
        ;;
    "name")
        if [ -z "$2" ]; then
            echo "Usage: $0 name 2DIGIT_CODE"
            echo "Example: $0 name 28"
            exit 1
        fi
        get_timezone_name "$2"
        ;;
    "current")
        current_tz=$(date +%Z)
        code=$(get_timezone_code "$current_tz")
        echo "Current timezone: $current_tz"
        echo "2-digit code: $code"
        echo "Full name: $(get_timezone_name "$code")"
        ;;
    "list")
        echo "Available timezone mappings:"
        echo "=========================="
        echo "EST/EDT  → 02 (Eastern Standard Time)"
        echo "CST/CDT  → 01 (Central Standard Time)"
        echo "PST/PDT  → 34 (Pacific Standard Time)"
        echo "MST/MDT  → 35 (Mountain Standard Time)"
        echo "AEDT/AEST → 28 (Australian Eastern Time)"
        echo "CET/CEST → 08 (Central European Time)"
        echo "JST      → 23 (Japan Standard Time)"
        echo "GMT      → 09 (Greenwich Mean Time)"
        echo "UTC      → 38 (Coordinated Universal Time)"
        echo "... and more (see style guide for complete list)"
        ;;
    "help"|"--help"|"-h"|"")
        echo "uDOS v1.3 Timezone Code Mapper"
        echo "Usage: $0 {map|name|current|list|help}"
        echo ""
        echo "Commands:"
        echo "  map TZ       - Convert 3-4 letter timezone to 2-digit code"
        echo "  name CODE    - Get full name from 2-digit code"
        echo "  current      - Show current system timezone info"
        echo "  list         - List all available timezone mappings"
        echo "  help         - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 map AEDT     # Returns: 28"
        echo "  $0 name 28      # Returns: Australian Eastern Time (AEDT)"
        echo "  $0 current      # Shows current system timezone"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
