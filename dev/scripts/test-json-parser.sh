#!/bin/bash
# Test uDOS JSON Parser v1.3.3
# Comprehensive test suite for the optimized JSON parser

# Test data
TEST_DATA_DIR="/tmp/udos-json-test"
PARSER_SCRIPT="/Users/agentdigital/uDOS/uCORE/core/json-parser-v1.3.3.sh"

# Create test environment
setup_test_environment() {
    echo "Setting up test environment..."
    mkdir -p "$TEST_DATA_DIR"
    cd "$TEST_DATA_DIR"

    # Create test JSON files

    # Test 1: Simple object
    cat > simple.json << 'EOF'
{
  "id": "USER-001",
  "name": "admin",
  "role": "administrator",
  "created": "2025-08-21T14:30:00Z"
}
EOF

    # Test 2: Array data
    cat > array.json << 'EOF'
[
  {
    "id": 1,
    "name": "admin",
    "role": "administrator"
  },
  {
    "id": 2,
    "name": "user",
    "role": "standard"
  },
  {
    "id": 3,
    "name": "guest",
    "role": "readonly"
  }
]
EOF

    # Test 3: Complex nested data
    cat > complex.json << 'EOF'
{
  "mission": {
    "id": "M001",
    "title": "Setup Environment",
    "tasks": [
      {
        "id": 1,
        "title": "Install dependencies",
        "done": true
      },
      {
        "id": 2,
        "title": "Configure settings",
        "done": false
      }
    ],
    "metadata": {
      "created": "2025-08-21",
      "priority": "high"
    }
  }
}
EOF

    # Test 4: Invalid JSON
    cat > invalid.json << 'EOF'
{
  "id": "USER-001",
  "name": "admin"
  "role": "administrator"
}
EOF

    echo "Test environment ready at: $TEST_DATA_DIR"
}

# Test JSON processing
test_json_processing() {
    echo
    echo "=== Testing JSON Processing ==="

    echo "Test 1: Simple object minification"
    "$PARSER_SCRIPT" process simple.json simple-output.json minified
    echo "Input:"
    cat simple.json
    echo
    echo "Output:"
    cat simple-output.json
    echo

    echo "Test 2: Array to one-per-line"
    "$PARSER_SCRIPT" process array.json array-output.json minified-lines
    echo "Input:"
    cat array.json
    echo
    echo "Output:"
    cat array-output.json
    echo

    echo "Test 3: Complex data minification"
    "$PARSER_SCRIPT" process complex.json complex-output.json minified
    echo "Input:"
    cat complex.json
    echo
    echo "Output:"
    cat complex-output.json
    echo
}

# Test uDATA file creation
test_udata_creation() {
    echo
    echo "=== Testing uDATA File Creation ==="

    echo "Test 1: Create user data file"
    user_data='{"users":[{"id":1,"name":"admin","role":"administrator"},{"id":2,"name":"guest","role":"readonly"}]}'
    udata_file=$("$PARSER_SCRIPT" create "user-data" "$user_data" ".")
    echo "Created file: $udata_file"
    echo "Contents:"
    cat "$udata_file"
    echo

    echo "Test 2: Create system state file"
    system_data='{"components":[{"name":"template-engine","status":"active","version":"1.3.3"},{"name":"json-parser","status":"active","version":"1.3.3"}]}'
    udata_file2=$("$PARSER_SCRIPT" create "system-state" "$system_data" ".")
    echo "Created file: $udata_file2"
    echo "Contents:"
    cat "$udata_file2"
    echo
}

# Test data extraction
test_data_extraction() {
    echo
    echo "=== Testing Data Extraction ==="

    # Use previously created uDATA file
    local udata_file="uDATA-$(date +%Y%m%d)-user-data.json"

    if [[ -f "$udata_file" ]]; then
        echo "Test 1: Extract all data"
        "$PARSER_SCRIPT" extract "$udata_file"
        echo

        echo "Test 2: Extract with query filter"
        "$PARSER_SCRIPT" extract "$udata_file" "admin"
        echo
    else
        echo "uDATA file not found for extraction test"
    fi
}

# Test validation
test_validation() {
    echo
    echo "=== Testing JSON Validation ==="

    echo "Test 1: Valid JSON file"
    "$PARSER_SCRIPT" validate simple.json
    echo

    echo "Test 2: Invalid JSON file"
    "$PARSER_SCRIPT" validate invalid.json || echo "Validation correctly failed"
    echo
}

