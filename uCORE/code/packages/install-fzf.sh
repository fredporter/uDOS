#!/bin/bash
# uDOS Package Installer: fzf (fuzzy finder)
# Command-line fuzzy finder for interactive selection

set -euo pipefail

PACKAGE_NAME="fzf"
PACKAGE_DESC="Command-line fuzzy finder"
UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Simple logging"
log_info() { echo "ℹ️  $*"; }; log_success() { echo "✅ $*"; }; log_warn() { echo "⚠️  $*"; }; log_error() { echo "❌ $*"; }"

# Package information
GITHUB_REPO="junegunn/fzf"
HOMEBREW_FORMULA="fzf"
APT_PACKAGE="fzf"

log_info "Installing ${PACKAGE_NAME}: ${PACKAGE_DESC}"

# Detect platform and install
case "$(uname -s)" in
    Darwin*)
        log_info "Detected macOS - using Homebrew"
        if command -v brew >/dev/null 2>&1; then
            if ! brew list fzf >/dev/null 2>&1; then
                log_info "Installing fzf via Homebrew..."
                brew install fzf
                # Install shell integrations
                $(brew --prefix)/opt/fzf/install --key-bindings --completion --no-update-rc
            else
                log_info "fzf already installed via Homebrew"
            fi
        else
            log_warn "Homebrew not found - using git installation"
            if [[ ! -d ~/.fzf ]]; then
                log_info "Cloning fzf repository..."
                git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
                ~/.fzf/install --key-bindings --completion --no-update-rc
            else
                log_info "fzf already installed via git"
            fi
        fi
        ;;
    Linux*)
        log_info "Detected Linux - using package manager"
        if command -v apt-get >/dev/null 2>&1; then
            log_info "Installing fzf via apt..."
            sudo apt-get update && sudo apt-get install -y fzf
        elif command -v yum >/dev/null 2>&1; then
            log_info "Installing fzf via yum..."
            sudo yum install -y fzf
        elif command -v dnf >/dev/null 2>&1; then
            log_info "Installing fzf via dnf..."
            sudo dnf install -y fzf
        else
            log_warn "No supported package manager found - using git"
            if [[ ! -d ~/.fzf ]]; then
                log_info "Cloning fzf repository..."
                git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
                ~/.fzf/install --key-bindings --completion --no-update-rc
            else
                log_info "fzf already installed via git"
            fi
        fi
        ;;
    *)
        log_error "Unsupported platform: $(uname -s)"
        exit 1
        ;;
esac

# Verify installation
if command -v fzf >/dev/null 2>&1; then
    FZF_VERSION=$(fzf --version | cut -d' ' -f1)
    log_success "Successfully installed: fzf ${FZF_VERSION}"
    
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
           --arg version "fzf ${FZF_VERSION}" \
           --arg installed "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           '.[$name] = {description: $desc, version: $version, installed: $installed, status: "active"}' \
           "$PACKAGE_FILE" > "$PACKAGE_FILE.tmp" && mv "$PACKAGE_FILE.tmp" "$PACKAGE_FILE"
    else
        log_info "Package registry updated (jq not available for JSON formatting)"
    fi
    
    # Create usage examples
    cat > "${UDOS_ROOT}/package/utils/fzf.md" << 'EOF'
# fzf - Fuzzy Finder

## Overview
`fzf` is a general-purpose command-line fuzzy finder for interactive selection.

## Usage Examples

```bash
# Find files interactively
find . -type f | fzf

# Find and edit file
vim $(find . -name "*.md" | fzf)

# Search command history
history | fzf

# Interactive directory navigation
cd $(find . -type d | fzf)

# Multi-select with tab
find . -name "*.txt" | fzf -m

# Preview files
find . -name "*.md" | fzf --preview 'cat {}'

# Custom prompt
ls | fzf --prompt="Select file: "
```

## Key Bindings

- `Ctrl+C` or `Esc` - Exit
- `Enter` - Select
- `Tab` - Multi-select toggle
- `Ctrl+A` - Select all
- `Ctrl+D` - Deselect all
- `Ctrl+U` - Clear query

## uDOS Integration

uCode shell workflows:
- Interactive file selection
- Mission and milestone browsing
- Template selection
- Dataset exploration
- Log file navigation

## uDOS Specific Usage

```bash
# Interactive mission selection
fd "mission-*.md" uMemory/missions | fzf --preview 'glow {}'

# Select template interactively
fd "*.md" uTemplate/system | fzf --preview 'head -20 {}'

# Browse datasets
fd "*.json" uMapping/datasets | fzf --preview 'jq . {} | head -20'

# Interactive log viewing
fd "*.log" uMemory/logs | fzf --preview 'tail -20 {}'

# Choose package to install
echo -e "bat\nfd\nglow\njq\nfzf" | fzf --prompt="Install package: "
```

## Advanced Options

```bash
# Exact match
fzf -e

# Case sensitive
fzf +i

# Reverse order
fzf --reverse

# Custom preview window
fzf --preview 'cat {}' --preview-window right:50%

# Height control
fzf --height 40%

# Border
fzf --border

# Header
fzf --header "Select a file:"
```

## Shell Integration

Add to your shell config for experience:

```bash
# Bash/Zsh key bindings
export FZF_DEFAULT_OPTS="--height 40% --layout=reverse --border"

# Use fd with fzf
export FZF_DEFAULT_COMMAND='fd --type f'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

# Use fzf for directory navigation
export FZF_ALT_C_COMMAND='fd --type d'
```
EOF

    log_success "Package documentation created: package/utils/fzf.md"
    log_success "fzf installation complete and ready for use!"
    
else
    log_error "Installation failed - fzf command not found"
    exit 1
fi
