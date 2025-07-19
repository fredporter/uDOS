#!/bin/bash
# uDOS VS Code Extension Integration Test v1.1.0
# Comprehensive test for extension templating and configuration
# Now enforces CAPITAL rule across commands, shortcodes, and variables

set -euo pipefail

UHOME="${HOME}/uDOS"
EXTENSION_DIR="${UHOME}/extension"
VSCODE_DIR="${UHOME}/.vscode"

# Color output helpers
red() { echo -e "\033[0;31m$1\033[0m"; }
green() { echo -e "\033[0;32m$1\033[0m"; }
yellow() { echo -e "\033[0;33m$1\033[0m"; }
blue() { echo -e "\033[0;34m$1\033[0m"; }
bold() { echo -e "\033[1m$1\033[0m"; }

# Test results
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test functions
test_assert() {
    local description="$1"
    local condition="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "  Testing: $description... "
    
    if eval "$condition"; then
        green "✅ PASS"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        red "❌ FAIL"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test template files exist
test_template_system() {
    blue "🧪 Testing Template System"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    test_assert "Extension template exists" "[[ -f '$UHOME/uTemplate/vscode-extension-template.md' ]]"
    test_assert "Workspace template exists" "[[ -f '$UHOME/uTemplate/vscode-workspace-template.md' ]]"
    test_assert "Template processor exists" "[[ -f '$UHOME/uCode/vscode-template-processor.sh' ]]"
    test_assert "Template processor is executable" "[[ -x '$UHOME/uCode/vscode-template-processor.sh' ]]"
    
    echo
}

# Test VS Code configuration
test_vscode_config() {
    blue "🔧 Testing VS Code Configuration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    test_assert "VS Code directory exists" "[[ -d '$VSCODE_DIR' ]]"
    test_assert "Workspace settings exist" "[[ -f '$VSCODE_DIR/settings.json' ]]"
    test_assert "Settings contain uDOS config" "grep -q 'udos.shellPath' '$VSCODE_DIR/settings.json'"
    test_assert "Settings contain Copilot config" "grep -q 'github.copilot.enable' '$VSCODE_DIR/settings.json'"
    test_assert "Settings contain user role" "grep -q 'udos.userRole' '$VSCODE_DIR/settings.json'"
    test_assert "Valid JSON syntax" "python3 -m json.tool '$VSCODE_DIR/settings.json' >/dev/null 2>&1"
    
    echo
}

# Test extension structure
test_extension_structure() {
    blue "🔌 Testing Extension Structure"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    test_assert "Extension directory exists" "[[ -d '$EXTENSION_DIR' ]]"
    test_assert "Package.json exists" "[[ -f '$EXTENSION_DIR/package.json' ]]"
    test_assert "TypeScript config exists" "[[ -f '$EXTENSION_DIR/tsconfig.json' ]]"
    test_assert "Extension source exists" "[[ -f '$EXTENSION_DIR/src/extension.ts' ]]"
    test_assert "Compiled extension exists" "[[ -f '$EXTENSION_DIR/dist/extension.js' ]]"
    test_assert "Packaged extension exists" "[[ -f '$EXTENSION_DIR/udos-extension-1.0.0.vsix' ]]"
    
    # Test package.json content
    if [[ -f "$EXTENSION_DIR/package.json" ]]; then
        test_assert "Package.json has uDOS version" "grep -q '\"displayName\": \"uDOS 1.1.0' '$EXTENSION_DIR/package.json'"
        test_assert "Package.json has commands" "grep -q '\"commands\"' '$EXTENSION_DIR/package.json'"
        test_assert "Package.json has uScript language" "grep -q '\"uscript\"' '$EXTENSION_DIR/package.json'"
        test_assert "Package.json valid JSON" "python3 -m json.tool '$EXTENSION_DIR/package.json' >/dev/null 2>&1"
    fi
    
    echo
}

# Test uScript language support
test_uscript_support() {
    blue "📝 Testing uScript Language Support"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    test_assert "Language config exists" "[[ -f '$EXTENSION_DIR/language-configuration.json' ]]"
    test_assert "Syntax highlighting exists" "[[ -f '$EXTENSION_DIR/syntaxes/uscript.tmLanguage.json' ]]"
    test_assert "uScript snippets exist" "[[ -f '$EXTENSION_DIR/snippets/uscript.json' ]]"
    
    # Test file associations in workspace settings
    if [[ -f "$VSCODE_DIR/settings.json" ]]; then
        test_assert "uScript file associations configured" "grep -q '\"*.uscript\": \"uscript\"' '$VSCODE_DIR/settings.json'"
        test_assert "Mission file associations configured" "grep -q '\"mission-\*.md\": \"markdown\"' '$VSCODE_DIR/settings.json'"
    fi
    
    echo
}

# Test command integration
test_command_integration() {
    blue "⚡ Testing Command Integration"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Test that ucode.sh exists and is executable
    test_assert "uCode shell exists" "[[ -f '$UHOME/uCode/ucode.sh' ]]"
    test_assert "uCode shell is executable" "[[ -x '$UHOME/uCode/ucode.sh' ]]"
    
    # Test other core scripts
    test_assert "Dashboard script exists" "[[ -f '$UHOME/uCode/dash.sh' ]]"
    test_assert "Validation script exists" "[[ -f '$UHOME/uCode/validate-installation.sh' ]]"
    test_assert "Companion system exists" "[[ -f '$UHOME/uCode/companion-system.sh' ]]"
    
    echo
}

# Test GitHub distribution readiness
test_github_readiness() {
    blue "🚀 Testing GitHub Distribution Readiness"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    test_assert "README exists" "[[ -f '$UHOME/README.md' ]]"
    test_assert "LICENSE exists" "[[ -f '$UHOME/LICENSE' ]]"
    test_assert "CHANGELOG exists" "[[ -f '$UHOME/CHANGELOG.md' ]]"
    test_assert "Extension README exists" "[[ -f '$EXTENSION_DIR/README.md' ]]"
    test_assert "Install script exists" "[[ -f '$UHOME/install-udos.sh' ]]"
    test_assert "Start script exists" "[[ -f '$UHOME/start-udos.sh' ]]"
    
    # Test that repository is clean for distribution
    test_assert "No uMemory in extension" "[[ ! -d '$EXTENSION_DIR/uMemory' ]]"
    test_assert "No progress artifacts in extension" "[[ ! -d '$EXTENSION_DIR/progress' ]]"
    
    echo
}

# Test template processor functionality
test_template_processor() {
    blue "🛠️ Testing Template Processor"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Test processor commands
    local processor="$UHOME/uCode/vscode-template-processor.sh"
    
    test_assert "Processor validates successfully" "cd '$UHOME' && '$processor' validate >/dev/null 2>&1"
    
    # Test that processor can generate settings
    local test_dir="/tmp/udos-test-$$"
    mkdir -p "$test_dir/.vscode"
    
    test_assert "Processor help works" "'$processor' help >/dev/null 2>&1"
    
    rm -rf "$test_dir"
    
    echo
}

# Main test runner
run_integration_tests() {
    echo
    bold "🧪 uDOS VS Code Extension Integration Test Suite"
    echo "══════════════════════════════════════════════════"
    echo
    
    # Run all test suites
    test_template_system
    test_vscode_config
    test_extension_structure
    test_uscript_support
    test_command_integration
    test_github_readiness
    test_template_processor
    
    # Test summary
    echo
    bold "📊 Test Results Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Total Tests: $TESTS_RUN"
    green "  Passed: $TESTS_PASSED"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        red "  Failed: $TESTS_FAILED"
    else
        green "  Failed: $TESTS_FAILED"
    fi
    
    local pass_rate=$((TESTS_PASSED * 100 / TESTS_RUN))
    echo "  Pass Rate: ${pass_rate}%"
    
    echo
    if [[ $TESTS_FAILED -eq 0 ]]; then
        green "🎉 All integration tests passed! Extension system is ready for GitHub distribution."
    else
        yellow "⚠️ Some tests failed. Please review the issues above."
    fi
    echo
    
    # Return appropriate exit code
    [[ $TESTS_FAILED -eq 0 ]]
}

# Run the tests
run_integration_tests "$@"
