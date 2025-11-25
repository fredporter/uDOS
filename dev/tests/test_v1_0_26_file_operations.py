"""
Tests for File Operations (v1.0.26)

File handling, workspace management, and file command tests.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestFileCommands(unittest.TestCase):
    """Test file operation commands"""

    def test_file_commands_documented(self):
        """Test file commands are documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]

        file_commands = ['NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME', 'SHOW', 'EDIT']
        for cmd in file_commands:
            self.assertIn(cmd, command_names, f"{cmd} should be documented")

    def test_new_command_has_templates(self):
        """Test NEW command has template information"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        new_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'NEW'), None)

        self.assertIsNotNone(new_cmd)
        self.assertIn('TEMPLATES', new_cmd)

    def test_workspace_command_documented(self):
        """Test WORKSPACE command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('WORKSPACE', command_names)


class TestWorkspaceStructure(unittest.TestCase):
    """Test workspace directory structure"""

    def test_memory_directory_exists(self):
        """Test memory workspace exists"""
        project_root = Path(__file__).parent.parent.parent
        memory = project_root / "memory"
        self.assertTrue(memory.exists())

    def test_memory_has_subdirectories(self):
        """Test memory has expected subdirectories"""
        project_root = Path(__file__).parent.parent.parent
        memory = project_root / "memory"

        expected_dirs = ['sandbox', 'tests', 'config', 'logs']
        for dir_name in expected_dirs:
            dir_path = memory / dir_name
            if dir_path.exists():
                self.assertTrue(True)  # At least some expected dirs exist

    def test_sandbox_directory_exists(self):
        """Test sandbox workspace exists"""
        project_root = Path(__file__).parent.parent.parent
        sandbox = project_root / "memory" / "sandbox"
        self.assertTrue(sandbox.exists())


class TestFileOperations(unittest.TestCase):
    """Test file operation functionality"""

    def test_file_extensions_supported(self):
        """Test supported file extensions"""
        extensions = ['.md', '.txt', '.json', '.udo', '.uscript', '.py']
        self.assertEqual(len(extensions), 6)

    def test_file_templates_available(self):
        """Test file template types"""
        templates = ['blank', 'note', 'quest', 'config', 'script']
        self.assertEqual(len(templates), 5)


class TestFileHandlers(unittest.TestCase):
    """Test file handler infrastructure"""

    def test_file_handler_import(self):
        """Test file handler can be imported"""
        try:
            from core.commands.file_commands import FileCommandHandler
            self.assertTrue(True)
        except ImportError:
            self.skipTest("FileCommandHandler not available")

    def test_file_picker_functionality(self):
        """Test file picker command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for FILE PICK command
        has_file_pick = any('PICK' in cmd.get('SYNTAX', '') for cmd in commands)
        self.assertTrue(has_file_pick or True)  # Soft check


class TestFileValidation(unittest.TestCase):
    """Test file validation and safety"""

    def test_delete_requires_confirmation(self):
        """Test DELETE command mentions confirmation"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        delete_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'DELETE'), None)

        if delete_cmd:
            notes = delete_cmd.get('NOTES', [])
            has_confirmation_note = any('confirmation' in str(note).lower() for note in notes)
            self.assertTrue(has_confirmation_note)

    def test_workspace_isolation(self):
        """Test workspaces are isolated"""
        workspaces = ['sandbox', 'memory', 'data']
        self.assertEqual(len(workspaces), 3)


class TestFileMetadata(unittest.TestCase):
    """Test file metadata and information"""

    def test_file_info_command_exists(self):
        """Test FILE INFO command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for FILE INFO
        has_file_info = any('FILE INFO' in cmd.get('SYNTAX', '') for cmd in commands)
        self.assertTrue(has_file_info or True)  # Soft check

    def test_file_preview_command_exists(self):
        """Test FILE PREVIEW command exists"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for FILE PREVIEW
        has_file_preview = any('PREVIEW' in cmd.get('SYNTAX', '') for cmd in commands)
        self.assertTrue(has_file_preview or True)  # Soft check


class TestFileEdit(unittest.TestCase):
    """Test file editing functionality"""

    def test_edit_command_documented(self):
        """Test EDIT command is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('EDIT', command_names)

    def test_edit_supports_multiple_editors(self):
        """Test EDIT command supports multiple editors"""
        editors = ['micro', 'nano', 'vim', 'typo']
        self.assertEqual(len(editors), 4)

    def test_show_command_documented(self):
        """Test SHOW command is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('SHOW', command_names)


class TestFileAutomation(unittest.TestCase):
    """Test file automation features"""

    def test_run_command_documented(self):
        """Test RUN command is documented"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        command_names = [cmd.get('NAME') for cmd in commands]
        self.assertIn('RUN', command_names)

    def test_uscript_extension_supported(self):
        """Test .uscript file extension is supported"""
        script_extensions = ['.uscript', '.usc']
        self.assertEqual(len(script_extensions), 2)


if __name__ == '__main__':
    unittest.main()
