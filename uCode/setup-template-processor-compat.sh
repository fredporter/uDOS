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
    bold "👤 User Information"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    get_user_input "Enter your username" "USERNAME" ""
    get_user_input "Enter your email (optional)" "EMAIL" ""
    get_user_input "Enter your full name (optional)" "FULLNAME" ""
    
    echo
    bold "🌍 Location & Time"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    get_user_input "Enter your location" "LOCATION" "Unknown"
    get_user_input "Enter your timezone" "TIMEZONE" "UTC"
    
    echo
    bold "⚙️ Preferences"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    get_user_input "Theme preference (default/dark/light)" "THEME" "default"
    get_user_input "Enable debug mode? (y/N)" "DEBUG" "N"
    get_user_input "Enable auto backup? (Y/n)" "BACKUP" "Y"
    
    # Process and save results
    process_setup_results
}

# Process setup results and create identity file
process_setup_results() {
    local username email fullname location timezone theme debug backup
    local identity_file="${UMEM}/user/identity.md"
    local preferences_file="${UMEM}/user/preferences.json"
    
    # Get all variables
    username=$(get_var "USERNAME")
    email=$(get_var "EMAIL")
    fullname=$(get_var "FULLNAME")
    location=$(get_var "LOCATION")
    timezone=$(get_var "TIMEZONE")
    theme=$(get_var "THEME")
    debug=$(get_var "DEBUG")
    backup=$(get_var "BACKUP")
    
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
**Full Name**: ${fullname:-Not provided}
**Email**: ${email:-Not provided}
**Location**: ${location:-Unknown}
**Timezone**: ${timezone:-UTC}

## 📅 Account Information

- **Created**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
- **Setup Method**: Template-based (Bash 3.2 Compatible)
- **Identity File**: $(basename "$identity_file")

## 🎭 User Role

**Role**: Wizard 🧙‍♂️  
**Access Level**: Full system access with development tools
**Capabilities**: Mission creation, code development, system administration

---

*This identity was generated using the uDOS template system v2.1*
EOF

    # Generate preferences file
    cat > "$preferences_file" << EOF
{
  "theme": "${theme:-default}",
  "debug": $(if [[ "${debug,,}" == "y" ]]; then echo "true"; else echo "false"; fi),
  "autoBackup": $(if [[ "${backup,,}" == "n" ]]; then echo "false"; else echo "true"; fi),
  "setupMethod": "template-bash32",
  "setupDate": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "version": "1.0"
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
