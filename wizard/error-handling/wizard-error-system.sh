#!/bin/bash

# uDOS Wizard Error Handling System
# File: wizard-error-system.sh
# Purpose: Comprehensive error handling system for wizard development environment
# Level: 100/100 - Full Development Authority
# uHEX: E8012000 - Role Based Error Handling System

set -euo pipefail

# Get wizard root and load development logging system
WIZARD_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEV_LOGGER="$WIZARD_ROOT/error-handling/wizard-dev-logging.sh"

# Load development logging functions if available
if [[ -f "$DEV_LOGGER" ]]; then
    source "$DEV_LOGGER"
else
    # Fallback logging functions
    log_wizard_error() { echo "🔥 ERROR: $1" >&2; }
    log_wizard_warning() { echo "⚠️ WARNING: $1" >&2; }
    log_wizard_info() { echo "💡 INFO: $1"; }
    log_wizard_success() { echo "✨ SUCCESS: $1"; }
fi

# Error handling configuration
ERROR_RECOVERY_ENABLED="${WIZARD_ERROR_RECOVERY:-true}"
ERROR_NOTIFICATIONS_ENABLED="${WIZARD_ERROR_NOTIFICATIONS:-true}"
ERROR_AUTO_FIX_ENABLED="${WIZARD_ERROR_AUTO_FIX:-false}"

# Trap error signals and handle them
trap 'handle_wizard_error $? "$BASH_COMMAND" "$LINENO" "$BASH_SOURCE"' ERR
trap 'handle_wizard_exit' EXIT
trap 'handle_wizard_interrupt' INT TERM

# Global error context
WIZARD_ERROR_CONTEXT=""
WIZARD_OPERATION=""
WIZARD_ERROR_COUNT=0

# Set error context for operations
set_error_context() {
    WIZARD_ERROR_CONTEXT="$1"
    WIZARD_OPERATION="${2:-unknown}"
    log_wizard_debug "Error context set: $WIZARD_ERROR_CONTEXT [$WIZARD_OPERATION]"
}

# Clear error context
clear_error_context() {
    WIZARD_ERROR_CONTEXT=""
    WIZARD_OPERATION=""
}

# Main error handler
handle_wizard_error() {
    local exit_code="$1"
    local failed_command="$2"
    local line_number="$3"
    local source_file="$4"
    
    ((WIZARD_ERROR_COUNT++))
    
    local error_id="WIZ_ERR_$(date +%Y%m%d_%H%M%S)_${RANDOM}"
    
    log_wizard_error "Wizard Error Encountered - ID: $error_id"
    
    # Log detailed error information
    cat << EOF >&2

🔥 WIZARD DEVELOPMENT ERROR - $error_id
═══════════════════════════════════════════════════════════════
Exit Code: $exit_code
Failed Command: $failed_command
Line Number: $line_number
Source File: $source_file
Context: ${WIZARD_ERROR_CONTEXT:-unknown}
Operation: ${WIZARD_OPERATION:-unknown}
Error Count: $WIZARD_ERROR_COUNT
Timestamp: $(date -Iseconds)

Stack Trace:
$(print_stack_trace)

Environment:
Working Directory: $(pwd)
User: ${USER:-unknown}
Shell: $SHELL
Terminal: ${TERM:-unknown}

Git Context:
Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'not a git repo')
Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
Status: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ') uncommitted changes

System Resources:
$(get_system_resources)

═══════════════════════════════════════════════════════════════
EOF

    # Log to development logger
    if command -v dev_log >/dev/null 2>&1; then
        dev_log "ERROR" "Error ID $error_id: $failed_command (exit code $exit_code)" "wizard_error_handler" true
    fi
    
    # Attempt error recovery if enabled
    if [[ "$ERROR_RECOVERY_ENABLED" == "true" ]]; then
        attempt_error_recovery "$exit_code" "$failed_command" "$error_id"
    fi
    
    # Send notifications if enabled
    if [[ "$ERROR_NOTIFICATIONS_ENABLED" == "true" ]]; then
        send_error_notification "$error_id" "$failed_command" "$exit_code"
    fi
    
    # Suggest fixes based on error patterns
    suggest_error_fixes "$exit_code" "$failed_command"
    
    # Create error report
    create_error_report "$error_id" "$exit_code" "$failed_command" "$line_number" "$source_file"
}

