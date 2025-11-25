"""
Test Suite for v1.0.22 Documentation Commands
Tests DOC, MANUAL, HANDBOOK, and EXAMPLE commands

Author: uDOS Development Team
Version: 1.0.22
"""

import unittest
import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.commands.doc_handler import DocHandler
from core.commands.manual_handler import ManualHandler
from core.commands.handbook_handler import HandbookHandler
from core.commands.example_handler import ExampleHandler


class TestDocCommand(unittest.TestCase):
    """Test DOC command - documentation browser"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = DocHandler()

    def test_doc_help(self):
        """Test DOC help display"""
        result = self.handler.handle("HELP", [])
        self.assertIn("DOC - Documentation Browser", result)
        self.assertIn("USAGE:", result)
        self.assertIn("EXAMPLES:", result)

    def test_doc_index(self):
        """Test DOC INDEX - show all topics"""
        result = self.handler.handle("INDEX", [])
        self.assertIn("Documentation Index", result)
        self.assertIn("Total:", result)

    def test_doc_list(self):
        """Test DOC LIST - list documents"""
        result = self.handler.handle("LIST", [])
        self.assertIn("Available Documentation", result)

    def test_doc_search(self):
        """Test DOC SEARCH - search documentation"""
        result = self.handler.handle("SEARCH", ["command"])
        self.assertTrue("Search Results" in result or "No results" in result)

    def test_doc_search_no_query(self):
        """Test DOC SEARCH without query"""
        result = self.handler.handle("SEARCH", [])
        self.assertIn("Usage:", result)

    def test_doc_topic(self):
        """Test DOC <topic> - show specific topic"""
        result = self.handler.handle("configuration", [])
        # Should show content or error message
        self.assertTrue(len(result) > 0)

    def test_doc_unknown_topic(self):
        """Test DOC with unknown topic"""
        result = self.handler.handle("nonexistent-topic-xyz", [])
        self.assertIn("not found", result.lower())

    def test_doc_index_structure(self):
        """Test documentation index is properly built"""
        self.assertIsInstance(self.handler.doc_index, dict)
        # Should have some entries if wiki/ exists
        if Path("wiki").exists():
            self.assertGreater(len(self.handler.doc_index), 0)


class TestManualCommand(unittest.TestCase):
    """Test MANUAL command - quick reference"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = ManualHandler()

    def test_manual_help(self):
        """Test MANUAL help display"""
        result = self.handler.handle("HELP", [])
        self.assertIn("MANUAL - Quick Command Reference", result)
        self.assertIn("USAGE:", result)

    def test_manual_examples(self):
        """Test MANUAL --examples"""
        result = self.handler.handle("--examples", [])
        self.assertIn("Command Examples", result)

    def test_manual_search(self):
        """Test MANUAL --search"""
        result = self.handler.handle("--search", ["load"])
        self.assertTrue("Commands matching" in result or "No commands" in result)

    def test_manual_search_no_query(self):
        """Test MANUAL --search without query"""
        result = self.handler.handle("--search", [])
        self.assertIn("Usage:", result)

    def test_manual_load(self):
        """Test MANUAL LOAD - show LOAD command manual"""
        result = self.handler.handle("LOAD", [])
        self.assertIn("LOAD", result)
        self.assertIn("SYNTAX:", result)
        self.assertIn("EXAMPLES:", result)

    def test_manual_guide(self):
        """Test MANUAL GUIDE - show GUIDE command manual"""
        result = self.handler.handle("GUIDE", [])
        self.assertIn("GUIDE", result)
        self.assertIn("Interactive guide viewer", result)

    def test_manual_diagram(self):
        """Test MANUAL DIAGRAM - show DIAGRAM command manual"""
        result = self.handler.handle("DIAGRAM", [])
        self.assertIn("DIAGRAM", result)
        self.assertIn("ASCII art library", result)

    def test_manual_unknown_command(self):
        """Test MANUAL with unknown command"""
        result = self.handler.handle("NONEXISTENT", [])
        self.assertIn("No manual page", result)

    def test_manual_database(self):
        """Test manual database is properly populated"""
        self.assertIsInstance(self.handler.manuals, dict)
        self.assertGreater(len(self.handler.manuals), 0)
        # Check key commands exist
        self.assertIn("LOAD", self.handler.manuals)
        self.assertIn("GUIDE", self.handler.manuals)


