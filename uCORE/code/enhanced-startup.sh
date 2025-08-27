#!/bin/bash
# Enhanced uDOS Startup with Variable and Adventure Integration
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Enhanced startup sequence
enhanced_startup() {
    local current_role=$(cat "$UDOS_ROOT/sandbox/current-role.conf" 2>/dev/null | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"' || echo "GHOST")

    echo "🌟 uDOS Enhanced Startup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎭 Role: $current_role"

    # Check if startup story should run
    if "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" should-run "$current_role"; then
        echo "🎯 Running $current_role startup story..."
        "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$current_role"
        "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" mark-complete "$current_role"
    fi

    # Apply current variable integration
    "$UDOS_ROOT/uCORE/code/startup-variable-integration.sh" integrate "$current_role"

    # Check adventure mode
    local adventure_mode=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "ADVENTURE-MODE" 2>/dev/null || echo "enabled")
    if [[ "$adventure_mode" == "enabled" ]]; then
        echo "🎲 Adventure mode active!"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 STARTUP: $current_role role session started" >> "$UDOS_ROOT/sandbox/logs/adventure.log"
    fi

    echo ""
    echo "Available commands:"
    echo "  🎲 adventure    - Enter interactive adventure mode"
    echo "  📊 status       - Show system and adventure status"
    echo "  🔧 variables    - Manage system variables"
    echo "  🎭 role         - Change current role"
    echo "  ❓ help         - Show help information"
    echo ""

    # Start interactive session
    start_interactive_session "$current_role"
}

# Interactive session with enhanced commands
start_interactive_session() {
    local role="$1"

    while true; do
        read -p "🎯 uDOS ($role)> " command args

        case "$command" in
            "adventure")
                "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" adventure
                ;;
            "status")
                show_enhanced_status "$role"
                ;;
            "variables")
                "$UDOS_ROOT/uCORE/code/variable-manager.sh" LIST all
                ;;
            "role")
                change_role_interactive
                role=$(cat "$UDOS_ROOT/sandbox/current-role.conf" | grep "^ROLE=" | cut -d'=' -f2 | tr -d '"')
                ;;
            "startup")
                "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$role"
                ;;
            "help")
                show_enhanced_help
                ;;
            "exit"|"quit")
                echo "👋 Farewell, $role!"
                break
                ;;
            "")
                # Empty command, continue
                ;;
            *)
                echo "❓ Unknown command: $command"
                echo "💡 Type 'help' for available commands"
                ;;
        esac
    done
}

# Show enhanced status
show_enhanced_status() {
    local role="$1"

    echo "📊 uDOS Enhanced Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎭 Current Role: $role"

    # Show adventure stats if enabled
    local adventure_mode=$("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "ADVENTURE-MODE" 2>/dev/null || echo "disabled")
    if [[ "$adventure_mode" == "enabled" ]]; then
        local quest_count=$(grep -c "QUEST_START" "$UDOS_ROOT/sandbox/logs/adventure.log" 2>/dev/null || echo 0)
        local achievement_count=$(grep -c "ACHIEVEMENT" "$UDOS_ROOT/sandbox/logs/adventure.log" 2>/dev/null || echo 0)

        echo "🎲 Adventure Mode: Active"
        echo "🗡️ Quests Started: $quest_count"
        echo "🏆 Achievements: $achievement_count"
    else
        echo "🎲 Adventure Mode: Disabled"
    fi

    # Show key variables
    echo ""
    echo "🔧 Key Variables:"
    echo "   DISPLAY-MODE: $("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "DISPLAY-MODE" 2>/dev/null || echo "CLI")"
    echo "   DETAIL-LEVEL: $("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "DETAIL-LEVEL" 2>/dev/null || echo "STANDARD")"
    echo "   PROJECT-TYPE: $("$UDOS_ROOT/uCORE/code/variable-manager.sh" GET "PROJECT-TYPE" 2>/dev/null || echo "none")"
}

# Enhanced help
show_enhanced_help() {
    echo "🎯 uDOS Enhanced Commands"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🎲 Adventure & Role Commands:"
    echo "   adventure     - Enter interactive adventure mode"
    echo "   role          - Change current role with startup story"
    echo "   startup       - Run startup story for current role"
    echo ""
    echo "🔧 System Commands:"
    echo "   status        - Show enhanced system status"
    echo "   variables     - View and manage system variables"
    echo "   help          - Show this help"
    echo ""
    echo "🚪 Session Commands:"
    echo "   exit, quit    - End current session"
    echo ""
}

# Interactive role change
change_role_interactive() {
    echo "🎭 Role Change System"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Available roles:"
    echo "   10 👻 GHOST    - Ethereal explorer (demo access)"
    echo "   20 🗿 TOMB     - Archive keeper (storage focus)"
    echo "   30 🔐 CRYPT    - Security guardian (protection)"
    echo "   40 🤖 DRONE    - Automation specialist (efficiency)"
    echo "   50 ⚔️ KNIGHT   - System protector (service)"
    echo "   60 😈 IMP      - Creative developer (innovation)"
    echo "   80 🧙‍♂️ SORCERER - Advanced administrator (power)"
    echo "  100 🌟 WIZARD   - Supreme master (omnipotence)"
    echo ""

    read -p "🎯 Choose new role: " new_role
    new_role=$(echo "$new_role" | tr '[:lower:]' '[:upper:]')

    case "$new_role" in
        GHOST|TOMB|CRYPT|DRONE|KNIGHT|IMP|SORCERER|WIZARD)
            echo "ROLE=\"$new_role\"" > "$UDOS_ROOT/sandbox/current-role.conf"
            echo "TIMESTAMP=\"$(date '+%Y-%m-%d %H:%M:%S %Z')\"" >> "$UDOS_ROOT/sandbox/current-role.conf"

            echo "✅ Role changed to $new_role!"

            # Offer startup story
            read -p "🌟 Run $new_role startup story? (y/n): " run_startup
            if [[ "$run_startup" =~ ^[Yy] ]]; then
                "$UDOS_ROOT/uCORE/code/startup-story-manager.sh" startup "$new_role"
            fi
            ;;
        *)
            echo "❌ Invalid role choice"
            ;;
    esac
}

# Main execution
main() {
    case "${1:-start}" in
        "start"|"")
            enhanced_startup
            ;;
        "install")
            "$UDOS_ROOT/uCORE/code/enhanced-install-integration.sh" full
            ;;
        "quick-install")
            "$UDOS_ROOT/uCORE/code/enhanced-install-integration.sh" quick "${2:-GHOST}"
            ;;
        *)
            echo "Usage: $0 {start|install|quick-install} [ROLE]"
            exit 1
            ;;
    esac
}

main "$@"
