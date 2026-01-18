#!/usr/bin/env bash
#
# uDOS Environment Setup
# Source this file to configure your shell environment for uDOS
#

# Determine uDOS installation directory
if [ -n "$UDOS_HOME" ]; then
    # Already set
    :
elif [ -n "$BASH_SOURCE" ]; then
    # Bash
    UDOS_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
elif [ -n "$ZSH_VERSION" ]; then
    # Zsh
    UDOS_HOME="$(cd "$(dirname "$0")/.." && pwd)"
else
    # Fallback
    UDOS_HOME="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
fi

export UDOS_HOME

# Add uDOS bin to PATH
if [[ ":$PATH:" != *":$UDOS_HOME/bin:"* ]]; then
    export PATH="$UDOS_HOME/bin:$PATH"
fi

# Set Python path
export PYTHONPATH="$UDOS_HOME:$PYTHONPATH"

# Configuration
export UDOS_CONFIG="${UDOS_CONFIG:-$UDOS_HOME/core/data/config.json}"
export UDOS_THEME="${UDOS_THEME:-foundation}"

# Activate virtual environment if it exists
if [ -f "$UDOS_HOME/.venv/bin/activate" ]; then
    source "$UDOS_HOME/.venv/bin/activate"
fi

# Helper function to run .upy scripts
upy() {
    if [ -z "$1" ]; then
        echo "Usage: upy <script.upy> [args...]" >&2
        return 1
    fi

    udos "$@"
}

# Helper function to validate .upy scripts
upy-validate() {
    if [ -z "$1" ]; then
        echo "Usage: upy-validate <script.upy>" >&2
        return 1
    fi

    udos --validate "$1"
}

# Helper function to list uDOS commands
upy-commands() {
    python3 -c "
import sys
sys.path.insert(0, '$UDOS_HOME')
from core.runtime import CommandRegistry

registry = CommandRegistry()
commands = registry.list_commands()

print('\\nuDOS Commands (UPPERCASE-HYPHEN format):\\n')
for cmd in commands:
    print(f'  {cmd.name:25} {cmd.description}')
print()
"
}

# Completion for bash
if [ -n "$BASH_VERSION" ]; then
    _udos_complete() {
        local cur prev opts
        COMPREPLY=()
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"

        opts="--help --version --interactive --verbose --no-color --validate"

        if [[ ${cur} == -* ]]; then
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
            return 0
        fi

        # Complete .upy files
        COMPREPLY=( $(compgen -f -X '!*.upy' -- ${cur}) )
    }

    complete -F _udos_complete udos
    complete -F _udos_complete upy
fi

# Completion for zsh
if [ -n "$ZSH_VERSION" ]; then
    autoload -U compinit && compinit

    _udos() {
        local -a opts
        opts=(
            '--help:Show help message'
            '--version:Show version information'
            '--interactive:Force interactive mode'
            '--verbose:Enable verbose output'
            '--no-color:Disable colored output'
            '--validate:Validate script syntax'
        )

        _arguments \
            '1:script:_files -g "*.upy"' \
            '*::arg:->args' \
            $opts
    }

    compdef _udos udos
    compdef _udos upy
fi

echo "✅ uDOS environment configured"
echo "   UDOS_HOME: $UDOS_HOME"
echo "   Run 'udos' to start interactive mode"
echo "   Run 'upy-commands' to see available commands"
