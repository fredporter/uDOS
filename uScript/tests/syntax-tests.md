# uScript Syntax Tests

Comprehensive test suite for uScript language features and syntax validation.

---
title: "uScript Syntax Test Suite"
type: "testing"
version: "1.0.0"
author: "uDOS System"
---

## 🧪 Syntax Feature Tests

```uScript
' uScript Syntax Test Suite
' Tests all language features and constructs

SET test_suite_name = "uScript Syntax Tests"
SET test_start_time = NOW()
SET total_tests = 0
SET passed_tests = 0
SET failed_tests = 0

LOG_INFO "Starting " + test_suite_name + " at " + test_start_time

' Test 1: Variable Assignment and String Operations
LOG_INFO "Test 1: Variable Assignment and String Operations"
SET total_tests = total_tests + 1

SET test_string = "Hello"
SET test_number = 42
SET test_concat = test_string + " World"
SET test_number_string = "Answer: " + test_number

IF test_concat = "Hello World" AND test_number_string = "Answer: 42" THEN
    LOG_INFO "✅ Test 1 PASSED: Variable assignment and concatenation"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 1 FAILED: Variable assignment or concatenation error"
    SET failed_tests = failed_tests + 1
END IF

' Test 2: Conditional Logic (IF/THEN/ELSE)
LOG_INFO "Test 2: Conditional Logic"
SET total_tests = total_tests + 1

SET test_value = 10
SET condition_result = ""

IF test_value > 5 THEN
    SET condition_result = "greater"
ELSIF test_value = 5 THEN
    SET condition_result = "equal"
ELSE
    SET condition_result = "lesser"
END IF

IF condition_result = "greater" THEN
    LOG_INFO "✅ Test 2 PASSED: Conditional logic works correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 2 FAILED: Conditional logic error"
    SET failed_tests = failed_tests + 1
END IF

' Test 3: Logical Operators (AND, OR, NOT)
LOG_INFO "Test 3: Logical Operators"
SET total_tests = total_tests + 1

SET bool_a = true
SET bool_b = false
SET and_result = bool_a AND bool_b
SET or_result = bool_a OR bool_b
SET not_result = NOT bool_b

IF and_result = false AND or_result = true AND not_result = true THEN
    LOG_INFO "✅ Test 3 PASSED: Logical operators work correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 3 FAILED: Logical operator error"
    SET failed_tests = failed_tests + 1
END IF

' Test 4: Numeric Operations
LOG_INFO "Test 4: Numeric Operations"
SET total_tests = total_tests + 1

SET num_a = 15
SET num_b = 3
SET add_result = num_a + num_b
SET sub_result = num_a - num_b
SET mul_result = num_a * num_b
SET div_result = num_a / num_b
SET mod_result = num_a MOD num_b

IF add_result = 18 AND sub_result = 12 AND mul_result = 45 AND div_result = 5 AND mod_result = 0 THEN
    LOG_INFO "✅ Test 4 PASSED: Numeric operations work correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 4 FAILED: Numeric operation error"
    LOG_ERROR "Expected: 18, 12, 45, 5, 0"
    LOG_ERROR "Got: " + add_result + ", " + sub_result + ", " + mul_result + ", " + div_result + ", " + mod_result
    SET failed_tests = failed_tests + 1
END IF

' Test 5: FOR/NEXT Loops
LOG_INFO "Test 5: FOR/NEXT Loops" 
SET total_tests = total_tests + 1

SET loop_sum = 0
FOR i = 1 TO 5
    SET loop_sum = loop_sum + i
NEXT i

IF loop_sum = 15 THEN
    LOG_INFO "✅ Test 5 PASSED: FOR/NEXT loop works correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 5 FAILED: FOR/NEXT loop error - expected 15, got " + loop_sum
    SET failed_tests = failed_tests + 1
END IF

' Test 6: Array Operations
LOG_INFO "Test 6: Array Operations"
SET total_tests = total_tests + 1

SET test_array = ["apple", "banana", "cherry"]
SET first_item = test_array[1]
SET array_length = LEN(test_array)

IF first_item = "apple" AND array_length = 3 THEN
    LOG_INFO "✅ Test 6 PASSED: Array operations work correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 6 FAILED: Array operation error"
    SET failed_tests = failed_tests + 1
END IF

' Test 7: Function Calls
LOG_INFO "Test 7: Function Calls"
SET total_tests = total_tests + 1

SET current_date = TODAY()
SET current_timestamp = NOW()
SET string_length = LEN("testing")

IF LEN(current_date) = 10 AND string_length = 7 THEN
    LOG_INFO "✅ Test 7 PASSED: Function calls work correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 7 FAILED: Function call error"
    SET failed_tests = failed_tests + 1
END IF

' Test 8: JSON Object Creation
LOG_INFO "Test 8: JSON Object Creation"
SET total_tests = total_tests + 1

SET test_object = {
    "name": "Test Object",
    "value": 100,
    "active": true,
    "items": ["item1", "item2"]
}

IF test_object.name = "Test Object" AND test_object.value = 100 THEN
    LOG_INFO "✅ Test 8 PASSED: JSON object creation works correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 8 FAILED: JSON object creation error"
    SET failed_tests = failed_tests + 1
END IF

' Test 9: String Functions
LOG_INFO "Test 9: String Functions"
SET total_tests = total_tests + 1

SET test_str = "Hello World"
SET upper_str = UPPER(test_str)
SET lower_str = LOWER(test_str)
SET substr = MID(test_str, 7, 5)

IF upper_str = "HELLO WORLD" AND lower_str = "hello world" AND substr = "World" THEN
    LOG_INFO "✅ Test 9 PASSED: String functions work correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 9 FAILED: String function error"
    SET failed_tests = failed_tests + 1
END IF

' Test 10: Error Handling
LOG_INFO "Test 10: Error Handling"
SET total_tests = total_tests + 1

SET error_caught = false
TRY
    SET division_by_zero = 10 / 0
CATCH error
    SET error_caught = true
    LOG_INFO "Error caught as expected: " + error
END TRY

IF error_caught = true THEN
    LOG_INFO "✅ Test 10 PASSED: Error handling works correctly"
    SET passed_tests = passed_tests + 1
ELSE
    LOG_ERROR "❌ Test 10 FAILED: Error handling not working"
    SET failed_tests = failed_tests + 1
END IF

' Test Summary
SET test_end_time = NOW()
SET test_duration = time_diff(test_end_time, test_start_time)
SET success_rate = (passed_tests / total_tests) * 100

LOG_INFO "Test Suite Completed"
LOG_INFO "===================="
LOG_INFO "Total Tests: " + total_tests
LOG_INFO "Passed: " + passed_tests
LOG_INFO "Failed: " + failed_tests
LOG_INFO "Success Rate: " + success_rate + "%"
LOG_INFO "Duration: " + test_duration + "ms"

' Generate Test Report
SET report_file = "./uMemory/tests/syntax-test-" + TODAY() + ".md"
SET report_content = "# uScript Syntax Test Report\n\n"
SET report_content = report_content + "**Date:** " + TODAY() + "\n"
SET report_content = report_content + "**Duration:** " + test_duration + "ms\n\n"
SET report_content = report_content + "## Results\n\n"
SET report_content = report_content + "- **Total Tests:** " + total_tests + "\n"
SET report_content = report_content + "- **Passed:** " + passed_tests + "\n"
SET report_content = report_content + "- **Failed:** " + failed_tests + "\n"
SET report_content = report_content + "- **Success Rate:** " + success_rate + "%\n\n"

IF failed_tests = 0 THEN
    SET report_content = report_content + "✅ **All tests passed successfully!**\n"
    LOG_DASHBOARD "✅ uScript syntax tests: All " + total_tests + " tests passed"
ELSE
    SET report_content = report_content + "❌ **" + failed_tests + " test(s) failed - review required**\n"
    LOG_DASHBOARD "⚠️ uScript syntax tests: " + failed_tests + " failed out of " + total_tests
END IF

write_file(report_file, report_content)
LOG_INFO "Test report saved: " + report_file

' Performance Logging
LOG_PERFORMANCE "syntax_tests", test_duration

IF failed_tests = 0 THEN
    LOG_INFO "🎉 All syntax tests passed - uScript language working correctly!"
    EXIT 0
ELSE
    LOG_ERROR "⚠️ Some syntax tests failed - language implementation needs attention"
    EXIT 1
END IF
```

## 🔧 Test Categories

### Core Language Features
- Variable assignment and scoping
- Data types (string, number, boolean, array, object)
- Operators (arithmetic, logical, comparison)
- Control flow (IF/THEN/ELSE, FOR/NEXT, WHILE/DO)

### Built-in Functions
- String manipulation (UPPER, LOWER, MID, LEN)
- Date/time functions (NOW, TODAY, date_add, date_diff)
- File operations (file_exists, read_file, write_file)
- System functions (system_status, count_files)

### Advanced Features
- JSON object creation and manipulation
- Error handling (TRY/CATCH)
- Function definitions and calls
- Array operations and iteration

## 📊 Expected Results

All tests should pass with 100% success rate. Any failures indicate:
- Language parser issues
- Runtime execution problems
- Built-in function implementation errors
- Type system inconsistencies

## 🎯 Usage

Run this test suite to validate uScript implementation:

```bash
./uCode/ucode.sh run uScript/tests/syntax-tests.md
```

---

*This comprehensive test suite ensures uScript language features work correctly and consistently.*
