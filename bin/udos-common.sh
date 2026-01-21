#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    uDOS Common Shell Helpers                              ║
# ║              Shared by all launcher scripts                               ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# Source this at the top of any launcher:
#   source "$(dirname "$0")/udos-common.sh"

# ═══════════════════════════════════════════════════════════════════════════
# Colors and Formatting
# ═══════════════════════════════════════════════════════════════════════════
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
DIM='\033[2m'
NC='\033[0m'
BOLD='\033[1m'

# Box drawing characters
H_LINE="━"
V_LINE="┃"
TL="┏"
TR="┓"
BL="┗"
BR="┛"

# ═══════════════════════════════════════════════════════════════════════════
# Path Detection (works regardless of where uDOS is installed)
# ═══════════════════════════════════════════════════════════════════════════
UDOS_BIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UDOS_ROOT="$(dirname "$UDOS_BIN_DIR")"

# ═══════════════════════════════════════════════════════════════════════════
# Spinner Function
# ═══════════════════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════════════════
# Python Environment Setup
# ═══════════════════════════════════════════════════════════════════════════
ensure_python_env() {
    # Check venv - auto-create if missing
    if [ ! -d "$UDOS_ROOT/.venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found - creating...${NC}"
        if run_with_spinner "Creating virtual environment..." "python3 -m venv $UDOS_ROOT/.venv"; then
            echo -e "  ${GREEN}✅ Virtual environment created${NC}"
        else
            echo -e "  ${RED}❌ Failed to create virtual environment${NC}"
            return 1
        fi
    fi

    # Activate venv
    source "$UDOS_ROOT/.venv/bin/activate"
    echo -e "${GREEN}✅ Python venv activated${NC}"

    # Check dependencies - auto-install if missing
    if ! python -c "import flask" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Dependencies missing - installing (first time setup)...${NC}"
        echo ""
        pip install --progress-bar on -r "$UDOS_ROOT/requirements.txt"
        if [ $? -eq 0 ]; then
            echo ""
            echo -e "  ${GREEN}✅ Dependencies installed${NC}"
        else
            echo ""
            echo -e "  ${RED}❌ Failed to install dependencies${NC}"
            return 1
        fi
    fi

    # Set environment
    export PYTHONPATH="$UDOS_ROOT:$PYTHONPATH"
    export UDOS_DEV_MODE=1

    # Create log directory
    mkdir -p "$UDOS_ROOT/memory/logs"
}

# ═══════════════════════════════════════════════════════════════════════════
# Header Display
# ═══════════════════════════════════════════════════════════════════════════
print_header() {
    local title="$1"
    local width=75
    local padding=$(( (width - ${#title} - 2) / 2 ))

    echo ""
    echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    printf "${CYAN}${BOLD}║%*s%s%*s║${NC}\n" $padding "" "$title" $((padding + (width - ${#title} - 2) % 2)) ""
    echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
# Port Management
# ═══════════════════════════════════════════════════════════════════════════
kill_port() {
    local port="$1"
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port already in use, killing existing process...${NC}"
        "$UDOS_ROOT/bin/port-manager" kill :$port 2>/dev/null || lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# Service URL Display
# ═══════════════════════════════════════════════════════════════════════════
print_service_url() {
    local label="$1"
    local url="$2"
    printf "  ${DIM}%-14s${NC} ${GREEN}%s${NC}\n" "$label:" "$url"
}
