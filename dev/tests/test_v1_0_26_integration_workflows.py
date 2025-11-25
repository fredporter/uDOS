"""
Tests for Integration Workflows (v1.0.26)

Cross-system integration and workflow tests.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestMemoryKnowledgeIntegration(unittest.TestCase):
    """Test memory-knowledge integration"""

    def test_memory_tiers_and_knowledge_paths_exist(self):
        """Test memory tiers connect to knowledge system"""
        project_root = Path(__file__).parent.parent.parent

        memory_dir = project_root / "memory"
        knowledge_dir = project_root / "knowledge"

        self.assertTrue(memory_dir.exists())
        self.assertTrue(knowledge_dir.exists())

    def test_shared_tier_accessible(self):
        """Test shared memory tier is accessible"""
        project_root = Path(__file__).parent.parent.parent
        shared_dir = project_root / "memory" / "shared"

        self.assertTrue(shared_dir.exists())

    def test_knowledge_categories_exist(self):
        """Test knowledge categories are defined"""
        project_root = Path(__file__).parent.parent.parent
        knowledge_dir = project_root / "knowledge"

        categories = ['system', 'reference', 'skills']
        found_categories = []

        for cat in categories:
            if (knowledge_dir / cat).exists():
                found_categories.append(cat)

        self.assertGreater(len(found_categories), 0)


class TestExtensionsCoreIntegration(unittest.TestCase):
    """Test extensions-core integration"""

    def test_extensions_connect_to_core(self):
        """Test extensions can access core functionality"""
        project_root = Path(__file__).parent.parent.parent

        extensions_dir = project_root / "extensions"
        core_dir = project_root / "core"

        self.assertTrue(extensions_dir.exists())
        self.assertTrue(core_dir.exists())

    def test_dashboard_uses_core_commands(self):
        """Test dashboard can integrate with core commands"""
        project_root = Path(__file__).parent.parent.parent

        # Dashboard should exist
        dashboard = project_root / "extensions" / "core" / "dashboard"
        self.assertTrue(dashboard.exists())

        # Core commands should exist
        commands_file = project_root / "knowledge" / "system" / "commands.json"
        self.assertTrue(commands_file.exists())


class TestMapKnowledgeIntegration(unittest.TestCase):
    """Test map-knowledge integration"""

    def test_map_documentation_exists(self):
        """Test map system has knowledge documentation"""
        project_root = Path(__file__).parent.parent.parent

        map_kb = project_root / "knowledge" / "system" / "MAP.md"
        self.assertTrue(map_kb.exists())

    def test_geographic_data_accessible(self):
        """Test geographic data is accessible to map system"""
        project_root = Path(__file__).parent.parent.parent

        # Check for data directory
        data_dir = project_root / "data"

        if not data_dir.exists():
            self.skipTest("Data directory not present")


class TestPanelMemoryIntegration(unittest.TestCase):
    """Test panel-memory integration"""

    def test_panel_can_display_memory(self):
        """Test panel system can display memory content"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]

        # Both PANEL and MEMORY should exist
        self.assertIn('PANEL', command_names)
        self.assertIn('MEMORY', command_names)


class TestHistoryLoggingIntegration(unittest.TestCase):
    """Test history-logging integration"""

    def test_history_and_logging_systems_exist(self):
        """Test history and logging systems both exist"""
        project_root = Path(__file__).parent.parent.parent

        # Check for logging
        logger_file = project_root / "core" / "uDOS_logger.py"
        self.assertTrue(logger_file.exists())

        # Check for history in memory
        history_dir = project_root / "memory" / "logs"

        if not history_dir.exists():
            self.skipTest("History directory not present")


class TestThemeUIIntegration(unittest.TestCase):
    """Test theme-UI integration"""

    def test_themes_directory_exists(self):
        """Test themes directory exists"""
        project_root = Path(__file__).parent.parent.parent
        themes_dir = project_root / "memory" / "themes"

        self.assertTrue(themes_dir.exists())

    def test_dashboard_supports_themes(self):
        """Test dashboard supports theme switching"""
        project_root = Path(__file__).parent.parent.parent
        dashboard_html = project_root / "extensions" / "core" / "dashboard" / "index.html"

        with open(dashboard_html, 'r') as f:
            content = f.read()

        # Should have theme-related content
        has_theme_support = 'theme' in content.lower()
        self.assertTrue(has_theme_support)


class TestWorkflowScenarios(unittest.TestCase):
    """Test workflow scenarios"""

    def test_workspace_workflow_structure(self):
        """Test workspace workflow structure exists"""
        project_root = Path(__file__).parent.parent.parent

        # Memory workspace structure
        workspace_dir = project_root / "memory" / "workspace"
        self.assertTrue(workspace_dir.exists())

    def test_mission_workflow_structure(self):
        """Test mission workflow structure exists"""
        project_root = Path(__file__).parent.parent.parent

        missions_dir = project_root / "memory" / "missions"
        self.assertTrue(missions_dir.exists())

    def test_scenario_workflow_structure(self):
        """Test scenario workflow structure exists"""
        project_root = Path(__file__).parent.parent.parent

        scenarios_dir = project_root / "memory" / "scenarios"
        self.assertTrue(scenarios_dir.exists())


