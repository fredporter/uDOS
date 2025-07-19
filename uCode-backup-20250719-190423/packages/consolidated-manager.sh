#!/bin/bash
# uDOS Consolidated Package Manager v2.0.0
# Replaces manager.sh, manager-simple.sh, manager-enhanced.sh, manager-compatible.sh

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

# Package definitions - bash 3.2 compatible
PACKAGE_ripgrep="Fast text search with rg command"
PACKAGE_bat="Syntax-highlighted file viewer"
PACKAGE_fd="Fast file finder alternative to find"
PACKAGE_glow="Terminal markdown renderer"
PACKAGE_jq="JSON processor and query tool"
PACKAGE_fzf="Fuzzy finder for interactive selection"
PACKAGE_gemini="Google Gemini CLI companion for AI assistance"

# Get package list
get_packages() {
    echo "ripgrep bat fd glow jq fzf gemini"
}

# Get package description
get_package_description() {
    local package="$1"
    case "$package" in
        "ripgrep") echo "$PACKAGE_ripgrep" ;;
        "bat") echo "$PACKAGE_bat" ;;
        "fd") echo "$PACKAGE_fd" ;;
        "glow") echo "$PACKAGE_glow" ;;
        "jq") echo "$PACKAGE_jq" ;;
        "fzf") echo "$PACKAGE_fzf" ;;
        "gemini") echo "$PACKAGE_gemini" ;;
        *) echo "Unknown package" ;;
    esac
}

# Check if package is installed
is_installed() {
    local package="$1"
    case "$package" in
        "ripgrep") command -v rg >/dev/null 2>&1 ;;
        "gemini") command -v gemini >/dev/null 2>&1 ;;
        *) command -v "$package" >/dev/null 2>&1 ;;
    esac
}

# Get package status
get_status() {
    local package="$1"
    if is_installed "$package"; then
        green "✅ Installed"
    else
        yellow "⏳ Available"
    fi
}

# List all packages
list_packages() {
    local format="${1:-table}"
    
    blue "📦 uDOS Package Manager v2.0.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    local packages=$(get_packages)
    
    case "$format" in
        "table")
            printf "%-12s %-12s %s\n" "Package" "Status" "Description"
            echo "────────────────────────────────────────────────────────────────"
            for package in $packages; do
                local status_text
                if is_installed "$package"; then
                    status_text="Installed"
                else
                    status_text="Available"
                fi
                printf "%-12s %-12s %s\n" "$package" "$status_text" "$(get_package_description "$package")"
            done
            ;;
        "simple")
            for package in $packages; do
                echo "$package $(get_status "$package") - $(get_package_description "$package")"
            done
            ;;
        "json")
            echo "{"
            local first=true
            for package in $packages; do
                if [[ "$first" == true ]]; then
                    first=false
                else
                    echo ","
                fi
                local installed=$(is_installed "$package" && echo "true" || echo "false")
                echo -n "  \"$package\": {\"installed\": $installed, \"description\": \"$(get_package_description "$package")\"}"
            done
            echo ""
            echo "}"
            ;;
    esac
    echo
}

