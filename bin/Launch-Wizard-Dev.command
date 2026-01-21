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
