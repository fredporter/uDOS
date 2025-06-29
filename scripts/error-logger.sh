#!/bin/bash
# error-logger.sh — Capture and log command failure summaries

UHOME="${HOME}/uDOS"
mkdir -p "$UHOME/uMemory/logs"

cmd="$*"
output="$(eval "$cmd" 2>&1)"
status=$?

HEADLESS="${UCODE_HEADLESS:-false}"

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"

  # Log the error context to a timestamped markdown file
  ERROR_LOG_DIR="$UHOME/uMemory/logs/errors"
  mkdir -p "$ERROR_LOG_DIR"
  timestamp=$(date +"%Y-%m-%d-%H%M%S")
  LAST_MOVE="$(tail -n 1 "$UHOME/uMemory/logs/move-log-$(date +%Y-%m-%d).md" 2>/dev/null || echo "N/A")"
  error_log_file="$ERROR_LOG_DIR/error-log-$timestamp.md"

  {
    echo "# ❌ uDOS Error Log"
    echo "- 🕒 Timestamp: $(date)"
    echo "- 💬 Command: $cmd"
    echo "- ⚠️ Exit Status: $status"
    echo "- 🧭 Last User Input: $LAST_MOVE"
    echo ""
    echo "## 🔎 Output"
    echo '```'
    echo "$output"
    echo '```'
    echo ""
    echo "## 🛠 Recovery Suggestion"
    echo "You may try resetting uDOS by running:"
    echo '`bash scripts/uCode.sh DESTROY`'
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

  echo "🚨 Fatal error logged. Recommend reviewing: $error_log_file"
  exit $status
else
  echo "$output"
fi

show_error_log_browser() {
  echo "🗂️ Recent Error Logs:"
  find "$ERROR_LOG_DIR" -type f -name "error-log-*.md" | sort -r | head -5 | while read -r file; do
    echo "- $(basename "$file")"
  done
  echo ""
  read -rp "📄 Enter error log filename to view (or press Enter to cancel): " fname
  [[ -z "$fname" ]] && return
  fullpath="$ERROR_LOG_DIR/$fname"
  if [[ -f "$fullpath" ]]; then
    echo ""
    echo "📜 Showing $fname"
    echo "━━━━━━━━━━━━━━━━━━━━━━━"
    cat "$fullpath"
    echo "━━━━━━━━━━━━━━━━━━━━━━━"
  else
    echo "❌ File not found: $fullpath"
  fi
}

exit $status
