#!/bin/bash

# uDOS Deployment Manager v1.0 - Extension
# Comprehensive deployment system for multiple installation types
# Includes drone management plus additional deployment scenarios

set -euo pipefail

# Extension metadata
readonly EXTENSION_ID="deployment-manager"
readonly EXTENSION_VERSION="1.0.0"
readonly EXTENSION_NAME="uDOS Deployment Manager"

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly UCORE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
readonly PROJECT_ROOT="$(dirname "$UCORE_DIR")"
readonly TEMPLATES_DIR="$SCRIPT_DIR/templates"
readonly DEPLOYMENTS_DIR="$PROJECT_ROOT/uMEMORY/deployments"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# Logging function
log_action() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] DEPLOY: $message" >> "$PROJECT_ROOT/uMEMORY/logs/deployment.log"
}

# Display extension header
show_deploy_header() {
    echo ""
    echo -e "${CYAN}██████╗ ███████╗██████╗ ██╗      ██████╗ ██╗   ██╗███╗   ███╗███████╗███╗   ██╗████████╗${NC}"
    echo -e "${CYAN}██╔══██╗██╔════╝██╔══██╗██║     ██╔═══██╗╚██╗ ██╔╝████╗ ████║██╔════╝████╗  ██║╚══██╔══╝${NC}"
    echo -e "${CYAN}██║  ██║█████╗  ██████╔╝██║     ██║   ██║ ╚████╔╝ ██╔████╔██║█████╗  ██╔██╗ ██║   ██║   ${NC}"
    echo -e "${CYAN}██║  ██║██╔══╝  ██╔═══╝ ██║     ██║   ██║  ╚██╔╝  ██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   ${NC}"
    echo -e "${CYAN}██████╔╝███████╗██║     ███████╗╚██████╔╝   ██║   ██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   ${NC}"
    echo -e "${CYAN}╚═════╝ ╚══════╝╚═╝     ╚══════╝ ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ${NC}"
    echo ""
    echo -e "${BOLD}$EXTENSION_NAME v$EXTENSION_VERSION${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Initialize deployment system
init_deployment_system() {
    mkdir -p "$DEPLOYMENTS_DIR"/{active,completed,templates,logs}
    mkdir -p "$TEMPLATES_DIR"/{drone,standalone,server,portable,cloud,developer}
    
    # Create deployment log
    touch "$PROJECT_ROOT/uMEMORY/logs/deployment.log"
    
    log_action "Deployment system initialized"
}

# Create installation templates
create_deployment_templates() {
    local template_type="$1"
    
    case "$template_type" in
        "drone")
            cat > "$TEMPLATES_DIR/drone/minimal-drone.json" << 'EOF'
{
  "template_id": "minimal-drone",
  "name": "Minimal Drone Installation",
  "type": "drone",
  "description": "Lightweight remote installation with core functionality",
  "requirements": {
    "disk_space_mb": 50,
    "memory_mb": 256,
    "network": "optional"
  },
  "components": [
    "uCORE/code/ucode.sh",
    "uCORE/code/log.sh", 
    "uCORE/templates/system/",
    "uMEMORY/templates/"
  ],
  "structure": {
    "uCode/": ["ucode.sh", "log.sh"],
    "uMemory/": ["active/", "templates/", "archive/"],
    "uTemplate/": ["drone/", "system/", "user/"],
    ".drone/": ["config/", "status/", "logs/"],
    "docs/": ["README.md"],
    "install/": ["install-drone.sh"]
  },
  "config": {
    "offline_capable": true,
    "auto_sync": false,
    "telemetry": "minimal"
  }
}
EOF
            ;;
        "standalone")
            cat > "$TEMPLATES_DIR/standalone/standard-installation.json" << 'EOF'
{
  "template_id": "standard-installation",
  "name": "Standard Standalone Installation",
  "type": "standalone",
  "description": "Complete self-contained installation",
  "requirements": {
    "disk_space_mb": 500,
    "memory_mb": 512,
    "network": "recommended"
  },
  "components": [
    "uCORE/",
    "uMEMORY/",
    "uKNOWLEDGE/",
    "wizard/",
    "docs/"
  ],
  "structure": {
    "uCORE/": "complete",
    "uMEMORY/": "complete",
    "uKNOWLEDGE/": "complete", 
    "wizard/": "basic",
    "docs/": "user-facing"
  },
  "config": {
    "offline_capable": true,
    "auto_sync": true,
    "telemetry": "standard",
    "extensions_enabled": true
  }
}
EOF
            ;;
        "server")
            cat > "$TEMPLATES_DIR/server/server-deployment.json" << 'EOF'
{
  "template_id": "server-deployment",
  "name": "Server Installation",
  "type": "server",
  "description": "Server-based installation with multi-user support",
  "requirements": {
    "disk_space_mb": 2000,
    "memory_mb": 2048,
    "network": "required",
    "users": "multiple"
  },
  "components": [
    "uCORE/",
    "uMEMORY/shared/",
    "uSERVER/",
    "uAUTH/",
    "docs/"
  ],
  "structure": {
    "uCORE/": "server-optimized",
    "uMEMORY/shared/": "multi-user",
    "uSERVER/": ["api/", "web/", "auth/"],
    "uAUTH/": ["users/", "permissions/", "sessions/"],
    "logs/": ["access/", "system/", "security/"]
  },
  "config": {
    "offline_capable": false,
    "auto_sync": true,
    "telemetry": "full",
    "extensions_enabled": true,
    "multi_user": true,
    "api_enabled": true
  }
}
EOF
            ;;
        "portable")
            cat > "$TEMPLATES_DIR/portable/portable-package.json" << 'EOF'
{
  "template_id": "portable-package",
  "name": "Portable USB Installation",
  "type": "portable",
  "description": "USB/removable media installation",
  "requirements": {
    "disk_space_mb": 1000,
    "memory_mb": 256,
    "network": "optional",
    "media": "removable"
  },
  "components": [
    "uCORE/portable/",
    "uMEMORY/portable/",
    "uPORTABLE/",
    "launchers/"
  ],
  "structure": {
    "uCORE/portable/": "optimized",
    "uMEMORY/portable/": "compressed",
    "uPORTABLE/": ["sync/", "backup/", "settings/"],
    "launchers/": ["windows/", "macos/", "linux/"],
    "autorun/": ["autorun.inf", "start.sh", "start.bat"]
  },
  "config": {
    "offline_capable": true,
    "auto_sync": false,
    "telemetry": "none",
    "portable_mode": true,
    "cross_platform": true
  }
}
EOF
            ;;
        "developer")
            cat > "$TEMPLATES_DIR/developer/developer-setup.json" << 'EOF'
{
  "template_id": "developer-setup", 
  "name": "Developer Environment",
  "type": "developer",
  "description": "Development environment with full toolchain",
  "requirements": {
    "disk_space_mb": 5000,
    "memory_mb": 4096,
    "network": "required",
    "tools": "development"
  },
  "components": [
    "uCORE/",
    "uMEMORY/", 
    "uKNOWLEDGE/",
    "wizard/complete/",
    "docs/technical/",
    "tools/"
  ],
  "structure": {
    "uCORE/": "complete-with-source",
    "wizard/": "full-workflow-system",
    "tools/": ["debugger/", "profiler/", "analyzer/"],
    "environments/": ["staging/", "testing/", "production/"],
    "repositories/": ["local/", "remote/", "backup/"]
  },
  "config": {
    "offline_capable": true,
    "auto_sync": true,
    "telemetry": "development", 
    "extensions_enabled": true,
    "development_mode": true,
    "debugging_enabled": true
  }
}
EOF
            ;;
    esac
}

