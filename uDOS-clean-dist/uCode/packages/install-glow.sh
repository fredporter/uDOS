#!/bin/bash
# uDOS Package Installer: glow (terminal markdown renderer)
# Beautiful terminal markdown viewer

set -euo pipefail

PACKAGE_NAME="glow"
PACKAGE_DESC="Terminal markdown renderer"
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Simple logging"
log_info() { echo "ℹ️  $*"; }; log_success() { echo "✅ $*"; }; log_warn() { echo "⚠️  $*"; }; log_error() { echo "❌ $*"; }"

# Package information
GITHUB_REPO="charmbracelet/glow"
HOMEBREW_FORMULA="glow"

log_info "Installing ${PACKAGE_NAME}: ${PACKAGE_DESC}"

# Detect platform and install
case "$(uname -s)" in
    Darwin*)
        log_info "Detected macOS - using Homebrew"
        if command -v brew >/dev/null 2>&1; then
            if ! brew list glow >/dev/null 2>&1; then
                log_info "Installing glow via Homebrew..."
                brew install glow
            else
                log_info "glow already installed via Homebrew"
            fi
        else
            log_warn "Homebrew not found - manual installation required"
            echo "Please install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        ;;
    Linux*)
        log_info "Detected Linux - installing via script"
        if command -v curl >/dev/null 2>&1; then
            log_info "Installing glow via installation script..."
            curl -fsSL https://github.com/charmbracelet/glow/releases/latest/download/glow_linux_x86_64.tar.gz | sudo tar -xz -C /usr/local/bin glow
        elif command -v wget >/dev/null 2>&1; then
            log_info "Installing glow via wget..."
            wget -qO- https://github.com/charmbracelet/glow/releases/latest/download/glow_linux_x86_64.tar.gz | sudo tar -xz -C /usr/local/bin glow
        else
            log_warn "Neither curl nor wget found"
            echo "Please install glow manually from: https://github.com/${GITHUB_REPO}"
            exit 1
        fi
        ;;
    *)
        log_error "Unsupported platform: $(uname -s)"
        exit 1
        ;;
esac

# Verify installation
if command -v glow >/dev/null 2>&1; then
    GLOW_VERSION=$(glow --version | head -n1)
    log_success "Successfully installed: ${GLOW_VERSION}"
    
    # Update package registry
    PACKAGE_FILE="${UDOS_ROOT}/uMemory/state/packages.json"
    mkdir -p "$(dirname "$PACKAGE_FILE")"
    
    # Create or update package registry
    if [[ ! -f "$PACKAGE_FILE" ]]; then
        echo '{}' > "$PACKAGE_FILE"
    fi
    
    # Add package info using jq if available
    if command -v jq >/dev/null 2>&1; then
        jq --arg name "$PACKAGE_NAME" \
           --arg desc "$PACKAGE_DESC" \
           --arg version "$GLOW_VERSION" \
           --arg installed "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.[$name] = {description: $desc, version: $version, installed: $installed, status: "active"}' \
           "$PACKAGE_FILE" > "$PACKAGE_FILE.tmp" && mv "$PACKAGE_FILE.tmp" "$PACKAGE_FILE"
    else
        log_info "Package registry updated (jq not available for JSON formatting)"
    fi
    
    # Create usage examples
    cat > "${UDOS_ROOT}/uKnowledge/packages/glow.md" << 'EOF'
# glow - Terminal Markdown Renderer

## Overview
`glow` renders markdown files beautifully in the terminal with syntax highlighting.

## Usage Examples

```bash
# Render markdown file
glow README.md

# Render with specific style
glow -s dark README.md

# Render from URL
glow https://raw.githubusercontent.com/user/repo/main/README.md

# Page through content
glow -p README.md

# Word wrap
glow -w 100 README.md

# Print to stdout (no pager)
glow --print README.md
```

## uDOS Integration

Available in uCode shell:
- `glow <file>` - Beautiful markdown viewing
- Integrated with documentation system
- Used for viewing roadmap files
- Enhanced mission and milestone display

## Styles Available

- auto (default)
- dark
- light
- notty (for scripts)

## Configuration

Create `~/.config/glow/glow.yml`:
```yaml
style: "dark"
width: 120
mouse: true
pager: true
```

## uDOS Specific Usage

```bash
# View roadmap files
glow uKnowledge/roadmap/001-uDOS-foundation.md

# View mission templates
glow uTemplate/system/mission-template.md

# View dashboard markdown
glow uMemory/state/dashboard.md

# Pipe dashboard to glow
./uCode/enhanced-dash.sh build && glow uMemory/state/dashboard.md
```
EOF

    log_success "Package documentation created: uKnowledge/packages/glow.md"
    log_success "glow installation complete and ready for use!"
    
else
    log_error "Installation failed - glow command not found"
    exit 1
fi
