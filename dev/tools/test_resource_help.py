#!/usr/bin/env python3
"""
Debug test for RESOURCE HELP color output
Tests ANSI color rendering and command routing
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_ansi_colors():
    """Test basic ANSI color output"""
    print("=" * 70)
    print("Test 1: ANSI Color Codes")
    print("=" * 70)

    CYAN = '\033[1;36m'
    YELLOW = '\033[1;33m'
    GREEN = '\033[1;32m'
    BLUE = '\033[34m'
    RESET = '\033[0m'

    print(f"{CYAN}CYAN: This should be bright cyan{RESET}")
    print(f"{YELLOW}YELLOW: This should be bright yellow{RESET}")
    print(f"{GREEN}GREEN: This should be bright green{RESET}")
    print(f"{BLUE}BLUE: This should be blue{RESET}")
    print("WHITE: This should be default color")
    print()

def test_resource_handler_direct():
    """Test resource_handler directly"""
    print("=" * 70)
    print("Test 2: Direct resource_handler import and call")
    print("=" * 70)

    try:
        from core.commands.resource_handler import handle_resource_command
        print("✅ Import successful")

        print("\nCalling handle_resource_command('HELP')...")
        print("-" * 70)
        result = handle_resource_command('HELP')
        print("-" * 70)

        print(f"\n✅ Result: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    print()

def test_command_router():
    """Test through command handler routing"""
    print("=" * 70)
    print("Test 3: Command routing via CommandHandler")
    print("=" * 70)

    try:
        from core.uDOS_commands import CommandHandler
        print("✅ CommandHandler imported")

        # Initialize handler
        handler = CommandHandler()
        print("✅ CommandHandler initialized")

        # Test RESOURCE HELP via uCODE format
        print("\nCalling handler.handle_command('[RESOURCE|HELP]', None, None)...")
        print("-" * 70)
        result = handler.handle_command('[RESOURCE|HELP]', None, None)
        print("-" * 70)

        print(f"\n✅ Result type: {type(result)}")
        print(f"✅ Result preview: {str(result)[:100]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    print()

def test_color_in_output():
    """Test if ANSI codes are preserved in output"""
    print("=" * 70)
    print("Test 4: ANSI code preservation")
    print("=" * 70)

    test_string = '\033[1;36mCOLORED\033[0m text'
    print(f"Test string: {repr(test_string)}")
    print(f"Rendered: {test_string}")

    # Check if codes are in string
    has_ansi = '\033[' in test_string
    print(f"Contains ANSI codes: {has_ansi}")
    print()

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("RESOURCE HELP Color Debug Tests")
    print("=" * 70 + "\n")

    test_ansi_colors()
    test_color_in_output()
    test_resource_handler_direct()
    test_command_router()

    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)

if __name__ == '__main__':
    main()
