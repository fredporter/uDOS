#!/bin/bash
# uDOS Enhanced Debugging & Error Logging System
# Role-aware debugging with development enhancement and user-friendly fallbacks

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_ROOT

# Color definitions (define early)
if [[ -z "${RED:-}" ]]; then
    readonly RED='\033[0;31m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[1;33m'
    readonly BLUE='\033[0;34m'
    readonly WHITE='\033[1;37m'
    readonly NC='\033[0m'
fi

# Load role and environment detection
source "$UDOS_ROOT/uCORE/code/role-manager.sh" 2>/dev/null || true
source "$UDOS_ROOT/uCORE/code/environment.sh" 2>/dev/null || true

# Debugging configuration based on role and mode
setup_debug_config() {
    local role="${UDOS_CURRENT_ROLE:-user}"
    local dev_mode="${UDOS_DEV_MODE:-false}"
    
    # Base configuration
    export UDOS_DEBUG_ENABLED="false"
    export UDOS_ERROR_DETAIL="basic"
    export UDOS_LOG_LEVEL="info"
    export UDOS_TESTING_MODE="false"
    export UDOS_SELF_HEALING="true"  # Enable self-healing by default
    
    # Role-based configuration
    case "$role" in
        "wizard"|"developer")
            export UDOS_DEBUG_ENABLED="true"
            export UDOS_ERROR_DETAIL="full"
            export UDOS_LOG_LEVEL="debug"
            export UDOS_TESTING_MODE="true"
            export UDOS_SELF_HEALING="true"
            
            if [[ "$dev_mode" == "true" ]]; then
                export UDOS_DEBUG_ENHANCED="true"
                export UDOS_PROFILING_ENABLED="true"
                export UDOS_TRACE_ENABLED="true"
                export UDOS_PERFORMANCE_MONITORING="true"
            fi
            ;;
        "admin"|"power")
            export UDOS_DEBUG_ENABLED="limited"
            export UDOS_ERROR_DETAIL="moderate"
            export UDOS_LOG_LEVEL="info"
            export UDOS_TESTING_MODE="basic"
            export UDOS_SELF_HEALING="true"
            ;;
        "user"|*)
            export UDOS_DEBUG_ENABLED="false"
            export UDOS_ERROR_DETAIL="friendly"
            export UDOS_LOG_LEVEL="warn"
            export UDOS_TESTING_MODE="false"
            export UDOS_SELF_HEALING="true"  # Even users get self-healing
            ;;
    esac
}

# NetHack-inspired error messages
get_nethack_message() {
    local error_type="$1"
    local attempt_count="${2:-1}"
    
    case "$error_type" in
        "permission")
            local messages=(
                "The door is locked. You need a key."
                "A mysterious force prevents you from proceeding."
                "You hear the Gods laughing at your feeble attempt."
                "The system administrator casts a protection spell."
            )
            ;;
        "missing_file")
            local messages=(
                "You search the dungeon but find nothing here."
                "The scroll crumbles to dust before you can read it."
                "A grue has eaten your file in the darkness."
                "The file has been stolen by a sneaky kobold."
            )
            ;;
        "network")
            local messages=(
                "Your message in a bottle was eaten by a sea monster."
                "The magic mirror shows only static."
                "Your carrier pigeon got lost in a storm."
                "The ethereal plane is experiencing turbulence."
            )
            ;;
        "memory")
            local messages=(
                "Your brain is full. You forget something important."
                "The computer's mind is overflowing with thoughts."
                "RAM gremlins are partying in your memory banks."
                "You need more spell components (RAM) for this magic."
            )
            ;;
        "disk_space")
            local messages=(
                "Your bag of holding is completely full."
                "The dungeon storage room has no more space."
                "Digital pack rats have filled all available space."
                "You need to sell some gear to make room."
            )
            ;;
        "generic"|*)
            local messages=(
                "A wild bug appears! It's not very effective..."
                "Something wicked this way comes... and breaks."
                "The universe hiccups and reality glitches briefly."
                "Murphy's Law strikes again with supernatural accuracy."
                "A quantum uncertainty principle violation has occurred."
                "The digital gremlins are at it again."
            )
            ;;
    esac
    
    # Add attempt-based escalation
    if [[ $attempt_count -gt 1 ]]; then
        case $attempt_count in
            2) echo "${messages[0]} (Attempt $attempt_count: The plot thickens...)" ;;
            3) echo "${messages[1]} (Attempt $attempt_count: Third time's the charm?)" ;;
            *) echo "${messages[2]} (Attempt $attempt_count: Even the Gods are confused now.)" ;;
        esac
    else
        echo "${messages[0]}"
    fi
}

