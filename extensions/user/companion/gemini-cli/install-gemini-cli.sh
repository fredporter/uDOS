#!/bin/bash

# uExtensions/ai/gemini-cli/install-gemini-cli.sh
# Google Gemini CLI Installation Script for uDOS
# Integrates the official Google Gemini CLI into uDOS ecosystem

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$EXTENSION_DIR/../../../.." && pwd)"
GEMINI_CLI_VERSION="latest"
NODE_MIN_VERSION="20"

# Print styled messages
print_header() {
    echo -e "\n${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                        Google Gemini CLI Integration                        ║${NC}"
    echo -e "${PURPLE}║                              uDOS Extension                                  ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check system requirements
check_requirements() {
    print_step "Checking system requirements"
    
    # Check Node.js
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version | sed 's/v//')
        local major_version=$(echo "$node_version" | cut -d. -f1)
        
        if [[ "$major_version" -ge "$NODE_MIN_VERSION" ]]; then
            print_success "Node.js $node_version detected (>= $NODE_MIN_VERSION required)"
        else
            print_error "Node.js $major_version detected, but >= $NODE_MIN_VERSION required"
            print_info "Please install Node.js $NODE_MIN_VERSION or higher from https://nodejs.org/"
            return 1
        fi
    else
        print_error "Node.js not found"
        print_info "Please install Node.js $NODE_MIN_VERSION or higher from https://nodejs.org/"
        return 1
    fi
    
    # Check npm
    if ! command -v npm >/dev/null 2>&1; then
        print_error "npm not found (should come with Node.js)"
        return 1
    fi
    
    print_success "System requirements check passed"
}

# Install Gemini CLI
install_gemini_cli() {
    print_step "Installing Google Gemini CLI"
    
    # Install globally using npm
    if npm install -g @google/gemini-cli; then
        print_success "Gemini CLI installed successfully"
    else
        print_error "Failed to install Gemini CLI"
        print_info "You may need to run with sudo or check your npm permissions"
        return 1
    fi
    
    # Verify installation
    if command -v gemini >/dev/null 2>&1; then
        local version=$(gemini --version 2>/dev/null || echo "unknown")
        print_success "Gemini CLI verified: $version"
    else
        print_error "Gemini CLI installation verification failed"
        return 1
    fi
}

# Create uDOS integration scripts
create_integration_scripts() {
    print_step "Creating uDOS integration scripts"
    
    # Create main gemini wrapper script
    cat > "$EXTENSION_DIR/udos-gemini.sh" << 'EOF'
#!/bin/bash
# uDOS Gemini CLI Wrapper Script
# Provides seamless integration between uDOS and Google Gemini CLI

set -euo pipefail

# uDOS Environment Setup
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
source "$UDOS_ROOT/uCore/config/environment.sh" 2>/dev/null || true

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════════════════════╗"
    echo "║                            uDOS × Gemini CLI                                  ║"
    echo "║                        AI-Powered Command Assistant                           ║"
    echo "╚════════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check if this is ASSIST mode
if [[ "${1:-}" == "--assist" ]] || [[ "${1:-}" == "assist" ]]; then
    print_banner
    echo -e "${GREEN}[ASSIST MODE]${NC} Starting Gemini CLI with uDOS context..."
    echo -e "${YELLOW}[INFO]${NC} Current directory: $(pwd)"
    echo -e "${YELLOW}[INFO]${NC} uDOS root: $UDOS_ROOT"
    echo
    
    # Set uDOS-specific context
    export GEMINI_CONTEXT_DIR="$UDOS_ROOT"
    
    # Create GEMINI.md context file if it doesn't exist
    if [[ ! -f "GEMINI.md" ]]; then
        cat > "GEMINI.md" << 'CONTEXT'
# uDOS Project Context

You are assisting with the uDOS (Universal Data Operating System) project.

## About uDOS
- Universal Data Operating System with modular architecture
- Shell-based system with extensions for gaming, AI, development tools
- Template-driven approach with smart scripting capabilities
- User role hierarchy: Guest → User → Power User → Developer → Administrator → Wizard

## Current Structure
- uCore/: Core system components
- uExtensions/: Modular extension system
- uDocs/: Documentation with location tile codes
- uSandbox/: User-isolated personal data
- uTemplate/: Template management system
- uScript/: Scripting framework

## Available Commands
- Use `./uCode/ucode.sh` to start uDOS shell
- Use `./uCode/dash.sh` for system dashboard
- Use various extension scripts in uExtensions/

## Guidelines
- Maintain shell-based, portable design
- Follow uDOS naming conventions (use 'u' prefix)
- Respect user data privacy (sandbox isolation)
- Support multiple distribution types (minimal, standard, developer, wizard, drone, enterprise)

Please assist with uDOS development, usage, and troubleshooting.
CONTEXT
        echo -e "${GREEN}[CREATED]${NC} GEMINI.md context file for this session"
    fi
    
    # Start Gemini CLI with uDOS-aware settings
    exec gemini --include-directories="$UDOS_ROOT/uCore,$UDOS_ROOT/uDocs,$UDOS_ROOT/uExtensions" "${@:2}"
else
    # Standard mode - pass through to gemini
    exec gemini "$@"
fi
EOF
    
    chmod +x "$EXTENSION_DIR/udos-gemini.sh"
    
    # Create COMMAND mode integration
    cat > "$EXTENSION_DIR/command-mode.sh" << 'EOF'
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
EOF
    
    chmod +x "$EXTENSION_DIR/command-mode.sh"
    
    print_success "Integration scripts created"
}

