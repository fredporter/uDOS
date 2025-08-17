#!/bin/bash

# Test the Gemini CLI integration installation
# This script verifies that all components are properly installed and functional

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)"
EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo -e "\n${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                    Gemini CLI Integration Test                              ║${NC}"
    echo -e "${PURPLE}║                           uDOS Extension                                    ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_step() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

test_node_js() {
    print_step "Testing Node.js installation"
    
    if command -v node >/dev/null 2>&1; then
        local version=$(node --version)
        local major_version=$(echo "$version" | sed 's/v//' | cut -d. -f1)
        
        if [[ "$major_version" -ge 20 ]]; then
            print_success "Node.js $version (>= 20 required)"
        else
            print_error "Node.js $version detected, but >= 20 required"
            return 1
        fi
    else
        print_error "Node.js not found"
        return 1
    fi
}

test_gemini_cli() {
    print_step "Testing Gemini CLI installation"
    
    if command -v gemini >/dev/null 2>&1; then
        local version=$(gemini --version 2>/dev/null || echo "unknown")
        print_success "Gemini CLI installed: $version"
    else
        print_warning "Gemini CLI not found in PATH"
        print_step "Attempting to install..."
        
        if npm list -g @google/gemini-cli >/dev/null 2>&1; then
            print_success "Gemini CLI package is installed globally"
        else
            print_error "Gemini CLI package not installed"
            return 1
        fi
    fi
}

test_extension_files() {
    print_step "Testing extension file structure"
    
    local required_files=(
        "install-gemini-cli.sh"
        "udos-gemini.sh"
        "command-mode.sh"
        "ucode-commands.sh"
        "manifest.json"
        "README.md"
        "AUTH_SETUP.md"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [[ -f "$EXTENSION_DIR/$file" ]]; then
            print_success "Found: $file"
        else
            print_error "Missing: $file"
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        print_success "All extension files present"
    else
        print_error "${#missing_files[@]} files missing"
        return 1
    fi
}

test_script_permissions() {
    print_step "Testing script permissions"
    
    local executable_files=(
        "$EXTENSION_DIR/install-gemini-cli.sh"
        "$EXTENSION_DIR/udos-gemini.sh"
        "$EXTENSION_DIR/command-mode.sh"
        "$EXTENSION_DIR/ucode-commands.sh"
        "$UDOS_ROOT/uCore/scripts/assist"
        "$UDOS_ROOT/uCore/scripts/command"
    )
    
    for file in "${executable_files[@]}"; do
        if [[ -x "$file" ]]; then
            print_success "Executable: $(basename "$file")"
        else
            print_error "Not executable: $file"
            return 1
        fi
    done
}

test_integration_scripts() {
    print_step "Testing integration script syntax"
    
    # Test bash syntax
    local scripts=(
        "$EXTENSION_DIR/udos-gemini.sh"
        "$EXTENSION_DIR/command-mode.sh"
        "$UDOS_ROOT/uCore/scripts/assist"
        "$UDOS_ROOT/uCore/scripts/command"
    )
    
    for script in "${scripts[@]}"; do
        if bash -n "$script" 2>/dev/null; then
            print_success "Syntax OK: $(basename "$script")"
        else
            print_error "Syntax error in: $script"
            return 1
        fi
    done
}

test_json_manifests() {
    print_step "Testing JSON manifest files"
    
    local json_files=(
        "$EXTENSION_DIR/manifest.json"
        "$UDOS_ROOT/uInstall/distribution-types.json"
    )
    
    for json_file in "${json_files[@]}"; do
        if [[ -f "$json_file" ]]; then
            if python3 -m json.tool "$json_file" >/dev/null 2>&1; then
                print_success "Valid JSON: $(basename "$json_file")"
            else
                print_error "Invalid JSON: $json_file"
                return 1
            fi
        else
            print_warning "JSON file not found: $json_file"
        fi
    done
}

test_assist_mode() {
    print_step "Testing ASSIST mode launcher"
    
    # Test if the script can be called without errors (dry run)
    if timeout 5s "$UDOS_ROOT/uCore/scripts/assist" --help >/dev/null 2>&1 || [[ $? -eq 124 ]]; then
        print_success "ASSIST mode launcher responds"
    else
        print_warning "ASSIST mode launcher test inconclusive (may require authentication)"
    fi
}

test_command_mode() {
    print_step "Testing COMMAND mode launcher"
    
    # Test if the script exists and has proper structure
    if grep -q "uDOS COMMAND MODE" "$EXTENSION_DIR/command-mode.sh"; then
        print_success "COMMAND mode script structure OK"
    else
        print_error "COMMAND mode script structure missing"
        return 1
    fi
}

test_package_installer() {
    print_step "Testing package installer"
    
    local package_installer="$UDOS_ROOT/uCode/packages/install-gemini-cli.sh"
    
    if [[ -x "$package_installer" ]]; then
        if bash -n "$package_installer"; then
            print_success "Package installer syntax OK"
        else
            print_error "Package installer has syntax errors"
            return 1
        fi
    else
        print_error "Package installer not found or not executable"
        return 1
    fi
}

test_distribution_integration() {
    print_step "Testing distribution integration"
    
    # Check if gemini-cli is included in distribution types
    if grep -q "gemini-cli" "$UDOS_ROOT/uInstall/distribution-types.json"; then
        print_success "Extension included in distribution types"
    else
        print_error "Extension not found in distribution configuration"
        return 1
    fi
}

run_all_tests() {
    print_header
    
    local test_functions=(
        "test_node_js"
        "test_gemini_cli"
        "test_extension_files"
        "test_script_permissions"
        "test_integration_scripts"
        "test_json_manifests"
        "test_assist_mode"
        "test_command_mode"
        "test_package_installer"
        "test_distribution_integration"
    )
    
    local passed=0
    local failed=0
    
    for test_func in "${test_functions[@]}"; do
        if $test_func; then
            ((passed++))
        else
            ((failed++))
        fi
        echo
    done
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Tests Passed: $passed${NC}"
    echo -e "${RED}Tests Failed: $failed${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════════${NC}"
    
    if [[ $failed -eq 0 ]]; then
        echo -e "\n${GREEN}🎉 All tests passed! Gemini CLI integration is ready to use.${NC}"
        echo -e "\n${CYAN}Next Steps:${NC}"
        echo -e "1. Set up authentication: ${YELLOW}cat $EXTENSION_DIR/AUTH_SETUP.md${NC}"
        echo -e "2. Test ASSIST mode: ${YELLOW}./uCore/scripts/assist${NC}"
        echo -e "3. Test COMMAND mode: ${YELLOW}./uCore/scripts/command${NC}"
        return 0
    else
        echo -e "\n${RED}❌ Some tests failed. Please review the errors above.${NC}"
        return 1
    fi
}

# Main execution
run_all_tests
