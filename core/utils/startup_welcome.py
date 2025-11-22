"""
uDOS v1.0.30 - Startup Welcome & Demo Helper

Shows welcome message and offers optional demo of new features.
Called after system health check during startup.

Version: 1.0.30
"""

import os
import sys


def show_v1_0_30_welcome(viewport_width: int = 70):
    """
    Display v1.0.30 welcome message with new features.

    Args:
        viewport_width: Terminal width for formatting
    """
    width = min(viewport_width, 70)

    print()
    print("═" * width)
    print("  ✨ Welcome to uDOS v1.0.30!")
    print("═" * width)
    print()
    print("  New in this version:")
    print("  📺 Teletext-style block character UI")
    print("  ✏️  Built-in micro editor (FILE EDIT/VIEW)")
    print("  📁 Knowledge file picker (.md & .uscript)")
    print("  🔧 Robust CLI with fallback mode")
    print("  📋 Better copy-paste support")
    print()
    print("═" * width)
    print()


def offer_demo(skip_prompt: bool = False) -> bool:
    """
    Offer to show the v1.0.30 demo.

    Args:
        skip_prompt: If True, don't ask (for scripted startup)

    Returns:
        True if user wants to see demo
    """
    if skip_prompt:
        return False

    # Check if we're in an interactive terminal
    if not sys.stdin.isatty():
        return False

    print("  💡 See new features in action?")
    print()

    try:
        response = input("  Run v1.0.30 demo? (y/n): ").strip().lower()
        return response in ['y', 'yes']
    except (KeyboardInterrupt, EOFError):
        print()
        return False


def run_demo():
    """
    Run the v1.0.30 interactive demo.
    """
    try:
        # Import and run the demo
        import subprocess
        demo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'dev', 'demo_v1_0_30.py')

        if os.path.exists(demo_path):
            # Run demo with Python
            result = subprocess.run(
                [sys.executable, demo_path],
                cwd=os.path.dirname(demo_path)
            )
            return result.returncode == 0
        else:
            print(f"  ⚠️  Demo not found at: {demo_path}")
            print(f"  💡 Run manually: python dev/demo_v1_0_30.py")
            return False

    except Exception as e:
        print(f"  ❌ Error running demo: {e}")
        return False


def startup_sequence(viewport_width: int = 70, auto_skip_demo: bool = False):
    """
    Complete v1.0.30 startup sequence.

    Args:
        viewport_width: Terminal width
        auto_skip_demo: If True, skip demo prompt
    """
    # Show welcome message
    show_v1_0_30_welcome(viewport_width)

    # Offer demo (unless auto-skipping)
    if not auto_skip_demo:
        if offer_demo():
            print()
            print("  🎬 Starting demo...")
            print()
            input("  Press ENTER to begin...")
            print()

            if run_demo():
                print()
                print("  ✅ Demo complete!")
            else:
                print()
                print("  Demo ended.")

            print()
            input("  Press ENTER to continue to uDOS prompt...")
            print()


# Quick test
if __name__ == '__main__':
    startup_sequence(auto_skip_demo=False)