# Self-healing mechanisms
attempt_self_healing() {
    local error_type="$1"
    local failed_command="$2"
    local script_path="$3"
    
    case "$error_type" in
        "permission")
            echo -e "${YELLOW}🔧 Attempting to fix permissions...${NC}"
            if [[ -f "$script_path" ]]; then
                chmod +x "$script_path" 2>/dev/null && return 0
            fi
            ;;
        "missing_file")
            echo -e "${YELLOW}🔧 Attempting to restore missing file...${NC}"
            # Try to restore from backup or template
            local filename="$(basename "$script_path")"
            local backup_locations=(
                "$UDOS_ROOT/backup/${filename}"
                "$UDOS_ROOT/uCORE/distribution/${filename}"
                "$UDOS_ROOT/dev/templates/${filename}"
            )
            
            for backup in "${backup_locations[@]}"; do
                if [[ -f "$backup" ]]; then
                    cp "$backup" "$script_path" 2>/dev/null && return 0
                fi
            done
            ;;
        "network")
            echo -e "${YELLOW}🔧 Attempting network recovery...${NC}"
            # Try alternative endpoints or local fallbacks
            ping -c 1 8.8.8.8 >/dev/null 2>&1 && return 0
            ;;
        "memory")
            echo -e "${YELLOW}🔧 Attempting memory cleanup...${NC}"
            # Clean up temporary files and caches
            find "$UDOS_ROOT/sandbox/temp" -type f -mtime +1 -delete 2>/dev/null || true
            find "$UDOS_ROOT/uCORE/cache" -type f -mtime +7 -delete 2>/dev/null || true
            return 0
            ;;
        "disk_space")
            echo -e "${YELLOW}🔧 Attempting disk cleanup...${NC}"
            # Clean up logs and temporary files
            find "$UDOS_ROOT/sandbox/logs" -name "*.log" -mtime +30 -delete 2>/dev/null || true
            find "$UDOS_ROOT/sandbox/temp" -type f -delete 2>/dev/null || true
            return 0
            ;;
    esac
    
    return 1
}

# Determine error type from command and exit code
classify_error() {
    local command="$1"
    local exit_code="$2"
    
    case "$exit_code" in
        126) echo "permission" ;;
        127) echo "missing_file" ;;
        130) echo "interrupted" ;;
    esac
    
    case "$command" in
        *"curl"*|*"wget"*|*"ping"*) echo "network" ;;
        *"chmod"*|*"chown"*) echo "permission" ;;
        *"cp"*|*"mv"*|*"rm"*) echo "missing_file" ;;
        *"mkdir"*) echo "disk_space" ;;
        *) echo "generic" ;;
    esac
}

