#!/bin/bash
# VS Code Setup Script for uDOS Development
# Installs recommended extensions and configures development environment

echo "🔌 Setting up VS Code for uDOS Development..."
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check if VS Code is installed
if ! command -v code >/dev/null 2>&1; then
    echo -e "${RED}❌ VS Code 'code' command not found${NC}"
    echo -e "${YELLOW}💡 Please install VS Code and ensure 'code' is in your PATH${NC}"
    echo ""
    echo "Installation instructions:"
    echo "  • macOS: Install VS Code, then run 'Shell Command: Install code command in PATH'"
    echo "  • Windows: Install VS Code with 'Add to PATH' option"
    echo "  • Linux: Install via package manager or snap"
    exit 1
fi

echo -e "${GREEN}✅ VS Code found${NC}"

# Get script directory and uDOS root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo -e "${BLUE}📂 uDOS Root: $UDOS_ROOT${NC}"

# List of recommended extensions
EXTENSIONS=(
    "ms-python.python"                      # Python support and debugging
    "ms-python.debugpy"                     # Python debugger
    "ms-vscode.vscode-typescript-next"      # TypeScript support
    "yzhang.markdown-all-in-one"            # Markdown support
    "rogalmic.bash-debug"                   # Bash debugging
    "mads-hartmann.bash-ide-vscode"         # Bash IDE features
    "jeff-hykin.better-shellscript-syntax"  # Better shell syntax
    "ms-vscode.theme-monokai-dark"          # Nice dark theme
    "ms-vscode.hexeditor"                   # Hex editor
    "ms-vscode.vscode-json"                 # JSON support
    "redhat.vscode-yaml"                    # YAML support
    "ms-vscode.makefile-tools"              # Makefile support
    "github.copilot"                        # GitHub Copilot
    "github.copilot-chat"                   # GitHub Copilot Chat
)

# Optional extensions (ask user)
OPTIONAL_EXTENSIONS=(
    "ms-python.python"                      # Python support
    "ms-vscode.powershell"                  # PowerShell support (Windows users)
    "ms-vscode.cpptools"                    # C/C++ support
    "golang.go"                             # Go support
    "rust-lang.rust-analyzer"               # Rust support
    "ms-vscode.remote-ssh"                  # Remote SSH
    "ms-vscode-remote.remote-containers"    # Dev Containers
    "gitpod.gitpod-desktop"                 # Gitpod integration
)

# Install core extensions
echo -e "${YELLOW}📦 Installing core extensions...${NC}"
for ext in "${EXTENSIONS[@]}"; do
    echo -n "Installing $ext... "
    if code --install-extension "$ext" --force >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
    fi
done

echo ""

# Ask about optional extensions
echo -e "${BLUE}🤔 Optional extensions:${NC}"
for ext in "${OPTIONAL_EXTENSIONS[@]}"; do
    read -p "Install $ext? (y/N): " install
    if [[ "$install" =~ ^[Yy]$ ]]; then
        echo -n "Installing $ext... "
        if code --install-extension "$ext" --force >/dev/null 2>&1; then
            echo -e "${GREEN}✅${NC}"
        else
            echo -e "${RED}❌${NC}"
        fi
    fi
done

echo ""

# Copy VS Code configuration files
echo -e "${YELLOW}⚙️  Setting up workspace configuration...${NC}"

# Create .vscode directory in uDOS root
VSCODE_DIR="$UDOS_ROOT/.vscode"
mkdir -p "$VSCODE_DIR"

# Copy configuration files from actual .vscode directory
echo -e "${BLUE}📋 Copying VS Code configurations...${NC}"
UDOS_VSCODE_DIR="$UDOS_ROOT/.vscode"

if [ -f "$UDOS_VSCODE_DIR/settings.json" ]; then
    cp "$UDOS_VSCODE_DIR/settings.json" "$VSCODE_DIR/" && echo -e "${GREEN}✅ Enhanced settings copied${NC}"
else
    echo -e "${YELLOW}⚠️ Using fallback settings${NC}"
    cp "$SCRIPT_DIR/settings.json" "$VSCODE_DIR/" 2>/dev/null && echo -e "${GREEN}✅ Settings copied${NC}"
fi

if [ -f "$UDOS_VSCODE_DIR/tasks.json" ]; then
    cp "$UDOS_VSCODE_DIR/tasks.json" "$VSCODE_DIR/" && echo -e "${GREEN}✅ Enhanced tasks copied${NC}"
else
    echo -e "${YELLOW}⚠️ Using fallback tasks${NC}"
    cp "$SCRIPT_DIR/tasks.json" "$VSCODE_DIR/" 2>/dev/null && echo -e "${GREEN}✅ Tasks copied${NC}"
fi

if [ -f "$UDOS_VSCODE_DIR/launch.json" ]; then
    cp "$UDOS_VSCODE_DIR/launch.json" "$VSCODE_DIR/" && echo -e "${GREEN}✅ Enhanced launch config copied${NC}"
else
    echo -e "${YELLOW}⚠️ Using fallback launch config${NC}"
    cp "$SCRIPT_DIR/launch.json" "$VSCODE_DIR/" 2>/dev/null && echo -e "${GREEN}✅ Launch config copied${NC}"
fi

