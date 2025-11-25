"""
Tests for User Feedback Handler v1.1.0

Test feedback collection, bug reports, and session integration.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from core.commands.feedback_handler import (
    FeedbackHandler,
    BugReport,
    get_feedback_handler,
    capture_feedback,
    submit_report
)
from core.services.session_analytics import SessionAnalytics, FeedbackEntry


class TestFeedbackHandler(unittest.TestCase):
    """Test FeedbackHandler class"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.memory_root = self.test_dir / "memory"
        self.analytics = SessionAnalytics(
            session_dir=str(self.memory_root / "sessions"),
            log_dir=str(self.memory_root / "logs")
        )
        self.handler = FeedbackHandler(
            session_analytics=self.analytics,
            memory_root=self.memory_root
        )

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def test_handler_initialization(self):
        """Test handler is properly initialized"""
        self.assertIsNotNone(self.handler)
        self.assertIsNotNone(self.handler.analytics)
        self.assertTrue(self.handler.feedback_dir.exists())

    def test_handle_feedback_basic(self):
        """Test basic feedback handling"""
        result = self.handler.handle_feedback(
            message="Great feature!",
            category="praise"
        )

        self.assertIn("✅", result)
        self.assertIn("Feedback recorded", result)
        self.assertIn("praise", result)

    def test_handle_feedback_empty_message(self):
        """Test handling empty feedback message"""
        result = self.handler.handle_feedback(message="")

        self.assertIn("❌", result)
        self.assertIn("cannot be empty", result)

    def test_handle_feedback_with_context(self):
        """Test feedback with additional context"""
        context = {
            "command": "MAP",
            "params": ["CREATE", "mymap"]
        }

        result = self.handler.handle_feedback(
            message="Map creation is confusing",
            category="confusion",
            context=context
        )

        self.assertIn("✅", result)

        # Verify context saved
        feedback_items = self.handler._load_feedback(limit=1)
        self.assertEqual(len(feedback_items), 1)
        self.assertEqual(feedback_items[0]["context"], context)

    def test_handle_report_basic(self):
        """Test basic bug report creation"""
        result = self.handler.handle_report(
            title="Menu rendering issue",
            description="Menu text overlaps in narrow terminals",
            category="bug",
            severity="medium"
        )

        self.assertIn("Report", result)
        self.assertIn("created", result)
        self.assertIn("Menu rendering issue", result)

    def test_handle_report_missing_title(self):
        """Test report with missing title"""
        result = self.handler.handle_report(
            title="",
            description="Some description"
        )

        self.assertIn("❌", result)
        self.assertIn("title required", result)

    def test_handle_report_missing_description(self):
        """Test report with missing description"""
        result = self.handler.handle_report(
            title="Test",
            description=""
        )

        self.assertIn("❌", result)
        self.assertIn("description required", result)

    def test_handle_report_with_steps(self):
        """Test report with reproduction steps"""
        steps = [
            "Start uDOS",
            "Run MAP CREATE test",
            "Observe error"
        ]

        result = self.handler.handle_report(
            title="MAP CREATE fails",
            description="Creating map throws KeyError",
            category="bug",
            severity="high",
            steps=steps,
            expected="Map created successfully",
            actual="KeyError: 'map_data'"
        )

        self.assertIn("Report", result)

        # Verify steps saved
        reports = self.handler._load_reports(limit=1)
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["steps_to_reproduce"], steps)
        self.assertEqual(reports[0]["expected_behavior"], "Map created successfully")

    def test_severity_icons(self):
        """Test different severity levels use correct icons"""
        severities = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "📌",
            "low": "ℹ️",
            "info": "💡"
        }

        for severity, expected_icon in severities.items():
            icon = self.handler._get_severity_icon(severity)
            self.assertEqual(icon, expected_icon)

    def test_feedback_persistence(self):
        """Test feedback is persisted to file"""
        self.handler.handle_feedback(
            message="Test feedback",
            category="general"
        )

        # Verify file exists and contains data
        self.assertTrue(self.handler.feedback_file.exists())

        with open(self.handler.feedback_file, 'r') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0)

            data = json.loads(lines[-1])
            self.assertEqual(data["message"], "Test feedback")
            self.assertEqual(data["type"], "general")

    def test_report_persistence(self):
        """Test reports are persisted to file"""
        self.handler.handle_report(
            title="Test Report",
            description="Test description",
            category="bug"
        )

        # Verify file exists and contains data
        self.assertTrue(self.handler.reports_file.exists())

        with open(self.handler.reports_file, 'r') as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0)

            data = json.loads(lines[-1])
            self.assertEqual(data["title"], "Test Report")
            self.assertEqual(data["description"], "Test description")

    def test_session_integration(self):
        """Test feedback integrates with session analytics"""
        self.handler.handle_feedback(
            message="Integration test",
            category="test"
        )

        # Verify tracked in session analytics
        session_file = self.analytics.session_file
        self.assertTrue(session_file.exists())

        with open(session_file, 'r') as f:
            session_data = json.load(f)
            self.assertIn("feedback", session_data)
            self.assertGreater(len(session_data["feedback"]), 0)

    def test_get_feedback_summary(self):
        """Test getting feedback summary"""
        # Add some feedback
        self.handler.handle_feedback("First feedback", "general")
        self.handler.handle_feedback("Second feedback", "confusion")

        summary = self.handler.get_feedback_summary(limit=10)

        self.assertIn("Recent Feedback", summary)
        self.assertIn("First feedback", summary)
        self.assertIn("Second feedback", summary)

    def test_get_feedback_summary_empty(self):
        """Test feedback summary when no feedback exists"""
        summary = self.handler.get_feedback_summary()

        self.assertIn("No feedback recorded", summary)

    def test_get_reports_summary(self):
        """Test getting reports summary"""
        # Add some reports
        self.handler.handle_report("Bug 1", "Description 1", severity="high")
        self.handler.handle_report("Bug 2", "Description 2", severity="low")

        summary = self.handler.get_reports_summary(limit=10)

        self.assertIn("Recent Reports", summary)
        self.assertIn("Bug 1", summary)
        self.assertIn("Bug 2", summary)
        self.assertIn("HIGH", summary)

    def test_get_reports_summary_empty(self):
        """Test reports summary when no reports exist"""
        summary = self.handler.get_reports_summary()

        self.assertIn("No bug reports", summary)

    def test_multiple_feedback_items(self):
        """Test tracking multiple feedback items"""
        messages = [
            "Feedback 1",
            "Feedback 2",
            "Feedback 3"
        ]

        for msg in messages:
            self.handler.handle_feedback(msg, "general")

        feedback_items = self.handler._load_feedback(limit=10)
        self.assertEqual(len(feedback_items), 3)

    def test_feedback_limit(self):
        """Test feedback loading respects limit"""
        # Add many items
        for i in range(20):
            self.handler.handle_feedback(f"Feedback {i}", "general")

        # Load with limit
        feedback_items = self.handler._load_feedback(limit=5)
        self.assertEqual(len(feedback_items), 5)


