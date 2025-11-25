"""
uDOS v1.0.31 - Standardized Input System Tests
Demonstrates the new unified input interface with visual feedback

Run: python memory/tests/test_standardized_input.py
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.standardized_input import StandardizedInput
from core.ui.visual_selector import VisualSelector, TeletextChars


def test_numbered_menu():
    """Test numbered menu selection."""
    print("\n" + "="*60)
    print("TEST 1: Numbered Menu Selection")
    print("="*60)

    si = StandardizedInput()

    idx, choice = si.select_option(
        "Select Theme",
        ["Dungeon", "Science", "Cyberpunk", "Teletext", "Foundation"],
        descriptions=[
            "Dark fantasy RPG style",
            "Scientific lab interface",
            "Neon future aesthetic",
            "Retro teletext graphics",
            "Minimal clean design"
        ],
        icons=["🏰", "🔬", "🌃", "📺", "📋"]
    )

    print(f"\n✓ Selected: {choice} (index {idx})")
    return True


def test_checkbox_multi_select():
    """Test checkbox multi-select."""
    print("\n" + "="*60)
    print("TEST 2: Checkbox Multi-Select")
    print("="*60)

    si = StandardizedInput()

    selected_indices = si.select_multiple(
        "Select Extensions to Install",
        ["Dashboard", "Teletext Viewer", "Terminal", "Markdown Editor", "Font Designer"],
        default_selected=[0, 1],
        min_select=1,
        descriptions=[
            "Web-based system dashboard",
            "Teletext graphics viewer",
            "Terminal emulator",
            "Markdown file editor",
            "Bitmap font designer"
        ]
    )

    print(f"\n✓ Selected {len(selected_indices)} extensions")
    return True


def test_text_input():
    """Test text input with validation."""
    print("\n" + "="*60)
    print("TEST 3: Text Input with Validation")
    print("="*60)

    si = StandardizedInput()

    username = si.input_text(
        "Enter username",
        default="user",
        validate=lambda x: len(x) >= 3,
        suggestions=["admin", "user", "guest"]
    )

    print(f"\n✓ Username set to: {username}")
    return True


def test_confirmation():
    """Test yes/no confirmation."""
    print("\n" + "="*60)
    print("TEST 4: Confirmation Dialog")
    print("="*60)

    si = StandardizedInput()

    confirmed = si.confirm(
        "Install required dependencies?",
        default=True
    )

    print(f"\n✓ User response: {'Yes' if confirmed else 'No'}")
    return True


def test_progress_bar():
    """Test progress bar rendering."""
    print("\n" + "="*60)
    print("TEST 5: Progress Bar")
    print("="*60)

    si = StandardizedInput()

    # Simulate progress
    import time
    total_items = 10

    for i in range(total_items + 1):
        progress = si.show_progress(i, total_items, "Installing", width=40)
        print(f"\r{progress}", end="", flush=True)
        time.sleep(0.1)

    print("\n\n✓ Progress complete")
    return True


def test_status_messages():
    """Test status message rendering."""
    print("\n" + "="*60)
    print("TEST 6: Status Messages")
    print("="*60)

    si = StandardizedInput()

    si.show_status("System initialized", "success")
    si.show_status("Checking dependencies", "info", "Found 12 modules")
    si.show_status("Missing configuration file", "warning", "Will use defaults")
    si.show_status("Failed to connect to API", "error", "Check network settings")
    si.show_status("Loading data", "pending")

    print("\n✓ All status types displayed")
    return True


def test_visual_components():
    """Test visual selector components."""
    print("\n" + "="*60)
    print("TEST 7: Visual Components")
    print("="*60)

    vs = VisualSelector(width=60)

    # Banner
    print(vs.render_banner("uDOS v1.0.31", "double"))

    # Separator
    print(vs.render_separator("double"))

    # Info box
    info = vs.render_info_box(
        "System Information",
        {
            "Version": "1.0.31",
            "Platform": "macOS",
            "Terminal": "80x24",
            "Theme": "Dungeon"
        }
    )
    print(info)

    # File tree
    tree_items = [
        {"name": "knowledge/", "type": "dir", "path": "/knowledge"},
        {"name": "survival/", "type": "dir", "path": "/knowledge/survival"},
        {"name": "water.md", "type": "file", "path": "/knowledge/survival/water.md"},
        {"name": "shelter.md", "type": "file", "path": "/knowledge/survival/shelter.md"},
    ]
    tree = vs.render_file_tree("knowledge/", tree_items, selected_path="/knowledge/survival/water.md")
    print(tree)

    print("\n✓ Visual components rendered")
    return True


def test_teletext_chars():
    """Test teletext character set."""
    print("\n" + "="*60)
    print("TEST 8: Teletext Character Set")
    print("="*60)

    chars = TeletextChars()

    print("\nBlock characters:")
    print(f"  {chars.FULL} Full  {chars.DARK} Dark  {chars.MEDIUM} Medium  {chars.LIGHT} Light")

    print("\nBox drawing:")
    print(f"  {chars.TOP_LEFT}{chars.H_LINE * 20}{chars.TOP_RIGHT}")
    print(f"  {chars.V_LINE}{' ' * 20}{chars.V_LINE}")
    print(f"  {chars.BOTTOM_LEFT}{chars.H_LINE * 20}{chars.BOTTOM_RIGHT}")

    print("\nSelection indicators:")
    print(f"  {chars.CHECKBOX_ON} Checked  {chars.CHECKBOX_OFF} Unchecked")
    print(f"  {chars.RADIO_ON} Selected  {chars.RADIO_OFF} Unselected")

    print("\nStatus icons:")
    print(f"  {chars.SUCCESS} Success  {chars.ERROR} Error  {chars.WARNING} Warning  {chars.INFO} Info")

    print("\nArrows:")
    print(f"  {chars.ARROW_UP} Up  {chars.ARROW_DOWN} Down  {chars.ARROW_LEFT} Left  {chars.ARROW_RIGHT} Right")
    print(f"  {chars.POINTER} Pointer  {chars.BULLET} Bullet")

    print("\n✓ Character set complete")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("uDOS v1.0.31 - Standardized Input System Tests")
    print("="*60)

    tests = [
        ("Numbered Menu", test_numbered_menu),
        ("Checkbox Multi-Select", test_checkbox_multi_select),
        ("Text Input", test_text_input),
        ("Confirmation", test_confirmation),
        ("Progress Bar", test_progress_bar),
        ("Status Messages", test_status_messages),
        ("Visual Components", test_visual_components),
        ("Teletext Characters", test_teletext_chars),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} failed")
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")


if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests cancelled\n")
        sys.exit(0)
