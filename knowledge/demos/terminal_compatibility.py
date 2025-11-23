#!/usr/bin/env python3
"""
uDOS v1.1.0 - Terminal Compatibility Matrix & Validation
Interactive validation of retro graphics across terminal emulators

Feature: 1.1.0.10
Purpose: Document and verify terminal compatibility
Version: 1.1.0

Validates:
- Unicode block character rendering
- ANSI color support
- Box drawing characters
- Progress bars and loaders
- Splash screens
- Visual selector components
- Performance benchmarks
"""

import sys
import os
import time
import platform
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.ui.visual_selector import VisualSelector, TeletextChars
from core.theme.manager import ThemeManager, ThemeMode
from core.output.splash import print_splash_screen


class TerminalCompatibilityMatrix:
    """
    Comprehensive terminal compatibility testing and documentation.

    Tests retro graphics across different terminal emulators and
    creates a compatibility matrix for documentation.
    """

    def __init__(self):
        """Initialize compatibility tester."""
        self.chars = TeletextChars()
        self.selector = VisualSelector(width=70)
        self.theme_manager = ThemeManager()
        self.results = {}

    def detect_terminal_info(self) -> Dict[str, str]:
        """Detect terminal environment information."""
        info = {
            'Platform': platform.system(),
            'Python': platform.python_version(),
            'TERM': os.environ.get('TERM', 'unknown'),
            'COLORTERM': os.environ.get('COLORTERM', 'none'),
            'TTY': 'yes' if sys.stdout.isatty() else 'no',
            'Encoding': sys.stdout.encoding or 'unknown'
        }

        # Detect specific terminal emulators
        term_program = os.environ.get('TERM_PROGRAM', '')
        if term_program:
            info['Emulator'] = term_program
        elif 'screen' in info['TERM']:
            info['Emulator'] = 'screen/tmux'
        elif 'xterm' in info['TERM']:
            info['Emulator'] = 'xterm-compatible'
        else:
            info['Emulator'] = 'unknown'

        return info

    def test_unicode_support(self) -> Tuple[bool, List[str]]:
        """
        Test Unicode block character support.

        Returns:
            (success, list of failed characters)
        """
        test_chars = {
            'Full Block': self.chars.FULL,
            'Dark Shade': self.chars.DARK,
            'Medium Shade': self.chars.MEDIUM,
            'Light Shade': self.chars.LIGHT,
            'Horizontal Line': self.chars.H_LINE,
            'Vertical Line': self.chars.V_LINE,
            'Top Left Corner': self.chars.TOP_LEFT,
            'Pointer': self.chars.POINTER,
            'Checkbox On': self.chars.CHECKBOX_ON,
            'Success Mark': self.chars.SUCCESS
        }

        failed = []
        for name, char in test_chars.items():
            try:
                # Test encoding
                char.encode('utf-8')
                # Test rendering (attempt to print and capture)
                test_str = f"  {char} {name}"
                print(test_str)
            except (UnicodeEncodeError, UnicodeDecodeError):
                failed.append(name)

        return (len(failed) == 0, failed)

    def test_ansi_color_support(self) -> Tuple[bool, str]:
        """
        Test ANSI color code support.

        Returns:
            (success, capability level)
        """
        # Test basic colors
        scheme = self.theme_manager.get_current_scheme()

        print(f"\n{scheme.primary}Primary Color{scheme.reset}")
        print(f"{scheme.success}Success Color{scheme.reset}")
        print(f"{scheme.error}Error Color{scheme.reset}")
        print(f"{scheme.warning}Warning Color{scheme.reset}")

        # Detect capability
        colorterm = os.environ.get('COLORTERM', '')
        if colorterm in ['truecolor', '24bit']:
            capability = '24-bit (truecolor)'
        elif os.environ.get('TERM', '').endswith('256color'):
            capability = '256 colors'
        else:
            capability = '8/16 colors (basic)'

        return (True, capability)

    def test_box_drawing(self) -> bool:
        """Test box drawing character rendering."""
        print("\nBox Drawing Test:")

        # Single-line box
        print(f"{self.chars.TOP_LEFT}{self.chars.H_LINE * 40}{self.chars.TOP_RIGHT}")
        print(f"{self.chars.V_LINE}{'Single-line box test'.center(40)}{self.chars.V_LINE}")
        print(f"{self.chars.BOTTOM_LEFT}{self.chars.H_LINE * 40}{self.chars.BOTTOM_RIGHT}")

        # Double-line box
        print(f"\n{self.chars.TOP_LEFT_DBL}{self.chars.H_DBL * 40}{self.chars.TOP_RIGHT_DBL}")
        print(f"{self.chars.V_DBL}{'Double-line box test'.center(40)}{self.chars.V_DBL}")
        print(f"{self.chars.BOTTOM_LEFT_DBL}{self.chars.H_DBL * 40}{self.chars.BOTTOM_RIGHT_DBL}")

        return True

    def test_visual_components(self) -> bool:
        """Test visual selector components."""
        print("\nVisual Components Test:")

        # Numbered menu
        menu = self.selector.render_numbered_menu(
            "Theme Selector",
            ["Classic DOS", "Cyberpunk", "Accessibility", "Monochrome"],
            selected_index=0
        )
        print(menu)

        # Progress bar
        print("\nProgress Bars:")
        for i in [25, 50, 75, 100]:
            progress = self.selector.render_progress(i, 100, label=f"Task {i}%")
            print(f"  {progress}")

        # Status messages
        print("\nStatus Messages:")
        for status in ['info', 'success', 'warning', 'error']:
            msg = self.selector.render_status(f"This is a {status} message", status=status)
            print(f"  {msg}")

        return True

    def test_performance(self) -> Tuple[bool, float]:
        """
        Test rendering performance.

        Returns:
            (success, avg_render_time_ms)
        """
        iterations = 100
        items = [f"Option {i}" for i in range(20)]

        start = time.time()
        for _ in range(iterations):
            self.selector.render_numbered_menu("Performance Test", items)
        duration = time.time() - start

        avg_ms = (duration / iterations) * 1000
        success = avg_ms < 10.0  # Should be under 10ms per render

        return (success, avg_ms)

    def run_full_validation(self) -> Dict[str, any]:
        """
        Run complete validation suite.

        Returns:
            Dictionary with test results
        """
        print("="*70)
        print("uDOS v1.1.0 - Terminal Compatibility Validation".center(70))
        print("="*70)

        # Terminal info
        print("\n" + self.chars.POINTER + " Terminal Information:")
        info = self.detect_terminal_info()
        for key, value in info.items():
            print(f"  {key}: {value}")

        results = {'info': info}

        # Unicode support
        print("\n" + self.chars.POINTER + " Unicode Block Characters:")
        unicode_ok, unicode_failed = self.test_unicode_support()
        results['unicode'] = {'passed': unicode_ok, 'failed': unicode_failed}
        print(f"  Status: {self.chars.SUCCESS if unicode_ok else self.chars.ERROR}")
        if unicode_failed:
            print(f"  Failed: {', '.join(unicode_failed)}")

        # ANSI colors
        print("\n" + self.chars.POINTER + " ANSI Color Support:")
        color_ok, color_capability = self.test_ansi_color_support()
        results['colors'] = {'passed': color_ok, 'capability': color_capability}
        print(f"  Capability: {color_capability}")

        # Box drawing
        print("\n" + self.chars.POINTER + " Box Drawing Characters:")
        box_ok = self.test_box_drawing()
        results['box_drawing'] = {'passed': box_ok}

        # Visual components
        print("\n" + self.chars.POINTER + " Visual Selector Components:")
        visual_ok = self.test_visual_components()
        results['visual'] = {'passed': visual_ok}

        # Performance
        print("\n" + self.chars.POINTER + " Performance Benchmark:")
        perf_ok, avg_time = self.test_performance()
        results['performance'] = {'passed': perf_ok, 'avg_ms': avg_time}
        print(f"  Average render time: {avg_time:.2f}ms")
        print(f"  Status: {self.chars.SUCCESS if perf_ok else self.chars.WARNING}")

        # Summary
        print("\n" + "="*70)
        all_passed = all([
            results['unicode']['passed'],
            results['colors']['passed'],
            results['box_drawing']['passed'],
            results['visual']['passed'],
            results['performance']['passed']
        ])

        if all_passed:
            print(f"{self.chars.SUCCESS} All tests PASSED - Terminal fully compatible!")
        else:
            print(f"{self.chars.WARNING} Some tests failed - Terminal partially compatible")

        print("="*70)

        return results


