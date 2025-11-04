#!/usr/bin/env python3
"""
Test RUN command implementation
Tests basic .uscript execution
"""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from core.uDOS_ucode import UCodeInterpreter


def test_standalone_execution():
    """Test standalone script execution without full uDOS."""
    print("=" * 60)
    print("TEST: Standalone .uscript Execution")
    print("=" * 60)

    # Create a simple test script
    test_script = "/tmp/test_udos.uscript"
    with open(test_script, 'w') as f:
        f.write("""# Test Script
# Simple commands to validate execution

[SYSTEM|HELP]
[FILE|PWD]
""")

    # Execute without full context (should show warnings)
    interpreter = UCodeInterpreter()
    result = interpreter.execute_script(test_script)

    print(result)
    print("\n" + "=" * 60)
    print("✅ Test completed - check output above")
    print("   (Warnings expected without full uDOS context)")
    print("=" * 60)

    # Cleanup
    os.remove(test_script)


def test_script_parsing():
    """Test script parsing and line handling."""
    print("\n" + "=" * 60)
    print("TEST: Script Parsing")
    print("=" * 60)

    test_script = "/tmp/test_parse.uscript"
    with open(test_script, 'w') as f:
        f.write("""# Comment line - should be skipped

# Another comment
[SYSTEM|STATUS]

# Empty lines above and below should be ignored

[FILE|LS]
""")

    interpreter = UCodeInterpreter()
    result = interpreter.execute_script(test_script)

    print(result)

    # Check that comments were skipped
    if "Comment line" not in result:
        print("\n✅ Comments properly skipped")
    else:
        print("\n❌ Comments not skipped!")

    os.remove(test_script)


def test_error_handling():
    """Test error handling in scripts."""
    print("\n" + "=" * 60)
    print("TEST: Error Handling")
    print("=" * 60)

    test_script = "/tmp/test_errors.uscript"
    with open(test_script, 'w') as f:
        f.write("""# Test error handling
[INVALID|COMMAND]
[SYSTEM|HELP]
""")

    interpreter = UCodeInterpreter()
    result = interpreter.execute_script(test_script)

    print(result)

    # Should continue after error
    if "Error" in result and "HELP" in result:
        print("\n✅ Continues after error")

    os.remove(test_script)


if __name__ == '__main__':
    print("\n🧪 Testing RUN Command Implementation\n")

    test_standalone_execution()
    test_script_parsing()
    test_error_handling()

    print("\n" + "=" * 60)
    print("🎯 All tests completed!")
    print("=" * 60)
    print("\nNext: Test with full uDOS context using:")
    print("  ./start_udos.sh examples/hello-automation.uscript")
    print("=" * 60)
