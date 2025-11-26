#!/bin/bash
# Extension Launcher v1.0.25 - Uses unified extensions server
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXT_NAME="$(basename "$SCRIPT_DIR")"
cd "$SCRIPT_DIR/.."
echo "🎮 Starting $EXT_NAME Extension..."
python3 extensions_server.py "$EXT_NAME"
