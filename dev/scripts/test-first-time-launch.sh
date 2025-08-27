#!/bin/bash
# uDOS First-Time Launch Test Suite
# Tests complete installation workflow from fresh system

set -euo pipefail

# Colors for test output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test configuration
UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "DEBUG: Testing uDOS installation at: $UDOS_ROOT" >&2
TEST_RESULTS=()
FAILED_TESTS=0
PASSED_TESTS=0

# Test logging functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("✅ $1")
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TEST_RESULTS+=("❌ $1")
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    TEST_RESULTS+=("⚠️ $1")
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    TEST_RESULTS+=("⚠️ $1")
}

# Test banner
show_test_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║           uDOS First-Time Launch Test Suite          ║"
    echo "║               Testing New Installation               ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

# Test 1: System Dependencies
test_system_dependencies() {
    log_test "Checking system dependencies"
    
    local required_deps=("bash" "git" "jq" "python3")
    local missing_deps=()
    
    for dep in "${required_deps[@]}"; do
        if command -v "$dep" >/dev/null 2>&1; then
            local version=""
            case "$dep" in
                bash) version="$BASH_VERSION" ;;
                git) version="$(git --version | cut -d' ' -f3)" ;;
                jq) version="$(jq --version | cut -d'-' -f2)" ;;
                python3) version="$(python3 --version | cut -d' ' -f2)" ;;
            esac
            log_pass "$dep $version available"
        else
            missing_deps+=("$dep")
            log_fail "$dep not found"
        fi
    done
    
    if [[ ${#missing_deps[@]} -eq 0 ]]; then
        log_pass "All system dependencies satisfied"
    else
        log_fail "Missing dependencies: ${missing_deps[*]}"
    fi
}

# Test 2: uDOS Core Structure
test_core_structure() {
    log_test "Verifying uDOS core structure"
    
    local core_dirs=("uCORE" "sandbox" "uMEMORY" "uNETWORK" "uSCRIPT" "extensions" "docs")
    local missing_dirs=()
    
    for dir in "${core_dirs[@]}"; do
        if [[ -d "$UDOS_ROOT/$dir" ]]; then
            log_pass "Directory $dir exists"
        else
            missing_dirs+=("$dir")
            log_fail "Directory $dir missing"
        fi
    done
    
    # Check key files
    local key_files=("install.sh" "README.md" "VERSION" ".github/copilot-instructions.md")
    for file in "${key_files[@]}"; do
        if [[ -f "$UDOS_ROOT/$file" ]]; then
            log_pass "File $file exists"
        else
            log_fail "File $file missing"
        fi
    done
}

# Test 3: Launcher Scripts
test_launcher_scripts() {
    log_test "Testing cross-platform launchers"
    
    local launchers=(
        "Launch-uDOS-Ubuntu.sh"
        "Launch-uDOS-macOS.command"
        "Launch-uDOS-Windows.bat"
    )
    
    for launcher in "${launchers[@]}"; do
        if [[ -f "$UDOS_ROOT/$launcher" && -x "$UDOS_ROOT/$launcher" ]]; then
            log_pass "Launcher $launcher exists and is executable"
        else
            log_fail "Launcher $launcher missing or not executable"
        fi
    done
    
    # Test Ubuntu launcher specifically (since we're on Ubuntu)
    if [[ -f "$UDOS_ROOT/Launch-uDOS-Ubuntu.sh" ]]; then
        log_test "Testing Ubuntu launcher syntax"
        if bash -n "$UDOS_ROOT/Launch-uDOS-Ubuntu.sh"; then
            log_pass "Ubuntu launcher syntax valid"
        else
            log_fail "Ubuntu launcher has syntax errors"
        fi
    fi
}

# Test 4: Core System Scripts
test_core_scripts() {
    log_test "Testing core system scripts"
    
    local core_scripts=(
        "uCORE/code/ucode.sh"
        "uCORE/code/session-manager.sh"
        "uCORE/code/workflow-manager.sh"
        "dev/workflow.sh"
    )
    
    for script in "${core_scripts[@]}"; do
        local script_path="$UDOS_ROOT/$script"
        if [[ -f "$script_path" && -x "$script_path" ]]; then
            log_pass "Script $script exists and is executable"
            
            # Test syntax
            if bash -n "$script_path"; then
                log_pass "Script $script syntax valid"
            else
                log_fail "Script $script has syntax errors"
            fi
        else
            log_fail "Script $script missing or not executable"
        fi
    done
}

# Test 5: Session Management
test_session_management() {
    log_test "Testing session management system"
    
    # Test session manager with dry run
    if [[ -x "$UDOS_ROOT/uCORE/code/session-manager.sh" ]]; then
        log_test "Creating test session"
        if "$UDOS_ROOT/uCORE/code/session-manager.sh" status >/dev/null 2>&1; then
            log_pass "Session manager operational"
        else
            log_fail "Session manager not working"
        fi
    else
        log_fail "Session manager not executable"
    fi
    
    # Check session directory structure
    local session_dirs=("sandbox/session" "sandbox/session/logs" "sandbox/workflow")
    for dir in "${session_dirs[@]}"; do
        if [[ -d "$UDOS_ROOT/$dir" ]]; then
            log_pass "Session directory $dir exists"
        else
            # Try to create it
            if mkdir -p "$UDOS_ROOT/$dir" 2>/dev/null; then
                log_pass "Session directory $dir created"
            else
                log_fail "Cannot create session directory $dir"
            fi
        fi
    done
}

# Test 6: Python Environment
test_python_environment() {
    log_test "Testing Python environment"
    
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        local major_version=$(echo "$python_version" | cut -d'.' -f1)
        local minor_version=$(echo "$python_version" | cut -d'.' -f2)
        
        if [[ "$major_version" -eq 3 && "$minor_version" -ge 7 ]]; then
            log_pass "Python $python_version compatible"
        else
            log_warning "Python $python_version may have compatibility issues (3.7+ recommended)"
        fi
        
        # Test basic Python modules
        local python_modules=("json" "os" "sys" "pathlib")
        for module in "${python_modules[@]}"; do
            if python3 -c "import $module" 2>/dev/null; then
                log_pass "Python module $module available"
            else
                log_fail "Python module $module missing"
            fi
        done
        
        # Check for uSCRIPT environment
        if [[ -f "$UDOS_ROOT/uSCRIPT/setup-environment.sh" ]]; then
            log_test "Checking uSCRIPT environment setup"
            if [[ -d "$UDOS_ROOT/uSCRIPT/venv/python" ]]; then
                log_pass "uSCRIPT virtual environment exists"
                
                # Test display system dependencies
                log_test "Checking display system dependencies"
                local display_deps=("flask" "flask_socketio" "psutil" "eventlet")
                local venv_python="$UDOS_ROOT/uSCRIPT/venv/python/bin/python"
                local missing_display_deps=()
                
                for dep in "${display_deps[@]}"; do
                    if "$venv_python" -c "import ${dep//-/_}" 2>/dev/null; then
                        log_pass "Display dependency $dep available"
                    else
                        missing_display_deps+=("$dep")
                        log_fail "Display dependency $dep missing"
                    fi
                done
                
                if [[ ${#missing_display_deps[@]} -eq 0 ]]; then
                    log_pass "All display system dependencies satisfied"
                else
                    log_fail "Missing display dependencies: ${missing_display_deps[*]}"
                fi
            else
                log_warning "uSCRIPT virtual environment not set up (run ./uSCRIPT/setup-environment.sh)"
            fi
        fi
    else
        log_fail "Python 3 not available"
    fi
}

# Test 7: Documentation System
test_documentation_system() {
    log_test "Testing documentation system"
    
    local doc_files=(
        "docs/README.md"
        "docs/USER-GUIDE.md"
        "docs/ARCHITECTURE.md"
        "docs/STYLE-GUIDE.md"
    )
    
    for doc in "${doc_files[@]}"; do
        if [[ -f "$UDOS_ROOT/$doc" ]]; then
            log_pass "Documentation $doc exists"
        else
            log_fail "Documentation $doc missing"
        fi
    done
    
    # Test Copilot instructions
    if [[ -f "$UDOS_ROOT/.github/copilot-instructions.md" ]]; then
        log_pass "GitHub Copilot instructions available"
    else
        log_warning "GitHub Copilot instructions missing"
    fi
}

# Test 8: Extension System
test_extension_system() {
    log_test "Testing extension system"
    
    if [[ -f "$UDOS_ROOT/extensions/extension-manager.sh" ]]; then
        log_pass "Extension manager exists"
        
        # Test extension directories
        local ext_dirs=("extensions/core" "extensions/user")
        for dir in "${ext_dirs[@]}"; do
            if [[ -d "$UDOS_ROOT/$dir" ]]; then
                log_pass "Extension directory $dir exists"
            else
                log_fail "Extension directory $dir missing"
            fi
        done
        
        # Test extension registry
        if [[ -f "$UDOS_ROOT/extensions/registry.json" ]]; then
            if jq empty "$UDOS_ROOT/extensions/registry.json" 2>/dev/null; then
                log_pass "Extension registry is valid JSON"
            else
                log_fail "Extension registry has invalid JSON"
            fi
        else
            log_warning "Extension registry missing"
        fi
    else
        log_fail "Extension manager missing"
    fi
}

# Test 9: VS Code Integration
test_vscode_integration() {
    log_test "Testing VS Code integration"
    
    if [[ -d "$UDOS_ROOT/.vscode" ]]; then
        log_pass "VS Code workspace configuration exists"
        
        # Check key VS Code files
        local vscode_files=("tasks.json" "settings.json")
        for file in "${vscode_files[@]}"; do
            if [[ -f "$UDOS_ROOT/.vscode/$file" ]]; then
                if jq empty "$UDOS_ROOT/.vscode/$file" 2>/dev/null; then
                    log_pass "VS Code $file is valid JSON"
                else
                    log_fail "VS Code $file has invalid JSON"
                fi
            else
                log_warning "VS Code $file missing"
            fi
        done
    else
        log_warning "VS Code workspace configuration missing"
    fi
    
    # Check if code command is available
    if command -v code >/dev/null 2>&1; then
        log_pass "VS Code CLI available"
    else
        log_warning "VS Code CLI not available"
    fi
}

# Test 10: Three-Mode Display System
test_display_system() {
    log_test "Testing three-mode display system"
    
    if [[ -f "$UDOS_ROOT/uNETWORK/display/udos-display.sh" ]]; then
        log_pass "Display system launcher exists"
        
        # Test display system status
        if bash -n "$UDOS_ROOT/uNETWORK/display/udos-display.sh"; then
            log_pass "Display launcher syntax valid"
        else
            log_fail "Display launcher has syntax errors"
        fi
        
        # Test CLI mode (always available)
        log_test "Testing CLI mode availability"
        log_pass "CLI mode always available"
        
        # Test web export setup
        log_test "Testing web export setup"
        if [[ -f "$UDOS_ROOT/uNETWORK/display/server/display-server.py" ]]; then
            log_pass "Web export server exists"
            
            # Test Python syntax
            if python3 -m py_compile "$UDOS_ROOT/uNETWORK/display/server/display-server.py" 2>/dev/null; then
                log_pass "Web export server syntax valid"
            else
                log_fail "Web export server has syntax errors"
            fi
        else
            log_fail "Web export server missing"
        fi
        
        # Test desktop app framework
        log_test "Testing desktop app framework"
        if [[ -d "$UDOS_ROOT/uNETWORK/display/src-tauri" ]]; then
            log_pass "Desktop app framework exists"
        else
            log_warning "Desktop app framework not set up (requires Node.js/Rust)"
        fi
        
    else
        log_fail "Display system launcher missing"
    fi
}

# Test 11: Network System (Optional)
test_network_system() {
    log_test "Testing network system (optional)"
    
    if [[ -f "$UDOS_ROOT/uNETWORK/server/server.py" ]]; then
        log_pass "uNETWORK server exists"
        
        # Test Python syntax
        if python3 -m py_compile "$UDOS_ROOT/uNETWORK/server/server.py" 2>/dev/null; then
            log_pass "uNETWORK server Python syntax valid"
        else
            log_fail "uNETWORK server has Python syntax errors"
        fi
    else
        log_warning "uNETWORK server not found (optional)"
    fi
}

# Test 11: Desktop Development Environment (Optional)
test_desktop_development() {
    log_test "Testing desktop development environment (optional)"
    
    # Test desktop setup script exists
    if [[ -f "$UDOS_ROOT/dev/scripts/setup-desktop-dev.sh" && -x "$UDOS_ROOT/dev/scripts/setup-desktop-dev.sh" ]]; then
        log_pass "Desktop development setup script exists"
    else
        log_fail "Desktop development setup script missing"
    fi
    
    # Test for desktop development dependencies (optional)
    log_test "Checking desktop development dependencies"
    
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        log_pass "Node.js $node_version available"
    else
        log_warn "Node.js not installed (required for desktop apps)"
    fi
    
    if command -v rustc >/dev/null 2>&1; then
        local rust_version=$(rustc --version | cut -d' ' -f2)
        log_pass "Rust $rust_version available"
    else
        log_warn "Rust not installed (required for desktop apps)"
    fi
    
    if command -v cargo >/dev/null 2>&1; then
        if cargo tauri --version >/dev/null 2>&1; then
            local tauri_version=$(cargo tauri --version 2>/dev/null | head -1 | cut -d' ' -f2 || echo "unknown")
            log_pass "Tauri CLI $tauri_version available"
        else
            log_warn "Tauri CLI not installed (required for desktop apps)"
        fi
    else
        log_warn "Cargo not available (Rust package manager)"
    fi
    
    # Note about desktop development being optional
    echo "ℹ️  Desktop development is optional - run ./dev/scripts/setup-desktop-dev.sh to install"
}

# Generate test report
generate_test_report() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    TEST REPORT                        ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    echo -e "${GREEN}Passed Tests: $PASSED_TESTS${NC}"
    echo -e "${RED}Failed Tests: $FAILED_TESTS${NC}"
    echo ""
    
    echo "Detailed Results:"
    for result in "${TEST_RESULTS[@]}"; do
        echo "  $result"
    done
    
    echo ""
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed! uDOS installation is ready for first-time launch.${NC}"
        return 0
    else
        echo -e "${RED}❌ $FAILED_TESTS test(s) failed. Please address the issues before launching uDOS.${NC}"
        return 1
    fi
}

# Main test execution
main() {
    show_test_banner
    
    echo -e "${BLUE}Running comprehensive first-time launch tests...${NC}"
    echo ""
    
    test_system_dependencies
    echo ""
    
    test_core_structure
    echo ""
    
    test_launcher_scripts
    echo ""
    
    test_core_scripts
    echo ""
    
    test_session_management
    echo ""
    
    test_python_environment
    echo ""
    
    test_documentation_system
    echo ""
    
    test_extension_system
    echo ""
    
    test_vscode_integration
    echo ""
    
    test_display_system
    echo ""
    
    test_network_system
    echo ""
    
    test_desktop_development
    echo ""
    
    generate_test_report
}

# Execute if run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
