#!/bin/bash

# uDOS Extension Setup: Classicy Desktop
# Setup script for Classicy (Mac OS 8 Platinum interface)
# https://github.com/robbiebyrd/classicy

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

EXTENSION_NAME="classicy-desktop"
REPO_URL="https://github.com/robbiebyrd/classicy"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE_DIR="$SCRIPT_DIR/../cloned/classicy-desktop"

echo "🎨 uDOS Extension Setup: ${EXTENSION_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to check internet connectivity
check_online() {
    if ping -c 1 -W 2 github.com &> /dev/null; then
        return 0
    else
        return 1
    fi
}

print_status "Setting up ${EXTENSION_NAME} (Mac OS 8 Platinum interface)..."

# Create clone directory if it doesn't exist
mkdir -p "$(dirname "${CLONE_DIR}")"

# Check if classicy already exists and is functional
if [ -d "$CLONE_DIR" ] && [ -f "$CLONE_DIR/package.json" ]; then
    print_success "Classicy is already installed"
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

print_status "Cloning Classicy repository..."

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

# Check if Node.js is available for building
if command -v npm &> /dev/null; then
    print_status "Installing dependencies..."
    if npm install; then
        print_success "Dependencies installed"

        print_status "Building Classicy..."
        if npm run build 2>/dev/null; then
            print_success "Build completed successfully"
        else
            print_warning "Build failed, but source is available"
        fi
    else
        print_warning "npm install failed, but source is available"
    fi
else
    print_warning "npm not found - Classicy will need manual building"
    print_status "Install Node.js to build the project"
fi

# Verify installation
if [ -d "$CLONE_DIR" ] && [ -f "$CLONE_DIR/package.json" ]; then
    print_success "Classicy desktop installed successfully!"
    print_status "Location: $CLONE_DIR"
    print_status "To run: npm run serve (requires Node.js)"
    print_status "Then visit: http://localhost:3000"
else
    print_error "Installation verification failed"
    exit 1
fi

print_success "Setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
