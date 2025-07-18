#!/bin/bash
# uDOS v1.0 Installation Validation Script
# Comprehensive testing of uDOS installation and setup

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
log_success() { echo -e "${GREEN}✅ $1${NC}" | tee -a "$VALIDATION_LOG"; ((PASSED_CHECKS++)); }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$VALIDATION_LOG"; ((WARNING_CHECKS++)); }
log_error() { echo -e "${RED}❌ $1${NC}" | tee -a "$VALIDATION_LOG"; ((FAILED_CHECKS++)); }
log_bold() { echo -e "${BOLD}$1${NC}" | tee -a "$VALIDATION_LOG"; }

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                🔍 uDOS v1.0 VALIDATION SUITE                    ║"
    echo "║              Installation & Setup Verification                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_item() {
    ((TOTAL_CHECKS++))
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
            add_result "fail" "Missing core directory: ${dir}/"
        fi
    done
}

# Check critical system files
check_system_files() {
    echo "📂 Checking critical system files..."
    
    local required_files=(
        "uCode/ucode.sh:Main uDOS shell script"
        "uCode/init-user.sh:User initialization system" 
        "uCode/user-roles.sh:User role management"
        "uTemplate/uc-template.md:Core template system"
        "uKnowledge/ARCHITECTURE.md:System architecture docs"
        "uScript/README.md:uScript documentation"
        ".gitignore:Git ignore configuration"
        "README.md:Project documentation"
    )
    
    for entry in "${required_files[@]}"; do
        local file="${entry%%:*}"
        local desc="${entry#*:}"
        
        if [[ -f "${UHOME}/${file}" ]]; then
            add_result "pass" "System file exists: ${file} (${desc})"
        else
            add_result "fail" "Missing system file: ${file} (${desc})"
        fi
    done
}

# Check uMemory structure and privacy compliance
check_umemory_structure() {
    echo "🔐 Checking uMemory structure and privacy compliance..."
    
    if [[ ! -d "$UMEM" ]]; then
        add_result "fail" "uMemory directory missing - run user setup"
        return
    fi
    
    local required_umem_dirs=(
        "user:User identity and preferences"
        "logs:System and activity logs"
        "state:Application state management"
        "moves:User action history"
        "missions:Task and project management"
        "milestones:Achievement tracking"
        "sandbox:Safe testing environment"
        "templates:User template storage"
        "users:User role and permission system"
    )
    
    for entry in "${required_umem_dirs[@]}"; do
        local dir="${entry%%:*}"
        local desc="${entry#*:}"
        
        if [[ -d "${UMEM}/${dir}" ]]; then
            add_result "pass" "uMemory directory exists: ${dir}/ (${desc})"
        else
            add_result "warn" "uMemory directory missing: ${dir}/ (${desc})"
        fi
    done
    
    # Check gitignore compliance
    if grep -q "^uMemory/" "${UHOME}/.gitignore" 2>/dev/null; then
        add_result "pass" "uMemory properly excluded from git (privacy protected)"
    else
        add_result "fail" "uMemory not in .gitignore - privacy at risk!"
    fi
}

# Check user identity and single-user compliance
check_user_system() {
    echo "👤 Checking user system and single-user compliance..."
    
    local user_identity="${UMEM}/user/identity.md"
    if [[ -f "$user_identity" ]]; then
        local username
        username=$(grep "^\*\*Username\*\*:" "$user_identity" 2>/dev/null | cut -d' ' -f2)
        if [[ -n "$username" ]]; then
            add_result "pass" "User identity found: $username"
            
            # Check user role profile
            if [[ -f "${UMEM}/users/profiles/${username}.md" ]]; then
                local role
                role=$(grep "^\*\*Role\*\*:" "${UMEM}/users/profiles/${username}.md" 2>/dev/null | cut -d' ' -f2)
                add_result "pass" "User role profile exists: $username ($role)"
            else
                add_result "warn" "User role profile missing for: $username"
            fi
            
            # Check single-user compliance
            local user_count
            user_count=$(find "${UMEM}/users/profiles" -name "*.md" 2>/dev/null | wc -l)
            if [[ $user_count -eq 1 ]]; then
                add_result "pass" "Single-user installation (uDOS ethos compliant)"
            elif [[ $user_count -gt 1 ]]; then
                add_result "warn" "Multiple user profiles detected ($user_count) - consider separate installations"
            else
                add_result "fail" "No user profiles found"
            fi
        else
            add_result "fail" "User identity file corrupted - username not found"
        fi
    else
        add_result "fail" "User identity not found - run: ./uCode/init-user.sh"
    fi
}

