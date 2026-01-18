#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    uDOS Development Mode Launcher                         ║
# ║                     Alpha v1.0.0.36+ • Dev Dashboard                      ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
#
# This keeps a terminal window open for:
#   • Wizard Server coordination (API + WebSocket)
#   • Tauri app backend during development
#   • Live dashboard with requests/logs
#   • Interactive dev prompt for testing
#
# Runs until you type 'exit' or press Ctrl+C

set -e
cd "$(dirname "$0")/.."

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
# Configuration
# ═══════════════════════════════════════════════════════════════════════════
UDOS_ROOT="$(pwd)"
API_PORT=5001
WIZARD_PORT=8765
VITE_PORT=5173
LOG_DIR="$UDOS_ROOT/memory/logs"
PIDS_FILE="/tmp/udos-dev-pids.txt"

# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════
print_header() {
    clear
    echo ""
    echo -e "${CYAN}${TL}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${TR}${NC}"
    echo -e "${CYAN}${V_LINE}${NC}  ${WHITE}${BOLD}🧙 uDOS Development Mode${NC}                                       ${CYAN}${V_LINE}${NC}"
    echo -e "${CYAN}${V_LINE}${NC}  ${DIM}Wizard Server • API • Tauri Backend${NC}                             ${CYAN}${V_LINE}${NC}"
    echo -e "${CYAN}${BL}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${H_LINE}${BR}${NC}"
    echo ""
}

print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        "ok")     echo -e "  ${GREEN}✓${NC} $message" ;;
        "warn")   echo -e "  ${YELLOW}⚠${NC} $message" ;;
        "error")  echo -e "  ${RED}✗${NC} $message" ;;
        "info")   echo -e "  ${BLUE}ℹ${NC} $message" ;;
        "run")    echo -e "  ${MAGENTA}▶${NC} $message" ;;
        *)        echo -e "  $message" ;;
    esac
}

print_divider() {
    echo -e "${DIM}  ─────────────────────────────────────────────────────────────${NC}"
}

# ═══════════════════════════════════════════════════════════════════════════
# Cleanup Handler
# ═══════════════════════════════════════════════════════════════════════════
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down dev servers...${NC}"

    # Kill background processes
    if [ -f "$PIDS_FILE" ]; then
        while read -r pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null
                echo -e "  ${DIM}Stopped PID $pid${NC}"
            fi
        done < "$PIDS_FILE"
        rm -f "$PIDS_FILE"
    fi

    # Kill any remaining processes on our ports
    lsof -ti:$API_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -ti:$WIZARD_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true

    echo -e "${GREEN}✓ Clean shutdown complete${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# ═══════════════════════════════════════════════════════════════════════════
# Health Monitoring & Auto-Healing
# ═══════════════════════════════════════════════════════════════════════════

# Retry counters (reset every 30 minutes)
API_FAILURES=0
WIZARD_FAILURES=0
LAST_RESET=$(date +%s)
MAX_FAILURES=3  # Max failures before giving up for this cycle

check_and_heal_servers() {
    # Monitor server health and auto-restart on failure
    while true; do
        sleep 10  # Check every 10 seconds
        CURRENT_TIME=$(date +%s)

        # Reset counters every 30 minutes
        if [ $((CURRENT_TIME - LAST_RESET)) -ge 1800 ]; then
            API_FAILURES=0
            WIZARD_FAILURES=0
            LAST_RESET=$CURRENT_TIME
        fi

        # Check API Server
        if [ -n "$API_PID" ] && ! kill -0 "$API_PID" 2>/dev/null; then
            if [ $API_FAILURES -lt $MAX_FAILURES ]; then
                ((API_FAILURES++))
                echo -e "${YELLOW}⚠ API Server died (attempt $API_FAILURES/$MAX_FAILURES), restarting...${NC}"
                python extensions/api/server.py > "$LOG_DIR/api-dev-$(date +%Y-%m-%d).log" 2>&1 &
                API_PID=$!
                echo "$API_PID" >> "$PIDS_FILE"
                sleep 2
            fi
        fi

        # Check Wizard Server
        if [ -n "$WIZARD_PID" ] && ! kill -0 "$WIZARD_PID" 2>/dev/null; then
            if [ $WIZARD_FAILURES -lt $MAX_FAILURES ]; then
                ((WIZARD_FAILURES++))
                echo -e "${YELLOW}⚠ Wizard Server died (attempt $WIZARD_FAILURES/$MAX_FAILURES), restarting...${NC}"
                python wizard/server.py > "$LOG_DIR/wizard-$(date +%Y-%m-%d).log" 2>&1 &
                WIZARD_PID=$!
                echo "$WIZARD_PID" >> "$PIDS_FILE"
                sleep 2
            fi
        fi
    done
}

