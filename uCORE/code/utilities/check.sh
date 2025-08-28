#!/bin/bash
# uCODE: CHECK - Health companion for DASH and RESTORE

set -euo pipefail

# Color definitions
CYAN='\033[0;36m'
NC='\033[0m'

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo -e "${CYAN}🔎 System Health Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Disk: $(df -h $UDOS_ROOT | tail -1 | awk '{print $4}') available"
echo "Memory: $(free -h 2>/dev/null || vm_stat)"
echo "Python: $(python3 --version 2>&1)"
echo "Bash: $BASH_VERSION"
echo "User: $(whoami)"
