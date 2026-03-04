#!/usr/bin/env bash

# ============================================================
# uDOS Installation & Setup Script
# ============================================================
# Cross-platform installer for macOS and Linux
# Handles: OS detection, dependencies, .env setup, Dev Mode tooling,
#          v1.5 logic-assist preparation, optional TUI build, wizard lazy-loading, and more.
#
# Usage:
#   ./bin/install-udos-vibe.sh           # Full install
#   ./bin/install-udos-vibe.sh --core    # Core only (no wizard)
#   ./bin/install-udos-vibe.sh --wizard  # Add wizard to existing
#   ./bin/install-udos-vibe.sh --update  # Update existing install
# ============================================================

set -euo pipefail
export UV_PROJECT_ENVIRONMENT=.venv

# ── Colors & Output ──────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

function banner() {
    echo -e "${BOLD}${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║                 uDOS Installation Setup                   ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

function error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

function info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

function success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

function warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

function step() {
    echo -e "${MAGENTA}[→]${NC} ${BOLD}$1${NC}"
}

function prompt() {
    echo -e "${CYAN}[?]${NC} $1"
}

# ── Global Variables ─────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TINYCORE_INSTALLER="${REPO_ROOT}/distribution/installer.sh"
INSTALL_MODE="full"
UPDATE_MODE=false
CORE_ONLY=false
WIZARD_ONLY=false
REQUESTED_TIER="auto"
PREFLIGHT_JSON=false
PROFILE_SELECTION=""
SELECTED_PROFILES_CSV=""
SELECTED_TINYCORE_TIER="core"
SELECTED_PACKAGE_GROUPS=""
SELECTED_PROFILE_EXTENSIONS=""

OS_TYPE=""
OS_VERSION=""
KERNEL_VERSION=""
CPU_ARCH=""
CPU_CORES=""
TOTAL_RAM_GB=""
FREE_STORAGE_GB=""
HAS_GPU=false
GPU_VRAM_GB=0
INSTALL_TIER="tier1"
LOCAL_MODELS_ALLOWED=false
AUTO_TIER_RESULT="tier1"
LOCAL_MODEL_BLOCK_REASON="none"
LOCAL_MODEL_REMEDIATION="none"
LOGIC_ASSIST_RECOMMENDED_MODELS=""

VIBE_CLI_INSTALLED=false
UV_INSTALLED=false
MICRO_INSTALLED=false
OBSIDIAN_INSTALLED=false

# ── Installer Dispatch (Host vs TinyCore) ───────────────────
function maybe_dispatch_to_tinycore_installer() {
    local wants_tinycore=false
    local forwarded=()
    for arg in "$@"; do
        if [[ "$arg" == "--preflight-json" ]]; then
            return 0
        fi
        case "$arg" in
            --tinycore|--tier|--tier=*|-t|--packages|--packages=*|-p|--from|--from=*|-f|--yes|-y|--dry-run)
                wants_tinycore=true
                ;;
        esac
        if [[ "$arg" != "--tinycore" ]]; then
            forwarded+=("$arg")
        fi
    done

    if [[ "$wants_tinycore" == false ]]; then
        return 0
    fi

    if [[ ! -f "$TINYCORE_INSTALLER" ]]; then
        error "TinyCore installer not found: $TINYCORE_INSTALLER"
        exit 1
    fi

    info "Routing install request to TinyCore adapter: distribution/installer.sh"
    exec sh "$TINYCORE_INSTALLER" "${forwarded[@]}"
}

maybe_dispatch_to_tinycore_installer "$@"

# ── Parse Arguments ──────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --tinycore)
            # Handled by dispatch above; keep parser tolerant.
            shift
            ;;
        --core)
            CORE_ONLY=true
            INSTALL_MODE="core"
            shift
            ;;
        --wizard)
            WIZARD_ONLY=true
            INSTALL_MODE="wizard"
            shift
            ;;
        --update)
            UPDATE_MODE=true
            shift
            ;;
        --preflight-json)
            PREFLIGHT_JSON=true
            shift
            ;;
        --profile|--profiles)
            PROFILE_SELECTION="${2:-}"
            if [[ -z "${2:-}" ]]; then
                error "--profile requires a comma-separated value"
                exit 1
            fi
            shift 2
            ;;
        --profile=*|--profiles=*)
            PROFILE_SELECTION="${1#*=}"
            shift
            ;;
        --tier)
            REQUESTED_TIER="${2:-auto}"
            if [[ -z "${2:-}" ]]; then
                error "--tier requires a value: auto | 1 | 2 | 3"
                exit 1
            fi
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --core         Install core components only (no wizard)"
            echo "  --wizard       Install wizard components only (assumes core exists)"
            echo "  --update       Update existing installation"
            echo "  --profile      Certified profiles: core,home,creator,gaming,dev"
            echo "  --tinycore     Route to TinyCore package installer (distribution/installer.sh)"
            echo "  --tier         Runtime tier: auto | 1 | 2 | 3"
            echo "  --preflight-json  Print capability/tier decision as JSON and exit"
            echo "  --help, -h     Show this help message"
            echo ""
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

function _default_profile_selection() {
    if [[ "$WIZARD_ONLY" == true ]]; then
        echo "home"
        return
    fi
    if [[ "$CORE_ONLY" == true ]]; then
        echo "core"
        return
    fi
    echo "core,home"
}

function _profile_selected() {
    local needle="$1"
    [[ ",$SELECTED_PROFILES_CSV," == *",$needle,"* ]]
}

function select_certified_profiles() {
    local requested="${PROFILE_SELECTION:-$(_default_profile_selection)}"
    local resolved="$requested"

    if command -v uv >/dev/null 2>&1; then
        resolved="$(UDOS_ROOT="$REPO_ROOT" UV_PROJECT_ENVIRONMENT=.venv uv run python -m core.services.release_profile_cli resolved --repo-root "$REPO_ROOT" --profiles "$requested" 2>/dev/null || printf '%s' "$requested")"
        SELECTED_TINYCORE_TIER="$(UDOS_ROOT="$REPO_ROOT" UV_PROJECT_ENVIRONMENT=.venv uv run python -m core.services.release_profile_cli tier --repo-root "$REPO_ROOT" --profiles "$resolved" 2>/dev/null || printf 'core')"
        SELECTED_PACKAGE_GROUPS="$(UDOS_ROOT="$REPO_ROOT" UV_PROJECT_ENVIRONMENT=.venv uv run python -m core.services.release_profile_cli packages --repo-root "$REPO_ROOT" --profiles "$resolved" 2>/dev/null || true)"
        SELECTED_PROFILE_EXTENSIONS="$(UDOS_ROOT="$REPO_ROOT" UV_PROJECT_ENVIRONMENT=.venv uv run python -m core.services.release_profile_cli extensions --repo-root "$REPO_ROOT" --profiles "$resolved" 2>/dev/null || true)"
    fi

    SELECTED_PROFILES_CSV="$resolved"
    info "Certified profiles: $SELECTED_PROFILES_CSV"
    info "Package groups: ${SELECTED_PACKAGE_GROUPS:-utilities}"
    info "Official extensions: ${SELECTED_PROFILE_EXTENSIONS:-none}"
}

