#!/bin/bash
# Micro Editor Installation Script for uDOS
# Downloads and installs micro editor based on platform detection

set -euo pipefail

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
EXTENSION_DIR="$SCRIPT_DIR/.."
BIN_DIR="$EXTENSION_DIR/bin"

# Source logging functions
source "$UDOS_ROOT/uCORE/code/logging.sh" 2>/dev/null || {
    log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
    log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
    log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
}

# Platform detection
detect_platform() {
    local os_type
    os_type=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch_type
    arch_type=$(uname -m)

    case "$os_type" in
        darwin*)
            case "$arch_type" in
                x86_64) echo "osx" ;;
                arm64) echo "macos-arm64" ;;
                *) echo "osx" ;;  # fallback
            esac
            ;;
        linux*)
            case "$arch_type" in
                x86_64) echo "linux64" ;;
                aarch64|arm64) echo "linux-arm64" ;;
                armv7l) echo "linux-arm" ;;
                i386|i686) echo "linux32" ;;
                *) echo "linux64" ;;  # fallback
            esac
            ;;
        mingw*|msys*|cygwin*)
            case "$arch_type" in
                x86_64) echo "win64" ;;
                i386|i686) echo "win32" ;;
                *) echo "win64" ;;  # fallback
            esac
            ;;
        *)
            log_error "Unsupported platform: $os_type"
            exit 1
            ;;
    esac
}# Download and install micro
install_micro() {
    local platform
    platform=$(detect_platform)

    log_info "Installing micro editor for platform: $platform"

    # Create bin directory
    mkdir -p "$BIN_DIR"

    # Get latest release info
    local latest_url="https://api.github.com/repos/zyedidia/micro/releases/latest"
    local download_url

    # Try to get download URL from GitHub API
    if command -v curl >/dev/null 2>&1; then
        download_url=$(curl -s "$latest_url" | grep "browser_download_url.*$platform" | cut -d '"' -f 4 | head -1)
    elif command -v wget >/dev/null 2>&1; then
        download_url=$(wget -qO- "$latest_url" | grep "browser_download_url.*$platform" | cut -d '"' -f 4 | head -1)
    else
        log_error "Neither curl nor wget found. Cannot download micro."
        exit 1
    fi

    if [[ -z "$download_url" ]]; then
        log_error "Could not find download URL for platform: $platform"
        exit 1
    fi

    log_info "Downloading from: $download_url"

    # Download the archive
    local archive_name
    archive_name=$(basename "$download_url")
    local temp_dir="/tmp/micro-install-$$"
    mkdir -p "$temp_dir"

    if command -v curl >/dev/null 2>&1; then
        curl -L -o "$temp_dir/$archive_name" "$download_url"
    else
        wget -O "$temp_dir/$archive_name" "$download_url"
    fi

    # Extract based on file type
    cd "$temp_dir"
    if [[ "$archive_name" == *.tar.gz ]]; then
        tar -xzf "$archive_name"
    elif [[ "$archive_name" == *.zip ]]; then
        if command -v unzip >/dev/null 2>&1; then
            unzip -q "$archive_name"
        else
            log_error "unzip command not found. Cannot extract $archive_name"
            exit 1
        fi
    else
        log_error "Unknown archive format: $archive_name"
        exit 1
    fi

    # Find the micro binary and copy it
    local micro_binary
    micro_binary=$(find . -name "micro" -type f -executable | head -1)

    if [[ -z "$micro_binary" ]]; then
        log_error "Could not find micro binary in downloaded archive"
        exit 1
    fi

    # Copy to bin directory
    cp "$micro_binary" "$BIN_DIR/micro"
    chmod +x "$BIN_DIR/micro"

    # Clean up
    rm -rf "$temp_dir"

    log_success "Micro editor installed successfully to $BIN_DIR/micro"
}

# Verify installation
verify_installation() {
    if [[ -x "$BIN_DIR/micro" ]]; then
        local version
        version=$("$BIN_DIR/micro" --version 2>&1 | head -1)
        log_success "Micro editor verified: $version"
        return 0
    else
        log_error "Micro editor installation verification failed"
        return 1
    fi
}

# Create configuration
create_config() {
    local config_dir="$EXTENSION_DIR/config"
    mkdir -p "$config_dir"

    cat > "$config_dir/micro-settings.json" << 'EOF'
{
    "autoindent": true,
    "autosave": 2,
    "colorscheme": "default",
    "cursorline": true,
    "diffgutter": true,
    "ignorecase": false,
    "indentchar": " ",
    "keepautoindent": false,
    "keymenu": false,
    "mouse": true,
    "rmtrailingws": false,
    "ruler": true,
    "savecursor": false,
    "savehistory": true,
    "saveundo": false,
    "scrollbar": false,
    "scrollmargin": 3,
    "scrollspeed": 2,
    "softwrap": false,
    "splitbottom": true,
    "splitright": true,
    "statusformatl": "$(filename) $(modified)($(line),$(col)) $(status.paste)| ft:$(opt:filetype) | $(opt:fileformat) | $(opt:encoding)",
    "statusformatr": "$(bind:ToggleKeyMenu): bindings, $(bind:ToggleHelp): help",
    "statusline": true,
    "sucmd": "sudo",
    "syntax": true,
    "tabmovement": false,
    "tabsize": 4,
    "tabstospaces": false,
    "termtitle": false,
    "useprimary": true
}
EOF

    log_success "Created micro configuration at $config_dir/micro-settings.json"
}

# Main installation process
main() {
    log_info "Starting micro editor installation for uDOS"

    # Check if already installed
    if [[ -x "$BIN_DIR/micro" ]]; then
        log_warning "Micro editor already installed. Use --force to reinstall."
        if [[ "${1:-}" != "--force" ]]; then
            verify_installation
            exit 0
        fi
    fi

    install_micro
    verify_installation || exit 1
    create_config

    log_success "Micro editor installation complete!"
    log_info "Use [EDIT] <filename> to open files with micro editor"
}

# Run main function
main "$@"
