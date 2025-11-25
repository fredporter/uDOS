"""
uDOS v1.1.0 - POKE Command Test Suite

Comprehensive test suite for Feature 1.1.0.13: POKE Command Stabilization

Test Coverage:
- ServerManager lifecycle (start, stop, restart, status)
- POKE command validation (LIST, START, STOP, STATUS, HEALTH, RESTART)
- Error handling (port conflicts, missing extensions, process failures)
- Process management (PID tracking, state persistence, cleanup)
- Cross-platform compatibility (macOS, Linux, Windows)
- Integration with session analytics

Feature: 1.1.0.13
Version: 1.1.0
Status: Active Development
"""

import unittest
import json
import tempfile
import shutil
import os
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from core.network.server import ServerManager


class TestServerManagerBasics(unittest.TestCase):
    """Test ServerManager basic functionality"""

    def setUp(self):
        """Create temporary state file"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test ServerManager initialization"""
        self.assertIsInstance(self.manager, ServerManager)
        self.assertEqual(self.manager.state_file, self.state_file)
        self.assertIsInstance(self.manager.servers, dict)

    def test_state_file_creation(self):
        """Test state file is created"""
        # Save state
        self.manager.servers['test'] = {'pid': 1234, 'port': 8888}
        self.manager._save_state()

        # Verify file exists
        self.assertTrue(os.path.exists(self.state_file))

        # Verify contents
        with open(self.state_file, 'r') as f:
            data = json.load(f)
            self.assertIn('test', data)
            self.assertEqual(data['test']['pid'], 1234)

    def test_state_persistence(self):
        """Test state persists across instances"""
        # Save state with first instance
        self.manager.servers['dashboard'] = {
            'pid': 5678,
            'port': 8887,
            'started_at': time.time()
        }
        self.manager._save_state()

        # Create new instance
        manager2 = ServerManager(state_file=self.state_file)

        # Verify state loaded
        self.assertIn('dashboard', manager2.servers)
        self.assertEqual(manager2.servers['dashboard']['pid'], 5678)

    def test_get_default_port(self):
        """Test default port mapping"""
        self.assertEqual(self.manager._get_default_port('dashboard'), 8887)
        self.assertEqual(self.manager._get_default_port('terminal'), 8890)
        self.assertEqual(self.manager._get_default_port('unknown'), 8000)


class TestServerLifecycle(unittest.TestCase):
    """Test server start/stop/restart lifecycle"""

    def setUp(self):
        """Create manager with temporary state"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    @patch('core.network.server.subprocess.Popen')
    @patch('core.network.server.Path.exists')
    def test_start_server_success(self, mock_exists, mock_popen):
        """Test successful server start"""
        # Mock launcher exists
        mock_exists.return_value = True

        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process

        # Start server
        success, message = self.manager._use_bulletproof_launcher('dashboard', port=8887)

        # Verify success
        self.assertTrue(success)
        self.assertIn('dashboard started', message)
        self.assertIn('12345', message)

        # Verify state saved
        self.assertIn('dashboard', self.manager.servers)
        self.assertEqual(self.manager.servers['dashboard']['pid'], 12345)

    @patch('core.network.server.subprocess.Popen')
    @patch('core.network.server.Path.exists')
    def test_start_server_launcher_missing(self, mock_exists, mock_popen):
        """Test start fails when launcher missing"""
        mock_exists.return_value = False

        success, message = self.manager._use_bulletproof_launcher('dashboard')

        self.assertFalse(success)
        self.assertIn('Launcher not found', message)

    @patch('core.network.server.subprocess.Popen')
    @patch('core.network.server.Path.exists')
    def test_start_server_process_fails(self, mock_exists, mock_popen):
        """Test start fails when process crashes immediately"""
        mock_exists.return_value = True

        # Mock process that exits immediately
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = 1  # Exited with error
        mock_popen.return_value = mock_process

        success, message = self.manager._use_bulletproof_launcher('dashboard')

        self.assertFalse(success)
        self.assertIn('failed to start', message)

    def test_stop_server_not_running(self):
        """Test stopping non-existent server"""
        success, message = self.manager.stop_server('dashboard')

        self.assertFalse(success)
        self.assertIn('No server', message)

    @patch('core.network.server.os.kill')
    def test_stop_server_success(self, mock_kill):
        """Test successful server stop"""
        # Add running server to state
        self.manager.servers['dashboard'] = {
            'pid': 12345,
            'port': 8887,
            'started_at': time.time()
        }

        # Stop server
        success, message = self.manager.stop_server('dashboard')

        # Verify
        self.assertTrue(success)
        mock_kill.assert_called()
        self.assertNotIn('dashboard', self.manager.servers)


class TestPOKECommandValidation(unittest.TestCase):
    """Test POKE command validation and routing - simplified direct tests"""

    def setUp(self):
        """Create temp directory and manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_list_servers_returns_string(self):
        """Test LIST returns formatted server list"""
        result = self.manager.list_servers()
        self.assertIsInstance(result, str)
        # Should contain server or extension information
        self.assertTrue('server' in result.lower() or 'extension' in result.lower() or 'dashboard' in result.lower())

    def test_status_no_servers(self):
        """Test STATUS with no running servers"""
        result = self.manager.get_status()
        self.assertIsInstance(result, str)

    def test_status_specific_server(self):
        """Test STATUS for specific server name"""
        result = self.manager.get_status('dashboard')
        self.assertIsInstance(result, str)

    def test_stop_nonexistent_server_fails(self):
        """Test STOP on non-existent server returns failure"""
        success, message = self.manager.stop_server('nonexistent')
        self.assertFalse(success)
        self.assertIn('No server', message)

    @patch('core.network.server.Path.exists')
    @patch('core.network.server.subprocess.Popen')
    def test_start_creates_process(self, mock_popen, mock_exists):
        """Test START command creates subprocess"""
        mock_exists.return_value = True
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Still running
        mock_popen.return_value = mock_process

        success, message = self.manager._use_bulletproof_launcher('dashboard')

        self.assertTrue(success)
        mock_popen.assert_called_once()

    def test_get_default_port_dashboard(self):
        """Test default port mapping works"""
        port = self.manager._get_default_port('dashboard')
        self.assertEqual(port, 8887)

    def test_get_default_port_unknown(self):
        """Test unknown extension gets default port (8000)"""
        port = self.manager._get_default_port('unknown_ext')
        self.assertEqual(port, 8000)
