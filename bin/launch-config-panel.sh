#!/bin/bash

###############################################################################
#  🔐 Launch Secure Config Panel
#
#  Quick launcher for the Wizard Server config management UI
#
#  Usage:
#    ./bin/launch-config-panel.sh              # Launch with default settings
#    ./bin/launch-config-panel.sh --with-tui   # Also launch TUI alongside
#    ./bin/launch-config-panel.sh --test       # Run tests first
#
###############################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_ROOT/.venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
WITH_TUI=false
RUN_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --with-tui)
            WITH_TUI=true
            shift
            ;;
        --test)
            RUN_TESTS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./bin/launch-config-panel.sh [--with-tui] [--test]"
            exit 1
            ;;
    esac
done

###############################################################################
# Print Header
###############################################################################

echo ""
echo "███████████████████████████████████████████████████████████████"
echo "█"
echo "█  🔐 uDOS SECURE CONFIG PANEL"
echo "█"
echo "█  API Key & Credential Management"
echo "█"
echo "███████████████████████████████████████████████████████████████"
echo ""

###############################################################################
# Check Virtual Environment
###############################################################################

echo -e "${BLUE}📋 Checking environment...${NC}"

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${RED}❌ Virtual environment not found at: $VENV_PATH${NC}"
    echo ""
    echo "Create it with:"
    echo "  python3 -m venv $VENV_PATH"
    echo "  source $VENV_PATH/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

echo -e "${GREEN}✅ Virtual environment found${NC}"

###############################################################################
# Activate Virtual Environment
###############################################################################

echo "📦 Activating virtual environment..."
source "$VENV_PATH/bin/activate"

echo -e "${GREEN}✅ Virtual environment activated${NC}"

###############################################################################
# Check Dependencies
###############################################################################

echo "🔍 Checking dependencies..."

# Check FastAPI
if python -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✅ fastapi${NC}"
else
    echo -e "${RED}❌ fastapi not installed${NC}"
    echo "   Install with: pip install fastapi uvicorn"
    exit 1
fi

# Check cryptography
if python -c "from cryptography.fernet import Fernet" 2>/dev/null; then
    echo -e "${GREEN}✅ cryptography${NC}"
else
    echo -e "${YELLOW}⚠️  cryptography not installed (encryption unavailable)${NC}"
    echo "   Install with: pip install cryptography"
    # Don't exit - it's optional for testing
fi

###############################################################################
# Run Tests (Optional)
###############################################################################

if [ "$RUN_TESTS" = true ]; then
    echo ""
    echo -e "${BLUE}🧪 Running tests...${NC}"

    if python "$PROJECT_ROOT/test_secure_config_panel.py"; then
        echo -e "${GREEN}✅ Tests passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Some tests failed - continuing anyway${NC}"
    fi
fi

###############################################################################
# Display Configuration
###############################################################################

echo ""
echo -e "${BLUE}⚙️  Configuration${NC}"
echo "   Project Root: $PROJECT_ROOT"
echo "   Server: http://127.0.0.1:8765"
echo "   Config Panel: http://127.0.0.1:8765/api/v1/config/panel"
echo "   API Status: http://127.0.0.1:8765/api/v1/config/status"

###############################################################################
# Check Port
###############################################################################

if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8765 already in use${NC}"
    echo ""
    echo "Kill existing process with:"
    echo "  kill \$(lsof -ti:8765)"
    echo ""
    echo "Or use port manager:"
    echo "  ./bin/port-manager kill :8765"
    exit 1
fi

echo -e "${GREEN}✅ Port 8765 available${NC}"

###############################################################################
# Launch Wizard Server
###############################################################################

echo ""
echo -e "${BLUE}🚀 Launching Wizard Server...${NC}"
echo ""

if [ "$WITH_TUI" = true ]; then
    echo "Also launching TUI in parallel..."
    echo ""
    python "$PROJECT_ROOT/wizard/launch_wizard_dev.py"
else
    echo "Starting server (no TUI)..."
    echo ""
    python "$PROJECT_ROOT/wizard/launch_wizard_dev.py" --no-tui
fi
