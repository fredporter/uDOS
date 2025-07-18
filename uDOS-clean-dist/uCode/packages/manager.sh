#!/bin/bash
# uDOS Package Manager - Unified package installation anlist_packages() {
    echo "📦 Available uDOS Packages:"
    echo
    for package in ripgrep bat fd glow jq fzf; do
        local info=$(get_package_info "$package")
        IFS='|' read -r script desc <<< "$info"
        if command -v "$package" >/dev/null 2>&1; then
            status="✅ Installed"
        else
            status="⏳ Available"
        fi
        printf "%-12s %s - %s\n" "$package" "$status" "$desc"
    done
    echo
}

show_installed() {
    echo "✅ Installed Packages:"
    echo
    if [[ -f "$PACKAGE_REGISTRY" ]] && command -v jq >/dev/null 2>&1; then
        jq -r 'to_entries[] | "\(.key) - \(.value.description) (\(.value.version))"' "$PACKAGE_REGISTRY"
    else
        for package in $(get_all_packages); do
            if command -v "$package" >/dev/null 2>&1; then
                local info=$(get_package_info "$package")
                IFS='|' read -r script desc <<< "$info"
                version=$(command "$package" --version 2>/dev/null | head -n1 || echo "unknown")
                echo "$package - $desc ($version)"
            fi
        done
    fi
    echo
}

install_package() {
    local package="$1"
    local info=$(get_package_info "$package")
    
    if [[ -z "$info" ]]; then
        log_error "Unknown package: $package"
        echo "Available packages: $(get_all_packages)"
        return 1
    fi
    
    IFS='|' read -r script desc <<< "$info"
    local installer="${PACKAGE_DIR}/${script}"
    
    if [[ ! -f "$installer" ]]; then
        log_error "Installer not found: $installer"
        return 1
    fi
    
    if command -v "$package" >/dev/null 2>&1; then
        log_info "Package $package is already installed"
        return 0
    fi
    
    log_info "Installing package: $package"
    log_info "Description: $desc"
    
    if bash "$installer"; then
        log_success "Successfully installed $package"
    else
        log_error "Failed to install $package"
        return 1
    fi
}

install_all_packages() {
    echo "🚀 Installing all uDOS packages..."
    echo
    
    local failed_packages=""
    local installed_count=0
    
    for package in $(get_all_packages); do
        echo "─────────────────────────────────────"
        if install_package "$package"; then
            installed_count=$((installed_count + 1))
        else
            failed_packages="$failed_packages $package"
        fi
    done
    
    echo "─────────────────────────────────────"
    echo "📊 Installation Summary:"
    echo "✅ Successfully installed: $installed_count packages"
    
    if [[ -n "$failed_packages" ]]; then
        echo "❌ Failed to install:$failed_packages"
        return 1
    else
        echo "🎉 All packages installed successfully!"
    fi
}

check_status() {
    local package="$1"
    local info=$(get_package_info "$package")
    
    if [[ -z "$info" ]]; then
        log_error "Unknown package: $package"
        return 1
    fi
    
    echo "📋 Package Status: $package"
    echo
    
    if command -v "$package" >/dev/null 2>&1; then
        echo "Status: ✅ Installed"
        version=$(command "$package" --version 2>/dev/null | head -n1 || echo "unknown")
        echo "Version: $version"
        echo "Path: $(command -v "$package")"
        
        if [[ -f "$PACKAGE_REGISTRY" ]] && command -v jq >/dev/null 2>&1; then
            echo "Registry Info:"
            jq -r --arg pkg "$package" '.[$pkg] // "Not found in registry"' "$PACKAGE_REGISTRY"
        fi
    else
        echo "Status: ⏳ Not installed"
        IFS='|' read -r script desc <<< "$info"
        echo "Description: $desc"
        echo "Installer: ${PACKAGE_DIR}/${script}"
    fi
    echo
}

