#!/bin/bash
# 🌀 uDOS macOS Launcher v1.3.3
# Simple one-click launcher for macOS

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UDOS_ROOT="$SCRIPT_DIR"

# Color definitions
readonly CYAN='\033[0;36m'
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

echo -e "${CYAN}🌀 Launching uDOS...${NC}"

# Check if we're in the right place
if [[ ! -f "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" ]]; then
    echo -e "${RED}❌ uDOS not found in current directory${NC}"
    echo "Please run this script from the uDOS root directory"
    exit 1
fi

# Make sure the launcher is executable
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"

echo -e "${GREEN}✅ Starting uDOS...${NC}"

# Launch uDOS
exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
