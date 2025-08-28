#!/bin/bash
# uCORE Self-Healing Dependency Manager
# Automatically detects, diagnoses, and fixes dependency issues
# Version: 1.0.4.3 - NetHack-Inspired Comprehensive Self-Healing

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Configuration
HEAL_LOG="$UDOS_ROOT/sandbox/logs/self-healing.log"
DEPENDENCY_CONFIG="$UDOS_ROOT/uCORE/config/dependencies.json"
HEAL_ATTEMPTS_FILE="$UDOS_ROOT/sandbox/logs/.heal_attempts"

# Ensure log directory exists
mkdir -p "$(dirname "$HEAL_LOG")"
mkdir -p "$(dirname "$DEPENDENCY_CONFIG")"

# Logging functions
log_heal() {
    local level="$1"
    local message="$2"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$level] $message" >> "$HEAL_LOG"
    
    case "$level" in
        "SUCCESS") echo -e "${GREEN}✨ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}💀 $message${NC}" ;;
        "INFO") echo -e "${BLUE}🔧 $message${NC}" ;;
        "HEAL") echo -e "${CYAN}🎲 $message${NC}" ;;
    esac
}

# NetHack-style messages for dependency healing
get_healing_message() {
    local dep_type="$1"
    local attempt="$2"
    
    case "$dep_type" in
        "python")
            local messages=(
                "You cast 'summon python'. A friendly snake appears!"
                "The ancient python spirits answer your call..."
                "Your coding familiar materializes from the digital realm!"
            )
            ;;
        "pip")
            local messages=(
                "You invoke the package installation ritual..."
                "The pip wizard grants you dependency management powers!"
                "Package repositories open their vaults to you!"
            )
            ;;
        "venv")
            local messages=(
                "You create a magical isolation chamber for your spells..."
                "Virtual environment barriers shimmer into existence!"
                "The sandbox realm expands to accommodate your needs!"
            )
            ;;
        "nodejs")
            local messages=(
                "JavaScript elementals gather to serve your commands..."
                "The Node.js engine hums to life with ancient power!"
                "V8 engines roar across the digital landscape!"
            )
            ;;
        "system")
            local messages=(
                "System dependencies align with cosmic forces..."
                "The package manager spirits bless your installation!"
                "Ancient Unix deities smile upon your quest!"
            )
            ;;
        *)
            local messages=(
                "Mysterious forces work to restore balance..."
                "The self-healing magic flows through the system..."
                "Reality adjusts itself to accommodate your needs..."
            )
            ;;
    esac
    
    local index=$((attempt % ${#messages[@]}))
    echo "${messages[$index]}"
}

# Check if dependency is available
check_dependency() {
    local dep_name="$1"
    local check_command="${2:-command -v $dep_name}"
    
    eval "$check_command" >/dev/null 2>&1
}

# Get attempt count for healing
get_heal_attempts() {
    local dep_name="$1"
    local attempts_file="$HEAL_ATTEMPTS_FILE"
    
    if [[ -f "$attempts_file" ]]; then
        grep "^$dep_name:" "$attempts_file" 2>/dev/null | cut -d: -f2 || echo "0"
    else
        echo "0"
    fi
}

# Increment attempt count
increment_heal_attempts() {
    local dep_name="$1"
    local attempts_file="$HEAL_ATTEMPTS_FILE"
    local current_attempts=$(get_heal_attempts "$dep_name")
    local new_attempts=$((current_attempts + 1))
    
    # Remove old entry and add new one
    if [[ -f "$attempts_file" ]]; then
        grep -v "^$dep_name:" "$attempts_file" > "${attempts_file}.tmp" 2>/dev/null || true
        mv "${attempts_file}.tmp" "$attempts_file"
    fi
    
    echo "$dep_name:$new_attempts" >> "$attempts_file"
    echo "$new_attempts"
}

# Clear attempt count on success
clear_heal_attempts() {
    local dep_name="$1"
    local attempts_file="$HEAL_ATTEMPTS_FILE"
    
    if [[ -f "$attempts_file" ]]; then
        grep -v "^$dep_name:" "$attempts_file" > "${attempts_file}.tmp" 2>/dev/null || true
        mv "${attempts_file}.tmp" "$attempts_file"
    fi
}

# Platform detection
detect_platform() {
    case "$(uname -s)" in
        "Darwin") echo "macos" ;;
        "Linux") 
            if command -v apt >/dev/null 2>&1; then
                echo "debian"
            elif command -v dnf >/dev/null 2>&1; then
                echo "fedora"
            elif command -v pacman >/dev/null 2>&1; then
                echo "arch"
            else
                echo "linux"
            fi
            ;;
        "CYGWIN"*|"MINGW"*|"MSYS"*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

# Self-heal Python installation
heal_python() {
    local platform=$(detect_platform)
    local attempt=$(increment_heal_attempts "python")
    
    log_heal "HEAL" "$(get_healing_message "python" "$attempt")"
    log_heal "INFO" "Attempting to install Python (attempt $attempt/3)"
    
    if [[ $attempt -gt 3 ]]; then
        log_heal "ERROR" "Python healing exhausted after 3 attempts"
        return 1
    fi
    
    case "$platform" in
        "debian")
            if command -v apt >/dev/null 2>&1; then
                sudo apt update && sudo apt install -y python3 python3-pip python3-venv
            fi
            ;;
        "fedora")
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y python3 python3-pip python3-venv
            fi
            ;;
        "arch")
            if command -v pacman >/dev/null 2>&1; then
                sudo pacman -S --noconfirm python python-pip
            fi
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew install python3
            else
                log_heal "ERROR" "Homebrew not found. Please install Python manually."
                return 1
            fi
            ;;
        *)
            log_heal "ERROR" "Unsupported platform for Python auto-installation: $platform"
            return 1
            ;;
    esac
    
    # Verify installation
    if check_dependency "python3"; then
        clear_heal_attempts "python"
        log_heal "SUCCESS" "Python healing successful!"
        return 0
    else
        log_heal "ERROR" "Python healing failed"
        return 1
    fi
}

