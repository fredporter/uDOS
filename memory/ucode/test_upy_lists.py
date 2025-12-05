"""
Test Suite: uPY v2.0.2 List Operations

Tests list literals, LIST commands, and FOREACH enhancements.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.runtime.upy_runtime_v2 import UPYRuntime
from core.runtime.upy_lists import ListOperations


def test_list_literal_parsing():
    """Test parsing list literals."""
    print("\n=== Test: List Literal Parsing ===")

    # Empty list
    result = ListOperations.parse_list_literal("[]")
    assert result == [], f"Expected [], got {result}"
    print("✅ Empty list: []")

    # Simple list
    result = ListOperations.parse_list_literal("[apple, banana, cherry]")
    assert result == ["apple", "banana", "cherry"], f"Expected ['apple', 'banana', 'cherry'], got {result}"
    print("✅ Simple list: [apple, banana, cherry]")

    # List with quotes
    result = ListOperations.parse_list_literal('["apple", "banana", "cherry"]')
    assert result == ["apple", "banana", "cherry"], f"Expected ['apple', 'banana', 'cherry'], got {result}"
    print("✅ Quoted list: [\"apple\", \"banana\", \"cherry\"]")

    # Mixed quotes
    result = ListOperations.parse_list_literal("[apple, 'banana', \"cherry\"]")
    assert result == ["apple", "banana", "cherry"], f"Expected ['apple', 'banana', 'cherry'], got {result}"
    print("✅ Mixed quotes: [apple, 'banana', \"cherry\"]")

    print("✅ All list literal parsing tests passed!")


def test_list_operations():
    """Test LIST command operations."""
    print("\n=== Test: LIST Operations ===")

    runtime = UPYRuntime()

    # CREATE list
    result = runtime.execute_command('LIST', ['CREATE', 'fruits', 'apple', 'banana', 'cherry'])
    assert runtime.get_variable('fruits') == ['apple', 'banana', 'cherry']
    print("✅ LIST CREATE: fruits = ['apple', 'banana', 'cherry']")

    # APPEND
    runtime.execute_command('LIST', ['APPEND', 'fruits', 'orange'])
    assert runtime.get_variable('fruits') == ['apple', 'banana', 'cherry', 'orange']
    print("✅ LIST APPEND: fruits = ['apple', 'banana', 'cherry', 'orange']")

    # SIZE
    size = runtime.execute_command('LIST', ['SIZE', 'fruits'])
    assert size == 4, f"Expected size 4, got {size}"
    print(f"✅ LIST SIZE: {size}")

    # GET
    item = runtime.execute_command('LIST', ['GET', 'fruits', '1'])
    assert item == 'banana', f"Expected 'banana', got {item}"
    print(f"✅ LIST GET fruits[1]: {item}")

    # SET
    runtime.execute_command('LIST', ['SET', 'fruits', '1', 'blueberry'])
    assert runtime.get_variable('fruits')[1] == 'blueberry'
    print("✅ LIST SET fruits[1] = 'blueberry'")

    # INSERT
    runtime.execute_command('LIST', ['INSERT', 'fruits', '2', 'grape'])
    assert runtime.get_variable('fruits') == ['apple', 'blueberry', 'grape', 'cherry', 'orange']
    print("✅ LIST INSERT at index 2: fruits = ['apple', 'blueberry', 'grape', 'cherry', 'orange']")

    # CONTAINS
    contains = runtime.execute_command('LIST', ['CONTAINS', 'fruits', 'grape'])
    assert contains == True, f"Expected True, got {contains}"
    print("✅ LIST CONTAINS 'grape': True")

    # INDEX
    index = runtime.execute_command('LIST', ['INDEX', 'fruits', 'cherry'])
    assert index == 3, f"Expected index 3, got {index}"
    print(f"✅ LIST INDEX of 'cherry': {index}")

    # SLICE
    sliced = runtime.execute_command('LIST', ['SLICE', 'fruits', '1', '3'])
    assert sliced == ['blueberry', 'grape'], f"Expected ['blueberry', 'grape'], got {sliced}"
    print(f"✅ LIST SLICE [1:3]: {sliced}")

    # JOIN
    joined = runtime.execute_command('LIST', ['JOIN', 'fruits', ', '])
    assert joined == 'apple, blueberry, grape, cherry, orange', f"Expected 'apple, blueberry, grape, cherry, orange', got {joined}"
    print(f"✅ LIST JOIN: {joined}")

    # REMOVE
    runtime.execute_command('LIST', ['REMOVE', 'fruits', 'grape'])
    assert runtime.get_variable('fruits') == ['apple', 'blueberry', 'cherry', 'orange']
    print("✅ LIST REMOVE 'grape': fruits = ['apple', 'blueberry', 'cherry', 'orange']")

    # CLEAR
    runtime.execute_command('LIST', ['CLEAR', 'fruits'])
    assert runtime.get_variable('fruits') == []
    print("✅ LIST CLEAR: fruits = []")

    print("✅ All LIST operation tests passed!")


def test_list_literals_in_set():
    """Test using list literals with SET command."""
    print("\n=== Test: List Literals in SET ===")

    runtime = UPYRuntime()

    # Set variable to list literal
    runtime.execute_command('SET', ['colors', '[red, green, blue]'])
    colors = runtime.get_variable('colors')
    assert colors == ['red', 'green', 'blue'], f"Expected ['red', 'green', 'blue'], got {colors}"
    print("✅ SET colors [red, green, blue]")

    # Empty list
    runtime.execute_command('SET', ['empty', '[]'])
    empty = runtime.get_variable('empty')
    assert empty == [], f"Expected [], got {empty}"
    print("✅ SET empty []")

    print("✅ All list literal SET tests passed!")


def test_foreach_basic():
    """Test basic FOREACH loops."""
    print("\n=== Test: FOREACH Basic ===")

    script = """
