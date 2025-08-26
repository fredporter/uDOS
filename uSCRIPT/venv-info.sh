#!/bin/bash
# Display uSCRIPT environment information
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv/python"

echo "uSCRIPT v1.3.3 Environment Information"
echo "======================================"
echo "Virtual Environment: $VENV_DIR"
echo "Python Version: $(source "$VENV_DIR/bin/activate" && python --version)"
echo "Pip Version: $(source "$VENV_DIR/bin/activate" && pip --version)"

# Setup Homebrew path and check Node.js availability
if [[ -f "/opt/homebrew/bin/brew" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

if command -v node >/dev/null 2>&1; then
    echo "Node.js Version: $(node --version)"
    echo "npm Version: $(npm --version)"
else
    echo "Node.js: Not installed"
fi

echo ""
echo "Installed Packages:"
source "$VENV_DIR/bin/activate"
pip list --format=columns
deactivate
