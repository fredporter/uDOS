#!/usr/bin/env python3
"""
v1.0.17: Integration tests for debugger command handlers.
Tests DEBUG, BREAK, STEP, CONTINUE, INSPECT, WATCH, STACK commands.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.uDOS_ucode import UCodeInterpreter, UCodeDebugger
from core.commands.system_handler import SystemCommandHandler


class MockViewport:
    """Mock viewport for testing."""
    pass


class MockLogger:
    """Mock logger for testing."""
    pass


class MockParser:
    """Mock parser with ucode interpreter."""
    def __init__(self):
        self.ucode = UCodeInterpreter()
        # Set variables in global scope (overrides persisted variables)
        self.ucode.global_scope.set('x', 10)
        self.ucode.global_scope.set('y', 20)
        self.ucode.global_scope.set('name', 'test')


class MockGrid:
    """Mock grid for testing."""
    pass


def test_debug_help():
    """Test DEBUG command without params shows help."""
    handler = SystemCommandHandler(
        theme='dungeon',
        connection=None,
        viewport=MockViewport(),
        user_manager=None,
        history=None,
        command_history=None,
        logger=MockLogger()
    )

    result = handler.handle_debug([], MockGrid(), MockParser())
    assert 'uCODE DEBUGGER' in result
    assert 'DEBUG <script>' in result
    print("✅ DEBUG help displayed")


def test_debug_status():
    """Test DEBUG STATUS command."""
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
    result = handler.handle_debug(['STATUS'], MockGrid(), parser)
    assert 'DEBUGGER STATUS' in result
    assert 'State:' in result
    print("✅ DEBUG STATUS works")


def test_breakpoint_list_empty():
    """Test BREAK LIST with no breakpoints."""
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
    result = handler.handle_breakpoint(['LIST'], MockGrid(), parser)
    assert 'No breakpoints' in result
    print("✅ BREAK LIST (empty) works")


def test_breakpoint_set():
    """Test setting a breakpoint."""
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
    result = handler.handle_breakpoint(['10'], MockGrid(), parser)
    assert 'Breakpoint set at line 10' in result
    print("✅ BREAK <line> sets breakpoint")


def test_breakpoint_list_populated():
    """Test BREAK LIST after setting breakpoints."""
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

    # Set some breakpoints
    handler.handle_breakpoint(['10'], MockGrid(), parser)
    handler.handle_breakpoint(['20'], MockGrid(), parser)

    result = handler.handle_breakpoint(['LIST'], MockGrid(), parser)
    assert 'BREAKPOINTS' in result
    assert 'Line 10' in result
    assert 'Line 20' in result
    print("✅ BREAK LIST shows breakpoints")


def test_breakpoint_clear():
    """Test clearing a specific breakpoint."""
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

    # Set breakpoint
    handler.handle_breakpoint(['10'], MockGrid(), parser)

    # Clear it
    result = handler.handle_breakpoint(['CLEAR', '10'], MockGrid(), parser)
    assert 'Breakpoint cleared at line 10' in result
    print("✅ BREAK CLEAR <line> works")


def test_breakpoint_clear_all():
    """Test clearing all breakpoints."""
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

    # Set multiple breakpoints
    handler.handle_breakpoint(['10'], MockGrid(), parser)
    handler.handle_breakpoint(['20'], MockGrid(), parser)
    handler.handle_breakpoint(['30'], MockGrid(), parser)

    # Clear all
    result = handler.handle_breakpoint(['CLEAR', 'ALL'], MockGrid(), parser)
    assert 'All breakpoints cleared' in result
    print("✅ BREAK CLEAR ALL works")


def test_step_over():
    """Test STEP command (step over)."""
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
    result = handler.handle_step([], MockGrid(), parser)
    assert 'Stepped to next line' in result
    print("✅ STEP works")


def test_step_into():
    """Test STEP INTO command."""
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
    result = handler.handle_step(['INTO'], MockGrid(), parser)
    assert 'Stepped into function' in result
    print("✅ STEP INTO works")


def test_step_out():
    """Test STEP OUT command."""
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
    result = handler.handle_step(['OUT'], MockGrid(), parser)
    assert 'Stepped out of function' in result
    print("✅ STEP OUT works")


def test_continue():
    """Test CONTINUE command."""
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
    result = handler.handle_continue([], MockGrid(), parser)
    assert 'Continuing execution' in result
    print("✅ CONTINUE works")


def test_inspect_variable():
    """Test INSPECT <variable> command."""
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
    result = handler.handle_inspect(['x'], MockGrid(), parser)
    assert 'x = 10' in result
    print("✅ INSPECT <variable> works")


def test_inspect_all():
    """Test INSPECT ALL command."""
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
    result = handler.handle_inspect(['ALL'], MockGrid(), parser)
    assert 'VARIABLES' in result
    assert 'x' in result
    assert 'y' in result
    print("✅ INSPECT ALL works")


def test_watch_add():
    """Test adding a watch expression."""
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
    result = handler.handle_watch(['x'], MockGrid(), parser)
    assert 'Watching: x' in result
    print("✅ WATCH <variable> adds watch")


def test_watch_list():
    """Test WATCH LIST command."""
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

    # Add watches
    handler.handle_watch(['x'], MockGrid(), parser)
    handler.handle_watch(['y'], MockGrid(), parser)

    result = handler.handle_watch(['LIST'], MockGrid(), parser)
    assert 'WATCH LIST' in result
    assert 'x' in result
    print("✅ WATCH LIST works")


def test_watch_clear():
    """Test WATCH CLEAR <variable> command."""
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

    # Add watch
    handler.handle_watch(['x'], MockGrid(), parser)

    # Clear it
    result = handler.handle_watch(['CLEAR', 'x'], MockGrid(), parser)
    assert 'Watch removed: x' in result
    print("✅ WATCH CLEAR <variable> works")


def test_watch_clear_all():
    """Test WATCH CLEAR ALL command."""
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

    # Add multiple watches
    handler.handle_watch(['x'], MockGrid(), parser)
    handler.handle_watch(['y'], MockGrid(), parser)

    # Clear all
    result = handler.handle_watch(['CLEAR', 'ALL'], MockGrid(), parser)
    assert 'All watches cleared' in result
    print("✅ WATCH CLEAR ALL works")


def test_stack():
    """Test STACK command."""
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
    result = handler.handle_stack([], MockGrid(), parser)
    # Empty stack initially
    assert 'Call stack is empty' in result or 'CALL STACK' in result
    print("✅ STACK command works")


def run_all_tests():
    """Run all command integration tests."""
    print("=" * 80)
    print("uCODE v1.0.17 Debugger Command Integration Tests".center(80))
    print("=" * 80)
    print()

    tests = [
        test_debug_help,
        test_debug_status,
        test_breakpoint_list_empty,
        test_breakpoint_set,
        test_breakpoint_list_populated,
        test_breakpoint_clear,
        test_breakpoint_clear_all,
        test_step_over,
        test_step_into,
        test_step_out,
        test_continue,
        test_inspect_variable,
        test_inspect_all,
        test_watch_add,
        test_watch_list,
        test_watch_clear,
        test_watch_clear_all,
        test_stack,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__} error: {e}")
            failed += 1

    print()
    print("=" * 80)
    print(f"Total tests run: {len(tests)}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Pass rate: {passed/len(tests)*100:.1f}%")
    print("=" * 80)


if __name__ == '__main__':
    run_all_tests()
