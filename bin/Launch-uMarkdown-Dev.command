#!/bin/bash
# Launch uMarkdown Mac App with Goblin Dev Server
# Experimental development environment with dev features

set -e

# Get directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
APP_DIR="$PROJECT_ROOT/app"

# Source URL helper
source "$SCRIPT_DIR/udos-urls.sh"

clear

print_service_urls "🎨 uMarkdown Mac App - Development Environment"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}❌ App directory not found: $APP_DIR${NC}"
    echo "   Is the workspace set up correctly?"
    exit 1
fi

echo -e "${CYAN}${BOLD}Environment Setup${NC}"
echo ""

# Check if Goblin Dev Server is already running
if lsof -Pi :8767 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${GREEN}✅ Goblin Dev Server already running on port 8767${NC}"
else
    echo -e "${YELLOW}🚀 Starting Goblin Dev Server...${NC}"
    
    # Start Goblin Dev Server in background
    cd "$PROJECT_ROOT"
    
    # Check venv
    if [ ! -d "$PROJECT_ROOT/.venv" ]; then
        echo -e "${RED}❌ Virtual environment not found${NC}"
        exit 1
    fi
    
    source "$PROJECT_ROOT/.venv/bin/activate"
    
    # Start server
    python3 "$PROJECT_ROOT/dev/goblin/goblin_server.py" > "$PROJECT_ROOT/memory/logs/goblin-server.log" 2>&1 &
    GOBLIN_PID=$!
    
    # Wait for server to start
    echo -e "${YELLOW}⏳ Waiting for Goblin Dev Server to initialize...${NC}"
    sleep 3
    
    if lsof -Pi :8767 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${GREEN}✅ Goblin Dev Server started (PID: $GOBLIN_PID)${NC}"
    else
        echo -e "${RED}❌ Goblin Dev Server failed to start${NC}"
        echo -e "${RED}   Check logs: tail -50 $PROJECT_ROOT/memory/logs/goblin-server.log${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${CYAN}${BOLD}Frontend Setup${NC}"
echo ""

# Navigate to app directory
cd "$APP_DIR"

# Check Node.js
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js/npm not found${NC}"
    echo "   Install from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✅ Node.js available${NC}"

# Check/install dependencies
if [ ! -d "$APP_DIR/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing npm dependencies...${NC}"
    if npm install 2>&1 | grep -q "ERESOLVE\|peer"; then
        echo -e "${YELLOW}⚠️  Peer dependency conflict detected${NC}"
        echo "   Retrying with --legacy-peer-deps flag..."
        npm install --legacy-peer-deps || {
            echo -e "${RED}❌ npm install failed${NC}"
            exit 1
        }
    fi
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi

# Check Tauri dependencies (macOS specific)
if ! command -v cargo &> /dev/null; then
    echo -e "${YELLOW}⚠️  Rust/Cargo not found${NC}"
    echo "   Install from https://rustup.rs/"
    echo "   After install, run: cargo --version"
    exit 1
fi

echo -e "${GREEN}✅ Rust/Cargo available${NC}"

echo ""
echo -e "${YELLOW}🎨 Starting Tauri Dev Server...${NC}"
echo -e "${DIM}   This may take 30-60 seconds on first run${NC}"
echo ""

# Start Tauri dev
# Set environment variables for dev
export VITE_API_URL="http://127.0.0.1:8767"
export TAURI_PRIVATE_KEY=""  # Optional: set if you have signing key

# Run with better error handling
if npm run tauri:dev 2>&1 | tee "$PROJECT_ROOT/memory/logs/tauri-dev-$(date +%Y-%m-%d).log"; then
    echo -e "${GREEN}✅ Tauri dev server closed normally${NC}"
else
    ERROR_CODE=$?
    echo ""
    echo -e "${RED}❌ Tauri dev server exited with error code: $ERROR_CODE${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "  1. Check logs: tail -100 $PROJECT_ROOT/memory/logs/tauri-dev-*.log"
    echo "  2. Verify Rust: rustc --version && cargo --version"
    echo "  3. Update Rust: rustup update"
    echo "  4. Clear build cache: rm -rf src-tauri/target"
    echo "  5. Reinstall deps: npm install && npm run tauri:build"
    echo ""
fi

# Cleanup on exit (only if we started the server)
if [ ! -z "$GOBLIN_PID" ]; then
    echo ""
    echo -e "${YELLOW}🛑 Shutting down Goblin Dev Server (PID: $GOBLIN_PID)...${NC}"
    kill $GOBLIN_PID 2>/dev/null || true
    wait $GOBLIN_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
fi

echo ""
print_all_services
