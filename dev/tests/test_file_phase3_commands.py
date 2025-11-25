"""
Phase 3 FILE Command Tests (v1.0.29)

Tests for FILE BATCH, FILE BOOKMARKS, and FILE PREVIEW commands.

Author: uDOS Development Team
Version: 1.0.29
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestFileBatchCommand(unittest.TestCase):
    """Test FILE BATCH command functionality"""

    def test_batch_command_exists_in_json(self):
        """Test FILE BATCH command is documented in commands.json"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for FILE BATCH
        batch_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE BATCH'), None)
        self.assertIsNotNone(batch_cmd, "FILE BATCH command should be documented")

    def test_batch_has_proper_syntax(self):
        """Test FILE BATCH has correct syntax definition"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        batch_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE BATCH'), None)

        if batch_cmd:
            syntax = batch_cmd.get('SYNTAX', '')
            self.assertIn('DELETE', syntax)
            self.assertIn('COPY', syntax)
            self.assertIn('MOVE', syntax)

    def test_batch_handler_method_exists(self):
        """Test _handle_batch method exists in FileCommandHandler"""
        try:
            from core.commands.file_handler import FileCommandHandler
            handler = FileCommandHandler()
            self.assertTrue(hasattr(handler, '_handle_batch'))
        except ImportError:
            self.skipTest("FileCommandHandler not available")

    def test_batch_examples_provided(self):
        """Test FILE BATCH has examples"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        batch_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE BATCH'), None)

        if batch_cmd:
            examples = batch_cmd.get('EXAMPLES', [])
            self.assertGreater(len(examples), 0, "FILE BATCH should have examples")


class TestFileBookmarksCommand(unittest.TestCase):
    """Test FILE BOOKMARKS command functionality"""

    def test_bookmarks_command_exists_in_json(self):
        """Test FILE BOOKMARKS command is documented in commands.json"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for FILE BOOKMARKS
        bookmarks_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE BOOKMARKS'), None)
        self.assertIsNotNone(bookmarks_cmd, "FILE BOOKMARKS command should be documented")

    def test_bookmarks_has_proper_syntax(self):
        """Test FILE BOOKMARKS has correct syntax definition"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        bookmarks_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE BOOKMARKS'), None)

        if bookmarks_cmd:
            syntax = bookmarks_cmd.get('SYNTAX', '')
            self.assertIn('ADD', syntax)
            self.assertIn('REMOVE', syntax)

    def test_bookmarks_handler_method_exists(self):
        """Test _handle_bookmarks method exists in FileCommandHandler"""
        try:
            from core.commands.file_handler import FileCommandHandler
            handler = FileCommandHandler()
            self.assertTrue(hasattr(handler, '_handle_bookmarks'))
        except ImportError:
            self.skipTest("FileCommandHandler not available")

    def test_bookmarks_examples_provided(self):
        """Test FILE BOOKMARKS has examples"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        bookmarks_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE BOOKMARKS'), None)

        if bookmarks_cmd:
            examples = bookmarks_cmd.get('EXAMPLES', [])
            self.assertGreater(len(examples), 0, "FILE BOOKMARKS should have examples")


class TestFilePreviewCommand(unittest.TestCase):
    """Test FILE PREVIEW command functionality"""

    def test_preview_command_exists_in_json(self):
        """Test FILE PREVIEW command is documented in commands.json"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Look for FILE PREVIEW
        preview_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE PREVIEW'), None)
        self.assertIsNotNone(preview_cmd, "FILE PREVIEW command should be documented")

    def test_preview_has_proper_syntax(self):
        """Test FILE PREVIEW has correct syntax definition"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        preview_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE PREVIEW'), None)

        if preview_cmd:
            syntax = preview_cmd.get('SYNTAX', '')
            self.assertIn('<filename>', syntax)

    def test_preview_handler_method_exists(self):
        """Test _handle_preview method exists in FileCommandHandler"""
        try:
            from core.commands.file_handler import FileCommandHandler
            handler = FileCommandHandler()
            self.assertTrue(hasattr(handler, '_handle_preview'))
        except ImportError:
            self.skipTest("FileCommandHandler not available")

    def test_preview_examples_provided(self):
        """Test FILE PREVIEW has examples"""
        import json
        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])
        preview_cmd = next((cmd for cmd in commands if cmd.get('NAME') == 'FILE PREVIEW'), None)

        if preview_cmd:
            examples = preview_cmd.get('EXAMPLES', [])
            self.assertGreater(len(examples), 0, "FILE PREVIEW should have examples")


class TestFileCommandsIntegration(unittest.TestCase):
    """Test FILE commands work together"""

    def test_all_phase3_commands_in_handler(self):
        """Test all Phase 3 FILE commands are implemented"""
        try:
            from core.commands.file_handler import FileCommandHandler
            handler = FileCommandHandler()

            # Check all three Phase 3 commands have handlers
            self.assertTrue(hasattr(handler, '_handle_batch'))
            self.assertTrue(hasattr(handler, '_handle_bookmarks'))
            self.assertTrue(hasattr(handler, '_handle_preview'))

        except ImportError:
            self.skipTest("FileCommandHandler not available")

    def test_commands_routed_properly(self):
        """Test FILE commands are routed to correct handlers"""
        try:
            from core.commands.file_handler import FileCommandHandler
            import inspect

            handler = FileCommandHandler()

            # Check the handle method routes these commands
            source = inspect.getsource(handler.handle)

            self.assertIn('BATCH', source)
            self.assertIn('BOOKMARKS', source)
            self.assertIn('PREVIEW', source)

        except ImportError:
            self.skipTest("FileCommandHandler not available")


if __name__ == '__main__':
    unittest.main()
