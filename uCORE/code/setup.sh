#!/bin/bash
# uDOS System Setup
# Variable collection and profile generation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
UMEMORY_DIR="$UDOS_ROOT/uMEMORY"
VARIABLE_MANAGER="$UDOS_ROOT/uCORE/code/variable-manager.sh"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if first run
check_first_run() {
    local installation_file="$UMEMORY_DIR/user/installation.md"
    local user_file="$UDOS_ROOT/sandbox/user.md"

    if [[ ! -f "$installation_file" ]] || [[ ! -f "$user_file" ]]; then
        return 0  # First run
    else
        return 1  # Not first run
    fi
}

# Run installation STORY to collect system variables
run_installation_story() {
    log_info "Running installation setup STORY..."

    # Create installation STORY if it doesn't exist
    create_installation_story

    # Execute STORY using variable manager
    if [[ -x "$VARIABLE_MANAGER" ]]; then
        "$VARIABLE_MANAGER" story installation-setup
        log_success "Installation STORY completed"
    else
        log_error "Variable manager not found"
        return 1
    fi
}

# Run user onboarding STORY
run_user_onboarding() {
    log_info "Running user onboarding STORY..."

    if [[ -x "$VARIABLE_MANAGER" ]]; then
        "$VARIABLE_MANAGER" story user-onboarding
        log_success "User onboarding completed"
    else
        log_error "Variable manager not found"
        return 1
    fi
}

# Create installation STORY if missing
create_installation_story() {
    local story_file="$UMEMORY_DIR/system/stories/installation-setup.json"

    if [[ ! -f "$story_file" ]]; then
        log_info "Creating installation setup STORY..."

        mkdir -p "$(dirname "$story_file")"

        cat > "$story_file" << 'EOF'
{
    "metadata": {
        "name": "installation-setup",
        "title": "uDOS Installation Configuration",
        "type": "story",
        "created": "2025-08-26T00:00:00Z"
    },
    "story": {
        "introduction": "Let's configure your uDOS installation with the appropriate settings for your environment.",
        "context": "This will set up your installation profile, security settings, and system configuration.",
        "purpose": "Create installation.md with proper system variables"
    },
    "variables": [
        {
            "name": "INSTALLATION-TYPE",
            "type": "string",
            "description": "Type of installation",
            "required": true,
            "values": ["personal", "team", "enterprise", "development"],
            "prompt": "What type of uDOS installation is this?",
            "help": "Personal for individual use, Team for small groups, Enterprise for organizations"
        },
        {
            "name": "SECURITY-LEVEL",
            "type": "string",
            "description": "Security configuration level",
            "required": true,
            "values": ["basic", "standard", "enhanced", "maximum"],
            "prompt": "What security level do you need?",
            "help": "Basic for learning, Standard for most users, Enhanced for sensitive work"
        },
        {
            "name": "INSTALLATION-LIFESPAN",
            "type": "string",
            "description": "Expected installation duration",
            "required": true,
            "values": ["3 months", "6 months", "12 months", "24 months", "permanent"],
            "prompt": "How long will you use this installation?",
            "help": "This helps with backup retention and cleanup scheduling"
        },
        {
            "name": "MULTI-USER",
            "type": "string",
            "description": "Multi-user support",
            "required": true,
            "values": ["true", "false"],
            "prompt": "Will multiple users access this installation?",
            "help": "Affects user management and security settings"
        },
        {
            "name": "NETWORK-MODE",
            "type": "string",
            "description": "Network configuration",
            "required": true,
            "values": ["local", "shared", "remote", "isolated"],
            "prompt": "What network access do you need?",
            "help": "Local for single machine, Shared for network access, Remote for internet"
        }
    ],
    "flow": {
        "sequential": true,
        "allow_skip": false,
        "validate_each": true
    }
}
EOF

        log_success "Installation STORY created"
    fi
}

