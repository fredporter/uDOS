"""
Tests for v1.0.23 Command Consolidation Features

Tests:
- MEMORY unified handler
- Fuzzy file matching
- Alias manager
- Universal picker component

Author: uDOS Development Team
Version: 1.0.23
"""

import unittest
from pathlib import Path
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.commands.memory_unified_handler import MemoryUnifiedHandler
from core.services.fuzzy_matcher import FuzzyMatcher, SmartFilePicker
from core.services.alias_manager import AliasManager, AliasCommandHandler
from core.ui.picker import (
    UniversalPicker, PickerBuilder, PickerConfig, PickerItem, PickerType
)


class TestMemoryUnifiedHandler(unittest.TestCase):
    """Test MEMORY unified command"""

    def setUp(self):
        """Set up test handler"""
        self.handler = MemoryUnifiedHandler()

    def test_tier_definitions(self):
        """Test tier configuration"""
        self.assertEqual(len(self.handler.tiers), 4)
        self.assertIn('private', self.handler.tiers)
        self.assertIn('shared', self.handler.tiers)
        self.assertIn('community', self.handler.tiers)
        self.assertIn('public', self.handler.tiers)

    def test_tier_priorities(self):
        """Test tier priority ordering"""
        self.assertEqual(self.handler.tiers['private']['priority'], 4)
        self.assertEqual(self.handler.tiers['shared']['priority'], 3)
        self.assertEqual(self.handler.tiers['community']['priority'], 2)
        self.assertEqual(self.handler.tiers['public']['priority'], 1)

    def test_show_picker(self):
        """Test interactive picker display"""
        result = self.handler._show_picker()
        self.assertIn("MEMORY - Select tier", result)
        self.assertIn("🔒 PRIVATE", result)
        self.assertIn("🔐 SHARED", result)
        self.assertIn("👥 COMMUNITY", result)
        self.assertIn("🌍 PUBLIC", result)

    def test_show_help(self):
        """Test help display"""
        result = self.handler._show_help()
        self.assertIn("MEMORY - Unified 4-Tier", result)
        self.assertIn("USAGE:", result)
        self.assertIn("EXAMPLES:", result)

    def test_content_security_analysis_password(self):
        """Test password file detection"""
        tier = self.handler._analyze_content_security("mypassword.txt", [])
        self.assertEqual(tier, 'private')

    def test_content_security_analysis_api_key(self):
        """Test API key detection"""
        tier = self.handler._analyze_content_security("api_keys.json", [])
        self.assertEqual(tier, 'private')

    def test_content_security_analysis_config(self):
        """Test config file detection"""
        tier = self.handler._analyze_content_security("team_config.json", [])
        self.assertEqual(tier, 'shared')

    def test_content_security_analysis_script(self):
        """Test script file detection"""
        tier = self.handler._analyze_content_security("backup.py", [])
        self.assertEqual(tier, 'community')

    def test_content_security_analysis_readme(self):
        """Test documentation detection"""
        tier = self.handler._analyze_content_security("README.md", [])
        self.assertEqual(tier, 'public')

    def test_tier_reason_password(self):
        """Test reason generation for password"""
        reason = self.handler._get_tier_reason("password.txt", 'private')
        self.assertIn("sensitive", reason.lower())

    def test_tier_reason_config(self):
        """Test reason generation for config"""
        reason = self.handler._get_tier_reason("config.json", 'shared')
        self.assertIn("config", reason.lower())


