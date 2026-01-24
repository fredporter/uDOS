#!/bin/bash

# Wizard Server Launcher (.command for macOS)
# Double-click to start Wizard Server + Browser Dashboard

set -e

# Resolve uDOS root by locating uDOS.py
find_repo_root() {
    local start="$1"
    while [ -n "$start" ] && [ "$start" != "/" ]; do
        if [ -f "$start/uDOS.py" ]; then
            echo "$start"
            return 0
        fi
        start="$(dirname "$start")"
    done
    return 1
}

resolve_udos_root() {
    if [ -n "$UDOS_ROOT" ] && [ -f "$UDOS_ROOT/uDOS.py" ]; then
        echo "$UDOS_ROOT"
        return 0
    fi

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local found
    found="$(find_repo_root "$script_dir")" && { echo "$found"; return 0; }
    found="$(find_repo_root "$(pwd)")" && { echo "$found"; return 0; }

    echo "[ERROR] Could not locate uDOS repo root. Set UDOS_ROOT or run from inside the repo." >&2
    exit 1
}

UDOS_ROOT="$(resolve_udos_root)"
export UDOS_ROOT
cd "$UDOS_ROOT"

# Centralized logs
export UDOS_LOG_DIR="$UDOS_ROOT/memory/logs"
mkdir -p "$UDOS_LOG_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Get version dynamically from wizard/version.json
if [ -f "$UDOS_ROOT/wizard/version.json" ]; then
    WIZARD_VERSION=$(python3 -c "import json; v=json.load(open('$UDOS_ROOT/wizard/version.json'))['version']; print(f\"v{v['major']}.{v['minor']}.{v['patch']}.{v['build']}\")" 2>/dev/null || echo "1.1.0.1")
else
    WIZARD_VERSION="1.1.0.1"
fi

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║            🧙 Wizard Server ${WIZARD_VERSION}                         ║${NC}"
echo -e "${CYAN}║      Always-On • AI Routing • Webhooks • Device Auth          ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

PORT=8765

# Check if venv exists
if [ ! -f "$UDOS_ROOT/.venv/bin/activate" ]; then
    print_error "Virtual environment not found at .venv/"
    print_status "Creating virtual environment..."
    python3 -m venv "$UDOS_ROOT/.venv"
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$UDOS_ROOT/.venv/bin/activate"
print_success "Virtual environment activated"

# Install/update dependencies
print_status "Installing dependencies from requirements.txt..."
pip install -q -r "$UDOS_ROOT/requirements.txt" 2>/dev/null
print_success "Dependencies installed and ready"

# Check if Svelte dashboard needs to be built
DASHBOARD_PATH="$UDOS_ROOT/wizard/dashboard/dist"
if [ ! -d "$DASHBOARD_PATH" ]; then
    print_status "Checking for Node.js/npm..."

    if ! command -v npm &> /dev/null; then
        print_warning "npm not found - attempting automatic installation via Homebrew..."

        if command -v brew &> /dev/null; then
            print_status "Installing Node.js via Homebrew..."
            brew install node 2>&1 | grep -E "==>" || true

            if command -v npm &> /dev/null; then
                print_success "Node.js installed successfully!"
            else
                print_error "Failed to install Node.js"
                print_status "Please install manually: brew install node"
                print_warning "Using fallback HTML dashboard"
            fi
        else
            print_error "Homebrew not found"
            print_status "Please install Node.js from: https://nodejs.org/"
            print_warning "Using fallback HTML dashboard"
        fi
    fi

    # If npm is available, build the dashboard
    if command -v npm &> /dev/null; then
        print_success "Node.js/npm ready - building Svelte dashboard..."
        print_status "Installing dashboard dependencies..."
        cd "$UDOS_ROOT/wizard/dashboard"

        npm install --quiet 2>&1 | grep -v "npm WARN" || true
        print_success "Dashboard dependencies installed"

        print_status "Building Svelte dashboard..."
        if npm run build 2>&1 | grep -E "vite|building|Built" || true; then
            if [ -d "$UDOS_ROOT/wizard/dashboard/dist" ]; then
                print_success "Dashboard built successfully ✨"
            else
                print_warning "Dashboard build failed - using fallback HTML"
            fi
        else
            print_warning "Dashboard build failed - using fallback HTML"
        fi

        cd "$UDOS_ROOT"
    fi
else
    print_success "Svelte dashboard already built"
fi

# Use port manager to clean up any existing wizard process
print_status "Checking for existing Wizard Server on port ${PORT}..."
if lsof -i:${PORT} >/dev/null 2>&1; then
    print_warning "Port ${PORT} is already in use"
    print_status "Using port manager to clean up..."
    python3 -m wizard.cli_port_manager kill wizard >/dev/null 2>&1 || true
    python3 -m wizard.cli_port_manager kill ":${PORT}" >/dev/null 2>&1 || true
    sleep 1

    # If port manager didn't work, use direct kill
    if lsof -i:${PORT} >/dev/null 2>&1; then
        print_status "Port manager failed, using direct kill..."
        PIDS=$(lsof -ti:${PORT} 2>/dev/null || true)
        if [ -n "$PIDS" ]; then
            echo "$PIDS" | xargs kill -9 2>/dev/null || true
            sleep 1
        fi
    fi

    # Wait for port to actually be freed
    for i in {1..5}; do
        if ! lsof -i:${PORT} >/dev/null 2>&1; then
            print_success "Port ${PORT} freed"
            break
        fi
        sleep 1
        if [ $i -eq 5 ]; then
            print_error "Failed to free port ${PORT}"
            print_error "Manual cleanup required: lsof -ti:${PORT} | xargs kill -9"
            exit 1
        fi
    done
fi

# Start Wizard Server in interactive mode
print_success "Starting Wizard Server in interactive mode on port ${PORT}..."
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}📊 Dashboard: http://localhost:${PORT}${NC}"
echo -e "${MAGENTA}📡 API: http://localhost:${PORT}/api/v1${NC}"
echo -e "${MAGENTA}🔌 WebSocket: ws://localhost:${PORT}/ws${NC}"
echo ""
print_status "Press Ctrl+C to stop the server"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Open browser dashboard after a short delay
(sleep 3 && open "http://localhost:${PORT}" 2>/dev/null) &

# Run in foreground (interactive mode)
exec python3 -m wizard.server --port "$PORT"
