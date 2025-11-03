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
print_status "Setup includes: micro editor, typo web editor, monaspace fonts"
print_warning "CMD terminal is optional and can be installed separately"
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
    if bash "$SCRIPT_DIR/setup_typo.sh"; then
        print_success "typo editor setup complete"
    else
        print_warning "typo editor setup failed (non-critical)"
    fi
else
    print_warning "typo setup script not found"
fi
echo

# Setup monaspace fonts
print_header "Setting up monaspace fonts..."
if [ -f "$SCRIPT_DIR/setup_monaspace.sh" ]; then
    if bash "$SCRIPT_DIR/setup_monaspace.sh"; then
        print_success "monaspace fonts setup complete"
    else
        print_warning "monaspace fonts setup failed (non-critical)"
    fi
else
    print_warning "monaspace setup script not found"
fi
echo

# Setup CSS frameworks
print_header "Setting up CSS frameworks..."

# Setup Classicy (Mac OS 8)
if [ -f "$SCRIPT_DIR/setup_classicy.sh" ]; then
    if bash "$SCRIPT_DIR/setup_classicy.sh"; then
        print_success "Classicy (Mac OS 8) setup complete"
    else
        print_warning "Classicy setup failed (non-critical)"
    fi
fi

# Setup C64 CSS3
if [ -f "$SCRIPT_DIR/setup_c64css3.sh" ]; then
    if bash "$SCRIPT_DIR/setup_c64css3.sh"; then
        print_success "C64 CSS3 framework setup complete"
    else
        print_warning "C64 CSS3 setup failed (non-critical)"
    fi
fi

# Setup NES.css
if [ -f "$SCRIPT_DIR/setup_nes.sh" ]; then
    if bash "$SCRIPT_DIR/setup_nes.sh"; then
        print_success "NES.css framework setup complete"
    else
        print_warning "NES.css setup failed (non-critical)"
    fi
fi
echo

# Optional CMD setup
print_header "Optional: CMD terminal setup"
print_status "CMD terminal can be installed separately if needed"
print_status "Run: bash $SCRIPT_DIR/setup_cmd.sh"
echo

print_success "🎉 uDOS Extensions setup complete!"
echo
print_status "Bundled extensions (always available):"
print_status "  • Dashboard - Multi-theme system interface"
print_status "  • Shared Libraries - Common CSS/JS frameworks"
print_status "  • System Desktop - Desktop environment"
print_status "  • Teletext - Broadcast TV interface"
echo
print_status "External dependencies (now installed):"
print_status "  • micro - Modern terminal editor"
print_status "  • typo - Web-based markdown editor"
print_status "  • monaspace - Modern coding fonts"
print_status "  • Classicy - Mac OS 8 Platinum interface"
print_status "  • C64 CSS3 - Commodore 64 styling framework"
print_status "  • NES.css - 8-bit Nintendo styling framework"
echo
print_status "Location: $SCRIPT_DIR/../cloned/"
print_status "Use 'EDIT <file>' in uDOS to access editors"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
