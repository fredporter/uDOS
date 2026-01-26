#!/bin/bash
# ============================================================
# uDOS Installation Script
# ============================================================
# Alpha v1.0.3.0+
#
# Supports:
#   - Alpine Linux (APK packages)
#   - Linux (systemd, /opt/udos)
#   - macOS (LaunchAgent, /usr/local/udos)
#   - Development mode (in-place)
#
# Navigate to root directory if running from bin/
if [ "$(basename "$(pwd)")" = "bin" ]; then
    cd ..
fi
#
# Usage:
#   ./bin/install.sh                    # Interactive install
#   ./bin/install.sh --mode core        # Core only (TUI + API)
#   ./install.sh --mode desktop     # Core + Tauri
#   ./install.sh --mode wizard      # Full Wizard Server
#   ./install.sh --mode dev         # Development mode
#   ./install.sh --uninstall        # Remove installation
#
# ============================================================

set -e

VERSION="1.0.3.0"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd 2>/dev/null || echo "$SCRIPT_DIR")"

# shellcheck source=/dev/null
source "$SCRIPT_DIR/udos-common.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Print functions
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Detect platform
detect_platform() {
    case "$(uname -s)" in
        Linux)
            # Check for Alpine Linux
            if [ -f /etc/alpine-release ]; then
                echo "alpine"
                return
            fi
            if [ -f /etc/os-release ]; then
                if grep -qi "alpine" /etc/os-release 2>/dev/null; then
                    echo "alpine"
                    return
                fi
            fi
            if command -v apk &>/dev/null; then
                echo "alpine"
                return
            fi

            # Warn if TinyCore detected (deprecated)
            if [ -f /etc/os-release ]; then
                if grep -qi "tiny core" /etc/os-release 2>/dev/null; then
                    warn "TinyCore Linux detected. uDOS has migrated to Alpine Linux."
                    warn "Please consider migrating to Alpine Linux for continued support."
                fi
            fi
            if [ -d /home/tc ] && command -v tce-load &>/dev/null; then
                warn "TinyCore tools detected. uDOS has migrated to Alpine Linux."
            fi

            echo "linux"
            ;;
        Darwin)
            echo "macos"
            ;;
        MINGW*|CYGWIN*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

# Detect if running as root
is_root() {
    [ "$(id -u)" -eq 0 ]
}

# Get user home directory
get_user_home() {
    local platform="$1"
    if [ "$platform" = "alpine" ]; then
        # Alpine typically uses /root for root, /home/user for users
        echo "$HOME"
    else
        echo "$HOME"
    fi
}

# Print banner
print_banner() {
    echo ""
    echo -e "${CYAN}"
    echo "  ╔═══════════════════════════════════════╗"
    echo "  ║         uDOS Installation             ║"
    echo "  ║         Alpha v${VERSION}              ║"
    echo "  ╚═══════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print help
print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --mode MODE     Installation mode:"
    echo "                    core    - TUI + API (minimal)"
    echo "                    desktop - Core + Tauri app"
    echo "                    wizard  - Full Wizard Server"
    echo "                    dev     - Development mode (in-place)"
    echo ""
    echo "  --platform PLT  Override platform detection:"
    echo "                    alpine, linux, macos, windows"
    echo ""
    echo "  --prefix PATH   Installation prefix (default: /opt/udos or /usr/local/udos)"
    echo ""
    echo "  --uninstall     Remove uDOS installation"
    echo "  --help          Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --mode core              # Minimal install"
    echo "  $0 --mode desktop           # Desktop with Tauri"
    echo "  $0 --mode wizard            # Full Wizard Server"
    echo "  $0 --mode dev               # Development mode"
    echo ""
}

# Check Python
check_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
            success "Python $PYTHON_VERSION found"
            return 0
        else
            warn "Python 3.10+ required (found $PYTHON_VERSION)"
            return 1
        fi
    else
        error "Python 3 not found. Please install Python 3.10+"
    fi
}

# Check Node.js (for Tauri)
check_node() {
    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version 2>&1 | tr -d 'v')
        success "Node.js $NODE_VERSION found"
        return 0
    else
        warn "Node.js not found (required for Tauri desktop app)"
        return 1
    fi
}

# Check Rust (for Tauri)
check_rust() {
    if command -v cargo &>/dev/null; then
        RUST_VERSION=$(cargo --version 2>&1 | awk '{print $2}')
        success "Rust $RUST_VERSION found"
        return 0
    else
        warn "Rust not found (required for Tauri desktop app)"
        return 1
    fi
}

