#!/bin/bash
# uDOS Python Environment Manager
# Ensures all Python-based uDOS services use the virtual environment
# Location: uSCRIPT/activate-udos-python.sh

set -euo pipefail

# Get uDOS root and venv path
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USCRIPT_VENV="$UDOS_ROOT/uSCRIPT/venv/python"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to check and activate venv
activate_udos_venv() {
    if [ -f "$USCRIPT_VENV/bin/activate" ]; then
        echo -e "${GREEN}✅ Activating uDOS Python venv${NC}" >&2
        source "$USCRIPT_VENV/bin/activate"
        export UDOS_PYTHON_VENV_ACTIVE=true
        return 0
    else
        echo -e "${RED}❌ uDOS Python venv not found at: $USCRIPT_VENV${NC}" >&2
        echo -e "${YELLOW}🔧 Run: cd $UDOS_ROOT/uSCRIPT && ./setup-environment.sh${NC}" >&2
        return 1
    fi
}

# Function to run Python with venv
run_python_with_venv() {
    if activate_udos_venv; then
        python "$@"
    else
        echo -e "${RED}❌ Cannot run Python without venv${NC}" >&2
        exit 1
    fi
}

# Function to check if venv is active
check_venv_active() {
    if [ -n "${VIRTUAL_ENV:-}" ] && [ "${UDOS_PYTHON_VENV_ACTIVE:-false}" = "true" ]; then
        return 0
    else
        return 1
    fi
}

# Function to verify required packages
verify_packages() {
    echo -e "${BLUE}🔍 Verifying Python packages...${NC}" >&2

    local required_packages=("flask" "flask_socketio" "jinja2" "werkzeug")
    local missing_packages=()

    for package in "${required_packages[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done

    if [ ${#missing_packages[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All required packages available${NC}" >&2
        return 0
    else
        echo -e "${RED}❌ Missing packages: ${missing_packages[*]}${NC}" >&2
        echo -e "${YELLOW}🔧 Run: cd $UDOS_ROOT/uSCRIPT && ./setup-environment.sh${NC}" >&2
        return 1
    fi
}

# Show environment info
show_env_info() {
    echo -e "${BLUE}📍 uDOS Python Environment Info${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if check_venv_active; then
        echo -e "Virtual Env: ${GREEN}✅ Active${NC}"
        echo -e "Path: $VIRTUAL_ENV"
        echo -e "Python: $(which python)"
        echo -e "Version: $(python --version)"

        if verify_packages; then
            echo -e "Packages: ${GREEN}✅ Complete${NC}"
        else
            echo -e "Packages: ${RED}❌ Missing${NC}"
        fi
    else
        echo -e "Virtual Env: ${RED}❌ Not Active${NC}"
        echo -e "System Python: $(which python3 2>/dev/null || echo 'Not found')"
    fi
}

# Export functions for sourcing
export -f activate_udos_venv
export -f run_python_with_venv
export -f check_venv_active
export -f verify_packages
export -f show_env_info

# Main execution
case "${1:-activate}" in
    activate)
        activate_udos_venv
        ;;
    check)
        if check_venv_active; then
            echo -e "${GREEN}✅ uDOS Python venv is active${NC}"
            verify_packages
        else
            echo -e "${RED}❌ uDOS Python venv is not active${NC}"
            exit 1
        fi
        ;;
    info)
        show_env_info
        ;;
    run)
        shift
        run_python_with_venv "$@"
        ;;
    verify)
        activate_udos_venv && verify_packages
        ;;
    *)
        echo "uDOS Python Environment Manager"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  activate   - Activate the uDOS Python virtual environment"
        echo "  check      - Check if venv is active and packages available"
        echo "  info       - Show environment information"
        echo "  run <cmd>  - Run Python command with venv"
        echo "  verify     - Activate venv and verify packages"
        echo ""
        echo "Examples:"
        echo "  source $0 activate     # Activate in current shell"
        echo "  $0 run script.py       # Run Python script with venv"
        echo "  $0 check               # Check current status"
        ;;
esac
