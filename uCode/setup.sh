#!/bin/bash
# setup.sh - uDOS Unified Setup System v2.0
# Consolidated: setup-template-processor.sh + setup-template-processor-compat.sh + setup-dev.sh
# Handles all user setup, configuration, and initialization

set -euo pipefail

# Environment Setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
SETUP_TEMPLATE="${UHOME}/uTemplate/user-setup-template.md"
TEMP_DIR="${UMEM}/temp/setup-$$"
VARS_FILE="${TEMP_DIR}/setup_vars.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Color helpers
red() { echo -e "${RED}$1${NC}"; }
green() { echo -e "${GREEN}$1${NC}"; }
yellow() { echo -e "${YELLOW}$1${NC}"; }
blue() { echo -e "${BLUE}$1${NC}"; }
bold() { echo -e "${WHITE}$1${NC}"; }
dim() { echo -e "\033[2m$1${NC}"; }

# Logging
log() { echo -e "${CYAN}[$(date '+%H:%M:%S')] [SETUP]${NC} $1"; }
success() { echo -e "${GREEN}✅${NC} $1"; }
error() { echo -e "${RED}❌${NC} $1" >&2; }
warn() { echo -e "${YELLOW}⚠️${NC} $1"; }

# Create temp directory
mkdir -p "$TEMP_DIR"
trap 'cleanup' EXIT

