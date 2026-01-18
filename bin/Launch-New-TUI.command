#!/bin/bash
#
# Launch New TUI
# Lightweight CLI interface for uDOS (Phase 5G + 6A)
#
# Usage: ./bin/Launch-New-TUI.command
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🧙 uDOS New TUI Launcher${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check virtual environment
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "Please run: python3 -m venv .venv"
    exit 1
fi

# Activate venv
echo "📦 Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Set PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Check Python
echo "🐍 Checking Python..."
python --version

# Check core.tui module
echo ""
echo "🔍 Checking core.tui module..."
if ! python -c "from core.tui import TUIRepl" 2>/dev/null; then
    echo "❌ core.tui module not found"
    echo "Make sure you're in the project root and the module is installed"
    exit 1
fi
echo "✅ core.tui module found"

# Launch
echo ""
echo -e "${GREEN}🚀 Launching uDOS TUI...${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Navigation:  MAP, PANEL, GOTO, FIND, TELL"
echo "🎒 Inventory:   BAG, GRAB, SPAWN"
echo "👥 NPCs:        NPC, TALK, REPLY"
echo "💾 State:       SAVE, LOAD"
echo "🔧 System:      HELP, SHAKEDOWN, REPAIR"
echo "⌨️  Special:     STATUS, HISTORY, CLEAR, QUIT"
echo ""

cd "$PROJECT_ROOT"
python -m core.tui

echo ""
echo -e "${GREEN}✅ TUI Closed${NC}"