# Self-heal Python virtual environment
heal_python_venv() {
    local venv_path="$1"
    local attempt=$(increment_heal_attempts "venv")
    
    log_heal "HEAL" "$(get_healing_message "venv" "$attempt")"
    log_heal "INFO" "Recreating Python virtual environment (attempt $attempt/3)"
    
    if [[ $attempt -gt 3 ]]; then
        log_heal "ERROR" "Virtual environment healing exhausted"
        return 1
    fi
    
    # Remove corrupted venv
    if [[ -d "$venv_path" ]]; then
        rm -rf "$venv_path"
        log_heal "INFO" "Removed corrupted virtual environment"
    fi
    
    # Ensure python3-venv is available
    local platform=$(detect_platform)
    if [[ "$platform" == "debian" ]] && ! dpkg -l python3-venv >/dev/null 2>&1; then
        log_heal "INFO" "Installing python3-venv package..."
        sudo apt install -y python3-venv || return 1
    fi
    
    # Create new venv
    python3 -m venv "$venv_path" || return 1
    
    # Upgrade pip
    "$venv_path/bin/python" -m pip install --upgrade pip || return 1
    
    # Verify venv is working
    if [[ -f "$venv_path/bin/python" ]] && "$venv_path/bin/python" --version >/dev/null 2>&1; then
        clear_heal_attempts "venv"
        log_heal "SUCCESS" "Virtual environment healing successful!"
        return 0
    else
        log_heal "ERROR" "Virtual environment healing failed"
        return 1
    fi
}

# Self-heal Python packages
heal_python_packages() {
    local venv_path="$1"
    local requirements_file="$2"
    local attempt=$(increment_heal_attempts "pip")
    
    log_heal "HEAL" "$(get_healing_message "pip" "$attempt")"
    log_heal "INFO" "Installing Python packages (attempt $attempt/3)"
    
    if [[ $attempt -gt 3 ]]; then
        log_heal "ERROR" "Package installation healing exhausted"
        return 1
    fi
    
    # Ensure pip is working
    if ! "$venv_path/bin/python" -m pip --version >/dev/null 2>&1; then
        log_heal "INFO" "Fixing pip in virtual environment..."
        "$venv_path/bin/python" -m ensurepip --upgrade || return 1
    fi
    
    # Install packages
    if [[ -f "$requirements_file" ]]; then
        "$venv_path/bin/pip" install -r "$requirements_file" || return 1
    else
        # Install essential packages
        local essential_packages=("pyyaml" "requests" "click" "flask" "flask-socketio" "psutil" "eventlet")
        for package in "${essential_packages[@]}"; do
            "$venv_path/bin/pip" install "$package" || return 1
        done
    fi
    
    clear_heal_attempts "pip"
    log_heal "SUCCESS" "Python packages healing successful!"
    return 0
}

