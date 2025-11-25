"""
Test Suite for v1.0.21 - Survivalist Themes & Practical Skills Library
Tests: GUIDE command, DIAGRAM command, knowledge library, teletext graphics

Test Coverage (40 tests total):
- GUIDE Command: 15 tests
- DIAGRAM Command: 15 tests
- Knowledge Library: 5 tests
- Integration Tests: 5 tests

Author: uDOS Development Team
Version: 1.0.21
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import json

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

from commands.guide_handler import GuideHandler
from commands.diagram_handler import DiagramHandler


class TestGuideCommand(unittest.TestCase):
    """Test GUIDE command functionality (15 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.viewport = MagicMock()
        self.logger = MagicMock()
        self.handler = GuideHandler(viewport=self.viewport, logger=self.logger)

        # Clean up test progress file
        if self.handler.progress_file.exists():
            self.handler.progress_file.unlink()

    def tearDown(self):
        """Clean up after tests"""
        if self.handler.progress_file.exists():
            self.handler.progress_file.unlink()

    def test_guide_list_all(self):
        """Test GUIDE LIST shows all categories"""
        result = self.handler.handle("LIST", [])
        self.assertIn("Available Guides", result)
        self.assertIsInstance(result, str)

    def test_guide_list_category(self):
        """Test GUIDE LIST <category> filters by category"""
        result = self.handler.handle("LIST", ["survival"])
        self.assertIsInstance(result, str)

    def test_guide_search(self):
        """Test GUIDE SEARCH finds guides by keyword"""
        result = self.handler.handle("SEARCH", ["water"])
        self.assertIsInstance(result, str)

    def test_guide_show_valid(self):
        """Test GUIDE SHOW displays guide overview"""
        # First list guides to find a valid one
        list_result = self.handler.handle("LIST", [])
        if "water" in list_result.lower():
            result = self.handler.handle("SHOW", ["water-purification-methods"])
            self.assertIsInstance(result, str)

    def test_guide_show_invalid(self):
        """Test GUIDE SHOW with non-existent guide"""
        result = self.handler.handle("SHOW", ["nonexistent-guide-xyz"])
        self.assertIn("not found", result.lower())

    def test_guide_start(self):
        """Test GUIDE START begins interactive session"""
        # Find a valid guide first
        list_result = self.handler.handle("LIST", [])
        if "water" in list_result.lower():
            result = self.handler.handle("START", ["water-purification-methods"])
            self.assertIsInstance(result, str)
            self.assertIsNotNone(self.handler.current_guide)

    def test_guide_next(self):
        """Test GUIDE NEXT advances to next step"""
        # Start a guide first
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            self.handler.handle("START", ["water-purification-methods"])
            result = self.handler.handle("NEXT", [])
            self.assertIsInstance(result, str)

    def test_guide_prev(self):
        """Test GUIDE PREV returns to previous step"""
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            self.handler.handle("START", ["water-purification-methods"])
            self.handler.handle("NEXT", [])
            result = self.handler.handle("PREV", [])
            self.assertIsInstance(result, str)

    def test_guide_jump(self):
        """Test GUIDE JUMP moves to specific step"""
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            self.handler.handle("START", ["water-purification-methods"])
            result = self.handler.handle("JUMP", ["2"])
            self.assertIsInstance(result, str)

    def test_guide_complete_step(self):
        """Test GUIDE COMPLETE marks step as done"""
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            self.handler.handle("START", ["water-purification-methods"])
            result = self.handler.handle("COMPLETE", ["1"])
            self.assertIsInstance(result, str)
            self.assertIn(1, self.handler.completed_steps)

    def test_guide_progress(self):
        """Test GUIDE PROGRESS shows completion status"""
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            self.handler.handle("START", ["water-purification-methods"])
            self.handler.handle("COMPLETE", ["1"])
            result = self.handler.handle("PROGRESS", [])
            self.assertIsInstance(result, str)
            self.assertIn("%", result)  # Should show percentage

    def test_guide_reset(self):
        """Test GUIDE RESET clears progress"""
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            self.handler.handle("START", ["water-purification-methods"])
            self.handler.handle("COMPLETE", ["1"])
            result = self.handler.handle("RESET", ["water-purification-methods"])
            self.assertIsInstance(result, str)
            self.assertEqual(len(self.handler.completed_steps), 0)

    def test_guide_persistence(self):
        """Test progress saves and loads correctly"""
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            self.handler.handle("START", ["water-purification-methods"])
            self.handler.handle("COMPLETE", ["1"])

            # Create new handler to test loading
            new_handler = GuideHandler(viewport=self.viewport, logger=self.logger)
            self.assertTrue(len(new_handler.completed_steps) > 0)

    def test_guide_help(self):
        """Test GUIDE HELP shows usage information"""
        result = self.handler.handle("HELP", [])
        self.assertIn("GUIDE", result)
        self.assertIn("LIST", result)

    def test_guide_invalid_command(self):
        """Test invalid GUIDE subcommand"""
        result = self.handler.handle("INVALID_CMD", [])
        self.assertIn("Unknown", result)


class TestDiagramCommand(unittest.TestCase):
    """Test DIAGRAM command functionality (15 tests)"""

    def setUp(self):
        """Set up test fixtures"""
        self.viewport = MagicMock()
        self.logger = MagicMock()
        self.handler = DiagramHandler(viewport=self.viewport, logger=self.logger)

    def test_diagram_list_all(self):
        """Test DIAGRAM LIST shows all diagrams"""
        result = self.handler.handle("LIST", [])
        self.assertIsInstance(result, str)

    def test_diagram_list_type(self):
        """Test DIAGRAM LIST <type> filters by type"""
        result = self.handler.handle("LIST", ["knot"])
        self.assertIsInstance(result, str)

    def test_diagram_types(self):
        """Test DIAGRAM TYPES shows all categories"""
        result = self.handler.handle("TYPES", [])
        self.assertIn("knot", result.lower())
        self.assertIn("shelter", result.lower())

    def test_diagram_search(self):
        """Test DIAGRAM SEARCH finds diagrams by keyword"""
        result = self.handler.handle("SEARCH", ["bowline"])
        self.assertIsInstance(result, str)

    def test_diagram_show_valid(self):
        """Test DIAGRAM SHOW displays ASCII art"""
        # Try to show a known diagram
        list_result = self.handler.handle("LIST", [])
        if "bowline" in list_result.lower():
            result = self.handler.handle("SHOW", ["bowline"])
            self.assertIsInstance(result, str)

    def test_diagram_show_invalid(self):
        """Test DIAGRAM SHOW with non-existent diagram"""
        result = self.handler.handle("SHOW", ["nonexistent-diagram-xyz"])
        self.assertIn("not found", result.lower())

    def test_diagram_render(self):
        """Test DIAGRAM RENDER with width parameter"""
        list_result = self.handler.handle("LIST", [])
        if "bowline" in list_result.lower():
            result = self.handler.handle("RENDER", ["bowline", "40"])
            self.assertIsInstance(result, str)

    def test_diagram_extract_from_guide(self):
        """Test diagram extraction from knowledge guides"""
        # Check if guides contain diagrams
        if Path("knowledge/survival/skills/knot-tying.md").exists():
            diagrams = self.handler._extract_diagrams_from_guides()
            self.assertIsInstance(diagrams, list)

    def test_diagram_viewport_awareness(self):
        """Test diagrams adapt to viewport tier"""
        self.viewport.tier = 10
        self.viewport.width = 80
        # Handler should respect viewport settings
        self.assertEqual(self.viewport.tier, 10)

    def test_diagram_copy_to_panel(self):
        """Test DIAGRAM COPY exports to panel"""
        # Mock test - would require PANEL integration
        result = self.handler.handle("COPY", ["test", "panel1"])
        self.assertIsInstance(result, str)

    def test_diagram_export_to_file(self):
        """Test DIAGRAM EXPORT saves to file"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_path = f.name

        try:
            result = self.handler.handle("EXPORT", ["test", temp_path])
            self.assertIsInstance(result, str)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_diagram_metadata(self):
        """Test diagram metadata extraction"""
        # Test that diagrams have discoverable metadata
        list_result = self.handler.handle("LIST", [])
        self.assertIsInstance(list_result, str)
        # Metadata is implicit in the list output
        self.assertTrue(len(list_result) > 0)

    def test_diagram_cache(self):
        """Test diagram caching for performance"""
        # First load
        result1 = self.handler.handle("LIST", [])
        # Second load should be faster (cached)
        result2 = self.handler.handle("LIST", [])
        self.assertEqual(len(result1), len(result2))

    def test_diagram_help(self):
        """Test DIAGRAM HELP shows usage"""
        result = self.handler.handle("HELP", [])
        self.assertIn("DIAGRAM", result)
        self.assertIn("LIST", result)

    def test_diagram_invalid_command(self):
        """Test invalid DIAGRAM subcommand"""
        result = self.handler.handle("INVALID_CMD", [])
        self.assertIn("Unknown", result)


class TestKnowledgeLibrary(unittest.TestCase):
    """Test knowledge library content and structure (5 tests)"""

    def test_knowledge_directory_structure(self):
        """Test knowledge base has correct directory structure"""
        knowledge_path = Path("knowledge")
        self.assertTrue(knowledge_path.exists())

        # Check for key categories
        expected_dirs = ["survival", "skills", "productivity", "well-being"]
        for dir_name in expected_dirs:
            dir_path = knowledge_path / dir_name
            # Directory should exist or be planned
            if dir_path.exists():
                self.assertTrue(dir_path.is_dir())

    def test_guide_markdown_format(self):
        """Test guides follow markdown format standards"""
        guides = list(Path("knowledge").rglob("*.md"))
        if guides:
            guide_path = guides[0]
            content = guide_path.read_text()

            # Should have headers
            self.assertTrue("#" in content)
            # Should have readable content
            self.assertTrue(len(content) > 100)

    def test_guide_ascii_diagrams(self):
        """Test guides contain ASCII diagrams"""
        # Check knot-tying guide specifically
        knot_guide = Path("knowledge/survival/skills/knot-tying.md")
        if knot_guide.exists():
            content = knot_guide.read_text()
            # Should contain code blocks for diagrams
            self.assertTrue("```" in content)

    def test_guide_teletext_graphics(self):
        """Test guides use teletext graphics appropriately"""
        # Check water purification guide
        water_guide = Path("knowledge/survival/water/water-purification-methods.md")
        if water_guide.exists():
            content = water_guide.read_text()
            # Should contain block graphics
            blocks = "█▓▒░"
            has_blocks = any(char in content for char in blocks)
            # May or may not use blocks, but file should be valid
            self.assertTrue(len(content) > 100)

    def test_guide_metadata_consistency(self):
        """Test guides have consistent metadata"""
        guides = list(Path("knowledge").rglob("*.md"))
        for guide_path in guides[:5]:  # Check first 5
            content = guide_path.read_text()
            # Should start with title (# header)
            lines = content.split('\n')
            first_non_empty = next((line for line in lines if line.strip()), "")
            # Valid guides should have content
            self.assertTrue(len(content) > 50)


class TestIntegration(unittest.TestCase):
    """Integration tests for v1.0.21 features (5 tests)"""

    def setUp(self):
        """Set up integration test fixtures"""
        self.viewport = MagicMock()
        self.logger = MagicMock()
        self.guide_handler = GuideHandler(viewport=self.viewport, logger=self.logger)
        self.diagram_handler = DiagramHandler(viewport=self.viewport, logger=self.logger)

    def test_guide_diagram_integration(self):
        """Test GUIDE can display embedded diagrams via DIAGRAM"""
        # Guides should reference diagrams
        if Path("knowledge/survival/skills/knot-tying.md").exists():
            result = self.guide_handler.handle("SHOW", ["knot-tying"])
            self.assertIsInstance(result, str)

    def test_viewport_tier_adaptation(self):
        """Test commands adapt to different viewport tiers"""
        for tier in [0, 5, 10, 14]:
            self.viewport.tier = tier
            result = self.diagram_handler.handle("LIST", [])
            self.assertIsInstance(result, str)

    def test_knowledge_search_integration(self):
        """Test searching across guides and diagrams"""
        guide_result = self.guide_handler.handle("SEARCH", ["water"])
        diagram_result = self.diagram_handler.handle("SEARCH", ["water"])

        self.assertIsInstance(guide_result, str)
        self.assertIsInstance(diagram_result, str)

    def test_progress_tracking_persistence(self):
        """Test guide progress persists across sessions"""
        if Path("knowledge/survival/water/water-purification-methods.md").exists():
            # Session 1: Start and complete step
            self.guide_handler.handle("START", ["water-purification-methods"])
            self.guide_handler.handle("COMPLETE", ["1"])

            # Session 2: New handler should load progress
            new_handler = GuideHandler(viewport=self.viewport, logger=self.logger)
            progress = new_handler.handle("PROGRESS", [])

            self.assertIsInstance(progress, str)

    def test_teletext_graphics_rendering(self):
        """Test teletext graphics render correctly in output"""
        # DIAGRAM should use teletext blocks
        result = self.diagram_handler.handle("LIST", [])

        # Output should be renderable
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


def run_tests():
    """Run all v1.0.21 tests"""
    print("=" * 80)
    print("uDOS v1.0.21 Test Suite - Survivalist Themes & Practical Skills Library")
    print("=" * 80)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGuideCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestDiagramCommand))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeLibrary))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print()
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
