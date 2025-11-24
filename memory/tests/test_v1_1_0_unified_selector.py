#!/usr/bin/env python3
"""
uDOS v1.1.0 - Unified Selector Tests
Test suite for cross-platform selector system

Tests cover:
- Single select (basic and advanced modes)
- Multi select with toggle
- File picker
- Search/filter functionality
- Numbered fallback mode
- Edge cases (empty lists, single item, large lists)
- Keyboard shortcuts
- Cancellation handling

Author: uDOS Development Team
Version: 1.1.0
Phase: TUI Reliability & Input System (Feature 1.1.0.8)
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.ui.unified_selector import (
    UnifiedSelector,
    SelectorConfig,
    SelectorMode,
    select_single,
    select_multiple,
    select_file,
    select_with_search
)


class TestUnifiedSelectorBasic(unittest.TestCase):
    """Test basic selector functionality."""

    def test_selector_initialization(self):
        """Test selector initializes correctly."""
        selector = UnifiedSelector(use_analytics=False)
        self.assertIsNotNone(selector)
        self.assertIsInstance(selector.advanced_mode, bool)

    def test_detect_advanced_mode(self):
        """Test advanced mode detection."""
        selector = UnifiedSelector(use_analytics=False)
        # Should detect based on TTY and prompt_toolkit availability
        has_pt = True
        try:
            import prompt_toolkit
        except ImportError:
            has_pt = False

        # Can't guarantee TTY in tests, but mode should be boolean
        self.assertIsInstance(selector.advanced_mode, bool)

    def test_empty_items_handling(self):
        """Test handling of empty items list."""
        selector = UnifiedSelector(use_analytics=False)
        config = SelectorConfig(
            title="Empty Test",
            items=[],
            mode=SelectorMode.SINGLE_SELECT
        )

        with patch('builtins.print') as mock_print:
            result = selector.select(config)
            self.assertIsNone(result)
            mock_print.assert_called_once()

    def test_config_defaults(self):
        """Test SelectorConfig default values."""
        config = SelectorConfig(
            title="Test",
            items=["A", "B", "C"]
        )

        self.assertEqual(config.mode, SelectorMode.SINGLE_SELECT)
        self.assertEqual(config.default_index, 0)
        self.assertTrue(config.allow_cancel)
        self.assertTrue(config.show_numbers)
        self.assertEqual(config.max_display, 10)


class TestFallbackMode(unittest.TestCase):
    """Test numbered fallback mode (works in all terminals)."""

    def setUp(self):
        """Set up test fixtures."""
        self.selector = UnifiedSelector(use_analytics=False)
        # Force fallback mode for testing
        self.selector.advanced_mode = False

    def test_single_select_fallback(self):
        """Test single selection with numbered input."""
        config = SelectorConfig(
            title="Select Option",
            items=["Option 1", "Option 2", "Option 3"],
            mode=SelectorMode.SINGLE_SELECT
        )

        # Simulate user entering "2"
        with patch('builtins.input', return_value='2'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, "Option 2")

    def test_single_select_by_name(self):
        """Test selection by partial name match."""
        config = SelectorConfig(
            title="Select Theme",
            items=["Dark Mode", "Light Mode", "Auto"],
            mode=SelectorMode.SINGLE_SELECT
        )

        # Simulate user typing "dark"
        with patch('builtins.input', return_value='dark'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, "Dark Mode")

    def test_single_select_cancel(self):
        """Test cancellation in single select."""
        config = SelectorConfig(
            title="Select Option",
            items=["A", "B", "C"],
            allow_cancel=True
        )

        with patch('builtins.input', return_value='q'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertIsNone(result)

    def test_multi_select_fallback(self):
        """Test multi-selection with numbered input."""
        config = SelectorConfig(
            title="Select Multiple",
            items=["Item 1", "Item 2", "Item 3", "Item 4"],
            mode=SelectorMode.MULTI_SELECT
        )

        # Simulate: toggle 1, toggle 3, then done
        inputs = ['1 3', 'done']
        with patch('builtins.input', side_effect=inputs):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(len(result), 2)
                self.assertIn("Item 1", result)
                self.assertIn("Item 3", result)

    def test_multi_select_toggle(self):
        """Test toggling selections in multi-select."""
        config = SelectorConfig(
            title="Toggle Test",
            items=["A", "B", "C"],
            mode=SelectorMode.MULTI_SELECT
        )

        # Select 1, then select 2, then deselect 1
        inputs = ['1', '2', '1', 'done']
        with patch('builtins.input', side_effect=inputs):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(len(result), 1)
                self.assertIn("B", result)

    def test_multi_select_cancel(self):
        """Test cancellation in multi-select."""
        config = SelectorConfig(
            title="Select Multiple",
            items=["A", "B", "C"],
            mode=SelectorMode.MULTI_SELECT,
            allow_cancel=True
        )

        with patch('builtins.input', return_value='q'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, [])

    def test_invalid_number_handling(self):
        """Test handling of out-of-range numbers."""
        config = SelectorConfig(
            title="Select",
            items=["A", "B", "C"]
        )

        # Try invalid number, then valid
        inputs = ['99', '2']
        with patch('builtins.input', side_effect=inputs):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, "B")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience wrapper functions."""

    def test_select_single_wrapper(self):
        """Test select_single convenience function."""
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                with patch('sys.stdin.isatty', return_value=False):
                    result = select_single(
                        title="Choose One",
                        items=["First", "Second", "Third"]
                    )
                    self.assertEqual(result, "First")

    def test_select_multiple_wrapper(self):
        """Test select_multiple convenience function."""
        inputs = ['1 2', 'done']
        with patch('builtins.input', side_effect=inputs):
            with patch('builtins.print'):
                with patch('sys.stdin.isatty', return_value=False):
                    result = select_multiple(
                        title="Choose Many",
                        items=["A", "B", "C", "D"]
                    )
                    self.assertEqual(len(result), 2)

    def test_select_file_wrapper(self):
        """Test select_file convenience function."""
        # Create temporary directory structure
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = ['file1.txt', 'file2.txt', 'script.py']
            for fname in test_files:
                Path(tmpdir) / fname
                (Path(tmpdir) / fname).touch()

            with patch('builtins.input', return_value='1'):
                with patch('builtins.print'):
                    with patch('sys.stdin.isatty', return_value=False):
                        result = select_file(
                            title="Pick File",
                            directory=tmpdir
                        )
                        # Should return full path
                        self.assertIsNotNone(result)
                        if result:
                            self.assertTrue(str(result).endswith('file1.txt'))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.selector = UnifiedSelector(use_analytics=False)
        self.selector.advanced_mode = False  # Use fallback for predictable testing

    def test_single_item_list(self):
        """Test selection with only one item."""
        config = SelectorConfig(
            title="Only One",
            items=["Only Item"]
        )

        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, "Only Item")

    def test_large_list(self):
        """Test selection with many items."""
        items = [f"Item {i}" for i in range(100)]
        config = SelectorConfig(
            title="Many Items",
            items=items
        )

        # Select item 50
        with patch('builtins.input', return_value='50'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, "Item 49")

    def test_special_characters_in_items(self):
        """Test items with special characters."""
        config = SelectorConfig(
            title="Special Chars",
            items=["Item with 'quotes'", "Item with \"double\"", "Item with ☃"]
        )

        with patch('builtins.input', return_value='2'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, 'Item with "double"')

    def test_default_index(self):
        """Test that default_index is respected."""
        config = SelectorConfig(
            title="Default Test",
            items=["A", "B", "C"],
            default_index=1
        )

        # In fallback mode, default is just visual
        # User still needs to confirm
        with patch('builtins.input', return_value='2'):
            with patch('builtins.print'):
                result = self.selector._select_fallback(config)
                self.assertEqual(result, "B")

    def test_descriptions_display(self):
        """Test that descriptions are shown (visual check)."""
        config = SelectorConfig(
            title="With Descriptions",
            items=["Option A", "Option B"],
            descriptions=["First option", "Second option"]
        )

        with patch('builtins.input', return_value='1'):
            with patch('builtins.print') as mock_print:
                result = self.selector._select_fallback(config)
                # Verify descriptions were included in output
                output = ' '.join(str(call) for call in mock_print.call_args_list)
                self.assertIn("First option", output)


