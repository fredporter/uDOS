"""
Test Suite: uPY v2.0.2 File I/O Operations

Tests FILE and JSON commands for reading, writing, and data persistence.
"""

import sys
import json
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.runtime.upy_runtime_v2 import UPYRuntime
from core.runtime.upy_file_io import FileIO, FileIOError


def test_file_read_write():
    """Test basic file read and write operations."""
    print("\n=== Test: File Read/Write ===")

    runtime = UPYRuntime()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("Hello, uPY!")

    try:
        # Read file
        content = runtime.execute_command('FILE', ['READ', test_file])
        assert content == "Hello, uPY!", f"Expected 'Hello, uPY!', got {content}"
        print(f"✅ FILE READ: {content}")

        # Read into variable
        runtime.execute_command('FILE', ['READ', test_file, 'file_content'])
        var_content = runtime.get_variable('file_content')
        assert var_content == "Hello, uPY!", f"Expected 'Hello, uPY!', got {var_content}"
        print(f"✅ FILE READ into variable: {var_content}")

        # Write new content
        new_file = test_file.replace('.txt', '_new.txt')
        runtime.execute_command('FILE', ['WRITE', new_file, 'New content!'])

        # Read back
        new_content = runtime.execute_command('FILE', ['READ', new_file])
        assert new_content == "New content!", f"Expected 'New content!', got {new_content}"
        print(f"✅ FILE WRITE then READ: {new_content}")

        # Append
        runtime.execute_command('FILE', ['WRITE', new_file, '\nAppended line', 'APPEND'])
        appended_content = runtime.execute_command('FILE', ['READ', new_file])
        assert "Appended line" in appended_content
        print(f"✅ FILE WRITE APPEND: {appended_content}")

        # Clean up
        Path(new_file).unlink()

    finally:
        Path(test_file).unlink()

    print("✅ All file read/write tests passed!")


def test_file_exists():
    """Test file existence checks."""
    print("\n=== Test: File EXISTS ===")

    runtime = UPYRuntime()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("test")

    try:
        # Check existing file
        exists = runtime.execute_command('FILE', ['EXISTS', test_file])
        assert exists == True, f"Expected True, got {exists}"
        print(f"✅ FILE EXISTS (existing): {exists}")

        # Check non-existing file
        exists = runtime.execute_command('FILE', ['EXISTS', '/tmp/nonexistent_file_xyz.txt'])
        assert exists == False, f"Expected False, got {exists}"
        print(f"✅ FILE EXISTS (non-existing): {exists}")

    finally:
        Path(test_file).unlink()

    print("✅ All file exists tests passed!")


def test_file_delete():
    """Test file deletion."""
    print("\n=== Test: File DELETE ===")

    runtime = UPYRuntime()

    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write("to be deleted")

    # Verify exists
    assert Path(test_file).exists()
    print(f"✅ File created: {test_file}")

    # Delete
    result = runtime.execute_command('FILE', ['DELETE', test_file])
    assert result == True
    assert not Path(test_file).exists()
    print(f"✅ FILE DELETE: Success")

    print("✅ All file delete tests passed!")


def test_file_size():
    """Test file size retrieval."""
    print("\n=== Test: File SIZE ===")

    runtime = UPYRuntime()

    # Create temp file with known content
    content = "1234567890"  # 10 bytes
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = f.name
        f.write(content)

    try:
        size = runtime.execute_command('FILE', ['SIZE', test_file])
        assert size == 10, f"Expected 10, got {size}"
        print(f"✅ FILE SIZE: {size} bytes")

    finally:
        Path(test_file).unlink()

    print("✅ All file size tests passed!")


def test_json_parse_stringify():
    """Test JSON parsing and stringification."""
    print("\n=== Test: JSON PARSE/STRINGIFY ===")

    runtime = UPYRuntime()

    # Parse JSON string
    json_str = '{"name": "Alice", "age": 30, "city": "Sydney"}'
    data = runtime.execute_command('JSON', ['PARSE', json_str])
    assert data['name'] == 'Alice', f"Expected 'Alice', got {data['name']}"
    assert data['age'] == 30, f"Expected 30, got {data['age']}"
    print(f"✅ JSON PARSE: {data}")

    # Parse into variable
    runtime.execute_command('JSON', ['PARSE', json_str, 'user_data'])
    var_data = runtime.get_variable('user_data')
    assert var_data['name'] == 'Alice'
    print(f"✅ JSON PARSE into variable: {var_data}")

    # Stringify
    runtime.set_variable('person', {'name': 'Bob', 'age': 25})
    json_output = runtime.execute_command('JSON', ['STRINGIFY', 'person'])
    assert 'Bob' in json_output
    assert '25' in json_output
    print(f"✅ JSON STRINGIFY: {json_output}")

    # Stringify with indent
    runtime.execute_command('JSON', ['STRINGIFY', 'person', 'json_result', '2'])
    json_pretty = runtime.get_variable('json_result')
    assert '\n' in json_pretty  # Should have newlines with indentation
    print(f"✅ JSON STRINGIFY (pretty): {json_pretty}")

    print("✅ All JSON parse/stringify tests passed!")


