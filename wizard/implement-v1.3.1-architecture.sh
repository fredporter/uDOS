#!/bin/bash
# uDOS v1.3.1 Architecture Implementation Script
# Phase 1: Script Consolidation & Separation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UCORE="$UDOS_ROOT/uCORE"
USCRIPT="$UDOS_ROOT/uSCRIPT"

log_info "uDOS v1.3.1 Architecture Implementation"
log_info "Root: $UDOS_ROOT"

# ═══════════════════════════════════════════════════════════════════════
# PHASE 1: DIRECTORY STRUCTURE PREPARATION
# ═══════════════════════════════════════════════════════════════════════

create_directory_structure() {
    log_info "Creating new directory structure..."
    
    # uCORE reorganization
    mkdir -p "$UCORE/bin"
    mkdir -p "$UCORE/core"
    mkdir -p "$UCORE/compat/legacy"
    mkdir -p "$UCORE/compat/minimal"
    mkdir -p "$UCORE/compat/portable"
    
    # uSCRIPT enhancement
    mkdir -p "$USCRIPT/bin"
    mkdir -p "$USCRIPT/library/core"
    mkdir -p "$USCRIPT/library/automation"
    mkdir -p "$USCRIPT/library/python"
    mkdir -p "$USCRIPT/library/extensions"
    mkdir -p "$USCRIPT/venv"
    mkdir -p "$USCRIPT/runtime/sessions"
    mkdir -p "$USCRIPT/runtime/background"
    mkdir -p "$USCRIPT/runtime/isolation"
    mkdir -p "$USCRIPT/config"
    
    log_success "Directory structure created"
}

# ═══════════════════════════════════════════════════════════════════════
# PHASE 2: SCRIPT CLASSIFICATION AND MOVEMENT
# ═══════════════════════════════════════════════════════════════════════

classify_and_move_scripts() {
    log_info "Classifying and moving scripts..."
    
    # Command Interface Scripts (stay in uCORE, refactor)
    log_info "Processing command interface scripts..."
    
    # Create new command router (extract from ucode.sh)
    cat > "$UCORE/core/command-router.sh" << 'EOF'
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
EOF
    
    chmod +x "$UCORE/core/command-router.sh"
    
    # Create environment detection
    cat > "$UCORE/core/environment.sh" << 'EOF'
#!/bin/bash
# Environment Detection and Setup

# Detect system capabilities
detect_environment() {
    # Platform detection
    case "$(uname -s)" in
        Darwin) export UDOS_PLATFORM="macos" ;;
        Linux)  export UDOS_PLATFORM="linux" ;;
        CYGWIN*|MINGW*) export UDOS_PLATFORM="windows" ;;
        *) export UDOS_PLATFORM="unknown" ;;
    esac
    
    # Architecture detection
    export UDOS_ARCH="$(uname -m)"
    
    # Bash version compatibility
    local bash_version="${BASH_VERSION%%.*}"
    if [[ "$bash_version" -lt 4 ]]; then
        export UDOS_COMPAT_MODE="bash3"
        log_warning "Bash 3.x detected - using compatibility mode"
    else
        export UDOS_COMPAT_MODE="modern"
    fi
    
    # Python availability
    if command -v python3 >/dev/null 2>&1; then
        export UDOS_PYTHON_AVAILABLE="true"
        export UDOS_PYTHON_VERSION="$(python3 --version 2>&1 | cut -d' ' -f2)"
    else
        export UDOS_PYTHON_AVAILABLE="false"
        log_warning "Python 3 not available - some features will be limited"
    fi
    
    log_info "Environment: $UDOS_PLATFORM/$UDOS_ARCH, Bash: $UDOS_COMPAT_MODE, Python: $UDOS_PYTHON_AVAILABLE"
}

