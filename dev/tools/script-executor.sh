#!/bin/bash

# uDEV Script Executor v1.3
# Individual script runner with logging and error handling

set -euo pipefail

# Configuration
readonly UDEV_ROOT="/Users/agentdigital/uDOS/uDEV"
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
    
    # Log to file if specified
    if [[ -n "${SCRIPT_LOG:-}" ]]; then
        echo "[$timestamp] [$level] $message" >> "$SCRIPT_LOG"
    fi
}

# Generate log filename for script execution
generate_script_log() {
    local script_name="$1"
    local timestamp=$(date '+%Y%m%d-%H%M')
    local clean_name=$(echo "$script_name" | sed 's/[^a-zA-Z0-9]//g' | tr '[:lower:]' '[:upper:]' | head -c 6)
    echo "$LOGS_DIR/system/uLOG-$timestamp-$TIMEZONE_CODE-SC$clean_name.md"
}

# Execute script with full logging
execute_script() {
    local script_path="$1"
    local timeout_seconds="${2:-300}"
    local retry_count="${3:-1}"
    
    if [[ ! -f "$script_path" ]]; then
        log "ERROR" "Script not found: $script_path"
        return 1
    fi
    
    local script_name=$(basename "$script_path")
    SCRIPT_LOG=$(generate_script_log "$script_name")
    mkdir -p "$(dirname "$SCRIPT_LOG")"
    
    log "INFO" "Starting script execution: $script_name"
    
    # Initialize log file
    cat > "$SCRIPT_LOG" << EOF
# Script Execution Log

**Script**: $script_name  
**Path**: $script_path  
**Start Time**: $(date '+%Y-%m-%d %H:%M:%S')  
**Timeout**: ${timeout_seconds}s  
**Retry Count**: $retry_count  
**Status**: RUNNING  

## Execution Log

EOF
    
    local attempt=1
    local success=false
    
    while [[ $attempt -le $retry_count ]] && [[ "$success" == "false" ]]; do
        log "INFO" "Attempt $attempt of $retry_count"
        echo "### Attempt $attempt" >> "$SCRIPT_LOG"
        echo "**Time**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$SCRIPT_LOG"
        echo "" >> "$SCRIPT_LOG"
        
        local start_time=$(date +%s)
        local exit_code=0
        
        # Create temporary files for output
        local stdout_file=$(mktemp)
        local stderr_file=$(mktemp)
        
        # Execute script with timeout
        if timeout "$timeout_seconds" bash "$script_path" > "$stdout_file" 2> "$stderr_file"; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            
            log "SUCCESS" "Script completed successfully in ${duration}s"
            success=true
            
            # Append output to log
            echo "**Status**: ✅ SUCCESS" >> "$SCRIPT_LOG"
            echo "**Duration**: ${duration} seconds" >> "$SCRIPT_LOG"
            echo "**Exit Code**: 0" >> "$SCRIPT_LOG"
            echo "" >> "$SCRIPT_LOG"
            
            if [[ -s "$stdout_file" ]]; then
                echo "#### Standard Output" >> "$SCRIPT_LOG"
                echo '```' >> "$SCRIPT_LOG"
                cat "$stdout_file" >> "$SCRIPT_LOG"
                echo '```' >> "$SCRIPT_LOG"
                echo "" >> "$SCRIPT_LOG"
            fi
            
        else
            exit_code=$?
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            
            log "ERROR" "Script failed with exit code $exit_code (attempt $attempt)"
            
            # Append error to log
            echo "**Status**: ❌ FAILED" >> "$SCRIPT_LOG"
            echo "**Duration**: ${duration} seconds" >> "$SCRIPT_LOG"
            echo "**Exit Code**: $exit_code" >> "$SCRIPT_LOG"
            echo "" >> "$SCRIPT_LOG"
            
            if [[ -s "$stdout_file" ]]; then
                echo "#### Standard Output" >> "$SCRIPT_LOG"
                echo '```' >> "$SCRIPT_LOG"
                cat "$stdout_file" >> "$SCRIPT_LOG"
                echo '```' >> "$SCRIPT_LOG"
                echo "" >> "$SCRIPT_LOG"
            fi
            
            if [[ -s "$stderr_file" ]]; then
                echo "#### Standard Error" >> "$SCRIPT_LOG"
                echo '```' >> "$SCRIPT_LOG"
                cat "$stderr_file" >> "$SCRIPT_LOG"
                echo '```' >> "$SCRIPT_LOG"
                echo "" >> "$SCRIPT_LOG"
            fi
        fi
        
        # Cleanup temp files
        rm -f "$stdout_file" "$stderr_file"
        
        attempt=$((attempt + 1))
        
        # Wait before retry if not the last attempt
        if [[ $attempt -le $retry_count ]] && [[ "$success" == "false" ]]; then
            log "INFO" "Waiting 5 seconds before retry..."
            sleep 5
        fi
    done
    
    # Final log update
    local final_status
    if [[ "$success" == "true" ]]; then
        final_status="COMPLETED"
        echo -e "${GREEN}✅ Script execution successful: $script_name${NC}"
    else
        final_status="FAILED"
        echo -e "${RED}❌ Script execution failed: $script_name${NC}"
    fi
    
    # Update log header
    sed -i '' "s/RUNNING/$final_status/" "$SCRIPT_LOG"
    
    # Add final summary
    cat >> "$SCRIPT_LOG" << EOF

## Summary
- **Final Status**: $final_status
- **Total Attempts**: $((attempt - 1))
- **Log File**: $SCRIPT_LOG
- **Completed**: $(date '+%Y-%m-%d %H:%M:%S')

*Generated by uDEV Script Executor v1.3*
EOF
    
    if [[ "$success" == "true" ]]; then
        return 0
    else
        return 1
    fi
}

# Show help
show_help() {
    cat << 'EOF'
🔧 uDEV Script Executor v1.3

USAGE:
    script-executor.sh <script_path> [timeout] [retry_count]

PARAMETERS:
    script_path     Path to script file (required)
    timeout         Timeout in seconds (default: 300)
    retry_count     Number of retry attempts (default: 1)

EXAMPLES:
    ./script-executor.sh cleanup/cleanup-filenames.sh
    ./script-executor.sh maintenance/organize-files.sh 600 2
    ./script-executor.sh ../cleanup-filenames.sh 300 3

FEATURES:
    - Comprehensive logging with timestamps
    - Configurable timeout and retry logic
    - Automatic log file generation
    - Standard output and error capture
    - Color-coded status messages

LOG FILES:
    Generated in: uDEV/logs/system/
    Format: uLOG-YYYYMMDD-HHMM-TZ-SCNAME.md

EOF
}

# Main function
main() {
    if [[ $# -lt 1 ]] || [[ "$1" == "help" ]] || [[ "$1" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    local script_path="$1"
    local timeout_seconds="${2:-300}"
    local retry_count="${3:-1}"
    
    # Validate parameters
    if [[ ! "$timeout_seconds" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}❌ Invalid timeout: $timeout_seconds${NC}" >&2
        exit 1
    fi
    
    if [[ ! "$retry_count" =~ ^[0-9]+$ ]] || [[ $retry_count -lt 1 ]]; then
        echo -e "${RED}❌ Invalid retry count: $retry_count${NC}" >&2
        exit 1
    fi
    
    # Execute script
    execute_script "$script_path" "$timeout_seconds" "$retry_count"
}

# Run main with all arguments
main "$@"
