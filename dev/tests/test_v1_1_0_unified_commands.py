#!/usr/bin/env python3
"""
uDOS v1.1.0 - Unified Commands Test Suite
Tests DOCS, LEARN, and MEMORY unified handlers

Feature: 1.1.0.11
Purpose: Validate smart prompts and zero-argument behavior
Version: 1.1.0

Test Coverage:
- Zero-argument interactive pickers
- Smart content detection and routing
- Cross-source search functionality
- Backwards compatibility with v1.0.x
- Error handling and edge cases
- Session analytics integration
- User experience validation
"""

import unittest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from io import StringIO
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.commands.docs_unified_handler import DocsUnifiedHandler
from core.commands.learn_unified_handler import LearnUnifiedHandler
from core.commands.memory_unified_handler import MemoryUnifiedHandler


class TestDocsUnifiedHandler(unittest.TestCase):
    """Test DOCS unified command handler."""

    def setUp(self):
        """Initialize handler for testing."""
        self.handler = DocsUnifiedHandler()

    def test_zero_args_shows_picker(self):
        """Test DOCS with no arguments shows interactive picker."""
        result = self.handler.handle("", [])

        self.assertIsNotNone(result)
        self.assertIn("DOCS", result)
        self.assertIn("Documentation", result)
        self.assertIn("Manual", result)
        self.assertIn("Handbook", result)
        self.assertIn("Examples", result)
        # Should have numbered options
        self.assertIn("1.", result)
        self.assertIn("2.", result)

    def test_help_command(self):
        """Test DOCS HELP shows help information."""
        result = self.handler.handle("HELP", [])

        self.assertIsNotNone(result)
        self.assertIn("DOCS", result)
        self.assertIn("USAGE", result)
        self.assertIn("EXAMPLES", result)

    def test_help_flag(self):
        """Test DOCS --help shows help information."""
        result = self.handler.handle("--help", [])

        self.assertIsNotNone(result)
        self.assertIn("DOCS", result)

    def test_manual_direct_access(self):
        """Test DOCS --manual routes to manual handler."""
        # Manual handler should handle empty command gracefully
        result = self.handler.handle("--manual", [])
        self.assertIsNotNone(result)

    def test_handbook_direct_access(self):
        """Test DOCS --handbook routes to handbook handler."""
        result = self.handler.handle("--handbook", [])
        self.assertIsNotNone(result)

    def test_example_direct_access(self):
        """Test DOCS --example routes to example handler."""
        result = self.handler.handle("--example", [])
        self.assertIsNotNone(result)

    def test_search_explicit(self):
        """Test DOCS --search performs unified search."""
        result = self.handler.handle("--search", ["test", "query"])
        self.assertIsNotNone(result)

    def test_smart_search_single_word(self):
        """Test smart search with single word."""
        result = self.handler.handle("guide", [])
        self.assertIsNotNone(result)

    def test_smart_search_multi_word(self):
        """Test smart search with multiple words."""
        result = self.handler.handle("getting", ["started"])
        self.assertIsNotNone(result)

    def test_unified_index_built(self):
        """Test unified index is properly built."""
        self.assertIsNotNone(self.handler.unified_index)
        self.assertIn('documentation', self.handler.unified_index)
        self.assertIn('manual', self.handler.unified_index)
        self.assertIn('handbook', self.handler.unified_index)
        self.assertIn('examples', self.handler.unified_index)

    def test_backwards_compatibility(self):
        """Test that old DOC/MANUAL/HANDBOOK commands still work."""
        # These are handled by main command parser, but sub-handlers should work
        self.assertIsNotNone(self.handler.doc_handler)
        self.assertIsNotNone(self.handler.manual_handler)
        self.assertIsNotNone(self.handler.handbook_handler)
        self.assertIsNotNone(self.handler.example_handler)


