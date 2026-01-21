#!/bin/bash

# Empire Private Server - TUI Launcher
# Launches the Empire CRM and business intelligence system
# Version: 1.0.0.1

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏛️  Empire Private Server - v1.0.0.1${NC}"
echo "────────────────────────────────────────"

# Check virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not detected${NC}"
    echo "Activating .venv..."
    if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
        source "$PROJECT_ROOT/.venv/bin/activate"
        echo -e "${GREEN}✅ Venv activated${NC}"
    else
        echo -e "${RED}✗ .venv not found at $PROJECT_ROOT/.venv${NC}"
        exit 1
    fi
fi

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"

# Check Empire folder structure
echo ""
echo "Checking Empire structure..."
if [ -f "$PROJECT_ROOT/empire/version.json" ]; then
    VERSION=$(python -c "import json; print(json.load(open('$PROJECT_ROOT/empire/version.json'))['version'])" 2>/dev/null || echo "unknown")
    echo -e "${GREEN}✅ Empire v${VERSION}${NC}"
else
    echo -e "${RED}✗ Empire folder not found or missing version.json${NC}"
    exit 1
fi

# Check required Python modules
echo ""
echo "Checking Python dependencies..."
REQUIRED_MODULES=("sqlite3" "json" "os" "sys")
MISSING=0

for module in "${REQUIRED_MODULES[@]}"; do
    if python -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}  ✓ $module${NC}"
    else
        echo -e "${YELLOW}  ⚠ $module (optional)${NC}"
    fi
done

# Launch Empire Server TUI
echo ""
echo -e "${GREEN}────────────────────────────────────────${NC}"
echo -e "${GREEN}Launching Empire Server TUI...${NC}"
echo -e "${GREEN}────────────────────────────────────────${NC}"
echo ""

cd "$PROJECT_ROOT"

# Try to import and run Empire TUI
python -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')

try:
    from empire.tui import EmpireServerTUI
    server = EmpireServerTUI()
    server.run()
except ImportError:
    print('⚠️  Empire TUI not yet implemented')
    print('Importing core modules...')
    from empire import id_generator, marketing_db
    print('✅ Core modules loaded')
    print('')
    print('Empire server interactive mode:')
    import code
    code.interact(local=globals())
except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
"
