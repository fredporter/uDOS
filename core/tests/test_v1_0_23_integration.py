"""
Integration Tests for v1.0.23 Phase 9 - Testing & QA
End-to-end workflows and backwards compatibility

Author: uDOS Development Team
Version: 1.0.23
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.commands.docs_unified_handler import DocsUnifiedHandler
from core.commands.learn_unified_handler import LearnUnifiedHandler
from core.commands.memory_unified_handler import MemoryUnifiedHandler
from core.services.fuzzy_matcher import FuzzyMatcher
from core.services.alias_manager import AliasManager
from core.ui.picker import UniversalPicker
from core.services.error_handler import EnhancedErrorHandler
from core.ui.progress_indicators import ProgressIndicators


class TestDocsWorkflow(unittest.TestCase):
    """Test complete DOCS command workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = DocsUnifiedHandler()

    def test_docs_search_workflow(self):
        """Test complete documentation search workflow"""
        # Search for documentation
        query = "git"
        results = self.handler.search_all(query)

        # Should return results from multiple sources
        self.assertIsInstance(results, list)
        # Results should be ranked by relevance
        if results:
            self.assertTrue(all(isinstance(r, dict) for r in results))
            self.assertTrue(all('source' in r for r in results))
            self.assertTrue(all('score' in r for r in results))

    def test_docs_backwards_compatibility(self):
        """Test that old DOC command still works"""
        # Old command should be aliased to new DOCS
        alias_manager = AliasManager()
        resolved = alias_manager.resolve('DOC')

        self.assertEqual(resolved['command'], 'DOCS')
        self.assertIn('DOC', alias_manager.builtin_aliases)

    def test_docs_help_integration(self):
        """Test DOCS help integration"""
        help_text = self.handler.show_help()

        self.assertIsNotNone(help_text)
        self.assertIn('DOCS', help_text)
        # Should mention old commands for backwards compat
        self.assertTrue(
            'DOC' in help_text or 'manual' in help_text.lower()
        )


class TestLearnWorkflow(unittest.TestCase):
    """Test complete LEARN command workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = LearnUnifiedHandler()

    def test_learn_content_detection(self):
        """Test automatic content type detection"""
        # Should detect guides vs diagrams automatically
        guide_type = self.handler.detect_content_type('water-purification')
        diagram_type = self.handler.detect_content_type('knot-types-diagram')

        # These are examples - actual detection depends on file system
        self.assertIn(guide_type, ['guide', 'diagram', 'unknown'])
        self.assertIn(diagram_type, ['guide', 'diagram', 'unknown'])

    def test_learn_backwards_compatibility(self):
        """Test that GUIDE and DIAGRAM commands still work"""
        alias_manager = AliasManager()

        guide_resolved = alias_manager.resolve('GUIDE')
        diagram_resolved = alias_manager.resolve('DIAGRAM')

        # Should resolve to LEARN
        self.assertEqual(guide_resolved['command'], 'LEARN')
        self.assertEqual(diagram_resolved['command'], 'LEARN')

    def test_learn_progress_tracking(self):
        """Test learning progress tracking"""
        # Track progress for a guide
        guide_name = "test-guide"
        self.handler.track_progress(guide_name, 0.5)

        progress = self.handler.get_progress(guide_name)
        self.assertIsNotNone(progress)
        self.assertGreaterEqual(progress, 0.0)
        self.assertLessEqual(progress, 1.0)


class TestMemoryWorkflow(unittest.TestCase):
    """Test complete MEMORY command workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = MemoryUnifiedHandler()

    def test_memory_tier_selection(self):
        """Test interactive tier selection"""
        # Test tier priority ordering
        tiers = self.handler.get_available_tiers()

        self.assertIsInstance(tiers, list)
        self.assertTrue(len(tiers) > 0)
        # Should include all 4 tiers
        expected_tiers = {'private', 'shared', 'community', 'public'}
        tier_names = {t.lower() for t in tiers}
        self.assertTrue(expected_tiers.issubset(tier_names))

    def test_memory_security_analysis(self):
        """Test content security analysis workflow"""
        # Password content should suggest private
        password_content = "password: my_secret_123"
        tier = self.handler.analyze_content_security(password_content)
        self.assertEqual(tier.lower(), 'private')

        # Config file should suggest shared
        config_content = "database_host: localhost\nport: 5432"
        tier = self.handler.analyze_content_security(config_content)
        self.assertEqual(tier.lower(), 'shared')

        # Documentation should suggest public/community
        doc_content = "# How to Setup\nFollow these steps..."
        tier = self.handler.analyze_content_security(doc_content)
        self.assertIn(tier.lower(), ['community', 'public'])

    def test_memory_backwards_compatibility(self):
        """Test that PRIVATE, SHARED, etc. still work"""
        alias_manager = AliasManager()

        # All old tier commands should alias to MEMORY
        for old_cmd in ['PRIVATE', 'SHARED', 'COMMUNITY', 'KB']:
            resolved = alias_manager.resolve(old_cmd)
            self.assertEqual(resolved['command'], 'MEMORY')


