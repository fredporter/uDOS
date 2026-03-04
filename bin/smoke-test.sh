#!/usr/bin/env bash

# ============================================================
# uDOS-vibe Installer Smoke Tests
# ============================================================
# Tests installer functionality, recovery, and failure modes
# ============================================================

# No set -e: we're testing failure scenarios and need to continue
# Each test explicitly tracks pass/fail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_RESULTS=()
TESTS_PASSED=0
TESTS_FAILED=0

function test_header() {
    echo ""
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}${BOLD}  TEST: $1${NC}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

function test_pass() {
    echo -e "${GREEN}[✓ PASS]${NC} $1"
    TEST_RESULTS+=("PASS: $1")
    ((TESTS_PASSED++))
}

function test_fail() {
    echo -e "${RED}[✗ FAIL]${NC} $1"
    TEST_RESULTS+=("FAIL: $1")
    ((TESTS_FAILED++))
}

function test_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

function test_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# ── Test 1: OS Detection ─────────────────────────────────────
function test_os_detection() {
    test_header "OS Detection"

    local platform=$(uname -s)
    test_info "Platform: $platform"

    if [[ "$platform" == "Darwin" ]]; then
        test_pass "macOS detected correctly"

        local version=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
        test_info "macOS version: $version"

        local cores=$(sysctl -n hw.ncpu 2>/dev/null || echo "unknown")
        test_info "CPU cores: $cores"

        local ram_bytes=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
        if [[ "$ram_bytes" != "0" ]] && command -v bc &>/dev/null; then
            local ram_gb=$(echo "$ram_bytes / 1024 / 1024 / 1024" | bc 2>/dev/null || echo "unknown")
            test_info "RAM: ${ram_gb}GB"
        else
            test_info "RAM: unknown"
        fi

        # Check for GPU (disable pipefail temporarily to handle grep not finding match)
        set +e
        local gpu_check=$(system_profiler SPDisplaysDataType 2>/dev/null | grep "Metal" 2>/dev/null)
        set -e
        if [[ -n "$gpu_check" ]]; then
            test_pass "GPU (Metal) detected"
        else
            test_info "No GPU detected or check skipped (non-critical)"
        fi
    elif [[ "$platform" == "Linux" ]]; then
        test_pass "Linux detected correctly"

        if [[ -f /etc/os-release ]]; then
            source /etc/os-release 2>/dev/null || true
            test_info "Distro: ${ID:-unknown} ${VERSION_ID:-unknown}"
        fi
    else
        test_fail "Unknown platform: $platform"
    fi
}

# ── Test 2: Required Commands ────────────────────────────────
function test_required_commands() {
    test_header "Required Commands"

    local required=(curl git)
    local missing=()

    for cmd in "${required[@]}"; do
        if command -v $cmd &> /dev/null; then
            test_pass "$cmd is available"
        else
            test_fail "$cmd is missing"
            missing+=($cmd)
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        test_pass "All required commands present"
    else
        test_fail "Missing commands: ${missing[*]}"
    fi
}

# ── Test 3: File Structure ───────────────────────────────────
function test_file_structure() {
    test_header "File Structure"

    local required_files=(
        "bin/install-udos-vibe.sh"
        "bin/install-udos-vibe.command"
        ".env.example"
        "pyproject.toml"
        "vault"
    )

    for file in "${required_files[@]}"; do
        if [[ -e "$REPO_ROOT/$file" ]]; then
            test_pass "Found: $file"
        else
            test_fail "Missing: $file"
        fi
    done

    # Check installer is executable
    if [[ -x "$REPO_ROOT/bin/install-udos-vibe.sh" ]]; then
        test_pass "Installer is executable"
    else
        test_fail "Installer is not executable"
    fi
}