class TestLearnUnifiedHandler(unittest.TestCase):
    """Test LEARN unified command handler."""

    def setUp(self):
        """Initialize handler for testing."""
        self.handler = LearnUnifiedHandler()

    def test_zero_args_shows_picker(self):
        """Test LEARN with no arguments shows interactive picker."""
        result = self.handler.handle("", [])

        self.assertIsNotNone(result)
        self.assertIn("LEARN", result)
        self.assertIn("Guides", result)
        self.assertIn("Diagrams", result)
        # Should show progress
        self.assertIn("Progress", result)
        # Should have numbered options
        self.assertIn("1.", result)

    def test_help_command(self):
        """Test LEARN HELP shows help information."""
        result = self.handler.handle("HELP", [])

        self.assertIsNotNone(result)
        self.assertIn("LEARN", result)
        self.assertIn("USAGE", result)
        self.assertIn("EXAMPLES", result)

    def test_help_flag(self):
        """Test LEARN --help shows help information."""
        result = self.handler.handle("--help", [])

        self.assertIsNotNone(result)
        self.assertIn("LEARN", result)

    def test_list_guides(self):
        """Test LEARN --guides lists all guides."""
        result = self.handler.handle("--guides", [])
        self.assertIsNotNone(result)

    def test_list_diagrams(self):
        """Test LEARN --diagrams lists all diagrams."""
        result = self.handler.handle("--diagrams", [])
        self.assertIsNotNone(result)

    def test_list_all(self):
        """Test LEARN --list shows all content."""
        result = self.handler.handle("--list", [])
        self.assertIsNotNone(result)

    def test_continue_learning(self):
        """Test LEARN --continue resumes last session."""
        result = self.handler.handle("--continue", [])
        self.assertIsNotNone(result)

    def test_show_progress(self):
        """Test LEARN --progress shows learning progress."""
        result = self.handler.handle("--progress", [])
        self.assertIsNotNone(result)

    def test_smart_content_detection_single_word(self):
        """Test smart content detection with single word."""
        result = self.handler.handle("water", [])
        self.assertIsNotNone(result)

    def test_smart_content_detection_multi_word(self):
        """Test smart content detection with multiple words."""
        result = self.handler.handle("water", ["purification"])
        self.assertIsNotNone(result)

    def test_content_index_built(self):
        """Test content index is properly built."""
        self.assertIsNotNone(self.handler.content_index)
        self.assertIn('guides', self.handler.content_index)
        self.assertIn('diagrams', self.handler.content_index)

    def test_backwards_compatibility(self):
        """Test that old GUIDE/DIAGRAM commands still work."""
        self.assertIsNotNone(self.handler.guide_handler)
        self.assertIsNotNone(self.handler.diagram_handler)


