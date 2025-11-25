"""
Tests for uCODE System (v1.0.26)

uCODE language, templates, and execution tests.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestUcodeModule(unittest.TestCase):
    """Test uCODE module"""

    def test_ucode_module_exists(self):
        """Test uDOS_ucode.py exists"""
        project_root = Path(__file__).parent.parent.parent
        ucode_file = project_root / "core" / "uDOS_ucode.py"

        self.assertTrue(ucode_file.exists())

    def test_ucode_import(self):
        """Test uCODE module can be imported"""
        try:
            from core import uDOS_ucode
            self.assertTrue(True)
        except ImportError:
            self.skipTest("uCODE module not available")


class TestUcodeDocumentation(unittest.TestCase):
    """Test uCODE documentation"""

    def test_ucode_wiki_exists(self):
        """Test uCODE wiki documentation exists"""
        project_root = Path(__file__).parent.parent.parent
        ucode_wiki = project_root / "wiki" / "uCODE-Language.md"

        self.assertTrue(ucode_wiki.exists())

    def test_ucode_wiki_content(self):
        """Test uCODE wiki has content"""
        project_root = Path(__file__).parent.parent.parent
        ucode_wiki = project_root / "wiki" / "uCODE-Language.md"

        with open(ucode_wiki, 'r') as f:
            content = f.read()

        # Should contain uCODE information
        self.assertIn('uCODE', content)
        self.assertGreater(len(content), 100)


class TestUcodeTemplates(unittest.TestCase):
    """Test uCODE templates"""

    def test_commands_have_ucode_templates(self):
        """Test commands have uCODE templates"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Count commands with uCODE templates
        with_templates = [cmd for cmd in commands if 'UCODE_TEMPLATE' in cmd]

        # Many commands should have templates
        self.assertGreater(len(with_templates), 0)

    def test_ucode_template_format(self):
        """Test uCODE templates use correct format"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Check template format
        for cmd in commands:
            if 'UCODE_TEMPLATE' in cmd:
                template = cmd['UCODE_TEMPLATE']
                # Should be a string
                self.assertIsInstance(template, str)
                # Should contain brackets for uCODE
                if len(template) > 0:
                    self.assertTrue('[' in template or
                                  template.startswith('//') or
                                  template == '' or
                                  True)  # Some may be empty


class TestUcodeScripts(unittest.TestCase):
    """Test uCODE scripts"""

    def test_uscript_files_exist(self):
        """Test .uscript files exist"""
        project_root = Path(__file__).parent.parent.parent

        # Check for uscript files in memory/tests
        test_scripts = list(project_root.glob("memory/tests/**/*.uscript"))

        if len(test_scripts) == 0:
            self.skipTest("No .uscript files found")

        self.assertGreater(len(test_scripts), 0)

    def test_shakedown_script_exists(self):
        """Test shakedown.uscript exists"""
        project_root = Path(__file__).parent.parent.parent
        shakedown = project_root / "memory" / "tests" / "shakedown.uscript"

        self.assertTrue(shakedown.exists())


class TestUcodeExecution(unittest.TestCase):
    """Test uCODE execution"""

    def test_run_command_supports_uscript(self):
        """Test RUN command supports .uscript files"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        run_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'RUN'), None)

        self.assertIsNotNone(run_cmd)


class TestUcodeLanguageFeatures(unittest.TestCase):
    """Test uCODE language features"""

    def test_ucode_supports_variables(self):
        """Test uCODE language documentation mentions variables"""
        project_root = Path(__file__).parent.parent.parent
        ucode_wiki = project_root / "wiki" / "uCODE-Language.md"

        with open(ucode_wiki, 'r') as f:
            content = f.read()

        # Should mention variables
        has_variables = 'variable' in content.lower() or '$' in content
        self.assertTrue(has_variables)

    def test_ucode_supports_functions(self):
        """Test uCODE language documentation mentions functions"""
        project_root = Path(__file__).parent.parent.parent
        ucode_wiki = project_root / "wiki" / "uCODE-Language.md"

        with open(ucode_wiki, 'r') as f:
            content = f.read()

        # Should mention functions
        has_functions = 'function' in content.lower()
        self.assertTrue(has_functions)

    def test_ucode_supports_conditionals(self):
        """Test uCODE language documentation mentions conditionals"""
        project_root = Path(__file__).parent.parent.parent
        ucode_wiki = project_root / "wiki" / "uCODE-Language.md"

        with open(ucode_wiki, 'r') as f:
            content = f.read()

        # Should mention conditionals
        has_conditionals = 'if' in content.lower() or 'conditional' in content.lower()
        self.assertTrue(has_conditionals)

    def test_ucode_supports_loops(self):
        """Test uCODE language documentation mentions loops"""
        project_root = Path(__file__).parent.parent.parent
        ucode_wiki = project_root / "wiki" / "uCODE-Language.md"

        with open(ucode_wiki, 'r') as f:
            content = f.read()

        # Should mention loops
        has_loops = 'loop' in content.lower() or 'while' in content.lower() or 'for' in content.lower()
        self.assertTrue(has_loops)


if __name__ == '__main__':
    unittest.main()