# Self-heal Node.js installation
heal_nodejs() {
    local platform=$(detect_platform)
    local attempt=$(increment_heal_attempts "nodejs")
    
    log_heal "HEAL" "$(get_healing_message "nodejs" "$attempt")"
    log_heal "INFO" "Attempting to install Node.js (attempt $attempt/3)"
    
    if [[ $attempt -gt 3 ]]; then
        log_heal "ERROR" "Node.js healing exhausted after 3 attempts"
        return 1
    fi
    
    case "$platform" in
        "debian")
            sudo apt update && sudo apt install -y nodejs npm
            ;;
        "fedora")
            sudo dnf install -y nodejs npm
            ;;
        "arch")
            sudo pacman -S --noconfirm nodejs npm
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew install node
            else
                log_heal "ERROR" "Homebrew not found. Please install Node.js manually."
                return 1
            fi
            ;;
        *)
            log_heal "ERROR" "Unsupported platform for Node.js auto-installation: $platform"
            return 1
            ;;
    esac
    
    # Verify installation
    if check_dependency "node" && check_dependency "npm"; then
        clear_heal_attempts "nodejs"
        log_heal "SUCCESS" "Node.js healing successful!"
        return 0
    else
        log_heal "ERROR" "Node.js healing failed"
        return 1
    fi
}

# Self-heal system dependencies
heal_system_dependencies() {
    local platform=$(detect_platform)
    local attempt=$(increment_heal_attempts "system")
    
    log_heal "HEAL" "$(get_healing_message "system" "$attempt")"
    log_heal "INFO" "Installing system dependencies (attempt $attempt/3)"
    
    if [[ $attempt -gt 3 ]]; then
        log_heal "ERROR" "System dependencies healing exhausted"
        return 1
    fi
    
    local essential_deps=("curl" "wget" "git" "jq")
    local missing_deps=()
    
    # Check which dependencies are missing
    for dep in "${essential_deps[@]}"; do
        if ! check_dependency "$dep"; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -eq 0 ]]; then
        clear_heal_attempts "system"
        log_heal "SUCCESS" "All system dependencies already available!"
        return 0
    fi
    
    log_heal "INFO" "Missing dependencies: ${missing_deps[*]}"
    
    case "$platform" in
        "debian")
            sudo apt update && sudo apt install -y "${missing_deps[@]}"
            ;;
        "fedora")
            sudo dnf install -y "${missing_deps[@]}"
            ;;
        "arch")
            sudo pacman -S --noconfirm "${missing_deps[@]}"
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew install "${missing_deps[@]}"
            else
                log_heal "ERROR" "Homebrew not found. Please install dependencies manually."
                return 1
            fi
            ;;
        *)
            log_heal "ERROR" "Unsupported platform for auto-installation: $platform"
            return 1
            ;;
    esac
    
    # Verify all dependencies are now available
    for dep in "${missing_deps[@]}"; do
        if ! check_dependency "$dep"; then
            log_heal "ERROR" "Failed to install $dep"
            return 1
        fi
    done
    
    clear_heal_attempts "system"
    log_heal "SUCCESS" "System dependencies healing successful!"
    return 0
}