# Print stack trace
print_stack_trace() {
    local i=1
    echo "Call stack:"
    while caller $i 2>/dev/null; do
        ((i++))
    done | while read line func file; do
        echo "  $i. $func at $file:$line"
    done
}

# Get system resources
get_system_resources() {
    cat << EOF
Memory: $(get_memory_usage 2>/dev/null || echo "unknown")
CPU Load: $(uptime | awk -F'load average:' '{print $2}' | sed 's/^[ \t]*//' || echo "unknown")
Disk Space: $(df -h . 2>/dev/null | tail -1 | awk '{print $4 " available"}' || echo "unknown")
Network: $(ping -c 1 -W 1 google.com >/dev/null 2>&1 && echo "online" || echo "offline")
EOF
}

# Attempt error recovery
attempt_error_recovery() {
    local exit_code="$1"
    local failed_command="$2"
    local error_id="$3"
    
    log_wizard_info "Attempting error recovery for $error_id"
    
    case "$exit_code" in
        1)
            # General error - try basic recovery
            log_wizard_info "Attempting basic error recovery"
            basic_error_recovery "$failed_command"
            ;;
        2)
            # Command not found
            log_wizard_info "Command not found - suggesting alternatives"
            suggest_command_alternatives "$failed_command"
            ;;
        126)
            # Permission denied
            log_wizard_info "Permission denied - checking file permissions"
            check_permissions "$failed_command"
            ;;
        127)
            # Command not found
            log_wizard_info "Command not found - checking PATH"
            check_command_availability "$failed_command"
            ;;
        130)
            # Script interrupted
            log_wizard_info "Script interrupted - cleaning up"
            cleanup_interrupted_operation
            ;;
        *)
            log_wizard_info "Unknown error code $exit_code - performing general recovery"
            general_error_recovery "$exit_code" "$failed_command"
            ;;
    esac
}

# Basic error recovery
basic_error_recovery() {
    local failed_command="$1"
    
    # Check if it's a directory/file issue
    if [[ "$failed_command" =~ cd[[:space:]] ]]; then
        local dir=$(echo "$failed_command" | sed 's/cd[[:space:]]*//')
        log_wizard_info "Directory change failed - checking if directory exists: $dir"
        if [[ ! -d "$dir" ]]; then
            log_wizard_warning "Directory $dir does not exist"
            if [[ "$ERROR_AUTO_FIX_ENABLED" == "true" ]]; then
                log_wizard_info "Creating directory: $dir"
                mkdir -p "$dir" && log_wizard_success "Directory created successfully"
            fi
        fi
    fi
    
    # Check if it's a file operation issue
    if [[ "$failed_command" =~ (cp|mv|rm|cat|less|more)[[:space:]] ]]; then
        log_wizard_info "File operation failed - checking file existence and permissions"
        # Extract filename pattern and check
        local filename=$(echo "$failed_command" | awk '{print $NF}')
        if [[ -n "$filename" && ! -e "$filename" ]]; then
            log_wizard_warning "File does not exist: $filename"
        elif [[ -e "$filename" ]]; then
            log_wizard_info "File exists but operation failed - checking permissions"
            ls -la "$filename"
        fi
    fi
}

# Check command availability
check_command_availability() {
    local command_name=$(echo "$1" | awk '{print $1}')
    
    log_wizard_info "Checking availability of command: $command_name"
    
    if ! command -v "$command_name" >/dev/null 2>&1; then
        log_wizard_warning "Command '$command_name' not found in PATH"
        log_wizard_info "Current PATH: $PATH"
        
        # Suggest installation
        case "$command_name" in
            git) log_wizard_info "Try: brew install git" ;;
            node|npm) log_wizard_info "Try: brew install node" ;;
            python|python3) log_wizard_info "Try: brew install python" ;;
            jq) log_wizard_info "Try: brew install jq" ;;
            *) log_wizard_info "Try: brew install $command_name or check if it's available via package manager" ;;
        esac
    else
        log_wizard_info "Command '$command_name' is available at: $(command -v "$command_name")"
    fi
}

# Check permissions
check_permissions() {
    local failed_command="$1"
    local filename=$(echo "$failed_command" | awk '{print $NF}')
    
    if [[ -e "$filename" ]]; then
        log_wizard_info "File permissions for $filename:"
        ls -la "$filename"
        
        if [[ -f "$filename" && ! -x "$filename" ]]; then
            log_wizard_warning "File is not executable"
            if [[ "$ERROR_AUTO_FIX_ENABLED" == "true" ]]; then
                log_wizard_info "Making file executable: chmod +x $filename"
                chmod +x "$filename" && log_wizard_success "File made executable"
            else
                log_wizard_info "To fix: chmod +x $filename"
            fi
        fi
    fi
}