show_docs() {
    local package="$1"
    local docs_file="${UDOS_ROOT}/uKnowledge/packages/${package}.md"
    
    if [[ -f "$docs_file" ]]; then
        if command -v glow >/dev/null 2>&1; then
            glow "$docs_file"
        else
            cat "$docs_file"
        fi
    else
        log_warn "Documentation not found for $package"
        echo "Expected location: $docs_file"
    fi
} Enhanced package system for uDOS alpha v1.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"

# Simple logging functions
log_info() { echo "ℹ️  $*"; }
log_success() { echo "✅ $*"; }
log_warn() { echo "⚠️  $*"; }
log_error() { echo "❌ $*"; }

PACKAGE_DIR="${SCRIPT_DIR}"
PACKAGE_REGISTRY="${UDOS_ROOT}/uMemory/state/packages.json"

# Available packages (compatible with older bash)
get_package_info() {
    case "$1" in
        ripgrep) echo "install-ripgrep.sh|Fast text search" ;;
        bat) echo "install-bat.sh|Syntax-highlighted file viewer" ;;
        fd) echo "install-fd.sh|Fast file finder" ;;
        glow) echo "install-glow.sh|Terminal markdown renderer" ;;
        jq) echo "install-jq.sh|JSON processor" ;;
        fzf) echo "install-fzf.sh|Fuzzy finder" ;;
        *) echo "" ;;
    esac
}

get_all_packages() {
    echo "ripgrep bat fd glow jq fzf"
}

show_help() {
    cat << 'EOF'
🌀 uDOS Package Manager v1.0

USAGE:
    ./uCode/packages/manager.sh <command> [options]

COMMANDS:
    list                    List all available packages
    installed               Show installed packages
    install <package>       Install specific package
    install-all            Install all packages
    status <package>        Check package status
    update <package>        Update specific package
    docs <package>          Show package documentation
    help                   Show this help

PACKAGES:
    ripgrep               Fast text search (rg)
    bat                   Syntax-highlighted file viewer
    fd                    Fast file finder
    glow                  Terminal markdown renderer
    jq                    JSON processor
    fzf                   Fuzzy finder

EXAMPLES:
    ./uCode/packages/manager.sh list
    ./uCode/packages/manager.sh install bat
    ./uCode/packages/manager.sh install-all
    ./uCode/packages/manager.sh status jq
    ./uCode/packages/manager.sh docs fzf

EOF
}

list_packages() {
    echo "📦 Available uDOS Packages:"
    echo
    for package in "${!PACKAGES[@]}"; do
        IFS='|' read -r script desc <<< "${PACKAGES[$package]}"
        if command -v "$package" >/dev/null 2>&1; then
            status="✅ Installed"
        else
            status="⏳ Available"
        fi
        printf "%-12s %s - %s\n" "$package" "$status" "$desc"
    done
    echo
}

show_installed() {
    echo "✅ Installed Packages:"
    echo
    if [[ -f "$PACKAGE_REGISTRY" ]] && command -v jq >/dev/null 2>&1; then
        jq -r 'to_entries[] | "\(.key) - \(.value.description) (\(.value.version))"' "$PACKAGE_REGISTRY"
    else
        for package in "${!PACKAGES[@]}"; do
            if command -v "$package" >/dev/null 2>&1; then
                IFS='|' read -r script desc <<< "${PACKAGES[$package]}"
                version=$(command "$package" --version 2>/dev/null | head -n1 || echo "unknown")
                echo "$package - $desc ($version)"
            fi
        done
    fi
    echo
}

install_package() {
    local package="$1"
    
    if [[ ! "${PACKAGES[$package]:-}" ]]; then
        log_error "Unknown package: $package"
        echo "Available packages: ${!PACKAGES[*]}"
        return 1
    fi
    
    IFS='|' read -r script desc <<< "${PACKAGES[$package]}"
    local installer="${PACKAGE_DIR}/${script}"
    
    if [[ ! -f "$installer" ]]; then
        log_error "Installer not found: $installer"
        return 1
    fi
    
    if command -v "$package" >/dev/null 2>&1; then
        log_info "Package $package is already installed"
        return 0
    fi
    
    log_info "Installing package: $package"
    log_info "Description: $desc"
    
    if bash "$installer"; then
        log_success "Successfully installed $package"
    else
        log_error "Failed to install $package"
        return 1
    fi
}

