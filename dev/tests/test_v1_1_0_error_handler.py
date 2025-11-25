"""
uDOS v1.1.0 - Intelligent Error Handler Tests

Test suite for AI-powered error handling.

Version: 1.1.0
"""

import unittest
from unittest.mock import Mock, patch
from core.services.intelligent_error_handler import (
    IntelligentErrorHandler,
    get_error_handler,
    handle_command_error
)


class TestIntelligentErrorHandler(unittest.TestCase):
    """Test intelligent error handler functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create mock dependencies
        self.mock_gemini = Mock()
        self.mock_analytics = Mock()
        self.mock_audit = Mock()

        # Create handler with mocks
        self.handler = IntelligentErrorHandler(
            gemini=self.mock_gemini,
            session_analytics=self.mock_analytics,
            audit_logger=self.mock_audit
        )

    def test_handler_initialization(self):
        """Test handler is properly initialized"""
        self.assertIsNotNone(self.handler)
        self.assertEqual(self.handler.user_role, "user")
        self.assertIn('FileNotFoundError', self.handler.error_patterns)
        self.assertIn('ValueError', self.handler.error_patterns)

    def test_error_classification(self):
        """Test error classification patterns"""
        file_error = self.handler.error_patterns['FileNotFoundError']
        self.assertEqual(file_error['category'], 'file_access')
        self.assertEqual(file_error['severity'], 'medium')
        self.assertGreater(len(file_error['common_causes']), 0)
        self.assertGreater(len(file_error['quick_fixes']), 0)

    def test_handle_file_not_found_error(self):
        """Test handling FileNotFoundError"""
        error = FileNotFoundError("test.txt not found")

        error_msg, choice = self.handler.handle_error(
            error=error,
            command="LOAD",
            params=["test.txt"],
            context={"current_dir": "/test"}
        )

        # Check error message format
        self.assertIn("Error in LOAD", error_msg)
        self.assertIn("FileNotFoundError", error_msg)
        self.assertIn("Common Causes:", error_msg)
        self.assertIn("Quick Fixes:", error_msg)

        # Verify analytics was called
        self.mock_analytics.track_error.assert_called_once()
        call_args = self.mock_analytics.track_error.call_args
        self.assertEqual(call_args[1]['command'], "LOAD")
        self.assertEqual(call_args[1]['error_type'], "FileNotFoundError")

    def test_handle_value_error(self):
        """Test handling ValueError"""
        error = ValueError("Invalid map name")

        error_msg, choice = self.handler.handle_error(
            error=error,
            command="MAP",
            params=["CREATE", ""],
            context={}
        )

        self.assertIn("ValueError", error_msg)
        self.assertIn("Invalid map name", error_msg)
        # Should have validation-related fixes
        self.assertIn("validate", error_msg.lower())

    def test_handle_permission_error(self):
        """Test handling PermissionError with high severity"""
        error = PermissionError("Access denied")

        error_msg, choice = self.handler.handle_error(
            error=error,
            command="SAVE",
            params=["protected.txt"],
            context={}
        )

        # Should have high severity indicator
        self.assertIn("❌", error_msg)
        self.assertIn("PermissionError", error_msg)

    def test_handle_unknown_error(self):
        """Test handling unknown error type"""
        class CustomError(Exception):
            pass

        error = CustomError("Something unexpected")

        error_msg, choice = self.handler.handle_error(
            error=error,
            command="TEST",
            params=[],
            context={}
        )

        # Should still handle gracefully
        self.assertIn("Error in TEST", error_msg)
        self.assertIn("CustomError", error_msg)

    def test_format_error_message(self):
        """Test error message formatting"""
        classification = {
            'category': 'test',
            'severity': 'medium',
            'common_causes': ['Cause 1', 'Cause 2'],
            'quick_fixes': ['Fix 1', 'Fix 2']
        }

        formatted = self.handler._format_error_message(
            error_type="TestError",
            error_msg="Test error message",
            command="TEST",
            classification=classification
        )

        self.assertIn("TestError", formatted)
        self.assertIn("Test error message", formatted)
        self.assertIn("Cause 1", formatted)
        self.assertIn("Fix 1", formatted)
        self.assertIn("Options:", formatted)

    def test_error_context_capture(self):
        """Test error context is properly captured"""
        error = ValueError("Test")
        context = {
            'planet': 'Earth',
            'current_panel': 'main',
            'user_role': 'wizard'
        }

        error_msg, choice = self.handler.handle_error(
            error=error,
            command="TEST",
            params=["param1"],
            context=context
        )

        # Verify analytics received full context
        call_args = self.mock_analytics.track_error.call_args
        captured_context = call_args[1]['context']

        self.assertEqual(captured_context['command'], "TEST")
        self.assertEqual(captured_context['planet'], 'Earth')
        self.assertEqual(captured_context['current_panel'], 'main')
        self.assertIn('traceback', captured_context)

    def test_build_ai_prompt(self):
        """Test AI prompt building"""
        error = FileNotFoundError("test.txt")
        context = {
            'classification': {
                'category': 'file_access',
                'severity': 'medium'
            }
        }

        prompt = self.handler._build_ai_prompt(
            error=error,
            command="LOAD",
            params=["test.txt"],
            context=context
        )

        self.assertIn("LOAD", prompt)
        self.assertIn("FileNotFoundError", prompt)
        self.assertIn("test.txt", prompt)
        self.assertIn("file_access", prompt)
        self.assertIn("actionable", prompt.lower())

    def test_format_interactive_prompt_with_retry(self):
        """Test interactive prompt formatting with retry"""
        error_msg = "Test error message"

        prompt = self.handler.format_interactive_prompt(
            error_msg=error_msg,
            allow_retry=True,
            ai_suggestion=None
        )

        self.assertIn("Test error message", prompt)
        self.assertIn("Retry", prompt)
        self.assertIn("Get Help", prompt)
        self.assertIn("Report", prompt)
        self.assertIn("Continue", prompt)

    def test_format_interactive_prompt_with_ai(self):
        """Test interactive prompt with AI suggestion"""
        error_msg = "Test error"
        ai_suggestion = "Try using absolute path"

        prompt = self.handler.format_interactive_prompt(
            error_msg=error_msg,
            allow_retry=True,
            ai_suggestion=ai_suggestion
        )

        self.assertIn("AI Suggestion", prompt)

    def test_format_interactive_prompt_no_retry(self):
        """Test interactive prompt without retry option"""
        error_msg = "Test error"

        prompt = self.handler.format_interactive_prompt(
            error_msg=error_msg,
            allow_retry=False,
            ai_suggestion=None
        )

        # Retry should not be in first option
        self.assertNotIn("1. Retry", prompt)
        self.assertIn("Get Help", prompt)

    def test_severity_icons(self):
        """Test different severity levels use correct icons"""
        classifications = [
            ('low', '💡'),
            ('medium', '⚠️'),
            ('high', '❌'),
            ('critical', '🔴')
        ]

        for severity, expected_icon in classifications:
            classification = {
                'category': 'test',
                'severity': severity,
                'common_causes': [],
                'quick_fixes': []
            }

            formatted = self.handler._format_error_message(
                error_type="TestError",
                error_msg="Test",
                command="TEST",
                classification=classification
            )

            self.assertIn(expected_icon, formatted,
                         f"Should use {expected_icon} for {severity} severity")

    def test_multiple_error_tracking(self):
        """Test tracking multiple errors"""
        errors = [
            (FileNotFoundError("file1.txt"), "LOAD", ["file1.txt"]),
            (ValueError("Invalid"), "MAP", ["CREATE"]),
            (KeyError("missing"), "CONFIG", ["GET"])
        ]

        for error, command, params in errors:
            self.handler.handle_error(error, command, params)

        # Should have tracked all 3 errors
        self.assertEqual(self.mock_analytics.track_error.call_count, 3)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def test_get_error_handler(self):
        """Test getting global error handler instance"""
        handler = get_error_handler()

        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, IntelligentErrorHandler)

        # Should return same instance
        handler2 = get_error_handler()
        self.assertIs(handler, handler2)

    def test_handle_command_error(self):
        """Test convenience error handling function"""
        error = ValueError("Test error")

        result = handle_command_error(
            error=error,
            command="TEST",
            params=["param1", "param2"],
            context={'test': True}
        )

        self.assertIsInstance(result, str)
        self.assertIn("ValueError", result)
        self.assertIn("TEST", result)


class TestErrorPatterns(unittest.TestCase):
    """Test error classification patterns"""

    def setUp(self):
        """Set up test handler"""
        self.handler = IntelligentErrorHandler()

    def test_all_patterns_have_required_fields(self):
        """Test all error patterns have required fields"""
        required_fields = ['category', 'severity', 'common_causes', 'quick_fixes']

        for error_type, pattern in self.handler.error_patterns.items():
            for field in required_fields:
                self.assertIn(field, pattern,
                            f"{error_type} should have {field}")

            # Check lists are not empty
            self.assertGreater(len(pattern['common_causes']), 0,
                             f"{error_type} should have common causes")
            self.assertGreater(len(pattern['quick_fixes']), 0,
                             f"{error_type} should have quick fixes")

    def test_severity_levels(self):
        """Test severity levels are valid"""
        valid_severities = ['low', 'medium', 'high', 'critical']

        for error_type, pattern in self.handler.error_patterns.items():
            severity = pattern['severity']
            self.assertIn(severity, valid_severities,
                        f"{error_type} has invalid severity: {severity}")

    def test_categories(self):
        """Test error categories are consistent"""
        valid_categories = [
            'file_access', 'data_validation', 'data_access',
            'dependency', 'code_error', 'network', 'unknown'
        ]

        for error_type, pattern in self.handler.error_patterns.items():
            category = pattern['category']
            self.assertIn(category, valid_categories,
                        f"{error_type} has invalid category: {category}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