def test_json_read_write():
    """Test JSON file read and write operations."""
    print("\n=== Test: JSON READ/WRITE ===")

    runtime = UPYRuntime()

    # Create temp JSON file
    test_data = {
        "fruits": ["apple", "banana", "cherry"],
        "count": 3,
        "active": True
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        test_file = f.name
        json.dump(test_data, f)

    try:
        # Read JSON file
        data = runtime.execute_command('JSON', ['READ', test_file])
        assert data['fruits'] == ["apple", "banana", "cherry"]
        assert data['count'] == 3
        print(f"✅ JSON READ: {data}")

        # Read into variable
        runtime.execute_command('JSON', ['READ', test_file, 'config'])
        var_data = runtime.get_variable('config')
        assert var_data['active'] == True
        print(f"✅ JSON READ into variable: {var_data}")

        # Write JSON file
        runtime.set_variable('new_data', {
            "items": ["x", "y", "z"],
            "total": 100
        })
        new_file = test_file.replace('.json', '_new.json')
        runtime.execute_command('JSON', ['WRITE', new_file, 'new_data'])

        # Read back
        written_data = runtime.execute_command('JSON', ['READ', new_file])
        assert written_data['items'] == ["x", "y", "z"]
        assert written_data['total'] == 100
        print(f"✅ JSON WRITE then READ: {written_data}")

        # Clean up
        Path(new_file).unlink()

    finally:
        Path(test_file).unlink()

    print("✅ All JSON read/write tests passed!")


def test_file_io_with_lists():
    """Test file I/O integration with list operations."""
    print("\n=== Test: File I/O with Lists ===")

    script = """
# Create a list
(LIST|CREATE|shopping|milk|eggs|bread|butter)

# Convert to JSON and save
(JSON|STRINGIFY|shopping|shopping_json)
(FILE|WRITE|/tmp/upy_test_shopping.json|{$shopping_json})

# Read back
(JSON|READ|/tmp/upy_test_shopping.json|loaded_shopping)

# Print
(PRINT|Loaded shopping list: {$loaded_shopping})
"""

    runtime = UPYRuntime()
    output = runtime.execute_script(script)

    # Check loaded list
    loaded = runtime.get_variable('loaded_shopping')
    assert loaded == ["milk", "eggs", "bread", "butter"]
    print(f"✅ List saved and loaded: {loaded}")

    # Clean up
    Path('/tmp/upy_test_shopping.json').unlink()

    print("✅ File I/O with lists test passed!")


def test_complex_json_structures():
    """Test complex nested JSON structures."""
    print("\n=== Test: Complex JSON Structures ===")

    runtime = UPYRuntime()

    # Create complex structure
    complex_data = {
        "users": [
            {"name": "Alice", "age": 30, "skills": ["Python", "JavaScript"]},
            {"name": "Bob", "age": 25, "skills": ["Java", "C++"]}
        ],
        "metadata": {
            "version": "1.0",
            "created": "2025-12-06"
        }
    }

    runtime.set_variable('app_data', complex_data)

    # Write to file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        test_file = f.name

    try:
        runtime.execute_command('JSON', ['WRITE', test_file, 'app_data', '2'])

        # Read back
        loaded = runtime.execute_command('JSON', ['READ', test_file])

        # Verify structure
        assert loaded['users'][0]['name'] == 'Alice'
        assert loaded['users'][1]['skills'][0] == 'Java'
        assert loaded['metadata']['version'] == '1.0'
        print(f"✅ Complex JSON preserved: {loaded['users'][0]['name']} has {len(loaded['users'][0]['skills'])} skills")

    finally:
        Path(test_file).unlink()

    print("✅ Complex JSON test passed!")


def test_file_io_script():
    """Test complete file I/O workflow in a script."""
    print("\n=== Test: File I/O Script Workflow ===")

    script = """
# Create data
(SET|username|Explorer)
(SET|score|1000)
(SET|level|5)

# Check if save file exists
(FILE|EXISTS|/tmp/upy_savegame.txt)

# Write save data
(FILE|WRITE|/tmp/upy_savegame.txt|User: {$username}, Score: {$score}, Level: {$level})

# Read it back
(FILE|READ|/tmp/upy_savegame.txt|save_data)

# Print
(PRINT|Save data: {$save_data})
"""

    runtime = UPYRuntime()
    output = runtime.execute_script(script)

    # Verify
    save_data = runtime.get_variable('save_data')
    assert 'Explorer' in save_data
    assert '1000' in save_data
    assert 'Level: 5' in save_data
    print(f"✅ Save data: {save_data}")

    # Clean up
    Path('/tmp/upy_savegame.txt').unlink()

    print("✅ File I/O script workflow test passed!")


def run_all_tests():
    """Run all file I/O tests."""
    print("\n" + "=" * 60)
    print("uPY v2.0.2 - File I/O Operations Test Suite")
    print("=" * 60)

    try:
        test_file_read_write()
        test_file_exists()
        test_file_delete()
        test_file_size()
        test_json_parse_stringify()
        test_json_read_write()
        test_file_io_with_lists()
        test_complex_json_structures()
        test_file_io_script()

        print("\n" + "=" * 60)
        print("✅ ALL FILE I/O TESTS PASSED!")
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
