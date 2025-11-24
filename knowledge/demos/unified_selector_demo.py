#!/usr/bin/env python3
"""
uDOS v1.1.0 - Unified Selector Demo
Interactive demonstration of the new cross-platform selector system

This demo showcases:
- Single selection with arrow keys
- Multi-selection with toggle
- File picker
- Automatic fallback to numbered menus
- Integration with session analytics

Author: uDOS Development Team
Version: 1.1.0
Phase: TUI Reliability & Input System (Feature 1.1.0.8)
Date: November 24, 2025
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ui.unified_selector import (
    select_single,
    select_multiple,
    select_file,
    select_with_search,
    UnifiedSelector,
    SelectorConfig,
    SelectorMode
)


def demo_menu():
    """Show main demo menu."""
    print("\n" + "=" * 70)
    print("uDOS v1.1.0 - Unified Selector Demo".center(70))
    print("=" * 70)
    print("""
This demo showcases the new unified selector system that replaces
the fragmented implementations with a single, robust solution.

Features:
✓ Arrow key navigation (↑↓ to move, Enter to select)
✓ Numbered quick-jump (press 1-9 for instant selection)
✓ Multi-select with toggle (Spacebar to check/uncheck)
✓ Graceful fallback to numbered menus (works over SSH, etc.)
✓ Cross-platform compatibility (macOS, Linux, Windows)
✓ Session analytics integration
✓ Retro teletext aesthetics

Select a demo to run:
""")

    demos = [
        "Single Select - Theme Chooser",
        "Single Select - Command Palette",
        "Multi Select - Feature Toggles",
        "Multi Select - File Types",
        "File Picker - Browse Scripts",
        "Show Compatibility Info",
        "Exit Demo"
    ]

    choice = select_single(
        title="UNIFIED SELECTOR DEMO",
        items=demos,
        category="Demo Menu"
    )

    return choice


def run_theme_demo():
    """Demo theme selection."""
    print("\n" + "─" * 70)
    print("DEMO: Single Select - Theme Chooser")
    print("─" * 70)
    print("""
Use arrow keys (↑↓) to navigate, Enter to select.
Or press 1-5 for quick selection.
Press Q to cancel.
""")
    input("Press Enter to start...")

    themes = [
        "Cyberpunk Neon",
        "Retro Terminal Green",
        "Amber Monochrome",
        "Classic DOS Blue",
        "Synthwave Purple"
    ]

    descriptions = [
        "Bright neon colors on dark background",
        "Classic phosphor green glow",
        "Warm amber text, easy on eyes",
        "Nostalgic DOS blue and white",
        "80s synthwave aesthetic"
    ]

    result = select_single(
        title="SELECT THEME",
        items=themes,
        descriptions=descriptions,
        default_index=1,
        category="Themes"
    )

    if result:
        print(f"\n✅ Selected theme: {result}")
    else:
        print("\n❌ Selection cancelled")


def run_command_demo():
    """Demo command palette."""
    print("\n" + "─" * 70)
    print("DEMO: Single Select - Command Palette")
    print("─" * 70)
    print("""
Quick command selection with descriptions.
Arrow keys or numbers 1-9 for selection.
""")
    input("Press Enter to start...")

    commands = [
        "MAP VIEW",
        "GOTO",
        "DOCS BROWSE",
        "LEARN TOPIC",
        "MEMORY RECALL",
        "OK ASK",
        "FEEDBACK SUBMIT",
        "SCENARIO START"
    ]

    descriptions = [
        "View current map/location",
        "Navigate to coordinates",
        "Browse documentation",
        "Learn new skill",
        "Search memory banks",
        "Ask OK assistant",
        "Submit user feedback",
        "Start adventure scenario"
    ]

    result = select_single(
        title="COMMAND PALETTE",
        items=commands,
        descriptions=descriptions,
        category="Commands"
    )

    if result:
        print(f"\n✅ Would execute: {result}")
    else:
        print("\n❌ Selection cancelled")


def run_feature_toggles_demo():
    """Demo multi-select for features."""
    print("\n" + "─" * 70)
    print("DEMO: Multi Select - Feature Toggles")
    print("─" * 70)
    print("""
Multi-selection mode demonstration.
- Use ↑↓ arrows to navigate
- Press SPACE to toggle checkboxes
- Press ENTER when done
- Press Q to cancel
""")
    input("Press Enter to start...")

    features = [
        "Offline Mode",
        "AI Assist",
        "Auto-Save",
        "Notifications",
        "Animations",
        "Sound Effects",
        "Keyboard Shortcuts",
        "Advanced Logging"
    ]

    descriptions = [
        "Work without internet",
        "Enable AI assistance",
        "Save automatically",
        "Desktop notifications",
        "UI animations",
        "Audio feedback",
        "Quick key bindings",
        "Detailed debug logs"
    ]

    # Pre-select some features
    default_selected = [0, 2, 6]  # Offline, Auto-Save, Shortcuts

    result = select_multiple(
        title="SELECT FEATURES TO ENABLE",
        items=features,
        descriptions=descriptions,
        default_selected=default_selected,
        category="Features"
    )

    if result:
        print(f"\n✅ Enabled {len(result)} feature(s):")
        for feature in result:
            print(f"   • {feature}")
    else:
        print("\n❌ No changes made")


def run_file_types_demo():
    """Demo multi-select for file types."""
    print("\n" + "─" * 70)
    print("DEMO: Multi Select - File Type Filter")
    print("─" * 70)
    print("""