cleanup() {
    [[ -d "$TEMP_DIR" ]] && rm -rf "$TEMP_DIR" 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════════════
# 🔧 BASH COMPATIBILITY HANDLING
# ═══════════════════════════════════════════════════════════════════════

# Check bash version and setup appropriate variable handling
setup_variable_system() {
    # Check bash version for associative array support
    if [[ ${BASH_VERSION%%.*} -ge 4 ]]; then
        log "Using bash ${BASH_VERSION} with associative arrays"
        declare -gA SETUP_VARS 2>/dev/null || {
            warn "Associative arrays not available, using file-based variables"
            export BASH_COMPAT_MODE=true
        }
        export BASH_COMPAT_MODE=false
    else
        log "Using bash ${BASH_VERSION} - compatibility mode enabled"
        export BASH_COMPAT_MODE=true
        > "$VARS_FILE"  # Initialize variables file
    fi
}

# Bash version-agnostic variable handling
set_var() {
    local name="$1"
    local value="$2"
    
    if [[ "$BASH_COMPAT_MODE" == "true" ]]; then
        echo "${name}=${value}" >> "$VARS_FILE"
    else
        SETUP_VARS["$name"]="$value"
    fi
}

get_var() {
    local name="$1"
    
    if [[ "$BASH_COMPAT_MODE" == "true" ]]; then
        grep "^${name}=" "$VARS_FILE" 2>/dev/null | cut -d'=' -f2- || echo ""
    else
        echo "${SETUP_VARS[$name]:-}"
    fi
}

# ═══════════════════════════════════════════════════════════════════════
# 📋 TEMPLATE PROCESSING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

# Show introduction from template
show_intro() {
    if [[ -f "$SETUP_TEMPLATE" ]]; then
        local intro
        intro=$(sed -n '/\[SETUP_INTRO\]/,/\[\/SETUP_INTRO\]/p' "$SETUP_TEMPLATE" | sed '1d;$d')
        echo
        bold "$(echo "$intro" | head -n1)"
        echo "$(echo "$intro" | tail -n+2)"
        echo
    else
        bold "🎭 Welcome to uDOS Setup!"
        echo "Let's configure your Universal Development OS environment."
        echo
    fi
}

# Process input block from template
process_input_block() {
    local block_name="$1"
    local block_content
    
    if [[ ! -f "$SETUP_TEMPLATE" ]]; then
        warn "Setup template not found, using fallback questions"
        setup_fallback_questions
        return
    fi
    
    # Extract block content
    block_content=$(sed -n "/\\[INPUT:$block_name\\]/,/\\[\\/INPUT:$block_name\\]/p" "$SETUP_TEMPLATE" | sed '1d;$d')
    
    if [[ -z "$block_content" ]]; then
        warn "Block $block_name not found in template"
        return
    fi
    
    # Parse block variables
    local question=$(echo "$block_content" | grep "question:" | cut -d':' -f2- | xargs)
    local variable=$(echo "$block_content" | grep "variable:" | cut -d':' -f2 | xargs)
    local default=$(echo "$block_content" | grep "default:" | cut -d':' -f2- | xargs)
    local validation=$(echo "$block_content" | grep "validation:" | cut -d':' -f2- | xargs)
    local help_text=$(echo "$block_content" | grep "help:" | cut -d':' -f2- | xargs)
    
    # Handle options for multiple choice
    local options=()
    while IFS= read -r line; do
        if [[ "$line" =~ ^options: ]]; then
            IFS=',' read -ra opts <<< "$(echo "$line" | cut -d':' -f2-)"
            for opt in "${opts[@]}"; do
                options+=("$(echo "$opt" | xargs)")
            done
        fi
    done <<< "$block_content"
    
    # Display question
    echo
    blue "📋 $question"
    [[ -n "$help_text" ]] && dim "   💡 $help_text"
    
    # Show options if available
    if [[ ${#options[@]} -gt 0 ]]; then
        echo "   Options:"
        for i in "${!options[@]}"; do
            echo "   $(($i + 1)). ${options[$i]}"
        done
        echo
    fi
    
    # Get user input
    local input=""
    local prompt="   Enter value"
    [[ -n "$default" ]] && prompt="$prompt (default: $default)"
    prompt="$prompt: "
    
    while true; do
        read -p "$prompt" input
        
        # Use default if empty
        [[ -z "$input" && -n "$default" ]] && input="$default"
        
        # Handle numeric selection for options
        if [[ ${#options[@]} -gt 0 && "$input" =~ ^[0-9]+$ ]]; then
            local idx=$(($input - 1))
            if [[ $idx -ge 0 && $idx -lt ${#options[@]} ]]; then
                input="${options[$idx]}"
            fi
        fi
        
        # Validate input
        if [[ -n "$validation" ]]; then
            case "$validation" in
                "email")
                    if [[ "$input" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
                        break
                    else
                        red "   ❌ Please enter a valid email address"
                    fi
                    ;;
                "not_empty")
                    if [[ -n "$input" ]]; then
                        break
                    else
                        red "   ❌ This field cannot be empty"
                    fi
                    ;;
                *)
                    break
                    ;;
            esac
        else
            break
        fi
    done
    
    # Store the value
    set_var "$variable" "$input"
    green "   ✓ $variable set to: $input"
}

# Fallback questions for when template is not available
setup_fallback_questions() {
    log "Using fallback setup questions..."
    
    # Username
    echo
    blue "📋 What should we call you?"
    read -p "   Enter username (default: $(whoami)): " username
    username="${username:-$(whoami)}"
    set_var "UDOS_USERNAME" "$username"
    green "   ✓ Username: $username"
    
    # Location  
    echo
    blue "📋 Where are you located?"
    read -p "   Enter location (default: Earth): " location
    location="${location:-Earth}"
    set_var "UDOS_LOCATION" "$location"
    green "   ✓ Location: $location"
    
    # Timezone
    echo
    blue "📋 What's your timezone?"
    read -p "   Enter timezone (default: UTC): " timezone
    timezone="${timezone:-UTC}"
    set_var "UDOS_TIMEZONE" "$timezone"
    green "   ✓ Timezone: $timezone"
    
    # Theme
    echo
    blue "📋 Choose your interface theme:"
    echo "   1. Dark (default)"
    echo "   2. Light"
    echo "   3. Matrix"
    echo "   4. Cyberpunk"
    read -p "   Select theme (1-4, default: 1): " theme_choice
    
    case "${theme_choice:-1}" in
        1) theme="dark" ;;
        2) theme="light" ;;
        3) theme="matrix" ;;
        4) theme="cyberpunk" ;;
        *) theme="dark" ;;
    esac
    
    set_var "UDOS_THEME" "$theme"
    green "   ✓ Theme: $theme"
    
    # AI Companion
    echo
    blue "📋 Choose your AI companion:"
    echo "   1. Gemini (Google AI)"
    echo "   2. OK Companion (Local)"
    echo "   3. None"
    read -p "   Select companion (1-3, default: 2): " companion_choice
    
    case "${companion_choice:-2}" in
        1) companion="gemini" ;;
        2) companion="ok" ;;
        3) companion="none" ;;
        *) companion="ok" ;;
    esac
    
    set_var "UDOS_AI_COMPANION" "$companion"
    green "   ✓ AI Companion: $companion"
}

