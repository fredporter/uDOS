#!/bin/bash
# uDOS VS Code Development Mode Launcher
# Streamlined development with integrated UI preview

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
export UDOS_ROOT
export UDOS_MODE="vscode-dev"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

echo -e "${WHITE}🧙‍♂️ uDOS VS Code Development Mode${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Start development server in background
start_dev_server() {
    echo -e "${BLUE}🚀 Starting uDOS development server...${NC}"

    cd "$UDOS_ROOT"

    # Kill any existing server
    pkill -f "uNETWORK/server/server.py" 2>/dev/null || true

    # Activate Python virtual environment
    source "$UDOS_ROOT/uSCRIPT/activate-venv.sh"

    # Start server with development flags
    export UDOS_CURRENT_ROLE="wizard"
    export UDOS_ACCESS_LEVEL="100"
    export UDOS_DEV_MODE="true"

    python "$UDOS_ROOT/uNETWORK/server/server.py" &
    SERVER_PID=$!
    echo $SERVER_PID > /tmp/udos-dev-server.pid

    # Wait for server to start
    local attempts=0
    while [[ $attempts -lt 15 ]]; do
        if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Development server running on http://localhost:8080${NC}"
            return 0
        fi
        echo -e "${YELLOW}⏳ Waiting for server... ($((attempts + 1))/15)${NC}"
        sleep 1
        ((attempts++))
    done

    echo -e "${RED}❌ Failed to start development server${NC}"
    return 1
}

# Setup VS Code workspace configuration
setup_vscode_workspace() {
    echo -e "${BLUE}⚙️ Configuring VS Code workspace...${NC}"

    # Create development workspace file
    cat > "$UDOS_ROOT/.vscode/udos-dev.code-workspace" << 'EOF'
{
    "folders": [
        {
            "name": "🏠 uDOS Root",
            "path": "."
        },
        {
            "name": "🧠 uCORE",
            "path": "./uCORE"
        },
        {
            "name": "🖥️ uSERVER",
            "path": "./uSERVER"
        },
        {
            "name": "🌐 UI Components",
            "path": "./uCORE/launcher/universal/ucode-ui"
        }
    ],
    "settings": {
        "workbench.colorTheme": "Default Dark+",
        "terminal.integrated.defaultProfile.osx": "uDOS Development",
        "terminal.integrated.profiles.osx": {
            "uDOS Development": {
                "path": "/bin/bash",
                "args": ["-l"],
                "env": {
                    "UDOS_ROOT": "${workspaceFolder}",
                    "UDOS_MODE": "vscode-dev",
                    "PS1": "🧙‍♂️ uDOS-DEV \\w $ "
                },
                "icon": "terminal"
            }
        },
        "livePreview.defaultPreviewPath": "/uCORE/launcher/universal/ucode-ui/index.html",
        "files.associations": {
            "*.udos": "javascript",
            "*.ucode": "html"
        },
        "editor.minimap.enabled": false,
        "workbench.editor.limit.enabled": true,
        "workbench.editor.limit.value": 5
    },
    "extensions": {
        "recommendations": [
            "ms-vscode.vscode-livepreview",
            "bradlc.vscode-tailwindcss",
            "formulahendry.auto-rename-tag",
            "ms-python.python",
            "ms-vscode.vscode-json"
        ]
    }
}
EOF

    echo -e "${GREEN}✅ Workspace configuration created${NC}"
}

# Install and setup VS Code extensions
setup_vscode_extensions() {
    echo -e "${BLUE}📦 Setting up VS Code extensions...${NC}"

    # Install essential extensions for uDOS development
    local extensions=(
        "ms-vscode.vscode-livepreview"
        "ms-python.python"
        "bradlc.vscode-tailwindcss"
        "formulahendry.auto-rename-tag"
    )

    for ext in "${extensions[@]}"; do
        if ! code --list-extensions | grep -q "$ext"; then
            echo -e "${YELLOW}Installing $ext...${NC}"
            code --install-extension "$ext" --force
        else
            echo -e "${GREEN}✓ $ext already installed${NC}"
        fi
    done
}

