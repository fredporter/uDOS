"""
Tests for v1.0.23 Phase 8 - UI/UX Polish
Tests error handler, help system, and progress indicators

Author: uDOS Development Team
Version: 1.0.23
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
import sys
from io import StringIO

# Import components to test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.utils.error_handler import EnhancedErrorHandler, ErrorContext
from core.ui.progress_indicators import (
    ProgressBar, Spinner, MultiStageProgress, ProgressIndicators
)


class TestEnhancedErrorHandler(unittest.TestCase):
    """Test enhanced error handler"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EnhancedErrorHandler()

    def test_file_not_found_with_suggestions(self):
        """Test file not found error with similar file suggestions"""
        available = ['README.md', 'ROADMAP.md', 'LICENSE.txt']
        result = self.handler.file_not_found('READMI.md', available)

        self.assertIn('README.md', result)
        self.assertIn('READMI.md', result)
        self.assertIn('Did you mean', result)

    def test_file_not_found_no_suggestions(self):
        """Test file not found error without suggestions"""
        available = ['config.json', 'data.csv']
        result = self.handler.file_not_found('missing.txt', available)

        self.assertIn('missing.txt', result)
        self.assertIn('not found', result.lower())

    def test_command_not_found_with_suggestions(self):
        """Test command not found with similar command suggestions"""
        available = ['DOCS', 'DOC', 'LEARN', 'MEMORY']
        result = self.handler.command_not_found('doc', available)

        self.assertIn('DOC', result)
        self.assertIn('Did you mean', result)

    def test_permission_denied_private(self):
        """Test permission denied for private memory"""
        result = self.handler.permission_denied(
            'secrets.txt',
            required_tier='private',
            current_tier='shared'
        )

        self.assertIn('secrets.txt', result)
        self.assertIn('private', result.lower())
        self.assertIn('shared', result.lower())

    def test_permission_denied_with_upgrade_path(self):
        """Test permission denied with upgrade instructions"""
        result = self.handler.permission_denied(
            'admin.conf',
            required_tier='admin',
            current_tier='user'
        )

        self.assertIn('admin.conf', result)
        self.assertIn('upgrade', result.lower() or result)

    def test_invalid_argument_with_valid_values(self):
        """Test invalid argument error with valid options"""
        valid = ['private', 'shared', 'community', 'public']
        result = self.handler.invalid_argument(
            'tier',
            'privat',  # typo
            valid_values=valid
        )

        self.assertIn('tier', result)
        self.assertIn('privat', result)
        self.assertIn('private', result)  # Should suggest correct value

    def test_syntax_error_with_example(self):
        """Test syntax error with code example"""
        result = self.handler.syntax_error(
            'MEMORY',
            'MEMORY invalid syntax',
            expected_format='MEMORY <tier> <file>',
            example='MEMORY private notes.txt'
        )

        self.assertIn('MEMORY', result)
        self.assertIn('MEMORY <tier> <file>', result)
        self.assertIn('MEMORY private notes.txt', result)

    def test_timeout_error_with_retry(self):
        """Test timeout error with retry suggestion"""
        result = self.handler.timeout_error(
            'download_data',
            timeout_seconds=30,
            suggestion='Try increasing timeout or checking network'
        )

        self.assertIn('download_data', result)
        self.assertIn('30', result)
        self.assertIn('timeout', result.lower())


