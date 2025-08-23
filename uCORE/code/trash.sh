#!/bin/bash
# uCODE: TRASH - List and empty trash
set -euo pipefail

BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
trash_dir="$UDOS_ROOT/trash"
if [[ "$1" == "EMPTY" ]]; then
    rm -rf "$trash_dir"/*
    echo -e "${GREEN}✅ Trash emptied${NC}"
else
    echo -e "${BLUE}🗑️  Trash contents:${NC}"
    ls -lh "$trash_dir"
fi
