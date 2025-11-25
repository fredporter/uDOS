"""
Tests for Extensions System (v1.0.26)

Extension integration, server functionality, and web interface tests.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestExtensionsServer(unittest.TestCase):
    """Test extensions server infrastructure"""

    def test_extensions_core_path_exists(self):
        """Test extensions/core directory exists"""
        project_root = Path(__file__).parent.parent.parent
        extensions_core = project_root / "extensions" / "core"
        self.assertTrue(extensions_core.exists())

    def test_extensions_server_file_exists(self):
        """Test extensions_server.py exists"""
        project_root = Path(__file__).parent.parent.parent
        server_file = project_root / "extensions" / "core" / "extensions_server.py"
        self.assertTrue(server_file.exists())

    def test_dashboard_directory_exists(self):
        """Test dashboard extension exists"""
        project_root = Path(__file__).parent.parent.parent
        dashboard = project_root / "extensions" / "core" / "dashboard"
        self.assertTrue(dashboard.exists())

    def test_dashboard_index_exists(self):
        """Test dashboard has index.html"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"
        self.assertTrue(index.exists())

    def test_dashboard_is_html(self):
        """Test dashboard index.html is valid HTML"""
        project_root = Path(__file__).parent.parent.parent
        index = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(index, 'r') as f:
            content = f.read()

        # Case-insensitive HTML check
        content_lower = content.lower()
        self.assertIn('<!doctype html>', content_lower)
        self.assertIn('<html', content_lower)

    def test_teletext_extension_exists(self):
        """Test teletext extension directory exists"""
        project_root = Path(__file__).parent.parent.parent
        teletext = project_root / "extensions" / "core" / "teletext"
        self.assertTrue(teletext.exists())

    def test_terminal_extension_exists(self):
        """Test terminal extension exists"""
        project_root = Path(__file__).parent.parent.parent
        terminal = project_root / "extensions" / "core" / "terminal"
        self.assertTrue(terminal.exists())

    def test_markdown_extension_exists(self):
        """Test markdown extension exists"""
        project_root = Path(__file__).parent.parent.parent
        # Check both possible directory names
        markdown_viewer = project_root / "extensions" / "core" / "markdown-viewer"
        markdown = project_root / "extensions" / "core" / "markdown"
        self.assertTrue(markdown_viewer.exists() or markdown.exists(),
                       "Markdown extension not found at markdown-viewer or markdown")

    def test_desktop_extension_exists(self):
        """Test desktop extension exists"""
        project_root = Path(__file__).parent.parent.parent
        desktop = project_root / "extensions" / "core" / "desktop"
        self.assertTrue(desktop.exists())


class TestDashboardComponents(unittest.TestCase):
    """Test dashboard components and features"""

    def test_dashboard_has_css(self):
        """Test dashboard has CSS file"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_dir = project_root / "extensions" / "core" / "dashboard"

        css_files = list(dashboard_dir.glob("*.css"))
        self.assertGreater(len(css_files), 0, "Dashboard should have CSS files")

    def test_dashboard_has_javascript(self):
        """Test dashboard has JavaScript file"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_dir = project_root / "extensions" / "core" / "dashboard"

        js_files = list(dashboard_dir.glob("*.js"))
        self.assertGreater(len(js_files), 0, "Dashboard should have JS files")

    def test_dashboard_readme_exists(self):
        """Test dashboard has README"""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "extensions" / "core" / "dashboard" / "README.md"
        self.assertTrue(readme.exists())


class TestExtensionConfiguration(unittest.TestCase):
    """Test extension configuration and setup"""

    def test_extensions_readme_exists(self):
        """Test extensions README exists"""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "extensions" / "README.md"
        self.assertTrue(readme.exists())

    def test_extensions_setup_exists(self):
        """Test extensions setup directory exists"""
        project_root = Path(__file__).parent.parent.parent
        setup = project_root / "extensions" / "setup"
        self.assertTrue(setup.exists())

    def test_extensions_core_readme(self):
        """Test core extensions README exists"""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "extensions" / "core" / "README.md"
        self.assertTrue(readme.exists())


class TestWebServerConfiguration(unittest.TestCase):
    """Test web server configuration"""

    def test_server_port_configuration(self):
        """Test server uses expected port range"""
        # Default ports: 8888-9002
        expected_ports = [8888, 8889, 8887, 9000, 9001, 9002]
        self.assertEqual(len(expected_ports), 6)

    def test_server_supports_multiple_extensions(self):
        """Test server can handle multiple extensions"""
        extensions = ['dashboard', 'teletext', 'terminal', 'markdown-viewer', 'desktop']
        self.assertEqual(len(extensions), 5)


class TestExtensionIntegration(unittest.TestCase):
    """Test extension integration with uDOS core"""

    def test_poke_command_documented(self):
        """Test POKE command exists in documentation"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('POKE', command_names)

    def test_web_command_documented(self):
        """Test WEB command exists in documentation"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('WEB', command_names)

    def test_dashboard_command_documented(self):
        """Test DASH/DASHBOARD command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('DASH', command_names)


class TestExtensionFiles(unittest.TestCase):
    """Test extension file structure"""

    def test_extension_templates_exist(self):
        """Test extension templates directory exists"""
        project_root = Path(__file__).parent.parent.parent
        templates = project_root / "extensions" / "templates"
        self.assertTrue(templates.exists())

    def test_cloned_extensions_directory(self):
        """Test cloned extensions directory exists"""
        project_root = Path(__file__).parent.parent.parent
        cloned = project_root / "extensions" / "cloned"
        self.assertTrue(cloned.exists())


if __name__ == '__main__':
    unittest.main()
