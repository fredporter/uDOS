#!/bin/bash
# uDOS Installation Setup Wizard
# Creates installation.md and configures initial system
set -e

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Logging functions (bash 3.x compatible)
log_info() { echo -e "\033[0;36m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[SUCCESS]\033[0m $1"; }
log_warning() { echo -e "\033[0;33m[WARNING]\033[0m $1"; }
log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

# Installation paths
INSTALLATION_FILE="$UDOS_ROOT/uMEMORY/installation.md"
INSTALLATION_TEMPLATE="$UDOS_ROOT/uMEMORY/system/get/uGET-installation-setup.md"

# ASCII Header
echo "
██╗   ██╗██████╗  ██████╗ ███████╗
██║   ██║██╔══██╗██╔═══██╗██╔════╝
██║   ██║██║  ██║██║   ██║███████╗
██║   ██║██║  ██║██║   ██║╚════██║
╚██████╔╝██████╔╝╚██████╔╝███████║
 ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

Universal Device Operating System
Installation Setup Wizard v1.0.4.1
"

log_info "Welcome to uDOS Installation Setup"
echo "This wizard will configure your uDOS installation."
echo ""

# Check if installation already exists
if [ -f "$INSTALLATION_FILE" ]; then
    log_warning "Installation profile already exists at:"
    log_warning "$INSTALLATION_FILE"
    echo ""
    echo "Would you like to:"
    echo "1) View existing installation"
    echo "2) Reconfigure installation"
    echo "3) Exit"
    echo ""
    printf "Choose option (1-3): "
    read -r choice

    case "$choice" in
        1)
            log_info "Current installation profile:"
            cat "$INSTALLATION_FILE"
            exit 0
            ;;
        2)
            log_info "Reconfiguring installation..."
            ;;
        3|*)
            log_info "Exiting installation setup"
            exit 0
            ;;
    esac
fi

# Installation Type Selection
echo ""
log_info "🏗️ Installation Type Selection"
echo ""
echo "Available installation types:"
echo ""
echo "1) Demo - Read-only demonstration (Ghost role only)"
echo "   • Safe exploration of uDOS features"
echo "   • No data modification capabilities"
echo "   • Perfect for testing and learning"
echo ""
echo "2) Personal - Full personal use (Ghost → Sorcerer)"
echo "   • Complete 7-role hierarchy"
echo "   • Personal data storage and automation"
echo "   • Development tools and extensions"
echo ""
echo "3) Development - Full development access (All roles)"
echo "   • Complete 8-role hierarchy including Wizard"
echo "   • Core system development capabilities"
echo "   • Extension development and debugging"
echo ""
echo "4) Enterprise - Multi-user with audit trails"
echo "   • Role-based access control"
echo "   • Multi-user collaboration"
echo "   • Complete audit logging"
echo ""
printf "Select installation type (1-4): "
read -r install_type

case "$install_type" in
    1)
        INSTALLATION_TYPE="demo"
        INSTALLATION_DESC="Read-only demonstration installation"
        DEFAULT_ROLE="Ghost"
        ROLES_ENABLED="Ghost"
        MULTI_USER="false"
        SECURITY_MODE="demo"
        ;;
    2)
        INSTALLATION_TYPE="personal"
        INSTALLATION_DESC="Full personal use installation"
        DEFAULT_ROLE="Crypt"
        ROLES_ENABLED="Ghost, Tomb, Crypt, Drone, Knight, Imp, Sorcerer"
        MULTI_USER="false"
        SECURITY_MODE="standard"
        ;;
    3)
        INSTALLATION_TYPE="development"
        INSTALLATION_DESC="Full development installation with Wizard access"
        DEFAULT_ROLE="Wizard"
        ROLES_ENABLED="Ghost, Tomb, Crypt, Drone, Knight, Imp, Sorcerer, Wizard"
        MULTI_USER="false"
        SECURITY_MODE="development"
        ;;
    4)
        INSTALLATION_TYPE="enterprise"
        INSTALLATION_DESC="Multi-user enterprise installation"
        DEFAULT_ROLE="Knight"
        ROLES_ENABLED="Ghost, Tomb, Crypt, Drone, Knight, Imp, Sorcerer, Wizard"
        MULTI_USER="true"
        SECURITY_MODE="enterprise"
        ;;
    *)
        log_warning "Invalid selection, defaulting to Personal installation"
        INSTALLATION_TYPE="personal"
        INSTALLATION_DESC="Full personal use installation"
        DEFAULT_ROLE="Crypt"
        ROLES_ENABLED="Ghost, Tomb, Crypt, Drone, Knight, Imp, Sorcerer"
        MULTI_USER="false"
        SECURITY_MODE="standard"
        ;;
esac

log_success "Selected: $INSTALLATION_TYPE installation"

