#!/usr/bin/env python3
"""
TUI Arrow Key Test Script

Tests if arrow keys work properly in the current terminal environment.
Run this to verify your TUI setup before launching uDOS.

Usage:
    python3 bin/test-arrow-keys.py
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_terminal():
    """Check terminal capabilities."""
    print("=== Terminal Check ===\n")

    # Check TTY
    is_stdin_tty = sys.stdin.isatty()
    is_stdout_tty = sys.stdout.isatty()

    print(f"stdin is TTY:  {'✓' if is_stdin_tty else '✗'}")
    print(f"stdout is TTY: {'✓' if is_stdout_tty else '✗'}")

    # Check TERM
    term = os.environ.get('TERM', 'unknown')
    print(f"TERM:          {term}")

    if term == 'dumb':
        print("  ⚠️  TERM=dumb detected - arrow keys will not work")
    elif 'xterm' in term or 'screen' in term:
        print("  ✓ TERM supports arrow keys")

    return is_stdin_tty and is_stdout_tty


def check_modules():
    """Check required Python modules."""
    print("\n=== Module Check ===\n")

    modules_ok = True

    # Check prompt_toolkit
    try:
        import prompt_toolkit
        print(f"✓ prompt_toolkit {prompt_toolkit.__version__}")
    except ImportError:
        print("✗ prompt_toolkit not installed")
        print("  Fix: pip install prompt_toolkit>=3.0.0")
        modules_ok = False

    # Check readline
    try:
        import readline
        print("✓ readline available")
    except ImportError:
        print("✗ readline not available")
        print("  Fix (Ubuntu): sudo apt-get install libreadline-dev")
        modules_ok = False

    return modules_ok


def test_arrow_keys():
    """Test arrow key input."""
    print("\n=== Arrow Key Test ===\n")

    try:
        from prompt_toolkit import prompt
        from prompt_toolkit.key_binding import KeyBindings

        bindings = KeyBindings()

        @bindings.add('up')
        def _(event):
            print("\n✓ Up arrow detected!")

        @bindings.add('down')
        def _(event):
            print("\n✓ Down arrow detected!")

        @bindings.add('left')
        def _(event):
            print("\n✓ Left arrow detected!")

        @bindings.add('right')
        def _(event):
            print("\n✓ Right arrow detected!")

        print("Test arrow keys (press Ctrl+C or Ctrl+D to exit):")
        print("Try: ↑ ↓ ← →")
        print()

        try:
            result = prompt("Test: ", key_bindings=bindings)
            print(f"\nYou entered: {result}")
        except (KeyboardInterrupt, EOFError):
            print("\n\nTest cancelled.")

        return True

    except ImportError:
        print("✗ Cannot test - prompt_toolkit not available")
        return False


def test_fallback():
    """Test basic input fallback."""
    print("\n=== Fallback Test ===\n")
    print("Testing basic input (no arrow keys):")

    try:
        response = input("Enter text: ")
        print(f"✓ Basic input works: {response}")
        return True
    except Exception as e:
        print(f"✗ Basic input failed: {e}")
        return False


def print_recommendations():
    """Print fix recommendations."""
    print("\n=== Recommendations ===\n")

    # Check if Ubuntu/Debian
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read().lower()
            if 'ubuntu' in os_info or 'debian' in os_info:
                print("Ubuntu/Debian detected. Install system dependencies:")
                print()
                print("  sudo apt-get update")
                print("  sudo apt-get install -y libreadline-dev libncurses5-dev python3-dev")
                print()
                print("Then reinstall Python packages:")
                print()
                print("  source .venv/bin/activate")
                print("  pip install --upgrade --force-reinstall prompt_toolkit")
                print()
    except FileNotFoundError:
        pass

    print("For other issues, see:")
    print("  docs/troubleshooting/TUI-ARROW-KEYS-UBUNTU.md")
    print("  docs/troubleshooting/README.md")


def main():
    """Run all checks."""
    print()
    print("╔═══════════════════════════════════════════════════╗")
    print("║    uDOS TUI Arrow Key Test                        ║")
    print("╚═══════════════════════════════════════════════════╝")
    print()

    terminal_ok = check_terminal()
    modules_ok = check_modules()

    if not terminal_ok:
        print("\n⚠️  Terminal not interactive - arrow keys will not work")
        print("   Run this script in a proper terminal emulator")
        test_fallback()
        print_recommendations()
        return 1

    if not modules_ok:
        print("\n⚠️  Required modules missing - install dependencies")
        test_fallback()
        print_recommendations()
        return 1

    # Run arrow key test
    test_ok = test_arrow_keys()

    if test_ok:
        print("\n✅ Arrow keys are working correctly!")
        print("   uDOS TUI should work with full features.")
    else:
        print("\n⚠️  Arrow key test failed")
        print_recommendations()
        return 1

    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
