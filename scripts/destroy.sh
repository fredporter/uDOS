#!/bin/bash
# destroy.sh - Safe identity/memory wipe tool for uDOS

UHOME="${HOME}/uDOS"
UDENT="${UHOME}/uMemory/state/identity.md"

echo "💥 uDOS DESTROY Mode:"
echo "  [A] Remove identity (empty sandbox)"
echo "  [B] Kill sandbox and uMemory"
echo "  [C] Kill sandbox, create legacy, flush uMemory"
echo "  [D] Reboot (no data loss)"
echo "  [E] Exit to uCode (no data loss)"
read -n1 -rp $'\033[1;34m👉 Select DESTROY option:\033[0m ' choice
echo ""

case "$(echo "$choice" | tr '[:lower:]' '[:upper:]')" in
  A)
    echo "⚠️ Deleting sandbox only..."
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    echo "✅ Sandbox deleted."
    ;;
  B)
    echo "⚠️ Deleting sandbox and uMemory..."
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    [ -d "$UHOME/uMemory" ] && rm -rf "$UHOME/uMemory"
    echo "✅ Sandbox and memory deleted."
    ;;
  C)
    echo "⚠️ Flushing uMemory except legacy..."
    mkdir -p "$UHOME/legacy"
    [ -d "$UHOME/uMemory" ] && find "$UHOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
    echo "✅ Legacy preserved. All other memory cleared."
    ;;
  D)
    echo "♻️ Rebooting system only..."
    exec "$UHOME/scripts/uCode.sh"
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
exec "$UHOME/scripts/uCode.sh"
