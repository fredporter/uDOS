#!/bin/bash
# uDOS Package Installer: fd (fast file finder)
# Modern replacement for 'find' with intuitive syntax

set -euo pipefail

PACKAGE_NAME="fd"
PACKAGE_DESC="Fast file finder (modern find replacement)"
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Simple logging"
log_info() { echo "ℹ️  $*"; }; log_success() { echo "✅ $*"; }; log_warn() { echo "⚠️  $*"; }; log_error() { echo "❌ $*"; }"

# Package information
GITHUB_REPO="sharkdp/fd"
HOMEBREW_FORMULA="fd"
APT_PACKAGE="fd-find"

log_info "Installing ${PACKAGE_NAME}: ${PACKAGE_DESC}"

# Detect platform and install
case "$(uname -s)" in
    Darwin*)
        log_info "Detected macOS - using Homebrew"
        if command -v brew >/dev/null 2>&1; then
            if ! brew list fd >/dev/null 2>&1; then
                log_info "Installing fd via Homebrew..."
                brew install fd
            else
                log_info "fd already installed via Homebrew"
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
            log_info "Installing fd via apt..."
            sudo apt-get update && sudo apt-get install -y fd-find
            # Create symlink if needed (Ubuntu uses 'fdfind')
            if command -v fdfind >/dev/null 2>&1 && ! command -v fd >/dev/null 2>&1; then
                sudo ln -sf /usr/bin/fdfind /usr/local/bin/fd
            fi
        elif command -v yum >/dev/null 2>&1; then
            log_info "Installing fd via yum..."
            sudo yum install -y fd-find
        elif command -v dnf >/dev/null 2>&1; then
            log_info "Installing fd via dnf..."
            sudo dnf install -y fd-find
        else
            log_warn "No supported package manager found"
            echo "Please install fd manually from: https://github.com/${GITHUB_REPO}"
            exit 1
        fi
        ;;
    *)
        log_error "Unsupported platform: $(uname -s)"
        exit 1
        ;;
esac

# Verify installation
if command -v fd >/dev/null 2>&1; then
    FD_VERSION=$(fd --version | head -n1)
    log_success "Successfully installed: ${FD_VERSION}"
    
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
           --arg version "$FD_VERSION" \
           --arg installed "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.[$name] = {description: $desc, version: $version, installed: $installed, status: "active"}' \
           "$PACKAGE_FILE" > "$PACKAGE_FILE.tmp" && mv "$PACKAGE_FILE.tmp" "$PACKAGE_FILE"
    else
        log_info "Package registry updated (jq not available for JSON formatting)"
    fi
    
    # Create usage examples
    cat > "${UDOS_ROOT}/package/utils/fd.md" << 'EOF'
# fd - Fast File Finder

## Overview
`fd` is a fast and user-friendly alternative to `find` with intuitive syntax.

## Usage Examples

```bash
# Find files by name
fd filename

# Find with pattern
fd "*.py"

# Search in specific directory
fd config /etc

# Exclude directories
fd --exclude node_modules "*.js"

# Show hidden files
fd -H config

# Execute command on results
fd "*.txt" -x wc -l

# Find directories only
fd -t d config

# Find files only
fd -t f "*.md"
```

## uDOS Integration

Available in uCode shell:
- `fd <pattern>` - Fast file search
- Integrated with template system for file discovery
- Used in dashboard for system file monitoring
- Enhanced with ripgrep for content + filename search

## Advanced Features

```bash
# Case insensitive
fd -i CONFIG

# Full path search
fd -p src/main

# Limit depth
fd -d 3 "*.py"

# Show absolute paths
fd -a config

# Parallel execution
fd "*.log" -x grep -l "ERROR" {}
```
EOF

    log_success "Package documentation created: package/utils/fd.md"
    log_success "fd installation complete and ready for use!"
    
else
    log_error "Installation failed - fd command not found"
    exit 1
fi
