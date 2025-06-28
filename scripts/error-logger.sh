#!/bin/bash
# error-logger.sh — Capture and log command failure summaries

UHOME="${HOME}/uDOS"

cmd="$*"
output="$(eval "$cmd" 2>&1)"
status=$?

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"

  # Log the error context to a timestamped markdown file
  ERROR_LOG_DIR="$UHOME/uMemory/logs/errors"
  timestamp=$(date +"%Y-%m-%d-%H%M%S")
  error_log_file="$ERROR_LOG_DIR/error-log-$timestamp.md"

  {
    echo "# ❌ uDOS Error Log"
    echo "- 🕒 Timestamp: $(date)"
    echo "- 💬 Command: $cmd"
    echo ""
    echo "## 🔎 Output"
    echo '```'
    echo "$output"
    echo '```'
  } > "$error_log_file"

  echo "[$(date +%H:%M:%S)] → error → see: ${error_log_file#"$UHOME/"}" >> "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md"

  echo "📝 Error saved to: $error_log_file"

  echo ""
  echo "💥 An error occurred while executing:"
  echo "   $cmd"
  echo "📄 Log summary: $summary"
  echo ""
  echo "💬 Output:"
  echo "$output"
  echo ""
  echo "🧭 What would you like to do?"
  echo "   [R] Refresh  [B] Reboot  [D] Destroy  [V] View error log  [E] Exit"
  read -n1 -rp "👉 Choose an option: " choice
  echo ""

  case "${choice^^}" in
    R) echo "🔄 Refreshing..."; exec "$UHOME/scripts/uCode.sh" ;;
    B) echo "♻️ Rebooting..."; "$UHOME/scripts/uCode.sh" REBOOT ;;
    D) echo "☠️ Destroying..."; "$UHOME/scripts/uCode.sh" DESTROY ;;
    V) echo "📜 Showing error log:"; tail -n 20 "$error_log_file" ;;
    *) echo "🌀 Returning to uCode..."; "$UHOME/scripts/uCode.sh"; return ;;
  esac
else
  echo "$output"
fi

exit $status