# Start health monitor in background
check_and_heal_servers &
MONITOR_PID=$!
echo "$MONITOR_PID" >> "$PIDS_FILE"


print_header

echo -e "${WHITE}${BOLD}  Environment Setup${NC}"
print_divider

# Check virtual environment
if [ ! -d ".venv" ]; then
    print_status "error" "Virtual environment not found!"
    echo "       Run: python3 -m venv .venv"
    exit 1
fi

source .venv/bin/activate
print_status "ok" "Python venv activated"

# Set paths
export PYTHONPATH="$UDOS_ROOT:$PYTHONPATH"
export UDOS_DEV_MODE=1

# Check dependencies (auto-repair)
MISSING_DEPS=()

# Check Flask (API server)
if ! python -c "import flask" 2>/dev/null; then
    MISSING_DEPS+=("flask>=2.0.0")
fi

# Check FastAPI (Wizard server)
if ! python -c "import fastapi" 2>/dev/null; then
    MISSING_DEPS+=("fastapi>=0.95.0")
fi

# Check uvicorn (Wizard server)
if ! python -c "import uvicorn" 2>/dev/null; then
    MISSING_DEPS+=("uvicorn[standard]>=0.21.0")
fi

# Check cryptography (config panel)
if ! python -c "import cryptography" 2>/dev/null; then
    MISSING_DEPS+=("cryptography>=41.0.0")
fi

# Auto-install missing dependencies
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_status "warn" "Installing missing dependencies: ${MISSING_DEPS[*]}"
    pip install -q "${MISSING_DEPS[@]}" 2>&1 | grep -v "WARNING:" || true
    print_status "ok" "Dependencies installed"
else
    print_status "ok" "Python dependencies ready"
fi

# Check Node.js
if ! command -v npm &> /dev/null; then
    print_status "warn" "npm not found - Tauri dev mode unavailable"
    TAURI_AVAILABLE=0
else
    print_status "ok" "Node.js/npm available"
    TAURI_AVAILABLE=1
fi

# Create log directory
mkdir -p "$LOG_DIR"
print_status "ok" "Log directory: $LOG_DIR"

# Get version
VERSION=$(python -c "from core.version import get_core_version; print(get_core_version())" 2>/dev/null || echo "v1.0.0.0")
print_status "info" "uDOS Core $VERSION"

echo ""

# ═══════════════════════════════════════════════════════════════════════════
# Start Services
# ═══════════════════════════════════════════════════════════════════════════
echo -e "${WHITE}${BOLD}  Starting Services${NC}"
print_divider

# Clear PIDs file
> "$PIDS_FILE"

# Check for port conflicts first
python -m wizard.cli_port_manager conflicts > /dev/null 2>&1 || true

# Start API Server
print_status "run" "Starting API server on port $API_PORT..."
if lsof -ti:$API_PORT >/dev/null 2>&1; then
    print_status "warn" "Port $API_PORT in use, killing..."
    bin/port-manager kill :$API_PORT 2>/dev/null || lsof -ti:$API_PORT | xargs kill -9 2>/dev/null || true
    sleep 1
