#!/bin/bash
# uDOS Package Installer: bat (syntax-highlighted file viewer)
# Enhanced 'cat' with syntax highlighting and Git integration

PACKAGE_NAME="bat"
PACKAGE_DESC="Syntax-highlighted file viewer (enhanced cat)"
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Simple logging functions
log_info() { echo "ℹ️  $*"; }
log_success() { echo "✅ $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*"; }

# Package information
GITHUB_REPO="sharkdp/bat"
HOMEBREW_FORMULA="bat"
APT_PACKAGE="bat"

log_info "Installing ${PACKAGE_NAME}: ${PACKAGE_DESC}"

# Detect platform and install
case "$(uname -s)" in
    Darwin*)
        log_info "Detected macOS - using Homebrew"
        if command -v brew >/dev/null 2>&1; then
            if ! brew list bat >/dev/null 2>&1; then
                log_info "Installing bat via Homebrew..."
                brew install bat
            else
                log_info "bat already installed via Homebrew"
            fi
        else
            log_warn "Homebrew not found - manual installation required"
            echo "Please install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        ;;
    Linux*)
        log_info "Detected Linux - using package manager"
        if command -v apt-get >/dev/null 2>&1; then
            log_info "Installing bat via apt..."
            sudo apt-get update && sudo apt-get install -y bat
            # Create symlink if needed (Ubuntu uses 'batcat')
            if command -v batcat >/dev/null 2>&1 && ! command -v bat >/dev/null 2>&1; then
                sudo ln -sf /usr/bin/batcat /usr/local/bin/bat
            fi
        elif command -v yum >/dev/null 2>&1; then
            log_info "Installing bat via yum..."
            sudo yum install -y bat
        elif command -v dnf >/dev/null 2>&1; then
            log_info "Installing bat via dnf..."
            sudo dnf install -y bat
        else
            log_warn "No supported package manager found"
            echo "Please install bat manually from: https://github.com/${GITHUB_REPO}"
            exit 1
        fi
        ;;
    *)
        log_error "Unsupported platform: $(uname -s)"
        exit 1
        ;;
esac

# Verify installation
if command -v bat >/dev/null 2>&1; then
    BAT_VERSION=$(bat --version | head -n1)
    log_success "Successfully installed: ${BAT_VERSION}"
    
    # Update package registry
    PACKAGE_FILE="${UDOS_ROOT}/uMemory/state/packages.json"
    mkdir -p "$(dirname "$PACKAGE_FILE")"
    
    # Create or update package registry
    if [[ ! -f "$PACKAGE_FILE" ]]; then
        echo '{}' > "$PACKAGE_FILE"
    fi
    
    # Add package info using jq if available, otherwise simple append
    if command -v jq >/dev/null 2>&1; then
        jq --arg name "$PACKAGE_NAME" \
           --arg desc "$PACKAGE_DESC" \
           --arg version "$BAT_VERSION" \
           --arg installed "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.[$name] = {description: $desc, version: $version, installed: $installed, status: "active"}' \
           "$PACKAGE_FILE" > "$PACKAGE_FILE.tmp" && mv "$PACKAGE_FILE.tmp" "$PACKAGE_FILE"
    else
        log_info "Package registry updated (jq not available for JSON formatting)"
    fi
    
    # Create usage examples
    cat > "${UDOS_ROOT}/package/utils/bat.md" << 'EOF'
# bat - Syntax-highlighted File Viewer

## Overview
`bat` is a `cat` clone with syntax highlighting and Git integration.

## Usage Examples

```bash
# View file with syntax highlighting
bat file.py

# Show line numbers
bat -n file.js

# Show Git diff
bat --diff file.md

# Page through large files
bat --paging=always large-file.log

# Highlight specific lines
bat -H 10:20 file.txt
```

## uDOS Integration

Available in uCode shell:
- `bat <file>` - Enhanced file viewing
- Integrated with uScript for code display
- Used in dashboard for log file viewing

## Configuration

Create `~/.config/bat/config` for custom settings:
```
--theme="Dracula"
--style="numbers,changes,header"
--pager="less -FR"
```
EOF

    log_success "Package documentation created: package/utils/bat.md"
    log_success "bat installation complete and ready for use!"
    
else
    log_error "Installation failed - bat command not found"
    exit 1
fi
