#!/bin/bash
# Setup script for micro editor
# uDOS v1.1 Extension Installer

# Don't exit on error - we handle errors gracefully
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MICRO_DIR="$SCRIPT_DIR/clone/native/micro"
MICRO_BIN="$MICRO_DIR/micro"

echo "🔧 uDOS Extension Setup: micro editor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Ensure clone/native directory exists
mkdir -p "$SCRIPT_DIR/clone/native"

# Function to check internet connectivity
check_online() {
    if ping -c 1 -W 2 github.com &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if micro already exists and is functional
if [ -f "$MICRO_BIN" ]; then
    if "$MICRO_BIN" --version &> /dev/null; then
        echo "✅ micro is already installed and functional"
        echo "📍 Location: $MICRO_BIN"
        echo "📦 Version: $("$MICRO_BIN" --version | head -1)"

        # Skip prompt if auto-installing from dashboard
        if [ -z "$UDOS_AUTO_INSTALL" ]; then
            read -p "Reinstall anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "✅ Setup complete (using existing installation)"
                exit 0
            fi
        else
            echo "ℹ️  Auto-install mode: using existing installation"
            exit 0
        fi

        echo "🗑️  Removing existing installation..."
        rm -rf "$MICRO_DIR"
    fi
fi

# Check if we're online (needed for download)
if ! check_online; then
    echo "❌ ERROR: No internet connection detected"
    echo "🌐 Cannot download micro editor while offline"
    echo ""
    echo "💡 To install manually:"
    echo "   1. Visit: https://github.com/zyedidia/micro/releases"
    echo "   2. Download the release for your platform"
    echo "   3. Extract to: $MICRO_DIR"
    echo "   4. Ensure binary is named 'micro' and is executable"
    exit 1
fi

# Detect platform
OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux*)
        OS_NAME="linux"
        ;;
    Darwin*)
        OS_NAME="osx"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        OS_NAME="win"
        ;;
    *)
        echo "❌ ERROR: Unsupported operating system: $OS"
        exit 1
        ;;
esac

case "$ARCH" in
    x86_64|amd64)
        ARCH_NAME="amd64"
        ;;
    arm64|aarch64)
        ARCH_NAME="arm64"
        ;;
    armv7l|armv6l)
        ARCH_NAME="arm"
        ;;
    *)
        echo "⚠️  WARNING: Unknown architecture: $ARCH, using amd64"
        ARCH_NAME="amd64"
        ;;
esac

# Construct download URL
VERSION="v2.0.14"
VERSION_NUM="2.0.14"  # Without 'v' prefix

if [ "$OS_NAME" = "win" ]; then
    FILENAME="micro-${VERSION_NUM}-win64.zip"
elif [ "$OS_NAME" = "linux" ]; then
    if [ "$ARCH_NAME" = "arm64" ]; then
        FILENAME="micro-${VERSION_NUM}-linux-arm64.tar.gz"
    elif [ "$ARCH_NAME" = "arm" ]; then
        FILENAME="micro-${VERSION_NUM}-linux-arm.tar.gz"
    else
        FILENAME="micro-${VERSION_NUM}-linux64.tar.gz"
    fi
elif [ "$OS_NAME" = "osx" ]; then
    # macOS builds are universal
    FILENAME="micro-${VERSION_NUM}-osx.tar.gz"
else
    echo "❌ ERROR: Unsupported OS: $OS_NAME"
    exit 1
fi

URL="https://github.com/zyedidia/micro/releases/download/${VERSION}/${FILENAME}"

echo ""
echo "📦 Platform detected: ${OS_NAME}-${ARCH_NAME}"
echo "🔗 Downloading from: $URL"

# Create directories
mkdir -p "$MICRO_DIR"
DOWNLOAD_PATH="$SCRIPT_DIR/clone/native/$FILENAME"

# Download with better error handling
echo "⏬ Downloading..."
if ! curl -L -f -o "$DOWNLOAD_PATH" "$URL" 2>&1; then
    echo "❌ ERROR: Download failed"
    echo "🔗 URL: $URL"

    # Check if file was created but is too small (error page)
    if [ -f "$DOWNLOAD_PATH" ]; then
        SIZE=$(wc -c < "$DOWNLOAD_PATH")
        if [ "$SIZE" -lt 1000 ]; then
            echo "⚠️  Received error page instead of binary ($SIZE bytes)"
            cat "$DOWNLOAD_PATH"
            rm "$DOWNLOAD_PATH"
        fi
    fi

    echo ""
    echo "Possible issues:"
    echo "  • Check your internet connection"
    echo "  • GitHub may be temporarily unavailable"
    echo "  • The release version may have changed"
    exit 1
