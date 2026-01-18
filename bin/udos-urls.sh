#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║              uDOS Localhost URLs Helper                                   ║
# ║         Shared utility for all launch scripts                             ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Source this script in other launch scripts to display localhost URLs

# Colors
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

# Print a box with service URLs
print_service_urls() {
    local title="$1"
    
    echo ""
    echo -e "${CYAN}${BOLD}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓${NC}"
    echo -e "${CYAN}${BOLD}┃${NC}  ${WHITE}${BOLD}$title${NC}"
    echo -e "${CYAN}${BOLD}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛${NC}"
    echo ""
}

# Print individual service
print_service() {
    local name="$1"
    local url="$2"
    local description="$3"
    local status="${4:-⏳}"
    
    printf "  %-8s %s  %-35s  %s\n" "$status" "$name" "$url" "$description"
}

# Print all available services with their status
print_all_services() {
    echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}${BOLD}Available uDOS Services${NC}"
    echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Check each service and print status
    local tui_status="❌"
    local goblin_status="❌"
    local wizard_status="❌"
    local api_status="❌"
    local app_status="❌"
    
    # Check TUI (would be running from current terminal)
    # Check Goblin
    if lsof -Pi :8767 -sTCP:LISTEN -t >/dev/null 2>&1; then
        goblin_status="✅"
    fi
    
    # Check Wizard
    if lsof -Pi :8765 -sTCP:LISTEN -t >/dev/null 2>&1; then
        wizard_status="✅"
    fi
    
    # Check API
    if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        api_status="✅"
    fi
    
    # Check Vite (uMarkdown)
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
        app_status="✅"
    fi
    
    echo -e "${DIM}  Dev Servers:${NC}"
    print_service "TUI" "Terminal" "Command-line interface" "▶️"
    print_service "Goblin" "http://127.0.0.1:8767" "Dev server (experimental)" "$goblin_status"
    print_service "Goblin Docs" "http://127.0.0.1:8767/docs" "Swagger UI for endpoints" "$goblin_status"
    print_service "Goblin ReDoc" "http://127.0.0.1:8767/redoc" "ReDoc API documentation" "$goblin_status"
    
    echo ""
    echo -e "${DIM}  Production Servers:${NC}"
    print_service "Wizard" "http://127.0.0.1:8765" "Production server" "$wizard_status"
    print_service "API" "http://127.0.0.1:5001" "REST API" "$api_status"
    
    echo ""
    echo -e "${DIM}  Frontend:${NC}"
    print_service "uMarkdown" "http://localhost:5173" "Desktop app (Tauri)" "$app_status"
    
    echo ""
    echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Print quick commands reference
print_quick_reference() {
    echo ""
    echo -e "${YELLOW}${BOLD}Quick Commands:${NC}"
    echo -e "  ${DIM}gh auth login${NC}              — Authenticate GitHub CLI"
    echo -e "  ${DIM}npm run dev${NC}                 — Start frontend dev server"
    echo -e "  ${DIM}python dev/goblin/goblin_server.py${NC}  — Start Goblin backend"
    echo ""
}

# Print next steps
print_next_steps() {
    echo -e "${GREEN}${BOLD}Next Steps:${NC}"
    echo ""
}

export -f print_service_urls
export -f print_service
export -f print_all_services
export -f print_quick_reference
export -f print_next_steps
