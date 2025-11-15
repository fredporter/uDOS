#!/usr/bin/env python3
"""
v1.0.17 Phase 4: Tests for advanced debugging features.
Tests conditional breakpoints, variable modification, and performance profiling.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.uDOS_ucode import UCodeInterpreter
from core.commands.system_handler import SystemCommandHandler


class MockViewport:
    pass


class MockLogger:
    pass


class MockParser:
    def __init__(self):
        self.ucode = UCodeInterpreter()
        self.ucode.global_scope.set('x', 10)
        self.ucode.global_scope.set('y', 20)
        self.ucode.global_scope.set('counter', 5)


class MockGrid:
    pass


def test_conditional_breakpoint():
    """Test conditional breakpoints."""
    print("Testing conditional breakpoints...")

    interp = UCodeInterpreter()
    interp.global_scope.set('x', 5)

    # Set conditional breakpoint
    interp.debugger.set_breakpoint(10, "x > 3")

    # Should pause when x > 3
    should_pause = interp.debugger.should_pause(10)
    if should_pause:
        print("✅ Conditional breakpoint pauses when condition is true")
    else:
        print("❌ Conditional breakpoint failed to pause")
        return False

    # Change x so condition is false
    interp.global_scope.set('x', 1)
    interp.debugger.state = interp.debugger.state.NOT_STARTED  # Reset state

    # Should NOT pause when x <= 3
    should_pause = interp.debugger.should_pause(10)
    if not should_pause:
        print("✅ Conditional breakpoint doesn't pause when condition is false")
        return True
    else:
        print("❌ Conditional breakpoint paused incorrectly")
        return False


def test_breakpoint_hit_count():
    """Test breakpoint hit counting."""
    print("\nTesting breakpoint hit count...")

    interp = UCodeInterpreter()
    interp.debugger.set_breakpoint(10)

    # Hit the breakpoint 3 times
    for i in range(3):
        interp.debugger.should_pause(10)
        interp.debugger.state = interp.debugger.state.NOT_STARTED  # Reset

    hit_count = interp.debugger.breakpoint_hit_counts.get(10, 0)

    if hit_count == 3:
        print(f"✅ Breakpoint hit count tracked correctly: {hit_count}")
        return True
    else:
        print(f"❌ Breakpoint hit count wrong: {hit_count} (expected 3)")
        return False


def test_breakpoint_info():
    """Test getting breakpoint information."""
    print("\nTesting breakpoint info...")

    interp = UCodeInterpreter()

    # Set regular breakpoint
    interp.debugger.set_breakpoint(10)

    # Set conditional breakpoint
    interp.debugger.set_breakpoint(20, "x > 5")

    # Hit them
    interp.debugger.should_pause(10)
    interp.debugger.should_pause(20)

    # Get info
    info10 = interp.debugger.get_breakpoint_info(10)
    info20 = interp.debugger.get_breakpoint_info(20)

    if info10 and info10['hit_count'] == 1 and info10['condition'] is None:
        print("✅ Regular breakpoint info correct")
    else:
        print("❌ Regular breakpoint info wrong")
        return False

    if info20 and info20['hit_count'] == 1 and info20['condition'] == "x > 5":
        print("✅ Conditional breakpoint info correct")
        return True
    else:
        print("❌ Conditional breakpoint info wrong")
        return False


def test_set_variable():
    """Test variable modification during debugging."""
    print("\nTesting variable modification...")

    interp = UCodeInterpreter()
    interp.global_scope.set('x', 10)

    # Modify variable
    result = interp.debugger.set_variable('x', 42)

    # Check it was changed
    new_value = interp.global_scope.get('x')

    if new_value == 42:
        print(f"✅ Variable modified successfully: x = {new_value}")
        return True
    else:
        print(f"❌ Variable modification failed: x = {new_value} (expected 42)")
        return False


def test_performance_profiling():
    """Test performance profiling."""
    print("\nTesting performance profiling...")

    interp = UCodeInterpreter()

    # Record some execution times
    interp.debugger.record_line_time(10, 0.001)
    interp.debugger.record_line_time(10, 0.002)
    interp.debugger.record_line_time(20, 0.005)
    interp.debugger.record_line_time(30, 0.010)

    # Get profile
    profile = interp.debugger.get_performance_profile()

    # Check data
    if 10 in profile['lines']:
        line10 = profile['lines'][10]
        if line10['executions'] == 2:
            print(f"✅ Line execution count tracked: {line10['executions']}")
        else:
            print(f"❌ Wrong execution count: {line10['executions']}")
            return False

        if abs(line10['avg_time'] - 0.0015) < 0.0001:
            print(f"✅ Average time calculated correctly: {line10['avg_time']:.6f}s")
        else:
            print(f"❌ Wrong average time: {line10['avg_time']:.6f}s")
            return False
    else:
        print("❌ Line 10 not in profile")
        return False

    # Check slowest lines
    if profile['slowest_lines']:
        slowest = profile['slowest_lines'][0]
        if slowest[0] == 30:  # Line 30 should be slowest (0.010s)
            print(f"✅ Slowest line identified correctly: line {slowest[0]}")
            return True
        else:
            print(f"❌ Wrong slowest line: {slowest[0]}")
            return False
    else:
        print("❌ No slowest lines found")
        return False


def test_modify_command():
    """Test MODIFY command."""
    print("\nTesting MODIFY command...")

    handler = SystemCommandHandler(
        theme="dungeon",
        connection=None,
        viewport=MockViewport(),
        user_manager=None,
        history=None,
        command_history=None,
        logger=MockLogger()
    )

    parser = MockParser()

    # Modify a variable
    result = handler.handle_modify(['x', '=', '99'], MockGrid(), parser)

    if '✓' in result or '✅' in result:
        print("✅ MODIFY command executed")

        # Check value was changed
        new_value = parser.ucode.global_scope.get('x')
        if new_value == 99:
            print(f"✅ Variable modified via command: x = {new_value}")
            return True
        else:
            print(f"❌ Variable not modified: x = {new_value}")
            return False
    else:
        print(f"❌ MODIFY command failed: {result}")
        return False


def test_profile_command():
    """Test PROFILE command."""
    print("\nTesting PROFILE command...")

    handler = SystemCommandHandler(
        theme="dungeon",
        connection=None,
        viewport=MockViewport(),
        user_manager=None,
        history=None,
        command_history=None,
        logger=MockLogger()
    )

    parser = MockParser()

    # Add some profiling data
    parser.ucode.debugger.record_line_time(10, 0.001)
    parser.ucode.debugger.record_line_time(20, 0.005)

    # Get profile
    result = handler.handle_profile([], MockGrid(), parser)

    if 'PERFORMANCE PROFILE' in result:
        print("✅ PROFILE command shows data")
        return True
    else:
        print("❌ PROFILE command failed")
        return False


def test_conditional_breakpoint_command():
    """Test BREAK with IF condition."""
    print("\nTesting BREAK <line> IF <condition> command...")

    handler = SystemCommandHandler(
        theme="dungeon",
        connection=None,
        viewport=MockViewport(),
        user_manager=None,
        history=None,
        command_history=None,
        logger=MockLogger()
    )

    parser = MockParser()

    # Set conditional breakpoint
    result = handler.handle_breakpoint(['10', 'IF', 'x', '>', '5'], MockGrid(), parser)

    if 'Conditional breakpoint' in result:
        print("✅ Conditional breakpoint set via command")

        # Check it's in the debugger
        info = parser.ucode.debugger.get_breakpoint_info(10)
        if info and info['condition'] == 'x > 5':
            print(f"✅ Condition stored correctly: {info['condition']}")
            return True
        else:
            print(f"❌ Condition not stored correctly")
            return False
    else:
        print(f"❌ Conditional breakpoint command failed: {result}")
        return False


def test_break_list_with_details():
    """Test BREAK LIST shows hit counts and conditions."""
    print("\nTesting BREAK LIST with details...")

    handler = SystemCommandHandler(
        theme="dungeon",
        connection=None,
        viewport=MockViewport(),
        user_manager=None,
        history=None,
        command_history=None,
        logger=MockLogger()
    )

    parser = MockParser()

    # Set breakpoints
    parser.ucode.debugger.set_breakpoint(10)
    parser.ucode.debugger.set_breakpoint(20, "x > 10")

    # Hit them
    parser.ucode.debugger.should_pause(10)
    parser.ucode.debugger.should_pause(10)

    # List breakpoints
    result = handler.handle_breakpoint(['LIST'], MockGrid(), parser)

    if 'hits: 2' in result:
        print("✅ Hit counts shown in BREAK LIST")
    else:
        print("❌ Hit counts not shown")
        return False

    if 'IF x > 10' in result:
        print("✅ Conditions shown in BREAK LIST")
        return True
    else:
        print("❌ Conditions not shown")
        return False


def run_all_tests():
    """Run all Phase 4 tests."""
    print("=" * 80)
    print("uCODE v1.0.17 Phase 4 - Advanced Debugging Tests".center(80))
    print("=" * 80)
    print()

    tests = [
        test_conditional_breakpoint,
        test_breakpoint_hit_count,
        test_breakpoint_info,
        test_set_variable,
        test_performance_profiling,
        test_modify_command,
        test_profile_command,
        test_conditional_breakpoint_command,
        test_break_list_with_details,
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
