#!/bin/bash
# uDOS Consolidated Management System v1.0.0
# Consolidates multiple related scripts into unified command interfaces

set -euo pipefail

UHOME="${HOME}/uDOS"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PACKAGE MANAGEMENT CONSOLIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

package_management() {
    local command="${1:-help}"
    local package="${2:-}"
    
    case "$command" in
        "install")
            if [[ -n "$package" ]]; then
                if [[ -f "$SCRIPT_DIR/packages/install-${package}.sh" ]]; then
                    blue "📦 Installing $package..."
                    source "$SCRIPT_DIR/packages/install-${package}.sh"
                else
                    red "❌ Package installer not found: $package"
                    echo "Available packages:"
                    ls "$SCRIPT_DIR/packages/install-"*.sh 2>/dev/null | sed 's/.*install-//; s/.sh$//' | sed 's/^/  - /'
                fi
            else
                red "❌ Please specify a package to install"
            fi
            ;;
        "list")
            blue "📦 Available Packages:"
            if [[ -d "$SCRIPT_DIR/packages" ]]; then
                ls "$SCRIPT_DIR/packages/install-"*.sh 2>/dev/null | sed 's/.*install-//; s/.sh$//' | sed 's/^/  ✅ /' || echo "  No packages found"
            fi
            ;;
        "install-all")
            blue "📦 Installing all available packages..."
            for installer in "$SCRIPT_DIR/packages/install-"*.sh; do
                if [[ -f "$installer" ]]; then
                    package_name=$(basename "$installer" | sed 's/install-//; s/.sh$//')
                    blue "Installing $package_name..."
                    source "$installer"
                fi
            done
            green "✅ All packages installation complete"
            ;;
        "help")
            echo "📦 Package Management Commands:"
            echo "  install <package>  - Install specific package"
            echo "  install-all        - Install all available packages"
            echo "  list               - List available packages"
            echo "  help               - Show this help"
            ;;
        *)
            red "❌ Unknown package command: $command"
            package_management "help"
            ;;
    esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TEMPLATE PROCESSING CONSOLIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

template_processing() {
    local command="${1:-help}"
    local template_type="${2:-}"
    local target="${3:-}"
    
    case "$command" in
        "setup")
            blue "🔧 Running user setup template processing..."
            if command -v bash >/dev/null 2>&1; then
                local bash_version=$(bash --version | head -n1 | grep -o '[0-9]\+\.[0-9]\+' | head -n1)
                local major_version=$(echo "$bash_version" | cut -d. -f1)
                
                if [[ "$major_version" -ge 4 ]]; then
                    source "$SCRIPT_DIR/setup-template-processor.sh"
                else
                    source "$SCRIPT_DIR/setup-template-processor-compat.sh"
                fi
            else
                source "$SCRIPT_DIR/setup-template-processor-compat.sh"
            fi
            ;;
        "vscode")
            blue "🔧 Processing VS Code templates..."
            source "$SCRIPT_DIR/vscode-template-processor.sh" process
            ;;
        "vb")
            blue "🔧 Processing VB command templates..."
            source "$SCRIPT_DIR/vb-template-processor.sh" "$template_type" "$target"
            ;;
        "display")
            blue "🔧 Processing display templates..."
            source "$SCRIPT_DIR/display-template-processor.sh" "$template_type" "$target"
            ;;
        "finalize")
            blue "🔧 Finalizing template processing..."
            source "$SCRIPT_DIR/template-finalizer.sh"
            ;;
        "help")
            echo "🔧 Template Processing Commands:"
            echo "  setup              - Run user setup templates (with bash compatibility)"
            echo "  vscode             - Process VS Code extension templates"
            echo "  vb <type> <target> - Process VB command templates"
            echo "  display <type>     - Process display configuration templates"
            echo "  finalize           - Finalize all template processing"
            echo "  help               - Show this help"
            ;;
        *)
            red "❌ Unknown template command: $command"
            template_processing "help"
            ;;
    esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VALIDATION AND TESTING CONSOLIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

validation_testing() {
    local command="${1:-help}"
    local scope="${2:-quick}"
    
    case "$command" in
        "installation")
            blue "🔍 Running installation validation..."
            source "$SCRIPT_DIR/validate-installation.sh" "$scope"
            ;;
        "alpha")
            blue "🔍 Running alpha release validation..."
            source "$SCRIPT_DIR/validate-alpha.sh"
            ;;
        "final")
            blue "🔍 Running final release validation..."
            source "$SCRIPT_DIR/final-release-validation.sh"
            ;;
        "launch")
            blue "🔍 Running launch validation..."
            source "$SCRIPT_DIR/launch-validation.sh"
            ;;
        "extension")
            blue "🔍 Running VS Code extension integration tests..."
            source "$SCRIPT_DIR/test-extension-integration.sh"
            ;;
        "check")
            blue "🔍 Running system checks..."
            source "$SCRIPT_DIR/check.sh" "${scope:-all}"
            ;;
        "all")
            blue "🔍 Running comprehensive validation suite..."
            validation_testing "check" "all"
            validation_testing "installation" "full"
            validation_testing "extension"
            green "✅ Comprehensive validation complete"
            ;;
        "help")
            echo "🔍 Validation & Testing Commands:"
            echo "  installation [scope] - Validate installation (quick/full)"
            echo "  alpha                - Run alpha release validation"
            echo "  final                - Run final release validation"
            echo "  launch               - Run launch validation"
            echo "  extension            - Test VS Code extension integration"
            echo "  check [scope]        - Run system checks"
            echo "  all                  - Run comprehensive validation suite"
            echo "  help                 - Show this help"
            ;;
        *)
            red "❌ Unknown validation command: $command"
            validation_testing "help"
            ;;
    esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHORTCODE PROCESSING CONSOLIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

