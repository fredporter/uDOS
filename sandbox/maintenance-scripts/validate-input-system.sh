#!/bin/bash
# uDOS Input System Validation and Integration Test
# Integrated with template system and development mode support

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UHOME="${UHOME:-$HOME/uDOS}"
UDEV="$UHOME/uDev"

# Check if template validation is available
TEMPLATE_VALIDATION_AVAILABLE=false
if [[ -f "$SCRIPT_DIR/template-validation.sh" ]]; then
    TEMPLATE_VALIDATION_AVAILABLE=true
    source "$SCRIPT_DIR/template-validation.sh"
fi

# Check if development mode is enabled
DEV_MODE_ENABLED=false
if [[ -f "$UDEV/.dev-mode-enabled" || "${UDOS_DEV_MODE:-false}" == "true" ]]; then
    DEV_MODE_ENABLED=true
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m' 
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Test logging
test_log() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

test_pass() {
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
    echo -e "${GREEN}✅ PASS${NC} $1"
}

test_fail() {
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
    echo -e "${RED}❌ FAIL${NC} $1"
}

test_skip() {
    echo -e "${YELLOW}⏭️ SKIP${NC} $1"
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🧪 INPUT SYSTEM TESTS
# ═══════════════════════════════════════════════════════════════════════════════════════

test_script_files() {
    test_log "Testing input system file structure..."
    
    local required_files=(
        "$SCRIPT_DIR/input-system.sh"
        "$SCRIPT_DIR/input-handler.sh"
        "$UHOME/uTemplate/forms/user-setup.json"
        "$UHOME/uTemplate/forms/mission-create.json"
        "$UHOME/uTemplate/forms/system-config.json"
        "$UHOME/uTemplate/form-configuration-template.md"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            test_pass "File exists: $(basename "$file")"
        else
            test_fail "Missing file: $file"
        fi
    done
    
    # Check if scripts are executable
    if [[ -x "$SCRIPT_DIR/input-system.sh" ]]; then
        test_pass "input-system.sh is executable"
    else
        test_fail "input-system.sh is not executable"
    fi
    
    if [[ -x "$SCRIPT_DIR/input-handler.sh" ]]; then
        test_pass "input-handler.sh is executable"
    else
        test_fail "input-handler.sh is not executable"
    fi
}

test_json_configuration() {
    test_log "Testing JSON form configuration validity..."
    
    local form_files=(
        "$UHOME/uTemplate/forms/user-setup.json"
        "$UHOME/uTemplate/forms/mission-create.json"
        "$UHOME/uTemplate/forms/system-config.json"
    )
    
    for form in "${form_files[@]}"; do
        if [[ -f "$form" ]]; then
            if command -v jq >/dev/null 2>&1; then
                if jq '.' "$form" >/dev/null 2>&1; then
                    test_pass "Valid JSON: $(basename "$form")"
                else
                    test_fail "Invalid JSON: $(basename "$form")"
                fi
            else
                test_skip "JSON validation (jq not available): $(basename "$form")"
            fi
        else
            test_fail "Form file not found: $form"
        fi
    done
}

test_shortcode_dataset() {
    test_log "Testing shortcode dataset initialization..."
    
    # Test dataset initialization
    if bash "$SCRIPT_DIR/input-system.sh" init >/dev/null 2>&1; then
        test_pass "Dataset initialization successful"
    else
        test_fail "Dataset initialization failed"
    fi
    
    # Check if dataset was created
    local dataset_file="$UHOME/uTemplate/datasets/shortcodes.json"
    if [[ -f "$dataset_file" ]]; then
        test_pass "Shortcode dataset created"
        
        # Validate dataset structure
        if command -v jq >/dev/null 2>&1; then
            local shortcode_count
            shortcode_count=$(jq '.shortcodes | length' "$dataset_file" 2>/dev/null || echo "0")
            if [[ $shortcode_count -gt 0 ]]; then
                test_pass "Dataset contains $shortcode_count shortcodes"
            else
                test_fail "Dataset appears empty or malformed"
            fi
        fi
    else
        test_fail "Shortcode dataset not created"
    fi
}

test_input_system_help() {
    test_log "Testing input system help command..."
    
    if bash "$SCRIPT_DIR/input-system.sh" help >/dev/null 2>&1; then
        test_pass "Help command executes successfully"
    else
        test_fail "Help command failed"
    fi
}

test_form_validation() {
    test_log "Testing form configuration structure..."
    
    local form_file="$UHOME/uTemplate/forms/user-setup.json"
    
    if [[ -f "$form_file" ]] && command -v jq >/dev/null 2>&1; then
        # Test required fields
        local required_keys=("title" "description" "fields")
        
        for key in "${required_keys[@]}"; do
            if jq -e ".$key" "$form_file" >/dev/null 2>&1; then
                test_pass "Form has required key: $key"
            else
                test_fail "Form missing required key: $key"
            fi
        done
        
        # Test field structure
        local field_count
        field_count=$(jq '.fields | length' "$form_file" 2>/dev/null || echo "0")
        if [[ $field_count -gt 0 ]]; then
            test_pass "Form contains $field_count fields"
        else
            test_fail "Form has no fields defined"
        fi
        
        # Test first field structure
        local first_field_valid=true
        if ! jq -e '.fields[0].name' "$form_file" >/dev/null 2>&1; then
            first_field_valid=false
        fi
        if ! jq -e '.fields[0].label' "$form_file" >/dev/null 2>&1; then
            first_field_valid=false
        fi
        if ! jq -e '.fields[0].type' "$form_file" >/dev/null 2>&1; then
            first_field_valid=false
        fi
        
        if [[ "$first_field_valid" == true ]]; then
            test_pass "First form field has required structure"
        else
            test_fail "First form field missing required properties"
        fi
    else
        test_skip "Form validation (file not found or jq not available)"
    fi
}

test_integration_components() {
    test_log "Testing integration with uCode shell..."
    
    # Test if processor exists
    if [[ -f "$SCRIPT_DIR/processor.sh" ]]; then
        test_pass "Shortcode processor found"
    else
        test_fail "Shortcode processor missing (required for integration)"
    fi
    
    # Test uCode shell existence
    if [[ -f "$SCRIPT_DIR/ucode.sh" ]]; then
        test_pass "uCode shell found"
    else
        test_fail "uCode shell missing"
    fi
    
    # Test template system
    if [[ -d "$UHOME/uTemplate" ]]; then
        test_pass "uTemplate directory exists"
    else
        test_fail "uTemplate directory missing"
    fi
    
    # Test memory structure
    local memory_dirs=("uMemory/forms" "uMemory/config" "uMemory/user")
    for dir in "${memory_dirs[@]}"; do
        mkdir -p "$UHOME/$dir"
        if [[ -d "$UHOME/$dir" ]]; then
            test_pass "Directory exists: $dir"
        else
            test_fail "Failed to create directory: $dir"
        fi
    done
}

test_ascii_interface() {
    test_log "Testing ASCII interface components..."
    
    # Test display configuration
    if [[ -f "$UHOME/uMemory/config/display-vars.sh" ]]; then
        test_pass "Display configuration found"
    else
        test_skip "Display configuration (not required for basic functionality)"
    fi
    
    # Test ASCII interface template
    if [[ -f "$UHOME/uTemplate/ascii-interface-template.md" ]]; then
        test_pass "ASCII interface template found"
    else
        test_fail "ASCII interface template missing"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎯 DEMO FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════════

demo_shortcode_suggestions() {
    echo -e "${BOLD}${CYAN}🔍 Shortcode Suggestion Demo${NC}"
    echo
    
    echo "Testing shortcode suggestions for common prefixes:"
    echo
    
    local test_prefixes=("D" "CH" "M" "P")
    
    for prefix in "${test_prefixes[@]}"; do
        echo -e "${DIM}Prefix: '$prefix'${NC}"
        
        # Test the suggestion function directly
        if bash -c "
            source '$SCRIPT_DIR/input-system.sh'
            init_shortcode_datasets >/dev/null 2>&1
            get_shortcode_suggestions '$prefix' 3 | jq -r '.[] | \"  → [\(.command):\(.args[0])] - \(.description)\"' 2>/dev/null || echo '  No suggestions found'
        "; then
            echo
        else
            echo -e "${RED}  Error getting suggestions${NC}"
            echo
        fi
    done
}

demo_form_structure() {
    echo -e "${BOLD}${CYAN}📝 Form Configuration Demo${NC}"
    echo
    
    local form_file="$UHOME/uTemplate/forms/user-setup.json"
    
    if [[ -f "$form_file" ]] && command -v jq >/dev/null 2>&1; then
        echo "User Setup Form Structure:"
        echo
        
        local title
        title=$(jq -r '.title' "$form_file")
        echo -e "${BOLD}Title:${NC} $title"
        
        local field_count
        field_count=$(jq '.fields | length' "$form_file")
        echo -e "${BOLD}Fields:${NC} $field_count"
        
        echo
        echo "Sample fields:"
        jq -r '.fields[0:3][] | "  • \(.label) (\(.type)\(if .required then " - required" else "" end))"' "$form_file"
        
        echo
        echo -e "${DIM}Full form available at: $form_file${NC}"
    else
        echo -e "${RED}Form file not available or jq not installed${NC}"
    fi
}

# Test development mode integration
test_dev_mode_integration() {
    test_log "Testing development mode integration..."
    
    # Check development directory structure
    if [[ -d "$UDEV" ]]; then
        test_pass "Development directory exists"
        
        local required_dirs=("validation" "templates" "testing" "schemas" "tools")
        for dir in "${required_dirs[@]}"; do
            if [[ -d "$UDEV/$dir" ]]; then
                test_pass "Dev directory exists: $dir"
            else
                test_fail "Missing dev directory: $dir"
            fi
        done
        
        # Check development tools
        if [[ -d "$UDEV/tools" ]]; then
            local tool_count=$(find "$UDEV/tools" -name "*.sh" 2>/dev/null | wc -l)
            if [[ $tool_count -gt 0 ]]; then
                test_pass "Development tools available ($tool_count tools)"
            else
                test_fail "No development tools found"
            fi
        fi
        
        # Check schemas
        if [[ -f "$UDEV/schemas/dataget-schema.json" ]]; then
            test_pass "Dataget schema available"
        else
            test_fail "Missing dataget schema"
        fi
        
    else
        test_fail "Development directory not found"
        test_log "Enable development mode with: ./dev-mode.sh enable"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# 🎯 MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════════════

main() {
    local command="${1:-test}"
    
    case "$command" in
        "test"|"validate")
            echo -e "${BOLD}${CYAN}🧪 uDOS Input System Validation${NC}"
            if [[ "$TEMPLATE_VALIDATION_AVAILABLE" == "true" ]]; then
                echo -e "${CYAN}🔗 Template validation integration: ENABLED${NC}"
            fi
            if [[ "$DEV_MODE_ENABLED" == "true" ]]; then
                echo -e "${CYAN}🛠️ Development mode: ACTIVE${NC}"
            fi
            echo "═══════════════════════════════════════════════════════════"
            echo
            
            test_script_files
            echo
            test_json_configuration
            echo
            test_shortcode_dataset
            echo
            test_input_system_help
            echo
            test_form_validation
            echo
            test_integration_components
            echo
            
            # Run template validation if available
            if [[ "$TEMPLATE_VALIDATION_AVAILABLE" == "true" ]]; then
                test_log "Running integrated template validation..."
                if run_comprehensive_validation >/dev/null 2>&1; then
                    test_pass "Template validation integration successful"
                else
                    test_fail "Template validation integration failed"
                fi
                echo
            fi
            
            # Development mode specific tests
            if [[ "$DEV_MODE_ENABLED" == "true" ]]; then
                test_log "Running development mode specific tests..."
                test_dev_mode_integration
                echo
            fi
            test_ascii_interface
            echo
            
            # Summary
            echo "═══════════════════════════════════════════════════════════"
            echo -e "${BOLD}Test Summary:${NC}"
            echo -e "  Total Tests: $TESTS_TOTAL"
            echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
            echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
            
            if [[ $TESTS_FAILED -eq 0 ]]; then
                echo
                echo -e "${GREEN}🎉 All tests passed! Input system is ready for use.${NC}"
                echo
                echo -e "${BOLD}Next steps:${NC}"
                echo "  1. Run: ./input-system.sh demo"
                echo "  2. Try: [ (opens shortcode selector)" 
                echo "  3. Use: ucode FORM user-setup"
                return 0
            else
                echo
                echo -e "${RED}❌ Some tests failed. Please check the issues above.${NC}"
                return 1
            fi
            ;;
        "demo")
            echo -e "${BOLD}${CYAN}🎯 uDOS Input System Demo${NC}"
            echo "═══════════════════════════════════════════════════════════"
            echo
            
            demo_shortcode_suggestions
            echo
            demo_form_structure
            echo
            
            echo -e "${BOLD}Interactive Demo Options:${NC}"
            echo "  • Run: ./input-system.sh shortcode"
            echo "  • Run: ./input-system.sh form user-setup"  
            echo "  • Try typing [ in the uCode shell for predictive input"
            echo
            ;;
        "help")
            echo -e "${BOLD}uDOS Input System Validation${NC}"
            echo
            echo "USAGE:"
            echo "  $0 [COMMAND]"
            echo
            echo "COMMANDS:"
            echo "  test      Run complete validation suite"
            echo "  validate  Same as test"
            echo "  demo      Show system demonstrations"
            echo "  help      Show this help"
            echo
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo "Run '$0 help' for usage information."
            return 1
            ;;
    esac
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