# Setup environment variables
setup_environment() {
    # Core paths
    export UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    export UCORE="$UDOS_ROOT/uCORE"
    export USCRIPT="$UDOS_ROOT/uSCRIPT"
    export UMEMORY="$UDOS_ROOT/uMEMORY"
    
    # Version
    export UDOS_VERSION="v1.3.1"
    
    # Mode
    export UDOS_MODE="${UDOS_MODE:-COMMAND}"
    
    # Detect environment
    detect_environment
}
EOF
    
    chmod +x "$UCORE/core/environment.sh"
    
    # Execution Scripts (move to uSCRIPT/library/core)
    log_info "Moving execution scripts to uSCRIPT..."
    
    # Move and rename core execution scripts
    if [[ -f "$UCORE/code/backup-restore.sh" ]]; then
        cp "$UCORE/code/backup-restore.sh" "$USCRIPT/library/core/backup-system.sh"
        chmod +x "$USCRIPT/library/core/backup-system.sh"
    fi
    
    if [[ -f "$UCORE/code/session-logger.sh" ]]; then
        cp "$UCORE/code/session-logger.sh" "$USCRIPT/library/core/session-manager.sh"
        chmod +x "$USCRIPT/library/core/session-manager.sh"
    fi
    
    if [[ -f "$UCORE/code/user-auth.sh" ]]; then
        cp "$UCORE/code/user-auth.sh" "$USCRIPT/library/core/user-authentication.sh"
        chmod +x "$USCRIPT/library/core/user-authentication.sh"
    fi
    
    log_success "Scripts classified and moved"
}

# ═══════════════════════════════════════════════════════════════════════
# PHASE 3: VIRTUAL ENVIRONMENT SETUP
# ═══════════════════════════════════════════════════════════════════════

setup_virtual_environment() {
    log_info "Setting up virtual environment..."
    
    # Create Python requirements file
    cat > "$USCRIPT/config/requirements.txt" << 'EOF'
# uDOS Python Dependencies
# Core functionality
pyyaml>=6.0
requests>=2.28.0
click>=8.0.0

# Optional: Web server components
flask>=2.2.0
gunicorn>=20.1.0

# Optional: AI/ML components (commented out for minimal installation)
# openai>=1.0.0
# anthropic>=0.8.0
# numpy>=1.24.0
# pandas>=2.0.0
EOF

    # Create virtual environment activation script
    cat > "$USCRIPT/bin/activate-venv.sh" << 'EOF'
#!/bin/bash
# Virtual Environment Activation Manager

activate_venv() {
    local language="${1:-python}"
    local venv_path="$USCRIPT/venv/$language"
    
    case "$language" in
        python)
            if [[ ! -d "$venv_path" ]]; then
                log_info "Creating Python virtual environment..."
                python3 -m venv "$venv_path"
                source "$venv_path/bin/activate"
                pip install --upgrade pip
                pip install -r "$USCRIPT/config/requirements.txt"
                log_success "Python virtual environment created"
            else
                source "$venv_path/bin/activate"
                log_info "Python virtual environment activated"
            fi
            ;;
        *)
            log_warning "No virtual environment configuration for: $language"
            ;;
    esac
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    activate_venv "$@"
fi
EOF
    
    chmod +x "$USCRIPT/bin/activate-venv.sh"
    
    # Create session manager for isolation
    cat > "$USCRIPT/bin/session-manager.sh" << 'EOF'
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
EOF
    
    chmod +x "$USCRIPT/bin/session-manager.sh"
    
    log_success "Virtual environment setup complete"
}

# ═══════════════════════════════════════════════════════════════════════
# PHASE 4: CREATE NEW MAIN COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

