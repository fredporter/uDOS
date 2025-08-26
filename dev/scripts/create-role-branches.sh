#!/bin/bash
# uDOS Role-Based Branch Creation Script
# Creates distributable branches for each role installation with appropriate components

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEV_ROOT="$UDOS_ROOT/dev"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Role definitions with their permissions and components
declare -A ROLES=(
    ["ghost"]="10"
    ["tomb"]="20"
    ["crypt"]="30"
    ["drone"]="40"
    ["knight"]="50"
    ["imp"]="60"
    ["sorcerer"]="80"
    ["wizard"]="100"
)

# Component access matrix based on role levels
declare -A ROLE_COMPONENTS=(
    ["ghost"]="uCORE/launcher uCORE/code/basic uMEMORY/system uKNOWLEDGE docs/public sandbox/demo"
    ["tomb"]="uCORE/launcher uCORE/code uMEMORY uKNOWLEDGE docs sandbox/limited"
    ["crypt"]="uCORE uMEMORY uKNOWLEDGE uNETWORK/basic uSCRIPT/basic docs sandbox"
    ["drone"]="uCORE uMEMORY uKNOWLEDGE uNETWORK uSCRIPT docs sandbox"
    ["knight"]="uCORE uMEMORY uKNOWLEDGE uNETWORK uSCRIPT docs sandbox"
    ["imp"]="uCORE uMEMORY uKNOWLEDGE uNETWORK uSCRIPT docs sandbox extensions/user"
    ["sorcerer"]="uCORE uMEMORY uKNOWLEDGE uNETWORK uSCRIPT docs sandbox extensions"
    ["wizard"]="uCORE uMEMORY uKNOWLEDGE uNETWORK uSCRIPT docs sandbox extensions dev"
)

# Initialize role components - no longer needed since declared above
init_role_components() {
    : # No-op function for compatibility
}

# Logging function
log_branch() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        "INFO")  echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "BRANCH") echo -e "${MAGENTA}🌿 $message${NC}" ;;
    esac
}

# Show role branch banner
show_role_banner() {
    echo -e "${CYAN}${BOLD}"
    echo "██████╗  ██████╗ ██╗     ███████╗    ██████╗ ██████╗  █████╗ ███╗   ██╗ ██████╗██╗  ██╗"
    echo "██╔══██╗██╔═══██╗██║     ██╔════╝    ██╔══██╗██╔══██╗██╔══██╗████╗  ██║██╔════╝██║  ██║"
    echo "██████╔╝██║   ██║██║     █████╗      ██████╔╝██████╔╝███████║██╔██╗ ██║██║     ███████║"
    echo "██╔══██╗██║   ██║██║     ██╔══╝      ██╔══██╗██╔══██╗██╔══██║██║╚██╗██║██║     ██╔══██║"
    echo "██║  ██║╚██████╔╝███████╗███████╗    ██████╔╝██║  ██║██║  ██║██║ ╚████║╚██████╗██║  ██║"
    echo "╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝"
    echo -e "${NC}"
    echo -e "${YELLOW}uDOS Role-Based Installation Branch Creation${NC}"
    echo -e "${BLUE}Universal Device Operating System - Branch Manager v1.0.4.1${NC}"
    echo ""
}

# Check if we're in the right directory and have git
check_prerequisites() {
    log_branch "INFO" "Checking prerequisites..."

    if [[ ! -d "$UDOS_ROOT/.git" ]]; then
        log_branch "ERROR" "Not in a git repository. Please run from uDOS root directory."
        exit 1
    fi

    if ! command -v git >/dev/null 2>&1; then
        log_branch "ERROR" "Git not found. Please install git."
        exit 1
    fi

    # Check current branch
    local current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        log_branch "WARNING" "Current branch is '$current_branch', not 'main'. Switching to main..."
        git checkout main
    fi

    # Ensure we have latest changes
    log_branch "INFO" "Pulling latest changes from main..."
    git pull origin main || log_branch "WARNING" "Could not pull from origin"

    log_branch "SUCCESS" "Prerequisites checked"
}