# Generate installation.md from variables
generate_installation_profile() {
    log_info "Generating installation profile..."

    local installation_file="$UMEMORY_DIR/user/installation.md"
    local template_file="$UMEMORY_DIR/templates/installation.template.md"

    # Ensure template exists
    if [[ ! -f "$template_file" ]]; then
        log_error "Installation template not found: $template_file"
        return 1
    fi

    # Create installation file from template with variable substitution
    cp "$template_file" "$installation_file"

    # Replace template variables with actual values
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local install_id="uDOS-$(date '+%Y%m%d')-$(openssl rand -hex 2)"
    local platform="$(uname -s) ($(uname -m))"

    # Get variables from variable manager
    local installation_type="$("$VARIABLE_MANAGER" get INSTALLATION-TYPE 2>/dev/null || echo "personal")"
    local security_level="$("$VARIABLE_MANAGER" get SECURITY-LEVEL 2>/dev/null || echo "standard")"
    local lifespan="$("$VARIABLE_MANAGER" get INSTALLATION-LIFESPAN 2>/dev/null || echo "12 months")"

    # Perform template substitution
    sed -i.bak \
        -e "s/{GENERATION-TIMESTAMP}/$timestamp/g" \
        -e "s/{INSTALLATION-ID}/$install_id/g" \
        -e "s/{INSTALLATION-TYPE}/$installation_type/g" \
        -e "s/{PLATFORM}/$platform/g" \
        -e "s/{SECURITY-LEVEL}/$security_level/g" \
        -e "s/{INSTALLATION-LIFESPAN}/$lifespan/g" \
        "$installation_file"

    rm -f "$installation_file.bak"
    log_success "Installation profile generated: $installation_file"
    local eol_date
    case "$lifespan" in
        "3 months") eol_date=$(date -d "+3 months" '+%Y-%m-%d' 2>/dev/null || date -v+3m '+%Y-%m-%d') ;;
        "6 months") eol_date=$(date -d "+6 months" '+%Y-%m-%d' 2>/dev/null || date -v+6m '+%Y-%m-%d') ;;
        "12 months") eol_date=$(date -d "+12 months" '+%Y-%m-%d' 2>/dev/null || date -v+12m '+%Y-%m-%d') ;;
        "24 months") eol_date=$(date -d "+24 months" '+%Y-%m-%d' 2>/dev/null || date -v+24m '+%Y-%m-%d') ;;
        *) eol_date="indefinite" ;;
    esac

    cat > "$installation_file" << EOF
# uDOS Installation Profile

**Installation ID**: $install_id
**Version**: v1.0.4.1
**Type**: $installation_type
**Created**: $timestamp
**Platform**: $platform
**Lifespan**: $lifespan

> **Status**: Active
> **Mode**: $security_level
> **Multi-User**: $multi_user
> **Network**: $network_mode
> **EOL Date**: $eol_date

---

## 📋 Installation Configuration

### 🏗️ Installation Type
**Type**: $installation_type
**Description**: $(get_installation_description "$installation_type")

### 🔐 Security Level
**Security Mode**: $security_level
**Authentication**: $(get_auth_mode "$security_level")
**Encryption**: $(get_encryption_mode "$security_level")

### 👥 User Management
**Multi-User**: $multi_user
**Max Users**: $(get_max_users "$multi_user")
**Default Role**: $(get_default_role "$installation_type")

### 🌐 Network Configuration
**Network Mode**: $network_mode
**Sharing Enabled**: $(get_sharing_status "$network_mode")
**Remote Access**: $(get_remote_access "$network_mode")

### 📅 Installation Lifespan
**Planned Duration**: $lifespan
**Start Date**: $timestamp
**Estimated Completion**: $eol_date
**Current Phase**: active
**EOL Warning**: $(get_eol_warning "$lifespan")
**Legacy Preparation**: $(get_legacy_prep "$lifespan")

---

## 🎯 Available Roles

### $installation_type Installation
$(get_available_roles "$installation_type")

---

## 📊 System Capabilities

