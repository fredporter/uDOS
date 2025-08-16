#!/bin/bash
# destroy.sh - Realm Reset Tool for uDOS

HEADLESS="${UCODE_HEADLESS:-false}"

UHOME="${HOME}/uDOS"
UDENT="${UHOME}/sandbox/identity.md"

echo -e "\033[1;31m⚔️ uDOS Realm Reset\033[0m"
echo -e "\033[1;33m🏰 Choose your path, adventurer:\033[0m"
echo ""
echo -e "  \033[1;36m[A]\033[0m \033[0;36mReset Identity\033[0m    - Clear sandbox, keep all data"
echo -e "  \033[1;36m[B]\033[0m \033[0;33mFresh Start\033[0m      - Clear sandbox and memory (clean slate)"
echo -e "  \033[1;36m[C]\033[0m \033[0;35mArchive & Reset\033[0m  - Save to legacy, clear everything else"
echo -e "  \033[1;36m[D]\033[0m \033[0;32mReboot Only\033[0m      - Restart system (no data loss)"
echo -e "  \033[1;36m[E]\033[0m \033[0;37mExit Safely\033[0m      - Return to uDOS (no changes)"
echo ""
read -n1 -rp $'\033[1;34m�️ Select your destiny:\033[0m ' choice
echo ""

if [[ "$HEADLESS" == "true" ]]; then
  echo "🧪 Realm reset called in headless mode. Auto-exiting..."
  exit 0
fi

case "$(echo "$choice" | tr '[:lower:]' '[:upper:]')" in
  A)
    echo -e "\n\033[1;33m⚠️ Clearing adventurer identity only...\033[0m"
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    echo -e "\033[1;32m✅ Identity cleared. Your data remains safe.\033[0m"
    echo -e "\033[0;36m📝 Action: RESET A → Identity wiped, data preserved\033[0m"
    ;;
  B)
    echo -e "\n\033[1;31m⚠️ Beginning fresh journey (clearing all data)...\033[0m"
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    [ -d "$UHOME/uMemory" ] && rm -rf "$UHOME/uMemory"
    echo -e "\033[1;32m✅ Fresh start complete. Welcome, new adventurer!\033[0m"
    echo -e "\033[0;36m📝 Action: RESET B → Complete fresh start\033[0m"
    ;;
  C)
    echo -e "\n\033[1;35m⚠️ Archiving your journey to legacy vault...\033[0m"
    # Ensure legacy directory exists in uMemory
    mkdir -p "$UHOME/uMemory/legacy"
    # Move current data to legacy before clearing
    if [ -d "$UHOME/uMemory" ]; then
        timestamp=$(date +%Y%m%d_%H%M%S)
        [ -f "$UHOME/uMemory/identity.md" ] && mv "$UHOME/uMemory/identity.md" "$UHOME/uMemory/legacy/identity_$timestamp.md" 2>/dev/null
        find "$UHOME/uMemory" -mindepth 1 -maxdepth 1 ! -name "legacy" -exec rm -rf {} +
    fi
    [ -d "$UHOME/sandbox" ] && rm -rf "$UHOME/sandbox"
    echo -e "\033[1;32m✅ Your journey archived. Ready for new adventures!\033[0m"
    echo -e "\033[0;36m📝 Action: RESET C → Archived to legacy, fresh slate created\033[0m"
    ;;
  D)
    echo -e "\n\033[1;32m♻️ Restarting the realm...\033[0m"
    exec "$UHOME/uCode/ucode.sh"
    ;;
  E)
    echo -e "\n\033[1;37m� Returning to the realm safely...\033[0m"
    exit 0
    ;;
  *)
    echo -e "\n\033[1;31m❌ Invalid choice. The realm remains unchanged.\033[0m"
    ;;
esac

echo -e "\n\033[1;36m� Restarting realm to apply changes...\033[0m"
exec "$UHOME/uCode/ucode.sh" || exec bash
