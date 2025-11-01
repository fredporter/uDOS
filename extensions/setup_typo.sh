#!/bin/bash
# Setup script for typo web editor (rossrobino/typo)
# uDOS v1.1 Extension Installer

# Don't exit on error - we handle errors gracefully
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TYPO_DIR="$SCRIPT_DIR/clone/web/typo"
TYPO_REPO="https://github.com/rossrobino/typo.git"

echo "🔧 uDOS Extension Setup: typo web editor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Ensure clone/web directory exists
mkdir -p "$SCRIPT_DIR/clone/web"

# Function to check internet connectivity
check_online() {
    if ping -c 1 -W 2 github.com &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if typo already exists and is functional
if [ -f "$TYPO_DIR/package.json" ]; then
    echo "✅ typo directory exists"
    if [ -d "$TYPO_DIR/node_modules" ]; then
        echo "✅ Dependencies already installed"

        # Skip prompt if auto-installing from dashboard
        if [ -z "$UDOS_AUTO_INSTALL" ]; then
            read -p "Reinstall anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "✅ Setup complete (using existing installation)"
                echo ""
                echo "To start typo server:"
                echo "  cd $TYPO_DIR && npm run dev"
                echo "  Or use: 🔮 server start typo"
                exit 0
            fi
        else
            echo "ℹ️  Auto-install mode: using existing installation"
            exit 0
        fi

        echo "🔄 Reinstalling..."
        rm -rf "$TYPO_DIR/node_modules"
    else
        echo "⚠️  Dependencies not installed, will install now"
    fi
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ ERROR: Node.js not found"
    echo "📦 typo is a web application and requires Node.js"
    echo ""
    echo "🔧 To install Node.js:"
    echo "  • macOS: brew install node"
    echo "  • Linux: sudo apt install nodejs npm  (or equivalent)"
    echo "  • Windows: Download from https://nodejs.org"
    echo ""
    echo "🔗 Or visit: https://nodejs.org"
    echo ""
    read -p "Continue anyway? (not recommended) (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js found: $NODE_VERSION"
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ ERROR: npm not found"
    echo "📦 npm is required to install typo dependencies"
    echo ""
    if command -v node &> /dev/null; then
        echo "⚠️  Node.js is installed but npm is missing"
        echo "   This is unusual - try reinstalling Node.js"
    fi
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ npm found: v$NPM_VERSION"

# Clone typo repository (if needed)
if [ ! -d "$TYPO_DIR" ]; then
    # Check if we're online
    if ! check_online; then
        echo "❌ ERROR: No internet connection detected"
        echo "🌐 Cannot clone typo repository while offline"
        echo "💡 If you have the repository locally, manually copy it to:"
        echo "   $TYPO_DIR"
        exit 1
    fi

    echo ""
    echo "📥 Cloning typo from $TYPO_REPO..."

    # Create web directory if it doesn't exist
    mkdir -p "$SCRIPT_DIR/web"

    if ! git clone "$TYPO_REPO" "$TYPO_DIR" 2>&1; then
        echo "❌ ERROR: Failed to clone typo repository"
        echo "🌐 Check your internet connection"
        echo "🔗 Repository: $TYPO_REPO"
        exit 1
    fi
    echo "✅ Clone successful"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies (this may take a few minutes)..."
cd "$TYPO_DIR" || exit 1

if ! npm install 2>&1 | tee /tmp/typo_install.log; then
    echo ""
    echo "❌ ERROR: npm install failed"
    echo "📋 Install log saved to: /tmp/typo_install.log"
    echo ""
    echo "Common issues:"
    echo "  • Outdated Node.js version - try: nvm install --lts"
    echo "  • Permission issues - avoid using sudo with npm"
    echo "  • Network issues - check your connection"
    exit 1
fi

# Verify installation
if [ -d "$TYPO_DIR/node_modules" ] && [ -f "$TYPO_DIR/package.json" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ typo installed successfully!"
    echo "📍 Location: $TYPO_DIR"
    echo "📦 Dependencies: $(find "$TYPO_DIR/node_modules" -maxdepth 1 -type d | wc -l | tr -d ' ') packages"
    echo ""
    echo "Features:"
    echo "  • Web-based markdown editor"
    echo "  • Live preview"
    echo "  • File System API support"
    echo "  • Auto-save (when supported)"
    echo "  • Slide creation with --- separators"
    echo "  • Code block execution (js/ts)"
    echo ""
    echo "Usage in uDOS:"
    echo "  🔮 server start typo        # Start typo server"
    echo "  🔮 edit --web myfile.md     # Open file in typo"
    echo "  🔮 server stop typo         # Stop server"
    echo ""
    echo "Manual usage:"
    echo "  cd $TYPO_DIR"
    echo "  npm run dev                 # Starts on http://localhost:5173"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "❌ ERROR: Installation completed but verification failed"
    echo "📍 Expected: $TYPO_DIR/node_modules"
    echo "📋 Check install log: /tmp/typo_install.log"
    exit 1
fi

# Clean up install log if successful
rm -f /tmp/typo_install.log

echo ""
echo "💡 Tip: typo server runs on port 5173 by default"
echo "    Use 'server status' to check if it's running"
