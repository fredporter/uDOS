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
