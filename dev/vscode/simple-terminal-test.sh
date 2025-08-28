#!/bin/bash
# uDOS Simple Terminal Integration Test
# Lightweight version to test terminal commands

UDOS_ROOT="${UDOS_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Simple command aliases for testing
udos() {
    "$UDOS_ROOT/uCORE/code/command-router.sh" "$@"
}

# Native CLI command functions
dash() {
    echo "🎛️ Quick Dashboard:"
    udos status
}

role() {
    echo "👤 Current Role:"
    udos role
}

assist() {
    if [[ "${1:-}" == "enter" ]]; then
        echo "🚀 Entering ASSIST mode:"
        udos assist enter
    else
        echo "🤖 ASSIST status:"
        udos assist status
    fi
}

heal() {
    echo "🛠️ Self-healing check:"
    udos heal
}

help() {
    echo "📖 uDOS Help:"
    udos help
}

list() {
    echo "📋 System List:"
    udos list
}

templates() {
    echo "📝 Available Templates:"
    udos template list
}

# Test function
test_commands() {
    echo "🧪 Testing uDOS Terminal Integration Commands:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo ""
    echo "1. Testing native CLI command:"
    udos role
    
    echo ""
    echo "2. Testing role alias:"
    role
    
    echo ""
    echo "3. Testing dashboard alias:"
    dash
    
    echo ""
    echo "4. Testing multi-word commands:"
    udos template list
    
    echo ""
    echo "5. Testing assist commands:"
    assist
    echo "3. Testing dashboard alias:"
    dash
    
    echo ""
    echo "4. Testing assist alias:"
    assist
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Terminal integration test complete!"
}

# Show available commands
show_help() {
    echo "🧙‍♂️ uDOS Terminal Commands (Simple Test Version):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  udos '[COMMAND]'  - Execute uDOS command directly"
    echo "  dash              - Show dashboard"
    echo "  role              - Show current role"
    echo "  assist [enter]    - ASSIST mode"
    echo "  heal              - Self-healing check"
    echo "  test_commands     - Run integration test"
    echo "  show_help         - Show this help"
    echo ""
}

# Auto-run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "🌀 uDOS Simple Terminal Integration"
    show_help
    test_commands
fi
