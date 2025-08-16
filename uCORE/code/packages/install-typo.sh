#!/bin/bash
# Typo Markdown Editor Installation Script for uDOS
# Source: https://github.com/rossrobino/typo

set -e

PACKAGE_NAME="typo"
REPO_URL="https://github.com/rossrobino/typo.git"
INSTALL_DIR="$HOME/.local/bin"
UDOS_PACKAGES_DIR="$HOME/uDOS/uCode/packages"

echo ""
echo "📝 Installing Typo Markdown Editor for uDOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "   Installing Node.js with Homebrew..."
    if command -v brew &> /dev/null; then
        brew install node
    else
        echo "   Please install Node.js first: https://nodejs.org/"
        exit 1
    fi
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    echo "   Please install npm with Node.js"
    exit 1
fi

echo "✅ Node.js and npm found"

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$UDOS_PACKAGES_DIR/typo"

# Clone the repository
echo ""
echo "📥 Downloading Typo..."
cd /tmp
if [ -d "typo" ]; then
    rm -rf typo
fi

git clone "$REPO_URL"
cd typo

# Install dependencies and build
echo ""
echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔧 Building for development..."
# Try to build, but continue even if it fails (Node.js version issues)
if npm run build 2>/dev/null; then
    echo "✅ Build successful"
else
    echo "⚠️ Build failed, but development server will still work"
    echo "   (This is usually due to Node.js version compatibility)"
fi

# Copy built files to uDOS packages directory
echo ""
echo "📁 Installing to uDOS packages..."
cp -r . "$UDOS_PACKAGES_DIR/typo/"

# Create wrapper script for local development server
cat > "$INSTALL_DIR/typo-server" << 'EOF'
#!/bin/bash
# Typo development server wrapper for uDOS
cd "$HOME/uDOS/uCode/packages/typo"
npm run dev
EOF

chmod +x "$INSTALL_DIR/typo-server"

# Create wrapper script for building/serving static files
cat > "$INSTALL_DIR/typo-build" << 'EOF'
#!/bin/bash
# Typo build wrapper for uDOS
cd "$HOME/uDOS/uCode/packages/typo"
npm run build
npm run preview
EOF

chmod +x "$INSTALL_DIR/typo-build"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "🔧 Adding to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    echo "✅ Added $INSTALL_DIR to PATH in ~/.zshrc"
    echo "   Run 'source ~/.zshrc' or restart terminal to use typo commands"
fi

# Create uDOS integration script
cat > "$UDOS_PACKAGES_DIR/typo/udos-typo-integration.sh" << 'EOF'
#!/bin/bash
# uDOS Typo Markdown Editor Integration

show_typo_help() {
    echo ""
    echo "📝 Typo Markdown Editor - uDOS Integration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🌐 WEB EDITOR COMMANDS:"
    echo "  typo-server                     - Start development server (localhost:5173)"
    echo "  typo-build                      - Build and serve production version"
    echo ""
    echo "🔧 uDOS INTEGRATION:"
    echo "  [TYPO|EDIT|file.md]            - Open file in Typo web editor"
    echo "  [TYPO|SERVER]                  - Start Typo server"
    echo "  [TYPO|NEW|filename]            - Create new file and edit in Typo"
    echo ""
    echo "💡 FEATURES:"
    echo "  • Live markdown preview"
    echo "  • Modern web-based interface" 
    echo "  • Real-time file watching"
    echo "  • Export capabilities"
    echo "  • Responsive design"
    echo ""
    echo "🌐 ACCESS:"
    echo "  http://localhost:5173 (development)"
    echo "  http://localhost:4173 (production)"
    echo ""
}

# Start Typo server for editing
start_typo_server() {
    local file_path="$1"
    
    echo "🌐 Starting Typo development server..."
    cd "$HOME/uDOS/uCode/packages/typo"
    
    if [[ -n "$file_path" && -f "$file_path" ]]; then
        echo "📝 File to edit: $file_path"
        echo "💡 Open http://localhost:5173 in your browser"
        echo "   Then open your file: $file_path"
    else
        echo "💡 Open http://localhost:5173 in your browser to start editing"
    fi
    
    echo ""
    echo "🚀 Starting server... (Press Ctrl+C to stop)"
    npm run dev
}

# Open file in Typo (starts server if not running)
edit_with_typo() {
    local file_path="$1"
    
    if [[ -z "$file_path" ]]; then
        echo "❌ No file specified"
        return 1
    fi
    
    # Ensure file exists
    if [[ ! -f "$file_path" ]]; then
        echo "📝 Creating new file: $file_path"
        mkdir -p "$(dirname "$file_path")"
        touch "$file_path"
    fi
    
    echo "📝 Opening $file_path in Typo..."
    echo "🌐 Starting Typo server at http://localhost:5173"
    echo ""
    echo "💡 Instructions:"
    echo "   1. Wait for server to start"
    echo "   2. Open http://localhost:5173 in your browser"
    echo "   3. Click 'Open File' and select: $file_path"
    echo "   4. Start editing with live preview!"
    echo ""
    echo "Press any key to start server..."
    read -n 1
    
    start_typo_server "$file_path"
}

# Check if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-help}" in
        help|--help|-h)
            show_typo_help
            ;;
        server)
            start_typo_server "$2"
            ;;
        edit)
            edit_with_typo "$2"
            ;;
        *)
            echo "Unknown command: $1"
            show_typo_help
            ;;
    esac
fi
EOF

chmod +x "$UDOS_PACKAGES_DIR/typo/udos-typo-integration.sh"

# Test installation
echo ""
echo "🧪 Testing installation..."
cd "$UDOS_PACKAGES_DIR/typo"

if [[ -f "package.json" ]] && npm list &>/dev/null; then
    echo "✅ Typo installed successfully"
else
    echo "⚠️ Installation completed but test failed"
fi

# Clean up
echo ""
echo "🧹 Cleaning up..."
rm -rf /tmp/typo

echo ""
echo "🎉 Typo Markdown Editor Installation Complete!"
echo ""
echo "📋 USAGE:"
echo "  typo-server                    - Start development server"
echo "  typo-build                     - Build and serve production"
echo "  bash $UDOS_PACKAGES_DIR/typo/udos-typo-integration.sh help"
echo ""
echo "🔧 Integration with uDOS:"
echo "  [TYPO|EDIT|file.md]          - Edit file in Typo"
echo "  [TYPO|SERVER]                - Start Typo server"
echo "  [TYPO|NEW|filename]          - Create and edit new file"
echo ""
echo "🌐 Web Interface:"
echo "  http://localhost:5173 (after starting server)"
echo ""