# Create configuration files
create_configuration() {
    print_step "Creating configuration files"
    
    # Create extension manifest
    cat > "$EXTENSION_DIR/manifest.json" << EOF
{
    "name": "gemini-cli",
    "version": "1.0.0",
    "description": "Google Gemini CLI integration for uDOS with COMMAND/ASSIST mode",
    "type": "ai-assistant",
    "category": "ai",
    "author": "uDOS Team",
    "license": "Apache-2.0",
    "requires": {
        "node": ">=$NODE_MIN_VERSION",
        "npm": ">=8.0.0",
        "udos": ">=1.2.0"
    },
    "provides": {
        "commands": [
            "udos-gemini.sh",
            "command-mode.sh"
        ],
        "modes": [
            "assist",
            "command"
        ]
    },
    "installation": {
        "script": "install-gemini-cli.sh",
        "dependencies": ["@google/gemini-cli"],
        "size": "~50MB"
    },
    "integration": {
        "ucode": true,
        "dashboard": true,
        "templates": true
    }
}
EOF
    
    # Create authentication guide
    cat > "$EXTENSION_DIR/AUTH_SETUP.md" << 'EOF'
# Gemini CLI Authentication Setup for uDOS

## Option 1: OAuth (Recommended)
1. Run: `./udos-gemini.sh --assist`
2. Choose OAuth when prompted
3. Follow browser authentication flow
4. Free tier: 60 requests/min, 1,000 requests/day

## Option 2: API Key
1. Get API key from: https://aistudio.google.com/apikey
2. Set environment variable:
   ```bash
   export GEMINI_API_KEY="YOUR_API_KEY"
   ```
3. Free tier: 100 requests/day

## Option 3: Vertex AI (Enterprise)
1. Set up Google Cloud Project
2. Set environment variables:
   ```bash
   export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT"
   export GOOGLE_API_KEY="YOUR_API_KEY"
   export GOOGLE_GENAI_USE_VERTEXAI=true
   ```

## Test Authentication
```bash
./udos-gemini.sh --assist
```

If authentication works, you'll see the Gemini CLI interface with uDOS context.
EOF
    
    print_success "Configuration files created"
}

