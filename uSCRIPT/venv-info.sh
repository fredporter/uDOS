#!/bin/bash
# Display uSCRIPT environment information
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv/python"

echo "uSCRIPT v1.3.3 Environment Information"
echo "======================================"
echo "Virtual Environment: $VENV_DIR"
echo "Python Version: $(source "$VENV_DIR/bin/activate" && python --version)"
echo "Pip Version: $(source "$VENV_DIR/bin/activate" && pip --version)"
echo ""
echo "Installed Packages:"
source "$VENV_DIR/bin/activate"
pip list --format=columns
deactivate
