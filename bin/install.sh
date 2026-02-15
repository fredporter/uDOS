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
#   ./install.sh --mode desktop     # Desktop profile (under development)
#   ./install.sh --mode wizard      # Full Wizard Server
#   ./install.sh --mode dev         # Development mode
#   ./install.sh --uninstall        # Remove installation
#
# ============================================================

set -e

VERSION="1.0.3.0"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd 2>/dev/null || echo "$SCRIPT_DIR")"

# Bootstrap if running outside a repo (e.g., curl | bash)
if [ ! -f "$PROJECT_ROOT/uDOS.py" ]; then
    if [ "${UDOS_BOOTSTRAPPED:-0}" = "1" ]; then
        echo "[ERROR] Could not locate uDOS repo root (missing uDOS.py)." >&2
        echo "[ERROR] Set UDOS_REPO_URL to a valid repo or run from inside the repo." >&2
        exit 1
    fi

    if ! command -v git >/dev/null 2>&1; then
        echo "[ERROR] git is required to bootstrap the uDOS repository." >&2
        exit 1
    fi

    TARGET_DIR="${UDOS_HOME_ROOT:-$HOME/uDOS}"
    REPO_URL="${UDOS_REPO_URL:-https://github.com/fredporter/uDOS.git}"

    if [ ! -d "$TARGET_DIR/.git" ]; then
        echo "[BOOT] Cloning uDOS into $TARGET_DIR"
        git clone "$REPO_URL" "$TARGET_DIR"
    fi

    export UDOS_BOOTSTRAPPED=1
    exec "$TARGET_DIR/bin/install.sh" "$@"
fi

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
    echo "                    desktop - Core + Wizard web tooling (under development)"
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
    echo "  $0 --mode desktop           # Desktop profile (under development)"
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

# Install system dependencies for TUI (Ubuntu/Debian)
install_system_deps_ubuntu() {
    info "Checking system dependencies for TUI..."

    local missing_deps=()

    # Check for readline development libraries (required for proper arrow key support)
    if ! dpkg -l | grep -q libreadline-dev; then
        missing_deps+=("libreadline-dev")
    fi

    # Check for ncurses (required for terminal manipulation)
    if ! dpkg -l | grep -q libncurses5-dev; then
        missing_deps+=("libncurses5-dev")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        warn "Missing system dependencies: ${missing_deps[*]}"
        info "Installing system dependencies..."
        if is_root; then
            apt-get update -qq
            apt-get install -y "${missing_deps[@]}"
            success "System dependencies installed"
        else
            warn "Please install system dependencies manually:"
            echo "  sudo apt-get install ${missing_deps[*]}"
            return 1
        fi
    else
        success "All system dependencies installed"
    fi
    return 0
}

# Check Node.js (for optional web tooling)
check_node() {
    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version 2>&1 | tr -d 'v')
        success "Node.js $NODE_VERSION found"
        return 0
    else
        warn "Node.js not found (optional for web tooling)"
        return 1
    fi
}

# Check Rust (legacy desktop tooling)
check_rust() {
    if command -v cargo &>/dev/null; then
        RUST_VERSION=$(cargo --version 2>&1 | awk '{print $2}')
        success "Rust $RUST_VERSION found"
        return 0
    else
        warn "Rust not found (optional for legacy desktop tooling)"
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

    # Install system dependencies for Ubuntu/Debian
    if [ "$platform" = "linux" ]; then
        if command -v apt-get &>/dev/null; then
            install_system_deps_ubuntu || warn "Some system dependencies may be missing"
        fi
    fi

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
    mkdir -p "$prefix/bin"
    cp "$PROJECT_ROOT/bin/ucli" "$prefix/bin/"
    cp "$PROJECT_ROOT/bin/udos-common.sh" "$prefix/bin/"
    cp "$PROJECT_ROOT/bin/udos-self-heal.sh" "$prefix/bin/"
    chmod +x "$prefix/bin/ucli"

    # Create Python venv
    info "Creating Python virtual environment..."
    python3 -m venv "$prefix/venv"
    source "$prefix/venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$prefix/requirements.txt"
    deactivate

    # Create launcher
    info "Creating launcher..."
    local launcher="/usr/local/bin/ucli"
    if ! is_root; then
        launcher="$HOME/.local/bin/ucli"
        mkdir -p "$HOME/.local/bin"
    fi

    cat > "$launcher" <<EOF
#!/bin/bash
# uCLI Launcher - v$VERSION
source "$prefix/venv/bin/activate"
cd "$prefix"
exec "$prefix/bin/ucli" "\$@"
EOF
    chmod +x "$launcher"

    # Desktop profile remains reserved while Wizard web rendering/web view matures.
    if [ "$mode" = "desktop" ]; then
        info "Desktop profile is under development (future Wizard web view/rendering capabilities)."
    fi

    # Build TypeScript runtime if Node.js is available
    if command -v node &>/dev/null && command -v npm &>/dev/null; then
        info "Building TypeScript runtime..."
        cd "$PROJECT_ROOT"
        if bash core/tools/build_ts_runtime.sh; then
            success "TypeScript runtime built"
        else
            warn "TypeScript runtime build failed (non-fatal)"
        fi
    else
        warn "Skipping TypeScript runtime build (Node.js/npm not found)"
        info "Run 'bash core/tools/build_ts_runtime.sh' after installing Node.js"
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
    info "Run 'ucli' to start (ensure $launcher is in PATH)"

    if [ "${UDOS_AUTOSTART:-0}" = "1" ]; then
        info "Auto-starting uDOS..."
        "$prefix/bin/ucli" core
    fi
}

