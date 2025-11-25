"""
uDOS v1.0.30 - Error Handling Tests

Tests for improved error handling including:
- Parser error handling with malformed commands
- Theme message loading and formatting
- Unknown command handling
- Bare except clause fixes
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_parser_default_params_handling():
    """Test parser handles DEFAULT_PARAMS type checking."""
    from core.uDOS_parser import Parser

    parser = Parser()

    # Test with command that has dict DEFAULT_PARAMS
    result = parser.parse('SET STORY.USER_NAME Fred')
    assert result == '[SYSTEM|SET*STORY.USER_NAME*Fred]'

    # Test with no params (empty DEFAULT_PARAMS)
    result = parser.parse('SET')
    assert result == '[SYSTEM|SET**]'

    print("✅ Parser DEFAULT_PARAMS handling works correctly")
    return True


def test_theme_message_loading():
    """Test theme messages are loaded correctly."""
    from core.commands.system_handler import SystemCommandHandler

    handler = SystemCommandHandler(theme='dungeon')

    # Check messages loaded
    assert len(handler.messages) > 0, "Messages should be loaded"
    assert len(handler.lexicon) > 0, "Lexicon should be loaded"

    # Check specific message exists
    assert 'ERROR_UNKNOWN_SYSTEM_COMMAND' in handler.messages

    print(f"✅ Theme loaded: {len(handler.messages)} messages, {len(handler.lexicon)} lexicon entries")
    return True


def test_unknown_command_error():
    """Test unknown command shows proper error message."""
    from core.commands.system_handler import SystemCommandHandler

    handler = SystemCommandHandler(theme='dungeon')

    # Test with unknown command
    result = handler.get_message('ERROR_UNKNOWN_SYSTEM_COMMAND', command='q')

    # Should be formatted, not raw template
    assert result != '<ERROR_UNKNOWN_SYSTEM_COMMAND>'
    assert result != 'ERROR_UNKNOWN_SYSTEM_COMMAND'
    assert 'q' in result

    # Should match dungeon theme style
    assert '💀' in result or 'UNKNOWN' in result

    print(f"✅ Unknown command error: {result}")
    return True


def test_fallback_error_messages():
    """Test fallback error messages for missing keys."""
    from core.commands.system_handler import SystemCommandHandler

    handler = SystemCommandHandler(theme='dungeon')

    # Test with non-existent key and params
    result1 = handler.get_message('NONEXISTENT_KEY', param='value')
    assert '⚠️' in result1
    assert 'NONEXISTENT_KEY' in result1

    # Test with non-existent key without params
    result2 = handler.get_message('ANOTHER_MISSING_KEY')
    assert '⚠️' in result2
    assert 'ANOTHER_MISSING_KEY' in result2

    print(f"✅ Fallback messages work: '{result1}', '{result2}'")
    return True


def test_specific_exceptions():
    """Test that bare except clauses have been replaced with specific exceptions."""
    import inspect
    from core.ui import micro_editor
    from core.services import file_picker, session_manager

    # Get source code
    micro_source = inspect.getsource(micro_editor)
    picker_source = inspect.getsource(file_picker)
    session_source = inspect.getsource(session_manager)

    # Check for improvements (should have specific exceptions)
    assert 'except (KeyboardInterrupt, EOFError)' in micro_source
    assert 'except (subprocess.CalledProcessError' in picker_source
    assert 'except (ImportError, AttributeError' in session_source

    print("✅ Specific exception types used instead of bare except")
    return True


def test_parser_error_resilience():
    """Test parser handles various error conditions gracefully."""
    from core.uDOS_parser import Parser

    parser = Parser()

    # Test empty input
    result = parser.parse('')
    assert isinstance(result, str)

    # Test unknown command
    result = parser.parse('NONEXISTENT_COMMAND')
    assert isinstance(result, str)

    # Test malformed input
    result = parser.parse('   ')
    assert isinstance(result, str)

    print("✅ Parser handles error conditions gracefully")
    return True


def test_end_to_end_error_flow():
    """Test complete error flow from command to output."""
    from core.commands.system_handler import SystemCommandHandler

    handler = SystemCommandHandler(theme='dungeon')

    # Simulate unknown command through handler
    result = handler.handle('INVALID_COMMAND', [], None, None)

    # Should return themed error message
    assert isinstance(result, str)
    assert len(result) > 0
    assert result != '<ERROR_UNKNOWN_SYSTEM_COMMAND>'

    print(f"✅ End-to-end error flow: {result}")
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("uDOS v1.0.30 - Error Handling Tests")
    print("="*60 + "\n")

    tests = [
        ("Parser DEFAULT_PARAMS handling", test_parser_default_params_handling),
        ("Theme message loading", test_theme_message_loading),
        ("Unknown command error", test_unknown_command_error),
        ("Fallback error messages", test_fallback_error_messages),
        ("Specific exception types", test_specific_exceptions),
        ("Parser error resilience", test_parser_error_resilience),
        ("End-to-end error flow", test_end_to_end_error_flow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"\n{test_name}:")
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    sys.exit(0 if failed == 0 else 1)
