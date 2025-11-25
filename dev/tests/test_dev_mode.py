"""
DEV MODE Test Suite (v1.5.0)

Comprehensive tests for DEV MODE system:
- Master user authentication
- Session management and persistence
- Permission system for dangerous commands
- Activity logging
- Toggle ON/OFF functionality
- DEV MODE indicator in prompt
- Session auto-expiry
- Command tracking

Version: 1.0.0
Author: uDOS Development Team
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json
import sys
import time
from datetime import datetime, timedelta

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.dev_mode_manager import DevModeManager, get_dev_mode_manager, reset_dev_mode_manager
from core.config_manager import ConfigManager


class TestDevModeBasics(unittest.TestCase):
    """Test basic DEV MODE initialization and authentication"""

    def setUp(self):
        """Create temporary test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.env_path = self.test_dir / '.env'

        # Create test config
        self.config = ConfigManager(base_path=self.test_dir)
        self.config.load_all()
        self.config.set('UDOS_MASTER_PASSWORD', 'test_password_123', persist=True)
        self.config.set('UDOS_MASTER_USER', 'testuser', persist=True)
        self.config.set('username', 'testuser', persist=True)

        # Reset singleton
        reset_dev_mode_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_dev_mode_manager()

    def test_dev_mode_initialization(self):
        """Test DevModeManager initializes correctly"""
        dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        self.assertIsNotNone(dev_mode)
        self.assertFalse(dev_mode.is_active)

    def test_log_directory_creation(self):
        """Test log directory is created automatically"""
        dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        log_dir = self.test_dir / 'memory' / 'logs'
        self.assertTrue(log_dir.exists())

    def test_dangerous_commands_defined(self):
        """Test dangerous commands list is populated"""
        dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        self.assertGreater(len(dev_mode.dangerous_commands), 0)
        self.assertIn('DELETE', dev_mode.dangerous_commands)
        self.assertIn('DESTROY', dev_mode.dangerous_commands)


class TestAuthentication(unittest.TestCase):
    """Test master user authentication"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = ConfigManager(base_path=self.test_dir)
        self.config.load_all()
        self.config.set('UDOS_MASTER_PASSWORD', 'secure_pass_456', persist=True)
        self.config.set('UDOS_MASTER_USER', 'master', persist=True)
        self.config.set('username', 'master', persist=True)

        self.dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        reset_dev_mode_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_dev_mode_manager()

    def test_correct_password_authentication(self):
        """Test authentication succeeds with correct password"""
        result = self.dev_mode.authenticate('secure_pass_456')
        self.assertTrue(result)
        self.assertEqual(self.dev_mode.authenticated_user, 'master')

    def test_incorrect_password_authentication(self):
        """Test authentication fails with wrong password"""
        result = self.dev_mode.authenticate('wrong_password')
        self.assertFalse(result)
        self.assertIsNone(self.dev_mode.authenticated_user)

    def test_authentication_requires_master_user(self):
        """Test authentication fails if current user is not master user"""
        self.config.set('username', 'regularuser', persist=False)
        result = self.dev_mode.authenticate('secure_pass_456')
        self.assertFalse(result)

    def test_authentication_without_config(self):
        """Test authentication fails gracefully without config"""
        dev_mode_no_config = DevModeManager(config_manager=None, base_path=self.test_dir)
        result = dev_mode_no_config.authenticate('any_password')
        self.assertFalse(result)


class TestEnableDisable(unittest.TestCase):
    """Test DEV MODE enable/disable functionality"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = ConfigManager(base_path=self.test_dir)
        self.config.load_all()
        self.config.set('UDOS_MASTER_PASSWORD', 'enable_test_pass', persist=True)
        self.config.set('UDOS_MASTER_USER', 'admin', persist=True)
        self.config.set('username', 'admin', persist=True)

        self.dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        reset_dev_mode_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_dev_mode_manager()

    def test_enable_with_correct_password(self):
        """Test enabling DEV MODE with correct password"""
        success, message = self.dev_mode.enable(password='enable_test_pass', interactive=False)
        self.assertTrue(success)
        self.assertTrue(self.dev_mode.is_active)
        self.assertIn('ACTIVATED', message)

    def test_enable_with_wrong_password(self):
        """Test enabling DEV MODE fails with wrong password"""
        success, message = self.dev_mode.enable(password='wrong_pass', interactive=False)
        self.assertFalse(success)
        self.assertFalse(self.dev_mode.is_active)
        self.assertIn('failed', message.lower())

    def test_enable_sets_session_start(self):
        """Test enabling DEV MODE sets session start time"""
        self.dev_mode.enable(password='enable_test_pass', interactive=False)
        self.assertIsNotNone(self.dev_mode.session_start)
        self.assertIsInstance(self.dev_mode.session_start, datetime)

    def test_disable_clears_session(self):
        """Test disabling DEV MODE clears session data"""
        self.dev_mode.enable(password='enable_test_pass', interactive=False)
        success, message = self.dev_mode.disable()

        self.assertTrue(success)
        self.assertFalse(self.dev_mode.is_active)
        self.assertIsNone(self.dev_mode.session_start)
        self.assertIsNone(self.dev_mode.authenticated_user)
        self.assertEqual(self.dev_mode.command_count, 0)

    def test_disable_when_not_active(self):
        """Test disabling when DEV MODE is not active"""
        success, message = self.dev_mode.disable()
        self.assertFalse(success)
        self.assertIn('not active', message)

    def test_enable_when_already_active(self):
        """Test enabling when already active"""
        self.dev_mode.enable(password='enable_test_pass', interactive=False)
        success, message = self.dev_mode.enable(password='enable_test_pass', interactive=False)
        self.assertFalse(success)
        self.assertIn('already active', message)


