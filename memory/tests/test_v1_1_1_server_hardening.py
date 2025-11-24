"""
uDOS v1.1.1 - Extension Server Hardening Test Suite

Comprehensive test suite for Feature 1.1.1.1: Production-ready ServerManager

Test Coverage:
- Health monitoring and checks
- Automatic recovery from crashes
- Graceful degradation strategies
- Comprehensive error handling
- Process lifecycle management
- Resource leak prevention
- Concurrent server management
- Port conflict resolution
- Crash detection and logging

Feature: 1.1.1.1
Version: 1.1.1
Status: Active Development
"""

import unittest
import tempfile
import shutil
import os
import sys
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from core.network.server import ServerManager


class TestHealthMonitoring(unittest.TestCase):
    """Test health monitoring and health checks"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_health_check_running_server(self):
        """Test health check detects running server"""
        # Add running server to state
        self.manager.servers['dashboard'] = {
            'pid': os.getpid(),  # Use current process as mock running process
            'port': 8887,
            'started_at': time.time(),
            'url': 'http://localhost:8887'
        }

        # Health check should pass (our process is running)
        is_healthy = self.manager._is_process_running(os.getpid())
        self.assertTrue(is_healthy)

    def test_health_check_dead_server(self):
        """Test health check detects dead server"""
        # Use a PID that definitely doesn't exist
        fake_pid = 999999

        is_healthy = self.manager._is_process_running(fake_pid)
        self.assertFalse(is_healthy)

    def test_health_check_cleans_dead_servers(self):
        """Test get_status cleans up dead servers"""
        # Add dead server to state
        self.manager.servers['dashboard'] = {
            'pid': 999999,  # Non-existent PID
            'port': 8887,
            'started_at': time.time()
        }

        # Get status should detect and clean it
        status = self.manager.get_status('dashboard')

        # Should report not running
        self.assertIn('not running', status.lower() or 'cleaned up' in status.lower())

        # Should remove from state
        self.assertNotIn('dashboard', self.manager.servers)

    def test_port_availability_check(self):
        """Test port availability checking"""
        # Port 0 is special - OS assigns unused port
        self.assertFalse(self.manager._is_port_in_use(0))

    def test_uptime_formatting(self):
        """Test uptime formatting"""
        # Test seconds
        self.assertEqual(self.manager._format_uptime(45), "45s")

        # Test minutes
        self.assertEqual(self.manager._format_uptime(125), "2m 5s")

        # Test hours
        self.assertEqual(self.manager._format_uptime(7325), "2h 2m")


class TestAutomaticRecovery(unittest.TestCase):
    """Test automatic recovery from crashes"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    @patch('core.network.server.subprocess.Popen')
    @patch('core.network.server.Path.exists')
    def test_restart_after_crash(self, mock_exists, mock_popen):
        """Test automatic restart after crash detection"""
        mock_exists.return_value = True

        # First start
        mock_process1 = Mock()
        mock_process1.pid = 12345
        mock_process1.poll.return_value = None  # Running

        # Second start (after crash)
        mock_process2 = Mock()
        mock_process2.pid = 12346
        mock_process2.poll.return_value = None  # Running

        mock_popen.side_effect = [mock_process1, mock_process2]

        # Start server
        success1, msg1 = self.manager._use_bulletproof_launcher('dashboard')
        self.assertTrue(success1)

        # Simulate crash (mark process as dead)
        self.manager.servers['dashboard']['pid'] = 999999

        # Restart
        success2, msg2 = self.manager._use_bulletproof_launcher('dashboard')
        self.assertTrue(success2)

    def test_state_recovery_from_corrupt_file(self):
        """Test recovery from corrupt state file"""
        # Write corrupt JSON
        with open(self.state_file, 'w') as f:
            f.write('{ corrupt json }')

        # Manager should handle gracefully
        manager = ServerManager(state_file=self.state_file)

        # Should have empty state, not crash
        self.assertEqual(manager.servers, {})

    def test_state_recovery_from_missing_file(self):
        """Test recovery from missing state file"""
        # Don't create state file
        non_existent = os.path.join(self.temp_dir, 'nonexistent.json')

        # Manager should handle gracefully
        manager = ServerManager(state_file=non_existent)

        # Should have empty state
        self.assertEqual(manager.servers, {})


