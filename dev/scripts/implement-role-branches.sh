#!/bin/bash
# uDOS Role Branch Implementation Script
# Creates actual GitHub branches for role-based installations

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPO_URL="https://github.com/fredporter/uDOS.git"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_git_status() {
    log_info "Checking git repository status..."

    if [[ ! -d "$UDOS_ROOT/.git" ]]; then
        log_error "Not in a git repository"
        exit 1
    fi

    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        log_warning "Current branch is '$current_branch', switching to main..."
        git checkout main
    fi

    log_info "Pulling latest changes..."
    git pull origin main || log_warning "Could not pull from origin"

    log_success "Git repository ready"
}

# Create a single role branch
create_single_role_branch() {
    local role="$1"
    local level="$2"
    local description="$3"
    local branch_name="role-$role"

    log_info "Creating branch: $branch_name (Level $level)"

    cd "$UDOS_ROOT"

    # Create orphan branch (clean slate)
    if git branch | grep -q "$branch_name"; then
        log_warning "Branch $branch_name exists, deleting and recreating..."
        git branch -D "$branch_name" 2>/dev/null || true
    fi

    git checkout --orphan "$branch_name"
    git rm -rf . 2>/dev/null || true

    # Create role-specific content based on level
    create_role_content "$role" "$level" "$description"

    # Add and commit
    git add .
    git commit -m "🎭 ${role^^} Role Installation (Level $level)

Role: ${role^^}
Level: $level/100
Purpose: $description

This branch provides a clean, role-specific installation of uDOS
configured for ${role^^} level users with appropriate permissions
and capabilities.

Components included:
$(get_role_components "$role")

Installation:
git clone -b $branch_name $REPO_URL uDOS-${role^^}
cd uDOS-${role^^}
./install-$role.sh

Created: $(date)
uDOS Version: 1.0.4.1"

    log_success "Branch $branch_name created"

    # Return to main
    git checkout main
}

# Create role-specific content
create_role_content() {
    local role="$1"
    local level="$2"
    local description="$3"

    # Create basic structure
    mkdir -p {uCORE,uMEMORY,uKNOWLEDGE,uNETWORK,uSCRIPT,sandbox,docs,extensions}

    # Copy components based on role level
    case "$level" in
        "10") # GHOST - minimal
            create_ghost_content "$role"
            ;;
        "20") # TOMB - archive
            create_tomb_content "$role"
            ;;
        "30") # CRYPT - crypto + basic network
            create_crypt_content "$role"
            ;;
        "40"|"50") # DRONE/KNIGHT - full system minus dev
            create_drone_knight_content "$role"
            ;;
        "60") # IMP - development
            create_imp_content "$role"
            ;;
        "80") # SORCERER - advanced
            create_sorcerer_content "$role"
            ;;
        "100") # WIZARD - complete
            create_wizard_content "$role"
            ;;
    esac

    # Create role-specific files
    create_role_installer "$role" "$level" "$description"
    create_role_readme "$role" "$level" "$description"
    create_role_config "$role" "$level"

    # Copy common files
    echo "# uDOS ${role^^} Role Installation" > README.md
    echo "Version: 1.0.4.1" > VERSION
    echo "Role: ${role^^} (Level $level)" >> VERSION

    cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 uDOS Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
}

# Content creation functions for each role
create_ghost_content() {
    local role="$1"

    # Minimal uCORE
    mkdir -p uCORE/{launcher,code}
    echo "# uCORE Launcher for GHOST role" > uCORE/launcher/README.md
    echo "# Basic commands for GHOST role" > uCORE/code/README.md

    # Demo sandbox
    mkdir -p sandbox/demo
    echo "# Demo workspace for learning" > sandbox/demo/README.md

    # Basic docs
    mkdir -p docs/public
    echo "# Public documentation for GHOST users" > docs/public/README.md
}

create_tomb_content() {
    local role="$1"

    # Full uCORE
    mkdir -p uCORE/{launcher,code,core}
    echo "# Complete uCORE system" > uCORE/README.md

    # Read-only uMEMORY
    mkdir -p uMEMORY/{system,archives}
    echo "# Read-only memory access for archives" > uMEMORY/README.md

    # Historical uKNOWLEDGE
    mkdir -p uKNOWLEDGE/historical
    echo "# Historical knowledge base" > uKNOWLEDGE/README.md

    # Limited sandbox
    mkdir -p sandbox/limited
    echo "# Limited workspace for data exploration" > sandbox/README.md

    # Full docs
    mkdir -p docs
    echo "# Complete documentation" > docs/README.md
}

