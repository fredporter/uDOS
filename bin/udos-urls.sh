#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
#  uDOS URL Helper Functions
#  Shared utilities for displaying service URLs across launch scripts
# ═══════════════════════════════════════════════════════════════════════════

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

# Function: Print a beautiful service URL banner
print_service_urls() {
    local title="$1"

    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                                                                           ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${BOLD}${title}${NC}"
    local padding=$((75 - ${#title}))
    printf "${CYAN}║${NC}\n"
    echo -e "${CYAN}║${NC}                                                                           ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function: Print individual service URL
print_url() {
    local label="$1"
    local url="$2"
    local color="${3:-$CYAN}"

    printf "  ${BOLD}%-20s${NC} ${color}%s${NC}\n" "$label:" "$url"
}

# Function: Print Wizard Server URLs
print_wizard_urls() {
    echo -e "${BOLD}📍 Service URLs:${NC}"
    echo ""
    print_url "🔐 Config Panel" "http://127.0.0.1:8765/api/v1/config/panel" "$GREEN"
    print_url "📊 API Status" "http://127.0.0.1:8765/api/v1/config/status" "$CYAN"
    print_url "💚 Health Check" "http://127.0.0.1:8765/health" "$BLUE"
    print_url "📖 API Docs" "http://127.0.0.1:8765/docs" "$YELLOW"
    print_url "🔌 Port Manager" "http://127.0.0.1:8765/api/v1/ports/status" "$MAGENTA"
    echo ""
}

# Function: Print Goblin Dev Server URLs
print_goblin_urls() {
    echo -e "${BOLD}📍 Service URLs:${NC}"
    echo ""
    print_url "🧪 Dev Server" "http://127.0.0.1:8767/health" "$GREEN"
    print_url "📊 GitHub Status" "http://127.0.0.1:8767/api/v0/github/status" "$CYAN"
    print_url "🤖 AI Services" "http://127.0.0.1:8767/api/v0/ai/status" "$BLUE"
    print_url "📝 Workflow" "http://127.0.0.1:8767/api/v0/workflow/status" "$YELLOW"
    echo ""
}

# Function: Print API Extension URLs
print_api_urls() {
    echo -e "${BOLD}📍 Service URLs:${NC}"
    echo ""
    print_url "🔌 API Server" "http://127.0.0.1:8766/health" "$GREEN"
    print_url "📊 Status" "http://127.0.0.1:8766/status" "$CYAN"
    print_url "🌐 WebSocket" "ws://127.0.0.1:8766/ws" "$BLUE"
    echo ""
}

# Function: Print Tauri App URLs
print_tauri_urls() {
    echo -e "${BOLD}📍 Service URLs:${NC}"
    echo ""
    print_url "🎨 Tauri Dev" "http://localhost:1420" "$GREEN"
    print_url "⚡ Vite Dev" "http://localhost:5173" "$CYAN"
    echo ""
}

# Function: Print all development URLs
print_dev_mode_urls() {
    print_service_urls "🚀 uDOS Development Mode - All Services"

    echo -e "${BOLD}${CYAN}Wizard Server (Port 8765)${NC}"
    print_wizard_urls

    echo -e "${BOLD}${MAGENTA}Goblin Dev Server (Port 8767)${NC}"
    print_goblin_urls

    echo -e "${BOLD}${BLUE}API Extension (Port 8766)${NC}"
    print_api_urls

    echo -e "${BOLD}${YELLOW}Tauri Desktop App${NC}"
    print_tauri_urls

    echo -e "${BOLD}💡 Quick Commands:${NC}"
    echo "  • Open Config Panel: open http://127.0.0.1:8765/api/v1/config/panel"
    echo "  • Check All Ports:    ./bin/port-manager status"
    echo "  • Stop All Services:  pkill -f 'wizard|goblin|uvicorn'"
    echo ""
}

# Function: Print separator line
print_separator() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
}

# Function: Print success message with checkmark
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function: Print error message with X
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function: Print warning message
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function: Print info message
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Export functions so they're available in scripts that source this file
export -f print_service_urls
export -f print_url
export -f print_wizard_urls
export -f print_goblin_urls
export -f print_api_urls
export -f print_tauri_urls
export -f print_dev_mode_urls
export -f print_separator
export -f print_success
export -f print_error
export -f print_warning
export -f print_info
