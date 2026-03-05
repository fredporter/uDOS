#!/usr/bin/env bash

# Dev Mode Tooling Installation Script
# Installs or updates the globally installed `vibe` runtime used by the uDOS Dev Mode lane.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

function info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

function success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

function warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

function check_platform() {
    local platform=$(uname -s)

    if [[ "$platform" == "Linux" ]]; then
        info "Detected Linux platform"
        PLATFORM="linux"
    elif [[ "$platform" == "Darwin" ]]; then
        info "Detected macOS platform"
        PLATFORM="macos"
    else
        error "Unsupported platform: $platform"
        error "This installation script currently only supports Linux and macOS"
        exit 1
    fi
}

function check_vibe_installed() {
    if command -v vibe &> /dev/null; then
        info "vibe is already installed"
        VIBE_INSTALLED=true
    else
        VIBE_INSTALLED=false
    fi
}

function install_vibe() {
    info "Installing vibe using official installer..."
    curl -fsSL https://vibe.mistral.ai/install.sh | sh

    success "Vibe installed successfully! (commands: vibe, vibe-acp)"
}

function update_vibe() {
    info "Updating vibe using official installer..."
    curl -fsSL https://vibe.mistral.ai/install.sh | sh

    success "Vibe updated successfully!"
}

function main() {
    echo
    echo "██████████████████░░"
    echo "██████████████████░░"
    echo "████  ██████  ████░░"
    echo "████    ██    ████░░"
    echo "████          ████░░"
    echo "████  ██  ██  ████░░"
    echo "██      ██      ██░░"
    echo "██████████████████░░"
    echo "██████████████████░░"
    echo
    echo "Starting Vibe installation..."
    echo

    check_platform

    check_vibe_installed

    if [[ "$VIBE_INSTALLED" == "false" ]]; then
        install_vibe
    else
        update_vibe
    fi

    if command -v vibe &> /dev/null; then
        success "Installation completed successfully!"
        echo
        echo "You can now run vibe with:"
        echo "  vibe"
        echo
        echo "Or for ACP mode:"
        echo "  vibe-acp"
    else
        error "Installation completed but 'vibe' command not found"
        error "Please check your installation and PATH settings"
        exit 1
    fi
}

main