class TestPermissions(unittest.TestCase):
    """Test permission system for dangerous commands"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = ConfigManager(base_path=self.test_dir)
        self.config.load_all()
        self.config.set('UDOS_MASTER_PASSWORD', 'perm_test', persist=True)
        self.config.set('UDOS_MASTER_USER', 'admin', persist=True)
        self.config.set('username', 'admin', persist=True)

        self.dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        reset_dev_mode_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_dev_mode_manager()

    def test_dangerous_command_blocked_without_dev_mode(self):
        """Test dangerous commands are blocked when DEV MODE is off"""
        allowed, message = self.dev_mode.check_permission('DELETE')
        self.assertFalse(allowed)
        self.assertIn('requires DEV MODE', message)

    def test_dangerous_command_allowed_with_dev_mode(self):
        """Test dangerous commands are allowed when DEV MODE is on"""
        self.dev_mode.enable(password='perm_test', interactive=False)
        allowed, message = self.dev_mode.check_permission('DELETE')
        self.assertTrue(allowed)
        self.assertIn('Dangerous operation', message)

    def test_safe_command_always_allowed(self):
        """Test safe commands are allowed without DEV MODE"""
        allowed, message = self.dev_mode.check_permission('HELP')
        self.assertTrue(allowed)
        self.assertIsNone(message)

    def test_case_insensitive_permission_check(self):
        """Test permission check is case-insensitive"""
        allowed1, _ = self.dev_mode.check_permission('delete')
        allowed2, _ = self.dev_mode.check_permission('DELETE')
        allowed3, _ = self.dev_mode.check_permission('DeLeTe')

        self.assertEqual(allowed1, allowed2)
        self.assertEqual(allowed2, allowed3)


class TestLogging(unittest.TestCase):
    """Test activity logging functionality"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = ConfigManager(base_path=self.test_dir)
        self.config.load_all()
        self.config.set('UDOS_MASTER_PASSWORD', 'log_test', persist=True)
        self.config.set('UDOS_MASTER_USER', 'admin', persist=True)
        self.config.set('username', 'admin', persist=True)

        self.dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        self.dev_mode.enable(password='log_test', interactive=False)
        reset_dev_mode_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_dev_mode_manager()

    def test_log_file_created(self):
        """Test log file is created"""
        self.dev_mode.log_command('TEST', ['param1', 'param2'])
        self.assertTrue(self.dev_mode.log_path.exists())

    def test_command_logging(self):
        """Test commands are logged correctly"""
        self.dev_mode.log_command('DELETE', ['file.txt'], result='Success')

        with open(self.dev_mode.log_path, 'r') as f:
            content = f.read()

        self.assertIn('DELETE', content)
        self.assertIn('file.txt', content)
        self.assertIn('Success', content)

    def test_command_count_increments(self):
        """Test command counter increments"""
        initial_count = self.dev_mode.command_count

        self.dev_mode.log_command('CMD1', [])
        self.assertEqual(self.dev_mode.command_count, initial_count + 1)

        self.dev_mode.log_command('CMD2', [])
        self.assertEqual(self.dev_mode.command_count, initial_count + 2)

    def test_json_log_created(self):
        """Test JSON command log is created"""
        self.dev_mode.log_command('TEST', ['param'])
        json_log = self.dev_mode.log_path.parent / 'dev_mode_commands.json'
        self.assertTrue(json_log.exists())

    def test_json_log_structure(self):
        """Test JSON log has correct structure"""
        self.dev_mode.log_command('TEST_CMD', ['arg1', 'arg2'], result='OK')
        json_log = self.dev_mode.log_path.parent / 'dev_mode_commands.json'

        with open(json_log, 'r') as f:
            logs = json.load(f)

        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)

        entry = logs[0]
        self.assertIn('timestamp', entry)
        self.assertIn('user', entry)
        self.assertIn('command', entry)
        self.assertIn('params', entry)
        self.assertIn('result', entry)


