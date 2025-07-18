#!/bin/bash
# alpha-v1.0-validation.sh - Comprehensive Alpha v1.0 Feature Validation
# Tests all new systems and reorganization

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🚀 uDOS Alpha v1.0 Validation"
echo "============================="
echo "Testing location: $UDOS_ROOT"
echo ""

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TESTS_RUN++))
    echo -n "Testing $test_name... "
    
    if eval "$test_command" 2>/dev/null; then
        echo "✅ PASS"
        ((TESTS_PASSED++))
        return 0
    else
        echo "❌ FAIL"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Continue on test failures
set +e

echo "🔍 STRUCTURAL VALIDATION"
echo "========================"

# Test 1: Check folder reorganization
run_test "extension/ folder exists" "[[ -d '$UDOS_ROOT/extension' ]]"
run_test "package/ folder exists" "[[ -d '$UDOS_ROOT/package' ]]"
run_test "install/ folder exists" "[[ -d '$UDOS_ROOT/install' ]]"
run_test "sandbox/ folder exists" "[[ -d '$UDOS_ROOT/sandbox' ]]"
run_test "uExtension/ removed" "[[ ! -d '$UDOS_ROOT/uExtension' ]]"

echo ""
echo "📦 PACKAGE SYSTEM VALIDATION"
echo "============================"

# Test package system files
run_test "package manifest exists" "[[ -f '$UDOS_ROOT/package/manifest.json' ]]"
run_test "install queue exists" "[[ -f '$UDOS_ROOT/package/install-queue.txt' ]]"
run_test "package manager script" "[[ -x '$UDOS_ROOT/uCode/package-manager.sh' ]]"

# Test package manager functionality
run_test "package manager runs" "'$UDOS_ROOT/uCode/package-manager.sh' list"
run_test "package validation works" "'$UDOS_ROOT/uCode/package-manager.sh' validate"

echo ""
echo "🏖️ SANDBOX SYSTEM VALIDATION"
echo "============================"

# Test sandbox structure
run_test "sandbox/today exists" "[[ -d '$UDOS_ROOT/sandbox/today' ]]"
run_test "sandbox/sessions exists" "[[ -d '$UDOS_ROOT/sandbox/sessions' ]]"
run_test "sandbox/temp exists" "[[ -d '$UDOS_ROOT/sandbox/temp' ]]"
run_test "sandbox/drafts exists" "[[ -d '$UDOS_ROOT/sandbox/drafts' ]]"
run_test "sandbox/finalized exists" "[[ -d '$UDOS_ROOT/sandbox/finalized' ]]"
run_test "sandbox manager script" "[[ -x '$UDOS_ROOT/uCode/sandbox-manager.sh' ]]"

# Test sandbox functionality
run_test "sandbox manager runs" "'$UDOS_ROOT/uCode/sandbox-manager.sh' status"

echo ""
echo "🔧 DEVELOPER MODE VALIDATION"
echo "============================"

# Test developer mode system
run_test "developer mode script" "[[ -x '$UDOS_ROOT/uCode/developer-mode.sh' ]]"
run_test "developer mode status" "'$UDOS_ROOT/uCode/developer-mode.sh' status"

echo ""
echo "🚀 INSTALLATION SYSTEM VALIDATION"
echo "================================="

# Test installation files
run_test "install README exists" "[[ -f '$UDOS_ROOT/install/README.md' ]]"
run_test "original install script" "[[ -f '$UDOS_ROOT/install-udos.sh' ]]"

echo ""
echo "🔌 EXTENSION VALIDATION"
echo "======================"

# Test extension files
run_test "extension package.json" "[[ -f '$UDOS_ROOT/extension/package.json' ]]"
run_test "extension source exists" "[[ -d '$UDOS_ROOT/extension/src' ]]"
run_test "extension syntaxes" "[[ -d '$UDOS_ROOT/extension/syntaxes' ]]"

echo ""
echo "⚙️ UCODE INTEGRATION VALIDATION"
echo "==============================="

# Test uCode enhancements
run_test "ucode.sh updated" "grep -q 'PACKAGE\\|SANDBOX\\|DEVELOPER' '$UDOS_ROOT/uCode/ucode.sh'"
run_test "help shows new commands" "grep -q 'ALPHA v1.0' '$UDOS_ROOT/uCode/ucode.sh'"

echo ""
echo "📚 DOCUMENTATION VALIDATION"
echo "==========================="

# Test documentation updates
run_test "README updated" "grep -q 'sandbox/' '$UDOS_ROOT/README.md'"
run_test "REPO_STRUCTURE updated" "grep -q 'Alpha v1.0' '$UDOS_ROOT/REPO_STRUCTURE_v1.0.md'"
run_test "Alpha v1.0 summary exists" "[[ -f '$UDOS_ROOT/ALPHA_v1.0_READY.md' ]]"

echo ""
echo "🎯 WORKFLOW VALIDATION"
echo "====================="

# Test critical workflow files
run_test "uCode main script executable" "[[ -x '$UDOS_ROOT/uCode/ucode.sh' ]]"
run_test "start script exists" "[[ -f '$UDOS_ROOT/start-udos.sh' ]]"
run_test "VS Code tasks exist" "[[ -f '$UDOS_ROOT/.vscode/tasks.json' ]]"

echo ""
echo "🔐 USER DATA SEPARATION"
echo "======================"

# Test data organization
run_test "uMemory exists" "[[ -d '$UDOS_ROOT/uMemory' ]]"
run_test "uKnowledge exists" "[[ -d '$UDOS_ROOT/uKnowledge' ]]"
run_test "sandbox separate from uMemory" "[[ '$UDOS_ROOT/sandbox' != '$UDOS_ROOT/uMemory'* ]]"

echo ""
echo "📊 VALIDATION SUMMARY"
echo "==================="
echo "Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo ""
    echo "🎉 ALL TESTS PASSED!"
    echo "✅ uDOS Alpha v1.0 is ready for GitHub launch!"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Commit all changes"
    echo "   2. Create Alpha v1.0 release tag"
    echo "   3. Push to GitHub"
    echo "   4. Create GitHub release with ALPHA_v1.0_READY.md"
    exit 0
else
    echo ""
    echo "❌ VALIDATION FAILED!"
    echo "🔧 Please fix the failed tests before launch"
    exit 1
fi
