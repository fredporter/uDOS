#!/bin/bash
# uDOS Display Module v1.3
# Handles all display, banner, and layout functionality

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)" pwd)"
UMEMORY="$UDOS_ROOT/uMEMORY"

# Display functions
show_banner() {
    # Load banner from template
    local banner_template="$UMEMORY/templates/ascii-interface-template.md"
    
    if [[ -f "$banner_template" ]]; then
        # Extract ASCII banner from template
        sed -n '/```ascii/,/```/p' "$banner_template" 2>/dev/null | sed '1d;$d' 2>/dev/null || show_simple_banner
    else
        show_simple_banner
    fi
}

show_simple_banner() {
    echo -e "${BLUE}"
    echo "    ██╗   ██╗██████╗  ██████╗ ███████╗"
    echo "    ██║   ██║██╔══██╗██╔═══██╗██╔════╝"
    echo "    ██║   ██║██║  ██║██║   ██║███████╗"
    echo "    ██║   ██║██║  ██║██║   ██║╚════██║"
    echo "    ╚██████╔╝██████╔╝╚██████╔╝███████║"
    echo "     ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝"
    echo ""
    echo "    Universal Data Operating System"
    echo "    ═══════════════════════════════════════════════════════"
    echo "    ▓▓▓▓▓ Terminal-Native ▓▓▓▓▓ Markdown-First ▓▓▓▓▓"
    echo "    ═══════════════════════════════════════════════════════"
    echo -e "${NC}"
}

show_boot_sequence() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║                                                       ║"
    echo "║   ▓▓▓▓▓ uDOS v1.3 MODULAR SYSTEM ▓▓▓▓▓         ║"
    echo "║                                                       ║"
    echo "╠═══════════════════════════════════════════════════════╣"
    echo "║ ► Memory subsystem............ [OK]             ║"
    echo "║ ► uSCRIPT execution engine.... [OK]             ║"
    echo "║ ► Modular command routing..... [OK]             ║"
    echo "║ ► Template system............. [OK]             ║"
    echo "║ ► Session logging............. [OK]             ║"
    echo "║ ► Authentication system....... [OK]             ║"
    echo "║                                                       ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

recommend_terminal_size() {
    echo -e "${CYAN}📐 Terminal Size Optimizer${NC}"
    echo ""
    echo "Current terminal size: $(tput cols)x$(tput lines)"
    echo ""
    echo "Recommended sizes:"
    echo "  📱 Compact:   80x24   (minimal, efficient)"
    echo "  💻 Standard: 120x30   (balanced, comfortable)"
    echo "  🖥️  Wide:     140x35   (spacious, detailed)"
    echo "  📝 Coding:   120x50   (tall for code)"
    echo "  📊 Dashboard: 160x40   (wide for data)"
    echo ""
    echo "💡 For best experience, resize your terminal to 120x30 or larger"
}

# Main function
display_main() {
    local action="${1:-banner}"
    
    case "$action" in
        "banner")
            show_banner
            show_boot_sequence
            ;;
        "simple-banner")
            show_simple_banner
            ;;
        "boot")
            show_boot_sequence
            ;;
        "resize"|"size")
            recommend_terminal_size
            ;;
        *)
            echo "Display module - Available actions: banner, simple-banner, boot, resize"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    display_main "$@"
fi
