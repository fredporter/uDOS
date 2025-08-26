#!/bin/bash
# uSCRIPT Full Development Environment Activation
# Activates Python venv + Node.js/npm + Homebrew path

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Activating uSCRIPT Development Environment...${NC}"

# Setup Homebrew path (for Node.js/npm)
if [[ -f "/opt/homebrew/bin/brew" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo -e "${GREEN}✅ Homebrew environment loaded${NC}"
else
    echo -e "${GREEN}⚠️  Homebrew not found - Node.js commands may not be available${NC}"
fi

# Setup Rust environment (for Tauri development)
if [[ -f "$HOME/.cargo/env" ]]; then
    source "$HOME/.cargo/env"
    echo -e "${GREEN}✅ Rust environment loaded${NC}"
else
    echo -e "${GREEN}⚠️  Rust not found - Tauri development may not be available${NC}"
fi

# Activate Python virtual environment
source "$SCRIPT_DIR/venv/python/bin/activate"
echo -e "${GREEN}✅ Python virtual environment activated${NC}"

# Display environment info
echo ""
echo -e "${BLUE}📋 Development Environment Ready:${NC}"
echo "  Python: $(python --version)"
echo "  Pip: $(pip --version | cut -d' ' -f1-2)"
if command -v node >/dev/null 2>&1; then
    echo "  Node.js: $(node --version)"
    echo "  npm: $(npm --version)"
else
    echo "  Node.js: Not available"
fi
if command -v rustc >/dev/null 2>&1; then
    echo "  Rust: $(rustc --version | cut -d' ' -f1-2)"
    echo "  Cargo: $(cargo --version | cut -d' ' -f1-2)"
else
    echo "  Rust: Not available"
fi

echo ""
echo -e "${GREEN}💡 Environment is ready for uDOS development!${NC}"
echo "   • Python scripts will use the virtual environment"
echo "   • Node.js/npm commands are available for Tauri development"
echo "   • Rust/Cargo commands are available for Tauri backend"
echo "   • Use 'deactivate' to exit the Python environment"
echo ""
