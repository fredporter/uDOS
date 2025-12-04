#!/bin/bash
# Enable uDOS VS Code Extension in this workspace

EXTENSION_DIR="$HOME/.vscode/extensions/udos.vscode-udos-1.0.0"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 Enabling uDOS VS Code Extension..."

# Remove old symlink if exists
if [ -L "$EXTENSION_DIR" ]; then
    echo "   Removing old symlink..."
    rm "$EXTENSION_DIR"
fi

# Create symlink to extension directory
echo "   Creating symlink: $EXTENSION_DIR -> $SOURCE_DIR"
ln -sf "$SOURCE_DIR" "$EXTENSION_DIR"

# Verify
if [ -L "$EXTENSION_DIR" ]; then
    echo "✅ Extension enabled! Restart VS Code to activate."
    echo ""
    echo "To restart: Cmd+Shift+P → 'Developer: Reload Window'"
else
    echo "❌ Failed to create symlink"
    exit 1
fi
