#!/bin/bash
# Enhanced Installation Integration with Variable System
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Run complete installation with variable integration
run_complete_installation() {
    echo "🚀 uDOS Enhanced Installation with Variable Integration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 1. Initialize the enhanced variable system
    "$UDOS_ROOT/uCORE/code/system-variable-integration.sh" init

    # 2. Run installation configuration story
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" STORY EXECUTE \
        "$UDOS_ROOT/uMEMORY/system/stories/installation-setup.json" "install-$(date +%s)"

    # 3. Initialize startup story system
    "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" create-stories

    # 4. Run user onboarding story
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" STORY EXECUTE \
        "$UDOS_ROOT/uMEMORY/system/stories/user-onboarding.json" "onboard-$(date +%s)"

    # 5. Get selected role and run role-specific startup
    local user_role=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "USER-ROLE" || echo "GHOST")
    "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$user_role"

    # 6. Apply role-specific variable configurations
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" integrate "$user_role"
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" mark-complete "$user_role"

    # 7. Initialize adventure system if enabled
    local adventure_mode=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "ADVENTURE-MODE" || echo "enabled")
    if [[ "$adventure_mode" == "enabled" ]]; then
        echo "🎲 Initializing adventure system..."
        echo "Welcome to your uDOS adventure!" > "$UDOS_ROOT/sandbox/logs/adventure.log"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🎯 INSTALLATION_COMPLETE: uDOS installation completed with role $user_role" >> "$UDOS_ROOT/sandbox/logs/adventure.log"
    fi

    echo ""
    echo "✅ Enhanced installation complete!"
    echo "🎭 Role: $user_role"
    echo "🎲 Adventure Mode: $adventure_mode"
    echo ""
    echo "Next steps:"
    echo "  • Run: ./uCORE/code/startup-story-manager.sh adventure"
    echo "  • Or: ./uCORE/code/ucode.sh"
}

# Quick role-based installation
quick_install_for_role() {
    local target_role="$1"

    echo "🚀 Quick Installation for $target_role Role"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Set up minimal variable system
    "$UDOS_ROOT/uCORE/code/system-variable-integration.sh" init

    # Set role without story
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "USER-ROLE" "$target_role"
    echo "ROLE=\"$target_role\"" > "$UDOS_ROOT/sandbox/current-role.conf"
    echo "TIMESTAMP=\"$(date '+%Y-%m-%d %H:%M:%S %Z')\"" >> "$UDOS_ROOT/sandbox/current-role.conf"

    # Apply role-specific variables
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" integrate "$target_role"

    # Enable adventure mode by default
    "$UDOS_ROOT/uCORE/code/variable-manager.sh" SET "ADVENTURE-MODE" "enabled"

    echo "✅ Quick installation complete for $target_role role!"
}

main() {
    case "${1:-full}" in
        "full")
            run_complete_installation
            ;;
        "quick")
            quick_install_for_role "${2:-GHOST}"
            ;;
        *)
            echo "Usage: $0 {full|quick} [ROLE]"
            exit 1
            ;;
    esac
}

main "$@"
