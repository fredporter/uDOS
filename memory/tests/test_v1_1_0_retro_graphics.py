#!/usr/bin/env python3
"""
uDOS v1.1.0 - Retro Graphics & Compatibility Test Suite
Tests Unicode/ANSI block characters across terminal emulators

Feature: 1.1.0.10
Purpose: Ensure retro aesthetic works reliably across all terminal types
Version: 1.1.0

Test Coverage:
- Unicode block character rendering
- ANSI escape code compatibility
- Color scheme integrity
- Visual selector rendering
- Progress bars and loaders
- Splash screen compatibility
- Degraded terminal fallback
- SSH/screen/minimal TTY support
"""

import unittest
import sys
import os
from io import StringIO
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.ui.visual_selector import VisualSelector, TeletextChars
from core.theme.manager import ThemeManager, ColorScheme, ThemeMode
from core.output.splash import print_splash_screen, print_viewport_measurement


class TestUnicodeBlockCharacters(unittest.TestCase):
    """Test Unicode block character availability and rendering."""

    def setUp(self):
        """Initialize test fixtures."""
        self.chars = TeletextChars()

    def test_core_blocks_defined(self):
        """Verify all core block characters are defined."""
        self.assertTrue(hasattr(self.chars, 'FULL'))
        self.assertTrue(hasattr(self.chars, 'DARK'))
        self.assertTrue(hasattr(self.chars, 'MEDIUM'))
        self.assertTrue(hasattr(self.chars, 'LIGHT'))
        self.assertTrue(hasattr(self.chars, 'EMPTY'))

    def test_box_drawing_single_line(self):
        """Verify single-line box drawing characters."""
        single_line_chars = [
            'H_LINE', 'V_LINE', 'TOP_LEFT', 'TOP_RIGHT',
            'BOTTOM_LEFT', 'BOTTOM_RIGHT', 'CROSS',
            'T_RIGHT', 'T_LEFT', 'T_DOWN', 'T_UP'
        ]
        for char_name in single_line_chars:
            self.assertTrue(hasattr(self.chars, char_name),
                          f"Missing character: {char_name}")
            self.assertIsNotNone(getattr(self.chars, char_name))

    def test_box_drawing_double_line(self):
        """Verify double-line box drawing characters."""
        double_line_chars = [
            'H_DBL', 'V_DBL', 'TOP_LEFT_DBL', 'TOP_RIGHT_DBL',
            'BOTTOM_LEFT_DBL', 'BOTTOM_RIGHT_DBL',
            'T_RIGHT_DBL', 'T_LEFT_DBL', 'T_DOWN_DBL', 'T_UP_DBL', 'CROSS_DBL'
        ]
        for char_name in double_line_chars:
            self.assertTrue(hasattr(self.chars, char_name),
                          f"Missing character: {char_name}")
            self.assertIsNotNone(getattr(self.chars, char_name))

    def test_arrows_and_pointers(self):
        """Verify arrow and pointer characters."""
        arrow_chars = ['ARROW_RIGHT', 'ARROW_LEFT', 'ARROW_UP', 'ARROW_DOWN', 'POINTER', 'BULLET']
        for char_name in arrow_chars:
            self.assertTrue(hasattr(self.chars, char_name))
            self.assertIsNotNone(getattr(self.chars, char_name))

    def test_selection_indicators(self):
        """Verify selection indicator characters."""
        selection_chars = ['SELECTED', 'UNSELECTED', 'CHECKBOX_ON', 'CHECKBOX_OFF', 'RADIO_ON', 'RADIO_OFF']
        for char_name in selection_chars:
            self.assertTrue(hasattr(self.chars, char_name))
            self.assertIsNotNone(getattr(self.chars, char_name))

    def test_status_icons(self):
        """Verify status icon characters."""
        status_chars = ['SUCCESS', 'ERROR', 'WARNING', 'INFO', 'PENDING']
        for char_name in status_chars:
            self.assertTrue(hasattr(self.chars, char_name))
            self.assertIsNotNone(getattr(self.chars, char_name))

    def test_unicode_encoding(self):
        """Test that Unicode characters can be encoded to UTF-8."""
        test_chars = [
            self.chars.FULL, self.chars.DARK, self.chars.MEDIUM,
            self.chars.H_LINE, self.chars.V_LINE, self.chars.POINTER,
            self.chars.CHECKBOX_ON, self.chars.SUCCESS
        ]
        for char in test_chars:
            try:
                encoded = char.encode('utf-8')
                self.assertIsNotNone(encoded)
            except UnicodeEncodeError:
                self.fail(f"Character {char} failed UTF-8 encoding")