# Test batch processing
test_batch_processing() {
    echo
    echo "=== Testing Batch Processing ==="

    mkdir -p input_batch output_batch
    cp simple.json array.json complex.json input_batch/

    echo "Processing batch files..."
    "$PARSER_SCRIPT" batch input_batch output_batch minified-lines

    echo "Batch output files:"
    ls -la output_batch/

    echo "Sample output from batch processing:"
    echo "File: output_batch/array.json"
    cat output_batch/array.json
    echo
}

# Performance test
test_performance() {
    echo
    echo "=== Performance Testing ==="

    # Create larger test file
    echo "Creating large test file..."
    {
        echo "["
        for i in {1..1000}; do
            echo "  {\"id\": $i, \"name\": \"user$i\", \"timestamp\": \"$(date -Iseconds)\"},"
        done | sed '$ s/,$//'
        echo "]"
    } > large.json

    echo "Original file size: $(wc -c < large.json) bytes"

    # Process with timing
    echo "Processing large file..."
    time "$PARSER_SCRIPT" process large.json large-output.json minified-lines

    echo "Processed file size: $(wc -c < large-output.json) bytes"
    echo "Record count: $(wc -l < large-output.json) lines"

    # Calculate compression ratio
    original_size=$(wc -c < large.json)
    processed_size=$(wc -c < large-output.json)
    compression_ratio=$(( (original_size - processed_size) * 100 / original_size ))
    echo "Compression ratio: ${compression_ratio}%"
}

# Test integration with uDOS patterns
test_udos_integration() {
    echo
    echo "=== Testing uDOS Integration Patterns ==="

    # Test uDATA filename parsing
    echo "Test 1: uDATA filename format"
    test_filename="uDATA-20250821-move-patterns.json"
    echo "Filename: $test_filename"

    # Create test data that matches uDOS patterns
    move_data='[{"timestamp":"2025-08-21T14:30:00Z","user":"admin","action":"GET-RETRIEVE","resource":"user-data"},{"timestamp":"2025-08-21T14:31:00Z","user":"admin","action":"POST-CREATE","resource":"system-config"}]'

    echo "Creating move patterns file..."
    "$PARSER_SCRIPT" create "move-patterns" "$move_data" "."

    move_file="uDATA-$(date +%Y%m%d)-move-patterns.json"
    echo "Created: $move_file"
    echo "Contents:"
    cat "$move_file"
    echo

    # Test system log format
    log_data='[{"level":"INFO","timestamp":"2025-08-21T14:30:00Z","component":"template-engine","message":"Processing template with TERM syntax"},{"level":"INFO","timestamp":"2025-08-21T14:31:00Z","component":"json-parser","message":"Minified JSON output generated"}]'

    echo "Creating system log file..."
    "$PARSER_SCRIPT" create "system-log" "$log_data" "."

    log_file="uDATA-$(date +%Y%m%d)-system-log.json"
    echo "Created: $log_file"
    echo "Contents:"
    cat "$log_file"
    echo
}

# Cleanup test environment
cleanup_test_environment() {
    echo
    echo "=== Cleanup ==="
    echo "Test files created in: $TEST_DATA_DIR"
    echo "To remove test files, run: rm -rf $TEST_DATA_DIR"
}

# Main test execution
main() {
    echo "uDOS JSON Parser v1.3.3 - Test Suite"
    echo "===================================="

    # Check if parser script exists
    if [[ ! -f "$PARSER_SCRIPT" ]]; then
        echo "ERROR: Parser script not found at $PARSER_SCRIPT"
        exit 1
    fi

    # Check if parser script is executable
    if [[ ! -x "$PARSER_SCRIPT" ]]; then
        echo "ERROR: Parser script is not executable"
        echo "Run: chmod +x $PARSER_SCRIPT"
        exit 1
    fi

    setup_test_environment
    test_json_processing
    test_udata_creation
    test_data_extraction
    test_validation
    test_batch_processing
    test_performance
    test_udos_integration
    cleanup_test_environment

    echo
    echo "=== Test Suite Complete ==="
    echo "All tests executed. Check output above for results."
}

# Run tests
main "$@"
