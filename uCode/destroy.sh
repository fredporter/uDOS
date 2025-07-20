#!/bin/bash
# destroy.sh - Safe identity/memory wipe tool for uDOS

HEADLESS="${UCODE_HEADLESS:-false}"

UHOME="${HOME}/uDOS"
UDENT="${UHOME}/sandbox/identity.md"

echo "💥 uDOS DESTROY Mode:"
echo "  [A] Remove identity (empty sandbox)"
echo "  [B] Kill sandbox and uMemory"
echo "  [C] Kill sandbox, create legacy, flush uMemory"
echo "  [D] Reboot (no data loss)"
echo "  [E] Exit to uCode (no data loss)"
read -n1 -rp $'\033[1;34m👉 Select DESTROY option:\033[0m ' choice
echo ""

if [[ "$HEADLESS" == "true" ]]; then
  echo "🧪 DESTROY called in headless mode. Auto-exiting..."
  exit 0
fi

case "$(echo "$choice" | tr '[:lower:]' '[:upper:]')" in
  A)
    echo "⚠️ Deleting sandbox only..."
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    echo "✅ Sandbox deleted."
    echo "📝 Action: DESTROY A → sandbox wiped"
    ;;
  B)
    echo "⚠️ Deleting sandbox and uMemory..."
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    [ -d "$UHOME/uMemory" ] && rm -rf "$UHOME/uMemory"
    echo "✅ Sandbox and memory deleted."
    echo "📝 Action: DESTROY B → sandbox and memory wiped"
    ;;
  C)
    echo "⚠️ Flushing uMemory except legacy..."
    # Ensure legacy directory exists in uMemory
    mkdir -p "$UHOME/uMemory"
    # Remove everything from uMemory except the legacy folder
    [ -d "$UHOME/uMemory" ] && find "$UHOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
    # Also remove sandbox
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    echo "✅ Legacy preserved. All other memory cleared."
    echo "📝 Action: DESTROY C → legacy preserved, memory flushed"
    ;;
  D)
    echo "♻️ Rebooting system only..."
    exec "$UHOME/uCode/ucode.sh"
    ;;
  E)
    echo "🌀 Exiting to uCode..."
    exit 0
    ;;
  *)
    echo "❌ Invalid option. Cancelled."
    ;;
esac

echo "🔁 Rebooting to apply changes..."
exec "$UHOME/uCode/ucode.sh" || exec bash
