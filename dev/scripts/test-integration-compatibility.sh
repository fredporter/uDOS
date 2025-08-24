#!/bin/bash
# uDOS Integration Compatibility Test v1.3.3
# Tests compatibility between uNETWORK, uSCRIPT, and uCORE protocols

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_LOG="$UDOS_ROOT/sandbox/logs/integration-test-$(date +%Y%m%d-%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
mkdir -p "$(dirname "$TEST_LOG")"
exec > >(tee -a "$TEST_LOG")
exec 2>&1

log_test() {
    local status="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$status" in
        "PASS") echo -e "${GREEN}[PASS]${NC} $message" ;;
        "FAIL") echo -e "${RED}[FAIL]${NC} $message" ;;
        "WARN") echo -e "${YELLOW}[WARN]${NC} $message" ;;
        "INFO") echo -e "${BLUE}[INFO]${NC} $message" ;;
        "TEST") echo -e "${CYAN}[TEST]${NC} $message" ;;
    esac

    echo "[$timestamp] [$status] $message" >> "$TEST_LOG"
}

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNINGS=0

run_test() {
    local test_name="$1"
    local test_function="$2"

    ((TESTS_TOTAL++))
    log_test "TEST" "Running: $test_name"

    if $test_function; then
        ((TESTS_PASSED++))
        log_test "PASS" "$test_name"
        return 0
    else
        ((TESTS_FAILED++))
        log_test "FAIL" "$test_name"
        return 1
    fi
}

# Test uCORE logging protocol integration
test_ucore_logging() {
    local ucore_logging="$UDOS_ROOT/uCORE/core/logging.sh"

    if [[ -f "$ucore_logging" ]]; then
        source "$ucore_logging" 2>/dev/null || return 1

        # Test logging functions
        if command -v log_info >/dev/null 2>&1 && \
           command -v log_error >/dev/null 2>&1 && \
           command -v log_success >/dev/null 2>&1; then
            return 0
        fi
    fi

    return 1
}

# Test uCORE error handler integration
test_ucore_error_handler() {
    local error_handler="$UDOS_ROOT/uCORE/system/error-handler.sh"

    if [[ -f "$error_handler" ]]; then
        # Check if error handler functions are available
        if grep -q "init_error_logging" "$error_handler" && \
           grep -q "log_error" "$error_handler" && \
           grep -q "generate_error_id" "$error_handler"; then
            return 0
        fi
    fi

    return 1
}

# Test backup protocol integration
test_backup_protocol() {
    local backup_dir="$UDOS_ROOT/backup"

    if [[ -d "$backup_dir" ]]; then
        # Check if backup scripts exist
        if find "$backup_dir" -name "*.tar.gz" -o -name "backup-*.json" >/dev/null 2>&1; then
            return 0
        fi

        # Directory exists but no backups - still valid
        return 0
    fi

    # Try to create backup directory
    mkdir -p "$backup_dir" 2>/dev/null && return 0
    return 1
}

# Test role-based permission system
test_role_permissions() {
    local role_file="$UDOS_ROOT/uMEMORY/system/uDATA-user-roles.json"
    local current_role_conf="$UDOS_ROOT/sandbox/current-role.conf"

    if [[ -f "$role_file" && -f "$current_role_conf" ]]; then
        # Test role file format
        if jq empty "$role_file" 2>/dev/null; then
            # Test current role configuration
            if grep -q "CURRENT_ROLE=" "$current_role_conf"; then
                return 0
            fi
        fi
    fi

    return 1
}

# Test uNETWORK integration
test_unetwork_integration() {
    local server_py="$UDOS_ROOT/uNETWORK/server/server.py"
    local integration_py="$UDOS_ROOT/uNETWORK/server/integration/ucore_protocols.py"

    if [[ -f "$server_py" && -f "$integration_py" ]]; then
        # Check if server imports integration
        if grep -q "ucore_protocols" "$server_py"; then
            # Test Python syntax
            python3 -m py_compile "$integration_py" 2>/dev/null && return 0
        fi
    fi

    return 1
}

# Test uSCRIPT integration
test_uscript_integration() {
    local uscript_main="$UDOS_ROOT/uSCRIPT/uscript.sh"
    local integration_sh="$UDOS_ROOT/uSCRIPT/integration/ucore-integration.sh"

    if [[ -f "$uscript_main" && -f "$integration_sh" ]]; then
        # Check if main script sources integration
        if grep -q "ucore-integration.sh" "$uscript_main"; then
            # Test bash syntax
            bash -n "$integration_sh" 2>/dev/null && return 0
        fi
    fi

    return 1
}

# Test sandbox access
test_sandbox_access() {
    local sandbox_dir="$UDOS_ROOT/sandbox"

    if [[ -d "$sandbox_dir" ]]; then
        # Test write access to sandbox
        local test_file="$sandbox_dir/integration-test-$(date +%s).tmp"
        if echo "test" > "$test_file" 2>/dev/null; then
            rm -f "$test_file"
            return 0
        fi
    fi

    return 1
}

# Test uMEMORY resource access
test_umemory_access() {
    local umemory_dir="$UDOS_ROOT/uMEMORY"
    local system_dir="$umemory_dir/system"

    if [[ -d "$system_dir" ]]; then
        # Check for key system files
        local required_files=(
            "uDATA-user-roles.json"
            "uDATA-commands.json"
            "uDATA-colours.json"
        )

        for file in "${required_files[@]}"; do
            if [[ ! -f "$system_dir/$file" ]]; then
                return 1
            fi
        done

        return 0
    fi

    return 1
}

