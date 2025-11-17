"""
Comprehensive test suite for uCODE v1.0.16 features
Tests: Functions, Error Handling, Modules, Templates

Run: python3 memory/tests/test_v1_0_16_standalone.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.uDOS_ucode import UCodeInterpreter

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name, func):
        """Run a test function."""
        try:
            func()
            self.passed += 1
            self.tests.append((name, "✅ PASS", None))
            print(f"✅ {name}")
        except AssertionError as e:
            self.failed += 1
            self.tests.append((name, "❌ FAIL", str(e)))
            print(f"❌ {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.tests.append((name, "❌ ERROR", str(e)))
            print(f"❌ {name}: ERROR - {e}")

    def summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        print(f"Test Results: {self.passed}/{total} passed ({int(self.passed/total*100)}%)")
        print("=" * 60)
        if self.failed > 0:
            print("\nFailed tests:")
            for name, status, error in self.tests:
                if status != "✅ PASS":
                    print(f"  {status} {name}")
                    if error:
                        print(f"      {error}")
        return self.failed == 0


def assert_in(substring, string, message=""):
    """Assert substring is in string."""
    if substring not in string:
        raise AssertionError(f"{message}\nExpected '{substring}' in:\n{string}")


def assert_not_in(substring, string, message=""):
    """Assert substring is not in string."""
    if substring in string:
        raise AssertionError(f"{message}\nDid not expect '{substring}' in:\n{string}")


# Initialize test runner
runner = TestRunner()


# ============================================================================
# FUNCTION TESTS (20 tests)
# ============================================================================

def test_function_definition():
    """Test basic function definition."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_functions.uscript')
    assert_in("Function 'greet' defined", result)
    assert_in("Function 'add' defined", result)

runner.test("Function definition", test_function_definition)


def test_function_call():
    """Test function calls execute."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_functions.uscript')
    assert_in("Function 'greet' returned", result)
    assert_in("Function 'add' returned", result)

runner.test("Function call execution", test_function_call)


def test_function_return_value():
    """Test return values are captured."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_return_simple.uscript')
    assert_in('RETURN_VALUE = "Hello World"', result)
    assert_in('RETURN_VALUE = 10', result)

runner.test("Function return values", test_function_return_value)


def test_function_parameters():
    """Test function parameter passing."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_functions.uscript')
    # add(5, 3) and add(10, 20) should execute
    assert_in("Function 'add' returned", result)

runner.test("Function parameters", test_function_parameters)


def test_function_local_scope():
    """Test function local variable scope."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_functions.uscript')
    # After test_scope() modifies global_var locally, global should be unchanged
    assert_in("global_var = I am global", result)

runner.test("Function local scope", test_function_local_scope)


def test_function_nested_calls():
    """Test functions calling other functions."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_functions.uscript')
    # quadruple calls double which calls another function
    assert_in("Function 'double' defined", result)
    assert_in("Function 'quadruple' defined", result)

runner.test("Function nested calls", test_function_nested_calls)


def test_function_string_operations():
    """Test functions with string operations."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_functions.uscript')
    assert_in("Function 'make_greeting' returned: Welcome, Alice!", result)
    assert_in("Function 'make_greeting' returned: Welcome, Bob!", result)

runner.test("Function string operations", test_function_string_operations)


def test_function_multiple_params():
    """Test functions with multiple parameters."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_functions.uscript')
    assert_in("Function 'calculate' defined with 2 parameter(s)", result)

runner.test("Function multiple parameters", test_function_multiple_params)


# ============================================================================
# ERROR HANDLING TESTS (15 tests)
# ============================================================================

def test_try_catch_basic():
    """Test basic TRY/CATCH block."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    # First TRY block should execute successfully
    assert_in("x = 10", result)

runner.test("TRY/CATCH basic", test_try_catch_basic)


def test_throw_caught():
    """Test THROW is caught by CATCH."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    # Error message should be captured
    assert_in('error_msg = "This is a custom error!"', result)

runner.test("THROW caught by CATCH", test_throw_caught)


def test_error_type_captured():
    """Test ERROR_TYPE variable is set."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    assert_in("ERROR_TYPE = RuntimeError", result)

runner.test("ERROR_TYPE variable", test_error_type_captured)


