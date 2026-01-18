#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    Wizard Server Dev Launcher                             ║
# ║                  Production Server (port 8765)                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Get directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Source colors and helpers
source "$SCRIPT_DIR/udos-urls.sh"

# Colors (already sourced, but define for clarity)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

clear
print_service_urls "🧙 Wizard Server - Production Environment"

# Check venv
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Create it with: python -m venv .venv"
    exit 1
fi

source "$PROJECT_ROOT/.venv/bin/activate"
echo -e "${GREEN}✅ Python venv activated${NC}"

# Check dependencies (auto-repair)
echo -e "${CYAN}Checking dependencies...${NC}"
MISSING_DEPS=()

# Check FastAPI
if ! python -c "import fastapi" 2>/dev/null; then
    MISSING_DEPS+=("fastapi>=0.95.0")
fi

# Check uvicorn
if ! python -c "import uvicorn" 2>/dev/null; then
    MISSING_DEPS+=("uvicorn[standard]>=0.21.0")
fi

# Check pydantic
if ! python -c "import pydantic" 2>/dev/null; then
    MISSING_DEPS+=("pydantic>=2.0.0")
fi

# Check cryptography
if ! python -c "import cryptography" 2>/dev/null; then
    MISSING_DEPS+=("cryptography>=41.0.0")
fi

# Auto-install missing dependencies
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo -e "${CYAN}Installing...${NC}"
    pip install -q "${MISSING_DEPS[@]}" 2>&1 | grep -v "WARNING:" || true
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ All dependencies satisfied${NC}"
fi

# Set environment
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export UDOS_DEV_MODE=1

# Create log directory
mkdir -p "$PROJECT_ROOT/memory/logs"
echo -e "${GREEN}✅ Log directory ready${NC}"

echo ""
echo -e "${CYAN}${BOLD}Starting Wizard Server...${NC}"
echo ""

# Start Wizard Server
cd "$PROJECT_ROOT"

# Check if port 8765 is already in use
if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Port 8765 already in use, killing existing process...${NC}"
    bin/port-manager kill :8765 2>/dev/null || lsof -ti:8765 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Launch Wizard Server
python -m wizard.server 2>&1

# Cleanup on exit
trap "echo -e '${YELLOW}Shutting down Wizard Server...${NC}'" EXIT