create_crypt_content() {
    local role="$1"

    # Full uCORE
    mkdir -p uCORE/{launcher,code,core,security}
    echo "# Complete uCORE with security modules" > uCORE/README.md

    # Encrypted uMEMORY
    mkdir -p uMEMORY/{system,user,encrypted}
    echo "# Encrypted memory management" > uMEMORY/README.md

    # Security uKNOWLEDGE
    mkdir -p uKNOWLEDGE/{security,protocols}
    echo "# Security knowledge base" > uKNOWLEDGE/README.md

    # Basic uNETWORK
    mkdir -p uNETWORK/{basic,display}
    echo "# Basic networking capabilities" > uNETWORK/README.md

    # Basic uSCRIPT
    mkdir -p uSCRIPT/{basic,security}
    echo "# Basic scripting with security focus" > uSCRIPT/README.md

    # Full sandbox
    mkdir -p sandbox/{workspace,experiments}
    echo "# Full workspace with encryption" > sandbox/README.md

    # Security docs
    mkdir -p docs/{security,protocols}
    echo "# Security-focused documentation" > docs/README.md
}

create_drone_knight_content() {
    local role="$1"

    # Complete operational system
    mkdir -p uCORE/{launcher,code,core,automation}
    mkdir -p uMEMORY/{system,user,templates}
    mkdir -p uKNOWLEDGE/{documentation,procedures}
    mkdir -p uNETWORK/{server,display,networking}
    mkdir -p uSCRIPT/{scripts,automation,integration}
    mkdir -p sandbox/{workspace,experiments,logs}
    mkdir -p docs/{user,system,automation}

    echo "# Complete operational uDOS system" > README.md
    echo "# Role: ${role^^} - Automation and operations focus" >> README.md
}

create_imp_content() {
    local role="$1"

    # Complete system with development tools
    mkdir -p uCORE/{launcher,code,core,development}
    mkdir -p uMEMORY/{system,user,templates,projects}
    mkdir -p uKNOWLEDGE/{documentation,development,apis}
    mkdir -p uNETWORK/{server,display,networking,apis}
    mkdir -p uSCRIPT/{scripts,automation,integration,development}
    mkdir -p sandbox/{workspace,experiments,projects,logs}
    mkdir -p docs/{user,system,development,apis}
    mkdir -p extensions/user

    echo "# Development-focused uDOS installation" > README.md
    echo "# Role: IMP - Creative development and API integration" >> README.md
}

create_sorcerer_content() {
    local role="$1"

    # Advanced system with platform extensions
    mkdir -p uCORE/{launcher,code,core,development,management}
    mkdir -p uMEMORY/{system,user,templates,projects,coordination}
    mkdir -p uKNOWLEDGE/{documentation,development,management}
    mkdir -p uNETWORK/{server,display,networking,coordination}
    mkdir -p uSCRIPT/{scripts,automation,integration,management}
    mkdir -p sandbox/{workspace,experiments,projects,coordination,logs}
    mkdir -p docs/{user,system,development,management}
    mkdir -p extensions/{user,platform}

    echo "# Advanced management uDOS installation" > README.md
    echo "# Role: SORCERER - Advanced coordination and management" >> README.md
}

create_wizard_content() {
    local role="$1"

    # Complete system including development environment
    mkdir -p uCORE/{launcher,code,core,development,management,admin}
    mkdir -p uMEMORY/{system,user,templates,projects,coordination,admin}
    mkdir -p uKNOWLEDGE/{documentation,development,management,admin}
    mkdir -p uNETWORK/{server,display,networking,coordination,admin}
    mkdir -p uSCRIPT/{scripts,automation,integration,management,admin}
    mkdir -p sandbox/{workspace,experiments,projects,coordination,admin,logs}
    mkdir -p docs/{user,system,development,management,architecture}
    mkdir -p extensions/{user,platform,core}
    mkdir -p dev/{scripts,docs,templates,tools}

    echo "# Complete uDOS installation with development environment" > README.md
    echo "# Role: WIZARD - Full system access and core development" >> README.md
}