# Open VS Code with integrated preview
open_vscode_with_preview() {
    echo -e "${BLUE}📝 Opening VS Code with integrated UI preview...${NC}"

    # Open workspace
    code "$UDOS_ROOT/.vscode/udos-dev.code-workspace"

    # Wait for VS Code to load
    sleep 3

    # Start live preview of the UI
    code --command "livePreview.start.preview.atFile" "$UDOS_ROOT/uCORE/launcher/universal/ucode-ui/index.html"

    echo -e "${GREEN}✅ VS Code opened with live UI preview${NC}"
}

# Create development CLI interface
start_dev_cli() {
    echo ""
    echo -e "${WHITE}🖥️ uDOS Development CLI Ready${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📝 VS Code: Workspace with live UI preview${NC}"
    echo -e "${YELLOW}🌐 Server: http://localhost:8080${NC}"
    echo -e "${YELLOW}🔧 API: http://localhost:8080/api/${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${WHITE}Development commands:${NC}"
    echo "  s | status     - Show server status"
    echo "  r | restart    - Restart development server"
    echo "  l | logs       - Show server logs"
    echo "  u | ui         - Open UI in browser"
    echo "  p | preview    - Refresh VS Code preview"
    echo "  t | test       - Run quick tests"
    echo "  c | commit     - Quick git commit"
    echo "  q | quit       - Stop development server"
    echo "  h | help       - Show this help"
    echo ""

    dev_cli_loop
}

# Development CLI command loop
dev_cli_loop() {
    while true; do
        read -p "🧙‍♂️ uDOS-DEV> " -r command args

        case "$command" in
            "status"|"s")
                show_dev_status
                ;;
            "restart"|"r")
                restart_dev_server
                ;;
            "logs"|"l")
                show_dev_logs
                ;;
            "ui"|"u")
                open http://localhost:8080
                echo -e "${GREEN}✅ UI opened in browser${NC}"
                ;;
            "preview"|"p")
                code --command "livePreview.start.preview.atFile" "$UDOS_ROOT/uCORE/launcher/universal/ucode-ui/index.html"
                echo -e "${GREEN}✅ VS Code preview refreshed${NC}"
                ;;
            "test"|"t")
                run_quick_tests
                ;;
            "commit"|"c")
                quick_commit "$args"
                ;;
            "quit"|"q"|"exit")
                stop_dev_server
                break
                ;;
            "help"|"h"|"")
                echo "Commands: status(s), restart(r), logs(l), ui(u), preview(p), test(t), commit(c), quit(q)"
                ;;
            *)
                echo -e "${RED}Unknown command: $command${NC} (try 'help')"
                ;;
        esac
    done
}

