#!/bin/bash
# error-logger.sh — Logs errors to /uMemory/logs/errors/error-YYYY-MM-DD.md

log_error() {
  local msg="$1"
  local now="$(date '+%Y-%m-%d %H:%M:%S')"
  local date_str="$(date '+%Y-%m-%d')"
  local log_dir="${UOS_MEMORY_DIR:-/uMemory}/logs/errors"
  local log_file="$log_dir/error-${date_str}.md"
  mkdir -p "$log_dir"
  echo "- [$now] $msg" >> "$log_file"
}