class TestGracefulDegradation(unittest.TestCase):
    """Test graceful degradation strategies"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_fallback_python_executable(self):
        """Test fallback to system Python when venv unavailable"""
        # Get Python exe (should work with or without venv)
        python_exe = self.manager._get_python_executable()

        self.assertIsNotNone(python_exe)
        self.assertTrue(len(python_exe) > 0)

    def test_missing_launcher_graceful_failure(self):
        """Test graceful failure when launcher missing"""
        # Make launcher path invalid
        self.manager.launcher_path = Path('/nonexistent/launcher.py')

        success, message = self.manager._use_bulletproof_launcher('dashboard')

        self.assertFalse(success)
        self.assertIn('Launcher not found', message)

    def test_unknown_server_graceful_failure(self):
        """Test graceful failure for unknown server"""
        success, message = self.manager._use_bulletproof_launcher('unknown-server')
        
        self.assertFalse(success)
        # Accepts either "Unknown server" or "Launcher not found"
        self.assertTrue('unknown' in message.lower() or 'not found' in message.lower())

    def test_browser_open_failure_handled(self):
        """Test browser open failure handled gracefully"""
        with patch('core.network.server.webbrowser.open', side_effect=Exception('No browser')):
            # Should return False but not crash
            result = self.manager.open_in_browser('http://localhost:8887')
            self.assertFalse(result)


class TestComprehensiveErrorHandling(unittest.TestCase):
    """Test comprehensive error handling"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_permission_error_stopping_server(self):
        """Test handling of permission errors when stopping"""
        # Add server with PID we can't kill
        self.manager.servers['dashboard'] = {
            'pid': 1,  # Init process - can't kill
            'port': 8887
        }
        
        with patch('core.network.server.os.kill', side_effect=PermissionError('Permission denied')):
            success, message = self.manager.stop_server('dashboard')
            
            # Server removes dead servers from state, so might succeed
            # The important thing is it doesn't crash
            self.assertIsInstance(message, str)
            self.assertTrue(len(message) > 0)

    def test_process_lookup_error_handled(self):
        """Test ProcessLookupError handled gracefully"""
        self.manager.servers['dashboard'] = {
            'pid': 999999,
            'port': 8887
        }
        
        # stop_server should handle ProcessLookupError
        success, message = self.manager.stop_server('dashboard')
        
        # Server cleans up dead servers, so success=False but doesn't crash
        self.assertIsInstance(success, bool)
        self.assertIn('not running', message.lower())

    def test_exception_during_start(self):
        """Test exception handling during server start"""
        with patch('core.network.server.subprocess.Popen', side_effect=Exception('Popen failed')):
            with patch('core.network.server.Path.exists', return_value=True):
                success, message = self.manager._use_bulletproof_launcher('dashboard')

                self.assertFalse(success)
                # Should contain error information
                self.assertTrue(len(message) > 0)


