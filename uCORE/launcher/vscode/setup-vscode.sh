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

# Copy configuration files
cp "$SCRIPT_DIR/settings.json" "$VSCODE_DIR/" 2>/dev/null && echo -e "${GREEN}✅ Settings copied${NC}"
cp "$SCRIPT_DIR/tasks.json" "$VSCODE_DIR/" 2>/dev/null && echo -e "${GREEN}✅ Tasks copied${NC}"
cp "$SCRIPT_DIR/launch.json" "$VSCODE_DIR/" 2>/dev/null && echo -e "${GREEN}✅ Launch config copied${NC}"

# Create workspace file
WORKSPACE_FILE="$UDOS_ROOT/uDOS.code-workspace"
if [ ! -f "$WORKSPACE_FILE" ]; then
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
        }
    ],
    "settings": {
        "terminal.integrated.defaultProfile.osx": "bash",
        "terminal.integrated.defaultProfile.linux": "bash",
        "terminal.integrated.defaultProfile.windows": "Git Bash",
        "terminal.integrated.cwd": "${workspaceFolder}"
    }
}
EOF
    echo -e "${GREEN}✅ Workspace file created${NC}"
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
