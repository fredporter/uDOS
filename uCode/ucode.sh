#!/bin/bash
# uDOS v1.2 - Unified Command System
# Minimal, efficient, flat-structure design

set -euo pipefail

# Core Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${HOME}/uDOS"
UMEMORY="${UHOME}/uMemory"
UTEMPLATE="${UHOME}/uTemplate"
UDEV="${UHOME}/uDev"

# Version
VERSION="v1.2"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Rainbow colors for ASCII art
RAINBOW_RED='\033[91m'
RAINBOW_YELLOW='\033[93m'
RAINBOW_GREEN='\033[92m'
RAINBOW_CYAN='\033[96m'
RAINBOW_BLUE='\033[94m'
RAINBOW_PURPLE='\033[95m'

# Logging
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "\n${BOLD}${CYAN}🌀 $1${NC}\n"; }

# Initialize directories
init_directories() {
    local dirs=(
        "$UHOME"
        "$UMEMORY" 
        "$UTEMPLATE"
        "$UDEV"
        "$UHOME/uScript"
        "$UHOME/uKnowledge"
        "$UHOME/package"
        "$UHOME/sandbox"
        "$UHOME/docs"
        "$UHOME/extension"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done
}

# Terminal size detection and management
detect_terminal_size() {
    # Get current terminal dimensions
    if command -v tput >/dev/null 2>&1; then
        CURRENT_COLS=$(tput cols 2>/dev/null || echo "80")
        CURRENT_ROWS=$(tput lines 2>/dev/null || echo "24")
    else
        # Fallback using stty
        CURRENT_COLS=$(stty size 2>/dev/null | cut -d' ' -f2 || echo "80")
        CURRENT_ROWS=$(stty size 2>/dev/null | cut -d' ' -f1 || echo "24")
    fi
    
    # Ensure we have valid numbers
    [[ "$CURRENT_COLS" =~ ^[0-9]+$ ]] || CURRENT_COLS=80
    [[ "$CURRENT_ROWS" =~ ^[0-9]+$ ]] || CURRENT_ROWS=24
}

# Set terminal window size using ANSI escape sequences
set_terminal_size() {
    local cols=${1:-120}
    local rows=${2:-30}
    
    # ANSI escape sequence to resize terminal (works on most terminals)
    printf '\e[8;%d;%dt' "$rows" "$cols"
    
    # Additional positioning (center on screen)
    printf '\e[3;100;100t'
    
    # For macOS Terminal.app specifically
    if [[ "$OSTYPE" == "darwin"* ]] && [[ "$TERM_PROGRAM" == "Apple_Terminal" ]]; then
        local width=$((cols * 8 + 50))
        local height=$((rows * 20 + 50))
        osascript -e "tell application \"Terminal\" to set bounds of front window to {100, 100, $width, $height}" 2>/dev/null || true
    fi
    
    # Update our tracking variables
    CURRENT_COLS=$cols
    CURRENT_ROWS=$rows
}

# Terminal size recommendation engine
recommend_terminal_size() {
    detect_terminal_size
    
    log_info "Current terminal: ${CURRENT_COLS}x${CURRENT_ROWS}"
    
    # Determine best recommendation based on current size
    local recommended="standard"
    local recommended_size="120x30"
    
    if (( CURRENT_COLS >= 160 )); then
        recommended="ultra-wide"
        recommended_size="160x40"
    elif (( CURRENT_COLS >= 140 )); then
        recommended="wide" 
        recommended_size="140x35"
    elif (( CURRENT_COLS >= 120 )); then
        recommended="standard"
        recommended_size="120x30"
    else
        recommended="compact"
        recommended_size="80x24"
    fi
    
    echo -e "\n${YELLOW}🖥️  Terminal Size Optimizer${NC}"
    echo -e "${BLUE}Current Size:${NC} ${CURRENT_COLS}x${CURRENT_ROWS}"
    echo -e "${GREEN}Recommended:${NC} ${recommended_size} (${recommended})"
    echo -e ""
    echo -e "${BOLD}Available Presets:${NC}"
    echo -e "  ${CYAN}1.${NC} Compact     - 80x24 (minimal)"
    echo -e "  ${CYAN}2.${NC} Standard    - 120x30 (recommended)"
    echo -e "  ${CYAN}3.${NC} Wide        - 140x35 (comfortable)"
    echo -e "  ${CYAN}4.${NC} Ultra-wide  - 160x40 (spacious)"
    echo -e "  ${CYAN}5.${NC} Coding      - 120x50 (tall for code)"
    echo -e "  ${CYAN}6.${NC} Dashboard   - 140x45 (data viewing)"
    echo -e "  ${CYAN}c.${NC} Keep current size"
    echo -e "  ${CYAN}Enter${NC} Use recommended (${recommended})"
    echo -e ""
    
    read -p "Select size [1-6/c/Enter]: " choice
    
    case "$choice" in
        1) apply_size_preset "compact" ;;
        2) apply_size_preset "standard" ;;
        3) apply_size_preset "wide" ;;
        4) apply_size_preset "ultra-wide" ;;
        5) apply_size_preset "coding" ;;
        6) apply_size_preset "dashboard" ;;
        c|C) log_info "Keeping current size: ${CURRENT_COLS}x${CURRENT_ROWS}" ;;
        "") apply_size_preset "$recommended" ;;
        *) log_warning "Invalid choice, keeping current size" ;;
    esac
}

