#!/bin/bash

# Type Terminal Typing Game Installation Script for uDOS
# Repository: https://github.com/qurle/type
# A terminal-based typing speed test and practice game

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TYPE_DIR="$SCRIPT_DIR/type-game"

echo "⌨️  Installing Type Terminal Typing Game from GitHub..."

# Check if already installed
if [ -d "$TYPE_DIR" ]; then
    echo "⚠️  Type game already exists at $TYPE_DIR"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Updating Type game..."
        cd "$TYPE_DIR"
        git pull origin main
    else
        echo "❌ Installation cancelled"
        exit 0
    fi
else
    # Clone the repository
    echo "📥 Cloning Type game repository..."
    git clone https://github.com/qurle/type.git "$TYPE_DIR"
    cd "$TYPE_DIR"
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    echo "Please install npm (usually comes with Node.js)"
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

# Create launch script
cat > "$SCRIPT_DIR/launch-type-game.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/type-game"

echo "⌨️  Starting Type - Terminal Typing Game"
echo "🎯 Practice your typing speed and accuracy!"
echo "📊 Get real-time WPM and accuracy stats"
echo ""

npm start
EOF

chmod +x "$SCRIPT_DIR/launch-type-game.sh"

echo "✅ Type Terminal Typing Game installation complete!"
echo ""
echo "📋 Usage:"
echo "  To play: ./launch-type-game.sh"
echo "  Location: $TYPE_DIR"
echo ""
echo "🎮 Game features:"
echo "  - Real-time typing speed measurement (WPM)"
echo "  - Accuracy tracking"
echo "  - Terminal-based interface"
echo "  - Practice typing skills"
echo ""
echo "🔗 GitHub: https://github.com/qurle/type"
