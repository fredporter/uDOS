#!/bin/bash

# Wizard Server Launcher Script
# Starts Wizard Server + Browser Dashboard

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

# Get version dynamically from wizard/version.json
if [ -f "$UDOS_ROOT/wizard/version.json" ]; then
    WIZARD_VERSION=$(python3 -c "import json; v=json.load(open('$UDOS_ROOT/wizard/version.json'))['version']; print(f\"v{v['major']}.{v['minor']}.{v['patch']}.{v['build']}\")" 2>/dev/null || echo "1.0.0.0")
else
    WIZARD_VERSION="1.0.0.0"
fi

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🧙 Wizard Server v${WIZARD_VERSION}${NC}"
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

INTERACTIVE=0
PORT=8765
ALLOW_FALLBACK=0

# Parse simple flags/port
for arg in "$@"; do
    case "$arg" in
        --interactive|-i)
            INTERACTIVE=1
            ;;
        --allow-fallback)
            ALLOW_FALLBACK=1
            ;;
        --port=*)
            PORT="${arg#*=}"
            ;;
        ""|*[!0-9]*)
            ;; # ignore non-numeric positional
        *)
            PORT="$arg"
            ;;
    esac
done

# Check if Svelte dashboard needs to be built
DASHBOARD_PATH="$UDOS_ROOT/wizard/dashboard/dist"
if [ ! -d "$DASHBOARD_PATH" ]; then
    print_status "Checking for Node.js/npm..."

    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_warning "npm not found - attempting automatic installation..."

        # Try automatic installation based on system
        if command -v apt-get &> /dev/null; then
            print_status "Installing Node.js 20 LTS via NodeSource (this may take 2-3 minutes)..."
            echo ""

            # Install NodeSource repository for Node 20 LTS
            echo -e "${BLUE}[→]${NC} Adding NodeSource repository..."
            if curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - 2>&1 | grep -E "Repository|setup" || true; then
                echo ""
                echo -e "${BLUE}[→]${NC} Installing Node.js 20..."
                sudo apt-get install -y nodejs 2>&1 | grep -E "Unpacking|Setting up|Processing" || true
                echo ""

                if command -v npm &> /dev/null; then
                    NODE_VER=$(node -v)
                    print_success "Node.js ${NODE_VER} installed successfully!"
                else
                    print_error "Failed to install Node.js automatically"
                    if [ "$ALLOW_FALLBACK" -eq 1 ]; then
                        print_warning "Continuing with fallback HTML dashboard..."
                    else
                        print_error "Dashboard build aborted (npm unavailable). Use --allow-fallback to skip build."
                        exit 1
                    fi
                fi
            else
                print_error "Failed to add NodeSource repository"
                if [ "$ALLOW_FALLBACK" -eq 1 ]; then
                    print_warning "Continuing with fallback HTML dashboard..."
                else
                    print_error "Dashboard build aborted (NodeSource setup failed). Use --allow-fallback to skip build."
                    exit 1
                fi
            fi
        elif command -v brew &> /dev/null; then
            print_status "Installing Node.js via Homebrew (this may take a minute)..."
            echo ""
            echo -e "${BLUE}[→]${NC} Running brew install node..."
            brew install node 2>&1 | grep -E "==>" || true
            echo ""
            if command -v npm &> /dev/null; then
                print_success "Node.js installed successfully!"
            else
                print_error "Failed to install Node.js automatically"
                print_status "Please run manually: brew install node"
                if [ "$ALLOW_FALLBACK" -eq 1 ]; then
                    print_warning "Continuing with fallback HTML dashboard..."
                else
                    print_error "Dashboard build aborted (npm unavailable). Use --allow-fallback to skip build."
                    exit 1
                fi
            fi
        elif [ -d "$HOME/.nvm" ]; then
            print_status "Installing Node.js via nvm..."
            source ~/.nvm/nvm.sh
            if nvm install --lts && nvm use --lts; then
                print_success "Node.js installed successfully!"
            else
                print_error "Failed to install Node.js via nvm"
                if [ "$ALLOW_FALLBACK" -eq 1 ]; then
                    print_warning "Continuing with fallback HTML dashboard..."
                else
                    print_error "Dashboard build aborted (npm unavailable). Use --allow-fallback to skip build."
                    exit 1
                fi
            fi
        else
            print_error "No supported package manager found"
            print_status "Please install Node.js manually from: https://nodejs.org/"
            if [ "$ALLOW_FALLBACK" -eq 1 ]; then
                print_warning "Continuing with fallback HTML dashboard..."
            else
                print_error "Dashboard build aborted (npm unavailable). Use --allow-fallback to skip build."
                exit 1
            fi
        fi
    fi

    # Enforce minimum Node version
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | cut -dv -f2)
        NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d'.' -f1)
        if [ "$NODE_MAJOR" -lt 18 ]; then
            print_error "Node.js $NODE_VERSION is too old (need >=18, recommended 20)."
            if command -v apt-get &> /dev/null; then
                print_status "Reinstalling Node.js 20 via NodeSource..."
                if curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs; then
                    print_success "Node.js upgraded to $(node -v)"
                else
                    if [ "$ALLOW_FALLBACK" -eq 1 ]; then
                        print_warning "Continuing with fallback HTML dashboard..."
                        NODE_TOO_OLD=1
                    else
                        print_error "Dashboard build aborted (Node too old). Use --allow-fallback to skip build."
                        exit 1
                    fi
                fi
            else
                if [ "$ALLOW_FALLBACK" -eq 1 ]; then
                    print_warning "Continuing with fallback HTML dashboard..."
                    NODE_TOO_OLD=1
                else
                    print_error "Dashboard build aborted (Node too old). Upgrade Node >=18."
                    exit 1
                fi
            fi
        fi
    fi

    # Re-check if npm is now available after installation attempt
    if command -v npm &> /dev/null; then
        # npm is available, build the dashboard
        print_success "Node.js/npm ready - building Svelte dashboard..."
        start_spinner "Installing dashboard dependencies..."
        cd "$UDOS_ROOT/wizard/dashboard"

        npm install --quiet 2>&1 | grep -v "npm WARN" || true
        stop_spinner "Dashboard dependencies installed"

        start_spinner "Building Svelte dashboard..."
        if npm run build 2>&1 | tee /tmp/vite_build.log | grep -E "vite|building|Built" || true; then
            if [ -d "$UDOS_ROOT/wizard/dashboard/dist" ]; then
                stop_spinner "Dashboard built successfully ✨"
            else
                stop_spinner "Dashboard build failed (check /tmp/vite_build.log)"
                if [ "$ALLOW_FALLBACK" -eq 1 ] || [ "$NODE_TOO_OLD" = "1" ]; then
                    print_warning "Falling back to HTML dashboard"
                else
                    print_error "Build failed; see /tmp/vite_build.log"
                    exit 1
                fi
            fi
        else
            stop_spinner "Dashboard build failed"
            if [ "$ALLOW_FALLBACK" -eq 1 ] || [ "$NODE_TOO_OLD" = "1" ]; then
                print_warning "Falling back to HTML dashboard"
            else
                print_error "Build failed; see /tmp/vite_build.log"
                exit 1
            fi
        fi

        cd "$UDOS_ROOT"
        if [ "$ALLOW_FALLBACK" -eq 1 ] && [ ! -d "$UDOS_ROOT/wizard/dashboard/dist" ]; then
            print_warning "Svelte dashboard not built; using fallback HTML"
        else
            print_success "Svelte dashboard is ready!"
        fi
    else
        print_warning "npm still not available after installation attempt"
        if [ "$ALLOW_FALLBACK" -eq 1 ]; then
            print_warning "Using fallback HTML dashboard"
        else
            print_error "Dashboard build aborted (npm unavailable). Use --allow-fallback to skip build."
            exit 1
        fi
    fi
