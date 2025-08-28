#!/bin/bash
# uDOS Auto-completion Integration Script v1.0.4.4
# Installs and manages the uDOS command auto-completion system

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPLETION_SCRIPT="$UDOS_ROOT/uCORE/completion/udos-completion.bash"

# ════════════════════════════════════════════════════════════════
# 🎯 INSTALLATION FUNCTIONS
# ════════════════════════════════════════════════════════════════

install_for_user() {
    local bashrc_file="$HOME/.bashrc"
    local completion_line="source '$COMPLETION_SCRIPT'"
    
    echo "🔧 Installing uDOS auto-completion for current user..."
    
    # Check if already installed
    if grep -q "udos-completion.bash" "$bashrc_file" 2>/dev/null; then
        echo "✅ Auto-completion already installed in $bashrc_file"
    else
        echo "" >> "$bashrc_file"
        echo "# uDOS Auto-completion" >> "$bashrc_file"
        echo "$completion_line" >> "$bashrc_file"
        echo "✅ Added auto-completion to $bashrc_file"
    fi
    
    # Install for current session
    source "$COMPLETION_SCRIPT"
    echo "✅ Auto-completion active for current session"
}

install_system_wide() {
    local completion_dir="/etc/bash_completion.d"
    local completion_file="$completion_dir/udos"
    
    echo "🔧 Installing uDOS auto-completion system-wide..."
    
    if [[ ! -d "$completion_dir" ]]; then
        echo "❌ System completion directory not found: $completion_dir"
        echo "💡 Try user installation instead: $0 --user"
        return 1
    fi
    
    if [[ $EUID -ne 0 ]]; then
        echo "❌ System-wide installation requires root privileges"
        echo "💡 Try: sudo $0 --system"
        echo "💡 Or user installation: $0 --user"
        return 1
    fi
    
    cp "$COMPLETION_SCRIPT" "$completion_file"
    chmod 644 "$completion_file"
    echo "✅ Installed to $completion_file"
    echo "💡 Restart shell or run: source $completion_file"
}

install_for_session() {
    echo "🔧 Installing uDOS auto-completion for current session only..."
    source "$COMPLETION_SCRIPT"
    echo "✅ Auto-completion active for current session"
    echo "💡 For permanent installation, use: $0 --user"
}

# ════════════════════════════════════════════════════════════════
# 🧪 TESTING AND VALIDATION
# ════════════════════════════════════════════════════════════════

test_completion() {
    echo "🧪 Testing uDOS Auto-completion System"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Test if completion script exists
    if [[ ! -f "$COMPLETION_SCRIPT" ]]; then
        echo "❌ Completion script not found: $COMPLETION_SCRIPT"
        return 1
    fi
    
    # Source and test
    source "$COMPLETION_SCRIPT"
    udos_completion_test
    
    echo ""
    echo "🎯 Quick Test Commands:"
    echo "  udos status    # System dashboard"
    echo "  udos role      # Current role"
    echo "  udos help      # Command help"
    echo "  udos template list  # List templates"
    echo ""
    echo "💡 Try typing 'udos ' and press TAB for completion"
}

show_status() {
    echo "📊 uDOS Auto-completion Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check if completion script exists
    if [[ -f "$COMPLETION_SCRIPT" ]]; then
        echo "✅ Completion script: $COMPLETION_SCRIPT"
    else
        echo "❌ Completion script not found: $COMPLETION_SCRIPT"
    fi
    
    # Check if installed in bashrc
    if grep -q "udos-completion.bash" "$HOME/.bashrc" 2>/dev/null; then
        echo "✅ User installation: Found in ~/.bashrc"
    else
        echo "➖ User installation: Not found in ~/.bashrc"
    fi
    
    # Check system installation
    if [[ -f "/etc/bash_completion.d/udos" ]]; then
        echo "✅ System installation: Found in /etc/bash_completion.d/"
    else
        echo "➖ System installation: Not found"
    fi
    
    # Check current session
    if type -t udos >/dev/null 2>&1; then
        echo "✅ Current session: 'udos' alias active"
    else
        echo "➖ Current session: 'udos' alias not loaded"
    fi
    
    echo ""
    echo "💡 Use '$0 --install' to install auto-completion"
}

# ════════════════════════════════════════════════════════════════
# 🎪 MAIN SCRIPT LOGIC
# ════════════════════════════════════════════════════════════════

show_help() {
    echo "🎯 uDOS Auto-completion Integration Script v1.0.4.4"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --install, -i    Install for current user (recommended)"
    echo "  --user           Install for current user only"
    echo "  --system         Install system-wide (requires root)"
    echo "  --session        Install for current session only"
    echo "  --test, -t       Test completion functionality"
    echo "  --status, -s     Show installation status"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --install     # Install for current user"
    echo "  $0 --test        # Test completion system"
    echo "  $0 --status      # Check installation status"
    echo ""
    echo "Features:"
    echo "  • Tab completion for native CLI commands"
    echo "  • Context-aware suggestions based on user role"
    echo "  • Template name completion"
    echo "  • Variable name completion"
    echo "  • Convenient 'udos' alias"
}

# Main execution
main() {
    case "${1:-}" in
        --install|-i|--user)
            install_for_user
            ;;
        --system)
            install_system_wide
            ;;
        --session)
            install_for_session
            ;;
        --test|-t)
            test_completion
            ;;
        --status|-s)
            show_status
            ;;
        --help|-h|"")
            show_help
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "💡 Use --help for usage information"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