# Network Configuration
echo ""
log_info "🌐 Network Configuration"
echo ""
echo "Network modes:"
echo "1) Local - Local-only operation (most secure)"
echo "2) Network - LAN sharing enabled"
echo "3) Public - Internet-accessible (advanced users)"
echo ""
printf "Select network mode (1-3): "
read -r network_choice

case "$network_choice" in
    1)
        NETWORK_MODE="local"
        SHARING_ENABLED="false"
        REMOTE_ACCESS="false"
        ;;
    2)
        NETWORK_MODE="network"
        SHARING_ENABLED="true"
        REMOTE_ACCESS="false"
        ;;
    3)
        NETWORK_MODE="public"
        SHARING_ENABLED="true"
        REMOTE_ACCESS="true"
        ;;
    *)
        log_warning "Invalid selection, defaulting to Local mode"
        NETWORK_MODE="local"
        SHARING_ENABLED="false"
        REMOTE_ACCESS="false"
        ;;
esac

log_success "Network mode: $NETWORK_MODE"

# Feature Configuration
echo ""
log_info "🔧 Feature Configuration"

# Determine features based on installation type
case "$INSTALLATION_TYPE" in
    "demo")
        UCORE_ENABLED="true"
        TEMPLATES_ENABLED="true"
        GEO_ENABLED="true"
        LOGGING_ENABLED="true"
        USCRIPT_ENABLED="false"
        PYTHON_ENABLED="false"
        SERVER_ENABLED="false"
        UI_ENABLED="false"
        EXTENSIONS_ENABLED="false"
        VSCODE_ENABLED="false"
        GIT_ENABLED="false"
        PACKAGES_ENABLED="false"
        ;;
    "personal")
        UCORE_ENABLED="true"
        TEMPLATES_ENABLED="true"
        GEO_ENABLED="true"
        LOGGING_ENABLED="true"
        USCRIPT_ENABLED="true"
        PYTHON_ENABLED="true"
        SERVER_ENABLED="true"
        UI_ENABLED="true"
        EXTENSIONS_ENABLED="true"
        VSCODE_ENABLED="true"
        GIT_ENABLED="true"
        PACKAGES_ENABLED="true"
        ;;
    "development"|"enterprise")
        UCORE_ENABLED="true"
        TEMPLATES_ENABLED="true"
        GEO_ENABLED="true"
        LOGGING_ENABLED="true"
        USCRIPT_ENABLED="true"
        PYTHON_ENABLED="true"
        SERVER_ENABLED="true"
        UI_ENABLED="true"
        EXTENSIONS_ENABLED="true"
        VSCODE_ENABLED="true"
        GIT_ENABLED="true"
        PACKAGES_ENABLED="true"
        ;;
esac

echo "Core features: uCORE utilities, templates, geographic data, logging"
if [ "$USCRIPT_ENABLED" = "true" ]; then
    echo "Advanced features: uSCRIPT engine, Python, network server, UI"
fi
if [ "$EXTENSIONS_ENABLED" = "true" ]; then
    echo "Extensions: Full extension ecosystem, VS Code integration"
fi

# Generate Installation ID
INSTALLATION_ID="uDOS-$(date +%Y%m%d)-$(printf "%04x" $RANDOM)"

# Create installation profile
log_info "Creating installation profile..."

# Create the installation.md file
cat > "$INSTALLATION_FILE" << EOF
# uDOS Installation Profile

**Installation ID**: $INSTALLATION_ID
**Version**: v1.0.4.1
**Type**: $INSTALLATION_TYPE
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Platform**: $(uname -s) ($(uname -m))

> **Status**: Active
> **Mode**: $SECURITY_MODE
> **Roles Available**: $ROLES_ENABLED

---

## 📋 Installation Configuration

### 🏗️ Installation Type
**Type**: $INSTALLATION_TYPE
**Description**: $INSTALLATION_DESC

### 🔐 Security Level
**Security Mode**: $SECURITY_MODE
**Authentication**: local
**Encryption**: enabled

### 👥 User Management
**Multi-User**: $MULTI_USER
**Max Users**: $([ "$MULTI_USER" = "true" ] && echo "unlimited" || echo "1")
**Default Role**: $DEFAULT_ROLE

### 🌐 Network Configuration
**Network Mode**: $NETWORK_MODE
**Sharing Enabled**: $SHARING_ENABLED
**Remote Access**: $REMOTE_ACCESS

---

## 🎯 Available Roles

EOF

# Add role-specific information
case "$INSTALLATION_TYPE" in
    "demo")
        cat >> "$INSTALLATION_FILE" << EOF
### Demo Installation
- **Ghost** - Read-only demonstration access
- **Tomb** - Basic file operations (limited)
EOF
        ;;
    "personal")
        cat >> "$INSTALLATION_FILE" << EOF