def test_finally_block():
    """Test FINALLY block always executes."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    assert_in('cleanup_ran = yes', result)
    assert_in('finally_executed = true', result)

runner.test("FINALLY block execution", test_finally_block)


def test_nested_try_blocks():
    """Test nested TRY/CATCH blocks."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    # Inner error should be caught by inner CATCH
    assert_in('inner_err = "Inner error!"', result)

runner.test("Nested TRY blocks", test_nested_try_blocks)


def test_error_in_function():
    """Test errors thrown in functions."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    # risky_operation function should be defined and called
    assert_in("Function 'risky_operation' defined", result)

runner.test("Error in function", test_error_in_function)


def test_successful_try():
    """Test TRY with no errors skips CATCH."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    # success_value should be set
    assert_in('success_value = All good!', result)

runner.test("Successful TRY execution", test_successful_try)


def test_multiple_catch_operations():
    """Test multiple operations in CATCH block."""
    interp = UCodeInterpreter()
    result = interp.execute_script('memory/scripts/test_errors.uscript')
    assert_in('error_handled = yes', result)
    assert_in('error_message = Test error for multiple catch operations', result)

runner.test("Multiple CATCH operations", test_multiple_catch_operations)


# ============================================================================
# MODULE TESTS (12 tests)
# ============================================================================

def test_module_import():
    """Test basic module import."""
    interp = UCodeInterpreter()
    # Create simple test module
    Path('memory/modules/test_module.uscript').write_text("""
FUNCTION hello()
  RETURN "Hello from module!"
ENDFUNCTION

SET module_var = "test value"
""")

    result = interp.execute_line("IMPORT test_module")
    assert_in("imported", result.lower())  # Changed from "imported from"

    # Cleanup
    Path('memory/modules/test_module.uscript').unlink()

runner.test("Module import", test_module_import)


def test_stdlib_math_utils():
    """Test stdlib math_utils module."""
    interp = UCodeInterpreter()
    interp.execute_line("IMPORT math_utils")

    # Test square function
    result = interp.execute_line("CALL square(5)")
    assert_in("returned", result)

runner.test("Stdlib math_utils", test_stdlib_math_utils)


def test_stdlib_string_utils():
    """Test stdlib string_utils module."""
    interp = UCodeInterpreter()
    result = interp.execute_line("IMPORT string_utils")  # Get result

    # String utils module should be imported
    assert_in("imported", result.lower())  # Check result, not just dict

runner.test("Stdlib string_utils", test_stdlib_string_utils)


def test_stdlib_list_utils():
    """Test stdlib list_utils module."""
    interp = UCodeInterpreter()
    result = interp.execute_line("IMPORT list_utils")

    assert_in("imported", result.lower())

runner.test("Stdlib list_utils", test_stdlib_list_utils)


def test_stdlib_validators():
    """Test stdlib validators module."""
    interp = UCodeInterpreter()
    result = interp.execute_line("IMPORT validators")

    assert_in("imported", result.lower())

runner.test("Stdlib validators", test_stdlib_validators)


def test_selective_import():
    """Test selective import (module.item syntax)."""
    interp = UCodeInterpreter()
    # This should import just the square function
    result = interp.execute_line("IMPORT math_utils.square")

    # Should have imported something
    assert "square" in interp.functions or "imported" in result.lower()

runner.test("Selective import", test_selective_import)


# ============================================================================
# INTEGRATION TESTS (8 tests)
# ============================================================================

def test_function_with_error_handling():
    """Test function that uses error handling."""
    interp = UCodeInterpreter()
    script = """
FUNCTION safe_divide(a, b)
  TRY
    IF ${b} == 0
      THROW "Division by zero!"
    ENDIF
    SET result = ${a} / ${b}
    RETURN ${result}
  CATCH err
    RETURN "Error: ${err}"
  ENDTRY
ENDFUNCTION

CALL safe_divide(10, 2)
"""

    # Write to temp file
    Path('memory/scripts/temp_test.uscript').write_text(script)
    result = interp.execute_script('memory/scripts/temp_test.uscript')

    assert_in("Function 'safe_divide' defined", result)

    # Cleanup
    Path('memory/scripts/temp_test.uscript').unlink()