class TestFuzzyMatcher(unittest.TestCase):
    """Test fuzzy file matching"""

    def setUp(self):
        """Set up test matcher"""
        self.matcher = FuzzyMatcher()

    def test_abbreviations(self):
        """Test common abbreviations"""
        self.assertEqual(self.matcher.abbreviations['readme'], 'README.md')
        self.assertEqual(self.matcher.abbreviations['rm'], 'README.md')
        self.assertEqual(self.matcher.abbreviations['road'], 'ROADMAP.MD')

    def test_levenshtein_exact(self):
        """Test Levenshtein distance - exact match"""
        distance = self.matcher._levenshtein_distance("hello", "hello")
        self.assertEqual(distance, 0)

    def test_levenshtein_one_char(self):
        """Test Levenshtein distance - one character difference"""
        distance = self.matcher._levenshtein_distance("hello", "hallo")
        self.assertEqual(distance, 1)

    def test_levenshtein_multiple_chars(self):
        """Test Levenshtein distance - multiple differences"""
        distance = self.matcher._levenshtein_distance("kitten", "sitting")
        self.assertEqual(distance, 3)

    def test_calculate_score_exact_filename(self):
        """Test scoring - exact filename match"""
        score = self.matcher._calculate_score("README.md", "docs/README.md")
        self.assertGreaterEqual(score, 1000)

    def test_calculate_score_starts_with(self):
        """Test scoring - filename starts with query"""
        score = self.matcher._calculate_score("read", "README.md")
        self.assertGreaterEqual(score, 600)

    def test_calculate_score_contains(self):
        """Test scoring - filename contains query"""
        score = self.matcher._calculate_score("map", "ROADMAP.MD")
        self.assertGreaterEqual(score, 500)

    def test_get_match_reason(self):
        """Test match reason generation"""
        reason = self.matcher._get_match_reason("README", "README.md", 1000)
        self.assertEqual(reason, "Exact filename match")

        reason = self.matcher._get_match_reason("read", "README.md", 600)
        self.assertEqual(reason, "Filename contains query")

    def test_get_match_type(self):
        """Test match type categorization"""
        self.assertEqual(self.matcher._get_match_type(1000), "exact")
        self.assertEqual(self.matcher._get_match_type(600), "partial")
        self.assertEqual(self.matcher._get_match_type(350), "fuzzy")
        self.assertEqual(self.matcher._get_match_type(100), "weak")

    def test_recent_files_add(self):
        """Test adding recent files"""
        self.matcher.add_recent_file("file1.txt")
        self.matcher.add_recent_file("file2.txt")
        recent = self.matcher.get_recent_files()

        self.assertEqual(recent[0], "file2.txt")
        self.assertEqual(recent[1], "file1.txt")

    def test_recent_files_duplicate(self):
        """Test duplicate recent files (should move to front)"""
        self.matcher.add_recent_file("file1.txt")
        self.matcher.add_recent_file("file2.txt")
        self.matcher.add_recent_file("file1.txt")  # Duplicate
        recent = self.matcher.get_recent_files()

        self.assertEqual(recent[0], "file1.txt")
        self.assertEqual(len([f for f in recent if f == "file1.txt"]), 1)

    def test_recent_files_clear(self):
        """Test clearing recent files"""
        self.matcher.add_recent_file("file1.txt")
        self.matcher.clear_recent_files()
        recent = self.matcher.get_recent_files()

        self.assertEqual(len(recent), 0)


