#!/bin/bash
# enhanced-script-runner.sh - Enhanced uScript Execution Engine
# Version: 1.7.1
# Description: Advanced uScript runner with error handling, logging, and containerization

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
USCRIPT_DIR="$UHOME/uScript"
ERROR_HANDLER="$UHOME/uCode/error-handler.sh"
SHORTCODE_PROCESSOR="$UHOME/uCode/shortcode-processor.sh"
BASH_CONTAINER="$SCRIPT_DIR/bash-container.sh"

# Source error handler
source "$ERROR_HANDLER" 2>/dev/null || {
    echo "⚠️ Error handler not available - using basic error handling"
    error_warning() { echo "WARN: $1" >&2; }
    error_critical() { echo "ERROR: $1" >&2; }
    error_fatal() { echo "FATAL: $1" >&2; exit 1; }
    set_error_context() { true; }
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script execution context
EXECUTION_ID=""
SCRIPT_PATH=""
SCRIPT_TYPE=""
EXECUTION_MODE="native"  # native, container, hybrid
MISSION_CONTEXT=""
RETRY_ENABLED=true
MAX_RETRIES=3
CURRENT_RETRY=0

# Performance tracking
START_TIME=""
END_TIME=""
EXECUTION_DURATION=""

# Initialize execution environment
init_execution() {
    local script_path="$1"
    local mode="${2:-native}"
    
    EXECUTION_ID="exec_$(date +%Y%m%d_%H%M%S)_$$"
    SCRIPT_PATH="$script_path"
    EXECUTION_MODE="$mode"
    START_TIME=$(date +%s)
    
    set_error_context "script_execution" "$script_path" "$MISSION_CONTEXT"
    
    echo -e "${BLUE}🚀 Initializing script execution${NC}"
    echo -e "${CYAN}   ID: $EXECUTION_ID${NC}"
    echo -e "${CYAN}   Script: $script_path${NC}"
    echo -e "${CYAN}   Mode: $EXECUTION_MODE${NC}"
    
    # Create execution log directory
    local log_dir="$UHOME/uMemory/logs/executions"
    mkdir -p "$log_dir"
    
    # Start execution log
    cat > "$log_dir/${EXECUTION_ID}.md" << EOF
# Script Execution Log: $EXECUTION_ID

## Execution Details
- **Script**: $script_path
- **Mode**: $EXECUTION_MODE
- **Started**: $(date -Iseconds)
- **Mission Context**: ${MISSION_CONTEXT:-"None"}

## Progress Log
EOF
    
    echo -e "${GREEN}✅ Execution environment initialized${NC}"
}

# Detect script type and language
detect_script_type() {
    local script_path="$1"
    
    if [[ ! -f "$script_path" ]]; then
        error_critical "Script file not found: $script_path"
        return 1
    fi
    
    # Check file extension
    case "${script_path##*.}" in
        "md")
            SCRIPT_TYPE="markdown"
            ;;
        "sh")
            SCRIPT_TYPE="bash"
            ;;
        "py")
            SCRIPT_TYPE="python"
            ;;
        "js")
            SCRIPT_TYPE="javascript"
            ;;
        "usc"|"uscript")
            SCRIPT_TYPE="uscript"
            ;;
        *)
            # Check shebang or content
            local first_line=$(head -1 "$script_path")
            if [[ "$first_line" =~ ^#!/bin/bash ]]; then
                SCRIPT_TYPE="bash"
            elif [[ "$first_line" =~ ^#!/usr/bin/env\ python ]]; then
                SCRIPT_TYPE="python"
            elif [[ "$first_line" =~ ^#!/usr/bin/env\ node ]]; then
                SCRIPT_TYPE="javascript"
            elif grep -q "^LANGUAGE:" "$script_path"; then
                local lang=$(grep "^LANGUAGE:" "$script_path" | cut -d':' -f2 | xargs)
                SCRIPT_TYPE="${lang,,}"  # lowercase
            else
                SCRIPT_TYPE="unknown"
            fi
            ;;
    esac
    
    echo -e "${BLUE}🔍 Detected script type: $SCRIPT_TYPE${NC}"
    return 0
}

# Pre-execution validation
validate_script() {
    local script_path="$1"
    
    echo -e "${BLUE}🔍 Validating script: $script_path${NC}"
    
    # Check file exists and is readable
    if [[ ! -f "$script_path" ]]; then
        error_critical "Script file not found: $script_path"
        return 1
    fi
    
    if [[ ! -r "$script_path" ]]; then
        error_critical "Script file not readable: $script_path"
        return 1
    fi
    
    # Check for security issues
    if grep -q "rm -rf /" "$script_path"; then
        error_fatal "Dangerous command detected in script: rm -rf /"
        return 1
    fi
    
    # Validate based on script type
    case "$SCRIPT_TYPE" in
        "bash")
            validate_bash_script "$script_path"
            ;;
        "python")
            validate_python_script "$script_path"
            ;;
        "markdown"|"uscript")
            validate_uscript "$script_path"
            ;;
        *)
            echo -e "${YELLOW}⚠️ Unknown script type - skipping specific validation${NC}"
            ;;
    esac
    
    echo -e "${GREEN}✅ Script validation passed${NC}"
    return 0
}

# Validate bash script
validate_bash_script() {
    local script_path="$1"
    
    # Check syntax
    if ! bash -n "$script_path"; then
        error_critical "Bash syntax error in script"
        return 1
    fi
    
    # Check for executable permission
    if [[ ! -x "$script_path" ]]; then
        echo -e "${YELLOW}⚠️ Script not executable - fixing permissions${NC}"
        chmod +x "$script_path"
    fi
    
    return 0
}

# Validate Python script
validate_python_script() {
    local script_path="$1"
    
    # Check syntax
    if ! python3 -m py_compile "$script_path" 2>/dev/null; then
        error_critical "Python syntax error in script"
        return 1
    fi
    
    return 0
}

# Validate uScript
validate_uscript() {
    local script_path="$1"
    
    # Check for valid uScript markers
    if ! grep -q "```uScript\|```uscript\|```bash\|```python" "$script_path"; then
        error_warning "No recognizable code blocks found in uScript"
    fi
    
    # Check for shortcodes
    if grep -q "\[.*:.*\]" "$script_path"; then
        echo -e "${CYAN}🔧 Shortcodes detected - will be processed${NC}"
    fi
    
    return 0
}

# Execute script based on type and mode
execute_script() {
    local script_path="$1"
    local args="${2:-}"
    
    echo -e "${PURPLE}⚡ Executing script: $script_path${NC}"
    
    # Log execution start
    log_execution_event "Execution started" "info"
    
    local exit_code=0
    case "$SCRIPT_TYPE" in
        "bash")
            execute_bash_script "$script_path" "$args"
            exit_code=$?
            ;;
        "python")
            execute_python_script "$script_path" "$args"
            exit_code=$?
            ;;
        "javascript")
            execute_javascript_script "$script_path" "$args"
            exit_code=$?
            ;;
        "markdown"|"uscript")
            execute_uscript "$script_path" "$args"
            exit_code=$?
            ;;
        *)
            error_critical "Unsupported script type: $SCRIPT_TYPE"
            exit_code=1
            ;;
    esac
    
    # Log execution completion
    if [[ $exit_code -eq 0 ]]; then
        log_execution_event "Execution completed successfully" "success"
        echo -e "${GREEN}✅ Script executed successfully${NC}"
    else
        log_execution_event "Execution failed with exit code $exit_code" "error"
        echo -e "${RED}❌ Script execution failed (exit code: $exit_code)${NC}"
        
        # Attempt retry if enabled
        if [[ "$RETRY_ENABLED" == true && $CURRENT_RETRY -lt $MAX_RETRIES ]]; then
            ((CURRENT_RETRY++))
            echo -e "${YELLOW}🔄 Retrying execution (attempt $CURRENT_RETRY/$MAX_RETRIES)${NC}"
            sleep 2
            execute_script "$script_path" "$args"
            return $?
        fi
    fi
    
    return $exit_code
}

