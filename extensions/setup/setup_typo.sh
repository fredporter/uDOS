#!/bin/bash
# uDOS Extension Setup: typo Editor
# Clones and installs the typo markdown editor for uDOS

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
EXTENSION_NAME="typo"
REPO_URL="https://github.com/rossrobino/typo"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE_DIR="$SCRIPT_DIR/../cloned/typo"

print_status "Setting up ${EXTENSION_NAME} editor..."

# Check if Node.js is available
if ! command -v node >/dev/null 2>&1; then
    print_error "Node.js not found. Please install Node.js 18+ to use ${EXTENSION_NAME}"
    print_status "Visit: https://nodejs.org"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "${NODE_VERSION}" -lt 18 ]; then
    print_error "Node.js 18+ required (found v${NODE_VERSION})"
    print_status "Please upgrade Node.js: https://nodejs.org"
    exit 1
fi

# Create clone directory if it doesn't exist
mkdir -p "$(dirname "${CLONE_DIR}")"

# Check if already installed
if [ -d "${CLONE_DIR}" ] && [ -f "${CLONE_DIR}/package.json" ]; then
    if [ -z "${UDOS_AUTO_INSTALL}" ]; then
        print_warning "${EXTENSION_NAME} already installed at ${CLONE_DIR}"
        read -p "Reinstall? (y/N): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            print_status "Skipping ${EXTENSION_NAME} installation"
            exit 0
        fi
    else
        print_success "${EXTENSION_NAME} already installed"
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

# Install dependencies
print_status "Installing ${EXTENSION_NAME} dependencies..."
npm install

# Build the project
print_status "Building ${EXTENSION_NAME}..."
npm run build

# Verify installation
if [ -f "package.json" ] && [ -d "node_modules" ]; then
    print_success "${EXTENSION_NAME} installation complete!"
    print_status "Location: $(pwd)"
    print_status "Usage: SERVER START typo"
    print_status "       EDIT --web filename.md"
else
    print_error "${EXTENSION_NAME} installation failed"
    exit 1
fi