function sync_certified_profiles() {
    if [[ -z "$SELECTED_PROFILES_CSV" ]]; then
        return
    fi
    if command -v uv >/dev/null 2>&1; then
        UDOS_ROOT="$REPO_ROOT" UV_PROJECT_ENVIRONMENT=.venv uv run python -m core.services.release_profile_cli install --repo-root "$REPO_ROOT" --profiles "$SELECTED_PROFILES_CSV" >/dev/null 2>&1 || warning "Could not persist certified profile state"
        return
    fi
    mkdir -p "$REPO_ROOT/memory/ucode"
    cat > "$REPO_ROOT/memory/ucode/release-profiles.json" <<EOF
{
  "enabled": ["$(printf '%s' "$SELECTED_PROFILES_CSV" | sed 's/,/","/g')"],
  "installed": ["$(printf '%s' "$SELECTED_PROFILES_CSV" | sed 's/,/","/g')"]
}
EOF
}

# ── OS Detection ─────────────────────────────────────────────
function detect_os() {
    step "Detecting operating system and hardware..."

    local platform=$(uname -s)
    CPU_ARCH=$(uname -m)
    KERNEL_VERSION=$(uname -r)

    if [[ "$platform" == "Darwin" ]]; then
        OS_TYPE="mac"
        OS_VERSION=$(sw_vers -productVersion)
        CPU_CORES=$(sysctl -n hw.ncpu)
        TOTAL_RAM_GB=$(awk -v b="$(sysctl -n hw.memsize)" 'BEGIN{printf "%d", b/1073741824}')
        FREE_STORAGE_GB=$(df -Pk "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1048576}')

        # Check for GPU (basic check)
        if system_profiler SPDisplaysDataType 2>/dev/null | grep -q "Metal"; then
            HAS_GPU=true
        fi

    elif [[ "$platform" == "Linux" ]]; then
        if [[ -f /etc/os-release ]]; then
            source /etc/os-release
            if [[ "$ID" == "ubuntu" ]]; then
                OS_TYPE="ubuntu"
            elif [[ "$ID" == "alpine" ]]; then
                OS_TYPE="alpine"
            else
                OS_TYPE="linux"
            fi
            OS_VERSION="${VERSION_ID:-unknown}"
        else
            OS_TYPE="linux"
            OS_VERSION="unknown"
        fi

        CPU_CORES=$(nproc 2>/dev/null || echo "unknown")
        TOTAL_RAM_GB=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "unknown")
        FREE_STORAGE_GB=$(df -Pk "$REPO_ROOT" | awk 'NR==2 {printf "%d", $4/1048576}')

        # Check for NVIDIA GPU
        if command -v nvidia-smi &> /dev/null; then
            HAS_GPU=true
        fi

    else
        error "Unsupported operating system: $platform"
        error "This installer supports macOS and Linux only"
        exit 1
    fi

    _apply_probe_overrides
    if [[ "$(_as_int_or_zero "$GPU_VRAM_GB")" -le 0 ]]; then
        GPU_VRAM_GB="$(_probe_gpu_vram_gb)"
    fi

    info "$OS_TYPE $OS_VERSION detected"
    info "Architecture: $CPU_ARCH"
    info "CPU Cores: $CPU_CORES"
    info "RAM: ${TOTAL_RAM_GB}GB"
    info "Free Storage: ${FREE_STORAGE_GB}GB"
    if [[ "$HAS_GPU" == true ]]; then
        info "GPU: Detected"
    else
        info "GPU: Not detected"
    fi
    if [[ "$HAS_GPU" == true ]]; then
        info "GPU VRAM: ${GPU_VRAM_GB}GB"
    fi
}

function _as_int_or_zero() {
    local raw="${1:-0}"
    if [[ "$raw" =~ ^[0-9]+$ ]]; then
        echo "$raw"
    else
        echo "0"
    fi
}

function _mac_version_supported() {
    local major minor
    major="$(echo "$OS_VERSION" | awk -F. '{print $1}')"
    minor="$(echo "$OS_VERSION" | awk -F. '{print $2}')"
    major="$(_as_int_or_zero "$major")"
    minor="$(_as_int_or_zero "$minor")"
    [[ "$major" -gt 10 ]] || [[ "$major" -eq 10 && "$minor" -ge 15 ]]
}

function _linux_kernel_supported() {
    local major
    major="$(echo "$KERNEL_VERSION" | awk -F. '{print $1}')"
    major="$(_as_int_or_zero "$major")"
    [[ "$major" -ge 4 ]]
}

function _tier_level() {
    case "$1" in
        tier3|3) echo "3" ;;
        tier2|2) echo "2" ;;
        *) echo "1" ;;
    esac
}

function _tier_name() {
    case "$1" in
        3|tier3) echo "tier3" ;;
        2|tier2) echo "tier2" ;;
        *) echo "tier1" ;;
    esac
}

function _to_lower() {
    printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

function _configure_tier() {
    local candidate="$1"
    INSTALL_TIER="$candidate"
    if [[ "$candidate" == "tier1" ]]; then
        LOCAL_MODELS_ALLOWED=false
    else
        LOCAL_MODELS_ALLOWED=true
    fi
}

function _logic_assist_tier_profile_csv() {
    case "$1" in
        tier2|2)
            echo "devstral-small-2,mistral,llama3.2,qwen3"
            ;;
        tier3|3)
            echo "mistral,devstral-small-2,llama3.2,qwen3,codellama,phi3,gemma2,deepseek-coder"
            ;;
        *)
            echo ""
            ;;
    esac
}

function _json_array_from_csv() {
    local csv="${1:-}"
    local out="["
    local first=1
    local item
    local IFS=','
    for item in $csv; do
        item="$(printf '%s' "$item" | sed 's/^ *//;s/ *$//')"
        if [[ -z "$item" ]]; then
            continue
        fi
        if [[ "$first" -eq 0 ]]; then
            out="${out}, "
        fi
        out="${out}\"${item}\""
        first=0
    done
    out="${out}]"
    echo "$out"
}

function _bool_to_json() {
    if [[ "$1" == true ]]; then
        echo "true"
    else
        echo "false"
    fi
}