# Execute bash script
execute_bash_script() {
    local script_path="$1"
    local args="$2"
    
    case "$EXECUTION_MODE" in
        "container")
            echo -e "${CYAN}🐳 Executing bash script in container${NC}"
            bash "$BASH_CONTAINER" script "$script_path"
            ;;
        "native")
            echo -e "${BLUE}🏃 Executing bash script natively${NC}"
            bash "$script_path" $args
            ;;
        *)
            echo -e "${BLUE}🏃 Executing bash script (default mode)${NC}"
            bash "$script_path" $args
            ;;
    esac
}

# Execute Python script
execute_python_script() {
    local script_path="$1"
    local args="$2"
    
    case "$EXECUTION_MODE" in
        "container")
            echo -e "${CYAN}🐳 Executing Python script in container${NC}"
            bash "$BASH_CONTAINER" exec "python3 '$script_path' $args"
            ;;
        "native")
            echo -e "${BLUE}🐍 Executing Python script natively${NC}"
            python3 "$script_path" $args
            ;;
        *)
            echo -e "${BLUE}🐍 Executing Python script (default mode)${NC}"
            python3 "$script_path" $args
            ;;
    esac
}

# Execute JavaScript script
execute_javascript_script() {
    local script_path="$1"
    local args="$2"
    
    case "$EXECUTION_MODE" in
        "container")
            echo -e "${CYAN}🐳 Executing JavaScript script in container${NC}"
            bash "$BASH_CONTAINER" exec "node '$script_path' $args"
            ;;
        "native")
            echo -e "${BLUE}📜 Executing JavaScript script natively${NC}"
            node "$script_path" $args
            ;;
        *)
            echo -e "${BLUE}📜 Executing JavaScript script (default mode)${NC}"
            node "$script_path" $args
            ;;
    esac
}