# Show development status
show_dev_status() {
    echo -e "${BLUE}📊 Development Status:${NC}"
    echo "─────────────────────────────"

    # Check server
    if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
        echo -e "🟢 Server: ${GREEN}Running on port 8080${NC}"

        # Get detailed status
        local status_info=$(curl -s http://localhost:8080/api/status | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Mode: {data.get('mode', 'unknown')}, Clients: {data.get('clients', 0)}, Uptime: {int(data.get('uptime', 0))}s\")")
        echo -e "   ${YELLOW}$status_info${NC}"
    else
        echo -e "🔴 Server: ${RED}Not responding${NC}"
    fi

    # Check VS Code
    if pgrep -f "Visual Studio Code" >/dev/null 2>&1; then
        echo -e "🟢 VS Code: ${GREEN}Running${NC}"
    else
        echo -e "🔴 VS Code: ${RED}Not detected${NC}"
    fi

    # Check files
    if [ -f "$UDOS_ROOT/uCORE/launcher/universal/ucode-ui/index.html" ]; then
        echo -e "🟢 UI Files: ${GREEN}Available${NC}"
    else
        echo -e "🔴 UI Files: ${RED}Missing${NC}"
    fi

    echo -e "📁 Working directory: ${YELLOW}$PWD${NC}"
    echo -e "🧙‍♂️ Role: ${WHITE}Wizard (Development Mode)${NC}"
}

# Restart development server
restart_dev_server() {
    echo -e "${YELLOW}🔄 Restarting development server...${NC}"

    # Stop current server
    stop_dev_server

    # Start new server
    start_dev_server

    # Refresh VS Code preview
    sleep 1
    code --command "livePreview.start.preview.atFile" "$UDOS_ROOT/uCORE/launcher/universal/ucode-ui/index.html"

    echo -e "${GREEN}✅ Development server restarted${NC}"
}

# Show development logs
show_dev_logs() {
    echo -e "${BLUE}📋 Development Logs:${NC}"
    echo "─────────────────────"

    # Show recent terminal output or server logs
    if [ -f "/tmp/udos-dev.log" ]; then
        tail -20 /tmp/udos-dev.log
    else
        echo -e "${YELLOW}No development logs found${NC}"
        echo "Server should be logging to console..."
    fi
}

# Run quick tests
run_quick_tests() {
    echo -e "${BLUE}🧪 Running quick tests...${NC}"

    local passed=0
    local total=0

    # Test 1: Server Response
    echo -n "1. Server Response: "
    ((total++))
    if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Pass${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ Fail${NC}"
    fi

    # Test 2: UI Loading
    echo -n "2. UI Loading: "
    ((total++))
    if curl -s http://localhost:8080 | grep -q "uDOS" 2>/dev/null; then
        echo -e "${GREEN}✅ Pass${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ Fail${NC}"
    fi

    # Test 3: API Endpoints
    echo -n "3. API Endpoints: "
    ((total++))
    if curl -s http://localhost:8080/api/status | grep -q "running" 2>/dev/null; then
        echo -e "${GREEN}✅ Pass${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ Fail${NC}"
    fi

    # Test 4: File Structure
    echo -n "4. File Structure: "
    ((total++))
    if [ -f "$UDOS_ROOT/uNETWORK/server/server.py" ] && [ -d "$UDOS_ROOT/uCORE" ]; then
        echo -e "${GREEN}✅ Pass${NC}"
        ((passed++))
    else
        echo -e "${RED}❌ Fail${NC}"
    fi

    echo "─────────────────────"
    echo -e "Results: ${GREEN}$passed${NC}/${total} tests passed"
}

# Quick commit function
quick_commit() {
    local message="$*"
    if [ -z "$message" ]; then
        message="Development update - $(date '+%H:%M')"
    fi

    echo -e "${YELLOW}📝 Quick commit: $message${NC}"

    # Show what will be committed
    echo -e "${BLUE}Changes to commit:${NC}"
    git status --porcelain | head -10

    # Commit
    git add -A
    if git commit -m "$message"; then
        echo -e "${GREEN}✅ Committed successfully${NC}"
    else
        echo -e "${RED}❌ Commit failed${NC}"
    fi
}

# Stop development server
stop_dev_server() {
    echo -e "${YELLOW}🛑 Stopping development server...${NC}"

    # Kill server process
    if [ -f /tmp/udos-dev-server.pid ]; then
        local pid=$(cat /tmp/udos-dev-server.pid)
        kill -TERM $pid 2>/dev/null || kill -9 $pid 2>/dev/null || true
        rm -f /tmp/udos-dev-server.pid
    fi

    # Also kill any remaining python server processes
    pkill -f "uNETWORK/server/server.py" 2>/dev/null || true

    echo -e "${GREEN}✅ Development server stopped${NC}"
}

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up development session...${NC}"
    stop_dev_server
    echo -e "${WHITE}👋 uDOS Development session ended${NC}"
}

trap cleanup EXIT INT TERM

# Main execution
main() {
    echo -e "${BLUE}🔧 Initializing uDOS Development Environment...${NC}"

    # Start development server
    start_dev_server || {
        echo -e "${RED}❌ Failed to start development server${NC}"
        exit 1
    }

    # Setup VS Code workspace
    setup_vscode_workspace

    # Setup extensions
    setup_vscode_extensions

    # Open VS Code with preview
    open_vscode_with_preview

    # Start development CLI
    start_dev_cli
}

# Execute main function
main "$@"
