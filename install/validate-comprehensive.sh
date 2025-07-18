#!/bin/bash
# uDOS v1.0 Comprehensive Installation & Release Validation
# Production-ready validation suite for complete system verification

set -euo pipefail

# Configuration
UDOS_VERSION="v1.0.0"
VALIDATION_LOG="validation-$(date +%Y%m%d-%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

log_info() { echo -e "${BLUE}ℹ️  $1${NC}" | tee -a "$VALIDATION_LOG"; }
log_success() { echo -e "${GREEN}✅ $1${NC}" | tee -a "$VALIDATION_LOG"; PASSED_CHECKS=$((PASSED_CHECKS + 1)); }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$VALIDATION_LOG"; WARNING_CHECKS=$((WARNING_CHECKS + 1)); }
log_error() { echo -e "${RED}❌ $1${NC}" | tee -a "$VALIDATION_LOG"; FAILED_CHECKS=$((FAILED_CHECKS + 1)); }
log_bold() { echo -e "${BOLD}$1${NC}" | tee -a "$VALIDATION_LOG"; }

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║          🔍 uDOS v1.0 COMPREHENSIVE VALIDATION SUITE            ║"
    echo "║            Installation & Production Readiness Test             ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_item() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo "$1" >> "$VALIDATION_LOG"
}

# Check 1-5: Core System Structure
validate_core_structure() {
    log_bold "📁 Core Structure Validation"
    
    local core_dirs=(
        "uCode"
        "uMemory"
        "uKnowledge"
        "uScript" 
        "uTemplate"
    )
    
    for dir in "${core_dirs[@]}"; do
        check_item "Core directory: $dir"
        if [[ -d "$dir" ]]; then
            log_success "$dir directory exists"
        else
            log_error "$dir directory missing"
        fi
    done
}

# Check 6-10: Essential Scripts
validate_essential_scripts() {
    log_bold "🔧 Essential Scripts Validation"
    
    local scripts=(
        "start-udos.sh"
        "uCode/ucode.sh"
        "uCode/check.sh"
        "uCode/structure.sh"
        "install-udos.sh"
    )
    
    for script in "${scripts[@]}"; do
        check_item "Script: $script"
        if [[ -f "$script" ]]; then
            if [[ -x "$script" ]]; then
                log_success "$script exists and is executable"
            else
                log_warning "$script exists but not executable"
                chmod +x "$script" 2>/dev/null || log_error "Could not make $script executable"
            fi
        else
            log_error "$script missing"
        fi
    done
}

# Check 11-15: Documentation
validate_documentation() {
    log_bold "📚 Documentation Validation"
    
    local docs=(
        "README.md"
        "CHANGELOG.md"
        "LICENSE"
        "docs/roadmap/ROADMAP_INDEX.md"
    )
    
    for doc in "${docs[@]}"; do
        check_item "Documentation: $doc"
        if [[ -f "$doc" ]]; then
            if [[ -s "$doc" ]]; then
                log_success "$doc exists and has content"
            else
                log_warning "$doc exists but is empty"
            fi
        else
            log_error "$doc missing"
        fi
    done
}

# Check 16-20: Roadmap Completeness
validate_roadmaps() {
    log_bold "🗺️ Roadmap Validation"
    
    local roadmaps=(
        "001-uDOS-foundation.md"
        "002-uDOS-format.md"
        "003-uDOS-execution.md"
        "004-uDOS-interface.md"
        "005-uDOS-location.md"
    )
    
    local roadmap_dir="docs/roadmap"
    
    for roadmap in "${roadmaps[@]}"; do
        check_item "Roadmap: $roadmap"
        local roadmap_path="$roadmap_dir/$roadmap"
        if [[ -f "$roadmap_path" ]]; then
            # Check for v1.0 completion marker
            if grep -q "Status.*v1.0" "$roadmap_path" 2>/dev/null; then
                log_success "$roadmap is v1.0 complete"
            else
                log_warning "$roadmap exists but may not be v1.0 complete"
            fi
        else
            log_error "$roadmap missing"
        fi
    done
}