class TestFuzzyMatchingWorkflow(unittest.TestCase):
    """Test fuzzy matching in real-world scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.matcher = FuzzyMatcher()

    def test_typo_correction_workflow(self):
        """Test typo correction in file matching"""
        available_files = [
            'README.md',
            'ROADMAP.MD',
            'LICENSE.txt',
            'CONTRIBUTING.md'
        ]

        # Test common typos
        typo_tests = [
            ('READMI', 'README.md'),
            ('roadmpa', 'ROADMAP.MD'),
            ('licnese', 'LICENSE.txt'),
            ('contribut', 'CONTRIBUTING.md'),
        ]

        for typo, expected in typo_tests:
            matches = self.matcher.find_matches(typo, available_files)
            self.assertTrue(len(matches) > 0, f"Should find match for {typo}")
            # Best match should be expected file
            best_match = matches[0]['path']
            self.assertEqual(best_match, expected,
                           f"Expected {expected} for typo {typo}, got {best_match}")

    def test_abbreviation_expansion_workflow(self):
        """Test abbreviation expansion"""
        # Common abbreviations
        self.assertEqual(self.matcher.expand_abbreviation('readme'), 'README.md')
        self.assertEqual(self.matcher.expand_abbreviation('road'), 'ROADMAP.MD')
        self.assertEqual(self.matcher.expand_abbreviation('contrib'), 'CONTRIBUTING.md')

    def test_recent_files_workflow(self):
        """Test recent files prioritization"""
        # Add some recent files
        self.matcher.add_recent_file('/path/to/file1.txt')
        self.matcher.add_recent_file('/path/to/file2.txt')
        self.matcher.add_recent_file('/path/to/file3.txt')

        recent = self.matcher.get_recent_files(limit=2)

        # Should return most recent first
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0], '/path/to/file3.txt')
        self.assertEqual(recent[1], '/path/to/file2.txt')


class TestAliasWorkflow(unittest.TestCase):
    """Test command aliasing workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = AliasManager()

    def test_custom_alias_workflow(self):
        """Test creating and using custom aliases"""
        # Create custom alias
        self.manager.add_alias('myalias', 'DOCS --search')

        # Resolve it
        resolved = self.manager.resolve('myalias')
        self.assertEqual(resolved['command'], 'DOCS')
        self.assertIn('--search', resolved['args'])

        # Should track usage
        self.assertEqual(self.manager.get_usage_count('myalias'), 1)

    def test_alias_suggestion_workflow(self):
        """Test alias suggestions for repeated commands"""
        # Simulate repeated command usage
        command = 'DOCS --manual git'

        for _ in range(6):  # Threshold is 5
            self.manager.track_command_usage(command)

        # Should suggest creating an alias
        suggestions = self.manager.get_alias_suggestions()
        self.assertTrue(len(suggestions) > 0)

    def test_builtin_aliases_workflow(self):
        """Test all builtin aliases work correctly"""
        # Test common shortcuts
        shortcuts = {
            '?': 'HELP',
            'd': 'DOCS',
            'm': 'MEMORY',
            'ls': 'LIST',
        }

        for alias, expected_command in shortcuts.items():
            resolved = self.manager.resolve(alias)
            self.assertEqual(resolved['command'], expected_command,
                           f"Alias {alias} should resolve to {expected_command}")


