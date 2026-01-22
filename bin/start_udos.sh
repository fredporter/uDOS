#!/bin/bash

# uDOS Core TUI Launcher - Minimal Edition
# TUI only - no GUI, no API keys, no web extensions

set -e

# Resolve script location and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$UDOS_ROOT"

# Centralized logs
export UDOS_LOG_DIR="$UDOS_ROOT/memory/logs"
mkdir -p "$UDOS_LOG_DIR"

# Data directories (memory-based)
mkdir -p "$UDOS_ROOT/memory/ucode/sandbox" "$UDOS_ROOT/memory/ucode/scripts" "$UDOS_ROOT/memory/logs" "$UDOS_ROOT/memory/drafts" 2>/dev/null

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Get version
if [ -f "$UDOS_ROOT/core/version.json" ]; then
    UDOS_VERSION=$(python3 -c "import json, pathlib; p=pathlib.Path('$UDOS_ROOT')/'core'/'version.json'; v=json.load(open(p))['version']; print(f\"v{v['major']}.{v['minor']}.{v['patch']}.{v['build']}\")" 2>/dev/null || echo "v1.0.0.0")
else
    UDOS_VERSION="v1.0.0.0"
fi

echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${MAGENTA}🎮 uDOS Core TUI ${UDOS_VERSION}${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Python check (minimum 3.8)
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        print_error "Python $PYTHON_VERSION too old (need >=3.8)"
        exit 1
    fi
    print_success "Python $PYTHON_VERSION"
else
    print_error "Python 3 not found"
    exit 1
fi

# Virtual environment
if [ ! -d "$UDOS_ROOT/.venv" ]; then
    echo -e "${BLUE}[→]${NC} Creating venv..."
    python3 -m venv "$UDOS_ROOT/.venv"
fi

source "$UDOS_ROOT/.venv/bin/activate"
print_success "Virtual environment activated"

# Dependencies (silent)
pip install -q -r "$UDOS_ROOT/requirements.txt" 2>/dev/null || true
print_success "Dependencies ready"

# Launch core TUI
echo ""
python uDOS.py "$@"

deactivate
