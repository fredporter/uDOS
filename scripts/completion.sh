#!/usr/bin/env bash
#
# uDOS Shell Completion
# Tab completion for udos commands
#
# Installation:
#   # Bash
#   echo "source $(pwd)/scripts/completion.sh" >> ~/.bashrc
#
#   # Zsh
#   echo "source $(pwd)/scripts/completion.sh" >> ~/.zshrc
#

# Common uDOS commands (extracted from core/data/commands.json)
_UDOS_COMMANDS=(
    # System
    "HELP" "STATUS" "REBOOT" "REPAIR" "DESTROY" "DASHBOARD" "VERSION"
    "CLEAN" "TIDY" "CONFIG" "THEME" "EXTENSION" "SERVER"

    # File operations
    "NEW" "EDIT" "VIEW" "DELETE" "COPY" "MOVE" "RENAME" "SHOW" "RUN"
    "PEEK" "POKE" "TYPO" "SAVE" "LOAD"

    # Knowledge
    "LEARN" "TEACH" "REMEMBER" "FORGET" "RECALL" "KNOW" "SEARCH"

    # Assistant
    "ASK" "ANALYZE" "EXPLAIN" "SUGGEST" "IMPROVE" "GENERATE"

    # Map/Navigation
    "GOTO" "LOCATE" "LAYER" "SCAN" "EXPLORE" "PLANET"

    # Play/Game
    "STORY" "QUEST" "SPRITE" "OBJECT" "ROLL" "INVENTORY"

    # Development
    "TEST" "DEBUG" "TRACE" "STEP" "BREAKPOINT" "INSPECT"

    # uPY/Scripting
    "PRINT" "IF" "FUNCTION" "RETURN" "JSON"
)

# Completion function for bash
_udos_bash_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"

    # If first argument (command), complete with command list
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=($(compgen -W "${_UDOS_COMMANDS[*]}" -- "$cur"))
    # If second argument and previous was certain commands, complete with files
    elif [[ ${COMP_CWORD} -eq 2 ]]; then
        case "$prev" in
            EDIT|VIEW|RUN|SHOW|DELETE|PEEK|TYPO)
                # Complete with .md and .uscript files
                COMPREPLY=($(compgen -f -X '!*.@(md|uscript|upy|json)' -- "$cur"))
                ;;
            THEME)
                # Complete with theme names (if themes directory exists)
                if [[ -d "core/data/themes" ]]; then
                    local themes=$(ls core/data/themes/*.json 2>/dev/null | xargs -n1 basename | sed 's/\.json$//')
                    COMPREPLY=($(compgen -W "$themes" -- "$cur"))
                fi
                ;;
            EXTENSION)
                # Complete with extension subcommands
                COMPREPLY=($(compgen -W "list enable disable install update status" -- "$cur"))
                ;;
            *)
                # Default file completion
                COMPREPLY=($(compgen -f -- "$cur"))
                ;;
        esac
    else
        # Default file completion
        COMPREPLY=($(compgen -f -- "$cur"))
    fi
}

# Completion function for zsh
_udos_zsh_complete() {
    local -a commands
    commands=(${_UDOS_COMMANDS[@]})

    if [[ $CURRENT -eq 2 ]]; then
        # First argument - complete with commands
        _describe 'udos commands' commands
    elif [[ $CURRENT -eq 3 ]]; then
        # Second argument - file completion for certain commands
        case "$words[2]" in
            EDIT|VIEW|RUN|SHOW|DELETE|PEEK|TYPO)
                _files -g '*.md *.uscript *.upy *.json'
                ;;
            THEME)
                if [[ -d "core/data/themes" ]]; then
                    local -a themes
                    themes=(${(f)"$(ls core/data/themes/*.json 2>/dev/null | xargs -n1 basename | sed 's/\.json$//')"})
                    _describe 'themes' themes
                fi
                ;;
            EXTENSION)
                local -a ext_cmds
                ext_cmds=('list' 'enable' 'disable' 'install' 'update' 'status')
                _describe 'extension commands' ext_cmds
                ;;
            *)
                _files
                ;;
        esac
    else
        _files
    fi
}

# Register completion based on shell
if [[ -n "$BASH_VERSION" ]]; then
    complete -F _udos_bash_complete udos
    echo "✅ uDOS shell completion loaded (bash)"
elif [[ -n "$ZSH_VERSION" ]]; then
    # Load compinit if not already loaded
    autoload -Uz compinit 2>/dev/null || true
    compdef _udos_zsh_complete udos 2>/dev/null || echo "⚠️  zsh completion registration failed (compinit may not be loaded)"
    echo "✅ uDOS shell completion loaded (zsh)"
fi