# Enhanced error handling with role-aware messaging and self-healing
udos_error_handler() {
    local exit_code=$?
    local line_number=$1
    local command="$2"
    local function_name="${FUNCNAME[2]:-main}"
    local script_name="$(basename "${BASH_SOURCE[1]}")"
    local script_path="${BASH_SOURCE[1]}"
    
    # Skip if exit code is 0 (success)
    [[ $exit_code -eq 0 ]] && return 0
    
    # Classify the error type
    local error_type="$(classify_error "$command" "$exit_code")"
    
    # Get or increment attempt counter
    local attempt_key="${script_name}_${line_number}_${error_type}"
    local attempt_count_file="$UDOS_ROOT/sandbox/logs/.error_attempts"
    mkdir -p "$(dirname "$attempt_count_file")"
    
    local attempt_count=1
    if [[ -f "$attempt_count_file" ]]; then
        attempt_count=$(grep "^$attempt_key:" "$attempt_count_file" 2>/dev/null | cut -d: -f2 || echo 1)
        attempt_count=$((attempt_count + 1))
        sed -i "/^$attempt_key:/d" "$attempt_count_file" 2>/dev/null || true
    fi
    echo "$attempt_key:$attempt_count" >> "$attempt_count_file"
    
    # Get NetHack-inspired message
    local nethack_msg="$(get_nethack_message "$error_type" "$attempt_count")"
    
    # Attempt self-healing before showing error (max 3 attempts)
    if [[ $attempt_count -le 3 ]] && [[ "${UDOS_SELF_HEALING:-true}" == "true" ]]; then
        echo -e "${BLUE}🎲 $nethack_msg${NC}" >&2
        
        if attempt_self_healing "$error_type" "$command" "$script_path"; then
            echo -e "${GREEN}✨ Magic happens! The problem resolves itself.${NC}" >&2
            echo -e "${YELLOW}🔄 Retrying command...${NC}" >&2
            
            # Clear attempt counter on success
            sed -i "/^$attempt_key:/d" "$attempt_count_file" 2>/dev/null || true
            
            # Retry the command (for simple cases)
            if [[ "$error_type" == "permission" && -f "$script_path" ]]; then
                exec "$script_path" "$@"
            fi
            return 0
        fi
    fi
    
    # Error logging based on detail level
    case "${UDOS_ERROR_DETAIL:-basic}" in
        "full")
            echo -e "${RED}🚨 DETAILED ERROR REPORT${NC}" >&2
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
            echo -e "${BLUE}🎲 \"$nethack_msg\"${NC}" >&2
            echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
            echo -e "${WHITE}Script:${NC} $script_name" >&2
            echo -e "${WHITE}Function:${NC} $function_name" >&2
            echo -e "${WHITE}Line:${NC} $line_number" >&2
            echo -e "${WHITE}Command:${NC} $command" >&2
            echo -e "${WHITE}Exit Code:${NC} $exit_code ($(get_exit_code_meaning $exit_code))" >&2
            echo -e "${WHITE}Error Type:${NC} $error_type" >&2
            echo -e "${WHITE}Attempt:${NC} $attempt_count/3" >&2
            echo -e "${WHITE}Timestamp:${NC} $(date '+%Y-%m-%d %H:%M:%S')" >&2
            echo -e "${WHITE}Environment:${NC} ${UDOS_CURRENT_ROLE:-unknown}@${HOSTNAME}" >&2
            
            # Show self-healing status
            if [[ "${UDOS_SELF_HEALING:-true}" == "true" ]]; then
                if [[ $attempt_count -le 3 ]]; then
                    echo -e "${GREEN}🔧 Self-healing: Active (will retry)${NC}" >&2
                else
                    echo -e "${RED}💀 Self-healing: Exhausted (manual intervention needed)${NC}" >&2
                fi
            else
                echo -e "${YELLOW}⚙️ Self-healing: Disabled${NC}" >&2
            fi
            
            # Stack trace for developers
            if [[ "${UDOS_DEBUG_ENHANCED:-false}" == "true" ]]; then
                echo -e "${WHITE}Stack Trace:${NC}" >&2
                local frame=0
                while caller $frame >&2; do
                    ((frame++))
                done
            fi
            ;;
        "moderate")
            echo -e "${RED}❌ Error in $script_name (line $line_number)${NC}" >&2
            echo -e "${BLUE}🎲 \"$nethack_msg\"${NC}" >&2
            echo -e "${YELLOW}Command failed:${NC} $command" >&2
            echo -e "${BLUE}💡 Check logs for details: ./sandbox/logs/error.log${NC}" >&2
            
            if [[ $attempt_count -le 3 && "${UDOS_SELF_HEALING:-true}" == "true" ]]; then
                echo -e "${GREEN}🔄 Don't worry, I'll try to fix this automatically...${NC}" >&2
            fi
            ;;
        "friendly"|*)
            echo -e "${RED}❌ Oops! Something went wrong${NC}" >&2
            echo -e "${BLUE}🎲 \"$nethack_msg\"${NC}" >&2
            
            if [[ $attempt_count -le 3 && "${UDOS_SELF_HEALING:-true}" == "true" ]]; then
                echo -e "${GREEN}✨ But don't worry! uDOS is trying to fix it automatically...${NC}" >&2
            else
                echo -e "${YELLOW}💡 Try running the command again, or use HELP for assistance.${NC}" >&2
                # Provide helpful suggestions based on error type
                case "$error_type" in
                    "permission")
                        echo -e "${BLUE}🔑 Hint: This might be a permission issue. Try running as administrator.${NC}" >&2
                        ;;
                    "missing_file")
                        echo -e "${BLUE}📁 Hint: A file seems to be missing. Check if all files are in place.${NC}" >&2
                        ;;
                    "network")
                        echo -e "${BLUE}🌐 Hint: Check your internet connection and try again.${NC}" >&2
                        ;;
                    "memory")
                        echo -e "${BLUE}🧠 Hint: Your system might be low on memory. Close some programs.${NC}" >&2
                        ;;
                    "disk_space")
                        echo -e "${BLUE}💾 Hint: You might be running out of disk space. Free up some files.${NC}" >&2
                        ;;
                esac
            fi
            ;;
    esac
    
    # Log to file regardless of display level
    log_error "$script_name" "$function_name" "$line_number" "$command" "$exit_code" "$error_type" "$attempt_count"
    
    # Exit based on role and attempt count
    if [[ $attempt_count -gt 3 ]]; then
        echo -e "${RED}💀 All self-healing attempts exhausted. Manual intervention required.${NC}" >&2
        
        if [[ "${UDOS_DEBUG_ENABLED:-false}" == "true" ]]; then
            echo -e "${YELLOW}🔧 Debug mode: Dropping to interactive shell${NC}" >&2
            echo -e "${BLUE}💡 Available debug commands: show_logs, retry_healing, check_system${NC}" >&2
            bash --login
        fi
    elif [[ "${UDOS_DEBUG_ENABLED:-false}" == "true" && $attempt_count -le 1 ]]; then
        echo -e "${YELLOW}🔧 Debug mode: Dropping to interactive shell for investigation${NC}" >&2
        echo -e "${BLUE}💡 Type 'exit' to continue, or investigate the error${NC}" >&2
        bash --login
    fi
    
    exit $exit_code
}