# Create a list
(LIST|CREATE|fruits|apple|banana|cherry)

# Iterate and print
FOREACH {$item} IN {$fruits}
    (PRINT|{$item})
END
"""

    runtime = UPYRuntime()
    output = runtime.execute_script(script)

    assert len(output) == 3, f"Expected 3 outputs, got {len(output)}"
    assert output[0] == 'apple', f"Expected 'apple', got {output[0]}"
    assert output[1] == 'banana', f"Expected 'banana', got {output[1]}"
    assert output[2] == 'cherry', f"Expected 'cherry', got {output[2]}"

    print(f"✅ FOREACH output: {output}")
    print("✅ FOREACH basic test passed!")


def test_foreach_with_operations():
    """Test FOREACH with list operations inside loop."""
    print("\n=== Test: FOREACH with Operations ===")

    script = """
# Create source list
(LIST|CREATE|numbers|1|2|3|4|5)

# Create result list
(LIST|CREATE|doubled)

# Double each number and add to result
FOREACH {$n} IN {$numbers}
    (SET|doubled_value|{$n} * 2)
    (LIST|APPEND|doubled|{$doubled_value})
END

# Print result
(PRINT|Doubled: {$doubled})
"""

    runtime = UPYRuntime()
    output = runtime.execute_script(script)

    # Check doubled list
    doubled = runtime.get_variable('doubled')
    assert len(doubled) == 5, f"Expected 5 items, got {len(doubled)}"
    # Values are strings from math evaluation output
    assert str(doubled[0]) == '2', f"Expected '2', got {doubled[0]}"
    assert str(doubled[4]) == '10', f"Expected '10', got {doubled[4]}"

    print(f"✅ Doubled list: {doubled}")
    print("✅ FOREACH with operations test passed!")


def test_nested_lists():
    """Test nested list structures."""
    print("\n=== Test: Nested Lists ===")

    runtime = UPYRuntime()

    # Create list with list literal containing lists (as strings for now)
    runtime.execute_command('SET', ['matrix', '[[1,2,3], [4,5,6], [7,8,9]]'])
    matrix = runtime.get_variable('matrix')

    # Should be a list with 3 string elements (inner lists not parsed yet)
    assert isinstance(matrix, list), f"Expected list, got {type(matrix)}"
    assert len(matrix) == 3, f"Expected 3 rows, got {len(matrix)}"

    print(f"✅ Matrix created: {matrix}")
    print("✅ Nested list test passed!")


def test_list_with_variables():
    """Test list operations with variable substitution."""
    print("\n=== Test: Lists with Variables ===")

    script = """
# Set some variables
(SET|fruit1|apple)
(SET|fruit2|banana)
(SET|fruit3|cherry)

# Create list from variables
(LIST|CREATE|fruits|{$fruit1}|{$fruit2}|{$fruit3})

# Print
(PRINT|Fruits: {$fruits})
"""

    runtime = UPYRuntime()
    output = runtime.execute_script(script)

    fruits = runtime.get_variable('fruits')
    assert fruits == ['apple', 'banana', 'cherry'], f"Expected ['apple', 'banana', 'cherry'], got {fruits}"

    print(f"✅ Fruits from variables: {fruits}")
    print("✅ List with variables test passed!")


def test_list_negative_indexing():
    """Test negative index support."""
    print("\n=== Test: Negative Indexing ===")

    runtime = UPYRuntime()
    runtime.execute_command('LIST', ['CREATE', 'items', 'first', 'second', 'third', 'fourth'])

    # Get last item
    last = runtime.execute_command('LIST', ['GET', 'items', '-1'])
    assert last == 'fourth', f"Expected 'fourth', got {last}"
    print(f"✅ GET items[-1]: {last}")

    # Get second to last
    second_last = runtime.execute_command('LIST', ['GET', 'items', '-2'])
    assert second_last == 'third', f"Expected 'third', got {second_last}"
    print(f"✅ GET items[-2]: {second_last}")

    print("✅ Negative indexing test passed!")


def run_all_tests():
    """Run all list operation tests."""
    print("\n" + "=" * 60)
    print("uPY v2.0.2 - List Operations Test Suite")
    print("=" * 60)

    try:
        test_list_literal_parsing()
        test_list_operations()
        test_list_literals_in_set()
        test_foreach_basic()
        test_foreach_with_operations()
        test_nested_lists()
        test_list_with_variables()
        test_list_negative_indexing()

        print("\n" + "=" * 60)
        print("✅ ALL LIST TESTS PASSED!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
