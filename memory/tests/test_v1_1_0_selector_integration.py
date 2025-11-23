#!/usr/bin/env python3
"""
uDOS v1.1.0 - Unified Selector Integration Tests
Test that unified selector properly integrates with existing command infrastructure

Tests cover:
- InteractivePrompt.ask_choice() migration
- InputManager.prompt_choice() migration
- Backward compatibility with old imports
- Fallback behavior when selector unavailable
- File picker integration

Author: uDOS Development Team
Version: 1.1.0
Phase: TUI Reliability & Input System (Feature 1.1.0.9)
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.input.interactive import InteractivePrompt
from core.services.input_manager import InputManager


class TestInteractivePromptMigration(unittest.TestCase):
    """Test InteractivePrompt migrated to unified selector."""

    def setUp(self):
        """Set up test fixtures."""
        self.prompt = InteractivePrompt(use_arrow_keys=True)

    def test_ask_choice_uses_unified_selector(self):
        """Test that ask_choice uses unified selector when available."""
        choices = ["Option A", "Option B", "Option C"]

        # Mock the unified selector
        with patch('core.ui.unified_selector.select_single', return_value="Option B") as mock_select:
            result = self.prompt.ask_choice(
                prompt="Choose one",
                choices=choices,
                default="Option A"
            )

            # Should have called unified selector
            mock_select.assert_called_once()
            self.assertEqual(result, "Option B")

    def test_ask_choice_fallback_on_cancel(self):
        """Test fallback to text mode when selector is cancelled."""
        choices = ["A", "B", "C"]

        # Mock selector returning None (cancelled)
        with patch('core.ui.unified_selector.select_single', return_value=None):
            with patch('builtins.input', return_value='2'):
                with patch('builtins.print'):
                    result = self.prompt.ask_choice(
                        prompt="Choose",
                        choices=choices
                    )

                    # Should fall back to text mode and select B
                    self.assertEqual(result, "B")

    def test_ask_choice_fallback_on_error(self):
        """Test fallback to text mode when selector fails."""
        choices = ["X", "Y", "Z"]

        # Mock selector raising exception
        with patch('core.ui.unified_selector.select_single', side_effect=ImportError("Not found")):
            with patch('builtins.input', return_value='1'):
                with patch('builtins.print'):
                    result = self.prompt.ask_choice(
                        prompt="Choose",
                        choices=choices
                    )

                    # Should fall back and select X
                    self.assertEqual(result, "X")

    def test_ask_choice_respects_default(self):
        """Test that default parameter is passed correctly."""
        choices = ["First", "Second", "Third"]
        default = "Second"

        with patch('core.ui.unified_selector.select_single') as mock_select:
            mock_select.return_value = default

            result = self.prompt.ask_choice(
                prompt="Pick one",
                choices=choices,
                default=default
            )

            # Should have found default index (1)
            call_kwargs = mock_select.call_args.kwargs
            self.assertEqual(call_kwargs['default_index'], 1)
            self.assertEqual(result, default)

    def test_ask_choice_with_arrow_keys_disabled(self):
        """Test that arrow keys can be disabled."""
        prompt_no_arrows = InteractivePrompt(use_arrow_keys=False)
        choices = ["A", "B"]

        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                result = prompt_no_arrows.ask_choice(
                    prompt="Choose",
                    choices=choices
                )

                # Should use text mode directly
                self.assertEqual(result, "A")


class TestInputManagerMigration(unittest.TestCase):
    """Test InputManager migrated to unified selector."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the dependencies that InputManager needs
        with patch('core.services.input_manager.Style'):
            with patch('core.services.input_manager.WordCompleter'):
                self.input_mgr = InputManager()

    def test_prompt_choice_uses_unified_selector(self):
        """Test that prompt_choice uses unified selector."""
        choices = ["theme1", "theme2", "theme3"]

        with patch('core.ui.unified_selector.select_single', return_value="theme2") as mock_select:
            result = self.input_mgr.prompt_choice(
                message="Select theme",
                choices=choices,
                default="theme1"
            )

            # Should have called unified selector
            mock_select.assert_called_once()
            self.assertEqual(result, "theme2")

    def test_prompt_choice_with_custom_allowed(self):
        """Test prompt_choice with allow_custom flag."""
        choices = ["A", "B", "C"]

        # User cancels selector, should fall through to text input
        with patch('core.ui.unified_selector.select_single', return_value=None):
            with patch('core.services.input_manager.prompt', return_value="custom_value"):
                with patch('builtins.print'):
                    result = self.input_mgr.prompt_choice(
                        message="Choose or enter custom",
                        choices=choices,
                        allow_custom=True
                    )

                    # Should allow custom value
                    self.assertEqual(result, "custom_value")

    def test_prompt_choice_fallback_on_cancel_no_custom(self):
        """Test that cancelling without allow_custom returns default."""
        choices = ["opt1", "opt2"]
        default = "opt1"

        with patch('core.ui.unified_selector.select_single', return_value=None):
            result = self.input_mgr.prompt_choice(
                message="Choose",
                choices=choices,
                default=default,
                allow_custom=False
            )

            # Should return default when cancelled and no custom allowed
            self.assertEqual(result, default)

    def test_prompt_choice_legacy_fallback(self):
        """Test fallback to legacy mode when unified selector unavailable."""
        choices = ["legacy1", "legacy2"]

        with patch('core.ui.unified_selector.select_single', side_effect=ImportError):
            with patch('core.services.input_manager.prompt', return_value="legacy1"):
                with patch('builtins.print'):
                    result = self.input_mgr.prompt_choice(
                        message="Select",
                        choices=choices
                    )

                    # Should fall back to legacy prompt mode
                    self.assertEqual(result, "legacy1")


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with old imports."""

    def test_old_imports_still_work(self):
        """Test that old import paths still function."""
        # These imports should still work for backward compatibility
        from core.ui.pickers import OptionSelector, EnhancedFilePicker

        self.assertIsNotNone(OptionSelector)
        self.assertIsNotNone(EnhancedFilePicker)

    def test_new_imports_available(self):
        """Test that new unified selector is importable."""
        try:
            from core.ui.pickers import UnifiedSelector, select_single
            self.assertIsNotNone(UnifiedSelector)
            self.assertIsNotNone(select_single)
        except ImportError:
            self.fail("Unified selector should be available from pickers package")

    def test_direct_unified_import(self):
        """Test direct import from unified_selector module."""
        from core.ui.unified_selector import (
            UnifiedSelector,
            select_single,
            select_multiple,
            select_file
        )

        self.assertIsNotNone(UnifiedSelector)
        self.assertIsNotNone(select_single)
        self.assertIsNotNone(select_multiple)
        self.assertIsNotNone(select_file)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases in migration."""

    def test_empty_choices_handling(self):
        """Test handling of empty choices list."""
        prompt = InteractivePrompt()

        with patch('core.ui.unified_selector.select_single', return_value=None):
            with patch('builtins.print'):
                with patch('builtins.input', return_value=''):
                    result = prompt.ask_choice(
                        prompt="Choose",
                        choices=[],
                        default=""
                    )

                    # Should handle gracefully
                    self.assertIsNotNone(result)

    def test_single_choice_handling(self):
        """Test handling of single-item choices."""
        prompt = InteractivePrompt()
        choices = ["Only Option"]

        with patch('core.ui.unified_selector.select_single', return_value="Only Option"):
            result = prompt.ask_choice(
                prompt="Only one choice",
                choices=choices
            )

            self.assertEqual(result, "Only Option")

    def test_default_not_in_choices(self):
        """Test behavior when default is not in choices list."""
        prompt = InteractivePrompt()
        choices = ["A", "B", "C"]
        default = "D"  # Not in choices

        with patch('core.ui.unified_selector.select_single') as mock_select:
            mock_select.return_value = "A"

            result = prompt.ask_choice(
                prompt="Choose",
                choices=choices,
                default=default
            )

            # Should default to index 0 when default not found
            call_kwargs = mock_select.call_args.kwargs
            self.assertEqual(call_kwargs['default_index'], 0)


def run_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestInteractivePromptMigration))
    suite.addTests(loader.loadTestsFromTestCase(TestInputManagerMigration))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
