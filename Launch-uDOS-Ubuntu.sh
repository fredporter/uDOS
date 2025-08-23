#!/bin/bash
# 🌀 uDOS Ubuntu 22 Launcher v1.3.3
# Simple one-click launcher for Ubuntu 22.04+

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UDOS_ROOT="$SCRIPT_DIR"

# Color definitions
readonly CYAN='\033[0;36m'
readonly GREEN='\033[0;32m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

echo -e "${CYAN}🌀 Launching uDOS on Ubuntu...${NC}"

# Check if we're in the right place
if [[ ! -f "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh" ]]; then
    echo -e "${RED}❌ uDOS not found in current directory${NC}"
    echo "Please run this script from the uDOS root directory"
    exit 1
fi

# Check for required dependencies
echo -e "${YELLOW}🔍 Checking dependencies...${NC}"

# Check for bash
if ! command -v bash >/dev/null 2>&1; then
    echo -e "${RED}❌ Bash not found${NC}"
    echo "Please install bash: sudo apt update && sudo apt install bash"
    exit 1
fi

# Check for python3
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Python3 not found, installing...${NC}"
    sudo apt update && sudo apt install python3 python3-pip -y
fi

# Check for git
if ! command -v git >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Git not found, installing...${NC}"
    sudo apt update && sudo apt install git -y
fi

# Make sure the launcher is executable
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"

echo -e "${GREEN}✅ Starting uDOS...${NC}"

# Launch uDOS
exec "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