# Create role-specific configuration
create_role_config() {
    local role="$1"
    local role_level="${ROLES[$role]}"
    local temp_dir="$2"

    log_branch "INFO" "Creating role configuration for $role (Level $role_level)..."

    # Create role-specific configuration file
    cat > "$temp_dir/role-config.json" << EOF
{
    "role": {
        "name": "${role^^}",
        "level": $role_level,
        "capabilities": "$(get_role_capabilities "$role")",
        "installation_type": "role-based",
        "version": "1.0.4.1"
    },
    "components": {
        "uCORE": $(get_ucore_config "$role"),
        "uMEMORY": $(get_umemory_config "$role"),
        "uKNOWLEDGE": $(get_uknowledge_config "$role"),
        "uNETWORK": $(get_unetwork_config "$role"),
        "uSCRIPT": $(get_uscript_config "$role"),
        "sandbox": $(get_sandbox_config "$role"),
        "extensions": $(get_extensions_config "$role"),
        "dev": $(get_dev_config "$role")
    },
    "permissions": {
        "system_access": $(get_system_access "$role"),
        "memory_access": "$(get_memory_access "$role")",
        "script_execution": $(get_script_execution "$role"),
        "network_access": $(get_network_access "$role"),
        "development_access": $(get_dev_access "$role")
    },
    "installation": {
        "overlay_mode": true,
        "shared_components": ["uCORE/core", "uMEMORY/system", "uKNOWLEDGE/public"],
        "role_specific": ["sandbox", "uMEMORY/user", "extensions/user"],
        "branch": "role-$role",
        "upstream": "main"
    }
}
EOF

    # Create role-specific installer script
    create_role_installer "$role" "$temp_dir"

    # Create role-specific README
    create_role_readme "$role" "$temp_dir"

    log_branch "SUCCESS" "Role configuration created for $role"
}

# Get role capabilities description
get_role_capabilities() {
    local role="$1"
    case "$role" in
        "ghost") echo "Demo installation with read-only access and basic learning environment" ;;
        "tomb") echo "Archive installation with encrypted storage and historical data access" ;;
        "crypt") echo "Cryptographic installation with advanced encryption and security protocols" ;;
        "drone") echo "Automation installation with scheduling and monitoring capabilities" ;;
        "knight") echo "Security operations with threat detection and incident response" ;;
        "imp") echo "Development installation with API integration and project tools" ;;
        "sorcerer") echo "Advanced management with team coordination and workflow control" ;;
        "wizard") echo "Full installation with complete system access and development tools" ;;
    esac
}

# Component configuration functions
get_ucore_config() {
    local role="$1"
    case "$role" in
        "ghost") echo '{"access": "launcher_only", "components": ["launcher", "basic_commands"]}' ;;
        "tomb"|"crypt") echo '{"access": "limited", "components": ["launcher", "core", "security"]}' ;;
        "drone"|"knight") echo '{"access": "system", "components": ["launcher", "core", "automation", "security"]}' ;;
        "imp"|"sorcerer") echo '{"access": "full", "components": ["launcher", "core", "development", "automation"]}' ;;
        "wizard") echo '{"access": "complete", "components": ["all"]}' ;;
    esac
}

get_umemory_config() {
    local role="$1"
    case "$role" in
        "ghost") echo '{"access": "none", "components": []}' ;;
        "tomb") echo '{"access": "read_only", "components": ["system", "archives"]}' ;;
        "crypt"|"drone"|"knight") echo '{"access": "encrypted", "components": ["system", "user", "secure"]}' ;;
        "imp"|"sorcerer"|"wizard") echo '{"access": "full", "components": ["system", "user", "templates", "archives"]}' ;;
    esac
}

get_uknowledge_config() {
    local role="$1"
    case "$role" in
        "ghost") echo '{"access": "none", "components": []}' ;;
        "tomb") echo '{"access": "historical", "components": ["archives", "documentation"]}' ;;
        "crypt"|"drone"|"knight") echo '{"access": "security", "components": ["documentation", "security_knowledge"]}' ;;
        "imp"|"sorcerer"|"wizard") echo '{"access": "full", "components": ["documentation", "knowledge_base", "tutorials"]}' ;;
    esac
}

get_unetwork_config() {
    local role="$1"
    case "$role" in
        "ghost"|"tomb") echo '{"access": "none", "components": []}' ;;
        "crypt") echo '{"access": "basic", "components": ["display", "basic_server"]}' ;;
        "drone"|"knight"|"imp"|"sorcerer"|"wizard") echo '{"access": "full", "components": ["server", "display", "networking"]}' ;;
    esac
}

get_uscript_config() {
    local role="$1"
    case "$role" in
        "ghost"|"tomb") echo '{"access": "none", "components": []}' ;;
        "crypt") echo '{"access": "basic", "components": ["basic_scripts"]}' ;;
        "drone"|"knight"|"imp"|"sorcerer"|"wizard") echo '{"access": "full", "components": ["scripts", "automation", "integration"]}' ;;
    esac
}

get_sandbox_config() {
    local role="$1"
    case "$role" in
        "ghost") echo '{"access": "demo", "components": ["demo_workspace"]}' ;;
        "tomb") echo '{"access": "limited", "components": ["read_only_workspace"]}' ;;
        *) echo '{"access": "full", "components": ["workspace", "experiments", "logs"]}' ;;
    esac
}