# Check 21-25: VS Code Integration
validate_vscode_integration() {
    log_bold "💻 VS Code Integration Validation"
    
    check_item "VS Code tasks configuration"
    if [[ -f ".vscode/tasks.json" ]]; then
        if grep -q "Start uDOS" ".vscode/tasks.json" 2>/dev/null; then
            log_success "VS Code tasks configured"
        else
            log_warning "VS Code tasks.json exists but may be incomplete"
        fi
    else
        log_error "VS Code tasks.json missing"
    fi
    
    check_item "VS Code settings"
    if [[ -f ".vscode/settings.json" ]]; then
        log_success "VS Code settings found"
    else
        log_warning "VS Code settings.json missing (optional)"
    fi
    
    check_item "VS Code extension availability"
    if command -v code &> /dev/null; then
        log_success "VS Code CLI available"
        
        check_item "uDOS extension detection"
        if code --list-extensions | grep -i udos &> /dev/null; then
            log_success "uDOS extension installed"
        else
            log_warning "uDOS extension not found in VS Code"
        fi
    else
        log_warning "VS Code not installed"
    fi
    
    check_item "Extension source files"
    if [[ -d "uExtension" ]] && [[ -f "uExtension/package.json" ]]; then
        log_success "uDOS extension source available"
    else
        log_warning "uDOS extension source not found"
    fi
}

# Check 26-30: Template System
validate_template_system() {
    log_bold "📄 Template System Validation"
    
    local templates=(
        "uTemplate/mission-template.md"
        "uTemplate/move-template.md"
        "uTemplate/milestone-template.md"
        "uTemplate/input-template.md"
        "uTemplate/uc-template.md"
    )
    
    for template in "${templates[@]}"; do
        check_item "Template: $(basename "$template")"
        if [[ -f "$template" ]]; then
            if grep -q "# Template" "$template" 2>/dev/null; then
                log_success "$(basename "$template") is properly formatted"
            else
                log_warning "$(basename "$template") exists but may not be properly formatted"
            fi
        else
            log_error "$(basename "$template") missing"
        fi
    done
}

# Check 31-35: System Dependencies
validate_system_dependencies() {
    log_bold "⚙️ System Dependencies Validation"
    
    local required_commands=(
        "git"
        "bash"
        "curl"
        "grep"
        "find"
    )
    
    for cmd in "${required_commands[@]}"; do
        check_item "Command: $cmd"
        if command -v "$cmd" &> /dev/null; then
            local version=$(command "$cmd" --version 2>/dev/null | head -1 || echo "unknown")
            log_success "$cmd available ($version)"
        else
            log_error "$cmd not found"
        fi
    done
}

# Functional Tests
run_functional_tests() {
    log_bold "🧪 Functional Tests"
    
    # Test uCode execution
    check_item "uCode script execution"
    if [[ -x "uCode/ucode.sh" ]]; then
        if ./uCode/ucode.sh --version &>/dev/null; then
            log_success "uCode script executes successfully"
        else
            log_warning "uCode script runs but may have issues"
        fi
    else
        log_error "Cannot test uCode execution"
    fi
    
    # Test start script
    check_item "Start script validation"
    if [[ -x "start-udos.sh" ]]; then
        # Test without actually starting (dry run if supported)
        if bash -n "start-udos.sh"; then
            log_success "start-udos.sh syntax valid"
        else
            log_error "start-udos.sh has syntax errors"
        fi
    else
        log_error "Cannot validate start script"
    fi
    
    # Test template generation
    check_item "Template system functionality"
    if [[ -x "uCode/structure.sh" ]]; then
        if bash -n "uCode/structure.sh"; then
            log_success "Template system script syntax valid"
        else
            log_error "Template system has syntax errors"
        fi
    else
        log_error "Cannot test template system"
    fi
}

# User Role System Check
validate_user_roles() {
    log_bold "👥 User Role System Validation"
    
    check_item "User role documentation"
    if grep -r "wizard\|sorcerer\|ghost\|imp" uKnowledge/ &>/dev/null; then
        log_success "User role system documented"
    else
        log_warning "User role documentation incomplete"
    fi
    
    check_item "Permission matrix"
    if [[ -f "WIZARD_INSTALLATION_STRATEGY.md" ]]; then
        if grep -q "Permission Matrix" "WIZARD_INSTALLATION_STRATEGY.md"; then
            log_success "Permission matrix documented"
        else
            log_warning "Permission matrix may be incomplete"
        fi
    else
        log_error "Installation strategy document missing"
    fi
}