fi

# Verify download size
if [ -f "$DOWNLOAD_PATH" ]; then
    SIZE=$(wc -c < "$DOWNLOAD_PATH")
    if [ "$SIZE" -lt 100000 ]; then
        echo "❌ ERROR: Downloaded file is too small ($SIZE bytes)"
        echo "⚠️  This is likely an error page, not the actual binary"
        rm "$DOWNLOAD_PATH"
        exit 1
    fi
    echo "✅ Download complete ($(numfmt --to=iec-i --suffix=B $SIZE 2>/dev/null || echo "${SIZE} bytes"))"
else
    echo "❌ ERROR: Download file not created"
    exit 1
fi

# Extract
echo "📂 Extracting..."

if [ "$OS_NAME" = "win" ]; then
    # Windows ZIP extraction
    if command -v unzip &> /dev/null; then
        unzip -q "$DOWNLOAD_PATH" -d "$SCRIPT_DIR/clone/native"
    else
        echo "❌ ERROR: unzip command not found"
        echo "💡 Install unzip or extract manually"
        exit 1
    fi

    # Move from extracted directory
    EXTRACTED_DIR="$SCRIPT_DIR/clone/native/micro-$VERSION_NUM"
    if [ -d "$EXTRACTED_DIR" ]; then
        mv "$EXTRACTED_DIR/micro.exe" "$MICRO_DIR/"
        rm -rf "$EXTRACTED_DIR"
    fi

    MICRO_BIN="$MICRO_DIR/micro.exe"
else
    # Unix tar.gz extraction
    if ! tar -xzf "$DOWNLOAD_PATH" -C "$SCRIPT_DIR/clone/native" 2>&1; then
        echo "❌ ERROR: Extraction failed"
        echo "⚠️  Archive may be corrupted or incomplete"
        rm -f "$DOWNLOAD_PATH"
        exit 1
    fi

    # Move from extracted directory to micro/
    EXTRACTED_DIR="$SCRIPT_DIR/clone/native/micro-$VERSION_NUM"
    if [ -d "$EXTRACTED_DIR" ]; then
        if [ -f "$EXTRACTED_DIR/micro" ]; then
            mv "$EXTRACTED_DIR/micro" "$MICRO_BIN"
            chmod +x "$MICRO_BIN"
        fi
        rm -rf "$EXTRACTED_DIR"
    fi
fi

# Clean up download
rm -f "$DOWNLOAD_PATH"

# Verify installation
if [ -f "$MICRO_BIN" ]; then
    if "$MICRO_BIN" --version &> /dev/null; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ micro installed successfully!"
        echo "📍 Location: $MICRO_BIN"
        echo "📦 Version: $("$MICRO_BIN" --version | head -1)"
        echo ""
        echo "Features:"
        echo "  • Syntax highlighting for 100+ languages"
        echo "  • Mouse support"
        echo "  • Multiple cursors"
        echo "  • Plugin system"
        echo "  • Common keybindings (Ctrl+S, Ctrl+Q, etc.)"
        echo ""
        echo "Usage in uDOS:"
        echo "  🔮 edit myfile.txt"
        echo "  🔮 edit --cli sandbox/USER.UDO"
        echo ""
        echo "Quick Start:"
        echo "  Ctrl+Q - Quit"
        echo "  Ctrl+S - Save"
        echo "  Ctrl+E - Command bar"
        echo "  Ctrl+G - Help"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    else
        echo ""
        echo "⚠️  WARNING: Binary installed but may not be functional"
        echo "📍 Location: $MICRO_BIN"
        echo "🧪 Try running: $MICRO_BIN --version"
    fi
else
    echo ""
    echo "❌ ERROR: Installation completed but binary not found"
    echo "📍 Expected location: $MICRO_BIN"
    echo ""
    echo "Debug information:"
    echo "  • Download URL: $URL"
    echo "  • Extracted directory should be: $EXTRACTED_DIR"
    echo "  • Contents of native/:"
    ls -la "$SCRIPT_DIR/native" 2>/dev/null || echo "    (directory not accessible)"
    exit 1
fi

echo ""
echo "💡 Tip: micro is now set as your default CLI editor in uDOS"
echo "    To change editors, run: 🔮 edit --config"
