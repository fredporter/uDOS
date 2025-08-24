#!/bin/bash
# uDOS v1.4 Display System Setup
# Sets up desktop app and web export capabilities

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DISPLAY_DIR="$UDOS_ROOT/uNETWORK/display"

# Load core systems
source "$UDOS_ROOT/uSCRIPT/library/shell/ensure-utf8.sh"
source "$UDOS_ROOT/uCORE/system/polaroid-colors.sh"

# Setup functions
setup_nodejs() {
    polaroid_echo "cyan" "📦 Setting up Node.js for desktop app..."

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
            cp -r static/* src/ 2>/dev/null || true
        fi
        if [[ -d "templates" ]]; then
            cp -r templates/* src/ 2>/dev/null || true
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

build_desktop_app() {
    polaroid_echo "cyan" "� Building desktop application..."

    cd "$DISPLAY_DIR"

    if [[ ! -f "src-tauri/Cargo.toml" ]]; then
        polaroid_echo "orange" "❌ Tauri project not set up. Run setup first."
        return 1
    fi

    # Build the Tauri app
    npm run tauri build

    if [[ -f "src-tauri/target/release/udos-display" ]]; then
        polaroid_echo "lime" "✅ Desktop app built successfully!"
    else
        polaroid_echo "yellow" "⚠️  Build completed but executable not found. Try development mode:"
        polaroid_echo "cyan" "   npm run tauri dev"
    fi
}

# Main function
main() {
    polaroid_echo "cyan" "🚀 uDOS v1.4 Display System Setup"
    echo

    case "${1:-setup}" in
        "setup"|"install")
            setup_nodejs
            setup_rust
            setup_tauri_project
            setup_dependencies

            polaroid_echo "lime" "✅ Display system setup complete!"
            echo
            polaroid_echo "cyan" "Next steps:"
            polaroid_echo "cyan" "  1. Build desktop app: ./setup-display-system.sh build"
            polaroid_echo "cyan" "  2. Test with: ./uNETWORK/display/udos-display.sh app"
            polaroid_echo "cyan" "  3. Or try browser mode: ./uNETWORK/display/udos-display.sh export"
            ;;
        "build")
            build_desktop_app
            ;;
        "test")
            polaroid_echo "cyan" "🧪 Testing display system..."

            # Check if display launcher exists
            if [[ -f "$DISPLAY_DIR/udos-display.sh" ]]; then
                polaroid_echo "lime" "✅ Display launcher found: $DISPLAY_DIR/udos-display.sh"
            else
                polaroid_echo "orange" "❌ Display launcher not found."
                return 1
            fi

            # Check dependencies
            local has_node=0
            local has_rust=0
            local has_tauri=0

            if command -v node >/dev/null 2>&1; then
                polaroid_echo "lime" "✅ Node.js: $(node --version)"
                has_node=1
            else
                polaroid_echo "orange" "❌ Node.js not installed"
            fi

            if command -v cargo >/dev/null 2>&1; then
                polaroid_echo "lime" "✅ Rust: $(rustc --version | cut -d' ' -f2)"
                has_rust=1
            else
                polaroid_echo "orange" "❌ Rust not installed"
            fi

            # Check if Tauri app is built
            if [[ -f "$DISPLAY_DIR/src-tauri/target/release/udos-display" ]] || \
               [[ -f "$DISPLAY_DIR/src-tauri/target/debug/udos-display" ]]; then
                polaroid_echo "lime" "✅ Tauri desktop app built"
                has_tauri=1
            else
                polaroid_echo "orange" "❌ Tauri desktop app not built"
            fi

            echo
            if [[ $has_node -eq 1 && $has_rust -eq 1 && $has_tauri -eq 1 ]]; then
                polaroid_echo "lime" "🎉 Display system fully ready!"
            elif [[ $has_node -eq 1 && $has_rust -eq 1 ]]; then
                polaroid_echo "yellow" "⚠️  Display system ready, but desktop app needs building"
                polaroid_echo "cyan" "   Run: ./setup-display-system.sh build"
            else
                polaroid_echo "orange" "❌ Display system needs setup"
                polaroid_echo "cyan" "   Run: ./setup-display-system.sh setup"
            fi
            ;;
        "help"|"-h"|"--help")
            cat << EOF
🎯 uDOS v1.4 Display System Setup

Usage: $0 <command>

Commands:
  setup     Install Node.js, Rust, and set up Tauri project
  build     Build the desktop application
  test      Test if display system is working
  help      Show this help

This sets up the three-mode display system:
  - CLI Terminal (always available)
  - Desktop Application (native Tauri app)
  - Web Export (browser interface)
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