function _truthy_env() {
    local value
    value="$(_to_lower "${1:-}")"
    [[ "$value" == "1" || "$value" == "true" || "$value" == "yes" || "$value" == "y" ]]
}

function _probe_gpu_vram_gb() {
    if [[ "$HAS_GPU" != true ]]; then
        echo "0"
        return
    fi

    if [[ "$OS_TYPE" == "mac" ]]; then
        local vram_text
        vram_text=$(system_profiler SPDisplaysDataType 2>/dev/null | awk -F': ' '/VRAM \(Total\)|VRAM/{print $2; exit}' || true)
        if [[ -z "$vram_text" ]]; then
            echo "0"
            return
        fi
        local number unit
        number=$(echo "$vram_text" | grep -Eo '[0-9]+' | head -n1 || echo "0")
        unit=$(_to_lower "$(echo "$vram_text" | grep -Eo 'GB|MB' | head -n1 || true)")
        number="$(_as_int_or_zero "$number")"
        if [[ "$unit" == "mb" ]]; then
            echo $((number / 1024))
        else
            echo "$number"
        fi
        return
    fi

    if command -v nvidia-smi &> /dev/null; then
        local vram_mb
        vram_mb=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -n1 || echo "0")
        vram_mb="$(_as_int_or_zero "$vram_mb")"
        echo $((vram_mb / 1024))
        return
    fi

    echo "0"
}

function _apply_probe_overrides() {
    if [[ -n "${UDOS_INSTALLER_PROBE_OS_TYPE:-}" ]]; then
        OS_TYPE="${UDOS_INSTALLER_PROBE_OS_TYPE}"
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_OS_VERSION:-}" ]]; then
        OS_VERSION="${UDOS_INSTALLER_PROBE_OS_VERSION}"
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_KERNEL_VERSION:-}" ]]; then
        KERNEL_VERSION="${UDOS_INSTALLER_PROBE_KERNEL_VERSION}"
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_CPU_ARCH:-}" ]]; then
        CPU_ARCH="${UDOS_INSTALLER_PROBE_CPU_ARCH}"
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_CPU_CORES:-}" ]]; then
        CPU_CORES="${UDOS_INSTALLER_PROBE_CPU_CORES}"
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_RAM_GB:-}" ]]; then
        TOTAL_RAM_GB="${UDOS_INSTALLER_PROBE_RAM_GB}"
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_FREE_STORAGE_GB:-}" ]]; then
        FREE_STORAGE_GB="${UDOS_INSTALLER_PROBE_FREE_STORAGE_GB}"
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_HAS_GPU:-}" ]]; then
        if _truthy_env "${UDOS_INSTALLER_PROBE_HAS_GPU}"; then
            HAS_GPU=true
        else
            HAS_GPU=false
        fi
    fi
    if [[ -n "${UDOS_INSTALLER_PROBE_GPU_VRAM_GB:-}" ]]; then
        GPU_VRAM_GB="${UDOS_INSTALLER_PROBE_GPU_VRAM_GB}"
    fi
}

function emit_preflight_json() {
    cat <<EOF
{
  "os_type": "$OS_TYPE",
  "os_version": "$OS_VERSION",
  "kernel_version": "$KERNEL_VERSION",
  "cpu_arch": "$CPU_ARCH",
  "cpu_cores": $(_as_int_or_zero "$CPU_CORES"),
  "ram_gb": $(_as_int_or_zero "$TOTAL_RAM_GB"),
  "storage_free_gb": $(_as_int_or_zero "$FREE_STORAGE_GB"),
  "has_gpu": $(_bool_to_json "$HAS_GPU"),
  "gpu_vram_gb": $(_as_int_or_zero "$GPU_VRAM_GB"),
  "requested_tier": "$REQUESTED_TIER",
  "auto_tier": "$AUTO_TIER_RESULT",
  "selected_tier": "$INSTALL_TIER",
  "local_models_allowed": $(_bool_to_json "$LOCAL_MODELS_ALLOWED"),
  "logic_assist_recommended_models": $(_json_array_from_csv "$LOGIC_ASSIST_RECOMMENDED_MODELS"),
  "block_reason": "$LOCAL_MODEL_BLOCK_REASON",
  "remediation": "$LOCAL_MODEL_REMEDIATION"
}
EOF
}

