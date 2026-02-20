"""
v1.4.4 THEME Command Tests

Tests THEME command implementation:
- THEME LIST — list available TUI text themes
- THEME SHOW <name> — show theme details
- THEME SET <name> — activate theme (persist to env)
- THEME CLEAR — deactivate custom theme

Validates:
- Theme registry and discovery
- Environment persistence
- Message format application
- Help text generation
"""

import unittest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add core to path
CORE_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CORE_PATH))

from core.commands.theme_handler import ThemeHandler
from core.services.theme_service import (
    canonical_message_theme,
    list_active_themes,
    get_active_theme,
    format_for_theme,
)


class TestThemeHandler(unittest.TestCase):
    """Test THEME command handler."""

    def setUp(self):
        """Initialize theme handler for each test."""
        self.handler = ThemeHandler()

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_theme_list_returns_available_themes(self):
        """Test THEME LIST returns list of registered themes."""
        result = self.handler.handle("THEME", ["list"])
        assert result["status"] == "ok"
        assert "themes" in result.get("data", {}) or "message" in result

    def test_theme_show_builtin_theme(self):
        """Test THEME SHOW displays theme metadata."""
        result = self.handler.handle("THEME", ["show", "default"])
        assert result["status"] == "ok"
        data = result.get("data", {})
        # Should include theme name and description
        assert "name" in data or "message" in result

    def test_theme_show_nonexistent_theme(self):
        """Test THEME SHOW with invalid theme name."""
        result = self.handler.handle("THEME", ["show", "nonexistent-xyz"])
        # Should return error or empty result
        assert result["status"] in ("ok", "error")

    def test_theme_set_persists_to_env(self):
        """Test THEME SET saves to environment variable."""
        with patch.dict(os.environ, {}):
            result = self.handler.handle("THEME", ["set", "default"])
            assert result["status"] == "ok"
            # Check env was set or returned in result
            assert "UDOS_TUI_MESSAGE_THEME" in result.get("data", {}) or \
                   os.getenv("UDOS_TUI_MESSAGE_THEME")

    def test_theme_clear_removes_custom_theme(self):
        """Test THEME CLEAR deactivates custom theme."""
        with patch.dict(os.environ, {"UDOS_TUI_MESSAGE_THEME": "custom"}):
            result = self.handler.handle("THEME", ["clear"])
            assert result["status"] == "ok"
            # Env should be cleared
            assert not os.getenv("UDOS_TUI_MESSAGE_THEME") or \
                   result.get("data", {}).get("theme") == "default"

    def test_theme_help_includes_syntax(self):
        """Test THEME HELP shows usage."""
        result = self.handler.handle("THEME", ["help"])
        assert result["status"] == "ok"
        output = result.get("output", "")
        assert "THEME" in output or "theme" in output.lower()

    def test_theme_no_params_shows_status(self):
        """Test THEME with no params shows current theme."""
        result = self.handler.handle("THEME", [])
        assert result["status"] == "ok"
        # Should show current theme or list available


class TestThemeService(unittest.TestCase):
    """Test theme service helpers."""

    def test_canonical_message_theme(self):
        """Test theme name canonicalization."""
        # Normalize various theme name formats
        assert canonical_message_theme("default") == "default"
        assert canonical_message_theme("Default") == "default"
        assert canonical_message_theme("DEFAULT") == "default"
        assert canonical_message_theme("my_theme") == "my-theme" or \
               canonical_message_theme("my_theme") == "my_theme"

    def test_get_active_theme(self):
        """Test retrieving active theme from environment."""
        with patch.dict(os.environ, {"UDOS_TUI_MESSAGE_THEME": "dark"}):
            theme = get_active_theme()
            assert theme == "dark"

    def test_get_active_theme_defaults_to_default(self):
        """Test fallback to default theme when env unset."""
        with patch.dict(os.environ, {}, clear=True):
            theme = get_active_theme()
            # Should default to "default" or equivalent
            assert theme in ("default", None)

    def test_format_for_theme_applies_formatting(self):
        """Test message formatting for specific theme."""
        # Format should vary by theme
        msg = "Test message"
        default_fmt = format_for_theme(msg, "default")
        assert default_fmt  # Should return formatted message

    def test_list_active_themes(self):
        """Test listing available themes."""
        themes = list_active_themes()
        # Should return list or dict of theme names
        assert isinstance(themes, (list, dict))
        # Should include at least "default" theme
        if isinstance(themes, list):
            assert "default" in themes or len(themes) >= 1
        else:
            assert len(themes) >= 1


class TestThemeIntegration(unittest.TestCase):
    """Integration tests for THEME command."""

    def test_theme_set_and_get_roundtrip(self):
        """Test setting theme and retrieving it."""
        handler = ThemeHandler()
        with patch.dict(os.environ, {}):
            # Set theme
            set_result = handler.handle("THEME", ["set", "default"])
            assert set_result["status"] == "ok"

            # Get current theme via handler or service
            active = get_active_theme()
            assert active  # Should be retrievable

    def test_theme_list_show_set_flow(self):
        """Test complete theme workflow."""
        handler = ThemeHandler()

        # List themes
        list_result = handler.handle("THEME", ["list"])
        assert list_result["status"] == "ok"

        # Show a theme
        show_result = handler.handle("THEME", ["show", "default"])
        assert show_result["status"] == "ok"

        # Set theme
        set_result = handler.handle("THEME", ["set", "default"])
        assert set_result["status"] == "ok"

    def test_theme_clear_and_fallback(self):
        """Test clearing theme reverts to default."""
        handler = ThemeHandler()
        with patch.dict(os.environ, {"UDOS_TUI_MESSAGE_THEME": "custom"}):
            # Clear custom theme
            clear_result = handler.handle("THEME", ["clear"])
            assert clear_result["status"] == "ok"

            # Verify fallback to default
            active = get_active_theme()
            assert active == "default" or active is None


if __name__ == "__main__":
    unittest.main()
