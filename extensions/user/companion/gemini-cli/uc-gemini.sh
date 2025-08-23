#!/bin/bash
# uDOS UC Gemini CLI Integration

UC_DIR="${HOME}/uDOS/uCompanion"
GEMINI_DIR="${UC_DIR}/gemini"
CONFIGS_DIR="${GEMINI_DIR}/configs"
SESSIONS_DIR="${GEMINI_DIR}/sessions"

# Check if Gemini CLI is available
check_gemini() {
    if ! command -v gemini >/dev/null 2>&1; then
        echo "❌ Gemini CLI not found. Please install first:"
        echo "   ./uCode/packages/install-gemini.sh"
        return 1
    fi
    return 0
}

# Start Chester session
start_chester() {
    if ! check_gemini; then return 1; fi
    
    local session_id="chester-$(date +%Y%m%d-%H%M%S)"
    local config_file="${CONFIGS_DIR}/chester.json"
    
    echo "🧙‍♂️ Starting Chester - Wizard's Assistant..."
    echo "Session: $session_id"
    echo
    
    # Load uDOS context
    local context=""
    if [[ -f "${HOME}/uDOS/uKnowledge/ARCHITECTURE.md" ]]; then
        context="uDOS Architecture Context:\n$(head -50 "${HOME}/uDOS/uKnowledge/ARCHITECTURE.md")\n\n"
    fi
    
    # Start Gemini with Chester context
    echo -e "${context}Hello! I'm Chester, your Wizard's Assistant for uDOS development. How can I help you today?" | \
    gemini -model gemini-pro \
           -system "$(jq -r '.system_prompt' "$config_file" 2>/dev/null || echo 'You are Chester, the Wizard Assistant for uDOS.')" \
           -session "$session_id"
}

# Start Sorcerer's Assistant session
start_sorcerer() {
    if ! check_gemini; then return 1; fi
    
    local session_id="sorcerer-$(date +%Y%m%d-%H%M%S)"
    local config_file="${CONFIGS_DIR}/sorcerer.json"
    
    echo "🔮 Starting Sorcerer's Assistant..."
    echo "Session: $session_id"
    echo
    
    # Load uDOS context for Sorcerer
    local context=""
    if [[ -d "${HOME}/uDOS/uTemplate" ]]; then
        context="uDOS Template System Overview:\n$(find "${HOME}/uDOS/uTemplate" -name "*.md" -exec head -10 {} \; | head -30)\n\n"
    fi
    
    # Start Gemini with Sorcerer context
    echo -e "${context}Greetings! I'm your Sorcerer's Assistant, ready to help with advanced uDOS magic and creative solutions. What mystical challenge shall we tackle?" | \
    gemini -model gemini-pro \
           -system "$(jq -r '.system_prompt' "$config_file" 2>/dev/null || echo 'You are the Sorcerer Assistant for advanced uDOS operations.')" \
           -session "$session_id"
}

# Show available assistants
list_assistants() {
    echo "🤝 Available uDOS User Companions:"
    echo
    echo "🧙‍♂️  Chester - Wizard's Assistant (AI-Connected)"
    echo "   Specialization: Development, Architecture, Debugging"
    echo "   Command: $0 chester"
    echo
    echo "🔮 Sorcerer's Assistant (AI-Connected)"
    echo "   Specialization: Advanced Systems, Creative Solutions"
    echo "   Command: $0 sorcerer"
    echo
    echo "👹 Imp Companion (Offline Assistant)"
    echo "   Specialization: Quick Tasks, System Maintenance"
    echo "   Command: $0 imp"
    echo
    echo "🤖 Drone Companion (Offline Assistant)"
    echo "   Specialization: Automation, Monitoring"
    echo "   Command: $0 drone"
    echo
    echo "👻 Ghost Companion (Offline Assistant)"
    echo "   Specialization: Stealth Operations, Background Tasks"
    echo "   Command: $0 ghost"
}

# Main execution
case "${1:-list}" in
    "chester")
        start_chester
        ;;
    "sorcerer")
        start_sorcerer
        ;;
    "imp")
        echo "👹 Starting Imp Companion (offline assistant)..."
        "${UC_DIR}/reasoning/imp/imp-engine.sh" "${@:2}"
        ;;
    "drone")
        echo "🤖 Starting Drone Companion (offline assistant)..."
        "${UC_DIR}/reasoning/drone/drone-engine.sh" "${@:2}"
        ;;
    "ghost")
        echo "👻 Starting Ghost Companion (offline assistant)..."
        "${UC_DIR}/reasoning/ghost/ghost-engine.sh" "${@:2}"
        ;;
    "list"|"help"|*)
        list_assistants
        ;;
esac
