#!/bin/bash
# uDOS v1.0.4.2 - Native Development Environment Manager
# Simple, lean, fast - foundational system design
# NO external dependencies - pure uDOS approach

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TOOLS_DIR="$UDOS_ROOT/uSCRIPT/tools"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

show_banner() {
    echo -e "${PURPLE}"
    echo "██╗   ██╗██████╗  ██████╗ ███████╗"
    echo "██║   ██║██╔══██╗██╔═══██╗██╔════╝"
    echo "██║   ██║██║  ██║██║   ██║███████╗"
    echo "██║   ██║██║  ██║██║   ██║╚════██║"
    echo "╚██████╔╝██████╔╝╚██████╔╝███████║"
    echo " ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${CYAN}Universal Device Operating System${NC}"
    echo -e "${GREEN}Native Development Environment${NC}"
    echo ""
}

# Check what we actually have vs what we need
check_native_capabilities() {
    log "Checking native system capabilities..."

    # Python (required for uDOS server)
    if command -v python3 >/dev/null 2>&1; then
        success "Python 3: $(python3 --version)"
        PYTHON_AVAILABLE=true
    else
        error "Python 3 not found - required for uDOS server"
        PYTHON_AVAILABLE=false
    fi

    # Check if we actually need Node.js for basic uDOS operation
    log "Analyzing Node.js requirement..."
    if [[ -f "$UDOS_ROOT/uNETWORK/server/server.py" ]]; then
        success "uDOS server is Python-based - Node.js not required for core functionality"
        NODE_REQUIRED=false
    else
        warn "Node.js may be needed for development features"
        NODE_REQUIRED=true
    fi

    # Rust (only needed if we're building Tauri)
    if [[ -d "$UDOS_ROOT/uNETWORK/display/udos-desktop" ]]; then
        log "Tauri project detected - Rust recommended for desktop app"
        if command -v rustc >/dev/null 2>&1; then
            success "Rust: $(rustc --version | cut -d' ' -f1-2)"
            RUST_AVAILABLE=true
        else
            warn "Rust not found - needed for Tauri desktop app compilation"
            RUST_AVAILABLE=false
        fi
    else
        success "No Tauri project - Rust not required"
        RUST_AVAILABLE=true  # Not needed
    fi
}

# Install only what we actually need, using system tools
install_minimal_requirements() {
    log "Installing minimal requirements using native methods..."

    # Python environment (already handled by uSCRIPT)
    if [[ -d "$UDOS_ROOT/uSCRIPT/venv/python" ]]; then
        success "Python virtual environment ready"
    else
        log "Setting up Python environment..."
        cd "$UDOS_ROOT/uSCRIPT" && ./setup-environment.sh
    fi

    # Setup Rust environment within uSCRIPT
    setup_rust_in_uscript

    # Only install Node.js if we're actually doing frontend development
    if [[ "$NODE_REQUIRED" == "true" ]] && ! command -v node >/dev/null 2>&1; then
        log "Node.js needed for frontend development..."
        install_nodejs_native
    fi
}

# Setup Rust within uSCRIPT environment
setup_rust_in_uscript() {
    log "Setting up Rust environment within uSCRIPT..."

    local RUST_ENV_DIR="$UDOS_ROOT/uSCRIPT/venv/rust"

    # Create Rust environment directory structure
    mkdir -p "$RUST_ENV_DIR"/{bin,env,cargo_home,rustup_home}

    # Check if Rust is already installed
    if [[ -f "$RUST_ENV_DIR/env/cargo-env" ]]; then
        success "Rust environment already exists in uSCRIPT"
        return 0
    fi

    # Install Rust with custom RUSTUP_HOME and CARGO_HOME
    if [[ -d "$UDOS_ROOT/uNETWORK/display/udos-desktop" ]] && [[ "$RUST_AVAILABLE" == "false" ]]; then
        log "Installing Rust for Tauri development into uSCRIPT environment..."

        # Set custom environment variables
        export RUSTUP_HOME="$RUST_ENV_DIR/rustup_home"
        export CARGO_HOME="$RUST_ENV_DIR/cargo_home"

        # Install Rust
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --no-modify-path -y

        # Create uSCRIPT-specific Rust environment file
        cat > "$RUST_ENV_DIR/env/cargo-env" << EOF
# uSCRIPT Rust Environment
export RUSTUP_HOME="$RUST_ENV_DIR/rustup_home"
export CARGO_HOME="$RUST_ENV_DIR/cargo_home"
export PATH="\$CARGO_HOME/bin:\$PATH"
EOF

        success "Rust installed in uSCRIPT environment"
    elif [[ "$RUST_AVAILABLE" == "true" ]]; then
        # Rust is already available system-wide, create symlinks
        log "Integrating existing Rust installation with uSCRIPT..."

        if [[ -f "$HOME/.cargo/env" ]]; then
            # Create uSCRIPT wrapper for existing Rust
            cat > "$RUST_ENV_DIR/env/cargo-env" << EOF
# uSCRIPT Rust Environment (System Integration)
source "\$HOME/.cargo/env"
EOF
            success "Integrated system Rust with uSCRIPT"
        fi
    fi
}

