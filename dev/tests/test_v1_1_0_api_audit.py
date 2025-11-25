"""
uDOS v1.1.0 - API Audit Logger Tests

Test suite for API usage audit logging.

Version: 1.1.0
"""

import unittest
import json
import time
from pathlib import Path
from core.services.api_audit import (
    APIAuditLogger,
    APICallRecord,
    get_audit_logger,
    log_api_call
)


class TestAPIAuditLogger(unittest.TestCase):
    """Test API audit logging functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_log_dir = Path("memory/logs/test")
        self.logger = APIAuditLogger(log_dir=str(self.test_log_dir))

    def tearDown(self):
        """Clean up test files"""
        # Keep test logs for manual inspection
        pass

    def test_logger_initialization(self):
        """Test logger is properly initialized"""
        self.assertTrue(self.logger.audit_file.exists())
        self.assertTrue(self.logger.audit_json.exists())
        self.assertEqual(len(self.logger.session_records), 0)

    def test_log_api_call(self):
        """Test logging an API call"""
        self.logger.log_api_call(
            user_role="wizard",
            operation="OK ASK",
            api_type="gemini",
            query="How do I create a map?",
            tokens_used=150,
            cost_estimate=0.00045,
            duration_ms=1243.5,
            success=True
        )

        self.assertEqual(len(self.logger.session_records), 1)
        record = self.logger.session_records[0]
        self.assertEqual(record.user_role, "wizard")
        self.assertEqual(record.operation, "OK ASK")
        self.assertEqual(record.api_type, "gemini")
        self.assertEqual(record.tokens_used, 150)
        self.assertTrue(record.success)

    def test_log_failed_call(self):
        """Test logging a failed API call"""
        self.logger.log_api_call(
            user_role="user",
            operation="OK ASK",
            api_type="gemini",
            query="Test query",
            success=False,
            error_msg="Connection timeout"
        )

        record = self.logger.session_records[0]
        self.assertFalse(record.success)
        self.assertEqual(record.error_msg, "Connection timeout")

    def test_query_truncation(self):
        """Test long queries are truncated for privacy"""
        long_query = "a" * 200

        self.logger.log_api_call(
            user_role="user",
            operation="OK ASK",
            api_type="gemini",
            query=long_query
        )

        record = self.logger.session_records[0]
        self.assertLessEqual(len(record.query), 103)  # 100 chars + "..."
        self.assertTrue(record.query.endswith("..."))

    def test_text_log_writing(self):
        """Test text log file is written"""
        self.logger.log_api_call(
            user_role="wizard",
            operation="OK ASK",
            api_type="gemini",
            query="Test",
            tokens_used=100,
            cost_estimate=0.0003
        )

        # Check file exists and has content
        self.assertTrue(self.logger.audit_file.exists())
        content = self.logger.audit_file.read_text()
        self.assertIn("OK ASK", content)
        self.assertIn("wizard", content)
        self.assertIn("Test", content)

    def test_json_log_writing(self):
        """Test JSON log file is written"""
        self.logger.log_api_call(
            user_role="user",
            operation="OK DEV",
            api_type="gemini",
            query="Debug error"
        )

        # Check JSON file
        self.assertTrue(self.logger.audit_json.exists())
        with open(self.logger.audit_json, 'r') as f:
            data = json.load(f)

        self.assertIn('records', data)
        self.assertGreater(len(data['records']), 0)

        # Find our specific record (may have others from previous tests)
        our_record = None
        for record in data['records']:
            if record.get('operation') == "OK DEV" and record.get('query') == "Debug error":
                our_record = record
                break

        self.assertIsNotNone(our_record, "Should find our test record")
        self.assertEqual(our_record['operation'], "OK DEV")
        self.assertEqual(our_record['user_role'], "user")

    def test_session_summary(self):
        """Test session summary calculation"""
        # Log multiple calls
        for i in range(5):
            self.logger.log_api_call(
                user_role="wizard",
                operation="OK ASK",
                api_type="gemini",
                query=f"Question {i}",
                tokens_used=100 + i * 10,
                cost_estimate=0.0003 + i * 0.0001
            )

        # Add one failed call
        self.logger.log_api_call(
            user_role="user",
            operation="OK ASK",
            api_type="gemini",
            query="Failed query",
            success=False
        )

        summary = self.logger.get_session_summary()

        self.assertEqual(summary['total_calls'], 6)
        self.assertEqual(summary['total_tokens'], 100 + 110 + 120 + 130 + 140)  # Sum of successful calls
        self.assertAlmostEqual(summary['success_rate'], 5/6, places=2)
        self.assertIn('OK ASK', summary['by_operation'])
        self.assertIn('gemini', summary['by_api'])

    def test_format_session_summary(self):
        """Test formatted session summary"""
        self.logger.log_api_call(
            user_role="wizard",
            operation="OK ASK",
            api_type="gemini",
            query="Test",
            tokens_used=150,
            cost_estimate=0.00045
        )

        formatted = self.logger.format_session_summary()

        self.assertIn("API Usage Summary", formatted)
        self.assertIn("Total Calls:", formatted)
        self.assertIn("Total Tokens:", formatted)
        self.assertIn("Estimated Cost:", formatted)
        self.assertIn("OK ASK", formatted)

    def test_empty_session_summary(self):
        """Test summary with no API calls"""
        summary = self.logger.get_session_summary()

        self.assertEqual(summary['total_calls'], 0)
        self.assertEqual(summary['total_tokens'], 0)
        self.assertEqual(summary['total_cost'], 0.0)
        self.assertEqual(summary['success_rate'], 0.0)

    def test_convenience_function(self):
        """Test convenience log_api_call function"""
        log_api_call(
            user_role="wizard",
            operation="OK ASK",
            api_type="gemini",
            query="Convenience test",
            tokens=200,
            cost=0.0006
        )

        # Should create logger instance
        logger = get_audit_logger()
        self.assertIsNotNone(logger)

        # Should have logged the call
        found = any(
            record.query == "Convenience test"
            for record in logger.session_records
        )
        self.assertTrue(found, "API call should be logged")

    def test_multiple_operations(self):
        """Test tracking multiple operation types"""
        operations = ["OK ASK", "OK DEV", "FETCH", "OK ASK"]

        for op in operations:
            self.logger.log_api_call(
                user_role="wizard",
                operation=op,
                api_type="gemini",
                query="Test"
            )

        summary = self.logger.get_session_summary()
        self.assertEqual(summary['by_operation']['OK ASK'], 2)
        self.assertEqual(summary['by_operation']['OK DEV'], 1)
        self.assertEqual(summary['by_operation']['FETCH'], 1)


class TestAPICallRecord(unittest.TestCase):
    """Test APICallRecord dataclass"""

    def test_record_creation(self):
        """Test creating an API call record"""
        record = APICallRecord(
            timestamp="2025-11-23T15:00:00",
            user_role="wizard",
            operation="OK ASK",
            api_type="gemini",
            query="Test query",
            tokens_used=150,
            cost_estimate=0.00045,
            success=True
        )

        self.assertEqual(record.user_role, "wizard")
        self.assertEqual(record.operation, "OK ASK")
        self.assertTrue(record.success)

    def test_record_to_dict(self):
        """Test converting record to dictionary"""
        record = APICallRecord(
            timestamp="2025-11-23T15:00:00",
            user_role="user",
            operation="OK ASK",
            api_type="gemini",
            query="Test",
            success=True
        )

        d = record.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d['user_role'], "user")
        self.assertNotIn('error_msg', d)  # None values excluded


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
