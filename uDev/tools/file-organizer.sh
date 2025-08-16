#!/bin/bash

# uDEV File Organizer v1.3
# Automatic filing system for completed scripts and workflows

set -euo pipefail

# Configuration
readonly UDEV_ROOT="/Users/agentdigital/uDOS/uDEV"
readonly SCRIPTS_DIR="$UDEV_ROOT/scripts"
readonly WORKFLOWS_DIR="$UDEV_ROOT/workflows"
readonly LOGS_DIR="$UDEV_ROOT/logs"
readonly TIMEZONE_CODE="28"
readonly LOCATION_CODE="00SY01"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >&2
}

# Generate archive filename with proper naming convention
generate_archive_name() {
    local original_file="$1"
    local file_type="$2"
    local timestamp=$(date '+%Y%m%d-%H%M')
    
    # Extract base name without extension
    local base_name=$(basename "$original_file" .sh)
    local clean_name=$(echo "$base_name" | tr '[:lower:]' '[:upper:]' | tr '-' '_' | head -c 8)
    
    echo "uSCRIPT-$timestamp-$TIMEZONE_CODE-AR$clean_name.sh"
}

# Archive completed script
archive_script() {
    local script_path="$1"
    local script_type="${2:-general}"
    
    if [[ ! -f "$script_path" ]]; then
        log "ERROR" "Script not found: $script_path"
        return 1
    fi
    
    local script_name=$(basename "$script_path")
    local archive_dir="$SCRIPTS_DIR/archive"
    local archive_name=$(generate_archive_name "$script_name" "$script_type")
    local archive_path="$archive_dir/$archive_name"
    
    log "INFO" "Archiving script: $script_name → $archive_name"
    
    # Ensure archive directory exists
    mkdir -p "$archive_dir"
    
    # Create archive with metadata header
    cat > "$archive_path" << EOF
#!/bin/bash
# ARCHIVED SCRIPT - uDEV File Organizer v1.3
#
# Original File: $script_name
# Original Path: $script_path
# Archive Date: $(date '+%Y-%m-%d %H:%M:%S')
# Script Type: $script_type
# Archive Name: $archive_name
# Status: ARCHIVED
#
# This script has been archived after successful execution.
# Original functionality preserved below.
# ═══════════════════════════════════════════════════════════════

EOF
    
    # Append original script content
    cat "$script_path" >> "$archive_path"
    
    # Make archive executable
    chmod +x "$archive_path"
    
    # Create metadata file
    local metadata_file="$archive_dir/$archive_name.meta.json"
    cat > "$metadata_file" << EOF
{
  "archive_info": {
    "original_file": "$script_name",
    "original_path": "$script_path",
    "archive_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "archive_name": "$archive_name",
    "script_type": "$script_type",
    "archived_by": "uDEV File Organizer v1.3"
  },
  "script_metadata": {
    "file_size": $(wc -c < "$script_path"),
    "line_count": $(wc -l < "$script_path"),
    "checksum": "$(shasum -a 256 "$script_path" | cut -d' ' -f1)"
  },
  "execution_history": {
    "last_executed": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "execution_count": 1,
    "success_rate": 1.0
  }
}
EOF
    
    log "SUCCESS" "Script archived successfully: $archive_path"
    echo -e "${GREEN}✅ Archive created: $archive_name${NC}"
    echo -e "${CYAN}📄 Metadata: $metadata_file${NC}"
    
    return 0
}

# Move script to appropriate category directory
organize_script() {
    local script_path="$1"
    local target_category="$2"
    
    if [[ ! -f "$script_path" ]]; then
        log "ERROR" "Script not found: $script_path"
        return 1
    fi
    
    local script_name=$(basename "$script_path")
    local target_dir="$SCRIPTS_DIR/$target_category"
    local target_path="$target_dir/$script_name"
    
    # Validate category
    case "$target_category" in
        cleanup|maintenance|migration|validation)
            ;;
        *)
            log "ERROR" "Invalid category: $target_category"
            return 1
            ;;
    esac
    
    log "INFO" "Organizing script: $script_name → $target_category/"
    
    # Ensure target directory exists
    mkdir -p "$target_dir"
    
    # Move script if not already in target location
    if [[ "$(dirname "$script_path")" != "$target_dir" ]]; then
        mv "$script_path" "$target_path"
        log "SUCCESS" "Script moved to: $target_path"
    else
        log "INFO" "Script already in correct location: $target_path"
    fi
    
    echo -e "${GREEN}✅ Script organized: $target_category/$script_name${NC}"
    return 0
}

# Archive workflow after completion
archive_workflow() {
    local workflow_id="$1"
    local source_dir="${2:-completed}"
    
    local workflow_file="$WORKFLOWS_DIR/$source_dir/$workflow_id.json"
    
    if [[ ! -f "$workflow_file" ]]; then
        log "ERROR" "Workflow not found: $workflow_file"
        return 1
    fi
    
    local timestamp=$(date '+%Y%m%d-%H%M')
    local archive_name="uWORKFLOW-$timestamp-$TIMEZONE_CODE-$(echo "$workflow_id" | tr '[:lower:]' '[:upper:]' | head -c 6).json"
    local archive_dir="$WORKFLOWS_DIR/archive"
    local archive_path="$archive_dir/$archive_name"
    
    log "INFO" "Archiving workflow: $workflow_id → $archive_name"
    
    # Ensure archive directory exists
    mkdir -p "$archive_dir"
    
    # Create archive with metadata
    jq ". + {
        \"archive_info\": {
            \"original_id\": \"$workflow_id\",
            \"archive_date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
            \"archive_name\": \"$archive_name\",
            \"source_status\": \"$source_dir\",
            \"archived_by\": \"uDEV File Organizer v1.3\"
        }
    }" "$workflow_file" > "$archive_path"
    
    log "SUCCESS" "Workflow archived: $archive_path"
    echo -e "${GREEN}✅ Workflow archived: $archive_name${NC}"
    
    return 0
}

