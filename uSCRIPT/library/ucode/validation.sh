#!/bin/bash
# uDOS Validation Module v1.3
# System validation, health checks, and integrity verification

# Get uDOS paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
UCORE="$UDOS_ROOT/uCORE"
UMEMORY="$UDOS_ROOT/uMEMORY"
USCRIPT="$UDOS_ROOT/uSCRIPT"
SANDBOX="$UDOS_ROOT/sandbox"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Validation results
VALIDATION_RESULTS=()

# Add validation result
add_result() {
    local status="$1"
    local component="$2"
    local message="$3"
    
    VALIDATION_RESULTS+=("$status|$component|$message")
}

# Validate core directories
validate_directories() {
    echo -e "${BLUE}🏗️ Validating Directory Structure${NC}"
    
    local required_dirs=(
        "$UCORE:uCORE - Core system"
        "$UMEMORY:uMEMORY - Memory system"
        "$USCRIPT:uSCRIPT - Script system"
        "$SANDBOX:sandbox - User workspace"
        "$UCORE/code:uCORE/code - Core modules"
        "$USCRIPT/library:uSCRIPT/library - Script library"
        "$UMEMORY/templates:uMEMORY/templates - Templates"
    )
    
    for dir_info in "${required_dirs[@]}"; do
        IFS=':' read -r dir_path dir_desc <<< "$dir_info"
        
        if [[ -d "$dir_path" ]]; then
            add_result "OK" "Directory" "$dir_desc"
            echo -e "  ✅ ${GREEN}$dir_desc${NC}"
        else
            add_result "ERROR" "Directory" "$dir_desc (missing)"
            echo -e "  ❌ ${RED}$dir_desc (missing)${NC}"
        fi
    done
}

# Validate core files
validate_core_files() {
    echo -e "${BLUE}📁 Validating Core Files${NC}"
    
    local core_files=(
        "$UCORE/code/ucode-v13.sh:Modular Core"
        "$UCORE/code/user-auth.sh:Authentication Module"
        "$UCORE/code/session-logger.sh:Session Logger"
        "$UDOS_ROOT/ucode.sh:Legacy Core"
    )
    
    for file_info in "${core_files[@]}"; do
        IFS=':' read -r file_path file_desc <<< "$file_info"
        
        if [[ -f "$file_path" ]]; then
            if [[ -x "$file_path" ]]; then
                add_result "OK" "Core File" "$file_desc (executable)"
                echo -e "  ✅ ${GREEN}$file_desc (executable)${NC}"
            else
                add_result "WARN" "Core File" "$file_desc (not executable)"
                echo -e "  ⚠️  ${YELLOW}$file_desc (not executable)${NC}"
            fi
        else
            add_result "ERROR" "Core File" "$file_desc (missing)"
            echo -e "  ❌ ${RED}$file_desc (missing)${NC}"
        fi
    done
}

# Validate uSCRIPT modules
validate_modules() {
    echo -e "${BLUE}📦 Validating uSCRIPT Modules${NC}"
    
    local required_modules=(
        "help:Help System"
        "status:Status Monitor"
        "display:Display Manager"
        "user:User Management"
        "session:Session Manager"
        "memory:Memory System"
        "dashboard:System Dashboard"
        "layout:Layout Manager"
        "ascii:ASCII Graphics"
        "input:Input System"
    )
    
    for module_info in "${required_modules[@]}"; do
        IFS=':' read -r module_name module_desc <<< "$module_info"
        local module_path="$USCRIPT/library/ucode/${module_name}.sh"
        
        if [[ -f "$module_path" ]]; then
            if [[ -x "$module_path" ]]; then
                add_result "OK" "Module" "$module_desc"
                echo -e "  ✅ ${GREEN}$module_desc${NC}"
            else
                add_result "WARN" "Module" "$module_desc (not executable)"
                echo -e "  ⚠️  ${YELLOW}$module_desc (not executable)${NC}"
            fi
        else
            add_result "ERROR" "Module" "$module_desc (missing)"
            echo -e "  ❌ ${RED}$module_desc (missing)${NC}"
        fi
    done
}

