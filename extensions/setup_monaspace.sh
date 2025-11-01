#!/bin/bash
# Setup script for Monaspace fonts
# uDOS v1.1 Extension Installer

# Don't exit on error - we handle errors gracefully
set +e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONTS_DIR="$SCRIPT_DIR/clone/fonts/monaspace"
MONASPACE_VERSION="v1.101"
MONASPACE_RELEASE="monaspace-${MONASPACE_VERSION}"
MONASPACE_ZIP="${MONASPACE_RELEASE}.zip"
MONASPACE_URL="https://github.com/githubnext/monaspace/releases/download/${MONASPACE_VERSION}/${MONASPACE_ZIP}"

echo "🔧 uDOS Font Setup: Monaspace"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Ensure clone/fonts directory exists
mkdir -p "$SCRIPT_DIR/clone/fonts"

# Function to check internet connectivity
check_online() {
    if ping -c 1 -W 2 github.com &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if fonts already installed
if [ -d "$FONTS_DIR" ] && [ -f "$FONTS_DIR/MonaspaceNeon-Regular.woff2" ]; then
    echo "✅ Monaspace fonts already installed"
    echo "📍 Location: $FONTS_DIR"
    echo "📦 Variants: $(find "$FONTS_DIR" -name "*.woff2" | wc -l | tr -d ' ') font files"
    read -p "Reinstall anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✅ Setup complete (using existing installation)"
        exit 0
    fi
    echo "🔄 Reinstalling..."
    rm -rf "$FONTS_DIR"
fi

# Check if we're online
if ! check_online; then
    echo "❌ ERROR: No internet connection detected"
    echo "🌐 Cannot download Monaspace fonts while offline"
    echo "💡 To install manually:"
    echo "   1. Visit: https://github.com/githubnext/monaspace/releases"
    echo "   2. Download: $MONASPACE_ZIP"
    echo "   3. Extract fonts to: $FONTS_DIR"
    exit 1
fi

# Create fonts directory
echo ""
echo "📂 Creating fonts directory..."
mkdir -p "$FONTS_DIR"

# Download Monaspace
echo "📥 Downloading Monaspace $MONASPACE_VERSION..."
echo "🔗 URL: $MONASPACE_URL"

DOWNLOAD_PATH="$SCRIPT_DIR/fonts/$MONASPACE_ZIP"

if ! curl -L -o "$DOWNLOAD_PATH" "$MONASPACE_URL" 2>&1; then
    echo "❌ ERROR: Download failed"
    echo "🔗 URL: $MONASPACE_URL"
    echo ""
    echo "Possible issues:"
    echo "  • Check your internet connection"
    echo "  • GitHub may be temporarily unavailable"
    echo "  • The release version may have changed"
    exit 1
fi

echo "✅ Download complete ($(du -h "$DOWNLOAD_PATH" | cut -f1))"

# Extract fonts
echo "📂 Extracting fonts..."

if ! command -v unzip &> /dev/null; then
    echo "❌ ERROR: unzip command not found"
    echo "💡 Install unzip:"
    echo "  • macOS: brew install unzip"
    echo "  • Linux: sudo apt install unzip"
    rm -f "$DOWNLOAD_PATH"
    exit 1
fi

TEMP_EXTRACT="$SCRIPT_DIR/fonts/temp_extract"
mkdir -p "$TEMP_EXTRACT"

if ! unzip -q "$DOWNLOAD_PATH" -d "$TEMP_EXTRACT" 2>&1; then
    echo "❌ ERROR: Extraction failed"
    rm -f "$DOWNLOAD_PATH"
    rm -rf "$TEMP_EXTRACT"
    exit 1
fi

# Move web fonts (WOFF2) to fonts directory
echo "📦 Installing web fonts..."

# Find and copy WOFF2 files
WEBFONT_DIR="$TEMP_EXTRACT/monaspace-${MONASPACE_VERSION}/fonts/webfonts"
if [ -d "$WEBFONT_DIR" ]; then
    cp -r "$WEBFONT_DIR"/*.woff2 "$FONTS_DIR/" 2>/dev/null || true
fi

# Also check otf directory for conversion
OTF_DIR="$TEMP_EXTRACT/monaspace-${MONASPACE_VERSION}/fonts/otf"
if [ -d "$OTF_DIR" ] && [ ! -f "$FONTS_DIR/MonaspaceNeon-Regular.woff2" ]; then
    echo "⚠️  WOFF2 files not found, using OTF files"
    echo "💡 For web use, consider converting OTF to WOFF2"
    cp -r "$OTF_DIR"/*.otf "$FONTS_DIR/" 2>/dev/null || true
fi

# Clean up
rm -f "$DOWNLOAD_PATH"
rm -rf "$TEMP_EXTRACT"

# Verify installation
FONT_COUNT=$(find "$FONTS_DIR" -type f \( -name "*.woff2" -o -name "*.otf" \) | wc -l | tr -d ' ')

if [ "$FONT_COUNT" -gt 0 ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Monaspace fonts installed successfully!"
    echo "📍 Location: $FONTS_DIR"
    echo "📦 Fonts installed: $FONT_COUNT files"
    echo ""
    echo "Monaspace Variants:"
    echo "  • Neon    - Neo-grotesque sans (default)"
    echo "  • Argon   - Humanist sans"
    echo "  • Xenon   - Slab serif"
    echo "  • Radon   - Handwriting"
    echo "  • Krypton - Mechanical sans"
    echo ""
    echo "Features:"
    echo "  • Texture Healing™ - Adaptive character widths"
    echo "  • Coding ligatures"
    echo "  • Powerline symbols"
    echo "  • Variable font technology"
    echo ""
    echo "Usage in uDOS web terminal (future):"
    echo "  🔮 font list           # Show available fonts"
    echo "  🔮 font set neon       # Use Neon variant"
    echo "  🔮 font info           # Display current font"
    echo ""
    echo "For web integration:"
    echo "  • Fonts ready for cmd.js terminal (Round 3)"
    echo "  • CSS @font-face declarations needed"
    echo "  • Works with typo editor when integrated"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # List installed fonts
    echo ""
    echo "📋 Installed fonts:"
    find "$FONTS_DIR" -type f \( -name "*.woff2" -o -name "*.otf" \) | sort | while read font; do
        echo "   • $(basename "$font")"
    done
else
    echo ""
    echo "❌ ERROR: No fonts were installed"
    echo "📍 Expected location: $FONTS_DIR"
    echo "🔍 Check extraction process"
    exit 1
fi

echo ""
echo "💡 Tip: Monaspace fonts will be used in:"
echo "    • Web terminal interface (cmd.js - Round 3)"
echo "    • Browser-based editors (typo)"
echo "    • Any web-based uDOS extensions"
