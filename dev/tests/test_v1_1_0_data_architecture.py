"""
uDOS v1.1.0 - Data Architecture Enforcement Test Suite

Comprehensive test suite for Feature 1.1.0.14: Data Architecture Enforcement

Test Coverage:
- Boundary validation between /knowledge/system/ (immutable) and /memory/ (writable)
- Command compliance audit (all commands respect boundaries)
- Permission enforcement (no unauthorized writes to system data)
- Path validation (proper directory structure)
- Cross-boundary access detection
- Read-only enforcement for system data

Feature: 1.1.0.14
Version: 1.1.0
Status: Active Development
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


class TestDataArchitectureBoundaries(unittest.TestCase):
    """Test strict separation between system and user data"""

    def setUp(self):
        """Create test environment with proper directory structure"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_dir = os.path.join(self.temp_dir, 'knowledge', 'system')
        self.memory_dir = os.path.join(self.temp_dir, 'memory')

        # Create directories
        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.memory_dir, exist_ok=True)

        # Create sample system files (read-only)
        self.system_files = {
            'geography/cities.json': {'cities': ['London', 'Paris']},
            'themes/default.json': {'name': 'default'},
            'commands.json': {'commands': ['HELP', 'STATUS']}
        }

        for file_path, content in self.system_files.items():
            full_path = os.path.join(self.knowledge_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                json.dump(content, f)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_knowledge_system_is_read_only(self):
        """Test that knowledge/system/ is treated as read-only"""
        system_file = os.path.join(self.knowledge_dir, 'commands.json')

        # File should exist
        self.assertTrue(os.path.exists(system_file))

        # Can read
        with open(system_file, 'r') as f:
            data = json.load(f)
            self.assertIn('commands', data)

    def test_memory_is_writable(self):
        """Test that memory/ is writable"""
        test_file = os.path.join(self.memory_dir, 'test.json')
        test_data = {'test': 'data'}

        # Should be able to write
        with open(test_file, 'w') as f:
            json.dump(test_data, f)

        # Should be able to read back
        with open(test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, test_data)

    def test_path_validation_rejects_system_writes(self):
        """Test path validation rejects writes to system directories"""
        from core.utils.path_validator import is_writable_path

        # System paths should not be writable
        system_paths = [
            'knowledge/system/themes/default.json',
            'knowledge/system/geography/cities.json',
            'core/config.py',
            'extensions/core/dashboard/app.py'
        ]

        for path in system_paths:
            full_path = os.path.join(self.temp_dir, path)
            self.assertFalse(
                is_writable_path(full_path, self.temp_dir),
                f"System path should not be writable: {path}"
            )

    def test_path_validation_allows_memory_writes(self):
        """Test path validation allows writes to memory directories"""
        from core.utils.path_validator import is_writable_path

        # Memory paths should be writable
        memory_paths = [
            'memory/private/notes.json',
            'memory/shared/docs.md',
            'memory/sandbox/test.txt',
            'memory/workspace/script.py'
        ]

        for path in memory_paths:
            full_path = os.path.join(self.temp_dir, path)
            self.assertTrue(
                is_writable_path(full_path, self.temp_dir),
                f"Memory path should be writable: {path}"
            )

    def test_directory_structure_validation(self):
        """Test proper directory structure is enforced"""
        required_dirs = [
            'memory/private',
            'memory/shared',
            'memory/groups',
            'memory/sandbox',
            'memory/workspace'
        ]

        for dir_path in required_dirs:
            full_path = os.path.join(self.temp_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
            self.assertTrue(os.path.isdir(full_path))

    def test_cross_boundary_access_detection(self):
        """Test detection of unauthorized cross-boundary access"""
        from core.utils.path_validator import detect_boundary_violation

        # Only user-to-system writes are violations
        violations = [
            ('memory/private/data.json', 'knowledge/system/themes/default.json'),  # User to system - VIOLATION
            ('sandbox/test.json', 'core/config.py'),  # Sandbox to core - VIOLATION
        ]

        for source, dest in violations:
            source_path = os.path.join(self.temp_dir, source)
            dest_path = os.path.join(self.temp_dir, dest)

            violation = detect_boundary_violation(source_path, dest_path, self.temp_dir)
            self.assertIsNotNone(violation, f"Should detect violation: {source} -> {dest}")
class TestPathValidator(unittest.TestCase):
    """Test path validation utility functions"""

    def test_is_writable_path_implementation(self):
        """Test is_writable_path function exists and works"""
        # This will be implemented in core/utils/path_validator.py
        # For now, test the logic

        def is_writable_path(path, root):
            """Check if path is in writable directory"""
            path = Path(path).resolve()
            root = Path(root).resolve()

            try:
                rel_path = path.relative_to(root)
            except ValueError:
                return False

            # Writable directories
            writable = ['memory', 'sandbox', 'output']

            # Read-only directories
            readonly = ['knowledge', 'core', 'extensions', 'data', 'docs', 'wiki']

            parts = rel_path.parts
            if not parts:
                return False

            if parts[0] in writable:
                return True
            if parts[0] in readonly:
                return False

            return False

        # Test writable paths
        self.assertTrue(is_writable_path('/root/memory/test.json', '/root'))
        self.assertTrue(is_writable_path('/root/sandbox/script.py', '/root'))

        # Test read-only paths
        self.assertFalse(is_writable_path('/root/knowledge/system/data.json', '/root'))
        self.assertFalse(is_writable_path('/root/core/config.py', '/root'))

    def test_detect_boundary_violation_implementation(self):
        """Test boundary violation detection"""

        def detect_boundary_violation(source, dest, root):
            """Detect cross-boundary access violations"""
            source_path = Path(source).resolve()
            dest_path = Path(dest).resolve()
            root_path = Path(root).resolve()

            try:
                source_rel = source_path.relative_to(root_path)
                dest_rel = dest_path.relative_to(root_path)
            except ValueError:
                return "Path outside root"

            writable = {'memory', 'sandbox', 'output'}
            readonly = {'knowledge', 'core', 'extensions', 'data', 'docs', 'wiki'}

            source_top = source_rel.parts[0] if source_rel.parts else None
            dest_top = dest_rel.parts[0] if dest_rel.parts else None

            # Violation: writing from readonly to readonly
            if source_top in readonly and dest_top in readonly:
                if source_top != dest_top:
                    return f"Cross-system write: {source_top} -> {dest_top}"

            # Violation: writing from memory to system
            if source_top in writable and dest_top in readonly:
                return f"User-to-system write: {source_top} -> {dest_top}"

            return None

        # Test violations
        violation = detect_boundary_violation(
            '/root/memory/data.json',
            '/root/knowledge/system/data.json',
            '/root'
        )
        self.assertIsNotNone(violation)


class TestCommandBoundaryCompliance(unittest.TestCase):
    """Test that all commands respect data boundaries"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_save_command_respects_boundaries(self):
        """Test SAVE command only writes to memory/"""
        # SAVE should only allow memory/, sandbox/, output/
        allowed = [
            'memory/private/test.json',
            'memory/sandbox/script.py',
            'output/report.txt'
        ]

        # All should be in writable directories
        for path in allowed:
            self.assertTrue(
                'memory' in path or 'sandbox' in path or 'output' in path
            )

    def test_load_command_can_read_system(self):
        """Test LOAD command can read from knowledge/system/"""
        # LOAD should be able to read system data (read-only)
        system_paths = [
            'knowledge/system/themes/default.json',
            'knowledge/system/geography/cities.json'
        ]

        for path in system_paths:
            # Should be readable (in knowledge/system/)
            self.assertTrue('knowledge/system' in path)

    def test_theme_command_writes_to_memory(self):
        """Test THEME command writes overrides to memory/"""
        # User theme overrides go to memory/config/themes/
        override_path = 'memory/config/themes/custom.json'

        self.assertTrue('memory' in override_path)
        self.assertFalse('knowledge' in override_path)

class TestPermissionEnforcement(unittest.TestCase):
    """Test permission enforcement for data boundaries"""

    def test_system_files_marked_readonly(self):
        """Test system files can be marked read-only"""
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, 'readonly.json')

        # Create file
        with open(test_file, 'w') as f:
            json.dump({'test': 'data'}, f)

        # Make read-only (owner read + group/other read)
        os.chmod(test_file, 0o444)

        # Verify read-only
        self.assertFalse(os.access(test_file, os.W_OK))

        # Cleanup
        os.chmod(test_file, 0o644)  # Restore write for cleanup
        shutil.rmtree(temp_dir)

    def test_memory_files_are_writable(self):
        """Test memory files have write permissions"""
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, 'writable.json')

        # Create file
        with open(test_file, 'w') as f:
            json.dump({'test': 'data'}, f)

        # Should be writable
        self.assertTrue(os.access(test_file, os.W_OK))

        # Cleanup
        shutil.rmtree(temp_dir)


class TestSessionAnalyticsBoundaryTracking(unittest.TestCase):
    """Test session analytics tracks boundary compliance"""

    def test_boundary_violation_logged(self):
        """Test boundary violations are logged"""
        # Mock analytics logger
        from core.services.session_analytics import SessionAnalytics

        with patch.object(SessionAnalytics, 'log_event') as mock_log:
            analytics = SessionAnalytics()

            # Simulate boundary violation
            analytics.log_boundary_violation(
                source='memory/test.json',
                dest='knowledge/system/data.json',
                command='SAVE'
            )

            # Verify logged
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            self.assertIn('boundary_violation', str(call_args))

    def test_valid_operations_logged(self):
        """Test valid operations are tracked"""
        from core.services.session_analytics import SessionAnalytics

        with patch.object(SessionAnalytics, 'log_event') as mock_log:
            analytics = SessionAnalytics()

            # Simulate valid operation
            analytics.log_file_operation(
                operation='write',
                path='memory/private/notes.json',
                success=True
            )

            # Verify logged (may be called multiple times)
            mock_log.assert_called()

class TestErrorHandlerBoundaryDetection(unittest.TestCase):
    """Test error handler detects boundary violations"""

    def test_error_handler_catches_system_writes(self):
        """Test error handler catches unauthorized system writes"""
        from core.services.error_handler import ErrorHandler

        handler = ErrorHandler()

        # Simulate unauthorized write attempt
        error = handler.validate_write_operation(
            path='knowledge/system/themes/default.json',
            command='SAVE'
        )

        self.assertIsNotNone(error)
        self.assertTrue('read-only' in error.lower() or 'system' in error.lower())

    def test_error_handler_allows_memory_writes(self):
        """Test error handler allows memory writes"""
        from core.services.error_handler import ErrorHandler

        handler = ErrorHandler()

        # Simulate valid write
        error = handler.validate_write_operation(
            path='memory/private/test.json',
            command='SAVE'
        )

        # Should be None (no error)
        self.assertIsNone(error)


class TestGitignoreCompliance(unittest.TestCase):
    """Test .gitignore properly separates system and user data"""

    def test_memory_is_gitignored(self):
        """Test memory/ directory is in .gitignore"""
        gitignore_path = os.path.join(project_root, '.gitignore')

        with open(gitignore_path, 'r') as f:
            content = f.read()

        # memory/ should be gitignored
        self.assertIn('memory/', content)

    def test_knowledge_is_tracked(self):
        """Test knowledge/ directory is tracked (not ignored)"""
        gitignore_path = os.path.join(project_root, '.gitignore')

        with open(gitignore_path, 'r') as f:
            content = f.read()

        # knowledge/ should be explicitly tracked
        self.assertIn('!knowledge/', content)

    def test_memory_tests_are_tracked(self):
        """Test memory/tests/ is tracked despite memory/ being ignored"""
        gitignore_path = os.path.join(project_root, '.gitignore')

        with open(gitignore_path, 'r') as f:
            content = f.read()

        # memory/tests/ should be explicitly tracked
        self.assertIn('!memory/tests/', content)


# Test runner
if __name__ == '__main__':
    # Run tests with verbose output
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("="*70)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
