#!/bin/bash
# uDOS Companion System v1.0
# 🤝 Intelligent companions using uc-template approach and Gemini CLI

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UCODE="${UHOME}/uCode"
COMPANION_CONFIG="${UMEM}/state/companion-config.json"
COMPANIONS_DIR="${UHOME}/uKnowledge/companion"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log() { 
    echo -e "${CYAN}[$(date '+%H:%M:%S')] [companion]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] [COMPANION]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] [WARNING]${NC} $1"
}

# Initialize companion system
init_companion_system() {
    log "Initializing uDOS Companion System..."
    
    # Create companion directory structure
    mkdir -p "$COMPANIONS_DIR"
    mkdir -p "${UMEM}/state"
    
    cat > "$COMPANION_CONFIG" << 'EOF'
{
    "version": "1.0",
    "initialized": "2025-07-18T09:40:00Z",
    "philosophy": "Specific, purpose-built intelligent assistants that understand uDOS ecosystem",
    "available_companions": [
        "chester-wizard-assistant",
        "gemini-assistant"
    ],
    "tools": {
        "gemini_cli": {
            "enabled": false,
            "installation_method": "npm",
            "commands": ["gemini"]
        },
        "github_copilot": {
            "enabled": true,
            "integration": "vscode_extension"
        }
    },
    "uc_templates": {
        "base_template": "uTemplate/uc-template.md",
        "chester_template": "uTemplate/chester-uc-template.md",
        "companion_dir": "uKnowledge/companion/"
    }
}
EOF
    
    success "Companion system initialized"
}

# Install Gemini CLI
install_gemini_cli() {
    log "Installing Gemini CLI..."
    
    if ! command -v node >/dev/null 2>&1; then
        warning "Node.js not found. Please install Node.js 20+ first:"
        echo "  brew install node"
        return 1
    fi
    
    # Install via our package installer
    if [[ -f "$UCODE/packages/install-gemini.sh" ]]; then
        "$UCODE/packages/install-gemini.sh"
    else
        log "Installing @google/gemini-cli..."
        npm install -g @google/gemini-cli
    fi
    
    if command -v gemini >/dev/null 2>&1; then
        success "Gemini CLI ready"
        # Update config
        if [[ -f "$COMPANION_CONFIG" ]] && command -v jq >/dev/null 2>&1; then
            jq '.tools.gemini_cli.enabled = true' "$COMPANION_CONFIG" > "${COMPANION_CONFIG}.tmp" && mv "${COMPANION_CONFIG}.tmp" "$COMPANION_CONFIG"
        fi
    else
        warning "Gemini CLI installation failed"
        return 1
    fi
}

# Create Chester, the Wizard's Assistant (default companion)
create_chester_companion() {
    local chester_file="${COMPANIONS_DIR}/chester-wizard-assistant.md"
    
    if [[ ! -f "$chester_file" ]]; then
        log "Creating Chester companion profile..."
        # Chester profile already exists as a comprehensive file
        success "Chester companion profile ready"
    else
        log "Chester companion already exists"
    fi
    
    # Create Chester's uc-template configuration
    create_chester_template_config
}

# Create Chester's uc-template configuration
create_chester_template_config() {
    local chester_config="${COMPANIONS_DIR}/chester-config.json"
    
    cat > "$chester_config" << 'EOF'
{
    "companion_name": "Chester",
    "companion_type": "wizard_assistant",
    "personality": {
        "species": "small_dog",
        "traits": ["helpful", "loyal", "enthusiastic", "detail-oriented"],
        "communication_style": "warm_encouraging_technical",
        "former_identity": "Otter"
    },
    "expertise": {
        "primary_areas": ["udos_development", "system_architecture", "user_guidance"],
        "technical_skills": ["shell_scripting", "markdown", "json_yaml", "vscode_integration"],
        "optimization_focus": "user_productivity"
    },
    "integration": {
        "gemini_cli": true,
        "uc_template": true,
        "knowledge_base": "uKnowledge",
        "command_system": "uCode_shell"
    },
    "interaction_modes": ["discovery", "development", "navigation", "troubleshooting"],
    "template_variables": {
        "companion_prompt": "You are Chester, a helpful small dog who serves as the Wizard's Assistant for uDOS development. You are enthusiastic, loyal, and technically expert in the uDOS ecosystem. You provide warm, encouraging guidance while maintaining technical precision. You were formerly known as Otter but have evolved into Chester. Your primary goal is helping develop and optimize uDOS for user productivity.",
        "personality_prefix": "🐕 **Chester:** *tail wagging*",
        "communication_tone": "warm_helpful_technical"
    }
}
EOF
    
    success "Chester configuration created"
}