# Clean up old log files
cleanup_logs() {
    local retention_days="${1:-30}"
    
    log "INFO" "Cleaning up log files older than $retention_days days"
    
    local files_removed=0
    
    # Clean workflow logs
    if [[ -d "$LOGS_DIR/workflows" ]]; then
        while IFS= read -r -d '' file; do
            rm "$file"
            ((files_removed++))
        done < <(find "$LOGS_DIR/workflows" -name "*.md" -mtime +$retention_days -print0 2>/dev/null)
    fi
    
    # Clean system logs
    if [[ -d "$LOGS_DIR/system" ]]; then
        while IFS= read -r -d '' file; do
            rm "$file"
            ((files_removed++))
        done < <(find "$LOGS_DIR/system" -name "*.md" -mtime +$retention_days -print0 2>/dev/null)
    fi
    
    # Clean daily logs
    if [[ -d "$LOGS_DIR/daily" ]]; then
        while IFS= read -r -d '' file; do
            rm "$file"
            ((files_removed++))
        done < <(find "$LOGS_DIR/daily" -name "*.md" -mtime +$retention_days -print0 2>/dev/null)
    fi
    
    log "SUCCESS" "Cleaned up $files_removed old log files"
    echo -e "${GREEN}✅ Removed $files_removed old log files${NC}"
    
    return 0
}

# Generate organization report
generate_report() {
    local timestamp=$(date '+%Y%m%d-%H%M')
    local report_file="$UDEV_ROOT/reports/summaries/uREPORT-$timestamp-$TIMEZONE_CODE-ORGANIZE.md"
    
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
# uDEV File Organization Report

**Generated**: $(date '+%Y-%m-%d %H:%M:%S')  
**Report Type**: File Organization Summary  
**System**: uDEV File Organizer v1.3  

---

## Directory Status

### Scripts by Category
EOF
    
    for category in cleanup maintenance migration validation archive; do
        local count=0
        if [[ -d "$SCRIPTS_DIR/$category" ]]; then
            count=$(find "$SCRIPTS_DIR/$category" -name "*.sh" | wc -l | tr -d ' ')
        fi
        echo "- **$category**: $count scripts" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

### Workflows by Status
EOF
    
    for status in active pending completed failed; do
        local count=0
        if [[ -d "$WORKFLOWS_DIR/$status" ]]; then
            count=$(find "$WORKFLOWS_DIR/$status" -name "*.json" | wc -l | tr -d ' ')
        fi
        echo "- **$status**: $count workflows" >> "$report_file"
    done
    
    cat >> "$report_file" << EOF

### Storage Usage
- **Scripts Directory**: $(du -sh "$SCRIPTS_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
- **Workflows Directory**: $(du -sh "$WORKFLOWS_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
- **Logs Directory**: $(du -sh "$LOGS_DIR" 2>/dev/null | cut -f1 || echo "Unknown")

---

*Generated by uDEV File Organizer v1.3*
EOF
    
    echo -e "${GREEN}✅ Organization report generated: $report_file${NC}"
    log "SUCCESS" "Report generated: $report_file"
}

# Show help
show_help() {
    cat << 'EOF'
🗂️ uDEV File Organizer v1.3

USAGE:
    file-organizer.sh <command> [options]

COMMANDS:
    archive-script <script_path> [type]     Archive completed script
    organize-script <script_path> <category> Move script to category
    archive-workflow <workflow_id> [status] Archive workflow
    cleanup-logs [retention_days]           Clean old log files (default: 30)
    report                                   Generate organization report
    help                                     Show this help

SCRIPT CATEGORIES:
    cleanup          File and directory cleanup scripts
    maintenance      System maintenance scripts  
    migration        Data migration and conversion scripts
    validation       Testing and validation scripts

EXAMPLES:
    ./file-organizer.sh archive-script cleanup-filenames.sh cleanup
    ./file-organizer.sh organize-script my-script.sh maintenance
    ./file-organizer.sh archive-workflow cleanup-maintenance-v1
    ./file-organizer.sh cleanup-logs 14
    ./file-organizer.sh report

FEATURES:
    - Automatic naming convention application
    - Metadata preservation and generation
    - Comprehensive organization reporting
    - Log file retention management
    - Workflow state management

EOF
}

# Main function
main() {
    case "${1:-help}" in
        "archive-script")
            [[ $# -lt 2 ]] && { echo "Usage: $0 archive-script <script_path> [type]" >&2; exit 1; }
            archive_script "$2" "${3:-general}"
            ;;
        "organize-script")
            [[ $# -lt 3 ]] && { echo "Usage: $0 organize-script <script_path> <category>" >&2; exit 1; }
            organize_script "$2" "$3"
            ;;
        "archive-workflow")
            [[ $# -lt 2 ]] && { echo "Usage: $0 archive-workflow <workflow_id> [status]" >&2; exit 1; }
            archive_workflow "$2" "${3:-completed}"
            ;;
        "cleanup-logs")
            cleanup_logs "${2:-30}"
            ;;
        "report")
            generate_report
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Execute main with all arguments
main "$@"