class TestMemoryUnifiedHandler(unittest.TestCase):
    """Test MEMORY unified command handler."""

    def setUp(self):
        """Initialize handler for testing."""
        self.handler = MemoryUnifiedHandler()

    def test_zero_args_shows_picker(self):
        """Test MEMORY with no arguments shows interactive picker."""
        result = self.handler.handle("", [])

        self.assertIsNotNone(result)
        self.assertIn("MEMORY", result)
        self.assertIn("PRIVATE", result)
        self.assertIn("SHARED", result)
        self.assertIn("COMMUNITY", result)
        self.assertIn("PUBLIC", result)
        # Should show security info
        self.assertIn("AES", result)
        # Should have numbered options
        self.assertIn("1.", result)

    def test_help_command(self):
        """Test MEMORY HELP shows help information."""
        result = self.handler.handle("HELP", [])

        self.assertIsNotNone(result)
        self.assertIn("MEMORY", result)
        self.assertIn("USAGE", result)

    def test_help_flag(self):
        """Test MEMORY --help shows help information."""
        result = self.handler.handle("--help", [])

        self.assertIsNotNone(result)
        self.assertIn("MEMORY", result)

    def test_tier_access_private(self):
        """Test MEMORY --tier=private accesses private tier."""
        result = self.handler.handle("--tier=private", [])
        self.assertIsNotNone(result)

    def test_tier_access_shared(self):
        """Test MEMORY --tier=shared accesses shared tier."""
        result = self.handler.handle("--tier=shared", [])
        self.assertIsNotNone(result)

    def test_tier_access_community(self):
        """Test MEMORY --tier=community accesses community tier."""
        result = self.handler.handle("--tier=community", [])
        self.assertIsNotNone(result)

    def test_tier_access_public(self):
        """Test MEMORY --tier=public accesses public tier."""
        result = self.handler.handle("--tier=public", [])
        self.assertIsNotNone(result)

    def test_private_shortcut(self):
        """Test MEMORY -p shortcut for private tier."""
        result = self.handler.handle("-p", [])
        self.assertIsNotNone(result)

    def test_shared_shortcut(self):
        """Test MEMORY -s shortcut for shared tier."""
        result = self.handler.handle("-s", [])
        self.assertIsNotNone(result)

    def test_community_shortcut(self):
        """Test MEMORY -c shortcut for community tier."""
        result = self.handler.handle("-c", [])
        self.assertIsNotNone(result)

    def test_kb_shortcut(self):
        """Test MEMORY --kb shortcut for knowledge base."""
        result = self.handler.handle("--kb", [])
        self.assertIsNotNone(result)

    def test_list_all(self):
        """Test MEMORY --list shows all accessible content."""
        result = self.handler.handle("--list", [])
        self.assertIsNotNone(result)

    def test_smart_search_single_word(self):
        """Test smart search with single word."""
        result = self.handler.handle("config", [])
        self.assertIsNotNone(result)

    def test_smart_search_multi_word(self):
        """Test smart search with multiple words."""
        result = self.handler.handle("my", ["notes"])
        self.assertIsNotNone(result)

    def test_tiers_defined(self):
        """Test all memory tiers are properly defined."""
        self.assertIsNotNone(self.handler.tiers)
        self.assertIn('private', self.handler.tiers)
        self.assertIn('shared', self.handler.tiers)
        self.assertIn('community', self.handler.tiers)
        self.assertIn('public', self.handler.tiers)

    def test_tier_security_levels(self):
        """Test tier security levels are defined."""
        for tier_name, tier_data in self.handler.tiers.items():
            self.assertIn('security', tier_data)
            self.assertIn('access', tier_data)
            self.assertIn('priority', tier_data)

    def test_backwards_compatibility(self):
        """Test that old tier commands still work."""
        self.assertIsNotNone(self.handler.private_handler)
        self.assertIsNotNone(self.handler.shared_handler)
        self.assertIsNotNone(self.handler.community_handler)
        self.assertIsNotNone(self.handler.kb_handler)


class TestUnifiedCommandsIntegration(unittest.TestCase):
    """Integration tests for unified commands."""

    def test_all_handlers_instantiate(self):
        """Test all unified handlers can be instantiated."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()
        memory = MemoryUnifiedHandler()

        self.assertIsNotNone(docs)
        self.assertIsNotNone(learn)
        self.assertIsNotNone(memory)

    def test_handlers_have_help(self):
        """Test all handlers provide help."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()
        memory = MemoryUnifiedHandler()

        docs_help = docs.handle("HELP", [])
        learn_help = learn.handle("HELP", [])
        memory_help = memory.handle("HELP", [])

        self.assertIn("DOCS", docs_help)
        self.assertIn("LEARN", learn_help)
        self.assertIn("MEMORY", memory_help)

    def test_handlers_have_pickers(self):
        """Test all handlers show interactive pickers."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()
        memory = MemoryUnifiedHandler()

        docs_picker = docs.handle("", [])
        learn_picker = learn.handle("", [])
        memory_picker = memory.handle("", [])

        # All should have numbered options
        self.assertIn("1.", docs_picker)
        self.assertIn("1.", learn_picker)
        self.assertIn("1.", memory_picker)


class TestSmartSearchFunctionality(unittest.TestCase):
    """Test smart search across unified handlers."""

    def setUp(self):
        """Initialize handlers."""
        self.docs = DocsUnifiedHandler()
        self.learn = LearnUnifiedHandler()
        self.memory = MemoryUnifiedHandler()

    def test_docs_smart_search(self):
        """Test DOCS smart search functionality."""
        # Should not crash with various queries
        queries = ["help", "getting started", "commands", ""]
        for query in queries:
            result = self.docs.handle(query, [])
            self.assertIsNotNone(result)

    def test_learn_smart_search(self):
        """Test LEARN smart content detection."""
        queries = ["water", "knots", "system", ""]
        for query in queries:
            result = self.learn.handle(query, [])
            self.assertIsNotNone(result)

    def test_memory_smart_search(self):
        """Test MEMORY smart search."""
        queries = ["notes", "config", "password", ""]
        for query in queries:
            result = self.memory.handle(query, [])
            self.assertIsNotNone(result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_string_command(self):
        """Test handlers with empty string command."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()
        memory = MemoryUnifiedHandler()

        # Empty string should show picker (same as no args)
        self.assertIsNotNone(docs.handle("", []))
        self.assertIsNotNone(learn.handle("", []))
        self.assertIsNotNone(memory.handle("", []))

    def test_whitespace_command(self):
        """Test handlers with whitespace command."""
        docs = DocsUnifiedHandler()

        # Should handle gracefully
        result = docs.handle("   ", [])
        self.assertIsNotNone(result)

    def test_special_characters(self):
        """Test handlers with special characters."""
        docs = DocsUnifiedHandler()

        # Should not crash
        result = docs.handle("@#$%", [])
        self.assertIsNotNone(result)

    def test_very_long_query(self):
        """Test handlers with very long queries."""
        docs = DocsUnifiedHandler()

        long_query = "word " * 100
        result = docs.handle(long_query, [])
        self.assertIsNotNone(result)

    def test_unicode_query(self):
        """Test handlers with unicode characters."""
        docs = DocsUnifiedHandler()

        result = docs.handle("水", [])  # Chinese character
        self.assertIsNotNone(result)


