#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    Wizard Server Dev Launcher                             ║
# ║                  Production Server (port 8765)                            ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Source shared helpers
source "$(dirname "$0")/udos-common.sh"
cd "$UDOS_ROOT"

clear
print_header "🧙 Wizard Server - Production Environment"
print_service_url "Wizard API" "http://localhost:8765"
print_service_url "Health Check" "http://localhost:8765/health"
echo ""

# Setup Python environment (venv + dependencies)
ensure_python_env || exit 1
echo -e "${GREEN}✅ Log directory ready${NC}"

echo ""
echo -e "${CYAN}${BOLD}Starting Wizard Server...${NC}"
echo ""

# Kill any existing process on port 8765
kill_port 8765

# Launch Wizard Server
python -m wizard.server 2>&1

# Cleanup on exit
trap "echo -e '${YELLOW}Shutting down Wizard Server...${NC}'" EXIT
