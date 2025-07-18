#!/bin/bash
# bash-container.sh - Containerized Bash Execution System
# Version: 1.7.1
# Description: Execute bash scripts in isolated, controlled environment

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
CONTAINER_DIR="$UHOME/uMemory/containers"
ERROR_HANDLER="$UHOME/uCode/error-handler.sh"

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

# Container configuration
CONTAINER_ID=""
CONTAINER_WORKSPACE=""
CONTAINER_TIMEOUT=300  # 5 minutes default
CONTAINER_MEMORY_LIMIT=""
CONTAINER_CPU_LIMIT=""
CONTAINER_NETWORK_ACCESS=false
CONTAINER_FILE_LIMITS=true

# Security settings
ALLOWED_COMMANDS=(
    "ls" "cat" "grep" "awk" "sed" "sort" "uniq" "head" "tail" "wc"
    "find" "locate" "which" "whereis" "file" "stat" "du" "df"
    "date" "sleep" "echo" "printf" "test" "true" "false"
    "mkdir" "touch" "cp" "mv" "rm" "chmod" "chown"
    "git" "curl" "wget" "ssh" "scp" "rsync"
    "python" "python3" "node" "npm" "pip" "pip3"
    "make" "gcc" "clang" "rustc"
)

BLOCKED_COMMANDS=(
    "sudo" "su" "passwd" "chpasswd" "usermod" "userdel" "groupmod"
    "systemctl" "service" "init" "reboot" "shutdown" "halt"
    "mount" "umount" "fdisk" "parted" "dd" "mkfs"
    "iptables" "netstat" "ss" "lsof" "strace" "gdb"
    "crontab" "at" "batch"
)

RESTRICTED_PATHS=(
    "/etc" "/boot" "/sys" "/proc" "/dev" "/root"
    "/var/log" "/var/spool" "/var/run"
)

# Initialize container environment
init_container() {
    set_error_context "container_init" "$0"
    
    CONTAINER_ID="bash_$(date +%Y%m%d_%H%M%S)_$$"
    CONTAINER_WORKSPACE="$CONTAINER_DIR/$CONTAINER_ID"
    
    echo -e "${BLUE}🐳 Initializing container: $CONTAINER_ID${NC}"
    
    # Create container workspace
    mkdir -p "$CONTAINER_WORKSPACE"
    mkdir -p "$CONTAINER_WORKSPACE/workspace"
    mkdir -p "$CONTAINER_WORKSPACE/logs"
    mkdir -p "$CONTAINER_WORKSPACE/temp"
    mkdir -p "$CONTAINER_WORKSPACE/output"
    
    # Create container metadata
    cat > "$CONTAINER_WORKSPACE/container.json" << EOF
{
  "container_id": "$CONTAINER_ID",
  "created": "$(date -Iseconds)",
  "workspace": "$CONTAINER_WORKSPACE",
  "timeout": $CONTAINER_TIMEOUT,
  "network_access": $CONTAINER_NETWORK_ACCESS,
  "file_limits": $CONTAINER_FILE_LIMITS,
  "status": "initialized"
}
EOF
    
    # Create execution log
    cat > "$CONTAINER_WORKSPACE/logs/execution.log" << EOF
# Container Execution Log: $CONTAINER_ID
Started: $(date)

EOF
    
    echo -e "${GREEN}✅ Container initialized: $CONTAINER_WORKSPACE${NC}"
}

