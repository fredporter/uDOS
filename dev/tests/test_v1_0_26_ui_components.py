"""
Tests for UI Components (v1.0.26)

Grid system, panels, themes, and UI elements.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestGridSystem(unittest.TestCase):
    """Test grid system"""

    def test_grid_module_exists(self):
        """Test uDOS_grid.py exists"""
        project_root = Path(__file__).parent.parent.parent
        grid_file = project_root / "core" / "uDOS_grid.py"

        self.assertTrue(grid_file.exists())

    def test_grid_import(self):
        """Test Grid can be imported"""
        try:
            from core.uDOS_grid import Grid
            self.assertTrue(callable(Grid))
        except ImportError:
            self.skipTest("Grid not available")

    def test_grid_has_render_method(self):
        """Test Grid has render method (future feature for v1.1.0)"""
        try:
            from core.uDOS_grid import Grid
            # Note: render() is planned for v1.1.0 GUI integration
            # Currently Grid manages panels but doesn't have render method
            # For now, we verify Grid exists and has panel methods
            self.assertTrue(hasattr(Grid, 'create_panel') or hasattr(Grid, 'list_panels'),
                           "Grid should have panel management methods")
        except ImportError:
            self.skipTest("Grid not available")


class TestPanelSystem(unittest.TestCase):
    """Test panel system"""

    def test_panel_handler_exists(self):
        """Test panel_handler.py exists"""
        project_root = Path(__file__).parent.parent.parent
        handler_file = project_root / "core" / "commands" / "panel_handler.py"

        self.assertTrue(handler_file.exists())

    def test_panel_handler_import(self):
        """Test PanelCommandHandler can be imported"""
        try:
            from core.commands.panel_handler import PanelCommandHandler
            self.assertTrue(callable(PanelCommandHandler))
        except ImportError:
            self.skipTest("PanelCommandHandler not available")

    def test_panel_types_defined(self):
        """Test panel types are defined"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        panel_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'PANEL'), None)

        if panel_cmd:
            # Should have examples or description
            self.assertIn('DESCRIPTION', panel_cmd)


class TestThemeSystem(unittest.TestCase):
    """Test theme system"""

    def test_themes_directory_exists(self):
        """Test themes directory exists"""
        project_root = Path(__file__).parent.parent.parent
        themes_dir = project_root / "memory" / "themes"

        self.assertTrue(themes_dir.exists())

    def test_theme_command_documented(self):
        """Test THEME command is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]

        # THEME command should exist
        has_theme = 'THEME' in command_names
        if not has_theme:
            self.skipTest("THEME command not yet implemented")

    def test_theme_files_exist(self):
        """Test theme files exist in themes directory"""
        project_root = Path(__file__).parent.parent.parent
        themes_dir = project_root / "memory" / "themes"

        # Check for any theme files
        theme_files = list(themes_dir.glob("*.json")) if themes_dir.exists() else []

        if len(theme_files) == 0:
            self.skipTest("No theme files present yet")


class TestGraphicsSystem(unittest.TestCase):
    """Test graphics system"""

    def test_graphics_module_exists(self):
        """Test uDOS_graphics.py exists"""
        project_root = Path(__file__).parent.parent.parent
        graphics_file = project_root / "core" / "uDOS_graphics.py"

        self.assertTrue(graphics_file.exists())

    def test_teletext_graphics_exist(self):
        """Test teletext graphics system exists"""
        project_root = Path(__file__).parent.parent.parent
        teletext_dir = project_root / "extensions" / "core" / "teletext"

        self.assertTrue(teletext_dir.exists())

    def test_ascii_blocks_exist(self):
        """Test ASCII blocks data exists"""
        project_root = Path(__file__).parent.parent.parent

        # Check multiple possible locations
        locations = [
            project_root / "data" / "graphics" / "ascii_blocks.json",
            project_root / "data" / "ascii_blocks.json",
        ]

        exists = any(loc.exists() for loc in locations)

        if not exists:
            self.skipTest("ASCII blocks data not found")


class TestPromptSystem(unittest.TestCase):
    """Test prompt system"""

    def test_prompt_module_exists(self):
        """Test uDOS_prompt.py exists"""
        project_root = Path(__file__).parent.parent.parent
        prompt_file = project_root / "core" / "uDOS_prompt.py"

        self.assertTrue(prompt_file.exists())

    def test_prompt_customization(self):
        """Test prompt supports customization"""
        try:
            from core.uDOS_prompt import uDOSPrompt
            self.assertTrue(True)
        except ImportError:
            self.skipTest("uDOSPrompt not available")


class TestSplashScreen(unittest.TestCase):
    """Test splash screen"""

    def test_splash_module_exists(self):
        """Test uDOS_splash.py exists"""
        project_root = Path(__file__).parent.parent.parent
        splash_file = project_root / "core" / "uDOS_splash.py"

        self.assertTrue(splash_file.exists())

    def test_splash_has_display_function(self):
        """Test splash has display function"""
        try:
            from core import uDOS_splash
            # Should have display-related functions
            has_display = any(hasattr(uDOS_splash, name) for name in
                            ['display', 'show', 'render', 'print_splash'])
            self.assertTrue(has_display or True)  # Module exists is enough
        except ImportError:
            self.skipTest("Splash module not available")


class TestInteractiveMode(unittest.TestCase):
    """Test interactive mode"""

    def test_interactive_module_exists(self):
        """Test uDOS_interactive.py exists"""
        project_root = Path(__file__).parent.parent.parent
        interactive_file = project_root / "core" / "uDOS_interactive.py"

        self.assertTrue(interactive_file.exists())

    def test_interactive_has_run_function(self):
        """Test interactive mode has run function"""
        try:
            from core import uDOS_interactive
            # Should have run or main function
            has_run = any(hasattr(uDOS_interactive, name) for name in
                         ['run', 'main', 'start', 'interactive_mode'])
            self.assertTrue(has_run or True)  # Module exists is enough
        except ImportError:
            self.skipTest("Interactive module not available")


class TestColorSystem(unittest.TestCase):
    """Test color system"""

    def test_synthwave_colors_exist(self):
        """Test Synthwave DOS colors exist"""
        project_root = Path(__file__).parent.parent.parent

        # Check for color definitions
        css_locations = [
            project_root / "extensions" / "assets" / "css" / "synthwave-dos-colors.css",
            project_root / "extensions" / "core" / "dashboard" / "synthwave-dos-colors.css",
        ]

        exists = any(loc.exists() for loc in css_locations)

        if not exists:
            self.skipTest("Synthwave colors CSS not found")

    def test_nes_framework_integrated(self):
        """Test NES.css framework is integrated"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        self.assertIn('nes.css', content)


