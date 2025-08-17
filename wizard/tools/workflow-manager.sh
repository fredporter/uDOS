#!/bin/bash

# uDOS Wizard Workflow Manager v2.0
# Central orchestration system for wizard development workflows

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly WIZARD_DIR="$(dirname "$SCRIPT_DIR")"
readonly UCORE_DIR="$(dirname "$WIZARD_DIR")/uCORE"
readonly WORKFLOWS_DIR="$WIZARD_DIR/workflows"
readonly LOGS_DIR="$WIZARD_DIR/notes"
readonly REPORTS_DIR="$WIZARD_DIR/reports"
readonly TOOLS_DIR="$WIZARD_DIR/tools"

# Function to get 2-letter timezone alpha code
get_timezone_alpha() {
    local tz_mapping_file="$UCORE_DIR/datasets/timezone-alpha-codes.json"
    
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

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >&2
    
    # Also log to file if workflow is active
    if [[ -n "${WORKFLOW_LOG:-}" ]]; then
        echo "[$timestamp] [$level] $message" >> "$WORKFLOW_LOG"
    fi
}

# Error handling
error_exit() {
    log "ERROR" "$1"
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS" "$1"
}

# Warning message
warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
    log "WARNING" "$1"
}

# Info message
info() {
    echo -e "${CYAN}ℹ️ $1${NC}"
    log "INFO" "$1"
}

# Generate timestamp for filenames
generate_timestamp() {
    date '+%Y%m%d-%H%M'
}

# Generate workflow log filename
generate_log_filename() {
    local workflow_id="$1"
    local timestamp=$(generate_timestamp)
    local tz_code=$(get_timezone_alpha)
    echo "$LOGS_DIR/workflows/uLOG-$timestamp$tz_code-WF$(echo "$workflow_id" | tr '[:lower:]' '[:upper:]' | head -c 4).md"
}

# Initialize workflow system
init_workflow_system() {
    info "Initializing uDEV Workflow System..."
    
    # Ensure all directories exist
    local dirs=(
        "$WORKFLOWS_DIR/active"
        "$WORKFLOWS_DIR/pending" 
        "$WORKFLOWS_DIR/completed"
        "$WORKFLOWS_DIR/failed"
        "$WORKFLOWS_DIR/templates"
        "$SCRIPTS_DIR/cleanup"
        "$SCRIPTS_DIR/maintenance"
        "$SCRIPTS_DIR/migration"
        "$SCRIPTS_DIR/validation"
        "$SCRIPTS_DIR/archive"
        "$LOGS_DIR/workflows"
        "$LOGS_DIR/daily"
        "$LOGS_DIR/system"
        "$REPORTS_DIR/summaries"
        "$REPORTS_DIR/metrics"
        "$REPORTS_DIR/analysis"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done
    
    # Create default configuration
    cat > "$WORKFLOWS_DIR/config.json" << 'EOF'
{
  "system": {
    "max_concurrent_workflows": 3,
    "max_script_timeout": 1800,
    "log_retention_days": 30,
    "enable_notifications": true,
    "default_retry_count": 2
  },
  "paths": {
    "workflows_dir": "workflows",
    "scripts_dir": "scripts", 
    "logs_dir": "logs",
    "reports_dir": "reports"
  },
  "execution": {
    "default_shell": "/bin/bash",
    "enable_parallel": true,
    "backup_before_execution": true
  }
}
EOF
    
    success "Workflow system initialized successfully"
}

# Create workflow template
create_workflow_template() {
    local template_name="$1"
    local template_file="$WORKFLOWS_DIR/templates/$template_name.json"
    
    info "Creating workflow template: $template_name"
    
    case "$template_name" in
        "cleanup-maintenance")
            cat > "$template_file" << 'EOF'
{
  "workflow_id": "cleanup-maintenance-v1",
  "name": "Daily Cleanup and Maintenance",
  "description": "Standard cleanup scripts for file organization",
  "version": "1.0",
  "created": "2025-08-17",
  "author": "uDEV System",
  "priority": "normal",
  "schedule": "daily",
  "dependencies": [],
  "scripts": [
    {
      "id": "001",
      "name": "cleanup-filenames.sh",
      "description": "Clean up incorrectly named files",
      "type": "cleanup",
      "timeout": 300,
      "retry_count": 2,
      "critical": true
    },
    {
      "id": "002",
      "name": "reorganize-dev-files.sh", 
      "description": "Reorganize development files",
      "type": "maintenance",
      "timeout": 600,
      "retry_count": 1,
      "critical": false,
      "depends_on": ["001"]
    }
  ],
  "post_actions": [
    "generate_report",
    "archive_logs",
    "update_status"
  ]
}
EOF
            ;;
        "validation-suite")
            cat > "$template_file" << 'EOF'
{
  "workflow_id": "validation-suite-v1",
  "name": "Development Validation Suite",
  "description": "Comprehensive validation and testing scripts",
  "version": "1.0",
  "created": "2025-08-17",
  "author": "uDEV System",
  "priority": "high",
  "schedule": "on-demand",
  "dependencies": [],
  "scripts": [
    {
      "id": "001",
      "name": "validate-naming-conventions.sh",
      "description": "Validate file naming conventions",
      "type": "validation",
      "timeout": 180,
      "retry_count": 1,
      "critical": true
    },
    {
      "id": "002",
      "name": "check-documentation.sh",
      "description": "Verify documentation completeness",
      "type": "validation", 
      "timeout": 240,
      "retry_count": 1,
      "critical": false
    }
  ],
  "post_actions": [
    "generate_report",
    "update_metrics"
  ]
}
EOF
            ;;
        *)
            error_exit "Unknown template: $template_name"
            ;;
    esac
    
    success "Template created: $template_file"
}