# Install a specific package
install_package() {
    local package="$1"
    local force="${2:-false}"
    local packages=$(get_packages)
    
    if [[ -z "$package" ]]; then
        red "❌ Package name required"
        echo "Usage: install <package> [force]"
        return 1
    fi
    
    # Check if package is in our list
    local package_found=false
    for pkg in $packages; do
        if [[ "$pkg" == "$package" ]]; then
            package_found=true
            break
        fi
    done
    
    if [[ "$package_found" == false ]]; then
        red "❌ Unknown package: $package"
        echo "Available packages:"
        for pkg in $packages; do
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

# Install all packages
install_all_packages() {
    local force="${1:-false}"
    local failed_packages=()
    local installed_count=0
    local packages=$(get_packages)
    local total_count=$(echo $packages | wc -w)
    
    blue "🚀 Installing all packages..."
    echo "Total packages: $total_count"
    echo
    
    for package in $packages; do
        echo "────────────────────────────────────────────────────"
        blue "Installing $package ($((++installed_count))/$total_count)..."
        
        if install_package "$package" "$force"; then
            green "✅ $package completed"
        else
            red "❌ $package failed"
            failed_packages+=("$package")
        fi
        echo
    done
    
    echo "════════════════════════════════════════════════════"
    blue "Installation Summary:"
    echo "  Total packages: $total_count"
    green "  Successful: $((total_count - ${#failed_packages[@]}))"
    
    if [[ ${#failed_packages[@]} -gt 0 ]]; then
        red "  Failed: ${#failed_packages[@]}"
        echo "  Failed packages: ${failed_packages[*]}"
    else
        green "  All packages installed successfully! 🎉"
    fi
}

# Update package installers
update_installers() {
    blue "🔄 Checking package installer updates..."
    
    local installers_updated=0
    
    for package in "${!PACKAGES[@]}"; do
        local installer="${SCRIPT_DIR}/install-${package}.sh"
        if [[ -f "$installer" ]]; then
            echo "  ✓ $package installer found"
        else
            yellow "  ⚠️ $package installer missing"
        fi
    done
    
    if [[ "$installers_updated" -eq 0 ]]; then
        green "✅ All installers are up to date"
    else
        green "✅ Updated $installers_updated installers"
    fi
}

# Remove a package (where possible)
remove_package() {
    local package="$1"
    local packages=$(get_packages)
    
    if [[ -z "$package" ]]; then
        red "❌ Package name required"
        echo "Usage: remove <package>"
        return 1
    fi
    
    # Check if package is in our list
    local package_found=false
    for pkg in $packages; do
        if [[ "$pkg" == "$package" ]]; then
            package_found=true
            break
        fi
    done
    
    if [[ "$package_found" == false ]]; then
        red "❌ Unknown package: $package"
        return 1
    fi
    
    if ! is_installed "$package"; then
        yellow "⚠️ $package is not installed"
        return 0
    fi
    
    blue "🗑️ Attempting to remove $package..."
    
    # Try different removal methods based on installation method
    local removed=false
    
    # Try Homebrew
    if command -v brew >/dev/null 2>&1; then
        if brew list "$package" >/dev/null 2>&1; then
            brew uninstall "$package" && removed=true
        fi
    fi
    
    # Try package managers
    if [[ "$removed" == false ]]; then
        if command -v apt >/dev/null 2>&1; then
            sudo apt remove "$package" -y && removed=true
        elif command -v yum >/dev/null 2>&1; then
            sudo yum remove "$package" -y && removed=true
        elif command -v pacman >/dev/null 2>&1; then
            sudo pacman -R "$package" --noconfirm && removed=true
        fi
    fi
    
    if [[ "$removed" == true ]]; then
        green "✅ $package removed successfully"
    else
        yellow "⚠️ Could not automatically remove $package (manual removal may be required)"
    fi
}

# Show package info
show_package_info() {
    local package="$1"
    local packages=$(get_packages)
    
    if [[ -z "$package" ]]; then
        red "❌ Package name required"
        echo "Usage: info <package>"
        return 1
    fi
    
    # Check if package is in our list
    local package_found=false
    for pkg in $packages; do
        if [[ "$pkg" == "$package" ]]; then
            package_found=true
            break
        fi
    done
    
    if [[ "$package_found" == false ]]; then
        red "❌ Unknown package: $package"
        return 1
    fi
    
    blue "📋 Package Information: $package"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Description: $(get_package_description "$package")"
    echo "Status: $(get_status "$package")"
    
    if is_installed "$package"; then
        echo "Installation: System-wide"
        
        # Try to get version info
        case "$package" in
            "ripgrep")
                if command -v rg >/dev/null 2>&1; then
                    echo "Version: $(rg --version | head -n1)"
                    echo "Location: $(command -v rg)"
                fi
                ;;
            "bat")
                if command -v bat >/dev/null 2>&1; then
                    echo "Version: $(bat --version)"
                    echo "Location: $(command -v bat)"
                fi
                ;;
            "jq")
                if command -v jq >/dev/null 2>&1; then
                    echo "Version: $(jq --version)"
                    echo "Location: $(command -v jq)"
                fi
                ;;
            *)
                if command -v "$package" >/dev/null 2>&1; then
                    echo "Location: $(command -v "$package")"
                fi
                ;;
        esac
    else
        echo "Installation: Not installed"
        echo "Installer: ${SCRIPT_DIR}/install-${package}.sh"
    fi
    echo
}

