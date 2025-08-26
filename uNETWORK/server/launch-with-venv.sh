#!/bin/bash
# uNETWORK Server Launcher with Guaranteed venv Usage
# Location: uNETWORK/server/launch-with-venv.sh

set -euo pipefail

# Get uDOS root
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
USCRIPT_VENV="$UDOS_ROOT/uSCRIPT/venv/python"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔧 uNETWORK Server Launcher${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if venv exists
if [ ! -f "$USCRIPT_VENV/bin/activate" ]; then
    echo -e "${RED}❌ uSCRIPT virtual environment not found!${NC}"
    echo -e "${YELLOW}📍 Expected: $USCRIPT_VENV${NC}"
    echo ""
    echo -e "${BLUE}🔧 Setting up virtual environment...${NC}"

    # Try to setup the environment
    if [ -f "$UDOS_ROOT/uSCRIPT/setup-environment.sh" ]; then
        cd "$UDOS_ROOT/uSCRIPT"
        ./setup-environment.sh
    else
        echo -e "${RED}❌ Setup script not found. Please run:${NC}"
        echo "   cd $UDOS_ROOT/uSCRIPT && ./setup-environment.sh"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "${GREEN}✅ Activating uSCRIPT virtual environment${NC}"
source "$USCRIPT_VENV/bin/activate"

# Verify activation
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo -e "${GREEN}✅ Virtual environment active: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# Check Python and dependencies
echo -e "${BLUE}📍 Python: $(which python)${NC}"
echo -e "${BLUE}📦 Version: $(python --version)${NC}"

# Check required packages
echo -e "${BLUE}🔍 Checking required packages...${NC}"
python -c "import flask, flask_socketio; print('✅ Flask and SocketIO available')" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Installing missing packages...${NC}"
    pip install flask flask-socketio
}

# Change to server directory
cd "$UDOS_ROOT/uNETWORK/server"

# Set environment variables
export UDOS_ROOT="$UDOS_ROOT"
export USERVER_PORT="${USERVER_PORT:-8080}"
export USERVER_HOST="${USERVER_HOST:-127.0.0.1}"
export UDOS_CURRENT_ROLE="${UDOS_CURRENT_ROLE:-wizard}"
export UDOS_SERVER_MODE="integrated"
export FLASK_ENV="development"

echo ""
echo -e "${GREEN}🚀 Starting uNETWORK server with venv...${NC}"
echo -e "${BLUE}🌐 URL: http://$USERVER_HOST:$USERVER_PORT${NC}"
echo ""

# Start the server
exec python server.py "$@"