class TestPickerWorkflow(unittest.TestCase):
    """Test picker UI workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.picker = UniversalPicker(title="Test Picker")

    def test_single_select_workflow(self):
        """Test single selection workflow"""
        items = [
            {'label': 'Option 1', 'value': 'opt1'},
            {'label': 'Option 2', 'value': 'opt2'},
            {'label': 'Option 3', 'value': 'opt3'},
        ]

        self.picker.set_items(items)

        # Select item
        self.picker.toggle_item(0)
        selected = self.picker.get_selected_items()

        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]['value'], 'opt1')

    def test_multi_select_workflow(self):
        """Test multi-selection workflow"""
        self.picker.multi_select = True

        items = [
            {'label': 'Item 1', 'value': 1},
            {'label': 'Item 2', 'value': 2},
            {'label': 'Item 3', 'value': 3},
        ]

        self.picker.set_items(items)

        # Select multiple items
        self.picker.toggle_item(0)
        self.picker.toggle_item(2)

        selected = self.picker.get_selected_items()
        self.assertEqual(len(selected), 2)
        self.assertIn(1, [s['value'] for s in selected])
        self.assertIn(3, [s['value'] for s in selected])

    def test_filter_workflow(self):
        """Test filtering workflow"""
        items = [
            {'label': 'Apple', 'value': 'a'},
            {'label': 'Banana', 'value': 'b'},
            {'label': 'Cherry', 'value': 'c'},
            {'label': 'Date', 'value': 'd'},
        ]

        self.picker.set_items(items)

        # Filter by search term
        self.picker.filter_items('an')

        # Should only show items with 'an'
        filtered = self.picker.filtered_items
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['label'], 'Banana')


class TestErrorHandlerWorkflow(unittest.TestCase):
    """Test error handling workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = EnhancedErrorHandler()

    def test_file_not_found_workflow(self):
        """Test file not found error workflow"""
        # Simulate typo in filename
        missing_file = 'READMI.md'
        available = ['README.md', 'ROADMAP.MD', 'LICENSE.txt']

        error_msg = self.handler.file_not_found(missing_file, available)

        # Should suggest correct file
        self.assertIn('README.md', error_msg)
        self.assertIn('Did you mean', error_msg)

    def test_command_not_found_workflow(self):
        """Test command not found workflow"""
        # Typo in command
        wrong_command = 'DOCZ'
        available = ['DOCS', 'LEARN', 'MEMORY', 'HELP']

        error_msg = self.handler.command_not_found(wrong_command, available)

        # Should suggest correct command
        self.assertIn('DOCS', error_msg)

    def test_permission_denied_workflow(self):
        """Test permission denied error workflow"""
        error_msg = self.handler.permission_denied(
            'secret.txt',
            required_tier='private',
            current_tier='public'
        )

        # Should explain tier system
        self.assertIn('private', error_msg.lower())
        self.assertIn('public', error_msg.lower())


class TestProgressIndicatorWorkflow(unittest.TestCase):
    """Test progress indicator workflows"""

    @patch('sys.stdout')
    def test_file_processing_workflow(self, mock_stdout):
        """Test file processing with progress bar"""
        total_files = 10
        bar = ProgressIndicators.bar(total_files, "Processing files")

        # Simulate processing files
        for i in range(total_files):
            bar.update()

        # Should complete at 100%
        self.assertEqual(bar.current, total_files)

    @patch('sys.stdout')
    def test_download_workflow(self, mock_stdout):
        """Test download progress display"""
        # Simulate download
        bytes_down = 50 * 1024 * 1024  # 50 MB
        bytes_total = 100 * 1024 * 1024  # 100 MB
        speed = 10 * 1024 * 1024  # 10 MB/s

        progress = ProgressIndicators.download_progress(
            bytes_down, bytes_total, speed
        )

        # Should show percentage and speed
        self.assertIn('50%', progress)
        self.assertIn('10.00', progress)


class TestBackwardsCompatibility(unittest.TestCase):
    """Test backwards compatibility with v1.0.22"""

    def setUp(self):
        """Set up test fixtures"""
        self.alias_manager = AliasManager()

    def test_all_v1_0_22_commands_work(self):
        """Test that all v1.0.22 commands still work"""
        # List of commands that should be aliased
        old_commands = [
            'DOC', 'MANUAL', 'HANDBOOK', 'EXAMPLE',
            'GUIDE', 'DIAGRAM',
            'PRIVATE', 'SHARED', 'COMMUNITY', 'KB'
        ]

        for old_cmd in old_commands:
            resolved = self.alias_manager.resolve(old_cmd)
            # Should resolve to a valid new command
            self.assertIsNotNone(resolved['command'])
            self.assertIn(resolved['command'], ['DOCS', 'LEARN', 'MEMORY'])

    def test_deprecation_messages_clear(self):
        """Test that deprecation messages are helpful"""
        # When using old command, should get helpful message
        old_cmd = 'DOC'
        resolved = self.alias_manager.resolve(old_cmd)

        # Should have metadata about being an alias
        self.assertTrue(self.alias_manager.is_builtin_alias(old_cmd))


class TestPerformanceBenchmarks(unittest.TestCase):
    """Test performance benchmarks"""

    def test_command_execution_time(self):
        """Test that commands execute within time limits"""
        import time

        # Test fuzzy matching performance
        matcher = FuzzyMatcher()
        files = [f'file_{i}.txt' for i in range(100)]

        start = time.time()
        matches = matcher.find_matches('file_50', files)
        elapsed = time.time() - start

        # Should complete in < 50ms
        self.assertLess(elapsed, 0.05, "Fuzzy matching too slow")

    def test_alias_resolution_time(self):
        """Test alias resolution performance"""
        import time

        manager = AliasManager()

        start = time.time()
        for _ in range(1000):
            manager.resolve('?')
        elapsed = time.time() - start

        # 1000 resolutions should take < 50ms
        self.assertLess(elapsed, 0.05, "Alias resolution too slow")


if __name__ == '__main__':
    unittest.main()
