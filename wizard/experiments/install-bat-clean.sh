#!/bin/bash
# install-bat-clean.sh - Simple bat installer for uDOS
# Terminal syntax-highlighted file viewer

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

show_header() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                     ${YELLOW}🦇 bat Installation${NC}                      ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}              Syntax-highlighted file viewer                ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

install_bat() {
    log_info "Installing bat via system package manager..."
    
    # Detect OS and install
    case "$(uname -s)" in
        Darwin)
            if command -v brew >/dev/null 2>&1; then
                log_info "Installing via Homebrew..."
                brew install bat
            else
                log_warning "Homebrew not found. Please install Homebrew first:"
                log_info "Visit: https://brew.sh"
                return 1
            fi
            ;;
        Linux)
            if command -v apt >/dev/null 2>&1; then
                log_info "Installing via apt..."
                sudo apt update && sudo apt install -y bat
                # Ubuntu/Debian installs as 'batcat'
                if command -v batcat >/dev/null 2>&1 && ! command -v bat >/dev/null 2>&1; then
                    log_info "Creating bat symlink for batcat..."
                    sudo ln -sf /usr/bin/batcat /usr/local/bin/bat
                fi
            elif command -v yum >/dev/null 2>&1; then
                log_info "Installing via yum..."
                sudo yum install -y bat
            elif command -v dnf >/dev/null 2>&1; then
                log_info "Installing via dnf..."
                sudo dnf install -y bat
            elif command -v pacman >/dev/null 2>&1; then
                log_info "Installing via pacman..."
                sudo pacman -S bat
            else
                log_error "No supported package manager found"
                log_info "Please install bat manually: https://github.com/sharkdp/bat"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported operating system: $(uname -s)"
            return 1
            ;;
    esac
}

verify_installation() {
    if command -v bat >/dev/null 2>&1; then
        local version=$(bat --version)
        log_success "bat installed successfully: $version"
        return 0
    else
        log_error "bat installation failed - command not found"
        return 1
    fi
}

create_ucode_integration() {
    log_info "Creating uDOS integration..."
    
    # Create simple usage examples
    cat > "/tmp/bat_examples.md" << 'EOF'
# bat Usage Examples

## Basic usage
bat filename.txt

## Show line numbers
bat -n filename.txt

## Show git changes
bat --diff filename.txt

## View multiple files
bat file1.txt file2.txt

## Pipe content
echo "Hello World" | bat -l python
EOF

    log_info "Created usage examples in /tmp/bat_examples.md"
    log_info "View with: bat /tmp/bat_examples.md"
}

main() {
    show_header
    
    if install_bat && verify_installation; then
        create_ucode_integration
        echo
        log_success "🎉 bat installation completed!"
        echo
        echo -e "${BLUE}Usage Examples:${NC}"
        echo -e "  ${YELLOW}bat README.md${NC}           # View file with syntax highlighting"
        echo -e "  ${YELLOW}bat -n script.sh${NC}        # Show with line numbers"
        echo -e "  ${YELLOW}echo 'code' | bat -l py${NC} # Pipe with language detection"
        echo
    else
        log_error "Installation failed"
        exit 1
    fi
}

main "$@"
