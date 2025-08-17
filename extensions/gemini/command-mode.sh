#!/bin/bash
# uDOS COMMAND Mode - Interactive AI Assistant
# Provides natural language command interface using Gemini CLI

set -euo pipefail

EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$EXTENSION_DIR/../../../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    clear
    echo -e "${PURPLE}"
    cat << 'BANNER'
╔══════════════════════════════════════════════════════════════════════════════╗
║                              uDOS COMMAND MODE                              ║
║                           AI-Powered Natural Language                       ║
║                              Command Interface                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
    echo -e "${CYAN}[INFO]${NC} Type natural language commands to interact with uDOS"
    echo -e "${CYAN}[INFO]${NC} Examples: 'start the dashboard', 'create a new template', 'check system status'"
    echo -e "${CYAN}[INFO]${NC} Type 'exit' or 'quit' to return to normal shell"
    echo -e "${CYAN}[INFO]${NC} Type 'help' for available commands"
    echo
}

# Command interpreter using Gemini CLI
interpret_command() {
    local user_input="$1"
    
    # Special cases
    case "$user_input" in
        "exit"|"quit"|"q")
            echo -e "${GREEN}[COMMAND]${NC} Exiting COMMAND mode..."
            exit 0
            ;;
        "help")
            show_help
            return
            ;;
        "status"|"check status"|"system status")
            echo -e "${GREEN}[COMMAND]${NC} Checking uDOS system status..."
            "$UDOS_ROOT/uCode/validate-installation.sh" quick
            return
            ;;
        "dashboard"|"start dashboard"|"show dashboard")
            echo -e "${GREEN}[COMMAND]${NC} Starting uDOS dashboard..."
            "$UDOS_ROOT/uCode/dash.sh"
            return
            ;;
        "shell"|"start shell"|"ucode")
            echo -e "${GREEN}[COMMAND]${NC} Starting uDOS shell..."
            "$UDOS_ROOT/uCode/ucode.sh"
            return
            ;;
    esac
    
    # Use Gemini CLI to interpret the command
    echo -e "${BLUE}[AI]${NC} Interpreting: '$user_input'"
    
    # Create a temporary prompt for command interpretation
    local prompt="You are a uDOS command interpreter. The user said: '$user_input'

Based on this input, suggest the most appropriate uDOS command(s) to run. Available options include:

System Commands:
- ./uCode/ucode.sh - Start uDOS interactive shell
- ./uCode/dash.sh - Start system dashboard  
- ./uCode/validate-installation.sh - Check system status
- ./uCode/setup.sh - System setup

Extension Commands:
- List files in uExtensions/ for available extensions
- Gaming: ./uExtensions/gaming/*/
- AI tools: ./uExtensions/ai/*/
- Editors: ./uExtensions/editors/*/

Template Commands:
- ./uTemplate/ - Template management
- ./uScript/ - Script management

Please respond with:
1. The exact command to run (if applicable)
2. A brief explanation of what it does
3. Any relevant parameters or options

Keep responses concise and actionable. If the request is unclear, ask for clarification."

    # Execute Gemini CLI with the prompt
    if command -v gemini >/dev/null 2>&1; then
        echo "$prompt" | gemini -p -
    else
        echo -e "${RED}[ERROR]${NC} Gemini CLI not available. Please run the installation first."
        echo -e "${YELLOW}[INFO]${NC} Use: $EXTENSION_DIR/install-gemini-cli.sh"
    fi
}

show_help() {
    echo -e "${YELLOW}[HELP]${NC} uDOS COMMAND Mode - Natural Language Interface"
    echo
    echo "Available command patterns:"
    echo "  • 'start the dashboard' or 'dashboard' - Launch system dashboard"
    echo "  • 'check status' or 'status' - Validate system installation"
    echo "  • 'start shell' or 'shell' - Launch interactive uDOS shell"
    echo "  • 'help' - Show this help"
    echo "  • 'exit' or 'quit' - Return to normal shell"
    echo
    echo "Natural language examples:"
    echo "  • 'show me the available games'"
    echo "  • 'create a new template for documentation'"
    echo "  • 'list all AI extensions'"
    echo "  • 'how do I start the micro editor?'"
    echo "  • 'what logging options are available?'"
    echo
    echo -e "${CYAN}[TIP]${NC} Speak naturally - the AI will interpret your intent!"
}

# Main interactive loop
main() {
    print_header
    
    while true; do
        echo -n -e "${GREEN}uDOS-AI${NC} > "
        read -r user_input
        
        if [[ -n "$user_input" ]]; then
            interpret_command "$user_input"
            echo
        fi
    done
}

main "$@"