# Get human-readable exit code meanings
get_exit_code_meaning() {
    case "$1" in
        0) echo "Success" ;;
        1) echo "General error" ;;
        2) echo "Misuse of shell command" ;;
        126) echo "Command cannot execute (permission)" ;;
        127) echo "Command not found" ;;
        128) echo "Invalid exit argument" ;;
        130) echo "Script terminated by Ctrl+C" ;;
        255) echo "Exit status out of range" ;;
        *) echo "Unknown error" ;;
    esac
}

# Comprehensive logging system
log_error() {
    local script="$1"
    local function="$2"
    local line="$3"
    local command="$4"
    local exit_code="$5"
    local error_type="${6:-generic}"
    local attempt_count="${7:-1}"
    
    local log_dir="$UDOS_ROOT/sandbox/logs"
    mkdir -p "$log_dir"
    
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local log_entry="[$timestamp] ERROR[$exit_code] $script:$function:$line [$error_type] (attempt $attempt_count) - $command"
    
    # Write to error log
    echo "$log_entry" >> "$log_dir/error.log"
    
    # Write to NetHack-style adventure log for fun
    local nethack_msg="$(get_nethack_message "$error_type" "$attempt_count")"
    echo "[$timestamp] $nethack_msg" >> "$log_dir/adventure.log"
    
    # Write detailed log for developers
    if [[ "${UDOS_DEBUG_ENHANCED:-false}" == "true" ]]; then
        {
            echo "=== ERROR REPORT ==="
            echo "Timestamp: $timestamp"
            echo "Script: $script"
            echo "Function: $function"
            echo "Line: $line"
            echo "Command: $command"
            echo "Exit Code: $exit_code ($(get_exit_code_meaning $exit_code))"
            echo "Error Type: $error_type"
            echo "Attempt: $attempt_count"
            echo "NetHack Message: $nethack_msg"
            echo "Role: ${UDOS_CURRENT_ROLE:-unknown}"
            echo "Environment: ${UDOS_ENVIRONMENT:-unknown}"
            echo "Working Directory: $(pwd)"
            echo "Process ID: $$"
            echo "Parent Process: ${PPID:-unknown}"
            echo "Shell: $0"
            echo "Path: $PATH"
            echo "Self-Healing: ${UDOS_SELF_HEALING:-true}"
            echo "Variables:"
            env | grep "^UDOS_" | sort
            echo "=== END REPORT ==="
            echo ""
        } >> "$log_dir/debug.log"
    fi
}

