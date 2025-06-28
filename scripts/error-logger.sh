#!/bin/bash
# error-logger.sh — Capture and log command failure summaries

UDOSE_HOME="/root/uDOS"

cmd="$*"
output="$(eval "$cmd" 2>&1)"
status=$?

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"
  bash "$UDOSE_HOME/scripts/error-logger.sh" "$summary" "$output"

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
    R) echo "🔄 Refreshing..."; "$UDOSE_HOME/scripts/uCode.sh" REFRESH ;;
    B) echo "♻️ Rebooting..."; "$UDOSE_HOME/scripts/uCode.sh" REBOOT ;;
    D) echo "☠️ Destroying..."; "$UDOSE_HOME/scripts/uCode.sh" DESTROY ;;
    V) echo "📜 Showing error log:"; tail -n 20 "$UDOSE_HOME/uMemory/logs/errors/$(date +%Y-%m-%d)-error-log.md" ;;
    *) echo "👋 Exiting."; exit $status ;;
  esac
else
  echo "$output"
fi

exit $status