class TestAliasManager(unittest.TestCase):
    """Test alias management"""

    def setUp(self):
        """Set up test manager"""
        # Use temp path for testing
        self.temp_path = "/tmp/test_aliases.json"
        self.manager = AliasManager(user_data_path=self.temp_path)
        self.manager.custom_aliases = {}  # Clear any loaded aliases

    def tearDown(self):
        """Clean up temp file"""
        import os
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def test_builtin_aliases(self):
        """Test built-in aliases exist"""
        self.assertIn('?', self.manager.BUILTIN_ALIASES)
        self.assertIn('!!', self.manager.BUILTIN_ALIASES)
        self.assertIn('@', self.manager.BUILTIN_ALIASES)
        self.assertEqual(self.manager.BUILTIN_ALIASES['?'], 'HELP')

    def test_resolve_builtin_alias(self):
        """Test resolving built-in alias"""
        result = self.manager.resolve_alias("?")
        self.assertEqual(result, "HELP")

        result = self.manager.resolve_alias("d")
        self.assertEqual(result, "DOCS")

    def test_resolve_alias_with_args(self):
        """Test resolving alias with arguments"""
        result = self.manager.resolve_alias("d git")
        self.assertEqual(result, "DOCS git")

    def test_resolve_non_alias(self):
        """Test resolving non-alias command"""
        result = self.manager.resolve_alias("MEMORY --list")
        self.assertEqual(result, "MEMORY --list")

    def test_add_custom_alias(self):
        """Test adding custom alias"""
        success, msg = self.manager.add_alias("gm", "DOCS --manual git")
        self.assertTrue(success)
        self.assertIn("gm", self.manager.custom_aliases)
        self.assertEqual(self.manager.custom_aliases["gm"], "DOCS --manual git")

    def test_add_duplicate_alias(self):
        """Test adding duplicate alias without force"""
        self.manager.add_alias("gm", "DOCS --manual git")
        success, msg = self.manager.add_alias("gm", "OTHER COMMAND")

        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_add_duplicate_alias_force(self):
        """Test overriding alias with force"""
        self.manager.add_alias("gm", "DOCS --manual git")
        success, msg = self.manager.add_alias("gm", "OTHER COMMAND", force=True)

        self.assertTrue(success)
        self.assertEqual(self.manager.custom_aliases["gm"], "OTHER COMMAND")

    def test_remove_alias(self):
        """Test removing alias"""
        self.manager.add_alias("gm", "DOCS --manual git")
        success, msg = self.manager.remove_alias("gm")

        self.assertTrue(success)
        self.assertNotIn("gm", self.manager.custom_aliases)

    def test_remove_nonexistent_alias(self):
        """Test removing non-existent alias"""
        success, msg = self.manager.remove_alias("nonexistent")
        self.assertFalse(success)

    def test_invalid_alias_name(self):
        """Test invalid alias name"""
        success, msg = self.manager.add_alias("invalid alias!", "COMMAND")
        self.assertFalse(success)
        self.assertIn("Invalid", msg)

    def test_alias_usage_tracking(self):
        """Test usage tracking"""
        self.manager.resolve_alias("?")
        self.manager.resolve_alias("?")
        self.manager.resolve_alias("d")

        self.assertEqual(self.manager.alias_usage.get("?", 0), 2)
        self.assertEqual(self.manager.alias_usage.get("d", 0), 1)


