"""
uDOS v1.1.0 - Session Analytics Tests

Test suite for comprehensive session logging and analysis.

Version: 1.1.0
"""

import unittest
import json
import time
from pathlib import Path
from datetime import datetime
from core.services.session_analytics import (
    SessionAnalytics,
    CommandTrace,
    ErrorEntry,
    FeedbackEntry,
    get_session_analytics,
    track_command_execution
)


class TestSessionAnalytics(unittest.TestCase):
    """Test session analytics functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path("memory/sessions/test")
        self.test_log_dir = Path("memory/logs/test")

        # Create test analytics instance
        self.analytics = SessionAnalytics(
            session_dir=str(self.test_dir.parent),
            log_dir=str(self.test_log_dir.parent)
        )

    def tearDown(self):
        """Clean up test files"""
        # Note: Keep test session logs for manual inspection
        # They're in memory/sessions/auto/ which is .gitignored
        pass

    def test_session_initialization(self):
        """Test session is properly initialized"""
        self.assertIsNotNone(self.analytics.session_id)
        self.assertTrue(self.analytics.session_id.startswith("session_"))
        self.assertIsNotNone(self.analytics.started_at)
        self.assertEqual(self.analytics.user_role, "user")
        self.assertTrue(self.analytics.session_file.exists())

    def test_command_tracking(self):
        """Test command execution tracking"""
        # Track a successful command
        self.analytics.track_command(
            command="MAP",
            params=["CREATE", "test_map"],
            duration_ms=125.5,
            success=True,
            context={"planet": "Earth", "panel": "main"}
        )

        self.assertEqual(len(self.analytics.commands), 1)
        cmd = self.analytics.commands[0]
        self.assertEqual(cmd.command, "MAP")
        self.assertEqual(cmd.params, ["CREATE", "test_map"])
        self.assertEqual(cmd.duration_ms, 125.5)
        self.assertTrue(cmd.success)
        self.assertIsNotNone(cmd.context)

    def test_error_tracking(self):
        """Test error logging and tracking"""
        self.analytics.track_error(
            command="LOAD",
            params=["nonexistent.txt"],
            error_type="FileNotFoundError",
            error_msg="File 'nonexistent.txt' not found",
            context={"current_dir": "/test"},
            resolution="retry",
            ai_suggested_fix="Check file path and try again"
        )

        self.assertEqual(len(self.analytics.errors), 1)
        error = self.analytics.errors[0]
        self.assertEqual(error.command, "LOAD")
        self.assertEqual(error.error_type, "FileNotFoundError")
        self.assertEqual(error.resolution, "retry")
        self.assertIsNotNone(error.ai_suggested_fix)

    def test_feedback_tracking(self):
        """Test user feedback capture"""
        self.analytics.track_feedback(
            feedback_type="confusion",
            message="Not sure what TIZO means",
            context={"command": "MAP VIEW"},
            command_context="MAP VIEW"
        )

        self.assertEqual(len(self.analytics.feedback), 1)
        feedback = self.analytics.feedback[0]
        self.assertEqual(feedback.type, "confusion")
        self.assertTrue("TIZO" in feedback.message)
        self.assertEqual(feedback.command_context, "MAP VIEW")

    def test_performance_calculation(self):
        """Test performance metrics calculation"""
        # Add multiple commands with varying durations
        for i in range(10):
            self.analytics.track_command(
                command="TEST",
                params=[str(i)],
                duration_ms=100 * (i + 1),  # 100ms to 1000ms
                success=True
            )

        # Add one slow command
        self.analytics.track_command(
            command="SLOW",
            params=[],
            duration_ms=1500,
            success=True
        )

        perf = self.analytics._calculate_performance()

        self.assertEqual(perf['total_commands'], 11)
        self.assertEqual(perf['successful_commands'], 11)
        self.assertEqual(perf['failed_commands'], 0)
        self.assertEqual(perf['slow_commands'], 1)  # Only 1500ms is >1000ms
        self.assertGreater(perf['avg_response_ms'], 0)

    def test_error_pattern_analysis(self):
        """Test error pattern detection"""
        # Create multiple errors of same type
        for i in range(3):
            self.analytics.track_error(
                command="LOAD",
                params=[f"file{i}.txt"],
                error_type="FileNotFoundError",
                error_msg=f"File not found: file{i}.txt",
                context={}
            )

        # Create a different error type
        self.analytics.track_error(
            command="MAP",
            params=["CREATE"],
            error_type="ValueError",
            error_msg="Invalid map name",
            context={},
            resolution="fixed"
        )

        patterns = self.analytics.get_error_patterns()

        self.assertIn("most_common_errors", patterns)
        self.assertIn("commands_with_most_errors", patterns)
        self.assertIn("unresolved_errors", patterns)

        # FileNotFoundError should be most common
        most_common = patterns['most_common_errors'][0]
        self.assertEqual(most_common[0], "FileNotFoundError")
        self.assertEqual(most_common[1], 3)

        # Should have 3 unresolved (the FileNotFoundErrors)
        self.assertEqual(patterns['unresolved_errors'], 3)

    def test_session_persistence(self):
        """Test session data is saved to disk"""
        # Track some data
        self.analytics.track_command(
            command="TEST",
            params=["persistence"],
            duration_ms=50,
            success=True
        )

        self.analytics.track_error(
            command="TEST",
            params=["error"],
            error_type="TestError",
            error_msg="Test error message",
            context={}
        )

        self.analytics._save_session()

        # Verify file exists and contains data
        self.assertTrue(self.analytics.session_file.exists())

        with open(self.analytics.session_file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['session_id'], self.analytics.session_id)
        self.assertGreater(len(data['commands']), 0)
        self.assertGreater(len(data['errors']), 0)
        self.assertIn('performance', data)
        self.assertIn('metadata', data)

    def test_gemini_api_tracking(self):
        """Test Gemini API call tracking"""
        api_call_data = {
            "tokens": 150,
            "cost_estimate": 0.00045,
            "model": "gemini-pro"
        }

        self.analytics.track_command(
            command="OK ASK",
            params=["What is a map?"],
            duration_ms=1243,
            success=True,
            gemini_api_call=api_call_data
        )

        cmd = self.analytics.commands[0]
        self.assertIsNotNone(cmd.gemini_api_call)
        self.assertEqual(cmd.gemini_api_call['tokens'], 150)
        self.assertIn('cost_estimate', cmd.gemini_api_call)

    def test_session_summary(self):
        """Test session summary generation"""
        # Add some varied data
        for i in range(5):
            self.analytics.track_command(
                command="TEST",
                params=[str(i)],
                duration_ms=200,
                success=True
            )

        self.analytics.track_error(
            command="TEST",
            params=["error"],
            error_type="TestError",
            error_msg="Test",
            context={}
        )

        self.analytics.track_feedback(
            feedback_type="feature_request",
            message="Would be nice to have X",
            context={}
        )

        summary = self.analytics.get_session_summary()

        self.assertIn("Session Analytics Summary", summary)
        self.assertIn(self.analytics.session_id, summary)
        self.assertIn("Total Commands:", summary)
        self.assertIn("Performance:", summary)
        self.assertIn("Errors:", summary)
        self.assertIn("User Feedback:", summary)

    def test_convenience_function(self):
        """Test track_command_execution convenience function"""
        start_time = time.time()
        time.sleep(0.1)  # Simulate command execution

        track_command_execution(
            command="TEST",
            params=["convenience"],
            start_time=start_time,
            success=True,
            context={"test": True}
        )

        # Should create analytics instance if not exists
        analytics = get_session_analytics()
        self.assertIsNotNone(analytics)

        # Should have tracked the command
        # Note: This might have other commands from previous tests
        # if using shared instance
        found = any(
            cmd.command == "TEST" and cmd.params == ["convenience"]
            for cmd in analytics.commands
        )
        self.assertTrue(found, "Command should be tracked")


class TestCommandTrace(unittest.TestCase):
    """Test CommandTrace dataclass"""

    def test_command_trace_creation(self):
        """Test creating command trace"""
        trace = CommandTrace(
            timestamp="2025-11-23T15:00:00",
            command="MAP",
            params=["CREATE"],
            duration_ms=125.5,
            success=True,
            context={"planet": "Earth"}
        )

        self.assertEqual(trace.command, "MAP")
        self.assertEqual(trace.params, ["CREATE"])
        self.assertTrue(trace.success)

    def test_command_trace_to_dict(self):
        """Test converting to dictionary"""
        trace = CommandTrace(
            timestamp="2025-11-23T15:00:00",
            command="MAP",
            params=["CREATE"],
            duration_ms=125.5,
            success=True
        )

        d = trace.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['command'], "MAP")
        self.assertNotIn('error_type', d)  # None values excluded


class TestErrorEntry(unittest.TestCase):
    """Test ErrorEntry dataclass"""

    def test_error_entry_creation(self):
        """Test creating error entry"""
        error = ErrorEntry(
            timestamp="2025-11-23T15:00:00",
            command="LOAD",
            params=["test.txt"],
            error_type="FileNotFoundError",
            error_msg="File not found",
            context={"dir": "/test"}
        )

        self.assertEqual(error.error_type, "FileNotFoundError")
        self.assertEqual(error.command, "LOAD")


class TestFeedbackEntry(unittest.TestCase):
    """Test FeedbackEntry dataclass"""

    def test_feedback_entry_creation(self):
        """Test creating feedback entry"""
        feedback = FeedbackEntry(
            timestamp="2025-11-23T15:00:00",
            type="confusion",
            message="Not sure about this",
            context={"command": "MAP"}
        )

        self.assertEqual(feedback.type, "confusion")
        self.assertFalse(feedback.resolved)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
