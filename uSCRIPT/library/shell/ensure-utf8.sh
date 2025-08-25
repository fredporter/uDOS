#!/bin/bash
# uDOS v1.4 UTF-8 Environment Enforcer
# Ensures consistent UTF-8 encoding across all uDOS components
# Source this from all entry points to prevent text/font rendering issues

# Force UTF-8 locale settings
export LANG=en_AU.UTF-8
export LC_ALL=en_AU.UTF-8
export UDOS_ENCODING=UTF-8

# Terminal compatibility settings
export TERM=${TERM:-xterm-256color}

# Store encoding preference in user memory for persistence
if [[ -d "uMEMORY/user" ]]; then
    echo "UDOS_ENCODING=UTF-8" > uMEMORY/user/encoding.env
    echo "LANG=en_AU.UTF-8" >> uMEMORY/user/encoding.env
    echo "LC_ALL=en_AU.UTF-8" >> uMEMORY/user/encoding.env
fi

# Verify UTF-8 support
if ! locale -a | grep -q "en_AU.utf8\|en_AU.UTF-8"; then
    echo "⚠️  Warning: en_AU.UTF-8 locale not available on this system"
    echo "   Falling back to C.UTF-8 or en_US.UTF-8"

    if locale -a | grep -q "C.UTF-8"; then
        export LANG=C.UTF-8
        export LC_ALL=C.UTF-8
    elif locale -a | grep -q "en_US.utf8\|en_US.UTF-8"; then
        export LANG=en_US.UTF-8
        export LC_ALL=en_US.UTF-8
    fi
fi

# Debug mode - show encoding settings if requested
if [[ "${UDOS_DEBUG_ENCODING:-0}" == "1" ]]; then
    echo "🔤 uDOS UTF-8 Enforcer Active:"
    echo "   LANG=$LANG"
    echo "   LC_ALL=$LC_ALL"
    echo "   TERM=$TERM"
    echo "   UDOS_ENCODING=$UDOS_ENCODING"
fi