class TestStatus(unittest.TestCase):
    """Test status reporting"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = ConfigManager(base_path=self.test_dir)
        self.config.load_all()
        self.config.set('UDOS_MASTER_PASSWORD', 'status_test', persist=True)
        self.config.set('UDOS_MASTER_USER', 'admin', persist=True)
        self.config.set('username', 'admin', persist=True)

        self.dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        reset_dev_mode_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_dev_mode_manager()

    def test_status_when_inactive(self):
        """Test status returns correct data when inactive"""
        status = self.dev_mode.get_status()

        self.assertFalse(status['active'])
        self.assertIn('master_user', status)

    def test_status_when_active(self):
        """Test status returns correct data when active"""
        self.dev_mode.enable(password='status_test', interactive=False)
        status = self.dev_mode.get_status()

        self.assertTrue(status['active'])
        self.assertEqual(status['user'], 'admin')
        self.assertIn('session_start', status)
        self.assertIn('duration', status)
        self.assertIn('commands_executed', status)


class TestSessionPersistence(unittest.TestCase):
    """Test session persistence and restoration"""

    def setUp(self):
        """Create test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = ConfigManager(base_path=self.test_dir)
        self.config.load_all()
        self.config.set('UDOS_MASTER_PASSWORD', 'persist_test', persist=True)
        self.config.set('UDOS_MASTER_USER', 'admin', persist=True)
        self.config.set('username', 'admin', persist=True)

        reset_dev_mode_manager()

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        reset_dev_mode_manager()

    def test_session_file_created_on_enable(self):
        """Test session file is created when DEV MODE is enabled"""
        dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        dev_mode.enable(password='persist_test', interactive=False)

        self.assertTrue(dev_mode.session_file.exists())

    def test_session_file_deleted_on_disable(self):
        """Test session file is deleted when DEV MODE is disabled"""
        dev_mode = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        dev_mode.enable(password='persist_test', interactive=False)
        dev_mode.disable()

        self.assertFalse(dev_mode.session_file.exists())

    def test_session_restoration_within_timeout(self):
        """Test session is restored if recent (within 1 hour)"""
        # Create and enable first instance
        dev_mode1 = DevModeManager(config_manager=self.config, base_path=self.test_dir)
        dev_mode1.enable(password='persist_test', interactive=False)
        dev_mode1.command_count = 5
        dev_mode1._save_session()

        # Create second instance (should restore session)
        dev_mode2 = DevModeManager(config_manager=self.config, base_path=self.test_dir)

        self.assertTrue(dev_mode2.is_active)
        self.assertEqual(dev_mode2.command_count, 5)


class TestSingleton(unittest.TestCase):
    """Test singleton pattern"""

    def setUp(self):
        """Reset singleton"""
        reset_dev_mode_manager()

    def tearDown(self):
        """Reset singleton"""
        reset_dev_mode_manager()

    def test_singleton_returns_same_instance(self):
        """Test get_dev_mode_manager() returns same instance"""
        dm1 = get_dev_mode_manager()
        dm2 = get_dev_mode_manager()

        self.assertIs(dm1, dm2)

    def test_reset_clears_singleton(self):
        """Test reset_dev_mode_manager() clears singleton"""
        dm1 = get_dev_mode_manager()
        reset_dev_mode_manager()
        dm2 = get_dev_mode_manager()

        self.assertIsNot(dm1, dm2)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
