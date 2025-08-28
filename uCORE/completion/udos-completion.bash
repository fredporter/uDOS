#!/bin/bash
# uDOS Command Auto-completion System v1.0.4.4
# Provides intelligent tab completion for native CLI and uCODE commands
# Integration: source this file or install as bash completion

# ════════════════════════════════════════════════════════════════
# 🎯 CORE COMPLETION LOGIC
# ════════════════════════════════════════════════════════════════

# Get uDOS root directory
_udos_get_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$(cd "$script_dir/../.." && pwd)"
}

# Get current user role for context-aware completion
_udos_get_role() {
    local udos_root="$(_udos_get_root)"
    if [[ -f "$udos_root/sandbox/user.md" ]]; then
        grep "^Role:" "$udos_root/sandbox/user.md" 2>/dev/null | cut -d' ' -f2 || echo "GHOST"
    else
        echo "GHOST"
    fi
}

# Get user level for permission-based completion
_udos_get_level() {
    local udos_root="$(_udos_get_root)"
    if [[ -f "$udos_root/sandbox/user.md" ]]; then
        grep "^Level:" "$udos_root/sandbox/user.md" 2>/dev/null | cut -d' ' -f2 || echo "0"
    else
        echo "0"
    fi
}

# ════════════════════════════════════════════════════════════════
# 📋 COMMAND DEFINITIONS
# ════════════════════════════════════════════════════════════════

# Native CLI commands (no brackets)
_udos_native_commands() {
    echo "status role help list heal assist template variable get set"
}

# Template-specific completions
_udos_template_commands() {
    echo "list render status variables"
}

# Variable-specific completions
_udos_variable_commands() {
    echo "list test cache resolve set"
}

# Assist-specific completions
_udos_assist_commands() {
    echo "enter exit status next finalize roadmap"
}

# Available templates (dynamic from system)
_udos_available_templates() {
    local udos_root="$(_udos_get_root)"
    local template_dir="$udos_root/uMEMORY/system/templates"
    
    if [[ -d "$template_dir" ]]; then
        find "$template_dir" -name "*.md" -type f | \
        sed "s|$template_dir/||g" | \
        sed 's|\.md$||g' | \
        sed 's|/|-|g' | \
        sort
    fi
}

# Role-based command filtering
_udos_filter_by_role() {
    local commands="$1"
    local role="$(_udos_get_role)"
    local level="$(_udos_get_level)"
    
    # For now, return all commands - can be enhanced with role filtering
    echo "$commands"
}

# ════════════════════════════════════════════════════════════════
# 🔧 COMPLETION FUNCTIONS
# ════════════════════════════════════════════════════════════════

# Main completion function for uDOS commands
_udos_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Get base command (first argument after script name)
    local base_cmd=""
    if [[ ${#COMP_WORDS[@]} -gt 1 ]]; then
        base_cmd="${COMP_WORDS[1]}"
    fi
    
    case "${COMP_CWORD}" in
        1)
            # First argument - native commands
            opts="$(_udos_filter_by_role "$(_udos_native_commands)")"
            COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
            ;;
        2)
            # Second argument - depends on first command
            case "${base_cmd}" in
                "template")
                    opts="$(_udos_template_commands)"
                    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
                    ;;
                "variable")
                    opts="$(_udos_variable_commands)"
                    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
                    ;;
                "assist")
                    opts="$(_udos_assist_commands)"
                    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
                    ;;
                "get"|"set")
                    # Variable names - could be enhanced with actual variable list
                    opts="USER-ROLE USER-LEVEL PROJECT-NAME WORKSPACE-PATH TIMESTAMP SYSTEM-STATUS"
                    COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
                    ;;
                *)
                    # No additional completions for other commands
                    COMPREPLY=()
                    ;;
            esac
            ;;
        3)
            # Third argument - template names for 'template render'
            if [[ "${base_cmd}" == "template" && "${prev}" == "render" ]]; then
                opts="$(_udos_available_templates)"
                COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
            fi
            ;;
    esac
}

# ════════════════════════════════════════════════════════════════
# 🎨 ENHANCED COMPLETION FEATURES
# ════════════════════════════════════════════════════════════════

# Show help hints for partial completions
_udos_show_hints() {
    local partial="$1"
    local udos_root="$(_udos_get_root)"
    
    case "$partial" in
        "stat"*) echo "💡 Hint: 'status' - Show system dashboard" ;;
        "rol"*) echo "💡 Hint: 'role' - Display current role information" ;;
        "hel"*) echo "💡 Hint: 'help' - Show command reference" ;;
        "ass"*) echo "💡 Hint: 'assist' - Development assistance mode" ;;
        "tem"*) echo "💡 Hint: 'template' - Template system commands" ;;
        "hea"*) echo "💡 Hint: 'heal' - Run self-healing checks" ;;
    esac
}

# Context-aware help display
_udos_context_help() {
    local role="$(_udos_get_role)"
    local level="$(_udos_get_level)"
    
    echo "🎯 uDOS Completion Help (Role: $role, Level: $level)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Available Commands:"
    echo "  status          - System dashboard"
    echo "  role           - Current role info"
    echo "  help           - Command reference"
    echo "  list           - System variables"
    echo "  heal           - Self-healing check"
    echo "  assist [action] - Development assistance"
    echo "  template [cmd]  - Template operations"
    echo ""
    echo "💡 Press TAB for auto-completion"
    echo "💡 Type 'help' for detailed command reference"
}

# ════════════════════════════════════════════════════════════════
# 🚀 INSTALLATION AND INTEGRATION
# ════════════════════════════════════════════════════════════════

# Install completion for current session
udos_completion_install() {
    local udos_root="$(_udos_get_root)"
    local router_script="$udos_root/uCORE/code/command-router.sh"
    
    if [[ -f "$router_script" ]]; then
        # Register completion for the command router script
        complete -F _udos_completion "$router_script"
        
        # Create convenient alias
        alias udos="$router_script"
        complete -F _udos_completion udos
        
        echo "✅ uDOS auto-completion installed for current session"
        echo "💡 Use: udos <TAB> or $router_script <TAB>"
        echo "📖 Type 'udos help' for command reference"
    else
        echo "❌ uDOS command router not found at: $router_script"
    fi
}

# Test completion functionality
udos_completion_test() {
    echo "🧪 Testing uDOS Auto-completion System"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    echo "📋 Native Commands: $(_udos_native_commands)"
    echo "🎨 Template Commands: $(_udos_template_commands)"
    echo "🤖 Assist Commands: $(_udos_assist_commands)"
    echo "📝 Available Templates:"
    _udos_available_templates | head -5
    echo ""
    echo "👤 Current Role: $(_udos_get_role)"
    echo "🎯 Current Level: $(_udos_get_level)"
    echo ""
    echo "✅ Completion system ready!"
}

# ════════════════════════════════════════════════════════════════
# 🎪 INITIALIZATION
# ════════════════════════════════════════════════════════════════

# Auto-install if sourced directly
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    # Script is being sourced
    udos_completion_install
fi

# Export functions for external use
export -f _udos_completion
export -f udos_completion_install
export -f udos_completion_test
export -f _udos_context_help
