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
        polaroid_echo "yellow" "⚠️  No package manager found. Installing Node.js manually..."

        # Detect platform and provide specific instructions
        if [[ "$OSTYPE" == "darwin"* ]]; then
            polaroid_echo "cyan" "   macOS detected. Options:"
            polaroid_echo "cyan" "   1) Install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            polaroid_echo "cyan" "   2) Download from: https://nodejs.org/en/download/"
            polaroid_echo "cyan" "   3) Use Node Version Manager: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
        else
            polaroid_echo "cyan" "   Download and install from: https://nodejs.org"
        fi

        polaroid_echo "cyan" "   After installing Node.js, run: ./setup-display-system.sh setup"
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
    if curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; then
        # Source the cargo environment for this session
        export PATH="$HOME/.cargo/bin:$PATH"
        source "$HOME/.cargo/env" 2>/dev/null || true

        polaroid_echo "lime" "✅ Rust installed successfully"
        polaroid_echo "cyan" "   Note: You may need to restart your terminal or run:"
        polaroid_echo "cyan" "   source ~/.cargo/env"
    else
        polaroid_echo "orange" "❌ Failed to install Rust automatically"
        polaroid_echo "cyan" "   Please install manually from: https://rustup.rs/"
        return 1
    fi
}

setup_tauri_project() {
    polaroid_echo "cyan" "🏗️  Setting up Tauri project structure..."

    cd "$DISPLAY_DIR"

    # Create Tauri project if it doesn't exist
    if [[ ! -f "src-tauri/Cargo.toml" ]]; then
        polaroid_echo "cyan" "   Creating new Tauri project..."
        npm create tauri-app@latest -- --name udos-display --template vanilla --yes

        polaroid_echo "cyan" "   Tauri project created successfully"
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

    # Use uSCRIPT venv for Python dependencies
    polaroid_echo "cyan" "🐍 Setting up Python dependencies in uSCRIPT venv..."

    if [[ -f "$UDOS_ROOT/uSCRIPT/activate-venv.sh" ]]; then
        polaroid_echo "lime" "✅ Found uSCRIPT virtual environment"

        # Activate venv and install missing packages
        (
            source "$UDOS_ROOT/uSCRIPT/activate-venv.sh" >/dev/null 2>&1

            # Check what we have vs what we need
            local missing_packages=()

            if ! python -c "import flask_socketio" >/dev/null 2>&1; then
                missing_packages+=("flask-socketio")
            fi

            if ! python -c "import psutil" >/dev/null 2>&1; then
                missing_packages+=("psutil")
            fi

            if ! python -c "import eventlet" >/dev/null 2>&1; then
                missing_packages+=("eventlet")
            fi

            if [[ ${#missing_packages[@]} -gt 0 ]]; then
                polaroid_echo "cyan" "   Installing missing packages: ${missing_packages[*]}"
                pip install "${missing_packages[@]}"
            else
                polaroid_echo "lime" "✅ All Python dependencies already installed"
            fi

            # Show final status
            polaroid_echo "cyan" "   Display system Python dependencies:"
            python -c "
import sys
packages = ['flask', 'flask_socketio', 'psutil', 'eventlet']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'   ✅ {pkg}')
    except ImportError:
        print(f'   ❌ {pkg}')
"
        )
    else
        polaroid_echo "yellow" "⚠️  uSCRIPT venv not found, falling back to global pip"
        pip3 install flask flask-socketio psutil eventlet 2>/dev/null || {
            polaroid_echo "yellow" "⚠️  Could not install Python dependencies globally"
            polaroid_echo "cyan" "   They will be installed when needed"
        }
    fi
}

build_desktop_app() {
    polaroid_echo "cyan" "🔨 Building desktop application..."

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
        "python"|"deps")
            # Install only Python dependencies using uSCRIPT venv
            polaroid_echo "cyan" "🐍 Installing Python dependencies in uSCRIPT venv..."
            setup_dependencies
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
            local has_python_deps=0

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

            # Check Python dependencies in uSCRIPT venv
            if [[ -f "$UDOS_ROOT/uSCRIPT/activate-venv.sh" ]]; then
                polaroid_echo "cyan" "🐍 Checking Python dependencies in uSCRIPT venv..."
                (
                    source "$UDOS_ROOT/uSCRIPT/activate-venv.sh" >/dev/null 2>&1
                    local missing=0

                    for pkg in flask flask_socketio psutil eventlet; do
                        if python -c "import $pkg" >/dev/null 2>&1; then
                            polaroid_echo "lime" "   ✅ $pkg"
                        else
                            polaroid_echo "orange" "   ❌ $pkg"
                            missing=1
                        fi
                    done

                    if [[ $missing -eq 0 ]]; then
                        has_python_deps=1
                    fi
                )
            else
                polaroid_echo "orange" "❌ uSCRIPT venv not found"
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
            if [[ $has_node -eq 1 && $has_rust -eq 1 && $has_python_deps -eq 1 && $has_tauri -eq 1 ]]; then
                polaroid_echo "lime" "🎉 Display system fully ready!"
            elif [[ $has_node -eq 1 && $has_rust -eq 1 && $has_python_deps -eq 1 ]]; then
                polaroid_echo "yellow" "⚠️  Display system ready, but desktop app needs building"
                polaroid_echo "cyan" "   Run: ./setup-display-system.sh build"
            else
                polaroid_echo "orange" "❌ Display system needs setup"
                polaroid_echo "cyan" "   Run: ./setup-display-system.sh setup"
                if [[ $has_python_deps -eq 0 ]]; then
                    polaroid_echo "cyan" "   Or just Python deps: ./setup-display-system.sh python"
                fi
            fi
            ;;
        "help"|"-h"|"--help")
            cat << EOF
🎯 uDOS v1.4 Display System Setup

Usage: $0 <command>

Commands:
  setup     Install Node.js, Rust, and set up Tauri project
  python    Install only Python dependencies in uSCRIPT venv
  build     Build the desktop application
  test      Test if display system is working
  help      Show this help

This sets up the three-mode display system:
  - CLI Terminal (always available)
  - Desktop Application (native Tauri app)
  - Web Export (browser interface)

The Python backend leverages the existing uSCRIPT virtual environment.
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
