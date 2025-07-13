#!/bin/bash
# uDOS Package Installation Script for ripgrep
# Version: v1.7.0
# Purpose: Install ripgrep (rg) for fast text searching

set -e

echo "📦 Installing ripgrep for uDOS..."

# Check if already installed
if command -v rg >/dev/null 2>&1; then
    echo "✅ ripgrep is already installed: $(rg --version)"
    exit 0
fi

# Detect OS
case "$(uname -s)" in
    Darwin)
        echo "🍎 Detected macOS - installing via Homebrew fallback or direct download"
        if command -v brew >/dev/null 2>&1; then
            brew install ripgrep
        else
            echo "⚠️  Homebrew not found - please install ripgrep manually"
            echo "   Visit: https://github.com/BurntSushi/ripgrep/releases"
            exit 1
        fi
        ;;
    Linux)
        echo "🐧 Detected Linux - installing ripgrep"
        # Try package managers
        if command -v apt >/dev/null 2>&1; then
            sudo apt update && sudo apt install -y ripgrep
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y ripgrep
        else
            echo "⚠️  Package manager not found - please install ripgrep manually"
            exit 1
        fi
        ;;
    *)
        echo "❌ Unsupported OS: $(uname -s)"
        exit 1
        ;;
esac

# Verify installation
if command -v rg >/dev/null 2>&1; then
    echo "✅ ripgrep installed successfully: $(rg --version)"
    
    # Create uDOS integration wrapper
    mkdir -p "$(dirname "$0")"
    cat > "$(dirname "$0")/run-ripgrep.sh" << 'EOF'
#!/bin/bash
# uDOS ripgrep wrapper
# Usage: ./uCode/packages/run-ripgrep.sh [search term] [path]

SEARCH_TERM="${1:-TODO}"
SEARCH_PATH="${2:-./uMemory/}"

echo "🔍 Searching for '$SEARCH_TERM' in $SEARCH_PATH"
rg "$SEARCH_TERM" "$SEARCH_PATH" --type md --context 2 --color always

# Log search to uMemory
echo "$(date): Searched for '$SEARCH_TERM' in $SEARCH_PATH" >> ./uMemory/logs/package-usage.log
EOF
    
    chmod +x "$(dirname "$0")/run-ripgrep.sh"
    echo "📝 Created uDOS wrapper: run-ripgrep.sh"
    
    # Test basic functionality
    echo "🧪 Testing ripgrep..."
    rg --version
    
    echo "🎉 ripgrep integration complete!"
    echo "Usage: ./uCode/packages/run-ripgrep.sh 'search term' './path/'"
else
    echo "❌ Installation failed - ripgrep not found in PATH"
    exit 1
fi
