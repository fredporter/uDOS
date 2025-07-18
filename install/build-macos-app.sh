#!/bin/bash
# uDOS v1.0 macOS App Bundle Builder
# Creates a standalone .app for distribution

set -euo pipefail

# Configuration
APP_NAME="uDOS"
APP_VERSION="1.0.0"
BUNDLE_ID="com.fredporter.udos"
BUILD_DIR="./build"
APP_DIR="$BUILD_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                📱 uDOS v1.0 macOS App Builder                    ║"
    echo "║                  Creating Standalone .app                       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        log_error "This script must be run on macOS"
        exit 1
    fi
    
    if ! command -v xcode-select &> /dev/null; then
        log_error "Xcode command line tools required"
        log_info "Install with: xcode-select --install"
        exit 1
    fi
    
    log_success "Prerequisites met"
}

# Clean and create build directory
setup_build_directory() {
    log_info "Setting up build directory..."
    
    if [[ -d "$BUILD_DIR" ]]; then
        rm -rf "$BUILD_DIR"
    fi
    
    mkdir -p "$MACOS_DIR"
    mkdir -p "$RESOURCES_DIR"
    
    log_success "Build directory created"
}

# Create Info.plist
create_info_plist() {
    log_info "Creating Info.plist..."
    
    cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>uDOS</string>
    <key>CFBundleExecutable</key>
    <string>uDOS</string>
    <key>CFBundleIconFile</key>
    <string>uDOS.icns</string>
    <key>CFBundleIdentifier</key>
    <string>$BUNDLE_ID</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>uDOS</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$APP_VERSION</string>
    <key>CFBundleVersion</key>
    <string>$APP_VERSION</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 Fred Porter. All rights reserved.</string>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.developer-tools</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>md</string>
                <string>markdown</string>
            </array>
            <key>CFBundleTypeName</key>
            <string>Markdown Document</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>LSTypeIsPackage</key>
            <false/>
        </dict>
    </array>
    <key>UTExportedTypeDeclarations</key>
    <array>
        <dict>
            <key>UTTypeIdentifier</key>
            <string>com.fredporter.udos.uscript</string>
            <key>UTTypeDescription</key>
            <string>uScript Document</string>
            <key>UTTypeTagSpecification</key>
            <dict>
                <key>public.filename-extension</key>
                <array>
                    <string>us</string>
                    <string>uscript</string>
                </array>
            </dict>
        </dict>
    </array>
</dict>
</plist>
EOF
    
    log_success "Info.plist created"
}

