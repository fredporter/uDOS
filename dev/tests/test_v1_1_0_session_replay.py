"""
uDOS v1.1.0 - Session Replay & Analysis Tests

Comprehensive test suite for Feature 1.1.0.12: Session Replay & Analysis

Test Coverage:
- Session loading and parsing
- Replay step navigation
- Pattern detection
- Error analysis
- UX friction detection
- AI-powered insights
- Report generation

Feature: 1.1.0.12
Version: 1.1.0
Status: Active Development
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from core.services.session_replay import (
    SessionReplayer,
    SessionPatternAnalyzer,
    ReplayStep,
    PatternInsight,
    replay_session,
    analyze_session_file,
    list_sessions
)


class TestSessionReplayer(unittest.TestCase):
    """Test SessionReplayer basic functionality"""

    def setUp(self):
        """Create temporary session directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.replayer = SessionReplayer(session_dir=self.temp_dir)

        # Create sample session file
        self.session_data = {
            "session_id": "session_20251124_100000",
            "started_at": "2025-11-24T10:00:00",
            "commands": [
                {
                    "timestamp": "2025-11-24T10:00:05",
                    "command": "MAP",
                    "params": ["CREATE"],
                    "duration_ms": 150.5,
                    "success": True
                },
                {
                    "timestamp": "2025-11-24T10:00:10",
                    "command": "LEARN",
                    "params": [],
                    "duration_ms": 75.2,
                    "success": True
                },
                {
                    "timestamp": "2025-11-24T10:00:15",
                    "command": "DOCS",
                    "params": ["INVALID"],
                    "duration_ms": 50.0,
                    "success": False,
                    "error_type": "CommandError",
                    "error_msg": "Invalid documentation topic"
                }
            ],
            "errors": [
                {
                    "timestamp": "2025-11-24T10:00:15",
                    "command": "DOCS",
                    "params": ["INVALID"],
                    "error_type": "CommandError",
                    "error_msg": "Invalid documentation topic",
                    "context": {}
                }
            ],
            "feedback": [],
            "metadata": {
                "total_commands": 3,
                "total_errors": 1
            }
        }

        self.session_file = Path(self.temp_dir) / "session_20251124_100000.json"
        with open(self.session_file, 'w') as f:
            json.dump(self.session_data, f)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_load_session_success(self):
        """Test successful session loading"""
        result = self.replayer.load_session("session_20251124_100000")
        self.assertTrue(result)
        self.assertEqual(len(self.replayer.replay_steps), 3)
        self.assertEqual(self.replayer.current_step, 0)

    def test_load_session_with_extension(self):
        """Test loading session with .json extension"""
        result = self.replayer.load_session("session_20251124_100000.json")
        self.assertTrue(result)
        self.assertEqual(len(self.replayer.replay_steps), 3)

    def test_load_session_not_found(self):
        """Test loading non-existent session"""
        result = self.replayer.load_session("session_99999999_999999")
        self.assertFalse(result)
        self.assertEqual(len(self.replayer.replay_steps), 0)

    def test_replay_step_structure(self):
        """Test ReplayStep creation and structure"""
        self.replayer.load_session("session_20251124_100000")

        step = self.replayer.get_step(0)
        self.assertIsNotNone(step)
        self.assertEqual(step.index, 0)
        self.assertEqual(step.command, "MAP")
        self.assertEqual(step.params, ["CREATE"])
        self.assertTrue(step.success)

    def test_navigation_next(self):
        """Test next step navigation"""
        self.replayer.load_session("session_20251124_100000")

        step = self.replayer.next_step()
        self.assertIsNotNone(step)
        self.assertEqual(step.command, "LEARN")
        self.assertEqual(self.replayer.current_step, 1)

    def test_navigation_previous(self):
        """Test previous step navigation"""
        self.replayer.load_session("session_20251124_100000")
        self.replayer.current_step = 2

        step = self.replayer.previous_step()
        self.assertIsNotNone(step)
        self.assertEqual(step.command, "LEARN")
        self.assertEqual(self.replayer.current_step, 1)

    def test_navigation_jump_to(self):
        """Test jump to specific step"""
        self.replayer.load_session("session_20251124_100000")

        step = self.replayer.jump_to(2)
        self.assertIsNotNone(step)
        self.assertEqual(step.command, "DOCS")
        self.assertEqual(self.replayer.current_step, 2)

    def test_navigation_bounds(self):
        """Test navigation boundary conditions"""
        self.replayer.load_session("session_20251124_100000")

        # At start, previous returns None
        self.replayer.current_step = 0
        self.assertIsNone(self.replayer.previous_step())

        # At end, next returns None
        self.replayer.current_step = 2
        self.assertIsNone(self.replayer.next_step())

        # Invalid jump returns None
        self.assertIsNone(self.replayer.jump_to(999))
        self.assertIsNone(self.replayer.jump_to(-1))