# Apply size preset
apply_size_preset() {
    local preset=$1
    local size cols rows
    
    case "$preset" in
        "compact") size="80x24" ;;
        "standard") size="120x30" ;;
        "wide") size="140x35" ;;
        "ultra-wide") size="160x40" ;;
        "coding") size="120x50" ;;
        "dashboard") size="140x45" ;;
        *) size="120x30" ;; # fallback
    esac
    
    cols="${size%x*}"
    rows="${size#*x}"
    
    log_info "Applying $preset preset: ${cols}x${rows}"
    set_terminal_size "$cols" "$rows"
    
    # Brief pause to let terminal adjust
    sleep 0.5
}

# Rainbow ASCII Art
show_rainbow_ascii() {
    echo -e "${RAINBOW_RED}    ██╗   ██╗${RAINBOW_YELLOW}██████╗ ${RAINBOW_GREEN} ██████╗ ${RAINBOW_CYAN}███████╗${NC}"
    echo -e "${RAINBOW_RED}    ██║   ██║${RAINBOW_YELLOW}██╔══██╗${RAINBOW_GREEN}██╔═══██╗${RAINBOW_CYAN}██╔════╝${NC}"
    echo -e "${RAINBOW_RED}    ██║   ██║${RAINBOW_YELLOW}██║  ██║${RAINBOW_GREEN}██║   ██║${RAINBOW_CYAN}███████╗${NC}"
    echo -e "${RAINBOW_RED}    ██║   ██║${RAINBOW_YELLOW}██║  ██║${RAINBOW_GREEN}██║   ██║${RAINBOW_CYAN}╚════██║${NC}"
    echo -e "${RAINBOW_RED}    ╚██████╔╝${RAINBOW_YELLOW}██████╔╝${RAINBOW_GREEN}╚██████╔╝${RAINBOW_CYAN}███████║${NC}"
    echo -e "${RAINBOW_RED}     ╚═════╝ ${RAINBOW_YELLOW}╚═════╝ ${RAINBOW_GREEN} ╚═════╝ ${RAINBOW_CYAN}╚══════╝${NC}"
    echo -e ""
    echo -e "${RAINBOW_PURPLE}    Universal Disk Operating System${NC}"
    echo -e "${RAINBOW_BLUE}    ═══════════════ v1.2 ═══════════════${NC}"
    echo -e ""
}

# System validation
validate_system() {
    local validation_failed=false
    
    log_info "Validating system integrity..."
    
    # Check critical directories
    local critical_dirs=("$UHOME" "$UMEMORY" "$UTEMPLATE")
    for dir in "${critical_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_error "Critical directory missing: $dir"
            validation_failed=true
        fi
    done
    
    # Check critical files
    local critical_files=("$UMEMORY/identity.md")
    for file in "${critical_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_warning "Critical file missing: $file"
            validation_failed=true
        fi
    done
    
    # Check for DESTROY scenario
    if [[ ! -f "$UMEMORY/identity.md" ]] || [[ ! -d "$UHOME" ]]; then
        log_warning "DESTROY scenario detected - full setup required"
        validation_failed=true
    fi
    
    if [[ "$validation_failed" == true ]]; then
        log_warning "System validation failed - initiating recovery"
        return 1
    fi
    
    log_success "System validation passed"
    return 0
}

# Password authentication
authenticate_user() {
    # Check if password is set
    local password_file="$UMEMORY/.auth"
    
    if [[ -f "$password_file" ]]; then
        local stored_hash=$(cat "$password_file")
        
        # Skip if blank password is set
        if [[ "$stored_hash" == "BLANK" ]]; then
            return 0
        fi
        
        echo -ne "${CYAN}🔐 Enter password: ${NC}"
        read -s password
        echo ""
        
        # Simple hash check (for demo - use proper hashing in production)
        local input_hash=$(echo -n "$password" | sha256sum | cut -d' ' -f1)
        
        if [[ "$input_hash" != "$stored_hash" ]]; then
            log_error "Authentication failed"
            exit 1
        fi
        
        log_success "Authentication successful"
    else
        # First time - set password
        echo -ne "${CYAN}🔐 Set password (or press Enter for none): ${NC}"
        read -s password
        echo ""
        
        if [[ -z "$password" ]]; then
            echo "BLANK" > "$password_file"
            log_info "Password disabled"
        else
            echo -n "$password" | sha256sum | cut -d' ' -f1 > "$password_file"
            log_success "Password set"
        fi
    fi
}

# Check if first-time setup needed
check_setup() {
    # Always prompt setup if critical files missing or DESTROY scenario
    if [[ ! -f "$UMEMORY/identity.md" ]] || [[ ! -d "$UHOME" ]] || [[ ! -d "$UMEMORY" ]]; then
        log_warning "Critical system files missing - setup required"
        setup_user
        return 0
    fi
    return 1
}

