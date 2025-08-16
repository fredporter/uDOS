#!/bin/bash
# uDOS NetHack Integration

show_nethack_help() {
    echo ""
    echo "🎮 NetHack - The Classic Roguelike Adventure"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🗡️ GAME COMMANDS:"
    echo "  [NETHACK|PLAY]                  - Start NetHack adventure"
    echo "  [NETHACK|CONTINUE]              - Continue saved game"
    echo "  [NETHACK|SCORES]                - View high scores"
    echo "  [NETHACK|HELP]                  - Game help and tutorial"
    echo ""
    echo "⚔️ GAME FEATURES:"
    echo "  • Classic ASCII-based dungeon crawler"
    echo "  • Rich fantasy adventure with deep gameplay"
    echo "  • Procedurally generated dungeons"
    echo "  • Character classes and races"
    echo "  • Inventory management and crafting"
    echo "  • Spells, artifacts, and treasure"
    echo ""
    echo "🎯 uDOS INTEGRATION:"
    echo "  • Save games stored in uMemory"
    echo "  • Progress logged to uDOS activity"
    echo "  • ASCII art integration"
    echo "  • Terminal-optimized experience"
    echo ""
    echo "📚 QUICK START:"
    echo "  • Use arrow keys or hjkl to move"
    echo "  • Press '?' for help in-game"
    echo "  • Press 'Q' to quit and save"
    echo "  • Visit nethack.org for strategy guides"
    echo ""
}

# Launch NetHack with uDOS integration
launch_nethack() {
    local action="${1:-play}"
    
    # Ensure uMemory NetHack directory exists
    local nethack_dir="$HOME/uDOS/uMemory/games/nethack"
    mkdir -p "$nethack_dir"
    
    case "$action" in
        play|start)
            echo ""
            echo "🎮 Starting NetHack Adventure!"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "🗡️ Welcome to the Dungeons of Doom!"
            echo ""
            echo "💡 Quick Tips:"
            echo "   • Use arrow keys or hjkl to move"
            echo "   • Press '?' for complete help"
            echo "   • Press 'Q' to quit and save progress"
            echo "   • Press 'S' to save without quitting"
            echo ""
            echo "🎯 Your quest: Retrieve the Amulet of Yendor!"
            echo ""
            echo "Press any key to enter the dungeon..."
            read -n 1
            
            # Change to NetHack save directory
            cd "$nethack_dir"
            
            # Launch NetHack
            if command -v nethack &> /dev/null; then
                nethack
            else
                echo "❌ NetHack not found. Please install it first."
                return 1
            fi
            ;;
        continue|resume)
            echo "🔄 Continuing your NetHack adventure..."
            cd "$nethack_dir"
            nethack
            ;;
        scores|highscores)
            echo "🏆 NetHack High Scores:"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            cd "$nethack_dir"
            nethack -s 2>/dev/null || echo "No scores yet - start playing to set records!"
            ;;
        help|tutorial)
            echo "📚 NetHack Help & Tutorial"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "🎮 BASIC CONTROLS:"
            echo "   Movement: Arrow keys or hjkl (vi-style)"
            echo "   Diagonal: yubn (numpad directions)"
            echo "   Wait: . (period)"
            echo "   Search: s"
            echo "   Open door: o"
            echo "   Close door: c"
            echo ""
            echo "⚔️ COMBAT & INTERACTION:"
            echo "   Attack: Move into monster"
            echo "   Pickup: ,"
            echo "   Drop: d"
            echo "   Inventory: i"
            echo "   Wear/Wield: w"
            echo "   Remove: R"
            echo ""
            echo "🔮 MAGIC & ADVANCED:"
            echo "   Cast spell: Z"
            echo "   Read scroll: r"
            echo "   Quaff potion: q"
            echo "   Apply tool: a"
            echo "   Zap wand: z"
            echo ""
            echo "💾 GAME MANAGEMENT:"
            echo "   Save & Quit: Q"
            echo "   Save only: S"
            echo "   Help: ?"
            echo "   Options: O"
            echo ""
            echo "🌐 For complete strategy guides, visit: https://nethack.org"
            ;;
        *)
            echo "Unknown NetHack command: $action"
            show_nethack_help
            ;;
    esac
}

# Check if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-help}" in
        help|--help|-h)
            show_nethack_help
            ;;
        play|start|continue|scores|tutorial)
            launch_nethack "$1"
            ;;
        *)
            launch_nethack "$1"
            ;;
    esac
fi
