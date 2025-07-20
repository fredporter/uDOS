#!/bin/bash
# processor.sh - uDOS Unified Processing System v2.0  
# Consolidated: shortcode-processor-simple.sh + json-processor.sh + data processing
# Handles all shortcode processing, JSON operations, and data manipulation

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
DATASET_DIR="${UHOME}/uTemplate/datasets"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Logging
log() { echo -e "${CYAN}[$(date '+%H:%M:%S')] [PROCESSOR]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1" >&2; }
warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
info() { echo -e "${BLUE}ℹ️${NC} $1"; }

# ═══════════════════════════════════════════════════════════════════════
# 🔧 SHORTCODE PROCESSING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Available shortcodes
SHORTCODES=(
    "DASH:Dashboard operations"
    "CHECK:System health checks"
    "PACKAGE:Package management"
    "MISSION:Mission operations"
    "DATA:Data processing"
    "LOG:Logging operations"
    "ERROR:Error handling"
    "BASH:Shell execution"
    "SCRIPT:uScript execution"
    "JSON:JSON processing"
    "SEARCH:File searching"
    "TEMPLATE:Template operations"
)

# Process shortcode string
process_shortcode() {
    local input="$1"
    local context="${2:-command}"
    
    log "Processing shortcode: $input"
    
    # Extract shortcode pattern [COMMAND:args]
    if [[ "$input" =~ \[([A-Z]+):([^]]+)\] ]]; then
        local command="${BASH_REMATCH[1]}"
        local args="${BASH_REMATCH[2]}"
        
        case "$command" in
            "DASH")
                execute_dash_shortcode "$args"
                ;;
            "CHECK")
                execute_check_shortcode "$args"
                ;;
            "PACKAGE"|"PKG")
                execute_package_shortcode "$args"
                ;;
            "MISSION")
                execute_mission_shortcode "$args"
                ;;
            "DATA")
                execute_data_shortcode "$args"
                ;;
            "LOG")
                execute_log_shortcode "$args"
                ;;
            "ERROR")
                execute_error_shortcode "$args"
                ;;
            "BASH")
                execute_bash_shortcode "$args"
                ;;
            "SCRIPT")
                execute_script_shortcode "$args"
                ;;
            "JSON")
                execute_json_shortcode "$args"
                ;;
            "SEARCH")
                execute_search_shortcode "$args"
                ;;
            "TEMPLATE")
                execute_template_shortcode "$args"
                ;;
            *)
                warn "Unknown shortcode: $command"
                return 1
                ;;
        esac
    else
        error "Invalid shortcode format: $input"
        info "Expected format: [COMMAND:args]"
        return 1
    fi
}

# Execute dashboard shortcode
execute_dash_shortcode() {
    local args="$1"
    info "🔧 Executing dashboard command: $args"
    
    if [[ -f "$UHOME/uCode/dash.sh" ]]; then
        bash "$UHOME/uCode/dash.sh" $args
    else
        error "Dashboard script not found"
    fi
}

# Execute check shortcode  
execute_check_shortcode() {
    local args="$1"
    info "🔍 Executing system check: $args"
    
    if [[ -f "$UHOME/uCode/core.sh" ]]; then
        bash "$UHOME/uCode/core.sh" $args
    elif [[ -f "$UHOME/uCode/check.sh" ]]; then
        bash "$UHOME/uCode/check.sh" $args
    else
        error "Check system not found"
    fi
}

# Execute package shortcode
execute_package_shortcode() {
    local args="$1"
    info "📦 Executing package command: $args"
    
    if [[ -f "$UHOME/uCode/package.sh" ]]; then
        bash "$UHOME/uCode/package.sh" $args
    elif [[ -f "$UHOME/uCode/package-manager.sh" ]]; then
        bash "$UHOME/uCode/package-manager.sh" $args
    else
        error "Package manager not found"
    fi
}

# Execute bash shortcode (containerized execution)
execute_bash_shortcode() {
    local args="$1"
    warn "🐚 Executing bash command: $args"
    
    # Basic safety check
    if [[ "$args" =~ (rm\s+-rf|mkfs|dd\s+if=|>\s*/dev/) ]]; then
        error "Potentially dangerous command blocked: $args"
        return 1
    fi
    
    # Execute with timeout
    timeout 30s bash -c "$args" 2>&1 || {
        error "Command failed or timed out"
        return 1
    }
}

# Execute script shortcode
execute_script_shortcode() {
    local args="$1"
    info "📜 Executing uScript: $args"
    
    # Look for script
    local script_path=""
    if [[ -f "$UHOME/uScript/system/$args.sh" ]]; then
        script_path="$UHOME/uScript/system/$args.sh"
    elif [[ -f "$UHOME/uScript/utilities/$args.sh" ]]; then
        script_path="$UHOME/uScript/utilities/$args.sh"
    elif [[ -f "$args" ]]; then
        script_path="$args"
    else
        error "Script not found: $args"
        return 1
    fi
    
    bash "$script_path"
}

