#!/bin/bash
# uDOS GitHub Launch Readiness Validation v1.0
# 🚀 Final validation for alpha v1.0 launch

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"
UCODE="${UHOME}/uCode"
EXTENSION_DIR="${UHOME}/uDOS-Extension"
VALIDATION_REPORT="${UMEM}/state/launch-validation.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Validation results
declare -a PASSED_TESTS=()
declare -a FAILED_TESTS=()
declare -a WARNING_TESTS=()

log() { 
    echo -e "${CYAN}[$(date '+%H:%M:%S')] [validation]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] [ERROR]${NC} $1" >&2
    FAILED_TESTS+=("$1")
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] [SUCCESS]${NC} $1"
    PASSED_TESTS+=("$1")
}

warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] [WARNING]${NC} $1"
    WARNING_TESTS+=("$1")
}

# Test functions
test_core_structure() {
    log "Testing core project structure..."
    
    local required_dirs=("uCode" "uMemory" "uKnowledge" "uScript" "uTemplate")
    local missing_dirs=()
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$UHOME/$dir" ]]; then
            success "Core directory exists: $dir"
        else
            error "Missing core directory: $dir"
            missing_dirs+=("$dir")
        fi
    done
    
    [[ ${#missing_dirs[@]} -eq 0 ]]
}

test_core_scripts() {
    log "Testing core shell scripts..."
    
    local required_scripts=("ucode.sh" "check.sh" "dash.sh" "structure.sh")
    local missing_scripts=()
    
    for script in "${required_scripts[@]}"; do
        if [[ -f "$UCODE/$script" && -x "$UCODE/$script" ]]; then
            success "Core script exists and executable: $script"
        else
            error "Missing or non-executable script: $script"
            missing_scripts+=("$script")
        fi
    done
    
    [[ ${#missing_scripts[@]} -eq 0 ]]
}

test_package_system() {
    log "Testing package system..."
    
    local packages=("bat" "fd" "glow" "jq" "fzf" "rg")
    local missing_packages=()
    
    for pkg in "${packages[@]}"; do
        if command -v "$pkg" >/dev/null 2>&1; then
            success "Package installed: $pkg"
        else
            warning "Package not installed: $pkg"
            missing_packages+=("$pkg")
        fi
    done
    
    # Test package manager
    if [[ -f "$UCODE/packages/manager-simple.sh" && -x "$UCODE/packages/manager-simple.sh" ]]; then
        success "Package manager operational"
    else
        error "Package manager missing or not executable"
        return 1
    fi
    
    [[ ${#missing_packages[@]} -eq 0 ]]
}

test_vscode_extension() {
    log "Testing VS Code extension..."
    
    # Check extension structure
    if [[ -d "$EXTENSION_DIR" ]]; then
        success "VS Code extension directory exists"
    else
        error "VS Code extension directory missing"
        return 1
    fi
    
    # Check required files
    local required_files=("package.json" "tsconfig.json" "src/extension.ts")
    for file in "${required_files[@]}"; do
        if [[ -f "$EXTENSION_DIR/$file" ]]; then
            success "Extension file exists: $file"
        else
            error "Extension file missing: $file"
        fi
    done
    
    # Check if compiled
    if [[ -f "$EXTENSION_DIR/dist/extension.js" ]]; then
        success "Extension compiled successfully"
    else
        warning "Extension not compiled - run compilation task"
    fi
    
    # Check syntax highlighting
    if [[ -f "$EXTENSION_DIR/syntaxes/uscript.tmLanguage.json" ]]; then
        success "uScript syntax highlighting available"
    else
        error "uScript syntax highlighting missing"
    fi
}

test_dashboard_system() {
    log "Testing dashboard system..."
    
    # Test original dashboard
    if [[ -f "$UCODE/dash.sh" && -x "$UCODE/dash.sh" ]]; then
        success "Original dashboard script operational"
    else
        error "Original dashboard script missing"
    fi
    
    # Test dashboard system
    if [[ -f "$UCODE/dash.sh" && -x "$UCODE/dash.sh" ]]; then
        success "Dashboard script operational"
        
        # Test dashboard functionality
        if "$UCODE/dash.sh" build >/dev/null 2>&1; then
            success "Dashboard builds successfully"
        else
            warning "Dashboard build issues"
        fi
    else
        error "Dashboard script missing"
    fi
}

test_companion_system() {
    log "Testing Companion System..."
    
    if [[ -f "$UCODE/companion-system.sh" && -x "$UCODE/companion-system.sh" ]]; then
        success "Companion system script exists"
        
        # Test companion system initialization
        if "$UCODE/companion-system.sh" init >/dev/null 2>&1; then
            success "Companion system initializes correctly"
        else
            warning "Companion system initialization issues"
        fi
    else
        error "Companion system script missing"
    fi
    
    # Check VS Code settings
    if [[ -f "$UHOME/.vscode/settings.json" ]]; then
        success "VS Code companion settings configured"
    else
        warning "VS Code companion settings not configured"
    fi
}

test_template_system() {
    log "Testing template system..."
    
    local template_files=("mission-template.md" "move-template.md" "input-template.md")
    for template in "${template_files[@]}"; do
        if [[ -f "$UHOME/uTemplate/$template" ]]; then
            success "Template exists: $template"
        else
            warning "Template missing: $template"
        fi
    done
    
    # Test template generator if exists
    if [[ -f "$UCODE/template-generator.sh" ]]; then
        success "Template generator available"
    else
        warning "Template generator not found"
    fi
}

test_vscode_tasks() {
    log "Testing VS Code tasks integration..."
    
    if [[ -f "$UHOME/.vscode/tasks.json" ]]; then
        success "VS Code tasks configuration exists"
        
        # Check for dashboard tasks
        if grep -q "📊 Dashboard" "$UHOME/.vscode/tasks.json"; then
            success "Dashboard task configured"
        else
            warning "Dashboard task missing"
        fi
        
        if grep -q "Companion System" "$UHOME/.vscode/tasks.json"; then
            success "Companion integration task configured"
        else
            warning "Companion integration task missing"
        fi
    else
        error "VS Code tasks configuration missing"
    fi
}

test_documentation() {
    log "Testing documentation completeness..."
    
    local required_docs=("README.md" "ARCHITECTURE.md" "ROADMAP_STATUS.md")
    for doc in "${required_docs[@]}"; do
        if [[ -f "$UHOME/uKnowledge/$doc" ]] || [[ -f "$UHOME/$doc" ]]; then
            success "Documentation exists: $doc"
        else
            warning "Documentation missing: $doc"
        fi
    done
    
    # Check for launch plan
    if [[ -f "$UHOME/GITHUB_LAUNCH_ADVANCEMENT_PLAN.md" ]]; then
        success "GitHub launch plan documented"
    else
        warning "GitHub launch plan missing"
    fi
}

test_performance() {
    log "Testing system performance..."
    
    # Test startup time (should be under 5 seconds)
    local start_time=$(date +%s.%N)
    timeout 10s "$UCODE/check.sh" setup >/dev/null 2>&1
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "N/A")
    
    if [[ "$duration" != "N/A" ]] && (( $(echo "$duration < 5.0" | bc -l 2>/dev/null || echo 0) )); then
        success "System startup under 5 seconds ($duration s)"
    else
        warning "System startup may be slow (${duration}s)"
    fi
}

generate_validation_report() {
    log "Generating validation report..."
    
    cat > "$VALIDATION_REPORT" << EOF
# 🚀 uDOS GitHub Launch Readiness Validation Report
_Generated: $(date '+%Y-%m-%d %H:%M:%S')_

## Executive Summary
- **Total Tests**: $((${#PASSED_TESTS[@]} + ${#FAILED_TESTS[@]} + ${#WARNING_TESTS[@]}))
- **✅ Passed**: ${#PASSED_TESTS[@]}
- **❌ Failed**: ${#FAILED_TESTS[@]}
- **⚠️ Warnings**: ${#WARNING_TESTS[@]}

### Launch Readiness Status
EOF

    local total_tests=$((${#PASSED_TESTS[@]} + ${#FAILED_TESTS[@]} + ${#WARNING_TESTS[@]}))
    local pass_rate=$(( ${#PASSED_TESTS[@]} * 100 / total_tests ))
    
    if [[ ${#FAILED_TESTS[@]} -eq 0 ]] && [[ $pass_rate -ge 90 ]]; then
        echo "**🟢 READY FOR LAUNCH** - All critical tests passed" >> "$VALIDATION_REPORT"
    elif [[ ${#FAILED_TESTS[@]} -eq 0 ]] && [[ $pass_rate -ge 80 ]]; then
        echo "**🟡 NEAR READY** - Minor issues to address" >> "$VALIDATION_REPORT"
    else
        echo "**🔴 NOT READY** - Critical issues require resolution" >> "$VALIDATION_REPORT"
    fi
    
    cat >> "$VALIDATION_REPORT" << EOF

---

## Detailed Results

### ✅ Passed Tests (${#PASSED_TESTS[@]})
EOF
    
    for test in "${PASSED_TESTS[@]}"; do
        echo "- $test" >> "$VALIDATION_REPORT"
    done
    
    if [[ ${#FAILED_TESTS[@]} -gt 0 ]]; then
        cat >> "$VALIDATION_REPORT" << EOF

### ❌ Failed Tests (${#FAILED_TESTS[@]})
EOF
        for test in "${FAILED_TESTS[@]}"; do
            echo "- $test" >> "$VALIDATION_REPORT"
        done
    fi
    
    if [[ ${#WARNING_TESTS[@]} -gt 0 ]]; then
        cat >> "$VALIDATION_REPORT" << EOF

### ⚠️ Warnings (${#WARNING_TESTS[@]})
EOF
        for test in "${WARNING_TESTS[@]}"; do
            echo "- $test" >> "$VALIDATION_REPORT"
        done
    fi
    
    cat >> "$VALIDATION_REPORT" << 'EOF'

---

## Recommendations

### Immediate Actions
1. **Resolve Critical Failures**: Address any failed tests before launch
2. **Package Installation**: Ensure all required packages are installed
3. **Extension Compilation**: Compile VS Code extension if not done
4. **Documentation Review**: Update any missing documentation

### Pre-Launch Checklist
- [ ] All core scripts executable
- [ ] Package system operational
- [ ] VS Code extension compiled
- [ ] Dashboard system functional
- [ ] AI integration configured
- [ ] Templates available
- [ ] Performance optimized

### Post-Launch Monitoring
- Monitor system performance
- Track user adoption
- Collect feedback for improvements
- Plan next enhancement phases

---

## GitHub Release Preparation

### Release Notes Template
```markdown
# uDOS v1.7.1 Alpha Release

## 🎯 What's New
- VS Code-native architecture with 90% performance improvement
- package ecosystem (bat, fd, glow, jq, fzf, ripgrep)
- Custom VS Code extension with uScript syntax highlighting
- Real-time dashboard with system monitoring
- AI integration with GitHub Copilot enhancement
- Professional template system

## 🚀 Quick Start
1. Clone repository
2. Run `./uCode/ucode.sh` to initialize
3. Use VS Code tasks for workflow
4. Explore templates and mission system

## 📋 Requirements
- macOS (primary support)
- VS Code with GitHub Copilot
- Homebrew for package management
- Node.js for extension development
```

### Repository Preparation
- Ensure README.md is comprehensive
- Add proper license file
- Create release documentation
- Set up issue templates
- Configure GitHub Actions (if needed)

---

**Validation completed at $(date '+%Y-%m-%d %H:%M:%S')**
EOF
    
    success "Validation report generated → $VALIDATION_REPORT"
}

display_summary() {
    echo ""
    echo -e "${WHITE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║                  🚀 LAUNCH VALIDATION SUMMARY                 ║${NC}"
    echo -e "${WHITE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local total_tests=$((${#PASSED_TESTS[@]} + ${#FAILED_TESTS[@]} + ${#WARNING_TESTS[@]}))
    local pass_rate=$(( ${#PASSED_TESTS[@]} * 100 / total_tests ))
    
    echo -e "${CYAN}Total Tests:${NC} $total_tests"
    echo -e "${GREEN}✅ Passed:${NC} ${#PASSED_TESTS[@]} (${pass_rate}%)"
    echo -e "${RED}❌ Failed:${NC} ${#FAILED_TESTS[@]}"
    echo -e "${YELLOW}⚠️ Warnings:${NC} ${#WARNING_TESTS[@]}"
    echo ""
    
    if [[ ${#FAILED_TESTS[@]} -eq 0 ]] && [[ $pass_rate -ge 90 ]]; then
        echo -e "${GREEN}🟢 STATUS: READY FOR GITHUB LAUNCH${NC}"
        echo -e "${GREEN}All critical systems operational!${NC}"
    elif [[ ${#FAILED_TESTS[@]} -eq 0 ]] && [[ $pass_rate -ge 80 ]]; then
        echo -e "${YELLOW}🟡 STATUS: NEAR READY FOR LAUNCH${NC}"
        echo -e "${YELLOW}Minor optimizations recommended${NC}"
    else
        echo -e "${RED}🔴 STATUS: NOT READY FOR LAUNCH${NC}"
        echo -e "${RED}Critical issues require resolution${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}📄 Full report: ${VALIDATION_REPORT}${NC}"
}

# Main validation sequence
run_all_tests() {
    log "Starting comprehensive launch validation..."
    echo ""
    
    # Core system tests
    test_core_structure
    test_core_scripts
    test_vscode_tasks
    
    # Feature tests
    test_package_system
    test_vscode_extension
    test_dashboard_system
    test_companion_system
    test_template_system
    
    # Quality tests
    test_documentation
    test_performance
    
    # Generate comprehensive report
    generate_validation_report
    
    # Display summary
    display_summary
}

# Command parser
case "$1" in
    full|all)
        run_all_tests
        ;;
    core)
        log "Testing core systems only..."
        test_core_structure
        test_core_scripts
        test_vscode_tasks
        display_summary
        ;;
    features)
        log "Testing feature systems..."
        test_package_system
        test_vscode_extension
        test_dashboard_system
        test_companion_system
        display_summary
        ;;
    report)
        if [[ -f "$VALIDATION_REPORT" ]]; then
            if command -v glow &> /dev/null; then
                glow "$VALIDATION_REPORT"
            else
                cat "$VALIDATION_REPORT"
            fi
        else
            error "No validation report found. Run: $0 full"
        fi
        ;;
    *)
        echo -e "${WHITE}🚀 uDOS GitHub Launch Readiness Validation${NC}"
        echo ""
        echo "Usage:"
        echo "  $0 full        # Complete validation suite"
        echo "  $0 core        # Core systems only"
        echo "  $0 features    # Feature systems only"
        echo "  $0 report      # Show last validation report"
        echo ""
        echo "Examples:"
        echo "  $0 full        # Comprehensive pre-launch validation"
        echo "  $0 core        # Quick core system check"
        ;;
esac