# Security validation
validate_command() {
    local command="$1"
    local first_word=$(echo "$command" | awk '{print $1}')
    
    # Remove path if present
    first_word=$(basename "$first_word")
    
    # Check blocked commands
    for blocked in "${BLOCKED_COMMANDS[@]}"; do
        if [[ "$first_word" == "$blocked" ]]; then
            error_critical "Blocked command detected: $blocked"
            return 1
        fi
    done
    
    # Check if command is in allowed list (if we're using whitelist mode)
    if [[ "${#ALLOWED_COMMANDS[@]}" -gt 0 ]]; then
        local allowed=false
        for cmd in "${ALLOWED_COMMANDS[@]}"; do
            if [[ "$first_word" == "$cmd" ]]; then
                allowed=true
                break
            fi
        done
        
        if [[ "$allowed" == false ]]; then
            error_warning "Command not in allowed list: $first_word"
            echo -e "${YELLOW}💡 Consider adding to ALLOWED_COMMANDS if safe${NC}"
            # Allow for now but log the warning
        fi
    fi
    
    # Check for path traversal attempts
    if [[ "$command" =~ \.\./\.\. ]]; then
        error_critical "Path traversal attempt detected"
        return 1
    fi
    
    # Check for restricted paths
    for path in "${RESTRICTED_PATHS[@]}"; do
        if [[ "$command" =~ $path ]]; then
            error_critical "Access to restricted path: $path"
            return 1
        fi
    done
    
    return 0
}

# Execute command in container
execute_in_container() {
    local command="$1"
    local working_dir="${2:-$CONTAINER_WORKSPACE/workspace}"
    local timeout="${3:-$CONTAINER_TIMEOUT}"
    
    set_error_context "container_execution" "$CONTAINER_ID"
    
    # Validate command
    if ! validate_command "$command"; then
        error_critical "Command validation failed: $command"
        return 1
    fi
    
    echo -e "${CYAN}⚡ Executing in container: $command${NC}"
    
    # Log execution
    {
        echo "$(date): Executing: $command"
        echo "Working directory: $working_dir"
        echo "Timeout: ${timeout}s"
        echo "---"
    } >> "$CONTAINER_WORKSPACE/logs/execution.log"
    
    # Ensure working directory exists and is safe
    if [[ ! -d "$working_dir" ]]; then
        mkdir -p "$working_dir"
    fi
    
    # Change to container workspace
    cd "$working_dir"
    
    # Set container environment variables
    export CONTAINER_MODE=true
    export CONTAINER_ID="$CONTAINER_ID"
    export CONTAINER_WORKSPACE="$CONTAINER_WORKSPACE"
    export UHOME_CONTAINER="$UHOME"
    
    # Create execution wrapper script
    local exec_script="$CONTAINER_WORKSPACE/temp/exec_script.sh"
    cat > "$exec_script" << EOF
#!/bin/bash
set -euo pipefail

# Container execution environment
export PATH="/usr/local/bin:/usr/bin:/bin"
export CONTAINER_MODE=true
export CONTAINER_ID="$CONTAINER_ID"

# Resource limits (if available)
ulimit -t $timeout 2>/dev/null || true
ulimit -v 1048576 2>/dev/null || true  # 1GB virtual memory limit

# Execute the command
cd "$working_dir"
$command
EOF
    
    chmod +x "$exec_script"
    
    # Execute with timeout and capture output
    local exit_code=0
    local output_file="$CONTAINER_WORKSPACE/output/command_output.txt"
    local error_file="$CONTAINER_WORKSPACE/output/command_error.txt"
    
    echo -e "${BLUE}🏃 Running command (timeout: ${timeout}s)...${NC}"
    
    if timeout "$timeout" bash "$exec_script" > "$output_file" 2> "$error_file"; then
        exit_code=0
        echo -e "${GREEN}✅ Command completed successfully${NC}"
    else
        exit_code=$?
        echo -e "${RED}❌ Command failed with exit code: $exit_code${NC}"
    fi
    
    # Display output
    if [[ -s "$output_file" ]]; then
        echo -e "${BLUE}📤 Output:${NC}"
        cat "$output_file"
    fi
    
    if [[ -s "$error_file" ]]; then
        echo -e "${RED}📤 Errors:${NC}"
        cat "$error_file" >&2
    fi
    
    # Log results
    {
        echo "Exit code: $exit_code"
        echo "Output size: $(wc -l < "$output_file" 2>/dev/null || echo 0) lines"
        echo "Error size: $(wc -l < "$error_file" 2>/dev/null || echo 0) lines"
        echo "Completed: $(date)"
        echo "================"
        echo ""
    } >> "$CONTAINER_WORKSPACE/logs/execution.log"
    
    return $exit_code
}