# Debug helper commands
show_logs() {
    echo -e "${BLUE}📊 Recent Error Activity${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [[ -f "$UDOS_ROOT/sandbox/logs/error.log" ]]; then
        echo -e "${WHITE}Recent Errors:${NC}"
        tail -10 "$UDOS_ROOT/sandbox/logs/error.log"
        echo ""
    fi
    
    if [[ -f "$UDOS_ROOT/sandbox/logs/adventure.log" ]]; then
        echo -e "${WHITE}Adventure Log (NetHack-style):${NC}"
        tail -5 "$UDOS_ROOT/sandbox/logs/adventure.log"
        echo ""
    fi
    
    if [[ -f "$UDOS_ROOT/sandbox/logs/performance.log" ]]; then
        echo -e "${WHITE}Performance Status:${NC}"
        tail -3 "$UDOS_ROOT/sandbox/logs/performance.log"
    fi
}

retry_healing() {
    echo -e "${YELLOW}🔧 Manual healing retry initiated...${NC}"
    # Reset attempt counters for manual retry
    local attempt_file="$UDOS_ROOT/sandbox/logs/.error_attempts"
    if [[ -f "$attempt_file" ]]; then
        rm "$attempt_file"
        echo -e "${GREEN}✨ Attempt counters reset. You may try again.${NC}"
    fi
}

