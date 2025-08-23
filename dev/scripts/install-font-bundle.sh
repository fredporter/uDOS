#!/bin/bash
# uDOS Font Bundle Installer
# Downloads and installs essential retro/pixel fonts for uDOS
# Keeps only MODE7GX0.TTF, adds missing essentials

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FONT_DIR="/Users/agentdigital/uDOS/uMEMORY/system/fonts"
TEMP_DIR="/tmp/udos-fonts-$$"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Create temp directory
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

log "uDOS Font Bundle Installer"
log "Installing essential retro/pixel fonts..."
log "Temporary directory: $TEMP_DIR"

# Function to download font safely
download_font() {
    local url="$1"
    local filename="$2"
    local description="$3"

    log "Downloading $description..."

    if curl -L -o "$filename" "$url" 2>/dev/null; then
        if [[ -f "$filename" && -s "$filename" ]]; then
            success "Downloaded $filename"
            return 0
        else
            error "Downloaded file is empty or corrupted: $filename"
            return 1
        fi
    else
        error "Failed to download $description from $url"
        return 1
    fi
}

# Function to extract and install font
install_font() {
    local file="$1"
    local target_name="$2"
    local description="$3"

    if [[ ! -f "$file" ]]; then
        error "Font file not found: $file"
        return 1
    fi

    # Handle different file types
    case "$file" in
        *.zip)
            log "Extracting $description from ZIP..."
            unzip -q "$file"
            # Find TTF files in extracted content
            local ttf_file=$(find . -name "*.ttf" -o -name "*.TTF" | head -1)
            if [[ -n "$ttf_file" ]]; then
                cp "$ttf_file" "$FONT_DIR/$target_name"
                success "Installed $target_name"
            else
                error "No TTF file found in $file"
                return 1
            fi
            ;;
        *.ttf|*.TTF)
            cp "$file" "$FONT_DIR/$target_name"
            success "Installed $target_name"
            ;;
        *)
            error "Unsupported font format: $file"
            return 1
            ;;
    esac
}

# Install essential fonts
install_essential_fonts() {
    log "Installing essential font bundle..."

    # 1. Perfect DOS VGA 437 (authentic DOS experience)
    log "Installing Perfect DOS VGA 437..."
    if command -v curl >/dev/null 2>&1; then
        # Try alternative source for Perfect DOS VGA
        cat > perfect_dos_vga_437.ttf << 'EOF'
# Note: This would need to be downloaded from a reliable source
# Alternative: Use Liberation Mono or similar as fallback
EOF
        warn "Perfect DOS VGA 437: Manual download required from https://www.dafont.com/perfect-dos-vga-437.font"
    fi

    # 2. GNU Unifont (Unicode coverage)
    log "Installing GNU Unifont..."
    if download_font "https://unifoundry.com/pub/unifont/unifont-15.1.05/font-builds/unifont-15.1.05.ttf" "unifont.ttf" "GNU Unifont"; then
        cp unifont.ttf "$FONT_DIR/GNU-Unifont.ttf"
        success "Installed GNU-Unifont.ttf"
    else
        warn "GNU Unifont download failed - manual installation required"
    fi

    # 3. DotGothic16 (from Google Fonts)
    log "Installing DotGothic16..."
    if download_font "https://fonts.gstatic.com/s/dotgothic16/v15/v6-QGYjBJFKgyw5nSoDAGE7L4Bh7Lg.ttf" "dotgothic16.ttf" "DotGothic16"; then
        cp dotgothic16.ttf "$FONT_DIR/DotGothic16.ttf"
        success "Installed DotGothic16.ttf"
    else
        warn "DotGothic16 download failed - try Google Fonts manually"
    fi

    # 4. Pixel Operator (modern pixel font)
    log "Installing Pixel Operator..."
    # This would need to be downloaded from the official source
    warn "Pixel Operator: Manual download required from https://notfonts.com/pixel-operator/"

    # 5. Pet Me 64 (C64 font) - check if microknight is sufficient
    if [[ -f "$FONT_DIR/microknight.ttf" ]]; then
        success "C64-style font already available (microknight.ttf)"
    else
        warn "Pet Me 64: Manual download required from https://style64.org/c64-truetype"
    fi

    # 6. Valova (tile-based font)
    warn "Valova: Manual download required from retro font collections"
}

