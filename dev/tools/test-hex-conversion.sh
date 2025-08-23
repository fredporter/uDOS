#!/bin/bash
# uDOS Hex Filename Converter v2.0 - Test Mode
# Shows what timestamp files would be converted to

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to calculate days since epoch (2025-01-01)
calculate_days_since_epoch() {
    local date_str="$1"
    local year="${date_str:0:4}"
    local month="${date_str:4:2}"
    local day="${date_str:6:2}"
    
    # Calculate days difference from 2025-01-01
    local epoch_date="20250101"
    local target_date="$date_str"
    
    # Simple calculation (approximate)
    local year_diff=$((year - 2025))
    local days=$((year_diff * 365))
    
    # Add days for months (approximate)
    case "$month" in
        "01") days=$((days + 0)) ;;
        "02") days=$((days + 31)) ;;
        "03") days=$((days + 59)) ;;
        "04") days=$((days + 90)) ;;
        "05") days=$((days + 120)) ;;
        "06") days=$((days + 151)) ;;
        "07") days=$((days + 181)) ;;
        "08") days=$((days + 212)) ;;
        "09") days=$((days + 243)) ;;
        "10") days=$((days + 273)) ;;
        "11") days=$((days + 304)) ;;
        "12") days=$((days + 334)) ;;
    esac
    
    days=$((days + $((10#$day)) - 1))
    echo $days
}

# Function to generate hex code
generate_hex_code() {
    local date_str="$1"
    local time_str="$2"
    local timezone_alpha="$3"
    
    # Calculate days since epoch
    local days=$(calculate_days_since_epoch "$date_str")
    
    # Extract time components (force decimal interpretation)
    local hour=$((10#${time_str:0:2}))
    local minute=$((10#${time_str:2:2}))
    local second=$((10#${time_str:4:2}))
    
    # Convert timezone alpha code to UTC offset encoding
    local tz_encoded=12 # Default UTC
    case "$timezone_alpha" in
        "C0"|"c0") tz_encoded=20 ;; # UTC+8
        "AE"|"ae") tz_encoded=16 ;; # UTC+4
        "UT"|"ut") tz_encoded=12 ;; # UTC+0
        "PS"|"ps") tz_encoded=4 ;;  # UTC-8
        *) tz_encoded=12 ;;         # Default UTC
    esac
    
    # Create composite values for hex encoding
    local date_val=$((days % 256))
    local time_val=$(((hour * 60 + minute) % 256))
    local tz_sec_val=$(((tz_encoded * 16 + second / 4) % 256))
    local role_tile_val=$((10 * 16 + 0)) # wizard=10, tile=0
    
    # Generate 8-character hex code
    printf "%02X%02X%02X%02X" $date_val $time_val $tz_sec_val $role_tile_val
}

echo "🧪 Testing hex conversion on sample files:"
echo ""

# Test on a few sample files
test_files=(
    "uDEV-20250817-180846C0-Directory-Rename-Summary.md"
    "uDEV-20250816-234500C0-System-Session.md"
    "uDOC-20250817-193620AE-Timezone-Alpha-Update.md"
)

for filename in "${test_files[@]}"; do
    if [[ "$filename" =~ ^(u[A-Z]+)-([0-9]{8})-([0-9]{6})([A-Z0-9]{2})-(.*)\.(md|txt|log)$ ]]; then
        prefix="${BASH_REMATCH[1]}"
        date_part="${BASH_REMATCH[2]}"
        time_part="${BASH_REMATCH[3]}"
        timezone_alpha="${BASH_REMATCH[4]}"
        title_part="${BASH_REMATCH[5]}"
        extension="${BASH_REMATCH[6]}"
        
        # Clean title (limit to 26 chars)
        title=$(echo "$title_part" | sed 's/[^a-zA-Z0-9-]//g')
        if [ ${#title} -gt 26 ]; then
            title="${title:0:23}..."
        fi
        
        hex_code=$(generate_hex_code "$date_part" "$time_part" "$timezone_alpha")
        new_filename="${prefix}-${hex_code}-${title}.${extension}"
        
        echo "OLD: $filename"
        echo "NEW: $new_filename"
        echo "HEX: $hex_code (date: $date_part, time: $time_part, tz: $timezone_alpha)"
        echo ""
    fi
done

echo "Ready to run actual conversion? The script will:"
echo "1. Find all timestamp-based uDOS files"
echo "2. Convert to 8-character hex format"
echo "3. Preserve original title (max 26 chars)"
echo "4. Maintain file extensions and prefixes"
