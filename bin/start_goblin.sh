#!/bin/bash

# Goblin Dev Server Launcher Script
# Starts Goblin Dev Server + Browser Dashboard (localhost only)

set -e

# Resolve script location and uDOS root (works regardless of current cwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$UDOS_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Get version dynamically from dev/goblin/version.json if available
if [ -f "dev/goblin/version.json" ]; then
    GOBLIN_VERSION=$(python3 -c "import json; print(json.load(open('dev/goblin/version.json'))['version'])" 2>/dev/null || echo "0.1.0.0")
else
    GOBLIN_VERSION="0.1.0.0"
fi

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}👺 Goblin Dev Server v${GOBLIN_VERSION}${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Spinner animation
SPINNER_PID=""
start_spinner() {
    local message="$1"
    local frames=( '⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏' )
    local i=0

    echo -ne "${BLUE}[..] ${NC}${message}${NC}"

    while true; do
        echo -ne "\r${BLUE}[${frames[i]}]${NC} ${message}"
        i=$(( (i + 1) % ${#frames[@]} ))
        sleep 0.1
    done &

    SPINNER_PID=$!
}

stop_spinner() {
    local message="$1"
    if [ -n "$SPINNER_PID" ]; then
        kill $SPINNER_PID 2>/dev/null || true
        wait $SPINNER_PID 2>/dev/null || true
    fi
    echo -ne "\r${GREEN}[✓]${NC} ${message}\n"
}

# Check if venv exists
if [ ! -f "$UDOS_ROOT/.venv/bin/activate" ]; then
    print_error "Virtual environment not found at .venv/"
    print_status "Creating virtual environment..."
    start_spinner "Creating venv..."
    python3 -m venv "$UDOS_ROOT/.venv"
    stop_spinner "Virtual environment created"
fi

# Activate virtual environment
start_spinner "Activating virtual environment..."
source "$UDOS_ROOT/.venv/bin/activate"
stop_spinner "Virtual environment activated"

# Install/update all required dependencies
start_spinner "Installing dependencies from requirements.txt..."
pip install -q -r "$UDOS_ROOT/requirements.txt" 2>/dev/null
stop_spinner "Dependencies installed and ready"

# Determine port (default to 8767)
PORT=${1:-8767}

# Start Goblin Dev Server in background
start_spinner "Starting Goblin Dev Server on port ${PORT}..."
python "$UDOS_ROOT/dev/goblin/goblin_server.py" --port "$PORT" --no-interactive 2>/dev/null &
GOBLIN_PID=$!

# Wait for server startup
sleep 3

# Check if server is running
if kill -0 $GOBLIN_PID 2>/dev/null; then
    stop_spinner "Goblin Dev Server started (PID: $GOBLIN_PID)"
else
    echo -ne "\r${RED}[✗]${NC} Failed to start Goblin Dev Server\n"
    print_warning "Note: Goblin Dev Server is in the private submodule (dev/)"
    print_status "Ensure submodule is initialized: git submodule update --init --recursive"
    exit 1
fi

# Determine which browser to use
BROWSER_CMD=""
if command -v xdg-open &> /dev/null; then
    BROWSER_CMD="xdg-open"
elif command -v open &> /dev/null; then
    BROWSER_CMD="open"
elif command -v firefox &> /dev/null; then
    BROWSER_CMD="firefox"
elif command -v google-chrome &> /dev/null; then
    BROWSER_CMD="google-chrome"
elif command -v chromium &> /dev/null; then
    BROWSER_CMD="chromium"
fi

# Open browser dashboard if available
if [ -n "$BROWSER_CMD" ]; then
    start_spinner "Opening browser dashboard..."
    sleep 1
    $BROWSER_CMD "http://localhost:${PORT}" 2>/dev/null &
    stop_spinner "Browser opened"
else
    print_warning "No browser detected. Open manually: http://localhost:${PORT}"
fi

echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
print_success "Goblin Dev Server is running (LOCALHOST ONLY)!"
echo -e "${MAGENTA}🧪 Dashboard: http://localhost:${PORT}${NC}"
echo -e "${MAGENTA}📡 API: http://localhost:${PORT}/api/v0${NC}"
echo -e "${MAGENTA}🔌 WebSocket: ws://localhost:${PORT}/ws${NC}"
echo ""
print_status "Features: Notion sync, Runtime execution, Task scheduling, Binder compilation"
print_status "Press Ctrl+C to stop the server"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Keep script running and handle cleanup
trap "print_warning 'Shutting down Goblin Dev Server...'; kill $GOBLIN_PID 2>/dev/null || true; deactivate 2>/dev/null || true; echo ''; print_success 'Goblin Dev Server stopped'; exit 0" SIGINT SIGTERM

wait $GOBLIN_PID
