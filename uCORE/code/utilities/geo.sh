#!/bin/bash
# uCORE Simple GEO - Basic geographic operations
set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

# Get uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
GEO_DIR="$UDOS_ROOT/uMEMORY/system/geo"

case "${1:-list}" in
    list|LIST)
        echo -e "${BLUE}📍 Available geographic data:${NC}"
        echo "Maps:"
        ls -1 "$GEO_DIR/maps/" 2>/dev/null | head -5 || echo "  No maps found"
        echo "Tiles:"
        ls -1 "$GEO_DIR/tiles/" 2>/dev/null | head -5 || echo "  No tiles found"
        ;;
    show|SHOW)
        if [ -n "${2:-}" ]; then
            echo -e "${BLUE}📍 Geographic file: $2${NC}"
            if [ -f "$GEO_DIR/maps/$2" ]; then
                head -20 "$GEO_DIR/maps/$2"
            elif [ -f "$GEO_DIR/tiles/$2" ]; then
                head -20 "$GEO_DIR/tiles/$2"
            else
                echo "File not found: $2"
            fi
        else
            echo "Usage: geo show <filename>"
        fi
        ;;
    *)
        echo "Simple GEO commands:"
        echo "  geo list    - Show available maps and tiles"
        echo "  geo show    - Display geographic file content"
        ;;
esac