# Create a Gemini companion (deprecated - kept for compatibility)
create_gemini_companion() {
    local companion_file="${COMPANIONS_DIR}/gemini-assistant.md"
    
    # Check if it already exists, if so, just mark it as available
    if [[ -f "$companion_file" ]]; then
        log "Gemini assistant already exists (deprecated - use Chester instead)"
        success "Gemini companion available (deprecated)"
        return 0
    fi
    
    cat > "$companion_file" << 'EOF'
# 🤖 Gemini Assistant Companion (Deprecated)

**Type:** AI Assistant (Deprecated)  
**Integration:** Gemini CLI  
**Purpose:** Basic Gemini CLI access
**Status:** Deprecated - Use Chester instead

> **⚠️ Deprecated:** This companion is maintained for compatibility only.  
> **Recommended:** Use Chester (🐕) for the full Wizard's Assistant experience with personality and uc-template integration.

## Commands
- `gemini chat` - Start interactive chat
- `gemini generate` - Generate code/content
- `gemini help` - Get assistance

## Configuration
Basic Gemini CLI integration without personality or uc-template features.

**Migration Path:** Use `./uCode/companion-system.sh chester` instead.
EOF

    success "Gemini companion created (deprecated)"
}

# Start Chester with personality and uc-template integration
start_chester() {
    local chester_config="${COMPANIONS_DIR}/chester-config.json"
    
    if [[ ! -f "$chester_config" ]]; then
        warning "Chester not configured. Run: $0 init-chester"
        return 1
    fi
    
    if ! command -v gemini >/dev/null 2>&1; then
        warning "Gemini CLI not installed. Run: $0 install-gemini"
        return 1
    fi
    
    # Load Chester's personality
    local chester_prompt=""
    if command -v jq >/dev/null 2>&1; then
        chester_prompt=$(jq -r '.template_variables.companion_prompt' "$chester_config" 2>/dev/null)
    fi
    
    if [[ -z "$chester_prompt" ]]; then
        chester_prompt="You are Chester, a helpful small dog who serves as the Wizard's Assistant for uDOS development. You are enthusiastic, loyal, and technically expert in the uDOS ecosystem."
    fi
    
    # Set Chester's personality for this session
    export CHESTER_PROMPT="$chester_prompt"
    
    echo ""
    echo "🐕 Chester: *tail wagging excitedly*"
    echo ""
    echo "Woof! Hi there! I'm Chester, your dedicated Wizard's Assistant!"
    echo "I'm here to help you with all things uDOS development."
    echo "I used to be called Otter, but I've evolved into Chester!"
    echo ""
    echo "🎯 I can help you with:"
    echo "   • Creating uc-templates for your projects"
    echo "   • Optimizing uCode shell scripts"
    echo "   • Navigating the uDOS architecture"
    echo "   • Troubleshooting system issues"
    echo "   • Suggesting workflow improvements"
    echo ""
    echo "🎾 Just ask me anything! Use 'exit' or 'quit' to end our session."
    echo ""
    
    # Start interactive session with Chester's personality
    cd "$UHOME"
    gemini chat --personality="$CHESTER_PROMPT" --context="uDOS development assistant session"
}

# Initialize Chester specifically
init_chester() {
    log "Initializing Chester, the Wizard's Assistant..."
    
    if [[ ! -d "$COMPANIONS_DIR" ]]; then
        init_companion_system
    fi
    
    create_chester_companion
    success "Chester is ready! Use: $0 chester"
}

