#!/bin/bash
# uCORE: BACKUP - Create backup using enhanced backup system
set -euo pipefail

# Get script directory and uDOS root
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_HANDLER="$UDOS_ROOT/uCO../backup-handler.sh"

# Use enhanced backup handler if available, otherwise simple backup
if [ -f "$BACKUP_HANDLER" ]; then
    # Use enhanced backup with encryption and role-based features
    "$BACKUP_HANDLER" BACKUP CREATE "${1:-manual}" "${2:-uCORE backup command}"
else
    # Fallback to simple backup
    GREEN='\033[0;32m'
    NC='\033[0m'
    src="${1:-$UDOS_ROOT}"
    dest="$UDOS_ROOT/backup"
    mkdir -p "$dest"
    tar czf "$dest/backup-$(date +%Y%m%d-%H%M%S).tar.gz" -C "$src" .
    echo -e "${GREEN}✅ Backup created at $dest${NC}"
fi# uCODE: BACKUP - Create backup of system/user data
set -euo pipefail

GREEN='\033[0;32m'
NC='\033[0m'
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
src="${1:-$UDOS_ROOT}"
dest="${2:-$UDOS_ROOT/backup}"
mkdir -p "$dest"
tar czf "$dest/backup-$(date +%Y%m%d-%H%M%S).tar.gz" -C "$src" .
echo -e "${GREEN}✅ Backup created at $dest${NC}"
