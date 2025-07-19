#!/bin/bash
# uDOS Template System - User Setup Processor v2.1 (bash 3.2 compatible)
# Processes user setup template with simplified variable handling

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
SETUP_TEMPLATE="${UHOME}/uTemplate/user-setup-template.md"
TEMP_DIR="${UMEM}/temp/setup-$$"
VARS_FILE="${TEMP_DIR}/setup_vars.txt"

# Color output helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }
dim() { echo -e "\033[2m$1\033[0m"; }

# Create temp directory
mkdir -p "$TEMP_DIR"

# Check if template exists
if [[ ! -f "$SETUP_TEMPLATE" ]]; then
    yellow "⚠️ Template file not found: $SETUP_TEMPLATE"
    yellow "🔄 Falling back to legacy setup..."
    exit 1
fi

# Initialize variables file
> "$VARS_FILE"

# Bash 3.2 compatible variable handling
set_var() {
    local name="$1"
    local value="$2"
    echo "${name}=${value}" >> "$VARS_FILE"
}

get_var() {
    local name="$1"
    grep "^${name}=" "$VARS_FILE" 2>/dev/null | cut -d'=' -f2- || echo ""
}

# Helper functions
show_intro() {
    if [[ -f "$SETUP_TEMPLATE" ]]; then
        local intro
        intro=$(sed -n '/\[SETUP_INTRO\]/,/\[\/SETUP_INTRO\]/p' "$SETUP_TEMPLATE" | sed '1d;$d')
        echo
        bold "$(echo "$intro" | head -n1)"
        echo "$(echo "$intro" | tail -n+2)"
        echo
    fi
}

# Simple input processing for bash 3.2
get_user_input() {
    local prompt="$1"
    local variable="$2"
    local default="$3"
    local value
    
    if [[ -n "$default" ]]; then
        echo -n "${prompt} [${default}]: "
    else
        echo -n "${prompt}: "
    fi
    
    read -r value
    
    if [[ -z "$value" && -n "$default" ]]; then
        value="$default"
    fi
    
    set_var "$variable" "$value"
    echo "$value"
}

# Main setup process
main() {
    blue "🎭 uDOS Template-Based Setup (Bash 3.2 Compatible)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    show_intro
    
    # Core user information
    bold "👤 Identity Information"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    get_user_input "Enter your username (required)" "USERNAME" "$USER"
    get_user_input "Enter your password (blank for none)" "PASSWORD" ""
    
    echo
    bold "🌍 Location & Time" 
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local default_timezone=$(timedatectl show --property=Timezone --value 2>/dev/null || date +%Z)
    get_user_input "Enter your timezone" "TIMEZONE" "$default_timezone"
    get_user_input "Enter your location" "LOCATION" "Unknown"
    
    echo
    bold "⚙️ System Preferences"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    get_user_input "Theme preference (default/dark/light/auto)" "THEME" "default" 
    get_user_input "Enable debug mode? (y/N)" "DEBUG_MODE" "N"
    get_user_input "Enable auto backup? (Y/n)" "AUTO_BACKUP" "Y"
    get_user_input "Enable OK Companion? (Y/n)" "AI_COMPANION" "Y"
    
    echo
    bold "🎯 Development Preferences"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    get_user_input "Default user role (wizard/sorcerer/ghost/drone/imp)" "DEFAULT_ROLE" "wizard"
    get_user_input "Auto install packages? (Y/n)" "AUTO_PACKAGES" "Y"
    get_user_input "Install VS Code extension? (Y/n)" "VSCODE_EXTENSION" "Y"
    
    # Process and save results
    process_setup_results
}

# Process setup results and create identity file
process_setup_results() {
    local username password location timezone theme debug_mode auto_backup ai_companion default_role auto_packages vscode_extension
    local identity_file="${UMEM}/user/identity.md"
    local preferences_file="${UMEM}/user/preferences.json"
    
    # Get all variables  
    username=$(get_var "USERNAME")
    password=$(get_var "PASSWORD")
    location=$(get_var "LOCATION")
    timezone=$(get_var "TIMEZONE")
    theme=$(get_var "THEME")
    debug_mode=$(get_var "DEBUG_MODE")
    auto_backup=$(get_var "AUTO_BACKUP")
    ai_companion=$(get_var "AI_COMPANION")
    default_role=$(get_var "DEFAULT_ROLE")
    auto_packages=$(get_var "AUTO_PACKAGES")
    vscode_extension=$(get_var "VSCODE_EXTENSION")
    
    # Create user directory
    mkdir -p "${UMEM}/user"
    
    # Generate identity file
    cat > "$identity_file" << EOF
---
title: "User Identity"
created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
updated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
version: "1.0"
template: "user-identity"
---

# 👤 User Identity

**Username**: ${username:-Unknown}
**Created**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Version**: v1.0.0
**Architecture**: Single-User Installation

## Profile Information
- **Role**: ${default_role:-wizard}
- **Setup**: Complete

## Location & Time  
- **Location**: ${location:-Unknown}
- **Timezone**: ${timezone:-UTC}

## System Preferences
- **Theme**: ${theme:-default}
- **Debug Mode**: ${debug_mode:-N}
- **Auto Backup**: ${auto_backup:-Y}
- **OK Companion**: ${ai_companion:-Y}
- **Auto Install Packages**: ${auto_packages:-Y}
- **VS Code Extension**: ${vscode_extension:-Y}

## System Paths
- **uDOS Home**: $UHOME
- **User Memory**: $UMEM
- **Setup Timestamp**: $(date '+%s')

## Installation
- **Type**: Single-user bound
- **Setup Method**: Template-based (Bash 3.2 Compatible)
- **Privacy Mode**: Local-Only

---

*Identity generated by uDOS Template System v2.0 (Compatible)*
EOF

    # Generate preferences JSON
    cat > "$preferences_file" << EOF
{
  "user": {
    "username": "${username:-Unknown}",
    "location": "${location:-Unknown}",
    "timezone": "${timezone:-UTC}",
    "role": "${default_role:-wizard}"
  },
  "system": {
    "theme": "${theme:-default}",
    "debug_mode": "${debug_mode:-N}",
    "auto_backup": "${auto_backup:-Y}",
    "ai_companion": "${ai_companion:-Y}",
    "auto_packages": "${auto_packages:-Y}",
    "vscode_extension": "${vscode_extension:-Y}"
  },
  "metadata": {
    "created": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "setup_method": "template_bash32_compatible",
    "version": "1.0"
  }
}
EOF

    echo
    green "✅ Setup completed successfully!"
    echo
    echo "📁 Files created:"
    echo "   Identity: $identity_file"
    echo "   Preferences: $preferences_file"
    echo
    
    # Clean up temp directory
    rm -rf "$TEMP_DIR"
    
    green "🎉 Welcome to uDOS, ${username}!"
}

# Error handling
cleanup() {
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}

trap cleanup EXIT

# Run main setup
main "$@"
