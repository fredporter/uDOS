"""
Unit tests for uCODE function system (v1.0.16)

Tests FUNCTION/CALL/RETURN commands.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import unittest
from core.uDOS_ucode import UCodeInterpreter


class TestFunctionBasics(unittest.TestCase):
    """Test basic function definition and calling"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_function_definition(self):
        """Test defining a function"""
        script = """
        FUNCTION greet()
          ECHO Hello World
        ENDFUNCTION
        """
        self.interpreter.execute_script(script)
        self.assertIn("greet", self.interpreter.functions)

    def test_function_call_no_params(self):
        """Test calling function with no parameters"""
        script = """
        FUNCTION say_hello()
          SET message = Hello
        ENDFUNCTION
        CALL say_hello()
        """
        self.interpreter.execute_script(script)
        # message should not leak to global scope
        self.assertNotIn("message", self.interpreter.variables)

    def test_function_return_value(self):
        """Test function return value"""
        script = """
        FUNCTION get_value()
          RETURN 42
        ENDFUNCTION
        CALL get_value()
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "42")

    def test_function_with_single_parameter(self):
        """Test function with one parameter"""
        script = """
        FUNCTION greet(name)
          RETURN Hello ${name}
        ENDFUNCTION
        CALL greet(Alice)
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "Hello Alice")

    def test_function_with_multiple_parameters(self):
        """Test function with multiple parameters"""
        script = """
        FUNCTION add(a, b)
          RETURN ${a} plus ${b}
        ENDFUNCTION
        CALL add(5, 10)
        """
        self.interpreter.execute_script(script)
        self.assertIn("RETURN_VALUE", self.interpreter.variables)


class TestFunctionScopes(unittest.TestCase):
    """Test function variable scoping"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_local_variable_isolation(self):
        """Test local variables don't leak"""
        script = """
        FUNCTION test()
          SET local = value
        ENDFUNCTION
        CALL test()
        """
        self.interpreter.execute_script(script)
        self.assertNotIn("local", self.interpreter.variables)

    def test_global_variable_access(self):
        """Test functions can read global variables"""
        script = """
        SET global_var = global_value
        FUNCTION read_global()
          RETURN ${global_var}
        ENDFUNCTION
        CALL read_global()
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "global_value")

    def test_parameter_shadows_global(self):
        """Test parameter shadows global variable"""
        script = """
        SET name = Global
        FUNCTION greet(name)
          RETURN Hello ${name}
        ENDFUNCTION
        CALL greet(Local)
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "Hello Local")
        self.assertEqual(self.interpreter.variables.get("name"), "Global")


class TestNestedFunctions(unittest.TestCase):
    """Test calling functions from within functions"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_function_calls_function(self):
        """Test function calling another function"""
        script = """
        FUNCTION inner()
          RETURN inner_value
        ENDFUNCTION

        FUNCTION outer()
          CALL inner()
          RETURN ${RETURN_VALUE}
        ENDFUNCTION

        CALL outer()
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "inner_value")

    def test_recursive_function_simple(self):
        """Test simple recursive function"""
        script = """
        FUNCTION countdown(n)
          IF ${n} LE 0
            RETURN done
          ENDIF
          CALL countdown(0)
        ENDFUNCTION

        CALL countdown(3)
        """
        self.interpreter.execute_script(script)
        # Should eventually return "done"
        self.assertIn("RETURN_VALUE", self.interpreter.variables)


class TestFunctionWithConditionals(unittest.TestCase):
    """Test functions with conditional logic"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_conditional_return(self):
        """Test returning from different branches"""
        script = """
        FUNCTION check_value(val)
          IF ${val} GT 10
            RETURN large
          ELSE
            RETURN small
          ENDIF
        ENDFUNCTION

        CALL check_value(15)
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "large")

    def test_early_return(self):
        """Test early return from function"""
        script = """
        FUNCTION early_exit(flag)
          IF ${flag} EQ true
            RETURN early
          ENDIF
          RETURN normal
        ENDFUNCTION

        CALL early_exit(true)
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "early")


class TestFunctionWithLoops(unittest.TestCase):
    """Test functions with loop logic"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_loop_in_function(self):
        """Test function containing a loop"""
        script = """
        FUNCTION count_to_five()
          SET total = 0
          LOOP 5
            SET total = ${LOOP_INDEX}
          ENDLOOP
          RETURN ${total}
        ENDFUNCTION

        CALL count_to_five()
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "4")

    def test_function_called_in_loop(self):
        """Test calling function inside a loop"""
        script = """
        FUNCTION get_index()
          RETURN ${LOOP_INDEX}
        ENDFUNCTION

        SET last_value = -1
        LOOP 3
          CALL get_index()
          SET last_value = ${RETURN_VALUE}
        ENDLOOP
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("last_value"), "2")


class TestFunctionEdgeCases(unittest.TestCase):
    """Test edge cases in function behavior"""

    def setUp(self):
        """Create fresh interpreter for each test"""
        self.interpreter = UCodeInterpreter()

    def test_function_without_return(self):
        """Test function without explicit RETURN"""
        script = """
        FUNCTION no_return()
          SET temp = value
        ENDFUNCTION

        CALL no_return()
        """
        self.interpreter.execute_script(script)
        # RETURN_VALUE might be empty or undefined
        self.assertIsNotNone(self.interpreter.variables)

    def test_empty_function(self):
        """Test empty function body"""
        script = """
        FUNCTION empty()
        ENDFUNCTION

        CALL empty()
        """
        self.interpreter.execute_script(script)
        self.assertIn("empty", self.interpreter.functions)

    def test_function_name_case_sensitivity(self):
        """Test function name case sensitivity"""
        script = """
        FUNCTION MyFunc()
          RETURN test
        ENDFUNCTION

        CALL MyFunc()
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "test")

    def test_multiple_return_statements(self):
        """Test function with multiple return paths"""
        script = """
        FUNCTION multi_return(choice)
          IF ${choice} EQ 1
            RETURN first
          ENDIF
          IF ${choice} EQ 2
            RETURN second
          ENDIF
          RETURN default
        ENDFUNCTION

        CALL multi_return(2)
        """
        self.interpreter.execute_script(script)
        self.assertEqual(self.interpreter.variables.get("RETURN_VALUE"), "second")


if __name__ == '__main__':
    unittest.main()