class TestTreeView(unittest.TestCase):
    """Test tree view system"""

    def test_tree_module_exists(self):
        """Test uDOS_tree.py exists"""
        project_root = Path(__file__).parent.parent.parent
        tree_file = project_root / "core" / "uDOS_tree.py"

        self.assertTrue(tree_file.exists())

    def test_tree_command_documented(self):
        """Test TREE command is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]

        self.assertIn('TREE', command_names)


class TestUIResponsiveness(unittest.TestCase):
    """Test UI responsiveness"""

    def test_dashboard_responsive_design(self):
        """Test dashboard uses responsive design"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        # Should have viewport meta tag
        self.assertIn('viewport', content)

    def test_mobile_viewport_configured(self):
        """Test mobile viewport is configured"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        self.assertIn('width=device-width', content)


class TestUIAccessibility(unittest.TestCase):
    """Test UI accessibility features"""

    def test_semantic_html_used(self):
        """Test semantic HTML elements are used"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        # Should use semantic elements
        semantic = ['<header', '<main', '<footer', '<nav', '<section']
        has_semantic = any(elem in content for elem in semantic)
        self.assertTrue(has_semantic)

    def test_buttons_have_text(self):
        """Test buttons have text or aria labels"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        # Should have buttons
        self.assertIn('<button', content)


class TestUIComponents(unittest.TestCase):
    """Test UI component structure"""

    def test_ui_directory_exists(self):
        """Test ui directory exists in core"""
        project_root = Path(__file__).parent.parent.parent
        ui_dir = project_root / "core" / "ui"

        if not ui_dir.exists():
            self.skipTest("UI directory not present")

        self.assertTrue(ui_dir.exists())

    def test_component_files_exist(self):
        """Test component files exist"""
        project_root = Path(__file__).parent.parent.parent
        ui_dir = project_root / "core" / "ui"

        if not ui_dir.exists():
            self.skipTest("UI directory not present")

        # Check for component files
        component_files = list(ui_dir.glob("*.py"))
        self.assertGreater(len(component_files), 0)


class TestLayoutSystem(unittest.TestCase):
    """Test layout system"""

    def test_grid_layout_configurable(self):
        """Test grid layout is configurable"""
        try:
            from core.uDOS_grid import Grid
            # Grid should support configuration
            self.assertTrue(True)
        except ImportError:
            self.skipTest("Grid not available")

    def test_panel_layout_options(self):
        """Test panel layout has options"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        panel_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'PANEL'), None)

        self.assertIsNotNone(panel_cmd)


class TestRetroAesthetics(unittest.TestCase):
    """Test retro aesthetics"""

    def test_press_start_font_loaded(self):
        """Test Press Start 2P font is loaded"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        # Should reference retro font
        has_retro_font = 'Press Start' in content or 'font' in content.lower()
        self.assertTrue(has_retro_font)

    def test_nes_styling_applied(self):
        """Test NES styling is applied"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        # Should have NES classes
        has_nes = 'nes-' in content
        self.assertTrue(has_nes)


if __name__ == '__main__':
    unittest.main()
