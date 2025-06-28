#!/bin/bash
# command.sh — Wrapper to run commands and log stderr if failure

UHOME="${HOME}/uDOS"

cmd="$*"
output="$(bash -c "$cmd" 2>&1)"
status=$?

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"
  echo "💥 Error while executing: $cmd"
  echo "💬 $output"
  echo "❌ Command failed with exit code $status" >> "$UHOME/uMemory/logs/command-errors-log-$(date +%Y-%m-%d).md"
  bash "$UHOME/scripts/error-logger.sh" "$summary" "$output"
else
  echo "$output"
fi

exit $status