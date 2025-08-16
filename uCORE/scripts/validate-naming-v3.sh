#!/bin/bash
# uDOS v3.0 Naming Convention Validator
# Validates files against the new CAPS-NUMERIC-DASH naming standard

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

validate_v3_naming() {
    local target="$1"
    local fix_mode="$2"
    
    echo -e "${CYAN}🔍 uDOS v3.0 Naming Validator${NC}"
    echo "================================"
    
    if [ -z "$target" ]; then
        echo -e "${RED}❌ No target specified${NC}"
        echo "Usage: $0 [file|directory] [--fix]"
        return 1
    fi
    
    local total_files=0
    local valid_files=0
    local invalid_files=0
    local fixed_files=0
    
    if [ -f "$target" ]; then
        # Single file validation
        validate_single_file "$target" "$fix_mode"
        return $?
    elif [ -d "$target" ]; then
        # Directory validation
        echo "📁 Scanning directory: $target"
        echo ""
        
        # Find all .md files except special ones
        while IFS= read -r -d '' file; do
            local basename=$(basename "$file")
            
            # Skip special files
            if [[ "$basename" =~ ^(README|CHANGELOG|LICENSE|\..*).md$ ]]; then
                continue
            fi
            
            ((total_files++))
            
            if validate_single_file "$file" "$fix_mode"; then
                ((valid_files++))
            else
                ((invalid_files++))
                if [ "$fix_mode" = "--fix" ]; then
                    if fix_filename "$file"; then
                        ((fixed_files++))
                    fi
                fi
            fi
            
        done < <(find "$target" -name "*.md" -type f -print0)
        
        # Summary
        echo ""
        echo -e "${CYAN}📊 Validation Summary${NC}"
        echo "==================="
        echo "Total files: $total_files"
        echo -e "Valid files: ${GREEN}$valid_files${NC}"
        echo -e "Invalid files: ${RED}$invalid_files${NC}"
        
        if [ "$fix_mode" = "--fix" ]; then
            echo -e "Fixed files: ${YELLOW}$fixed_files${NC}"
        fi
        
        if [ $invalid_files -eq 0 ]; then
            echo -e "${GREEN}🎉 All files comply with v3.0 naming convention!${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ Some files need attention${NC}"
            if [ "$fix_mode" != "--fix" ]; then
                echo "Run with --fix to automatically correct naming issues"
            fi
            return 1
        fi
    else
        echo -e "${RED}❌ Target not found: $target${NC}"
        return 1
    fi
}

validate_single_file() {
    local file="$1"
    local fix_mode="$2"
    local basename=$(basename "$file")
    local issues=()
    
    echo -n "📄 Validating: $basename"
    
    # Check v3.0 filename format: uTYPE-YYYYMMDD-HHMM-TZ-MMLLNN.md
    if [[ "$basename" =~ ^u[A-Z]+-[0-9]{8}-[0-9]{4}-[0-9]{2}-[0-9]{2}[A-Z]{2}[0-9]{2}\.md$ ]]; then
        echo -e " ${GREEN}✅${NC}"
        
        # Detailed validation
        validate_filename_components "$basename"
        return $?
    else
        echo -e " ${RED}❌${NC}"
        
        # Analyze specific issues
        analyze_filename_issues "$basename" issues
        
        for issue in "${issues[@]}"; do
            echo -e "  ${RED}• $issue${NC}"
        done
        
        return 1
    fi
}

