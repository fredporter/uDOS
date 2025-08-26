#!/bin/bash
# uCODE: LIST - Show directory contents with simple formatting
set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

# Function to show directory contents
show_directory_contents() {
    local target_path="$1"

    # Convert relative paths to absolute
    if [ ! "$target_path" = /* ]; then
        target_path="$UDOS_ROOT/$target_path"
    fi

    if [ ! -d "$target_path" ]; then
        echo -e "${YELLOW}⚠️  Directory not found: $target_path${NC}"
        return 1
    fi

    echo -e "${BLUE}📁 Contents of: $target_path${NC}"
    echo "$(printf '%.0s─' {1..50})"

    # Show directories first, then files
    if command -v ls >/dev/null 2>&1; then
        # Use ls with color if available
        ls -la --color=auto "$target_path" 2>/dev/null || ls -la "$target_path"
    else
        # Fallback to basic ls
        ls -la "$target_path"
    fi
}

# Main execution
if [ $# -eq 0 ]; then
    # No arguments - show current directory or uDOS root
    show_directory_contents "$(pwd)"
elif [ $# -eq 1 ]; then
    # Single argument - show specified directory
    show_directory_contents "$1"
else
    echo -e "${YELLOW}Usage: list [directory_path]${NC}"
    echo ""
    echo "Examples:"
    echo "  list                    # Show current directory"
    echo "  list uMEMORY/user      # Show uMEMORY/user contents"
    echo "  list /absolute/path     # Show absolute path"
    exit 1
fi