function evaluate_install_tier() {
    step "Running preflight capability assessment..."

    local cores ram storage gpu_vram
    cores="$(_as_int_or_zero "$CPU_CORES")"
    ram="$(_as_int_or_zero "$TOTAL_RAM_GB")"
    storage="$(_as_int_or_zero "$FREE_STORAGE_GB")"
    gpu_vram="$(_as_int_or_zero "$GPU_VRAM_GB")"

    local os_allows_local=true
    if [[ "$OS_TYPE" == "mac" ]]; then
        if ! _mac_version_supported; then
            os_allows_local=false
            warning "macOS $OS_VERSION is below 10.15; local-model path disabled."
        fi
    elif [[ "$OS_TYPE" == "linux" || "$OS_TYPE" == "ubuntu" || "$OS_TYPE" == "alpine" ]]; then
        if ! _linux_kernel_supported; then
            os_allows_local=false
            warning "Linux kernel $KERNEL_VERSION is below 4.x; local-model path disabled."
        fi
    fi

    local auto_tier="tier1"
    if [[ "$os_allows_local" == true && "$ram" -ge 16 && "$cores" -ge 8 && "$storage" -ge 50 && "$HAS_GPU" == true && "$gpu_vram" -ge 8 ]]; then
        auto_tier="tier3"
    elif [[ "$os_allows_local" == true && "$ram" -ge 8 && "$cores" -ge 4 && "$storage" -ge 10 ]]; then
        auto_tier="tier2"
    fi
    AUTO_TIER_RESULT="$auto_tier"

    local requested
    requested="$(_to_lower "$REQUESTED_TIER")"
    local selected="$auto_tier"
    if [[ "$requested" != "auto" ]]; then
        if [[ ! "$requested" =~ ^[123]$ ]]; then
            error "Invalid --tier value: $REQUESTED_TIER (expected auto|1|2|3)"
            exit 1
        fi
        selected="$(_tier_name "$requested")"
    fi

    local meets_tier2_min=false
    if [[ "$ram" -ge 8 && "$cores" -ge 4 && "$storage" -ge 10 ]]; then
        meets_tier2_min=true
    fi
    local meets_tier3_min=false
    if [[ "$ram" -ge 16 && "$cores" -ge 8 && "$storage" -ge 50 && "$HAS_GPU" == true && "$gpu_vram" -ge 8 ]]; then
        meets_tier3_min=true
    fi

    if [[ "$os_allows_local" == false && "$selected" != "tier1" ]]; then
        warning "Requested local-model tier is unsupported on this OS/kernel; forcing tier1."
        warning "Remediation: upgrade to macOS 10.15+ or Linux kernel 4.x+."
        LOCAL_MODEL_BLOCK_REASON="legacy_platform"
        LOCAL_MODEL_REMEDIATION="upgrade_os_or_kernel_for_local_models"
        selected="tier1"
    fi

    if [[ "$selected" == "tier2" && "$meets_tier2_min" != true ]]; then
        warning "Tier2 local-model requirements not met (need >=4 cores, >=8GB RAM, >=10GB free). Forcing tier1."
        warning "Remediation: free storage and use a host with >=4 cores and >=8GB RAM."
        LOCAL_MODEL_BLOCK_REASON="insufficient_resources"
        LOCAL_MODEL_REMEDIATION="require_4_cores_8gb_ram_10gb_storage_for_tier2"
        selected="tier1"
    fi

    if [[ "$selected" == "tier3" && "$meets_tier3_min" != true ]]; then
        warning "Tier3 local-model requirements not met (need >=8 cores, >=16GB RAM, >=50GB free, GPU >=8GB VRAM)."
        warning "Remediation: use Tier2 on this machine or add GPU/VRAM and resources for Tier3."
        LOCAL_MODEL_BLOCK_REASON="insufficient_resources"
        LOCAL_MODEL_REMEDIATION="require_8_cores_16gb_ram_50gb_storage_gpu_8gb_vram_for_tier3"
        if [[ "$meets_tier2_min" == true ]]; then
            selected="tier2"
        else
            selected="tier1"
        fi
    fi

    if [[ "$(_tier_level "$selected")" -gt "$(_tier_level "$auto_tier")" ]]; then
        warning "Requested tier exceeds detected capabilities; downgrading to $auto_tier."
        if [[ "$auto_tier" == "tier1" ]]; then
            LOCAL_MODEL_BLOCK_REASON="insufficient_resources"
            LOCAL_MODEL_REMEDIATION="tier_forced_to_cloud_only_due_to_detected_limits"
        fi
        selected="$auto_tier"
    fi

    _configure_tier "$selected"
    LOGIC_ASSIST_RECOMMENDED_MODELS="$(_logic_assist_tier_profile_csv "$INSTALL_TIER")"

    info "Selected install tier: $INSTALL_TIER (requested: $REQUESTED_TIER, auto-detected: $auto_tier)"
    case "$INSTALL_TIER" in
        tier1)
            info "Tier1 profile: offline-first core plus Wizard review; local GPT4All setup disabled."
            ;;
        tier2)
            info "Tier2 profile: eligible for GPT4All local assist with smaller models and Wizard escalation."
            ;;
        tier3)
            info "Tier3 profile: eligible for larger GPT4All local assist models with Wizard escalation."
            ;;
    esac

    if [[ "$ram" -lt 4 || "$cores" -lt 2 || "$storage" -lt 5 ]]; then
        warning "System is below recommended minimum baseline (2 cores / 4GB RAM / 5GB free)."
        warning "Installer will continue, but expect reduced performance and use cloud/offline fallback mode."
    fi
}

# ── Check Dependencies ───────────────────────────────────────
function check_required_commands() {
    step "Checking required system commands..."

    local missing=()

    # Essential tools
    for cmd in curl git; do
        if ! command -v $cmd &> /dev/null; then
            missing+=($cmd)
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing required commands: ${missing[*]}"
        error "Please install them first:"
        if [[ "$OS_TYPE" == "mac" ]]; then
            error "  brew install ${missing[*]}"
        elif [[ "$OS_TYPE" == "ubuntu" ]]; then
            error "  sudo apt-get install ${missing[*]}"
        elif [[ "$OS_TYPE" == "alpine" ]]; then
            error "  apk add ${missing[*]}"
        fi
        exit 1
    fi

    success "Required commands present"
}

# ── Install uv ───────────────────────────────────────────────
function install_uv() {
    if command -v uv &> /dev/null; then
        UV_INSTALLED=true
        info "uv already installed: $(uv --version)"
        return
    fi

    step "Installing uv (Python package manager)..."

    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        success "uv installed successfully"
        export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"
        UV_INSTALLED=true
    else
        error "Failed to install uv"
        exit 1
    fi
}

# ── Install micro editor ─────────────────────────────────────
function install_micro() {
    if command -v micro &> /dev/null; then
        MICRO_INSTALLED=true
        info "micro editor already installed"
        return
    fi

    prompt "Install micro text editor for TUI editing? (recommended) [Y/n]"
    read -r response
    if [[ "$response" =~ ^[Nn] ]]; then
        warning "Skipping micro installation"
        return
    fi

    step "Installing micro editor..."

    if [[ "$OS_TYPE" == "mac" ]]; then
        if command -v brew &> /dev/null; then
            brew install micro
        else
            curl https://getmic.ro | bash
            sudo mv micro /usr/local/bin/
        fi
    else
        curl https://getmic.ro | bash
        sudo mv micro /usr/local/bin/ 2>/dev/null || mv micro ~/.local/bin/
    fi

    if command -v micro &> /dev/null; then
        MICRO_INSTALLED=true
        success "micro editor installed"
    else
        warning "micro installation failed (non-critical)"
    fi
}

# ── Check Obsidian ───────────────────────────────────────────
function check_obsidian() {
    step "Checking for Obsidian..."

    if [[ "$OS_TYPE" == "mac" ]]; then
        if [[ -d "/Applications/Obsidian.app" ]]; then
            OBSIDIAN_INSTALLED=true
            success "Obsidian found"
        else
            warning "Obsidian not found"
            prompt "Install Obsidian? (recommended for vault management) [Y/n]"
            read -r response
            if [[ ! "$response" =~ ^[Nn] ]]; then
                info "Opening Obsidian download page..."
                open "https://obsidian.md/download"
                info "Please install Obsidian and re-run this installer"
            fi
        fi
    elif [[ "$OS_TYPE" == "ubuntu" ]]; then
        if command -v obsidian &> /dev/null || snap list obsidian &> /dev/null 2>&1; then
            OBSIDIAN_INSTALLED=true
            success "Obsidian found"
        else
            warning "Obsidian not found (optional but recommended)"
            info "Install with: snap install obsidian --classic"
        fi
    else
        info "Obsidian check skipped on $OS_TYPE"
    fi
}

function upsert_env_var() {
    local env_file="$1"
    local key="$2"
    local value="$3"
    if grep -q "^${key}=" "$env_file"; then
        sed -i.bak "s|^${key}=.*|${key}=${value}|g" "$env_file"
    else
        echo "${key}=${value}" >> "$env_file"
    fi
    rm -f "$env_file.bak"
}

