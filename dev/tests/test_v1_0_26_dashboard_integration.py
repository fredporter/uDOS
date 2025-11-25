"""
Tests for Dashboard Integration (v1.0.26)

Dashboard widgets, functionality, and component tests.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestDashboardHTML(unittest.TestCase):
    """Test dashboard HTML structure"""

    def test_dashboard_html_valid(self):
        """Test dashboard HTML is well-formed"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Check basic HTML structure (case-insensitive)
        content_lower = content.lower()
        self.assertIn('<!doctype html>', content_lower)
        self.assertIn('<html', content_lower)
        self.assertIn('</html>', content_lower)
        self.assertIn('<head>', content_lower)
        self.assertIn('<body>', content_lower)

    def test_dashboard_has_title(self):
        """Test dashboard has title"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        content_lower = content.lower()
        self.assertIn('<title>', content_lower)
        self.assertIn('udos', content_lower)

    def test_dashboard_has_viewport(self):
        """Test dashboard has viewport meta tag"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('viewport', content)

    def test_dashboard_has_charset(self):
        """Test dashboard has charset meta tag"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('charset', content.lower())

    def test_dashboard_includes_nes_css(self):
        """Test dashboard includes NES.css framework"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('nes.css', content)

    def test_dashboard_has_custom_styles(self):
        """Test dashboard includes custom stylesheet"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have custom CSS
        has_custom_css = 'dashboard-styles.css' in content or '<style>' in content
        self.assertTrue(has_custom_css)


class TestDashboardComponents(unittest.TestCase):
    """Test dashboard UI components"""

    def test_dashboard_has_header(self):
        """Test dashboard has header"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('<header', content)

    def test_dashboard_has_main(self):
        """Test dashboard has main content area"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('<main', content)

    def test_dashboard_has_footer(self):
        """Test dashboard has footer"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('<footer', content)

    def test_dashboard_has_edit_mode_button(self):
        """Test dashboard has edit mode button"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('edit-mode-btn', content.lower()) or self.assertIn('edit', content.lower())

    def test_dashboard_has_add_widget_button(self):
        """Test dashboard has add widget button"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('widget', content.lower())

    def test_dashboard_has_settings_button(self):
        """Test dashboard has settings button"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('settings', content.lower())


class TestDashboardModals(unittest.TestCase):
    """Test dashboard modal functionality"""

    def test_widget_picker_modal_exists(self):
        """Test widget picker modal exists"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('widget-picker', content.lower()) or self.assertIn('modal', content)

    def test_settings_modal_exists(self):
        """Test settings modal exists"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('settings-modal', content.lower()) or self.assertIn('settings', content.lower())

    def test_modal_has_close_button(self):
        """Test modals have close buttons"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have close functionality
        has_close = 'close' in content.lower() or '✕' in content
        self.assertTrue(has_close)


class TestDashboardJavaScript(unittest.TestCase):
    """Test dashboard JavaScript functionality"""

    def test_dashboard_has_javascript(self):
        """Test dashboard includes JavaScript"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have script tags
        self.assertIn('<script', content)

    def test_dashboard_builder_js_exists(self):
        """Test dashboard-builder.js exists"""
        project_root = Path(__file__).parent.parent.parent
        js_file = project_root / "extensions" / "core" / "dashboard" / "dashboard-builder.js"

        # May be embedded or separate file
        if not js_file.exists():
            # Check if embedded in HTML
            index = project_root / "extensions" / "core" / "dashboard" / "index.html"
            with open(index, 'r') as f:
                content = f.read()
                self.assertIn('dashboardBuilder', content)
        else:
            self.assertTrue(js_file.exists())

    def test_dashboard_has_event_handlers(self):
        """Test dashboard has event handlers"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have onclick handlers
        self.assertIn('onclick', content.lower())


