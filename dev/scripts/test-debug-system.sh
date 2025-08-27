#!/bin/bash
# Test script for enhanced debugging, error logging, and self-healing
# This demonstrates the NetHack-inspired error messages and self-healing

set -euo pipefail

UDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_ROOT

# Color definitions (define before sourcing enhanced-debug.sh)
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m'

# Source the enhanced debugging system
source "$UDOS_ROOT/dev/scripts/enhanced-debug.sh"

# Set up test environment
export UDOS_CURRENT_ROLE="wizard"
export UDOS_DEV_MODE="true"
export UDOS_DEBUG_ENHANCED="true"

echo -e "${WHITE}🧪 Enhanced Debugging & Self-Healing Test Suite${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test 1: Permission error with self-healing
test_permission_error() {
    echo -e "${YELLOW}Test 1: Permission Error with Self-Healing${NC}"
    
    # Create a test file and remove execute permission
    local test_file="/tmp/udos_test_script.sh"
    echo '#!/bin/bash' > "$test_file"
    echo 'echo "Test successful!"' >> "$test_file"
    chmod -x "$test_file"
    
    echo "Attempting to execute file without permission..."
    if "$test_file" 2>/dev/null; then
        echo -e "${GREEN}✅ Self-healing fixed the permission issue!${NC}"
    else
        echo -e "${RED}❌ Permission test failed (expected)${NC}"
    fi
    
    rm -f "$test_file"
    echo ""
}

# Test 2: Missing file error
test_missing_file() {
    echo -e "${YELLOW}Test 2: Missing File Error${NC}"
    
    echo "Attempting to access non-existent file..."
    if cat /tmp/non_existent_file_$(date +%s).txt 2>/dev/null; then
        echo -e "${GREEN}✅ File was somehow found${NC}"
    else
        echo -e "${BLUE}ℹ️ Expected missing file error occurred${NC}"
    fi
    echo ""
}

# Test 3: Network error simulation
test_network_error() {
    echo -e "${YELLOW}Test 3: Network Error Simulation${NC}"
    
    echo "Attempting to connect to invalid host..."
    if curl -m 2 http://invalid.nonexistent.domain.test 2>/dev/null; then
        echo -e "${GREEN}✅ Network somehow worked${NC}"
    else
        echo -e "${BLUE}ℹ️ Expected network error occurred${NC}"
    fi
    echo ""
}

# Test 4: Memory stress test
test_memory_monitoring() {
    echo -e "${YELLOW}Test 4: Memory Monitoring Test${NC}"
    
    echo "Checking system health..."
    check_system
    echo ""
}

# Test 5: Show logs
test_log_display() {
    echo -e "${YELLOW}Test 5: Log Display Test${NC}"
    
    echo "Displaying recent logs..."
    show_logs
    echo ""
}

# Test 6: Adventure log entries
test_adventure_log() {
    echo -e "${YELLOW}Test 6: Adventure Log Test${NC}"
    
    local log_dir="$UDOS_ROOT/sandbox/logs"
    mkdir -p "$log_dir"
    
    # Add some test entries
    echo "$(date '+%Y-%m-%d %H:%M:%S') You enter the debugging dungeon..." >> "$log_dir/adventure.log"
    echo "$(date '+%Y-%m-%d %H:%M:%S') A wild segfault appears!" >> "$log_dir/adventure.log"
    echo "$(date '+%Y-%m-%d %H:%M:%S') You cast self-healing. It's super effective!" >> "$log_dir/adventure.log"
    
    echo "Recent adventure log entries:"
    tail -5 "$log_dir/adventure.log" 2>/dev/null || echo "No adventure log found"
    echo ""
}

# Run all tests
main() {
    # Initialize the debug system
    initialize_debug_system
    
    test_permission_error
    test_missing_file
    test_network_error
    test_memory_monitoring
    test_adventure_log
    test_log_display
    
    echo -e "${GREEN}🎉 All debugging tests completed!${NC}"
    echo -e "${BLUE}💡 Check ./sandbox/logs/ for detailed logs and adventure entries${NC}"
    
    # Show final debug info
    show_debug_info
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
