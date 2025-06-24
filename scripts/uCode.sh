#!/bin/bash
# check_permissions.sh — Validate and fix permissions for uDOS scripts and files

UDOSE_HOME="${UDOSE_HOME:-$HOME/uDOS}"

LOG_FILE="$UDOSE_HOME/uMemory/logs/permissions-$(date +%Y-%m-%d).log"
mkdir -p "$(dirname "$LOG_FILE")"

TARGET_DIRS=(
  "$UDOSE_HOME/scripts"
  "$UDOSE_HOME/uMemory"
  "$UDOSE_HOME/uKnowledge"
  "$UDOSE_HOME/sandbox"
)

get_file_owner_and_perm() {
  local file="$1"
  local owner perm
  if stat --version >/dev/null 2>&1; then
    # GNU stat
    owner=$(stat -c '%U' "$file")
    perm=$(stat -c '%a' "$file")
  else
    # BSD stat (macOS)
    owner=$(stat -f '%Su' "$file")
    perm=$(stat -f '%Lp' "$file")
  fi
  echo "$owner $perm"
}

check_shebang() {
  local file="$1"
  local first_line interpreter
  if [[ -f "$file" ]]; then
    read -r first_line < "$file"
    if [[ "$first_line" =~ ^#! ]]; then
      interpreter="${first_line#\#!}"
      # Check if interpreter exists in PATH or as absolute path
      if [[ "$interpreter" == /* ]]; then
        if [[ ! -x "$interpreter" ]]; then
          echo "⚠️ Interpreter not executable or missing: $interpreter in $file" | tee -a "$LOG_FILE"
          return 1
        fi
      else
        if ! command -v "$interpreter" >/dev/null 2>&1; then
          echo "⚠️ Interpreter not found in PATH: $interpreter in $file" | tee -a "$LOG_FILE"
          return 1
        fi
      fi
    else
      echo "⚠️ Missing shebang line in $file" | tee -a "$LOG_FILE"
      return 1
    fi
  fi
  return 0
}

echo "🔍 Starting permissions check at $(date)" | tee -a "$LOG_FILE"

for DIR in "${TARGET_DIRS[@]}"; do
  if [[ -d "$DIR" ]]; then
    find "$DIR" -type f ! -perm /u+x | while read -r FILE; do
      # Skip system-command.sh here to handle explicitly later
      if [[ "$(basename "$FILE")" == "system-command.sh" ]]; then
        continue
      fi
      chmod +x "$FILE"
      echo "✅ Fixed permissions: $FILE" | tee -a "$LOG_FILE"
      check_shebang "$FILE"
    done
  else
    echo "⚠️ Directory not found: $DIR" | tee -a "$LOG_FILE"
  fi
done

# Explicit check for system-command.sh
SYSTEM_CMD="$UDOSE_HOME/scripts/system-command.sh"
if [[ -f "$SYSTEM_CMD" && ! -x "$SYSTEM_CMD" ]]; then
  chmod +x "$SYSTEM_CMD"
  echo "✅ Fixed permissions: $SYSTEM_CMD" | tee -a "$LOG_FILE"
fi
check_shebang "$SYSTEM_CMD"

echo "✅ Permissions check completed at $(date)" | tee -a "$LOG_FILE"

# Main command dispatch loop
case "${1^^}" in
  # ... (other command cases go here)

  BYE)
    echo "👋 uDOS is now entering shutdown mode..."
    echo "🔒 Session is idle. You can type:"
    echo "   [R] RESTART → Soft refresh"
    echo "   [B] REBOOT  → Full setup and check"
    echo "   [D] DESTROY → Delete your identity"
    echo "   [C] CANCEL  → Return to CLI"
    read -n1 -rp "👉 Choose next step: " next
    echo ""
    case "${next^^}" in
      R) $0 RESTART ;;
      B) $0 REBOOT ;;
      D) $0 DESTROY ;;
      *) echo "🌀 Returning to CLI..." ;;
    esac
    ;;

  EXIT)
    $0 BYE
    ;;

  QUIT)
    $0 BYE
    ;;
esac