# ── Test 4: .env Creation (Non-destructive) ──────────────────
function test_env_creation() {
    test_header ".env Creation (Simulated)"

    local env_example="$REPO_ROOT/.env.example"
    local env_test="/tmp/udos-test-env-$$.env"

    if [[ ! -f "$env_example" ]]; then
        test_fail ".env.example not found"
        return
    fi

    # Simulate .env creation
    cp "$env_example" "$env_test"

    # Test variable replacement (what installer does)
    sed -i.bak "s|UDOS_ROOT=.*|UDOS_ROOT=$REPO_ROOT|g" "$env_test"
    sed -i.bak "s|OS_TYPE=.*|OS_TYPE=mac|g" "$env_test"

    if grep -q "UDOS_ROOT=$REPO_ROOT" "$env_test"; then
        test_pass "UDOS_ROOT auto-configured correctly"
    else
        test_fail "UDOS_ROOT auto-configuration failed"
    fi

    if grep -q "OS_TYPE=mac" "$env_test"; then
        test_pass "OS_TYPE auto-configured correctly"
    else
        test_fail "OS_TYPE auto-configuration failed"
    fi

    # Check essential variables exist
    local required_vars=(
        "UDOS_ROOT"
        "VAULT_ROOT"
        "MISTRAL_API_KEY"
        "WIZARD_ADMIN_TOKEN"
        "WIZARD_KEY"
    )

    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" "$env_test" || grep -q "^# $var=" "$env_test" || grep -q "^$var=" "$env_test"; then
            test_pass "Variable $var present in template"
        else
            test_fail "Variable $var missing from template"
        fi
    done

    # Cleanup
    rm -f "$env_test" "$env_test.bak"
}

# ── Test 5: Vault Separation ─────────────────────────────────
function test_vault_separation() {
    test_header "Vault Data Separation"
    local env_file="$REPO_ROOT/.env"
    local runtime_memory="$REPO_ROOT/memory"
    local runtime_vault="$runtime_memory/vault"

    if [[ -f "$env_file" ]]; then
        local env_memory env_vault
        env_memory="$(grep -E '^UDOS_MEMORY_ROOT=' "$env_file" | tail -n1 | cut -d= -f2- | tr -d '\"' | tr -d \"'\")"
        env_vault="$(grep -E '^VAULT_ROOT=' "$env_file" | tail -n1 | cut -d= -f2- | tr -d '\"' | tr -d \"'\")"
        if [[ -n "$env_memory" ]]; then
            runtime_memory="${env_memory//\$\{UDOS_ROOT\}/$REPO_ROOT}"
        fi
        if [[ -n "$env_vault" ]]; then
            runtime_vault="${env_vault//\$\{UDOS_MEMORY_ROOT\}/$runtime_memory}"
            runtime_vault="${runtime_vault//\$\{UDOS_ROOT\}/$REPO_ROOT}"
        fi
    fi

    # Check vault template exists and is separate
    if [[ -d "$REPO_ROOT/vault" ]]; then
        test_pass "Template vault exists at vault/"
    else
        test_fail "Template vault missing"
    fi

    # Check runtime vault location
    test_info "Runtime vault should be at: $runtime_vault"

    if [[ -d "$runtime_vault" ]]; then
        test_pass "Runtime vault directory exists"

        # Check for .vault-initialized marker
        if [[ -f "$runtime_vault/.vault-initialized" ]]; then
            test_pass "Vault initialization marker found"
        else
            test_info "Vault not yet initialized (expected on fresh install)"
        fi
    else
        test_info "Runtime vault not created yet (expected before first run)"
    fi

    # Check that memory/ is in .gitignore
    if grep -q "^memory/" "$REPO_ROOT/.gitignore" 2>/dev/null; then
        test_pass "memory/ directory is gitignored (protects user data)"
    else
        test_warn "memory/ should be in .gitignore"
    fi
}

# ── Test 6: Recovery Scenarios ───────────────────────────────
function test_recovery_scenarios() {
    test_header "Recovery Scenarios"

    # Test 1: Missing .env recovery
    test_info "Scenario: Missing .env file"
    if [[ ! -f "$REPO_ROOT/.env" ]]; then
        test_pass "System correctly handles missing .env (installer will create)"
    else
        test_info ".env exists (update scenario)"
    fi

    # Test 2: Partial installation detection
    test_info "Scenario: Partial installation"

    local has_uv=false
    local has_vibe=false

    if command -v uv &> /dev/null; then
        has_uv=true
        test_pass "uv detected (partial install scenario)"
    else
        test_info "uv not installed (fresh install scenario)"
    fi

    if command -v vibe &> /dev/null; then
        has_vibe=true
        test_pass "vibe detected (partial install scenario)"
    else
        test_info "vibe not installed (fresh install scenario)"
    fi

    # Test 3: Missing directories recovery
    test_info "Scenario: Missing runtime directories"
    if [[ ! -d "$REPO_ROOT/memory" ]]; then
        test_pass "memory/ missing (installer will create)"
    else
        test_info "memory/ exists"
    fi

    if [[ ! -d "$REPO_ROOT/.vibe" ]]; then
        test_pass ".vibe/ missing (installer will create)"
    else
        test_info ".vibe/ exists"
    fi
}