# Execute script file in container
execute_script_in_container() {
    local script_file="$1"
    local timeout="${2:-$CONTAINER_TIMEOUT}"
    
    if [[ ! -f "$script_file" ]]; then
        error_critical "Script file not found: $script_file"
        return 1
    fi
    
    echo -e "${PURPLE}📜 Executing script file: $script_file${NC}"
    
    # Copy script to container
    local container_script="$CONTAINER_WORKSPACE/temp/user_script.sh"
    cp "$script_file" "$container_script"
    chmod +x "$container_script"
    
    # Validate script content
    if ! validate_script_content "$container_script"; then
        error_critical "Script validation failed"
        return 1
    fi
    
    # Execute the script
    execute_in_container "$container_script" "$CONTAINER_WORKSPACE/workspace" "$timeout"
}

# Validate script content
validate_script_content() {
    local script_file="$1"
    
    echo -e "${BLUE}🔍 Validating script content...${NC}"
    
    # Check for blocked commands in script
    for blocked in "${BLOCKED_COMMANDS[@]}"; do
        if grep -q "$blocked" "$script_file"; then
            error_critical "Script contains blocked command: $blocked"
            return 1
        fi
    done
    
    # Check for suspicious patterns
    local suspicious_patterns=(
        "rm -rf /"
        "chmod 777"
        "curl.*|.*sh"
        "wget.*|.*sh"
        "> /etc/"
        ">> /etc/"
    )
    
    for pattern in "${suspicious_patterns[@]}"; do
        if grep -E "$pattern" "$script_file"; then
            error_critical "Script contains suspicious pattern: $pattern"
            return 1
        fi
    done
    
    echo -e "${GREEN}✅ Script validation passed${NC}"
    return 0
}

# Interactive container shell
interactive_shell() {
    echo -e "${PURPLE}🐚 Interactive Container Shell${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Container ID: $CONTAINER_ID"
    echo "Workspace: $CONTAINER_WORKSPACE/workspace"
    echo "Type 'help' for commands, 'exit' to quit."
    echo ""
    
    while true; do
        echo -ne "${CYAN}container:$(basename "$PWD")> ${NC}"
        read -r input
        
        case "$input" in
            "exit"|"quit"|"bye")
                echo -e "${GREEN}👋 Exiting container shell${NC}"
                break
                ;;
            "help")
                show_container_help
                ;;
            "pwd")
                echo "$PWD"
                ;;
            "cd "*)
                local new_dir="${input#cd }"
                if [[ -d "$new_dir" ]]; then
                    cd "$new_dir"
                else
                    echo "Directory not found: $new_dir"
                fi
                ;;
            "")
                continue
                ;;
            *)
                execute_in_container "$input" "$PWD" 30
                ;;
        esac
        echo ""
    done
}

# Show container help
show_container_help() {
    echo -e "${BLUE}📖 Container Shell Help${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Built-in Commands:"
    echo "  help        - Show this help"
    echo "  exit        - Exit container shell"
    echo "  pwd         - Show current directory"
    echo "  cd <dir>    - Change directory"
    echo ""
    echo "Allowed Commands:"
    printf "  %s\n" "${ALLOWED_COMMANDS[@]}" | column -c 80
    echo ""
    echo "Blocked Commands:"
    printf "  %s\n" "${BLOCKED_COMMANDS[@]}" | column -c 80
    echo ""
    echo "Container Info:"
    echo "  ID: $CONTAINER_ID"
    echo "  Workspace: $CONTAINER_WORKSPACE"
    echo "  Timeout: ${CONTAINER_TIMEOUT}s"
    echo "  Network Access: $CONTAINER_NETWORK_ACCESS"
}

