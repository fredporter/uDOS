#!/usr/bin/env python3
"""
uCODE v1.0.17 Debugger Test Suite
Tests interactive debugging features including breakpoints, stepping, and inspection
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.uDOS_ucode import UCodeInterpreter, UCodeDebugger, DebugState


class TestDebugger:
    """Test suite for uCODE debugger."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.interpreter = UCodeInterpreter()

    def test(self, name: str, condition: bool):
        """Run a test and track results."""
        self.tests_run += 1
        if condition:
            print(f"✅ {name}")
            self.tests_passed += 1
        else:
            print(f"❌ {name}")

    def run_all_tests(self):
        """Run all debugger tests."""
        print("=" * 60)
        print("uCODE v1.0.17 Debugger Test Suite".center(60))
        print("=" * 60)
        print()

        # Debugger initialization tests
        self.test_debugger_initialization()

        # Breakpoint tests
        self.test_set_breakpoint()
        self.test_clear_breakpoint()
        self.test_clear_all_breakpoints()
        self.test_list_breakpoints()

        # Step execution tests
        self.test_step_modes()
        self.test_should_pause()

        # Variable inspection tests
        self.test_inspect_variable()
        self.test_get_context()

        # Watch expression tests
        self.test_add_watch()
        self.test_remove_watch()
        self.test_evaluate_watches()

        # Summary
        print()
        print("=" * 60)
        print(f"Total tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Pass rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        print("=" * 60)

        return self.tests_passed == self.tests_run

    def test_debugger_initialization(self):
        """Test debugger initializes correctly."""
        debugger = self.interpreter.debugger

        self.test("Debugger exists", debugger is not None)
        self.test("Initial state is NOT_STARTED", debugger.state == DebugState.NOT_STARTED)
        self.test("No breakpoints initially", len(debugger.breakpoints) == 0)
        self.test("Current line is 0", debugger.current_line == 0)
        self.test("Call stack empty", len(debugger.call_stack) == 0)
        self.test("No watch expressions", len(debugger.watch_expressions) == 0)

    def test_set_breakpoint(self):
        """Test setting breakpoints."""
        debugger = self.interpreter.debugger
        debugger.breakpoints.clear()  # Reset

        result = debugger.set_breakpoint(10)
        self.test("Set breakpoint returns message", "Breakpoint set" in result)
        self.test("Breakpoint added to set", 10 in debugger.breakpoints)

        debugger.set_breakpoint(20)
        self.test("Multiple breakpoints", len(debugger.breakpoints) == 2)

    def test_clear_breakpoint(self):
        """Test clearing specific breakpoint."""
        debugger = self.interpreter.debugger
        debugger.breakpoints = {10, 20, 30}

        result = debugger.clear_breakpoint(20)
        self.test("Clear breakpoint returns message", "cleared" in result)
        self.test("Breakpoint removed", 20 not in debugger.breakpoints)
        self.test("Other breakpoints remain", len(debugger.breakpoints) == 2)

        result = debugger.clear_breakpoint(99)
        self.test("Clear nonexistent breakpoint", "No breakpoint" in result)

    def test_clear_all_breakpoints(self):
        """Test clearing all breakpoints."""
        debugger = self.interpreter.debugger
        debugger.breakpoints = {10, 20, 30}

        result = debugger.clear_breakpoint()
        self.test("Clear all returns count", "3" in result)
        self.test("All breakpoints cleared", len(debugger.breakpoints) == 0)

    def test_list_breakpoints(self):
        """Test listing breakpoints."""
        debugger = self.interpreter.debugger
        debugger.breakpoints.clear()

        result = debugger.list_breakpoints()
        self.test("Empty breakpoints message", "No breakpoints" in result)

        debugger.breakpoints = {10, 20}
        result = debugger.list_breakpoints()
        self.test("List shows breakpoints", "Line 10" in result and "Line 20" in result)

    def test_step_modes(self):
        """Test step execution modes."""
        debugger = self.interpreter.debugger

        debugger.step()
        self.test("STEP sets mode", debugger.step_mode == 'STEP')
        self.test("STEP sets state STEPPING", debugger.state == DebugState.STEPPING)

        debugger.step_into()
        self.test("STEP INTO sets mode", debugger.step_mode == 'STEP_INTO')

        debugger.call_stack = ['func1', 'func2']
        debugger.step_out()
        self.test("STEP OUT sets mode", debugger.step_mode == 'STEP_OUT')
        self.test("STEP OUT sets target depth", debugger.step_target_depth == 1)

        debugger.continue_execution()
        self.test("CONTINUE clears step mode", debugger.step_mode is None)
        self.test("CONTINUE sets state RUNNING", debugger.state == DebugState.RUNNING)

    def test_should_pause(self):
        """Test pause logic."""
        debugger = self.interpreter.debugger
        debugger.breakpoints = {10, 20}
        debugger.state = DebugState.RUNNING

        # Test breakpoint pause
        result = debugger.should_pause(10)
        self.test("Pauses at breakpoint", result == True)
        self.test("Sets state to PAUSED", debugger.state == DebugState.PAUSED)

        # Test step mode pause
        debugger.state = DebugState.STEPPING
        debugger.step_mode = 'STEP'
        result = debugger.should_pause(15)
        self.test("Pauses in STEP mode", result == True)
        self.test("Clears step mode after pause", debugger.step_mode is None)

        # Test no pause
        debugger.state = DebugState.RUNNING
        debugger.step_mode = None
        result = debugger.should_pause(15)
        self.test("No pause when running without breakpoint", result == False)

    def test_inspect_variable(self):
        """Test variable inspection."""
        debugger = self.interpreter.debugger
        self.interpreter.current_scope.set("test_var", "test_value")

        value = debugger.inspect_variable("test_var")
        self.test("Inspects existing variable", value == "test_value")

        # v1.0.17: inspect_variable now returns None instead of raising error
        value = debugger.inspect_variable("nonexistent")
        self.test("Returns None for nonexistent variable", value is None)

    def test_get_context(self):
        """Test getting execution context."""
        debugger = self.interpreter.debugger
        debugger.current_line = 42
        debugger.current_file = "test.uscript"
        debugger.breakpoints = {10, 20}
        self.interpreter.current_scope.set("x", 100)

        context = debugger.get_context()
        self.test("Context has line number", context['line'] == 42)
        self.test("Context has file name", context['file'] == "test.uscript")
        self.test("Context has state", context['state'] == debugger.state.value)
        self.test("Context has breakpoints", 10 in context['breakpoints'])
        self.test("Context has variables", 'x' in context['variables'])

    def test_add_watch(self):
        """Test adding watch expressions."""
        debugger = self.interpreter.debugger
        debugger.watch_expressions.clear()

        result = debugger.add_watch("x")
        self.test("Add watch returns message", "Watching" in result)
        self.test("Watch added", "x" in debugger.watch_expressions)

        debugger.add_watch("y + 10", "sum")
        self.test("Named watch added", "sum" in debugger.watch_expressions)

    def test_remove_watch(self):
        """Test removing watch expressions."""
        debugger = self.interpreter.debugger
        debugger.watch_expressions = {"x": "x", "sum": "y + 10"}

        result = debugger.remove_watch("x")
        self.test("Remove watch returns message", "Removed" in result)
        self.test("Watch removed", "x" not in debugger.watch_expressions)

        result = debugger.remove_watch("nonexistent")
        self.test("Remove nonexistent watch", "No watch" in result)

    def test_evaluate_watches(self):
        """Test evaluating watch expressions."""
        debugger = self.interpreter.debugger
        debugger.watch_expressions = {"x": "x", "unknown": "y"}
        self.interpreter.current_scope.set("x", 42)

        results = debugger.evaluate_watches()
        self.test("Evaluates existing variable", results["x"] == 42)
        self.test("Shows undefined for missing variable", "undefined" in results["unknown"])


if __name__ == "__main__":
    tester = TestDebugger()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