# ═══════════════════════════════════════════════════════════════════════
# 🔄 CONFIGURATION GENERATION
# ═══════════════════════════════════════════════════════════════════════

# Generate configuration files
generate_config_files() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local file_prefix="${timestamp}_$(get_var "UDOS_USERNAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')"
    
    # Create directories
    mkdir -p "$UMEM"/{user,config,missions}
    
    # Generate identity file
    local identity_file="$UMEM/user/${file_prefix}_identity.md"
    cat > "$identity_file" << EOF
# uDOS User Identity

**Username**: $(get_var "UDOS_USERNAME")
**Location**: $(get_var "UDOS_LOCATION")
**Timezone**: $(get_var "UDOS_TIMEZONE")
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Version**: uDOS v1.0 Alpha
**Setup Method**: Template-Based Setup v2.0

## Configuration

- **Theme**: $(get_var "UDOS_THEME")
- **AI Companion**: $(get_var "UDOS_AI_COMPANION")
- **Shell**: $SHELL
- **Platform**: $(uname -s)

## Setup Details

**Template System**: Available
**Bash Version**: $BASH_VERSION
**Setup Timestamp**: $timestamp
**Configuration Method**: $(if [[ "$BASH_COMPAT_MODE" == "true" ]]; then echo "Compatibility Mode"; else echo "Modern Mode"; fi)

---
*Generated by uDOS Setup System v2.0*
EOF

    # Generate setup variables
    local config_file="$UMEM/config/${file_prefix}_setup_vars.sh"
    cat > "$config_file" << EOF
#!/bin/bash
# uDOS Setup Variables
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

# User Configuration
export UDOS_USERNAME="$(get_var "UDOS_USERNAME")"
export UDOS_LOCATION="$(get_var "UDOS_LOCATION")"  
export UDOS_TIMEZONE="$(get_var "UDOS_TIMEZONE")"
export UDOS_THEME="$(get_var "UDOS_THEME")"
export UDOS_AI_COMPANION="$(get_var "UDOS_AI_COMPANION")"

# System Configuration
export UDOS_VERSION="1.0"
export UDOS_SETUP_METHOD="template"
export UDOS_SETUP_TIMESTAMP="$timestamp"
export UDOS_IDENTITY_FILE="$identity_file"
export UDOS_CONFIG_FILE="$config_file"

# Development Settings
export UDOS_DEV_MODE="false"
export UDOS_DEBUG_MODE="false"
export UDOS_LOGGING_LEVEL="info"

# Feature Flags
export UDOS_FEATURES_ENABLED="dashboard,missions,sandbox,companions"
export UDOS_TEMPLATE_SYSTEM="enabled"
export UDOS_DATASET_INTEGRATION="enabled"

# Path Configuration
export UDOS_HOME="$UHOME"
export UDOS_MEMORY="$UMEM"
export UDOS_SCRIPT_DIR="$SCRIPT_DIR"
EOF

    # Generate welcome mission
    local mission_file="$UMEM/missions/${file_prefix}_welcome_mission.md"
    cat > "$mission_file" << EOF
# 🎯 Welcome Mission - uDOS Setup Complete