else
    print_success "Svelte dashboard already built"
fi

# Start Wizard Server in background (daemon by default, TUI if --interactive)
start_spinner "Starting Wizard Server on port ${PORT}..."
if [ "$INTERACTIVE" -eq 1 ]; then
    python -m wizard.server --port "$PORT" --interactive &
else
    python -m wizard.server --port "$PORT" --no-interactive &
fi
WIZARD_PID=$!

# Wait for server startup
sleep 3

# Check if server is running
if kill -0 $WIZARD_PID 2>/dev/null; then
    stop_spinner "Wizard Server started (PID: $WIZARD_PID)"
else
    echo -ne "\r${RED}[✗]${NC} Failed to start Wizard Server\n"
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
print_success "Wizard Server is running!"
echo -e "${MAGENTA}📊 Dashboard: http://localhost:${PORT}${NC}"
echo -e "${MAGENTA}📡 API: http://localhost:${PORT}/api/v1${NC}"
echo -e "${MAGENTA}🔌 WebSocket: ws://localhost:${PORT}/ws${NC}"
echo ""
print_status "Press Ctrl+C to stop the server"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Keep script running and handle cleanup
trap "print_warning 'Shutting down Wizard Server...'; kill $WIZARD_PID 2>/dev/null || true; deactivate 2>/dev/null || true; echo ''; print_success 'Wizard Server stopped'; exit 0" SIGINT SIGTERM

wait $WIZARD_PID
