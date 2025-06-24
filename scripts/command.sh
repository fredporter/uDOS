#!/bin/bash
# command.sh — Wrapper to run commands and log stderr if failure

UDOSE_HOME="/root/uDOS"

cmd="$*"
output="$(bash -c "$cmd" 2>&1)"
status=$?

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"
  echo "💥 Error while executing: $cmd"
  echo "💬 $output"
  echo "❌ Command failed with exit code $status" >> "$UDOSE_HOME/uMemory/logs/command-errors-$(date +%Y-%m-%d).log"
  bash "$UDOSE_HOME/scripts/error-logger.sh" "$summary" "$output"
else
  echo "$output"
fi

exit $status