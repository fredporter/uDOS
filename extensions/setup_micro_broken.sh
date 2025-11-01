#!/bin/bash#!/bin/bash

# uDOS Extension Setup: micro Editor# Setup script for micro editor

# Clones and installs the micro text editor for uDOS# uDOS v1.0.0 Extension Installer



set -e# Don't exit on error - we handle errors gracefully

set +e

# Colors for output

RED='\033[0;31m'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'MICRO_DIR="$SCRIPT_DIR/forks/micro"

YELLOW='\033[0;33m'MICRO_BIN="$MICRO_DIR/micro"

BLUE='\033[0;34m'

NC='\033[0m' # No Colorecho "🔧 uDOS Extension Setup: micro editor"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to print colored output

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }# Ensure forks directory exists

print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }mkdir -p "$SCRIPT_DIR/forks"

print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

print_error() { echo -e "${RED}[ERROR]${NC} $1"; }# Function to check internet connectivity

check_online() {

# Extension details    if ping -c 1 -W 2 github.com &> /dev/null; then

EXTENSION_NAME="micro"        return 0

REPO_URL="https://github.com/zyedidia/micro"    else

CLONE_DIR="extensions/clone/native/micro"        return 1

BINARY_NAME="micro"    fi

}

print_status "Setting up ${EXTENSION_NAME} editor..."

# Check if micro already exists and is functional

# Create clone directory if it doesn't exist
mkdir -p "$(dirname "${CLONE_DIR}")"

if [ -f "$MICRO_BIN" ]; then
    if "$MICRO_BIN" --version &> /dev/null; then

        echo "✅ micro is already installed and functional"

# Check if already installed        echo "📍 Location: $MICRO_BIN"

if [ -f "${CLONE_DIR}/${BINARY_NAME}" ]; then        echo "📦 Version: $("$MICRO_BIN" --version | head -1)"

    if [ -z "${UDOS_AUTO_INSTALL}" ]; then

        print_warning "${EXTENSION_NAME} already installed at ${CLONE_DIR}/${BINARY_NAME}"        # Skip prompt if auto-installing from dashboard

        read -p "Reinstall? (y/N): " confirm        if [ -z "$UDOS_AUTO_INSTALL" ]; then

        if [[ ! $confirm =~ ^[Yy]$ ]]; then            read -p "Reinstall anyway? (y/n): " -n 1 -r

            print_status "Skipping ${EXTENSION_NAME} installation"            echo

            exit 0            if [[ ! $REPLY =~ ^[Yy]$ ]]; then

        fi                echo "✅ Setup complete (using existing installation)"

    else                exit 0

        print_success "${EXTENSION_NAME} already installed"            fi

        exit 0        else

    fi            echo "ℹ️  Auto-install mode: using existing installation"

fi            exit 0

        fi

# Remove existing directory if present

if [ -d "${CLONE_DIR}" ]; then        echo "🗑️  Removing existing installation..."

    print_status "Removing existing ${EXTENSION_NAME} installation..."        rm -rf "$MICRO_DIR"

    rm -rf "${CLONE_DIR}"    fi

fifi



# Clone the repository# Check if we're online (needed for download)

print_status "Cloning ${EXTENSION_NAME} from ${REPO_URL}..."if ! check_online; then

git clone "${REPO_URL}" "${CLONE_DIR}"    echo "❌ ERROR: No internet connection detected"

    echo "🌐 Cannot download micro editor while offline"

cd "${CLONE_DIR}"    echo ""

    echo "💡 To install manually:"

# Build micro    echo "   1. Visit: https://github.com/zyedidia/micro/releases"

print_status "Building ${EXTENSION_NAME}..."    echo "   2. Download the release for your platform"

if command -v go >/dev/null 2>&1; then    echo "   3. Extract to: $MICRO_DIR"

    make build    echo "   4. Ensure binary is named 'micro' and is executable"

    if [ -f "${BINARY_NAME}" ]; then    exit 1

        print_success "${EXTENSION_NAME} built successfully"fi

    else

        print_error "Build failed - ${BINARY_NAME} binary not found"# Detect platform

        exit 1OS="$(uname -s)"

    fiARCH="$(uname -m)"

else

    print_error "Go compiler not found. Please install Go to build micro."case "$OS" in

    print_status "Alternative: Download pre-built binary from releases"    Linux*)

            OS_NAME="linux"

    # Detect platform for download        ;;

    OS=$(uname -s | tr '[:upper:]' '[:lower:]')    Darwin*)

    ARCH=$(uname -m)        OS_NAME="osx"

            ;;

    case "${ARCH}" in    MINGW*|MSYS*|CYGWIN*)

        x86_64) ARCH="amd64" ;;        OS_NAME="win"

        aarch64|arm64) ARCH="arm64" ;;        ;;

        armv7l) ARCH="arm" ;;    *)

        *) ARCH="amd64" ;;        echo "❌ ERROR: Unsupported operating system: $OS"

    esac        exit 1

            ;;

    case "${OS}" inesac

        darwin) OS="osx" ;;

        linux) OS="linux" ;;case "$ARCH" in

        *) print_error "Unsupported OS: ${OS}"; exit 1 ;;    x86_64|amd64)

    esac        ARCH_NAME="amd64"

            ;;

    VERSION="v2.0.14"    arm64|aarch64)

    FILENAME="micro-${VERSION}-${OS}-${ARCH}.tar.gz"        ARCH_NAME="arm64"

    DOWNLOAD_URL="https://github.com/zyedidia/micro/releases/download/${VERSION}/${FILENAME}"        ;;

        armv7l|armv6l)

    print_status "Downloading pre-built ${EXTENSION_NAME} ${VERSION}..."        ARCH_NAME="arm"

    curl -L "${DOWNLOAD_URL}" -o "${FILENAME}"        ;;

        *)

    print_status "Extracting ${EXTENSION_NAME}..."        echo "⚠️  WARNING: Unknown architecture: $ARCH, using amd64"

    tar -xzf "${FILENAME}"        ARCH_NAME="amd64"

            ;;

    # Move binary to expected locationesac

    EXTRACTED_DIR="micro-${VERSION}"

    if [ -f "${EXTRACTED_DIR}/micro" ]; then# Construct download URL

        mv "${EXTRACTED_DIR}/micro" .VERSION="v2.0.14"

        rm -rf "${EXTRACTED_DIR}" "${FILENAME}"VERSION_NUM="2.0.14"  # Without 'v' prefix

        print_success "${EXTENSION_NAME} installed successfully"

    elseif [ "$OS_NAME" = "win" ]; then

        print_error "Failed to extract ${EXTENSION_NAME} binary"    FILENAME="micro-${VERSION_NUM}-win64.zip"

        exit 1elif [ "$OS_NAME" = "linux" ]; then

    fi    if [ "$ARCH_NAME" = "arm64" ]; then

fi        FILENAME="micro-${VERSION_NUM}-linux-arm64.tar.gz"

    elif [ "$ARCH_NAME" = "arm" ]; then

# Make binary executable        FILENAME="micro-${VERSION_NUM}-linux-arm.tar.gz"

chmod +x "${BINARY_NAME}"    else

        FILENAME="micro-${VERSION_NUM}-linux64.tar.gz"

print_success "${EXTENSION_NAME} installation complete!"    fi

print_status "Location: $(pwd)/${BINARY_NAME}"elif [ "$OS_NAME" = "osx" ]; then

print_status "Usage: EDIT --editor micro filename.txt"    # macOS builds are universal
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