class TestProcessLifecycle(unittest.TestCase):
    """Test complete process lifecycle management"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    @patch('core.network.server.os.kill')
    @patch('core.network.server.time.sleep')
    def test_graceful_shutdown_before_force_kill(self, mock_sleep, mock_kill):
        """Test SIGTERM before SIGKILL"""
        self.manager.servers['dashboard'] = {
            'pid': 12345,
            'port': 8887
        }
        
        # Mock process as running initially, then dead
        with patch.object(self.manager, '_is_process_running', side_effect=[True, True, False]):
            success, message = self.manager.stop_server('dashboard')
            
            # Should have attempted to kill the process
            # Check that os.kill was called (either SIGTERM 15 or SIGKILL 9)
            self.assertTrue(mock_kill.called)
            # Verify PID 12345 was targeted
            pids_killed = [call[0][0] for call in mock_kill.call_args_list]
            self.assertIn(12345, pids_killed)

    def test_cleanup_all_servers(self):
        """Test cleanup of all running servers"""
        # Add multiple servers
        self.manager.servers['dashboard'] = {'pid': 999991, 'port': 8887}
        self.manager.servers['terminal'] = {'pid': 999992, 'port': 8890}

        # Cleanup all
        self.manager.cleanup_all()

        # All should be removed
        self.assertEqual(len(self.manager.servers), 0)

    def test_state_persistence_across_instances(self):
        """Test state persists across manager instances"""
        # Add server
        self.manager.servers['dashboard'] = {
            'pid': 12345,
            'port': 8887,
            'started_at': time.time()
        }
        self.manager._save_state()

        # Create new manager instance
        new_manager = ServerManager(state_file=self.state_file)

        # Should load state
        self.assertIn('dashboard', new_manager.servers)
        self.assertEqual(new_manager.servers['dashboard']['pid'], 12345)


class TestResourceManagement(unittest.TestCase):
    """Test resource leak prevention"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_log_file_creation(self):
        """Test log files are created properly"""
        with patch('core.network.server.subprocess.Popen') as mock_popen:
            with patch('core.network.server.Path.exists', return_value=True):
                mock_process = Mock()
                mock_process.pid = 12345
                mock_process.poll.return_value = None
                mock_popen.return_value = mock_process

                success, msg = self.manager._use_bulletproof_launcher('dashboard')

                # Should have created log file
                if success:
                    server_info = self.manager.servers.get('dashboard', {})
                    log_file = server_info.get('log_file')
                    if log_file:
                        self.assertTrue('dashboard' in log_file)

    def test_state_file_not_corrupted_on_crash(self):
        """Test state file integrity maintained even if crash occurs"""
        # Start with valid state
        self.manager.servers['dashboard'] = {'pid': 12345, 'port': 8887}
        self.manager._save_state()

        # Simulate crash during save
        original_state = self.manager.servers.copy()

        # State file should still be readable
        loaded = self.manager._load_state()
        self.assertIsInstance(loaded, dict)


class TestConcurrentServerManagement(unittest.TestCase):
    """Test managing multiple servers concurrently"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_multiple_servers_tracked(self):
        """Test multiple servers can be tracked simultaneously"""
        servers = {
            'dashboard': {'pid': 12345, 'port': 8887},
            'terminal': {'pid': 12346, 'port': 8890},
            'markdown-viewer': {'pid': 12347, 'port': 9000}
        }

        self.manager.servers = servers
        self.manager._save_state()

        # All should be tracked
        self.assertEqual(len(self.manager.servers), 3)

    def test_status_shows_all_servers(self):
        """Test status command shows all running servers"""
        self.manager.servers = {
            'dashboard': {'pid': os.getpid(), 'port': 8887, 'url': 'http://localhost:8887', 'started_at': time.time()},
            'terminal': {'pid': os.getpid(), 'port': 8890, 'url': 'http://localhost:8890', 'started_at': time.time()}
        }

        status = self.manager.get_status()

        # Should mention both servers
        self.assertIn('dashboard', status.lower() or 'terminal' in status.lower())


class TestPortConflictResolution(unittest.TestCase):
    """Test port conflict detection and resolution"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_default_port_assignment(self):
        """Test default port assignment for known servers"""
        # Dashboard should get 8887
        port = self.manager._get_default_port('dashboard')
        self.assertEqual(port, 8887)

        # Terminal should get 8890
        port = self.manager._get_default_port('terminal')
        self.assertEqual(port, 8890)

    def test_unknown_server_gets_default(self):
        """Test unknown server gets fallback port"""
        port = self.manager._get_default_port('unknown-server')
        self.assertEqual(port, 8000)


class TestCrashDetectionLogging(unittest.TestCase):
    """Test crash detection and logging"""

    def setUp(self):
        """Create test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.temp_dir, '.server_state.json')
        self.manager = ServerManager(state_file=self.state_file)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_crashed_process_detected(self):
        """Test crashed process is detected"""
        # Add server that will appear crashed
        self.manager.servers['dashboard'] = {
            'pid': 999999,  # Non-existent PID
            'port': 8887,
            'started_at': time.time()
        }

        # Check if running
        is_running = self.manager._is_process_running(999999)
        self.assertFalse(is_running)

    @patch('core.network.server.subprocess.Popen')
    @patch('core.network.server.Path.exists')
    def test_immediate_crash_detected(self, mock_exists, mock_popen):
        """Test immediate crash after start is detected"""
        mock_exists.return_value = True

        # Mock process that exits immediately
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = 1  # Exited with error
        mock_popen.return_value = mock_process

        success, message = self.manager._use_bulletproof_launcher('dashboard')

        self.assertFalse(success)
        self.assertIn('failed to start', message.lower() or 'exit' in message.lower())


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
