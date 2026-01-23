#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║                    uDOS Wizard Configuration Setup                        ║
# ║         Automate API key configuration where possible                     ║
# ╚═══════════════════════════════════════════════════════════════════════════╝

set -e

# Navigate to root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."
UDOS_ROOT="$(pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m'
BOLD='\033[1m'

# Config paths
CONFIG_DIR="$UDOS_ROOT/wizard/config"
ASSISTANT_KEYS="$CONFIG_DIR/assistant_keys.json"
GITHUB_KEYS="$CONFIG_DIR/github_keys.json"
NOTION_KEYS="$CONFIG_DIR/notion_keys.json"

# Flags
INTERACTIVE=1
AUTO_MODE=0
SKIP_BROWSER=0

# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════

print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║         uDOS Wizard Configuration Setup                               ║${NC}"
    echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${DIM}ℹ${NC} $1"
}

# ═══════════════════════════════════════════════════════════════════════════
# Setup Functions
# ═══════════════════════════════════════════════════════════════════════════

setup_github() {
    print_section "GitHub Integration"

    # Check for GitHub CLI
    if ! command -v gh &> /dev/null; then
        print_warning "GitHub CLI not installed"
        print_info "Install: ${CYAN}brew install gh${NC} (macOS) or ${CYAN}apt install gh${NC} (Linux)"
        return 1
    fi

    print_success "GitHub CLI found"

    # Check authentication
    if ! gh auth status &> /dev/null; then
        print_warning "Not authenticated with GitHub"

        if [ $INTERACTIVE -eq 1 ]; then
            read -p "Authenticate now? (y/N) " AUTH_NOW
            if [ "$AUTH_NOW" = "y" ] || [ "$AUTH_NOW" = "Y" ]; then
                gh auth login --web
            else
                print_info "Run later: ${CYAN}gh auth login${NC}"
                return 1
            fi
        else
            print_info "Run: ${CYAN}gh auth login${NC}"
            return 1
        fi
    fi

    print_success "GitHub authenticated"

    # Get token and save
    TOKEN=$(gh auth token 2>/dev/null || echo "")
    if [ -n "$TOKEN" ]; then
        # Create or update config
        cat > "$GITHUB_KEYS" <<EOF
{
  "github_token": "$TOKEN",
  "github_webhook_secret": null,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
        chmod 600 "$GITHUB_KEYS"
        print_success "GitHub token saved to $(basename $GITHUB_KEYS)"
    else
        print_error "Could not retrieve GitHub token"
        return 1
    fi
}

setup_ollama() {
    print_section "Ollama (Local AI)"

    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_success "Ollama is running on port 11434"

        # Update or create assistant_keys.json with Ollama config
        if [ -f "$ASSISTANT_KEYS" ]; then
            # Update existing file
            TMP_FILE=$(mktemp)
            jq '. + {"OLLAMA_HOST": "http://localhost:11434"}' "$ASSISTANT_KEYS" > "$TMP_FILE"
            mv "$TMP_FILE" "$ASSISTANT_KEYS"
        else
            # Create new file from template
            if [ -f "$CONFIG_DIR/assistant_keys.template.json" ]; then
                cp "$CONFIG_DIR/assistant_keys.template.json" "$ASSISTANT_KEYS"
                TMP_FILE=$(mktemp)
                jq '. + {"OLLAMA_HOST": "http://localhost:11434"}' "$ASSISTANT_KEYS" > "$TMP_FILE"
                mv "$TMP_FILE" "$ASSISTANT_KEYS"
            else
                cat > "$ASSISTANT_KEYS" <<EOF
{
  "_comment": "API keys for uDOS Wizard Server - NEVER commit with real keys!",
  "OLLAMA_HOST": "http://localhost:11434",
  "GEMINI_API_KEY": "",
  "OPENAI_API_KEY": "",
  "ANTHROPIC_API_KEY": ""
}
EOF
            fi
        fi
        chmod 600 "$ASSISTANT_KEYS"
        print_success "Ollama configured in $(basename $ASSISTANT_KEYS)"
    else
        print_warning "Ollama not running"
        print_info "Start Ollama: ${CYAN}ollama serve${NC}"
        print_info "Or install: ${CYAN}brew install ollama${NC} (macOS)"
    fi
}

setup_ssh_keys() {
    print_section "SSH Keys (GitHub)"

    if [ -f "$HOME/.ssh/id_ed25519_github" ]; then
        print_success "GitHub SSH key exists"

        # Test connection
        if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
            print_success "SSH connection verified"
        else
            print_warning "SSH key exists but connection test failed"
            print_info "Test manually: ${CYAN}ssh -T git@github.com${NC}"
        fi
    else
        print_warning "No GitHub SSH key found"

        if [ $INTERACTIVE -eq 1 ]; then
            read -p "Generate SSH key now? (y/N) " GEN_SSH
            if [ "$GEN_SSH" = "y" ] || [ "$GEN_SSH" = "Y" ]; then
                "$UDOS_ROOT/bin/setup_github_ssh.sh" --auto
            else
                print_info "Run later: ${CYAN}./bin/setup_github_ssh.sh${NC}"
            fi
        else
            print_info "Run: ${CYAN}./bin/setup_github_ssh.sh${NC}"
        fi
    fi
}

setup_manual_keys() {
    print_section "AI Provider Keys (Manual Setup Required)"

    echo ""
    echo "These services require web dashboard authentication:"
    echo ""
    echo "  ${CYAN}OpenAI:${NC}     https://platform.openai.com/api-keys"
    echo "  ${CYAN}OpenRouter:${NC} https://openrouter.ai/keys"
    echo "  ${CYAN}Mistral:${NC}    https://console.mistral.ai/api-keys"
    echo "  ${CYAN}Anthropic:${NC}  https://console.anthropic.com/settings/keys"
    echo ""

    if [ $INTERACTIVE -eq 1 ] && [ $SKIP_BROWSER -eq 0 ]; then
        read -p "Open these URLs in browser? (y/N) " OPEN_URLS
        if [ "$OPEN_URLS" = "y" ] || [ "$OPEN_URLS" = "Y" ]; then
            xdg-open "https://platform.openai.com/api-keys" 2>/dev/null || \
            open "https://platform.openai.com/api-keys" 2>/dev/null || true

            xdg-open "https://openrouter.ai/keys" 2>/dev/null || \
            open "https://openrouter.ai/keys" 2>/dev/null || true

            echo ""
            print_info "After generating keys, add them via dashboard:"
            echo "  ${CYAN}http://localhost:8765/#config${NC} → Assistant Keys"
        fi
    else
        print_info "Copy keys manually to: ${CYAN}$ASSISTANT_KEYS${NC}"
        print_info "Or use dashboard: ${CYAN}http://localhost:8765/#config${NC}"
    fi
}

setup_notion() {
    print_section "Notion Integration (Optional)"

    if [ $INTERACTIVE -eq 1 ]; then
        read -p "Set up Notion integration? (y/N) " SETUP_NOTION
        if [ "$SETUP_NOTION" = "y" ] || [ "$SETUP_NOTION" = "Y" ]; then
            echo ""
            print_info "Opening Notion integrations page..."
            xdg-open "https://www.notion.so/my-integrations" 2>/dev/null || \
            open "https://www.notion.so/my-integrations" 2>/dev/null || true

            echo ""
            echo "Steps:"
            echo "  1. Click 'New integration'"
            echo "  2. Name it 'uDOS Wizard'"
            echo "  3. Copy the 'Internal Integration Token'"
            echo ""
            read -p "Paste Notion token (or Enter to skip): " NOTION_TOKEN

            if [ -n "$NOTION_TOKEN" ]; then
                cat > "$NOTION_KEYS" <<EOF
{
  "notion_token": "$NOTION_TOKEN",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
                chmod 600 "$NOTION_KEYS"
                print_success "Notion configured in $(basename $NOTION_KEYS)"
            else
                print_info "Skipped Notion setup"
            fi
        fi
    else
        print_info "Notion setup requires interactive mode"
    fi
}

print_summary() {
    echo ""
    echo -e "${GREEN}${BOLD}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║                    Setup Complete!                                    ║${NC}"
    echo -e "${GREEN}${BOLD}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Configuration files:"
    [ -f "$ASSISTANT_KEYS" ] && echo "  ✓ $(basename $ASSISTANT_KEYS)"
    [ -f "$GITHUB_KEYS" ] && echo "  ✓ $(basename $GITHUB_KEYS)"
    [ -f "$NOTION_KEYS" ] && echo "  ✓ $(basename $NOTION_KEYS)"
    echo ""
    echo "Dashboard: ${CYAN}http://localhost:8765/#config${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start Wizard Server: ${CYAN}python -m wizard.server${NC}"
    echo "  2. Add remaining API keys via dashboard"
    echo "  3. Run uDOS: ${CYAN}./bin/start_udos.sh${NC}"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════════════════

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --auto)
            AUTO_MODE=1
            INTERACTIVE=0
            shift
            ;;
        --no-browser)
            SKIP_BROWSER=1
            shift
            ;;
        --help|-h)
            echo "uDOS Wizard Configuration Setup"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto          Non-interactive mode (skip prompts)"
            echo "  --no-browser    Don't open URLs in browser"
            echo "  --help          Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                    # Interactive setup"
            echo "  $0 --auto             # Automated setup (no prompts)"
            echo "  $0 --no-browser       # Don't open browser URLs"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run with --help for usage"
            exit 1
            ;;
    esac
done

# Create config directory if needed
mkdir -p "$CONFIG_DIR"

# Run setup
print_header

# Automated setups (no user input needed)
setup_ollama
setup_ssh_keys

# CLI-assisted setups
setup_github

# Manual setups
setup_manual_keys
setup_notion

# Summary
print_summary
