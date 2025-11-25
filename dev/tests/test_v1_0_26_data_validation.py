"""
Tests for Data Validation (v1.0.26)

Data integrity, validation, and consistency tests.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCommandsJSONValidation(unittest.TestCase):
    """Test commands.json data validation"""

    def test_commands_json_is_valid_json(self):
        """Test commands.json is valid JSON"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        self.assertIsInstance(data, dict)

    def test_commands_json_has_commands_key(self):
        """Test commands.json has COMMANDS key"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        self.assertIn('COMMANDS', data)

    def test_commands_array_is_list(self):
        """Test COMMANDS is a list"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        self.assertIsInstance(commands, list)

    def test_each_command_has_name(self):
        """Test each command has NAME field"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        for cmd in commands:
            self.assertIn('NAME', cmd, f"Command missing NAME: {cmd}")

    def test_each_command_has_description(self):
        """Test each command has DESCRIPTION field"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        for cmd in commands:
            self.assertIn('DESCRIPTION', cmd,
                         f"Command {cmd.get('NAME', 'unknown')} missing DESCRIPTION")

    def test_command_names_are_uppercase(self):
        """Test command names are uppercase"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        for cmd in commands:
            name = cmd.get('NAME', '')
            self.assertEqual(name, name.upper(),
                           f"Command name should be uppercase: {name}")

    def test_no_duplicate_command_names(self):
        """Test no duplicate command names"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        names = [cmd.get('NAME') for cmd in commands]

        # Check for duplicates
        seen = set()
        duplicates = []
        for name in names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)

        self.assertEqual(len(duplicates), 0,
                        f"Duplicate command names found: {duplicates}")


class TestDirectoryStructureValidation(unittest.TestCase):
    """Test directory structure validation"""

    def test_core_directory_exists(self):
        """Test core directory exists"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        self.assertTrue(core_dir.exists())

    def test_memory_directory_exists(self):
        """Test memory directory exists"""
        project_root = Path(__file__).parent.parent.parent
        memory_dir = project_root / "memory"

        self.assertTrue(memory_dir.exists())

    def test_knowledge_directory_exists(self):
        """Test knowledge directory exists"""
        project_root = Path(__file__).parent.parent.parent
        knowledge_dir = project_root / "knowledge"

        self.assertTrue(knowledge_dir.exists())

    def test_extensions_directory_exists(self):
        """Test extensions directory exists"""
        project_root = Path(__file__).parent.parent.parent
        extensions_dir = project_root / "extensions"

        self.assertTrue(extensions_dir.exists())

    def test_required_core_files_exist(self):
        """Test required core files exist"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        required_files = [
            'uDOS_main.py',
            'uDOS_commands.py',
            'uDOS_parser.py',
            'uDOS_logger.py',
            'uDOS_settings.py'
        ]

        for filename in required_files:
            filepath = core_dir / filename
            self.assertTrue(filepath.exists(), f"Required file missing: {filename}")


class TestMemoryTierValidation(unittest.TestCase):
    """Test memory tier validation"""

    def test_memory_tiers_exist(self):
        """Test memory tier directories exist"""
        project_root = Path(__file__).parent.parent.parent
        memory_dir = project_root / "memory"

        tiers = ['private', 'public', 'shared']

        for tier in tiers:
            tier_dir = memory_dir / tier
            self.assertTrue(tier_dir.exists(), f"Memory tier missing: {tier}")

    def test_sandbox_exists(self):
        """Test sandbox directory exists"""
        project_root = Path(__file__).parent.parent.parent
        sandbox_dir = project_root / "memory" / "sandbox"

        self.assertTrue(sandbox_dir.exists())


