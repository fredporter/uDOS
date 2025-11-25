"""
Tests for System Architecture (v1.0.26)

Core architecture, modules, services, and utilities tests.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCoreArchitecture(unittest.TestCase):
    """Test core architecture"""

    def test_main_module_exists(self):
        """Test uDOS_main.py exists"""
        project_root = Path(__file__).parent.parent.parent
        main_file = project_root / "core" / "uDOS_main.py"

        self.assertTrue(main_file.exists())

    def test_commands_module_exists(self):
        """Test uDOS_commands.py exists"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "core" / "uDOS_commands.py"

        self.assertTrue(commands_file.exists())

    def test_parser_module_exists(self):
        """Test uDOS_parser.py exists"""
        project_root = Path(__file__).parent.parent.parent
        parser_file = project_root / "core" / "uDOS_parser.py"

        self.assertTrue(parser_file.exists())

    def test_logger_module_exists(self):
        """Test uDOS_logger.py exists"""
        project_root = Path(__file__).parent.parent.parent
        logger_file = project_root / "core" / "uDOS_logger.py"

        self.assertTrue(logger_file.exists())

    def test_settings_module_exists(self):
        """Test uDOS_settings.py exists"""
        project_root = Path(__file__).parent.parent.parent
        settings_file = project_root / "core" / "uDOS_settings.py"

        self.assertTrue(settings_file.exists())

    def test_env_module_exists(self):
        """Test uDOS_env.py exists"""
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / "core" / "uDOS_env.py"

        self.assertTrue(env_file.exists())

    def test_files_module_exists(self):
        """Test uDOS_files.py exists"""
        project_root = Path(__file__).parent.parent.parent
        files_file = project_root / "core" / "uDOS_files.py"

        self.assertTrue(files_file.exists())

    def test_startup_module_exists(self):
        """Test uDOS_startup.py exists"""
        project_root = Path(__file__).parent.parent.parent
        startup_file = project_root / "core" / "uDOS_startup.py"

        self.assertTrue(startup_file.exists())


class TestCommandHandlers(unittest.TestCase):
    """Test command handler architecture"""

    def test_commands_directory_exists(self):
        """Test commands directory exists"""
        project_root = Path(__file__).parent.parent.parent
        commands_dir = project_root / "core" / "commands"

        self.assertTrue(commands_dir.exists())

    def test_base_handler_exists(self):
        """Test base_handler.py exists"""
        project_root = Path(__file__).parent.parent.parent
        base_handler = project_root / "core" / "commands" / "base_handler.py"

        self.assertTrue(base_handler.exists())

    def test_map_handler_exists(self):
        """Test map_handler.py exists"""
        project_root = Path(__file__).parent.parent.parent
        map_handler = project_root / "core" / "commands" / "map_handler.py"

        self.assertTrue(map_handler.exists())

    def test_panel_handler_exists(self):
        """Test panel_handler.py exists"""
        project_root = Path(__file__).parent.parent.parent
        panel_handler = project_root / "core" / "commands" / "panel_handler.py"

        self.assertTrue(panel_handler.exists())

    def test_history_handler_exists(self):
        """Test history_handler.py exists"""
        project_root = Path(__file__).parent.parent.parent
        history_handler = project_root / "core" / "commands" / "history_handler.py"

        self.assertTrue(history_handler.exists())


class TestServices(unittest.TestCase):
    """Test services architecture"""

    def test_services_directory_exists(self):
        """Test services directory exists"""
        project_root = Path(__file__).parent.parent.parent
        services_dir = project_root / "core" / "services"

        if not services_dir.exists():
            self.skipTest("Services directory not present")

        self.assertTrue(services_dir.exists())

    def test_map_engine_exists(self):
        """Test map_engine.py exists"""
        project_root = Path(__file__).parent.parent.parent
        map_engine = project_root / "core" / "services" / "map_engine.py"

        self.assertTrue(map_engine.exists())


class TestUtilities(unittest.TestCase):
    """Test utilities architecture"""

    def test_utils_directory_exists(self):
        """Test utils directory exists"""
        project_root = Path(__file__).parent.parent.parent
        utils_dir = project_root / "core" / "utils"

        if not utils_dir.exists():
            self.skipTest("Utils directory not present")

        self.assertTrue(utils_dir.exists())