install_nodejs_native() {
    log "Installing Node.js using native system methods..."

    # Check if we're on macOS and try system installer first
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v xcode-select >/dev/null 2>&1; then
            # Use system installer
            log "Checking for system Node.js options..."
            # Alternative: download official installer
            warn "For native installation, download Node.js from: https://nodejs.org"
            warn "Or we can continue with web-based uDOS development only"
        fi
    fi
}

# Create multitasking rules for uDOS development
create_multitasking_rules() {
    log "Creating uDOS multitasking coordination rules..."

    mkdir -p "$UDOS_ROOT/uSCRIPT/runtime/locks"

    cat > "$UDOS_ROOT/uSCRIPT/runtime/process-manager.sh" << 'EOF'
#!/bin/bash
# uDOS Process Manager - Coordinate multiple development processes

LOCK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/locks"
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$LOCK_DIR"

# Process coordination
check_server_running() {
    if [[ -f "$LOCK_DIR/server.pid" ]] && kill -0 "$(cat "$LOCK_DIR/server.pid")" 2>/dev/null; then
        return 0
    fi
    return 1
}

start_server() {
    if check_server_running; then
        echo "uDOS server already running (PID: $(cat "$LOCK_DIR/server.pid"))"
        return 0
    fi

    echo "Starting uDOS server..."
    cd "$UDOS_ROOT/uNETWORK/server"
    python server.py &
    echo $! > "$LOCK_DIR/server.pid"
    echo "Server started (PID: $!)"
}

stop_server() {
    if [[ -f "$LOCK_DIR/server.pid" ]]; then
        local pid=$(cat "$LOCK_DIR/server.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "Stopped server (PID: $pid)"
        fi
        rm -f "$LOCK_DIR/server.pid"
    fi
}

status() {
    echo "uDOS Process Status:"
    if check_server_running; then
        echo "  🟢 Server: Running (PID: $(cat "$LOCK_DIR/server.pid"))"
    else
        echo "  🔴 Server: Not running"
    fi

    if pgrep -f "tauri dev" >/dev/null; then
        echo "  🟢 Tauri: Running"
    else
        echo "  🔴 Tauri: Not running"
    fi
}

case "$1" in
    start-server) start_server ;;
    stop-server) stop_server ;;
    status) status ;;
    *) echo "Usage: $0 {start-server|stop-server|status}" ;;
esac
EOF

    chmod +x "$UDOS_ROOT/uSCRIPT/runtime/process-manager.sh"
    success "Created process coordination system"
}

# Main setup
main() {
    show_banner

    log "uDOS Native Development Environment Setup"
    log "Simple • Lean • Fast • No External Dependencies"
    echo

    check_native_capabilities
    echo

    install_minimal_requirements
    echo

    create_multitasking_rules
    echo

    success "uDOS native development environment ready!"
    log "Available commands:"
    log "  $UDOS_ROOT/uSCRIPT/runtime/process-manager.sh status"
    log "  $UDOS_ROOT/uSCRIPT/runtime/process-manager.sh start-server"
    log "  $UDOS_ROOT/uSCRIPT/runtime/process-manager.sh stop-server"
    echo
    log "Core principle: Only install what you actually use"
    log "Web development: Python + uNETWORK server (no Node.js needed)"
    log "Desktop development: Add Rust for Tauri compilation"
    log "External tools: Only when specifically required"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
