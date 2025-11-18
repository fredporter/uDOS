#!/bin/bash
# uDOS Core Extensions Unified Launcher v1.0.25

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
CYAN='\033[1;36m'
YELLOW='\033[1;33m'
GREEN='\033[1;32m'
RED='\033[1;31m'
RESET='\033[0m'

echo -e "\n${CYAN}${'='*60}${RESET}"
echo -e "${CYAN}🎮 uDOS Core Extensions Launcher v1.0.25${RESET}"
echo -e "${CYAN}${'='*60}${RESET}\n"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 not found${RESET}"
    echo -e "${YELLOW}Please install Python 3 to continue${RESET}\n"
    exit 1
fi

# Parse arguments
EXTENSION="${1:-all}"
PORT="$2"

# Show help
if [[ "$EXTENSION" == "-h" ]] || [[ "$EXTENSION" == "--help" ]]; then
    echo "Usage: $0 [extension] [port]"
    echo ""
    echo "Extensions:"
    echo "  all         - Status page (default)"
    echo "  dashboard   - Dashboard Builder"
    echo "  teletext    - Teletext Interface"
    echo "  terminal    - C64 Terminal"
    echo "  markdown    - Markdown Viewer"
    echo "  character   - Character Editor"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run status page on port 8888"
    echo "  $0 dashboard          # Run dashboard on port 8888"
    echo "  $0 teletext 9002      # Run teletext on port 9002"
    echo ""
    exit 0
fi

# List extensions
if [[ "$EXTENSION" == "-l" ]] || [[ "$EXTENSION" == "--list" ]]; then
    python3 extensions_server.py --list
    exit 0
fi

# Run server
if [[ -z "$PORT" ]]; then
    python3 extensions_server.py "$EXTENSION"
else
    python3 extensions_server.py "$EXTENSION" --port "$PORT"
fi