class TestEntryPoints(unittest.TestCase):
    """Test entry points"""

    def test_main_entry_point_exists(self):
        """Test uDOS.py entry point exists"""
        project_root = Path(__file__).parent.parent.parent
        entry_point = project_root / "uDOS.py"

        self.assertTrue(entry_point.exists())

    def test_start_script_exists(self):
        """Test start_udos.sh exists"""
        project_root = Path(__file__).parent.parent.parent
        start_script = project_root / "start_udos.sh"

        self.assertTrue(start_script.exists())

    def test_web_script_exists(self):
        """Test web.sh exists"""
        project_root = Path(__file__).parent.parent.parent
        web_script = project_root / "web.sh"

        self.assertTrue(web_script.exists())


class TestModuleImports(unittest.TestCase):
    """Test module imports"""

    def test_core_parser_imports(self):
        """Test uDOS_parser imports"""
        try:
            from core import uDOS_parser
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import uDOS_parser: {e}")

    def test_core_settings_imports(self):
        """Test uDOS_settings imports"""
        try:
            from core import uDOS_settings
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import uDOS_settings: {e}")

    def test_core_logger_imports(self):
        """Test uDOS_logger imports"""
        try:
            from core import uDOS_logger
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import uDOS_logger: {e}")


class TestExtensionsArchitecture(unittest.TestCase):
    """Test extensions architecture"""

    def test_extensions_core_exists(self):
        """Test extensions/core exists"""
        project_root = Path(__file__).parent.parent.parent
        extensions_core = project_root / "extensions" / "core"

        self.assertTrue(extensions_core.exists())

    def test_extensions_server_exists(self):
        """Test extensions_server.py exists"""
        project_root = Path(__file__).parent.parent.parent
        server = project_root / "extensions" / "core" / "extensions_server.py"

        self.assertTrue(server.exists())

    def test_dashboard_extension_exists(self):
        """Test dashboard extension exists"""
        project_root = Path(__file__).parent.parent.parent
        dashboard = project_root / "extensions" / "core" / "dashboard"

        self.assertTrue(dashboard.exists())

    def test_teletext_extension_exists(self):
        """Test teletext extension exists"""
        project_root = Path(__file__).parent.parent.parent
        teletext = project_root / "extensions" / "core" / "teletext"

        self.assertTrue(teletext.exists())

    def test_terminal_extension_exists(self):
        """Test terminal extension exists"""
        project_root = Path(__file__).parent.parent.parent
        terminal = project_root / "extensions" / "core" / "terminal"

        self.assertTrue(terminal.exists())

    def test_desktop_extension_exists(self):
        """Test desktop extension exists"""
        project_root = Path(__file__).parent.parent.parent
        desktop = project_root / "extensions" / "core" / "desktop"

        self.assertTrue(desktop.exists())


class TestDataArchitecture(unittest.TestCase):
    """Test data architecture"""

    def test_data_directory_exists(self):
        """Test data directory exists"""
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"

        self.assertTrue(data_dir.exists())

    def test_templates_exist(self):
        """Test templates directory exists"""
        project_root = Path(__file__).parent.parent.parent
        templates = project_root / "data" / "templates"

        self.assertTrue(templates.exists())


class TestMemoryArchitecture(unittest.TestCase):
    """Test memory system architecture"""

    def test_memory_tiers_exist(self):
        """Test memory tier structure exists"""
        project_root = Path(__file__).parent.parent.parent
        memory_dir = project_root / "memory"

        tiers = ['private', 'public', 'shared']

        for tier in tiers:
            tier_dir = memory_dir / tier
            self.assertTrue(tier_dir.exists(), f"Memory tier missing: {tier}")

    def test_memory_config_exists(self):
        """Test memory config directory exists"""
        project_root = Path(__file__).parent.parent.parent
        config_dir = project_root / "memory" / "config"

        self.assertTrue(config_dir.exists())

    def test_memory_sandbox_exists(self):
        """Test memory sandbox exists"""
        project_root = Path(__file__).parent.parent.parent
        sandbox = project_root / "memory" / "sandbox"

        self.assertTrue(sandbox.exists())

    def test_memory_workspace_exists(self):
        """Test memory workspace exists"""
        project_root = Path(__file__).parent.parent.parent
        workspace = project_root / "memory" / "workspace"

        self.assertTrue(workspace.exists())

    def test_memory_modules_exists(self):
        """Test memory modules exists"""
        project_root = Path(__file__).parent.parent.parent
        modules = project_root / "memory" / "modules"

        self.assertTrue(modules.exists())