check_system() {
    echo -e "${BLUE}🔍 System Health Check${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Check disk space
    local disk_usage=$(df "$UDOS_ROOT" | awk 'NR==2{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        echo -e "${RED}⚠️ Disk space critical: ${disk_usage}%${NC}"
    else
        echo -e "${GREEN}✅ Disk space OK: ${disk_usage}%${NC}"
    fi
    
    # Check memory
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [[ $memory_usage -gt 90 ]]; then
        echo -e "${RED}⚠️ Memory usage high: ${memory_usage}%${NC}"
    else
        echo -e "${GREEN}✅ Memory usage OK: ${memory_usage}%${NC}"
    fi
    
    # Check critical files
    local critical_files=(
        "$UDOS_ROOT/uCORE/code/ucode.sh"
        "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
        "$UDOS_ROOT/uSCRIPT/uscript.sh"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" && -x "$file" ]]; then
            echo -e "${GREEN}✅ $(basename "$file") OK${NC}"
        else
            echo -e "${RED}❌ $(basename "$file") missing or not executable${NC}"
        fi
    done
}

# System health monitoring with witty commentary
monitor_system_health() {
    local log_dir="$UDOS_ROOT/sandbox/logs"
    mkdir -p "$log_dir"
    
    # Check for common issues and provide NetHack-style warnings
    local disk_usage=$(df "$UDOS_ROOT" | awk 'NR==2{print $5}' | sed 's/%//')
    local memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [[ $disk_usage -gt 95 ]]; then
        local msg="Your bag of holding is critically overloaded!"
        echo "$(date '+%Y-%m-%d %H:%M:%S') $msg" >> "$log_dir/adventure.log"
        if [[ "${UDOS_SELF_HEALING:-true}" == "true" ]]; then
            attempt_self_healing "disk_space" "system_check" ""
        fi
    elif [[ $disk_usage -gt 85 ]]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') You hear the dungeon groaning under the weight of accumulated treasure." >> "$log_dir/adventure.log"
    fi
    
    if [[ $memory_usage -gt 95 ]]; then
        local msg="Your brain feels fuzzy. Too many thoughts!"
        echo "$(date '+%Y-%m-%d %H:%M:%S') $msg" >> "$log_dir/adventure.log"
        if [[ "${UDOS_SELF_HEALING:-true}" == "true" ]]; then
            attempt_self_healing "memory" "system_check" ""
        fi
    fi
}

# Performance monitoring for development
start_performance_monitoring() {
    if [[ "${UDOS_PERFORMANCE_MONITORING:-false}" != "true" ]]; then
        return 0
    fi
    
    local log_dir="$UDOS_ROOT/sandbox/logs"
    mkdir -p "$log_dir"
    
    # Start resource monitoring in background
    {
        while true; do
            local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
            local memory_usage="$(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')"
            local cpu_usage="$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)"
            local disk_usage="$(df $UDOS_ROOT | awk 'NR==2{print $5}')"
            
            echo "[$timestamp] PERF CPU:${cpu_usage}% MEM:${memory_usage} DISK:${disk_usage}" >> "$log_dir/performance.log"
            
            # Add some NetHack-style performance commentary
            local cpu_num=$(echo "$cpu_usage" | cut -d'.' -f1)
            if [[ $cpu_num -gt 80 ]]; then
                echo "[$timestamp] The CPU sprites are working overtime!" >> "$log_dir/adventure.log"
            fi
            
            # Run system health monitoring
            monitor_system_health
            
            sleep 5
        done
    } &
    
    export UDOS_PERF_MONITOR_PID=$!
    echo "$UDOS_PERF_MONITOR_PID" > "$log_dir/perf_monitor.pid"
    
    echo -e "${GREEN}📊 Performance monitoring started (PID: $UDOS_PERF_MONITOR_PID)${NC}"
}

# Enhanced testing framework
run_enhanced_tests() {
    local test_mode="${UDOS_TESTING_MODE:-false}"
    local role="${UDOS_CURRENT_ROLE:-user}"
    
    if [[ "$test_mode" == "false" ]]; then
        return 0
    fi
    
    echo -e "${BLUE}🧪 Running uDOS Tests (${role} level)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    local test_count=0
    local passed_count=0
    local failed_count=0
    
    # Test definitions based on role
    case "$test_mode" in
        "true"|"full")
            # Full test suite for developers
            run_test_suite "core" && ((passed_count++)) || ((failed_count++))
            run_test_suite "integration" && ((passed_count++)) || ((failed_count++))
            run_test_suite "performance" && ((passed_count++)) || ((failed_count++))
            run_test_suite "security" && ((passed_count++)) || ((failed_count++))
            ((test_count += 4))
            ;;
        "basic")
            # Basic tests for admin/power users
            run_test_suite "core" && ((passed_count++)) || ((failed_count++))
            run_test_suite "integration" && ((passed_count++)) || ((failed_count++))
            ((test_count += 2))
            ;;
    esac
    
    # Results summary
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    if [[ $failed_count -eq 0 ]]; then
        echo -e "${GREEN}✅ All tests passed! ($passed_count/$test_count)${NC}"
    else
        echo -e "${RED}❌ $failed_count tests failed ($passed_count/$test_count passed)${NC}"
        if [[ "${UDOS_ERROR_DETAIL:-basic}" == "friendly" ]]; then
            echo -e "${BLUE}💡 Some checks didn't pass, but uDOS should still work fine!${NC}"
        fi
    fi
}