function read_env_var() {
    local env_file="$1"
    local key="$2"
    local line
    line="$(grep -E "^${key}=" "$env_file" | tail -n1 || true)"
    if [[ -z "$line" ]]; then
        echo ""
        return
    fi
    local value="${line#*=}"
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
    echo "$value"
}

function timezone_city_default() {
    local tz_name="$1"
    case "$tz_name" in
        ""|"UTC"|"Etc/UTC"|"GMT")
            echo "Greenwich"
            return
            ;;
    esac
    local city="${tz_name##*/}"
    city="${city//_/ }"
    if [[ -z "$city" ]]; then
        echo "Greenwich"
    else
        echo "$city"
    fi
}

# ── Setup .env File ──────────────────────────────────────────
function setup_env_file() {
    step "Setting up environment configuration..."

    local env_file="$REPO_ROOT/.env"
    local env_example="$REPO_ROOT/.env.example"

    if [[ -f "$env_file" ]]; then
        warning ".env file already exists"
        prompt "Overwrite with fresh template? [y/N]"
        read -r response
        if [[ ! "$response" =~ ^[Yy] ]]; then
            info "Keeping existing .env file"
            return
        fi
    fi

    if [[ ! -f "$env_example" ]]; then
        error ".env.example not found!"
        exit 1
    fi

    # Copy template
    cp "$env_example" "$env_file"

    # Auto-detect and set values
    sed -i.bak "s|UDOS_ROOT=.*|UDOS_ROOT=$REPO_ROOT|g" "$env_file"
    sed -i.bak "s|UDOS_MEMORY_ROOT=.*|UDOS_MEMORY_ROOT=\${UDOS_ROOT}/memory|g" "$env_file"
    sed -i.bak "s|VAULT_ROOT=.*|VAULT_ROOT=\${UDOS_MEMORY_ROOT}/vault|g" "$env_file"
    sed -i.bak "s|VAULT_MD_ROOT=.*|VAULT_MD_ROOT=\${VAULT_ROOT}|g" "$env_file"
    sed -i.bak "s|OS_TYPE=.*|OS_TYPE=$OS_TYPE|g" "$env_file"
    rm -f "$env_file.bak"

    success ".env file created at $env_file"

    # Prompt for essential values
    echo ""
    prompt "Enter your username (leave empty for 'Ghost' mode):"
    read -r username
    if [[ -n "$username" ]]; then
        upsert_env_var "$env_file" "USER_NAME" "$username"
        # Canonical username key is USER_NAME; remove legacy alias to avoid drift.
        sed -i.bak '/^USER_USERNAME=/d' "$env_file"
        if [[ "$(_to_lower "$username")" != "ghost" ]]; then
            upsert_env_var "$env_file" "USER_ROLE" "user"
        fi
        rm -f "$env_file.bak"
    fi

    echo ""
    prompt "Enter your Mistral API key for Wizard network review (optional; leave blank for offline-first install):"
    read -r api_key
    if [[ -n "$api_key" ]]; then
        sed -i.bak "s|MISTRAL_API_KEY=.*|MISTRAL_API_KEY=$api_key|g" "$env_file"
        rm -f "$env_file.bak"
    fi

    upsert_env_var "$env_file" "VIBE_INSTALL_TIER" "$INSTALL_TIER"
    upsert_env_var "$env_file" "LOCAL_MODELS_ALLOWED" "$(if [[ "$LOCAL_MODELS_ALLOWED" == true ]]; then echo "1"; else echo "0"; fi)"
    upsert_env_var "$env_file" "UDOS_LOGIC_LOCAL_RUNTIME" "GPT4All"
    upsert_env_var "$env_file" "UDOS_LOGIC_INSTALL_TIER" "$INSTALL_TIER"
    upsert_env_var "$env_file" "UDOS_LOGIC_RECOMMENDED_MODELS" "$LOGIC_ASSIST_RECOMMENDED_MODELS"

    # Generate wizard admin token if needed
    if [[ "$INSTALL_MODE" != "core" ]]; then
        local wizard_token
        wizard_token=$(UV_PROJECT_ENVIRONMENT=.venv uv run python -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
        sed -i.bak "s|WIZARD_ADMIN_TOKEN=.*|WIZARD_ADMIN_TOKEN=$wizard_token|g" "$env_file"

        local wizard_key
        wizard_key=$(UV_PROJECT_ENVIRONMENT=.venv uv run python -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
        sed -i.bak "s|WIZARD_KEY=.*|WIZARD_KEY=$wizard_key|g" "$env_file"
        rm -f "$env_file.bak"
    fi

    success "Environment configured"
}

function enforce_env_policy() {
    local env_file="$REPO_ROOT/.env"
    if [[ ! -f "$env_file" ]]; then
        return
    fi

    local user_name user_legacy user_role
    user_name="$(read_env_var "$env_file" "USER_NAME")"
    user_legacy="$(read_env_var "$env_file" "USER_USERNAME")"
    if [[ -z "$user_name" && -n "$user_legacy" ]]; then
        upsert_env_var "$env_file" "USER_NAME" "$user_legacy"
        user_name="$user_legacy"
    fi
    sed -i.bak '/^USER_USERNAME=/d' "$env_file"
    rm -f "$env_file.bak"

    user_role="$(read_env_var "$env_file" "USER_ROLE")"
    if [[ -n "$user_name" && "$(_to_lower "$user_name")" != "ghost" ]]; then
        if [[ -z "$user_role" || "$(_to_lower "$user_role")" == "ghost" ]]; then
            upsert_env_var "$env_file" "USER_ROLE" "user"
        fi
    fi

    local mistral_key staging_key
    mistral_key="$(read_env_var "$env_file" "MISTRAL_API_KEY")"
    staging_key="$(read_env_var "$env_file" "STAGING_MISTRAL_API_KEY")"
    if [[ -z "$mistral_key" && -n "$staging_key" ]]; then
        upsert_env_var "$env_file" "MISTRAL_API_KEY" "$staging_key"
    fi
    sed -i.bak '/^STAGING_MISTRAL_API_KEY=/d' "$env_file"
    rm -f "$env_file.bak"

    local timezone_value tz_legacy
    timezone_value="$(read_env_var "$env_file" "UDOS_TIMEZONE")"
    tz_legacy="$(read_env_var "$env_file" "TZ")"
    if [[ -z "$timezone_value" ]]; then
        if [[ -n "$tz_legacy" ]]; then
            upsert_env_var "$env_file" "UDOS_TIMEZONE" "$tz_legacy"
            timezone_value="$tz_legacy"
        else
            upsert_env_var "$env_file" "UDOS_TIMEZONE" "UTC"
            timezone_value="UTC"
        fi
    fi
    sed -i.bak '/^TZ=/d' "$env_file"
    rm -f "$env_file.bak"

    local grid_code location_name
    grid_code="$(read_env_var "$env_file" "UDOS_LOCATION")"
    if [[ -z "$grid_code" ]]; then
        upsert_env_var "$env_file" "UDOS_LOCATION" "grid-code"
    fi

    location_name="$(read_env_var "$env_file" "UDOS_LOCATION_NAME")"
    if [[ -z "$location_name" ]]; then
        upsert_env_var "$env_file" "UDOS_LOCATION_NAME" "$(timezone_city_default "$timezone_value")"
    fi
}

function write_provider_hints() {
    local env_file="$REPO_ROOT/.env"
    local primary_hint="$1"
    local secondary_hint="$2"
    if [[ ! -f "$env_file" ]]; then
        return
    fi

    sed -i.bak '/^VIBE_PRIMARY_PROVIDER=/d' "$env_file"
    sed -i.bak '/^VIBE_SECONDARY_PROVIDER=/d' "$env_file"
    sed -i.bak '/^# VIBE_PRIMARY_PROVIDER=/d' "$env_file"
    sed -i.bak '/^# VIBE_SECONDARY_PROVIDER=/d' "$env_file"
    rm -f "$env_file.bak"

    {
        echo "# VIBE_PRIMARY_PROVIDER=${primary_hint}"
        echo "# VIBE_SECONDARY_PROVIDER=${secondary_hint}"
    } >> "$env_file"
}

function reconcile_user_identity_state() {
    local env_file="$REPO_ROOT/.env"
    if [[ ! -f "$env_file" ]]; then
        return
    fi

    # Keep runtime user state aligned with .env identity so startup doesn't stick in ghost mode.
    uv run python - "$REPO_ROOT" "$env_file" <<'PY' >/dev/null 2>&1 || true
import json
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
env_path = Path(sys.argv[2])

env_vars = {}
for raw in env_path.read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    env_vars[key.strip()] = value.strip().strip('"').strip("'")

memory_root = Path(env_vars.get("UDOS_MEMORY_ROOT") or (repo_root / "memory"))
private_dir = memory_root / "bank" / "private"
private_dir.mkdir(parents=True, exist_ok=True)
users_file = private_dir / "users.json"
current_file = private_dir / "current_user.txt"

username = (env_vars.get("USER_NAME") or "").strip().lower()
if not username or username == "ghost":
    raise SystemExit(0)

role = (env_vars.get("USER_ROLE") or "user").strip().lower()
if role not in {"admin", "user", "guest"}:
    role = "user"

if users_file.exists():
    try:
        payload = json.loads(users_file.read_text())
    except Exception:
        payload = {}
else:
    payload = {}

entry = payload.get(username) or {}
payload[username] = {
    "username": username,
    "role": role,
    "created": entry.get("created") or "installer",
    "last_login": "installer",
}
users_file.write_text(json.dumps(payload, indent=2) + "\n")
current_file.write_text(username)
PY
}

# ── Setup Vault Structure ────────────────────────────────────
function setup_vault_structure() {
    step "Setting up vault structure..."

    local env_file="$REPO_ROOT/.env"
    local memory_root vault_root
    memory_root="$(read_env_var "$env_file" "UDOS_MEMORY_ROOT")"
    vault_root="$(read_env_var "$env_file" "VAULT_ROOT")"
    if [[ -z "$memory_root" ]]; then
        memory_root="$REPO_ROOT/memory"
    fi
    if [[ -z "$vault_root" ]]; then
        vault_root="$memory_root/vault"
    fi

    # Create essential directories
    mkdir -p "$vault_root"
    mkdir -p "$memory_root/logs"
    mkdir -p "$REPO_ROOT/.vibe"

    # Copy vault template if it doesn't exist
    if [[ -d "$REPO_ROOT/vault" ]] && [[ ! -f "$vault_root/.vault-initialized" ]]; then
        info "Initializing vault from template..."
        cp -R "$REPO_ROOT/vault/"* "$vault_root/" 2>/dev/null || true
        touch "$vault_root/.vault-initialized"
    fi

    success "Vault structure ready"

    if [[ "$OBSIDIAN_INSTALLED" == true ]]; then
        prompt "Open vault in Obsidian? [Y/n]"
        read -r response
        if [[ ! "$response" =~ ^[Nn] ]]; then
            if [[ "$OS_TYPE" == "mac" ]]; then
                open -a Obsidian "$vault_root"
            fi
        fi
    fi
}

# ── Install Dev Mode Tooling ─────────────────────────────────
function install_vibe_cli() {
    step "Installing Dev Mode tooling (vibe)..."
    local vibe_install_url="${VIBE_INSTALL_URL:-https://mistral.ai/vibe/install.sh}"

    if command -v vibe &> /dev/null; then
        VIBE_CLI_INSTALLED=true
        local current_version=$(vibe --version 2>/dev/null | head -n1 || echo "unknown")
        info "Dev Mode tooling already installed: $current_version"

        if [[ "$UPDATE_MODE" == true ]]; then
            prompt "Update Dev Mode tooling? [Y/n]"
            read -r response
            if [[ ! "$response" =~ ^[Nn] ]]; then
                if curl -fsSL "$vibe_install_url" | sh; then
                    success "Dev Mode tooling updated"
                else
                    warning "Dev Mode tooling update skipped (installer URL unavailable or network/DNS issue)."
                fi
            fi
        fi
        return
    fi

    info "Installing vibe for Dev Mode using official installer..."
    if ! curl -fsSL "$vibe_install_url" | sh; then
        warning "Dev Mode tooling install skipped (installer URL unavailable or network/DNS issue)."
        warning "Set VIBE_INSTALL_URL to an alternate installer endpoint, or install vibe manually and rerun --update."
        VIBE_CLI_INSTALLED=false
        return
    fi

    if command -v vibe &> /dev/null; then
        VIBE_CLI_INSTALLED=true
        success "Dev Mode tooling installed successfully"
        vibe --version
    else
        warning "Dev Mode tooling installer completed but 'vibe' binary is not on PATH yet."
        warning "Continue setup now, then rerun with --update after confirming PATH."
        VIBE_CLI_INSTALLED=false
    fi
}

# ── Setup Vibe Integration ───────────────────────────────────
function setup_vibe_integration() {
    step "Setting up Dev Mode tooling bridge..."

    # Run the existing setup-vibe.sh script
    if [[ -f "$REPO_ROOT/bin/setup-vibe.sh" ]]; then
        bash "$REPO_ROOT/bin/setup-vibe.sh"
    else
        # Manual setup if script missing
        mkdir -p "$REPO_ROOT/.vibe"

        if [[ -d "$REPO_ROOT/vibe/core/tools/ucode" ]]; then
            rm -f "$REPO_ROOT/.vibe/tools"
            ln -s ../vibe/core/tools/ucode "$REPO_ROOT/.vibe/tools"
        fi

        if [[ -d "$REPO_ROOT/vibe/core/skills/ucode" ]]; then
            rm -f "$REPO_ROOT/.vibe/skills"
            ln -s ../vibe/core/skills/ucode "$REPO_ROOT/.vibe/skills"
        fi

        success "Dev Mode tooling bridge configured"
    fi

}

# ── Install Core Requirements ────────────────────────────────
function install_core_requirements() {
    step "Installing core Python requirements..."

    cd "$REPO_ROOT"

    if [[ -f "pyproject.toml" ]]; then
        info "Syncing uv environment (core profile: --extra udos, verbose progress)..."
        UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos --verbose
        success "Core requirements installed"
    else
        error "pyproject.toml not found!"
        exit 1
    fi
}

# ── Install Wizard Requirements (Lazy) ──────────────────────
function install_wizard_requirements() {
    if [[ "$CORE_ONLY" == true ]] || ! _profile_selected "home"; then
        info "Skipping wizard requirements (home profile not selected)"
        return
    fi

    step "Installing wizard requirements..."

    cd "$REPO_ROOT"

    # Install wizard profile (includes core via optional-dependency chain)
    UV_PROJECT_ENVIRONMENT=.venv uv sync --extra udos-wizard --verbose

    success "Wizard requirements installed"

    # Setup wizard config
    if [[ ! -f "$REPO_ROOT/wizard/config/.env" ]]; then
        if [[ -f "$REPO_ROOT/wizard/config/.env.example" ]]; then
            cp "$REPO_ROOT/wizard/config/.env.example" "$REPO_ROOT/wizard/config/.env"
            info "Wizard config template created"
        fi
    fi
}

function setup_logic_assist_runtime() {
    local env_file="$REPO_ROOT/.env"
    if [[ ! -f "$env_file" ]]; then
        return
    fi

    if ! _profile_selected "dev"; then
        info "Skipping local logic-assist tooling (dev profile not selected)"
        return
    fi

    if [[ "$LOCAL_MODELS_ALLOWED" != true ]]; then
        info "Skipping local logic-assist tooling (selected $INSTALL_TIER profile disables local GPT4All setup)"
        return
    fi

    step "Preparing v1.5 local logic-assist tooling..."
    local setup_output=""
    if setup_output=$(UV_PROJECT_ENVIRONMENT=.venv uv run python - "$REPO_ROOT" <<'PY'
from pathlib import Path
import sys

from core.services.logic_assist_setup import run_logic_assist_setup

repo_root = Path(sys.argv[1])
result = run_logic_assist_setup(repo_root)
for line in result.get("steps", []):
    print(f"STEP:{line}")
for line in result.get("warnings", []):
    print(f"WARN:{line}")
PY
); then
        while IFS= read -r line; do
            case "$line" in
                STEP:*) info "${line#STEP:}" ;;
                WARN:*) warning "${line#WARN:}" ;;
            esac
        done <<< "$setup_output"
    else
        warning "Logic-assist setup helper did not complete cleanly. You can rerun with: ./bin/udos then SETUP dev"
    fi
}