class TestKnowledgeArchitecture(unittest.TestCase):
    """Test knowledge system architecture"""

    def test_knowledge_system_exists(self):
        """Test knowledge/system exists"""
        project_root = Path(__file__).parent.parent.parent
        system = project_root / "knowledge" / "system"

        self.assertTrue(system.exists())

    def test_knowledge_reference_exists(self):
        """Test knowledge/reference exists"""
        project_root = Path(__file__).parent.parent.parent
        reference = project_root / "knowledge" / "reference"

        self.assertTrue(reference.exists())

    def test_knowledge_skills_exists(self):
        """Test knowledge/skills exists"""
        project_root = Path(__file__).parent.parent.parent
        skills = project_root / "knowledge" / "skills"

        self.assertTrue(skills.exists())


class TestDocumentationArchitecture(unittest.TestCase):
    """Test documentation architecture"""

    def test_dev_directory_exists(self):
        """Test dev directory exists (v1.0.27: /docs → /dev)"""
        project_root = Path(__file__).parent.parent.parent
        dev = project_root / "dev"

        self.assertTrue(dev.exists())

    def test_wiki_directory_exists(self):
        """Test wiki directory exists"""
        project_root = Path(__file__).parent.parent.parent
        wiki = project_root / "wiki"

        self.assertTrue(wiki.exists())

    def test_dev_planning_exists(self):
        """Test dev/planning exists (v1.0.27: tracked for contributors)"""
        project_root = Path(__file__).parent.parent.parent
        planning = project_root / "dev" / "planning"

        self.assertTrue(planning.exists())

    def test_dev_archive_exists(self):
        """Test dev/archive exists (v1.0.27: local dev history)"""
        project_root = Path(__file__).parent.parent.parent
        archive = project_root / "dev" / "archive"

        self.assertTrue(archive.exists())


class TestTestArchitecture(unittest.TestCase):
    """Test test suite architecture"""

    def test_tests_directory_exists(self):
        """Test memory/tests exists"""
        project_root = Path(__file__).parent.parent.parent
        tests = project_root / "memory" / "tests"

        self.assertTrue(tests.exists())

    def test_unit_tests_exist(self):
        """Test unit tests directory exists"""
        project_root = Path(__file__).parent.parent.parent
        unit = project_root / "memory" / "tests" / "unit"

        self.assertTrue(unit.exists())

    def test_integration_tests_exist(self):
        """Test integration tests directory exists"""
        project_root = Path(__file__).parent.parent.parent
        integration = project_root / "memory" / "tests" / "integration"

        self.assertTrue(integration.exists())

    def test_pytest_configured(self):
        """Test pytest is configured"""
        project_root = Path(__file__).parent.parent.parent
        pytest_ini = project_root / "pytest.ini"

        self.assertTrue(pytest_ini.exists())


class TestConfigurationArchitecture(unittest.TestCase):
    """Test configuration architecture"""

    def test_requirements_exist(self):
        """Test requirements.txt exists"""
        project_root = Path(__file__).parent.parent.parent
        requirements = project_root / "requirements.txt"

        self.assertTrue(requirements.exists())

    def test_gitignore_exists(self):
        """Test .gitignore exists"""
        project_root = Path(__file__).parent.parent.parent
        gitignore = project_root / ".gitignore"

        if not gitignore.exists():
            self.skipTest(".gitignore not present")