# Development mode
install_dev() {
    info "Setting up development mode..."

    # Just setup venv and user directory
    if [ ! -d "$PROJECT_ROOT/venv" ]; then
        info "Creating Python virtual environment..."
        python3 -m venv "$PROJECT_ROOT/venv"
    fi

    info "Installing Python dependencies..."
    source "$PROJECT_ROOT/venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_ROOT/requirements.txt"
    deactivate

    # Setup user directory
    setup_user_directory "$HOME"

    success "Development environment ready"
    info "Run: source venv/bin/activate && ./bin/ucli"

    if [ "${UDOS_AUTOSTART:-0}" = "1" ]; then
        info "Auto-starting uDOS..."
        "${PROJECT_ROOT}/bin/ucli" core
    fi
}

# Setup user directory structure
setup_user_directory() {
    local home="$1"
    local udos_home="$home/.udos"

    info "Setting up user directory: $udos_home"

    # Create directories with appropriate permissions
    mkdir -p "$udos_home/config"
    chmod 700 "$udos_home/config"

    mkdir -p "$udos_home/memory/inbox"
    mkdir -p "$udos_home/memory/sandbox"
    mkdir -p "$udos_home/memory/sandbox/binders"
    mkdir -p "$udos_home/memory/sandbox/workflows"
    mkdir -p "$udos_home/memory/sandbox/processed"
    mkdir -p "$udos_home/memory/bank/scripts"
    mkdir -p "$udos_home/memory/knowledge"
    mkdir -p "$udos_home/memory/logs"
    mkdir -p "$udos_home/memory/logs/monitoring"
    mkdir -p "$udos_home/memory/logs/quotas"
    mkdir -p "$udos_home/memory/.cache"
    mkdir -p "$udos_home/memory/.backups"
    chmod 755 "$udos_home/memory"

    # Provide ~/memory convenience link for logs/workspace
    if [ ! -e "$home/memory" ]; then
        ln -s "$udos_home/memory" "$home/memory" 2>/dev/null || true
    fi

    mkdir -p "$udos_home/.credentials"
    chmod 700 "$udos_home/.credentials"

    # Create bank directory structure for seed data
    mkdir -p "$udos_home/memory/bank/locations"
    mkdir -p "$udos_home/memory/bank/help"
    mkdir -p "$udos_home/memory/bank/templates"
    mkdir -p "$udos_home/memory/bank/graphics/diagrams/templates"
    mkdir -p "$udos_home/memory/bank/system"
    mkdir -p "$udos_home/memory/bank/workflows"
    chmod 755 "$udos_home/memory/bank"

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
    echo "  - /usr/local/bin/ucli launcher"
    echo ""
    echo "User data (~/.udos) will be preserved."
    echo ""
    read -p "Continue? (y/N) " confirm

    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        if is_root; then
            rm -rf /opt/udos /usr/local/udos
            rm -f /usr/local/bin/ucli
        else
            rm -rf "$HOME/.local/udos"
            rm -f "$HOME/.local/bin/ucli"
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
        echo "  2) desktop - Core + Wizard web tooling (under development)"
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