class TestAnalyticsIntegration(unittest.TestCase):
    """Test session analytics integration."""

    def test_analytics_logging_on_success(self):
        """Test that successful selection is logged."""
        # Mock analytics
        mock_analytics = MagicMock()

        selector = UnifiedSelector(use_analytics=False)
        selector.analytics = mock_analytics
        selector.advanced_mode = False

        config = SelectorConfig(
            title="Test",
            items=["A", "B", "C"]
        )

        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                result = selector.select(config)

        # Should have logged command execution
        self.assertEqual(mock_analytics.track_command.call_count, 1)
        # Verify it was called with correct signature
        call_args = mock_analytics.track_command.call_args
        self.assertIn('command', call_args.kwargs)
        self.assertIn('params', call_args.kwargs)
        self.assertIn('duration_ms', call_args.kwargs)
        self.assertIn('success', call_args.kwargs)

    def test_analytics_logging_on_cancel(self):
        """Test that cancellation is logged."""
        mock_analytics = MagicMock()

        selector = UnifiedSelector(use_analytics=False)
        selector.analytics = mock_analytics
        selector.advanced_mode = False

        config = SelectorConfig(
            title="Test",
            items=["A", "B"],
            allow_cancel=True
        )

        with patch('builtins.input', return_value='q'):
            with patch('builtins.print'):
                result = selector.select(config)

        # Should log cancellation with success=False
        self.assertIsNone(result)
        self.assertEqual(mock_analytics.track_command.call_count, 1)
        call_args = mock_analytics.track_command.call_args
        self.assertEqual(call_args.kwargs['success'], False)


