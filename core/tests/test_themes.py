"""
Unit tests for uDOS theme system.

Tests:
- Theme loading from knowledge and memory
- Message formatting with placeholders
- User override merging
- Error handling for missing/malformed themes
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.theme import load_theme
from core.utils.theme_validator import ThemeValidator


class TestThemeLoader(unittest.TestCase):
    """Test theme_loader.py functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = Path(__file__).parent.parent.parent
        self.knowledge_themes = self.root / 'knowledge' / 'system' / 'themes'
        self.memory_themes = self.root / 'memory' / 'system' / 'themes'

    def test_load_default_theme(self):
        """Test loading default theme."""
        theme = load_theme('default', self.root)

        self.assertIsInstance(theme, dict)
        self.assertIn('TERMINOLOGY', theme)
        self.assertIn('MESSAGES', theme)
        self.assertIn('THEME_NAME', theme)

    def test_load_teletext_theme(self):
        """Test loading teletext theme."""
        theme = load_theme('teletext', self.root)

        self.assertIsInstance(theme, dict)
        self.assertIn('TERMINOLOGY', theme)
        self.assertIn('MESSAGES', theme)
        self.assertEqual(theme['THEME_NAME'], 'teletext')

    def test_required_messages_present(self):
        """Test that critical messages exist in themes."""
        required = [
            'ERROR_CRASH', 'ERROR_INVALID_UCODE_FORMAT',
            'ERROR_UNKNOWN_SYSTEM_COMMAND', 'INFO_EXIT'
        ]

        for theme_name in ['default', 'teletext']:
            theme = load_theme(theme_name, self.root)
            messages = theme.get('MESSAGES', {})

            for msg_key in required:
                with self.subTest(theme=theme_name, message=msg_key):
                    self.assertIn(msg_key, messages,
                                f"{msg_key} missing in {theme_name}")

    def test_message_formatting(self):
        """Test that message templates can be formatted."""
        theme = load_theme('default', self.root)
        messages = theme.get('MESSAGES', {})

        # Test ERROR_CRASH with command placeholder
        if 'ERROR_CRASH' in messages:
            template = messages['ERROR_CRASH']
            try:
                formatted = template.format(command='TEST')
                self.assertIn('TEST', formatted)
            except KeyError as e:
                self.fail(f"ERROR_CRASH formatting failed: {e}")

        # Test ERROR_UNKNOWN_MODULE
        if 'ERROR_UNKNOWN_MODULE' in messages:
            template = messages['ERROR_UNKNOWN_MODULE']
            try:
                formatted = template.format(module='test_module')
                self.assertIn('test_module', formatted)
            except KeyError as e:
                self.fail(f"ERROR_UNKNOWN_MODULE formatting failed: {e}")

    def test_memory_override(self):
        """Test that memory overrides work correctly."""
        # Create a temporary memory override
        self.memory_themes.mkdir(parents=True, exist_ok=True)

        override_theme = self.memory_themes / 'test_override.json'
        override_data = {
            "THEME_NAME": "test_override",
            "TERMINOLOGY": {
                "PROMPT": "CUSTOM>>>"
            },
            "MESSAGES": {
                "INFO_EXIT": "Custom exit message"
            }
        }

        try:
            with override_theme.open('w', encoding='utf-8') as f:
                json.dump(override_data, f, indent=2)

            # Load with override
            theme = load_theme('test_override', self.root)

            self.assertEqual(theme['TERMINOLOGY']['PROMPT'], 'CUSTOM>>>')
            self.assertEqual(theme['MESSAGES']['INFO_EXIT'], 'Custom exit message')

        finally:
            # Cleanup
            if override_theme.exists():
                override_theme.unlink()

    def test_missing_theme_fallback(self):
        """Test graceful handling of missing theme."""
        theme = load_theme('nonexistent_theme_xyz', self.root)

        # Should return empty or minimal structure
        self.assertIsInstance(theme, dict)