Select which file types to display in file browser.
Multiple selections allowed.
""")
    input("Press Enter to start...")

    file_types = [
        "Python Scripts (.py)",
        "uDOS Scripts (.uscript)",
        "Markdown Docs (.md)",
        "JSON Data (.json)",
        "Text Files (.txt)",
        "Log Files (.log)",
        "Config Files (.conf, .cfg)",
        "All Files (*)"
    ]

    default_selected = [0, 1, 2]  # Python, uScript, Markdown

    result = select_multiple(
        title="SELECT FILE TYPES TO SHOW",
        items=file_types,
        default_selected=default_selected,
        category="File Filters"
    )

    if result:
        print(f"\n✅ Will show {len(result)} file type(s):")
        for ft in result:
            print(f"   • {ft}")
    else:
        print("\n❌ No file types selected")


def run_file_picker_demo():
    """Demo file picker."""
    print("\n" + "─" * 70)
    print("DEMO: File Picker - Browse Scripts")
    print("─" * 70)
    print("""
File picker demonstration.
Browse and select a .uscript file from examples directory.
""")
    input("Press Enter to start...")

    # Try to find examples directory
    examples_dir = Path(__file__).parent.parent.parent / "examples"
    if not examples_dir.exists():
        examples_dir = Path.cwd()

    result = select_file(
        title="SELECT SCRIPT FILE",
        directory=str(examples_dir),
        extensions=['.uscript', '.py'],
        allow_multi=False
    )

    if result:
        print(f"\n✅ Selected file: {result}")
    else:
        print("\n❌ No file selected")


def show_compatibility_info():
    """Show compatibility information."""
    print("\n" + "=" * 70)
    print("Unified Selector - Compatibility Information".center(70))
    print("=" * 70)

    # Detect current mode
    selector = UnifiedSelector(use_analytics=False)

    print(f"""
Current Environment:
-------------------
Terminal Type: {sys.stdin.name if hasattr(sys.stdin, 'name') else 'Unknown'}
Is TTY: {sys.stdin.isatty()}
Advanced Mode: {selector.advanced_mode}

Supported Terminals:
-------------------
✅ macOS Terminal
✅ iTerm2
✅ Linux xterm
✅ Linux gnome-terminal
✅ Windows Terminal
✅ Windows PowerShell
✅ tmux
✅ screen
✅ SSH sessions
✅ Minimal TTY

Features by Mode:
----------------
Advanced Mode (prompt_toolkit):
  • Arrow key navigation (↑↓)
  • Real-time visual feedback
  • Smooth scrolling
  • Keyboard shortcuts
  • Full interactivity

Fallback Mode (numbered):
  • Numbered selection (1-9)
  • Text input matching
  • Reliable in any terminal
  • Works over SSH
  • Screen reader compatible

Progressive Enhancement:
-----------------------
The selector automatically detects terminal capabilities and
provides the best experience possible. If advanced features
aren't available, it gracefully degrades to numbered menus
while maintaining full functionality.

Session Analytics:
-----------------
All selector interactions are logged to session analytics:
  • Selection mode (advanced vs fallback)
  • Navigation patterns (arrow keys vs numbers)
  • Selection timing
  • Cancel/retry rates
  • Error patterns

This data helps optimize the UX based on real-world usage.
""")

    input("\nPress Enter to continue...")


def main():
    """Main demo loop."""
    print("\n🎮 uDOS v1.1.0 - Unified Selector System Demo")
    print("   Cross-platform TUI selection with automatic fallback")
    print("   Part of Phase 1: TUI Reliability & Input System")

    while True:
        choice = demo_menu()

        if not choice or choice == "Exit Demo":
            print("\n👋 Thanks for trying the unified selector demo!")
            print("   Phase 1 (Feature 1.1.0.8) - TUI Selector Refactor\n")
            break

        if choice == "Single Select - Theme Chooser":
            run_theme_demo()
        elif choice == "Single Select - Command Palette":
            run_command_demo()
        elif choice == "Multi Select - Feature Toggles":
            run_feature_toggles_demo()
        elif choice == "Multi Select - File Types":
            run_file_types_demo()
        elif choice == "File Picker - Browse Scripts":
            run_file_picker_demo()
        elif choice == "Show Compatibility Info":
            show_compatibility_info()

        print()

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Demo interrupted by user")
        sys.exit(1)
