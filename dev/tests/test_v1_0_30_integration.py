#!/usr/bin/env python3
"""
Test v1.0.30 Integration

Verifies all new components work together:
- Micro editor
- Knowledge file picker
- Enhanced smart prompt with fallback
- FILE EDIT/VIEW commands
"""

import sys
import os

# Add to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_micro_editor():
    """Test micro editor module loads."""
    print("Testing micro editor...")
    try:
        from core.ui.micro_editor import MicroEditor, edit_file, view_file
        print("  ✅ Micro editor module loaded")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def test_knowledge_picker():
    """Test knowledge file picker."""
    print("\nTesting knowledge file picker...")
    try:
        from core.services.knowledge_file_picker import KnowledgeFilePicker
        picker = KnowledgeFilePicker()

        # Get files
        k_files = picker.get_workspace_files('knowledge')
        m_files = picker.get_workspace_files('memory')

        print(f"  ✅ Found {len(k_files)} knowledge files")
        print(f"  ✅ Found {len(m_files)} memory files")

        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def test_smart_prompt():
    """Test enhanced smart prompt with fallback."""
    print("\nTesting smart prompt with fallback...")
    try:
        from core.input.smart_prompt import SmartPrompt

        # Test normal mode
        prompt = SmartPrompt(use_fallback=False)
        print("  ✅ SmartPrompt created (autocomplete mode)")

        # Test fallback mode
        prompt_fallback = SmartPrompt(use_fallback=True)
        print("  ✅ SmartPrompt created (fallback mode)")

        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_teletext_ui():
    """Test teletext UI components."""
    print("\nTesting teletext UI...")
    try:
        from core.ui.teletext_prompt import TeletextPromptStyle, TeletextBlocks
        from core.ui.picker import UniversalPicker, PickerConfig, PickerType, PickerItem

        style = TeletextPromptStyle()
        blocks = TeletextBlocks()

        # Test selection box
        items = ["Option 1", "Option 2", "Option 3"]
        box = style.create_selection_box("Test Menu", items)

        print("  ✅ Selection box created")

        # Test picker with teletext mode
        config = PickerConfig(title="Test", teletext_mode=True)
        picker = UniversalPicker(config)
        picker.add_item(PickerItem(id="1", label="Test Item"))

        output = picker.render()
        print("  ✅ Teletext picker rendered")

        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_handler_integration():
    """Test FILE handler integration."""
    print("\nTesting FILE handler integration...")
    try:
        from core.commands.file_handler import FileCommandHandler

        handler = FileCommandHandler()
        print("  ✅ File handler created")

        # Check methods exist
        assert hasattr(handler, '_handle_edit')
        assert hasattr(handler, '_handle_show')
        print("  ✅ Edit/Show methods present")

        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup_welcome():
    """Test startup welcome module."""
    print("\nTesting startup welcome...")
    try:
        from core.utils.startup_welcome import show_v1_0_30_welcome

        # This will print the welcome
        show_v1_0_30_welcome(70)
        print("  ✅ Welcome message displayed")

        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("uDOS v1.0.30 Integration Test Suite")
    print("=" * 70)
    print()

    tests = [
        test_micro_editor,
        test_knowledge_picker,
        test_smart_prompt,
        test_teletext_ui,
        test_file_handler_integration,
        test_startup_welcome,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  💥 Test crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 All integration tests passed! v1.0.30 is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
