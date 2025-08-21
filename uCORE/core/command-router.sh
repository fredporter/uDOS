#!/bin/bash
# uDOS Command Router - Pure command interface
# Handles command parsing and routing to execution engines

# Route command to appropriate execution engine
route_command() {
    local command="$1"
    shift
    local args="$@"
    
    # Classify command execution requirements
    local runtime="$(classify_command_runtime "$command")"
    
    case "$runtime" in
        bash)
            execute_bash_command "$command" $args
            ;;
        python)
            execute_python_command "$command" $args
            ;;
        isolated)
            execute_isolated_command "$command" $args
            ;;
        *)
            log_error "Unknown runtime: $runtime"
            return 1
            ;;
    esac
}

# Classify command runtime requirements
classify_command_runtime() {
    local command="$1"
    
    case "$command" in
        # Pure bash commands (no venv needed)
        HELP|help|STATUS|status|TREE|tree|DISPLAY|display|LAYOUT|layout|ASCII|ascii)
            echo "bash"
            ;;
        # Python-dependent commands (venv required)  
        AI|ai|ANALYSIS|analysis|WEB|web|SERVER|server)
            echo "python"
            ;;
        # Isolated execution commands
        DESTROY|destroy|BACKUP|backup|MISSION|mission)
            echo "isolated"
            ;;
        # Default to bash for unknown commands
        *)
            echo "bash"
            ;;
    esac
}

# Execute bash-only command
execute_bash_command() {
    local command="$1"
    shift
    local args="$@"
    
    local script_path="$USCRIPT/library/ucode/${command}.sh"
    
    if [[ -f "$script_path" && -x "$script_path" ]]; then
        "$script_path" $args
    else
        log_error "Script not found: $command"
        return 1
    fi
}

# Execute Python command with virtual environment
execute_python_command() {
    local command="$1"
    shift  
    local args="$@"
    
    # Activate Python virtual environment
    source "$USCRIPT/bin/activate-venv.sh" python
    
    # Execute command
    execute_bash_command "$command" $args
}

# Execute command in isolated session
execute_isolated_command() {
    local command="$1"
    shift
    local args="$@"
    
    # Use session manager for isolation
    "$USCRIPT/bin/session-manager.sh" execute "$command" $args
}
