#!/bin/bash
# uDOS Test Runner v1.0.0
# Comprehensive testing framework for uDOS components

set -euo pipefail

# Configuration
TEST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UDOS_ROOT="$(cd "$TEST_ROOT/../.." && pwd)"
TEST_RESULTS="$TEST_ROOT/results"
TEST_REPORTS="$TEST_ROOT/reports"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Initialize test environment
init_testing() {
    mkdir -p "$TEST_RESULTS"
    mkdir -p "$TEST_REPORTS"
    
    echo -e "${CYAN}🧪 uDOS Test Runner v1.0.0${NC}"
    echo "================================="
    echo ""
    echo -e "${BLUE}📁 Test Directory: $TEST_ROOT${NC}"
    echo -e "${BLUE}📁 Results: $TEST_RESULTS${NC}"
    echo -e "${BLUE}📁 Reports: $TEST_REPORTS${NC}"
    echo ""
}

# Run a single test
run_test() {
    local test_file="$1"
    local test_name=$(basename "$test_file" .sh)
    
    echo -ne "${YELLOW}🔄 Running: $test_name... ${NC}"
    
    ((TESTS_RUN++))
    
    local result_file="$TEST_RESULTS/$test_name.result"
    local log_file="$TEST_RESULTS/$test_name.log"
    
    if bash "$test_file" > "$log_file" 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        echo "PASSED" > "$result_file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "FAILED" > "$result_file"
        ((TESTS_FAILED++))
        
        # Show error details
        echo -e "${RED}   Error details:${NC}"
        tail -3 "$log_file" | sed 's/^/   /'
    fi
}