shortcode_processing() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "simple"|"basic")
            blue "⚡ Using simple shortcode processor..."
            source "$SCRIPT_DIR/shortcode-processor-simple.sh" "$@"
            ;;
        "advanced"|"full")
            blue "⚡ Using advanced shortcode processor..."
            source "$SCRIPT_DIR/shortcode-processor.sh" "$@"
            ;;
        "auto")
            # Auto-detect based on requirements
            if [[ "$*" =~ container|dashboard|advanced ]]; then
                shortcode_processing "advanced" "$@"
            else
                shortcode_processing "simple" "$@"
            fi
            ;;
        "help")
            echo "⚡ Shortcode Processing Commands:"
            echo "  simple <args>    - Use simple shortcode processor"
            echo "  advanced <args>  - Use advanced shortcode processor"
            echo "  auto <args>      - Auto-select processor based on requirements"
            echo "  help             - Show this help"
            ;;
        *)
            # Default to auto mode
            shortcode_processing "auto" "$command" "$@"
            ;;
    esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VB COMMAND SYSTEM CONSOLIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

vb_command_system() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "generate")
            blue "🔧 Generating VB commands..."
            source "$SCRIPT_DIR/vb-command-generator.sh" "$@"
            ;;
        "interpret")
            blue "🔧 Interpreting VB commands..."
            source "$SCRIPT_DIR/vb-command-interpreter.sh" "$@"
            ;;
        "enhanced")
            blue "🔧 Using enhanced VB interpreter..."
            source "$SCRIPT_DIR/vb-enhanced-interpreter.sh" "$@"
            ;;
        "run")
            blue "🔧 Running VB program..."
            source "$SCRIPT_DIR/vb-program-runner.sh" "$@"
            ;;
        "template")
            blue "🔧 Processing VB templates..."
            source "$SCRIPT_DIR/vb-template-processor.sh" "$@"
            ;;
        "help")
            echo "🔧 VB Command System:"
            echo "  generate <args>    - Generate VB commands"
            echo "  interpret <args>   - Interpret VB commands"
            echo "  enhanced <args>    - Use enhanced VB interpreter"
            echo "  run <args>         - Run VB program"
            echo "  template <args>    - Process VB templates"
            echo "  help               - Show this help"
            ;;
        *)
            red "❌ Unknown VB command: $command"
            vb_command_system "help"
            ;;
    esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SANDBOX AND ENVIRONMENT CONSOLIDATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

sandbox_environment() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "manage")
            blue "📦 Managing sandbox environment..."
            source "$SCRIPT_DIR/sandbox-manager.sh" "$@"
            ;;
        "enhanced")
            blue "📦 Using enhanced sandbox manager..."
            source "$SCRIPT_DIR/enhanced-sandbox-manager.sh" "$@"
            ;;
        "location")
            blue "🌍 Managing location..."
            source "$SCRIPT_DIR/location-manager.sh" "$@"
            ;;
        "privacy")
            blue "🔒 Managing privacy settings..."
            source "$SCRIPT_DIR/privacy-guard.sh" "$@"
            ;;
        "variables")
            blue "⚙️ Managing variables..."
            source "$SCRIPT_DIR/variable-manager.sh" "$@"
            ;;
        "help")
            echo "📦 Sandbox & Environment:"
            echo "  manage <args>      - Manage sandbox environment"
            echo "  enhanced <args>    - Use enhanced sandbox manager"
            echo "  location <args>    - Manage location settings"
            echo "  privacy <args>     - Manage privacy settings"
            echo "  variables <args>   - Manage system variables"
            echo "  help               - Show this help"
            ;;
        *)
            red "❌ Unknown sandbox command: $command"
            sandbox_environment "help"
            ;;
    esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN COMMAND DISPATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "package"|"pkg")
            package_management "$@"
            ;;
        "template"|"tpl")
            template_processing "$@"
            ;;
        "validate"|"test")
            validation_testing "$@"
            ;;
        "shortcode"|"sc")
            shortcode_processing "$@"
            ;;
        "vb")
            vb_command_system "$@"
            ;;
        "sandbox"|"env")
            sandbox_environment "$@"
            ;;
        "help"|"--help"|"-h")
            echo
            bold "🛠️ uDOS Consolidated Management System v1.0.0"
            echo "═══════════════════════════════════════════════"
            echo
            echo "Available command groups:"
            echo "  package   - Package management (install, list, etc.)"
            echo "  template  - Template processing (setup, vscode, vb, etc.)"
            echo "  validate  - Validation and testing (installation, alpha, etc.)"
            echo "  shortcode - Shortcode processing (simple, advanced, auto)"
            echo "  vb        - VB command system (generate, interpret, run)"
            echo "  sandbox   - Sandbox and environment management"
            echo
            echo "Examples:"
            echo "  $0 package install ripgrep"
            echo "  $0 template setup"
            echo "  $0 validate all"
            echo "  $0 shortcode auto [run ls]"
            echo "  $0 vb generate examples"
            echo
            echo "Use '$0 <group> help' for group-specific help"
            echo
            ;;
        *)
            red "❌ Unknown command group: $command"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function if script is called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