# Install for TinyCore
install_tinycore() {
    local mode="$1"
    info "Installing for TinyCore Linux..."

    # Check if TCZ builder exists
    if [ ! -f "$PROJECT_ROOT/distribution/tcz/build-core.sh" ]; then
        error "TCZ builder not found. Run from uDOS project root."
    fi

    info "Building TCZ package..."
    cd "$PROJECT_ROOT/distribution/tcz"
    ./build-core.sh "$VERSION"

    # Install TCZ
    if [ -f "udos-core.tcz" ]; then
        info "Installing TCZ..."
        tce-load -i udos-core.tcz
        success "uDOS Core TCZ installed"
    else
        error "TCZ build failed"
    fi

    # Setup user directory
    setup_user_directory "/home/tc"
}

# Install for Linux/macOS
install_unix() {
    local platform="$1"
    local mode="$2"
    local prefix="$3"

    info "Installing for $platform (mode: $mode)..."

    # Determine install prefix
    if [ -z "$prefix" ]; then
        if [ "$platform" = "macos" ]; then
            prefix="/usr/local/udos"
        else
            prefix="/opt/udos"
        fi
    fi

    # Create installation directory
    if is_root; then
        mkdir -p "$prefix"
    else
        if [ ! -d "$prefix" ]; then
            warn "Installation to $prefix requires root privileges"
            info "Installing in user space: ~/.local/udos"
            prefix="$HOME/.local/udos"
            mkdir -p "$prefix"
        fi
    fi

    # Copy core files
    info "Copying core files to $prefix..."
    cp -r "$PROJECT_ROOT/core" "$prefix/"
    cp -r "$PROJECT_ROOT/extensions" "$prefix/"
    cp -r "$PROJECT_ROOT/knowledge" "$prefix/"
    cp "$PROJECT_ROOT/requirements.txt" "$prefix/"
    cp "$PROJECT_ROOT/start_udos.sh" "$prefix/"
    chmod +x "$prefix/start_udos.sh"

    # Create Python venv
    info "Creating Python virtual environment..."
    python3 -m venv "$prefix/.venv"
    source "$prefix/.venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$prefix/requirements.txt"
    deactivate

    # Create launcher
    info "Creating launcher..."
    local launcher="/usr/local/bin/udos"
    if ! is_root; then
        launcher="$HOME/.local/bin/udos"
        mkdir -p "$HOME/.local/bin"
    fi

    cat > "$launcher" <<EOF
#!/bin/bash
# uDOS Launcher - v$VERSION
source "$prefix/.venv/bin/activate"
cd "$prefix"
python -m core.uDOS_main "\$@"
EOF
    chmod +x "$launcher"

    # Desktop mode: install Tauri
    if [ "$mode" = "desktop" ] || [ "$mode" = "wizard" ]; then
        if check_node && check_rust; then
            info "Building Tauri desktop app..."
            cd "$PROJECT_ROOT/app"
            npm install
            npm run tauri:build
            success "Tauri app built"
        else
            warn "Skipping Tauri build (missing Node.js or Rust)"
        fi
    fi

    # Wizard mode: additional setup
    if [ "$mode" = "wizard" ]; then
        info "Setting up Wizard Server..."
        cp -r "$PROJECT_ROOT/wizard" "$prefix/"

        # Create wizard library directories
        mkdir -p "$prefix/library/os-images"
        mkdir -p "$prefix/library/containers"
        mkdir -p "$prefix/library/packages"

        success "Wizard Server configured"
    fi

    # Setup user directory
    setup_user_directory "$(get_user_home "$platform")"

    success "uDOS installed to $prefix"
    info "Run 'udos' to start (ensure $launcher is in PATH)"
}

# Development mode
install_dev() {
    info "Setting up development mode..."

    # Just setup venv and user directory
    if [ ! -d "$PROJECT_ROOT/.venv" ]; then
        info "Creating Python virtual environment..."
        python3 -m venv "$PROJECT_ROOT/.venv"
    fi

    info "Installing Python dependencies..."
    source "$PROJECT_ROOT/.venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt"
    deactivate

    # Setup user directory
    setup_user_directory "$HOME"

    success "Development environment ready"
    info "Run: source .venv/bin/activate && ./start_udos.sh"
}

