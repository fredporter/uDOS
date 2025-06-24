#!/bin/bash
# invoke-command.sh — Wrapper to run commands and log stderr if failure

cmd="$*"
output="$(eval "$cmd" 2>&1)"
status=$?

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"
  bash /uDOS/scripts/error-logger.sh "$summary" "$output"

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
    R) echo "🔄 Refreshing..."; $HOME/uDOS/scripts/uCode.sh REFRESH ;;
    B) echo "♻️ Rebooting..."; $HOME/uDOS/scripts/uCode.sh REBOOT ;;
    D) echo "☠️ Destroying..."; $HOME/uDOS/scripts/uCode.sh DESTROY ;;
    V) echo "📜 Showing error log:"; tail -n 20 $HOME/uDOS/uMemory/logs/errors/$(date +%Y-%m-%d)-errorlog.md ;;
    *) echo "👋 Exiting."; exit $status ;;
  esac
else
  echo "$output"
fi

exit $status
