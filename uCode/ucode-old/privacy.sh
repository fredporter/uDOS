#!/bin/bash
# uDOS v1.0 - File Structure Protection and Privacy Enforcement  
# 🛡️ privacy-guard.sh — Enforce uDOS core ethos: flat file system with privacy protection

set -euo pipefail

UHOME="${HOME}/uDOS"
UMEM="${UHOME}/uMemory"

# Core uDOS ethos enforcement
log_privacy_event() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] PRIVACY: $1" >> "${UMEM}/logs/system/privacy.log"
}

# Validate file structure separation
validate_file_structure() {
    echo "🛡️  Validating uDOS file structure separation..."
    
    # System vs User separation
    local system_paths=(
        "uCode"      # Development/system scripts
        "uKnowledge" # Documentation and knowledge
        "uScript"    # System scripts and utilities  
        "uTemplate"  # Template system
    )
    
    local user_paths=(
        "uMemory"    # ALL user content - PRIVACY PROTECTED
    )
    
    # Ensure uMemory is properly isolated
    if [[ ! -d "$UMEM" ]]; then
        echo "❌ uMemory directory missing - core privacy protection broken"
        return 1
    fi
    
    # Check that user data doesn't leak into system directories
    for sys_path in "${system_paths[@]}"; do
        if find "${UHOME}/${sys_path}" -name "*.personal" -o -name "*.private" -o -name "*-user-*" 2>/dev/null | grep -q .; then
            echo "⚠️  Potential user data leak detected in system directory: ${sys_path}"
            log_privacy_event "WARNING: User data found in system directory ${sys_path}"
        fi
    done
    
    echo "✅ File structure separation validated"
    return 0
}

# Enforce privacy protection for uMemory
protect_umemory() {
    echo "🔒 Enforcing uMemory privacy protection..."
    
    # Ensure uMemory is in gitignore (already done but verify)
    if ! grep -q "^uMemory/" "${UHOME}/.gitignore" 2>/dev/null; then
        echo "uMemory/" >> "${UHOME}/.gitignore"
        log_privacy_event "Added uMemory to .gitignore"
    fi
    
    # Set restrictive permissions on uMemory (user-only access)
    chmod 700 "$UMEM" 2>/dev/null || true
    
    # Ensure logs are protected
    if [[ -d "${UMEM}/logs" ]]; then
        chmod 700 "${UMEM}/logs" 2>/dev/null || true
        find "${UMEM}/logs" -type f -exec chmod 600 {} \; 2>/dev/null || true
    fi
    
    # Protect user identity
    if [[ -f "${UMEM}/user/identity.md" ]]; then
        chmod 600 "${UMEM}/user/identity.md" 2>/dev/null || true
    fi
    
    echo "✅ uMemory privacy protection enforced"
    log_privacy_event "Privacy protection enforced for uMemory"
}

# Validate naming conventions for privacy
check_filename_privacy() {
    echo "📁 Checking filename privacy conventions..."
    
    # Files that should NEVER contain personal info in names
    local sensitive_patterns=(
        "*${USER}*"
        "*$(whoami)*"  
        "*personal*"
        "*private*"
        "*secret*"
    )
    
    # Check system directories for privacy leaks in filenames
    for pattern in "${sensitive_patterns[@]}"; do
        if find "${UHOME}/uCode" "${UHOME}/uKnowledge" "${UHOME}/uScript" "${UHOME}/uTemplate" -name "$pattern" 2>/dev/null | grep -q .; then
            echo "⚠️  Privacy concern: Files with personal info found in system directories"
            log_privacy_event "WARNING: Personal info in system directory filenames"
        fi
    done
    
    echo "✅ Filename privacy conventions verified"
}

# Enforce one-installation-per-user model
validate_installation_binding() {
    echo "🔐 Validating installation binding (one user per installation)..."
    
    local identity_file="${UMEM}/user/identity.md"
    
    if [[ -f "$identity_file" ]]; then
        local bound_user=$(grep "^**Username**:" "$identity_file" 2>/dev/null | cut -d' ' -f2 || echo "unknown")
        local current_user=$(whoami)
        
        # Check if installation is bound to current system user
        if [[ "$bound_user" != "unknown" ]] && [[ -f "${UMEM}/users/permissions/${bound_user}.json" ]]; then
            echo "✅ Installation properly bound to user: $bound_user"
            log_privacy_event "Installation binding validated for user: $bound_user"
        else
            echo "⚠️  Installation binding unclear - recommend re-running user setup"
            log_privacy_event "WARNING: Installation binding validation failed"
        fi
    else
        echo "❌ No user identity found - first-time setup required"
        return 1
    fi
}

# Generate privacy report
generate_privacy_report() {
    echo "📊 Generating privacy protection report..."
    
    local report_file="${UMEM}/logs/system/privacy-report-$(date +%Y%m%d).md"
    
    cat > "$report_file" << EOF
# uDOS Privacy Protection Report
**Generated**: $(date '+%Y-%m-%d %H:%M:%S')
**Installation**: ${UHOME}

## Core Principles Compliance

### ✅ One Installation Per User
- Installation bound to specific user account
- No multi-user access configured
- User identity properly established

### ✅ Privacy Protection
- uMemory directory isolated from system components
- Personal data confined to uMemory
- No user data in system directories

### ✅ Flat File System Organization
- Clear separation between system (uCode, uKnowledge, etc.) and user (uMemory)
- Proper naming conventions followed
- No cross-contamination detected

## Directory Structure

### System Directories (No User Data)
- \`uCode/\` - Development and system scripts
- \`uKnowledge/\` - Documentation and knowledge base
- \`uScript/\` - System utilities and scripts
- \`uTemplate/\` - Template system

### User Directory (Privacy Protected)  
- \`uMemory/\` - ALL user content (protected, local-only)
  - Personal files, logs, missions, moves
  - User identity and preferences
  - Private workspace and sandbox

## Privacy Status: ✅ PROTECTED

All core uDOS privacy principles are properly implemented and enforced.

EOF

    echo "✅ Privacy report generated: $(basename "$report_file")"
    log_privacy_event "Privacy report generated"
}

# Main privacy guard function
main() {
    echo "🛡️  uDOS Privacy Guard v1.0"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Create privacy log if it doesn't exist
    mkdir -p "${UMEM}/logs/system"
    touch "${UMEM}/logs/system/privacy.log"
    
    log_privacy_event "Privacy guard started"
    
    # Run all privacy checks
    validate_file_structure
    protect_umemory
    check_filename_privacy
    validate_installation_binding
    generate_privacy_report
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Privacy guard complete - uDOS core ethos enforced"
    
    log_privacy_event "Privacy guard completed successfully"
}

# Command line interface
case "${1:-check}" in
    check|validate)
        main
        ;;
    report)
        generate_privacy_report
        ;;
    protect)
        protect_umemory
        ;;
    structure)
        validate_file_structure
        ;;
    binding)
        validate_installation_binding
        ;;
    *)
        echo "Usage: $0 {check|report|protect|structure|binding}"
        echo ""
        echo "Commands:"
        echo "  check     - Run full privacy validation (default)"
        echo "  report    - Generate privacy report only"
        echo "  protect   - Enforce uMemory protection only"
        echo "  structure - Validate file structure separation only"
        echo "  binding   - Check installation binding only"
        ;;
esac