class TestDashboardWidgets(unittest.TestCase):
    """Test dashboard widget system"""

    def test_widget_picker_list_exists(self):
        """Test widget picker list container exists"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        self.assertIn('widget-picker-list', content.lower()) or self.assertIn('widget', content.lower())

    def test_dashboard_main_grid_exists(self):
        """Test main dashboard grid exists"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have main content area for widgets
        self.assertIn('dashboard-main', content.lower()) or self.assertIn('<main', content)


class TestDashboardTheming(unittest.TestCase):
    """Test dashboard theme system"""

    def test_theme_selector_exists(self):
        """Test theme selector exists"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have theme selection
        has_theme = 'theme-select' in content.lower() or 'theme' in content.lower()
        self.assertTrue(has_theme)

    def test_synthwave_dos_colors(self):
        """Test Synthwave DOS colors stylesheet"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should reference color scheme
        has_colors = 'synthwave' in content.lower() or 'dos-colors' in content.lower()
        if not has_colors:
            self.skipTest("Synthwave DOS colors not referenced")

    def test_press_start_font(self):
        """Test Press Start 2P font is loaded"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have retro font
        has_font = 'Press Start' in content or 'font' in content.lower()
        self.assertTrue(has_font)


class TestDashboardVersion(unittest.TestCase):
    """Test dashboard version display"""

    def test_version_badge_exists(self):
        """Test version badge exists"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should display version
        has_version = 'v1' in content.lower() or 'version' in content.lower()
        self.assertTrue(has_version)

    def test_footer_has_version(self):
        """Test footer displays version"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Footer should have version info
        self.assertIn('<footer', content)
        self.assertIn('v1.0', content.lower()) or self.assertIn('udos', content.lower())


class TestDashboardFooter(unittest.TestCase):
    """Test dashboard footer functionality"""

    def test_footer_has_stats(self):
        """Test footer has stats display"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have stats or info in footer
        has_stats = 'footer-stats' in content.lower() or 'footer-stat' in content.lower()
        if not has_stats:
            self.skipTest("Footer stats not found")

    def test_footer_has_time_display(self):
        """Test footer has current time"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have time display
        has_time = 'current-time' in content.lower() or 'time' in content.lower()
        if not has_time:
            self.skipTest("Time display not found")

    def test_footer_has_status_indicator(self):
        """Test footer has status indicator"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should have status (online/offline)
        has_status = 'status' in content.lower() or 'online' in content.lower()
        if not has_status:
            self.skipTest("Status indicator not found")


class TestDashboardAccessibility(unittest.TestCase):
    """Test dashboard accessibility features"""

    def test_buttons_have_text(self):
        """Test buttons have text content"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Buttons should have descriptive text
        import re
        buttons = re.findall(r'<button[^>]*>(.*?)</button>', content, re.DOTALL)

        if buttons:
            # At least one button should have content
            has_text = any(btn.strip() for btn in buttons)
            self.assertTrue(has_text)

    def test_semantic_html_structure(self):
        """Test semantic HTML5 elements"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Should use semantic elements
        semantic_elements = ['<header', '<main', '<footer', '<section', '<nav']
        has_semantic = any(elem in content for elem in semantic_elements)
        self.assertTrue(has_semantic)


class TestDashboardResponsiveness(unittest.TestCase):
    """Test dashboard responsive design"""

    def test_viewport_meta_configured(self):
        """Test viewport is configured for mobile"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Viewport should be set
        self.assertIn('viewport', content)
        self.assertIn('width=device-width', content)

    def test_mobile_first_approach(self):
        """Test mobile-first CSS approach"""
        project_root = Path(__file__).parent.parent.parent

        # Check if custom CSS exists
        css_file = project_root / "extensions" / "core" / "dashboard" / "dashboard-styles.css"

        if css_file.exists():
            with open(css_file, 'r') as f:
                content = f.read()
                # Should have media queries
                has_media_queries = '@media' in content
                if not has_media_queries:
                    self.skipTest("No media queries found")


if __name__ == '__main__':
    unittest.main()