function reconcile_provider_mode() {
    local env_file="$REPO_ROOT/.env"
    if [[ ! -f "$env_file" ]]; then
        return
    fi

    local mistral_key
    mistral_key="$(read_env_var "$env_file" "MISTRAL_API_KEY")"
    local cloud_ready=false
    if [[ -n "$mistral_key" ]]; then
        cloud_ready=true
    fi

    local local_ready=false
    local local_model_path local_model_name local_model_file
    local_model_path="$(awk -F': ' '/^- local_model_path:/{print $2; exit}' "$REPO_ROOT/core/framework/seed/bank/typo-workspace/settings/logic-assist.md" 2>/dev/null || true)"
    local_model_name="$(awk -F': ' '/^- local_model_name:/{print $2; exit}' "$REPO_ROOT/core/framework/seed/bank/typo-workspace/settings/logic-assist.md" 2>/dev/null || true)"
    if [[ -n "$local_model_path" && -n "$local_model_name" ]]; then
        local_model_file="$REPO_ROOT/${local_model_path#./}/$local_model_name"
        if [[ -f "$local_model_file" ]]; then
            local_ready=true
        fi
    fi

    if [[ "$local_ready" == true ]]; then
        write_provider_hints "local" "$(if [[ "$cloud_ready" == true ]]; then echo "cloud"; else echo "none"; fi)"
        info "Provider mode: local GPT4All primary$(if [[ "$cloud_ready" == true ]]; then echo ", Wizard cloud secondary"; else echo ""; fi)"
        return
    fi

    if [[ "$cloud_ready" == true ]]; then
        write_provider_hints "cloud" "cloud"
        info "Provider mode: Wizard cloud primary (local GPT4All model unavailable)"
        return
    fi

    write_provider_hints "none" "none"
    warning "No logic-assist provider is currently ready (local GPT4All model missing and cloud key absent)."
    warning "Remediation: run SETUP dev, place the configured GPT4All model file in memory/models/gpt4all, or set MISTRAL_API_KEY in .env and rerun --update."
}