# Test template engine
test_template_engine() {
    local test_name="template-engine"
    echo -ne "${YELLOW}🔄 Testing: Template Engine... ${NC}"
    
    ((TESTS_RUN++))
    
    local template_engine="$UDOS_ROOT/uCORE/templates/engine/template-engine.sh"
    local test_output="$TEST_RESULTS/template-test-output.md"
    
    if [[ ! -x "$template_engine" ]]; then
        echo -e "${RED}❌ FAILED - Template engine not found${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
    
    # Test template rendering with component name
    UDOS_ROOT="$UDOS_ROOT" "$template_engine" set COMPONENT_NAME "test-component" > /dev/null 2>&1
    UDOS_ROOT="$UDOS_ROOT" "$template_engine" render component basic "$test_output" > /dev/null 2>&1
    
    if [[ -f "$test_output" ]] && grep -q "test-component" "$test_output"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
        rm -f "$test_output"
    else
        echo -e "${RED}❌ FAILED - Template rendering failed${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test command router
test_command_router() {
    local test_name="command-router"
    echo -ne "${YELLOW}🔄 Testing: Command Router... ${NC}"
    
    ((TESTS_RUN++))
    
    local command_router="$UDOS_ROOT/uCORE/code/command-router.sh"
    
    if [[ ! -x "$command_router" ]]; then
        echo -e "${RED}❌ FAILED - Command router not found${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
    
    # Test basic command
    if "$command_router" "[HELP]" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED - Command router error${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test udos executable
test_udos_executable() {
    local test_name="udos-executable"
    echo -ne "${YELLOW}🔄 Testing: uDOS Executable... ${NC}"
    
    ((TESTS_RUN++))
    
    local udos_exec="$UDOS_ROOT/udos"
    
    if [[ ! -x "$udos_exec" ]]; then
        echo -e "${RED}❌ FAILED - uDOS executable not found${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
    
    # Test help command
    if "$udos_exec" help > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED - uDOS executable error${NC}"
        ((TESTS_FAILED++))
    fi
}

# Run all tests in a directory
run_test_suite() {
    local test_dir="${1:-$TEST_ROOT/suites}"
    
    if [[ ! -d "$test_dir" ]]; then
        echo -e "${YELLOW}⚠️  Test directory not found: $test_dir${NC}"
        return 0
    fi
    
    echo -e "${BLUE}📋 Running test suite: $(basename "$test_dir")${NC}"
    echo ""
    
    for test_file in "$test_dir"/*.sh; do
        if [[ -f "$test_file" && -x "$test_file" ]]; then
            run_test "$test_file"
        fi
    done
}

# Generate test report
generate_report() {
    local report_file="$TEST_REPORTS/test-report-$(date +%Y%m%d-%H%M%S).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>uDOS Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f8ff; padding: 20px; border-radius: 8px; }
        .passed { color: #28a745; }
        .failed { color: #dc3545; }
        .summary { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 uDOS Test Report</h1>
        <p><strong>Generated:</strong> $(date)</p>
        <p><strong>uDOS Version:</strong> 1.0.5.7</p>
    </div>
    
    <div class="summary">
        <h2>📊 Test Summary</h2>
        <p><strong>Total Tests:</strong> $TESTS_RUN</p>
        <p class="passed"><strong>Passed:</strong> $TESTS_PASSED</p>
        <p class="failed"><strong>Failed:</strong> $TESTS_FAILED</p>
        <p><strong>Success Rate:</strong> $(( TESTS_RUN > 0 ? TESTS_PASSED * 100 / TESTS_RUN : 0 ))%</p>
    </div>
    
    <h2>📋 Test Details</h2>
    <ul>
EOF

    for result_file in "$TEST_RESULTS"/*.result; do
        if [[ -f "$result_file" ]]; then
            local test_name=$(basename "$result_file" .result)
            local status=$(cat "$result_file")
            local css_class=$([[ "$status" == "PASSED" ]] && echo "passed" || echo "failed")
            
            echo "        <li class=\"$css_class\">$test_name: $status</li>" >> "$report_file"
        fi
    done

    cat >> "$report_file" << EOF
    </ul>
</body>
</html>
EOF

    echo -e "${GREEN}📄 Report generated: $report_file${NC}"
}

# Show test summary
show_summary() {
    echo ""
    echo -e "${CYAN}📊 Test Summary${NC}"
    echo "==============="
    echo -e "${BLUE}Total Tests: $TESTS_RUN${NC}"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [[ $TESTS_RUN -gt 0 ]]; then
        local success_rate=$((TESTS_PASSED * 100 / TESTS_RUN))
        echo -e "${BLUE}Success Rate: ${success_rate}%${NC}"
        
        if [[ $success_rate -ge 95 ]]; then
            echo -e "${GREEN}🎉 Excellent! Phase 2 quality gate passed!${NC}"
        elif [[ $success_rate -ge 80 ]]; then
            echo -e "${YELLOW}⚠️  Good, but some improvements needed${NC}"
        else
            echo -e "${RED}❌ Quality gate failed - needs attention${NC}"
        fi
    fi
    echo ""
}

# Show help
show_help() {
    echo -e "${CYAN}🧪 uDOS Test Runner${NC}"
    echo "===================="
    echo ""
    echo -e "${WHITE}Commands:${NC}"
    echo "  init                    - Initialize test environment"
    echo "  run <test-file>         - Run single test"
    echo "  suite [directory]       - Run test suite"
    echo "  template                - Test template engine"
    echo "  router                  - Test command router"
    echo "  executable              - Test uDOS executable"
    echo "  core                    - Run core system tests"
    echo "  all                     - Run all available tests"
    echo "  report                  - Generate HTML report"
    echo "  continuous              - Run continuous testing"
    echo ""
    echo -e "${WHITE}Examples:${NC}"
    echo "  $0 init"
    echo "  $0 core"
    echo "  $0 all"
    echo "  $0 continuous"
    echo ""
}

# Main function
main() {
    local command="${1:-help}"
    shift || true
    
    case "$command" in
        "init")
            init_testing
            ;;
        "run")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}❌ Usage: $0 run <test-file>${NC}"
                exit 1
            fi
            init_testing
            run_test "$1"
            show_summary
            ;;
        "suite")
            init_testing
            run_test_suite "$1"
            show_summary
            ;;
        "template")
            init_testing
            test_template_engine
            show_summary
            ;;
        "router")
            init_testing
            test_command_router
            show_summary
            ;;
        "executable")
            init_testing
            test_udos_executable
            show_summary
            ;;
        "core")
            init_testing
            echo -e "${BLUE}🔧 Running Core System Tests${NC}"
            echo ""
            test_udos_executable
            test_command_router
            test_template_engine
            show_summary
            ;;
        "all")
            init_testing
            echo -e "${BLUE}🔧 Running All Tests${NC}"
            echo ""
            test_udos_executable
            test_command_router
            test_template_engine
            run_test_suite "$TEST_ROOT/suites"
            show_summary
            generate_report
            ;;
        "report")
            generate_report
            ;;
        "continuous")
            echo -e "${BLUE}🔄 Starting continuous testing...${NC}"
            while true; do
                clear
                init_testing
                test_udos_executable
                test_command_router
                test_template_engine
                show_summary
                echo -e "${YELLOW}⏰ Next run in 30 seconds... (Ctrl+C to stop)${NC}"
                sleep 30
            done
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
