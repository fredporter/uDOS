#!/usr/bin/env python3
"""
uDOS Color Diagnostic Tool
Checks if rich library is installed and colors are working
"""

import sys

print("uDOS Color Diagnostic Tool")
print("=" * 60)
print()

# Check 1: Rich library installed
print("1. Checking rich library installation...")
try:
    import rich
    print(f"   ✓ rich library installed (version {rich.__version__})")
    rich_available = True
except ImportError:
    print("   ✗ rich library NOT installed")
    print("   → Install with: pip install rich>=13.0.0")
    rich_available = False
print()

# Check 2: Terminal color support
print("2. Checking terminal color support...")
if sys.stdout.isatty():
    print("   ✓ stdout is a TTY (terminal)")
else:
    print("   ✗ stdout is not a TTY (output redirected/piped)")
print()

# Check 3: Try rendering colors
print("3. Testing color rendering...")
if rich_available:
    from rich.console import Console
    console = Console()

    print("   Testing rainbow gradient:")
    colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    for color in colors:
        console.print(f"   ████████ {color}", style=f"bold {color}")

    print()
    print("   If you see colors above, rich is working!")
else:
    print("   ⚠ Cannot test colors (rich not installed)")
print()

# Check 4: Test splash screen
print("4. Testing splash screen...")
if rich_available:
    try:
        from core.output.splash import print_splash_screen
        print_splash_screen()
        print("   ✓ Splash screen rendered")
    except Exception as e:
        print(f"   ✗ Error rendering splash: {e}")
else:
    print("   ⚠ Cannot test splash (rich not installed)")
print()

# Summary
print("=" * 60)
print("SUMMARY:")
if rich_available and sys.stdout.isatty():
    print("✓ Colors should be working!")
    print("  If you don't see colors, check your terminal settings.")
elif not rich_available:
    print("✗ Install rich library: pip install rich>=13.0.0")
    print("  Or activate virtual environment: source .venv/bin/activate")
else:
    print("⚠ Output is redirected (not a terminal)")
    print("  Colors won't show when piped or redirected")
print()
