#!/usr/bin/env python3
"""
uDOS v1.0.30 - Interactive Demo

Live demonstration of the new teletext UI enhancements.
Run this script to see all the new visual features in action.

Usage: python demo_v1_0_30.py
"""

import sys
import os
import time

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.ui.picker import UniversalPicker, PickerConfig, PickerType, PickerItem
from core.ui.teletext_prompt import TeletextPromptStyle, TeletextBlocks, EnhancedPromptRenderer


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def pause(message="Press ENTER to continue..."):
    """Pause for user input"""
    input(f"\n{message}")


def demo_header(title):
    """Show demo section header"""
    print("\n" + TeletextBlocks.FULL * 70)
    print(f"{TeletextBlocks.POINTER} {title}")
    print(TeletextBlocks.FULL * 70 + "\n")


def demo_intro():
    """Introduction to the demo"""
    clear_screen()

    print(TeletextBlocks.DOUBLE_H * 70)
    print(" " * 15 + "uDOS v1.0.30 - Interactive Demo")
    print(TeletextBlocks.DOUBLE_H * 70)
    print()
    print("This demo showcases the new teletext block UI enhancements.")
    print()
    print("Features demonstrated:")
    print(f"  {TeletextBlocks.SUCCESS} Enhanced pickers with visual selection")
    print(f"  {TeletextBlocks.SUCCESS} File tree visualization")
    print(f"  {TeletextBlocks.SUCCESS} Autocomplete with score bars")
    print(f"  {TeletextBlocks.SUCCESS} Multi-select with checkboxes")
    print(f"  {TeletextBlocks.SUCCESS} Retro teletext aesthetic")
    print()

    pause()


def demo_single_select():
    """Demonstrate single-select picker"""
    clear_screen()
    demo_header("Feature 1: Single-Select Picker")

    print("The classic menu selection, now with teletext styling:")
    print()

    config = PickerConfig(
        title="Main Menu",
        picker_type=PickerType.SINGLE,
        teletext_mode=True
    )

    picker = UniversalPicker(config)

    items = [
        PickerItem(id="1", label="Start New Mission", icon="🚀"),
        PickerItem(id="2", label="Load Saved Session", icon="💾"),
        PickerItem(id="3", label="Configure Settings", icon="⚙"),
        PickerItem(id="4", label="Browse Knowledge", icon="📚"),
        PickerItem(id="5", label="View Statistics", icon="📊"),
        PickerItem(id="6", label="Exit uDOS", icon="🚪"),
    ]

    for item in items:
        picker.add_item(item)

    print(picker.render())

    print("\nNotice:")
    print(f"  {TeletextBlocks.POINTER} Double-line borders (╔═╗)")
    print(f"  {TeletextBlocks.POINTER} Radio button indicators (◉ ○)")
    print(f"  {TeletextBlocks.POINTER} Numbered shortcuts (1-6)")
    print(f"  {TeletextBlocks.POINTER} Visual selection with pointer")

    pause()


def demo_multi_select():
    """Demonstrate multi-select picker"""
    clear_screen()
    demo_header("Feature 2: Multi-Select Picker")

    print("Choose multiple options with visual checkboxes:")
    print()

    config = PickerConfig(
        title="Install Extensions",
        picker_type=PickerType.MULTI,
        teletext_mode=True
    )

    picker = UniversalPicker(config)

    items = [
        PickerItem(id="1", label="Dashboard", icon="📊", description="Stats & overview", selected=True),
        PickerItem(id="2", label="Teletext Renderer", icon="📺", description="Mosaic art system", selected=False),
        PickerItem(id="3", label="Map Viewer", icon="🗺", description="Spatial navigation", selected=True),
        PickerItem(id="4", label="Data Browser", icon="💾", description="File explorer", selected=False),
        PickerItem(id="5", label="Command Palette", icon="⌨", description="Quick commands", selected=True),
    ]

    for item in items:
        picker.add_item(item)

    print(picker.render())

    print("\nNotice:")
    print(f"  {TeletextBlocks.CHECKBOX_ON} Checked items (3 selected)")
    print(f"  {TeletextBlocks.CHECKBOX_OFF} Unchecked items")
    print(f"  {TeletextBlocks.POINTER} Selection counter at bottom")
    print(f"  {TeletextBlocks.POINTER} SPACE to toggle instruction")

    pause()


def demo_file_tree():
    """Demonstrate file tree visualization"""
    clear_screen()
    demo_header("Feature 3: File Tree Visualization")

    print("Navigate files and directories with visual indicators:")
    print()

    style = TeletextPromptStyle()

    files = [
        {'name': 'README.md', 'is_dir': False, 'size': 2048},
        {'name': 'core', 'is_dir': True, 'size': 0},
        {'name': 'main.py', 'is_dir': False, 'size': 5120},
        {'name': 'config.json', 'is_dir': False, 'size': 512},
        {'name': 'extensions', 'is_dir': True, 'size': 0},
        {'name': 'utils.py', 'is_dir': False, 'size': 3072},
        {'name': 'data.csv', 'is_dir': False, 'size': 8192},
        {'name': 'theme.css', 'is_dir': False, 'size': 1536},
    ]

    output = style.create_file_tree(
        path='/Users/fred/uDOS',
        files=files,
        selected_index=2
    )

    print(output)

    print("\nNotice:")
    print(f"  {TeletextBlocks.FILE} File type icons (📄 📁 📝 📊)")
    print(f"  {TeletextBlocks.POINTER} Light fill shows file size visually")
    print(f"  {TeletextBlocks.POINTER} Selected file highlighted with arrow")
    print(f"  {TeletextBlocks.POINTER} Folders vs files clearly distinguished")

    pause()


