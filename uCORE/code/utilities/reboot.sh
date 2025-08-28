#!/bin/bash
# uCODE: REBOOT - Reboot uDOS system (soft)
set -euo pipefail

YELLOW='\033[1;33m'
NC='\033[0m'
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo -e "${YELLOW}🔄 Rebooting uDOS...${NC}"
exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