# Create role installer script
create_role_installer() {
    local role="$1"
    local level="$2"
    local description="$3"

    cat > "install-$role.sh" << EOF
#!/bin/bash
# uDOS ${role^^} Role Installation Script
# $description

set -euo pipefail

ROLE="${role^^}"
ROLE_LEVEL="$level"
INSTALL_DIR="\${1:-\$HOME/uDOS-\$ROLE}"

echo "🎭 Installing uDOS \$ROLE Role (Level \$ROLE_LEVEL)..."
echo "📁 Installation directory: \$INSTALL_DIR"
echo ""

# Create installation directory
mkdir -p "\$INSTALL_DIR"

# Copy all files to installation directory
echo "📦 Copying uDOS \$ROLE components..."
cp -r * "\$INSTALL_DIR/" 2>/dev/null || true

# Set up role configuration
echo "CURRENT_ROLE=\"\$ROLE\"" > "\$INSTALL_DIR/current-role.conf"
echo "ROLE_LEVEL=\"\$ROLE_LEVEL\"" >> "\$INSTALL_DIR/current-role.conf"
echo "INSTALLATION_DATE=\"\$(date)\"" >> "\$INSTALL_DIR/current-role.conf"

# Set permissions
find "\$INSTALL_DIR" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

echo ""
echo "✅ uDOS \$ROLE installation completed!"
echo ""
echo "📋 Installation Summary:"
echo "   Role: \$ROLE (Level \$ROLE_LEVEL)"
echo "   Location: \$INSTALL_DIR"
echo "   Purpose: $description"
echo ""
echo "🚀 To start uDOS:"
echo "   cd \$INSTALL_DIR"
echo "   ./start-$role.sh"
echo ""
EOF

    chmod +x "install-$role.sh"
}

