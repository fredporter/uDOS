#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# uDOS Self-Healing System
# ═══════════════════════════════════════════════════════════════════════════
#
# Run diagnostics and auto-repair common issues:
#   - Missing dependencies
#   - Port conflicts
#   - File permissions
#   - Deprecated code warnings
#
# Usage:
#   ./bin/udos-self-heal.sh [component] [--no-repair]
#
# Examples:
#   ./bin/udos-self-heal.sh wizard          # Check and repair Wizard
#   ./bin/udos-self-heal.sh goblin --no-repair  # Check only, no repairs
#   ./bin/udos-self-heal.sh                 # Check all components

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$UDOS_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# Parse args
COMPONENT="${1:-all}"
AUTO_REPAIR="yes"

if [[ "$2" == "--no-repair" ]] || [[ "$1" == "--no-repair" ]]; then
    AUTO_REPAIR="no"
    if [[ "$1" == "--no-repair" ]]; then
        COMPONENT="all"
    fi
fi

# Ensure venv is activated
if [ ! -f "$UDOS_ROOT/.venv/bin/activate" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Run: python3 -m venv .venv"
    exit 1
fi

source "$UDOS_ROOT/.venv/bin/activate"

# Header
echo ""
echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║                  uDOS Self-Healing System                     ║${NC}"
echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${DIM}Component: ${BOLD}${COMPONENT}${NC}"
echo -e "${DIM}Auto-repair: ${BOLD}${AUTO_REPAIR}${NC}"
echo ""

# Function to run self-heal for a component
run_self_heal() {
    local comp="$1"

    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}${BOLD}  Checking: ${comp}${NC}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if [ "$AUTO_REPAIR" == "yes" ]; then
        python -m core.services.self_healer "$comp"
    else
        python -m core.services.self_healer "$comp" --no-repair
    fi

    local exit_code=$?
    echo ""

    return $exit_code
}

# Run checks
COMPONENTS=()
if [ "$COMPONENT" == "all" ]; then
    COMPONENTS=("core" "wizard" "goblin")
else
    COMPONENTS=("$COMPONENT")
fi

EXIT_CODE=0
for comp in "${COMPONENTS[@]}"; do
    if ! run_self_heal "$comp"; then
        EXIT_CODE=1
    fi
done

# Summary
echo ""
echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}${BOLD}  ✅ System healthy!${NC}"
else
    echo -e "${YELLOW}${BOLD}  ⚠️  Some issues require attention${NC}"
    echo ""
    echo -e "${DIM}  Re-run with ${BOLD}--no-repair${DIM} to see details without changes${NC}"
fi
echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

exit $EXIT_CODE