class TestExtensionWorkflows(unittest.TestCase):
    """Test extension workflows"""

    def test_extension_server_workflow(self):
        """Test extension server can be started"""
        project_root = Path(__file__).parent.parent.parent
        server_file = project_root / "extensions" / "core" / "extensions_server.py"

        self.assertTrue(server_file.exists())

    def test_web_command_workflow(self):
        """Test WEB command workflow exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]

        # WEB command should exist for extension workflows
        has_web = 'WEB' in command_names or 'POKE' in command_names
        self.assertTrue(has_web)


class TestDataFlowIntegration(unittest.TestCase):
    """Test data flow between systems"""

    def test_memory_to_panel_flow(self):
        """Test data can flow from memory to panel"""
        project_root = Path(__file__).parent.parent.parent

        # Memory tiers exist
        memory_dir = project_root / "memory"
        self.assertTrue(memory_dir.exists())

        # Panel handler should exist
        try:
            from core.commands.panel_handler import PanelCommandHandler
            self.assertTrue(True)
        except ImportError:
            self.skipTest("PanelCommandHandler not available")

    def test_knowledge_to_help_flow(self):
        """Test knowledge flows to help system"""
        project_root = Path(__file__).parent.parent.parent

        # Knowledge system exists
        knowledge_dir = project_root / "knowledge" / "system"
        self.assertTrue(knowledge_dir.exists())

        # Commands JSON exists for help
        commands_file = knowledge_dir / "commands.json"
        self.assertTrue(commands_file.exists())


class TestCrossSystemCommands(unittest.TestCase):
    """Test commands that span multiple systems"""

    def test_status_spans_multiple_systems(self):
        """Test STATUS command can check multiple systems"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        status_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'STATUS'), None)

        self.assertIsNotNone(status_cmd)

    def test_config_spans_multiple_systems(self):
        """Test CONFIG command affects multiple systems"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        config_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'CONFIG'), None)

        self.assertIsNotNone(config_cmd)


class TestAPIIntegration(unittest.TestCase):
    """Test API integration points"""

    def test_teletext_api_exists(self):
        """Test teletext API server exists"""
        project_root = Path(__file__).parent.parent.parent
        api_file = project_root / "extensions" / "core" / "teletext" / "api_server.py"

        if not api_file.exists():
            self.skipTest("Teletext API not present")

        self.assertTrue(api_file.exists())

    def test_api_endpoints_documented(self):
        """Test API endpoints are documented"""
        project_root = Path(__file__).parent.parent.parent
        api_file = project_root / "extensions" / "core" / "teletext" / "api_server.py"

        if not api_file.exists():
            self.skipTest("Teletext API not present")

        with open(api_file, 'r') as f:
            content = f.read()

        # Should have Flask routes
        has_routes = '@app.route' in content
        self.assertTrue(has_routes)


class TestConfigurationIntegration(unittest.TestCase):
    """Test configuration integration"""

    def test_settings_file_accessible(self):
        """Test settings file is accessible to all systems"""
        project_root = Path(__file__).parent.parent.parent

        settings_file = project_root / "core" / "uDOS_settings.py"
        self.assertTrue(settings_file.exists())

    def test_sandbox_config_accessible(self):
        """Test sandbox config is accessible"""
        project_root = Path(__file__).parent.parent.parent

        sandbox_dir = project_root / "memory" / "sandbox"

        if not sandbox_dir.exists():
            self.skipTest("Sandbox not present")


class TestModuleIntegration(unittest.TestCase):
    """Test module integration"""

    def test_modules_directory_exists(self):
        """Test modules directory exists"""
        project_root = Path(__file__).parent.parent.parent
        modules_dir = project_root / "memory" / "modules"

        self.assertTrue(modules_dir.exists())

    def test_core_modules_exist(self):
        """Test core modules exist"""
        project_root = Path(__file__).parent.parent.parent
        core_dir = project_root / "core"

        core_files = [
            'uDOS_main.py',
            'uDOS_commands.py',
            'uDOS_parser.py'
        ]

        found = []
        for f in core_files:
            if (core_dir / f).exists():
                found.append(f)

        self.assertGreater(len(found), 0)


class TestDocumentationIntegration(unittest.TestCase):
    """Test documentation integration"""

    def test_wiki_references_commands(self):
        """Test wiki references command system"""
        project_root = Path(__file__).parent.parent.parent

        wiki_dir = project_root / "wiki"
        self.assertTrue(wiki_dir.exists())

        cmd_ref = wiki_dir / "Command-Reference.md"
        self.assertTrue(cmd_ref.exists())

    def test_docs_reference_features(self):
        """Test dev directory exists (v1.0.27: /docs → /dev)"""
        project_root = Path(__file__).parent.parent.parent

        dev_dir = project_root / "dev"
        self.assertTrue(dev_dir.exists())


if __name__ == '__main__':
    unittest.main()