# Create role-specific README
create_role_readme() {
    local role="$1"
    local level="$2"
    local description="$3"

    cat > "README-$role.md" << EOF
# uDOS ${role^^} Role Installation

**Level**: $level/100
**Purpose**: $description

## Quick Installation

\`\`\`bash
git clone -b role-$role https://github.com/fredporter/uDOS.git uDOS-${role^^}
cd uDOS-${role^^}
./install-$role.sh
\`\`\`

## One-Command Installation

\`\`\`bash
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-$role/install-$role.sh | bash
\`\`\`

## Role Capabilities

$(get_role_capabilities "$role")

## Getting Started

After installation:
\`\`\`bash
cd uDOS-${role^^}
./start-$role.sh
\`\`\`

## Components Included

$(get_role_components "$role")

## Role Progression

This ${role^^} installation can be upgraded to:
$(get_upgrade_path "$role")

---

*uDOS ${role^^} Role - Universal Device Operating System v1.0.4.1*
EOF
}

# Create role configuration
create_role_config() {
    local role="$1"
    local level="$2"

    cat > "role-config.json" << EOF
{
    "role": {
        "name": "${role^^}",
        "level": $level,
        "installation_type": "role-based",
        "version": "1.0.4.1"
    },
    "capabilities": "$(get_role_capabilities "$role")",
    "components": $(get_components_json "$role"),
    "permissions": $(get_permissions_json "$role"),
    "installation": {
        "branch": "role-$role",
        "installer": "install-$role.sh",
        "startup": "start-$role.sh"
    }
}
EOF
}

# Helper functions
get_role_capabilities() {
    local role="$1"
    case "$role" in
        "ghost") echo "Demo installation with safe learning environment" ;;
        "tomb") echo "Archive access and historical data analysis" ;;
        "crypt") echo "Cryptographic operations and security protocols" ;;
        "drone") echo "Automation and system monitoring" ;;
        "knight") echo "Security operations and threat detection" ;;
        "imp") echo "Development tools and API integration" ;;
        "sorcerer") echo "Advanced management and team coordination" ;;
        "wizard") echo "Complete system access and development environment" ;;
    esac
}

get_role_components() {
    local role="$1"
    case "$role" in
        "ghost") echo "- uCORE launcher, Basic commands, Demo sandbox, Public docs" ;;
        "tomb") echo "- Complete uCORE, Read-only uMEMORY, Historical uKNOWLEDGE, Limited sandbox" ;;
        "crypt") echo "- Complete uCORE, Encrypted uMEMORY, Security uKNOWLEDGE, Basic uNETWORK/uSCRIPT" ;;
        "drone"|"knight") echo "- Complete operational system (all components except dev environment)" ;;
        "imp") echo "- Complete system plus user extensions and development tools" ;;
        "sorcerer") echo "- Complete system plus user and platform extensions" ;;
        "wizard") echo "- Complete system plus all extensions and development environment" ;;
    esac
}

get_upgrade_path() {
    local role="$1"
    case "$role" in
        "ghost") echo "TOMB → CRYPT → DRONE → KNIGHT → IMP → SORCERER → WIZARD" ;;
        "tomb") echo "CRYPT → DRONE → KNIGHT → IMP → SORCERER → WIZARD" ;;
        "crypt") echo "DRONE → KNIGHT → IMP → SORCERER → WIZARD" ;;
        "drone") echo "KNIGHT → IMP → SORCERER → WIZARD" ;;
        "knight") echo "IMP → SORCERER → WIZARD" ;;
        "imp") echo "SORCERER → WIZARD" ;;
        "sorcerer") echo "WIZARD" ;;
        "wizard") echo "**Maximum Role** - Complete system access" ;;
    esac
}

get_components_json() {
    local role="$1"
    case "$role" in
        "ghost") echo '{"uCORE": "launcher", "sandbox": "demo", "docs": "public"}' ;;
        "tomb") echo '{"uCORE": "full", "uMEMORY": "read-only", "uKNOWLEDGE": "historical", "sandbox": "limited", "docs": "full"}' ;;
        "crypt") echo '{"uCORE": "full", "uMEMORY": "encrypted", "uKNOWLEDGE": "security", "uNETWORK": "basic", "uSCRIPT": "basic", "sandbox": "full", "docs": "security"}' ;;
        *) echo '{"uCORE": "full", "uMEMORY": "full", "uKNOWLEDGE": "full", "uNETWORK": "full", "uSCRIPT": "full", "sandbox": "full", "docs": "full"}' ;;
    esac
}

get_permissions_json() {
    local role="$1"
    case "$role" in
        "ghost") echo '{"system_access": false, "memory_access": "none", "script_execution": false, "network_access": false}' ;;
        "tomb") echo '{"system_access": "read_only", "memory_access": "archives", "script_execution": false, "network_access": false}' ;;
        "crypt") echo '{"system_access": "limited", "memory_access": "encrypted", "script_execution": "basic", "network_access": "basic"}' ;;
        *) echo '{"system_access": true, "memory_access": "full", "script_execution": true, "network_access": true}' ;;
    esac
}

# Create all role branches
create_all_role_branches() {
    log_info "Creating all role-based installation branches..."

    # Define roles with their levels and descriptions
    local roles=(
        "ghost:10:Demo and learning environment"
        "tomb:20:Archive access and data archaeology"
        "crypt:30:Cryptographic operations and security"
        "drone:40:Automation and monitoring"
        "knight:50:Security operations and defense"
        "imp:60:Development and creative projects"
        "sorcerer:80:Advanced management and coordination"
        "wizard:100:Complete system access and development"
    )

    for role_info in "${roles[@]}"; do
        IFS=':' read -r role level description <<< "$role_info"
        create_single_role_branch "$role" "$level" "$description"
    done

    log_success "All role branches created successfully!"
}

# Push branches to remote
push_role_branches() {
    log_info "Pushing role branches to remote repository..."

    local roles=("ghost" "tomb" "crypt" "drone" "knight" "imp" "sorcerer" "wizard")

    for role in "${roles[@]}"; do
        local branch_name="role-$role"
        log_info "Pushing branch: $branch_name"

        if git push origin "$branch_name" --force; then
            log_success "Pushed $branch_name successfully"
        else
            log_warning "Failed to push $branch_name"
        fi
    done

    log_success "Role branches push completed"
}

# Main execution
main() {
    echo "🎭 uDOS Role Branch Implementation"
    echo "=================================="
    echo ""

    case "${1:-create}" in
        "create")
            check_git_status
            create_all_role_branches
            echo ""
            log_success "Role branch creation completed!"
            echo ""
            echo "Next steps:"
            echo "1. Review branches: git branch -a"
            echo "2. Push to remote: $0 push"
            echo "3. Test installations"
            ;;
        "push")
            push_role_branches
            ;;
        *)
            echo "Usage: $0 {create|push}"
            echo ""
            echo "Commands:"
            echo "  create  - Create all role-based branches locally"
            echo "  push    - Push role branches to remote repository"
            ;;
    esac
}

# Execute
main "$@"