# ═══════════════════════════════════════════════════════════════════════
# 📊 JSON PROCESSING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Process JSON data
process_json() {
    local operation="$1"
    local json_input="$2"
    local query="${3:-}"
    
    case "$operation" in
        "query"|"search")
            query_json "$json_input" "$query"
            ;;
        "validate")
            validate_json "$json_input"
            ;;
        "format"|"pretty")
            format_json "$json_input"
            ;;
        "merge")
            merge_json "$json_input" "$query"
            ;;
        "extract")
            extract_json "$json_input" "$query"
            ;;
        *)
            error "Unknown JSON operation: $operation"
            show_json_help
            return 1
            ;;
    esac
}

# Query JSON data
query_json() {
    local json_input="$1"
    local query="$2"
    
    if command -v jq >/dev/null 2>&1; then
        if [[ -f "$json_input" ]]; then
            jq "$query" "$json_input"
        else
            echo "$json_input" | jq "$query"
        fi
    else
        error "jq not installed. Install with: ucode package install jq"
        return 1
    fi
}

# Validate JSON
validate_json() {
    local json_input="$1"
    
    if command -v jq >/dev/null 2>&1; then
        if [[ -f "$json_input" ]]; then
            if jq empty "$json_input" 2>/dev/null; then
                success "Valid JSON: $json_input"
            else
                error "Invalid JSON: $json_input"
                return 1
            fi
        else
            if echo "$json_input" | jq empty 2>/dev/null; then
                success "Valid JSON input"
            else
                error "Invalid JSON input"
                return 1
            fi
        fi
    else
        warn "jq not available for validation"
    fi
}

# Format JSON  
format_json() {
    local json_input="$1"
    
    if command -v jq >/dev/null 2>&1; then
        if [[ -f "$json_input" ]]; then
            jq '.' "$json_input"
        else
            echo "$json_input" | jq '.'
        fi
    else
        echo "$json_input"
    fi
}

# Execute JSON shortcode
execute_json_shortcode() {
    local args="$1"
    
    # Parse arguments: operation file [query]
    local operation=$(echo "$args" | cut -d' ' -f1)
    local file=$(echo "$args" | cut -d' ' -f2)
    local query=$(echo "$args" | cut -d' ' -f3-)
    
    [[ "$query" == "$file" ]] && query=""
    
    process_json "$operation" "$file" "$query"
}

# ═══════════════════════════════════════════════════════════════════════
# 📊 DATASET PROCESSING
# ═══════════════════════════════════════════════════════════════════════

# Query dataset
query_dataset() {
    local dataset="$1"
    local search_term="$2"
    local dataset_file="$DATASET_DIR/$dataset"
    
    if [[ ! -f "$dataset_file" ]]; then
        error "Dataset not found: $dataset"
        return 1
    fi
    
    log "Searching dataset: $dataset for '$search_term'"
    
    if [[ "$dataset_file" =~ \.json$ ]]; then
        if command -v jq >/dev/null 2>&1; then
            jq -r ".[] | select(. | tostring | test(\"$search_term\"; \"i\"))" "$dataset_file" 2>/dev/null || {
                warn "No matches found in $dataset"
            }
        else
            grep -i "$search_term" "$dataset_file" || warn "No matches found"
        fi
    else
        grep -i "$search_term" "$dataset_file" || warn "No matches found"
    fi
}

# Show dataset statistics
show_dataset_stats() {
    log "Dataset statistics:"
    
    if [[ -d "$DATASET_DIR" ]]; then
        local total_files=$(find "$DATASET_DIR" -type f | wc -l | tr -d ' ')
        local json_files=$(find "$DATASET_DIR" -name "*.json" | wc -l | tr -d ' ')
        local csv_files=$(find "$DATASET_DIR" -name "*.csv" | wc -l | tr -d ' ')
        
        echo "  📊 Total datasets: $total_files"
        echo "  🔧 JSON datasets: $json_files"  
        echo "  📊 CSV datasets: $csv_files"
        
        # Show individual dataset info
        find "$DATASET_DIR" -type f | while read -r dataset; do
            local name=$(basename "$dataset")
            local size=$(du -h "$dataset" | cut -f1)
            echo "    📄 $name ($size)"
        done
    else
        warn "Dataset directory not found: $DATASET_DIR"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# 🔍 FILE PROCESSING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Process file-based shortcodes
process_file_shortcode() {
    local command="$1"
    local file_path="$2"
    local args="${3:-}"
    
    case "$command" in
        "read"|"cat")
            if [[ -f "$file_path" ]]; then
                if command -v bat >/dev/null 2>&1; then
                    bat "$file_path"
                else
                    cat "$file_path"
                fi
            else
                error "File not found: $file_path"
            fi
            ;;
        "edit")
            if command -v micro >/dev/null 2>&1; then
                micro "$file_path"
            elif command -v nano >/dev/null 2>&1; then
                nano "$file_path"
            else
                error "No editor available"
            fi
            ;;
        "search")
            if command -v rg >/dev/null 2>&1; then
                rg "$args" "$file_path"
            else
                grep -n "$args" "$file_path" 2>/dev/null || warn "No matches found"
            fi
            ;;
        *)
            error "Unknown file command: $command"
            ;;
    esac
}

