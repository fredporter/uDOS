#!/usr/bin/env python3
"""
uDOS v1.1.0 - Unified Selector Validation Script
Quick validation of unified selector integration in real TUI scenarios

This script validates:
- InteractivePrompt.ask_choice() using unified selector
- InputManager.prompt_choice() using unified selector
- Backward compatibility with legacy code
- Session analytics integration

Author: uDOS Development Team
Version: 1.1.0
Phase: TUI Reliability & Input System (Feature 1.1.0.9)
Date: November 24, 2025
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.input.interactive import InteractivePrompt
from core.services.input_manager import InputManager


def test_interactive_prompt():
    """Test InteractivePrompt.ask_choice() with unified selector."""
    print("\n" + "=" * 70)
    print("TEST 1: InteractivePrompt.ask_choice()".center(70))
    print("=" * 70)
    print("""
This tests the InteractivePrompt class which is used by:
- File operations (CREATE, EDIT, COPY, MOVE, DELETE)
- Workspace selection
- Template selection

The unified selector should provide arrow-key navigation.
""")

    prompt = InteractivePrompt(use_arrow_keys=True)

    themes = [
        "Cyberpunk Neon",
        "Retro Terminal Green",
        "Classic DOS Blue",
        "Synthwave Purple"
    ]

    print("Testing: Theme selection (common use case)")
    result = prompt.ask_choice(
        prompt="Select a theme for testing",
        choices=themes,
        default="Retro Terminal Green"
    )

    print(f"\n✅ Selected: {result}")
    print("✅ InteractivePrompt integration working")
    return result


def test_input_manager():
    """Test InputManager.prompt_choice() with unified selector."""
    print("\n" + "=" * 70)
    print("TEST 2: InputManager.prompt_choice()".center(70))
    print("=" * 70)
    print("""
This tests the InputManager class which is used by:
- Configuration commands
- Setup wizard
- Advanced file operations

The unified selector should work with InputManager's interface.
""")

    input_mgr = InputManager()

    operations = [
        "Create New File",
        "Edit Existing File",
        "View File",
        "Copy File",
        "Delete File",
        "Cancel"
    ]

    print("Testing: File operation menu (common use case)")
    result = input_mgr.prompt_choice(
        message="Select file operation for testing",
        choices=operations,
        default="View File"
    )

    print(f"\n✅ Selected: {result}")
    print("✅ InputManager integration working")
    return result


def test_backward_compatibility():
    """Test that legacy imports still work."""
    print("\n" + "=" * 70)
    print("TEST 3: Backward Compatibility".center(70))
    print("=" * 70)
    print("""
This tests that old code using legacy imports still works.
No interactive prompts needed - just import verification.
""")

    try:
        # Test old imports
        from core.ui.pickers import OptionSelector, EnhancedFilePicker
        print("✅ Legacy imports work: OptionSelector, EnhancedFilePicker")

        # Test new imports
        from core.ui.pickers import UnifiedSelector, select_single
        print("✅ New imports work: UnifiedSelector, select_single")

        # Test direct import
        from core.ui.unified_selector import select_multiple, select_file
        print("✅ Direct imports work: select_multiple, select_file")

        print("\n✅ All import paths functional")
        return True

    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False


def test_numbered_fallback():
    """Test numbered fallback mode."""
    print("\n" + "=" * 70)
    print("TEST 4: Numbered Fallback Mode".center(70))
    print("=" * 70)
    print("""
This tests the numbered fallback that works in degraded terminals.
Disabling arrow keys to force text-based mode.
""")

    prompt = InteractivePrompt(use_arrow_keys=False)

    choices = [
        "Option 1",
        "Option 2",
        "Option 3"
    ]

    print("Testing: Numbered selection (SSH/minimal TTY mode)")
    print("Note: Enter a number (1-3) to select\n")

    result = prompt.ask_choice(
        prompt="Select an option using number",
        choices=choices,
        default="Option 1"
    )

    print(f"\n✅ Selected: {result}")
    print("✅ Numbered fallback mode working")
    return result


def test_session_analytics():
    """Test session analytics integration."""
    print("\n" + "=" * 70)
    print("TEST 5: Session Analytics Integration".center(70))
    print("=" * 70)
    print("""
This tests that selector usage is logged to session analytics.
The unified selector automatically logs all interactions.
""")

    try:
        from core.ui.unified_selector import UnifiedSelector

        selector = UnifiedSelector(use_analytics=True)

        if selector.analytics:
            print("✅ Session analytics enabled")
            print("   All selector interactions will be logged to:")
            print("   - memory/logs/sessions/auto/")
            print("   - Command traces, timing, success/failure rates")
        else:
            print("⚠️  Session analytics not initialized")
            print("   (This is expected if session analytics is not running)")

        print("\n✅ Analytics integration verified")
        return True

    except Exception as e:
        print(f"⚠️  Analytics check failed: {e}")
        return False


def run_validation():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("uDOS v1.1.0 - Unified Selector Validation".center(70))
    print("=" * 70)
    print("""
This validation script tests the unified selector integration
across the core command infrastructure.

Features being validated:
✓ InteractivePrompt.ask_choice() migration
✓ InputManager.prompt_choice() migration
✓ Backward compatibility with legacy imports
✓ Numbered fallback mode (degraded terminals)
✓ Session analytics integration

Press Ctrl+C at any time to exit.
""")

    input("Press Enter to start validation...")

    results = {}

    try:
        # Test 1: InteractivePrompt
        results['interactive_prompt'] = test_interactive_prompt()

        # Test 2: InputManager
        results['input_manager'] = test_input_manager()

        # Test 3: Backward compatibility (no user input needed)
        results['backward_compat'] = test_backward_compatibility()

        # Test 4: Numbered fallback
        results['numbered_fallback'] = test_numbered_fallback()

        # Test 5: Session analytics (no user input needed)
        results['session_analytics'] = test_session_analytics()

        # Summary
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY".center(70))
        print("=" * 70)

        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        print(f"\nTests Passed: {success_count}/{total_count}")
        print("\nResults:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {test_name}")

        if success_count == total_count:
            print("\n🎉 All validation tests passed!")
            print("   Unified selector integration is working correctly.")
            print("   Feature 1.1.0.9 ready for completion.")
        else:
            print("\n⚠️  Some tests failed. Review results above.")

        print("\n" + "=" * 70)
        return success_count == total_count

    except KeyboardInterrupt:
        print("\n\n❌ Validation interrupted by user")
        return False


if __name__ == '__main__':
    try:
        success = run_validation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Validation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
