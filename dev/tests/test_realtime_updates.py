"""
Test suite for v1.0.19 Real-time Updates and API Integration
Tests Phase 4 (Dashboard Real-time Updates) and Startup Integration
"""

import unittest
import sys
import time
import threading
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from extensions.bundled.web.teletext.api_server import (
        get_system_state, detect_changes, app, socketio
    )
    from core.services.api_server_manager import APIServerManager
    API_AVAILABLE = True
except ImportError as e:
    API_AVAILABLE = False
    print(f"⚠️  API modules not available: {e}")


class TestRealTimeUpdates(unittest.TestCase):
    """Test real-time update broadcasting system."""

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_get_system_state(self):
        """Test getting current system state."""
        state = get_system_state()

        # Should return a dict with expected keys
        self.assertIsInstance(state, dict)
        self.assertIn('timestamp', state)
        self.assertIn('xp', state)
        self.assertIn('level', state)
        self.assertIn('health', state)
        self.assertIn('energy', state)
        self.assertIn('hydration', state)
        self.assertIn('file_count', state)
        self.assertIn('position', state)

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_detect_changes(self):
        """Test change detection between states."""
        old_state = {
            'xp': 100,
            'level': 1,
            'health': 100,
            'energy': 80,
            'hydration': 90,
            'file_count': 5,
            'position': {'cell': 'A1', 'latitude': 0, 'longitude': 0}
        }

        new_state = {
            'xp': 150,  # Changed
            'level': 2,  # Changed
            'health': 100,
            'energy': 70,  # Changed
            'hydration': 90,
            'file_count': 7,  # Changed
            'position': {'cell': 'B2', 'latitude': 1, 'longitude': 1}  # Changed
        }

        changes = detect_changes(old_state, new_state)

        # Should detect XP change
        self.assertIn('xp', changes)
        self.assertEqual(changes['xp']['old'], 100)
        self.assertEqual(changes['xp']['new'], 150)
        self.assertEqual(changes['xp']['delta'], 50)

        # Should detect level change
        self.assertIn('level', changes)
        self.assertEqual(changes['level']['delta'], 1)

        # Should detect energy change
        self.assertIn('energy', changes)
        self.assertEqual(changes['energy']['delta'], -10)

        # Should detect file count change
        self.assertIn('file_count', changes)
        self.assertEqual(changes['file_count']['delta'], 2)

        # Should detect position change
        self.assertIn('position', changes)
        self.assertEqual(changes['position']['new']['cell'], 'B2')

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_no_changes_detected(self):
        """Test that identical states produce no changes."""
        state = {
            'xp': 100,
            'level': 1,
            'health': 100,
            'energy': 80,
            'hydration': 90,
            'file_count': 5,
            'position': {'cell': 'A1', 'latitude': 0, 'longitude': 0}
        }

        changes = detect_changes(state, state.copy())

        # Should have no changes
        self.assertEqual(len(changes), 0)


class TestAPIServerManager(unittest.TestCase):
    """Test API server manager functionality."""

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_manager_initialization(self):
        """Test APIServerManager initialization."""
        manager = APIServerManager(port=5001, auto_restart=True)

        self.assertEqual(manager.port, 5001)
        self.assertTrue(manager.auto_restart)
        self.assertEqual(manager.restart_attempts, 0)
        self.assertFalse(manager.running)

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_port_availability_check(self):
        """Test port availability checking."""
        manager = APIServerManager(port=5001)

        # Port should be available or in use
        result = manager.is_port_available()
        self.assertIsInstance(result, bool)

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_find_available_port(self):
        """Test finding an available port."""
        manager = APIServerManager(port=5001)

        available_port = manager.find_available_port()

        # Should return a port number or None
        if available_port:
            self.assertIsInstance(available_port, int)
            self.assertGreaterEqual(available_port, 5001)
            self.assertLess(available_port, 5101)

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_pid_file_operations(self):
        """Test PID file reading."""
        manager = APIServerManager(port=5001)

        # Get PID (should return None if not running)
        pid = manager.get_pid()
        self.assertTrue(pid is None or isinstance(pid, int))

        # Check if running
        is_running = manager.is_running()
        self.assertIsInstance(is_running, bool)


class TestWebSocketIntegration(unittest.TestCase):
    """Test WebSocket real-time update integration."""

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_flask_app_exists(self):
        """Test that Flask app is properly configured."""
        self.assertIsNotNone(app)
        self.assertEqual(app.config['SECRET_KEY'], 'udos-teletext-api-v1.0.19')

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_socketio_exists(self):
        """Test that SocketIO is properly configured."""
        self.assertIsNotNone(socketio)


class TestStartupIntegration(unittest.TestCase):
    """Test API server startup integration."""

    @unittest.skipIf(not API_AVAILABLE, "API modules not available")
    def test_api_server_manager_import(self):
        """Test that APIServerManager can be imported."""
        from core.services.api_server_manager import APIServerManager

        self.assertIsNotNone(APIServerManager)

        # Test instantiation
        manager = APIServerManager()
        self.assertIsNotNone(manager)


def run_tests():
    """Run all tests with verbose output."""
    print("\n" + "="*70)
    print("v1.0.19 REAL-TIME UPDATES & API INTEGRATION TESTS")
    print("="*70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRealTimeUpdates))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIServerManager))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStartupIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed")

    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
