#!/bin/bash
# uDOS Variable System Initialization
# Called during system startup to ensure all variables are properly configured

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Source the export system
source "$SCRIPT_DIR/export-variables.sh"

# Initialize variable system
initialize_variable_system() {
    echo "🔧 Initializing uDOS Variable System..."

    # Create default session values if they don't exist
    local current_values="$SCRIPT_DIR/../user/variables/values-current.json"

    if [[ ! -f "$current_values" ]]; then
        mkdir -p "$(dirname "$current_values")"
        echo '{"values": {}}' > "$current_values"
    fi

    # Export all variables to environment
    export_for_uscript

    # Set system-specific defaults
    export UDOS_INITIALIZED="true"
    export UDOS_VARIABLE_SYSTEM="enhanced"
    export UDOS_SYSTEM_READY="true"

    echo "✅ Variable system initialized successfully"
}

# Run initialization
initialize_variable_system
