#!/bin/bash
# View the NetHack-style adventure log

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
log_file="$UDOS_ROOT/sandbox/logs/adventure.log"

if [[ -f "$log_file" ]]; then
    echo "🎲 Your Adventure So Far:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat "$log_file"
else
    echo "🎲 No adventures yet! Start using uDOS to begin your quest."
fi
