#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load shared env helpers when available
if [ -f "$SCRIPT_DIR/udos-common.sh" ]; then
  # shellcheck disable=SC1090
  source "$SCRIPT_DIR/udos-common.sh"
  resolve_udos_root >/dev/null 2>&1 || true
fi

# Prefer system-installed vibe CLI (mistral-vibe), avoid recursion
vibe_bin="$(command -v vibe 2>/dev/null || true)"
if [ -n "$vibe_bin" ] && [ "$vibe_bin" != "$SCRIPT_DIR/vibe" ]; then
  exec "$vibe_bin" "$@"
fi

vibe_bin="$(which -a vibe 2>/dev/null | grep -v "${SCRIPT_DIR}/vibe" | head -n 1 || true)"
if [ -n "$vibe_bin" ]; then
  exec "$vibe_bin" "$@"
fi

cat <<'EOF' >&2
[vibe] CLI not found on PATH.

Fix:
  - Run: ./bin/ucli cmd "SETUP vibe"
  - Or install: pip install mistral-vibe

Note:
  - Tasks pipe commands into ./bin/vibe, which expects the vibe CLI.
EOF
exit 1