class TestSessionAnalysis(unittest.TestCase):
    """Test session analysis and statistics"""

    def setUp(self):
        """Create temporary session directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.replayer = SessionReplayer(session_dir=self.temp_dir)

        # Create comprehensive session with various patterns
        self.session_data = {
            "session_id": "session_20251124_110000",
            "started_at": "2025-11-24T11:00:00",
            "commands": [
                {"timestamp": "2025-11-24T11:00:01", "command": "MAP", "params": ["CREATE"], "duration_ms": 150, "success": True},
                {"timestamp": "2025-11-24T11:00:02", "command": "LEARN", "params": [], "duration_ms": 75, "success": True},
                {"timestamp": "2025-11-24T11:00:03", "command": "DOCS", "params": ["INVALID"], "duration_ms": 50, "success": False, "error_type": "CommandError"},
                {"timestamp": "2025-11-24T11:00:04", "command": "MEMORY", "params": ["-p", "TEST"], "duration_ms": 2500, "success": True},  # Slow
                {"timestamp": "2025-11-24T11:00:05", "command": "MAP", "params": ["VIEW"], "duration_ms": 100, "success": True},
                {"timestamp": "2025-11-24T11:00:06", "command": "DOCS", "params": ["GUIDE"], "duration_ms": 1500, "success": True},  # Slow
            ],
            "errors": [
                {"timestamp": "2025-11-24T11:00:03", "command": "DOCS", "params": ["INVALID"], "error_type": "CommandError", "error_msg": "Invalid topic", "context": {}}
            ],
            "feedback": [],
            "performance": {},
            "metadata": {"total_commands": 6, "total_errors": 1}
        }

        self.session_file = Path(self.temp_dir) / "session_20251124_110000.json"
        with open(self.session_file, 'w') as f:
            json.dump(self.session_data, f)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)

    def test_find_errors(self):
        """Test finding error steps"""
        self.replayer.load_session("session_20251124_110000")

        errors = self.replayer.find_errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].command, "DOCS")
        self.assertEqual(errors[0].error_type, "CommandError")

    def test_find_slow_commands(self):
        """Test finding slow commands"""
        self.replayer.load_session("session_20251124_110000")

        slow = self.replayer.find_slow_commands(threshold_ms=1000)
        self.assertEqual(len(slow), 2)  # MEMORY and DOCS
        commands = [step.command for step in slow]
        self.assertIn("MEMORY", commands)
        self.assertIn("DOCS", commands)

    def test_find_command_sequence(self):
        """Test finding command sequences"""
        self.replayer.load_session("session_20251124_110000")

        # Find MAP -> LEARN sequence
        matches = self.replayer.find_command_sequence(["MAP", "LEARN"])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], 0)

    def test_get_session_stats(self):
        """Test session statistics calculation"""
        self.replayer.load_session("session_20251124_110000")

        stats = self.replayer.get_session_stats()
        self.assertEqual(stats['total_commands'], 6)
        self.assertEqual(stats['total_errors'], 1)
        self.assertAlmostEqual(stats['error_rate'], 1/6, places=2)
        self.assertEqual(stats['slow_commands'], 2)

        # Check most used commands
        most_used = dict(stats['most_used_commands'])
        self.assertEqual(most_used['MAP'], 2)

    def test_list_available_sessions(self):
        """Test listing available sessions"""
        sessions = self.replayer.list_available_sessions()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['session_id'], 'session_20251124_110000')
        self.assertEqual(sessions[0]['total_commands'], 6)


class TestPatternDetection(unittest.TestCase):
    """Test pattern detection and analysis"""

    def setUp(self):
        """Set up pattern analyzer with mock Gemini service"""
        self.mock_gemini = Mock()
        self.analyzer = SessionPatternAnalyzer(gemini_service=self.mock_gemini)
        self.analyzer.gemini_available = False  # Disable AI for unit tests

    def test_error_pattern_detection(self):
        """Test detection of repeated error patterns"""
        session_data = {
            "session_id": "test_session",
            "commands": [],
            "errors": [
                {"error_type": "ValueError", "command": "MAP", "params": []},
                {"error_type": "ValueError", "command": "MAP", "params": []},
                {"error_type": "ValueError", "command": "MAP", "params": []},
            ],
            "feedback": [],
            "performance": {}
        }

        insights = self.analyzer.analyze_session(session_data)

        # Should detect pattern of 3+ repeated ValueError errors
        error_patterns = [i for i in insights if i.category == 'error_pattern']
        self.assertGreater(len(error_patterns), 0)
        self.assertIn('ValueError', error_patterns[0].description)

    def test_confusion_point_detection(self):
        """Test detection of user confusion points"""
        session_data = {
            "session_id": "test_session",
            "commands": [
                {"command": "LEARN", "params": [], "success": False, "error_type": "ValueError"},
                {"command": "HELP", "params": [], "success": True}  # Help after error
            ],
            "errors": [],
            "feedback": [
                {"type": "confusion", "message": "I don't understand this", "command_context": "LEARN"}
            ],
            "performance": {}
        }

        insights = self.analyzer.analyze_session(session_data)

        # Should detect confusion from both help-seeking and feedback
        confusion = [i for i in insights if i.category == 'confusion_point']
        self.assertGreater(len(confusion), 0)

    def test_ux_friction_repeated_commands(self):
        """Test detection of UX friction from repeated commands"""
        session_data = {
            "session_id": "test_session",
            "commands": [
                {"command": "SAVE", "params": [], "success": True, "duration_ms": 100},
                {"command": "SAVE", "params": [], "success": True, "duration_ms": 100},
                {"command": "SAVE", "params": [], "success": True, "duration_ms": 100},
            ],
            "errors": [],
            "feedback": [],
            "performance": {}
        }

        insights = self.analyzer.analyze_session(session_data)

        # Should detect repeated SAVE commands as potential friction
        friction = [i for i in insights if i.category == 'ux_friction']
        self.assertGreater(len(friction), 0)
        self.assertIn('SAVE', friction[0].description)

    def test_ux_friction_slow_commands(self):
        """Test detection of slow command patterns"""
        session_data = {
            "session_id": "test_session",
            "commands": [
                {"command": "SEARCH", "params": ["test"], "success": True, "duration_ms": 2500},
                {"command": "LEARN", "params": [], "success": True, "duration_ms": 100},
                {"command": "SEARCH", "params": ["data"], "success": True, "duration_ms": 2200},
                {"command": "MAP", "params": [], "success": True, "duration_ms": 50},
                {"command": "SEARCH", "params": ["info"], "success": True, "duration_ms": 2800},
                {"command": "DOCS", "params": [], "success": True, "duration_ms": 75},
                {"command": "SEARCH", "params": ["help"], "success": True, "duration_ms": 2100},
            ],
            "errors": [],
            "feedback": [],
            "performance": {}
        }

        insights = self.analyzer.analyze_session(session_data)

        # Should detect slow SEARCH commands
        friction = [i for i in insights if i.category == 'ux_friction']
        self.assertGreater(len(friction), 0)

        # Look for slow command insight (may be first or second depending on repetition detection)
        slow_insight = None
        for f in friction:
            if 'slow' in f.description.lower():
                slow_insight = f
                break

        self.assertIsNotNone(slow_insight)
        self.assertIn('SEARCH', slow_insight.description)

    def test_severity_sorting(self):
        """Test insights sorted by severity"""
        session_data = {
            "session_id": "test_session",
            "commands": [],
            "errors": [
                {"error_type": "CriticalError", "command": "SYS", "params": []},
                {"error_type": "CriticalError", "command": "SYS", "params": []},
                {"error_type": "CriticalError", "command": "SYS", "params": []},
                {"error_type": "CriticalError", "command": "SYS", "params": []},
                {"error_type": "CriticalError", "command": "SYS", "params": []},  # 5+ = high severity
            ],
            "feedback": [],
            "performance": {}
        }

        insights = self.analyzer.analyze_session(session_data)

        # First insight should be high severity
        if insights:
            self.assertEqual(insights[0].severity, 'high')


class TestReportGeneration(unittest.TestCase):
    """Test report generation and formatting"""

    def setUp(self):
        """Set up analyzer"""
        self.mock_gemini = Mock()
        self.analyzer = SessionPatternAnalyzer(gemini_service=self.mock_gemini)
        self.analyzer.gemini_available = False

    def test_generate_empty_report(self):
        """Test report generation for clean session"""
        session_data = {
            "session_id": "clean_session",
            "started_at": "2025-11-24T12:00:00",
            "commands": [
                {"command": "MAP", "params": [], "success": True, "duration_ms": 50}
            ],
            "errors": [],
            "feedback": [],
            "performance": {}
        }

        report = self.analyzer.generate_report(session_data)

        self.assertIn("Session Pattern Analysis Report", report)
        self.assertIn("clean_session", report)
        self.assertIn("No significant issues", report)

    def test_generate_detailed_report(self):
        """Test report generation with multiple insights"""
        session_data = {
            "session_id": "problem_session",
            "started_at": "2025-11-24T12:00:00",
            "commands": [
                {"command": "MAP", "params": [], "success": False, "duration_ms": 50, "error_type": "ValueError"},
                {"command": "MAP", "params": [], "success": False, "duration_ms": 50, "error_type": "ValueError"},
                {"command": "MAP", "params": [], "success": False, "duration_ms": 50, "error_type": "ValueError"},
                {"command": "HELP", "params": [], "success": True, "duration_ms": 30},
            ],
            "errors": [
                {"error_type": "ValueError", "command": "MAP", "params": [], "error_msg": "Test", "context": {}},
                {"error_type": "ValueError", "command": "MAP", "params": [], "error_msg": "Test", "context": {}},
                {"error_type": "ValueError", "command": "MAP", "params": [], "error_msg": "Test", "context": {}},
            ],
            "feedback": [
                {"type": "confusion", "message": "Confused about MAP", "command_context": "MAP"}
            ],
            "performance": {}
        }

        report = self.analyzer.generate_report(session_data)

        self.assertIn("Session Pattern Analysis Report", report)
        self.assertIn("problem_session", report)
        self.assertIn("Error Pattern", report)
        self.assertIn("Confusion Point", report)
        self.assertIn("ValueError", report)


class TestStepFormatting(unittest.TestCase):
    """Test replay step formatting"""

    def setUp(self):
        """Create replayer with test data"""
        self.temp_dir = tempfile.mkdtemp()
        self.replayer = SessionReplayer(session_dir=self.temp_dir)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    def test_format_successful_step(self):
        """Test formatting successful step"""
        step = ReplayStep(
            index=0,
            timestamp="2025-11-24T10:00:00",
            command="MAP",
            params=["CREATE"],
            duration_ms=150.5,
            success=True
        )

        formatted = self.replayer.format_step(step)

        self.assertIn("✅", formatted)
        self.assertIn("MAP", formatted)
        self.assertIn("CREATE", formatted)
        self.assertIn("150ms", formatted)

    def test_format_failed_step(self):
        """Test formatting failed step"""
        step = ReplayStep(
            index=1,
            timestamp="2025-11-24T10:00:05",
            command="DOCS",
            params=["INVALID"],
            duration_ms=50.0,
            success=False,
            error_type="CommandError",
            error_msg="Invalid topic"
        )

        formatted = self.replayer.format_step(step)

        self.assertIn("❌", formatted)
        self.assertIn("DOCS", formatted)
        self.assertIn("CommandError", formatted)
        self.assertIn("Invalid topic", formatted)

    def test_format_step_with_context(self):
        """Test formatting step with context"""
        step = ReplayStep(
            index=2,
            timestamp="2025-11-24T10:00:10",
            command="LEARN",
            params=[],
            duration_ms=100.0,
            success=True,
            context={"panel": "main", "role": "user"}
        )

        formatted = self.replayer.format_step(step, show_context=True)

        self.assertIn("Context:", formatted)
        self.assertIn("panel", formatted)
        self.assertIn("role", formatted)


class TestAIAnalysis(unittest.TestCase):
    """Test AI-powered pattern analysis"""

    def setUp(self):
        """Set up analyzer with mock Gemini"""
        self.mock_gemini = Mock()
        self.analyzer = SessionPatternAnalyzer(gemini_service=self.mock_gemini)

    def test_ai_analysis_enabled(self):
        """Test AI analysis when Gemini available"""
        self.mock_gemini.ask.return_value = '''[{
                "category": "feature_gap",
                "severity": "medium",
                "description": "User attempted batch operations",
                "evidence": ["MAP CREATE", "MAP CREATE", "MAP CREATE"],
                "suggestion": "Add BATCH MAP command",
                "impact": "Reduced repetitive typing"
            }]'''
        self.analyzer.gemini_available = True

        session_data = {
            "session_id": "test",
            "commands": [{"command": "MAP", "params": ["CREATE"], "success": True, "duration_ms": 100}],
            "errors": [],
            "feedback": [],
            "performance": {}
        }

        insights = self.analyzer.analyze_session(session_data)

        # Should include AI-generated insight
        feature_gaps = [i for i in insights if i.category == 'feature_gap']
        self.assertGreater(len(feature_gaps), 0)
        self.assertIn("batch", feature_gaps[0].description.lower())

    def test_ai_analysis_disabled(self):
        """Test fallback when AI unavailable"""
        self.analyzer.gemini_available = False

        session_data = {
            "session_id": "test",
            "commands": [{"command": "MAP", "params": [], "success": True, "duration_ms": 50}],
            "errors": [],
            "feedback": [],
            "performance": {}
        }

        insights = self.analyzer.analyze_session(session_data)

        # Should still work with local pattern detection only
        self.assertIsInstance(insights, list)

    def test_ai_analysis_error_handling(self):
        """Test graceful degradation when AI fails"""
        self.mock_gemini.ask.side_effect = Exception("API Error")
        self.analyzer.gemini_available = True

        session_data = {
            "session_id": "test",
            "commands": [],
            "errors": [],
            "feedback": [],
            "performance": {}
        }

        # Should not raise exception
        insights = self.analyzer.analyze_session(session_data)
        self.assertIsInstance(insights, list)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def setUp(self):
        """Create temporary directory"""
        self.temp_dir = tempfile.mkdtemp()

        # Create test session
        session_data = {
            "session_id": "test_session",
            "started_at": "2025-11-24T10:00:00",
            "commands": [{"command": "MAP", "params": [], "success": True, "duration_ms": 50}],
            "errors": [],
            "feedback": [],
            "metadata": {"total_commands": 1}
        }

        session_file = Path(self.temp_dir) / "test_session.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)

    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir)

    @patch('core.services.session_replay.SessionReplayer')
    def test_replay_session_function(self, mock_replayer_class):
        """Test replay_session convenience function"""
        mock_instance = Mock()
        mock_instance.load_session.return_value = True
        mock_replayer_class.return_value = mock_instance

        result = replay_session("test_session")

        self.assertIsNotNone(result)
        mock_instance.load_session.assert_called_once_with("test_session")

    def test_analyze_session_file_function(self):
        """Test analyze_session_file convenience function"""
        session_file = Path(self.temp_dir) / "test_session.json"

        report = analyze_session_file(str(session_file))

        self.assertIsInstance(report, str)
        self.assertIn("Session Pattern Analysis", report)

    @patch('core.services.session_replay.SessionReplayer')
    def test_list_sessions_function(self, mock_replayer_class):
        """Test list_sessions convenience function"""
        mock_instance = Mock()
        mock_instance.list_available_sessions.return_value = [
            {"session_id": "test", "total_commands": 1}
        ]
        mock_replayer_class.return_value = mock_instance

        sessions = list_sessions()

        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['session_id'], 'test')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_empty_session(self):
        """Test handling empty session"""
        temp_dir = tempfile.mkdtemp()
        try:
            replayer = SessionReplayer(session_dir=temp_dir)

            # Create empty session
            empty_session = {
                "session_id": "empty",
                "commands": [],
                "errors": [],
                "feedback": [],
                "metadata": {}
            }

            session_file = Path(temp_dir) / "empty.json"
            with open(session_file, 'w') as f:
                json.dump(empty_session, f)

            result = replayer.load_session("empty")
            self.assertTrue(result)
            self.assertEqual(len(replayer.replay_steps), 0)

            # Navigation should handle empty gracefully
            self.assertIsNone(replayer.get_step())
            self.assertIsNone(replayer.next_step())

        finally:
            shutil.rmtree(temp_dir)

    def test_malformed_json(self):
        """Test handling malformed JSON"""
        temp_dir = tempfile.mkdtemp()
        try:
            replayer = SessionReplayer(session_dir=temp_dir)

            # Create malformed JSON file
            session_file = Path(temp_dir) / "malformed.json"
            with open(session_file, 'w') as f:
                f.write("{ invalid json }")

            result = replayer.load_session("malformed")
            self.assertFalse(result)

        finally:
            shutil.rmtree(temp_dir)

    def test_missing_fields(self):
        """Test handling sessions with missing fields"""
        temp_dir = tempfile.mkdtemp()
        try:
            replayer = SessionReplayer(session_dir=temp_dir)

            # Session with minimal fields
            minimal_session = {
                "session_id": "minimal"
            }

            session_file = Path(temp_dir) / "minimal.json"
            with open(session_file, 'w') as f:
                json.dump(minimal_session, f)

            result = replayer.load_session("minimal")
            self.assertTrue(result)
            self.assertEqual(len(replayer.replay_steps), 0)

        finally:
            shutil.rmtree(temp_dir)


def run_test_suite():
    """Run complete test suite with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSessionReplayer))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestPatternDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestStepFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestAIAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

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