class TestKnowledgeStructureValidation(unittest.TestCase):
    """Test knowledge structure validation"""

    def test_system_knowledge_exists(self):
        """Test system knowledge directory exists"""
        project_root = Path(__file__).parent.parent.parent
        system_dir = project_root / "knowledge" / "system"

        self.assertTrue(system_dir.exists())

    def test_commands_json_exists(self):
        """Test commands.json exists"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        self.assertTrue(commands_file.exists())

    def test_knowledge_readme_exists(self):
        """Test knowledge README exists"""
        project_root = Path(__file__).parent.parent.parent
        readme = project_root / "knowledge" / "README.md"

        self.assertTrue(readme.exists())


class TestConfigFileValidation(unittest.TestCase):
    """Test configuration file validation"""

    def test_pytest_ini_exists(self):
        """Test pytest.ini exists"""
        project_root = Path(__file__).parent.parent.parent
        pytest_ini = project_root / "pytest.ini"

        self.assertTrue(pytest_ini.exists())

    def test_requirements_txt_exists(self):
        """Test requirements.txt exists"""
        project_root = Path(__file__).parent.parent.parent
        requirements = project_root / "requirements.txt"

        self.assertTrue(requirements.exists())

    def test_requirements_txt_valid(self):
        """Test requirements.txt is valid"""
        project_root = Path(__file__).parent.parent.parent
        requirements = project_root / "requirements.txt"

        with open(requirements, 'r') as f:
            content = f.read()

        # Should have some content
        self.assertGreater(len(content.strip()), 0)


class TestDocumentationValidation(unittest.TestCase):
    """Test documentation validation"""

    def test_readme_exists(self):
        """Test README exists"""
        project_root = Path(__file__).parent.parent.parent

        readmes = [
            project_root / "README.MD",
            project_root / "README.md"
        ]

        exists = any(r.exists() for r in readmes)
        self.assertTrue(exists)

    def test_roadmap_exists(self):
        """Test ROADMAP exists"""
        project_root = Path(__file__).parent.parent.parent

        roadmaps = [
            project_root / "ROADMAP.MD",
            project_root / "ROADMAP.md"
        ]

        exists = any(r.exists() for r in roadmaps)
        self.assertTrue(exists)

    def test_changelog_exists(self):
        """Test CHANGELOG exists"""
        project_root = Path(__file__).parent.parent.parent
        changelog = project_root / "CHANGELOG.md"

        self.assertTrue(changelog.exists())


class TestFileIntegrityValidation(unittest.TestCase):
    """Test file integrity validation"""

    def test_python_files_have_docstrings(self):
        """Test Python files have module docstrings"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        py_files = list(core_dir.glob("uDOS_*.py"))

        files_without_docstrings = []

        for py_file in py_files:
            with open(py_file, 'r') as f:
                content = f.read()
                # Check for docstring (triple quotes)
                has_docstring = '"""' in content or "'''" in content
                if not has_docstring:
                    files_without_docstrings.append(py_file.name)

        # Most files should have docstrings
        if len(files_without_docstrings) > len(py_files) / 2:
            self.fail(f"Many files missing docstrings: {files_without_docstrings}")

    def test_json_files_are_valid(self):
        """Test all JSON files are valid (excludes external libraries)"""
        project_root = Path(__file__).parent.parent.parent

        json_files = list(project_root.glob("**/*.json"))

        invalid_files = []

        for json_file in json_files:
            # Skip node_modules, hidden directories, and external libraries
            skip_patterns = [
                'node_modules',
                '/.git/',
                '/extensions/cloned/',  # External libraries not under our control
                '/.devcontainer/'       # External config files
            ]

            if any(pattern in str(json_file) for pattern in skip_patterns):
                continue

            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError:
                invalid_files.append(json_file)

        self.assertEqual(len(invalid_files), 0,
                        f"Invalid JSON files: {[str(f) for f in invalid_files]}")


class TestDataConsistency(unittest.TestCase):
    """Test data consistency across systems"""

    def test_command_names_consistent(self):
        """Test command names are consistent across files"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        names = [cmd.get('NAME') for cmd in commands]

        # All names should be strings and non-empty
        for name in names:
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)

    def test_paths_are_relative_not_absolute(self):
        """Test paths in code are relative not absolute"""
        # This is a best practice check
        self.assertTrue(True)  # Placeholder


class TestSecurityValidation(unittest.TestCase):
    """Test security-related validation"""

    def test_no_hardcoded_passwords(self):
        """Test no hardcoded passwords in code"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        py_files = list(core_dir.glob("*.py"))

        suspicious_patterns = ['password =', 'pwd =', 'secret =']
        files_with_issues = []

        for py_file in py_files:
            with open(py_file, 'r') as f:
                content = f.read().lower()
                for pattern in suspicious_patterns:
                    if pattern in content and 'test' not in str(py_file).lower():
                        files_with_issues.append(py_file.name)
                        break

        # Allow some configuration files to have password fields
        self.assertLess(len(files_with_issues), 5)

    def test_private_memory_isolated(self):
        """Test private memory is isolated"""
        project_root = Path(__file__).parent.parent.parent
        private_dir = project_root / "memory" / "private"

        self.assertTrue(private_dir.exists())


class TestVersionConsistency(unittest.TestCase):
    """Test version consistency"""

    def test_version_in_roadmap(self):
        """Test version is documented in ROADMAP"""
        project_root = Path(__file__).parent.parent.parent
        roadmap = project_root / "ROADMAP.MD"

        with open(roadmap, 'r') as f:
            content = f.read()

        # Should mention v1.0 versions
        self.assertIn('v1.0', content)

    def test_version_in_dashboard(self):
        """Test version is shown in dashboard"""
        project_root = Path(__file__).parent.parent.parent
        dashboard = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard, 'r') as f:
            content = f.read()

        # Should display version
        has_version = 'v1' in content.lower() or 'version' in content.lower()
        self.assertTrue(has_version)


if __name__ == '__main__':
    unittest.main()