function build_optional_tui() {
    if [[ ! -f "$REPO_ROOT/scripts/build_udos_tui.sh" ]]; then
        return
    fi
    if ! command -v go >/dev/null 2>&1; then
        info "Skipping Bubble Tea/Lip Gloss TUI build (go not installed)"
        return
    fi

    step "Building optional v1.5 uDOS TUI frontend..."
    if "$REPO_ROOT/scripts/build_udos_tui.sh"; then
        success "udos-tui built"
    else
        warning "udos-tui build failed (non-critical). Core shell remains available through ./bin/udos"
    fi
}

# ── Run Health Check ─────────────────────────────────────────
function run_health_check() {
    step "Running system health check..."

    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Installation Summary"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "System Information:"
    echo "  OS: $OS_TYPE $OS_VERSION"
    echo "  Architecture: $CPU_ARCH"
    echo "  CPU Cores: $CPU_CORES"
    echo "  RAM: ${TOTAL_RAM_GB}GB"
    echo "  Free Storage: ${FREE_STORAGE_GB}GB"
    echo "  GPU: $(if [[ "$HAS_GPU" == true ]]; then echo "Yes"; else echo "No"; fi)"
    echo "  Selected Tier: $INSTALL_TIER"
    echo "  Certified Profiles: ${SELECTED_PROFILES_CSV:-core}"
    echo "  TinyCore Tier Mapping: $SELECTED_TINYCORE_TIER"
    echo "  Package Groups: ${SELECTED_PACKAGE_GROUPS:-utilities}"
    echo "  Official Extensions: ${SELECTED_PROFILE_EXTENSIONS:-none}"
    echo "  Local Models Allowed: $(if [[ "$LOCAL_MODELS_ALLOWED" == true ]]; then echo "Yes"; else echo "No"; fi)"
    echo ""
    echo "Installed Components:"
    echo "  uv: $(if command -v uv &> /dev/null; then echo "✓ $(uv --version)"; else echo "✗"; fi)"
    echo "  Dev Mode Tooling: $(if command -v vibe &> /dev/null; then echo "✓ $(vibe --version | head -n1)"; else echo "✗"; fi)"
    echo "  micro: $(if command -v micro &> /dev/null; then echo "✓"; else echo "✗"; fi)"
    echo "  Obsidian: $(if [[ "$OBSIDIAN_INSTALLED" == true ]]; then echo "✓"; else echo "✗"; fi)"
    echo "  GPT4All package: $(UV_PROJECT_ENVIRONMENT=.venv uv run python -c "import importlib.util; print('✓' if importlib.util.find_spec('gpt4all') else '✗')" 2>/dev/null || echo "✗")"
    echo "  udos-tui: $(if [[ -x "$REPO_ROOT/tui/bin/udos-tui" ]]; then echo "✓ $REPO_ROOT/tui/bin/udos-tui"; else echo "✗"; fi)"
    echo ""
    echo "Configuration:"
    echo "  Repo Root: $REPO_ROOT"
    echo "  .env: $(if [[ -f "$REPO_ROOT/.env" ]]; then echo "✓"; else echo "✗"; fi)"
    local summary_memory_root="$REPO_ROOT/memory"
    local summary_vault_root="$summary_memory_root/vault"
    if [[ -f "$REPO_ROOT/.env" ]]; then
        local env_memory_root env_vault_root
        env_memory_root="$(read_env_var "$REPO_ROOT/.env" "UDOS_MEMORY_ROOT")"
        env_vault_root="$(read_env_var "$REPO_ROOT/.env" "VAULT_ROOT")"
        if [[ -n "$env_memory_root" ]]; then
            summary_memory_root="$env_memory_root"
        fi
        if [[ -n "$env_vault_root" ]]; then
            summary_vault_root="$env_vault_root"
        fi
    fi
    echo "  Memory Root: $(if [[ -d "$summary_memory_root" ]]; then echo "✓ $summary_memory_root"; else echo "✗ $summary_memory_root"; fi)"
    echo "  Vault Root: $(if [[ -d "$summary_vault_root" ]]; then echo "✓ $summary_vault_root"; else echo "✗ $summary_vault_root"; fi)"
    echo "  Dev Tool Bridge: $(if [[ -L "$REPO_ROOT/.vibe/tools" ]]; then echo "✓"; else echo "✗"; fi)"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
}

