#!/bin/bash
# uSCRIPT Unified Development Environment Activation
# Activates Python venv + Rust environment + optional Node.js - all within uSCRIPT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🚀 Activating uSCRIPT Unified Development Environment...${NC}"

# 1. Setup Python virtual environment
if [[ -f "$SCRIPT_DIR/venv/python/bin/activate" ]]; then
    source "$SCRIPT_DIR/venv/python/bin/activate"
    echo -e "${GREEN}✅ Python virtual environment activated${NC}"
else
    echo -e "${YELLOW}⚠️  Python venv not found - run ./setup-environment.sh first${NC}"
fi

# 2. Setup Rust environment (if exists)
if [[ -f "$SCRIPT_DIR/venv/rust/env/cargo-env" ]]; then
    source "$SCRIPT_DIR/venv/rust/env/cargo-env"
    echo -e "${GREEN}✅ Rust environment loaded (uSCRIPT managed)${NC}"
elif [[ -f "$HOME/.cargo/env" ]]; then
    source "$HOME/.cargo/env"
    echo -e "${GREEN}✅ Rust environment loaded (system)${NC}"
else
    echo -e "${YELLOW}⚠️  Rust not available - install via ./setup-native-dev.sh if needed${NC}"
fi

# 3. Setup Homebrew/Node.js (if available and needed)
if [[ -f "/opt/homebrew/bin/brew" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    if command -v node >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Node.js environment loaded${NC}"
    fi
fi

# Display comprehensive environment info
echo ""
echo -e "${BLUE}📋 uSCRIPT Unified Development Environment:${NC}"

# Python info
if command -v python >/dev/null 2>&1; then
    echo "  🐍 Python: $(python --version)"
    echo "  📦 Pip: $(pip --version | cut -d' ' -f1-2)"
else
    echo "  🐍 Python: Not available"
fi

# Rust info
if command -v rustc >/dev/null 2>&1; then
    echo "  🦀 Rust: $(rustc --version | cut -d' ' -f1-2)"
    echo "  📦 Cargo: $(cargo --version | cut -d' ' -f1-2)"
    if [[ -n "$CARGO_HOME" ]]; then
        echo "    └─ CARGO_HOME: $CARGO_HOME"
    fi
else
    echo "  🦀 Rust: Not available"
fi

# Node.js info (optional)
if command -v node >/dev/null 2>&1; then
    echo "  🟢 Node.js: $(node --version)"
    echo "  📦 npm: $(npm --version)"
else
    echo "  🟢 Node.js: Not installed (optional)"
fi

echo ""
echo -e "${GREEN}💡 uSCRIPT Environment Ready!${NC}"
echo "   🐍 Python scripts will use the virtual environment"
echo "   🦀 Rust/Cargo commands available for Tauri development"
echo "   🟢 Node.js available for frontend development (if installed)"
echo "   🔧 All tools managed within uSCRIPT namespace"
echo ""
echo -e "${BLUE}Available development commands:${NC}"
echo "   ./runtime/process-manager.sh status    # Check process status"
echo "   ./runtime/process-manager.sh start-server  # Start uDOS server"
echo "   deactivate                            # Exit Python environment"
echo ""