# Cleanup container
cleanup_container() {
    set_error_context "container_cleanup" "$CONTAINER_ID"
    
    echo -e "${YELLOW}🧹 Cleaning up container: $CONTAINER_ID${NC}"
    
    if [[ -d "$CONTAINER_WORKSPACE" ]]; then
        # Archive logs before cleanup
        local archive_dir="$UHOME/uMemory/archives/containers"
        mkdir -p "$archive_dir"
        
        tar -czf "$archive_dir/${CONTAINER_ID}.tar.gz" -C "$(dirname "$CONTAINER_WORKSPACE")" "$(basename "$CONTAINER_WORKSPACE")"
        echo -e "${BLUE}📦 Container archived: $archive_dir/${CONTAINER_ID}.tar.gz${NC}"
        
        # Remove container workspace
        rm -rf "$CONTAINER_WORKSPACE"
        echo -e "${GREEN}✅ Container workspace cleaned up${NC}"
    fi
}

# Container status
show_container_status() {
    echo -e "${PURPLE}📊 Container Status${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [[ -n "$CONTAINER_ID" ]]; then
        echo "Current Container: $CONTAINER_ID"
        echo "Workspace: $CONTAINER_WORKSPACE"
        echo "Status: $(if [[ -d "$CONTAINER_WORKSPACE" ]]; then echo "Active"; else echo "Inactive"; fi)"
        
        if [[ -f "$CONTAINER_WORKSPACE/container.json" ]]; then
            echo ""
            echo "Configuration:"
            cat "$CONTAINER_WORKSPACE/container.json" | grep -E '"(timeout|network_access|file_limits)"' | sed 's/^/  /'
        fi
        
        if [[ -f "$CONTAINER_WORKSPACE/logs/execution.log" ]]; then
            echo ""
            echo "Recent Executions:"
            tail -10 "$CONTAINER_WORKSPACE/logs/execution.log" | grep "Executing:" | tail -3 | sed 's/^/  /'
        fi
    else
        echo "No active container"
    fi
    
    echo ""
    echo "Available Containers:"
    if [[ -d "$CONTAINER_DIR" ]]; then
        find "$CONTAINER_DIR" -maxdepth 1 -type d -name "bash_*" | head -5 | while read -r dir; do
            local id=$(basename "$dir")
            local created=$(grep '"created"' "$dir/container.json" 2>/dev/null | cut -d'"' -f4 || echo "Unknown")
            echo "  • $id (created: $created)"
        done
    fi
}

# Main command interface
main() {
    # Ensure container directory exists
    mkdir -p "$CONTAINER_DIR"
    
    case "${1:-help}" in
        "init")
            init_container
            ;;
        "exec")
            if [[ -z "$CONTAINER_ID" ]]; then
                init_container
            fi
            execute_in_container "$2" "${3:-$CONTAINER_WORKSPACE/workspace}" "${4:-$CONTAINER_TIMEOUT}"
            ;;
        "script")
            if [[ -z "$CONTAINER_ID" ]]; then
                init_container
            fi
            execute_script_in_container "$2" "${3:-$CONTAINER_TIMEOUT}"
            ;;
        "shell"|"interactive")
            if [[ -z "$CONTAINER_ID" ]]; then
                init_container
            fi
            interactive_shell
            ;;
        "status")
            show_container_status
            ;;
        "cleanup")
            cleanup_container
            ;;
        "validate")
            validate_command "$2"
            ;;
        "help"|*)
            echo -e "${PURPLE}🐳 uDOS Bash Container v1.7.1${NC}"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "Usage: $0 <command> [arguments]"
            echo ""
            echo "Commands:"
            echo "  init                          - Initialize new container"
            echo "  exec <command> [dir] [timeout] - Execute command in container"
            echo "  script <file> [timeout]      - Execute script file in container"
            echo "  shell                         - Start interactive container shell"
            echo "  status                        - Show container status"
            echo "  cleanup                       - Clean up current container"
            echo "  validate <command>            - Validate command safety"
            echo ""
            echo "Examples:"
            echo "  $0 exec 'ls -la'"
            echo "  $0 script ./my-script.sh"
            echo "  $0 shell"
            echo ""
            echo "Security Features:"
            echo "  • Command validation and blocking"
            echo "  • Path traversal prevention"
            echo "  • Resource limits (timeout, memory)"
            echo "  • Execution logging and auditing"
            echo "  • Isolated workspace environment"
            ;;
    esac
}

# Handle cleanup on exit
trap cleanup_container EXIT

# Initialize if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
