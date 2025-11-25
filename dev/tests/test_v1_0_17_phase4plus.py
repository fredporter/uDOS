#!/usr/bin/env python3
"""
Tests for uCODE Debugger v1.0.17 Phase 4+ (Enhanced Features)
Tests breakpoint disable/enable, variable history tracking, and auto-profiling
"""

import unittest
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from core.uDOS_ucode import UCodeInterpreter


class TestDebuggerPhase4Plus(unittest.TestCase):
    """Test Phase 4+ enhanced debugger features"""

    def setUp(self):
        """Set up test interpreter with debug mode"""
        self.interpreter = UCodeInterpreter()
        self.interpreter.debug_mode = True
        self.debugger = self.interpreter.debugger

    def test_disable_enable_breakpoint(self):
        """Test disabling and enabling breakpoints"""
        # Set a breakpoint
        self.debugger.set_breakpoint(5)
        self.assertTrue(self.debugger.is_breakpoint_enabled(5))

        # Disable it
        self.debugger.disable_breakpoint(5)
        self.assertFalse(self.debugger.is_breakpoint_enabled(5))
        self.assertIn(5, self.debugger.disabled_breakpoints)
        self.assertIn(5, self.debugger.breakpoints)  # Still exists

        # Re-enable it
        self.debugger.enable_breakpoint(5)
        self.assertTrue(self.debugger.is_breakpoint_enabled(5))
        self.assertNotIn(5, self.debugger.disabled_breakpoints)

    def test_disabled_breakpoint_no_pause(self):
        """Test that disabled breakpoints don't pause execution"""
        self.debugger.set_breakpoint(5)
        self.debugger.disable_breakpoint(5)

        # Should not pause on disabled breakpoint
        self.assertFalse(self.debugger.should_pause(5))

    def test_enable_nonexistent_breakpoint(self):
        """Test enabling a breakpoint that doesn't exist"""
        # Should not raise error, just not be in disabled set
        self.debugger.enable_breakpoint(99)
        self.assertNotIn(99, self.debugger.disabled_breakpoints)

    def test_disable_nonexistent_breakpoint(self):
        """Test disabling a breakpoint that doesn't exist"""
        # Should add to disabled set even if not in breakpoints
        self.debugger.disable_breakpoint(99)
        self.assertIn(99, self.debugger.disabled_breakpoints)

    def test_variable_history_tracking(self):
        """Test tracking variable value changes"""
        # Track a variable change
        self.debugger.track_variable_change('x', None, 10, 1)
        self.debugger.track_variable_change('x', 10, 20, 2)
        self.debugger.track_variable_change('x', 20, 30, 5)

        # Get history
        history = self.debugger.get_variable_history('x')
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['old_value'], None)
        self.assertEqual(history[0]['new_value'], 10)
        self.assertEqual(history[0]['line'], 1)
        self.assertEqual(history[1]['old_value'], 10)
        self.assertEqual(history[1]['new_value'], 20)
        self.assertEqual(history[2]['new_value'], 30)

    def test_variable_history_multiple_vars(self):
        """Test tracking multiple variables independently"""
        self.debugger.track_variable_change('x', 0, 10, 1)
        self.debugger.track_variable_change('y', 0, 20, 2)
        self.debugger.track_variable_change('x', 10, 15, 3)

        x_history = self.debugger.get_variable_history('x')
        y_history = self.debugger.get_variable_history('y')

        self.assertEqual(len(x_history), 2)
        self.assertEqual(len(y_history), 1)
        self.assertEqual(x_history[0]['new_value'], 10)
        self.assertEqual(x_history[1]['new_value'], 15)
        self.assertEqual(y_history[0]['new_value'], 20)

    def test_variable_history_nonexistent(self):
        """Test getting history for non-tracked variable"""
        history = self.debugger.get_variable_history('nonexistent')
        self.assertEqual(history, [])

    def test_clear_variable_history_specific(self):
        """Test clearing history for specific variable"""
        self.debugger.track_variable_change('x', 0, 10, 1)
        self.debugger.track_variable_change('y', 0, 20, 2)

        self.debugger.clear_variable_history('x')

        self.assertEqual(self.debugger.get_variable_history('x'), [])
        self.assertEqual(len(self.debugger.get_variable_history('y')), 1)

    def test_clear_variable_history_all(self):
        """Test clearing all variable history"""
        self.debugger.track_variable_change('x', 0, 10, 1)
        self.debugger.track_variable_change('y', 0, 20, 2)

        self.debugger.clear_variable_history()

        self.assertEqual(self.debugger.get_variable_history('x'), [])
        self.assertEqual(self.debugger.get_variable_history('y'), [])
        self.assertEqual(len(self.debugger.variable_history), 0)

    def test_auto_profile_initialization(self):
        """Test auto_profile flag is initialized correctly"""
        self.assertFalse(self.debugger.auto_profile)

    def test_auto_profile_toggle(self):
        """Test enabling and disabling auto-profiling"""
        self.debugger.auto_profile = False
        self.assertFalse(self.debugger.auto_profile)

        self.debugger.auto_profile = True
        self.assertTrue(self.debugger.auto_profile)

        self.debugger.auto_profile = False
        self.assertFalse(self.debugger.auto_profile)

    def test_record_line_time(self):
        """Test recording line execution times"""
        # Record some execution times
        self.debugger.record_line_time(1, 0.001)
        self.debugger.record_line_time(2, 0.002)
        self.debugger.record_line_time(1, 0.001)  # Same line again

        # Check profiling data
        self.assertIn(1, self.debugger.line_execution_times)
        self.assertIn(2, self.debugger.line_execution_times)

        line1_times = self.debugger.line_execution_times[1]
        self.assertEqual(len(line1_times), 2)  # Executed twice
        self.assertAlmostEqual(sum(line1_times), 0.002, places=6)

    def test_breakpoint_list_shows_disabled_status(self):
        """Test that breakpoint info includes enabled/disabled status"""
        self.debugger.set_breakpoint(5)
        self.debugger.set_breakpoint(10)
        self.debugger.disable_breakpoint(10)

        # Check enabled status
        self.assertTrue(self.debugger.is_breakpoint_enabled(5))
        self.assertFalse(self.debugger.is_breakpoint_enabled(10))

    def test_conditional_breakpoint_can_be_disabled(self):
        """Test that conditional breakpoints can be disabled"""
        self.debugger.set_breakpoint(5, "x > 10")
        self.debugger.disable_breakpoint(5)

        # Should be disabled
        self.assertFalse(self.debugger.is_breakpoint_enabled(5))
        self.assertFalse(self.debugger.should_pause(5))

        # But condition should still be there
        self.assertEqual(self.debugger.conditional_breakpoints.get(5), "x > 10")

    def test_history_includes_timestamp(self):
        """Test that history entries include timestamps"""
        self.debugger.track_variable_change('x', 0, 10, 1)
        history = self.debugger.get_variable_history('x')

        self.assertEqual(len(history), 1)
        self.assertIn('timestamp', history[0])
        # Should be ISO format
        self.assertRegex(history[0]['timestamp'], r'\d{4}-\d{2}-\d{2}')


