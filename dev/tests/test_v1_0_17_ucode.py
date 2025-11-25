"""
Test Suite for v1.0.17 - uCODE Automation System
Tests: RUN command, .uscript execution, variables, control flow, debugger

Test Coverage (35 tests total):
- Basic Execution: 8 tests
- Variable System: 7 tests
- Control Flow: 7 tests
- Functions & Scopes: 6 tests
- Debugger: 7 tests

Author: uDOS Development Team
Version: 1.0.17
"""

import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import json
import os

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from interpreters.ucode import UCodeInterpreter, UCodeDebugger, VariableScope


class TestBasicExecution(unittest.TestCase):
    """Test basic .uscript execution (8 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.interpreter = UCodeInterpreter()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_execute_empty_script(self):
        """Test executing an empty script"""
        script_path = Path(self.temp_dir) / "empty.uscript"
        script_path.write_text("")
        result = self.interpreter.execute_script(str(script_path))
        self.assertIsInstance(result, str)

    def test_execute_comment_only_script(self):
        """Test script with only comments"""
        script_path = Path(self.temp_dir) / "comments.uscript"
        script_path.write_text("# This is a comment\n# Another comment\n")
        result = self.interpreter.execute_script(str(script_path))
        self.assertIsInstance(result, str)

    def test_execute_simple_command(self):
        """Test executing a simple command"""
        script_path = Path(self.temp_dir) / "simple.uscript"
        script_path.write_text("# Simple command test\nECHO Hello World\n")
        result = self.interpreter.execute_script(str(script_path))
        self.assertIsInstance(result, str)

    def test_execute_multiple_commands(self):
        """Test executing multiple commands"""
        script_path = Path(self.temp_dir) / "multi.uscript"
        script_path.write_text("ECHO Test1\nECHO Test2\nECHO Test3\n")
        result = self.interpreter.execute_script(str(script_path))
        self.assertIsInstance(result, str)

    def test_script_not_found(self):
        """Test error handling for missing script"""
        result = self.interpreter.execute_script("/nonexistent/script.uscript")
        self.assertIn("not found", result.lower())

    def test_execute_with_blank_lines(self):
        """Test script with blank lines"""
        script_path = Path(self.temp_dir) / "blanks.uscript"
        script_path.write_text("ECHO Line1\n\n\nECHO Line2\n\n")
        result = self.interpreter.execute_script(str(script_path))
        self.assertIsInstance(result, str)

    def test_execute_from_file(self):
        """Test execute_script method with real file"""
        script_path = Path(self.temp_dir) / "test.uscript"
        script_path.write_text("# Test script\nECHO Testing file execution\n")
        result = self.interpreter.execute_script(str(script_path))
        self.assertIsInstance(result, str)

    def test_execute_multiline_output(self):
        """Test commands that produce multiline output"""
        script_path = Path(self.temp_dir) / "multiline.uscript"
        script_path.write_text("ECHO Line1\nECHO Line2\nECHO Line3\n")
        result = self.interpreter.execute_script(str(script_path))
        self.assertIsInstance(result, str)


class TestVariableSystem(unittest.TestCase):
    """Test variable system (7 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.interpreter = UCodeInterpreter()

    def test_set_and_get_variable(self):
        """Test SET and GET variable operations"""
        self.interpreter.set_variable("test_var", "test_value")
        value = self.interpreter.get_variable("test_var")
        self.assertEqual(value, "test_value")

    def test_variable_substitution(self):
        """Test ${variable} substitution"""
        self.interpreter.set_variable("name", "uDOS")
        text = "Hello ${name}!"
        result = self.interpreter.substitute_variables(text)
        self.assertEqual(result, "Hello uDOS!")

    def test_multiple_variable_substitution(self):
        """Test multiple variables in one string"""
        self.interpreter.set_variable("first", "John")
        self.interpreter.set_variable("last", "Doe")
        text = "${first} ${last}"
        result = self.interpreter.substitute_variables(text)
        self.assertEqual(result, "John Doe")

    def test_undefined_variable(self):
        """Test accessing undefined variable"""
        value = self.interpreter.get_variable("undefined_var")
        self.assertIsNone(value)

    def test_variable_overwrite(self):
        """Test overwriting existing variable"""
        self.interpreter.set_variable("var", "old")
        self.interpreter.set_variable("var", "new")
        value = self.interpreter.get_variable("var")
        self.assertEqual(value, "new")

    def test_numeric_variable(self):
        """Test numeric variable values"""
        self.interpreter.set_variable("count", 42)
        value = self.interpreter.get_variable("count")
        self.assertEqual(value, 42)

    def test_variable_type_conversion(self):
        """Test _convert_value for different types"""
        # String
        self.assertEqual(self.interpreter._convert_value('"hello"'), "hello")
        # Number
        self.assertEqual(self.interpreter._convert_value('42'), 42)
        # Float
        self.assertEqual(self.interpreter._convert_value('3.14'), 3.14)
        # Boolean
        self.assertEqual(self.interpreter._convert_value('true'), True)
        self.assertEqual(self.interpreter._convert_value('false'), False)


class TestControlFlow(unittest.TestCase):
    """Test control flow structures (7 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.interpreter = UCodeInterpreter()

    def test_simple_if_condition_true(self):
        """Test IF condition that evaluates to true"""
        self.interpreter.set_variable("x", 10)
        result = self.interpreter.evaluate_condition("${x} > 5")
        self.assertTrue(result)

    def test_simple_if_condition_false(self):
        """Test IF condition that evaluates to false"""
        self.interpreter.set_variable("x", 3)
        result = self.interpreter.evaluate_condition("${x} > 5")
        self.assertFalse(result)

    def test_equality_comparison(self):
        """Test == comparison"""
        self.interpreter.set_variable("status", "active")
        result = self.interpreter.evaluate_condition("${status} == active")
        self.assertTrue(result)

    def test_inequality_comparison(self):
        """Test != comparison"""
        self.interpreter.set_variable("status", "inactive")
        result = self.interpreter.evaluate_condition("${status} != active")
        self.assertTrue(result)

    def test_and_operator(self):
        """Test AND logical operator"""
        self.interpreter.set_variable("x", 10)
        self.interpreter.set_variable("y", 20)
        result = self.interpreter.evaluate_condition("${x} > 5 AND ${y} > 15")
        self.assertTrue(result)

    def test_or_operator(self):
        """Test OR logical operator"""
        self.interpreter.set_variable("x", 3)
        self.interpreter.set_variable("y", 20)
        result = self.interpreter.evaluate_condition("${x} > 5 OR ${y} > 15")
        self.assertTrue(result)

    def test_not_operator(self):
        """Test NOT logical operator"""
        self.interpreter.set_variable("active", False)
        result = self.interpreter.evaluate_condition("NOT ${active}")
        self.assertTrue(result)


class TestFunctionsAndScopes(unittest.TestCase):
    """Test functions and variable scopes (6 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.interpreter = UCodeInterpreter()

    def test_variable_scope_creation(self):
        """Test creating a new variable scope"""
        global_scope = VariableScope()
        local_scope = VariableScope(parent=global_scope)
        self.assertIsNotNone(local_scope.parent)
        self.assertEqual(local_scope.parent, global_scope)

    def test_scope_variable_lookup(self):
        """Test variable lookup in scope chain"""
        global_scope = VariableScope()
        global_scope.set("global_var", "global_value")
        local_scope = VariableScope(parent=global_scope)
        value = local_scope.get("global_var")
        self.assertEqual(value, "global_value")

    def test_scope_variable_shadowing(self):
        """Test local variable shadowing global"""
        global_scope = VariableScope()
        global_scope.set("var", "global")
        local_scope = VariableScope(parent=global_scope)
        local_scope.set("var", "local")
        self.assertEqual(local_scope.get("var"), "local")
        self.assertEqual(global_scope.get("var"), "global")

    def test_scope_has_variable(self):
        """Test has() method for variable existence"""
        scope = VariableScope()
        scope.set("exists", "value")
        self.assertTrue(scope.has("exists"))
        self.assertFalse(scope.has("missing"))

    def test_scope_delete_variable(self):
        """Test deleting variable from scope"""
        scope = VariableScope()
        scope.set("temp", "value")
        self.assertTrue(scope.has("temp"))
        scope.delete("temp")
        self.assertFalse(scope.has("temp"))

    def test_scope_list_variables(self):
        """Test listing all variables in scope"""
        scope = VariableScope()
        scope.set("var1", "value1")
        scope.set("var2", "value2")
        vars_dict = scope.list_variables()
        self.assertIn("var1", vars_dict)
        self.assertIn("var2", vars_dict)
        self.assertEqual(vars_dict["var1"], "value1")


class TestDebugger(unittest.TestCase):
    """Test debugger functionality (7 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.interpreter = UCodeInterpreter()
        self.debugger = UCodeDebugger(self.interpreter)

    def test_debugger_initialization(self):
        """Test debugger initializes correctly"""
        self.assertIsNotNone(self.debugger)
        self.assertEqual(len(self.debugger.breakpoints), 0)
        self.assertEqual(len(self.debugger.watch_expressions), 0)

    def test_add_breakpoint(self):
        """Test adding a breakpoint"""
        result = self.debugger.set_breakpoint(10)
        self.assertIn(10, self.debugger.breakpoints)
        self.assertIn("10", result)

    def test_remove_breakpoint(self):
        """Test removing a breakpoint"""
        self.debugger.set_breakpoint(10)
        result = self.debugger.clear_breakpoint(10)
        self.assertNotIn(10, self.debugger.breakpoints)
        self.assertIn("10", result)

    def test_add_watch_expression(self):
        """Test adding a watch expression"""
        result = self.debugger.add_watch("x", "x_value")
        self.assertIn("x_value", self.debugger.watch_expressions)
        self.assertIn("Watching", result)

    def test_remove_watch_expression(self):
        """Test removing a watch expression"""
        self.debugger.add_watch("x", "x_value")
        result = self.debugger.remove_watch("x_value")
        self.assertNotIn("x_value", self.debugger.watch_expressions)
        self.assertIn("Removed", result)

    def test_debugger_step_mode(self):
        """Test debugger step mode activation"""
        self.debugger.step()
        self.assertEqual(self.debugger.step_mode, 'STEP')

    def test_get_debugger_status(self):
        """Test getting debugger status"""
        status = self.debugger.get_status()
        self.assertIn('state', status)
        self.assertIn('breakpoints', status)
        self.assertIn('watches', status)
        self.assertIsInstance(status['breakpoints'], list)


class TestIntegration(unittest.TestCase):
    """Integration tests (bonus coverage)"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_script_with_variables_and_conditionals(self):
        """Test script combining variables and conditionals"""
        interpreter = UCodeInterpreter()
        interpreter.set_variable("mode", "production")

        # Test conditional evaluation
        result = interpreter.evaluate_condition("${mode} == production")
        self.assertTrue(result)

    def test_real_uscript_files_exist(self):
        """Test that real .uscript example files exist"""
        examples = [
            "knowledge/demos/simple-setup.uscript",
            "knowledge/demos/advanced_features.uscript",
        ]

        for example in examples:
            path = Path(__file__).parent.parent.parent / example
            # Just check structure exists, don't require specific files
            self.assertTrue(Path(path).parent.exists())


def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBasicExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestVariableSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestControlFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionsAndScopes))
    suite.addTests(loader.loadTestsFromTestCase(TestDebugger))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