# Suggest command alternatives
suggest_command_alternatives() {
    local failed_command="$1"
    local command_name=$(echo "$failed_command" | awk '{print $1}')
    
    log_wizard_info "Suggesting alternatives for: $command_name"
    
    case "$command_name" in
        ls) log_wizard_info "Alternatives: dir, find ." ;;
        cat) log_wizard_info "Alternatives: less, more, head, tail" ;;
        grep) log_wizard_info "Alternatives: rg (ripgrep), ag (silver searcher)" ;;
        find) log_wizard_info "Alternatives: fd, locate" ;;
        vim|vi) log_wizard_info "Alternatives: nano, emacs, code" ;;
        *) log_wizard_info "Check if command name is spelled correctly" ;;
    esac
}

# Suggest error fixes
suggest_error_fixes() {
    local exit_code="$1"
    local failed_command="$2"
    
    log_wizard_info "🔧 Suggested fixes for error (exit code $exit_code):"
    
    case "$exit_code" in
        1) echo "  - Check command syntax and arguments" ;;
        2) echo "  - Verify command exists and is installed" ;;
        126) echo "  - Check file permissions (try: chmod +x filename)" ;;
        127) echo "  - Command not found - check spelling or install" ;;
        130) echo "  - Script was interrupted - run again" ;;
        *) echo "  - Check system resources and dependencies" ;;
    esac
    
    echo "  - Review recent changes that might have caused this error"
    echo "  - Check the wizard development documentation"
    echo "  - Enable debug mode for more detailed information"
}

# Send error notification
send_error_notification() {
    local error_id="$1"
    local failed_command="$2"
    local exit_code="$3"
    
    # macOS notification
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"Command failed: $failed_command\" with title \"Wizard Error\" subtitle \"Error ID: $error_id\"" 2>/dev/null || true
    fi
    
    # System log
    if command -v logger >/dev/null 2>&1; then
        logger -t "uDOS-Wizard-Error" "[$error_id] Command failed: $failed_command (exit code: $exit_code)"
    fi
}