create_new_ucode() {
    log_info "Creating new ucode command interface..."
    
    cat > "$UCORE/bin/ucode" << 'EOF'
#!/bin/bash
# uDOS v1.3.1 - Pure Command Interface
# Routes commands to appropriate execution engines

set -euo pipefail

# Load core components
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../core/environment.sh"
source "$SCRIPT_DIR/../core/command-router.sh"

# Colors and logging
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Initialize environment
setup_environment

# Main command processing
main() {
    local command="${1:-HELP}"
    shift || true
    local args="$@"
    
    # Show header for interactive commands
    if [[ "$command" != "help" && "$command" != "HELP" ]]; then
        log_info "uDOS $UDOS_VERSION - $command"
    fi
    
    # Route command to appropriate handler
    route_command "$command" $args
}

# Execute main function
main "$@"
EOF
    
    chmod +x "$UCORE/bin/ucode"
    
    # Create symbolic link for backward compatibility
    if [[ ! -L "$UCORE/code/ucode.sh" ]]; then
        ln -sf "../bin/ucode" "$UCORE/code/ucode.sh"
    fi
    
    log_success "New ucode command interface created"
}

# ═══════════════════════════════════════════════════════════════════════
# PHASE 5: CREATE MINIMAL INSTALLATION
# ═══════════════════════════════════════════════════════════════════════

create_minimal_installation() {
    log_info "Creating minimal installation..."
    
    mkdir -p "$UCORE/compat/minimal"
    
    cat > "$UCORE/compat/minimal/ucode-minimal" << 'EOF'
#!/bin/bash
# uDOS Minimal - Single-file bash-only installation
# Compatible with Bash 3.2+ and basic UNIX tools

set -euo pipefail

# Configuration
UDOS_VERSION="v1.3.1-minimal"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors (if supported)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    BLUE=''
    YELLOW=''
    NC=''
fi

# Logging
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Basic commands implemented in pure bash
cmd_help() {
    cat << 'HELP_EOF'
uDOS Minimal v1.3.1 - Bash-Only Installation

Available Commands:
  help      Show this help
  status    Show system status
  version   Show version information
  env       Show environment information

This is a minimal installation with basic functionality only.
For full features, install the standard uDOS distribution.
HELP_EOF
}

cmd_status() {
    log_info "uDOS Minimal Status"
    echo "Version: $UDOS_VERSION"
    echo "Platform: $(uname -s)/$(uname -m)"
    echo "Bash: $BASH_VERSION"
    echo "Directory: $SCRIPT_DIR"
    echo "Uptime: $(uptime 2>/dev/null || echo "N/A")"
}

cmd_version() {
    echo "$UDOS_VERSION"
}

cmd_env() {
    log_info "Environment Information"
    echo "SHELL: ${SHELL:-unknown}"
    echo "PATH: $PATH"
    echo "PWD: $PWD"
    echo "USER: ${USER:-unknown}"
    echo "HOME: ${HOME:-unknown}"
}

# Main command processing
main() {
    local command="${1:-help}"
    
    case "$command" in
        help|HELP|--help|-h)
            cmd_help
            ;;
        status|STATUS)
            cmd_status
            ;;
        version|VERSION|--version|-v)
            cmd_version
            ;;
        env|ENV|environment)
            cmd_env
            ;;
        *)
            log_error "Unknown command: $command"
            echo "Use 'help' to see available commands."
            exit 1
            ;;
    esac
}

# Execute
main "$@"
EOF
    
    chmod +x "$UCORE/compat/minimal/ucode-minimal"
    
    log_success "Minimal installation created"
}

# ═══════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════

main() {
    log_info "Starting uDOS v1.3.1 Architecture Implementation"
    
    create_directory_structure
    classify_and_move_scripts
    setup_virtual_environment
    create_new_ucode
    create_minimal_installation
    
    log_success "Phase 1 implementation complete!"
    log_info "Next steps:"
    echo "  1. Test new command interface: $UCORE/bin/ucode HELP"
    echo "  2. Test minimal installation: $UCORE/compat/minimal/ucode-minimal help"
    echo "  3. Validate virtual environment: $USCRIPT/bin/activate-venv.sh python"
    echo "  4. Review logs and adjust as needed"
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
