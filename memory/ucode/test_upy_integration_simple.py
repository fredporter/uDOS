"""
uPY v2.0.2 Integration Tests (Simplified)

Integration tests combining features using execute_command() API.
Tests realistic workflows combining math, lists, and file I/O.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.runtime.upy_runtime_v2 import UPYRuntime


def test_math_with_lists():
    """Test mathematical operations combined with list operations."""
    print("\n=== Test: Math + Lists Integration ===")

    runtime = UPYRuntime()

    # Create list of numbers
    runtime.execute_command('LIST', ['CREATE', 'numbers', '10', '20', '30'])

    # Get first two numbers and add them
    val1 = runtime.execute_command('LIST', ['GET', 'numbers', '0'])
    val2 = runtime.execute_command('LIST', ['GET', 'numbers', '1'])

    # Store in variables
    runtime.set_variable('a', val1)
    runtime.set_variable('b', val2)

    # Use math parser through SET command
    runtime.execute_command('SET', ['sum', '{$a} + {$b}'])
    result = runtime.get_variable('sum')

    assert result == 30 or result == '30', f"Expected '30', got {result}"
    print(f"✅ Math + Lists: 10 + 20 = {result}")

    # Create result list and append
    runtime.execute_command('LIST', ['CREATE', 'results'])
    runtime.execute_command('LIST', ['APPEND', 'results', result])

    results_list = runtime.get_variable('results')
    assert len(results_list) == 1, f"Expected 1 item, got {len(results_list)}"
    assert results_list[0] == 30 or result == '30', f"Expected '30', got {results_list[0]}"
    print(f"✅ Result stored in list: {results_list}")

    print("✅ Math + Lists integration test passed!")


def test_lists_with_file_io():
    """Test list operations combined with file I/O."""
    print("\n=== Test: Lists + File I/O Integration ===")

    runtime = UPYRuntime()

    # Create test directory
    test_dir = tempfile.mkdtemp(prefix='upy_integration_')
    test_file = os.path.join(test_dir, 'list_data.json')

    try:
        # Create list
        runtime.execute_command('LIST', ['CREATE', 'fruits', 'apple', 'banana', 'cherry'])
        fruits = runtime.get_variable('fruits')  # Get value after creation

        # Save to JSON (JSON WRITE expects variable name)
        runtime.execute_command('JSON', ['WRITE', test_file, 'fruits'])  # Pass variable name, not value

        assert os.path.exists(test_file), "JSON file should be created"
        print(f"✅ List saved to JSON: {test_file}")

        # Load back
        runtime.execute_command('JSON', ['READ', test_file, 'loaded_fruits'])
        loaded = runtime.get_variable('loaded_fruits')

        assert loaded == fruits, f"Expected {fruits}, got {loaded}"
        print(f"✅ List loaded from JSON: {loaded}")

        # Modify loaded list
        runtime.execute_command('LIST', ['APPEND', 'loaded_fruits', 'orange'])
        modified = runtime.get_variable('loaded_fruits')

        assert len(modified) == 4, f"Expected 4 items, got {len(modified)}"
        print(f"✅ Modified list: {modified}")

    finally:
        shutil.rmtree(test_dir)
        print(f"✅ Cleaned up: {test_dir}")

    print("✅ Lists + File I/O integration test passed!")


def test_math_with_file_io():
    """Test mathematical calculations combined with file I/O."""
    print("\n=== Test: Math + File I/O Integration ===")

    runtime = UPYRuntime()

    # Create test directory
    test_dir = tempfile.mkdtemp(prefix='upy_integration_')
    calc_file = os.path.join(test_dir, 'calculations.txt')

    try:
        # Perform calculations
        runtime.set_variable('x', '10')
        runtime.set_variable('y', '5')

        runtime.execute_command('SET', ['sum', '{$x} + {$y}'])
        runtime.execute_command('SET', ['product', '{$x} * {$y}'])
        runtime.execute_command('SET', ['power', '{$x} ** 2'])

        sum_val = runtime.get_variable('sum')
        product_val = runtime.get_variable('product')
        power_val = runtime.get_variable('power')

        assert sum_val == 15 or result == '15', f"Expected '15', got {sum_val}"
        assert product_val == 50 or result == '50', f"Expected '50', got {product_val}"
        assert power_val == 100 or result == '100', f"Expected '100', got {power_val}"
        print(f"✅ Calculations: sum={sum_val}, product={product_val}, power={power_val}")

        # Write results to file
        results_text = f"Sum: {sum_val}\nProduct: {product_val}\nPower: {power_val}"
        runtime.execute_command('FILE', ['WRITE', calc_file, results_text])

        assert os.path.exists(calc_file), "Results file should be created"
        print(f"✅ Results saved to file: {calc_file}")

        # Read back and verify
        runtime.execute_command('FILE', ['READ', calc_file, 'file_content'])
        content = runtime.get_variable('file_content')

        assert 'Sum: 15' in content, f"Expected 'Sum: 15' in {content}"
        assert 'Product: 50' in content, f"Expected 'Product: 50' in {content}"
        assert 'Power: 100' in content, f"Expected 'Power: 100' in {content}"
        print(f"✅ Results verified from file")

    finally:
        shutil.rmtree(test_dir)
        print(f"✅ Cleaned up: {test_dir}")

    print("✅ Math + File I/O integration test passed!")


def test_complete_workflow():
    """Test complete workflow combining all features."""
    print("\n=== Test: Complete Workflow (All Features) ===")

    runtime = UPYRuntime()

    # Create test directory
    test_dir = tempfile.mkdtemp(prefix='upy_integration_')
    scores_file = os.path.join(test_dir, 'scores.json')
    report_file = os.path.join(test_dir, 'report.txt')

    try:
        # Step 1: Create test scores list
        runtime.execute_command('LIST', ['CREATE', 'scores', '85', '92', '78', '95', '88'])
        scores = runtime.get_variable('scores')
        print(f"✅ Step 1: Created scores list: {scores}")

        # Step 2: Save to JSON
        runtime.execute_command('JSON', ['WRITE', scores_file, str(scores)])
        assert os.path.exists(scores_file), "Scores file should exist"
        print(f"✅ Step 2: Saved to JSON")

        # Step 3: Calculate statistics using math operations
        # Get each score
        s1 = runtime.execute_command('LIST', ['GET', 'scores', '0'])
        s2 = runtime.execute_command('LIST', ['GET', 'scores', '1'])
        s3 = runtime.execute_command('LIST', ['GET', 'scores', '2'])
        s4 = runtime.execute_command('LIST', ['GET', 'scores', '3'])
        s5 = runtime.execute_command('LIST', ['GET', 'scores', '4'])

        # Calculate sum
        runtime.set_variable('sum', '0')
        runtime.execute_command('SET', ['sum', f'{{$sum}} + {s1}'])
        runtime.execute_command('SET', ['sum', f'{{$sum}} + {s2}'])
        runtime.execute_command('SET', ['sum', f'{{$sum}} + {s3}'])
        runtime.execute_command('SET', ['sum', f'{{$sum}} + {s4}'])
        runtime.execute_command('SET', ['sum', f'{{$sum}} + {s5}'])

        total_sum = runtime.get_variable('sum')
        print(f"✅ Step 3: Calculated sum: {total_sum}")

        # Calculate average
        count = runtime.execute_command('LIST', ['SIZE', 'scores'])
        runtime.set_variable('count', str(count))
        runtime.execute_command('SET', ['average', '{$sum} / {$count}'])
        average = runtime.get_variable('average')

        assert average == 87.6 or result == '87.6', f"Expected '87.6', got {average}"
        print(f"✅ Step 4: Calculated average: {average}")

        # Step 5: Generate report
        min_score = min([int(s) for s in scores])
        max_score = max([int(s) for s in scores])

        report = f"""Test Scores Report