class TestThemeValidator(unittest.TestCase):
    """Test theme_validator.py functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = Path(__file__).parent.parent.parent
        self.validator = ThemeValidator(self.root)

    def test_validate_default_theme(self):
        """Test that bundled default theme is valid."""
        theme_path = self.root / 'knowledge' / 'system' / 'themes' / 'default.json'

        if theme_path.exists():
            is_valid, errors = self.validator.validate_theme_file(theme_path)

            if not is_valid:
                print(f"\nDefault theme validation errors: {errors}")

            self.assertTrue(is_valid, f"Default theme invalid: {errors}")

    def test_validate_teletext_theme(self):
        """Test that bundled teletext theme is valid."""
        theme_path = self.root / 'knowledge' / 'system' / 'themes' / 'teletext.json'

        if theme_path.exists():
            is_valid, errors = self.validator.validate_theme_file(theme_path)

            if not is_valid:
                print(f"\nTeletext theme validation errors: {errors}")

            self.assertTrue(is_valid, f"Teletext theme invalid: {errors}")

    def test_validate_all_bundled_themes(self):
        """Test that all bundled themes are valid."""
        results = self.validator.validate_all_themes()

        invalid_themes = {name: errors for name, (valid, errors)
                         in results.items() if not valid}

        if invalid_themes:
            print("\nInvalid themes found:")
            for theme_name in invalid_themes:
                is_valid, errors = results[theme_name]
                print(f"  {theme_name}: {errors}")

        self.assertEqual(len(invalid_themes), 0,
                        f"Invalid themes: {list(invalid_themes.keys())}")

    def test_invalid_json_handling(self):
        """Test validator handles malformed JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{ invalid json }')
            temp_path = Path(f.name)

        try:
            is_valid, errors = self.validator.validate_theme_file(temp_path)

            self.assertFalse(is_valid)
            self.assertTrue(any('JSON' in err for err in errors))
        finally:
            temp_path.unlink()

    def test_missing_required_keys(self):
        """Test validator catches missing required keys."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"THEME_NAME": "incomplete"}, f)
            temp_path = Path(f.name)

        try:
            is_valid, errors = self.validator.validate_theme_file(temp_path)

            self.assertFalse(is_valid)
            self.assertTrue(any('Missing required keys' in err for err in errors))
        finally:
            temp_path.unlink()

    def test_invalid_format_string(self):
        """Test validator catches invalid format strings."""
        invalid_theme = {
            "THEME_NAME": "test",
            "TERMINOLOGY": {},
            "MESSAGES": {
                "ERROR_CRASH": "Error: {missing_close",
                "INFO_EXIT": "Valid message"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_theme, f)
            temp_path = Path(f.name)

        try:
            is_valid, errors = self.validator.validate_theme_file(temp_path)

            self.assertFalse(is_valid)
            self.assertTrue(any('invalid format string' in err.lower()
                              for err in errors))
        finally:
            temp_path.unlink()


class TestMessageFormatting(unittest.TestCase):
    """Test actual message formatting scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.root = Path(__file__).parent.parent.parent

    def test_format_error_crash(self):
        """Test ERROR_CRASH formatting."""
        theme = load_theme('default', self.root)
        template = theme.get('MESSAGES', {}).get('ERROR_CRASH', '')

        if template:
            formatted = template.format(command='HELP')
            self.assertIsInstance(formatted, str)
            self.assertGreater(len(formatted), 0)

    def test_format_with_safe_fallback(self):
        """Test safe formatting with missing placeholders."""
        theme = load_theme('default', self.root)
        template = theme.get('MESSAGES', {}).get('ERROR_CRASH', 'Error: {command}')

        # Safe formatting (as used in CommandHandler)
        try:
            formatted = template.format(command='TEST')
        except KeyError:
            formatted = template

        self.assertIsInstance(formatted, str)

    def test_all_messages_format_safely(self):
        """Test that all messages in default theme can be formatted."""
        theme = load_theme('default', self.root)
        messages = theme.get('MESSAGES', {})

        for key, template in messages.items():
            with self.subTest(message=key):
                # Extract placeholders
                import re
                placeholders = re.findall(r'\{([^}]+)\}', template)

                # Create dummy kwargs
                dummy_kwargs = {p: f'test_{p}' for p in placeholders}

                # Should format without error
                try:
                    formatted = template.format(**dummy_kwargs)
                    self.assertIsInstance(formatted, str)
                except Exception as e:
                    self.fail(f"Message {key} failed to format: {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