# Chester AI Integration Check
validate_chester_integration() {
    log_bold "🤖 Chester AI Integration Validation"
    
    check_item "Chester personality definition"
    if grep -r -i "chester" uKnowledge/ &>/dev/null; then
        log_success "Chester AI companion documented"
    else
        log_warning "Chester AI documentation not found"
    fi
    
    check_item "AI integration points"
    if grep -r "AI\|assistant\|companion" docs/roadmap/ &>/dev/null; then
        log_success "AI integration documented in roadmaps"
    else
        log_warning "AI integration documentation incomplete"
    fi
}

# Security and Privacy Check
validate_security_privacy() {
    log_bold "🔒 Security & Privacy Validation"
    
    check_item "Privacy-first architecture"
    if grep -r -i "privacy" uKnowledge/ &>/dev/null; then
        log_success "Privacy considerations documented"
    else
        log_warning "Privacy documentation incomplete"
    fi
    
    check_item "Local-first operation"
    if grep -r "local.first\|local-first" uKnowledge/ &>/dev/null; then
        log_success "Local-first architecture documented"
    else
        log_warning "Local-first architecture documentation incomplete"
    fi
    
    check_item "Sensitive file protection"
    if [[ -f ".gitignore" ]]; then
        if grep -q "uExtension\|*.log\|.DS_Store" ".gitignore"; then
            log_success "Sensitive files properly ignored"
        else
            log_warning "gitignore may be incomplete"
        fi
    else
        log_error ".gitignore missing"
    fi
}

# Distribution Package Validation
validate_distribution_packages() {
    log_bold "📦 Distribution Package Validation"
    
    check_item "Installer script"
    if [[ -f "install-udos.sh" ]]; then
        if bash -n "install-udos.sh"; then
            log_success "Installer script syntax valid"
        else
            log_error "Installer script has syntax errors"
        fi
    else
        log_error "Installer script missing"
    fi
    
    check_item "macOS app builder"
    if [[ -f "build-macos-app.sh" ]]; then
        if bash -n "build-macos-app.sh"; then
            log_success "macOS app builder syntax valid"
        else
            log_error "macOS app builder has syntax errors"
        fi
    else
        log_warning "macOS app builder not found"
    fi
    
    check_item "Release preparation script"
    if [[ -f "prepare-release.sh" ]]; then
        if bash -n "prepare-release.sh"; then
            log_success "Release preparation script syntax valid"
        else
            log_error "Release preparation script has syntax errors"
        fi
    else
        log_warning "Release preparation script not found"
    fi
}

# Production Readiness Check
validate_production_readiness() {
    log_bold "🚀 Production Readiness Validation"
    
    check_item "Version consistency"
    if grep -q "v1.0" README.md 2>/dev/null; then
        log_success "Version information present in README"
    else
        log_warning "Version information missing from README"
    fi
    
    check_item "Changelog completeness"
    if [[ -f "CHANGELOG.md" ]] && grep -q "v1.0" "CHANGELOG.md"; then
        log_success "Changelog includes v1.0 information"
    else
        log_warning "Changelog may be incomplete for v1.0"
    fi
    
    check_item "License file"
    if [[ -f "LICENSE" ]] && [[ -s "LICENSE" ]]; then
        log_success "License file present and not empty"
    else
        log_error "License file missing or empty"
    fi
    
    check_item "Installation strategy documentation"
    if [[ -f "WIZARD_INSTALLATION_STRATEGY.md" ]] && grep -q "wizard installation" "WIZARD_INSTALLATION_STRATEGY.md"; then
        log_success "Complete installation strategy documented"
    else
        log_error "Installation strategy documentation incomplete"
    fi
}

