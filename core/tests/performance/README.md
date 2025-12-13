# Performance Test Suite

Performance benchmarks for the Universal Input Device System (v1.2.25).

## Overview

These tests validate that the input system maintains excellent performance even with large datasets and rapid input sequences.

## Test Files

### test_selector_performance.py
Performance tests for SelectorFramework with large datasets.

**Test Coverage:**
- Load 1,000 items (< 100ms)
- Pagination through 1,000 items (< 50ms per page)
- Search 1,000 items (< 200ms)
- Clear filter (< 10ms)
- Number selection (< 5ms)
- Get page items (< 5ms)
- Stress test with 10,000 items (< 500ms load)
- Memory efficiency (< 1MB for 10k items)
- Callback overhead (< 50% increase)

**Performance Targets:**
- 1,000 items: Instant operations
- 10,000 items: Sub-second operations
- Callbacks: Minimal overhead

### test_mouse_performance.py
Performance tests for MouseHandler with many clickable regions.

**Test Coverage:**
- Register 100 regions (< 50ms)
- Click detection with 100 regions (< 10ms per click)
- Hover detection with 100 regions (< 10ms per hover)
- Region lookup (< 5ms)
- Clear 100 regions (< 10ms)
- Unregister regions (< 5ms per region)
- Overlapping regions (< 20ms per click)
- Stress test with 500 regions (< 500ms for 100 clicks)

**Performance Targets:**
- 100 regions: All operations < 50ms
- 500 regions: Stress test < 500ms
- Region lookup: < 5ms

### test_keypad_performance.py
Performance tests for KeypadHandler with rapid input.

**Test Coverage:**
- Process 1,000 rapid key presses (< 100ms, < 0.1ms per key)
- Mode switching (< 1ms per switch)
- Callback execution (< 1ms)
- Pagination (< 1ms)
- Undo/redo (< 2ms)
- Help display (< 5ms)
- Unregister keys (< 1ms)
- Get available keys (< 1ms)
- Stress test with 1,000 rapid keys (< 200ms)

**Performance Targets:**
- Key processing: < 0.1ms per key
- Mode switching: < 1ms
- Rapid input: 1,000 keys < 200ms

## Running Tests

### Run All Performance Tests
```bash
# From project root
pytest core/tests/performance/ -v -s

# With detailed timing output
pytest core/tests/performance/ -v -s --tb=short
```

### Run Individual Test Files
```bash
# Selector performance
pytest core/tests/performance/test_selector_performance.py -v -s

# Mouse performance
pytest core/tests/performance/test_mouse_performance.py -v -s

# Keypad performance
pytest core/tests/performance/test_keypad_performance.py -v -s
```

### Run Specific Tests
```bash
# Stress tests only
pytest core/tests/performance/ -v -s -k "stress"

# Memory efficiency tests
pytest core/tests/performance/ -v -s -k "memory"

# Callback overhead tests
pytest core/tests/performance/ -v -s -k "callback"
```

## Performance Metrics

### Selector Framework
| Operation | Dataset Size | Target | Typical |
|-----------|-------------|--------|---------|
| Load items | 1,000 | < 100ms | ~20ms |
| Load items | 10,000 | < 500ms | ~200ms |
| Pagination | 1,000 items | < 50ms | ~5ms |
| Search | 1,000 items | < 200ms | ~50ms |
| Selection | Any | < 5ms | ~1ms |

### Mouse Handler
| Operation | Region Count | Target | Typical |
|-----------|-------------|--------|---------|
| Register | 100 | < 50ms | ~10ms |
| Click detect | 100 | < 10ms | ~2ms |
| Hover detect | 100 | < 10ms | ~2ms |
| Region lookup | Any | < 5ms | ~0.5ms |

### Keypad Handler
| Operation | Input Count | Target | Typical |
|-----------|------------|--------|---------|
| Key process | 1,000 | < 100ms | ~20ms |
| Per key | 1 | < 0.1ms | ~0.02ms |
| Mode switch | 1 | < 1ms | ~0.1ms |
| Callback | 1 | < 1ms | ~0.2ms |

## Interpreting Results

### Good Performance
```
✓ Loaded 1000 items in 18.42ms
✓ Pagination: avg=4.23ms, max=8.15ms
✓ Search found 100 items in 47.83ms
```

### Performance Issues
```
✗ Loading took 250.15ms (should be < 100ms)
✗ Avg page time 75.42ms (should be < 50ms)
```

## Optimization Tips

If performance tests fail:

1. **Check dataset size**: Ensure you're not accidentally testing with more items than expected
2. **Review algorithm complexity**: Look for O(n²) operations
3. **Profile the code**: Use cProfile to find bottlenecks
4. **Check memory usage**: Large memory allocations can slow operations
5. **Verify test environment**: Ensure no other processes are consuming CPU

## Continuous Integration

These tests run as part of the CI pipeline to catch performance regressions:

```yaml
# .github/workflows/performance.yml
- name: Run performance tests
  run: pytest core/tests/performance/ -v --tb=short
```

Performance baselines are tracked over time to detect gradual degradation.

## Adding New Performance Tests

When adding new performance tests:

1. Use `time.perf_counter()` for high-resolution timing
2. Run operations multiple times and average results
3. Set realistic performance targets based on use cases
4. Include both typical and stress test scenarios
5. Document expected performance in test docstrings

Example:
```python
def test_new_operation_performance(self, handler):
    """Test new operation is fast (< 50ms)."""
    start_time = time.perf_counter()
    handler.new_operation()
    operation_time = (time.perf_counter() - start_time) * 1000
    
    assert operation_time < 50, f"Operation took {operation_time:.2f}ms"
    print(f"\n✓ New operation: {operation_time:.2f}ms")
```

## Performance Goals

Universal Input Device System performance goals:

- ✅ **Responsive**: All user interactions < 100ms
- ✅ **Scalable**: Handle 1,000+ items without lag
- ✅ **Efficient**: Minimal CPU and memory overhead
- ✅ **Smooth**: 60 FPS-equivalent for visual updates (< 16ms per frame)

## Benchmarking

For detailed profiling:

```bash
# Profile selector with cProfile
python -m cProfile -s cumtime core/tests/performance/test_selector_performance.py

# Profile with line_profiler
kernprof -l -v core/input/selector_framework.py

# Memory profiling
python -m memory_profiler core/tests/performance/test_selector_performance.py
```

## Results Archive

Performance test results are archived for trend analysis:

```
core/tests/performance/results/
├── 2025-12-13_selector_results.txt
├── 2025-12-13_mouse_results.txt
└── 2025-12-13_keypad_results.txt
```

Track these over time to ensure performance doesn't degrade with new features.
