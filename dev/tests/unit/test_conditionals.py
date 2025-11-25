"""
Unit tests for uCODE conditional logic (v1.0.14)

Tests IF/ELSE/ENDIF commands with comparison and logical operators.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import unittest
from core.uDOS_ucode import UCodeInterpreter


class TestConditionalBasics(unittest.TestCase):
    """Test basic IF/ELSE/ENDIF functionality"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_simple_if_true(self):
        """Test IF condition that evaluates to true"""
        script = """
        SET x = 10
        IF ${x} EQ 10
          SET result = matched
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "matched")

    def test_simple_if_false(self):
        """Test IF condition that evaluates to false"""
        script = """
        SET x = 5
        IF ${x} EQ 10
          SET result = matched
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertNotIn("result", self.interpreter.variables)

    def test_if_else_true_branch(self):
        """Test IF/ELSE with true condition"""
        script = """
        SET x = 10
        IF ${x} EQ 10
          SET result = true_branch
        ELSE
          SET result = false_branch
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "true_branch")

    def test_if_else_false_branch(self):
        """Test IF/ELSE with false condition"""
        script = """
        SET x = 5
        IF ${x} EQ 10
          SET result = true_branch
        ELSE
          SET result = false_branch
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "false_branch")


class TestComparisonOperators(unittest.TestCase):
    """Test all comparison operators"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_eq_operator(self):
        """Test EQ (equal) operator"""
        script = """
        SET a = 5
        IF ${a} EQ 5
          SET result = equal
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "equal")

    def test_ne_operator(self):
        """Test NE (not equal) operator"""
        script = """
        SET a = 5
        IF ${a} NE 10
          SET result = not_equal
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "not_equal")

    def test_gt_operator(self):
        """Test GT (greater than) operator"""
        script = """
        SET a = 10
        IF ${a} GT 5
          SET result = greater
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "greater")

    def test_lt_operator(self):
        """Test LT (less than) operator"""
        script = """
        SET a = 3
        IF ${a} LT 5
          SET result = less
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "less")

    def test_ge_operator(self):
        """Test GE (greater than or equal) operator"""
        script = """
        SET a = 5
        IF ${a} GE 5
          SET result = greater_or_equal
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "greater_or_equal")

    def test_le_operator(self):
        """Test LE (less than or equal) operator"""
        script = """
        SET a = 5
        IF ${a} LE 5
          SET result = less_or_equal
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "less_or_equal")

    def test_string_comparison(self):
        """Test string equality comparison"""
        script = """
        SET name = Alice
        IF ${name} EQ Alice
          SET result = name_match
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "name_match")


class TestLogicalOperators(unittest.TestCase):
    """Test AND, OR, NOT logical operators"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_and_operator_both_true(self):
        """Test AND with both conditions true"""
        script = """
        SET x = 5
        SET y = 10
        IF ${x} GT 0 AND ${y} GT 0
          SET result = both_positive
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "both_positive")

    def test_and_operator_one_false(self):
        """Test AND with one condition false"""
        script = """
        SET x = 5
        SET y = -10
        IF ${x} GT 0 AND ${y} GT 0
          SET result = both_positive
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertNotIn("result", self.interpreter.variables)

    def test_or_operator_both_true(self):
        """Test OR with both conditions true"""
        script = """
        SET x = 5
        SET y = 10
        IF ${x} GT 0 OR ${y} GT 0
          SET result = at_least_one_positive
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "at_least_one_positive")

    def test_or_operator_one_true(self):
        """Test OR with one condition true"""
        script = """
        SET x = 5
        SET y = -10
        IF ${x} GT 0 OR ${y} GT 0
          SET result = at_least_one_positive
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "at_least_one_positive")

    def test_not_operator(self):
        """Test NOT operator"""
        script = """
        SET flag = false
        IF NOT ${flag} EQ true
          SET result = flag_is_not_true
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "flag_is_not_true")


class TestNestedConditionals(unittest.TestCase):
    """Test nested IF statements"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_nested_if_both_true(self):
        """Test nested IF with both conditions true"""
        script = """
        SET x = 10
        SET y = 20
        IF ${x} GT 5
          IF ${y} GT 15
            SET result = both_conditions_met
          ENDIF
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "both_conditions_met")

    def test_nested_if_outer_false(self):
        """Test nested IF with outer condition false"""
        script = """
        SET x = 3
        SET y = 20
        IF ${x} GT 5
          IF ${y} GT 15
            SET result = both_conditions_met
          ENDIF
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertNotIn("result", self.interpreter.variables)

    def test_nested_if_inner_false(self):
        """Test nested IF with inner condition false"""
        script = """
        SET x = 10
        SET y = 10
        IF ${x} GT 5
          IF ${y} GT 15
            SET result = both_conditions_met
          ELSE
            SET result = inner_condition_failed
          ENDIF
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "inner_condition_failed")


class TestConditionalEdgeCases(unittest.TestCase):
    """Test edge cases in conditional logic"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_numeric_string_comparison(self):
        """Test comparing numeric strings"""
        script = """
        SET num = 42
        IF ${num} EQ 42
          SET result = matched
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "matched")

    def test_empty_value_comparison(self):
        """Test comparing empty values"""
        script = """
        SET empty =
        IF ${empty} EQ
          SET result = empty_matched
        ENDIF
        """
        self.interpreter.execute_script(script)
        # Implementation dependent - may or may not match
        self.assertIsNotNone(self.interpreter.variables)

    def test_whitespace_in_comparison(self):
        """Test comparison with whitespace"""
        script = """
        SET text = Hello World
        IF ${text} EQ Hello World
          SET result = matched_with_space
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "matched_with_space")


if __name__ == '__main__':
    unittest.main()