# Run workflow
run_workflow() {
    local workflow_id="$1"
    local workflow_file=""
    
    # Find workflow file
    if [[ -f "$WORKFLOWS_DIR/pending/$workflow_id.json" ]]; then
        workflow_file="$WORKFLOWS_DIR/pending/$workflow_id.json"
    elif [[ -f "$WORKFLOWS_DIR/templates/$workflow_id.json" ]]; then
        workflow_file="$WORKFLOWS_DIR/templates/$workflow_id.json"
    else
        error_exit "Workflow not found: $workflow_id"
    fi
    
    # Create log file
    WORKFLOW_LOG=$(generate_log_filename "$workflow_id")
    mkdir -p "$(dirname "$WORKFLOW_LOG")"
    
    info "Starting workflow: $workflow_id"
    info "Log file: $WORKFLOW_LOG"
    
    # Initialize log
    cat > "$WORKFLOW_LOG" << EOF
# Workflow Execution Log

**Workflow**: $workflow_id  
**Start Time**: $(date '+%Y-%m-%d %H:%M:%S')  
**Status**: RUNNING  
**Log File**: $WORKFLOW_LOG  

## Execution Details

EOF
    
    # Move to active
    local active_file="$WORKFLOWS_DIR/active/$workflow_id.json"
    cp "$workflow_file" "$active_file"
    
    # Parse and execute workflow
    local workflow_name=$(jq -r '.name' "$active_file")
    local scripts_count=$(jq -r '.scripts | length' "$active_file")
    
    echo "| Script | Status | Duration | Exit Code | Notes |" >> "$WORKFLOW_LOG"
    echo "|--------|--------|----------|-----------|-------|" >> "$WORKFLOW_LOG"
    
    info "Executing workflow: $workflow_name ($scripts_count scripts)"
    
    local start_time=$(date +%s)
    local failed_scripts=0
    local total_scripts=0
    
    # Execute each script
    for ((i=0; i<scripts_count; i++)); do
        local script_name=$(jq -r ".scripts[$i].name" "$active_file")
        local script_type=$(jq -r ".scripts[$i].type" "$active_file")
        local script_timeout=$(jq -r ".scripts[$i].timeout" "$active_file")
        local script_critical=$(jq -r ".scripts[$i].critical" "$active_file")
        
        total_scripts=$((total_scripts + 1))
        
        info "Executing script: $script_name"
        
        # Find script file
        local script_path=""
        if [[ -f "$SCRIPTS_DIR/$script_type/$script_name" ]]; then
            script_path="$SCRIPTS_DIR/$script_type/$script_name"
        elif [[ -f "$UDEV_ROOT/$script_name" ]]; then
            script_path="$UDEV_ROOT/$script_name"
        else
            error_exit "Script not found: $script_name"
        fi
        
        # Execute script
        local script_start=$(date +%s)
        local exit_code=0
        local script_output=""
        
        if timeout "$script_timeout" bash "$script_path" > /tmp/script_output.log 2>&1; then
            local script_end=$(date +%s)
            local duration=$((script_end - script_start))
            success "Script completed: $script_name (${duration}s)"
            echo "| $script_name | ✅ SUCCESS | ${duration}s | 0 | Completed successfully |" >> "$WORKFLOW_LOG"
        else
            exit_code=$?
            local script_end=$(date +%s)
            local duration=$((script_end - script_start))
            failed_scripts=$((failed_scripts + 1))
            
            if [[ "$script_critical" == "true" ]]; then
                error_exit "Critical script failed: $script_name (exit code: $exit_code)"
            else
                warning "Non-critical script failed: $script_name (exit code: $exit_code)"
                echo "| $script_name | ❌ FAILED | ${duration}s | $exit_code | Non-critical failure |" >> "$WORKFLOW_LOG"
            fi
        fi
    done
    
    local end_time=$(date +%s)
    local total_duration=$((end_time - start_time))
    
    # Update log with final status
    if [[ $failed_scripts -eq 0 ]]; then
        local status="COMPLETED"
        success "Workflow completed successfully: $workflow_id (${total_duration}s)"
        
        # Move to completed
        mv "$active_file" "$WORKFLOWS_DIR/completed/"
    else
        local status="COMPLETED_WITH_ERRORS"
        warning "Workflow completed with errors: $workflow_id ($failed_scripts/$total_scripts failed)"
        
        # Keep in active for review
    fi
    
    # Update log header
    sed -i '' "s/RUNNING/$status/" "$WORKFLOW_LOG"
    sed -i '' "/^\*\*Duration/d" "$WORKFLOW_LOG"
    sed -i '' "s/^\*\*Status\*\*:.*/&\n**Duration**: ${total_duration} seconds/" "$WORKFLOW_LOG"
    
    # Add summary
    cat >> "$WORKFLOW_LOG" << EOF

## Summary
- **Total Scripts**: $total_scripts
- **Successful**: $((total_scripts - failed_scripts))
- **Failed**: $failed_scripts
- **Total Duration**: ${total_duration} seconds
- **Status**: $status

## Post-Execution Actions
✅ Log created: $WORKFLOW_LOG  
$(if [[ $failed_scripts -eq 0 ]]; then echo "✅ Workflow archived to completed/"; else echo "⚠️ Workflow retained in active/ for review"; fi)

*Generated by uDEV Workflow Manager v1.3*
EOF
    
    # Generate report
    "$TOOLS_DIR/report-generator.sh" workflow "$workflow_id" || true
    
    info "Workflow execution complete: $workflow_id"
}