install_all_packages() {
    echo "🚀 Installing all uDOS packages..."
    echo
    
    local failed_packages=()
    local installed_count=0
    
    for package in "${!PACKAGES[@]}"; do
        echo "─────────────────────────────────────"
        if install_package "$package"; then
            ((installed_count++))
        else
            failed_packages+=("$package")
        fi
    done
    
    echo "─────────────────────────────────────"
    echo "� Installation Summary:"
    echo "✅ Successfully installed: $installed_count packages"
    
    if [[ ${#failed_packages[@]} -gt 0 ]]; then
        echo "❌ Failed to install: ${failed_packages[*]}"
        return 1
    else
        echo "🎉 All packages installed successfully!"
    fi
}

check_status() {
    local package="$1"
    
    if [[ ! "${PACKAGES[$package]:-}" ]]; then
        log_error "Unknown package: $package"
        return 1
    fi
    
    echo "📋 Package Status: $package"
    echo
    
    if command -v "$package" >/dev/null 2>&1; then
        echo "Status: ✅ Installed"
        version=$(command "$package" --version 2>/dev/null | head -n1 || echo "unknown")
        echo "Version: $version"
        echo "Path: $(command -v "$package")"
        
        if [[ -f "$PACKAGE_REGISTRY" ]] && command -v jq >/dev/null 2>&1; then
            echo "Registry Info:"
            jq -r --arg pkg "$package" '.[$pkg] // "Not found in registry"' "$PACKAGE_REGISTRY"
        fi
    else
        echo "Status: ⏳ Not installed"
        IFS='|' read -r script desc <<< "${PACKAGES[$package]}"
        echo "Description: $desc"
        echo "Installer: ${PACKAGE_DIR}/${script}"
    fi
    echo
}

show_docs() {
    local package="$1"
    local docs_file="${UDOS_ROOT}/uKnowledge/packages/${package}.md"
    
    if [[ -f "$docs_file" ]]; then
        if command -v glow >/dev/null 2>&1; then
            glow "$docs_file"
        else
            cat "$docs_file"
        fi
    else
        log_warn "Documentation not found for $package"
        echo "Expected location: $docs_file"
    fi
}

# Main command processing
case "${1:-help}" in
    list|ls)
        list_packages
        ;;
    installed|status-all)
        show_installed
        ;;
    install)
        if [[ $# -lt 2 ]]; then
            log_error "Package name required"
            echo "Usage: $0 install <package>"
            exit 1
        fi
        install_package "$2"
        ;;
    install-all)
        install_all_packages
        ;;
    status)
        if [[ $# -lt 2 ]]; then
            log_error "Package name required"
            echo "Usage: $0 status <package>"
            exit 1
        fi
        check_status "$2"
        ;;
    docs|doc)
        if [[ $# -lt 2 ]]; then
            log_error "Package name required"
            echo "Usage: $0 docs <package>"
            exit 1
        fi
        show_docs "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
    if [[ -f "$install_script" ]]; then
      echo "📦 Package Information: $package"
      echo ""
      # Extract description from script comments
      grep "^#.*" "$install_script" | head -5
      echo ""
      echo "📍 Install script: $install_script"
    else
      echo "❌ Package not found: $package"
    fi
    ;;
    
  remove)
    package="$2"
    echo "🗑️ Package removal not yet implemented for: $package"
    echo "💡 You can manually remove package files if needed"
    ;;
    
  update)
    echo "🔄 Package updates not yet implemented"
    echo "💡 Individual packages may have update mechanisms"
    ;;
    
  *)
    echo "📦 uDOS Package Manager"
    echo ""
    echo "Usage: PACKAGE <action> [package]"
    echo ""
    echo "Actions:"
    echo "   list              → List all available packages"
    echo "   info <package>    → Show package information"
    echo "   remove <package>  → Remove installed package"
    echo "   update            → Update all packages"
    echo ""
    ;;
esac
