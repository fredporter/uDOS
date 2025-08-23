#!/bin/bash

# Min Browser Installation Script for uDOS
# Repository: https://github.com/minbrowser/min
# A minimal, fast browser for testing web interfaces

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIN_DIR="$SCRIPT_DIR/min-browser"

echo "🌐 Installing Min Browser from GitHub..."

# Check if already installed
if [ -d "$MIN_DIR" ]; then
    echo "⚠️  Min Browser already exists at $MIN_DIR"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Updating Min Browser..."
        cd "$MIN_DIR"
        git pull origin main
    else
        echo "❌ Installation cancelled"
        exit 0
    fi
else
    # Clone the repository
    echo "📥 Cloning Min Browser repository..."
    git clone https://github.com/minbrowser/min.git "$MIN_DIR"
    cd "$MIN_DIR"
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

echo "🔧 Building Min Browser..."
npm run build

# Create launch script
cat > "$SCRIPT_DIR/launch-min-browser.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/min-browser"
npm start
EOF

chmod +x "$SCRIPT_DIR/launch-min-browser.sh"

echo "✅ Min Browser installation complete!"
echo ""
echo "📋 Usage:"
echo "  To launch: ./launch-min-browser.sh"
echo "  Location: $MIN_DIR"
echo ""
echo "🔗 More info: https://minbrowser.org"
echo "📚 GitHub: https://github.com/minbrowser/min"
