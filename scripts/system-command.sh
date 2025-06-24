#!/bin/bash
# system-command.sh — Wrapper to run commands and log stderr if failure

UDOSE_HOME="${UDOSE_HOME:-$HOME/uDOS}"

cmd="$*"
tmpfile="$(mktemp)"
bash -c "$cmd" > "$tmpfile" 2>&1
status=$?

output="$(cat "$tmpfile")"
rm -f "$tmpfile"

if [ $status -ne 0 ]; then
  summary="Command failed: $cmd"
  bash "$UDOSE_HOME/scripts/error-logger.sh" "$summary" "$output"
  echo "💥 Error while executing: $cmd"
  echo "💬 $output"
else
  echo "$output"
fi

exit $status