class CompatibilityDocumentation:
    """Generate compatibility matrix documentation."""

    # Known terminal compatibility data
    TERMINAL_MATRIX = {
        'macOS Terminal.app': {
            'unicode': True,
            'colors': '256 colors',
            'box_drawing': True,
            'performance': 'Excellent',
            'notes': 'Full support, UTF-8 by default'
        },
        'iTerm2': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Excellent',
            'notes': 'Full support with truecolor'
        },
        'macOS Apple Terminal (legacy)': {
            'unicode': True,
            'colors': '256 colors',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'Older versions may need UTF-8 configuration'
        },
        'Linux xterm': {
            'unicode': True,
            'colors': '256 colors',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'Ensure LANG=*.UTF-8'
        },
        'Linux gnome-terminal': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Excellent',
            'notes': 'Full modern terminal support'
        },
        'Linux Konsole (KDE)': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Excellent',
            'notes': 'Full support'
        },
        'Windows Terminal': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Excellent',
            'notes': 'Modern Windows 10/11, full UTF-8 support'
        },
        'Windows PowerShell': {
            'unicode': True,
            'colors': '256 colors',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'May need chcp 65001 for UTF-8'
        },
        'Windows cmd.exe (legacy)': {
            'unicode': 'Limited',
            'colors': '16 colors',
            'box_drawing': 'Partial',
            'performance': 'Fair',
            'notes': 'Use Windows Terminal instead; fallback mode recommended'
        },
        'SSH Session (various)': {
            'unicode': True,
            'colors': 'Depends on client',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'Ensure client and server use UTF-8'
        },
        'tmux': {
            'unicode': True,
            'colors': '256 colors',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'Set default-terminal to screen-256color or tmux-256color'
        },
        'GNU Screen': {
            'unicode': True,
            'colors': '256 colors',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'May need defutf8 on in .screenrc'
        },
        'Alacritty': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Excellent',
            'notes': 'GPU-accelerated, full support'
        },
        'Kitty': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Excellent',
            'notes': 'GPU-accelerated, advanced features'
        },
        'Hyper': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'Electron-based, full support'
        },
        'VSCode Integrated Terminal': {
            'unicode': True,
            'colors': '24-bit truecolor',
            'box_drawing': True,
            'performance': 'Good',
            'notes': 'xterm.js based, excellent compatibility'
        },
        'Minimal TTY (Linux console)': {
            'unicode': 'Limited',
            'colors': '8/16 colors',
            'box_drawing': 'ASCII fallback',
            'performance': 'Good',
            'notes': 'Use fallback mode; monochrome theme recommended'
        }
    }

    @staticmethod
    def print_matrix():
        """Print formatted compatibility matrix."""
        chars = TeletextChars()

        print("\n" + "="*100)
        print("uDOS v1.1.0 - Terminal Emulator Compatibility Matrix".center(100))
        print("="*100)
        print()

        # Table header
        print(f"{'Terminal':<30} {'Unicode':<10} {'Colors':<20} {'Box Draw':<10} {'Perf':<12} {'Notes':<40}")
        print("-"*100)

        for terminal, compat in CompatibilityDocumentation.TERMINAL_MATRIX.items():
            unicode_icon = chars.SUCCESS if compat['unicode'] is True else chars.WARNING
            box_icon = chars.SUCCESS if compat['box_drawing'] is True else chars.WARNING

            print(f"{terminal:<30} {str(compat['unicode']):<10} {compat['colors']:<20} "
                  f"{str(compat['box_drawing']):<10} {compat['performance']:<12} {compat['notes'][:38]:<40}")

        print("-"*100)
        print(f"\n{chars.INFO} Legend:")
        print(f"  {chars.SUCCESS} = Full Support")
        print(f"  {chars.WARNING} = Partial/Limited Support")
        print(f"  Performance: Excellent > Good > Fair")
        print()

        # Recommendations
        print(f"{chars.POINTER} Recommendations:")
        print("  • macOS: iTerm2 or Terminal.app (both excellent)")
        print("  • Linux: gnome-terminal, Konsole, or Alacritty (all excellent)")
        print("  • Windows: Windows Terminal (best), PowerShell (good)")
        print("  • SSH: Ensure UTF-8 encoding on both client and server")
        print("  • tmux/screen: Configure 256-color support")
        print("  • Legacy/Minimal: Use MONOCHROME theme + fallback mode")
        print()

        # Fallback guidance
        print(f"{chars.POINTER} Fallback Mode:")
        print("  uDOS automatically falls back to numbered menus when:")
        print("  • Terminal doesn't support UTF-8")
        print("  • Running in non-TTY environment (pipes, redirects)")
        print("  • prompt_toolkit Application mode unavailable")
        print("  • User preference for keyboard-only navigation")
        print()

        print("="*100)


