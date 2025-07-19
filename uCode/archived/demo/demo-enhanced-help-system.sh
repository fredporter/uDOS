#!/bin/bash
# demo-enhanced-help-system.sh - Comprehensive Demo of Dataset-Linked Help System
# Version: 1.0.0
# Description: Demonstrates the improved uCode commands and HELP integration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"

# Colors for demo
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

demo_header() {
    clear
    echo -e "${BOLD}${PURPLE}🔧 Enhanced uDOS Help System Demo${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "This demo showcases the ${YELLOW}dataset-driven help system${NC} that"
    echo -e "links uCode commands to comprehensive ${GREEN}documentation and templates${NC}."
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_command_help() {
    echo -e "${BLUE}▶ Demo 1: Individual Command Help${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "Let's get detailed help for the ${GREEN}PRINT${NC} command:"
    echo ""
    
    echo -e "${CYAN}$ ./uCode/enhanced-help-system.sh command PRINT${NC}"
    ./uCode/enhanced-help-system.sh command PRINT
    
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_category_browsing() {
    echo -e "${BLUE}▶ Demo 2: Category-Based Command Browsing${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "Browse commands by category - let's look at ${GREEN}file${NC} commands:"
    echo ""
    
    echo -e "${CYAN}$ ./uCode/enhanced-help-system.sh category file${NC}"
    ./uCode/enhanced-help-system.sh category file
    
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_dataset_stats() {
    echo -e "${BLUE}▶ Demo 3: Dataset Statistics and Integration${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "View comprehensive statistics from the ${GREEN}command dataset${NC}:"
    echo ""
    
    echo -e "${CYAN}$ ./uCode/enhanced-help-system.sh stats${NC}"
    ./uCode/enhanced-help-system.sh stats
    
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_comprehensive_docs() {
    echo -e "${BLUE}▶ Demo 4: Comprehensive Documentation Generation${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "Generate complete documentation from the ${GREEN}dataset${NC}:"
    echo ""
    
    echo -e "${CYAN}$ ./uCode/enhanced-help-system.sh generate${NC}"
    ./uCode/enhanced-help-system.sh generate
    
    if [[ -f "$UHOME/uMemory/generated/comprehensive-help.md" ]]; then
        echo ""
        echo -e "📄 ${GREEN}Generated documentation preview:${NC}"
        echo ""
        head -20 "$UHOME/uMemory/generated/comprehensive-help.md"
        echo "..."
        echo -e "${YELLOW}[Truncated - see full file at uMemory/generated/comprehensive-help.md]${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_search_functionality() {
    echo -e "${BLUE}▶ Demo 5: Search Functionality${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "Search for commands related to ${GREEN}variables${NC}:"
    echo ""
    
    echo -e "${CYAN}$ ./uCode/enhanced-help-system.sh search variable${NC}"
    ./uCode/enhanced-help-system.sh search variable
    
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_template_integration() {
    echo -e "${BLUE}▶ Demo 6: Template System Integration${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "The help system integrates with ${GREEN}uTemplate${NC} for rich documentation:"
    echo ""
    
    if [[ -f "$UHOME/uTemplate/command-help-template.md" ]]; then
        echo -e "📋 ${GREEN}Template available:${NC}"
        echo -e "${CYAN}$ head -15 uTemplate/command-help-template.md${NC}"
        head -15 "$UHOME/uTemplate/command-help-template.md"
    else
        echo -e "❌ ${YELLOW}Template not found - would show template integration${NC}"
    fi
    
    echo ""
    echo -e "🔗 ${GREEN}Dataset files used:${NC}"
    if [[ -d "$UHOME/uTemplate/datasets" ]]; then
        find "$UHOME/uTemplate/datasets" -name "*.json" | while read -r file; do
            echo -e "  • ${CYAN}$(basename "$file")${NC} - $(jq length "$file" 2>/dev/null || echo "N/A") records"
        done
    fi
    
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_shortcode_integration() {
    echo -e "${BLUE}▶ Demo 7: Shortcode System Enhancement${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "The shortcode processor now links to the ${GREEN}enhanced help${NC}:"
    echo ""
    
    echo -e "${CYAN}$ ./uCode/shortcode-processor-simple.sh process '[HELP]'${NC}"
    ./uCode/shortcode-processor-simple.sh process '[HELP]' | head -15
    echo "..."
    echo -e "${YELLOW}[Truncated - shows enhanced help integration]${NC}"
    
    echo ""
    read -p "Press Enter to continue..." -r
    echo ""
}

demo_benefits_summary() {
    echo -e "${BLUE}▶ Summary: Key Benefits of Enhanced Help System${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "✅ ${GREEN}Dataset-Driven:${NC} All commands sourced from structured JSON"
    echo -e "✅ ${GREEN}Template Integration:${NC} Links to comprehensive documentation"
    echo -e "✅ ${GREEN}Cross-Referenced:${NC} Commands connect to related docs and examples"
    echo -e "✅ ${GREEN}Search Capable:${NC} Find commands by name, category, or description"
    echo -e "✅ ${GREEN}Auto-Generated:${NC} Documentation created dynamically from datasets"
    echo -e "✅ ${GREEN}Interactive Mode:${NC} Explore commands through guided interface"
    echo -e "✅ ${GREEN}Extensible:${NC} Easy to add new commands via JSON dataset"
    echo -e "✅ ${GREEN}Consistent:${NC} Standardized help format across all commands"
    echo ""
    echo -e "📊 ${YELLOW}Current Dataset:${NC}"
    if command -v jq >/dev/null 2>&1 && [[ -f "$UHOME/uTemplate/datasets/ucode-commands.json" ]]; then
        local total_commands=$(jq length "$UHOME/uTemplate/datasets/ucode-commands.json")
        local total_categories=$(jq -r '.[].category' "$UHOME/uTemplate/datasets/ucode-commands.json" | sort -u | wc -l)
        echo -e "  • ${CYAN}$total_commands${NC} total commands"
        echo -e "  • ${CYAN}$total_categories${NC} command categories"
        echo -e "  • ${CYAN}Full integration${NC} with uDOS template system"
    fi
    
    echo ""
    echo -e "🚀 ${GREEN}Usage Examples:${NC}"
    echo -e "  • ${CYAN}HELP <command>${NC} - Get detailed help for any command"
    echo -e "  • ${CYAN}./uCode/enhanced-help-system.sh interactive${NC} - Interactive explorer"
    echo -e "  • ${CYAN}./uCode/enhanced-help-system.sh generate${NC} - Create comprehensive docs"
    echo -e "  • ${CYAN}[HELP]${NC} in shortcodes - Access enhanced help system"
    echo ""
}

main() {
    demo_header
    demo_command_help
    demo_category_browsing
    demo_dataset_stats
    demo_comprehensive_docs
    demo_search_functionality
    demo_template_integration
    demo_shortcode_integration
    demo_benefits_summary
    
    echo -e "${BOLD}${GREEN}🎉 Enhanced Help System Demo Complete!${NC}"
    echo ""
    echo -e "The uDOS help system now provides ${YELLOW}comprehensive, dataset-driven${NC}"
    echo -e "command documentation with ${GREEN}template integration${NC} and ${CYAN}cross-references${NC}."
    echo ""
    echo -e "Try it yourself: ${BOLD}HELP <command>${NC} or ${BOLD}./uCode/enhanced-help-system.sh interactive${NC}"
    echo ""
}

# Run demo if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
