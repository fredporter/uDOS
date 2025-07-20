#!/bin/bash
# core.sh - uDOS Core System Management v2.0
# Consolidated: check.sh + init-user.sh + validate-installation.sh
# Handles all core system validation, initialization, and health checks

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UDENT="${UHOME}/sandbox/identity.md"

# Required directory structure
REQUIRED_DIRS=(
    "uCode" 
    "uMemory/logs/moves" 
    "uMemory/state" 
    "uMemory/user"
    "uMemory/sandbox"
    "uTemplate" 
    "uKnowledge" 
    "uScript/system"
    "uTemplate/system"
    "uMemory/config"
    "uMemory/missions"
    "uMemory/milestones"
    "extension"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Load centralized logging
source "$(dirname "$0")/log-utils.sh" 2>/dev/null || true

# Logging functions
log() { echo -e "${CYAN}[$(date '+%H:%M:%S')] [CORE]${NC} $1"; }
ok() { echo -e "${GREEN}✔${NC} $1"; }
warn() { 
    echo -e "${YELLOW}⚠️${NC} $1"
    # Log to centralized system
    if declare -f log_warning >/dev/null 2>&1; then
        log_warning "$1" "core"
    fi
}
fail() { echo -e "${RED}❌${NC} $1"; }
info() { echo -e "${BLUE}ℹ️${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { 
    echo -e "${RED}[ERROR]${NC} $1" >&2
    # Log to centralized system
    if declare -f log_error >/dev/null 2>&1; then
        log_error "$1" "core"
    fi
}

# Header display
show_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    🛠️  uDOS CORE SYSTEM                     ║${NC}"
    echo -e "${PURPLE}║                 Validation · Setup · Health                  ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

# ═══════════════════════════════════════════════════════════════════════
# 🔍 VALIDATION FUNCTIONS (from check.sh + validate-installation.sh)
# ═══════════════════════════════════════════════════════════════════════

# Check directory structure
check_structure() {
    log "Checking directory structure..."
    local missing=0
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ -d "$UHOME/$dir" ]]; then
            ok "$dir exists"
        else
            fail "$dir missing"
            ((missing++))
        fi
    done
    
    return $missing
}

# Check core system files
check_system_files() {
    log "Checking critical system files..."
    local missing=0
    
    local required_files=(
        "uCode/ucode.sh:Main uDOS shell script"
        "uTemplate/uc-template.md:Core template system"
        "uKnowledge/ARCHITECTURE.md:System architecture docs"
        "extension/package.json:VS Code extension config"
        ".gitignore:Git ignore configuration"
        "README.md:Project documentation"
    )
    
    for entry in "${required_files[@]}"; do
        local file="${entry%%:*}"
        local desc="${entry#*:}"
        
        if [[ -f "$UHOME/$file" ]]; then
            ok "$desc exists"
        else
            fail "$desc missing: $file"
            ((missing++))
        fi
    done
    
    return $missing
}

# Check script permissions
check_permissions() {
    log "Checking script permissions..."
    local issues=0
    
    local executable_scripts=(
        "uCode/ucode.sh"
        "uCode/core.sh"
        "uCode/dash.sh"
        "uCode/setup.sh"
        "uCode/companion.sh"
    )
    
    for script in "${executable_scripts[@]}"; do
        if [[ -f "$UHOME/$script" ]]; then
            if [[ -x "$UHOME/$script" ]]; then
                ok "$script is executable"
            else
                warn "$script not executable - fixing..."
                chmod +x "$UHOME/$script" 2>/dev/null && ok "Fixed: $script" || { fail "Cannot fix: $script"; ((issues++)); }
            fi
        fi
    done
    
    # Check uMemory privacy
    if [[ -d "$UMEM" ]]; then
        local umem_perms=$(stat -f "%OLp" "$UMEM" 2>/dev/null || stat -c "%a" "$UMEM" 2>/dev/null || echo "unknown")
        if [[ "$umem_perms" =~ ^7[0-5][0-5]$ ]]; then
            ok "uMemory permissions secure ($umem_perms)"
        else
            warn "uMemory permissions may be too open ($umem_perms)"
        fi
    fi
    
    return $issues
}