validate_filename_components() {
    local filename="$1"
    local issues=()
    
    # Extract components
    local file_type=$(echo "$filename" | cut -d'-' -f1 | sed 's/^u//')
    local date_part=$(echo "$filename" | cut -d'-' -f2)
    local time_part=$(echo "$filename" | cut -d'-' -f3)
    local tz_part=$(echo "$filename" | cut -d'-' -f4)
    local location_part=$(echo "$filename" | cut -d'-' -f5 | sed 's/\.md$//')
    
    # Validate file type
    local valid_types=("SCRIPT" "LOG" "DATA" "DOC" "MISSION" "LEGACY" "CONFIG" "TEMPLATE" "REPORT" "TEST" "BACKUP" "TMP")
    local type_valid=false
    for valid_type in "${valid_types[@]}"; do
        if [ "$file_type" = "$valid_type" ]; then
            type_valid=true
            break
        fi
    done
    
    if [ "$type_valid" = false ]; then
        issues+=("Invalid file type: $file_type")
    fi
    
    # Validate date (YYYYMMDD)
    if ! [[ "$date_part" =~ ^[0-9]{8}$ ]]; then
        issues+=("Invalid date format: $date_part")
    else
        # Check if date is valid (macOS compatible)
        local year=${date_part:0:4}
        local month=${date_part:4:2}
        local day=${date_part:6:2}
        
        if [ "$month" -lt 1 ] || [ "$month" -gt 12 ] || [ "$day" -lt 1 ] || [ "$day" -gt 31 ]; then
            issues+=("Invalid date values: $date_part")
        fi
    fi
    
    # Validate time (HHMM)
    if ! [[ "$time_part" =~ ^[0-9]{4}$ ]] || [ "${time_part:0:2}" -gt 23 ] || [ "${time_part:2:2}" -gt 59 ]; then
        issues+=("Invalid time format: $time_part")
    fi
    
    # Validate timezone code (00-38)
    if ! [[ "$tz_part" =~ ^[0-9]{2}$ ]] || [ "$tz_part" -gt 38 ]; then
        issues+=("Invalid timezone code: $tz_part (range: 00-38)")
    fi
    
    # Validate location code (MMLLNN)
    if ! [[ "$location_part" =~ ^[0-9]{2}[A-Z]{2}[0-9]{2}$ ]]; then
        issues+=("Invalid location code format: $location_part (expected: MMLLNN)")
    else
        local map_num=${location_part:0:2}
        local tile_num=${location_part:4:2}
        
        if [ "$map_num" -gt 99 ]; then
            issues+=("Invalid map number: $map_num (max: 99)")
        fi
        
        if [ "$tile_num" -lt 1 ] || [ "$tile_num" -gt 99 ]; then
            issues+=("Invalid tile number: $tile_num (range: 01-99)")
        fi
    fi
    
    # Report component validation results
    if [ ${#issues[@]} -eq 0 ]; then
        echo "  ✅ All components valid"
        return 0
    else
        for issue in "${issues[@]}"; do
            echo -e "  ${YELLOW}⚠️ $issue${NC}"
        done
        return 1
    fi
}

analyze_filename_issues() {
    local filename="$1"
    local -n issues_ref=$2
    
    # Check basic structure
    if [[ ! "$filename" =~ \.md$ ]]; then
        issues_ref+=("Missing .md extension")
    fi
    
    if [[ ! "$filename" =~ ^u[A-Z]+ ]]; then
        issues_ref+=("Missing uTYPE prefix (e.g., uSCRIPT, uLOG, uDATA)")
    fi
    
    # Count dashes
    local dash_count=$(echo "$filename" | tr -cd '-' | wc -c)
    if [ "$dash_count" -ne 4 ]; then
        issues_ref+=("Incorrect number of dashes: $dash_count (expected: 4)")
    fi
    
    # Check for lowercase
    if [[ "$filename" =~ [a-z] ]]; then
        issues_ref+=("Contains lowercase letters (v3.0 requires CAPS-NUMERIC-DASH only)")
    fi
    
    # Check for underscores
    if [[ "$filename" =~ _ ]]; then
        issues_ref+=("Contains underscores (use dashes instead)")
    fi
    
    # Check for invalid characters
    if [[ "$filename" =~ [^A-Z0-9.-] ]]; then
        issues_ref+=("Contains invalid characters (only A-Z, 0-9, -, . allowed)")
    fi
}

fix_filename() {
    local file="$1"
    local basename=$(basename "$file")
    local dirname=$(dirname "$file")
    
    echo ""
    echo -e "${YELLOW}🔧 Attempting to fix: $basename${NC}"
    
    # Try to extract meaningful components and reconstruct
    local file_type=""
    local description=""
    
    # Common patterns to detect file type
    if [[ "$basename" =~ (script|automation|build) ]]; then
        file_type="SCRIPT"
    elif [[ "$basename" =~ (log|activity|system) ]]; then
        file_type="LOG"
    elif [[ "$basename" =~ (data|dataset|info) ]]; then
        file_type="DATA"
    elif [[ "$basename" =~ (doc|manual|guide|readme) ]]; then
        file_type="DOC"
    elif [[ "$basename" =~ (mission|project|task) ]]; then
        file_type="MISSION"
    elif [[ "$basename" =~ (legacy|archive|old) ]]; then
        file_type="LEGACY"
    elif [[ "$basename" =~ (config|setting|setup) ]]; then
        file_type="CONFIG"
    elif [[ "$basename" =~ (template|tmpl) ]]; then
        file_type="TEMPLATE"
    elif [[ "$basename" =~ (report|summary) ]]; then
        file_type="REPORT"
    elif [[ "$basename" =~ (test|validation) ]]; then
        file_type="TEST"
    elif [[ "$basename" =~ (backup|bak) ]]; then
        file_type="BACKUP"
    elif [[ "$basename" =~ (tmp|temp|temporary) ]]; then
        file_type="TMP"
    else
        file_type="DATA"  # Default fallback
    fi
    
    # Generate new filename
    local new_filename=$(/Users/agentdigital/uDOS/uCORE/scripts/generate-filename-v3.sh "$file_type" "Migrated from $basename" 2>/dev/null | tail -1)
    
    if [ -n "$new_filename" ] && [ "$new_filename" != "$basename" ]; then
        local new_path="$dirname/$new_filename"
        
        echo "  Old: $basename"
        echo "  New: $new_filename"
        
        if [ ! -e "$new_path" ]; then
            mv "$file" "$new_path"
            echo -e "  ${GREEN}✅ Successfully renamed${NC}"
            return 0
        else
            echo -e "  ${RED}❌ Target file already exists${NC}"
            return 1
        fi
    else
        echo -e "  ${RED}❌ Could not generate valid filename${NC}"
        return 1
    fi
}

show_help() {
    echo -e "${CYAN}🔍 uDOS v3.0 Naming Convention Validator${NC}"
    echo ""
    echo "Usage: $0 [target] [options]"
    echo ""
    echo "Targets:"
    echo "  file.md           - Validate single file"
    echo "  directory/        - Validate all .md files in directory"
    echo "  .                 - Validate current directory"
    echo ""
    echo "Options:"
    echo "  --fix             - Automatically fix naming issues"
    echo "  --help, -h        - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 uSCRIPT-20250816-1640-33-00SY43.md"
    echo "  $0 ./uMEMORY --fix"
    echo "  $0 . --fix"
    echo ""
    echo "v3.0 Format: uTYPE-YYYYMMDD-HHMM-TZ-MMLLNN.md"
    echo "  uTYPE     - File type (SCRIPT, LOG, DATA, DOC, etc.)"
    echo "  YYYYMMDD  - Date (e.g., 20250816)"
    echo "  HHMM      - Time (e.g., 1640)"
    echo "  TZ        - Timezone code (00-38)"
    echo "  MMLLNN    - Location (Map+Letters+Numbers)"
}

# Command line interface
case "$1" in
    "help"|"--help"|"-h")
        show_help
        ;;
    "")
        echo -e "${RED}❌ No target specified${NC}"
        echo "Usage: $0 [file|directory] [--fix]"
        echo "Run '$0 help' for more information"
        exit 1
        ;;
    *)
        validate_v3_naming "$1" "$2"
        exit $?
        ;;
esac