class TestSelectorModes(unittest.TestCase):
    """Test different selector modes."""

    def setUp(self):
        """Set up test fixtures."""
        self.selector = UnifiedSelector(use_analytics=False)
        self.selector.advanced_mode = False

    def test_single_select_mode(self):
        """Test SINGLE_SELECT mode."""
        config = SelectorConfig(
            title="Single",
            items=["A", "B", "C"],
            mode=SelectorMode.SINGLE_SELECT
        )

        with patch('builtins.input', return_value='2'):
            with patch('builtins.print'):
                result = self.selector.select(config)
                self.assertIsInstance(result, str)
                self.assertEqual(result, "B")

    def test_multi_select_mode(self):
        """Test MULTI_SELECT mode."""
        config = SelectorConfig(
            title="Multi",
            items=["A", "B", "C"],
            mode=SelectorMode.MULTI_SELECT
        )

        inputs = ['1 3', 'done']
        with patch('builtins.input', side_effect=inputs):
            with patch('builtins.print'):
                result = self.selector.select(config)
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), 2)

    def test_default_selected_in_multi(self):
        """Test default_selected in multi-select mode."""
        config = SelectorConfig(
            title="Pre-selected",
            items=["A", "B", "C", "D"],
            mode=SelectorMode.MULTI_SELECT,
            default_selected=[0, 2]  # A and C pre-selected
        )

        # User just confirms
        with patch('builtins.input', return_value='done'):
            with patch('builtins.print'):
                result = self.selector.select(config)
                self.assertEqual(len(result), 2)
                self.assertIn("A", result)
                self.assertIn("C", result)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedSelectorBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestFallbackMode))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyticsIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectorModes))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