class TestBugReport(unittest.TestCase):
    """Test BugReport dataclass"""

    def test_bug_report_creation(self):
        """Test creating bug report"""
        report = BugReport(
            timestamp="2024-01-01T12:00:00",
            category="bug",
            severity="high",
            title="Test Bug",
            description="Test description",
            steps_to_reproduce=["Step 1", "Step 2"],
            expected_behavior="Expected",
            actual_behavior="Actual",
            context={"key": "value"},
            session_id="test123"
        )

        self.assertEqual(report.title, "Test Bug")
        self.assertEqual(report.severity, "high")

    def test_bug_report_to_dict(self):
        """Test converting bug report to dictionary"""
        report = BugReport(
            timestamp="2024-01-01T12:00:00",
            category="bug",
            severity="high",
            title="Test Bug",
            description="Test description",
            steps_to_reproduce=["Step 1"],
            expected_behavior="Expected",
            actual_behavior="Actual",
            context={},
            session_id="test123"
        )

        data = report.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["title"], "Test Bug")
        self.assertEqual(data["severity"], "high")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())

        # Reset global handler
        import core.commands.feedback_handler as fh
        fh._global_feedback_handler = None

    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_get_feedback_handler(self):
        """Test getting global feedback handler"""
        handler1 = get_feedback_handler()
        handler2 = get_feedback_handler()

        self.assertIsNotNone(handler1)
        self.assertIs(handler1, handler2)  # Same instance

    def test_capture_feedback(self):
        """Test convenience feedback capture"""
        result = capture_feedback("Test message", category="test")

        self.assertIn("✅", result)
        self.assertIn("Feedback recorded", result)

    def test_submit_report(self):
        """Test convenience report submission"""
        result = submit_report(
            title="Test Report",
            description="Test description",
            category="bug",
            severity="medium"
        )

        self.assertIn("Report", result)
        self.assertIn("created", result)


if __name__ == '__main__':
    unittest.main()
