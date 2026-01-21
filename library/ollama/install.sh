#!/bin/bash
# Ollama Installation Script for uDOS
# ====================================
# Installs Ollama for offline AI capabilities (Vibe CLI)
#
# This script detects the platform and installs Ollama
# for LOCAL AI model execution - no cloud, no API keys.

set -e

echo "🦙 Ollama Installation for uDOS"
echo "================================"
echo ""
echo "This will install Ollama for OFFLINE AI capabilities."
echo "Models run entirely on your device - no cloud required."
echo ""

# Detect platform
OS=$(uname -s)
ARCH=$(uname -m)

install_macos() {
    echo "📱 Detected: macOS ($ARCH)"
    
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama already installed: $(ollama --version)"
        return 0
    fi
    
    if command -v brew &> /dev/null; then
        echo "🍺 Installing via Homebrew..."
        brew install ollama
    else
        echo "📥 Downloading Ollama.dmg..."
        curl -fsSL https://ollama.com/download/Ollama-darwin.zip -o /tmp/ollama.zip
        unzip -o /tmp/ollama.zip -d /Applications
        rm /tmp/ollama.zip
        echo "✅ Ollama installed to /Applications"
    fi
}

install_linux() {
    echo "🐧 Detected: Linux ($ARCH)"
    
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama already installed: $(ollama --version)"
        return 0
    fi
    
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
}

install_tinycore() {
    echo "🐧 Detected: Tiny Core Linux ($ARCH)"
    
    # Tiny Core specific installation
    # Uses manual binary installation
    
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama already installed: $(ollama --version)"
        return 0
    fi
    
    echo "📥 Downloading Ollama binary..."
    
    if [ "$ARCH" = "x86_64" ]; then
        BINARY_URL="https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        BINARY_URL="https://github.com/ollama/ollama/releases/latest/download/ollama-linux-arm64"
    else
        echo "❌ Unsupported architecture: $ARCH"
        exit 1
    fi
    
    # Download to /usr/local/bin (persistent on TC)
    sudo curl -fsSL "$BINARY_URL" -o /usr/local/bin/ollama
    sudo chmod +x /usr/local/bin/ollama
    
    echo "✅ Ollama installed to /usr/local/bin/ollama"
    
    # Create systemd-free service script for TC
    cat > /tmp/ollama-serve.sh << 'EOF'
#!/bin/sh
# Ollama server for Tiny Core Linux
export OLLAMA_HOST=0.0.0.0:11434
exec ollama serve
EOF
    
    sudo mv /tmp/ollama-serve.sh /usr/local/bin/ollama-serve
    sudo chmod +x /usr/local/bin/ollama-serve
    
    echo "📝 To start Ollama server: ollama-serve &"
}

download_recommended_models() {
    echo ""
    echo "📦 Download Recommended Models?"
    echo "================================"
    echo ""
    echo "Models for coding (Vibe CLI):"
    echo "  1) gemma2:2b      (1.6GB) - Tiny Core friendly"
    echo "  2) deepseek-coder (3.8GB) - Best for coding"
    echo "  3) mistral:7b     (4.1GB) - Balanced general use"
    echo "  4) codellama:7b   (3.8GB) - Meta's code model"
    echo ""
    echo "  a) All of the above"
    echo "  s) Skip for now"
    echo ""
    read -p "Select (1-4, a, or s): " choice
    
    case $choice in
        1)
            ollama pull gemma2:2b
            ;;
        2)
            ollama pull deepseek-coder:6.7b
            ;;
        3)
            ollama pull mistral:7b
            ;;
        4)
            ollama pull codellama:7b
            ;;
        a)
            ollama pull gemma2:2b
            ollama pull deepseek-coder:6.7b
            ollama pull mistral:7b
            ollama pull codellama:7b
            ;;
        s)
            echo "⏭️  Skipping model download"
            echo "   Run 'ollama pull <model>' later to download models"
            ;;
        *)
            echo "Invalid choice, skipping"
            ;;
    esac
}

# Main installation
case "$OS" in
    Darwin)
        install_macos
        ;;
    Linux)
        # Check for Tiny Core
        if [ -f /etc/os-release ] && grep -q "TinyCore\|Core" /etc/os-release; then
            install_tinycore
        else
            install_linux
        fi
        ;;
    *)
        echo "❌ Unsupported OS: $OS"
        echo "Please install Ollama manually from https://ollama.com"
        exit 1
        ;;
esac

# Verify installation
if command -v ollama &> /dev/null; then
    echo ""
    echo "✅ Ollama installed successfully!"
    ollama --version
    
    # Offer to download models
    download_recommended_models
    
    echo ""
    echo "🎉 Done! Vibe CLI is now ready for offline AI."
    echo ""
    echo "Quick start:"
    echo "  ollama serve &     # Start server (if not running)"
    echo "  ollama run gemma2  # Chat with model"
    echo ""
    echo "In uDOS TUI:"
    echo "  OK FIX <file>      # Offline code analysis"
    echo "  OK ASK <question>  # Local AI assistant"
else
    echo ""
    echo "❌ Installation failed. Please install manually:"
    echo "   https://ollama.com/download"
fi