class TestDebuggerPhase4PlusIntegration(unittest.TestCase):
    """Integration tests for Phase 4+ features with actual script execution"""

    def setUp(self):
        """Set up test interpreter"""
        self.interpreter = UCodeInterpreter()

    def test_auto_profile_during_execution(self):
        """Test that auto-profiling works during script execution"""
        script = [
            "LET x = 0",
            "REPEAT 5",
            "  LET x = x + 1",
            "END",
            "PRINT x"
        ]

        self.interpreter.debug_mode = True
        self.interpreter.debugger.auto_profile = True

        # Execute script using _execute_lines
        results = []
        self.interpreter._execute_lines(script, results, start_index=0)

        # Should have profiling data
        profile = self.interpreter.debugger.get_performance_profile()
        self.assertGreater(len(profile['lines']), 0)

        # Some lines should have been executed
        self.assertGreater(len(self.interpreter.debugger.line_execution_times), 0)

    def test_variable_history_during_execution(self):
        """Test variable history tracking during execution"""
        self.interpreter.debug_mode = True

        # Manually track during execution (in real execution, SET would call this)
        # For now, manually track to verify the mechanism
        self.interpreter.debugger.track_variable_change('x', None, 10, 1)
        self.interpreter.debugger.track_variable_change('x', 10, 20, 2)
        self.interpreter.debugger.track_variable_change('x', 20, 30, 3)

        # Check history
        history = self.interpreter.debugger.get_variable_history('x')
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['new_value'], 10)
        self.assertEqual(history[1]['new_value'], 20)
        self.assertEqual(history[2]['new_value'], 30)

    def test_disabled_breakpoint_allows_execution(self):
        """Test that disabled breakpoints don't stop execution"""
        self.interpreter.debug_mode = True
        self.interpreter.debugger.set_breakpoint(3)
        self.interpreter.debugger.disable_breakpoint(3)

        # Test that should_pause returns False for disabled breakpoint
        self.assertFalse(self.interpreter.debugger.should_pause(3))

        # Verify breakpoint exists but is disabled
        self.assertIn(3, self.interpreter.debugger.breakpoints)
        self.assertIn(3, self.interpreter.debugger.disabled_breakpoints)


def run_tests():
    """Run all Phase 4+ tests"""
    print("\n" + "=" * 70)
    print("uCODE Debugger v1.0.17 - Phase 4+ Enhanced Features Tests")
    print("=" * 70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDebuggerPhase4Plus))
    suite.addTests(loader.loadTestsFromTestCase(TestDebuggerPhase4PlusIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