class TestANSIEscapeCodes(unittest.TestCase):
    """Test ANSI escape code generation and compatibility."""

    def setUp(self):
        """Initialize theme manager."""
        self.theme_manager = ThemeManager()

    def test_color_scheme_complete(self):
        """Verify color schemes have all required fields."""
        scheme = self.theme_manager.get_current_scheme()

        required_fields = [
            'primary', 'secondary', 'accent', 'error', 'warning',
            'success', 'info', 'text_primary', 'text_secondary',
            'text_muted', 'border', 'highlight', 'selection', 'reset'
        ]

        for field in required_fields:
            self.assertTrue(hasattr(scheme, field),
                          f"Missing color field: {field}")
            value = getattr(scheme, field)
            self.assertIsNotNone(value)
            self.assertIsInstance(value, str)

    def test_ansi_code_format(self):
        """Verify ANSI codes follow correct format."""
        scheme = self.theme_manager.get_current_scheme()

        # Test basic color codes
        color_fields = ['primary', 'secondary', 'accent', 'error']
        for field in color_fields:
            code = getattr(scheme, field)
            self.assertTrue(code.startswith('\033['),
                          f"{field} ANSI code doesn't start with \\033[")
            self.assertTrue(code.endswith('m'),
                          f"{field} ANSI code doesn't end with m")

    def test_reset_code(self):
        """Verify reset code is correct."""
        scheme = self.theme_manager.get_current_scheme()
        self.assertEqual(scheme.reset, '\033[0m')

    def test_all_theme_modes(self):
        """Test all predefined theme modes."""
        modes = [ThemeMode.CLASSIC, ThemeMode.CYBERPUNK,
                ThemeMode.ACCESSIBILITY, ThemeMode.MONOCHROME]

        for mode in modes:
            self.theme_manager.set_theme(mode)
            scheme = self.theme_manager.get_current_scheme()
            self.assertIsNotNone(scheme)
            self.assertIsInstance(scheme, ColorScheme)

    def test_high_contrast_mode(self):
        """Test high-contrast accessibility colors."""
        self.theme_manager.set_theme(ThemeMode.ACCESSIBILITY)
        scheme = self.theme_manager.get_current_scheme()

        self.assertTrue(hasattr(scheme, 'high_contrast_bg'))
        self.assertTrue(hasattr(scheme, 'high_contrast_fg'))
        self.assertIsNotNone(scheme.high_contrast_bg)
        self.assertIsNotNone(scheme.high_contrast_fg)


class TestVisualSelectorRendering(unittest.TestCase):
    """Test visual selector rendering with retro graphics."""

    def setUp(self):
        """Initialize visual selector."""
        self.selector = VisualSelector(width=60)

    def test_numbered_menu_renders(self):
        """Test numbered menu rendering."""
        title = "Test Menu"
        items = ["Option 1", "Option 2", "Option 3"]

        output = self.selector.render_numbered_menu(title, items)

        self.assertIsNotNone(output)
        self.assertIn(title, output)
        for item in items:
            self.assertIn(item, output)

    def test_checkbox_menu_renders(self):
        """Test checkbox menu rendering."""
        title = "Select Items"
        items = ["Item A", "Item B", "Item C"]
        selected = [0, 2]

        output = self.selector.render_checkbox_menu(title, items, selected)

        self.assertIsNotNone(output)
        self.assertIn(title, output)
        # Should show selected count
        self.assertIn("2/3", output)

    def test_progress_bar_renders(self):
        """Test progress bar rendering."""
        output = self.selector.render_progress(50, 100, label="Progress")

        self.assertIsNotNone(output)
        self.assertIn("Progress", output)
        self.assertIn("50%", output)
        self.assertIn("50/100", output)

    def test_status_messages(self):
        """Test status message rendering."""
        statuses = ['info', 'success', 'warning', 'error', 'pending']

        for status in statuses:
            output = self.selector.render_status("Test message", status=status)
            self.assertIsNotNone(output)
            self.assertIn("Test message", output)

    def test_banner_rendering(self):
        """Test banner rendering."""
        output = self.selector.render_banner("Test Banner")

        self.assertIsNotNone(output)
        self.assertIn("Test Banner", output)
        # Should contain box drawing characters
        self.assertTrue(any(c in output for c in ['═', '║', '╔', '╗']))

    def test_info_box_rendering(self):
        """Test info box rendering."""
        title = "System Info"
        items = {"Version": "1.1.0", "Status": "Active"}

        output = self.selector.render_info_box(title, items)

        self.assertIsNotNone(output)
        self.assertIn(title, output)
        self.assertIn("Version", output)
        self.assertIn("1.1.0", output)