# Check VS Code integration
check_vscode_integration() {
    echo "🔷 Checking VS Code integration..."
    
    if [[ -d "${UHOME}/.vscode" ]]; then
        add_result "pass" "VS Code workspace configuration exists"
        
        if [[ -f "${UHOME}/.vscode/tasks.json" ]]; then
            local task_count
            task_count=$(grep -c '"label":' "${UHOME}/.vscode/tasks.json" 2>/dev/null || echo 0)
            add_result "pass" "VS Code tasks configured ($task_count tasks available)"
        else
            add_result "warn" "VS Code tasks not configured"
        fi
    else
        add_result "warn" "VS Code workspace not initialized"
    fi
}

# Check permissions and file ownership
check_permissions() {
    echo "🛡️  Checking file permissions and ownership..."
    
    # Check if uCode scripts are executable
    local scripts=(
        "uCode/ucode.sh"
        "uCode/init-user.sh"
        "uCode/user-roles.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "${UHOME}/${script}" ]]; then
            if [[ -x "${UHOME}/${script}" ]]; then
                add_result "pass" "Script executable: ${script}"
            else
                add_result "warn" "Script not executable: ${script} (run: chmod +x ${script})"
            fi
        fi
    done
    
    # Check uMemory privacy
    if [[ -d "$UMEM" ]]; then
        local umem_perms
        umem_perms=$(stat -f "%A" "$UMEM" 2>/dev/null || stat -c "%a" "$UMEM" 2>/dev/null || echo "unknown")
        if [[ "$umem_perms" == "700" ]] || [[ "$umem_perms" == "755" ]]; then
            add_result "pass" "uMemory permissions secure ($umem_perms)"
        else
            add_result "warn" "uMemory permissions may not be optimal ($umem_perms)"
        fi
    fi
}

# Check system compatibility
check_system_compatibility() {
    echo "💻 Checking system compatibility..."
    
    # Check shell
    if [[ "$SHELL" == *"bash"* ]] || [[ "$SHELL" == *"zsh"* ]]; then
        add_result "pass" "Compatible shell detected: $SHELL"
    else
        add_result "warn" "Untested shell: $SHELL (uDOS optimized for bash/zsh)"
    fi
    
    # Check macOS specific features
    if [[ "$(uname)" == "Darwin" ]]; then
        add_result "pass" "macOS detected - full feature support available"
        
        if [[ -d "${UHOME}/launcher" ]]; then
            add_result "pass" "macOS launcher system available"
        fi
    else
        add_result "pass" "Non-macOS system - core features available"
    fi
}

# Generate validation report
generate_report() {
    echo
    bold "📋 uDOS v1.0 Installation Validation Report"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📅 Generated: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "🏠 Installation: $UHOME"
    echo
    
    # Show all results
    for result in "${validation_results[@]}"; do
        echo "$result"
    done
    
    echo
    echo "📊 Summary:"
    echo "   Total checks: ${#validation_results[@]}"
    echo "   Warnings: ${#warnings[@]}"
    echo "   Errors: ${#errors[@]}"
    
    if [[ ${#errors[@]} -eq 0 ]]; then
        if [[ ${#warnings[@]} -eq 0 ]]; then
            green "🎉 Perfect installation! uDOS v1.0 is ready for use."
        else
            yellow "⚠️  Installation functional with minor issues."
            echo "   Consider addressing warnings for optimal experience."
        fi
    else
        red "❌ Installation has critical issues that need attention."
        echo
        echo "🔧 Critical issues to resolve:"
        for error in "${errors[@]}"; do
            echo "   • $error"
        done
    fi
    
    # Core ethos validation
    echo
    blue "🧭 uDOS Core Ethos Validation:"
    if grep -q "Single-user installation" <<< "${validation_results[*]}"; then
        echo "   ✅ One installation per user: Compliant"
    else
        echo "   ❌ One installation per user: Non-compliant"
    fi
    
    if grep -q "privacy protected" <<< "${validation_results[*]}"; then
        echo "   ✅ Privacy-first architecture: Compliant"  
    else
        echo "   ❌ Privacy-first architecture: Non-compliant"
    fi
    
    if grep -q "User identity found" <<< "${validation_results[*]}"; then
        echo "   ✅ Local data sovereignty: Compliant"
    else
        echo "   ❌ Local data sovereignty: Non-compliant"
    fi
}

# Main validation routine
main() {
    local mode="${1:-full}"
    
    case "$mode" in
        "quick"|"q")
            check_core_structure
            check_user_system
            ;;
        "privacy"|"p") 
            check_umemory_structure
            check_user_system
            check_permissions
            ;;
        "full"|"f"|*)
            check_core_structure
            check_system_files
            check_umemory_structure
            check_user_system
            check_vscode_integration
            check_permissions
            check_system_compatibility
            ;;
    esac
    
    generate_report
    
    # Exit with appropriate code
    if [[ ${#errors[@]} -gt 0 ]]; then
        exit 1
    elif [[ ${#warnings[@]} -gt 0 ]]; then
        exit 2
    else
        exit 0
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "🔍 uDOS v1.0 Installation Validation"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    main "$@"
fi