fi
python extensions/api/server.py > "$LOG_DIR/api-dev-$(date +%Y-%m-%d).log" 2>&1 &
API_PID=$!
echo "$API_PID" >> "$PIDS_FILE"
sleep 2

if kill -0 "$API_PID" 2>/dev/null; then
    print_status "ok" "API server running (PID: $API_PID)"
else
    print_status "error" "API server failed to start"
fi

# Start Wizard Server (production)
if [ -f "wizard/server.py" ]; then
    print_status "run" "Starting Wizard server (production) on port $WIZARD_PORT..."
    if lsof -ti:$WIZARD_PORT >/dev/null 2>&1; then
        print_status "warn" "Port $WIZARD_PORT in use, killing..."
        bin/port-manager kill :$WIZARD_PORT 2>/dev/null || lsof -ti:$WIZARD_PORT | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
    python wizard/server.py > "$LOG_DIR/wizard-$(date +%Y-%m-%d).log" 2>&1 &
    WIZARD_PID=$!
    echo "$WIZARD_PID" >> "$PIDS_FILE"
    sleep 2

    if kill -0 "$WIZARD_PID" 2>/dev/null; then
        print_status "ok" "Wizard server running (PID: $WIZARD_PID)"
    else
        print_status "warn" "Wizard server failed to start (optional)"
        WIZARD_PID=""
    fi
else
    print_status "warn" "Wizard server not found (optional)"
    WIZARD_PID=""
fi

# Note: For experimental features, use Goblin Dev Server (port 8767)
# Run: ./bin/Launch-Goblin-Dev.command

echo ""

# ═══════════════════════════════════════════════════════════════════════════
# Dashboard Display
# ═══════════════════════════════════════════════════════════════════════════
show_dashboard() {
    echo -e "${WHITE}${BOLD}  Services Dashboard${NC}"
    print_divider

    # API Server status
    if kill -0 "$API_PID" 2>/dev/null; then
        echo -e "  ${GREEN}●${NC} API Server        ${DIM}http://localhost:$API_PORT${NC}"
    else
        echo -e "  ${RED}●${NC} API Server        ${DIM}(stopped)${NC}"
    fi

    # Wizard Server status
    if [ -n "$WIZARD_PID" ] && kill -0 "$WIZARD_PID" 2>/dev/null; then
        echo -e "  ${GREEN}●${NC} Wizard Server     ${DIM}http://localhost:$WIZARD_PORT${NC}"
    else
        echo -e "  ${YELLOW}●${NC} Wizard Server     ${DIM}(not running)${NC}"
    fi

    # Tauri dev server (if running)
    if lsof -i:$VITE_PORT &>/dev/null; then
        echo -e "  ${GREEN}●${NC} Vite Dev Server   ${DIM}http://localhost:$VITE_PORT${NC}"
    else
        echo -e "  ${DIM}○${NC} Vite Dev Server   ${DIM}(not started)${NC}"
    fi

    echo ""
    echo -e "${WHITE}${BOLD}  Quick Links${NC}"
    print_divider
    echo -e "  ${CYAN}API:${NC}      http://localhost:$API_PORT/api/health"
    echo -e "  ${CYAN}Swagger:${NC}  http://localhost:$API_PORT/docs (if enabled)"
    echo -e "  ${CYAN}Logs:${NC}     $LOG_DIR"
    echo ""
}

show_dashboard

