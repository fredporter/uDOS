#!/usr/bin/env python3
"""
uDOS v1.0.19 - Option Selector Demo
Interactive demonstration of arrow-key navigation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.option_selector import (
    OptionSelector,
    EnhancedFilePicker,
    select_theme,
    select_command,
    select_map_cell
)


def demo_menu():
    """Show main demo menu."""
    print("\n" + "="*70)
    print("🎮 uDOS v1.0.19 - Option Selector Demo")
    print("="*70)
    print("\nAvailable demos:")
    print("  1. Theme Selector")
    print("  2. Command Selector")
    print("  3. Map Cell Selector")
    print("  4. Custom Options (Single Select)")
    print("  5. Custom Options (Multi-Select)")
    print("  6. File Picker")
    print("  0. Exit")
    print("\n" + "="*70)

    choice = input("\nSelect demo (0-6): ").strip()
    return choice


def run_theme_demo():
    """Demo theme selection."""
    print("\n🎨 Theme Selector Demo")
    print("Use ↑/↓ arrows to navigate, Enter to select, Q to cancel\n")
    input("Press Enter to start...")

    result = select_theme(current_theme='midnight')

    if result:
        print(f"\n✅ Selected theme: {result}")
    else:
        print("\n❌ Selection cancelled")


def run_command_demo():
    """Demo command selection."""
    print("\n💻 Command Selector Demo")
    print("Use ↑/↓ arrows to navigate, Enter to select, Q to cancel\n")

    categories = ['FILE', 'MAP', 'THEME', 'SYSTEM', 'GRID', 'ASSIST']

    selector = OptionSelector()
    category = selector.select(
        prompt="First, select a command category",
        options=categories,
        category="Categories"
    )

    if not category:
        print("\n❌ Selection cancelled")
        return

    print(f"\n✅ Selected category: {category}")
    print("Now selecting command from that category...\n")

    result = select_command(category=category)

    if result:
        print(f"\n✅ Selected command: {category} {result}")
    else:
        print("\n❌ Selection cancelled")


def run_map_cell_demo():
    """Demo map cell selection."""
    print("\n🗺️  Map Cell Selector Demo")
    print("Use ↑/↓ arrows to navigate 100 cells (A1-J10)")
    print("Press 1-9 for quick jump, Enter to select, Q to cancel\n")
    input("Press Enter to start...")

    result = select_map_cell(current_cell='E5')

    if result:
        print(f"\n✅ Selected cell: {result}")
    else:
        print("\n❌ Selection cancelled")


def run_custom_single_demo():
    """Demo custom single-select."""
    print("\n📋 Custom Single-Select Demo")
    print("Use ↑/↓ arrows, Enter to select, Q to cancel\n")
    input("Press Enter to start...")

    selector = OptionSelector()

    options = [
        "Enable offline mode",
        "Enable assist mode",
        "Enable debug logging",
        "Enable auto-save",
        "Enable notifications",
        "Enable animations",
        "Enable sound effects",
        "Enable keyboard shortcuts"
    ]

    descriptions = [
        "Work without internet",
        "OK assisted",
        "Detailed error messages",
        "Save work automatically",
        "Desktop notifications",
        "UI animations",
        "Audio feedback",
        "Quick actions"
    ]

    result = selector.select(
        prompt="Select a feature to toggle",
        options=options,
        descriptions=descriptions,
        default="Enable assist mode",
        category="Features"
    )

    if result:
        print(f"\n✅ Selected: {result}")
    else:
        print("\n❌ Selection cancelled")


def run_custom_multi_demo():
    """Demo custom multi-select."""
    print("\n☑️  Custom Multi-Select Demo")
    print("Use ↑/↓ arrows, SPACEBAR to toggle, Enter to confirm, Q to cancel\n")
    input("Press Enter to start...")

    selector = OptionSelector()

    options = [
        "Python",
        "JavaScript",
        "TypeScript",
        "Rust",
        "Go",
        "Java",
        "C++",
        "Ruby",
        "PHP",
        "Swift"
    ]

    descriptions = [
        "General-purpose, beginner-friendly",
        "Web development standard",
        "JavaScript with types",
        "Systems programming",
        "Cloud-native development",
        "Enterprise applications",
        "High-performance computing",
        "Web frameworks",
        "Server-side scripting",
        "iOS development"
    ]

    result = selector.select(
        prompt="Select programming languages you know (toggle with spacebar)",
        options=options,
        descriptions=descriptions,
        allow_multi=True,
        category="Languages"
    )

    if result:
        print(f"\n✅ Selected {len(result)} languages:")
        for lang in result:
            print(f"   • {lang}")
    else:
        print("\n❌ Selection cancelled")


def run_file_picker_demo():
    """Demo enhanced file picker."""
    print("\n📁 Enhanced File Picker Demo")
    print("Use ↑/↓ arrows, Enter to select, Q to cancel\n")
    print("Note: Will show files in examples/ directory")
    input("Press Enter to start...")

    picker = EnhancedFilePicker()

    result = picker.select_file(
        prompt="Select a uDOS script file",
        directory="examples",
        extension=".uscript",
        allow_multi=False
    )

    if result:
        print(f"\n✅ Selected: {result}")
    else:
        print("\n❌ Selection cancelled")


def main():
    """Main demo loop."""
    print("\n🌀 Welcome to uDOS v1.0.19 Option Selector Demo!")
    print("This demo showcases arrow-key navigation for option selection.")

    while True:
        choice = demo_menu()

        try:
            if choice == '0':
                print("\n👋 Thanks for trying the demo!")
                break
            elif choice == '1':
                run_theme_demo()
            elif choice == '2':
                run_command_demo()
            elif choice == '3':
                run_map_cell_demo()
            elif choice == '4':
                run_custom_single_demo()
            elif choice == '5':
                run_custom_multi_demo()
            elif choice == '6':
                run_file_picker_demo()
            else:
                print("\n❌ Invalid choice. Please select 0-6.")

        except KeyboardInterrupt:
            print("\n\n❌ Demo interrupted")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        input("\nPress Enter to continue...")

    return 0


if __name__ == '__main__':
    sys.exit(main())
