#!/bin/bash
#!/bin/bash
# uDOS Consolidated Package Manager v1.3.1
# Enhanced package management with dependency resolution and caching
# Focused on core integrated packages + external package guides

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(dirname "$SCRIPT_DIR")"
UHOME="${HOME}/uDOS"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Core integrated package definitions
PACKAGE_jq="JSON processor and query tool"
PACKAGE_urltomarkdown="Web content extraction to Markdown format"

# External packages (install manually - see EXTERNAL_PACKAGES.md)
EXTERNAL_ripgrep="Fast text search with rg command"
EXTERNAL_bat="Syntax-highlighted file viewer"
EXTERNAL_fd="Fast file finder alternative to find"
EXTERNAL_glow="Terminal markdown renderer"
EXTERNAL_fzf="Fuzzy finder for interactive selection"
EXTERNAL_gemini="Google Gemini CLI companion for AI assistance"

# Get core package list (integrated packages only)
get_packages() {
    echo "jq urltomarkdown"
}

# Get external package list
get_external_packages() {
    echo "ripgrep bat fd glow fzf gemini"
}

# Get package description
get_package_description() {
    local package="$1"
    case "$package" in
        "jq") echo "$PACKAGE_jq" ;;
        "urltomarkdown") echo "$PACKAGE_urltomarkdown" ;;
        "ripgrep") echo "$EXTERNAL_ripgrep" ;;
        "bat") echo "$EXTERNAL_bat" ;;
        "fd") echo "$EXTERNAL_fd" ;;
        "glow") echo "$EXTERNAL_glow" ;;
        "fzf") echo "$EXTERNAL_fzf" ;;
        "gemini") echo "$EXTERNAL_gemini" ;;
        *) echo "Unknown package" ;;
    esac
}

# Check if package is installed
is_installed() {
    local package="$1"
    case "$package" in
        "jq") command -v jq >/dev/null 2>&1 ;;
        "urltomarkdown") [[ -f "$SCRIPT_DIR/urltomarkdown/urltomarkdown.py" ]] ;;
        "ripgrep") command -v rg >/dev/null 2>&1 ;;
        "bat") command -v bat >/dev/null 2>&1 ;;
        "fd") command -v fd >/dev/null 2>&1 || command -v fdfind >/dev/null 2>&1 ;;
        "glow") command -v glow >/dev/null 2>&1 ;;
        "fzf") command -v fzf >/dev/null 2>&1 ;;
        "gemini") command -v gemini >/dev/null 2>&1 ;;
        *) return 1 ;;
    esac
}

# Check if package is external (manual install)
is_external() {
    local package="$1"
    case "$package" in
        "ripgrep"|"bat"|"fd"|"glow"|"fzf"|"gemini") return 0 ;;
        *) return 1 ;;
    esac
}

show_header() {
    blue "📦 uDOS Package Manager v1.3.1"
    blue "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
}

show_help() {
    cat << EOF
Usage: $0 COMMAND [PACKAGE]

Commands:
  status [PACKAGE]     Show package installation status
  install PACKAGE      Install core integrated package
  list                 List all packages
  external             Show external package installation guide
  help                 Show this help

Core Packages (Integrated):
  jq                   JSON processor and query tool
  urltomarkdown        Web content extraction to Markdown format

External Packages (Manual Install):
  ripgrep              Fast text search with rg command
  bat                  Syntax-highlighted file viewer
  fd                   Fast file finder alternative to find
  glow                 Terminal markdown renderer
  fzf                  Fuzzy finder for interactive selection
  gemini               Google Gemini CLI companion

Examples:
  $0 status            # Show all package status
  $0 install urltomarkdown
  $0 external          # Show external installation guide
EOF
}

show_status() {
    local specific_package="$1"

    show_header

    if [[ -n "$specific_package" ]]; then
        show_package_status "$specific_package"
        return
    fi

    # Show core packages
    echo -e "$(blue "🏠 CORE PACKAGES (Integrated):")"
    for package in $(get_packages); do
        show_package_status "$package"
    done

    echo
    echo -e "$(yellow "🌍 EXTERNAL PACKAGES (Manual Install):")"
    for package in $(get_external_packages); do
        show_package_status "$package"
    done

    echo
    echo -e "$(blue "💡 Run './consolidated-manager.sh external' for installation guide")"
}

show_package_status() {
    local package="$1"
    local description=$(get_package_description "$package")

    if is_installed "$package"; then
        printf "%-15s %s %s\n" "$package" "$(green "✅ Installed")" "- $description"
    elif is_external "$package"; then
        printf "%-15s %s %s\n" "$package" "$(yellow "📦 External")" "- $description"
    else
        printf "%-15s %s %s\n" "$package" "$(blue "⏳ Available")" "- $description"
    fi
}

show_external_guide() {
    if [[ -f "$SCRIPT_DIR/EXTERNAL_PACKAGES.md" ]]; then
        echo -e "$(blue "📋 External Package Installation Guide:")"
        echo
        if command -v bat >/dev/null 2>&1; then
            bat "$SCRIPT_DIR/EXTERNAL_PACKAGES.md"
        elif command -v glow >/dev/null 2>&1; then
            glow "$SCRIPT_DIR/EXTERNAL_PACKAGES.md"
        else
            cat "$SCRIPT_DIR/EXTERNAL_PACKAGES.md"
        fi
    else
        echo -e "$(red "❌ EXTERNAL_PACKAGES.md not found")"
        echo "Run package-cleanup.sh to generate the guide"
    fi
}

install_package() {
    local package="$1"
    local force="$2"

    if is_external "$package"; then
        red "❌ $package is an external package"
        echo "Install manually using your system package manager"
        echo "Run './consolidated-manager.sh external' for instructions"
        return 1
    fi

    if ! echo "$(get_packages)" | grep -q "$package"; then
        red "❌ Unknown package: $package"
        echo "Available core packages:"
        for pkg in $(get_packages); do
            echo "  - $pkg"
        done
        return 1
    fi

    local installer="${SCRIPT_DIR}/install-${package}.sh"

    if [[ ! -f "$installer" ]]; then
        red "❌ Installer not found: $installer"
        return 1
    fi

    if is_installed "$package" && [[ "$force" != "true" ]]; then
        yellow "⚠️ $package is already installed (use 'force' to reinstall)"
        return 0
    fi

    blue "📦 Installing $package..."
    echo "Description: $(get_package_description "$package")"
    echo

    if bash "$installer"; then
        green "✅ $package installed successfully"
        return 0
    else
        red "❌ Failed to install $package"
        return 1
    fi
}

main() {
    local command="${1:-help}"
    local package="${2:-}"
    local force="${3:-false}"

    case "$command" in
        "status"|"s")
            show_status "$package"
            ;;
        "install"|"i")
            if [[ -z "$package" ]]; then
                red "❌ Package name required"
                echo "Usage: $0 install PACKAGE"
                return 1
            fi
            install_package "$package" "$force"
            ;;
        "list"|"l")
            echo "Core packages: $(get_packages)"
            echo "External packages: $(get_external_packages)"
            ;;
        "external"|"ext")
            show_external_guide
            ;;
        "help"|"h"|"-h"|"--help")
            show_help
            ;;
        *)
            red "❌ Unknown command: $command"
            echo
            show_help
            return 1
            ;;
    esac
}

main "$@"
