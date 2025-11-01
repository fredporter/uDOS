#!/bin/bash

# uDOS Extension Setup: micro Editor
# Setup script for micro editor
# uDOS v1.0.2 Extension Installer

# Don't exit on error - we handle errors gracefully
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔧 uDOS Extension Setup: micro editor"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to print colored output
print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Extension details
EXTENSION_NAME="micro"
REPO_URL="https://github.com/zyedidia/micro"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE_DIR="$SCRIPT_DIR/clone/micro"
BINARY_NAME="micro"

# Function to check internet connectivity
check_online() {
    if ping -c 1 -W 2 github.com &> /dev/null; then
        return 0
    else
        return 1
    fi
}

print_status "Setting up ${EXTENSION_NAME} editor..."

# Check if micro already exists and is functional
MICRO_BIN="$CLONE_DIR/micro"

# Create clone directory if it doesn't exist
mkdir -p "$(dirname "${CLONE_DIR}")"

if [ -f "$MICRO_BIN" ]; then
    if "$MICRO_BIN" --version &> /dev/null; then
        print_success "micro is already installed and functional"
        if [ -z "$UDOS_AUTO_INSTALL" ]; then
            read -p "Reinstall? (y/N): " confirm
            if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                print_status "Keeping existing installation"
                exit 0
            fi
        fi
    fi
fi

# Check for --check flag
if [ "$1" = "--check" ]; then
    print_status "Dependency check mode"

    # Check if git is available
    if ! command -v git &> /dev/null; then
        print_error "git is required but not installed"
        exit 1
    fi

    # Check internet connectivity
    if ! check_online; then
        print_error "Internet connection required for installation"
        exit 1
    fi

    print_success "All dependencies available"
    exit 0
fi

# Check internet connectivity
if ! check_online; then
    print_error "No internet connection. Cannot clone repository."
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    print_error "git is required but not installed."
    print_status "Please install git and try again"
    exit 1
fi

print_status "Cloning micro repository..."

# Remove existing clone if present
if [ -d "$CLONE_DIR" ]; then
    print_warning "Removing existing clone..."
    rm -rf "$CLONE_DIR"
fi

# Clone the repository
if git clone "$REPO_URL" "$CLONE_DIR"; then
    print_success "Repository cloned successfully"
else
    print_error "Failed to clone repository"
    exit 1
fi

cd "$CLONE_DIR"

# Check if we have a compiled binary or need to build
print_status "Checking for pre-built binary..."

# Download the latest release binary if available
ARCH=$(uname -m)
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

# Map architecture names
case "$ARCH" in
    x86_64) ARCH="64" ;;
    arm64) ARCH="arm64" ;;
    aarch64) ARCH="arm64" ;;
    *) ARCH="64" ;;
esac

# Map OS names
case "$OS" in
    darwin) OS="osx" ;;
    linux) OS="linux" ;;
    *) OS="linux" ;;
esac

RELEASE_URL="https://github.com/zyedidia/micro/releases/latest/download/micro-${MICRO_VERSION:-*}-${OS}-${ARCH}.tar.gz"

print_status "Attempting to download pre-built binary..."

# Try to get the latest release info
if command -v curl &> /dev/null; then
    LATEST_VERSION=$(curl -s https://api.github.com/repos/zyedidia/micro/releases/latest | grep '"tag_name":' | sed -E 's/.*"v([^"]+)".*/\1/')
    if [ -n "$LATEST_VERSION" ]; then
        BINARY_URL="https://github.com/zyedidia/micro/releases/download/v${LATEST_VERSION}/micro-${LATEST_VERSION}-${OS}-${ARCH}.tar.gz"
        print_status "Downloading micro v${LATEST_VERSION}..."

        if curl -L -o "micro.tar.gz" "$BINARY_URL" 2>/dev/null; then
            if tar -xzf "micro.tar.gz" 2>/dev/null; then
                # Find the extracted binary
                EXTRACTED_BINARY=$(find . -name "micro" -type f -executable | head -1)
                if [ -n "$EXTRACTED_BINARY" ]; then
                    cp "$EXTRACTED_BINARY" ./micro
                    chmod +x ./micro
                    rm -f micro.tar.gz
                    rm -rf micro-*
                    print_success "Pre-built binary installed successfully"
                else
                    print_warning "Could not find binary in downloaded package"
                fi
            else
                print_warning "Could not extract downloaded package"
            fi
        else
            print_warning "Could not download pre-built binary"
        fi
    fi
fi

# If we don't have a working binary, try to build from source
if [ ! -f "./micro" ] || ! ./micro --version &> /dev/null; then
    print_status "Building from source..."

    # Check if Go is available
    if command -v go &> /dev/null; then
        print_status "Go found, building micro..."
        if make build; then
            print_success "Built from source successfully"
        else
            print_error "Failed to build from source"
            exit 1
        fi
    else
        print_error "Neither pre-built binary nor Go compiler available"
        print_status "Please install Go or download micro manually"
        exit 1
    fi
fi

# Verify installation
if [ -f "./micro" ] && ./micro --version &> /dev/null; then
    print_success "micro editor installed successfully!"
    print_status "Binary location: $CLONE_DIR/micro"
    print_status "You can now use 'EDIT <file>' in uDOS"

    # Create symlink in a common location for easy access
    COMMON_BIN="$SCRIPT_DIR/../core/bin"
    mkdir -p "$COMMON_BIN"
    ln -sf "$CLONE_DIR/micro" "$COMMON_BIN/micro" 2>/dev/null || true

else
    print_error "Installation verification failed"
    exit 1
fi

print_success "Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
