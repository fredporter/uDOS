#!/bin/bash
# error-logger.sh — Capture and log command failure summaries

UDOSE_HOME="/root/uDOS"

cmd="$*"
output="$(eval "$cmd" 2>&1)"
status=$?

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"
  bash "$UDOSE_HOME/scripts/error-logger.sh" "$summary" "$output"

  # Log the error context to a timestamped markdown file
  ERROR_LOG_DIR="$UDOSE_HOME/uMemory/logs/errors"
  mkdir -p "$ERROR_LOG_DIR"
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
    R) echo "🔄 Refreshing..."; exec "$UDOSE_HOME/scripts/uCode.sh" ;;
    B) echo "♻️ Rebooting..."; "$UDOSE_HOME/scripts/uCode.sh" REBOOT ;;
    D) echo "☠️ Destroying..."; "$UDOSE_HOME/scripts/uCode.sh" DESTROY ;;
    V) echo "📜 Showing error log:"; tail -n 20 "$UDOSE_HOME/uMemory/logs/errors/$(date +%Y-%m-%d)-error-log.md" ;;
    *) echo "🌀 Returning to uCode..."; "$UDOSE_HOME/scripts/uCode.sh"; return ;;
  esac
else
  echo "$output"
fi

exit $status
