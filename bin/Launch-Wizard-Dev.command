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

# Spinner function for long-running tasks
run_with_spinner() {
    local message="$1"
    shift
    local cmd="$@"
    local spin_chars='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0

    eval "$cmd" &
    local pid=$!

    printf "  ${YELLOW}⠋${NC} %s" "$message"
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i + 1) % 10 ))
        printf "\r  ${YELLOW}${spin_chars:$i:1}${NC} %s" "$message"
        sleep 0.1
    done

    wait $pid
    local exit_code=$?
    printf "\r"
    return $exit_code
}

clear
print_service_urls "🧙 Wizard Server - Production Environment"

# Check venv - auto-create if missing
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    if run_with_spinner "Creating virtual environment..." "python3 -m venv $PROJECT_ROOT/.venv"; then
        echo -e "  ${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "  ${RED}❌ Failed to create virtual environment${NC}"
        exit 1
    fi
fi

source "$PROJECT_ROOT/.venv/bin/activate"
echo -e "${GREEN}✅ Python venv activated${NC}"

# Check dependencies - auto-install if missing
if ! python -c "import flask" 2>/dev/null; then
    if run_with_spinner "Installing dependencies (this may take a minute)..." "pip install -q -r $PROJECT_ROOT/requirements.txt"; then
        echo -e "  ${GREEN}✅ Dependencies installed${NC}"
    else
        echo -e "  ${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
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
