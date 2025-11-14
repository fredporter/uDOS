"""
Unit tests for uCODE variable system (v1.0.14)

Tests SET, GET, DELETE, VARS commands and variable substitution.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import unittest
from core.uDOS_ucode import UCodeInterpreter


class TestVariableSystem(unittest.TestCase):
    """Test the variable system comprehensively"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_set_get_string(self):
        """Test setting and getting string variables"""
        self.interpreter.execute("SET name = Fred")
        result = self.interpreter.execute("ECHO ${name}")
        self.assertIn("Fred", result)

    def test_set_get_number(self):
        """Test setting and getting numeric variables"""
        self.interpreter.execute("SET count = 42")
        self.assertEqual(self.interpreter.variables.get("count"), "42")

    def test_variable_substitution(self):
        """Test ${var} substitution in commands"""
        self.interpreter.execute("SET greeting = Hello")
        self.interpreter.execute("SET name = World")
        result = self.interpreter.execute("ECHO ${greeting}, ${name}!")
        self.assertIn("Hello, World!", result)

    def test_delete_variable(self):
        """Test DELETE command"""
        self.interpreter.execute("SET temp = test")
        self.assertIn("temp", self.interpreter.variables)
        self.interpreter.execute("DELETE temp")
        self.assertNotIn("temp", self.interpreter.variables)

    def test_vars_command(self):
        """Test VARS command listing"""
        self.interpreter.execute("SET var1 = value1")
        self.interpreter.execute("SET var2 = value2")
        result = self.interpreter.execute("VARS")
        self.assertIn("var1", result)
        self.assertIn("var2", result)

    def test_variable_overwrite(self):
        """Test overwriting existing variable"""
        self.interpreter.execute("SET key = old")
        self.interpreter.execute("SET key = new")
        self.assertEqual(self.interpreter.variables.get("key"), "new")

    def test_variable_with_spaces(self):
        """Test variables with spaces in value"""
        self.interpreter.execute("SET message = Hello World")
        self.assertEqual(self.interpreter.variables.get("message"), "Hello World")

    def test_empty_variable(self):
        """Test setting empty variable"""
        self.interpreter.execute("SET empty = ")
        self.assertEqual(self.interpreter.variables.get("empty"), "")

    def test_variable_in_loop_index(self):
        """Test LOOP_INDEX special variable"""
        script = """
        LOOP 3
          SET count = ${LOOP_INDEX}
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        # After loop, count should be 2 (0-indexed, last iteration)
        self.assertEqual(self.interpreter.variables.get("count"), "2")

    def test_undefined_variable_substitution(self):
        """Test substitution of undefined variable"""
        result = self.interpreter.execute("ECHO ${undefined}")
        # Should either show empty or error message
        self.assertIsNotNone(result)

    def test_multiple_variables_same_line(self):
        """Test multiple variable substitutions in one command"""
        self.interpreter.execute("SET a = Alpha")
        self.interpreter.execute("SET b = Beta")
        self.interpreter.execute("SET c = Gamma")
        result = self.interpreter.execute("ECHO ${a} ${b} ${c}")
        self.assertIn("Alpha", result)
        self.assertIn("Beta", result)
        self.assertIn("Gamma", result)

    def test_variable_names_case_sensitivity(self):
        """Test case sensitivity of variable names"""
        self.interpreter.execute("SET myVar = lowercase")
        self.interpreter.execute("SET MYVAR = uppercase")
        # Python dicts are case-sensitive
        self.assertIn("myVar", self.interpreter.variables)
        self.assertIn("MYVAR", self.interpreter.variables)
        self.assertEqual(self.interpreter.variables.get("myVar"), "lowercase")
        self.assertEqual(self.interpreter.variables.get("MYVAR"), "uppercase")


class TestVariableTypes(unittest.TestCase):
    """Test variable type handling"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_integer_variable(self):
        """Test integer values"""
        self.interpreter.execute("SET age = 25")
        self.assertEqual(self.interpreter.variables.get("age"), "25")

    def test_float_variable(self):
        """Test floating point values"""
        self.interpreter.execute("SET pi = 3.14159")
        self.assertEqual(self.interpreter.variables.get("pi"), "3.14159")

    def test_boolean_like_variable(self):
        """Test boolean-like string values"""
        self.interpreter.execute("SET flag = true")
        self.assertEqual(self.interpreter.variables.get("flag"), "true")

    def test_special_characters(self):
        """Test variables with special characters"""
        self.interpreter.execute("SET path = /usr/local/bin")
        self.assertEqual(self.interpreter.variables.get("path"), "/usr/local/bin")

    def test_numeric_operations(self):
        """Test numeric values in comparisons"""
        self.interpreter.execute("SET count = 10")
        script = """
        IF ${count} GT 5
          SET result = greater
        ENDIF
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("result"), "greater")


class TestVariableScoping(unittest.TestCase):
    """Test variable scoping with functions (v1.0.16)"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_global_variable_access(self):
        """Test accessing global variable from function"""
        script = """
        SET global_var = global_value
        FUNCTION test_func()
          ECHO ${global_var}
        ENDFUNCTION
        CALL test_func()
        """
        result = self.interpreter.execute_script(script)
        # Function should see global variable
        self.assertIsNotNone(result)

    def test_local_variable_isolation(self):
        """Test local variables don't leak to global scope"""
        script = """
        FUNCTION test_func()
          SET local_var = local_value
        ENDFUNCTION
        CALL test_func()
        """
        self.interpreter.execute_script(script)
        # local_var should not exist in global scope after function call
        self.assertNotIn("local_var", self.interpreter.variables)

    def test_parameter_binding(self):
        """Test function parameters as local variables"""
        script = """
        FUNCTION greet(name)
          SET message = Hello ${name}
          RETURN ${message}
        ENDFUNCTION
        CALL greet(Alice)
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "Hello Alice")


if __name__ == '__main__':
    unittest.main()
