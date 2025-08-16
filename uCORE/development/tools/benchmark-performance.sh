#!/bin/bash
# Performance Benchmarking Tool
set -euo pipefail

UDEV="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "⚡ Running performance benchmarks..."

# Template processing benchmark
benchmark_template_processing() {
    local start_time=$(date +%s.%N)
    
    # Run template validation
    "$UDEV/../uCode/template-validation.sh" validate >/dev/null 2>&1
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    echo "Template validation: ${duration}s"
}

# Input system benchmark
benchmark_input_system() {
    local start_time=$(date +%s.%N)
    
    # Test input system loading
    source "$UDEV/../uCode/input-system.sh" >/dev/null 2>&1
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")
    
    echo "Input system load: ${duration}s"
}

benchmark_template_processing
benchmark_input_system

echo "✅ Performance benchmarks completed"
