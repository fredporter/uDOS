#!/bin/bash
# package-manager.sh - uDOS v1.0 Package Management System
# Handles bundled application installation and uCode integration

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGE_DIR="${UDOS_ROOT}/package"
MANIFEST_FILE="${PACKAGE_DIR}/manifest.json"
INSTALL_QUEUE="${PACKAGE_DIR}/install-queue.txt"

# Package Management Functions

install_package() {
    local package_name="$1"
    echo "📦 Installing package: $package_name"
    
    # Check if package exists in manifest
    if ! jq -e ".packages | to_entries[] | select(.value | has(\"$package_name\"))" "$MANIFEST_FILE" >/dev/null 2>&1; then
        echo "❌ Package '$package_name' not found in manifest"
        return 1
    fi
    
    # Get install command
    local install_cmd
    install_cmd=$(jq -r ".packages | to_entries[] | select(.value | has(\"$package_name\")) | .value.\"$package_name\".install_command" "$MANIFEST_FILE")
    
    echo "🔧 Running: $install_cmd"
    if eval "$install_cmd"; then
        echo "✅ Package '$package_name' installed successfully"
        return 0
    else
        echo "❌ Failed to install package '$package_name'"
        return 1
    fi
}

install_auto_packages() {
    echo "🚀 Installing auto-install packages from queue..."
    
    if [[ ! -f "$INSTALL_QUEUE" ]]; then
        echo "⚠️ Install queue not found: $INSTALL_QUEUE"
        return 1
    fi
    
    while IFS= read -r package_name || [[ -n "$package_name" ]]; do
        # Skip empty lines and comments
        [[ -z "$package_name" || "$package_name" =~ ^[[:space:]]*# ]] && continue
        
        echo "📦 Processing auto-install: $package_name"
        install_package "$package_name"
    done < "$INSTALL_QUEUE"
}

list_packages() {
    echo "📦 Available Packages:"
    echo "====================="
    
    jq -r '.packages | to_entries[] as $category | $category.value | to_entries[] | "\($category.key): \(.key) - \(.value.description)"' "$MANIFEST_FILE"
}

package_info() {
    local package_name="$1"
    echo "📋 Package Information: $package_name"
    echo "================================="
    
    # Find package in any category
    local info
    info=$(jq -r ".packages | to_entries[] | .value.\"$package_name\" // empty" "$MANIFEST_FILE")
    
    if [[ -z "$info" || "$info" == "null" ]]; then
        echo "❌ Package '$package_name' not found"
        return 1
    fi
    
    echo "Description: $(echo "$info" | jq -r '.description')"
    echo "Install Command: $(echo "$info" | jq -r '.install_command')"
    echo "uCode Commands: $(echo "$info" | jq -r '.ucode_commands | join(", ")')"
    echo "Auto Install: $(echo "$info" | jq -r '.auto_install')"
    echo "Priority: $(echo "$info" | jq -r '.priority')"
}

check_package_installed() {
    local package_name="$1"
    
    case "$package_name" in
        "nano") command -v nano >/dev/null 2>&1 ;;
        "micro") command -v micro >/dev/null 2>&1 ;;
        "helix") command -v hx >/dev/null 2>&1 ;;
        "ripgrep") command -v rg >/dev/null 2>&1 ;;
        "fd") command -v fd >/dev/null 2>&1 ;;
        "bat") command -v bat >/dev/null 2>&1 ;;
        "glow") command -v glow >/dev/null 2>&1 ;;
        "jq") command -v jq >/dev/null 2>&1 ;;
        *) return 1 ;;
    esac
}

validate_packages() {
    echo "✅ Package Validation:"
    echo "====================="
    
    while IFS= read -r package_name || [[ -n "$package_name" ]]; do
        [[ -z "$package_name" || "$package_name" =~ ^[[:space:]]*# ]] && continue
        
        if check_package_installed "$package_name"; then
            echo "✅ $package_name: installed"
        else
            echo "❌ $package_name: not installed"
        fi
    done < "$INSTALL_QUEUE"
}

# Command Interface
case "${1:-}" in
    "install")
        if [[ -n "${2:-}" ]]; then
            install_package "$2"
        else
            echo "Usage: package-manager.sh install <package_name>"
            exit 1
        fi
        ;;
    "install-all")
        install_auto_packages
        ;;
    "list")
        list_packages
        ;;
    "info")
        if [[ -n "${2:-}" ]]; then
            package_info "$2"
        else
            echo "Usage: package-manager.sh info <package_name>"
            exit 1
        fi
        ;;
    "validate")
        validate_packages
        ;;
    *)
        echo "uDOS Package Manager v1.0"
        echo "========================="
        echo "Commands:"
        echo "  install <package>  - Install specific package"
        echo "  install-all        - Install all auto-packages"
        echo "  list              - List available packages"
        echo "  info <package>    - Show package information"
        echo "  validate          - Check package installation status"
        echo ""
        echo "Examples:"
        echo "  ./package-manager.sh install nano"
        echo "  ./package-manager.sh install-all"
        echo "  ./package-manager.sh list"
        ;;
esac