class TestUserExperience(unittest.TestCase):
    """Test user experience aspects of unified commands."""

    def test_picker_has_clear_options(self):
        """Test pickers have clear, numbered options."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()
        memory = MemoryUnifiedHandler()

        docs_picker = docs.handle("", [])
        learn_picker = learn.handle("", [])
        memory_picker = memory.handle("", [])

        # Should have clear instructions
        self.assertIn("choice", docs_picker.lower())
        self.assertIn("choice", learn_picker.lower())
        self.assertIn("choice", memory_picker.lower())

    def test_help_has_examples(self):
        """Test help output includes usage examples."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()
        memory = MemoryUnifiedHandler()

        docs_help = docs.handle("HELP", [])
        learn_help = learn.handle("HELP", [])
        memory_help = memory.handle("HELP", [])

        self.assertIn("EXAMPLES", docs_help)
        self.assertIn("EXAMPLES", learn_help)
        # Memory might use different wording
        self.assertTrue("EXAMPLE" in memory_help or "example" in memory_help.lower())

    def test_picker_shows_statistics(self):
        """Test pickers show useful statistics."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()

        docs_picker = docs.handle("", [])
        learn_picker = learn.handle("", [])

        # DOCS should show counts
        self.assertTrue("Statistics" in docs_picker or "count" in docs_picker.lower())

        # LEARN should show progress
        self.assertIn("Progress", learn_picker)

    def test_quick_access_documented(self):
        """Test pickers document quick access patterns."""
        docs = DocsUnifiedHandler()
        learn = LearnUnifiedHandler()
        memory = MemoryUnifiedHandler()

        docs_picker = docs.handle("", [])
        learn_picker = learn.handle("", [])
        memory_picker = memory.handle("", [])

        # Should mention quick access
        self.assertTrue("Quick" in docs_picker)
        self.assertTrue("Quick" in learn_picker or "Actions" in learn_picker)
        self.assertTrue("Quick" in memory_picker or "Shortcuts" in memory_picker)


def suite():
    """Create comprehensive test suite."""
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_suite.addTests(loader.loadTestsFromTestCase(TestDocsUnifiedHandler))
    test_suite.addTests(loader.loadTestsFromTestCase(TestLearnUnifiedHandler))
    test_suite.addTests(loader.loadTestsFromTestCase(TestMemoryUnifiedHandler))
    test_suite.addTests(loader.loadTestsFromTestCase(TestUnifiedCommandsIntegration))
    test_suite.addTests(loader.loadTestsFromTestCase(TestSmartSearchFunctionality))
    test_suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    test_suite.addTests(loader.loadTestsFromTestCase(TestUserExperience))

    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())

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