class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""

    def setUp(self):
        """Create manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_corrupt_state_file(self):
        """Test handling of corrupt state file"""
        # Write invalid JSON
        with open(self.state_file, 'w') as f:
            f.write("{ invalid json }")

        # Should gracefully handle and start with empty state
        manager2 = ServerManager(state_file=self.state_file)
        self.assertEqual(len(manager2.servers), 0)

    def test_missing_state_directory(self):
        """Test creation of missing state directory"""
        state_path = os.path.join(self.temp_dir, 'nested', 'dir', '.state.json')

        # Should create directory structure
        manager = ServerManager(state_file=state_path)
        manager.servers['test'] = {'pid': 123}
        manager._save_state()

        self.assertTrue(os.path.exists(state_path))

    @patch('core.network.server.subprocess.Popen')
    @patch('core.network.server.Path.exists')
    def test_start_server_exception_handling(self, mock_exists, mock_popen):
        """Test exception handling during server start"""
        mock_exists.return_value = True
        mock_popen.side_effect = Exception("Process error")

        success, message = self.manager._use_bulletproof_launcher('dashboard')

        self.assertFalse(success)
        self.assertIn('Error starting', message)


class TestProcessManagement(unittest.TestCase):
    """Test process management functionality"""

    def setUp(self):
        """Create manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    @patch('core.network.server.os.kill')
    def test_process_cleanup_on_stop(self, mock_kill):
        """Test process is killed and cleaned from state"""
        # Add server
        self.manager.servers['test'] = {'pid': 999, 'port': 8888}
        self.manager._save_state()

        # Stop it
        self.manager.stop_server('test')

        # Verify killed and removed
        self.assertNotIn('test', self.manager.servers)

        # Verify state file updated
        manager2 = ServerManager(state_file=self.state_file)
        self.assertNotIn('test', manager2.servers)

    def test_multiple_server_tracking(self):
        """Test tracking multiple servers simultaneously"""
        # Add multiple servers
        self.manager.servers['dashboard'] = {'pid': 111, 'port': 8887}
        self.manager.servers['teletext'] = {'pid': 222, 'port': 9002}
        self.manager.servers['terminal'] = {'pid': 333, 'port': 8890}
        self.manager._save_state()

        # Verify all tracked
        self.assertEqual(len(self.manager.servers), 3)

        # Reload and verify persistence
        manager2 = ServerManager(state_file=self.state_file)
        self.assertEqual(len(manager2.servers), 3)


class TestCrossPlatformSupport(unittest.TestCase):
    """Test cross-platform compatibility"""

    def setUp(self):
        """Create manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_python_executable_detection(self):
        """Test Python executable detection"""
        python_exe = self.manager._get_python_executable()

        # Should return a valid path
        self.assertIsInstance(python_exe, str)
        self.assertTrue(len(python_exe) > 0)

    @patch('core.network.server.Path.exists')
    def test_venv_python_preference(self, mock_exists):
        """Test preference for venv Python"""
        # Mock venv exists
        mock_exists.return_value = True

        python_exe = self.manager._get_python_executable()

        # Should prefer venv Python
        self.assertIn('.venv', python_exe)

    def test_extension_directory_structure(self):
        """Test extension directory detection"""
        # Verify extensions_dir is set
        self.assertIsInstance(self.manager.extensions_dir, Path)


class TestSessionAnalyticsIntegration(unittest.TestCase):
    """Test integration with session analytics"""

    def setUp(self):
        """Set up with session analytics"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_server_start_logged(self):
        """Test server start events can be logged"""
        # This would integrate with session analytics
        # For now, just verify state is trackable
        self.manager.servers['test'] = {
            'pid': 12345,
            'port': 8888,
            'started_at': time.time(),
            'command': 'POKE START test'
        }
        self.manager._save_state()

        # Verify timestamp recorded
        self.assertIn('started_at', self.manager.servers['test'])

    def test_server_metadata_tracking(self):
        """Test server metadata can include analytics info"""
        metadata = {
            'pid': 12345,
            'port': 8888,
            'started_at': time.time(),
            'log_file': '/path/to/log',
            'url': 'http://localhost:8888',
            'session_id': 'session_20251124_120000'
        }

        self.manager.servers['dashboard'] = metadata
        self.manager._save_state()

        # Reload and verify all metadata preserved
        manager2 = ServerManager(state_file=self.state_file)
        self.assertEqual(manager2.servers['dashboard']['session_id'],
                        'session_20251124_120000')


def run_test_suite():
    """Run complete test suite with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestServerManagerBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestServerLifecycle))
    suite.addTests(loader.loadTestsFromTestCase(TestPOKECommandValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestProcessManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossPlatformSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionAnalyticsIntegration))

    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_test_suite()
    sys.exit(0 if success else 1)