class TestUniversalPicker(unittest.TestCase):
    """Test universal picker component"""

    def setUp(self):
        """Set up test picker"""
        self.config = PickerConfig(title="TEST PICKER")
        self.picker = UniversalPicker(self.config)

    def test_add_item(self):
        """Test adding items"""
        item = PickerItem(id="1", label="Test Item")
        self.picker.add_item(item)

        self.assertEqual(len(self.picker.items), 1)
        self.assertEqual(self.picker.items[0].label, "Test Item")

    def test_set_items(self):
        """Test setting multiple items"""
        items = [
            PickerItem(id="1", label="Item 1"),
            PickerItem(id="2", label="Item 2"),
        ]
        self.picker.set_items(items)

        self.assertEqual(len(self.picker.items), 2)

    def test_filter_items(self):
        """Test filtering items"""
        items = [
            PickerItem(id="1", label="Apple"),
            PickerItem(id="2", label="Banana"),
            PickerItem(id="3", label="Cherry"),
        ]
        self.picker.set_items(items)

        self.picker.filter_items("an")  # Should match Banana
        self.assertEqual(len(self.picker.filtered_items), 1)
        self.assertEqual(self.picker.filtered_items[0].label, "Banana")

    def test_filter_by_description(self):
        """Test filtering by description"""
        items = [
            PickerItem(id="1", label="A", description="Red fruit"),
            PickerItem(id="2", label="B", description="Yellow fruit"),
        ]
        self.picker.set_items(items)

        self.picker.filter_items("yellow")
        self.assertEqual(len(self.picker.filtered_items), 1)

    def test_toggle_item(self):
        """Test toggling item selection"""
        item = PickerItem(id="1", label="Test", selected=False)
        self.picker.add_item(item)

        self.picker.toggle_item("1")
        self.assertTrue(self.picker.items[0].selected)

        self.picker.toggle_item("1")
        self.assertFalse(self.picker.items[0].selected)

    def test_select_all(self):
        """Test selecting all items"""
        items = [
            PickerItem(id="1", label="Item 1"),
            PickerItem(id="2", label="Item 2"),
        ]
        self.picker.set_items(items)

        self.picker.select_all()
        for item in self.picker.items:
            self.assertTrue(item.selected)

    def test_deselect_all(self):
        """Test deselecting all items"""
        items = [
            PickerItem(id="1", label="Item 1", selected=True),
            PickerItem(id="2", label="Item 2", selected=True),
        ]
        self.picker.set_items(items)

        self.picker.deselect_all()
        for item in self.picker.items:
            self.assertFalse(item.selected)

    def test_get_selected_items(self):
        """Test getting selected items"""
        items = [
            PickerItem(id="1", label="Item 1", selected=True),
            PickerItem(id="2", label="Item 2", selected=False),
            PickerItem(id="3", label="Item 3", selected=True),
        ]
        self.picker.set_items(items)

        selected = self.picker.get_selected_items()
        self.assertEqual(len(selected), 2)

    def test_get_item_by_number(self):
        """Test getting item by number"""
        items = [
            PickerItem(id="1", label="First"),
            PickerItem(id="2", label="Second"),
        ]
        self.picker.set_items(items)

        item = self.picker.get_item_by_number(1)
        self.assertEqual(item.label, "First")

        item = self.picker.get_item_by_number(2)
        self.assertEqual(item.label, "Second")

        item = self.picker.get_item_by_number(99)
        self.assertIsNone(item)

    def test_render_output(self):
        """Test render produces output"""
        items = [
            PickerItem(id="1", label="Test Item", icon="📝"),
        ]
        self.picker.set_items(items)

        output = self.picker.render()
        self.assertIn("TEST PICKER", output)
        self.assertIn("Test Item", output)

    def test_compact_mode(self):
        """Test compact rendering"""
        self.picker.config.compact_mode = True
        items = [
            PickerItem(id="1", label="Item 1"),
        ]
        self.picker.set_items(items)

        output = self.picker.render()
        self.assertIn("TEST PICKER", output)
        self.assertIn("Item 1", output)


class TestPickerBuilder(unittest.TestCase):
    """Test picker builder"""

    def test_single_select_builder(self):
        """Test single-select builder"""
        items = [
            {'label': 'Option 1', 'icon': '📝'},
            {'label': 'Option 2', 'icon': '📄'},
        ]

        picker = PickerBuilder.single_select("TEST", items)

        self.assertEqual(picker.config.picker_type, PickerType.SINGLE)
        self.assertEqual(len(picker.items), 2)

    def test_multi_select_builder(self):
        """Test multi-select builder"""
        items = [
            {'label': 'Option 1'},
            {'label': 'Option 2'},
        ]

        picker = PickerBuilder.multi_select("TEST", items)

        self.assertEqual(picker.config.picker_type, PickerType.MULTI)
        self.assertEqual(len(picker.items), 2)

    def test_recent_picker_builder(self):
        """Test recent picker builder"""
        items = [
            {'label': 'Recent 1', 'icon': '📄'},
            {'label': 'Recent 2', 'icon': '📝'},
        ]

        picker = PickerBuilder.recent_picker("RECENT", items)

        self.assertEqual(picker.config.picker_type, PickerType.RECENT)
        self.assertEqual(len(picker.items), 2)


if __name__ == '__main__':
    unittest.main()