# Deploy drone installation (enhanced from original)
deploy_drone() {
    local target_path="$1"
    local template="${2:-minimal-drone}"
    
    show_deploy_header
    echo -e "${BLUE}🚁 Deploying Drone Installation${NC}"
    echo -e "Target: $target_path"
    echo -e "Template: $template"
    echo ""
    
    # Create template if it doesn't exist
    if [[ ! -f "$TEMPLATES_DIR/drone/$template.json" ]]; then
        echo -e "${YELLOW}⚠️ Template not found, creating minimal drone template...${NC}"
        create_deployment_templates "drone"
    fi
    
    # Load template configuration
    local template_file="$TEMPLATES_DIR/drone/$template.json"
    
    if command -v jq >/dev/null 2>&1; then
        local disk_requirement=$(jq -r '.requirements.disk_space_mb' "$template_file")
        local memory_requirement=$(jq -r '.requirements.memory_mb' "$template_file")
        
        echo -e "${CYAN}Requirements:${NC}"
        echo -e "  Disk Space: ${disk_requirement}MB"
        echo -e "  Memory: ${memory_requirement}MB"
        echo ""
    fi
    
    # Create drone directory structure
    echo -e "${CYAN}Creating directory structure...${NC}"
    mkdir -p "$target_path"/{uCode,uMemory/{active,templates,archive},uTemplate/{drone,system,user},.drone/{config,status,logs},docs,install}
    
    # Copy core files
    echo -e "${CYAN}Copying core files...${NC}"
    cp "$UCORE_DIR/code/ucode.sh" "$target_path/uCode/" 2>/dev/null || echo "⚠️ ucode.sh not found"
    cp "$UCORE_DIR/code/log.sh" "$target_path/uCode/" 2>/dev/null || echo "⚠️ log.sh not found"
    
    # Copy templates
    if [[ -d "$UCORE_DIR/templates" ]]; then
        cp -r "$UCORE_DIR/templates"/* "$target_path/uTemplate/" 2>/dev/null || true
    fi
    
    # Create drone-specific configuration
    cat > "$target_path/.drone/config/drone.json" << EOF
{
  "drone_id": "$(uuidgen 2>/dev/null || echo "drone-$(date +%s)")",
  "deployment_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "template": "$template",
  "version": "$EXTENSION_VERSION",
  "parent_system": "$(hostname)",
  "config": {
    "offline_mode": true,
    "sync_enabled": false,
    "telemetry_level": "minimal"
  }
}
EOF
    
    # Create README
    cat > "$target_path/README.md" << 'DRONE_README'
# uDOS Drone Installation

This is a lightweight uDOS drone installation created by the Deployment Manager extension.

## Quick Start
1. Navigate to the installation directory
2. Start the drone: `./uCode/ucode.sh`

## Features
- Offline-capable operation
- Template-driven workflows
- Clean, organized file structure
- Self-validating system

## Management
- Status: `./uCode/ucode.sh STATUS`
- Logs: `./uCode/log.sh recent`

Generated by uDOS Deployment Manager v1.0
DRONE_README
    
    # Create launcher script
    cat > "$target_path/start-drone.sh" << 'START_SCRIPT'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "🚁 Starting uDOS Drone..."
./uCode/ucode.sh
START_SCRIPT
    chmod +x "$target_path/start-drone.sh"
    
    # Validate deployment
    if validate_deployment "$target_path" "drone"; then
        echo -e "${GREEN}✅ Drone deployment successful!${NC}"
        echo ""
        echo -e "${BOLD}Next steps:${NC}"
        echo -e "  1. cd $target_path"
        echo -e "  2. ./start-drone.sh"
        echo ""
        
        log_action "Drone deployed successfully: $target_path (template: $template)"
        return 0
    else
        echo -e "${RED}❌ Drone deployment validation failed${NC}"
        return 1
    fi
}

# Deploy standalone installation
deploy_standalone() {
    local target_path="$1"
    local config="${2:-standard-installation}"
    
    show_deploy_header
    echo -e "${BLUE}🏠 Deploying Standalone Installation${NC}"
    echo -e "Target: $target_path"
    echo -e "Configuration: $config"
    echo ""
    
    # Create template if needed
    if [[ ! -f "$TEMPLATES_DIR/standalone/$config.json" ]]; then
        create_deployment_templates "standalone"
    fi
    
    echo -e "${CYAN}Creating complete uDOS installation...${NC}"
    
    # Copy entire uDOS system
    mkdir -p "$target_path"
    cp -r "$PROJECT_ROOT"/{uCORE,uMEMORY,uKNOWLEDGE,docs} "$target_path/" 2>/dev/null || true
    
    # Create standalone-specific configuration
    cat > "$target_path/uCORE/config/standalone.json" << EOF
{
  "installation_type": "standalone",
  "deployment_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "configuration": "$config",
  "features": {
    "offline_capable": true,
    "auto_sync": true,
    "extensions_enabled": true
  }
}
EOF
    
    # Create launcher
    cat > "$target_path/start-udos.sh" << 'STANDALONE_START'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "🚀 Starting uDOS Standalone..."
./uCORE/code/ucode.sh
STANDALONE_START
    chmod +x "$target_path/start-udos.sh"
    
    echo -e "${GREEN}✅ Standalone installation deployed!${NC}"
    log_action "Standalone deployment: $target_path (config: $config)"
}

# Deploy server installation
deploy_server() {
    local target_host="$1"
    local options="${2:-server-deployment}"
    
    show_deploy_header
    echo -e "${BLUE}🌐 Deploying Server Installation${NC}"
    echo -e "Target Host: $target_host"
    echo -e "Options: $options"
    echo ""
    
    echo -e "${YELLOW}Note: Server deployment requires SSH access and additional setup${NC}"
    echo -e "${CYAN}This would include:${NC}"
    echo -e "  • Multi-user authentication system"
    echo -e "  • Web API endpoints"
    echo -e "  • Shared memory management"
    echo -e "  • Security hardening"
    echo -e "  • Backup and recovery"
    echo ""
    
    log_action "Server deployment initiated: $target_host (options: $options)"
}

# Deploy portable installation
deploy_portable() {
    local target_device="$1"
    local size_limit="${2:-1000}"
    
    show_deploy_header
    echo -e "${BLUE}💾 Creating Portable Installation${NC}"
    echo -e "Target Device: $target_device"
    echo -e "Size Limit: ${size_limit}MB"
    echo ""
    
    # Create template if needed
    if [[ ! -f "$TEMPLATES_DIR/portable/portable-package.json" ]]; then
        create_deployment_templates "portable"
    fi
    
    echo -e "${CYAN}Creating portable package...${NC}"
    
    # Create optimized portable structure
    local portable_dir="$target_device/uDOS-Portable"
    mkdir -p "$portable_dir"/{uCORE-portable,uMemory-portable,launchers/{windows,macos,linux}}
    
    # Copy essential components only
    cp "$UCORE_DIR/code/ucode.sh" "$portable_dir/uCORE-portable/"
    cp "$UCORE_DIR/code/log.sh" "$portable_dir/uCORE-portable/"
    
    # Create cross-platform launchers
    cat > "$portable_dir/launchers/windows/start-udos.bat" << 'WIN_LAUNCHER'
@echo off
cd /d "%~dp0..\.."
echo Starting uDOS Portable...
bash uCORE-portable/ucode.sh
pause
WIN_LAUNCHER
    
    cat > "$portable_dir/launchers/macos/start-udos.command" << 'MAC_LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")/../.."
echo "Starting uDOS Portable..."
./uCORE-portable/ucode.sh
MAC_LAUNCHER
    chmod +x "$portable_dir/launchers/macos/start-udos.command"
    
    cat > "$portable_dir/launchers/linux/start-udos.sh" << 'LINUX_LAUNCHER'
#!/bin/bash
cd "$(dirname "$0")/../.."
echo "Starting uDOS Portable..."
./uCORE-portable/ucode.sh
LINUX_LAUNCHER
    chmod +x "$portable_dir/launchers/linux/start-udos.sh"
    
    echo -e "${GREEN}✅ Portable installation created!${NC}"
    log_action "Portable deployment: $target_device (size: ${size_limit}MB)"
}

# Validate deployment
validate_deployment() {
    local target_path="$1"
    local deployment_type="$2"
    
    local errors=0
    
    case "$deployment_type" in
        "drone")
            # Check drone-specific requirements
            local required_files=("uCode/ucode.sh" ".drone/config/drone.json" "start-drone.sh")
            ;;
        "standalone")
            local required_files=("uCORE/code/ucode.sh" "start-udos.sh")
            ;;
        "portable")
            local required_files=("uCORE-portable/ucode.sh" "launchers/macos/start-udos.command")
            ;;
        *)
            local required_files=("uCode/ucode.sh")
            ;;
    esac
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$target_path/$file" ]]; then
            echo -e "${RED}❌ Missing: $file${NC}"
            ((errors++))
        fi
    done
    
    if [[ $errors -eq 0 ]]; then
        echo -e "${GREEN}✅ Deployment validation successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Deployment validation failed ($errors errors)${NC}"
        return 1
    fi
}

# List available deployments and templates
list_deployments() {
    local filter="${1:-all}"
    
    show_deploy_header
    echo -e "${BOLD}📋 Available Deployment Types${NC}"
    echo ""
    
    echo -e "${CYAN}🚁 DRONE${NC} - Lightweight remote installations"
    echo -e "   Templates: minimal-drone, specialized-drone"
    echo -e "   Use: DEPLOY DRONE <path> [template]"
    echo ""
    
    echo -e "${CYAN}🏠 STANDALONE${NC} - Complete self-contained installations"
    echo -e "   Templates: standard-installation, custom-config"
    echo -e "   Use: DEPLOY STANDALONE <path> [config]"
    echo ""
    
    echo -e "${CYAN}🌐 SERVER${NC} - Multi-user server installations"
    echo -e "   Templates: server-deployment, enterprise-setup"
    echo -e "   Use: DEPLOY SERVER <host> [options]"
    echo ""
    
    echo -e "${CYAN}💾 PORTABLE${NC} - USB/removable media installations"
    echo -e "   Templates: portable-package, mini-portable"
    echo -e "   Use: DEPLOY PORTABLE <target> [size]"
    echo ""
    
    echo -e "${CYAN}☁️ CLOUD${NC} - Cloud-based deployments (Future)"
    echo -e "   Templates: aws-deployment, azure-setup"
    echo -e "   Use: DEPLOY CLOUD <provider> [config]"
    echo ""
    
    echo -e "${CYAN}👨‍💻 DEVELOPER${NC} - Development environments (Future)"
    echo -e "   Templates: developer-setup, testing-environment"
    echo -e "   Use: DEPLOY DEVELOPER <path> [tools]"
}

# Main command dispatcher
main() {
    case "${1:-LIST}" in
        "DRONE")
            [[ $# -lt 2 ]] && { echo "Usage: deployment-manager.sh DRONE <path> [template]" >&2; exit 1; }
            init_deployment_system
            deploy_drone "$2" "${3:-minimal-drone}"
            ;;
        "STANDALONE")
            [[ $# -lt 2 ]] && { echo "Usage: deployment-manager.sh STANDALONE <path> [config]" >&2; exit 1; }
            init_deployment_system
            deploy_standalone "$2" "${3:-standard-installation}"
            ;;
        "SERVER")
            [[ $# -lt 2 ]] && { echo "Usage: deployment-manager.sh SERVER <host> [options]" >&2; exit 1; }
            init_deployment_system
            deploy_server "$2" "${3:-server-deployment}"
            ;;
        "PORTABLE")
            [[ $# -lt 2 ]] && { echo "Usage: deployment-manager.sh PORTABLE <target> [size]" >&2; exit 1; }
            init_deployment_system
            deploy_portable "$2" "${3:-1000}"
            ;;
        "VALIDATE")
            [[ $# -lt 2 ]] && { echo "Usage: deployment-manager.sh VALIDATE <installation>" >&2; exit 1; }
            validate_deployment "$2" "auto-detect"
            ;;
        "LIST"|*)
            list_deployments "${2:-all}"
            ;;
    esac
}

# Execute main with all arguments
main "$@"