# Check installed packages
check_packages() {
    log "Checking essential packages..."
    local missing=0
    
    local packages=(
        "git:Version control"
        "curl:HTTP client"
        "jq:JSON processor"
        "bat:Syntax highlighting"
        "fd:Fast file finder"
        "rg:Fast text search"
        "glow:Markdown viewer"
    )
    
    for entry in "${packages[@]}"; do
        local pkg="${entry%%:*}"
        local desc="${entry#*:}"
        
        if command -v "$pkg" >/dev/null 2>&1; then
            ok "$desc ($pkg) installed"
        else
            warn "$desc ($pkg) not installed"
            ((missing++))
        fi
    done
    
    if [[ $missing -gt 0 ]]; then
        info "Run: ucode PACKAGE install-all"
    fi
    
    return $missing
}

# System health check
health_check() {
    log "Performing system health check..."
    
    # Check disk space
    local disk_usage=$(df "$HOME" 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//' || echo "0")
    if [[ $disk_usage -gt 90 ]]; then
        warn "Disk usage high: ${disk_usage}%"
    elif [[ $disk_usage -gt 80 ]]; then
        warn "Disk usage moderate: ${disk_usage}%"
    else
        ok "Disk usage normal: ${disk_usage}%"
    fi
    
    # Check memory usage
    if command -v free >/dev/null 2>&1; then
        local mem_usage=$(free | awk '/^Mem:/{printf "%.0f", $3/$2 * 100}' 2>/dev/null || echo "0")
        if [[ $mem_usage -gt 90 ]]; then
            warn "Memory usage high: ${mem_usage}%"
        else
            ok "Memory usage normal: ${mem_usage}%"
        fi
    elif command -v vm_stat >/dev/null 2>&1; then
        # macOS memory check
        ok "Memory status: $(vm_stat | head -1)"
    fi
    
    # Check uDOS-specific health
    local missions=$(find "$UMEM/missions" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    local moves=$(find "$UMEM/logs/moves" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    
    info "uDOS Stats: $missions missions, $moves logged moves"
    
    return 0
}

# ═══════════════════════════════════════════════════════════════════════
# 🚀 INITIALIZATION FUNCTIONS (from init-user.sh)
# ═══════════════════════════════════════════════════════════════════════

# Initialize directory structure
init_directories() {
    log "Creating uDOS directory structure..."
    
    # Create all required directories
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [[ ! -d "$UHOME/$dir" ]]; then
            mkdir -p "$UHOME/$dir" && ok "Created: $dir" || fail "Failed to create: $dir"
        fi
    done
    
    # Create additional subdirectories
    mkdir -p "$UMEM/logs"/{moves,missions,milestones,system}
    mkdir -p "$UMEM/users"/{profiles,roles,permissions,sessions}
    mkdir -p "$UHOME/uScript"/{utilities,automation,examples}
    mkdir -p "$UHOME/uTemplate"/{datasets,variables}
    
    # Set proper permissions
    chmod 700 "$UMEM" 2>/dev/null || true
    
    success "Directory structure initialized"
}

# Initialize configuration files
init_config() {
    log "Initializing configuration files..."
    
    # Create initial log files
    touch "$UMEM/logs/setup.log"
    touch "$UDEV/logs/system/startup.log"
    
    # Create basic configuration
    mkdir -p "$UDEV/config"
    cat > "$UDEV/config/system.conf" << EOF
# uDOS System Configuration
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

UDOS_VERSION=1.0
UDOS_INSTALLED=$(date '+%Y-%m-%d %H:%M:%S')
UDOS_USER=$(whoami)
UDOS_HOSTNAME=$(hostname)
UDOS_SHELL=$SHELL
EOF

    success "Configuration files initialized"
}

# Validate installation
validate_installation() {
    log "Validating uDOS installation integrity..."
    
    local required_paths=(
        "uCode/ucode.sh"
        "uTemplate/uc-template.md"
        "uKnowledge/ARCHITECTURE.md"
        "uScript/README.md"
    )
    
    local missing=0
    for path in "${required_paths[@]}"; do
        if [[ ! -f "$UHOME/$path" ]]; then
            error "Critical file missing: $path"
            ((missing++))
        fi
    done
    
    if [[ $missing -eq 0 ]]; then
        success "Installation validation passed"
        return 0
    else
        error "Installation validation failed: $missing missing files"
        return 1
    fi
}

# Welcome message for first-time setup
show_welcome() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                      🌟 Welcome to uDOS!                    ║${NC}"
    echo -e "${CYAN}║                  Universal Development OS                    ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}║  Your intelligent development companion is being set up...  ║${NC}"
    echo -e "${CYAN}║                                                              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    info "Initializing your uDOS environment..."
    sleep 1
}

# ═══════════════════════════════════════════════════════════════════════
# 🎯 MAIN COMMAND INTERFACE
# ═══════════════════════════════════════════════════════════════════════

# Show help
show_help() {
    show_header
    echo -e "${WHITE}uDOS Core System Commands:${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${CYAN}🔍 Validation & Health:${NC}"
    echo -e "${WHITE}  core check                   Complete system validation${NC}"
    echo -e "${WHITE}  core health                  System health diagnosis${NC}"
    echo -e "${WHITE}  core structure               Check directory structure${NC}"
    echo -e "${WHITE}  core files                   Check critical system files${NC}"
    echo -e "${WHITE}  core permissions             Check and fix script permissions${NC}"
    echo -e "${WHITE}  core packages                Check installed packages${NC}"
    echo
    echo -e "${CYAN}🚀 Initialization:${NC}"
    echo -e "${WHITE}  core init                    Initialize new uDOS installation${NC}"
    echo -e "${WHITE}  core setup                   Interactive system setup${NC}"
    echo -e "${WHITE}  core reset                   Reset system to clean state${NC}"
    echo
    echo -e "${CYAN}📊 Information:${NC}"
    echo -e "${WHITE}  core status                  Show complete system status${NC}"
    echo -e "${WHITE}  core version                 Show version information${NC}"
    echo -e "${WHITE}  core help                    Show this help message${NC}"
    echo
    echo -e "${PURPLE}💡 Examples:${NC}"
    echo -e "${WHITE}  ./core.sh check              # Full system validation${NC}"
    echo -e "${WHITE}  ./core.sh init               # First-time setup${NC}"
    echo -e "${WHITE}  ./core.sh health             # Quick health check${NC}"
    echo
}

# Main command router
main() {
    local command="${1:-help}"
    
    case "$command" in
        "check"|"validate"|"all")
            show_header
            log "Starting complete system validation..."
            
            local total_issues=0
            check_structure; ((total_issues += $?))
            check_system_files; ((total_issues += $?))
            check_permissions; ((total_issues += $?))
            check_packages; ((total_issues += $?))
            health_check
            
            echo
            if [[ $total_issues -eq 0 ]]; then
                success "✨ System validation completed successfully!"
                return 0
            else
                warn "⚠️ System validation completed with $total_issues issues"
                return $total_issues
            fi
            ;;
        "health"|"status")
            show_header
            health_check
            ;;
        "structure")
            show_header
            check_structure
            ;;
        "files")
            show_header
            check_system_files
            ;;
        "permissions"|"perms")
            show_header
            check_permissions
            ;;
        "packages"|"deps")
            show_header
            check_packages
            ;;
        "init"|"initialize")
            show_welcome
            init_directories
            init_config
            validate_installation
            success "🎉 uDOS initialization complete!"
            info "Next steps: Run './core.sh check' to validate your setup"
            ;;
        "setup")
            show_header
            if [[ -f "$SCRIPT_DIR/setup.sh" ]]; then
                log "Launching interactive setup..."
                "$SCRIPT_DIR/setup.sh" interactive
            else
                error "Setup script not found. Run: ./core.sh init"
                return 1
            fi
            ;;
        "reset")
            show_header
            warn "This will reset uDOS to a clean state!"
            read -p "Continue? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                log "Resetting uDOS system..."
                rm -rf "$UMEM" 2>/dev/null || true
                init_directories
                init_config
                success "System reset complete"
            else
                info "Reset cancelled"
            fi
            ;;
        "version"|"ver")
            show_header
            echo -e "${WHITE}uDOS Core System v2.0${NC}"
            echo -e "${CYAN}Consolidated system validation and initialization${NC}"
            if [[ -f "$UDENT" ]]; then
                local version=$(grep "Version:" "$UDENT" 2>/dev/null | cut -d':' -f2 | xargs || echo "Unknown")
                echo -e "${WHITE}uDOS Version: $version${NC}"
            fi
            ;;
        "help"|"-h"|"--help"|*)
            show_help
            ;;
    esac
}

# Execute main function if script is called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
