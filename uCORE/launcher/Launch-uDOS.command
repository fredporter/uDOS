#!/bin/bash
# uDOS macOS Launcher
# Simple, clean launcher that works with VS Code integration

set -e

echo "🌀 uDOS macOS Launcher"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if uDOS directory exists
UDOS_PATH="$HOME/uDOS"
if [[ ! -d "$UDOS_PATH" ]]; then
    echo "❌ uDOS not found at $UDOS_PATH"
    echo "📦 Please clone uDOS first:"
    echo "   git clone https://github.com/fredporter/uDOS.git ~/uDOS"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo "✅ Found uDOS at: $UDOS_PATH"
echo ""

# Check if VS Code is available
if command -v code &> /dev/null; then
    echo "🎯 VS Code detected - offering optimal experience"
    echo ""
    echo "Choose your preferred launch method:"
    echo "  [1] 🆚 Open in VS Code (Recommended)"
    echo "  [2] 🖥️  Terminal only"
    echo "  [3] ❌ Cancel"
    echo ""
    read -p "👉 Your choice (1-3): " choice
    
    case "$choice" in
        1)
            echo "🚀 Opening uDOS in VS Code..."
            cd "$UDOS_PATH"
            code .
            echo "💡 In VS Code: Cmd+Shift+P → '🌀 Start uDOS'"
            ;;
        2)
            echo "🖥️  Launching uDOS in this terminal..."
            cd "$UDOS_PATH"
            exec "$UDOS_PATH/uCORE/launcher/universal/start-udos.sh"
            ;;
        3)
            echo "👋 Cancelled"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
else
    echo "🖥️  VS Code not found - launching uDOS in this terminal..."
    cd "$UDOS_PATH"
    exec "$UDOS_PATH/uCORE/launcher/universal/start-udos.sh"
fi

echo ""
echo "✨ uDOS launcher completed"