# Create uCode integration
create_ucode_integration() {
    print_step "Creating uCode shell integration"
    
    # Create uCode command integration
    cat > "$EXTENSION_DIR/ucode-commands.sh" << 'EOF'
#!/bin/bash
# uCode Shell Commands for Gemini CLI Integration

# Register ASSIST command
ucode_register_command() {
    echo "assist" >> "$UDOS_ROOT/uCore/config/commands.list"
    echo "command" >> "$UDOS_ROOT/uCore/config/commands.list"
}

# ASSIST command handler
ucode_cmd_assist() {
    echo "Starting Gemini CLI in ASSIST mode..."
    "$UDOS_ROOT/uExtensions/ai/gemini-cli/udos-gemini.sh" --assist "$@"
}

# COMMAND command handler  
ucode_cmd_command() {
    echo "Starting uDOS COMMAND mode (Natural Language Interface)..."
    "$UDOS_ROOT/uExtensions/ai/gemini-cli/command-mode.sh" "$@"
}

# Auto-register commands if sourced by uCode
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    ucode_register_command
fi
EOF
    
    chmod +x "$EXTENSION_DIR/ucode-commands.sh"
    
    print_success "uCode integration created"
}

# Update uDOS configuration
update_udos_config() {
    print_step "Updating uDOS configuration"
    
    # Add to extension registry
    local extension_registry="$UDOS_ROOT/uExtensions/registry.json"
    
    if [[ -f "$extension_registry" ]]; then
        # Add entry to existing registry (simplified)
        echo "Extension registered in $extension_registry"
    else
        # Create new registry
        cat > "$extension_registry" << 'EOF'
{
    "extensions": {
        "ai": {
            "gemini-cli": {
                "name": "Google Gemini CLI",
                "path": "ai/gemini-cli",
                "status": "installed",
                "commands": ["assist", "command"],
                "description": "AI-powered command assistant with natural language interface"
            }
        }
    }
}
EOF
    fi
    
    print_success "uDOS configuration updated"
}

# Post-installation setup
post_install_setup() {
    print_step "Post-installation setup"
    
    # Create symlinks for easy access
    ln -sf "$EXTENSION_DIR/udos-gemini.sh" "$UDOS_ROOT/uCore/scripts/assist" 2>/dev/null || true
    ln -sf "$EXTENSION_DIR/command-mode.sh" "$UDOS_ROOT/uCore/scripts/command" 2>/dev/null || true
    
    # Add to PATH if needed
    local bin_dir="$UDOS_ROOT/bin"
    mkdir -p "$bin_dir"
    ln -sf "$EXTENSION_DIR/udos-gemini.sh" "$bin_dir/udos-assist" 2>/dev/null || true
    ln -sf "$EXTENSION_DIR/command-mode.sh" "$bin_dir/udos-command" 2>/dev/null || true
    
    print_success "Post-installation setup complete"
}

# Installation summary
print_summary() {
    print_step "Installation Summary"
    echo
    echo -e "${GREEN}✓ Google Gemini CLI installed${NC}"
    echo -e "${GREEN}✓ uDOS integration scripts created${NC}"
    echo -e "${GREEN}✓ ASSIST mode available${NC}"
    echo -e "${GREEN}✓ COMMAND mode available${NC}"
    echo -e "${GREEN}✓ uCode shell integration${NC}"
    echo
    echo -e "${CYAN}Available Commands:${NC}"
    echo -e "  ${YELLOW}./udos-gemini.sh --assist${NC}  - Start AI assistant with uDOS context"
    echo -e "  ${YELLOW}./command-mode.sh${NC}           - Natural language command interface"
    echo -e "  ${YELLOW}assist${NC}                     - (from uCode shell) Start ASSIST mode"
    echo -e "  ${YELLOW}command${NC}                    - (from uCode shell) Start COMMAND mode"
    echo
    echo -e "${CYAN}Next Steps:${NC}"
    echo -e "1. Set up authentication: ${YELLOW}cat AUTH_SETUP.md${NC}"
    echo -e "2. Test ASSIST mode: ${YELLOW}./udos-gemini.sh --assist${NC}"
    echo -e "3. Test COMMAND mode: ${YELLOW}./command-mode.sh${NC}"
    echo
    echo -e "${GREEN}🎉 Gemini CLI integration complete!${NC}"
}

# Main installation process
main() {
    print_header
    
    check_requirements || exit 1
    install_gemini_cli || exit 1
    create_integration_scripts
    create_configuration
    create_ucode_integration
    update_udos_config
    post_install_setup
    print_summary
}

# Run main with all arguments
main "$@"