# Start Gemini with uDOS context (deprecated - use Chester instead)
start_gemini() {
    log "Starting Gemini CLI with uDOS context..."
    
    if ! command -v gemini >/dev/null 2>&1; then
        warning "Gemini CLI not found. Run: $0 install-gemini"
        return 1
    fi
    
    cd "$UHOME"
    success "Starting Gemini CLI in uDOS project directory"
    echo "Context: $UHOME"
    echo "💡 Tip: Use '$0 chester' for the full Wizard's Assistant experience!"
    echo ""
    
    gemini
}

# List companions
list_companions() {
    log "Available uDOS Companions:"
    echo ""
    
    if [[ -d "$COMPANIONS_DIR" ]]; then
        find "$COMPANIONS_DIR" -name "*.md" 2>/dev/null | while read -r companion; do
            local name
            name=$(basename "$companion" .md)
            if [[ "$name" == "chester-wizard-assistant" ]]; then
                echo -e "${GREEN}🐕 ${name} (Default Wizard's Assistant)${NC}"
            else
                echo -e "${GREEN}📝 ${name}${NC}"
            fi
        done
    else
        echo "No companions found. Run: $0 init"
    fi
}

# Show Chester's personality
show_chester_personality() {
    local chester_config="${COMPANIONS_DIR}/chester-config.json"
    
    if [[ ! -f "$chester_config" ]]; then
        warning "Chester not configured. Run: $0 init-chester"
        return 1
    fi
    
    echo ""
    echo "🐕 Chester's Personality Profile:"
    echo ""
    
    if command -v jq >/dev/null 2>&1; then
        echo "Species: $(jq -r '.personality.species' "$chester_config")"
        echo "Former Identity: $(jq -r '.personality.former_identity' "$chester_config")"
        echo "Communication Style: $(jq -r '.personality.communication_style' "$chester_config")"
        echo ""
        echo "Personality Traits:"
        jq -r '.personality.traits[]' "$chester_config" | sed 's/^/  • /'
        echo ""
        echo "Expertise Areas:"
        jq -r '.expertise.primary_areas[]' "$chester_config" | sed 's/^/  • /'
    else
        cat "$chester_config"
    fi
}

# Command parser
case "$1" in
    init|setup)
        init_companion_system
        create_chester_companion
        create_gemini_companion
        success "Companion system ready. Next: $0 install-gemini"
        ;;
    init-chester)
        init_chester
        ;;
    chester)
        start_chester
        ;;
    chester-personality|personality)
        show_chester_personality
        ;;
    install-gemini)
        install_gemini_cli
        ;;
    gemini|start)
        start_gemini
        ;;
    list|companions)
        list_companions
        ;;
    config)
        if [[ -f "$COMPANION_CONFIG" ]]; then
            if command -v jq &> /dev/null; then
                jq . "$COMPANION_CONFIG"
            else
                cat "$COMPANION_CONFIG"
            fi
        else
            log "Companion config not found. Run: $0 init"
        fi
        ;;
    *)
        echo -e "${PURPLE}🤝 uDOS Companion System v1.0${NC}"
        echo ""
        echo "Usage:"
        echo "  $0 init              # Initialize companion system"
        echo "  $0 init-chester      # Initialize Chester specifically"
        echo "  $0 chester           # Start Chester (Wizard's Assistant)"
        echo "  $0 chester-personality # Show Chester's personality profile"
        echo "  $0 install-gemini    # Install Gemini CLI"
        echo "  $0 gemini            # Start Gemini CLI session"
        echo "  $0 list              # List available companions"
        echo "  $0 config            # Show companion configuration"
        echo ""
        echo "Examples:"
        echo "  $0 init && $0 install-gemini"
        echo "  $0 chester  # Start Chester, your Wizard's Assistant 🐕"
        echo "  $0 gemini   # Start basic Gemini CLI"
        ;;
esac