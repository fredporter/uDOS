#!/bin/bash
# uDOS VS Code Extension Setup
# Quick installation and testing script

set -e

echo "🚀 uDOS VS Code Extension Setup"
echo "================================"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version too old. Need 18+, found $(node -v)"
    exit 1
fi

echo "✅ Node.js $(node -v) found"

# Navigate to extension directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔨 Compiling TypeScript..."
npm run compile

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next Steps:"
echo ""
echo "1. Launch Extension Development Host:"
echo "   - Open VS Code in /Users/fredbook/Code/uDOS"
echo "   - Navigate to extensions/vscode-udos/"
echo "   - Press F5 (or Run → Start Debugging)"
echo ""
echo "2. Test in new window:"
echo "   - Create test.upy file"
echo "   - Type 'mission' and press Tab"
echo "   - Test IntelliSense (Ctrl+Space)"
echo ""
echo "3. Start uDOS API (for script execution):"
echo "   cd /Users/fredbook/Code/uDOS"
echo "   ./start_udos.sh"
echo "   # Then in uDOS: POKE API start"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: QUICKSTART.md"
echo "   - Full Guide: README.md"
echo ""
echo "🎉 Ready to develop with uDOS VS Code Extension!"
