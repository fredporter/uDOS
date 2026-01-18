#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                        uDOS TUI Launcher                                  ║
# ║                     Quick launch for macOS Terminal                       ║
# ║                                                                           ║
# ║  TUI provides a command-line interface to uDOS                           ║
# ║  For dev server features, also run: Launch-Goblin-Dev.command            ║
# ║  For runtime features, also run: Launch-Tauri-Dev.command (macOS app)    ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

# Change to script directory, then navigate to root
cd "$(dirname "$0")/.."

# Source URL helper
source bin/udos-urls.sh

# Header
clear

print_service_urls "🖥️  uDOS Terminal User Interface (TUI)"

echo -e "${CYAN}${BOLD}Launching TUI...${NC}"
echo ""

# Launch TUI
bin/start_udos.sh

# Cleanup on exit
trap "echo ''" EXIT

echo ""
echo -e "${GREEN}✅ uDOS TUI session ended${NC}"
print_all_services
echo -e "${CYAN}${BOLD}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Tip: To use development features, also launch:${NC}"
echo "  • ${CYAN}Launch-Goblin-Dev.command${NC} — Dev server (port 8767, experimental features)"
echo "  • ${CYAN}Launch-Wizard-Dev.command${NC}  — Wizard server (port 8765, production features)"
echo "  • ${CYAN}Launch-uMarkdown-Dev.command${NC} — Desktop app (Tauri, requires macOS)"
echo ""
read -p "Press Enter to close this window..."
