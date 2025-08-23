#!/bin/bash
# NetHack Installation Script for uDOS
# Source: https://github.com/NetHack/NetHack

set -e

PACKAGE_NAME="nethack"
REPO_URL="https://github.com/NetHack/NetHack.git"
INSTALL_DIR="$HOME/.local/bin"
UDOS_PACKAGES_DIR="$HOME/uDOS/uCode/packages"

echo ""
echo "🎮 Installing NetHack for uDOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if NetHack is already available via package manager
if command -v nethack &> /dev/null; then
    echo "✅ NetHack already installed via system package manager"
    echo "   Using existing installation"
    
    # Create uDOS integration script
    mkdir -p "$UDOS_PACKAGES_DIR/nethack"
    
    cat > "$UDOS_PACKAGES_DIR/nethack/udos-nethack-integration.sh" << 'EOF'
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
EOF

    chmod +x "$UDOS_PACKAGES_DIR/nethack/udos-nethack-integration.sh"
    
    echo "✅ uDOS NetHack integration created"
    echo ""
    echo "🎉 NetHack Integration Complete!"
    echo ""
    echo "📋 USAGE:"
    echo "  [NETHACK|PLAY]     - Start adventure"
    echo "  [NETHACK|CONTINUE] - Resume saved game"
    echo "  [NETHACK|SCORES]   - View high scores"
    echo "  [NETHACK|HELP]     - Tutorial and help"
    echo ""
    
    exit 0
fi

# Check if we should try to install via package manager first
echo "🔍 Checking for package manager installation options..."

if command -v brew &> /dev/null; then
    echo "📦 Homebrew detected - installing NetHack via brew..."
    if brew install nethack; then
        echo "✅ NetHack installed successfully via Homebrew"
        # Create integration and exit
        exec "$0"
    else
        echo "⚠️ Homebrew installation failed, will try building from source"
    fi
elif command -v apt-get &> /dev/null; then
    echo "📦 APT detected - installing NetHack via apt..."
    if sudo apt-get update && sudo apt-get install -y nethack-console; then
        echo "✅ NetHack installed successfully via APT"
        exec "$0"
    else
        echo "⚠️ APT installation failed, will try building from source"
    fi
elif command -v yum &> /dev/null; then
    echo "📦 YUM detected - installing NetHack via yum..."
    if sudo yum install -y nethack; then
        echo "✅ NetHack installed successfully via YUM"
        exec "$0"
    else
        echo "⚠️ YUM installation failed, will try building from source"
    fi
fi

# If package manager installation failed or not available, build from source
echo ""
echo "🔨 Building NetHack from source..."
echo ""

# Check build prerequisites
echo "🔍 Checking build prerequisites..."

if ! command -v gcc &> /dev/null && ! command -v clang &> /dev/null; then
    echo "❌ C compiler (gcc or clang) is required but not found."
    echo "   Please install development tools:"
    echo "   macOS: xcode-select --install"
    echo "   Ubuntu/Debian: sudo apt-get install build-essential"
    echo "   CentOS/RHEL: sudo yum groupinstall 'Development Tools'"
    exit 1
fi

if ! command -v make &> /dev/null; then
    echo "❌ make is required but not found."
    echo "   Please install build tools first."
    exit 1
fi

echo "✅ Build prerequisites found"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$UDOS_PACKAGES_DIR/nethack"

# Clone and build NetHack
echo ""
echo "📥 Downloading NetHack source..."
cd /tmp
if [ -d "NetHack" ]; then
    rm -rf NetHack
fi

git clone "$REPO_URL"
cd NetHack

echo ""
echo "🔧 Configuring NetHack build..."

# Create a minimal configuration
cat > include/config.h << 'EOF'
/* NetHack configuration for uDOS */
#define UNIX
#define TTY_GRAPHICS
#define CURSES_GRAPHICS
#define TEXTCOLOR
#define COMPRESS "/usr/bin/compress"
#define HACKDIR "/usr/local/lib/nethackdir"
#define VAR_PLAYGROUND "/var/lib/nethack"
#define WIZARD "wizard"
#define SHELL "/bin/sh"
EOF

echo ""
echo "🔨 Building NetHack..."
make all

echo ""
echo "📦 Installing NetHack..."
sudo make install

# Create uDOS integration script (same as above)
cat > "$UDOS_PACKAGES_DIR/nethack/udos-nethack-integration.sh" << 'EOF'
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
EOF

chmod +x "$UDOS_PACKAGES_DIR/nethack/udos-nethack-integration.sh"

# Test installation
echo ""
echo "🧪 Testing NetHack installation..."
if command -v nethack &> /dev/null; then
    echo "✅ NetHack installed and working"
else
    echo "⚠️ Installation completed but NetHack command not found"
    echo "   You may need to restart your terminal or add to PATH"
fi

# Clean up
echo ""
echo "🧹 Cleaning up build files..."
rm -rf /tmp/NetHack

echo ""
echo "🎉 NetHack Installation Complete!"
echo ""
echo "📋 USAGE:"
echo "  [NETHACK|PLAY]     - Start your adventure"
echo "  [NETHACK|CONTINUE] - Resume saved game"
echo "  [NETHACK|SCORES]   - View high scores"
echo "  [NETHACK|HELP]     - Tutorial and controls"
echo ""
echo "🎮 Quick Start:"
echo "  nethack            - Launch game directly"
echo "  bash $UDOS_PACKAGES_DIR/nethack/udos-nethack-integration.sh help"
echo ""
echo "🗡️ May your quest be successful, adventurer!"
echo ""
