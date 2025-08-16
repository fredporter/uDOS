#!/bin/bash
# test-consolidation.sh - Test consolidated uCode scripts

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test helpers
test_start() {
    local test_name="$1"
    ((TOTAL_TESTS++))
    echo -e "${BLUE}🧪 Testing: $test_name${NC}"
}

test_pass() {
    local test_name="$1"
    ((PASSED_TESTS++))
    echo -e "${GREEN}✅ PASS: $test_name${NC}"
}

test_fail() {
    local test_name="$1"
    local error="$2"
    ((FAILED_TESTS++))
    echo -e "${RED}❌ FAIL: $test_name${NC}"
    echo -e "${RED}   Error: $error${NC}"
}

# Test script execution
test_script() {
    local script="$1"
    local args="${2:-help}"
    local test_name="$script $args"
    
    test_start "$test_name"
    
    if [[ ! -f "./$script" ]]; then
        test_fail "$test_name" "Script not found"
        return 1
    fi
    
    if [[ ! -x "./$script" ]]; then
        test_fail "$test_name" "Script not executable"
        return 1
    fi
    
    # Test execution (without timeout, some systems don't have it)
    if "./$script" $args >/dev/null 2>&1; then
        test_pass "$test_name"
        return 0
    else
        local exit_code=$?
        test_fail "$test_name" "Execution failed with exit code $exit_code"
        return 1
    fi
}

# Main test suite
main() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║              🧪 uDOS CONSOLIDATION TEST SUITE               ║${NC}"
    echo -e "${PURPLE}║                Testing Consolidated Scripts                  ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    cd "$(dirname "$0")" || exit 1
    
    # Test consolidated core scripts
    echo -e "${CYAN}📋 Testing Core Consolidated Scripts:${NC}"
    test_script "core.sh" "help"
    test_script "setup.sh" "help" 
    test_script "template.sh" "help"
    test_script "processor.sh" "help"
    echo
    
    # Test renamed scripts
    echo -e "${CYAN}📋 Testing Renamed Scripts:${NC}"
    test_script "companion.sh" "help" 2>/dev/null || echo "⚠️  companion.sh may not have help command"
    test_script "package.sh" "help" 2>/dev/null || echo "⚠️  package.sh may not have help command"
    test_script "sandbox.sh" "help" 2>/dev/null || echo "⚠️  sandbox.sh may not have help command"  
    test_script "roles.sh" "help" 2>/dev/null || echo "⚠️  roles.sh may not have help command"
    test_script "privacy.sh" "help" 2>/dev/null || echo "⚠️  privacy.sh may not have help command"
    echo
    
    # Test core functionality
    echo -e "${CYAN}📋 Testing Core Functionality:${NC}"
    test_start "Core system structure check"
    if ./core.sh structure >/dev/null 2>&1; then
        test_pass "Core system structure check"
    else
        test_fail "Core system structure check" "Structure validation failed"
    fi
    
    test_start "Setup system validation"
    if ./setup.sh validate >/dev/null 2>&1; then
        test_pass "Setup system validation"
    else
        test_fail "Setup system validation" "Setup validation failed"
    fi
    
    test_start "Template system validation"
    if ./template.sh validate >/dev/null 2>&1; then
        test_pass "Template system validation"
    else
        test_fail "Template system validation" "Template validation failed"
    fi
    
    test_start "Processor shortcode listing"
    if ./processor.sh list >/dev/null 2>&1; then
        test_pass "Processor shortcode listing"
    else
        test_fail "Processor shortcode listing" "Shortcode listing failed"
    fi
    echo
    
    # Test integration
    echo -e "${CYAN}📋 Testing System Integration:${NC}"
    test_start "ucode.sh syntax check"
    if bash -n ucode.sh 2>/dev/null; then
        test_pass "ucode.sh syntax check"
    else
        test_fail "ucode.sh syntax check" "Syntax errors found"
    fi
    echo
    
    # Summary
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                        📊 TEST SUMMARY                      ║${NC}"  
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${WHITE}Total Tests: $TOTAL_TESTS${NC}"
    echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
    echo
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! Consolidation successful!${NC}"
        echo
        echo -e "${CYAN}📈 Consolidation Results:${NC}"
        echo "  ✅ Core system functions consolidated into 4 main scripts"
        echo "  ✅ Script names simplified and standardized"
        echo "  ✅ Functionality preserved and tested"
        echo "  ✅ Integration with main ucode.sh maintained"
        echo
        exit 0
    else
        echo -e "${YELLOW}⚠️  Some tests failed. Review the output above.${NC}"
        exit 1
    fi
}

main "$@"
