#!/bin/bash
# uCODE: RESTORE - Restore from backup
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
backup_file="${1:-}" # Path to backup file
restore_dir="${2:-$UDOS_ROOT}"
if [ -z "$backup_file" || ! -f "$backup_file" ]; then
    echo -e "${RED}❌ Backup file not found${NC}"
    exit 1
fi
mkdir -p "$restore_dir"
tar xzf "$backup_file" -C "$restore_dir"
echo -e "${GREEN}✅ Restored backup to $restore_dir${NC}"
