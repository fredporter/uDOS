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