def demo_autocomplete():
    """Demonstrate autocomplete panel"""
    clear_screen()
    demo_header("Feature 4: Autocomplete with Score Bars")

    print("Type a command and see visual match quality:")
    print()

    style = TeletextPromptStyle()

    # Simulate typing progression
    inputs = ["G", "GR", "GRI"]

    for user_input in inputs:
        print(f"User types: '{user_input}'")
        print()

        # Suggestions change as user types
        if user_input == "G":
            suggestions = [
                {'command': 'GRID', 'description': 'Grid panel management', 'score': 0.85},
                {'command': 'GET', 'description': 'Get configuration value', 'score': 0.70},
                {'command': 'GENERATE', 'description': 'Generate content', 'score': 0.60},
            ]
        elif user_input == "GR":
            suggestions = [
                {'command': 'GRID', 'description': 'Grid panel management', 'score': 0.95},
                {'command': 'GRAPH', 'description': 'Graph visualization', 'score': 0.75},
            ]
        else:  # GRI
            suggestions = [
                {'command': 'GRID', 'description': 'Grid panel management', 'score': 0.98},
            ]

        output = style.create_autocomplete_panel(
            current_input=user_input,
            suggestions=suggestions
        )

        print(output)

        if user_input != inputs[-1]:
            print("\n" + TeletextBlocks.LIGHT * 70 + "\n")

    print("\nNotice:")
    print(f"  {TeletextBlocks.FULL * 5} Score bars show match quality visually")
    print(f"  {TeletextBlocks.POINTER} Suggestions refine as you type")
    print(f"  {TeletextBlocks.POINTER} Keyboard shortcuts shown in footer")
    print(f"  {TeletextBlocks.POINTER} Clear visual hierarchy")

    pause()


def demo_comparison():
    """Show side-by-side comparison of classic vs teletext"""
    clear_screen()
    demo_header("Feature 5: Classic Mode Still Available")

    print("Teletext mode is enabled by default, but classic mode is preserved:")
    print()

    # Classic mode
    print("CLASSIC MODE (teletext_mode=False):")
    print()

    config_classic = PickerConfig(
        title="Theme Selector",
        picker_type=PickerType.SINGLE,
        teletext_mode=False,
        max_items_display=3
    )

    picker_classic = UniversalPicker(config_classic)
    items_classic = [
        PickerItem(id="1", label="Dungeon", description="Dark fantasy theme"),
        PickerItem(id="2", label="Cyberpunk", description="Neon future theme"),
        PickerItem(id="3", label="Synthwave", description="80s retro theme"),
    ]

    for item in items_classic:
        picker_classic.add_item(item)

    print(picker_classic.render())

    print("\n" + TeletextBlocks.DOUBLE_H * 70 + "\n")

    # Teletext mode
    print("TELETEXT MODE (teletext_mode=True, default):")
    print()

    config_teletext = PickerConfig(
        title="Theme Selector",
        picker_type=PickerType.SINGLE,
        teletext_mode=True,
        max_items_display=3
    )

    picker_teletext = UniversalPicker(config_teletext)
    items_teletext = [
        PickerItem(id="1", label="Dungeon", description="Dark fantasy theme", icon="⚔"),
        PickerItem(id="2", label="Cyberpunk", description="Neon future theme", icon="🤖"),
        PickerItem(id="3", label="Synthwave", description="80s retro theme", icon="🌆"),
    ]

    for item in items_teletext:
        picker_teletext.add_item(item)

    print(picker_teletext.render())

    print("\n100% Backward Compatible:")
    print(f"  {TeletextBlocks.SUCCESS} Existing code still works")
    print(f"  {TeletextBlocks.SUCCESS} Classic mode available if preferred")
    print(f"  {TeletextBlocks.SUCCESS} No breaking changes")
    print(f"  {TeletextBlocks.SUCCESS} Choose your style!")

    pause()


def demo_conclusion():
    """Wrap up the demo"""
    clear_screen()

    print(TeletextBlocks.DOUBLE_H * 70)
    print(" " * 20 + "Demo Complete!")
    print(TeletextBlocks.DOUBLE_H * 70)
    print()
    print("You've seen all the new v1.0.30 features:")
    print()
    print(f"  {TeletextBlocks.SUCCESS} Enhanced pickers with teletext styling")
    print(f"  {TeletextBlocks.SUCCESS} Visual file tree navigation")
    print(f"  {TeletextBlocks.SUCCESS} Autocomplete with score feedback")
    print(f"  {TeletextBlocks.SUCCESS} Multi-select with checkboxes")
    print(f"  {TeletextBlocks.SUCCESS} 100% backward compatible")
    print()
    print("These enhancements are now live in all uDOS interactive commands!")
    print()
    print("Try them out:")
    print(f"  {TeletextBlocks.POINTER} Run SETUP wizard for enhanced configuration")
    print(f"  {TeletextBlocks.POINTER} Use FILE commands for teletext file picker")
    print(f"  {TeletextBlocks.POINTER} Type any command to see autocomplete in action")
    print()
    print("Documentation:")
    print(f"  {TeletextBlocks.POINTER} wiki/Release-v1.0.30.md - Full feature docs")
    print(f"  {TeletextBlocks.POINTER} memory/tests/test_v1_0_30_teletext_ui.py - Test suite")
    print()
    print(TeletextBlocks.DOUBLE_H * 70)
    print()


def main():
    """Run the complete demo"""
    try:
        demo_intro()
        demo_single_select()
        demo_multi_select()
        demo_file_tree()
        demo_autocomplete()
        demo_comparison()
        demo_conclusion()

        return 0

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        return 130

    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