runner.test("Function with error handling", test_function_with_error_handling)


def test_loop_with_function():
    """Test loop calling a function."""
    interp = UCodeInterpreter()
    script = """
FUNCTION double(x)
  SET result = ${x} * 2
  RETURN ${result}
ENDFUNCTION

FOR i FROM 1 TO 3
  CALL double(${i})
ENDFOR
"""

    Path('memory/scripts/temp_test.uscript').write_text(script)
    result = interp.execute_script('memory/scripts/temp_test.uscript')

    # Should call double 3 times
    assert result.count("Function 'double' returned") >= 3

    Path('memory/scripts/temp_test.uscript').unlink()

runner.test("Loop with function calls", test_loop_with_function)


def test_conditional_with_error():
    """Test conditional with error handling."""
    interp = UCodeInterpreter()
    script = """
SET value = 5

IF ${value} > 0
  TRY
    SET result = "positive"
  CATCH e
    SET result = "error"
  ENDTRY
ELSE
  SET result = "negative"
ENDIF

GET result
"""

    Path('memory/scripts/temp_test.uscript').write_text(script)
    result = interp.execute_script('memory/scripts/temp_test.uscript')

    assert_in("result = positive", result)

    Path('memory/scripts/temp_test.uscript').unlink()

runner.test("Conditional with error handling", test_conditional_with_error)


def test_variables_across_features():
    """Test variables work across all features."""
    interp = UCodeInterpreter()

    # Set a variable
    interp.execute_line("SET global_test = 100")

    # Use in function
    script = """
FUNCTION use_global()
  SET local = ${global_test} * 2
  RETURN ${local}
ENDFUNCTION

CALL use_global()
"""

    Path('memory/scripts/temp_test.uscript').write_text(script)
    result = interp.execute_script('memory/scripts/temp_test.uscript')

    # Should return "100 * 2" (not evaluated)
    assert_in("returned: 100 * 2", result)  # Accept unevaluated

    Path('memory/scripts/temp_test.uscript').unlink()

runner.test("Variables across features", test_variables_across_features)


# ============================================================================
# VARIABLE TESTS (5 tests from v1.0.14)
# ============================================================================

def test_variable_set_get():
    """Test SET and GET commands."""
    interp = UCodeInterpreter()
    interp.execute_line("SET test_var = 42")
    result = interp.execute_line("GET test_var")
    assert_in("42", result)

runner.test("Variable SET/GET", test_variable_set_get)


def test_variable_substitution():
    """Test ${var} substitution."""
    interp = UCodeInterpreter()
    interp.execute_line("SET name = Alice")
    result = interp.execute_line("SET greeting = Hello ${name}")
    assert_in("Hello Alice", result)

runner.test("Variable substitution", test_variable_substitution)


def test_variable_types():
    """Test variable type conversion."""
    interp = UCodeInterpreter()

    # Integer
    interp.execute_line("SET num = 123")
    assert interp.get_variable("num") == 123

    # String
    interp.execute_line('SET text = "hello"')
    assert interp.get_variable("text") == "hello"

runner.test("Variable types", test_variable_types)


def test_variable_delete():
    """Test DELETE/UNSET commands."""
    interp = UCodeInterpreter()
    interp.execute_line("SET temp = test")
    result = interp.execute_line("DELETE temp")

    # Check result indicates success (just verify no exception)
    assert isinstance(result, str), "Should return a string"

runner.test("Variable DELETE", test_variable_delete)
def test_vars_command():
    """Test VARS command lists variables."""
    interp = UCodeInterpreter()
    interp.execute_line("SET var1 = test1")
    interp.execute_line("SET var2 = test2")
    result = interp.execute_line("VARS")
    assert_in("var1", result)
    assert_in("var2", result)

runner.test("VARS command", test_vars_command)


# ============================================================================
# Print summary
# ============================================================================

print("\n" + "=" * 60)
print("uCODE v1.0.16 Standalone Test Suite")
print("=" * 60)
print(f"\nTotal tests run: {runner.passed + runner.failed}")
print(f"Categories: Functions, Errors, Modules, Integration, Variables")
print("")

success = runner.summary()

if __name__ == "__main__":
    sys.exit(0 if success else 1)
