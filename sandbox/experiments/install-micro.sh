#!/bin/bash

# Micro Text Editor Installation Script for uDOS
# Repository: https://github.com/zyedidia/micro
# A modern and intuitive terminal-based text editor

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MICRO_DIR="$SCRIPT_DIR/micro-editor"

echo "📝 Installing Micro Text Editor from GitHub..."

# Check if already installed
if [ -d "$MICRO_DIR" ]; then
    echo "⚠️  Micro Editor already exists at $MICRO_DIR"
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Updating Micro Editor..."
        cd "$MICRO_DIR"
        git pull origin master
    else
        echo "❌ Installation cancelled"
        exit 0
    fi
else
    # Clone the repository
    echo "📥 Cloning Micro Editor repository..."
    git clone https://github.com/zyedidia/micro.git "$MICRO_DIR"
    cd "$MICRO_DIR"
fi

# Check for Go
if ! command -v go &> /dev/null; then
    echo "❌ Go is required but not installed"
    echo "Please install Go from https://golang.org/dl/"
    exit 1
fi

echo "🔧 Building Micro Editor..."
make build

# Create symlink in local bin if it doesn't exist
BIN_DIR="$SCRIPT_DIR/bin"
mkdir -p "$BIN_DIR"

if [ -f "$MICRO_DIR/micro" ]; then
    ln -sf "$MICRO_DIR/micro" "$BIN_DIR/micro"
    echo "🔗 Created symlink at $BIN_DIR/micro"
fi

# Create launch script
cat > "$SCRIPT_DIR/launch-micro.sh" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MICRO_BIN="$SCRIPT_DIR/bin/micro"

if [ -f "$MICRO_BIN" ]; then
    if [ $# -eq 0 ]; then
        echo "📝 Launching Micro Editor..."
        "$MICRO_BIN"
    else
        echo "📝 Opening file(s) in Micro Editor: $@"
        "$MICRO_BIN" "$@"
    fi
else
    echo "❌ Micro binary not found. Please run install-micro.sh first."
    exit 1
fi
EOF

chmod +x "$SCRIPT_DIR/launch-micro.sh"

echo "✅ Micro Text Editor installation complete!"
echo ""
echo "📋 Usage:"
echo "  To launch: ./launch-micro.sh"
echo "  Edit file: ./launch-micro.sh filename.txt"
echo "  Binary: $BIN_DIR/micro"
echo ""
echo "💡 Micro features:"
echo "  - Syntax highlighting"
echo "  - Common keybindings (Ctrl+S, Ctrl+C, etc.)"
echo "  - Mouse support"
echo "  - Plugin system"
echo ""
echo "🔗 More info: https://micro-editor.github.io/"
echo "📚 GitHub: https://github.com/zyedidia/micro"
