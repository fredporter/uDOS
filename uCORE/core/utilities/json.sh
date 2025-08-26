#!/bin/bash
# uCORE Simple JSON - Basic JSON operations
set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

case "${1:-help}" in
    validate|VALIDATE)
        if [ -n "${2:-}" ]; then
            echo -e "${BLUE}📄 Validating JSON: $2${NC}"
            if command -v python3 >/dev/null 2>&1; then
                python3 -m json.tool "$2" >/dev/null && echo -e "${GREEN}✅ Valid JSON${NC}" || echo -e "${YELLOW}❌ Invalid JSON${NC}"
            elif command -v jq >/dev/null 2>&1; then
                jq empty "$2" >/dev/null && echo -e "${GREEN}✅ Valid JSON${NC}" || echo -e "${YELLOW}❌ Invalid JSON${NC}"
            else
                echo "JSON validation requires python3 or jq"
            fi
        else
            echo "Usage: json validate <file.json>"
        fi
        ;;
    convert|CONVERT)
        if [ -n "${2:-}" && -n "${3:-}" ]; then
            echo -e "${BLUE}🔄 Converting: $2 → $3${NC}"
            bash "$UDOS_ROOT/uCORE/json/convert-to-udata.sh" "$2" "$3"
        else
            echo "Usage: json convert <input.json> <output.json>"
        fi
        ;;
    show|SHOW)
        if [ -n "${2:-}" ]; then
            echo -e "${BLUE}📄 JSON content: $2${NC}"
            if command -v jq >/dev/null 2>&1; then
                jq . "$2" 2>/dev/null || cat "$2"
            else
                cat "$2"
            fi
        else
            echo "Usage: json show <file.json>"
        fi
        ;;
    *)
        echo "Simple JSON commands:"
        echo "  json validate <file>    - Check if JSON is valid"
        echo "  json convert <in> <out> - Convert to uDATA format"
        echo "  json show <file>        - Display formatted JSON"
        ;;
esac
