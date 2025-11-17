#!/bin/bash

# uDOS Extension Setup: C64 CSS3
# Setup script for C64 CSS3 framework
# https://github.com/RoelN/c64css3

set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

EXTENSION_NAME="c64css3"
REPO_URL="https://github.com/RoelN/c64css3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE_DIR="$SCRIPT_DIR/../cloned/c64css3"

echo "🎮 uDOS Extension Setup: ${EXTENSION_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to check internet connectivity
check_online() {
    if ping -c 1 -W 2 github.com &> /dev/null; then
        return 0
    else
        return 1
    fi
}

print_status "Setting up ${EXTENSION_NAME} (Commodore 64 CSS3 framework)..."

# Create clone directory if it doesn't exist
mkdir -p "$(dirname "${CLONE_DIR}")"

# Check if c64css3 already exists
if [ -d "$CLONE_DIR" ] && [ -f "$CLONE_DIR/css.css" ]; then
    print_success "C64 CSS3 is already installed"
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
    exit 1
fi

print_status "Cloning C64 CSS3 repository..."

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

# Verify installation
if [ -d "$CLONE_DIR" ] && [ -f "$CLONE_DIR/css.css" ]; then
    print_success "C64 CSS3 framework installed successfully!"
    print_status "Location: $CLONE_DIR"
    print_status "Main CSS: $CLONE_DIR/css.css"
    print_status "Demo: Open $CLONE_DIR/index.html in browser"
    print_status "Integration: Import css.css in your web projects"
else
    print_error "Installation verification failed"
    exit 1
fi

print_success "Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
