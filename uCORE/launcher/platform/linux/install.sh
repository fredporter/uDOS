#!/bin/bash
# Linux Installation Script for uDOS Launcher

echo "🐧 Installing uDOS Linux Launcher..."

# Get uDOS root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "📂 uDOS Root: $UDOS_ROOT"

# Make launcher executable
chmod +x "$SCRIPT_DIR/uDOS.sh"
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh"
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/start-dev.sh"
chmod +x "$UDOS_ROOT/uCORE/launcher/universal/detect-platform.sh"

echo "✅ Made launcher scripts executable"

# Update desktop file with correct paths
DESKTOP_FILE="$SCRIPT_DIR/uDOS.desktop"
DESKTOP_FILE_UPDATED="$SCRIPT_DIR/uDOS-updated.desktop"

# Replace placeholder paths with actual paths
sed "s|/home/%u/uDOS|$UDOS_ROOT|g" "$DESKTOP_FILE" > "$DESKTOP_FILE_UPDATED"

echo "✅ Updated desktop file paths"

# Install desktop file
read -p "📱 Install desktop launcher for current user? (Y/n): " install_desktop
if [[ "$install_desktop" != "n" && "$install_desktop" != "N" ]]; then
    # Create desktop applications directory if it doesn't exist
    mkdir -p "$HOME/.local/share/applications"
    
    # Copy desktop file
    cp "$DESKTOP_FILE_UPDATED" "$HOME/.local/share/applications/udos.desktop"
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$HOME/.local/share/applications"
    fi
    
    echo "✅ Desktop launcher installed"
fi

# Create desktop shortcut
read -p "📍 Create shortcut on Desktop? (y/N): " create_desktop
if [[ "$create_desktop" =~ ^[Yy]$ ]]; then
    cp "$DESKTOP_FILE_UPDATED" "$HOME/Desktop/uDOS.desktop"
    chmod +x "$HOME/Desktop/uDOS.desktop"
    echo "✅ Desktop shortcut created"
fi

# System-wide installation (requires sudo)
read -p "🌐 Install system-wide for all users? (requires sudo) (y/N): " install_system
if [[ "$install_system" =~ ^[Yy]$ ]]; then
    if command -v sudo >/dev/null 2>&1; then
        sudo cp "$DESKTOP_FILE_UPDATED" "/usr/share/applications/udos.desktop"
        
        if command -v update-desktop-database >/dev/null 2>&1; then
            sudo update-desktop-database /usr/share/applications
        fi
        
        echo "✅ System-wide installation complete"
    else
        echo "❌ sudo not available, skipping system-wide installation"
    fi
fi

# Create command line alias
read -p "⚡ Create 'udos' command alias in shell? (Y/n): " create_alias
if [[ "$create_alias" != "n" && "$create_alias" != "N" ]]; then
    # Detect shell and add alias
    SHELL_CONFIG=""
    case "$SHELL" in
        */bash)
            SHELL_CONFIG="$HOME/.bashrc"
            ;;
        */zsh)
            SHELL_CONFIG="$HOME/.zshrc"
            ;;
        */fish)
            SHELL_CONFIG="$HOME/.config/fish/config.fish"
            ;;
    esac
    
    if [ -n "$SHELL_CONFIG" ] && [ -f "$SHELL_CONFIG" ]; then
        # Check if alias already exists
        if ! grep -q "alias udos=" "$SHELL_CONFIG" 2>/dev/null; then
            echo "" >> "$SHELL_CONFIG"
            echo "# uDOS launcher alias" >> "$SHELL_CONFIG"
            echo "alias udos='$UDOS_ROOT/uCORE/launcher/universal/start-udos.sh'" >> "$SHELL_CONFIG"
            echo "alias udos-dev='$UDOS_ROOT/uCORE/launcher/universal/start-dev.sh'" >> "$SHELL_CONFIG"
            
            echo "✅ Shell aliases added to $SHELL_CONFIG"
            echo "💡 Run 'source $SHELL_CONFIG' or restart terminal to use 'udos' command"
        else
            echo "✅ Shell aliases already exist"
        fi
    else
        echo "⚠️  Shell configuration file not found, manual alias setup required"
    fi
fi

# Clean up temporary file
rm -f "$DESKTOP_FILE_UPDATED"

echo ""
echo "🎉 Linux launcher installation complete!"
echo ""
echo "Usage:"
echo "  • GUI: Applications menu > uDOS"
echo "  • Terminal: $SCRIPT_DIR/uDOS.sh"
if [[ "$create_desktop" =~ ^[Yy]$ ]]; then
    echo "  • Desktop: uDOS.desktop"
fi
if [[ "$create_alias" != "n" && "$create_alias" != "N" ]]; then
    echo "  • Command: udos (after shell restart)"
fi

echo ""
echo "Development mode:"
echo "  • Command: udos-dev (after shell restart)"
echo "  • Direct: $UDOS_ROOT/uCORE/launcher/universal/start-dev.sh"