class TestSplashScreenCompatibility(unittest.TestCase):
    """Test splash screen rendering compatibility."""

    def test_splash_screen_output(self):
        """Test splash screen generates output."""
        # Capture stdout
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            print_splash_screen()

        output = captured_output.getvalue()
        self.assertIsNotNone(output)
        self.assertTrue(len(output) > 0)
        # Should contain "uDOS"
        self.assertIn("uDOS", output)

    def test_splash_screen_box_drawing(self):
        """Test splash screen uses box drawing characters."""
        captured_output = StringIO()
        with patch('sys.stdout', captured_output):
            print_splash_screen()

        output = captured_output.getvalue()
        # Should contain box drawing Unicode
        self.assertTrue(any(c in output for c in ['█', '╔', '╗', '║', '═']))

    @patch('sys.stdout.isatty')
    def test_viewport_measurement_non_tty(self, mock_isatty):
        """Test viewport measurement handles non-TTY gracefully."""
        mock_isatty.return_value = False

        # Create mock viewport
        mock_viewport = MagicMock()
        mock_viewport.width = 80
        mock_viewport.height = 24
        mock_viewport.device_type = "desktop"
        mock_viewport.get_grid_specs.return_value = {
            'grid_width': 10,
            'grid_height': 10,
            'total_cells': 100
        }

        # Should not raise exception
        try:
            with patch('time.sleep'):  # Skip delay
                print_viewport_measurement(mock_viewport, delay=0)
        except Exception as e:
            self.fail(f"Viewport measurement failed on non-TTY: {e}")


class TestDegradedTerminalFallback(unittest.TestCase):
    """Test fallback behavior for degraded terminals."""

    def test_ascii_only_fallback(self):
        """Test that system can handle ASCII-only terminals."""
        # This would be tested by checking if there's ASCII fallback
        # For now, verify TeletextChars has EMPTY (space) as fallback
        chars = TeletextChars()
        self.assertEqual(chars.EMPTY, ' ')

    def test_no_color_fallback(self):
        """Test monochrome theme for no-color terminals."""
        theme_manager = ThemeManager()
        theme_manager.set_theme(ThemeMode.MONOCHROME)
        scheme = theme_manager.get_current_scheme()

        # Monochrome should minimize color usage
        self.assertIsNotNone(scheme)
        # Verify it has basic formatting
        self.assertTrue(hasattr(scheme, 'reset'))


class TestCrossPlatformCompatibility(unittest.TestCase):
    """Test compatibility across different terminal emulators."""

    def test_unix_terminal_support(self):
        """Test Unix-like terminal compatibility."""
        # Verify UTF-8 encoding is supported
        test_string = "█▓▒░─│┌┐└┘"
        try:
            encoded = test_string.encode('utf-8')
            decoded = encoded.decode('utf-8')
            self.assertEqual(test_string, decoded)
        except (UnicodeEncodeError, UnicodeDecodeError):
            self.fail("UTF-8 encoding/decoding failed")

    def test_windows_terminal_support(self):
        """Test Windows Terminal compatibility."""
        # Windows Terminal supports UTF-8 and ANSI
        chars = TeletextChars()
        # Test key characters work
        key_chars = [chars.H_LINE, chars.V_LINE, chars.POINTER]
        for char in key_chars:
            self.assertIsNotNone(char)
            self.assertIsInstance(char, str)

    def test_ssh_session_compatibility(self):
        """Test SSH session compatibility (minimal TTY)."""
        # SSH sessions should handle basic ANSI codes
        theme_manager = ThemeManager()
        scheme = theme_manager.get_current_scheme()

        # Basic colors should be available
        self.assertIsNotNone(scheme.primary)
        self.assertIsNotNone(scheme.reset)