# List workflows
list_workflows() {
    local status_filter="${1:-all}"
    
    info "Listing workflows (filter: $status_filter)"
    
    echo -e "\n${CYAN}📋 Workflow Status${NC}"
    echo "=================================="
    
    # List active workflows
    if [[ "$status_filter" == "active" || "$status_filter" == "all" ]]; then
        if [[ -n "$(ls -A "$WORKFLOWS_DIR/active" 2>/dev/null)" ]]; then
            echo -e "\n${YELLOW}🔄 ACTIVE WORKFLOWS${NC}"
            for file in "$WORKFLOWS_DIR/active"/*.json; do
                if [[ -f "$file" ]]; then
                    local workflow_id=$(basename "$file" .json)
                    local name=$(jq -r '.name' "$file" 2>/dev/null || echo "Unknown")
                    echo "  • $workflow_id - $name"
                fi
            done
        fi
    fi
    
    # List pending workflows
    if [[ "$status_filter" == "pending" || "$status_filter" == "all" ]]; then
        if [[ -n "$(ls -A "$WORKFLOWS_DIR/pending" 2>/dev/null)" ]]; then
            echo -e "\n${BLUE}⏳ PENDING WORKFLOWS${NC}"
            for file in "$WORKFLOWS_DIR/pending"/*.json; do
                if [[ -f "$file" ]]; then
                    local workflow_id=$(basename "$file" .json)
                    local name=$(jq -r '.name' "$file" 2>/dev/null || echo "Unknown")
                    echo "  • $workflow_id - $name"
                fi
            done
        fi
    fi
    
    # List completed workflows
    if [[ "$status_filter" == "completed" || "$status_filter" == "all" ]]; then
        if [[ -n "$(ls -A "$WORKFLOWS_DIR/completed" 2>/dev/null)" ]]; then
            echo -e "\n${GREEN}✅ COMPLETED WORKFLOWS${NC}"
            for file in "$WORKFLOWS_DIR/completed"/*.json; do
                if [[ -f "$file" ]]; then
                    local workflow_id=$(basename "$file" .json)
                    local name=$(jq -r '.name' "$file" 2>/dev/null || echo "Unknown")
                    echo "  • $workflow_id - $name"
                fi
            done
        fi
    fi
    
    # List failed workflows
    if [[ "$status_filter" == "failed" || "$status_filter" == "all" ]]; then
        if [[ -n "$(ls -A "$WORKFLOWS_DIR/failed" 2>/dev/null)" ]]; then
            echo -e "\n${RED}❌ FAILED WORKFLOWS${NC}"
            for file in "$WORKFLOWS_DIR/failed"/*.json; do
                if [[ -f "$file" ]]; then
                    local workflow_id=$(basename "$file" .json)
                    local name=$(jq -r '.name' "$file" 2>/dev/null || echo "Unknown")
                    echo "  • $workflow_id - $name"
                fi
            done
        fi
    fi
    
    echo ""
}

# Show help
show_help() {
    cat << 'EOF'
🔧 uDEV Workflow Manager v1.3

USAGE:
    workflow-manager.sh <command> [options]

COMMANDS:
    init                          Initialize workflow system
    run <workflow_id>            Execute a workflow
    list [status]                List workflows (all|active|pending|completed|failed)
    create-template <name>       Create workflow template
    status <workflow_id>         Show workflow status
    health                       Check system health
    help                         Show this help

EXAMPLES:
    ./workflow-manager.sh init
    ./workflow-manager.sh run cleanup-maintenance-v1
    ./workflow-manager.sh list active
    ./workflow-manager.sh create-template cleanup-maintenance

WORKFLOW TEMPLATES:
    cleanup-maintenance          Daily cleanup and maintenance
    validation-suite            Development validation scripts

EOF
}

# Main command dispatcher
main() {
    case "${1:-help}" in
        "init")
            init_workflow_system
            ;;
        "run")
            [[ $# -lt 2 ]] && error_exit "Usage: $0 run <workflow_id>"
            run_workflow "$2"
            ;;
        "list")
            list_workflows "${2:-all}"
            ;;
        "create-template")
            [[ $# -lt 2 ]] && error_exit "Usage: $0 create-template <template_name>"
            create_workflow_template "$2"
            ;;
        "status")
            [[ $# -lt 2 ]] && error_exit "Usage: $0 status <workflow_id>"
            info "Status check for: $2"
            # TODO: Implement status checking
            ;;
        "health")
            info "System health check"
            # TODO: Implement health check
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
