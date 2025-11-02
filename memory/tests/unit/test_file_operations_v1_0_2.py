#!/usr/bin/env python3
"""
uDOS v1.0.2 File Operations Test Framework

Comprehensive testing for all FILE commands:
NEW, DELETE, COPY, MOVE, RENAME, SHOW, EDIT, RUN

Tests both interactive and non-interactive modes with mock environment.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add uDOS core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from commands.file_handler import FileCommandHandler


class MockInteractivePrompt:
    """Mock interactive prompt for testing."""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_count = {}

    def ask_text(self, prompt, default=None):
        """Mock text input."""
        key = f"ask_text_{prompt}"
        self.call_count[key] = self.call_count.get(key, 0) + 1
        return self.responses.get(key, default)

    def ask_choice(self, prompt, choices, default=None):
        """Mock choice selection."""
        key = f"ask_choice_{prompt}"
        self.call_count[key] = self.call_count.get(key, 0) + 1
        return self.responses.get(key, default)

    def ask_yes_no(self, prompt, default=False):
        """Mock yes/no confirmation."""
        key = f"ask_yes_no_{prompt}"
        self.call_count[key] = self.call_count.get(key, 0) + 1
        return self.responses.get(key, default)


class MockWorkspaceManager:
    """Mock workspace manager for testing."""

    def __init__(self, temp_dir):
        self.temp_dir = Path(temp_dir)
        self.current_workspace = 'sandbox'
        self.workspaces = {
            'sandbox': {'path': 'sandbox', 'description': 'Test sandbox'},
            'memory': {'path': 'memory', 'description': 'Test memory'},
            'data': {'path': 'data', 'description': 'Test data'}
        }
        self.TEMPLATES = {
            'blank': {'name': 'Blank', 'extension': '.md', 'content': '# Test\n'},
            'note': {'name': 'Note', 'extension': '.md', 'content': '# Note\n{date}\n'}
        }
        self._setup_dirs()

    def _setup_dirs(self):
        """Create test directories."""
        for workspace in self.workspaces.values():
            (self.temp_dir / workspace['path']).mkdir(exist_ok=True)

    def list_workspaces(self):
        """List available workspaces."""
        return {name: {**config, 'file_count': 0, 'current': name == self.current_workspace}
                for name, config in self.workspaces.items()}

    def list_files(self, workspace=None):
        """List files in workspace."""
        ws_path = self.get_workspace_path(workspace)
        return [f.name for f in ws_path.glob('*') if f.is_file()]

    def get_workspace_path(self, workspace=None):
        """Get workspace path."""
        ws = workspace or self.current_workspace
        return self.temp_dir / self.workspaces[ws]['path']

    def create_file(self, workspace, filename, template):
        """Create test file."""
        ws_path = self.get_workspace_path(workspace)
        file_path = ws_path / filename

        if file_path.exists():
            raise FileExistsError(f"File exists: {filename}")

        content = self.TEMPLATES[template]['content']
        content = content.replace('{date}', '2025-11-02')
        file_path.write_text(content)
        return file_path

    def delete_file(self, filename, workspace=None):
        """Delete test file."""
        ws_path = self.get_workspace_path(workspace)
        file_path = ws_path / filename

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        file_path.unlink()
        return True

    def copy_file(self, source, destination, dest_workspace=None):
        """Copy test file."""
        src_path = self.get_workspace_path() / source
        dest_path = self.get_workspace_path(dest_workspace) / destination

        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        if dest_path.exists():
            raise FileExistsError(f"Destination exists: {destination}")

        shutil.copy2(src_path, dest_path)
        return dest_path

    def move_file(self, source, dest_workspace, destination):
        """Move test file."""
        src_path = self.get_workspace_path() / source
        dest_path = self.get_workspace_path(dest_workspace) / destination

        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        if dest_path.exists():
            raise FileExistsError(f"Destination exists: {destination}")

        shutil.move(src_path, dest_path)
        return dest_path

    def rename_file(self, old_name, new_name, workspace=None):
        """Rename test file."""
        ws_path = self.get_workspace_path(workspace)
        old_path = ws_path / old_name
        new_path = ws_path / new_name

        if not old_path.exists():
            raise FileNotFoundError(f"File not found: {old_name}")

        if new_path.exists():
            raise FileExistsError(f"File exists: {new_name}")

        old_path.rename(new_path)
        return new_path


class MockEditorManager:
    """Mock editor manager for testing."""

    def edit_file(self, file_path, mode=None, editor=None):
        """Mock file editing."""
        return f"✅ Mock edit: {file_path} (mode: {mode}, editor: {editor})"


class FileOperationsTestFramework:
    """Comprehensive test framework for FILE operations."""

    def __init__(self):
        self.temp_dir = None
        self.handler = None
        self.mock_prompt = None
        self.test_results = []

    def setup(self):
        """Set up test environment."""
        print("🔧 Setting up test environment...")

        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix="udos_file_test_")
        print(f"   📁 Test directory: {self.temp_dir}")

        # Create mock handler
        self.handler = FileCommandHandler()
        self.handler._workspace_manager = MockWorkspaceManager(self.temp_dir)
        self.handler._editor_manager = MockEditorManager()

        # Create test files
        self._create_test_files()

        print("✅ Test environment ready")

    def teardown(self):
        """Clean up test environment."""
        print("🧹 Cleaning up test environment...")
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        print("✅ Cleanup complete")

    def _create_test_files(self):
        """Create test files for testing."""
        sandbox_path = Path(self.temp_dir) / 'sandbox'
        memory_path = Path(self.temp_dir) / 'memory'

        # Create test files in sandbox
        (sandbox_path / 'test_file.md').write_text("# Test File\nContent here\n")
        (sandbox_path / 'script.uscript').write_text("# Test Script\nHELP\n")
        (sandbox_path / 'data.json').write_text('{"test": "data"}\n')

        # Create test files in memory
        (memory_path / 'archive.md').write_text("# Archive\nOld content\n")
        (memory_path / 'notes.txt').write_text("Important notes\n")

    def run_test(self, test_name, test_func):
        """Run a single test and record result."""
        print(f"\n🧪 Running test: {test_name}")
        try:
            result = test_func()
            self.test_results.append({'name': test_name, 'status': 'PASS', 'result': result})
            print(f"✅ {test_name} - PASSED")
            return True
        except Exception as e:
            self.test_results.append({'name': test_name, 'status': 'FAIL', 'error': str(e)})
            print(f"❌ {test_name} - FAILED: {e}")
            return False

    def test_new_command(self):
        """Test NEW command with various scenarios."""
        # Test with parameters
        with patch('core.uDOS_interactive.InteractivePrompt') as mock_prompt_class:
            mock_prompt = MockInteractivePrompt({
                'ask_text_📄 File name': 'test_new.md',
                'ask_choice_📁 Workspace': 'sandbox - Test sandbox',
                'ask_choice_📝 Template': 'blank - Blank'
            })
            mock_prompt_class.return_value = mock_prompt

            result = self.handler._handle_new(['test_new.md'])

            # Check file was created
            test_file = Path(self.temp_dir) / 'sandbox' / 'test_new.md'
            if not test_file.exists():
                raise AssertionError("File was not created")

            return result

    def test_delete_command(self):
        """Test DELETE command with confirmation."""
        # Create a file to delete
        test_file = Path(self.temp_dir) / 'sandbox' / 'to_delete.md'
        test_file.write_text("Delete me")

        with patch('core.uDOS_interactive.InteractivePrompt') as mock_prompt_class:
            mock_prompt = MockInteractivePrompt({
                'ask_choice_🗑️  Delete file': 'to_delete.md',
                'ask_yes_no_⚠️  Delete to_delete.md? This cannot be undone!': True
            })
            mock_prompt_class.return_value = mock_prompt

            result = self.handler._handle_delete([])

            # Check file was deleted
            if test_file.exists():
                raise AssertionError("File was not deleted")

            return result

    def test_copy_command(self):
        """Test COPY command between workspaces."""
        with patch('core.uDOS_interactive.InteractivePrompt') as mock_prompt_class:
            mock_prompt = MockInteractivePrompt({
                'ask_choice_📄 Source file': 'test_file.md',
                'ask_text_📄 Destination name': 'copy_of_test.md',
                'ask_choice_📁 Destination workspace': 'memory'
            })
            mock_prompt_class.return_value = mock_prompt

            result = self.handler._handle_copy([])

            # Check file was copied
            copy_file = Path(self.temp_dir) / 'memory' / 'copy_of_test.md'
            if not copy_file.exists():
                raise AssertionError("File was not copied")

            return result

    def test_move_command(self):
        """Test MOVE command between workspaces."""
        # Create a file to move
        move_file = Path(self.temp_dir) / 'sandbox' / 'to_move.md'
        move_file.write_text("Move me")

        with patch('core.uDOS_interactive.InteractivePrompt') as mock_prompt_class:
            mock_prompt = MockInteractivePrompt({
                'ask_choice_📄 File to move': 'to_move.md',
                'ask_choice_📁 Move to workspace': 'memory',
                'ask_text_📄 New name (optional)': 'moved_file.md'
            })
            mock_prompt_class.return_value = mock_prompt

            result = self.handler._handle_move([])

            # Check file was moved
            original_file = Path(self.temp_dir) / 'sandbox' / 'to_move.md'
            moved_file = Path(self.temp_dir) / 'memory' / 'moved_file.md'

            if original_file.exists():
                raise AssertionError("Original file still exists")
            if not moved_file.exists():
                raise AssertionError("File was not moved to destination")

            return result

    def test_rename_command(self):
        """Test RENAME command within workspace."""
        # Create a file to rename
        rename_file = Path(self.temp_dir) / 'sandbox' / 'to_rename.md'
        rename_file.write_text("Rename me")

        with patch('core.uDOS_interactive.InteractivePrompt') as mock_prompt_class:
            mock_prompt = MockInteractivePrompt({
                'ask_choice_📄 File to rename': 'to_rename.md',
                'ask_text_📄 New name': 'renamed_file.md'
            })
            mock_prompt_class.return_value = mock_prompt

            result = self.handler._handle_rename([])

            # Check file was renamed
            original_file = Path(self.temp_dir) / 'sandbox' / 'to_rename.md'
            renamed_file = Path(self.temp_dir) / 'sandbox' / 'renamed_file.md'

            if original_file.exists():
                raise AssertionError("Original file still exists")
            if not renamed_file.exists():
                raise AssertionError("File was not renamed")

            return result

    def test_show_command(self):
        """Test SHOW command for displaying files."""
        result = self.handler._handle_show(['test_file.md'])

        if "# Test File" not in result:
            raise AssertionError("File content not displayed correctly")

        return result

    def test_edit_command(self):
        """Test EDIT command with mock editor."""
        result = self.handler._handle_edit(['test_file.md', '--cli'])

        if "Mock edit" not in result:
            raise AssertionError("Editor was not called")

        return result

    def test_run_command(self):
        """Test RUN command for scripts."""
        # Test with .uscript file
        with patch('core.uDOS_ucode.UCodeInterpreter') as mock_interpreter_class:
            mock_interpreter = Mock()
            mock_interpreter.execute_script.return_value = "Script executed successfully"
            mock_interpreter_class.return_value = mock_interpreter

            result = self.handler._handle_run(['script.uscript'], None)

            if "Script executed successfully" not in result:
                raise AssertionError("Script was not executed")

            return result

    def test_security_restrictions(self):
        """Test file access security restrictions."""
        # Try to access file outside allowed directories
        result = self.handler._handle_show(['/etc/passwd'])

        if "Access denied" not in result:
            raise AssertionError("Security restriction not enforced")

        return result

    def run_all_tests(self):
        """Run all FILE command tests."""
        print("=" * 80)
        print("🧪 uDOS v1.0.2 FILE OPERATIONS TEST FRAMEWORK")
        print("=" * 80)

        self.setup()

        tests = [
            ("NEW Command", self.test_new_command),
            ("DELETE Command", self.test_delete_command),
            ("COPY Command", self.test_copy_command),
            ("MOVE Command", self.test_move_command),
            ("RENAME Command", self.test_rename_command),
            ("SHOW Command", self.test_show_command),
            ("EDIT Command", self.test_edit_command),
            ("RUN Command", self.test_run_command),
            ("Security Restrictions", self.test_security_restrictions)
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
            else:
                failed += 1

        self.teardown()

        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {passed + failed}")

        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! FILE operations are working correctly.")
        else:
            print(f"\n⚠️  {failed} tests failed. Check the details above.")

        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{status_icon} {result['name']}: {result['status']}")
            if result['status'] == 'FAIL':
                print(f"   Error: {result['error']}")

        return failed == 0


if __name__ == "__main__":
    # Run the test framework
    framework = FileOperationsTestFramework()
    success = framework.run_all_tests()

    print("\n" + "=" * 80)
    print("🔬 v1.0.2 FILE OPERATIONS REVIEW COMPLETE")
    print("=" * 80)

    if success:
        print("✅ Ready to proceed with DEVELOPMENT phase")
    else:
        print("❌ Issues found - need to fix before development")

    sys.exit(0 if success else 1)