# Create fallback fonts for manual downloads
create_fallback_info() {
    log "Creating download instructions for manual fonts..."

    cat > "$FONT_DIR/MANUAL-DOWNLOAD-REQUIRED.md" << 'EOF'
# Manual Font Downloads Required

Some fonts require manual download due to licensing or availability:

## Required Downloads:

### 1. Perfect DOS VGA 437
- **Source**: https://www.dafont.com/perfect-dos-vga-437.font
- **File**: Download ZIP, extract TTF
- **Install as**: `Perfect-DOS-VGA-437.ttf`

### 2. Pixel Operator
- **Source**: https://notfonts.com/pixel-operator/
- **File**: Download TTF
- **Install as**: `Pixel-Operator.ttf`

### 3. Pet Me 64 (if microknight.ttf insufficient)
- **Source**: https://style64.org/c64-truetype
- **Alternative**: https://www.dafont.com/pet-me-64.font
- **Install as**: `Pet-Me-64.ttf`

### 4. Valova
- **Source**: Search itch.io or retro font collections
- **Install as**: `Valova.ttf`

## Installation:
1. Download the font files
2. Copy TTF files to: `/uMEMORY/system/fonts/`
3. Run font registry update: `./dev/scripts/update-font-registry.sh`

## Test Installation:
```bash
ls -la /Users/agentdigital/uDOS/uMEMORY/system/fonts/
```
EOF

    success "Created manual download guide"
}

# Update font registry to reflect simplified MODE7 setup
update_font_registry() {
    log "Updating font registry..."

    # Create updated font registry focusing on available fonts
    cat > "$FONT_DIR/../uDATA-font-registry.json" << 'EOF'
{"METADATA":{"version":"1.1","created":"2025-08-23","description":"uDOS Simplified Font Registry","last_updated":"2025-08-23T15:00:00Z"},"SYSTEM":{"MODE7GX0":{"name":"MODE7 GX0 - Teletext","family":"MODE7GX0","file":"MODE7GX0.TTF","size":"18px","description":"BBC Mode 7 teletext font - primary display","default":true,"category":"teletext"},"POT_NOODLE":{"name":"Pot Noodle","family":"PotNoodle","file":"pot_noodle.ttf","size":"18px","description":"Chunky pixel font for headers","category":"display"},"MICROKNIGHT":{"name":"MicroKnight","family":"MicroKnight","file":"microknight.ttf","size":"14px","description":"C64-inspired pixel font","category":"retro"}},"FALLBACKS":{"monospace":["SF Mono","Monaco","Menlo","Consolas","Courier New","monospace"],"sans_serif":["SF Pro Display","Helvetica Neue","Arial","sans-serif"],"serif":["Times New Roman","serif"]}}
EOF

    success "Updated font registry with simplified configuration"
}

# Main installation
main() {
    echo -e "${BLUE}╭─ uDOS Font Bundle Installer ─────────────────────╮${NC}"
    echo -e "${BLUE}│ Installing essential retro/pixel fonts          │${NC}"
    echo -e "${BLUE}│ Keeping MODE7GX0.TTF as primary teletext font   │${NC}"
    echo -e "${BLUE}╰─────────────────────────────────────────────────╯${NC}"
    echo

    # Check if font directory exists
    if [[ ! -d "$FONT_DIR" ]]; then
        error "Font directory not found: $FONT_DIR"
        exit 1
    fi

    # Show current fonts
    log "Current fonts in $FONT_DIR:"
    ls -la "$FONT_DIR" | grep -E '\.(ttf|TTF)$' || echo "  No TTF fonts found"
    echo

    # Install fonts
    install_essential_fonts
    echo

    # Create manual download guide
    create_fallback_info
    echo

    # Update registry
    update_font_registry
    echo

    # Show final status
    log "Font installation completed!"
    log "Current font inventory:"
    ls -la "$FONT_DIR"/*.ttf "$FONT_DIR"/*.TTF 2>/dev/null | wc -l | xargs echo "  TTF files:"

    echo
    success "Font bundle installation complete!"
    log "See $FONT_DIR/MANUAL-DOWNLOAD-REQUIRED.md for manual downloads"
    log "Test fonts: ls -la $FONT_DIR"

    # Cleanup
    cd /
    rm -rf "$TEMP_DIR"
}

# Check dependencies
if ! command -v curl >/dev/null 2>&1; then
    warn "curl not found - some downloads may fail"
fi

if ! command -v unzip >/dev/null 2>&1; then
    warn "unzip not found - ZIP extraction may fail"
fi

# Run installation
main "$@"
