#!/bin/bash
# macOS Installation Script for uDOS Launcher

echo "🍎 Installing uDOS macOS Launcher..."

# Get uDOS root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "📂 uDOS Root: $UDOS_ROOT"

# Make launcher executable
chmod +x "$SCRIPT_DIR/uDOS.command"
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-dev.sh"
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/detect-platform.sh"

echo "✅ Made launcher scripts executable"

# Create symbolic link in user's Desktop (optional)
read -p "📍 Create shortcut on Desktop? (y/N): " create_desktop
if [[ "$create_desktop" =~ ^[Yy]$ ]]; then
    ln -sf "$SCRIPT_DIR/uDOS.command" "$HOME/Desktop/Launch uDOS.command"
    echo "✅ Desktop shortcut created"
fi

# Create symbolic link in Applications (optional)
read -p "📱 Create shortcut in Applications? (y/N): " create_applications
if [[ "$create_applications" =~ ^[Yy]$ ]]; then
    ln -sf "$SCRIPT_DIR/uDOS.command" "/Applications/Launch uDOS.command"
    echo "✅ Applications shortcut created"
fi

echo ""
echo "🎉 macOS launcher installation complete!"
echo ""
echo "Usage:"
echo "  • Double-click: $SCRIPT_DIR/uDOS.command"
if [[ "$create_desktop" =~ ^[Yy]$ ]]; then
    echo "  • Desktop: Launch uDOS.command"
fi
if [[ "$create_applications" =~ ^[Yy]$ ]]; then
    echo "  • Applications: Launch uDOS.command"
fi