get_extensions_config() {
    local role="$1"
    case "$role" in
        "ghost"|"tomb"|"crypt"|"drone"|"knight") echo '{"access": "none", "components": []}' ;;
        "imp") echo '{"access": "user", "components": ["user_extensions"]}' ;;
        "sorcerer") echo '{"access": "platform", "components": ["user_extensions", "platform_extensions"]}' ;;
        "wizard") echo '{"access": "full", "components": ["user_extensions", "platform_extensions", "core_extensions"]}' ;;
    esac
}

get_dev_config() {
    local role="$1"
    case "$role" in
        "wizard") echo '{"access": "full", "components": ["development_environment", "tools", "documentation"]}' ;;
        *) echo '{"access": "none", "components": []}' ;;
    esac
}

# Permission configuration functions
get_system_access() {
    local role="$1"
    case "$role" in
        "ghost") echo "false" ;;
        "tomb"|"crypt") echo "\"read_only\"" ;;
        "drone"|"knight"|"imp") echo "\"limited\"" ;;
        "sorcerer"|"wizard") echo "true" ;;
    esac
}

get_memory_access() {
    local role="$1"
    case "$role" in
        "ghost") echo "none" ;;
        "tomb") echo "read_only" ;;
        "crypt"|"drone"|"knight") echo "encrypted" ;;
        "imp"|"sorcerer"|"wizard") echo "full" ;;
    esac
}

get_script_execution() {
    local role="$1"
    case "$role" in
        "ghost"|"tomb") echo "false" ;;
        "crypt") echo "\"basic\"" ;;
        "drone"|"knight"|"imp"|"sorcerer"|"wizard") echo "true" ;;
    esac
}

get_network_access() {
    local role="$1"
    case "$role" in
        "ghost"|"tomb") echo "false" ;;
        "crypt") echo "\"basic\"" ;;
        "drone"|"knight"|"imp"|"sorcerer"|"wizard") echo "true" ;;
    esac
}

get_dev_access() {
    local role="$1"
    case "$role" in
        "wizard") echo "true" ;;
        *) echo "false" ;;
    esac
}