# Handle shortcode commands
handle_shortcode_command() {
    local cmd="${1:-help}"
    shift || true
    
    case "$cmd" in
        "list"|"ls")
            list_packages "${1:-table}"
            ;;
        "install")
            if [[ $# -eq 0 ]]; then
                red "❌ Package name required"
                echo "Usage: [PACKAGE:install package_name]"
                return 1
            fi
            install_package "$1" "${2:-false}"
            ;;
        "install-all")
            install_all_packages "${1:-false}"
            ;;
        "status")
            if [[ $# -eq 0 ]]; then
                list_packages "simple"
            else
                show_package_info "$1"
            fi
            ;;
        "info")
            if [[ $# -eq 0 ]]; then
                red "❌ Package name required"
                echo "Usage: [PACKAGE:info package_name]"
                return 1
            fi
            show_package_info "$1"
            ;;
        "search")
            # Simple search by description
            local query="${1:-}"
            if [[ -z "$query" ]]; then
                red "❌ Search term required"
                echo "Usage: [PACKAGE:search search_term]"
                return 1
            fi
            
            echo "🔍 Searching packages for: $query"
            echo "═══════════════════════════════════════"
            local found=false
            for package in $(get_packages); do
                local desc=$(get_package_description "$package")
                if [[ "$desc" =~ $query ]] || [[ "$package" =~ $query ]]; then
                    printf "%-12s %s\n" "$package" "$desc"
                    found=true
                fi
            done
            if [[ "$found" == false ]]; then
                echo "No packages found matching: $query"
            fi
            ;;
        "help"|"")
            echo "📦 Package Shortcode Commands"
            echo "═══════════════════════════════════════"
            echo
            echo "Available shortcode commands:"
            echo "  [PACKAGE:list]              - List all packages"
            echo "  [PACKAGE:install package]   - Install specific package"
            echo "  [PACKAGE:install-all]       - Install all packages"
            echo "  [PACKAGE:status]            - Show installation status"
            echo "  [PACKAGE:status package]    - Show specific package status"
            echo "  [PACKAGE:info package]      - Show detailed package info"
            echo "  [PACKAGE:search term]       - Search packages"
            echo "  [PACKAGE:help]              - Show this help"
            echo
            echo "Shorthand alternatives:"
            echo "  [PKG:list]                  - Same as PACKAGE:list"
            echo "  [PKG:install-all]           - Same as PACKAGE:install-all"
            echo
            echo "Examples:"
            echo "  [PACKAGE:install ripgrep]   - Install ripgrep"
            echo "  [PKG:install-all]           - Install all packages"
            echo "  [PACKAGE:search markdown]   - Find markdown-related tools"
            ;;
        *)
            red "❌ Unknown shortcode command: $cmd"
            echo "Use [PACKAGE:help] for available commands"
            return 1
            ;;
    esac
}

# Main function
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "list"|"ls")
            list_packages "${1:-table}"
            ;;
        "install")
            if [[ $# -eq 0 ]]; then
                red "❌ Package name required"
                echo "Usage: $0 install <package> [force]"
                exit 1
            fi
            install_package "$1" "${2:-false}"
            ;;
        "install-all")
            install_all_packages "${1:-false}"
            ;;
        "remove"|"uninstall")
            if [[ $# -eq 0 ]]; then
                red "❌ Package name required"
                echo "Usage: $0 remove <package>"
                exit 1
            fi
            remove_package "$1"
            ;;
        "info")
            if [[ $# -eq 0 ]]; then
                red "❌ Package name required"
                echo "Usage: $0 info <package>"
                exit 1
            fi
            show_package_info "$1"
            ;;
        "update")
            update_installers
            ;;
        "status")
            list_packages "simple"
            ;;
        "shortcode")
            # Handle shortcode commands
            handle_shortcode_command "$@"
            ;;
        "help"|"--help"|"-h")
            echo
            bold "📦 uDOS Consolidated Package Manager v2.0.0"
            echo "═══════════════════════════════════════════════════"
            echo
            echo "Manages essential development tools for uDOS environment"
            echo
            echo "Commands:"
            echo "  list [format]      - List all packages (table/simple/json)"
            echo "  install <package>  - Install specific package"
            echo "  install-all        - Install all available packages"
            echo "  remove <package>   - Remove specific package"
            echo "  info <package>     - Show detailed package information"
            echo "  update             - Update package installers"
            echo "  status             - Show simple package status"
            echo "  help               - Show this help"
            echo
            echo "Available packages:"
            for package in $(get_packages); do
                echo "  $package - $(get_package_description "$package")"
            done
            echo
            echo "Examples:"
            echo "  $0 list"
            echo "  $0 install ripgrep"
            echo "  $0 install-all"
            echo "  $0 info bat"
            echo "  $0 remove fzf"
            echo
            ;;
        *)
            red "❌ Unknown command: $command"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