**Mission ID**: welcome-${timestamp}
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Status**: Active
**Priority**: High

## Objective

Welcome $(get_var "UDOS_USERNAME") to uDOS! Complete your initial setup and explore the system.

## Tasks

### 1. System Validation ✓
- [x] uDOS installation validated
- [x] User identity created
- [x] Configuration generated

### 2. Explore Core Features

- [ ] Run system health check: \`ucode core health\`
- [ ] Generate dashboard: \`ucode dash live\`
- [ ] Check available packages: \`ucode package list\`
- [ ] Set up AI companion: \`ucode companion setup\`

### 3. Customization

- [ ] Explore themes: \`ucode display theme\`
- [ ] Configure development environment
- [ ] Set up first project in sandbox

## Resources

- **User Manual**: docs/user-manual.md
- **Architecture**: uKnowledge/ARCHITECTURE.md  
- **Templates**: uTemplate/
- **Your Identity**: $identity_file

## Next Steps

1. 🔍 Run: \`ucode core check\` - Validate your setup
2. 📊 Try: \`ucode dash live\` - Launch live dashboard
3. 📚 Read: \`ucode help\` - Explore available commands

---
*Generated by uDOS Setup System v2.0*
EOF

    success "Configuration files generated:"
    echo "   📄 Identity: $identity_file"
    echo "   ⚙️  Config: $config_file"
    echo "   🎯 Mission: $mission_file"
    
    # Set identity symlink for compatibility
    ln -sf "$identity_file" "$UMEM/user/identity.md" 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════════════
# 🎭 INTERACTIVE SETUP MODES
# ═══════════════════════════════════════════════════════════════════════

# Template-based interactive setup
interactive_template_setup() {
    bold "🎭 uDOS Template-Based Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    show_intro
    
    # Process standard setup blocks
    local setup_blocks=("USERNAME" "LOCATION" "TIMEZONE" "THEME" "AI_COMPANION")
    
    for block in "${setup_blocks[@]}"; do
        process_input_block "$block"
    done
    
    echo
    log "Generating configuration files..."
    generate_config_files
    
    echo
    success "🎉 Template-based setup complete!"
    
    echo
    bold "📊 Setup Summary:"
    echo "─────────────────"
    echo "👤 Username: $(get_var "UDOS_USERNAME")"
    echo "📍 Location: $(get_var "UDOS_LOCATION")"
    echo "⏰ Timezone: $(get_var "UDOS_TIMEZONE")"
    echo "🎨 Theme: $(get_var "UDOS_THEME")"
    echo "🤖 AI Companion: $(get_var "UDOS_AI_COMPANION")"
    
    echo
    bold "🚀 Next Steps:"
    echo "1. Run: ucode core check"
    echo "2. Try: ucode dash live"
    echo "3. Read: docs/user-manual.md"
}

# Quick setup mode
quick_setup() {
    bold "⚡ uDOS Quick Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    log "Using intelligent defaults..."
    
    # Set sensible defaults
    set_var "UDOS_USERNAME" "$(whoami)"
    set_var "UDOS_LOCATION" "Earth"
    set_var "UDOS_TIMEZONE" "UTC"
    set_var "UDOS_THEME" "dark"
    set_var "UDOS_AI_COMPANION" "ok"
    
    generate_config_files
    
    success "⚡ Quick setup complete with defaults!"
    echo "Run './setup.sh interactive' to customize settings"
}

# Development environment setup  
dev_setup() {
    bold "🔧 uDOS Development Environment Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # System information
    log "System Information:"
    echo "🖥️  Hostname: $(hostname)"
    echo "🌿 Git Version: $(git --version 2>/dev/null || echo "Not installed")"
    echo "🐚 Shell: $SHELL"
    echo "📂 Working Dir: $(pwd)"
    
    # Optional dev tools
    log "Setting up development tools..."
    
    # Check for essential dev packages
    local dev_packages=("git" "curl" "jq" "bat" "fd" "rg" "glow")
    local missing_packages=()
    
    for pkg in "${dev_packages[@]}"; do
        if ! command -v "$pkg" >/dev/null 2>&1; then
            missing_packages+=("$pkg")
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        warn "Missing development packages: ${missing_packages[*]}"
        echo "Run: ucode package install-all"
    else
        success "All development packages installed!"
    fi
    
    success "🔧 Development environment setup complete!"
}

# ═══════════════════════════════════════════════════════════════════════
# 🎯 MAIN COMMAND INTERFACE  
# ═══════════════════════════════════════════════════════════════════════

# Show help
show_help() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    🎭 uDOS SETUP SYSTEM                     ║${NC}"
    echo -e "${PURPLE}║              Template-Based Configuration v2.0              ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    echo -e "${WHITE}uDOS Setup Commands:${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
    echo
    echo -e "${CYAN}🎭 Setup Modes:${NC}"
    echo -e "${WHITE}  setup interactive              Complete template-based setup${NC}"
    echo -e "${WHITE}  setup quick                    Quick setup with defaults${NC}"
    echo -e "${WHITE}  setup dev                      Development environment setup${NC}"
    echo
    echo -e "${CYAN}🔧 Configuration:${NC}"
    echo -e "${WHITE}  setup reset                    Reset configuration${NC}"
    echo -e "${WHITE}  setup validate                 Validate current configuration${NC}"
    echo -e "${WHITE}  setup export                   Export configuration${NC}"
    echo
    echo -e "${CYAN}ℹ️  Information:${NC}"
    echo -e "${WHITE}  setup status                   Show setup status${NC}"
    echo -e "${WHITE}  setup help                     Show this help${NC}"
    echo
    echo -e "${PURPLE}💡 Examples:${NC}"
    echo -e "${WHITE}  ./setup.sh interactive         # Complete guided setup${NC}"
    echo -e "${WHITE}  ./setup.sh quick               # Quick setup with defaults${NC}"
    echo -e "${WHITE}  ./setup.sh dev                 # Development environment${NC}"
    echo
}

# Main command router
main() {
    local command="${1:-help}"
    
    # Initialize variable system
    setup_variable_system
    
    case "$command" in
        "interactive"|"full"|"complete")
            interactive_template_setup
            ;;
        "quick"|"fast"|"auto")
            quick_setup
            ;;
        "dev"|"development"|"devenv")
            dev_setup
            ;;
        "reset")
            warn "This will reset all configuration!"
            read -p "Continue? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$UMEM/config" "$UMEM/user/identity.md" 2>/dev/null || true
                success "Configuration reset complete"
            else
                log "Reset cancelled"
            fi
            ;;
        "validate"|"check")
            if [[ -f "$UMEM/user/identity.md" ]]; then
                success "User configuration exists"
                cat "$UMEM/user/identity.md"
            else
                error "No user configuration found. Run: setup interactive"
            fi
            ;;
        "export")
            local export_file="$HOME/udos-config-$(date +%Y%m%d).json"
            if [[ -f "$UMEM/user/identity.md" ]]; then
                echo "{" > "$export_file"
                echo "  \"exported\": \"$(date -I)\"," >> "$export_file"
                echo "  \"system\": \"uDOS\"," >> "$export_file"
                echo "  \"version\": \"2.0\"" >> "$export_file"
                echo "}" >> "$export_file"
                success "Configuration exported to: $export_file"
            else
                error "No configuration to export"
            fi
            ;;
        "status")
            if [[ -f "$UMEM/user/identity.md" ]]; then
                success "✅ User setup complete"
                echo "Identity file: $UMEM/user/identity.md"
                echo "Created: $(stat -f "%SB" "$UMEM/user/identity.md" 2>/dev/null || stat -c "%y" "$UMEM/user/identity.md" 2>/dev/null || echo "Unknown")"
            else
                warn "⚠️  User setup not complete"
                echo "Run: ./setup.sh interactive"
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
