#!/bin/bash
# uScript - Development Script Manager
# Manages one-off cleanup and development scripts with sandbox execution

set -euo pipefail

UHOME="${UHOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
USCRIPT="$UHOME/uScript"
USANDBOX="$UHOME/sandbox"
TRASH="$UHOME/trash"
UDEV="$UHOME/uDev"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\main() {
    # Load centralized logging
    source "\$UHOME/uCode/log-utils.sh" 2>/dev/null || true
    
    # Log cleanup start
    if declare -f log_script_start >/dev/null 2>&1; then
        log_script_start "cleanup-\$(basename "\${BASH_SOURCE[0]}" .sh)" "cleanup"
    fi
    
    local start_time=\$(date +%s)
    
    cleanup_files
    update_references  
    create_summary
    
    # Log completion
    local end_time=\$(date +%s)
    local duration=\$((end_time - start_time))
    
    if declare -f log_script_end >/dev/null 2>&1; then
        log_script_end "cleanup-\$(basename "\${BASH_SOURCE[0]}" .sh)" "0" "\$duration"
    fi
}

if [[ "\${BASH_SOURCE[0]}" == "\${0}" ]]; then
    if ! main "\$@"; then
        if declare -f log_error >/dev/null 2>&1; then
            log_error "Cleanup script failed: \$(basename "\${BASH_SOURCE[0]}")" "cleanup"
        fi
        exit 1
    fi
fi'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Version and info
VERSION="2.0.0"
SCRIPT_NAME="uScript Development Manager"

show_header() {
    echo -e "${CYAN}🔧 $SCRIPT_NAME v$VERSION${NC}"
    echo "════════════════════════════════════════════"
}

show_help() {
    show_header
    echo "Development script management system for uDOS"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  create <name>         Create new development script"
    echo "  list                  List available scripts"  
    echo "  run <name>            Execute script in sandbox"
    echo "  edit <name>           Edit script in VS Code"
    echo "  delete <name>         Delete script permanently"
    echo "  clean                 Clean up executed scripts"
    echo "  status               Show system status"
    echo ""
    echo "Development Mode Commands:"
    echo "  install <script>      Install script from uCode/ to uScript/"
    echo "  template <type>       Create script from template"
    echo ""
    echo "Logging Commands:"
    echo "  logs [type]          Show recent logs (system, errors, scripts, performance)"
    echo "  logs-clean [days]    Clean old logs (default: 30 days)"
    echo ""
    echo "Examples:"
    echo "  $0 create cleanup-logs"
    echo "  $0 run cleanup-uknowledge" 
    echo "  $0 install cleanup-uknowledge.sh"
    echo "  $0 template cleanup"
    echo "  $0 logs errors"
}

create_directories() {
    mkdir -p "$USCRIPT"/{active,templates,executed,logs}
    mkdir -p "$USANDBOX/scripts"
    mkdir -p "$UDEV/logs/scripts"
}

create_script() {
    local script_name="$1"
    local script_file="$USCRIPT/active/${script_name}.sh"
    
    if [[ -f "$script_file" ]]; then
        echo -e "${YELLOW}⚠️ Script '$script_name' already exists${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📝 Creating new script: $script_name${NC}"
    
    cat > "$script_file" << EOF
#!/bin/bash
# Development Script: $script_name
# Created: $(date)
# Purpose: [Describe what this script does]

set -euo pipefail

UHOME="\${UHOME:-\$(cd "\$(dirname "\${BASH_SOURCE[0]}")/../.." && pwd)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔧 Running: $script_name"
echo "═══════════════════════════════════"

# Load centralized logging
source "\$UHOME/uCode/log-utils.sh" 2>/dev/null || true

main() {
    echo -e "\${BLUE}📋 Starting $script_name...\${NC}"
    
    # Log script start
    if declare -f log_script_start >/dev/null 2>&1; then
        log_script_start "$script_name" "custom"
    fi
    
    local start_time=\$(date +%s)
    
    # TODO: Add your script logic here
    echo "  • Step 1: [Describe step]"
    echo "  • Step 2: [Describe step]"
    
    # Log completion
    local end_time=\$(date +%s)
    local duration=\$((end_time - start_time))
    
    if declare -f log_script_end >/dev/null 2>&1; then
        log_script_end "$script_name" "0" "\$duration"
    fi
    
    echo -e "\${GREEN}✅ $script_name completed successfully!\${NC}"
}

# Error handling wrapper
run_with_error_handling() {
    if ! main "\$@"; then
        if declare -f log_error >/dev/null 2>&1; then
            log_error "$script_name execution failed" "custom-script"
        fi
        exit 1
    fi
}

# Run if executed directly
if [[ "\${BASH_SOURCE[0]}" == "\${0}" ]]; then
    run_with_error_handling "\$@"
fi
EOF

    chmod +x "$script_file"
    echo -e "${GREEN}✅ Created: $script_file${NC}"
    
    # Open in VS Code if available
    if command -v code >/dev/null 2>&1; then
        echo -e "${BLUE}🔧 Opening in VS Code...${NC}"
        code "$script_file"
    fi
}