# Create launcher script
create_launcher_script() {
    log_info "Creating launcher script..."
    
    cat > "$MACOS_DIR/uDOS" << 'EOF'
#!/bin/bash
# uDOS macOS App Launcher

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
UDOS_DIR="$APP_DIR/Contents/Resources/uDOS"

# Set up environment
export UDOS_APP_MODE=true
export UDOS_INSTALL_DIR="$UDOS_DIR"

# Check if uDOS is installed in app bundle
if [[ ! -d "$UDOS_DIR" ]]; then
    # First run - install uDOS
    osascript -e 'display dialog "Welcome to uDOS!\n\nThis appears to be your first run. uDOS will now set itself up." with title "uDOS First Run" buttons {"Continue"} default button "Continue"'
    
    # Create uDOS directory
    mkdir -p "$UDOS_DIR"
    
    # Download and install uDOS
    if command -v git &> /dev/null; then
        cd "$(dirname "$UDOS_DIR")"
        git clone https://github.com/fredporter/uDOS.git uDOS
        cd "$UDOS_DIR"
        chmod +x uCode/*.sh start-udos.sh
    else
        osascript -e 'display dialog "Git is required for uDOS installation.\n\nPlease install Xcode Command Line Tools first:\n\nxcode-select --install" with title "uDOS Setup Error" buttons {"OK"} default button "OK"'
        exit 1
    fi
fi

# Change to uDOS directory
cd "$UDOS_DIR"

# Open in terminal with uDOS
if command -v code &> /dev/null; then
    # Open in VS Code if available
    osascript << APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$UDOS_DIR' && echo '🧙‍♂️ Welcome to uDOS v1.0 - The Markdown-Native Operating System!' && echo '' && echo 'Opening in VS Code for optimal experience...' && code . && ./start-udos.sh"
end tell
APPLESCRIPT
else
    # Open in Terminal only
    osascript << APPLESCRIPT
tell application "Terminal"
    activate
    do script "cd '$UDOS_DIR' && echo '🧙‍♂️ Welcome to uDOS v1.0 - The Markdown-Native Operating System!' && echo '' && ./start-udos.sh"
end tell
APPLESCRIPT
fi
EOF
    
    chmod +x "$MACOS_DIR/uDOS"
    log_success "Launcher script created"
}

# Copy icon
copy_icon() {
    log_info "Setting up app icon..."
    
    if [[ -f "launcher/assets/diamond.icns" ]]; then
        cp "launcher/assets/diamond.icns" "$RESOURCES_DIR/uDOS.icns"
        log_success "App icon copied"
    else
        log_warning "Icon file not found - using default"
        # Create a simple icon placeholder
        mkdir -p temp_icon.iconset
        # This would normally require actual icon creation
        # For now, we'll skip the icon
    fi
}

# Create DMG installer
create_dmg() {
    log_info "Creating DMG installer..."
    
    local dmg_name="uDOS-v$APP_VERSION-macOS.dmg"
    local temp_dmg="temp-$dmg_name"
    
    # Create temporary DMG
    hdiutil create -size 100m -fs HFS+ -volname "uDOS v$APP_VERSION" "$temp_dmg"
    
    # Mount DMG
    local mount_point="/Volumes/uDOS v$APP_VERSION"
    hdiutil attach "$temp_dmg"
    
    # Copy app to DMG
    cp -R "$APP_DIR" "$mount_point/"
    
    # Create Applications symlink
    ln -s /Applications "$mount_point/Applications"
    
    # Add README
    cat > "$mount_point/README.txt" << EOF
uDOS v$APP_VERSION - Markdown-Native Operating System

Installation:
1. Drag uDOS.app to the Applications folder
2. Launch uDOS from Applications or Launchpad
3. Follow the setup wizard

Requirements:
- macOS 10.15 or later
- Git (Xcode Command Line Tools)
- VS Code (recommended)

For support and documentation:
https://github.com/fredporter/uDOS

Copyright © 2024 Fred Porter
EOF
    
    # Unmount DMG
    hdiutil detach "$mount_point"
    
    # Convert to compressed DMG
    hdiutil convert "$temp_dmg" -format UDZO -o "$dmg_name"
    rm "$temp_dmg"
    
    log_success "DMG created: $dmg_name"
}

# Set app permissions and signature (basic)
finalize_app() {
    log_info "Finalizing app bundle..."
    
    # Set proper permissions
    chmod -R 755 "$APP_DIR"
    chmod +x "$MACOS_DIR/uDOS"
    
    # Create PkgInfo
    echo -n "APPL????" > "$CONTENTS_DIR/PkgInfo"
    
    # Note: For distribution, you would need to sign the app:
    # codesign --force --deep --sign "Developer ID Application: Your Name" "$APP_DIR"
    
    log_success "App bundle finalized"
    log_warning "Note: App is not code-signed. For distribution, signing is required."
}

# Main build process
main() {
    print_header
    
    echo "This will create a standalone uDOS.app for macOS distribution."
    echo "The app will include a launcher that sets up uDOS on first run."
    echo ""
    
    read -p "Continue with build? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_info "Build cancelled by user"
        exit 0
    fi
    
    echo ""
    check_prerequisites
    setup_build_directory
    create_info_plist
    create_launcher_script
    copy_icon
    finalize_app
    
    if command -v hdiutil &> /dev/null; then
        echo ""
        read -p "Create DMG installer? (y/N): " create_dmg_confirm
        if [[ "$create_dmg_confirm" =~ ^[Yy]$ ]]; then
            create_dmg
        fi
    fi
    
    echo ""
    log_success "macOS app bundle created successfully!"
    echo ""
    echo "📱 App bundle: $APP_DIR"
    echo "📦 Ready for distribution"
    echo ""
    echo "Next steps:"
    echo "1. Test the app bundle"
    echo "2. Code sign for distribution (requires Developer ID)"
    echo "3. Notarize for Gatekeeper compatibility"
    echo "4. Distribute via DMG or direct download"
    echo ""
    echo "For testing: open '$APP_DIR'"
}

# Error handling
trap 'log_error "Build failed on line $LINENO"' ERR

# Run main build
main "$@"