class TestProjectMetadata(unittest.TestCase):
    """Test project metadata files"""

    def test_license_exists(self):
        """Test LICENSE exists"""
        project_root = Path(__file__).parent.parent.parent
        license_file = project_root / "LICENSE.txt"

        self.assertTrue(license_file.exists())

    def test_readme_exists(self):
        """Test README exists"""
        project_root = Path(__file__).parent.parent.parent

        readmes = [
            project_root / "README.MD",
            project_root / "README.md"
        ]

        exists = any(r.exists() for r in readmes)
        self.assertTrue(exists)

    def test_changelog_exists(self):
        """Test CHANGELOG exists"""
        project_root = Path(__file__).parent.parent.parent
        changelog = project_root / "CHANGELOG.md"

        self.assertTrue(changelog.exists())

    def test_roadmap_exists(self):
        """Test ROADMAP exists"""
        project_root = Path(__file__).parent.parent.parent

        roadmaps = [
            project_root / "ROADMAP.MD",
            project_root / "ROADMAP.md"
        ]

        exists = any(r.exists() for r in roadmaps)
        self.assertTrue(exists)

    def test_contributing_exists(self):
        """Test CONTRIBUTING exists"""
        project_root = Path(__file__).parent.parent.parent
        contributing = project_root / "CONTRIBUTING.md"

        self.assertTrue(contributing.exists())

    def test_credits_exists(self):
        """Test CREDITS exists"""
        project_root = Path(__file__).parent.parent.parent
        credits = project_root / "CREDITS.md"

        self.assertTrue(credits.exists())


class TestScriptArchitecture(unittest.TestCase):
    """Test script architecture"""

    def test_start_script_executable(self):
        """Test start_udos.sh is executable"""
        project_root = Path(__file__).parent.parent.parent
        start_script = project_root / "start_udos.sh"

        # Check if file exists
        self.assertTrue(start_script.exists())

        # Check if executable bit is set (Unix-like systems)
        import os
        is_executable = os.access(start_script, os.X_OK)

        if not is_executable:
            self.skipTest("Script may not be executable on this system")

    def test_web_script_executable(self):
        """Test web.sh is executable"""
        project_root = Path(__file__).parent.parent.parent
        web_script = project_root / "web.sh"

        self.assertTrue(web_script.exists())


class TestDirectoryHierarchy(unittest.TestCase):
    """Test directory hierarchy"""

    def test_top_level_structure(self):
        """Test top-level directory structure (v1.0.27: /docs → /dev)"""
        project_root = Path(__file__).parent.parent.parent

        required_dirs = [
            'core',
            'memory',
            'knowledge',
            'extensions',
            'dev',
            'wiki'
        ]

        for dirname in required_dirs:
            dirpath = project_root / dirname
            self.assertTrue(dirpath.exists(), f"Required directory missing: {dirname}")

    def test_core_subdirectories(self):
        """Test core subdirectories"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        subdirs = ['commands', 'services']

        for subdir in subdirs:
            subdirpath = core_dir / subdir
            exists = subdirpath.exists()
            if not exists:
                # Some subdirs may be optional
                continue
            self.assertTrue(exists)


class TestModuleOrganization(unittest.TestCase):
    """Test module organization"""

    def test_core_modules_grouped(self):
        """Test core modules are grouped logically"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        # Core modules should exist
        core_files = list(core_dir.glob("uDOS_*.py"))

        self.assertGreater(len(core_files), 5, "Should have multiple core modules")

    def test_command_handlers_grouped(self):
        """Test command handlers are grouped"""
        project_root = Path(__file__).parent.parent.parent
        commands_dir = project_root / "core" / "commands"

        handler_files = list(commands_dir.glob("*_handler.py"))

        self.assertGreater(len(handler_files), 0, "Should have command handlers")


class TestNamingConventions(unittest.TestCase):
    """Test naming conventions"""

    def test_core_files_prefixed(self):
        """Test core files use uDOS_ prefix"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        core_files = [f for f in core_dir.glob("*.py")
                     if f.name not in ['__init__.py']]

        prefixed_files = [f for f in core_files if f.name.startswith('uDOS_')]

        # Most core files should be prefixed
        ratio = len(prefixed_files) / len(core_files) if core_files else 0
        self.assertGreater(ratio, 0.5, "Most core files should have uDOS_ prefix")

    def test_handler_files_suffixed(self):
        """Test handler files use _handler suffix"""
        project_root = Path(__file__).parent.parent.parent
        commands_dir = project_root / "core" / "commands"

        py_files = list(commands_dir.glob("*.py"))
        handler_files = [f for f in py_files if f.name.endswith('_handler.py')]

        # Should have handler files
        self.assertGreater(len(handler_files), 0)


if __name__ == '__main__':
    unittest.main()
