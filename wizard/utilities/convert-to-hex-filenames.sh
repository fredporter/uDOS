#!/bin/bash
# uDOS Filename Converter v1.3
# Converts existing uDOS files to new hex filename convention

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 uDOS Filename Converter v1.3${NC}"
echo -e "${BLUE}Converting existing files to hex filename convention${NC}"
echo ""

# Function to generate hex code
generate_hex_code() {
    local date_str="$1"
    local time_str="$2"
    local timezone="$3"
    local role="$4"
    local tile="$5"
    
    # Calculate days since 2025-01-01
    local year="${date_str:0:4}"
    local month="${date_str:4:2}"
    local day="${date_str:6:2}"
    local epoch_date="2025-01-01"
    local target_date="${year}-${month}-${day}"
    
    # Simple day calculation (approximate)
    local days=$(( ($(date -d "$target_date" +%s) - $(date -d "$epoch_date" +%s)) / 86400 ))
    
    # Time encoding
    local hour="${time_str:0:2}"
    local minute="${time_str:2:2}"
    local second="${time_str:4:2}"
    
    # Encode timezone (UTC offset + 12)
    local tz_offset=0
    case "$timezone" in
        *C0*|*+8*) tz_offset=20 ;;
        *AE*|*+4*) tz_offset=16 ;;
        *UT*|*+0*) tz_offset=12 ;;
        *PS*|*-8*) tz_offset=4 ;;
        *) tz_offset=12 ;; # Default to UTC
    esac
    
    # Role encoding
    local role_code=10 # Default to Wizard
    case "$role" in
        *ghost*) role_code=1 ;;
        *tomb*) role_code=2 ;;
        *drone*) role_code=4 ;;
        *imp*) role_code=6 ;;
        *sorcerer*) role_code=8 ;;
        *wizard*) role_code=10 ;;
    esac
    
    # Generate simplified hex (for demonstration)
    local hex1=$(printf "%02X" $((days % 256)))
    local hex2=$(printf "%02X" $((hour * 8 + minute / 8)))
    local hex3=$(printf "%02X" $((second * 4 + tz_offset / 4)))
    local hex4=$(printf "%02X" $((role_code * 16 + tile)))
    
    echo "${hex1}${hex2}${hex3}${hex4}"
}

# Function to get file type prefix
get_file_prefix() {
    local filename="$1"
    local path="$2"
    
    # Determine prefix based on existing filename and location
    case "$filename" in
        *uDEV*|*DEV*) echo "uDEV" ;;
        *uDOC*|*DOC*) echo "uDOC" ;;
        *uREP*|*REP*|*REPORT*) echo "uREP" ;;
        *uLOG*|*LOG*) echo "uLOG" ;;
        *NOTE*|*note*) echo "uNOT" ;;
        *TASK*|*task*) echo "uTDO" ;;
        *CONFIG*|*config*) echo "uCFG" ;;
        *SCRIPT*|*script*) echo "uSCR" ;;
        *TEMPLATE*|*template*) echo "uTMP" ;;
        *MEMORY*|*memory*) echo "uMEM" ;;
        *MISSION*|*mission*) echo "uMIS" ;;
        *MILESTONE*|*milestone*) echo "uMIL" ;;
        *LEGACY*|*legacy*) echo "uLEG" ;;
        *BACKUP*|*backup*) echo "uBKP" ;;
        *ARCHIVE*|*archive*) echo "uARC" ;;
        *TEST*|*test*) echo "uTST" ;;
        *ERROR*|*error*) echo "uERR" ;;
        *DEBUG*|*debug*) echo "uDEB" ;;
        *)
            # Determine by path
            case "$path" in
                */wizard/*) echo "uDEV" ;;
                */docs/*) echo "uDOC" ;;
                */logs/*) echo "uLOG" ;;
                */scripts/*) echo "uSCR" ;;
                */templates/*) echo "uTMP" ;;
                */sandbox/*) echo "uTDO" ;;
                *) echo "uDOC" ;; # Default
            esac
            ;;
    esac
}

# Function to convert filename
convert_filename() {
    local old_file="$1"
    local old_filename=$(basename "$old_file")
    local old_dir=$(dirname "$old_file")
    
    # Skip if already in hex format
    if [[ "$old_filename" =~ ^u[A-Z]{3}-[0-9A-F]{8}- ]]; then
        echo -e "${GREEN}✅ Already converted: $old_filename${NC}"
        return 0
    fi
    
    # Extract components from old filename
    local prefix=""
    local date_part=""
    local time_part=""
    local timezone=""
    local title=""
    
    # Parse existing uDOS filename patterns
    if [[ "$old_filename" =~ ^uDEV-([0-9]{8})-([0-9]{6})([A-Z0-9]{2})-(.*).md$ ]]; then
        prefix="uDEV"
        date_part="${BASH_REMATCH[1]}"
        time_part="${BASH_REMATCH[2]}"
        timezone="${BASH_REMATCH[3]}"
        title="${BASH_REMATCH[4]}"
    elif [[ "$old_filename" =~ ^u[A-Z]+-([0-9]{8})-([0-9]{6})([A-Z0-9]{2})-(.*).md$ ]]; then
        prefix=$(get_file_prefix "$old_filename" "$old_dir")
        date_part="${BASH_REMATCH[1]}"
        time_part="${BASH_REMATCH[2]}"
        timezone="${BASH_REMATCH[3]}"
        title="${BASH_REMATCH[4]}"
    else
        # Generate components for non-standard files
        prefix=$(get_file_prefix "$old_filename" "$old_dir")
        date_part=$(date +%Y%m%d)
        time_part=$(date +%H%M%S)
        timezone="C0"
        title="${old_filename%.*}"
        title="${title#*-}" # Remove any existing prefix
    fi
    
    # Limit title to 26 characters
    if [ ${#title} -gt 26 ]; then
        title="${title:0:23}..."
    fi
    
    # Generate hex code
    local hex_code=$(generate_hex_code "$date_part" "$time_part" "$timezone" "wizard" "0")
    
    # Create new filename
    local new_filename="${prefix}-${hex_code}-${title}.md"
    local new_file="${old_dir}/${new_filename}"
    
    # Rename file
    if [ "$old_file" != "$new_file" ]; then
        mv "$old_file" "$new_file"
        echo -e "${GREEN}✅ Converted: ${old_filename} → ${new_filename}${NC}"
    else
        echo -e "${YELLOW}⚠️  No change needed: $old_filename${NC}"
    fi
}

# Find and convert files
echo -e "${BLUE}🔍 Finding files to convert...${NC}"

# Convert wizard development files
if [ -d "$UDOS_ROOT/wizard/notes" ]; then
    echo -e "${BLUE}📁 Converting wizard/notes files...${NC}"
    find "$UDOS_ROOT/wizard/notes" -name "*.md" -type f | while read -r file; do
        convert_filename "$file"
    done
fi

# Convert any remaining old format files
echo -e "${BLUE}📁 Converting remaining uDOS files...${NC}"
find "$UDOS_ROOT" -name "uDEV-*.md" -o -name "uDOC-*.md" -o -name "uREP-*.md" -o -name "uLOG-*.md" | while read -r file; do
    # Skip if in archived or backup directories
    if [[ "$file" =~ (archived|backup|\.git) ]]; then
        continue
    fi
    convert_filename "$file"
done

echo ""
echo -e "${GREEN}🎉 Filename conversion complete!${NC}"
echo -e "${BLUE}All files now use the new hex filename convention.${NC}"
