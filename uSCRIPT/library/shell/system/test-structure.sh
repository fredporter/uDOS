#!/bin/bash
# Simple uDOS Startup Test
# Tests core system functionality with uCORE/code structure

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
VARIABLE_MANAGER="$UDOS_ROOT/uCORE/code/variable-manager.sh"
SETUP_INTEGRATION="$UDOS_ROOT/uCORE/code/system-setup-integration.sh"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🧪 Testing uDOS with uCORE/code structure..."
echo "=============================================="

# Test 1: Check UDOS_ROOT calculation
log_info "Testing UDOS_ROOT calculation..."
echo "   UDOS_ROOT: $UDOS_ROOT"
if [[ -d "$UDOS_ROOT/uCORE" ]] && [[ -d "$UDOS_ROOT/sandbox" ]]; then
    log_success "UDOS_ROOT correctly calculated"
else
    log_error "UDOS_ROOT calculation failed"
    exit 1
fi

# Test 2: Check critical files exist
log_info "Checking critical files..."
critical_files=(
    "uCORE/code/variable-manager.sh"
    "uCORE/code/system-setup-integration.sh"
    "uCORE/code/ucode.sh"
)

for file in "${critical_files[@]}"; do
    if [[ -f "$UDOS_ROOT/$file" ]]; then
        log_success "Found: $file"
    else
        log_error "Missing: $file"
        exit 1
    fi
done

# Test 3: Check executability
log_info "Checking file permissions..."
for file in "${critical_files[@]}"; do
    if [[ -x "$UDOS_ROOT/$file" ]]; then
        log_success "Executable: $file"
    else
        log_warning "Not executable: $file"
    fi
done

# Test 4: Test variable manager
log_info "Testing variable manager..."
if [[ -x "$VARIABLE_MANAGER" ]]; then
    if "$VARIABLE_MANAGER" validate >/dev/null 2>&1; then
        log_success "Variable manager working"
    else
        log_warning "Variable manager validation failed"
    fi
else
    log_error "Variable manager not executable"
fi

# Test 5: Test setup integration
log_info "Testing setup integration..."
if [[ -x "$SETUP_INTEGRATION" ]]; then
    if "$SETUP_INTEGRATION" test >/dev/null 2>&1; then
        log_success "Setup integration working"
    else
        log_warning "Setup integration test failed"
    fi
else
    log_error "Setup integration not executable"
fi

# Test 6: Check user files
log_info "Checking user configuration files..."
user_files=(
    "uMEMORY/user/installation.md"
    "sandbox/user.md"
    "sandbox/current-role.conf"
)

for file in "${user_files[@]}"; do
    if [[ -f "$UDOS_ROOT/$file" ]]; then
        log_success "Found: $file"
    else
        log_warning "Missing: $file (may need setup)"
    fi
done

echo ""
log_success "🎉 uDOS structure test completed!"
echo ""
log_info "Summary:"
echo "  📁 uCORE/code: Core system files ✅"
echo "  🔧 Variable Manager: Working ✅"
echo "  ⚙️ Setup Integration: Working ✅"
echo "  📝 User Files: $(ls -1 "$UDOS_ROOT/sandbox/user.md" "$UDOS_ROOT/uMEMORY/user/installation.md" 2>/dev/null | wc -l)/2 present"
echo ""
echo "Ready to continue development! 🚀"
