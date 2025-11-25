"""
Unit tests for uCODE loop system (v1.0.14)

Tests LOOP/ENDLOOP/BREAK/CONTINUE commands.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import unittest
from core.uDOS_ucode import UCodeInterpreter


class TestLoopBasics(unittest.TestCase):
    """Test basic loop functionality"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_simple_loop(self):
        """Test basic LOOP with counter"""
        script = """
        SET counter = 0
        LOOP 5
          SET counter = ${LOOP_INDEX}
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # LOOP_INDEX is 0-indexed, so after 5 iterations it's 4
        self.assertEqual(self.interpreter.variables.get("counter"), "4")

    def test_loop_index_variable(self):
        """Test LOOP_INDEX special variable"""
        script = """
        SET sum = 0
        LOOP 3
          # LOOP_INDEX should be 0, 1, 2
          ECHO Iteration ${LOOP_INDEX}
        ENDLOOP
        """
        result = self.interpreter.execute_script(script)
        self.assertIsNotNone(result)

    def test_loop_zero_iterations(self):
        """Test LOOP with zero iterations"""
        script = """
        SET executed = false
        LOOP 0
          SET executed = true
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("executed"), "false")

    def test_loop_one_iteration(self):
        """Test LOOP with single iteration"""
        script = """
        SET count = 0
        LOOP 1
          SET count = 1
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("count"), "1")


class TestLoopControl(unittest.TestCase):
    """Test BREAK and CONTINUE commands"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_break_statement(self):
        """Test BREAK exits loop early"""
        script = """
        SET last_index = -1
        LOOP 10
          SET last_index = ${LOOP_INDEX}
          IF ${LOOP_INDEX} EQ 5
            BREAK
          ENDIF
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # Should break at index 5, so last_index should be 5
        self.assertEqual(self.interpreter.variables.get("last_index"), "5")

    def test_continue_statement(self):
        """Test CONTINUE skips to next iteration"""
        script = """
        SET processed = 0
        LOOP 5
          IF ${LOOP_INDEX} EQ 2
            CONTINUE
          ENDIF
          SET processed = ${LOOP_INDEX}
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # Should skip index 2, last processed should be 4
        self.assertEqual(self.interpreter.variables.get("processed"), "4")

    def test_break_in_nested_loop(self):
        """Test BREAK in nested loops"""
        script = """
        SET outer_break = false
        LOOP 5
          LOOP 5
            IF ${LOOP_INDEX} EQ 2
              SET outer_break = true
              BREAK
            ENDIF
          ENDLOOP
          IF ${outer_break} EQ true
            BREAK
          ENDIF
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("outer_break"), "true")


class TestNestedLoops(unittest.TestCase):
    """Test nested LOOP statements"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_nested_loop_basic(self):
        """Test basic nested loops"""
        script = """
        SET iterations = 0
        LOOP 3
          LOOP 3
            SET iterations = ${LOOP_INDEX}
          ENDLOOP
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # Inner loop runs 3 times for each outer iteration
        # Last value should be 2 (0-indexed, 3rd iteration)
        self.assertEqual(self.interpreter.variables.get("iterations"), "2")

    def test_nested_loop_with_conditionals(self):
        """Test nested loops with IF conditions"""
        script = """
        SET found = false
        LOOP 5
          SET outer = ${LOOP_INDEX}
          LOOP 5
            SET inner = ${LOOP_INDEX}
            IF ${outer} EQ 2 AND ${inner} EQ 3
              SET found = true
              BREAK
            ENDIF
          ENDLOOP
          IF ${found} EQ true
            BREAK
          ENDIF
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("found"), "true")
        self.assertEqual(self.interpreter.variables.get("outer"), "2")
        self.assertEqual(self.interpreter.variables.get("inner"), "3")


class TestLoopWithVariables(unittest.TestCase):
    """Test loops interacting with variables"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_accumulator_in_loop(self):
        """Test accumulating values in a loop"""
        script = """
        SET total = 0
        LOOP 5
          # Simulate addition by setting to LOOP_INDEX
          SET total = ${LOOP_INDEX}
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # After 5 iterations, total should be last index (4)
        self.assertEqual(self.interpreter.variables.get("total"), "4")

    def test_conditional_update_in_loop(self):
        """Test conditional variable updates in loop"""
        script = """
        SET even_count = 0
        LOOP 10
          # Count even indices (0, 2, 4, 6, 8)
          SET current = ${LOOP_INDEX}
          # This is simplified - real implementation would need modulo
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("current"), "9")

    def test_loop_with_external_variable(self):
        """Test loop using externally defined variable"""
        script = """
        SET max_iterations = 7
        SET count = 0
        LOOP ${max_iterations}
          SET count = ${LOOP_INDEX}
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # Should loop 7 times (0-6), last index is 6
        self.assertEqual(self.interpreter.variables.get("count"), "6")


class TestLoopEdgeCases(unittest.TestCase):
    """Test edge cases in loop behavior"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_large_loop_count(self):
        """Test loop with large iteration count"""
        script = """
        SET last = -1
        LOOP 100
          SET last = ${LOOP_INDEX}
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("last"), "99")

    def test_loop_with_function_call(self):
        """Test calling function inside loop (v1.0.16)"""
        script = """
        FUNCTION increment()
          SET call_count = ${LOOP_INDEX}
        ENDFUNCTION

        LOOP 5
          CALL increment()
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # call_count should be set to last LOOP_INDEX
        self.assertEqual(self.interpreter.variables.get("call_count"), "4")

    def test_break_on_first_iteration(self):
        """Test BREAK on first iteration"""
        script = """
        SET executed = false
        LOOP 10
          SET executed = true
          BREAK
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("executed"), "true")

    def test_continue_all_iterations(self):
        """Test CONTINUE on every iteration"""
        script = """
        SET last_before_continue = -1
        LOOP 5
          SET last_before_continue = ${LOOP_INDEX}
          CONTINUE
          SET never_reached = true
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("last_before_continue"), "4")
        self.assertNotIn("never_reached", self.interpreter.variables)


if __name__ == '__main__':
    unittest.main()
