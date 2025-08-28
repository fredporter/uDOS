#!/bin/bash
# uSCRIPT v1.3.3 Environment Setup
# Sets up Python virtual environment and dependencies with self-healing

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$SCRIPT_DIR/venv/python"
CONFIG_DIR="$SCRIPT_DIR/config"

# Self-healing integration
DEPENDENCY_HEALER="$UDOS_ROOT/uCORE/code/self-healing/dependency-healer.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check Python availability with self-healing
check_python() {
    log "Checking Python installation..."

    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        success "Python 3 found: $python_version"
        return 0
    else
        warn "Python 3 not found - attempting self-healing..."
        
        # Try self-healing if available
        if [[ -f "$DEPENDENCY_HEALER" ]]; then
            echo -e "${CYAN}🎲 Invoking self-healing magic...${NC}"
            if "$DEPENDENCY_HEALER" heal python; then
                success "Python successfully healed!"
                return 0
            fi
        fi
        
        error "Python 3 not found and self-healing failed."
        echo -e "${YELLOW}Please install Python 3.8+ manually:${NC}"
        echo -e "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
        echo -e "  macOS: brew install python3"
        echo -e "  Or download from: https://python.org/downloads/"
        return 1
    fi
}

# Setup virtual environment with self-healing
setup_venv() {
    log "Setting up Python virtual environment..."

    if [[ -d "$VENV_DIR" ]]; then
        warn "Virtual environment already exists at $VENV_DIR"
        log "Checking if it's valid..."

        # Test if venv is working
        if [[ -f "$VENV_DIR/bin/python" ]] && "$VENV_DIR/bin/python" --version >/dev/null 2>&1; then
            success "Existing virtual environment is valid"
            return 0
        else
            warn "Existing venv appears corrupted, attempting self-healing..."
            
            # Try self-healing if available
            if [[ -f "$DEPENDENCY_HEALER" ]]; then
                echo -e "${CYAN}🎲 Invoking virtual environment healing magic...${NC}"
                if "$DEPENDENCY_HEALER" python; then
                    success "Virtual environment successfully healed!"
                    return 0
                fi
            fi
            
            # Manual recreation as fallback
            warn "Self-healing failed, manually recreating..."
            rm -rf "$VENV_DIR"
        fi
    fi

    # Create virtual environment
    mkdir -p "$(dirname "$VENV_DIR")"
    
    # Check for python3-venv on Debian/Ubuntu
    if [[ "$(uname)" == "Linux" ]] && command -v apt >/dev/null 2>&1; then
        if ! dpkg -l python3-venv >/dev/null 2>&1; then
            log "Installing python3-venv package..."
            if ! sudo apt install -y python3-venv; then
                error "Failed to install python3-venv. Please run: sudo apt install python3-venv"
                return 1
            fi
        fi
    fi
    
    if python3 -m venv "$VENV_DIR"; then
        success "Virtual environment created at $VENV_DIR"
    else
        error "Failed to create virtual environment"
        
        # Try self-healing as last resort
        if [[ -f "$DEPENDENCY_HEALER" ]]; then
            warn "Attempting final self-healing attempt..."
            if "$DEPENDENCY_HEALER" python; then
                success "Virtual environment healed successfully!"
                return 0
            fi
        fi
        
        return 1
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing Python dependencies..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip first
    pip install --upgrade pip

    # Install requirements
    if [[ -f "$CONFIG_DIR/requirements.txt" ]]; then
        log "Installing from requirements.txt..."
        pip install -r "$CONFIG_DIR/requirements.txt"
        success "Dependencies installed successfully"
    else
        warn "No requirements.txt found, installing basic packages..."
        pip install pyyaml requests click
        success "Basic dependencies installed"
    fi

    # Deactivate virtual environment
    deactivate
}

