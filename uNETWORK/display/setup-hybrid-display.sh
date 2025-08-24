#!/bin/bash
# uDOS v1.4 Display System Setup
# Sets up desktop app and web export capabilities

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DISPLAY_DIR="$UDOS_ROOT/uNETWORK/display"

# Load core systems
source "$UDOS_ROOT/uSCRIPT/library/shell/ensure-utf8.sh"
source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"

main() {
    polaroid_echo "cyan" "🎯 Setting up uDOS v1.4 Display Modes"
    echo
    polaroid_echo "cyan" "Available display modes:"
    polaroid_echo "lime" "  1. CLI Terminal (always available)"
    polaroid_echo "lime" "  2. Desktop App (for DRONE+ roles)"  
    polaroid_echo "lime" "  3. Web Export (for sharing/presenting)"
    echo

# Setup functions
setup_nodejs() {
    polaroid_echo "cyan" "📦 Setting up Node.js for Tauri..."

    if command -v node >/dev/null 2>&1; then
        polaroid_echo "lime" "✅ Node.js already installed: $(node --version)"
        return 0
    fi

    # Try to install via package managers
    if command -v brew >/dev/null 2>&1; then
        polaroid_echo "cyan" "   Installing via Homebrew..."
        brew install node
    elif command -v apt >/dev/null 2>&1; then
        polaroid_echo "cyan" "   Installing via apt..."
        sudo apt update && sudo apt install -y nodejs npm
    elif command -v yum >/dev/null 2>&1; then
        polaroid_echo "cyan" "   Installing via yum..."
        sudo yum install -y nodejs npm
    else
        polaroid_echo "yellow" "⚠️  Please install Node.js manually from https://nodejs.org"
        return 1
    fi
}

setup_rust() {
    polaroid_echo "cyan" "🦀 Setting up Rust for Tauri..."

    if command -v cargo >/dev/null 2>&1; then
        polaroid_echo "lime" "✅ Rust already installed: $(rustc --version)"
        return 0
    fi

    polaroid_echo "cyan" "   Installing Rust via rustup..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
}

setup_tauri_project() {
    polaroid_echo "cyan" "🏗️  Setting up Tauri project structure..."

    cd "$DISPLAY_DIR"

    # Create Tauri project if it doesn't exist
    if [[ ! -f "src-tauri/Cargo.toml" ]]; then
        polaroid_echo "cyan" "   Creating new Tauri project..."
        npm create tauri-app@latest -- --name udos-display --template vanilla --yes

        # Move our existing assets
        if [[ -d "static" ]]; then
            polaroid_echo "cyan" "   Integrating existing web assets..."
            cp -r static/* src/
            cp -r templates/* src/
        fi
    else
        polaroid_echo "lime" "✅ Tauri project already exists"
    fi
}

setup_dependencies() {
    polaroid_echo "cyan" "📦 Installing dependencies..."

    cd "$DISPLAY_DIR"

    # Install npm dependencies
    if [[ -f "package.json" ]]; then
        npm install
    fi

    # Install Python dependencies for backend
    pip3 install flask flask-socketio psutil eventlet 2>/dev/null || {
        polaroid_echo "yellow" "⚠️  Could not install Python dependencies globally"
        polaroid_echo "cyan" "   They will be installed when needed"
    }
}

create_hybrid_launcher() {
    polaroid_echo "cyan" "🚀 Creating hybrid launcher..."

    cat > "$DISPLAY_DIR/udos-display.sh" << 'EOF'
#!/bin/bash
# uDOS v1.4 Hybrid Display Launcher
# Launches native app by default, browser as fallback

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DISPLAY_DIR="$UDOS_ROOT/uNETWORK/display"

# Load core systems
source "$UDOS_ROOT/uSCRIPT/library/shell/ensure-utf8.sh"
source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"

# Mode selection
MODE="${1:-auto}"
FORCE_BROWSER="${UDOS_FORCE_BROWSER:-0}"

detect_capabilities() {
    local has_tauri=0
    local has_browser=1  # Always available

    # Check if Tauri app is built
    if [[ -f "$DISPLAY_DIR/src-tauri/target/release/udos-display" ]] || \
       [[ -f "$DISPLAY_DIR/src-tauri/target/debug/udos-display" ]]; then
        has_tauri=1
    fi

    echo "$has_tauri:$has_browser"
}

launch_native() {
    polaroid_echo "cyan" "🖥️  Launching native uDOS Display App..."

    cd "$DISPLAY_DIR"

    # Try release build first, then debug
    if [[ -f "src-tauri/target/release/udos-display" ]]; then
        ./src-tauri/target/release/udos-display
    elif [[ -f "src-tauri/target/debug/udos-display" ]]; then
        ./src-tauri/target/debug/udos-display
    else
        polaroid_echo "yellow" "⚠️  Native app not built, building now..."
        npm run tauri build || npm run tauri dev
    fi
}

launch_browser() {
    polaroid_echo "cyan" "🌐 Launching browser interface..."
    "$DISPLAY_DIR/launch-display-server.sh" start --open
}

main() {
    local capabilities
    capabilities=$(detect_capabilities)
    local has_tauri="${capabilities%:*}"
    local has_browser="${capabilities#*:}"

    polaroid_echo "cyan" "🎯 uDOS v1.4 Display System"
    echo

    case "$MODE" in
        "native"|"app"|"tauri")
            if [[ "$has_tauri" == "1" ]]; then
                launch_native
            else
                polaroid_echo "orange" "❌ Native app not available"
                if [[ "$has_browser" == "1" ]]; then
                    polaroid_echo "cyan" "   Falling back to browser mode..."
                    launch_browser
                fi
            fi
            ;;
        "browser"|"web")
            launch_browser
            ;;
        "auto")
            if [[ "$FORCE_BROWSER" == "1" ]]; then
                launch_browser
            elif [[ "$has_tauri" == "1" ]]; then
                polaroid_echo "lime" "✨ Launching native app (preferred mode)"
                launch_native
            else
                polaroid_echo "cyan" "🌐 Native app not built, using browser mode"
                launch_browser
            fi
            ;;
        "build")
            polaroid_echo "cyan" "🔨 Building native app..."
            cd "$DISPLAY_DIR"
            npm run tauri build
            ;;
        "dev")
            polaroid_echo "cyan" "🛠️  Starting development mode..."
            cd "$DISPLAY_DIR"
            npm run tauri dev
            ;;
        "help"|"-h"|"--help")
            cat << HELP
🎯 uDOS v1.4 Hybrid Display System

Usage: $0 [mode] [options]

Modes:
  auto      Launch native app if available, browser otherwise (default)
  native    Force native app mode
  browser   Force browser mode
  build     Build native app
  dev       Start development mode
  help      Show this help

Environment:
  UDOS_FORCE_BROWSER=1    Always use browser mode

Examples:
  $0                      # Auto-detect best mode
  $0 native              # Force native app
  $0 browser             # Force browser
  $0 build               # Build native app

Native App: Professional desktop application
Browser Mode: Fallback web interface at http://localhost:8080
HELP
            ;;
        *)
            polaroid_echo "orange" "❌ Unknown mode: $MODE"
            polaroid_echo "cyan" "   Use: $0 help"
            exit 1
            ;;
    esac
}

main "$@"
EOF

    chmod +x "$DISPLAY_DIR/udos-display.sh"
    polaroid_echo "lime" "✅ Hybrid launcher created: $DISPLAY_DIR/udos-display.sh"
}

create_tauri_config() {
    polaroid_echo "cyan" "⚙️  Creating Tauri configuration..."

    # This will be created when we run the Tauri setup
    polaroid_echo "cyan" "   Configuration will be generated with Tauri project"
}

main() {
    polaroid_echo "cyan" "🚀 Setting up uDOS v1.4 Hybrid Display System"
    echo

    case "${1:-setup}" in
        "setup"|"install")
            setup_nodejs
            setup_rust
            setup_tauri_project
            setup_dependencies
            create_hybrid_launcher
            create_tauri_config

            polaroid_echo "lime" "✅ Hybrid Display System setup complete!"
            echo
            polaroid_echo "cyan" "Next steps:"
            polaroid_echo "cyan" "  1. Build native app: ./udos-display.sh build"
            polaroid_echo "cyan" "  2. Launch system: ./udos-display.sh"
            polaroid_echo "cyan" "  3. Force browser: ./udos-display.sh browser"
            ;;
        "test")
            if [[ -f "$DISPLAY_DIR/udos-display.sh" ]]; then
                "$DISPLAY_DIR/udos-display.sh" help
            else
                polaroid_echo "orange" "❌ Hybrid launcher not found. Run setup first."
            fi
            ;;
        "help"|"-h"|"--help")
            cat << EOF
🎯 uDOS v1.4 Hybrid Display Setup

Usage: $0 <command>

Commands:
  setup     Install all dependencies and create hybrid system
  test      Test the hybrid launcher
  help      Show this help

This creates:
  - Native Tauri desktop app (primary interface)
  - Browser fallback mode (compatibility)
  - Hybrid launcher that auto-detects best mode
EOF
            ;;
        *)
            polaroid_echo "orange" "❌ Unknown command: $1"
            polaroid_echo "cyan" "   Use: $0 help"
            exit 1
            ;;
    esac
}

main "$@"
