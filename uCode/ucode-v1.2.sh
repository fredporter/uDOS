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

# Check if first-time setup needed
check_setup() {
    if [[ ! -f "$UMEMORY/identity.md" ]]; then
        log_warning "First-time setup required"
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

# Show status
show_status() {
    log_header "uDOS v1.2 System Status"
    
    echo "📍 Location: $UHOME"
    echo "🧠 Memory: Flat structure ($(find "$UMEMORY" -type f | wc -l) files)"
    echo "📋 Missions: $(find "$UMEMORY" -name "*-mission.md" | wc -l)"
    echo "📊 Logs: $(find "$UMEMORY" -name "*-log-*.md" | wc -l)"
    echo "🎯 Version: $VERSION"
    
    if [[ -f "$UMEMORY/identity.md" ]]; then
        local user=$(grep "Name:" "$UMEMORY/identity.md" | cut -d':' -f2 | xargs)
        local role=$(grep "Role:" "$UMEMORY/identity.md" | cut -d':' -f2 | xargs)
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

EOF
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
        DEV)
            handle_dev "$args"
            ;;
        *)
            log_error "Unknown shortcode command: $cmd"
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
    
    # Check for arguments
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        log_header "uDOS v1.2 - Unified Command System"
        
        # Check setup
        check_setup
        
        while true; do
            echo -n "uDOS> "
            read -r input
            
            # Skip empty input
            [[ -z "$input" ]] && continue
            
            # Handle exit commands
            if [[ "$input" =~ ^(exit|quit|bye)$ ]]; then
                log_success "Goodbye!"
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
            echo "Type 'HELP' for available commands"
            ;;
    esac
}

# Run main function
main "$@"