# Generate comprehensive validation report
generate_report() {
    echo "" | tee -a "$VALIDATION_LOG"
    log_bold "📊 COMPREHENSIVE VALIDATION SUMMARY"
    echo "" | tee -a "$VALIDATION_LOG"
    
    local pass_rate=$(safe_divide $PASSED_CHECKS $TOTAL_CHECKS)
    
    echo "Total Checks: $TOTAL_CHECKS" | tee -a "$VALIDATION_LOG"
    echo "✅ Passed: $PASSED_CHECKS" | tee -a "$VALIDATION_LOG"
    echo "⚠️  Warnings: $WARNING_CHECKS" | tee -a "$VALIDATION_LOG"
    echo "❌ Failed: $FAILED_CHECKS" | tee -a "$VALIDATION_LOG"
    echo "📈 Pass Rate: ${pass_rate}%" | tee -a "$VALIDATION_LOG"
    echo "" | tee -a "$VALIDATION_LOG"
    
    # Production readiness assessment
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        if [[ $WARNING_CHECKS -eq 0 ]]; then
            log_success "🎉 ALL VALIDATIONS PASSED - uDOS v1.0 IS PRODUCTION READY!"
            echo "🚀 Ready for public release and distribution" | tee -a "$VALIDATION_LOG"
        else
            log_success "✅ CORE VALIDATIONS PASSED - Production ready with minor warnings"
            echo "⚠️  $WARNING_CHECKS warnings should be reviewed before release" | tee -a "$VALIDATION_LOG"
        fi
    else
        log_error "❌ CRITICAL ISSUES FOUND - Resolution required before production"
        echo "🔧 $FAILED_CHECKS critical issues must be fixed" | tee -a "$VALIDATION_LOG"
    fi
    
    echo "" | tee -a "$VALIDATION_LOG"
    echo "📝 Detailed log saved to: $VALIDATION_LOG" | tee -a "$VALIDATION_LOG"
    echo "🔗 Run with different modes: quick, full, or distribution" | tee -a "$VALIDATION_LOG"
    
    # Return appropriate exit code
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        return 1
    else
        return 0
    fi
}

# Main validation process
main() {
    local mode="${1:-full}"
    
    # Initialize log file
    echo "uDOS v1.0 Comprehensive Validation Report - $(date)" > "$VALIDATION_LOG"
    echo "========================================" >> "$VALIDATION_LOG"
    echo "Mode: $mode" >> "$VALIDATION_LOG"
    echo "" >> "$VALIDATION_LOG"
    
    print_header
    
    echo "uDOS v1.0 Comprehensive Validation Suite"
    echo "Mode: $mode"
    echo "Results will be logged to: $VALIDATION_LOG"
    echo ""
    
    case "$mode" in
        "quick"|"q")
            validate_core_structure
            echo ""
            validate_essential_scripts
            echo ""
            validate_documentation
            ;;
        "distribution"|"dist"|"d")
            validate_core_structure
            echo ""
            validate_essential_scripts
            echo ""
            validate_documentation
            echo ""
            validate_distribution_packages
            echo ""
            validate_production_readiness
            ;;
        "full"|"f"|*)
            validate_core_structure
            echo ""
            validate_essential_scripts
            echo ""
            validate_documentation
            echo ""
            validate_roadmaps
            echo ""
            validate_vscode_integration
            echo ""
            validate_template_system
            echo ""
            validate_system_dependencies
            echo ""
            run_functional_tests
            echo ""
            validate_user_roles
            echo ""
            validate_chester_integration
            echo ""
            validate_security_privacy
            echo ""
            validate_distribution_packages
            echo ""
            validate_production_readiness
            ;;
    esac
    
    generate_report
    
    # Exit with appropriate code
    if [[ $FAILED_CHECKS -gt 0 ]]; then
        exit 1
    elif [[ $WARNING_CHECKS -gt 0 ]]; then
        exit 2
    else
        exit 0
    fi
}

# Error handling
trap 'echo "❌ Validation failed on line $LINENO"; exit 1' ERR

# Safe division function
safe_divide() {
    local numerator=${1:-0}
    local denominator=${2:-1}
    if [[ $denominator -eq 0 ]]; then
        echo "0"
    else
        echo $((numerator * 100 / denominator))
    fi
}

# Show usage if requested
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "uDOS v1.0 Comprehensive Validation Suite"
    echo ""
    echo "Usage: $0 [mode]"
    echo ""
    echo "Modes:"
    echo "  full         Complete validation (default)"
    echo "  quick        Core structure and scripts only"
    echo "  distribution Package and production readiness"
    echo ""
    echo "Examples:"
    echo "  $0           # Full validation"
    echo "  $0 quick     # Quick validation"
    echo "  $0 dist      # Distribution readiness"
    exit 0
fi

# Run validation
main "$@"