# Validate authentication system
validate_authentication() {
    echo -e "${BLUE}🔐 Validating Authentication System${NC}"
    
    if [[ -f "$SANDBOX/user.md" ]]; then
        add_result "OK" "Authentication" "User data exists"
        echo -e "  ✅ ${GREEN}User data exists${NC}"
        
        # Check password protection
        if grep -q "^Password Hash:" "$SANDBOX/user.md" 2>/dev/null; then
            add_result "OK" "Authentication" "Password protection enabled"
            echo -e "  ✅ ${GREEN}Password protection enabled${NC}"
        else
            add_result "WARN" "Authentication" "No password protection"
            echo -e "  ⚠️  ${YELLOW}No password protection${NC}"
        fi
        
        # Check file permissions
        local perms=$(ls -la "$SANDBOX/user.md" | awk '{print $1}')
        if [[ "$perms" =~ ^-rw------- ]]; then
            add_result "OK" "Authentication" "Secure file permissions"
            echo -e "  ✅ ${GREEN}Secure file permissions${NC}"
        else
            add_result "WARN" "Authentication" "File permissions could be more secure"
            echo -e "  ⚠️  ${YELLOW}File permissions: $perms${NC}"
        fi
    else
        add_result "INFO" "Authentication" "No user account configured"
        echo -e "  ℹ️  ${CYAN}No user account configured${NC}"
    fi
}

# Validate memory system
validate_memory_system() {
    echo -e "${BLUE}🧠 Validating Memory System${NC}"
    
    # Check for session logs
    local session_count=$(find "$UMEMORY" -name "*Session.md" 2>/dev/null | wc -l)
    if [[ $session_count -gt 0 ]]; then
        add_result "OK" "Memory" "$session_count session logs found"
        echo -e "  ✅ ${GREEN}$session_count session logs found${NC}"
    else
        add_result "INFO" "Memory" "No session logs yet"
        echo -e "  ℹ️  ${CYAN}No session logs yet${NC}"
    fi
    
    # Check templates
    if [[ -d "$UMEMORY/templates" ]]; then
        local template_count=$(find "$UMEMORY/templates" -name "*.md" 2>/dev/null | wc -l)
        add_result "OK" "Memory" "$template_count templates available"
        echo -e "  ✅ ${GREEN}$template_count templates available${NC}"
    else
        add_result "WARN" "Memory" "Templates directory missing"
        echo -e "  ⚠️  ${YELLOW}Templates directory missing${NC}"
    fi
    
    # Check storage usage
    local storage_size=$(du -sh "$UMEMORY" 2>/dev/null | cut -f1)
    add_result "INFO" "Memory" "Storage usage: $storage_size"
    echo -e "  ℹ️  ${CYAN}Storage usage: $storage_size${NC}"
}

# Validate system performance
validate_performance() {
    echo -e "${BLUE}⚡ Validating System Performance${NC}"
    
    # Disk space check
    local disk_usage=$(df "$UDOS_ROOT" | tail -1 | awk '{print $5}' | tr -d '%')
    if [[ $disk_usage -lt 80 ]]; then
        add_result "OK" "Performance" "Disk usage: ${disk_usage}%"
        echo -e "  ✅ ${GREEN}Disk usage: ${disk_usage}%${NC}"
    elif [[ $disk_usage -lt 90 ]]; then
        add_result "WARN" "Performance" "Disk usage: ${disk_usage}%"
        echo -e "  ⚠️  ${YELLOW}Disk usage: ${disk_usage}%${NC}"
    else
        add_result "ERROR" "Performance" "Disk usage critical: ${disk_usage}%"
        echo -e "  ❌ ${RED}Disk usage critical: ${disk_usage}%${NC}"
    fi
    
    # Memory check (if available)
    if command -v free >/dev/null 2>&1; then
        local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
        if [[ $mem_usage -lt 80 ]]; then
            add_result "OK" "Performance" "Memory usage: ${mem_usage}%"
            echo -e "  ✅ ${GREEN}Memory usage: ${mem_usage}%${NC}"
        else
            add_result "WARN" "Performance" "Memory usage high: ${mem_usage}%"
            echo -e "  ⚠️  ${YELLOW}Memory usage high: ${mem_usage}%${NC}"
        fi
    fi
    
    # Process check
    local ucode_processes=$(pgrep -f "ucode" | wc -l)
    add_result "INFO" "Performance" "$ucode_processes ucode processes"
    echo -e "  ℹ️  ${CYAN}$ucode_processes ucode processes${NC}"
}

