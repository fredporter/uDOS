#!/usr/bin/env bash

set -euo pipefail

ok_count=0
warn_count=0
fail_count=0

ok() {
  printf '[OK] %s\n' "$1"
  ok_count=$((ok_count + 1))
}

warn() {
  printf '[WARN] %s\n' "$1"
  warn_count=$((warn_count + 1))
}

fail() {
  printf '[FAIL] %s\n' "$1"
  fail_count=$((fail_count + 1))
}

check_cmd() {
  local cmd="$1"
  local level="$2"
  local message="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "$message"
  else
    case "$level" in
      required) fail "$message (missing: $cmd)" ;;
      optional) warn "$message (missing: $cmd)" ;;
      *) warn "$message (missing: $cmd)" ;;
    esac
  fi
}

check_tty() {
  if [ -t 0 ] && [ -t 1 ]; then
    ok "Interactive TTY detected (selectors can run interactively)"
  else
    warn "No interactive TTY detected (use non-interactive flags like --file/--files)"
  fi
}

check_python_module() {
  local module="$1"
  local label="$2"
  if [ -x ".venv/bin/python" ] && .venv/bin/python -c "import ${module}" >/dev/null 2>&1; then
    ok "$label available in .venv"
  elif UV_PROJECT_ENVIRONMENT=.venv uv run python -c "import ${module}" >/dev/null 2>&1; then
    ok "$label available in project environment"
  else
    warn "$label not available in project environment"
  fi
}

printf 'uCODE selector readiness check\n'
printf '================================\n'

check_tty

# Shell selector stack (primary)
check_cmd "fzf" "required" "fzf available (primary file/multi selector)"
check_cmd "fd" "optional" "fd available (preferred fast file discovery)"
check_cmd "gum" "optional" "gum available (preferred menu selector)"
check_cmd "bat" "optional" "bat available (preview renderer for fzf)"

# Python selector stack (secondary)
check_python_module "pick" "pick (default Python selector)"
check_python_module "InquirerPy" "InquirerPy (optional rich prompts)"

printf '\nSelector policy summary\n'
printf '%s\n' '-----------------------'
printf '1) Interactive path: fzf+fd (files), gum (menus), pick (python default)\n'
printf '2) Non-interactive path: explicit flags (--file/--files/--choice)\n'
printf '3) Optional Python rich prompts: InquirerPy when installed\n'
printf '4) Fallback order: interactive selectors -> built-in shell select -> non-interactive args\n'

printf '\nResult\n'
printf '%s\n' '------'
printf 'OK: %s | WARN: %s | FAIL: %s\n' "$ok_count" "$warn_count" "$fail_count"

if [ "$fail_count" -gt 0 ]; then
  printf 'Selector readiness: NOT READY (missing required dependencies)\n'
  exit 2
fi

printf 'Selector readiness: READY (required dependencies present)\n'
