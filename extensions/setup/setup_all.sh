#!/bin/bash

# uDOS Extensions Master Setup Script
# Installs all external dependencies for uDOS extensions
# Updated for new extensions structure

set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${PURPLE}[SETUP]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 uDOS Extensions Master Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
print_header "This will install external dependencies for uDOS extensions"
print_status "Setup includes: micro editor and typo web editor"
print_status "All CSS frameworks are now bundled in /core"
echo

# Function to check internet connectivity
check_online() {
    if ping -c 1 -W 2 github.com &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check prerequisites
print_header "Checking prerequisites..."

if ! check_online; then
    print_error "No internet connection. Cannot download external dependencies."
    exit 1
fi

if ! command -v git &> /dev/null; then
    print_error "git is required but not installed."
    print_status "Please install git and try again"
    exit 1
fi

print_success "Prerequisites satisfied"
echo

# Setup micro editor
print_header "Setting up micro editor..."
if [ -f "$SCRIPT_DIR/setup_micro.sh" ]; then
    if bash "$SCRIPT_DIR/setup_micro.sh"; then
        print_success "micro editor setup complete"
    else
        print_warning "micro editor setup failed (non-critical)"
    fi
else
    print_warning "micro setup script not found"
fi
echo

# Setup typo editor
print_header "Setting up typo web editor..."
if [ -f "$SCRIPT_DIR/setup_typo.sh" ]; then
    export UDOS_AUTO_INSTALL=1  # Skip confirmation prompts
    if bash "$SCRIPT_DIR/setup_typo.sh"; then
        print_success "typo editor setup complete"
    else
        print_warning "typo editor setup failed (non-critical)"
        print_status "You can run setup_typo.sh manually later"
    fi
    unset UDOS_AUTO_INSTALL
else
    print_warning "typo setup script not found"
fi
echo

# Optional: Archived setup scripts
print_header "Additional Extensions"
print_status "Archived setup scripts available in extensions/archive/old-setup-scripts/"
print_status "  • setup_classicy.sh - Mac OS 8 framework (now bundled)"
print_status "  • setup_c64css3.sh - C64 framework (now bundled)"
print_status "  • setup_nes.sh - NES framework (now bundled)"
print_status "  • setup_cmd.sh - CMD terminal (optional)"
print_status "  • setup_monaspace.sh - Monaspace fonts (optional)"
echo

print_success "🎉 uDOS Extensions setup complete!"
echo
print_status "Core extensions (always bundled):"
print_status "  • C64 Terminal - Commodore 64 interface"
print_status "  • Character Editor - Font/sprite editor"
print_status "  • Dashboard - Multi-theme system interface"
print_status "  • Desktop - System 7 desktop environment"
print_status "  • Markdown - Web-based markdown viewer"
print_status "  • Teletext - BBC Teletext broadcast interface"
echo
print_status "External dependencies (installed):"
print_status "  • micro - Modern terminal editor"
print_status "  • typo - Web-based markdown editor (if Node.js available)"
echo
print_status "Shared components:"
print_status "  • CSS frameworks (Synthwave DOS, System 7, NES.css)"
print_status "  • JavaScript utilities (window manager, typography)"
print_status "  • Retro themes (C64, Teletext, Synthwave)"
echo
print_status "Location: $SCRIPT_DIR/../"
print_status "Use 'EDIT <file>' in uDOS to access editors"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
