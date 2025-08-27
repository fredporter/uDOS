#!/bin/bash
# uDOS VS Code Development Mode Launcher (Wizard Only) v1.0.4.1
# Enhanced development environment with full Git integration

set -euo pipefail

# Configuration
export UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
export UDOS_VERSION="1.0.4.1"

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# Check if wizard role is available
check_wizard_permissions() {
    if [[ ! -d "$UDOS_ROOT/wizard" ]]; then
        echo -e "${RED}❌ Wizard role not available${NC}"
        echo -e "${YELLOW}💡 VS Code development mode requires wizard role${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Wizard permissions verified${NC}"
}

# Check VS Code availability
check_vscode_availability() {
    if ! command -v code >/dev/null 2>&1; then
        echo -e "${RED}❌ VS Code not found${NC}"
        echo -e "${YELLOW}💡 Please install VS Code and add 'code' command to PATH${NC}"
        echo ""
        echo "Installation instructions:"
        echo "1. Install VS Code from https://code.visualstudio.com/"
        echo "2. Open VS Code"
        echo "3. Press Cmd+Shift+P"
        echo "4. Type 'Shell Command: Install 'code' command in PATH'"
        echo "5. Select and run the command"
        exit 1
    fi
    
    echo -e "${GREEN}✅ VS Code available${NC}"
}

# Setup VS Code workspace
setup_vscode_workspace() {
    echo -e "${BLUE}🔧 Setting up VS Code workspace...${NC}"
    
    # Create .vscode directory if it doesn't exist
    mkdir -p "$UDOS_ROOT/.vscode"
    
    # Create VS Code settings
    cat > "$UDOS_ROOT/.vscode/settings.json" << 'EOF'
{
    "terminal.integrated.defaultProfile.osx": "zsh",
    "terminal.integrated.profiles.osx": {
        "uDOS Terminal": {
            "path": "/bin/zsh",
            "args": ["-c", "export UDOS_MODE=development && cd '${workspaceFolder}' && exec zsh"]
        }
    },
    "files.associations": {
        "*.udos": "json",
        "*.uproject": "json",
        "*.uconfig": "json"
    },
    "editor.fontSize": 12,
    "editor.fontFamily": "Monaco, 'Courier New', monospace",
    "terminal.integrated.fontSize": 11,
    "terminal.integrated.fontFamily": "Monaco, 'Courier New', monospace",
    "workbench.colorTheme": "Default Dark+",
    "git.enableSmartCommit": true,
    "git.confirmSync": false,
    "git.autofetch": true,
    "extensions.autoUpdate": false,
    "telemetry.telemetryLevel": "off"
}
EOF

    # Create VS Code tasks
    cat > "$UDOS_ROOT/.vscode/tasks.json" << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "🧙‍♂️ Start uDOS Wizard",
            "type": "shell",
            "command": "${workspaceFolder}/uCORE/launcher/universal/start-udos.sh",
            "args": ["wizard", "--ui-mode"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "🔧 Start uSERVER Only",
            "type": "shell",
            "command": "${workspaceFolder}/uCORE/launcher/universal/start-udos.sh",
            "args": ["wizard", "--server-only"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        }
    ]
}
EOF

    echo -e "${GREEN}✅ VS Code workspace configured${NC}"
}

# Launch VS Code development environment
launch_vscode_development() {
    echo -e "${PURPLE}🧙‍♂️ Launching VS Code Development Environment...${NC}"
    
    cd "$UDOS_ROOT"
    
    # Run enhanced VS Code setup
    echo -e "${BLUE}🔧 Configuring VS Code for uDOS development...${NC}"
    if [ -f "$UDOS_ROOT/uSCRIPT/integration/vscode/setup-vscode.sh" ]; then
        "$UDOS_ROOT/uSCRIPT/integration/vscode/setup-vscode.sh"
    else
        echo -e "${YELLOW}⚠️ VS Code setup script not found, using basic workspace${NC}"
        # Create basic workspace file as fallback
        cat > "$UDOS_ROOT/uDOS.code-workspace" << 'EOF'
{
    "folders": [
        {
            "name": "🧙‍♂️ uDOS Wizard",
            "path": "."
        }
    ],
    "settings": {
        "terminal.integrated.defaultProfile.osx": "bash",
        "terminal.integrated.defaultProfile.linux": "bash"
    }
}
EOF
    fi
    
    # Open workspace
    echo -e "${BLUE}📂 Opening uDOS workspace in VS Code...${NC}"
    code "$UDOS_ROOT/uDOS.code-workspace"
    
    echo -e "${GREEN}✅ VS Code development environment ready${NC}"
    echo ""
    echo -e "${WHITE}Available VS Code features:${NC}"
    echo -e "  ${GREEN}🐛 Debugging${NC} - Press F5 to debug bash scripts"
    echo -e "  ${GREEN}⚡ Tasks${NC} - Ctrl+Shift+P > Tasks: Run Task"
    echo -e "  ${GREEN}🧙‍♂️ Copilot${NC} - AI-assisted development"
    echo -e "  ${GREEN}📝 Snippets${NC} - Type 'udos-' for code templates"
    echo ""
    echo -e "${WHITE}Quick tasks:${NC}"
    echo -e "  ${GREEN}🌀 Start uDOS${NC} - Launch full system"
    echo -e "  ${GREEN}🧠 Development Mode${NC} - Enhanced dev environment"
    echo -e "  ${GREEN}🔍 Check Installation${NC} - Validate system"
    echo -e "  ${GREEN}📊 Generate Dashboard${NC} - Create status dashboard"
    echo ""
}

# Main function
main() {
    echo -e "${PURPLE}"
    echo "   🧙‍♂️ uDOS VS Code Development Mode"
    echo "   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
    echo -e "${WHITE}Wizard Development Environment v$UDOS_VERSION${NC}"
    echo ""
    
    check_wizard_permissions
    check_vscode_availability
    setup_vscode_workspace
    launch_vscode_development
}

# Execute main function
main
