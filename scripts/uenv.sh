#!/usr/bin/env bash
#
# uDOS Environment Setup
# Source this script to activate the uDOS development environment
#
# Usage:
#   source scripts/uenv.sh
#   . scripts/uenv.sh
#

# Determine uDOS root directory
if [[ -n "$BASH_SOURCE" ]]; then
    UDOS_HOME="$(cd "$(dirname "$BASH_SOURCE")/.." && pwd)"
elif [[ -n "$ZSH_VERSION" ]]; then
    UDOS_HOME="$(cd "$(dirname "$0")/.." && pwd)"
else
    UDOS_HOME="$(pwd)"
fi

# Export environment variables
export UDOS_HOME
export UDOS_VERSION="1.1.9"

# Add bin directory to PATH (if not already there)
if [[ ":$PATH:" != *":$UDOS_HOME/bin:"* ]]; then
    export PATH="$UDOS_HOME/bin:$PATH"
fi

# Activate virtual environment if it exists
if [[ -f "$UDOS_HOME/.venv/bin/activate" ]]; then
    source "$UDOS_HOME/.venv/bin/activate"
    echo "✅ uDOS environment active (v$UDOS_VERSION)"
    echo "   UDOS_HOME: $UDOS_HOME"
    echo "   Virtual env: $(which python)"
else
    echo "⚠️  Virtual environment not found at $UDOS_HOME/.venv"
    echo "   Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
fi

# Set up shell aliases (optional)
alias udos-home="cd $UDOS_HOME"
alias udos-logs="tail -f $UDOS_HOME/sandbox/logs/dev.log"
alias udos-test="pytest $UDOS_HOME/sandbox/tests/ -v"

# Function to show uDOS environment info
udos-env() {
    echo "uDOS Environment Information:"
    echo "  Version: $UDOS_VERSION"
    echo "  Home: $UDOS_HOME"
    echo "  Python: $(which python)"
    echo "  Virtual env: ${VIRTUAL_ENV:-Not active}"
    echo ""
    echo "Aliases:"
    echo "  udos-home   - Change to uDOS directory"
    echo "  udos-logs   - Tail development logs"
    echo "  udos-test   - Run test suite"
}

# Show completion message
echo ""
echo "Type 'udos-env' for environment information"