==================
Number of scores: {count}
Total sum: {total_sum}
Average: {average}
Minimum: {min_score}
Maximum: {max_score}
"""

        runtime.execute_command('FILE', ['WRITE', report_file, report])
        assert os.path.exists(report_file), "Report file should exist"
        print(f"✅ Step 5: Generated report")

        # Step 6: Verify report content
        runtime.execute_command('FILE', ['READ', report_file, 'report_content'])
        content = runtime.get_variable('report_content')

        assert 'Average: 87.6' in content, "Report should contain average"
        print(f"✅ Step 6: Verified report content")

        print("✅ Complete workflow test passed!")

    finally:
        shutil.rmtree(test_dir)
        print(f"✅ Cleaned up: {test_dir}")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 70)
    print("🧪 uPY v2.0.2 INTEGRATION TEST SUITE (Simplified)")
    print("=" * 70)
    print("\nTesting feature combinations using execute_command() API\n")

    tests = [
        test_math_with_lists,
        test_lists_with_file_io,
        test_math_with_file_io,
        test_complete_workflow
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {e}")
            failed += 1
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    total = passed + failed
    if failed == 0:
        print(f"✅ ALL {total} INTEGRATION TESTS PASSED!")
    else:
        print(f"⚠️  {passed}/{total} tests passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