### 🔧 Core Features
- **uCORE Utilities**: true
- **Template System**: true
- **Geographic Data**: true
- **Logging System**: true

### 🚀 Advanced Features
- **uSCRIPT Engine**: true
- **Python Environment**: true
- **Network Server**: $(get_network_server_status "$network_mode")
- **UI Components**: true

### 🔌 Extensions
- **Extension System**: true
- **VS Code Integration**: true
- **Git Integration**: true
- **Package Management**: true

---

## 🏠 Directory Structure

### 📁 Core Directories
\`\`\`
uDOS/
├── uCORE/           Core system and utilities
├── uMEMORY/         Persistent data and templates
├── sandbox/         Active workspace
├── uSCRIPT/         Advanced scripting engine
├── uNETWORK/        Network and sharing features
└── extensions/      Extension ecosystem
\`\`\`

### 🔒 Data Separation
- **System Code**: uCORE (read-only in production)
- **Active Work**: sandbox (user workspace, logs)
- **Permanent Storage**: uMEMORY (archived data)
- **Development**: dev/ (wizard role only)

---

## 🚀 Installation Summary

**Installation ID**: $install_id
**Created**: $timestamp
**Platform**: $platform
**Version**: v1.0.4.1
**Type**: $installation_type
**Security**: $security_level
**Users**: $(get_user_summary "$multi_user")

### 🎯 Next Steps
1. Complete user setup (if required)
2. Configure role permissions
3. Setup development environment
4. Initialize data systems
5. Test core functionality

---

*Installation profile generated by uDOS v1.0.4.1 setup system*
EOF

    log_success "Installation profile generated: $installation_file"
}

# Generate user.md from variables
generate_user_profile() {
    log_info "Generating user profile..."

    local user_file="$UDOS_ROOT/sandbox/user.md"
    local template_file="$UDOS_ROOT/sandbox/templates/user.template.md"

    # Ensure template exists
    if [[ ! -f "$template_file" ]]; then
        log_error "User template not found: $template_file"
        return 1
    fi

    mkdir -p "$(dirname "$user_file")"

    # Create user file from template
    cp "$template_file" "$user_file"

    # Get variables from variable manager
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local developer_name="$("$VARIABLE_MANAGER" get DEVELOPER-NAME 2>/dev/null || echo "User")"
    local user_role="$("$VARIABLE_MANAGER" get USER-ROLE 2>/dev/null || echo "GHOST")"
    local display_mode="$("$VARIABLE_MANAGER" get DISPLAY-MODE 2>/dev/null || echo "CLI")"
    local project_type="$("$VARIABLE_MANAGER" get PROJECT-TYPE 2>/dev/null || echo "learning")"

    # Perform template substitution
    sed -i.bak \
        -e "s/{GENERATION-TIMESTAMP}/$timestamp/g" \
        -e "s/{DEVELOPER-NAME}/$developer_name/g" \
        -e "s/{USER-ROLE}/$user_role/g" \
        -e "s/{DISPLAY-MODE}/$display_mode/g" \
        -e "s/{PROJECT-TYPE}/$project_type/g" \
        "$user_file"

    rm -f "$user_file.bak"
    log_success "User profile generated: $user_file"

    # Generate username from developer name
    local username=$(echo "$developer_name" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')

    cat > "$user_file" << EOF
# 🎭 uDOS User Identity

**Name**: $developer_name
**Username**: $username
**User ID**: $username
**Created**: $timestamp
**Version**: v1.0.4.1

## Identity & Contact
- **Display Name**: $developer_name
- **Role**: $user_role
- **Primary Projects**: $project_type
- **Location**: $(get_user_location)
- **Timezone**: $(get_user_timezone)

## System Configuration
- **Default Role**: $user_role
- **Display Mode**: $display_mode
- **Detail Level**: $detail_level
- **Development Mode**: $(get_dev_mode "$user_role")
- **Auto Backup**: true
- **Logging Level**: $(get_logging_level "$detail_level")

## Preferences
- **Theme**: Polaroid
- **Language**: English
- **Date Format**: YYYY-MM-DD
- **Time Format**: 24-hour

## File Organization
- **User ID**: $username
- **Created**: $timestamp
- **Profile Type**: $(get_profile_type "$user_role")

---

*Profile generated by uDOS v1.0.4.1 setup system*
EOF

    log_success "User profile generated: $user_file"

    # Also create role-specific current-role.conf
    echo "CURRENT_ROLE=\"$user_role\"" > "$UDOS_ROOT/sandbox/current-role.conf"
    log_success "Role configuration updated"
}

# Helper functions for template generation
get_installation_description() {
    case "$1" in
        "personal") echo "Full personal use installation" ;;
        "team") echo "Team collaboration installation" ;;
        "enterprise") echo "Enterprise-grade installation" ;;
        "development") echo "Development and testing installation" ;;
        *) echo "Standard installation" ;;
    esac
}

get_auth_mode() {
    case "$1" in
        "basic") echo "local" ;;
        "standard") echo "local" ;;
        "enhanced") echo "encrypted" ;;
        "maximum") echo "multi-factor" ;;
        *) echo "local" ;;
    esac
}

get_encryption_mode() {
    case "$1" in
        "basic") echo "disabled" ;;
        "standard") echo "enabled" ;;
        "enhanced") echo "enhanced" ;;
        "maximum") echo "maximum" ;;
        *) echo "enabled" ;;
    esac
}

get_max_users() {
    case "$1" in
        "true") echo "10" ;;
        "false") echo "1" ;;
        *) echo "1" ;;
    esac
}

get_default_role() {
    case "$1" in
        "personal") echo "Crypt" ;;
        "team") echo "Imp" ;;
        "enterprise") echo "Sorcerer" ;;
        "development") echo "Wizard" ;;
        *) echo "Ghost" ;;
    esac
}

get_sharing_status() {
    case "$1" in
        "local") echo "false" ;;
        "shared") echo "true" ;;
        "remote") echo "true" ;;
        "isolated") echo "false" ;;
        *) echo "false" ;;
    esac
}

get_remote_access() {
    case "$1" in
        "remote") echo "true" ;;
        *) echo "false" ;;
    esac
}

get_eol_warning() {
    case "$1" in
        "3 months") echo "2 weeks before completion" ;;
        "6 months") echo "1 month before completion" ;;
        "12 months") echo "2 months before completion" ;;
        "24 months") echo "3 months before completion" ;;
        *) echo "Not applicable" ;;
    esac
}

get_legacy_prep() {
    case "$1" in
        "3 months") echo "1 month before completion" ;;
        "6 months") echo "2 months before completion" ;;
        "12 months") echo "3 months before completion" ;;
        "24 months") echo "6 months before completion" ;;
        *) echo "Not applicable" ;;
    esac
}

get_available_roles() {
    case "$1" in
        "personal") echo "- **Ghost** - Demo/public access
- **Tomb** - Basic storage
- **Crypt** - Secure personal use
- **Drone** - Automation tasks
- **Knight** - Security operations
- **Imp** - Development tools
- **Sorcerer** - Advanced administration" ;;
        "team") echo "- **Imp** - Development tools
- **Sorcerer** - Team coordination
- **Wizard** - Full administration" ;;
        "enterprise") echo "- **Knight** - Security operations
- **Sorcerer** - Management roles
- **Wizard** - System administration" ;;
        "development") echo "- **All Roles** - Complete access for testing" ;;
        *) echo "- **Ghost** - Basic access" ;;
    esac
}

get_network_server_status() {
    case "$1" in
        "local") echo "false" ;;
        *) echo "true" ;;
    esac
}

get_user_summary() {
    case "$1" in
        "true") echo "Multi-user" ;;
        "false") echo "Single-user" ;;
        *) echo "Single-user" ;;
    esac
}

get_user_location() {
    # Try to get location from system or default
    echo "Local"
}

get_user_timezone() {
    # Get system timezone
    if command -v timedatectl >/dev/null 2>&1; then
        timedatectl show --property=Timezone --value 2>/dev/null || echo "UTC"
    elif [[ -f /etc/timezone ]]; then
        cat /etc/timezone
    else
        echo "UTC"
    fi
}

get_dev_mode() {
    case "$1" in
        "WIZARD") echo "true" ;;
        "SORCERER") echo "limited" ;;
        *) echo "false" ;;
    esac
}

get_logging_level() {
    case "$1" in
        "MINIMAL") echo "WARN" ;;
        "STANDARD") echo "INFO" ;;
        "DETAILED") echo "DEBUG" ;;
        "VERBOSE") echo "TRACE" ;;
        *) echo "INFO" ;;
    esac
}

get_profile_type() {
    case "$1" in
        "GHOST") echo "demo" ;;
        "TOMB"|"CRYPT") echo "standard" ;;
        "DRONE"|"KNIGHT") echo "operational" ;;
        "IMP") echo "development" ;;
        "SORCERER") echo "management" ;;
        "WIZARD") echo "administration" ;;
        *) echo "basic" ;;
    esac
}

# Validate setup completion
validate_setup() {
    log_info "Validating setup completion..."

    local errors=()

    # Check installation.md
    if [[ ! -f "$UMEMORY_DIR/installation.md" ]]; then
        errors+=("Missing installation.md")
    fi

    # Check user.md
    if [[ ! -f "$UMEMORY_DIR/user/user.md" ]]; then
        errors+=("Missing user.md")
    fi

    # Check role configuration
    if [[ ! -f "$UDOS_ROOT/sandbox/current-role.conf" ]]; then
        errors+=("Missing role configuration")
    fi

    # Check required variables
    local required_vars=("USER-ROLE" "DEVELOPER-NAME" "INSTALLATION-TYPE")
    for var in "${required_vars[@]}"; do
        if ! "$VARIABLE_MANAGER" get "$var" >/dev/null 2>&1; then
            errors+=("Missing variable: $var")
        fi
    done

    if [[ ${#errors[@]} -eq 0 ]]; then
        log_success "Setup validation passed"
        return 0
    else
        log_error "Setup validation failed:"
        for error in "${errors[@]}"; do
            echo "  - $error"
        done
        return 1
    fi
}

# Main execution
main() {
    echo -e "${CYAN}🚀 uDOS System Setup Integration${NC}"
    echo "=================================="
    echo ""

    if check_first_run; then
        log_info "First run detected - starting full setup process"

        # Run installation STORY
        if ! run_installation_story; then
            log_error "Installation setup failed"
            exit 1
        fi

        # Run user onboarding STORY
        if ! run_user_onboarding; then
            log_error "User onboarding failed"
            exit 1
        fi

        # Generate system files
        generate_installation_profile
        generate_user_profile

        # Validate setup
        if validate_setup; then
            log_success "🎉 Complete system setup finished successfully!"
            echo ""
            echo "Next steps:"
            echo "1. Run startup test: ./uSCRIPT/library/shell/system/startup.sh"
            echo "2. Test role access: [ROLE|STATUS]"
            echo "3. Verify variable system: [VAR|LIST]"
        else
            log_error "Setup validation failed - please check configuration"
            exit 1
        fi
    else
        log_info "System already configured - skipping setup"
        log_info "Use 'reset' parameter to force reconfiguration"
    fi
}

# Handle reset option
if [[ "${1:-}" == "reset" ]]; then
    log_warning "Resetting system configuration..."
    rm -f "$UMEMORY_DIR/installation.md"
    rm -f "$UMEMORY_DIR/user/user.md"
    rm -f "$UDOS_ROOT/sandbox/current-role.conf"
    log_success "Configuration reset - rerun to setup"
fi

# Execute main function
main "$@"