# ── Main Installation Flow ───────────────────────────────────
function main() {
    banner

    detect_os
    evaluate_install_tier
    if [[ "$PREFLIGHT_JSON" == true ]]; then
        emit_preflight_json
        exit 0
    fi
    check_required_commands
    install_uv
    select_certified_profiles

    if [[ "$WIZARD_ONLY" == true ]]; then
        # Wizard-only mode: assume core is already installed
        install_wizard_requirements
        sync_certified_profiles
        success "Wizard components installed successfully!"
        exit 0
    fi

    # Core installation
    install_micro
    check_obsidian
    setup_env_file
    enforce_env_policy
    reconcile_user_identity_state
    setup_vault_structure
    if _profile_selected "dev"; then
        install_vibe_cli
        setup_vibe_integration
    else
        info "Skipping Dev Mode tooling installation (dev profile not selected)"
    fi
    install_core_requirements
    build_optional_tui

    # Wizard installation (home profile)
    if [[ "$CORE_ONLY" == false ]] && _profile_selected "home"; then
        install_wizard_requirements
    fi

    # Optional components
    setup_logic_assist_runtime
    reconcile_provider_mode
    sync_certified_profiles

    # Final checks
    run_health_check

    # Success message
    echo ""
    success "Installation complete!"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  Next Steps"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "1. Review and update .env with your configuration:"
    printf '%b\n' "   ${CYAN}micro $REPO_ROOT/.env${NC}"
    echo ""
    echo "2. Open the canonical uDOS runtime:"
    printf '%b\n' "   ${CYAN}./bin/udos${NC}"
    echo ""
    if _profile_selected "dev"; then
        echo "   Dev profile also installed contributor tooling:"
        printf '%b\n' "   ${CYAN}cd $REPO_ROOT${NC}"
        printf '%b\n' "   ${CYAN}vibe${NC}"
        printf '%b\n' "   ${CYAN}./bin/udos${NC} then type: ${BOLD}SETUP dev${NC}"
        echo ""
    fi
    if _profile_selected "home"; then
        echo "3. Start the wizard server:"
        printf '%b\n' "   ${CYAN}./bin/udos wizard start${NC}"
        echo ""
    fi
    echo "3. Review runtime status and profile surfaces:"
    printf '%b\n' "   ${CYAN}./bin/udos status${NC}"
    printf '%b\n' "   ${CYAN}./bin/udos${NC} then type: ${BOLD}UCODE PROFILE LIST${NC}"
    printf '%b\n' "   ${CYAN}./bin/udos${NC} then type: ${BOLD}UCODE OPERATOR STATUS${NC}"
    echo ""
    echo "4. Run the SETUP story to complete configuration:"
    printf '%b\n' "   ${CYAN}./bin/udos${NC} then type: ${BOLD}SETUP${NC}"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "For help and documentation:"
    echo "  README: $REPO_ROOT/README.md"
    echo "  Quick Start: $REPO_ROOT/QUICK-START.md"
    echo ""

    if [[ "${UDOS_AUTO_LAUNCH_UCODE:-0}" == "1" ]]; then
        if [[ -x "$REPO_ROOT/bin/udos" ]]; then
            info "Launching uDOS runtime..."
            cd "$REPO_ROOT"
            "$REPO_ROOT/bin/udos" || warning "uDOS runtime exited with non-zero status"
        else
            warning "Auto-launch requested but '$REPO_ROOT/bin/udos' is not executable"
        fi
    elif [[ "${UDOS_AUTO_LAUNCH_VIBE:-0}" == "1" ]]; then
        if command -v vibe &> /dev/null; then
            info "Launching Dev Mode tooling (vibe)..."
            cd "$REPO_ROOT"
            vibe || warning "Vibe exited with non-zero status"
        else
            warning "Auto-launch requested but 'vibe' is not on PATH"
        fi
    fi
}

# Run main installation
main "$@"
