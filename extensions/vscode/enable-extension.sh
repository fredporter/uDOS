#!/bin/bash
# Enable uDOS VS Code Extension in this workspace
#
# Note: Debug configuration is in root .vscode/launch.json
# Use "Run VS Code Extension" launch config to test

EXTENSION_DIR="$HOME/.vscode/extensions/udos.vscode-1.0.0"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 Enabling uDOS VS Code Extension..."

# Remove old symlinks if they exist
for old_link in "$HOME/.vscode/extensions/udos.vscode-udos-1.0.0" "$HOME/.vscode/extensions/udos.vscode-1.0.0"; do
    if [ -L "$old_link" ]; then
        echo "   Removing old symlink: $old_link"
        rm "$old_link"
    fi
done

# Create symlink to extension directory
echo "   Creating symlink: $EXTENSION_DIR -> $SOURCE_DIR"
ln -sf "$SOURCE_DIR" "$EXTENSION_DIR"

# Verify
if [ -L "$EXTENSION_DIR" ]; then
    echo "✅ Extension enabled! Restart VS Code to activate."
    echo ""
    echo "To restart: Cmd+Shift+P → 'Developer: Reload Window'"
    echo "To debug: Use 'Run VS Code Extension' launch config (F5)"
    echo ""
    echo "Debug config location: uDOS/.vscode/launch.json"
else
    echo "❌ Failed to create symlink"
    exit 1
fi