class TestProgressBar(unittest.TestCase):
    """Test progress bar functionality"""

    @patch('sys.stdout', new_callable=StringIO)
    def test_progress_bar_creation(self, mock_stdout):
        """Test progress bar initialization"""
        bar = ProgressBar(total=100, title="Test")
        self.assertEqual(bar.total, 100)
        self.assertEqual(bar.title, "Test")
        self.assertEqual(bar.current, 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_progress_bar_update(self, mock_stdout):
        """Test progress bar update"""
        bar = ProgressBar(total=10, title="Test")
        bar.update(current=5)
        self.assertEqual(bar.current, 5)

        output = mock_stdout.getvalue()
        self.assertIn('50%', output)
        self.assertIn('5/10', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_progress_bar_increment(self, mock_stdout):
        """Test progress bar increment"""
        bar = ProgressBar(total=10, title="Test")
        bar.update(increment=1)
        bar.update(increment=2)
        self.assertEqual(bar.current, 3)

    @patch('sys.stdout', new_callable=StringIO)
    def test_progress_bar_completion(self, mock_stdout):
        """Test progress bar completion"""
        bar = ProgressBar(total=10, title="Test")
        bar.finish()

        self.assertEqual(bar.current, bar.total)
        output = mock_stdout.getvalue()
        self.assertIn('100%', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_progress_bar_eta_format(self, mock_stdout):
        """Test ETA formatting"""
        bar = ProgressBar(total=100)

        # Test seconds
        self.assertEqual(bar._format_time(45), "45s")

        # Test minutes
        self.assertEqual(bar._format_time(90), "1m 30s")

        # Test hours
        self.assertEqual(bar._format_time(3661), "1h 1m")


class TestSpinner(unittest.TestCase):
    """Test spinner functionality"""

    @patch('sys.stdout', new_callable=StringIO)
    def test_spinner_creation(self, mock_stdout):
        """Test spinner initialization"""
        spinner = Spinner(title="Loading", style='dots')
        self.assertEqual(spinner.title, "Loading")
        self.assertIsNotNone(spinner.frames)

    @patch('sys.stdout', new_callable=StringIO)
    def test_spinner_styles(self, mock_stdout):
        """Test different spinner styles"""
        styles = ['dots', 'line', 'arrow', 'blocks', 'simple']

        for style in styles:
            spinner = Spinner(style=style)
            self.assertIsNotNone(spinner.frames)
            self.assertGreater(len(spinner.frames), 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_spinner_spin(self, mock_stdout):
        """Test spinner animation"""
        spinner = Spinner(title="Test")
        spinner.spin()

        output = mock_stdout.getvalue()
        self.assertIn('Test', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_spinner_stop(self, mock_stdout):
        """Test spinner stop with message"""
        spinner = Spinner()
        spinner.stop("Complete")

        output = mock_stdout.getvalue()
        self.assertIn('Complete', output)
        self.assertIn('✓', output)


class TestMultiStageProgress(unittest.TestCase):
    """Test multi-stage progress tracker"""

    @patch('builtins.print')
    def test_multi_stage_creation(self, mock_print):
        """Test multi-stage progress initialization"""
        stages = ["Stage 1", "Stage 2", "Stage 3"]
        progress = MultiStageProgress(stages)

        self.assertEqual(progress.total_stages, 3)
        self.assertEqual(progress.stages, stages)

    @patch('builtins.print')
    def test_start_stage(self, mock_print):
        """Test starting a stage"""
        stages = ["Stage 1", "Stage 2"]
        progress = MultiStageProgress(stages)
        progress.start_stage(0)

        self.assertIn(0, progress.stage_progress)
        self.assertEqual(progress.stage_progress[0]['status'], 'in_progress')

    @patch('builtins.print')
    def test_complete_stage(self, mock_print):
        """Test completing a stage"""
        stages = ["Stage 1", "Stage 2"]
        progress = MultiStageProgress(stages)
        progress.start_stage(0)
        progress.complete_stage(0)

        self.assertEqual(progress.stage_progress[0]['status'], 'complete')
        self.assertIn('end_time', progress.stage_progress[0])

    @patch('builtins.print')
    def test_render_output(self, mock_print):
        """Test render output format"""
        stages = ["Stage 1"]
        progress = MultiStageProgress(stages)
        progress.start_stage(0)
        output = progress.render()

        self.assertIn('PROGRESS', output)
        self.assertIn('Stage 1', output)


class TestProgressIndicators(unittest.TestCase):
    """Test unified progress indicators"""

    @patch('sys.stdout', new_callable=StringIO)
    def test_create_bar(self, mock_stdout):
        """Test creating progress bar via factory"""
        bar = ProgressIndicators.bar(100, "Test")
        self.assertIsInstance(bar, ProgressBar)
        self.assertEqual(bar.total, 100)

    @patch('sys.stdout', new_callable=StringIO)
    def test_create_spinner(self, mock_stdout):
        """Test creating spinner via factory"""
        spinner = ProgressIndicators.spinner("Loading")
        self.assertIsInstance(spinner, Spinner)
        self.assertEqual(spinner.title, "Loading")

    @patch('builtins.print')
    def test_create_multi_stage(self, mock_print):
        """Test creating multi-stage progress via factory"""
        stages = ["A", "B", "C"]
        progress = ProgressIndicators.multi_stage(stages)
        self.assertIsInstance(progress, MultiStageProgress)
        self.assertEqual(progress.total_stages, 3)

    def test_simple_progress(self):
        """Test simple progress indicator"""
        result = ProgressIndicators.simple_progress(50, 100, prefix="Files: ")
        self.assertIn('50/100', result)
        self.assertIn('50%', result)
        self.assertIn('Files:', result)

    def test_download_progress(self):
        """Test download progress indicator"""
        # 50 MB downloaded out of 100 MB at 10 MB/s
        bytes_down = 50 * 1024 * 1024
        bytes_total = 100 * 1024 * 1024
        speed = 10 * 1024 * 1024

        result = ProgressIndicators.download_progress(bytes_down, bytes_total, speed)
        self.assertIn('50.00', result)  # MB downloaded
        self.assertIn('100.00', result)  # Total MB
        self.assertIn('50%', result)
        self.assertIn('10.00', result)  # Speed

    def test_file_processing_progress(self):
        """Test file processing progress"""
        result = ProgressIndicators.file_processing_progress(
            25, 100, current_file='test.txt'
        )
        self.assertIn('25/100', result)
        self.assertIn('25%', result)
        self.assertIn('test.txt', result)


class TestErrorContextSuggestions(unittest.TestCase):
    """Test error context and suggestion quality"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EnhancedErrorHandler()

    def test_memory_tier_suggestions(self):
        """Test memory tier guidance in errors"""
        result = self.handler.invalid_argument(
            'tier',
            'pubic',  # typo of public
            valid_values=['private', 'shared', 'community', 'public']
        )

        self.assertIn('public', result)  # Should suggest correct tier

    def test_common_command_typos(self):
        """Test suggestions for common command typos"""
        available = ['DOCS', 'LEARN', 'MEMORY', 'VIEW', 'EDIT']

        test_cases = [
            ('doc', 'DOCS'),
            ('lern', 'LEARN'),
            ('mem', 'MEMORY'),
            ('viw', 'VIEW'),
        ]

        for typo, expected in test_cases:
            result = self.handler.command_not_found(typo, available)
            self.assertIn(expected, result, f"Should suggest {expected} for {typo}")

    def test_file_extension_awareness(self):
        """Test file extension in suggestions"""
        available = ['config.json', 'config.yaml', 'settings.ini']
        result = self.handler.file_not_found('config', available)

        # Should suggest files that start with 'config'
        self.assertIn('config', result.lower())


if __name__ == '__main__':
    unittest.main()
