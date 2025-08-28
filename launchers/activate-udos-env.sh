#!/bin/bash
# uDOS Environment Activator
# Always activates the Python venv for the current shell session
# Usage: source ./activate-udos-env.sh
# Location: root/activate-udos-env.sh

# Get uDOS root
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USCRIPT_VENV="$UDOS_ROOT/uSCRIPT/venv/python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 uDOS Environment Activator${NC}"

# Check if already activated
if [ -n "${VIRTUAL_ENV:-}" ] && [ "${VIRTUAL_ENV}" = "$USCRIPT_VENV" ]; then
    echo -e "${GREEN}✅ uDOS Python venv already active${NC}"
    echo -e "${BLUE}📍 Virtual Env: $VIRTUAL_ENV${NC}"
    echo -e "${BLUE}🐍 Python: $(which python)${NC}"
    return 0 2>/dev/null || exit 0
fi

# Check if venv exists
if [ ! -f "$USCRIPT_VENV/bin/activate" ]; then
    echo -e "${RED}❌ uDOS Python venv not found!${NC}"
    echo -e "${YELLOW}📍 Expected: $USCRIPT_VENV${NC}"
    echo -e "${YELLOW}🔧 Run: cd uSCRIPT && ./setup-environment.sh${NC}"
    return 1 2>/dev/null || exit 1
fi

# Activate the virtual environment
echo -e "${GREEN}🚀 Activating uDOS Python virtual environment...${NC}"
source "$USCRIPT_VENV/bin/activate"

# Verify activation
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo -e "${GREEN}✅ Virtual environment activated successfully${NC}"
    echo -e "${BLUE}📍 Virtual Env: $VIRTUAL_ENV${NC}"
    echo -e "${BLUE}🐍 Python: $(which python)${NC}"
    echo -e "${BLUE}📦 Version: $(python --version)${NC}"

    # Set uDOS environment variables
    export UDOS_PYTHON_VENV_ACTIVE=true
    export UDOS_ROOT="$UDOS_ROOT"

    # Check packages
    echo -e "${BLUE}🔍 Checking key packages...${NC}"
    if python -c "import flask, flask_socketio" 2>/dev/null; then
        echo -e "${GREEN}✅ Flask and SocketIO available${NC}"
    else
        echo -e "${YELLOW}⚠️  Some packages may be missing${NC}"
    fi

    echo -e "${GREEN}🎯 uDOS Python environment ready!${NC}"
else
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    return 1 2>/dev/null || exit 1
fi
