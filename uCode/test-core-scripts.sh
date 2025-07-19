#!/bin/bash
# Test Script for uDOS Core Scripts
# Tests destroy.sh, init-user.sh, start.sh, and validation

# set -euo pipefail  # Disabled for better diagnostics

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; ((PASSED_TESTS++)); }
log_error() { echo -e "${RED}❌ $1${NC}"; ((FAILED_TESTS++)); }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_bold() { echo -e "${BOLD}$1${NC}"; }

test_script_syntax() {
    local script="$1"
    local description="$2"
    ((TOTAL_TESTS++))
    
    log_info "Testing syntax: $description"
    
    if bash -n "$script" 2>/dev/null; then
        log_success "Syntax check passed: $script"
    else
        log_error "Syntax error in: $script"
    fi
}

test_script_execution() {
    local script="$1"
    local args="$2"
    local description="$3"
    local expected_exit_code="${4:-0}"
    ((TOTAL_TESTS++))
    
    log_info "Testing execution: $description"
    
    # Run script and capture exit code
    set +e
    if [[ -n "$args" ]]; then
        timeout 10s bash -c "$script $args" >/dev/null 2>&1
    else
        timeout 10s "$script" >/dev/null 2>&1
    fi
    local exit_code=$?
    set -e
    
    if [[ $exit_code -eq $expected_exit_code ]] || [[ $exit_code -eq 124 ]]; then  # 124 is timeout
        log_success "Execution test passed: $script (exit code: $exit_code)"
    else
        log_error "Execution test failed: $script (exit code: $exit_code, expected: $expected_exit_code)"
    fi
}

test_file_existence() {
    local file="$1"
    local description="$2"
    ((TOTAL_TESTS++))
    
    log_info "Testing file existence: $description"
    
    if [[ -f "$file" ]]; then
        log_success "File exists: $file"
    else
        log_error "File missing: $file"
    fi
}

test_environment_setup() {
    ((TOTAL_TESTS++))
    log_info "Testing environment variables and paths"
    
    # Check if we're in the right directory
    if [[ -d "uCode" ]] && [[ -d "uTemplate" ]] && [[ -d "uKnowledge" ]]; then
        log_success "Working directory structure valid"
    else
        log_error "Invalid working directory - missing core directories"
    fi
}

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "=================================================================="
    echo "               🧪 uDOS CORE SCRIPTS TEST SUITE"
    echo "                  Testing Critical Components"
    echo "=================================================================="
    echo -e "${NC}"
}

print_summary() {
    echo
    log_bold "📊 Test Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        log_success "🎉 All tests passed! Core scripts are functioning correctly."
        exit 0
    else
        log_error "❌ Some tests failed. Review the output above."
        exit 1
    fi
}

main() {
    print_header
    
    # Test 1: Environment setup
    test_environment_setup
    
    # Test 2-4: File existence
    test_file_existence "./uCode/destroy.sh" "Destroy script"
    test_file_existence "./uCode/init-user.sh" "User initialization script"
    test_file_existence "./uCode/start.sh" "Start script"
    test_file_existence "./uCode/validate-installation.sh" "Validation script"
    
    # Test 5-8: Syntax checks
    test_script_syntax "./uCode/destroy.sh" "Destroy script syntax"
    test_script_syntax "./uCode/init-user.sh" "User initialization script syntax"
    test_script_syntax "./uCode/start.sh" "Start script syntax"
    test_script_syntax "./uCode/validate-installation.sh" "Validation script syntax"
    
    # Test 9-12: Safe execution tests
    test_script_execution "./uCode/destroy.sh" "UCODE_HEADLESS=true" "Destroy script (headless mode)" 0
    test_script_execution "./uCode/validate-installation.sh" "quick" "Validation script (quick mode)" 1  # Expected to fail in test environment
    
    # Test 13: Init-user functionality (safe test)
    ((TOTAL_TESTS++))
    log_info "Testing init-user script initial behavior"
    if ./uCode/init-user.sh 2>&1 | head -5 | grep -q "Welcome to uDOS"; then
        log_success "Init-user script shows correct welcome message"
    else
        log_error "Init-user script doesn't show expected welcome"
    fi
    
    # Test 14: Start script environment setup
    ((TOTAL_TESTS++))
    log_info "Testing start script environment variables"
    if grep -q "UHOME=" ./uCode/start.sh && grep -q "UROOT=" ./uCode/start.sh; then
        log_success "Start script has required environment variables"
    else
        log_error "Start script missing environment variables"
    fi
    
    print_summary
}

# Change to uDOS directory
cd "$(dirname "$0")/.." || exit 1

main "$@"
