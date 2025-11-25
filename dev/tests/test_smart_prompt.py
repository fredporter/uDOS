"""
uDOS v1.0.19 - Smart Prompt Interactive Test
Manual test for autocomplete with prompt_toolkit
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.input.smart_prompt import SmartPrompt


def test_interactive_prompt():
    """
    Interactive test for smart prompt.
    User can type commands and see autocomplete in action.
    """
    print("\n" + "="*70)
    print("🚀 uDOS v1.0.19 - Smart Prompt Interactive Test")
    print("="*70)
    print("\nFeatures to test:")
    print("  • Type partial command (e.g., 'HE') and press Tab")
    print("  • Use arrow keys to navigate suggestions")
    print("  • Press Ctrl+R to search command history")
    print("  • Type 'THEME ' and press Tab for options")
    print("  • Type 'FILE ' and press Tab for file operations")
    print("  • Press Ctrl+C to exit")
    print("\n" + "="*70)

    smart_prompt = SmartPrompt()

    try:
        while True:
            command = smart_prompt.ask(prompt_text="\n\x1b[32muDOS>\x1b[0m ")

            if not command:
                continue

            if command.upper() in ['EXIT', 'QUIT', 'Q']:
                print("\n✅ Exiting test...")
                break

            # Echo the command
            print(f"\n✅ You entered: {command}")

            # Parse command for feedback
            words = command.split()
            if words:
                cmd = words[0].upper()
                print(f"   Command: {cmd}")
                if len(words) > 1:
                    print(f"   Options/Args: {' '.join(words[1:])}")

            # Provide command-specific feedback
            if cmd == 'HELP':
                print("\n   💡 HELP command - would show help information")
            elif cmd == 'FILE':
                print("\n   💡 FILE command - would perform file operations")
                if len(words) > 1:
                    print(f"      Operation: {words[1]}")
            elif cmd == 'MAP':
                print("\n   💡 MAP command - would show map navigation")
            elif cmd == 'THEME':
                print("\n   💡 THEME command - would manage themes")
                if len(words) > 1:
                    print(f"      Subcommand: {words[1]}")
            else:
                print(f"\n   💡 Would execute: {command}")

    except KeyboardInterrupt:
        print("\n\n✅ Test interrupted by user")

    print("\n" + "="*70)
    print("Test complete! Autocomplete features demonstrated:")
    print("  ✅ Command suggestions")
    print("  ✅ Option/subcommand suggestions")
    print("  ✅ Tab completion")
    print("  ✅ Arrow key navigation")
    print("  ✅ Command history (Ctrl+R)")
    print("="*70 + "\n")


def test_basic_functionality():
    """Test basic prompt functionality without interaction."""
    print("\n" + "="*70)
    print("TEST: Basic SmartPrompt Functionality")
    print("="*70)

    smart_prompt = SmartPrompt()

    # Test 1: Prompt creation
    print("\n1. SmartPrompt instance created")
    print(f"   ✅ Autocomplete service: {smart_prompt.autocomplete is not None}")
    print(f"   ✅ Completer: {smart_prompt.completer is not None}")
    print(f"   ✅ History: {smart_prompt.pt_history is not None}")

    # Test 2: Completer functionality
    print("\n2. Testing completer directly:")
    from prompt_toolkit.document import Document

    # Test command completion
    doc = Document('HE', cursor_position=2)
    completions = list(smart_prompt.completer.get_completions(doc, None))
    print(f"   Completions for 'HE': {len(completions)} found")
    for i, comp in enumerate(completions[:3], 1):
        print(f"      {i}. {comp.text} - {comp.display}")

    # Test option completion
    doc = Document('THEME SE', cursor_position=8)
    completions = list(smart_prompt.completer.get_completions(doc, None))
    print(f"\n   Completions for 'THEME SE': {len(completions)} found")
    for i, comp in enumerate(completions[:3], 1):
        print(f"      {i}. {comp.text}")

    print("\n✅ Basic functionality test complete")


if __name__ == '__main__':
    print("\n" + "🎯 uDOS v1.0.19 - Smart Prompt Test Suite")
    print("="*70)

    # Run basic tests first
    test_basic_functionality()

    print("\n" + "="*70)
    print("Ready for interactive test?")
    print("  • This will start an interactive prompt")
    print("  • You can test autocomplete features live")
    print("  • Type 'exit' or press Ctrl+C to quit")
    print("="*70)

    try:
        response = input("\nStart interactive test? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            test_interactive_prompt()
        else:
            print("\n✅ Skipping interactive test")
    except KeyboardInterrupt:
        print("\n\n✅ Test cancelled")

    print("\nAll tests complete! 🎉\n")
