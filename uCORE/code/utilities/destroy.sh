#!/bin/bash
# uCORE Simple DESTROY - Basic file removal with trash backup
set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Get uDOS root directory
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
TRASH_DIR="$UDOS_ROOT/trash"

if [ $# -eq 0 ]; then
    echo "Usage: destroy <file_or_directory>"
    echo "Note: Items are moved to trash, not permanently deleted"
    exit 1
fi

target="$1"

# Convert relative paths to absolute
if [ ! "$target" = /* ]; then
    target="$(pwd)/$target"
fi

if [ ! -e "$target" ]; then
    echo -e "${RED}❌ File or directory not found: $target${NC}"
    exit 1
fi

# Create trash directory if needed
mkdir -p "$TRASH_DIR"

# Generate timestamp for trash
timestamp=$(date +"%Y%m%d-%H%M%S")
basename_target=$(basename "$target")
trash_name="${timestamp}_${basename_target}"

# Move to trash
mv "$target" "$TRASH_DIR/$trash_name"

echo -e "${GREEN}🗑️  Moved to trash: $basename_target${NC}"
echo -e "${YELLOW}💡 To restore: mv '$TRASH_DIR/$trash_name' '$target'${NC}"