# Main dependency diagnosis and healing
heal_dependencies() {
    local context="${1:-general}"
    
    log_heal "INFO" "Starting dependency healing for context: $context"
    
    # Check and heal system dependencies first
    if ! check_dependency "curl" || ! check_dependency "git" || ! check_dependency "jq"; then
        log_heal "INFO" "System dependencies need healing..."
        heal_system_dependencies || return 1
    fi
    
    # Check and heal Python
    if ! check_dependency "python3"; then
        log_heal "INFO" "Python needs healing..."
        heal_python || return 1
    fi
    
    # Context-specific healing
    case "$context" in
        "python"|"uscript")
            local venv_path="$UDOS_ROOT/uSCRIPT/venv/python"
            local requirements="$UDOS_ROOT/uSCRIPT/config/requirements.txt"
            
            # Check virtual environment
            if [[ ! -f "$venv_path/bin/python" ]] || ! "$venv_path/bin/python" --version >/dev/null 2>&1; then
                log_heal "INFO" "Python virtual environment needs healing..."
                heal_python_venv "$venv_path" || return 1
            fi
            
            # Check Python packages
            if ! "$venv_path/bin/python" -c "import yaml, requests, click" >/dev/null 2>&1; then
                log_heal "INFO" "Python packages need healing..."
                heal_python_packages "$venv_path" "$requirements" || return 1
            fi
            ;;
            
        "desktop"|"tauri")
            # Check Node.js for desktop development
            if ! check_dependency "node" || ! check_dependency "npm"; then
                log_heal "INFO" "Node.js needs healing..."
                heal_nodejs || return 1
            fi
            ;;
    esac
    
    log_heal "SUCCESS" "Dependency healing completed successfully!"
    return 0
}

# Show healing status
show_healing_status() {
    echo -e "${CYAN}🎲 uDOS Self-Healing Dependency Status${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Check system dependencies
    echo -e "${WHITE}System Dependencies:${NC}"
    local system_deps=("curl" "wget" "git" "jq" "python3")
    for dep in "${system_deps[@]}"; do
        if check_dependency "$dep"; then
            echo -e "  ✅ $dep"
        else
            echo -e "  ❌ $dep (healing available)"
        fi
    done
    
    # Check Python environment
    echo -e "\n${WHITE}Python Environment:${NC}"
    local venv_path="$UDOS_ROOT/uSCRIPT/venv/python"
    if [[ -f "$venv_path/bin/python" ]]; then
        echo -e "  ✅ Virtual environment"
        
        # Check packages
        local py_packages=("yaml" "requests" "click" "flask")
        for pkg in "${py_packages[@]}"; do
            if "$venv_path/bin/python" -c "import $pkg" >/dev/null 2>&1; then
                echo -e "  ✅ $pkg"
            else
                echo -e "  ❌ $pkg (healing available)"
            fi
        done
    else
        echo -e "  ❌ Virtual environment (healing available)"
    fi
    
    # Check Node.js
    echo -e "\n${WHITE}Desktop Development:${NC}"
    if check_dependency "node"; then
        echo -e "  ✅ Node.js ($(node --version))"
    else
        echo -e "  ❌ Node.js (healing available)"
    fi
    
    if check_dependency "npm"; then
        echo -e "  ✅ npm ($(npm --version))"
    else
        echo -e "  ❌ npm (healing available)"
    fi
    
    # Show recent healing activities
    if [[ -f "$HEAL_LOG" ]]; then
        echo -e "\n${WHITE}Recent Healing Activity:${NC}"
        tail -5 "$HEAL_LOG" | while read -r line; do
            echo -e "  ${BLUE}$line${NC}"
        done
    fi
}

# Reset healing attempt counters
reset_healing_attempts() {
    if [[ -f "$HEAL_ATTEMPTS_FILE" ]]; then
        rm "$HEAL_ATTEMPTS_FILE"
        log_heal "INFO" "Healing attempt counters reset"
    fi
}

# Main command interface
main() {
    case "${1:-status}" in
        "heal")
            heal_dependencies "${2:-general}"
            ;;
        "status")
            show_healing_status
            ;;
        "reset")
            reset_healing_attempts
            ;;
        "python")
            heal_dependencies "python"
            ;;
        "desktop")
            heal_dependencies "desktop"
            ;;
        "system")
            heal_system_dependencies
            ;;
        "help")
            echo "uDOS Self-Healing Dependency Manager"
            echo "Usage: $0 {heal|status|reset|python|desktop|system|help}"
            echo ""
            echo "Commands:"
            echo "  heal [context]     Perform dependency healing (general, python, desktop)"
            echo "  status             Show current dependency status"
            echo "  reset              Reset healing attempt counters"
            echo "  python             Heal Python environment specifically"
            echo "  desktop            Heal desktop development dependencies"
            echo "  system             Heal system-level dependencies"
            echo "  help               Show this help"
            ;;
        *)
            echo "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
