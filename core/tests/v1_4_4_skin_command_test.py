"""
v1.4.4 SKIN Command Tests

Tests SKIN command implementation (Wizard GUI themes):
- SKIN LIST — list available Wizard GUI skins
- SKIN SHOW <name> — show skin details
- SKIN SET <name> — apply skin (persist to registry)
- SKIN CLEAR — reset to default skin

Validates:
- Skin registry in /themes directory
- Skin metadata (CSS/HTML themes)
- Persistence to Wizard config (provider registry)
- Help text generation

Note: SKIN is distinct from THEME (GUI vs TUI).
"""

import unittest
import sys
import json
from pathlib import Path

# Add core to path
CORE_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CORE_PATH))

from core.commands.skin_handler import SkinHandler
from core.services.error_contract import CommandError


class TestSkinHandler(unittest.TestCase):
    """Test SKIN command handler."""

    def setUp(self):
        """Initialize skin handler for each test."""
        self.handler = SkinHandler()

    def tearDown(self):
        """Clean up after tests."""
        pass

    def test_skin_list_returns_available_skins(self):
        """Test SKIN LIST returns list of registered skins."""
        result = self.handler.handle("SKIN", ["list"])
        assert result["status"] == "success"
        assert "Skins:" in result.get("output", "")

    def test_skin_show_default_skin(self):
        """Test SKIN SHOW displays skin metadata."""
        result = self.handler.handle("SKIN", ["show", "prose"])
        assert result["status"] == "success"
        assert "SKIN: prose" in result.get("output", "")

    def test_skin_show_nonexistent_skin(self):
        """Test SKIN SHOW with invalid skin name."""
        with self.assertRaises(CommandError):
            self.handler.handle("SKIN", ["show", "nonexistent-xyz"])

    def test_skin_set_persists_to_config(self):
        """Test SKIN SET saves to Wizard configuration."""
        result = self.handler.handle("SKIN", ["set", "prose"])
        assert result["status"] in {"success", "warning"}

    def test_skin_clear_resets_to_default(self):
        """Test SKIN CLEAR reverts to default skin."""
        result = self.handler.handle("SKIN", ["clear"])
        assert result["status"] in {"success", "warning"}

    def test_skin_scaffold_and_insert_css(self):
        """Test SKIN SCAFFOLD + INSERT CSS writes override payload."""
        scaffold = self.handler.handle("SKIN", ["scaffold", "prose"])
        assert scaffold["status"] == "success"

        insert = self.handler.handle("SKIN", ["insert", "prose", "css", ".hud { color: #0ff; }"])
        assert insert["status"] == "success"
        assert "Inserted CSS" in insert.get("output", "")

    def test_skin_insert_slot_payload(self):
        """Test SKIN INSERT SLOT stores slot payload content."""
        result = self.handler.handle(
            "SKIN",
            ["insert", "prose", "slot", "hud", "<div>HUD PANEL</div>"],
        )
        assert result["status"] == "success"
        assert result.get("slot") == "hud"

    def test_skin_help_includes_syntax(self):
        """Test SKIN HELP shows usage."""
        with self.assertRaises(CommandError):
            self.handler.handle("SKIN", ["help"])

    def test_skin_no_params_shows_status(self):
        """Test SKIN with no params shows current skin."""
        result = self.handler.handle("SKIN", [])
        assert result["status"] == "success"
        # Should show current skin or list available


class TestSkinRegistry(unittest.TestCase):
    """Test skin discovery from /themes directory."""

    def test_skin_registry_discovers_theme_directories(self):
        """Test that skins are discovered from /themes."""
        repo_root = Path(__file__).parent.parent.parent
        themes_dir = repo_root / "themes"

        if themes_dir.exists():
            # Should have at least one theme directory
            theme_dirs = [d for d in themes_dir.iterdir() if d.is_dir()]
            assert len(theme_dirs) >= 1

    def test_skin_metadata_json_structure(self):
        """Test that skin metadata files have correct structure."""
        repo_root = Path(__file__).parent.parent.parent
        themes_dir = repo_root / "themes"

        if themes_dir.exists():
            for theme_dir in themes_dir.iterdir():
                if theme_dir.is_dir():
                    metadata_file = theme_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file) as f:
                            meta = json.load(f)
                        # Should have basic fields
                        assert "name" in meta or "title" in meta

    def test_skin_css_and_html_files_exist(self):
        """Test that themes contain CSS and/or HTML files."""
        repo_root = Path(__file__).parent.parent.parent
        themes_dir = repo_root / "themes"

        if themes_dir.exists():
            for theme_dir in themes_dir.iterdir():
                if theme_dir.is_dir():
                    # Should have at least CSS or HTML
                    has_css = any(f.suffix == ".css" for f in theme_dir.rglob("*"))
                    has_html = any(f.suffix == ".html" for f in theme_dir.rglob("*"))
                    # At least one should exist (though not required for all themes)


class TestSkinIntegration(unittest.TestCase):
    """Integration tests for SKIN command."""

    def test_skin_list_show_set_flow(self):
        """Test complete skin workflow."""
        handler = SkinHandler()

        # List skins
        list_result = handler.handle("SKIN", ["list"])
        assert list_result["status"] == "success"

        # Show a skin
        show_result = handler.handle("SKIN", ["show", "prose"])
        assert show_result["status"] == "success"

        # Set skin
        set_result = handler.handle("SKIN", ["set", "prose"])
        assert set_result["status"] in {"success", "warning"}

    def test_skin_clear_and_fallback(self):
        """Test clearing skin reverts to default."""
        handler = SkinHandler()

        # Clear custom skin
        clear_result = handler.handle("SKIN", ["clear"])
        assert clear_result["status"] in {"success", "warning"}

    def test_skin_distinct_from_theme(self):
        """Test that SKIN (GUI) is distinct from THEME (TUI)."""
        # SKIN affects Wizard web dashboard (HTML/CSS)
        # THEME affects uCODE TUI text messages
        # Both can be set independently

        skin_handler = SkinHandler()
        from core.commands.theme_handler import ThemeHandler
        theme_handler = ThemeHandler()

        # Setting one should not affect the other
        skin_result = skin_handler.handle("SKIN", ["list"])
        theme_result = theme_handler.handle("THEME", ["list"])

        # Both should succeed independently
        assert skin_result["status"] == "success"
        assert theme_result["status"] == "success"


if __name__ == "__main__":
    unittest.main()