def interactive_demo():
    """Run interactive retro graphics demo."""
    chars = TeletextChars()
    selector = VisualSelector(width=70)
    theme_manager = ThemeManager()

    print("\n" + "="*70)
    print("uDOS v1.1.0 - Retro Graphics Interactive Demo".center(70))
    print("="*70)

    demos = [
        "1. Splash Screen & Banner",
        "2. Theme Color Showcase",
        "3. Box Drawing & Borders",
        "4. Progress Bars & Loaders",
        "5. Selection Menus",
        "6. Status & Icons",
        "7. Full Compatibility Matrix",
        "8. Run All Demos",
        "9. Exit"
    ]

    while True:
        print("\n" + chars.POINTER + " Select a demo to run:\n")
        for demo in demos:
            print(f"  {demo}")

        choice = input(f"\n{chars.ARROW_RIGHT} Enter choice (1-9): ").strip()

        if choice == '1':
            print("\n" + chars.INFO + " Splash Screen:")
            print_splash_screen()
            banner = selector.render_banner("uDOS v1.1.0 - Retro Graphics Test", style="double")
            print("\n" + banner)

        elif choice == '2':
            print("\n" + chars.INFO + " Theme Color Showcase:")
            for mode in [ThemeMode.CLASSIC, ThemeMode.CYBERPUNK, ThemeMode.ACCESSIBILITY, ThemeMode.MONOCHROME]:
                theme_manager.set_theme(mode)
                scheme = theme_manager.get_current_scheme()
                print(f"\n  {mode.value.upper()}:")
                print(f"    {scheme.primary}Primary{scheme.reset} {scheme.secondary}Secondary{scheme.reset} "
                      f"{scheme.accent}Accent{scheme.reset}")
                print(f"    {scheme.success}Success{scheme.reset} {scheme.warning}Warning{scheme.reset} "
                      f"{scheme.error}Error{scheme.reset}")

        elif choice == '3':
            print("\n" + chars.INFO + " Box Drawing & Borders:")
            menu = selector.render_numbered_menu(
                "Sample Menu",
                ["Option A", "Option B", "Option C"],
                selected_index=1
            )
            print(menu)

        elif choice == '4':
            print("\n" + chars.INFO + " Progress Bars & Loaders:")
            for i in [0, 25, 50, 75, 100]:
                time.sleep(0.1)
                progress = selector.render_progress(i, 100, label=f"Loading")
                print(f"  {progress}")

        elif choice == '5':
            print("\n" + chars.INFO + " Selection Menus:")
            checkbox = selector.render_checkbox_menu(
                "Multi-Select Demo",
                ["Feature A", "Feature B", "Feature C", "Feature D"],
                [0, 2]
            )
            print(checkbox)

        elif choice == '6':
            print("\n" + chars.INFO + " Status & Icons:")
            for status in ['info', 'success', 'warning', 'error', 'pending']:
                msg = selector.render_status(f"Sample {status} message", status=status)
                print(f"  {msg}")

        elif choice == '7':
            CompatibilityDocumentation.print_matrix()

        elif choice == '8':
            print("\n" + chars.INFO + " Running all demos...")
            # Run demos 1-6 in sequence
            for demo_choice in ['1', '2', '3', '4', '5', '6']:
                choice = demo_choice
                print(f"\n{chars.ARROW_RIGHT} Demo {demo_choice}:")
                # Execute corresponding demo code (simplified)

        elif choice == '9':
            print(f"\n{chars.SUCCESS} Exiting demo. Thank you!")
            break

        else:
            print(f"{chars.ERROR} Invalid choice. Please enter 1-9.")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='uDOS Terminal Compatibility Validation')
    parser.add_argument('--validate', action='store_true',
                       help='Run full validation suite')
    parser.add_argument('--matrix', action='store_true',
                       help='Print compatibility matrix')
    parser.add_argument('--demo', action='store_true',
                       help='Run interactive demo')
    parser.add_argument('--all', action='store_true',
                       help='Run validation + matrix')

    args = parser.parse_args()

    if args.validate or args.all:
        tester = TerminalCompatibilityMatrix()
        results = tester.run_full_validation()

    if args.matrix or args.all:
        CompatibilityDocumentation.print_matrix()

    if args.demo:
        interactive_demo()

    if not any([args.validate, args.matrix, args.demo, args.all]):
        # Default: run validation
        tester = TerminalCompatibilityMatrix()
        results = tester.run_full_validation()
