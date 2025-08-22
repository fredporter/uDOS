done
done
done
echo "Local directory setup complete."
#!/bin/bash
# Minimal uDOS Local Setup Checker
# Usage: ./setup-local.sh

set -e

ROOT_DIR="$(dirname "$0")/../.."
ERROR_HANDLER="$ROOT_DIR/uCORE/system/error-handler.sh"
DESTROY_CMD="$ROOT_DIR/uCORE/launcher/universal/destroy-udos.sh"
REBOOT_CMD="$ROOT_DIR/uCORE/launcher/universal/reboot-udos.sh"

function handle_error {
    echo "[uDOS Setup] ERROR: $1"
    if [ -f "$ERROR_HANDLER" ]; then
        bash "$ERROR_HANDLER" "$1"
    fi
    if [ -f "$DESTROY_CMD" ]; then
        bash "$DESTROY_CMD"
    fi
    if [ -f "$REBOOT_CMD" ]; then
        bash "$REBOOT_CMD"
    fi
    exit 1
}

# 1. Check for sandbox/user/user.md
USER_MD="$ROOT_DIR/sandbox/user/user.md"
if [ ! -f "$USER_MD" ]; then
    handle_error "Missing $USER_MD. Initiating DESTROY/REBOOT."
else
    echo "Found: $USER_MD"
fi

# 2. Check for system folders (must exist)
SYSTEM_DIRS=("$ROOT_DIR/uCORE" "$ROOT_DIR/uKNOWLEDGE" "$ROOT_DIR/docs" "$ROOT_DIR/uSCRIPT" "$ROOT_DIR/uSERVER")
for dir in "${SYSTEM_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        handle_error "System folder missing: $dir. Initiating DESTROY/REBOOT."
    else
        echo "Found: $dir"
    fi
done

# 3. Check for uMEMORY/user/installation.md
INSTALL_MD="$ROOT_DIR/uMEMORY/user/installation.md"
if [ ! -f "$INSTALL_MD" ]; then
    handle_error "Missing $INSTALL_MD. Initiating DESTROY/REBOOT."
else
    echo "Found: $INSTALL_MD"
fi

echo "uDOS minimal local setup verified."