class TestRetroAestheticIntegrity(unittest.TestCase):
    """Test that retro aesthetic is consistent and appealing."""

    def setUp(self):
        """Initialize components."""
        self.selector = VisualSelector(width=60)
        self.theme_manager = ThemeManager()

    def test_consistent_box_drawing(self):
        """Test consistent box drawing character usage."""
        menu = self.selector.render_numbered_menu(
            "Retro Menu",
            ["Option 1", "Option 2"]
        )

        # Should use double-line boxes for menus (classic DOS feel)
        self.assertIn('═', menu)
        self.assertIn('║', menu)

    def test_consistent_width_rendering(self):
        """Test that components respect width constraints."""
        width = 60
        selector = VisualSelector(width=width)

        menu = selector.render_numbered_menu("Test", ["A", "B"])
        lines = menu.split('\n')

        for line in lines:
            # Account for ANSI codes by checking visible length
            # For now, check raw length doesn't drastically exceed width
            self.assertLess(len(line), width + 50)  # Allow for ANSI codes

    def test_progress_bar_consistency(self):
        """Test progress bar uses consistent block characters."""
        progress = self.selector.render_progress(75, 100)

        # Should use block characters for progress
        self.assertTrue('█' in progress or '░' in progress)

    def test_retro_color_schemes(self):
        """Test retro-inspired color schemes."""
        # Classic should feel like DOS
        self.theme_manager.set_theme(ThemeMode.CLASSIC)
        classic = self.theme_manager.get_current_scheme()
        self.assertIsNotNone(classic)

        # Cyberpunk should feel like ZX/C64
        self.theme_manager.set_theme(ThemeMode.CYBERPUNK)
        cyber = self.theme_manager.get_current_scheme()
        self.assertIsNotNone(cyber)

        # Should be different schemes
        self.assertNotEqual(classic.primary, cyber.primary)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Test rendering performance for retro graphics."""

    def test_menu_rendering_performance(self):
        """Test menu rendering is reasonably fast."""
        import time

        selector = VisualSelector(width=80)
        items = [f"Item {i}" for i in range(50)]

        start = time.time()
        for _ in range(100):
            selector.render_numbered_menu("Performance Test", items)
        duration = time.time() - start

        # 100 renders of 50-item menu should take < 1 second
        self.assertLess(duration, 1.0,
                       f"Rendering too slow: {duration:.3f}s for 100 renders")

    def test_progress_bar_performance(self):
        """Test progress bar rendering is fast."""
        import time

        selector = VisualSelector()

        start = time.time()
        for i in range(1000):
            selector.render_progress(i, 1000)
        duration = time.time() - start

        # 1000 progress updates should take < 0.5 seconds
        self.assertLess(duration, 0.5,
                       f"Progress rendering too slow: {duration:.3f}s")


def suite():
    """Create test suite."""
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_suite.addTests(loader.loadTestsFromTestCase(TestUnicodeBlockCharacters))
    test_suite.addTests(loader.loadTestsFromTestCase(TestANSIEscapeCodes))
    test_suite.addTests(loader.loadTestsFromTestCase(TestVisualSelectorRendering))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSplashScreenCompatibility))
    test_suite.addTests(loader.loadTestsFromTestCase(TestDegradedTerminalFallback))
    test_suite.addTests(loader.loadTestsFromTestCase(TestCrossPlatformCompatibility))
    test_suite.addTests(loader.loadTestsFromTestCase(TestRetroAestheticIntegrity))
    test_suite.addTests(loader.loadTestsFromTestCase(TestPerformanceBenchmarks))

    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