# ═══════════════════════════════════════════════════════════════════════════
# Commands Help
# ═══════════════════════════════════════════════════════════════════════════
show_commands() {
    echo -e "${WHITE}${BOLD}  Dev Commands${NC}"
    print_divider
    echo -e "  ${CYAN}tauri${NC}         Launch Tauri app in dev mode"
    echo -e "  ${CYAN}browser${NC}       Open http://localhost:$VITE_PORT in browser"
    echo -e "  ${CYAN}tui${NC}           Start uDOS TUI in this terminal"
    echo -e "  ${CYAN}wizard-start${NC}   Start Wizard Server"
    echo -e "  ${CYAN}wizard-stop${NC}    Stop Wizard Server"
    echo -e "  ${CYAN}wizard-restart${NC} Restart Wizard Server"
    echo -e "  ${CYAN}wizard${NC}        Start Wizard Server TUI"
    echo -e "  ${CYAN}logs${NC}          Tail combined dev logs"
    echo -e "  ${CYAN}status${NC}        Show services dashboard"
    echo -e "  ${CYAN}health${NC}        Detailed health check & metrics"
    echo -e "  ${CYAN}restart${NC}       Restart all services"
    echo -e "  ${CYAN}test${NC}          Run quick API test"
    echo -e "  ${CYAN}version${NC}       Show all versions"
    echo -e "  ${CYAN}help${NC}          Show this help"
    echo -e "  ${CYAN}exit${NC}          Shutdown and exit"
    echo ""
    echo -e "${DIM}  🔄 Auto-healing: Failed servers restart automatically (max 3 retries/30min)${NC}"
    echo -e "${DIM}  Note: Commands like TIDY, CLEAN, REPAIR launch TUI automatically${NC}"
    echo ""
}

show_commands

# ═══════════════════════════════════════════════════════════════════════════
# Interactive Command Loop
# ═══════════════════════════════════════════════════════════════════════════
echo -e "${GREEN}${BOLD}Ready!${NC} Type a command or press Enter for TUI prompt."
echo ""

