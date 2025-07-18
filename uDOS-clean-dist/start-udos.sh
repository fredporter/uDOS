#!/bin/bash
# Simple uDOS launcher - no Docker required
# Modern VS Code + Copilot integrated version

echo "🌀 Modern uDOS Launcher"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we're in VS Code
if [[ "$TERM_PROGRAM" == "vscode" ]]; then
    echo "✅ Running in VS Code - optimal environment detected"
    echo "💡 Use Cmd+Shift+P → '🌀 Start uDOS' for best experience"
    echo ""
else
    echo "💡 For best experience, open this folder in VS Code"
    echo "   code ~/uDOS"
    echo ""
fi

# Check dependencies
if ! command -v bash &> /dev/null; then
    echo "❌ bash not found"
    exit 1
fi

echo "🚀 Launching uDOS native shell..."
echo ""

# Launch uDOS
exec ./uCode/ucode.sh
