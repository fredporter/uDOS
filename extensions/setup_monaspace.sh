#!/bin/bash
# uDOS Extension Setup: Monaspace Fonts
# Clones and installs the Monaspace font family for uDOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Extension details
EXTENSION_NAME="monaspace"
REPO_URL="https://github.com/githubnext/monaspace"
CLONE_DIR="extensions/clone/monaspace-fonts"

print_status "Setting up ${EXTENSION_NAME} fonts..."

# Create clone directory if it doesn't exist
mkdir -p "$(dirname "${CLONE_DIR}")"

# Check if already installed
if [ -d "${CLONE_DIR}/fonts" ]; then
    if [ -z "${UDOS_AUTO_INSTALL}" ]; then
        print_warning "${EXTENSION_NAME} fonts already installed at ${CLONE_DIR}"
        read -p "Reinstall? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            print_status "Skipping ${EXTENSION_NAME} installation"
            exit 0
        fi
    else
        print_success "${EXTENSION_NAME} fonts already installed"
        exit 0
    fi
fi

# Remove existing directory if present
if [ -d "${CLONE_DIR}" ]; then
    print_status "Removing existing ${EXTENSION_NAME} installation..."
    rm -rf "${CLONE_DIR}"
fi

# Clone the repository
print_status "Cloning ${EXTENSION_NAME} from ${REPO_URL}..."
git clone "${REPO_URL}" "${CLONE_DIR}"

cd "${CLONE_DIR}"

# Verify fonts directory exists
if [ -d "fonts" ]; then
    FONT_COUNT=$(find fonts -name "*.woff2" | wc -l)
    print_success "${EXTENSION_NAME} fonts installation complete!"
    print_status "Location: $(pwd)/fonts"
    print_status "Fonts available: ${FONT_COUNT} .woff2 files"
    print_status "Usage: FONT --list"
    print_status "       FONT --set neon"
else
    print_error "${EXTENSION_NAME} fonts installation failed - fonts directory not found"
    exit 1
fi
