#!/bin/bash
# uFont Manager - Font Distribution Script
# Part of uDOS Alpha v1.0.2.0
# Copies fonts from central repository to distribution targets

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🎨 uFont Manager - Font Distribution"
echo "======================================"
echo ""

# Read manifest to get distribution targets
MANIFEST="manifest.json"

if [ ! -f "$MANIFEST" ]; then
    echo "❌ Error: manifest.json not found"
    exit 1
fi

echo "📋 Reading manifest..."
echo ""

# Distribution targets
TARGETS=(
    "../public/fonts"
    # Add more targets here as needed
)

# Create target directories and copy fonts
for TARGET in "${TARGETS[@]}"; do
    echo "📦 Distributing to: $TARGET"
    
    # Create target directory structure
    mkdir -p "$TARGET"
    mkdir -p "$TARGET/retro/c64"
    mkdir -p "$TARGET/retro/teletext"
    mkdir -p "$TARGET/retro/apple"
    mkdir -p "$TARGET/retro/gaming"
    
    # Copy retro fonts
    if [ -d "retro/c64" ]; then
        cp -f retro/c64/*.ttf "$TARGET/retro/c64/" 2>/dev/null || true
    fi
    
    if [ -d "retro/teletext" ]; then
        cp -f retro/teletext/*.otf "$TARGET/retro/teletext/" 2>/dev/null || true
    fi
    
    if [ -d "retro/apple" ]; then
        cp -f retro/apple/*.ttf "$TARGET/retro/apple/" 2>/dev/null || true
    fi
    
    if [ -d "retro/gaming" ]; then
        cp -f retro/gaming/*.ttf "$TARGET/retro/gaming/" 2>/dev/null || true
    fi
    
    # Copy emoji fonts
    if [ -f "emoji/NotoColorEmoji.ttf" ]; then
        cp -f emoji/NotoColorEmoji.ttf "$TARGET/" 2>/dev/null || true
    fi
    
    if [ -f "emoji/NotoEmoji-Regular.ttf" ]; then
        cp -f emoji/NotoEmoji-Regular.ttf "$TARGET/" 2>/dev/null || true
    fi
    
    # Copy manifest.json for web access
    cp -f manifest.json "$TARGET/" 2>/dev/null || true
    
    # Copy Press Start 2P to root (as per fontCollections.ts)
    if [ -f "retro/gaming/PressStart2P-Regular.ttf" ]; then
        cp -f retro/gaming/PressStart2P-Regular.ttf "$TARGET/retro/" 2>/dev/null || true
    fi
    
    # Copy credits
    cp -f README.md "$TARGET/" 2>/dev/null || true
    
    echo "   ✅ Copied fonts to $TARGET"
    echo ""
done

echo "✨ Distribution complete!"
echo ""
echo "📊 Summary:"
echo "   - Retro fonts: C64, Teletext, Apple, Gaming"
echo "   - Emoji fonts: Noto Color, Noto Mono"
echo "   - Credits: README.md included"
echo ""
echo "🎯 Next steps:"
echo "   1. Fonts are now available at http://localhost:5173/fonts/"
echo "   2. Pixel editor will load fonts from /fonts/"
echo "   3. Check manifest.json for font metadata"
echo ""