# Create enhanced workspace file
WORKSPACE_FILE="$UDOS_ROOT/uDOS.code-workspace"
if [ ! -f "$WORKSPACE_FILE" ] || [ "$1" = "--force" ]; then
    cat > "$WORKSPACE_FILE" << 'EOF'
{
    "folders": [
        {
            "name": "🏠 uDOS Root",
            "path": "."
        },
        {
            "name": "🧠 Core System",
            "path": "./uCORE"
        },
        {
            "name": "💾 User Memory",
            "path": "./uMEMORY"
        },
        {
            "name": "📚 Knowledge Base",
            "path": "./uKNOWLEDGE"
        },
        {
            "name": "🏗️ Sandbox",
            "path": "./sandbox"
        },
        {
            "name": "🔧 Development",
            "path": "./dev"
        },
        {
            "name": "🌐 Network",
            "path": "./uNETWORK"
        },
        {
            "name": "🐍 Scripts",
            "path": "./uSCRIPT"
        }
    ],
    "settings": {
        "terminal.integrated.defaultProfile.osx": "bash",
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.defaultProfile.windows": "Git Bash",
        "terminal.integrated.cwd": "${workspaceFolder}",
        "files.associations": {
            "*.us": "shellscript",
            "*.utemplate": "markdown",
            "*.umemory": "json"
        },
        "workbench.colorCustomizations": {
            "titleBar.activeBackground": "#2D3748",
            "titleBar.activeForeground": "#FFFFFF",
            "statusBar.background": "#2D3748",
            "statusBar.foreground": "#FFFFFF"
        },
        "editor.rulers": [80, 120],
        "editor.wordWrap": "on",
        "markdown.preview.fontSize": 14,
        "git.ignoreLimitWarning": true
    },
    "extensions": {
        "recommendations": [
            "ms-python.python",
            "ms-python.debugpy",
            "ms-vscode.vscode-typescript-next",
            "yzhang.markdown-all-in-one",
            "ms-vscode.powershell",
            "rogalmic.bash-debug",
            "mads-hartmann.bash-ide-vscode",
            "jeff-hykin.better-shellscript-syntax",
            "github.copilot",
            "github.copilot-chat"
        ]
    }
}
EOF
    echo -e "${GREEN}✅ Enhanced workspace file created${NC}"
fi

# Create uDOS development snippets
SNIPPETS_DIR="$VSCODE_DIR/snippets"
mkdir -p "$SNIPPETS_DIR"

cat > "$SNIPPETS_DIR/udos-bash.json" << 'EOF'
{
    "uDOS Script Header": {
        "prefix": "udos-header",
        "body": [
            "#!/bin/bash",
            "# ${1:Script Description}",
            "# Part of uDOS - Universal Device Operating System",
            "",
            "# Get script directory and uDOS root",
            "SCRIPT_DIR=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"",
            "UDOS_ROOT=\"$(cd \"$SCRIPT_DIR/../..\" && pwd)\"",
            "",
            "# Source common functions",
            "source \"$UDOS_ROOT/uCORE/system/common.sh\"",
            "",
            "${0}"
        ],
        "description": "Standard uDOS bash script header"
    },
    "uDOS Function": {
        "prefix": "udos-function",
        "body": [
            "# ${1:Function description}",
            "${2:function_name}() {",
            "    local ${3:param}=\"$1\"",
            "    ",
            "    ${0}",
            "    ",
            "    return 0",
            "}"
        ],
        "description": "Standard uDOS function template"
    },
    "uDOS Error Handling": {
        "prefix": "udos-error",
        "body": [
            "if ! ${1:command}; then",
            "    echo \"❌ Error: ${2:description}\" >&2",
            "    exit 1",
            "fi"
        ],
        "description": "Standard uDOS error handling"
    },
    "uDOS JSON Check": {
        "prefix": "udos-json",
        "body": [
            "if ! jq empty \"${1:file.json}\" 2>/dev/null; then",
            "    echo \"❌ Invalid JSON in ${1:file.json}\" >&2",
            "    return 1",
            "fi"
        ],
        "description": "JSON validation check"
    }
}
EOF

echo -e "${GREEN}✅ uDOS development snippets created${NC}"

# Create Python environment setup for debugging
echo -e "${BLUE}🐍 Setting up Python debugging environment...${NC}"
cd "$UDOS_ROOT"
if [ -d "uSCRIPT/venv" ]; then
    echo -e "${GREEN}✅ Python virtual environment ready for debugging${NC}"
else
    echo -e "${YELLOW}⚠️ Run './uSCRIPT/setup-environment.sh' to create Python environment${NC}"
fi

echo ""
echo -e "${GREEN}🎉 VS Code setup complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Open uDOS workspace: ${YELLOW}code $WORKSPACE_FILE${NC}"
echo "  2. Use tasks: ${YELLOW}Ctrl+Shift+P > Tasks: Run Task${NC}"
echo "  3. Start debugging: ${YELLOW}F5${NC}"
echo ""
echo -e "${BLUE}Available tasks:${NC}"
echo "  • 🌀 Start uDOS"
echo "  • 🧠 Development Mode"
echo "  • 🔍 Check Installation"
echo "  • 📊 Generate Dashboard"
echo "  • 💾 Setup User Memory"