# Validate terminal environment
validate_terminal() {
    echo -e "${BLUE}🖥️ Validating Terminal Environment${NC}"
    
    local cols=$(tput cols 2>/dev/null || echo "unknown")
    local lines=$(tput lines 2>/dev/null || echo "unknown")
    
    if [[ "$cols" != "unknown" && "$lines" != "unknown" ]]; then
        add_result "OK" "Terminal" "Size: ${cols}x${lines}"
        echo -e "  ✅ ${GREEN}Terminal size: ${cols}x${lines}${NC}"
        
        # Check if size is optimal
        if [[ $cols -ge 120 && $lines -ge 30 ]]; then
            add_result "OK" "Terminal" "Size is optimal for uDOS"
            echo -e "  ✅ ${GREEN}Size is optimal for uDOS${NC}"
        elif [[ $cols -ge 80 && $lines -ge 24 ]]; then
            add_result "WARN" "Terminal" "Size is adequate but could be larger"
            echo -e "  ⚠️  ${YELLOW}Size is adequate but could be larger${NC}"
        else
            add_result "WARN" "Terminal" "Size may be too small for optimal experience"
            echo -e "  ⚠️  ${YELLOW}Size may be too small for optimal experience${NC}"
        fi
    else
        add_result "WARN" "Terminal" "Cannot determine terminal size"
        echo -e "  ⚠️  ${YELLOW}Cannot determine terminal size${NC}"
    fi
    
    # Check color support
    if [[ $TERM =~ color ]]; then
        add_result "OK" "Terminal" "Color support detected"
        echo -e "  ✅ ${GREEN}Color support detected${NC}"
    else
        add_result "WARN" "Terminal" "Limited color support"
        echo -e "  ⚠️  ${YELLOW}Limited color support${NC}"
    fi
}

# Generate validation report
generate_report() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                   VALIDATION REPORT                  ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local ok_count=0
    local warn_count=0
    local error_count=0
    local info_count=0
    
    for result in "${VALIDATION_RESULTS[@]}"; do
        IFS='|' read -r status component message <<< "$result"
        case "$status" in
            "OK") ((ok_count++)) ;;
            "WARN") ((warn_count++)) ;;
            "ERROR") ((error_count++)) ;;
            "INFO") ((info_count++)) ;;
        esac
    done
    
    echo -e "${GREEN}✅ OK: $ok_count${NC}"
    echo -e "${YELLOW}⚠️  WARNINGS: $warn_count${NC}"
    echo -e "${RED}❌ ERRORS: $error_count${NC}"
    echo -e "${CYAN}ℹ️  INFO: $info_count${NC}"
    echo ""
    
    # Overall status
    if [[ $error_count -eq 0 ]]; then
        if [[ $warn_count -eq 0 ]]; then
            echo -e "${GREEN}🎉 System validation: EXCELLENT${NC}"
        else
            echo -e "${YELLOW}✨ System validation: GOOD (minor issues)${NC}"
        fi
    else
        echo -e "${RED}🔧 System validation: NEEDS ATTENTION${NC}"
    fi
}

# Quick validation
quick_validation() {
    echo -e "${BLUE}⚡ Quick System Validation${NC}"
    echo ""
    
    # Core checks only
    local checks=(
        "uCORE/code/ucode-v13.sh:Modular Core"
        "uSCRIPT/library/ucode:Module Directory"
        "uMEMORY:Memory System"
        "sandbox:User Workspace"
    )
    
    for check in "${checks[@]}"; do
        IFS=':' read -r path desc <<< "$check"
        local full_path="$UDOS_ROOT/$path"
        
        if [[ -e "$full_path" ]]; then
            echo -e "  ✅ ${GREEN}$desc${NC}"
        else
            echo -e "  ❌ ${RED}$desc (missing)${NC}"
        fi
    done
}

# Fix common issues
fix_permissions() {
    echo -e "${BLUE}🔧 Fixing File Permissions${NC}"
    
    # Make core files executable
    chmod +x "$UCORE/code"/*.sh 2>/dev/null
    echo -e "  ✅ ${GREEN}Core modules made executable${NC}"
    
    # Make uSCRIPT modules executable
    chmod +x "$USCRIPT/library/ucode"/*.sh 2>/dev/null
    echo -e "  ✅ ${GREEN}uSCRIPT modules made executable${NC}"
    
    # Secure user data
    if [[ -f "$SANDBOX/user.md" ]]; then
        chmod 600 "$SANDBOX/user.md"
        echo -e "  ✅ ${GREEN}User data secured${NC}"
    fi
}

# Main validation function
validation_main() {
    local action="${1:-full}"
    
    # Clear results
    VALIDATION_RESULTS=()
    
    case "$action" in
        "full"|"complete")
            validate_directories
            echo ""
            validate_core_files
            echo ""
            validate_modules
            echo ""
            validate_authentication
            echo ""
            validate_memory_system
            echo ""
            validate_performance
            echo ""
            validate_terminal
            generate_report
            ;;
        "quick")
            quick_validation
            ;;
        "directories"|"dirs")
            validate_directories
            ;;
        "files")
            validate_core_files
            ;;
        "modules")
            validate_modules
            ;;
        "auth")
            validate_authentication
            ;;
        "memory")
            validate_memory_system
            ;;
        "performance"|"perf")
            validate_performance
            ;;
        "terminal")
            validate_terminal
            ;;
        "fix")
            fix_permissions
            ;;
        *)
            echo "Validation module - Available actions: full, quick, directories, files, modules, auth, memory, performance, terminal, fix"
            ;;
    esac
}

# Export main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    validation_main "$@"
fi