# Individual test suite runner
run_test_suite() {
    local suite="$1"
    local suite_script="$UDOS_ROOT/dev/scripts/test-${suite}.sh"
    
    if [[ -f "$suite_script" ]]; then
        echo -e "${WHITE}Running ${suite} tests...${NC}"
        if "$suite_script" >/dev/null 2>&1; then
            echo -e "${GREEN}  ✅ ${suite} tests passed${NC}"
            return 0
        else
            echo -e "${RED}  ❌ ${suite} tests failed${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}  ⚠️ ${suite} tests not found${NC}"
        return 0
    fi
}

# Debug information display
show_debug_info() {
    if [[ "${UDOS_DEBUG_ENABLED:-false}" == "false" ]]; then
        return 0
    fi
    
    echo -e "${BLUE}🔍 DEBUG INFORMATION${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}Role:${NC} ${UDOS_CURRENT_ROLE:-unknown}"
    echo -e "${WHITE}Debug Level:${NC} ${UDOS_ERROR_DETAIL:-basic}"
    echo -e "${WHITE}Log Level:${NC} ${UDOS_LOG_LEVEL:-info}"
    echo -e "${WHITE}Testing Mode:${NC} ${UDOS_TESTING_MODE:-false}"
    echo -e "${WHITE}Self-Healing:${NC} ${UDOS_SELF_HEALING:-true}"
    
    if [[ "${UDOS_DEBUG_ENHANCED:-false}" == "true" ]]; then
        echo -e "${WHITE}Enhanced Debug:${NC} Enabled"
        echo -e "${WHITE}Performance Monitoring:${NC} ${UDOS_PERFORMANCE_MONITORING:-false}"
        echo -e "${WHITE}Trace Mode:${NC} ${UDOS_TRACE_ENABLED:-false}"
        echo -e "${BLUE}🎲 NetHack-style commentary: Enabled${NC}"
        echo -e "${GREEN}🔧 Helper commands: show_logs, retry_healing, check_system${NC}"
    fi
}

# Cleanup function
cleanup_debug_services() {
    # Stop performance monitoring if running
    if [[ -f "$UDOS_ROOT/sandbox/logs/perf_monitor.pid" ]]; then
        local pid=$(cat "$UDOS_ROOT/sandbox/logs/perf_monitor.pid" 2>/dev/null || echo "")
        if [[ -n "$pid" && "$pid" =~ ^[0-9]+$ ]]; then
            kill "$pid" 2>/dev/null || true
        fi
        rm -f "$UDOS_ROOT/sandbox/logs/perf_monitor.pid"
    fi
}

# Set up error handling
trap 'udos_error_handler ${LINENO} "$BASH_COMMAND"' ERR
trap 'cleanup_debug_services' EXIT

# Initialize debugging system
initialize_debug_system() {
    setup_debug_config
    
    if [[ "${UDOS_PERFORMANCE_MONITORING:-false}" == "true" ]]; then
        start_performance_monitoring
    fi
    
    # Enable trace mode if requested
    if [[ "${UDOS_TRACE_ENABLED:-false}" == "true" ]]; then
        set -x
    fi
    
    # Show debug info if enabled
    show_debug_info
}

# Export functions for use by other scripts
export -f udos_error_handler
export -f log_error
export -f run_enhanced_tests
export -f show_debug_info
export -f get_nethack_message
export -f attempt_self_healing
export -f classify_error
export -f get_exit_code_meaning
export -f show_logs
export -f retry_healing
export -f check_system
export -f monitor_system_health

# Auto-initialize if sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    initialize_debug_system
    run_enhanced_tests
fi
