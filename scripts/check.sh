#!/bin/bash
# uDOS Beta v1.6.1
# 🧪 check.sh — Validate uDOS system integrity and permissions

UHOME="${HOME}/uDOS"
SANDBOX="${UHOME}/sandbox"
UMEM="${UHOME}/uMemory"
REQUIRED_DIRS=("uCode" "uMemory/moves" "uMemory/state" "uTemplate" "uKnowledge" "sandbox")

# Output helpers
ok()   { echo "✔ $1"; }
warn() { echo "⚠️  $1"; }
fail() { echo "❌ $1"; }

# Check folder structure
check_structure() {
  echo "Checking folder structure..."
  for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$UHOME/$dir" ]]; then
      ok "$dir exists"
    else
      fail "$dir missing"
    fi
  done
}

# Check basic file permissions
check_permissions() {
  echo "Checking file permissions in uDOS..."
  local testfile="$SANDBOX/.perms-test"

  touch "$testfile" 2>/dev/null
  if [[ $? -eq 0 ]]; then
    ok "Sandbox writable"
    rm "$testfile"
  else
    fail "Cannot write to sandbox/ — check permissions"
  fi

  if [[ -w "$UMEM/state" ]]; then
    ok "State directory writable"
  else
    fail "State directory not writable"
  fi
}

# Full system check
check_all() {
  check_structure
  echo
  check_permissions
}

# Parse command
case "$1" in
  setup|structure)
    check_structure
    ;;
  perms|permissions)
    check_permissions
    ;;
  all|"")
    check_all
    ;;
  *)
    echo "Usage:"
    echo "  ./check.sh structure      # Check folder layout"
    echo "  ./check.sh perms          # Check file write permissions"
    echo "  ./check.sh all            # Run full system check"
    ;;
esac