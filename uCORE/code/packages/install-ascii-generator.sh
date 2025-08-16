#!/bin/bash
# ASCII Generator Installation Script for uDOS
# Source: https://github.com/vietnh1009/ASCII-generator

set -e

PACKAGE_NAME="ascii-generator"
REPO_URL="https://github.com/vietnh1009/ASCII-generator.git"
INSTALL_DIR="$HOME/.local/bin"
UDOS_PACKAGES_DIR="$HOME/uDOS/uCode/packages"

echo ""
echo "📦 Installing ASCII Generator for uDOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    echo "   Please install Python3 first: brew install python3"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "   Please install pip3 first"
    exit 1
fi

echo "✅ Python3 and pip3 found"

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$UDOS_PACKAGES_DIR/ascii-generator"

# Clone the repository
echo ""
echo "📥 Downloading ASCII Generator..."
cd /tmp
if [ -d "ASCII-generator" ]; then
    rm -rf ASCII-generator
fi

git clone "$REPO_URL"
cd ASCII-generator

# Install Python dependencies
echo ""
echo "📦 Installing dependencies..."

# Try different installation methods
if pip3 install --user pillow argparse 2>/dev/null; then
    echo "✅ Dependencies installed with pip3 --user"
elif pip3 install --break-system-packages pillow argparse 2>/dev/null; then
    echo "✅ Dependencies installed with --break-system-packages"
elif command -v pipx &> /dev/null; then
    echo "Using pipx for installation..."
    pipx install pillow 2>/dev/null || true
else
    echo "⚠️ Could not install dependencies automatically"
    echo "   The ASCII generator may still work with existing Python libraries"
    echo "   Or install manually: pip3 install --user pillow"
fi

# Copy to uDOS packages directory
echo ""
echo "📁 Installing to uDOS packages..."
cp -r . "$UDOS_PACKAGES_DIR/ascii-generator/"

# Create wrapper script
cat > "$INSTALL_DIR/ascii-gen" << 'EOF'
#!/bin/bash
# ASCII Generator wrapper for uDOS
cd "$HOME/uDOS/uCode/packages/ascii-generator"
python3 ascii_generator.py "$@"
EOF

chmod +x "$INSTALL_DIR/ascii-gen"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "🔧 Adding to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    echo "✅ Added $INSTALL_DIR to PATH in ~/.zshrc"
    echo "   Run 'source ~/.zshrc' or restart terminal to use ascii-gen command"
fi

# Create uDOS integration script
cat > "$UDOS_PACKAGES_DIR/ascii-generator/udos-ascii-tools.sh" << 'EOF'
#!/bin/bash
# uDOS ASCII Generator Integration

show_ascii_help() {
    echo ""
    echo "🎨 ASCII Generator - uDOS Integration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📝 COMMANDS:"
    echo "  ascii-gen text 'Hello World'           - Generate ASCII text"
    echo "  ascii-gen image path/to/image.jpg      - Convert image to ASCII"
    echo "  ascii-gen banner 'uDOS' --font big     - Create ASCII banner"
    echo ""
    echo "🎛️ OPTIONS:"
    echo "  --width N        - Set output width (default: 80)"
    echo "  --height N       - Set output height"
    echo "  --font NAME      - Text font (small, big, block, etc.)"
    echo "  --invert         - Invert ASCII art"
    echo "  --save FILE      - Save output to file"
    echo ""
    echo "📁 INTEGRATION:"
    echo "  ascii-gen logo 'uDOS' > docs/ASCII-Art-Gallery.md"
    echo "  ascii-gen banner 'Welcome' >> uMemory/banner.md"
    echo ""
    echo "🔍 Available fonts: small, big, block, shadow, script"
    echo ""
}

# uDOS-specific ASCII generation functions
generate_udos_logo() {
    local text="${1:-uDOS}"
    local font="${2:-big}"
    
    echo "🎨 Generating uDOS logo..."
    ascii-gen text "$text" --font "$font" --width 60
}

generate_system_banner() {
    local title="${1:-System}"
    local subtitle="${2:-}"
    
    echo "🏷️ Generating system banner..."
    ascii-gen text "$title" --font big --width 80
    if [[ -n "$subtitle" ]]; then
        echo ""
        ascii-gen text "$subtitle" --font small --width 80
    fi
}

# Check if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-help}" in
        help|--help|-h)
            show_ascii_help
            ;;
        logo)
            generate_udos_logo "$2" "$3"
            ;;
        banner)
            generate_system_banner "$2" "$3"
            ;;
        *)
            ascii-gen "$@"
            ;;
    esac
fi
EOF

chmod +x "$UDOS_PACKAGES_DIR/ascii-generator/udos-ascii-tools.sh"

# Test installation
echo ""
echo "🧪 Testing installation..."
cd "$UDOS_PACKAGES_DIR/ascii-generator"

if python3 ascii_generator.py --help &>/dev/null; then
    echo "✅ ASCII Generator installed successfully"
else
    echo "⚠️ Installation completed but test failed"
fi

# Clean up
echo ""
echo "🧹 Cleaning up..."
rm -rf /tmp/ASCII-generator

echo ""
echo "🎉 ASCII Generator Installation Complete!"
echo ""
echo "📋 USAGE:"
echo "  ascii-gen text 'Hello World'"
echo "  ascii-gen image photo.jpg"
echo "  bash $UDOS_PACKAGES_DIR/ascii-generator/udos-ascii-tools.sh help"
echo ""
echo "🔧 Integration with uDOS:"
echo "  [ASCII|TEXT|Hello World] - Generate ASCII text"
echo "  [ASCII|LOGO|uDOS]        - Generate uDOS logo"
echo "  [ASCII|BANNER|Title]     - Generate banner"
echo ""
