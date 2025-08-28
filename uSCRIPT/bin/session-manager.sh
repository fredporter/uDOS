#!/bin/bash
# Session Manager - Handle isolated execution

# Generate session ID
generate_session_id() {
    date +"%Y%m%d%H%M%S" | md5sum | cut -c1-8
}

# Execute command in isolated session
execute_isolated() {
    local command="$1"
    shift
    local args="$@"
    local session_id="$(generate_session_id)"
    local log_file="$USCRIPT/runtime/sessions/${session_id}.log"
    
    log_info "Starting isolated session: $session_id"
    
    # Execute in background with logging
    (
        echo "Session: $session_id" > "$log_file"
        echo "Command: $command $args" >> "$log_file"
        echo "Started: $(date)" >> "$log_file"
        echo "───────────────────────────────────" >> "$log_file"
        
        # Execute the command
        "$USCRIPT/library/ucode/${command}.sh" $args >> "$log_file" 2>&1
        local exit_code=$?
        
        echo "───────────────────────────────────" >> "$log_file"
        echo "Finished: $(date)" >> "$log_file"
        echo "Exit Code: $exit_code" >> "$log_file"
        
        exit $exit_code
    ) &
    
    local pid=$!
    echo "$pid" > "$USCRIPT/runtime/sessions/${session_id}.pid"
    
    log_success "Session $session_id started (PID: $pid)"
    log_info "Log: $log_file"
}

# Main execution
case "${1:-}" in
    execute)
        shift
        execute_isolated "$@"
        ;;
    *)
        echo "Usage: $0 execute <command> [args...]"
        exit 1
        ;;
esac