class TestHandbookCommand(unittest.TestCase):
    """Test HANDBOOK command - structured reader"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = HandbookHandler()

    def test_handbook_help(self):
        """Test HANDBOOK help display"""
        result = self.handler.handle("HELP", [])
        self.assertIn("HANDBOOK - Structured Documentation Reader", result)
        self.assertIn("VOLUMES:", result)

    def test_handbook_vol1(self):
        """Test HANDBOOK VOL1 - show Volume 1"""
        result = self.handler.handle("VOL1", [])
        self.assertIn("Volume 1: System & Commands", result)
        self.assertIn("TABLE OF CONTENTS:", result)

    def test_handbook_vol2(self):
        """Test HANDBOOK VOL2 - show Volume 2"""
        result = self.handler.handle("VOL2", [])
        self.assertIn("Volume 2: Knowledge Library", result)

    def test_handbook_vol3(self):
        """Test HANDBOOK VOL3 - show Volume 3"""
        result = self.handler.handle("VOL3", [])
        self.assertIn("Volume 3: Development", result)

    def test_handbook_vol4(self):
        """Test HANDBOOK VOL4 - show Volume 4"""
        result = self.handler.handle("VOL4", [])
        self.assertIn("Volume 4: Practical Applications", result)

    def test_handbook_unknown_volume(self):
        """Test HANDBOOK with unknown volume"""
        result = self.handler.handle("VOL99", [])
        self.assertIn("Unknown volume", result)

    def test_handbook_progress(self):
        """Test HANDBOOK PROGRESS - show reading progress"""
        result = self.handler.handle("PROGRESS", [])
        self.assertIn("Reading Progress", result)
        self.assertIn("Progress:", result)

    def test_handbook_bookmark(self):
        """Test HANDBOOK BOOKMARK - show bookmarks"""
        result = self.handler.handle("BOOKMARK", [])
        self.assertTrue("Bookmarks" in result or "No bookmarks" in result)

    def test_handbook_volume_structure(self):
        """Test handbook volume structure"""
        self.assertIsInstance(self.handler.volumes, dict)
        self.assertEqual(len(self.handler.volumes), 4)
        for vol in ["VOL1", "VOL2", "VOL3", "VOL4"]:
            self.assertIn(vol, self.handler.volumes)
            self.assertIn("title", self.handler.volumes[vol])
            self.assertIn("chapters", self.handler.volumes[vol])

    def test_handbook_progress_persistence(self):
        """Test progress is loaded and can be saved"""
        self.assertIsInstance(self.handler.progress, dict)
        self.assertIn("current_volume", self.handler.progress)


class TestExampleCommand(unittest.TestCase):
    """Test EXAMPLE command - example library"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = ExampleHandler()

    def test_example_help(self):
        """Test EXAMPLE help display"""
        result = self.handler.handle("HELP", [])
        self.assertIn("EXAMPLE - Code Example Library", result)
        self.assertIn("USAGE:", result)

    def test_example_list(self):
        """Test EXAMPLE LIST - list all examples"""
        result = self.handler.handle("LIST", [])
        self.assertTrue("Available Examples" in result or "No examples" in result)

    def test_example_info(self):
        """Test EXAMPLE INFO - show example details"""
        # Test with a known example if it exists
        if self.handler.examples:
            first_example = list(self.handler.examples.keys())[0]
            result = self.handler.handle("INFO", [first_example])
            self.assertIn("Type:", result)
            self.assertIn("Category:", result)

    def test_example_info_no_name(self):
        """Test EXAMPLE INFO without name"""
        result = self.handler.handle("INFO", [])
        self.assertIn("Usage:", result)

    def test_example_run_no_name(self):
        """Test EXAMPLE RUN without name"""
        result = self.handler.handle("RUN", [])
        self.assertIn("Usage:", result)

    def test_example_save_no_name(self):
        """Test EXAMPLE SAVE without name"""
        result = self.handler.handle("SAVE", [])
        self.assertIn("Usage:", result)

    def test_example_index_structure(self):
        """Test example index is properly built"""
        self.assertIsInstance(self.handler.examples, dict)
        # Should have examples if examples/ directory exists
        if Path("examples").exists():
            # May have examples
            pass

    def test_example_categorization(self):
        """Test examples are properly categorized"""
        for ex_data in self.handler.examples.values():
            self.assertIn("category", ex_data)
            self.assertIn("type", ex_data)
            self.assertIn("path", ex_data)


class TestDocumentationIntegration(unittest.TestCase):
    """Test integration between documentation commands"""

    def setUp(self):
        """Set up test fixtures"""
        self.doc_handler = DocHandler()
        self.manual_handler = ManualHandler()
        self.handbook_handler = HandbookHandler()
        self.example_handler = ExampleHandler()

    def test_cross_references(self):
        """Test cross-references between commands"""
        # DOC help should mention MANUAL, HANDBOOK
        doc_help = self.doc_handler.handle("HELP", [])
        self.assertIn("MANUAL", doc_help)
        self.assertIn("HANDBOOK", doc_help)

        # MANUAL help should mention DOC
        manual_help = self.manual_handler.handle("HELP", [])
        self.assertIn("DOC", manual_help)

    def test_consistent_help_format(self):
        """Test all commands have consistent help format"""
        handlers = [
            self.doc_handler,
            self.manual_handler,
            self.handbook_handler,
            self.example_handler
        ]

        for handler in handlers:
            result = handler.handle("HELP", [])
            self.assertIn("USAGE:", result)
            self.assertIn("EXAMPLES:", result)

    def test_all_handlers_initialized(self):
        """Test all handlers initialize properly"""
        self.assertIsNotNone(self.doc_handler)
        self.assertIsNotNone(self.manual_handler)
        self.assertIsNotNone(self.handbook_handler)
        self.assertIsNotNone(self.example_handler)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDocCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestManualCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestHandbookCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestExampleCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentationIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary - v1.0.22 Documentation Commands")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