# Create role-specific installer
create_role_installer() {
    local role="$1"
    local temp_dir="$2"

    cat > "$temp_dir/install-${role}.sh" << EOF
#!/bin/bash
# uDOS ${role^^} Role Installation Script
# Installs uDOS with ${role^^} role permissions and capabilities

set -euo pipefail

# Configuration
ROLE="${role^^}"
ROLE_LEVEL="${ROLES[$role]}"
INSTALL_DIR="\${1:-\$HOME/uDOS-\$ROLE}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\${BLUE}Installing uDOS \$ROLE Role (Level \$ROLE_LEVEL)...\${NC}"
echo ""

# Create installation directory
mkdir -p "\$INSTALL_DIR"
cd "\$INSTALL_DIR"

# Copy role-specific components
$(generate_component_copy_commands "$role")

# Set up role configuration
cp role-config.json uCORE/config/
echo "CURRENT_ROLE=\"\$ROLE\"" > sandbox/current-role.conf

# Set permissions
chmod +x uCORE/launcher/*/*.sh 2>/dev/null || true
chmod +x uCORE/code/*.sh 2>/dev/null || true

echo ""
echo -e "\${GREEN}✅ uDOS \$ROLE installation completed!\${NC}"
echo ""
echo -e "\${YELLOW}Installation Directory:\${NC} \$INSTALL_DIR"
echo -e "\${YELLOW}Role Level:\${NC} \$ROLE_LEVEL"
echo -e "\${YELLOW}Capabilities:\${NC} $(get_role_capabilities "$role")"
echo ""
echo -e "\${BLUE}To start uDOS:\${NC}"
echo "  cd \$INSTALL_DIR"
echo "  ./uCORE/launcher/universal/start-\${role}.sh"
echo ""
EOF

    chmod +x "$temp_dir/install-${role}.sh"
}

# Generate component copy commands for installer
generate_component_copy_commands() {
    local role="$1"
    local components="${ROLE_COMPONENTS[$role]}"

    for component in $components; do
        case "$component" in
            "uCORE"|"uCORE/launcher"|"uCORE/code"*)
                echo "echo \"Copying uCORE components...\""
                echo "cp -r uCORE \"\$INSTALL_DIR/\""
                ;;
            "uMEMORY")
                echo "echo \"Setting up uMEMORY...\""
                echo "cp -r uMEMORY \"\$INSTALL_DIR/\""
                ;;
            "uKNOWLEDGE")
                echo "echo \"Setting up uKNOWLEDGE...\""
                echo "cp -r uKNOWLEDGE \"\$INSTALL_DIR/\""
                ;;
            "uNETWORK"*)
                echo "echo \"Setting up uNETWORK...\""
                echo "cp -r uNETWORK \"\$INSTALL_DIR/\""
                ;;
            "uSCRIPT"*)
                echo "echo \"Setting up uSCRIPT...\""
                echo "cp -r uSCRIPT \"\$INSTALL_DIR/\""
                ;;
            "sandbox"*)
                echo "echo \"Creating sandbox environment...\""
                echo "cp -r sandbox \"\$INSTALL_DIR/\""
                ;;
            "extensions"*)
                echo "echo \"Installing extensions...\""
                echo "cp -r extensions \"\$INSTALL_DIR/\""
                ;;
            "docs"*)
                echo "echo \"Installing documentation...\""
                echo "cp -r docs \"\$INSTALL_DIR/\""
                ;;
            "dev")
                echo "echo \"Setting up development environment...\""
                echo "cp -r dev \"\$INSTALL_DIR/\""
                ;;
        esac
    done | sort -u
}

# Create role-specific README
create_role_readme() {
    local role="$1"
    local temp_dir="$2"
    local role_level="${ROLES[$role]}"

    cat > "$temp_dir/README-${role}.md" << EOF
# uDOS ${role^^} Role Installation

**Role Level**: $role_level/100
**Capabilities**: $(get_role_capabilities "$role")

## Installation Overview

This is a role-specific installation of uDOS (Universal Device Operating System) configured for ${role^^} level access and capabilities.

### What's Included

$(generate_components_list "$role")

### Installation Instructions

1. **Quick Install**:
   \`\`\`bash
   curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-$role/install-${role}.sh | bash
   \`\`\`

2. **Manual Install**:
   \`\`\`bash
   git clone -b role-$role https://github.com/fredporter/uDOS.git uDOS-${role^^}
   cd uDOS-${role^^}
   ./install-${role}.sh
   \`\`\`

### Getting Started

After installation, start uDOS with:
\`\`\`bash
cd uDOS-${role^^}
./uCORE/launcher/universal/start-${role}.sh
\`\`\`

### Available Commands

$(generate_commands_list "$role")

### Role Progression

This ${role^^} installation can be upgraded to higher roles:
$(generate_upgrade_path "$role")

### Support

- **Documentation**: See \`docs/\` directory
- **Role Guide**: \`docs/ROLE-CAPABILITIES.md\`
- **Architecture**: \`docs/ARCHITECTURE.md\`
- **GitHub**: https://github.com/fredporter/uDOS

---

*uDOS ${role^^} Role Installation - Level $role_level*
EOF
}

# Generate components list for README
generate_components_list() {
    local role="$1"
    local components="${ROLE_COMPONENTS[$role]}"

    echo "#### Core Components"
    for component in $components; do
        case "$component" in
            "uCORE"*) echo "- **uCORE**: System core and launcher components" ;;
            "uMEMORY") echo "- **uMEMORY**: $(get_memory_description "$role")" ;;
            "uKNOWLEDGE") echo "- **uKNOWLEDGE**: $(get_knowledge_description "$role")" ;;
            "uNETWORK"*) echo "- **uNETWORK**: $(get_network_description "$role")" ;;
            "uSCRIPT"*) echo "- **uSCRIPT**: $(get_script_description "$role")" ;;
            "sandbox"*) echo "- **sandbox**: $(get_sandbox_description "$role")" ;;
            "extensions"*) echo "- **extensions**: $(get_extensions_description "$role")" ;;
            "docs"*) echo "- **docs**: Role-appropriate documentation" ;;
            "dev") echo "- **dev**: Full development environment" ;;
        esac
    done | sort -u
}

# Component descriptions
get_memory_description() {
    local role="$1"
    case "$role" in
        "tomb") echo "Read-only access to archived data and historical records" ;;
        "crypt"|"drone"|"knight") echo "Encrypted storage with role-appropriate access controls" ;;
        *) echo "Full memory access with user data management" ;;
    esac
}

get_knowledge_description() {
    local role="$1"
    case "$role" in
        "tomb") echo "Historical knowledge base and archived documentation" ;;
        "crypt"|"drone"|"knight") echo "Security-focused knowledge base and documentation" ;;
        *) echo "Complete knowledge base and documentation library" ;;
    esac
}

get_network_description() {
    local role="$1"
    case "$role" in
        "crypt") echo "Basic network capabilities with secure communication" ;;
        *) echo "Full network stack with server and client capabilities" ;;
    esac
}

get_script_description() {
    local role="$1"
    case "$role" in
        "crypt") echo "Basic script execution with security focus" ;;
        *) echo "Full scripting environment with automation capabilities" ;;
    esac
}

get_sandbox_description() {
    local role="$1"
    case "$role" in
        "ghost") echo "Demo workspace for learning and experimentation" ;;
        "tomb") echo "Read-only workspace for data exploration" ;;
        *) echo "Full workspace for active development and experimentation" ;;
    esac
}

get_extensions_description() {
    local role="$1"
    case "$role" in
        "imp") echo "User-installable extensions for development" ;;
        "sorcerer") echo "User and platform extensions for advanced features" ;;
        "wizard") echo "Complete extension system including core extensions" ;;
    esac
}

# Generate commands list for README
generate_commands_list() {
    local role="$1"
    case "$role" in
        "ghost")
            echo "- \`[SYS] <STATUS>\` - System status"
            echo "- \`[ROLE] <CURRENT>\` - Check current role"
            echo "- \`[WORKFLOW] <MODE>\` - Check workflow mode"
            ;;
        "tomb")
            echo "- \`[MEM] <RETRIEVE>\` - Access archived data"
            echo "- \`[KNOW] <SEARCH>\` - Search historical data"
            echo "- \`BACKUP list\` - List available backups"
            ;;
        "crypt")
            echo "- \`[CRYPT] <ENCRYPT>\` - Advanced encryption"
            echo "- \`[KEY] <GENERATE>\` - Key management"
            echo "- \`[VAULT] <SECURE>\` - Secure vault operations"
            ;;
        "drone")
            echo "- \`[SCRIPT] <SCHEDULE>\` - Schedule automation"
            echo "- \`[WORKFLOW] <CLEANUP>\` - Automated cleanup"
            echo "- \`[LOG] <INFO>\` - Automation logging"
            ;;
        "knight")
            echo "- \`[MONITOR] <THREAT>\` - Threat monitoring"
            echo "- \`[DEFEND] <BLOCK>\` - Threat blocking"
            echo "- \`[INCIDENT] <RESPOND>\` - Incident response"
            ;;
        "imp")
            echo "- \`[GET] <JSON>\` - API data retrieval"
            echo "- \`[POST] <JSON>\` - API data posting"
            echo "- \`[DATA] <PARSE>\` - Data processing"
            ;;
        "sorcerer")
            echo "- \`[WORKFLOW] <BRIEFINGS>\` - Advanced workflow management"
            echo "- \`[ASSIST] <ANALYZE>\` - Deep context analysis"
            echo "- \`[SESSION] <SAVE>\` - Session management"
            ;;
        "wizard")
            echo "- Complete uCODE command set"
            echo "- \`[SYS] <OPTIMIZE>\` - System optimization"
            echo "- \`[DEV] <INIT>\` - Development environment"
            ;;
    esac
}

# Generate upgrade path
generate_upgrade_path() {
    local role="$1"
    case "$role" in
        "ghost") echo "→ TOMB → CRYPT → DRONE → KNIGHT → IMP → SORCERER → WIZARD" ;;
        "tomb") echo "→ CRYPT → DRONE → KNIGHT → IMP → SORCERER → WIZARD" ;;
        "crypt") echo "→ DRONE → KNIGHT → IMP → SORCERER → WIZARD" ;;
        "drone") echo "→ KNIGHT → IMP → SORCERER → WIZARD" ;;
        "knight") echo "→ IMP → SORCERER → WIZARD" ;;
        "imp") echo "→ SORCERER → WIZARD" ;;
        "sorcerer") echo "→ WIZARD" ;;
        "wizard") echo "**Maximum Role** - Complete system access" ;;
    esac
}

# Filter components for role
filter_components_for_role() {
    local role="$1"
    local temp_dir="$2"

    log_branch "INFO" "Filtering components for $role role..."

    # Create role-specific directory structure
    mkdir -p "$temp_dir"/{uCORE,uMEMORY,uKNOWLEDGE,uNETWORK,uSCRIPT,sandbox,docs,extensions}

    # Copy base components based on role permissions
    case "$role" in
        "ghost")
            # Minimal installation - launcher and basic docs only
            cp -r "$UDOS_ROOT/uCORE/launcher" "$temp_dir/uCORE/"
            cp -r "$UDOS_ROOT/uCORE/code" "$temp_dir/uCORE/" 2>/dev/null || true
            mkdir -p "$temp_dir/sandbox/demo"
            cp -r "$UDOS_ROOT/docs" "$temp_dir/" 2>/dev/null || true
            ;;
        "tomb")
            # Archive access installation
            cp -r "$UDOS_ROOT/uCORE" "$temp_dir/"
            cp -r "$UDOS_ROOT/uMEMORY" "$temp_dir/"
            cp -r "$UDOS_ROOT/uKNOWLEDGE" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/sandbox" "$temp_dir/"
            cp -r "$UDOS_ROOT/docs" "$temp_dir/" 2>/dev/null || true
            ;;
        "crypt")
            # Cryptographic installation with basic network
            cp -r "$UDOS_ROOT/uCORE" "$temp_dir/"
            cp -r "$UDOS_ROOT/uMEMORY" "$temp_dir/"
            cp -r "$UDOS_ROOT/uKNOWLEDGE" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uNETWORK" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uSCRIPT" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/sandbox" "$temp_dir/"
            cp -r "$UDOS_ROOT/docs" "$temp_dir/" 2>/dev/null || true
            ;;
        "drone"|"knight")
            # Full system minus dev environment
            cp -r "$UDOS_ROOT/uCORE" "$temp_dir/"
            cp -r "$UDOS_ROOT/uMEMORY" "$temp_dir/"
            cp -r "$UDOS_ROOT/uKNOWLEDGE" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uNETWORK" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uSCRIPT" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/sandbox" "$temp_dir/"
            cp -r "$UDOS_ROOT/docs" "$temp_dir/" 2>/dev/null || true
            ;;
        "imp")
            # Development installation with user extensions
            cp -r "$UDOS_ROOT/uCORE" "$temp_dir/"
            cp -r "$UDOS_ROOT/uMEMORY" "$temp_dir/"
            cp -r "$UDOS_ROOT/uKNOWLEDGE" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uNETWORK" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uSCRIPT" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/sandbox" "$temp_dir/"
            cp -r "$UDOS_ROOT/docs" "$temp_dir/" 2>/dev/null || true
            mkdir -p "$temp_dir/extensions"
            cp -r "$UDOS_ROOT/extensions/user" "$temp_dir/extensions/" 2>/dev/null || true
            ;;
        "sorcerer")
            # Advanced installation with platform extensions
            cp -r "$UDOS_ROOT/uCORE" "$temp_dir/"
            cp -r "$UDOS_ROOT/uMEMORY" "$temp_dir/"
            cp -r "$UDOS_ROOT/uKNOWLEDGE" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uNETWORK" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uSCRIPT" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/sandbox" "$temp_dir/"
            cp -r "$UDOS_ROOT/docs" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/extensions" "$temp_dir/" 2>/dev/null || true
            ;;
        "wizard")
            # Complete installation including development environment
            cp -r "$UDOS_ROOT/uCORE" "$temp_dir/"
            cp -r "$UDOS_ROOT/uMEMORY" "$temp_dir/"
            cp -r "$UDOS_ROOT/uKNOWLEDGE" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uNETWORK" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/uSCRIPT" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/sandbox" "$temp_dir/"
            cp -r "$UDOS_ROOT/docs" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/extensions" "$temp_dir/" 2>/dev/null || true
            cp -r "$UDOS_ROOT/dev" "$temp_dir/" 2>/dev/null || true
            ;;
    esac

    # Always include core files
    cp "$UDOS_ROOT"/{README.md,LICENSE,VERSION,CHANGELOG.md} "$temp_dir/" 2>/dev/null || true
    cp "$UDOS_ROOT"/Launch-uDOS-*.* "$temp_dir/" 2>/dev/null || true

    log_branch "SUCCESS" "Components filtered for $role role"
}

# Create role branch
create_role_branch() {
    local role="$1"
    local branch_name="role-$role"
    local temp_dir="/tmp/udos-$role-branch"

    log_branch "BRANCH" "Creating branch: $branch_name"

    # Create temporary directory for role-specific content
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"

    # Filter components for this role
    filter_components_for_role "$role" "$temp_dir"

    # Create role-specific configuration
    create_role_config "$role" "$temp_dir"

    # Create and switch to role branch
    cd "$UDOS_ROOT"

    # Create orphan branch (clean slate)
    git checkout --orphan "$branch_name" 2>/dev/null || {
        log_branch "WARNING" "Branch $branch_name already exists, switching to it..."
        git checkout "$branch_name"
        git rm -rf . 2>/dev/null || true
    }

    # Copy role-specific content
    cp -r "$temp_dir"/* . 2>/dev/null || true

    # Add all files
    git add .

    # Create initial commit for role branch
    git commit -m "🎭 Initial ${role^^} role installation

Role: ${role^^} (Level ${ROLES[$role]})
Capabilities: $(get_role_capabilities "$role")
Components: ${ROLE_COMPONENTS[$role]}

This branch contains a clean, distributable installation
of uDOS configured specifically for ${role^^} role users.

Installation:
- Clone this branch: git clone -b $branch_name [repo]
- Run installer: ./install-${role}.sh
- Start uDOS: ./uCORE/launcher/universal/start-${role}.sh

Created by uDOS Role Branch Manager v1.0.4.1
"

    log_branch "SUCCESS" "Branch $branch_name created with role-specific content"

    # Clean up temp directory
    rm -rf "$temp_dir"

    # Return to main branch
    git checkout main
}

# Create all role branches
create_all_role_branches() {
    log_branch "INFO" "Creating all role-based installation branches..."

    for role in "${!ROLES[@]}"; do
        log_branch "INFO" "Processing role: ${role^^} (Level ${ROLES[$role]})"
        create_role_branch "$role"
    done

    log_branch "SUCCESS" "All role branches created successfully!"
}

# Push branches to remote
push_role_branches() {
    log_branch "INFO" "Pushing role branches to remote repository..."

    cd "$UDOS_ROOT"

    for role in "${!ROLES[@]}"; do
        local branch_name="role-$role"
        log_branch "INFO" "Pushing branch: $branch_name"

        if git push origin "$branch_name"; then
            log_branch "SUCCESS" "Branch $branch_name pushed successfully"
        else
            log_branch "WARNING" "Failed to push branch $branch_name"
        fi
    done

    log_branch "SUCCESS" "Role branches push completed"
}

# List created branches
list_role_branches() {
    log_branch "INFO" "Role-based installation branches:"
    echo ""

    for role in "${!ROLES[@]}"; do
        local branch_name="role-$role"
        local role_level="${ROLES[$role]}"
        local capabilities="$(get_role_capabilities "$role")"

        echo -e "${CYAN}🌿 $branch_name${NC}"
        echo -e "   ${YELLOW}Level:${NC} $role_level/100"
        echo -e "   ${YELLOW}Role:${NC} ${role^^}"
        echo -e "   ${YELLOW}Capabilities:${NC} $capabilities"
        echo -e "   ${YELLOW}Install:${NC} git clone -b $branch_name https://github.com/fredporter/uDOS.git"
        echo ""
    done
}

# Create branch strategy documentation
create_branch_documentation() {
    log_branch "INFO" "Creating branch strategy documentation..."

    cat > "$DEV_ROOT/docs/BRANCH-STRATEGY.md" << 'EOF'
# uDOS Role-Based Branch Strategy

## Overview

uDOS uses a comprehensive branching strategy to provide clean, distributable installations for each user role. This approach ensures users receive only the components appropriate for their role level while maintaining shared core functionality.

## Branch Architecture

### Main Branch
- **Purpose**: Complete development environment with all components
- **Access Level**: WIZARD (Level 100)
- **Components**: Full uDOS installation including development environment
- **Use Case**: Core development and full system administration

### Role Branches

Each role has its own distribution branch with filtered components:

#### role-ghost (Level 10)
- **Purpose**: Demo and learning environment
- **Components**: uCORE launcher, basic commands, demo sandbox, public docs
- **Installation**: `git clone -b role-ghost https://github.com/fredporter/uDOS.git`

#### role-tomb (Level 20)
- **Purpose**: Archive and data analysis
- **Components**: uCORE, uMEMORY (read-only), uKNOWLEDGE (historical), sandbox, docs
- **Installation**: `git clone -b role-tomb https://github.com/fredporter/uDOS.git`

#### role-crypt (Level 30)
- **Purpose**: Cryptographic operations and security
- **Components**: uCORE, uMEMORY (encrypted), uKNOWLEDGE, uNETWORK (basic), uSCRIPT (basic), sandbox, docs
- **Installation**: `git clone -b role-crypt https://github.com/fredporter/uDOS.git`

#### role-drone (Level 40)
- **Purpose**: Automation and monitoring
- **Components**: Full system minus development environment and advanced extensions
- **Installation**: `git clone -b role-drone https://github.com/fredporter/uDOS.git`

#### role-knight (Level 50)
- **Purpose**: Security operations and defense
- **Components**: Full system with security focus, minus development environment
- **Installation**: `git clone -b role-knight https://github.com/fredporter/uDOS.git`

#### role-imp (Level 60)
- **Purpose**: Development and creative projects
- **Components**: Full system plus user extensions, minus core development tools
- **Installation**: `git clone -b role-imp https://github.com/fredporter/uDOS.git`

#### role-sorcerer (Level 80)
- **Purpose**: Advanced management and coordination
- **Components**: Full system plus platform extensions, minus core development
- **Installation**: `git clone -b role-sorcerer https://github.com/fredporter/uDOS.git`

#### role-wizard (Level 100)
- **Purpose**: Complete system control and development
- **Components**: Complete uDOS installation with development environment
- **Installation**: `git clone -b role-wizard https://github.com/fredporter/uDOS.git`

## Shared Components Strategy

### Always Synchronized
These components are kept synchronized across all role branches from the main branch:

- **uCORE/core**: Essential system functions
- **uMEMORY/system**: System-level memory management
- **uKNOWLEDGE/public**: General knowledge base

### Role-Filtered Components
These components are filtered based on role permissions:

- **uNETWORK**: Available from CRYPT level and above
- **uSCRIPT**: Available from CRYPT level and above
- **extensions/user**: Available from IMP level and above
- **extensions/platform**: Available from SORCERER level and above
- **extensions/core**: Available only in WIZARD level
- **dev**: Available only in WIZARD level (main branch)

## Local Development Strategy

### Overlay Installation
In local development environments, roles operate as overlays:

1. **Shared Base**: Core components (uCORE, uMEMORY/system, uKNOWLEDGE) are shared
2. **Role Layer**: Role-specific components overlay the shared base
3. **User Layer**: User-specific data and customizations
4. **Development Layer**: Development tools and environment (WIZARD only)

### Development Workflow

1. **Development**: Work in main branch with full development environment
2. **Testing**: Test role-specific functionality in role branches
3. **Distribution**: Each role branch provides clean installation for end users
4. **Synchronization**: Core components sync from main to role branches

## Branch Maintenance

### Automated Synchronization
- Core components automatically sync from main branch
- Role-specific filters applied during sync
- Component permissions enforced during branch updates

### Manual Updates
- Role-specific configurations updated manually
- Installation scripts customized per role
- Documentation tailored to role capabilities

### Release Process
1. Development and testing in main branch
2. Core component updates pushed to all role branches
3. Role-specific updates applied to individual branches
4. Version tags applied across all branches

## Installation Examples

### Quick Installation
Each role branch includes a one-command installation:

```bash
# Ghost role (demo)
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-ghost/install-ghost.sh | bash

# Imp role (development)
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-imp/install-imp.sh | bash

# Wizard role (complete)
curl -sSL https://raw.githubusercontent.com/fredporter/uDOS/role-wizard/install-wizard.sh | bash
```

### Manual Installation
```bash
# Clone specific role
git clone -b role-imp https://github.com/fredporter/uDOS.git uDOS-IMP
cd uDOS-IMP
./install-imp.sh
```

## Benefits

### For Users
- **Clean Installations**: Only components needed for their role level
- **Appropriate Complexity**: Interface complexity matches user expertise
- **Easy Upgrades**: Clear progression path between roles
- **Security**: Role-based access controls enforced at installation level

### For Developers
- **Maintainable**: Clear separation between role-specific and shared components
- **Testable**: Each role can be tested independently
- **Distributable**: Clean, documented installation for each use case
- **Scalable**: Easy to add new roles or modify existing ones

### For System Architecture
- **Modular**: Components can be developed and tested independently
- **Consistent**: Shared core ensures consistent behavior across roles
- **Flexible**: Role overlays allow customization without breaking core functionality
- **Future-Proof**: Architecture supports role evolution and new capabilities

---

*Branch Strategy Documentation - uDOS v1.0.4.1*
EOF

    log_branch "SUCCESS" "Branch strategy documentation created"
}

# Main execution function
main() {
    show_role_banner

    case "${1:-create}" in
        "create"|"all")
            check_prerequisites
            create_all_role_branches
            create_branch_documentation
            list_role_branches
            echo ""
            log_branch "SUCCESS" "Role-based branch creation completed!"
            echo ""
            echo -e "${YELLOW}Next steps:${NC}"
            echo "1. Review created branches: git branch -a"
            echo "2. Push to remote: $0 push"
            echo "3. Test installations from role branches"
            ;;
        "push")
            push_role_branches
            ;;
        "list")
            list_role_branches
            ;;
        "docs")
            create_branch_documentation
            log_branch "SUCCESS" "Documentation created"
            ;;
        *)
            echo "Usage: $0 {create|push|list|docs}"
            echo ""
            echo "Commands:"
            echo "  create  - Create all role-based branches"
            echo "  push    - Push role branches to remote"
            echo "  list    - List role branches and installation commands"
            echo "  docs    - Create branch strategy documentation"
            ;;
    esac
}

# Execute main function
main "$@"
