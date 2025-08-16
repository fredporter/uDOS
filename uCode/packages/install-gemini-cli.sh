#!/bin/bash

# uCode/packages/install-gemini-cli.sh  
# Package installer for Google Gemini CLI extension
# Part of uDOS package management system

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}[PACKAGE]${NC} Installing Google Gemini CLI Extension for uDOS..."
echo -e "${YELLOW}[INFO]${NC} This will install the official Google Gemini CLI with uDOS integration"
echo

# Navigate to extension directory and run installer
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EXTENSION_DIR="$UDOS_ROOT/uExtensions/ai/gemini-cli"

if [[ -d "$EXTENSION_DIR" ]]; then
    cd "$EXTENSION_DIR"
    if [[ -x "install-gemini-cli.sh" ]]; then
        ./install-gemini-cli.sh
    else
        echo -e "${YELLOW}[WARNING]${NC} Installation script not found or not executable"
        exit 1
    fi
else
    echo -e "${YELLOW}[WARNING]${NC} Gemini CLI extension directory not found"
    echo -e "${YELLOW}[INFO]${NC} Please ensure uDOS repository is properly organized"
    exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} Gemini CLI extension installation complete!"
echo -e "${CYAN}[USAGE]${NC} Run 'assist' or 'command' from uCode shell to start AI assistance"
