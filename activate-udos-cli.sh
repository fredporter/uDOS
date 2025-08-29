#!/bin/bash
# uDOS CLI Auto-Startup Script
# Launches the enhanced CLI interface automatically

# Optional: Source environment setup if needed
if [ -f "$HOME/uDOS/activate-udos-env.sh" ]; then
    source "$HOME/uDOS/activate-udos-env.sh"
fi

# Run variable system optimizer if needed
if [ -f "$HOME/uDOS/uCORE/code/variable-system-optimizer.sh" ]; then
    bash "$HOME/uDOS/uCORE/code/variable-system-optimizer.sh"
fi

# Launch the enhanced CLI interface
exec bash "$HOME/uDOS/uCORE/launcher/universal/cli-interface-enhanced.sh"
