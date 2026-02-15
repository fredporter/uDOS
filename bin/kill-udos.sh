#!/bin/bash
# Kill uDOS processes for clean restart

echo "🛑 Stopping uDOS processes..."

# Kill TUI
pkill -f "python.*uDOS.py" 2>/dev/null && echo "  ✓ Stopped uDOS TUI" || echo "  • No TUI running"

# Kill Wizard server
pkill -f "python.*wizard.*server" 2>/dev/null && echo "  ✓ Stopped Wizard server" || echo "  • No Wizard server running"

# Kill any uCLI processes
pkill -f "/bin/ucli" 2>/dev/null && echo "  ✓ Stopped uCLI launcher" || echo "  • No uCLI launcher running"

# Wait a moment
sleep 1

# Check for remaining processes
REMAINING=$(ps aux | grep -E "python.*(uDOS|wizard|ucode)" | grep -v grep | wc -l)

if [ "$REMAINING" -gt 0 ]; then
    echo ""
    echo "⚠️  $REMAINING processes still running:"
    ps aux | grep -E "python.*(uDOS|wizard|ucode)" | grep -v grep
    echo ""
    echo "Force kill? [y/N]"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        pkill -9 -f "python.*(uDOS|wizard|ucode)" 2>/dev/null
        echo "  ✓ Force killed remaining processes"
    fi
else
    echo ""
    echo "✅ All uDOS processes stopped"
fi