while true; do
    echo -ne "${MAGENTA}dev>${NC} "
    read -r cmd args

    case "$cmd" in
        "tauri")
            if [ "$TAURI_AVAILABLE" -eq 1 ]; then
                print_status "run" "Launching Tauri dev mode..."
                cd app
                npm run tauri:dev &
                TAURI_PID=$!
                echo "$TAURI_PID" >> "$PIDS_FILE"
                cd "$UDOS_ROOT"
                print_status "ok" "Tauri launched (PID: $TAURI_PID)"
            else
                print_status "error" "npm not available"
            fi
            ;;

        "browser")
            print_status "run" "Opening browser..."
            if [ "$(uname)" = "Darwin" ]; then
                open "http://localhost:$VITE_PORT" 2>/dev/null || open "http://localhost:$API_PORT"
            else
                xdg-open "http://localhost:$VITE_PORT" 2>/dev/null || xdg-open "http://localhost:$API_PORT"
            fi
            ;;

        "tui")
            print_status "run" "Starting TUI..."
            bin/start_udos.sh
            print_header
            show_dashboard
            ;;

        "wizard")
            print_status "run" "Starting Wizard Server TUI..."
            cd wizard
            ./launch_wizard_tui.sh
            cd "$UDOS_ROOT"
            print_header
            show_dashboard
            ;;

        "wizard-start")
            if [ -n "$WIZARD_PID" ] && kill -0 "$WIZARD_PID" 2>/dev/null; then
                print_status "warn" "Wizard Server already running (PID: $WIZARD_PID)"
            else
                print_status "run" "Starting Wizard Server (production)..."
                python wizard/server.py > "$LOG_DIR/wizard-$(date +%Y-%m-%d).log" 2>&1 &
                WIZARD_PID=$!
                echo "$WIZARD_PID" >> "$PIDS_FILE"
                sleep 2

                if kill -0 "$WIZARD_PID" 2>/dev/null; then
                    print_status "ok" "Wizard Server started (PID: $WIZARD_PID)"
                else
                    print_status "error" "Wizard Server failed to start"
                    WIZARD_PID=""
                fi
            fi
            ;;

        "wizard-stop")
            if [ -z "$WIZARD_PID" ] || ! kill -0 "$WIZARD_PID" 2>/dev/null; then
                print_status "warn" "Wizard Server not running"
            else
                print_status "run" "Stopping Wizard Server (PID: $WIZARD_PID)..."
                kill "$WIZARD_PID" 2>/dev/null
                sleep 1
                if kill -0 "$WIZARD_PID" 2>/dev/null; then
                    kill -9 "$WIZARD_PID" 2>/dev/null
                fi
                print_status "ok" "Wizard Server stopped"
                WIZARD_PID=""
            fi
            ;;

        "wizard-restart")
            print_status "run" "Restarting Wizard Server..."

            # Stop if running
            if [ -n "$WIZARD_PID" ] && kill -0 "$WIZARD_PID" 2>/dev/null; then
                kill "$WIZARD_PID" 2>/dev/null
                sleep 1
                if kill -0 "$WIZARD_PID" 2>/dev/null; then
                    kill -9 "$WIZARD_PID" 2>/dev/null
                fi
            fi

            # Start fresh
            python wizard/server.py > "$LOG_DIR/wizard-$(date +%Y-%m-%d).log" 2>&1 &
            WIZARD_PID=$!
            echo "$WIZARD_PID" >> "$PIDS_FILE"
            sleep 2

            if kill -0 "$WIZARD_PID" 2>/dev/null; then
                print_status "ok" "Wizard Server restarted (PID: $WIZARD_PID)"
            else
                print_status "error" "Wizard Server failed to restart"
                WIZARD_PID=""
            fi
            ;;

        "logs")
            echo ""
            print_status "info" "Tailing logs in real-time (Ctrl+C to return to prompt)..."
            echo ""
            tail -f "$LOG_DIR"/*-dev-*.log "$LOG_DIR"/session-commands-*.log 2>/dev/null || tail -f "$LOG_DIR"/*.log
            ;;

        "status")
            print_header
            show_dashboard
            show_commands
            ;;

        "restart")
            print_status "run" "Restarting services..."
            # Kill existing
            while read -r pid; do
                kill "$pid" 2>/dev/null
            done < "$PIDS_FILE"
            > "$PIDS_FILE"
            sleep 1

            # Restart API
            python extensions/api/server.py > "$LOG_DIR/api-dev-$(date +%Y-%m-%d).log" 2>&1 &
            API_PID=$!
            echo "$API_PID" >> "$PIDS_FILE"

            # Restart Wizard
            if [ -f "wizard/server.py" ]; then
                python wizard/server.py > "$LOG_DIR/wizard-$(date +%Y-%m-%d).log" 2>&1 &
                WIZARD_PID=$!
                echo "$WIZARD_PID" >> "$PIDS_FILE"
            fi
            services..."

            # Test API
            echo -e "${CYAN}API Server:${NC}"
            curl -s "http://localhost:$API_PORT/api/health" | python -m json.tool 2>/dev/null || echo "  ❌ Not responding"

            # Test Wizard
            echo -e "\n${CYAN}Wizard Server:${NC}"
            curl -s "http://localhost:$WIZARD_PORT/health" | python -m json.tool 2>/dev/null || echo "  ❌ N
            print_status "ok" "Services restarted"
            show_dashboard
            ;;

        "health")
            print_status "info" "System Health Check"
            echo ""

            # Check processes
            echo -e "${CYAN}Process Status:${NC}"
            if kill -0 "$API_PID" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} API Server (PID: $API_PID)"
            else
                echo -e "  ${RED}✗${NC} API Server (not running)"
            fi

            if [ -n "$WIZARD_PID" ] && kill -0 "$WIZARD_PID" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} Wizard Server (PID: $WIZARD_PID)"
            else
                echo -e "  ${RED}✗${NC} Wizard Server (not running)"
            fi

            if kill -0 "$MONITOR_PID" 2>/dev/null; then
                echo -e "  ${GREEN}✓${NC} Health Monitor (PID: $MONITOR_PID)"
            else
                echo -e "  ${RED}✗${NC} Health Monitor (not running)"
            fi

            # Check endpoints
            echo -e "\n${CYAN}Endpoint Status:${NC}"
            API_HEALTH=$(curl -s -m 2 "http://localhost:$API_PORT/api/health" 2>/dev/null | python -m json.tool 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo -e "  ${GREEN}✓${NC} API http://localhost:$API_PORT/api/health"
            else
                echo -e "  ${RED}✗${NC} API http://localhost:$API_PORT/api/health"
            fi

            WIZARD_HEALTH=$(curl -s -m 2 "http://localhost:$WIZARD_PORT/health" 2>/dev/null | python -m json.tool 2>/dev/null)
            if [ $? -eq 0 ]; then
                echo -e "  ${GREEN}✓${NC} Wizard http://localhost:$WIZARD_PORT/health"
            else
                echo -e "  ${RED}✗${NC} Wizard http://localhost:$WIZARD_PORT/health"
            fi

            # Check failure counters
            echo -e "\n${CYAN}Failure Recovery:${NC}"
            echo "  API Server: $API_FAILURES failures (reset in $((1800 - ($(date +%s) - LAST_RESET))) seconds)"
            echo "  Wizard Server: $WIZARD_FAILURES failures (reset in $((1800 - ($(date +%s) - LAST_RESET))) seconds)"
            echo -e "  Max retries: $MAX_FAILURES"

            # Check logs
            echo -e "\n${CYAN}Recent Logs:${NC}"
            if [ -f "$LOG_DIR/api-dev-$(date +%Y-%m-%d).log" ]; then
                API_ERRORS=$(grep -i "error" "$LOG_DIR/api-dev-$(date +%Y-%m-%d).log" | wc -l)
                echo -e "  API: $API_ERRORS errors in today's log"
            fi

            if [ -f "$LOG_DIR/wizard-dev-$(date +%Y-%m-%d).log" ]; then
                WIZARD_ERRORS=$(grep -i "error" "$LOG_DIR/wizard-dev-$(date +%Y-%m-%d).log" | wc -l)
                echo -e "  Wizard: $WIZARD_ERRORS errors in today's log"
            fi
            ;;

        "test")
            print_status "run" "Testing API..."
            curl -s "http://localhost:$API_PORT/api/health" | python -m json.tool 2>/dev/null || echo "API not responding"
            ;;

        "version")
            python -m core.version show
            ;;

        "help"|"?")
            show_commands
            ;;

        "exit"|"quit"|"q")
            break
            ;;

        "")
            # Empty input - show prompt hint
            echo -e "${DIM}  Type 'help' for commands, 'tui' for full TUI, or 'exit' to quit${NC}"
            ;;

        # uDOS maintenance commands - not available in Dev Mode
        "tidy"|"TIDY"|"clean"|"CLEAN"|"repair"|"REPAIR"|"shakedown"|"SHAKEDOWN")
            print_status "warn" "Command '$cmd' not available in Dev Mode"
            echo -e "${DIM}  These commands require full TUI session${NC}"
            echo -e "${DIM}  Type 'tui' to launch full TUI, or 'exit' then run bin/start_udos.sh${NC}"
            ;;

        *)
            # Try to execute as uDOS command via API
            if [ -n "$cmd" ]; then
                print_status "run" "Executing via API: $cmd $args"
                RESPONSE=$(curl -s -X POST "http://localhost:$API_PORT/api/command" \
                    -H "Content-Type: application/json" \
                    -d "{\"command\": \"$cmd $args\"}" 2>/dev/null)

                if [ -n "$RESPONSE" ]; then
                    echo "$RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'output' in data:
        print(data['output'])
    elif 'error' in data:
        print(f\"Error: {data['error']}\")
    else:
        print(json.dumps(data, indent=2))
except:
    print(sys.stdin.read())
" 2>/dev/null || echo "$RESPONSE"
                else
                    print_status "warn" "No response - try 'status' to check services"
                fi
            fi
            ;;
    esac
done

# Cleanup happens via trap