# Test virtual environment integration
test_venv_integration() {
    local uscript_venv="$UDOS_ROOT/uSCRIPT/venv/python"

    if [[ -d "$uscript_venv" ]]; then
        local activate_script="$uscript_venv/bin/activate"
        if [[ -f "$activate_script" ]]; then
            # Test activation
            source "$activate_script" 2>/dev/null && deactivate 2>/dev/null && return 0
        fi
    fi

    # Virtual environment not required, but warn if missing
    ((TESTS_WARNINGS++))
    log_test "WARN" "Python virtual environment not found (optional)"
    return 0
}

# Test configuration validation
test_config_validation() {
    local network_config="$UDOS_ROOT/uNETWORK/server/config"
    local uscript_config="$UDOS_ROOT/uSCRIPT/config"

    if [[ -d "$network_config" && -d "$uscript_config" ]]; then
        # Test JSON configuration files
        for config_dir in "$network_config" "$uscript_config"; do
            for json_file in "$config_dir"/*.json; do
                if [[ -f "$json_file" ]]; then
                    if ! jq empty "$json_file" 2>/dev/null; then
                        return 1
                    fi
                fi
            done
        done

        return 0
    fi

    return 1
}

# Test cross-component communication
test_cross_component_communication() {
    # Test if uNETWORK can call uSCRIPT integration
    local integration_py="$UDOS_ROOT/uNETWORK/server/integration/ucore_protocols.py"

    if [[ -f "$integration_py" ]]; then
        # Test Python integration
        if python3 -c "
import sys
sys.path.append('$UDOS_ROOT/uNETWORK/server')
try:
    from integration import create_ucore_integration
    protocols = create_ucore_integration('$UDOS_ROOT')
    status = protocols.get_system_status()
    exit(0)
except Exception as e:
    exit(1)
" 2>/dev/null; then
            return 0
        fi
    fi

    return 1
}

# Test log directory structure
test_log_structure() {
    local required_log_dirs=(
        "$UDOS_ROOT/uMEMORY/system/logs"
        "$UDOS_ROOT/uMEMORY/system/logs/errors"
        "$UDOS_ROOT/uMEMORY/system/logs/debug"
        "$UDOS_ROOT/uMEMORY/system/logs/crashes"
    )

    for log_dir in "${required_log_dirs[@]}"; do
        if [[ ! -d "$log_dir" ]]; then
            mkdir -p "$log_dir" 2>/dev/null || return 1
        fi
    done

    return 0
}

# Test role switching functionality
test_role_switching() {
    local role_script="$UDOS_ROOT/uSCRIPT/library/ucode/roles.sh"

    if [[ -f "$role_script" ]]; then
        # Test role script functions
        source "$role_script" 2>/dev/null || return 1

        # Test get_user_role function
        if command -v get_user_role >/dev/null 2>&1; then
            local current_role=$(get_user_role)
            if [[ -n "$current_role" ]]; then
                return 0
            fi
        fi
    fi

    return 1
}

# Main test execution
main() {
    echo "uDOS Integration Compatibility Test v1.3.3"
    echo "==========================================="
    echo "Test log: $TEST_LOG"
    echo

    log_test "INFO" "Starting integration compatibility tests"
    log_test "INFO" "uDOS Root: $UDOS_ROOT"

    # Run all tests
    run_test "uCORE Logging Protocol" test_ucore_logging
    run_test "uCORE Error Handler" test_ucore_error_handler
    run_test "Backup Protocol" test_backup_protocol
    run_test "Role-based Permissions" test_role_permissions
    run_test "uNETWORK Integration" test_unetwork_integration
    run_test "uSCRIPT Integration" test_uscript_integration
    run_test "Sandbox Access" test_sandbox_access
    run_test "uMEMORY Resource Access" test_umemory_access
    run_test "Virtual Environment" test_venv_integration
    run_test "Configuration Validation" test_config_validation
    run_test "Cross-component Communication" test_cross_component_communication
    run_test "Log Directory Structure" test_log_structure
    run_test "Role Switching" test_role_switching

    echo
    echo "Test Results Summary"
    echo "===================="
    echo -e "Total Tests:  ${BLUE}$TESTS_TOTAL${NC}"
    echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
    echo -e "Warnings:     ${YELLOW}$TESTS_WARNINGS${NC}"
    echo

    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_test "PASS" "All critical integration tests passed"
        echo -e "${GREEN}✅ Integration compatibility: PASS${NC}"
        if [[ $TESTS_WARNINGS -gt 0 ]]; then
            echo -e "${YELLOW}⚠️  Some optional components have warnings${NC}"
        fi
        exit 0
    else
        log_test "FAIL" "$TESTS_FAILED integration tests failed"
        echo -e "${RED}❌ Integration compatibility: FAIL${NC}"
        echo "Check the test log for details: $TEST_LOG"
        exit 1
    fi
}

# Show detailed status if requested
if [[ "${1:-}" == "--status" ]]; then
    echo "Component Status Check"
    echo "====================="

    components=(
        "uCORE/core/logging.sh:uCORE Logging"
        "uCORE/system/error-handler.sh:uCORE Error Handler"
        "uMEMORY/system/uDATA-user-roles.json:Role Permissions"
        "uNETWORK/server/integration/ucore_protocols.py:uNETWORK Integration"
        "uSCRIPT/integration/ucore-integration.sh:uSCRIPT Integration"
        "sandbox:Sandbox Directory"
        "backup:Backup Directory"
    )

    for component in "${components[@]}"; do
        IFS=':' read -r path name <<< "$component"
        full_path="$UDOS_ROOT/$path"

        if [[ -e "$full_path" ]]; then
            echo -e "${GREEN}✅${NC} $name"
        else
            echo -e "${RED}❌${NC} $name (not found: $path)"
        fi
    done

    exit 0
fi

# Run the main test suite
main "$@"
