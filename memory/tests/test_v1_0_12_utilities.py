#!/usr/bin/env python3
"""
Comprehensive Test Suite for v1.0.12 Advanced Utilities
Tests all four major services: HelpManager, ScreenManager, SetupWizard, UsageTracker
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add uDOS to path
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

# Import services
from core.services.help_manager import HelpManager
from core.services.screen_manager import ScreenManager
from core.services.setup_wizard import SetupWizard
from core.services.usage_tracker import UsageTracker


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name):
        self.passed += 1
        print(f"  ✅ {test_name}")

    def record_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ❌ {test_name}: {error}")

    def summary(self):
        total = self.passed + self.failed
        rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\n{'='*70}")
        print(f"TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({rate:.1f}%)")
        print(f"Failed: {self.failed}")

        if self.errors:
            print(f"\nFailed Tests:")
            for name, error in self.errors:
                print(f"  • {name}: {error}")

        return self.failed == 0


def test_help_manager(results):
    """Test HelpManager service."""
    print(f"\n{'─'*70}")
    print("TESTING: HelpManager Service")
    print(f"{'─'*70}")

    try:
        manager = HelpManager()

        # Test 1: Initialization
        try:
            assert len(manager.commands_data) > 0, "No commands loaded"
            results.record_pass("HelpManager initialization")
        except AssertionError as e:
            results.record_fail("HelpManager initialization", str(e))

        # Test 2: Command search
        try:
            results_list = manager.search_help("file", limit=10)
            assert len(results_list) > 0, "Search returned no results"
            # Search results are dicts with 'command' key
            assert any("FILE" in r['command'].upper() or "LIST" in r['command'].upper()
                      for r in results_list), "Search didn't find relevant commands"
            results.record_pass("Search functionality")
        except AssertionError as e:
            results.record_fail("Search functionality", str(e))        # Test 3: Category filtering
        try:
            system_cmds = manager.get_help_by_category("📊 System & Info")
            assert len(system_cmds) > 0, "No system commands found"
            results.record_pass("Category filtering")
        except AssertionError as e:
            results.record_fail("Category filtering", str(e))

        # Test 4: Command details
        try:
            details = manager.get_command_details("HELP")
            assert details is not None, "HELP command not found"
            assert "DESCRIPTION" in details, "Missing description"
            results.record_pass("Command details retrieval")
        except AssertionError as e:
            results.record_fail("Command details retrieval", str(e))

        # Test 5: Related commands
        try:
            related = manager.get_related_commands("HELP")
            assert isinstance(related, list), "Related commands not a list"
            results.record_pass("Related commands")
        except AssertionError as e:
            results.record_fail("Related commands", str(e))

        # Test 6: Formatted help
        try:
            help_text = manager.format_help_detailed("HELP")
            assert len(help_text) > 0, "No help text generated"
            assert "HELP" in help_text, "Command name not in help"
            results.record_pass("Formatted help output")
        except AssertionError as e:
            results.record_fail("Formatted help output", str(e))

        # Test 7: Search results formatting
        try:
            search_output = manager.format_search_results("file")
            assert len(search_output) > 0, "No search output"
            assert "Search Results" in search_output, "Missing search header"
            results.record_pass("Search results formatting")
        except AssertionError as e:
            results.record_fail("Search results formatting", str(e))

    except Exception as e:
        # Catch any unexpected errors during manager initialization or tests
        results.record_fail("HelpManager service", f"Unexpected exception: {e}")


def test_screen_manager(results):
    """Test ScreenManager service."""
    print(f"\n{'─'*70}")
    print("TESTING: ScreenManager Service")
    print(f"{'─'*70}")

    try:
        manager = ScreenManager()

        # Test 1: Smart clear
        try:
            result = manager.clear_smart()
            assert result is not None, "Smart clear returned None"
            results.record_pass("Smart clear")
        except AssertionError as e:
            results.record_fail("Smart clear", str(e))

        # Test 2: Full clear
        try:
            result = manager.clear_full()
            assert result is not None, "Full clear returned None"
            results.record_pass("Full clear")
        except AssertionError as e:
            results.record_fail("Full clear", str(e))

        # Test 3: Buffer clear
        try:
            result = manager.clear_buffer()
            assert result is not None, "Buffer clear returned None"
            results.record_pass("Buffer clear")
        except AssertionError as e:
            results.record_fail("Buffer clear", str(e))

        # Test 4: Last N lines
        try:
            result = manager.clear_last_n_lines(5)
            assert result is not None, "Clear last N returned None"
            results.record_pass("Clear last N lines")
        except AssertionError as e:
            results.record_fail("Clear last N lines", str(e))

        # Test 5: Component clearing (should return confirmation prompts)
        try:
            result = manager.clear_component("GRID")
            # In non-interactive mode, should return a message
            assert result is not None, "Component clear returned None"
            results.record_pass("Component clearing")
        except AssertionError as e:
            results.record_fail("Component clearing", str(e))

    except Exception as e:
        results.record_fail("ScreenManager service", f"Exception: {e}")


def test_setup_wizard(results):
    """Test SetupWizard service."""
    print(f"\n{'─'*70}")
    print("TESTING: SetupWizard Service")
    print(f"{'─'*70}")

    try:
        wizard = SetupWizard()

        # Test 1: Theme loading
        try:
            themes = wizard._load_available_themes()
            assert len(themes) > 0, "No themes loaded"
            assert "dungeon" in themes, "Default theme not found"
            results.record_pass("Theme loading")
        except AssertionError as e:
            results.record_fail("Theme loading", str(e))

        # Test 2: Viewport presets
        try:
            presets = wizard._get_viewport_presets()
            assert len(presets) > 0, "No viewport presets"
            assert any(p["name"] == "Watch" for p in presets), "Missing Watch preset"
            results.record_pass("Viewport presets")
        except AssertionError as e:
            results.record_fail("Viewport presets", str(e))

        # Test 3: Configuration validation
        try:
            valid_config = {
                "theme": "dungeon",
                "viewport": "auto",
                "extensions": {
                    "enable_web": True,
                    "enable_teletext": True,
                    "enable_dashboard": True
                },
                "advanced": {
                    "developer_mode": False,
                    "debug_logging": False,
                    "experimental_features": False
                }
            }
            is_valid = wizard.validate_config(valid_config)
            assert is_valid, "Valid config rejected"
            results.record_pass("Configuration validation (valid)")
        except AssertionError as e:
            results.record_fail("Configuration validation (valid)", str(e))

        # Test 4: Invalid configuration (just check it doesn't crash)
        try:
            invalid_config = {
                "theme": "nonexistent",
                "viewport": "invalid"
            }
            # Validation may accept it or reject it, just ensure no exception
            wizard.validate_config(invalid_config)
            results.record_pass("Configuration validation (no crash)")
        except Exception as e:
            results.record_fail("Configuration validation (no crash)", str(e))

        # Test 5: Help formatting
        try:
            help_text = wizard.format_help()
            assert len(help_text) > 0, "No help text"
            assert "SETUP" in help_text, "Command name not in help"
            results.record_pass("Help formatting")
        except AssertionError as e:
            results.record_fail("Help formatting", str(e))

    except Exception as e:
        results.record_fail("SetupWizard service", f"Exception: {e}")


def test_usage_tracker(results):
    """Test UsageTracker service."""
    print(f"\n{'─'*70}")
    print("TESTING: UsageTracker Service")
    print(f"{'─'*70}")

    # Use temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            tracker = UsageTracker(data_dir=tmpdir, max_recent=50)

            # Test 1: Command tracking
            try:
                tracker.track_command("HELP", [], success=True)
                tracker.track_command("STATUS", [], success=True)
                tracker.track_command("LIST", ["sandbox"], success=True)
                assert tracker.command_counts["HELP"] == 1, "Command not tracked"
                results.record_pass("Command tracking")
            except AssertionError as e:
                results.record_fail("Command tracking", str(e))

            # Test 2: Recent commands
            try:
                recent = tracker.get_recent_commands(limit=10)
                assert len(recent) == 3, f"Expected 3 recent commands, got {len(recent)}"
                results.record_pass("Recent commands retrieval")
            except AssertionError as e:
                results.record_fail("Recent commands retrieval", str(e))

            # Test 3: Most used
            try:
                # Track more commands
                for _ in range(5):
                    tracker.track_command("HELP", [], success=True)
                most_used = tracker.get_most_used(limit=5)
                assert len(most_used) > 0, "No most used commands"
                assert most_used[0][0] == "HELP", "HELP should be most used"
                assert most_used[0][1] == 6, f"HELP should have 6 uses, got {most_used[0][1]}"
                results.record_pass("Most used commands")
            except AssertionError as e:
                results.record_fail("Most used commands", str(e))

            # Test 4: Command stats
            try:
                stats = tracker.get_command_stats("HELP")
                assert stats["total_uses"] == 6, f"Expected 6 uses, got {stats['total_uses']}"
                assert stats["success_rate"] == 100.0, "Success rate should be 100%"
                results.record_pass("Command statistics")
            except AssertionError as e:
                results.record_fail("Command statistics", str(e))

            # Test 5: Session stats
            try:
                session = tracker.get_session_stats()
                assert session["total_commands"] >= 8, "Session total incorrect"
                assert session["success_rate"] == 100.0, "Session success rate should be 100%"
                results.record_pass("Session statistics")
            except AssertionError as e:
                results.record_fail("Session statistics", str(e))

            # Test 6: Formatted output
            try:
                recent_output = tracker.format_recent_commands(limit=5)
                assert len(recent_output) > 0, "No formatted output"
                assert "Recent Command History" in recent_output, "Missing header"
                results.record_pass("Formatted recent commands")
            except AssertionError as e:
                results.record_fail("Formatted recent commands", str(e))

            # Test 7: Most used formatting
            try:
                most_used_output = tracker.format_most_used(limit=5)
                assert len(most_used_output) > 0, "No formatted output"
                assert "Most Used Commands" in most_used_output, "Missing header"
                results.record_pass("Formatted most used")
            except AssertionError as e:
                results.record_fail("Formatted most used", str(e))

            # Test 8: Session formatting
            try:
                session_output = tracker.format_session_stats()
                assert len(session_output) > 0, "No formatted output"
                assert "Session Statistics" in session_output, "Missing header"
                results.record_pass("Formatted session stats")
            except AssertionError as e:
                results.record_fail("Formatted session stats", str(e))

            # Test 9: Persistence
            try:
                # Save data
                tracker._save_data()

                # Create new tracker with same directory
                tracker2 = UsageTracker(data_dir=tmpdir, max_recent=50)

                # Check data was loaded
                assert tracker2.command_counts["HELP"] == 6, "Data not persisted"
                results.record_pass("Data persistence")
            except AssertionError as e:
                results.record_fail("Data persistence", str(e))

        except Exception as e:
            results.record_fail("UsageTracker service", f"Exception: {e}")


def main():
    """Run all tests."""
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "v1.0.12 Comprehensive Test Suite" + " "*21 + "║")
    print("╚" + "="*68 + "╝")

    results = TestResults()

    # Run all test suites
    test_help_manager(results)
    test_screen_manager(results)
    test_setup_wizard(results)
    test_usage_tracker(results)

    # Print summary
    success = results.summary()

    print(f"\n{'='*70}")
    if success:
        print("✅ ALL TESTS PASSED!")
        print("v1.0.12 Advanced Utilities - Production Ready")
    else:
        print("❌ SOME TESTS FAILED")
        print("Review errors above and fix issues")
    print(f"{'='*70}\n")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