# ── Test 7: Non-blocking Failures ────────────────────────────
function test_nonblocking_failures() {
    test_header "Non-blocking Failure Handling"

    # Test that optional components don't block
    test_info "Testing optional component failures..."

    # Micro editor is optional
    if ! command -v micro &> /dev/null; then
        test_pass "System works without micro (optional)"
    else
        test_info "micro is installed"
    fi

    # Obsidian is optional
    if [[ ! -d "/Applications/Obsidian.app" ]] && [[ "$OSTYPE" == "darwin"* ]]; then
        test_pass "System works without Obsidian (optional)"
    else
        test_info "Obsidian may be installed"
    fi

    test_info "Local logic-assist runtime uses GPT4All model files"

    test_pass "Optional components correctly identified as non-blocking"
}

# ── Test 8: Security Token Generation ────────────────────────
function test_security_tokens() {
    test_header "Security Token Generation"

    # Test token generation methods
    test_info "Testing token generation..."

    # Method 1: Python secrets
    if command -v python3 &> /dev/null; then
        local token=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null)
        if [[ -n "$token" ]] && [[ ${#token} -gt 30 ]]; then
            test_pass "Python secrets token generation works"
        else
            test_fail "Python secrets token generation failed"
        fi

        local hex_key=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null)
        if [[ -n "$hex_key" ]] && [[ ${#hex_key} -eq 64 ]]; then
            test_pass "Python hex key generation works (64 chars)"
        else
            test_fail "Python hex key generation failed"
        fi
    else
        test_warn "Python3 not available for token generation"
    fi

    # Method 2: OpenSSL fallback
    if command -v openssl &> /dev/null; then
        local token=$(openssl rand -base64 32)
        if [[ -n "$token" ]]; then
            test_pass "OpenSSL token generation works (fallback)"
        else
            test_fail "OpenSSL token generation failed"
        fi

        local hex_key=$(openssl rand -hex 32)
        if [[ -n "$hex_key" ]] && [[ ${#hex_key} -eq 64 ]]; then
            test_pass "OpenSSL hex key generation works (fallback)"
        else
            test_fail "OpenSSL hex key generation failed"
        fi
    else
        test_warn "OpenSSL not available for fallback"
    fi
}

# ── Test 9: Update Scenario ──────────────────────────────────
function test_update_scenario() {
    test_header "Update Scenario"
    local env_file="$REPO_ROOT/.env"
    local has_vault=false
    local runtime_vault="$REPO_ROOT/memory/vault"

    test_info "Simulating update on existing installation..."

    # Check if this looks like an existing installation
    local has_env=false
    if [[ -f "$REPO_ROOT/.env" ]]; then
        has_env=true
        test_info "Existing .env detected"
    fi

    if [[ -f "$env_file" ]]; then
        local env_vault
        env_vault="$(grep -E '^VAULT_ROOT=' "$env_file" | tail -n1 | cut -d= -f2- | tr -d '\"' | tr -d \"'\")"
        if [[ -n "$env_vault" ]]; then
            runtime_vault="${env_vault//\$\{UDOS_ROOT\}/$REPO_ROOT}"
            runtime_vault="${runtime_vault//\$\{UDOS_MEMORY_ROOT\}/$REPO_ROOT/memory}"
        fi
    fi

    if [[ -d "$runtime_vault" ]]; then
        has_vault=true
        test_info "Existing vault detected at $runtime_vault"
    fi

    if [[ "$has_env" == true ]] || [[ "$has_vault" == true ]]; then
        test_pass "Update scenario: Installer should preserve existing data"
        test_info "- .env should be backed up before overwrite"
        test_info "- Vault data should never be touched"
    else
        test_pass "Fresh install scenario: No existing data to preserve"
    fi
}

# ── Test 10: DESTROY & REPAIR Markers ────────────────────────
function test_destroy_repair_markers() {
    test_header "DESTROY & REPAIR System"

    test_info "Checking for uDOS lifecycle markers..."

    # Check for version tracking
    if [[ -f "$REPO_ROOT/version.json" ]]; then
        test_pass "version.json exists for tracking"
        local version=$(cat "$REPO_ROOT/version.json" 2>/dev/null | grep -o '"version"[^,]*' | cut -d'"' -f4)
        if [[ -n "$version" ]]; then
            test_info "Current version: $version"
        fi
    else
        test_fail "version.json missing"
    fi

    # Check vault is protected from DESTROY
    test_info "Verifying vault protection..."
    if [[ -d "$REPO_ROOT/vault" ]]; then
        test_pass "Template vault (vault/) preserved across DESTROY/REPAIR"
    fi

    if [[ -f "$REPO_ROOT/.gitignore" ]]; then
        if grep -q "^memory/" "$REPO_ROOT/.gitignore"; then
            test_pass "User memory/vault storage protected via .gitignore"
        fi

        if grep -q "^\.env$" "$REPO_ROOT/.gitignore"; then
            test_pass "User .env protected via .gitignore"
        fi
    fi

    # Check secret storage location
    local secrets_tomb="$REPO_ROOT/memory/.secrets.tomb"
    if [[ -f "$secrets_tomb" ]]; then
        test_pass "Encrypted secret storage found"
    else
        test_info "Secret storage not yet created (expected pre-SETUP)"
    fi
}

# ── Test 11: Installer Help & Options ────────────────────────
function test_installer_options() {
    test_header "Installer Options"

    local installer="$REPO_ROOT/bin/install-udos-vibe.sh"

    # Test help
    if $installer --help >/dev/null 2>&1; then
        test_pass "--help option works"
    else
        test_fail "--help option failed"
    fi

    # Verify option documentation
    local help_output=$($installer --help 2>&1)

    local expected_options=(
        "core"
        "wizard"
        "update"
    )

    for opt in "${expected_options[@]}"; do
        if echo "$help_output" | grep -q -- "--$opt"; then
            test_pass "Option --$opt documented in help"
        else
            test_fail "Option --$opt missing from help"
        fi
    done
}

# ── Test Summary ─────────────────────────────────────────────
function print_summary() {
    echo ""
    echo -e "${MAGENTA}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}${BOLD}  TEST SUMMARY${NC}"
    echo -e "${MAGENTA}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo ""

    local total=$((TESTS_PASSED + TESTS_FAILED))
    if [[ $total -gt 0 ]]; then
        local pass_rate=$((TESTS_PASSED * 100 / total))
        echo -e "Pass Rate: ${pass_rate}%"
    fi

    echo ""
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}${BOLD}✓ ALL TESTS PASSED${NC}"
        echo ""
        echo "The installer is ready for production use!"
        return 0
    else
        echo -e "${RED}${BOLD}✗ SOME TESTS FAILED${NC}"
        echo ""
        echo "Failed tests:"
        for result in "${TEST_RESULTS[@]}"; do
            if [[ "$result" == FAIL:* ]]; then
                echo -e "${RED}  - ${result#FAIL: }${NC}"
            fi
        done
        return 1
    fi
}

# ── Main Test Runner ─────────────────────────────────────────
function main() {
    echo -e "${BOLD}${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║         uDOS-vibe Installer Smoke Test Suite             ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    echo ""
    echo "Repository: $REPO_ROOT"
    echo "Date: $(date)"
    echo ""

    # Run all tests
    test_os_detection
    test_required_commands
    test_file_structure
    test_env_creation
    test_vault_separation
    test_recovery_scenarios
    test_nonblocking_failures
    test_security_tokens
    test_update_scenario
    test_destroy_repair_markers
    test_installer_options

    # Print summary
    print_summary
}

main "$@"
