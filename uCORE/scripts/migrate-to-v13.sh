#!/bin/bash
# uDOS v1.3 Migration Script
# Converts existing files to new CAPS-NUMERIC-DASH naming convention

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

TIMEZONE_MAPPER="/Users/agentdigital/uDOS/uCORE/scripts/timezone-mapper-v13.sh"
FILENAME_GENERATOR="/Users/agentdigital/uDOS/uCORE/scripts/generate-filename-v3.sh"

migrate_to_v13() {
    local target_dir="$1"
    local dry_run="$2"
    
    echo -e "${CYAN}🔄 uDOS v1.3 Migration Tool${NC}"
    echo "================================"
    
    if [ -z "$target_dir" ]; then
        target_dir="."
    fi
    
    if [ "$dry_run" = "--dry-run" ]; then
        echo -e "${YELLOW}⚠️ DRY RUN MODE - No files will be changed${NC}"
        echo ""
    fi
    
    local total_files=0
    local migrated_files=0
    local skipped_files=0
    local error_files=0
    
    echo "📁 Scanning directory: $target_dir"
    echo ""
    
    # Process all .md files except special ones
    while IFS= read -r -d '' file; do
        local basename=$(basename "$file")
        local dirname=$(dirname "$file")
        
        # Skip special files and already compliant files
        if should_skip_file "$basename"; then
            continue
        fi
        
        ((total_files++))
        
        echo -n "📄 Processing: $basename"
        
        # Check if already v1.3 compliant
        if is_v13_compliant "$basename"; then
            echo -e " ${GREEN}✅ Already compliant${NC}"
            ((skipped_files++))
            continue
        fi
        
        # Attempt migration
        local new_name=$(generate_migrated_filename "$basename" "$file")
        
        if [ -n "$new_name" ] && [ "$new_name" != "$basename" ]; then
            local new_path="$dirname/$new_name"
            
            echo -e " ${YELLOW}→${NC} $new_name"
            
            if [ "$dry_run" != "--dry-run" ]; then
                if [ ! -e "$new_path" ]; then
                    mv "$file" "$new_path"
                    echo -e "  ${GREEN}✅ Migrated successfully${NC}"
                    ((migrated_files++))
                else
                    echo -e "  ${RED}❌ Target file already exists${NC}"
                    ((error_files++))
                fi
            else
                echo -e "  ${BLUE}ℹ️ Would migrate (dry run)${NC}"
                ((migrated_files++))
            fi
        else
            echo -e " ${RED}❌ Could not generate new name${NC}"
            ((error_files++))
        fi
        
    done < <(find "$target_dir" -name "*.md" -type f -print0)
    
    # Summary
    echo ""
    echo -e "${CYAN}📊 Migration Summary${NC}"
    echo "==================="
    echo "Total files processed: $total_files"
    echo -e "Migrated: ${GREEN}$migrated_files${NC}"
    echo -e "Already compliant: ${YELLOW}$skipped_files${NC}"
    echo -e "Errors: ${RED}$error_files${NC}"
    
    if [ "$dry_run" = "--dry-run" ]; then
        echo ""
        echo -e "${BLUE}ℹ️ To perform actual migration, run without --dry-run${NC}"
    fi
}

should_skip_file() {
    local basename="$1"
    
    # Skip special files
    if [[ "$basename" =~ ^(README|CHANGELOG|LICENSE|\..*).md$ ]]; then
        return 0
    fi
    
    # Skip already migrated files in uLOG format
    if [[ "$basename" =~ ^uLOG-[0-9]{8}-[0-9]{4}-[0-9]{2}-[0-9]{2}[A-Z]{2}[0-9]{2}\.md$ ]]; then
        return 0
    fi
    
    return 1
}

is_v13_compliant() {
    local basename="$1"
    
    # Check v1.3 format: uTYPE-YYYYMMDD-HHMM-TTZ-MMLLNN.md
    if [[ "$basename" =~ ^u[A-Z]+-[0-9]{8}-[0-9]{4}-[0-9]{2}-[0-9]{2}[A-Z]{2}[0-9]{2}\.md$ ]]; then
        return 0
    fi
    
    return 1
}

generate_migrated_filename() {
    local old_basename="$1"
    local full_path="$2"
    
    # Extract file type from name patterns
    local file_type=$(detect_file_type "$old_basename" "$full_path")
    
    # Extract description
    local description=$(extract_description "$old_basename")
    
    # Get current timezone code
    local tz_code="28"  # Default to AEST for now
    if [ -f "$TIMEZONE_MAPPER" ]; then
        tz_code=$("$TIMEZONE_MAPPER" map "$(date +%Z)" 2>/dev/null || echo "28")
    fi
    
    # Get current location code
    local location_code=$(get_current_location_code)
    
    # Generate timestamp
    local date_stamp=$(date +%Y%m%d)
    local time_stamp=$(date +%H%M)
    
    # Generate new filename
    echo "u${file_type}-${date_stamp}-${time_stamp}-${tz_code}-${location_code}.md"
}

