"""
Tests for STATUS and VERSION commands (v1.0.26)

Core system information commands requiring test coverage.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.uDOS_startup import SystemHealth, check_system_health


class TestStatusCommand(unittest.TestCase):
    """Test STATUS command functionality"""

    def test_system_health_enum(self):
        """Test SystemHealth enum values"""
        self.assertEqual(SystemHealth.HEALTHY.value, "healthy")
        self.assertEqual(SystemHealth.DEGRADED.value, "degraded")
        self.assertEqual(SystemHealth.CRITICAL.value, "critical")

    def test_system_health_check_basic(self):
        """Test basic system health check"""
        health = check_system_health()
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)
        self.assertIn('issues', health)

    def test_system_health_status_values(self):
        """Test health status returns valid values"""
        health = check_system_health()
        valid_statuses = ['healthy', 'degraded', 'critical']
        self.assertIn(health['status'], valid_statuses)

    def test_system_health_issues_list(self):
        """Test issues is a list"""
        health = check_system_health()
        self.assertIsInstance(health['issues'], list)

    def test_system_health_when_healthy(self):
        """Test health check when system is healthy"""
        health = check_system_health()
        if health['status'] == 'healthy':
            self.assertEqual(len(health['issues']), 0)


class TestVersionCommand(unittest.TestCase):
    """Test VERSION command functionality"""

    def test_version_info_accessible(self):
        """Test that version information exists"""
        project_root = Path(__file__).parent.parent.parent
        
        # Check ROADMAP.MD exists as version source
        roadmap = project_root / "ROADMAP.MD"
        self.assertTrue(roadmap.exists())

    def test_roadmap_contains_version(self):
        """Test ROADMAP contains version info"""
        project_root = Path(__file__).parent.parent.parent
        roadmap = project_root / "ROADMAP.MD"
        
        with open(roadmap, 'r') as f:
            content = f.read()
        
        self.assertIn("v1.0", content)


class TestHelpCommand(unittest.TestCase):
    """Test HELP command functionality"""

    def test_commands_json_exists(self):
        """Test that commands.json exists"""
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"
        self.assertTrue(commands_file.exists(), "commands.json should exist")

    def test_commands_json_valid(self):
        """Test commands.json is valid JSON"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"
        
        with open(commands_file, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, dict)
        self.assertIn('COMMANDS', data)

    def test_commands_is_list(self):
        """Test commands is a list"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"
        
        with open(commands_file, 'r') as f:
            data = json.load(f)
        
        commands = data.get('COMMANDS', [])
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)

    def test_commands_have_required_fields(self):
        """Test each command has required fields"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"
        
        with open(commands_file, 'r') as f:
            data = json.load(f)
        
        commands = data.get('COMMANDS', [])
        required_fields = ['NAME', 'SYNTAX', 'DESCRIPTION']
        
        for cmd in commands[:5]:  # Test first 5 commands
            for field in required_fields:
                self.assertIn(field, cmd)

    def test_core_commands_documented(self):
        """Test core commands are documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"
        
        with open(commands_file, 'r') as f:
            data = json.load(f)
        
        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        
        core_commands = ['HELP', 'STATUS', 'MAP']
        for cmd in core_commands:
            self.assertIn(cmd, command_names)


class TestBlankCommand(unittest.TestCase):
    """Test BLANK command functionality"""

    def test_blank_command_exists(self):
        """Test BLANK command is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"
        
        with open(commands_file, 'r') as f:
            data = json.load(f)
        
        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('BLANK', command_names)


if __name__ == '__main__':
    unittest.main()