# Setup user directory structure
setup_user_directory() {
    local home="$1"
    local udos_home="$home/.udos"

    info "Setting up user directory: $udos_home"

    # Create directories with appropriate permissions
    mkdir -p "$udos_home/config"
    chmod 700 "$udos_home/config"

    mkdir -p "$udos_home/memory/sandbox/scripts"
    mkdir -p "$udos_home/memory/sandbox/workflows"
    mkdir -p "$udos_home/memory/knowledge"
    mkdir -p "$udos_home/memory/logs"
    mkdir -p "$udos_home/memory/.cache"
    mkdir -p "$udos_home/memory/.backups"
    chmod 755 "$udos_home/memory"

    mkdir -p "$udos_home/.credentials"
    chmod 700 "$udos_home/.credentials"

    # Create default config if not exists
    if [ ! -f "$udos_home/config/user.json" ]; then
        cat > "$udos_home/config/user.json" <<EOF
{
  "version": "$VERSION",
  "theme": "dungeon",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        chmod 600 "$udos_home/config/user.json"
    fi

    success "User directory configured: $udos_home"
}

# Uninstall
uninstall() {
    local platform="$1"
    info "Uninstalling uDOS..."

    warn "This will remove:"
    echo "  - /opt/udos (or /usr/local/udos)"
    echo "  - /usr/local/bin/udos launcher"
    echo ""
    echo "User data (~/.udos) will be preserved."
    echo ""
    read -p "Continue? (y/N) " confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        if is_root; then
            rm -rf /opt/udos /usr/local/udos
            rm -f /usr/local/bin/udos
        else
            rm -rf "$HOME/.local/udos"
            rm -f "$HOME/.local/bin/udos"
        fi
        success "uDOS uninstalled"
    else
        info "Uninstall cancelled"
    fi
}

# Main
main() {
    local mode="interactive"
    local platform=""
    local prefix=""
    local uninstall_flag=false

    # Parse arguments
    while [ $# -gt 0 ]; do
        case "$1" in
            --mode)
                mode="$2"
                shift 2
                ;;
            --platform)
                platform="$2"
                shift 2
                ;;
            --prefix)
                prefix="$2"
                shift 2
                ;;
            --uninstall)
                uninstall_flag=true
                shift
                ;;
            --help|-h)
                print_help
                exit 0
                ;;
            *)
                warn "Unknown option: $1"
                print_help
                exit 1
                ;;
        esac
    done

    print_banner

    # Detect platform if not specified
    if [ -z "$platform" ]; then
        platform=$(detect_platform)
    fi
    info "Platform: $platform"

    # Check Python
    check_python || exit 1

    # Dependency preflight before proceeding
    local tty_flag=0
    if [ -t 0 ] && [ -t 1 ]; then
        tty_flag=1
    fi
    UDOS_DEP_PYTHON_BIN="${UDOS_DEP_PYTHON_BIN:-python3}"
    if ! run_dependency_preflight "installer" "$tty_flag" 1; then
        error "Dependency preflight failed. Resolve the issues above and rerun install.sh"
    fi

    # Uninstall if requested
    if $uninstall_flag; then
        uninstall "$platform"
        exit 0
    fi

    # Interactive mode selection
    if [ "$mode" = "interactive" ]; then
        echo ""
        echo "Select installation mode:"
        echo "  1) core    - TUI + API (minimal, ~50MB)"
        echo "  2) desktop - Core + Tauri app (~200MB)"
        echo "  3) wizard  - Full Wizard Server (~500MB)"
        echo "  4) dev     - Development mode (in-place)"
        echo ""
        read -p "Choice [1-4]: " choice

        case "$choice" in
            1) mode="core" ;;
            2) mode="desktop" ;;
            3) mode="wizard" ;;
            4) mode="dev" ;;
            *) error "Invalid choice" ;;
        esac
    fi

    info "Installation mode: $mode"
    echo ""

    # Install based on platform and mode
    case "$platform" in
        tinycore)
            install_tinycore "$mode"
            ;;
        linux|macos)
            if [ "$mode" = "dev" ]; then
                install_dev
            else
                install_unix "$platform" "$mode" "$prefix"
            fi
            ;;
        windows)
            warn "Windows installation not yet implemented"
            info "Use WSL or development mode"
            ;;
        *)
            error "Unsupported platform: $platform"
            ;;
    esac

    echo ""
    success "Installation complete!"
    echo ""
}

main "$@"