detect_file_type() {
    local basename="$1"
    local full_path="$2"
    
    # Convert to uppercase for pattern matching
    local upper_basename=$(echo "$basename" | tr '[:lower:]' '[:upper:]')
    
    # Check content for better detection
    local has_script_content=false
    local has_log_content=false
    local has_mission_content=false
    
    if [ -f "$full_path" ]; then
        if grep -qi "#!/bin/bash\|script\|automation\|build" "$full_path" 2>/dev/null; then
            has_script_content=true
        fi
        if grep -qi "log\|timestamp\|error\|warning\|info" "$full_path" 2>/dev/null; then
            has_log_content=true
        fi
        if grep -qi "mission\|project\|task\|goal" "$full_path" 2>/dev/null; then
            has_mission_content=true
        fi
    fi
    
    # Pattern-based detection with content hints
    if [[ "$upper_basename" =~ (SCRIPT|BUILD|AUTO|RUN) ]] || [ "$has_script_content" = true ]; then
        echo "SCRIPT"
    elif [[ "$upper_basename" =~ (LOG|ACTIVITY|SYSTEM|DEBUG) ]] || [ "$has_log_content" = true ]; then
        echo "LOG"
    elif [[ "$upper_basename" =~ (MISSION|PROJECT|TASK) ]] || [ "$has_mission_content" = true ]; then
        echo "MISSION"
    elif [[ "$upper_basename" =~ (DOC|MANUAL|GUIDE|HELP|README) ]]; then
        echo "DOC"
    elif [[ "$upper_basename" =~ (DATA|DATASET|INFO|STATS) ]]; then
        echo "DATA"
    elif [[ "$upper_basename" =~ (CONFIG|SETTING|SETUP|CONF) ]]; then
        echo "CONFIG"
    elif [[ "$upper_basename" =~ (TEMPLATE|TMPL|FORM) ]]; then
        echo "TEMPLATE"
    elif [[ "$upper_basename" =~ (REPORT|SUMMARY|ANALYSIS) ]]; then
        echo "REPORT"
    elif [[ "$upper_basename" =~ (TEST|VALIDATION|CHECK) ]]; then
        echo "TEST"
    elif [[ "$upper_basename" =~ (BACKUP|BAK|ARCHIVE) ]]; then
        echo "BACKUP"
    elif [[ "$upper_basename" =~ (LEGACY|OLD|ARCHIVE|HIST) ]]; then
        echo "LEGACY"
    elif [[ "$upper_basename" =~ (TMP|TEMP|TEMPORARY) ]]; then
        echo "TMP"
    else
        echo "DATA"  # Default fallback
    fi
}

extract_description() {
    local basename="$1"
    
    # Remove extension
    local name_without_ext="${basename%.md}"
    
    # Clean up common patterns
    local description=$(echo "$name_without_ext" | \
        sed 's/-/ /g' | \
        sed 's/_/ /g' | \
        sed 's/[0-9]\{8\}//g' | \
        sed 's/[0-9]\{4\}//g' | \
        sed 's/  */ /g' | \
        sed 's/^ *//; s/ *$//')
    
    # Capitalize first letter
    description="$(echo "${description:0:1}" | tr '[:lower:]' '[:upper:]')${description:1}"
    
    # Fallback if empty
    if [ -z "$description" ]; then
        description="Migrated file"
    fi
    
    echo "$description"
}

get_current_location_code() {
    # Try to get from user config first
    if [ -f "/Users/agentdigital/uDOS/sandbox/user.md" ]; then
        local location=$(grep "^Location:" /Users/agentdigital/uDOS/sandbox/user.md 2>/dev/null | cut -d' ' -f2 | tr -d '[]')
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

show_help() {
    echo -e "${CYAN}🔄 uDOS v1.3 Migration Tool${NC}"
    echo ""
    echo "Usage: $0 [directory] [options]"
    echo ""
    echo "Options:"
    echo "  --dry-run         - Preview changes without modifying files"
    echo "  --help, -h        - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                - Migrate current directory"
    echo "  $0 ./uMEMORY      - Migrate uMEMORY directory"
    echo "  $0 . --dry-run    - Preview migration of current directory"
    echo ""
    echo "New v1.3 Format: uTYPE-YYYYMMDD-HHMM-TTZ-MMLLNN.md"
    echo "  uTYPE     - File type (SCRIPT, LOG, DATA, DOC, etc.)"
    echo "  YYYYMMDD  - Date (e.g., 20250816)"
    echo "  HHMM      - Time (e.g., 2244)"
    echo "  TTZ       - Timezone code (28 for AEST, etc.)"
    echo "  MMLLNN    - Location (Map+Letters+Numbers)"
}

# Command line interface
case "$1" in
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        migrate_to_v13 "." "$2"
        ;;
    *)
        if [ -d "$1" ]; then
            migrate_to_v13 "$1" "$2"
        else
            echo -e "${RED}❌ Directory not found: $1${NC}"
            echo "Run '$0 help' for usage information"
            exit 1
        fi
        ;;
esac
