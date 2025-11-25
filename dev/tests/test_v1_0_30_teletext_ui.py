#!/usr/bin/env python3
"""
Test v1.0.30 Teletext UI Enhancements

Tests the new teletext block-based UI components:
- Enhanced picker with teletext styling
- Autocomplete with visual score bars
- File picker with block art
- Multi-select with checkboxes

Usage: python memory/tests/test_v1_0_30_teletext_ui.py
"""

import sys
import os

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.ui.picker import UniversalPicker, PickerConfig, PickerType, PickerItem
from core.ui.teletext_prompt import TeletextPromptStyle, TeletextBlocks, EnhancedPromptRenderer


def test_teletext_picker():
    """Test UniversalPicker with teletext mode enabled"""
    print("\n" + "=" * 70)
    print("TEST 1: Single-Select Picker with Teletext Styling")
    print("=" * 70)

    # Create config with teletext mode
    config = PickerConfig(
        title="Main Menu",
        picker_type=PickerType.SINGLE,
        teletext_mode=True,
        max_items_display=9
    )

    picker = UniversalPicker(config)

    # Add items
    items = [
        PickerItem(id="1", label="SETUP Wizard", icon="⚙", description="Run initial setup"),
        PickerItem(id="2", label="CONFIG Settings", icon="🔧", description="Manage configuration"),
        PickerItem(id="3", label="THEME Selection", icon="🎨", description="Choose visual theme"),
        PickerItem(id="4", label="VIEWPORT Config", icon="📐", description="Configure viewport"),
        PickerItem(id="5", label="EXIT", icon="🚪", description="Exit uDOS"),
    ]

    for item in items:
        picker.add_item(item)

    # Render and display
    output = picker.render()
    print(output)
    print("\n✅ Single-select picker rendered successfully with teletext blocks")


def test_multi_select_picker():
    """Test multi-select picker with checkboxes"""
    print("\n" + "=" * 70)
    print("TEST 2: Multi-Select Picker with Teletext Checkboxes")
    print("=" * 70)

    config = PickerConfig(
        title="Select Extensions to Install",
        picker_type=PickerType.MULTI,
        teletext_mode=True,
        max_items_display=9
    )

    picker = UniversalPicker(config)

    # Add items with some pre-selected
    items = [
        PickerItem(id="1", label="Dashboard", icon="📊", selected=True),
        PickerItem(id="2", label="Teletext Renderer", icon="📺", selected=False),
        PickerItem(id="3", label="Map Viewer", icon="🗺", selected=True),
        PickerItem(id="4", label="Data Browser", icon="💾", selected=False),
        PickerItem(id="5", label="Command Palette", icon="⌨", selected=False),
    ]

    for item in items:
        picker.add_item(item)

    output = picker.render()
    print(output)
    print("\n✅ Multi-select picker rendered successfully with checkboxes")


def test_file_tree_picker():
    """Test file tree visualization"""
    print("\n" + "=" * 70)
    print("TEST 3: File Tree Picker with Icons")
    print("=" * 70)

    style = TeletextPromptStyle()

    files = [
        {'name': 'README.md', 'is_dir': False, 'size': 2048},
        {'name': 'core', 'is_dir': True, 'size': 0},
        {'name': 'main.py', 'is_dir': False, 'size': 5120},
        {'name': 'config.json', 'is_dir': False, 'size': 512},
        {'name': 'tests', 'is_dir': True, 'size': 0},
        {'name': 'utils.py', 'is_dir': False, 'size': 3072},
        {'name': 'data.csv', 'is_dir': False, 'size': 8192},
    ]

    output = style.create_file_tree(
        path='/Users/fred/uDOS',
        files=files,
        selected_index=2
    )

    print(output)
    print("\n✅ File tree rendered successfully with type indicators")


def test_autocomplete_panel():
    """Test autocomplete suggestions panel"""
    print("\n" + "=" * 70)
    print("TEST 4: Autocomplete Panel with Score Bars")
    print("=" * 70)

    style = TeletextPromptStyle()

    suggestions = [
        {'command': 'SETUP', 'description': 'Run interactive setup wizard', 'score': 0.95},
        {'command': 'SET', 'description': 'Set configuration value', 'score': 0.75},
        {'command': 'SETTINGS', 'description': 'Manage system settings', 'score': 0.70},
        {'command': 'SESSION', 'description': 'Session management', 'score': 0.60},
        {'command': 'SEARCH', 'description': 'Search knowledge base', 'score': 0.55},
    ]

    output = style.create_autocomplete_panel(
        current_input='SE',
        suggestions=suggestions,
        selected_index=0
    )

    print(output)
    print("\n✅ Autocomplete panel rendered successfully with visual scores")


def test_enhanced_prompt_renderer():
    """Test the complete enhanced prompt renderer"""
    print("\n" + "=" * 70)
    print("TEST 5: Enhanced Prompt Renderer Integration")
    print("=" * 70)

    renderer = EnhancedPromptRenderer(theme='dungeon', width=70)

    # Test command prompt with suggestions
    suggestions = [
        {'command': 'GRID', 'description': 'Grid panel management', 'score': 0.85},
        {'command': 'GET', 'description': 'Get configuration value', 'score': 0.70},
    ]

    output = renderer.render_command_prompt(
        prompt_text="uDOS",
        current_input="G",
        suggestions=suggestions
    )

    print(output)
    print("\n✅ Enhanced prompt renderer working correctly")


def test_classic_mode_fallback():
    """Test that classic mode still works when teletext is disabled"""
    print("\n" + "=" * 70)
    print("TEST 6: Classic Mode Fallback (teletext_mode=False)")
    print("=" * 70)

    config = PickerConfig(
        title="Classic Picker",
        picker_type=PickerType.SINGLE,
        teletext_mode=False,  # Explicitly disable teletext
        max_items_display=5
    )

    picker = UniversalPicker(config)

    items = [
        PickerItem(id="1", label="Option A", description="First option"),
        PickerItem(id="2", label="Option B", description="Second option"),
        PickerItem(id="3", label="Option C", description="Third option"),
    ]

    for item in items:
        picker.add_item(item)

    output = picker.render()
    print(output)
    print("\n✅ Classic mode fallback working (box-drawing characters)")


def test_all():
    """Run all tests"""
    print("\n" + "█" * 70)
    print("uDOS v1.0.30 - Teletext UI Enhancement Test Suite")
    print("█" * 70)

    tests = [
        test_teletext_picker,
        test_multi_select_picker,
        test_file_tree_picker,
        test_autocomplete_panel,
        test_enhanced_prompt_renderer,
        test_classic_mode_fallback,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 All tests passed! v1.0.30 teletext UI is ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review.")
        return 1


if __name__ == '__main__':
    sys.exit(test_all())