# Setup Node.js environment
setup_nodejs() {
    log "Setting up Node.js environment..."

    # Check if Node.js is already available
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version 2>/dev/null)
        success "Node.js found: $node_version"
        return 0
    fi

    # Check if we're on macOS and have Homebrew
    if [[ "$OSTYPE" == "darwin"* ]] && command -v brew >/dev/null 2>&1; then
        log "Installing Node.js via Homebrew..."
        if brew install node; then
            success "Node.js installed via Homebrew"
            local node_version=$(node --version 2>/dev/null)
            local npm_version=$(npm --version 2>/dev/null)
            success "Node.js: $node_version, npm: $npm_version"
            return 0
        else
            warn "Failed to install Node.js via Homebrew"
        fi
    fi

    # Check for system package manager or manual installation
    warn "Node.js not found. Please install Node.js manually:"
    warn "  macOS: brew install node"
    warn "  Linux: apt install nodejs npm (or equivalent)"
    warn "  Manual: https://nodejs.org/en/download/"
    return 1
}

# Verify installation
verify_installation() {
    log "Verifying installation..."

    source "$VENV_DIR/bin/activate"

    # Check key packages
    local packages=("yaml" "requests" "click")
    local failed=0

    for package in "${packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            success "Package '$package' is available"
        else
            error "Package '$package' is missing"
            ((failed++))
        fi
    done

    deactivate

    # Check Node.js if available
    if command -v node >/dev/null 2>&1; then
        success "Node.js: $(node --version)"
        success "npm: $(npm --version)"
    else
        warn "Node.js not available - install manually if needed for Tauri development"
    fi

    if [[ $failed -eq 0 ]]; then
        success "All core packages verified successfully"
        return 0
    else
        error "$failed packages are missing"
        return 1
    fi
}

# Create activation helper
create_helpers() {
    log "Creating helper scripts..."

    # Create activation script
    cat > "$SCRIPT_DIR/activate-venv.sh" << 'EOF'
#!/bin/bash
# Activate uSCRIPT Python virtual environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/python/bin/activate"
echo "uSCRIPT Python virtual environment activated"
echo "Use 'deactivate' to exit"
EOF

    chmod +x "$SCRIPT_DIR/activate-venv.sh"
    success "Created activate-venv.sh helper"

    # Create environment info script
    cat > "$SCRIPT_DIR/venv-info.sh" << 'EOF'
#!/bin/bash
# Display uSCRIPT environment information
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv/python"

echo "uSCRIPT v1.3.3 Environment Information"
echo "======================================"
echo "Virtual Environment: $VENV_DIR"
echo "Python Version: $(source "$VENV_DIR/bin/activate" && python --version)"
echo "Pip Version: $(source "$VENV_DIR/bin/activate" && pip --version)"
echo ""
echo "Installed Packages:"
source "$VENV_DIR/bin/activate"
pip list --format=columns
deactivate
EOF

    chmod +x "$SCRIPT_DIR/venv-info.sh"
    success "Created venv-info.sh helper"
}

# Main setup function
main() {
    echo -e "${BLUE}╭─ uSCRIPT v1.3.3 Environment Setup ──────────────────╮${NC}"
    echo -e "${BLUE}│ Setting up Python virtual environment and dependencies │${NC}"
    echo -e "${BLUE}╰────────────────────────────────────────────────────╯${NC}"
    echo

    # Run setup steps
    check_python || exit 1
    echo

    setup_venv || exit 1
    echo

    install_dependencies || exit 1
    echo

    setup_nodejs
    echo

    verify_installation || exit 1
    echo

    create_helpers
    echo

    success "uSCRIPT v1.3.3 environment setup complete!"
    log "Helper scripts created:"
    log "  ./activate-venv.sh  - Activate virtual environment"
    log "  ./venv-info.sh      - Show environment information"

    echo
    echo -e "${GREEN}To activate the virtual environment:${NC}"
    echo -e "  ${YELLOW}source ./activate-venv.sh${NC}"
    echo
    echo -e "${GREEN}To run uSCRIPT:${NC}"
    echo -e "  ${YELLOW}./uscript.sh help${NC}"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
