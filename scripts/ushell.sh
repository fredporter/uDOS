#!/bin/bash
echo "🌀 Welcome to uShell"
echo "Connected to uOS container as: $(whoami)"
echo "uKnowledge mounted at: /uKnowledge"
echo "Logging Moves to: /uKnowledge/logs"
exec ./src/ulog.sh
echo "Type 'exit' to leave the shell."

# Start interactive bash shell
exec bash