# Create error report
create_error_report() {
    local error_id="$1"
    local exit_code="$2"
    local failed_command="$3"
    local line_number="$4"
    local source_file="$5"
    
    local report_file="$WIZARD_ROOT/errors/error-report-$error_id.md"
    
    mkdir -p "$(dirname "$report_file")"
    
    cat > "$report_file" << EOF
# 🔥 Wizard Error Report - $error_id

**Timestamp**: $(date -Iseconds)  
**Error Count**: $WIZARD_ERROR_COUNT  
**Context**: ${WIZARD_ERROR_CONTEXT:-unknown}  
**Operation**: ${WIZARD_OPERATION:-unknown}

## Error Details

- **Exit Code**: $exit_code
- **Failed Command**: \`$failed_command\`
- **Line Number**: $line_number
- **Source File**: $source_file

## Environment Information

- **Working Directory**: $(pwd)
- **User**: ${USER:-unknown}
- **Shell**: $SHELL
- **Terminal**: ${TERM:-unknown}

## Git Context

- **Branch**: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'not a git repo')
- **Commit**: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
- **Uncommitted Changes**: $(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

## System Resources

$(get_system_resources)

## Stack Trace

\`\`\`
$(print_stack_trace)
\`\`\`

## Recovery Actions Taken

$(if [[ "$ERROR_RECOVERY_ENABLED" == "true" ]]; then echo "- Automatic error recovery attempted"; else echo "- No automatic recovery (disabled)"; fi)
$(if [[ "$ERROR_NOTIFICATIONS_ENABLED" == "true" ]]; then echo "- Error notifications sent"; else echo "- No notifications sent (disabled)"; fi)

## Recommendations

1. Review the failed command and its arguments
2. Check if all required dependencies are installed
3. Verify file permissions and directory existence
4. Review recent code changes that might have caused this error
5. Check system resources (memory, disk space, network)
6. Enable debug mode for more detailed logging

---

*Generated by uDOS Wizard Error Handling System v1.3*  
*uHEX: E8012000 - Role Based Error Handling System*
EOF

    log_wizard_info "Error report created: $report_file"
}

# Handle script exit
handle_wizard_exit() {
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log_wizard_success "Wizard operation completed successfully"
    else
        log_wizard_warning "Wizard operation exited with code: $exit_code"
    fi
    
    # Clear error context on exit
    clear_error_context
}

# Handle interrupt signals
handle_wizard_interrupt() {
    log_wizard_warning "Wizard operation interrupted"
    
    # Clean up any temporary files or processes
    cleanup_interrupted_operation
    
    exit 130
}

# Cleanup after interruption
cleanup_interrupted_operation() {
    log_wizard_info "Cleaning up interrupted operation"
    
    # Kill any background processes started by this script
    if [[ -n "${WIZARD_BG_PIDS:-}" ]]; then
        for pid in $WIZARD_BG_PIDS; do
            if kill -0 "$pid" 2>/dev/null; then
                log_wizard_info "Terminating background process: $pid"
                kill "$pid" 2>/dev/null || true
            fi
        done
    fi
    
    # Remove temporary files
    if [[ -n "${WIZARD_TEMP_FILES:-}" ]]; then
        for temp_file in $WIZARD_TEMP_FILES; do
            if [[ -f "$temp_file" ]]; then
                log_wizard_info "Removing temporary file: $temp_file"
                rm -f "$temp_file" 2>/dev/null || true
            fi
        done
    fi
}

# General error recovery
general_error_recovery() {
    local exit_code="$1"
    local failed_command="$2"
    
    log_wizard_info "Performing general error recovery"
    
    # Check system health
    if ! ping -c 1 -W 1 google.com >/dev/null 2>&1; then
        log_wizard_warning "Network connectivity issues detected"
    fi
    
    # Check disk space
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ "$disk_usage" -gt 90 ]]; then
        log_wizard_warning "Disk space is low: ${disk_usage}% used"
    fi
    
    # Check if we're in a git repository and if there are uncommitted changes
    if git rev-parse --git-dir >/dev/null 2>&1; then
        local uncommitted=$(git status --porcelain | wc -l | tr -d ' ')
        if [[ "$uncommitted" -gt 0 ]]; then
            log_wizard_info "Uncommitted changes detected: $uncommitted files"
        fi
    fi
}

# Safe command execution with error handling
safe_execute() {
    local command="$1"
    local context="${2:-safe_execute}"
    local operation="${3:-command}"
    
    set_error_context "$context" "$operation"
    
    log_wizard_info "Executing: $command"
    
    if eval "$command"; then
        log_wizard_success "Command completed successfully: $command"
        clear_error_context
        return 0
    else
        local exit_code=$?
        log_wizard_error "Command failed with exit code $exit_code: $command"
        clear_error_context
        return $exit_code
    fi
}

# Wizard-specific error categories
handle_build_error() {
    local error_message="$1"
    set_error_context "build" "compilation"
    log_wizard_error "Build Error: $error_message"
    track_dev_activity "build" "Build failed: $error_message" false
}

handle_deployment_error() {
    local error_message="$1"
    set_error_context "deployment" "release"
    log_wizard_error "Deployment Error: $error_message"
    track_dev_activity "deployment" "Deployment failed: $error_message" false
}

handle_test_error() {
    local error_message="$1"
    set_error_context "testing" "validation"
    log_wizard_error "Test Error: $error_message"
    track_dev_activity "test" "Test failed: $error_message" false
}

# Export functions for use in other scripts
export -f set_error_context
export -f clear_error_context
export -f safe_execute
export -f handle_build_error
export -f handle_deployment_error
export -f handle_test_error

# Show usage if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    cat << EOF
🧙‍♂️ uDOS Wizard Error Handling System v1.3

This script provides comprehensive error handling for the wizard development environment.

To use in your scripts:
  source "$0"

Then use functions like:
  set_error_context "build" "compilation"
  safe_execute "your-command" "context" "operation"
  handle_build_error "Build failed message"

Environment Variables:
  WIZARD_ERROR_RECOVERY=true         Enable automatic error recovery
  WIZARD_ERROR_NOTIFICATIONS=true    Enable error notifications
  WIZARD_ERROR_AUTO_FIX=false        Enable automatic fixes (use with caution)

🔮 Advanced Development Authority - Level 100 Access
uHEX: E8012000 - Role Based Error Handling System
EOF
fi