# User setup
setup_user() {
    log_header "uDOS v1.2 First-Time Setup"
    
    read -p "Enter your name: " USERNAME
    read -p "Enter your role (wizard/sorcerer/ghost/imp): " ROLE
    
    cat > "$UMEMORY/identity.md" << EOF
# 👤 User Identity

**Name**: $USERNAME  
**Role**: ${ROLE:-wizard}  
**Created**: $(date +%Y-%m-%d)  
**System**: uDOS $VERSION

## Configuration

- **Memory Type**: Flat structure
- **Template System**: Unified v1.2
- **Setup Date**: $(date +%Y-%m-%d)

---

*User identity and configuration for uDOS*
EOF

    cat > "$UMEMORY/setup-vars.sh" << EOF
#!/bin/bash
# uDOS Setup Variables

export UDOS_USER="$USERNAME"
export UDOS_ROLE="${ROLE:-wizard}"
export UDOS_VERSION="$VERSION"
export UDOS_SETUP_DATE="$(date +%Y-%m-%d)"
export UDOS_MEMORY_TYPE="flat"
EOF

    cat > "$UMEMORY/001-welcome-mission.md" << EOF
# 🎯 Mission: Welcome to uDOS v1.2

**Created**: $(date +%Y-%m-%d)  
**Status**: Active  
**Type**: Introduction

## Welcome, $USERNAME!

You've successfully set up uDOS v1.2 with the following features:

### 🧠 Flat Memory Structure
- All files in \`uMemory/\` directory
- Clear naming conventions
- Direct access to all data

### 🔄 Unified Commands
- Shortcode syntax: \`[COMMAND:args]\`
- Direct commands: \`COMMAND args\`
- Template processing integrated

### 🎯 Your Role: ${ROLE:-wizard}
- Full system access
- Command creation abilities
- Template modification rights

## Quick Start Commands

- \`HELP\` - Show all commands
- \`STATUS\` - System status
- \`MISSION list\` - Show missions
- \`LOG report\` - Daily activity

---

**Ready to explore!** 🚀
EOF

    log_success "Setup complete! Welcome to uDOS v1.2"
}

# Show dashboard
show_dashboard() {
    log_header "uDOS v1.2 Live Dashboard"
    
    # System Status
    echo -e "${BOLD}📊 System Overview${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Memory stats
    local memory_files=$(find "$UMEMORY" -type f | wc -l)
    local memory_size=$(du -sh "$UMEMORY" 2>/dev/null | cut -f1)
    echo -e "${CYAN}🧠 Memory:${NC}        $memory_files files ($memory_size)"
    
    # Mission stats
    local missions=$(find "$UMEMORY" -name "*-mission.md" | wc -l)
    local active_missions=$(grep -l "Status.*Active" "$UMEMORY"/*-mission.md 2>/dev/null | wc -l)
    echo -e "${PURPLE}🎯 Missions:${NC}       $missions total ($active_missions active)"
    
    # Log stats
    local logs=$(find "$UMEMORY" -name "*-log-*.md" | wc -l)
    echo -e "${YELLOW}📝 Logs:${NC}          $logs entries"
    
    # Template stats
    local templates=$(find "$UTEMPLATE" -name "*.md" | wc -l)
    echo -e "${GREEN}📋 Templates:${NC}     $templates available"
    
    # System health
    echo ""
    echo -e "${BOLD}🔍 System Health${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check critical commands
    local health_status="✅"
    for cmd in jq grep find; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            health_status="⚠️"
            break
        fi
    done
    echo -e "${GREEN}System Tools:${NC}     $health_status All essential tools available"
    
    # Storage check
    local disk_usage=$(df "$UHOME" | tail -1 | awk '{print $5}')
    if [[ ${disk_usage%\%} -gt 90 ]]; then
        echo -e "${RED}Storage:${NC}          ⚠️  Disk usage: $disk_usage"
    else
        echo -e "${GREEN}Storage:${NC}          ✅ Disk usage: $disk_usage"
    fi
    
    # Recent activity
    echo ""
    echo -e "${BOLD}📈 Recent Activity${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Show last 5 modified files
    find "$UMEMORY" -type f -exec ls -lt {} + | head -5 | while read line; do
        local file=$(echo "$line" | awk '{print $NF}')
        local date=$(echo "$line" | awk '{print $6, $7, $8}')
        local filename=$(basename "$file")
        echo -e "${BLUE}•${NC} $filename ${CYAN}($date)${NC}"
    done
    
    echo ""
    echo -e "${BOLD}🎯 Quick Actions${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}•${NC} Type ${BOLD}MISSION create <name>${NC} to start a new mission"
    echo -e "${GREEN}•${NC} Type ${BOLD}MEMORY list${NC} to see all your files"
    echo -e "${GREEN}•${NC} Type ${BOLD}LOG report${NC} to generate activity report"
    echo ""
}

# Variable and dataget detection system
detect_variables() {
    local variables=()
    
    # Scan memory files for $variables
    if [[ -d "$UMEMORY" ]]; then
        while IFS= read -r var; do
            variables+=("$var")
        done < <(grep -ho '\$[A-Za-z_][A-Za-z0-9_]*' "$UMEMORY"/*.md 2>/dev/null | sort -u | head -20)
    fi
    
    # Scan template files for $variables
    if [[ -d "$UTEMPLATE" ]]; then
        while IFS= read -r var; do
            variables+=("$var")
        done < <(grep -ho '\$[A-Za-z_][A-Za-z0-9_]*' "$UTEMPLATE"/*.md 2>/dev/null | sort -u | head -20)
    fi
    
    # Return unique variables
    printf '%s\n' "${variables[@]}" | sort -u
}

# Enhanced dataget processing with variable prediction
process_dataget() {
    local input="$1"
    local variables=()
    
    # Detect available variables
    mapfile -t variables < <(detect_variables)
    
    # If input contains partial variable, suggest completions
    if [[ "$input" == *'$'* ]]; then
        local partial_var=$(echo "$input" | grep -o '\$[A-Za-z_]*$' | tail -1)
        if [[ -n "$partial_var" ]]; then
            echo -e "\n${CYAN}💡 Available Variables:${NC}"
            for var in "${variables[@]}"; do
                if [[ "$var" == "$partial_var"* ]]; then
                    echo -e "  ${YELLOW}$var${NC}"
                fi
            done
            echo ""
        fi
    fi
    
    # Process the input normally
    echo "$input"
}

# Intelligent input system with autocomplete and prediction
intelligent_input() {
    local prompt="${1:-${RAINBOW_CYAN}WHIRL${NC}> }"
    local input=""
    local suggestions=()
    local suggestion_index=0
    local cursor_pos=0
    
    # Build command database
    local commands=("HELP" "STATUS" "DASH" "RESIZE" "DESTROY" "SETUP" "EXIT" 
                   "MEMORY list" "MEMORY view" "MEMORY search"
                   "MISSION list" "MISSION create" "MISSION complete"
                   "LOG report" "LOG stats" "LOG move"
                   "PACKAGE list" "PACKAGE install" "PACKAGE info"
                   "DEV status" "DEV report")
    
    # Build shortcode database
    local shortcodes=("[MEMORY:list]" "[MEMORY:view:]" "[MEMORY:search:]"
                     "[MISSION:list]" "[MISSION:create:]" "[MISSION:complete:]"
                     "[LOG:report]" "[LOG:stats]" "[LOG:move:]"
                     "[PACKAGE:list]" "[PACKAGE:install:]" "[PACKAGE:info:]"
                     "[DASH:live]" "[DEV:status]" "[DEV:report:]")
    
    # Get existing data for predictions
    local existing_missions=()
    local existing_files=()
    local existing_packages=("ripgrep" "fd" "bat" "glow" "micro" "jq")
    local existing_variables=()
    
    if [[ -d "$UMEMORY" ]]; then
        mapfile -t existing_missions < <(find "$UMEMORY" -name "*-mission.md" -exec basename {} .md \; | sed 's/^[0-9]*-//' | sed 's/-mission$//')
        mapfile -t existing_files < <(ls "$UMEMORY" 2>/dev/null | head -10)
    fi
    
    # Get available variables
    mapfile -t existing_variables < <(detect_variables)
    
    # Smart prediction based on input
    predict_input() {
        local current_input="$1"
        suggestions=()
        
        # If input starts with [, show shortcode options
        if [[ "$current_input" == "["* ]]; then
            for shortcode in "${shortcodes[@]}"; do
                if [[ "$shortcode" == "$current_input"* ]]; then
                    suggestions+=("$shortcode")
                fi
            done
        # Command prediction
        elif [[ -n "$current_input" ]]; then
            # Match commands
            for cmd in "${commands[@]}"; do
                if [[ "$cmd" == "$current_input"* ]] || [[ "${cmd,,}" == "${current_input,,}"* ]]; then
                    suggestions+=("$cmd")
                fi
            done
            
            # Context-aware suggestions
            case "$current_input" in
                *"view "*|*"view:")
                    for file in "${existing_files[@]}"; do
                        suggestions+=("${current_input%view*}view $file")
                    done
                    ;;
                *"complete "*|*"complete:")
                    for mission in "${existing_missions[@]}"; do
                        suggestions+=("${current_input%complete*}complete $mission")
                    done
                    ;;
                *"install "*|*"install:")
                    for pkg in "${existing_packages[@]}"; do
                        suggestions+=("${current_input%install*}install $pkg")
                    done
                    ;;
                *'$'*)
                    # Variable suggestions
                    local partial_var=$(echo "$current_input" | grep -o '\$[A-Za-z_]*$')
                    for var in "${existing_variables[@]}"; do
                        if [[ "$var" == "$partial_var"* ]]; then
                            suggestions+=("${current_input%\$*}$var")
                        fi
                    done
                    ;;
            esac
        else
            # Default suggestions when no input
            suggestions=("HELP" "STATUS" "DASH" "MEMORY list" "MISSION list" "[MEMORY:list]")
        fi
        
        # Limit suggestions
        if [[ ${#suggestions[@]} -gt 8 ]]; then
            suggestions=("${suggestions[@]:0:8}")
        fi
    }
    
    # Display suggestions
    show_suggestions() {
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            echo -e "\n${CYAN}💡 Suggestions:${NC}"
            for i in "${!suggestions[@]}"; do
                if [[ $i -eq $suggestion_index ]]; then
                    echo -e "  ${YELLOW}▶ ${suggestions[$i]}${NC}"
                else
                    echo -e "  ${BLUE}  ${suggestions[$i]}${NC}"
                fi
            done
            echo ""
        fi
    }
    
    # Clear suggestions display
    clear_suggestions() {
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            local lines_to_clear=$((${#suggestions[@]} + 2))
            for ((i=0; i<lines_to_clear; i++)); do
                echo -e "\033[A\033[K"
            done
        fi
    }
    
    echo -ne "$prompt"
    
    while true; do
        # Get current input and update predictions
        predict_input "$input"
        
        # Show suggestions if we have any
        if [[ ${#suggestions[@]} -gt 0 ]]; then
            show_suggestions
            echo -ne "$prompt$input"
        fi
        
        # Read single character
        read -rsn1 char
        
        case "$char" in
            # Enter key
            "")
                clear_suggestions
                if [[ ${#suggestions[@]} -gt 0 && -n "${suggestions[$suggestion_index]}" ]]; then
                    # Use selected suggestion
                    input="${suggestions[$suggestion_index]}"
                fi
                echo ""
                echo "$input"
                return 0
                ;;
            # Tab key - autocomplete with first suggestion
            $'\t')
                if [[ ${#suggestions[@]} -gt 0 ]]; then
                    clear_suggestions
                    input="${suggestions[0]}"
                    echo -ne "\r$prompt$input"
                fi
                ;;
            # Up arrow - previous suggestion
            $'\033')
                read -rsn2 -t 0.1 arrow_key
                case "$arrow_key" in
                    "[A") # Up arrow
                        if [[ ${#suggestions[@]} -gt 0 ]]; then
                            ((suggestion_index--))
                            if [[ $suggestion_index -lt 0 ]]; then
                                suggestion_index=$((${#suggestions[@]} - 1))
                            fi
                            clear_suggestions
                            echo -ne "\r$prompt$input"
                        fi
                        ;;
                    "[B") # Down arrow
                        if [[ ${#suggestions[@]} -gt 0 ]]; then
                            ((suggestion_index++))
                            if [[ $suggestion_index -ge ${#suggestions[@]} ]]; then
                                suggestion_index=0
                            fi
                            clear_suggestions
                            echo -ne "\r$prompt$input"
                        fi
                        ;;
                    "[C") # Right arrow - accept suggestion
                        if [[ ${#suggestions[@]} -gt 0 ]]; then
                            clear_suggestions
                            input="${suggestions[$suggestion_index]}"
                            echo -ne "\r$prompt$input"
                        fi
                        ;;
                esac
                ;;
            # Backspace
            $'\177'|$'\b')
                if [[ ${#input} -gt 0 ]]; then
                    clear_suggestions
                    input="${input%?}"
                    suggestion_index=0
                    echo -ne "\r$prompt$input\033[K"
                fi
                ;;
            # Ctrl+C
            $'\003')
                clear_suggestions
                echo ""
                return 130
                ;;
            # Regular character
            *)
                clear_suggestions
                input+="$char"
                suggestion_index=0
                echo -ne "\r$prompt$input"
                ;;
        esac
    done
}

# Enhanced shortcode browser
browse_shortcodes() {
    local category="${1:-all}"
    
    echo -e "\n${YELLOW}🔧 Shortcode Browser${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    case "$category" in
        memory|MEMORY)
            echo -e "${CYAN}🧠 Memory Shortcuts:${NC}"
            echo "  [MEMORY:list] - List all memory files"
            echo "  [MEMORY:view:filename] - View specific file"
            echo "  [MEMORY:search:term] - Search memory"
            ;;
        mission|MISSION)
            echo -e "${PURPLE}🎯 Mission Shortcuts:${NC}"
            echo "  [MISSION:list] - List all missions"
            echo "  [MISSION:create:name] - Create new mission"
            echo "  [MISSION:complete:name] - Complete mission"
            ;;
        package|PACKAGE)
            echo -e "${GREEN}📦 Package Shortcuts:${NC}"
            echo "  [PACKAGE:list] - Show available packages"
            echo "  [PACKAGE:install:name] - Install package"
            echo "  [PACKAGE:info:name] - Package information"
            ;;
        log|LOG)
            echo -e "${YELLOW}📝 Logging Shortcuts:${NC}"
            echo "  [LOG:report] - Generate daily report"
            echo "  [LOG:stats] - Show statistics"
            echo "  [LOG:move:command] - Log a command"
            ;;
        dash|DASH)
            echo -e "${BLUE}📊 Dashboard Shortcuts:${NC}"
            echo "  [DASH:live] - Live dashboard mode"
            ;;
        all|*)
            echo -e "${BOLD}📋 All Available Shortcodes:${NC}"
            echo ""
            browse_shortcodes "memory"
            echo ""
            browse_shortcodes "mission"
            echo ""
            browse_shortcodes "package"
            echo ""
            browse_shortcodes "log"
            echo ""
            browse_shortcodes "dash"
            ;;
    esac
    
    echo ""
    echo -e "${CYAN}💡 Tips:${NC}"
    echo "  • Type '[' to see shortcode suggestions"
    echo "  • Use Tab to autocomplete"
    echo "  • Use arrow keys to navigate suggestions"
    echo "  • Type 'shortcuts' to see this browser again"
    echo ""
}

# WHIRL prompt with intelligent input
show_whirl_prompt() {
    intelligent_input "${RAINBOW_CYAN}WHIRL${NC}> "
}
# Show status
show_status() {
    log_header "uDOS v1.2 System Status"
    
    echo "📍 Location: $UHOME"
    echo "🧠 Memory: Flat structure ($(find "$UMEMORY" -type f | wc -l) files)"
    echo "📋 Missions: $(find "$UMEMORY" -name "*-mission.md" | wc -l)"
    echo "📊 Logs: $(find "$UMEMORY" -name "*-log-*.md" | wc -l)"
    echo "🎯 Version: $VERSION"
    
    if [[ -f "$UMEMORY/identity.md" ]]; then
        local user=$(grep -E '\*\*Name\*\*:|\*\*Name:\*\*|Name:' "$UMEMORY/identity.md" | cut -d':' -f2 | xargs)
        local role=$(grep -E '\*\*Role\*\*:|\*\*Role:\*\*|Role:' "$UMEMORY/identity.md" | cut -d':' -f2 | xargs)
        echo "👤 User: $user ($role)"
    fi
    
    echo ""
}

# Show help
show_help() {
    log_header "uDOS v1.2 Command Reference"
    
    cat << 'EOF'
## Core Commands
- `HELP` - Show this help
- `STATUS` - System status and stats  
- `DASH` - Live dashboard with real-time stats
- `RESIZE` - Terminal size optimizer with intelligent recommendations
- `SHORTCUTS` - Browse available shortcodes and smart input features
- `DESTROY` - Reset system (requires confirmation)
- `SETUP` - Run first-time setup
- `EXIT` - Exit uDOS

## Memory Commands
- `MEMORY list` - Show all memory files
- `MEMORY view <file>` - View memory file
- `MEMORY search <term>` - Search memory

## Mission Commands  
- `MISSION list` - Show missions
- `MISSION create <name>` - Create new mission
- `MISSION complete <name>` - Complete mission

## Logging Commands
- `LOG report` - Generate daily report
- `LOG stats` - Show statistics
- `LOG move <command>` - Log a command

## Package Commands
- `PACKAGE list` - Show available packages
- `PACKAGE install <name>` - Install package
- `PACKAGE info <name>` - Package information

## Development Commands
- `DEV report <type>` - Create development report
- `DEV status` - Development system status
- `DEV migrate <component>` - Migration tools

## Shortcode Format
- `[COMMAND:args]` - Process shortcode
- `[MEMORY:list]` - List memory files
- `[MISSION:create:name]` - Create mission
- `[PACKAGE:install:name]` - Install package
- `[DASH:live]` - Live dashboard mode

EOF
}

# DESTROY command - complete system reset
handle_destroy() {
    log_header "🧹 DESTROY - Complete System Reset"
    log_warning "This will PERMANENTLY DELETE all uDOS data!"
    echo ""
    echo -e "${RED}This action will remove:${NC}"
    echo -e "${RED}• All memory files${NC}"
    echo -e "${RED}• All missions and logs${NC}"
    echo -e "${RED}• User identity and settings${NC}"
    echo -e "${RED}• All personal data${NC}"
    echo ""
    echo -ne "${BOLD}${RED}Type 'CONFIRM DESTROY' to proceed: ${NC}"
    read -r confirmation
    
    if [[ "$confirmation" == "CONFIRM DESTROY" ]]; then
        log_info "Initiating system destruction..."
        
        # Remove user data
        rm -rf "$UMEMORY"
        rm -rf "$UDEV"
        
        # Clear any cached data
        rm -rf "$UHOME/.cache" 2>/dev/null
        
        log_success "System destroyed successfully"
        log_info "Restarting fresh setup..."
        
        # Force fresh setup
        init_directories
        setup_user
    else
        log_info "Destruction cancelled"
    fi
}

# Process shortcode
process_shortcode() {
    local shortcode="$1"
    
    # Extract command and args from [COMMAND:args] format
    local cmd=$(echo "$shortcode" | sed -E 's/^\[([^:]+):.*\]$/\1/')
    local args=$(echo "$shortcode" | sed -E 's/^\[[^:]+:(.*)\]$/\1/')
    
    case "$cmd" in
        MEMORY)
            handle_memory "$args"
            ;;
        MISSION)
            handle_mission "$args"
            ;;
        PACKAGE)
            handle_package "$args"
            ;;
        LOG)
            handle_log "$args"
            ;;
        DASH)
            handle_dash "$args"
            ;;
        DEV)
            handle_dev "$args"
            ;;
        *)
            log_error "Unknown shortcode command: $cmd"
            ;;
    esac
}

# Handle dash commands
handle_dash() {
    local subcmd="$1"
    
    case "$subcmd" in
        live)
            log_info "Starting live dashboard..."
            while true; do
                clear
                show_dashboard
                echo ""
                echo -e "${CYAN}Press Ctrl+C to exit live mode${NC}"
                sleep 5
            done
            ;;
        *)
            show_dashboard
            ;;
    esac
}

# Handle memory commands
handle_memory() {
    local subcmd="$1"
    
    case "$subcmd" in
        list)
            log_info "Memory files:"
            ls -la "$UMEMORY" | grep -v "^total"
            ;;
        view:*)
            local file=$(echo "$subcmd" | cut -d':' -f2)
            if [[ -f "$UMEMORY/$file" ]]; then
                cat "$UMEMORY/$file"
            else
                log_error "File not found: $file"
            fi
            ;;
        search:*)
            local term=$(echo "$subcmd" | cut -d':' -f2)
            log_info "Searching for: $term"
            grep -r "$term" "$UMEMORY" || log_warning "No matches found"
            ;;
        *)
            log_error "Unknown memory command: $subcmd"
            ;;
    esac
}

# Handle mission commands
handle_mission() {
    local subcmd="$1"
    
    case "$subcmd" in
        list)
            log_info "Missions:"
            find "$UMEMORY" -name "*-mission.md" -exec basename {} \; | sort
            ;;
        create:*)
            local name=$(echo "$subcmd" | cut -d':' -f2)
            local mission_file="$UMEMORY/$(printf "%03d" $(($(find "$UMEMORY" -name "*-mission.md" | wc -l) + 1)))-${name}-mission.md"
            
            cat > "$mission_file" << EOF
# 🎯 Mission: $name

**Created**: $(date +%Y-%m-%d)  
**Status**: Active  
**Type**: User Created

## Objective

[Describe mission objective here]

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Progress

*Mission started*

---

**Status**: Active 🎯
EOF
            log_success "Mission created: $(basename "$mission_file")"
            ;;
        complete:*)
            local name=$(echo "$subcmd" | cut -d':' -f2)
            local mission_file=$(find "$UMEMORY" -name "*${name}*mission.md" | head -1)
            
            if [[ -f "$mission_file" ]]; then
                # Create legacy file
                local legacy_file="$UMEMORY/legacy-${name}-$(date +%Y%m%d-%H%M%S)-E001-UTC.md"
                
                cat > "$legacy_file" << EOF
# 💎 Device Legacy: $name

**Preserved**: $(date +%Y-%m-%d %H:%M:%S)
**Original Mission**: $name
**Status**: Completed

## Legacy Value

This completed mission has been preserved as device legacy.

## Mission Archive

$(cat "$mission_file")

---

## ✅ Mission Completed

**Completion Date**: $(date +%Y-%m-%d)
**Summary**: Mission successfully completed and archived.
EOF
                
                rm "$mission_file"
                log_success "Mission completed and archived: $(basename "$legacy_file")"
            else
                log_error "Mission not found: $name"
            fi
            ;;
        *)
            log_error "Unknown mission command: $subcmd"
            ;;
    esac
}

# Handle package commands  
handle_package() {
    local subcmd="$1"
    
    case "$subcmd" in
        list)
            log_info "Available packages:"
            echo "- ripgrep (fast text search)"
            echo "- fd (fast file finder)"
            echo "- bat (syntax-highlighted viewer)"
            echo "- glow (markdown renderer)"
            echo "- micro (terminal editor)"
            echo "- jq (JSON processor)"
            ;;
        install:*)
            local pkg=$(echo "$subcmd" | cut -d':' -f2)
            log_info "Installing package: $pkg"
            
            if command -v brew >/dev/null 2>&1; then
                brew install "$pkg" 2>/dev/null || log_warning "Package $pkg may already be installed"
                echo "$(date): Installed $pkg" >> "$UMEMORY/package-install.log"
                log_success "Package installed: $pkg"
            else
                log_error "Package manager not available"
            fi
            ;;
        info:*)
            local pkg=$(echo "$subcmd" | cut -d':' -f2)
            case "$pkg" in
                ripgrep) echo "ripgrep: Ultra-fast text search tool" ;;
                fd) echo "fd: Fast file finder, modern replacement for find" ;;
                bat) echo "bat: Syntax-highlighted file viewer with Git integration" ;;
                *) log_error "No info available for: $pkg" ;;
            esac
            ;;
        *)
            log_error "Unknown package command: $subcmd"
            ;;
    esac
}

# Handle log commands
handle_log() {
    local subcmd="$1"
    
    case "$subcmd" in
        report)
            if [[ -f "$SCRIPT_DIR/log.sh" ]]; then
                bash "$SCRIPT_DIR/log.sh" report
            else
                log_error "Logging system not available"
            fi
            ;;
        stats)
            if [[ -f "$SCRIPT_DIR/log.sh" ]]; then
                bash "$SCRIPT_DIR/log.sh" stats
            else
                log_error "Logging system not available"
            fi
            ;;
        move:*)
            local command=$(echo "$subcmd" | cut -d':' -f2)
            if [[ -f "$SCRIPT_DIR/log.sh" ]]; then
                bash "$SCRIPT_DIR/log.sh" move "$command"
            fi
            ;;
        *)
            log_error "Unknown log command: $subcmd"
            ;;
    esac
}

# Handle dev commands
handle_dev() {
    local subcmd="$1"
    
    case "$subcmd" in
        status)
            log_info "Development System Status:"
            echo "📁 Reports: $(find "$UDEV/reports" -name "*.md" | wc -l)"
            echo "🔄 Migrations: $(find "$UDEV/migrations" -name "*.md" | wc -l)"
            echo "🔍 Analysis: $(find "$UDEV/analysis" -name "*.md" | wc -l)"
            ;;
        report:*)
            local type=$(echo "$subcmd" | cut -d':' -f2)
            local timestamp=$(date +%Y%m%d_%H%M%S)
            local report_file="$UDEV/reports/${type^^}_REPORT_${timestamp}.md"
            
            cat > "$report_file" << EOF
# 📊 ${type^^} Report

**Generated**: $(date +%Y-%m-%d)  
**Type**: Development Report  
**Status**: Draft

## Summary

[Report summary here]

## Details

[Detailed information]

## Action Items

- [ ] Item 1
- [ ] Item 2

---

*Generated by uDOS v1.2 Development System*
EOF
            log_success "Report created: $(basename "$report_file")"
            ;;
        *)
            log_error "Unknown dev command: $subcmd"
            ;;
    esac
}

# Main command processing
main() {
    # Initialize system
    init_directories
    
    # Show rainbow ASCII art
    show_rainbow_ascii
    
    # Terminal size optimization (on first run or if requested)
    if [[ "${1:-}" == "--resize" ]] || [[ ! -f "$UMEMORY/terminal_size.conf" ]]; then
        recommend_terminal_size
        # Save preference for next time
        mkdir -p "$UMEMORY"
        detect_terminal_size
        echo "${CURRENT_COLS}x${CURRENT_ROWS}" > "$UMEMORY/terminal_size.conf"
    fi
    
    # Authenticate user
    authenticate_user
    
    # Validate system integrity
    if ! validate_system; then
        log_warning "System validation failed - forcing setup"
        setup_user
    fi
    
    # Check for arguments
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        log_header "System Ready - Welcome to uDOS!"
        echo -e "${CYAN}💡 Smart Input Features:${NC}"
        echo -e "  • Type '[' to browse shortcodes"
        echo -e "  • Use Tab for autocomplete"
        echo -e "  • Arrow keys to navigate suggestions"
        echo -e "  • Type 'shortcuts' for full reference"
        echo ""
        
        # Check setup (hardened - always setup if files missing)
        check_setup
        
        while true; do
            input=$(show_whirl_prompt)
            
            # Skip empty input
            [[ -z "$input" ]] && continue
            
            # Handle exit commands
            if [[ "$input" =~ ^(exit|quit|bye)$ ]]; then
                log_success "Goodbye from uDOS v1.2! 👋"
                break
            fi
            
            # Process input
            process_input "$input"
        done
    else
        # Command mode
        process_input "$*"
    fi
}

# Process user input
process_input() {
    local input="$1"
    
    # Special case: just '[' shows shortcode browser
    if [[ "$input" == "[" ]]; then
        browse_shortcodes
        return
    fi
    
    # Handle shortcode format [COMMAND:args]
    if [[ "$input" =~ ^\[.*\]$ ]]; then
        process_shortcode "$input"
        return
    fi
    
    # Parse command and arguments
    local cmd=$(echo "$input" | awk '{print $1}')
    local args=$(echo "$input" | cut -d' ' -f2-)
    
    case "$cmd" in
        HELP|help)
            show_help
            ;;
        STATUS|status)
            show_status
            ;;
        DASH|dash)
            show_dashboard
            ;;
        RESIZE|resize)
            recommend_terminal_size
            ;;
        SHORTCUTS|shortcuts)
            browse_shortcodes
            ;;
        DESTROY|destroy)
            handle_destroy
            ;;
        SETUP|setup)
            setup_user
            ;;
        MEMORY)
            handle_memory "$args"
            ;;
        MISSION)
            handle_mission "$args"
            ;;
        PACKAGE)
            handle_package "$args"
            ;;
        LOG)
            handle_log "$args"
            ;;
        DEV)
            handle_dev "$args"
            ;;
        *)
            log_error "Unknown command: $cmd"
            echo "Type 'HELP' for available commands or '[' for shortcode browser"
            ;;
    esac
}

# Run main function
main "$@"