# Execute search shortcode
execute_search_shortcode() {
    local args="$1"
    info "🔍 Executing search: $args"
    
    if command -v rg >/dev/null 2>&1; then
        rg $args "$UHOME"
    elif command -v grep >/dev/null 2>&1; then
        grep -r $args "$UHOME"
    else
        error "No search tool available"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# 🎯 MAIN COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

# Show shortcode help
show_shortcode_help() {
    echo -e "${CYAN}Available Shortcodes:${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo
    
    for shortcode in "${SHORTCODES[@]}"; do
        local cmd="${shortcode%%:*}"
        local desc="${shortcode#*:}"
        echo -e "${WHITE}  [${cmd}:args]${NC} - $desc"
    done
    
    echo
    echo -e "${CYAN}Examples:${NC}"
    echo -e "${WHITE}  [DASH:refresh]${NC}           - Refresh dashboard"
    echo -e "${WHITE}  [CHECK:health]${NC}           - System health check"
    echo -e "${WHITE}  [JSON:query data.json '.name']${NC} - Query JSON file"
    echo -e "${WHITE}  [BASH:ls -la]${NC}            - Execute bash command"
    echo
}

# Show JSON help
show_json_help() {
    echo -e "${CYAN}JSON Operations:${NC}"
    echo "  query    - Query JSON with jq syntax"
    echo "  validate - Validate JSON syntax"
    echo "  format   - Pretty print JSON"
    echo "  merge    - Merge two JSON files"
    echo "  extract  - Extract specific fields"
}

# Show help
show_help() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                🔧 uDOS PROCESSING SYSTEM                    ║${NC}"
    echo -e "${PURPLE}║           Shortcodes · JSON · Data Processing v2.0          ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${WHITE}Processing System Commands:${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${CYAN}🔧 Shortcode Processing:${NC}"
    echo -e "${WHITE}  processor shortcode '[CMD:args]'        Process shortcode${NC}"
    echo -e "${WHITE}  processor process <input>               Process shortcode in text${NC}"
    echo -e "${WHITE}  processor list                          List available shortcodes${NC}"
    echo
    echo -e "${CYAN}📊 JSON Operations:${NC}"
    echo -e "${WHITE}  processor json query <file> <query>     Query JSON file${NC}"
    echo -e "${WHITE}  processor json validate <file>          Validate JSON syntax${NC}"
    echo -e "${WHITE}  processor json format <file>            Format JSON file${NC}"
    echo
    echo -e "${CYAN}📈 Data Processing:${NC}"
    echo -e "${WHITE}  processor dataset query <name> <term>   Search dataset${NC}"
    echo -e "${WHITE}  processor dataset stats                 Show dataset statistics${NC}"
    echo
    echo -e "${CYAN}ℹ️  Information:${NC}"
    echo -e "${WHITE}  processor help                          Show this help${NC}"
    echo
}

# Main command router
main() {
    local command="${1:-help}"
    
    case "$command" in
        "shortcode"|"sc")
            local shortcode_input="${2:-}"
            if [[ -z "$shortcode_input" ]]; then
                error "Shortcode input required"
                show_shortcode_help
                return 1
            fi
            process_shortcode "$shortcode_input"
            ;;
        "process")
            local input_text="${2:-}"
            if [[ -z "$input_text" ]]; then
                error "Input text required"
                return 1
            fi
            # Find and process all shortcodes in text
            while [[ "$input_text" =~ \[([A-Z]+:[^]]+)\] ]]; do
                local shortcode="${BASH_REMATCH[1]}"
                process_shortcode "[$shortcode]"
                input_text="${input_text/\[$shortcode\]/}"
            done
            ;;
        "list"|"ls")
            show_shortcode_help
            ;;
        "json")
            local operation="${2:-}"
            local json_input="${3:-}"
            local query="${4:-}"
            
            if [[ -z "$operation" ]]; then
                show_json_help
                return 1
            fi
            
            process_json "$operation" "$json_input" "$query"
            ;;
        "dataset"|"data")
            local subcommand="${2:-stats}"
            case "$subcommand" in
                "query"|"search")
                    local dataset_name="${3:-}"
                    local search_term="${4:-}"
                    if [[ -z "$dataset_name" || -z "$search_term" ]]; then
                        error "Usage: processor dataset query <dataset_name> <search_term>"
                        return 1
                    fi
                    query_dataset "$dataset_name" "$search_term"
                    ;;
                "stats"|"info")
                    show_dataset_stats
                    ;;
                *)
                    error "Unknown dataset command: $subcommand"
                    echo "Available: query, stats"
                    ;;
            esac
            ;;
        "help"|"-h"|"--help"|*)
            show_help
            ;;
    esac
}

# Execute main function if script is called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