### Personal Installation
- **Ghost** - Demo/public access
- **Tomb** - Basic storage
- **Crypt** - Secure personal use
- **Drone** - Automation tasks
- **Knight** - Security operations
- **Imp** - Development tools
- **Sorcerer** - Advanced administration
EOF
        ;;
    "development")
        cat >> "$INSTALLATION_FILE" << EOF
### Development Installation
- **All Roles** - Complete 8-role hierarchy available
- **Development Mode** - Enhanced debugging and tools
- **Extension Support** - Full extension ecosystem
- **Wizard Access** - Core system development
EOF
        ;;
    "enterprise")
        cat >> "$INSTALLATION_FILE" << EOF
### Enterprise Installation
- **Role-Based Access Control** - Granular permissions
- **Audit Logging** - Complete activity tracking
- **Network Integration** - Enterprise network support
- **Multi-User Management** - Team collaboration
EOF
        ;;
esac

# Add capabilities section
cat >> "$INSTALLATION_FILE" << EOF

---

## 📊 System Capabilities

### 🔧 Core Features
- **uCORE Utilities**: $UCORE_ENABLED
- **Template System**: $TEMPLATES_ENABLED
- **Geographic Data**: $GEO_ENABLED
- **Logging System**: $LOGGING_ENABLED

### 🚀 Advanced Features
- **uSCRIPT Engine**: $USCRIPT_ENABLED
- **Python Environment**: $PYTHON_ENABLED
- **Network Server**: $SERVER_ENABLED
- **UI Components**: $UI_ENABLED

### 🔌 Extensions
- **Extension System**: $EXTENSIONS_ENABLED
- **VS Code Integration**: $VSCODE_ENABLED
- **Git Integration**: $GIT_ENABLED
- **Package Management**: $PACKAGES_ENABLED

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

**Installation ID**: $INSTALLATION_ID
**Created**: $(date '+%Y-%m-%d %H:%M:%S')
**Platform**: $(uname -s) ($(uname -m))
**Version**: v1.0.4.1
**Type**: $INSTALLATION_TYPE
**Security**: $SECURITY_MODE
**Users**: $([ "$MULTI_USER" = "true" ] && echo "Multi-user" || echo "Single-user")

### 🎯 Next Steps
1. Complete user setup (if required)
2. Configure role permissions
3. Setup development environment
4. Initialize data systems
5. Test core functionality

---

*Installation profile generated by uDOS v1.0.4.1 setup system*
EOF

log_success "Installation profile created: $INSTALLATION_FILE"

# Set default role in role configuration
ROLE_DIR="$UDOS_ROOT/uMEMORY/role"
if [ ! -d "$ROLE_DIR" ]; then
    mkdir -p "$ROLE_DIR"
fi

echo "$DEFAULT_ROLE" > "$ROLE_DIR/current.txt"
log_success "Default role set to: $DEFAULT_ROLE"

# Initialize directories based on installation type
log_info "Initializing directory structure..."

# Ensure required directories exist
mkdir -p "$UDOS_ROOT/sandbox/logs"
mkdir -p "$UDOS_ROOT/sandbox/sessions"
mkdir -p "$UDOS_ROOT/sandbox/data"
mkdir -p "$UDOS_ROOT/uMEMORY/user"
mkdir -p "$UDOS_ROOT/uMEMORY/system"

# Create installation log entry
LOG_FILE="$UDOS_ROOT/sandbox/logs/installation-$(date +%Y%m%d-%H%M%S).md"
cat > "$LOG_FILE" << EOF
# uDOS Installation Log

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Installation ID**: $INSTALLATION_ID
**Type**: $INSTALLATION_TYPE
**Platform**: $(uname -s) $(uname -m)

## Installation Summary
- Type: $INSTALLATION_TYPE ($INSTALLATION_DESC)
- Security: $SECURITY_MODE
- Network: $NETWORK_MODE
- Default Role: $DEFAULT_ROLE
- Multi-User: $MULTI_USER

## Features Enabled
- Core: $UCORE_ENABLED
- Scripts: $USCRIPT_ENABLED
- Network: $SERVER_ENABLED
- Extensions: $EXTENSIONS_ENABLED

Installation completed successfully.
EOF

log_success "Installation log created: $LOG_FILE"

# Final summary
echo ""
log_success "🎉 uDOS Installation Complete!"
echo ""
echo "Installation Summary:"
echo "• Installation ID: $INSTALLATION_ID"
echo "• Type: $INSTALLATION_TYPE"
echo "• Default Role: $DEFAULT_ROLE"
echo "• Security Mode: $SECURITY_MODE"
echo "• Network Mode: $NETWORK_MODE"
echo ""
echo "Your uDOS installation is ready!"
echo ""
echo "Next steps:"
echo "1. Run: ./uCORE/bin/ucode help"
echo "2. Complete user setup if needed"
echo "3. Explore uDOS features with your $DEFAULT_ROLE role"
echo ""

log_info "Installation profile: $INSTALLATION_FILE"
log_info "Installation log: $LOG_FILE"
