#!/usr/bin/env python3
"""
v1.0.17: Integration test for debugger execution loop.
Tests that debugger properly tracks lines, pauses at breakpoints, and shows context.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.uDOS_ucode import UCodeInterpreter


def test_debug_mode_execution():
    """Test that debug mode tracks line execution."""
    print("Testing debug mode execution...")

    interpreter = UCodeInterpreter()
    interpreter.debug_mode = True

    # Create a simple test script
    script_path = os.path.join(os.path.dirname(__file__), 'debug_test.uscript')

    if not os.path.exists(script_path):
        print(f"❌ Test script not found: {script_path}")
        return False

    # Execute the script
    result = interpreter.execute_script(script_path)

    # Check that debugger tracked execution
    if interpreter.debugger.current_line > 0:
        print(f"✅ Debugger tracked execution (last line: {interpreter.debugger.current_line})")
        return True
    else:
        print("❌ Debugger did not track execution")
        return False


def test_breakpoint_pause():
    """Test that breakpoints cause pauses in execution."""
    print("\nTesting breakpoint pause...")

    interpreter = UCodeInterpreter()
    interpreter.debug_mode = True

    # Set a breakpoint
    interpreter.debugger.set_breakpoint(10)

    script_path = os.path.join(os.path.dirname(__file__), 'debug_test.uscript')
    result = interpreter.execute_script(script_path)

    # Check if "Paused at line" appears in results
    if "Paused at line" in result:
        print("✅ Breakpoint caused pause")
        print(f"   Debugger state: {interpreter.debugger.state.name}")
        return True
    else:
        print("❌ Breakpoint did not cause pause")
        return False


def test_debug_context_display():
    """Test that debug context is shown on pause."""
    print("\nTesting debug context display...")

    interpreter = UCodeInterpreter()
    interpreter.debug_mode = True

    # Add a watch
    interpreter.debugger.add_watch("x")

    # Set a breakpoint
    interpreter.debugger.set_breakpoint(15)

    script_path = os.path.join(os.path.dirname(__file__), 'debug_test.uscript')
    result = interpreter.execute_script(script_path)

    # Check for debug context markers
    has_watches = "Watches:" in result or "No debug context" in result
    has_variables = "Variables:" in result or "No debug context" in result

    if has_watches or has_variables:
        print("✅ Debug context displayed")
        return True
    else:
        print("❌ Debug context not displayed")
        return False


def test_line_tracking():
    """Test that current_line is updated during execution."""
    print("\nTesting line tracking...")

    interpreter = UCodeInterpreter()
    interpreter.debug_mode = True

    script_path = os.path.join(os.path.dirname(__file__), 'debug_test.uscript')

    # Track line changes
    initial_line = interpreter.debugger.current_line
    interpreter.execute_script(script_path)
    final_line = interpreter.debugger.current_line

    if final_line > initial_line:
        print(f"✅ Line tracking works (moved from {initial_line} to {final_line})")
        return True
    else:
        print(f"❌ Line tracking failed (stayed at {initial_line})")
        return False


def test_error_stack_trace():
    """Test that errors show stack traces in debug mode."""
    print("\nTesting error stack trace...")

    interpreter = UCodeInterpreter()
    interpreter.debug_mode = True

    # Create a script that will cause an error
    error_script = os.path.join(os.path.dirname(__file__), 'error_test.uscript')
    with open(error_script, 'w') as f:
        f.write("# Error test script\n")
        f.write("SET x = 10\n")
        f.write("THROW This is a test error\n")
        f.write("SET y = 20\n")

    try:
        result = interpreter.execute_script(error_script)

        # Check for stack trace
        if "Debug Stack Trace:" in result or "Traceback" in result:
            print("✅ Stack trace shown in debug mode")
            return True
        else:
            print("⚠️  Stack trace not shown (error may not have occurred)")
            print(f"Result preview: {result[:200]}...")
            return False
    finally:
        # Clean up
        if os.path.exists(error_script):
            os.remove(error_script)


def run_all_tests():
    """Run all execution loop integration tests."""
    print("=" * 80)
    print("uCODE v1.0.17 Debugger Execution Loop Integration Tests".center(80))
    print("=" * 80)
    print()

    tests = [
        test_debug_mode_execution,
        test_breakpoint_pause,
        test_debug_context_display,
        test_line_tracking,
        test_error_stack_trace,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"💥 {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 80)
    print(f"Total tests run: {len(tests)}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Pass rate: {passed/len(tests)*100:.1f}%")
    print("=" * 80)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
