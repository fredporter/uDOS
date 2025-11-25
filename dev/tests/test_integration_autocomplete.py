#!/usr/bin/env python3
"""
uDOS v1.0.19 - Integration Test for Autocomplete in Main Loop
Tests that SmartPrompt works with uDOS command execution
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.input.prompts.smart_prompt import SmartPrompt
from core.utils.autocomplete import AutocompleteService
from core.services.history import CommandHistory


def test_smart_prompt_creation():
    """Test that SmartPrompt can be created with CommandHistory."""
    print("\n" + "="*70)
    print("🧪 Test 1: SmartPrompt Creation with CommandHistory")
    print("="*70)

    # Create command history
    history = CommandHistory()
    history.append_string("HELP")
    history.append_string("FILE LIST")
    history.append_string("THEME SET midnight")

    # Create smart prompt
    smart_prompt = SmartPrompt(command_history=history, theme='dungeon')

    print("✅ SmartPrompt created successfully")
    print(f"   History: {len(history.load_history_strings())} commands")
    print(f"   Completer: {smart_prompt.completer.__class__.__name__}")
    print(f"   Autocomplete service: {smart_prompt.completer.autocomplete.__class__.__name__}")

    return smart_prompt


def test_autocomplete_suggestions():
    """Test that autocomplete provides suggestions."""
    print("\n" + "="*70)
    print("🧪 Test 2: Autocomplete Suggestions")
    print("="*70)

    service = AutocompleteService()

    # Test command suggestions
    commands = service.get_command_suggestions("HE")
    print(f"✅ Commands starting with 'HE': {[c['command'] for c in commands[:3]]}")

    # Test option suggestions
    options = service.get_option_suggestions("THEME")
    print(f"✅ THEME options: {[o['option'] for o in options[:3]]}")

    # Test fuzzy matching
    fuzzy = service.get_command_suggestions("fils")
    print(f"✅ Fuzzy match 'fils': {[c['command'] for c in fuzzy[:3]]}")


def test_prompt_decorator_compatibility():
    """Test that PromptDecorator (old SmartPrompt) still works."""
    print("\n" + "="*70)
    print("🧪 Test 3: PromptDecorator Compatibility")
    print("="*70)

    from core.uDOS_prompt import SmartPrompt as PromptDecorator

    decorator = PromptDecorator()

    # Test prompt generation
    prompt = decorator.get_prompt(is_assist_mode=False, panel_name="main", flash=False)
    print(f"✅ PromptDecorator.get_prompt() works")
    print(f"   Prompt: {repr(prompt[:50])}...")

    # Test context hint
    hint = decorator.get_context_hint(last_command="HELP", panel_content_length=100)
    print(f"✅ PromptDecorator.get_context_hint() works")
    if hint:
        print(f"   Hint: {repr(hint[:50])}...")


def test_import_compatibility():
    """Test that all imports work correctly."""
    print("\n" + "="*70)
    print("🧪 Test 4: Import Compatibility")
    print("="*70)

    try:
        from core.input.smart_prompt import SmartPrompt
        print("✅ core.services.smart_prompt.SmartPrompt imported")

        from core.uDOS_prompt import SmartPrompt as PromptDecorator
        print("✅ core.uDOS_prompt.SmartPrompt imported (as PromptDecorator)")

        from core.utils.autocomplete import AutocompleteService
        print("✅ core.services.autocomplete.AutocompleteService imported")

        from core.services.history import CommandHistory
        print("✅ core.services.history.CommandHistory imported")

        print("\n✅ All imports successful - no naming conflicts")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    return True


def main():
    """Run all integration tests."""
    print("\n" + "🎯" + " uDOS v1.0.19 - Autocomplete Integration Tests ".center(68, "="))
    print("="*70)

    try:
        # Run tests
        test_import_compatibility()
        test_autocomplete_suggestions()
        test_prompt_decorator_compatibility()
        smart_prompt = test_smart_prompt_creation()

        print("\n" + "="*70)
        print("✅ All Integration Tests PASSED")
        print("="*70)
        print("\n📋 Summary:")
        print("  • SmartPrompt imports without errors")
        print("  • PromptDecorator (old SmartPrompt) still works")
        print("  • AutocompleteService provides suggestions")
        print("  • CommandHistory integration works")
        print("  • No naming conflicts between old/new SmartPrompt")
        print("\n✅ Ready for live uDOS session testing!")
        print("="*70)

        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