list_scripts() {
    show_header
    echo -e "${BLUE}📋 Available Development Scripts${NC}"
    echo ""
    
    if [[ -d "$USCRIPT/active" ]] && [[ "$(ls -A "$USCRIPT/active" 2>/dev/null)" ]]; then
        echo "Active Scripts:"
        for script in "$USCRIPT/active"/*.sh; do
            if [[ -f "$script" ]]; then
                local name=$(basename "$script" .sh)
                local size=$(stat -f%z "$script" 2>/dev/null || stat -c%s "$script" 2>/dev/null || echo "0")
                local modified=$(stat -f%m "$script" 2>/dev/null || stat -c%Y "$script" 2>/dev/null || echo "0")
                local date=$(date -r "$modified" '+%Y-%m-%d %H:%M' 2>/dev/null || echo "Unknown")
                printf "  • %-20s %6s bytes  %s\n" "$name" "$size" "$date"
            fi
        done
        echo ""
    else
        echo "No active scripts found."
        echo ""
    fi
    
    if [[ -d "$USCRIPT/executed" ]] && [[ "$(ls -A "$USCRIPT/executed" 2>/dev/null)" ]]; then
        echo "Recently Executed (in trash):"
        ls -la "$USCRIPT/executed" | tail -n +2 | while read -r line; do
            echo "  📁 $line"
        done
        echo ""
    fi
}

run_script() {
    local script_name="$1"
    local script_file="$USCRIPT/active/${script_name}.sh"
    local sandbox_file="$USANDBOX/scripts/${script_name}-$(date +%Y%m%d-%H%M%S).sh"
    
    if [[ ! -f "$script_file" ]]; then
        echo -e "${RED}❌ Script '$script_name' not found${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🚀 Executing script: $script_name${NC}"
    echo "  • Copying to sandbox: $(basename "$sandbox_file")"
    
    # Copy to sandbox for execution
    cp "$script_file" "$sandbox_file"
    chmod +x "$sandbox_file"
    
    echo "  • Running in sandbox..."
    echo ""
    
    # Load logging utilities
    source "$UHOME/uCode/log-utils.sh" 2>/dev/null || true
    
    # Log script start and time execution
    local start_time=$(date +%s)
    if declare -f log_script_start >/dev/null 2>&1; then
        log_script_start "$script_name" "uScript"
    fi
    
    # Execute in sandbox
    local exit_code=0
    if (cd "$USANDBOX" && "$sandbox_file"); then
        exit_code=$?
        echo ""
        echo -e "${GREEN}✅ Script executed successfully${NC}"
        
        # Move executed script to executed folder (soft archive)
        mkdir -p "$USCRIPT/executed"
        mv "$script_file" "$USCRIPT/executed/${script_name}-$(date +%Y%m%d-%H%M%S).sh"
        
        # Calculate duration and log completion
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        if declare -f log_script_end >/dev/null 2>&1; then
            log_script_end "$script_name" "$exit_code" "$duration"
        fi
        
        if declare -f log_performance >/dev/null 2>&1; then
            log_performance "uScript execution: $script_name" "$duration"
        fi
        
        echo "  • Script moved to executed archive"
        echo "  • Sandbox copy will be cleaned up"
        
        # Clean up sandbox after 1 minute (background)
        (sleep 60 && rm -f "$sandbox_file" 2>/dev/null) &
        
    else
        exit_code=$?
        echo ""
        echo -e "${RED}❌ Script execution failed${NC}"
        
        # Log failure
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        if declare -f log_script_end >/dev/null 2>&1; then
            log_script_end "$script_name" "$exit_code" "$duration"
        fi
        
        if declare -f log_error >/dev/null 2>&1; then
            log_error "uScript execution failed: $script_name (exit code: $exit_code)" "uScript"
        fi
        echo "  • Check sandbox file: $sandbox_file"
        return 1
    fi
}

install_from_ucode() {
    local script_name="$1"
    local source_file="$UHOME/uCode/$script_name"
    local dest_file="$USCRIPT/active/$(basename "$script_name" .sh).sh"
    
    if [[ ! -f "$source_file" ]]; then
        echo -e "${RED}❌ Script not found: $source_file${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📦 Installing script from uCode: $script_name${NC}"
    
    # Copy and ensure it's executable
    cp "$source_file" "$dest_file"
    chmod +x "$dest_file"
    
    echo -e "${GREEN}✅ Installed: $(basename "$dest_file")${NC}"
    echo "  • Source: $source_file"
    echo "  • Destination: $dest_file"
    echo "  • Run with: $0 run $(basename "$dest_file" .sh)"
}

create_from_template() {
    local template_type="$1"
    local script_name="${2:-${template_type}-$(date +%Y%m%d-%H%M%S)}"
    
    case "$template_type" in
        cleanup)
            create_cleanup_template "$script_name"
            ;;
        migration)  
            create_migration_template "$script_name"
            ;;
        validation)
            create_validation_template "$script_name"
            ;;
        *)
            echo -e "${RED}❌ Unknown template type: $template_type${NC}"
            echo "Available templates: cleanup, migration, validation"
            return 1
            ;;
    esac
}

create_cleanup_template() {
    local script_name="$1"
    local script_file="$USCRIPT/active/${script_name}.sh"
    
    cat > "$script_file" << 'EOF'
#!/bin/bash
# Cleanup Script Template
# Purpose: Clean up and reorganize files/directories

set -euo pipefail

UHOME="${UHOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m' 
BLUE='\033[0;34m'
NC='\033[0m'

echo "🧹 Cleanup Script"
echo "════════════════════"

cleanup_files() {
    echo "📋 Analyzing files to cleanup..."
    
    # TODO: Add cleanup logic here
    # Example:
    # if [[ -f "$UHOME/path/to/file" ]]; then
    #     echo "  • Moving file to appropriate location..."
    #     mv "$UHOME/path/to/file" "$UHOME/new/location/"
    # fi
    
    echo "  • Cleanup logic goes here"
}

update_references() {
    echo "🔧 Updating references..."
    
    # TODO: Update any file references
    # Example:
    # find "$UHOME" -name "*.sh" -exec sed -i '' 's|old/path|new/path|g' {} \;
    
    echo "  • Reference updates go here"
}

create_summary() {
    echo ""
    echo "📊 Cleanup Summary"
    echo "════════════════════"
    echo "  ✅ Files cleaned up"
    echo "  ✅ References updated" 
    echo "  ✅ System validated"
    echo ""
    echo "🎯 Cleanup completed successfully!"
}

main() {
    cleanup_files
    update_references  
    create_summary
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
EOF

    chmod +x "$script_file"
    echo -e "${GREEN}✅ Created cleanup template: $script_name${NC}"
}

clean_executed() {
    echo -e "${BLUE}🧹 Cleaning up executed scripts...${NC}"
    
    # Load logging utilities
    source "$UHOME/uCode/log-utils.sh" 2>/dev/null || true
    
    local count=0
    if [[ -d "$USCRIPT/executed" ]]; then
        count=$(ls -1 "$USCRIPT/executed" 2>/dev/null | wc -l | tr -d ' ')
        if [[ $count -gt 0 ]]; then
            mkdir -p "$TRASH"
            mv "$USCRIPT/executed"/* "$TRASH/" 2>/dev/null || {
                if declare -f log_error >/dev/null 2>&1; then
                    log_error "Failed to move executed scripts to trash" "uScript"
                fi
                echo -e "${RED}❌ Failed to clean executed scripts${NC}"
                return 1
            }
            echo -e "${GREEN}✅ Moved $count executed scripts to trash${NC}"
            
            if declare -f log_system >/dev/null 2>&1; then
                log_system "INFO" "Cleaned $count executed scripts"
            fi
        else
            echo "No executed scripts to clean"
        fi
    fi
    
    # Clean up old sandbox scripts
    if [[ -d "$USANDBOX/scripts" ]]; then
        local cleaned_count=$(find "$USANDBOX/scripts" -name "*.sh" -mtime +1 2>/dev/null | wc -l | tr -d ' ')
        find "$USANDBOX/scripts" -name "*.sh" -mtime +1 -delete 2>/dev/null || true
        if [[ $cleaned_count -gt 0 ]]; then
            echo "  • Cleaned up $cleaned_count old sandbox scripts"
            if declare -f log_system >/dev/null 2>&1; then
                log_system "INFO" "Cleaned $cleaned_count old sandbox scripts"
            fi
        else
            echo "  • No old sandbox scripts to clean"
        fi
    fi
}

show_status() {
    show_header
    echo -e "${BLUE}📊 System Status${NC}"
    echo ""
    
    # Active scripts
    local active_count=0
    if [[ -d "$USCRIPT/active" ]]; then
        active_count=$(ls -1 "$USCRIPT/active"/*.sh 2>/dev/null | wc -l | tr -d ' ')
    fi
    echo "Active Scripts: $active_count"
    
    # Executed scripts
    local executed_count=0
    if [[ -d "$USCRIPT/executed" ]]; then
        executed_count=$(ls -1 "$USCRIPT/executed" 2>/dev/null | wc -l | tr -d ' ')
    fi
    echo "Executed Scripts: $executed_count"
    
    # Sandbox scripts
    local sandbox_count=0
    if [[ -d "$USANDBOX/scripts" ]]; then
        sandbox_count=$(find "$USANDBOX/scripts" -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')
    fi
    echo "Sandbox Scripts: $sandbox_count"
    
    echo ""
    echo "Directories:"
    echo "  • Active: $USCRIPT/active/"
    echo "  • Executed: $USCRIPT/executed/"
    echo "  • Sandbox: $USANDBOX/scripts/"
    echo "  • Logs: $UDEV/logs/scripts/"
}

show_logs() {
    local log_type="${1:-all}"
    local lines="${2:-20}"
    
    show_header
    echo -e "${BLUE}📋 Recent Logs${NC}"
    
    case "$log_type" in
        system)
            echo ""
            echo "System Logs (last $lines lines):"
            if [[ -f "$UDEV/logs/system/$(date +%Y%m%d).log" ]]; then
                tail -n "$lines" "$UDEV/logs/system/$(date +%Y%m%d).log" 2>/dev/null || echo "No system logs today"
            else
                echo "No system logs found for today"
            fi
            ;;
        errors)
            echo ""
            echo "Error Logs (last $lines lines):"
            if [[ -f "$UDEV/logs/errors/$(date +%Y%m%d).log" ]]; then
                tail -n "$lines" "$UDEV/logs/errors/$(date +%Y%m%d).log" 2>/dev/null || echo "No error logs today"
            else
                echo "No error logs found for today"
            fi
            ;;
        scripts)
            echo ""
            echo "Script Logs (last $lines lines):"
            if [[ -f "$UDEV/logs/scripts/$(date +%Y%m%d).log" ]]; then
                tail -n "$lines" "$UDEV/logs/scripts/$(date +%Y%m%d).log" 2>/dev/null || echo "No script logs today"
            else
                echo "No script logs found for today"
            fi
            ;;
        performance)
            echo ""
            echo "Performance Logs (last $lines lines):"
            if [[ -f "$UDEV/logs/performance/$(date +%Y%m%d).log" ]]; then
                tail -n "$lines" "$UDEV/logs/performance/$(date +%Y%m%d).log" 2>/dev/null || echo "No performance logs today"
            else
                echo "No performance logs found for today"
            fi
            ;;
        all|*)
            echo ""
            echo "All Log Types (last 10 lines each):"
            echo ""
            echo "=== System ==="
            tail -n 10 "$UDEV/logs/system/$(date +%Y%m%d).log" 2>/dev/null || echo "No system logs"
            echo ""
            echo "=== Scripts ==="  
            tail -n 10 "$UDEV/logs/scripts/$(date +%Y%m%d).log" 2>/dev/null || echo "No script logs"
            echo ""
            echo "=== Errors ==="
            tail -n 10 "$UDEV/logs/errors/$(date +%Y%m%d).log" 2>/dev/null || echo "No error logs"
            ;;
    esac
    echo ""
}

clean_logs() {
    local days="${1:-30}"
    
    echo -e "${BLUE}🧹 Cleaning logs older than $days days...${NC}"
    
    # Load logging utilities
    source "$UHOME/uCode/log-utils.sh" 2>/dev/null || true
    
    if declare -f cleanup_logs >/dev/null 2>&1; then
        cleanup_logs "$days"
        echo -e "${GREEN}✅ Log cleanup completed${NC}"
    else
        echo -e "${YELLOW}⚠️ Log utilities not available${NC}"
        return 1
    fi
}

# Main command handling
main() {
    create_directories
    
    case "${1:-help}" in
        create)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ Script name required${NC}"
                echo "Usage: $0 create <script-name>"
                exit 1
            fi
            create_script "$2"
            ;;
        list)
            list_scripts
            ;;
        run)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ Script name required${NC}"
                echo "Usage: $0 run <script-name>"
                exit 1
            fi
            run_script "$2"
            ;;
        install)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ Script name required${NC}"
                echo "Usage: $0 install <script-name>"
                exit 1
            fi
            install_from_ucode "$2"
            ;;
        template)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}❌ Template type required${NC}"
                echo "Usage: $0 template <type> [name]"
                exit 1
            fi
            create_from_template "$2" "${3:-}"
            ;;
        clean)
            clean_executed
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "${2:-all}" "${3:-20}"
            ;;
        logs-clean)
            clean_logs "${2:-30}"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
