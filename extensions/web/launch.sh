#!/bin/bash
#
# uDOS Web Extensions v1.0.1 - Quick Launcher
# ============================================
#
# Simple wrapper script for the Python deployment manager
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   uDOS Web Extensions v1.0.1                ║"
    echo "║                     Quick Launcher                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to check Python
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi
}

# Main execution
main() {
    print_banner
    check_python
    
    # Pass all arguments to the Python script
    cd "$SCRIPT_DIR"
    python3 deploy.py "$@"
}

# Help function
show_help() {
    echo -e "${YELLOW}uDOS Web Extensions v1.0.1 - Quick Launcher${NC}"
    echo ""
    echo -e "${GREEN}Usage:${NC}"
    echo "  ./launch.sh [command]"
    echo ""
    echo -e "${GREEN}Commands:${NC}"
    echo "  start     Start all web extensions (default)"
    echo "  stop      Stop all running extensions"
    echo "  status    Show extension status"
    echo "  help      Show this help message"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo "  ./launch.sh           # Start all extensions"
    echo "  ./launch.sh start     # Start all extensions"
    echo "  ./launch.sh status    # Check status"
    echo "  ./launch.sh stop      # Stop all extensions"
    echo ""
    echo -e "${BLUE}💡 Tip: The Python deployment manager provides more detailed output${NC}"
}

# Handle command line arguments
case "${1:-start}" in
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        main "$@"
        ;;
esac