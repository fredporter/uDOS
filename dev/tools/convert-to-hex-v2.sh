#!/bin/bash
# uDOS Hex Filename Converter v2.0
# Converts timestamp-based uDOS files to new hex filename convention

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 uDOS Hex Filename Converter v2.0${NC}"
echo -e "${BLUE}Converting timestamp files to hex filename convention${NC}"
echo ""

# Function to calculate days since epoch (2025-01-01)
calculate_days_since_epoch() {
    local date_str="$1"
    local year="${date_str:0:4}"
    local month="${date_str:4:2}"
    local day="${date_str:6:2}"
    
    # Use date command to calculate difference
    local epoch_date="2025-01-01"
    local target_date="${year}-${month}-${day}"
    
    # Simple calculation for days since 2025-01-01
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
    local role="$4"
    local tile_num="$5"
    
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
    
    # Role encoding (installation type)
    local role_encoded=10 # Default wizard
    case "$role" in
        "ghost") role_encoded=1 ;;
        "tomb") role_encoded=2 ;;
        "drone") role_encoded=4 ;;
        "imp") role_encoded=6 ;;
        "sorcerer") role_encoded=8 ;;
        "wizard") role_encoded=10 ;;
        *) role_encoded=10 ;;
    esac
    
    # Create composite values for hex encoding
    local date_val=$((days % 256))
    local time_val=$(((hour * 60 + minute) % 256))
    local tz_sec_val=$(((tz_encoded * 16 + second / 4) % 256))
    local role_tile_val=$(((role_encoded * 16 + tile_num) % 256))
    
    # Generate 8-character hex code
    printf "%02X%02X%02X%02X" $date_val $time_val $tz_sec_val $role_tile_val
}

# Function to extract title from old filename
extract_title() {
    local filename="$1"
    local title=""
    
    # Extract title after the timezone code and dash
    if [[ "$filename" =~ ^u[A-Z]+-[0-9]{8}-[0-9]{6}[A-Z0-9]{2}-(.*)\.[^.]+$ ]]; then
        title="${BASH_REMATCH[1]}"
    else
        # Fallback: use everything after last dash
        title="${filename##*-}"
        title="${title%.*}" # Remove extension
    fi
    
    # Clean up title
    title=$(echo "$title" | sed 's/[^a-zA-Z0-9-]//g')
    
    # Limit to 26 characters
    if [ ${#title} -gt 26 ]; then
        title="${title:0:23}..."
    fi
    
    echo "$title"
}

# Function to convert single file
convert_file() {
    local old_file="$1"
    local old_filename=$(basename "$old_file")
    local old_dir=$(dirname "$old_file")
    
    # Check if file matches timestamp pattern
    if [[ ! "$old_filename" =~ ^(u[A-Z]+)-([0-9]{8})-([0-9]{6})([A-Z0-9]{2})-(.*)\.(md|txt|log)$ ]]; then
        echo -e "${YELLOW}⚠️  Skipping non-standard file: $old_filename${NC}"
        return 0
    fi
    
    local prefix="${BASH_REMATCH[1]}"
    local date_part="${BASH_REMATCH[2]}"
    local time_part="${BASH_REMATCH[3]}"
    local timezone_alpha="${BASH_REMATCH[4]}"
    local title_part="${BASH_REMATCH[5]}"
    local extension="${BASH_REMATCH[6]}"
    
    # Extract clean title
    local title=$(extract_title "$old_filename")
    
    # Generate hex code
    local hex_code=$(generate_hex_code "$date_part" "$time_part" "$timezone_alpha" "wizard" "0")
    
    # Create new filename
    local new_filename="${prefix}-${hex_code}-${title}.${extension}"
    local new_file="${old_dir}/${new_filename}"
    
    # Check if already exists
    if [ -f "$new_file" ] && [ "$old_file" != "$new_file" ]; then
        echo -e "${YELLOW}⚠️  Target exists, skipping: $new_filename${NC}"
        return 0
    fi
    
    # Rename file
    if [ "$old_file" != "$new_file" ]; then
        mv "$old_file" "$new_file"
        echo -e "${GREEN}✅ ${old_filename}${NC}"
        echo -e "${GREEN}   → ${new_filename}${NC}"
    else
        echo -e "${YELLOW}⚠️  No change needed: $old_filename${NC}"
    fi
}

# Main conversion process
echo -e "${BLUE}🔍 Finding timestamp-based files to convert...${NC}"

# Find all uDOS files with timestamp pattern
find "$UDOS_ROOT" -type f \( -name "u*-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]*" \) | \
grep -E '\.(md|txt|log)$' | \
grep -v -E '(\.git|archived|backup|temp)' | \
sort | \
while read -r file; do
    convert_file "$file"
done

echo ""
echo -e "${GREEN}🎉 Hex conversion complete!${NC}"
echo -e "${BLUE}Files now use 8-character hex codes instead of timestamps.${NC}"

# Show sample of converted files
echo ""
echo -e "${BLUE}📋 Sample of converted files:${NC}"
find "$UDOS_ROOT" -name "u*-[0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F][0-9A-F]-*" | head -5 | while read -r file; do
    echo -e "${GREEN}  $(basename "$file")${NC}"
done
