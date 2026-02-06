#!/usr/bin/env bash
#
# uDOS Startup Script
# Initializes system, runs setup story if needed, and launches interactive mode
#
# This script is typically run on first installation or after system reset.
# It ensures all system requirements are met and runs the setup story to configure
# the user profile and installation-specific settings.
#

set -e

# Determine uDOS home directory
UDOS_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_HOME

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $*${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $*${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $*${NC}"
}

log_error() {
    echo -e "${RED}❌ $*${NC}"
}

# Check Python environment
check_python() {
    log_info "Checking Python environment..."

    if [ -f "$UDOS_HOME/.venv/bin/python3" ]; then
        PYTHON="$UDOS_HOME/.venv/bin/python3"
        log_success "Found virtual environment at $UDOS_HOME/.venv"
    elif command -v python3 &> /dev/null; then
        PYTHON="python3"
        log_warning "Using system Python (no virtual environment)"
    else
        log_error "Python 3 not found. Please install Python 3.10+."
        exit 1
    fi

    export PYTHON
}

# Check core installation
check_core_install() {
    log_info "Checking Core installation..."

    if [ ! -d "$UDOS_HOME/core" ]; then
        log_error "Core not installed at $UDOS_HOME/core"
        exit 1
    fi

    if [ ! -f "$UDOS_HOME/uDOS.py" ]; then
        log_error "uDOS.py launcher not found at $UDOS_HOME/uDOS.py"
        exit 1
    fi

    log_success "Core installation verified"
}

# Initialize memory directories
init_memory_dirs() {
    log_info "Initializing memory directories..."

    mkdir -p "$UDOS_HOME/memory"/{story,system,logs,private}

    # Copy system seed files from memory/system if it exists
    if [ -d "$UDOS_HOME/memory/system" ]; then
        log_info "Copying system seed files..."
        cp -v "$UDOS_HOME/memory/system"/*.md "$UDOS_HOME/memory/story/" 2>/dev/null || true
    fi

    log_success "Memory directories initialized"
}

# Run setup story if needed
run_setup_if_needed() {
    log_info "Checking if setup is needed..."

    # Check if user profile exists
    if [ -f "$UDOS_HOME/memory/user/profile.json" ]; then
        log_success "User profile already exists, skipping setup"
        return 0
    fi

    log_info "First-time setup detected. Running setup story..."

    # Run the setup story
    "$PYTHON" "$UDOS_HOME/uDOS.py" STORY wizard-setup || {
        log_warning "Setup story failed or was cancelled"
        return 1
    }

    log_success "Setup completed successfully"
}

# Main startup sequence
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              uDOS Startup Script v1.0.0                    ║"
    echo "║         Offline-First Operating System for Survival        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    check_python
    check_core_install
    init_memory_dirs
    run_setup_if_needed

    log_success "Startup complete. Launching interactive mode..."
    echo ""

    # Launch interactive mode
    "$PYTHON" "$UDOS_HOME/uDOS.py"
}

# Run main
main "$@"