# Execute uScript (markdown-based)
execute_uscript() {
    local script_path="$1"
    local args="$2"
    
    echo -e "${PURPLE}📝 Executing uScript: $script_path${NC}"
    
    # Process shortcodes first if present
    if grep -q "\[.*:.*\]" "$script_path"; then
        echo -e "${CYAN}🔧 Processing shortcodes...${NC}"
        local processed_script=$(mktemp)
        bash "$SHORTCODE_PROCESSOR" file "$script_path" "$processed_script"
        script_path="$processed_script"
    fi
    
    # Extract and execute code blocks
    local temp_dir=$(mktemp -d)
    local block_count=0
    local current_lang=""
    local in_code_block=false
    local current_script=""
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^\`\`\`([a-zA-Z0-9]+) ]]; then
            # Start of code block
            current_lang="${BASH_REMATCH[1],,}"  # lowercase
            in_code_block=true
            ((block_count++))
            current_script="$temp_dir/block_${block_count}.${current_lang}"
            echo "# Generated from uScript block $block_count" > "$current_script"
            
        elif [[ "$line" =~ ^\`\`\`$ ]] && [[ "$in_code_block" == true ]]; then
            # End of code block - execute it
            in_code_block=false
            
            if [[ -s "$current_script" ]]; then
                echo -e "${BLUE}🔧 Executing code block $block_count ($current_lang)${NC}"
                
                case "$current_lang" in
                    "bash"|"sh")
                        chmod +x "$current_script"
                        bash "$current_script"
                        ;;
                    "python"|"py")
                        python3 "$current_script"
                        ;;
                    "javascript"|"js")
                        node "$current_script"
                        ;;
                    "uscript")
                        # Recursive uScript execution
                        execute_uscript "$current_script"
                        ;;
                    *)
                        echo -e "${YELLOW}⚠️ Unknown code block language: $current_lang${NC}"
                        ;;
                esac
            fi
            
        elif [[ "$in_code_block" == true ]]; then
            # Add line to current script
            echo "$line" >> "$current_script"
        fi
    done < "$script_path"
    
    # Cleanup
    rm -rf "$temp_dir"
    
    # Remove processed script if it was temporary
    if [[ "$script_path" =~ ^/tmp/ ]]; then
        rm -f "$script_path"
    fi
}

# Log execution events
log_execution_event() {
    local message="$1"
    local level="${2:-info}"
    local timestamp=$(date -Iseconds)
    
    local log_file="$UHOME/uMemory/logs/executions/${EXECUTION_ID}.md"
    
    case "$level" in
        "error")
            echo "- ❌ **$timestamp**: $message" >> "$log_file"
            ;;
        "warning")
            echo "- ⚠️ **$timestamp**: $message" >> "$log_file"
            ;;
        "success")
            echo "- ✅ **$timestamp**: $message" >> "$log_file"
            ;;
        *)
            echo "- ℹ️ **$timestamp**: $message" >> "$log_file"
            ;;
    esac
    
    # Also log to moves if significant
    if [[ "$level" == "error" || "$level" == "success" ]]; then
        bash "$UHOME/uCode/log.sh" move "Script execution: $message"
    fi
}

# Finalize execution
finalize_execution() {
    local exit_code="${1:-0}"
    
    END_TIME=$(date +%s)
    EXECUTION_DURATION=$((END_TIME - START_TIME))
    
    local log_file="$UHOME/uMemory/logs/executions/${EXECUTION_ID}.md"
    
    # Add execution summary
    cat >> "$log_file" << EOF

## Execution Summary
- **Duration**: ${EXECUTION_DURATION}s
- **Exit Code**: $exit_code
- **Retries**: $CURRENT_RETRY
- **Completed**: $(date -Iseconds)

## Performance Metrics
- **Script Type**: $SCRIPT_TYPE
- **Execution Mode**: $EXECUTION_MODE
- **Memory Usage**: $(ps -o rss= -p $$ | awk '{print $1}')KB

---
*Generated by Enhanced Script Runner v1.7.1*
EOF
    
    echo -e "${PURPLE}📊 Execution completed in ${EXECUTION_DURATION}s${NC}"
    
    # Performance logging
    if [[ -f "$UHOME/uCode/log.sh" ]]; then
        bash "$UHOME/uCode/log.sh" move "Script execution completed: ${SCRIPT_PATH} (${EXECUTION_DURATION}s)"
    fi
    
    # Update dashboard if available
    if [[ -f "$UHOME/uCode/dash.sh" ]]; then
        echo "Last script execution: $(basename "$SCRIPT_PATH") - ${EXECUTION_DURATION}s" >> "$UHOME/uMemory/state/recent-activity.log"
    fi
}

# Show execution statistics
show_execution_stats() {
    echo -e "${PURPLE}📊 Script Execution Statistics${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local log_dir="$UHOME/uMemory/logs/executions"
    if [[ -d "$log_dir" ]]; then
        local total_executions=$(find "$log_dir" -name "exec_*.md" | wc -l)
        local today_executions=$(find "$log_dir" -name "exec_*.md" -mtime 0 | wc -l)
        local successful_executions=$(grep -l "Exit Code.*: 0" "$log_dir"/exec_*.md 2>/dev/null | wc -l)
        
        echo "📊 Total Executions: $total_executions"
        echo "📅 Today: $today_executions"
        echo "✅ Successful: $successful_executions"
        
        if [[ $total_executions -gt 0 ]]; then
            local success_rate=$((successful_executions * 100 / total_executions))
            echo "📈 Success Rate: ${success_rate}%"
        fi
        
        echo ""
        echo "🔍 Recent Executions:"
        find "$log_dir" -name "exec_*.md" -mtime 0 | head -5 | while read -r file; do
            local script=$(grep "^- \*\*Script\*\*:" "$file" | cut -d':' -f2- | xargs)
            local duration=$(grep "^- \*\*Duration\*\*:" "$file" | cut -d':' -f2 | cut -d's' -f1 | xargs)
            local exit_code=$(grep "^- \*\*Exit Code\*\*:" "$file" | cut -d':' -f2 | xargs)
            echo "  • $(basename "$script") - ${duration}s (exit: $exit_code)"
        done
    else
        echo "No execution logs found"
    fi
}

# Main command interface
main() {
    case "${1:-help}" in
        "run")
            local script_path="$2"
            local mode="${3:-native}"
            local args="${4:-}"
            
            if [[ -z "$script_path" ]]; then
                error_critical "Script path required"
                return 1
            fi
            
            init_execution "$script_path" "$mode"
            detect_script_type "$script_path"
            
            if validate_script "$script_path"; then
                execute_script "$script_path" "$args"
                local exit_code=$?
                finalize_execution $exit_code
                return $exit_code
            else
                finalize_execution 1
                return 1
            fi
            ;;
        "validate")
            local script_path="$2"
            detect_script_type "$script_path"
            validate_script "$script_path"
            ;;
        "stats")
            show_execution_stats
            ;;
        "help"|*)
            echo -e "${PURPLE}🚀 Enhanced uScript Runner v1.7.1${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Usage: $0 <command> [arguments]"
            echo ""
            echo "Commands:"
            echo "  run <script> [mode] [args]    - Execute script (mode: native|container)"
            echo "  validate <script>             - Validate script without execution"
            echo "  stats                         - Show execution statistics"
            echo ""
            echo "Supported Script Types:"
            echo "  • Bash (.sh) - Shell scripts"
            echo "  • Python (.py) - Python scripts"  
            echo "  • JavaScript (.js) - Node.js scripts"
            echo "  • uScript (.md) - Markdown-based scripts with code blocks"
            echo ""
            echo "Execution Modes:"
            echo "  • native - Direct execution (default)"
            echo "  • container - Sandboxed execution"
            echo ""
            echo "Examples:"
            echo "  $0 run ./uScript/examples/hello-world.md"
            echo "  $0 run ./scripts/backup.sh container"
            echo "  $0 validate ./uScript/automation/daily-tasks.md"
            echo ""
            echo "Features:"
            echo "  ✅ Multi-language support"
            echo "  ✅ Error handling and recovery"
            echo "  ✅ Performance tracking"
            echo "  ✅ Shortcode processing"
            echo "  ✅ Containerized execution"
            echo "  ✅ Comprehensive logging"
            ;;
    esac
}

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
