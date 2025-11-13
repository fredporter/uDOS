#!/usr/bin/env python3
"""
Comprehensive Test Suite for v1.0.13 Theme System Enhancement
Tests ThemeManager, ThemeBuilder, import/export, validation, and preview rendering
Target: 100% pass rate
"""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add uDOS to path
sys.path.insert(0, '/Users/fredbook/Code/uDOS')

# Import services
from core.services.theme_manager import ThemeManager
from core.services.theme_builder import ThemeBuilder


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
            print(f"\n{'='*70}")
            print(f"FAILED TESTS")
            print(f"{'='*70}")
            for test_name, error in self.errors:
                print(f"  ❌ {test_name}")
                print(f"     {error}")

        return rate >= 100.0


def test_theme_manager_initialization(results):
    """Test ThemeManager initialization and setup."""
    print("\n" + "="*70)
    print("THEME MANAGER INITIALIZATION TESTS")
    print("="*70)

    try:
        manager = ThemeManager()
        results.record_pass("ThemeManager instantiation")
    except Exception as e:
        results.record_fail("ThemeManager instantiation", str(e))
        return

    # Test attributes exist
    try:
        assert hasattr(manager, 'json_themes_dir'), "Missing json_themes_dir"
        assert hasattr(manager, 'json_themes_cache'), "Missing json_themes_cache"
        assert hasattr(manager, 'available_json_themes'), "Missing available_json_themes"
        results.record_pass("ThemeManager has required attributes")
    except AssertionError as e:
        results.record_fail("ThemeManager attributes", str(e))

    # Test themes directory exists
    try:
        themes_dir = Path(manager.json_themes_dir)
        assert themes_dir.exists(), f"Themes directory not found: {themes_dir}"
        results.record_pass("Themes directory exists")
    except AssertionError as e:
        results.record_fail("Themes directory check", str(e))


def test_theme_manager_list_themes(results):
    """Test listing available themes."""
    print("\n" + "="*70)
    print("THEME MANAGER LIST TESTS")
    print("="*70)

    try:
        manager = ThemeManager()

        # Test basic listing
        theme_list = manager.list_json_themes(detailed=False)
        assert isinstance(theme_list, str), "list_json_themes should return string"
        results.record_pass("list_json_themes() returns string")

        # Test detailed listing
        detailed_list = manager.list_json_themes(detailed=True)
        assert isinstance(detailed_list, str), "Detailed listing should return string"
        assert len(detailed_list) >= len(theme_list), "Detailed should be longer"
        results.record_pass("list_json_themes(detailed=True) works")

        # Test available themes populated
        assert len(manager.available_json_themes) > 0, "Should have available themes"
        results.record_pass(f"Found {len(manager.available_json_themes)} available themes")

    except Exception as e:
        results.record_fail("Theme listing", str(e))


def test_theme_manager_load_theme(results):
    """Test loading themes."""
    print("\n" + "="*70)
    print("THEME MANAGER LOAD TESTS")
    print("="*70)

    manager = ThemeManager()

    # Test loading foundation theme (should exist)
    try:
        theme_data = manager.load_json_theme("foundation")
        assert theme_data is not None, "Foundation theme should load"
        assert isinstance(theme_data, dict), "Theme should be dict"
        assert "THEME_NAME" in theme_data, "Theme should have THEME_NAME"
        results.record_pass("load_json_theme('foundation') successful")
    except Exception as e:
        results.record_fail("Load foundation theme", str(e))

    # Test caching
    try:
        theme_data2 = manager.load_json_theme("foundation")
        assert "foundation" in manager.json_themes_cache, "Theme should be cached"
        results.record_pass("Theme caching works")
    except Exception as e:
        results.record_fail("Theme caching", str(e))

    # Test loading non-existent theme
    try:
        non_existent = manager.load_json_theme("this_theme_does_not_exist_12345")
        assert non_existent is None, "Non-existent theme should return None"
        results.record_pass("Non-existent theme returns None")
    except Exception as e:
        results.record_fail("Non-existent theme handling", str(e))


def test_theme_manager_validation(results):
    """Test theme validation."""
    print("\n" + "="*70)
    print("THEME MANAGER VALIDATION TESTS")
    print("="*70)

    manager = ThemeManager()

    # Test valid theme
    valid_theme = {
        "THEME_NAME": "TEST_THEME",
        "VERSION": "1.0.0",
        "NAME": "Test Theme",
        "STYLE": "Test",
        "DESCRIPTION": "Test theme",
        "ICON": "🧪",
        "CORE_SYSTEM": {
            "PROMPT_BASE": ">",
            "SYSTEM_NAME": "TEST"
        },
        "CORE_USER": {
            "USER_NAME": "Tester"
        },
        "TERMINOLOGY": {
            "CMD_CATALOG": "LIST",
            "CMD_LOAD": "LOAD",
            "CMD_SAVE": "SAVE",
            "CMD_HELP": "HELP",
            "CMD_CLS": "CLEAR"
        }
    }

    try:
        is_valid, errors = manager.validate_json_theme(valid_theme)
        assert is_valid, f"Valid theme rejected: {errors}"
        results.record_pass("Valid theme passes validation")
    except Exception as e:
        results.record_fail("Valid theme validation", str(e))

    # Test invalid theme (missing required fields)
    invalid_theme = {
        "THEME_NAME": "INVALID"
        # Missing VERSION, NAME, etc.
    }

    try:
        is_valid, errors = manager.validate_json_theme(invalid_theme)
        assert not is_valid, "Invalid theme should fail validation"
        assert len(errors) > 0, "Should report errors"
        results.record_pass("Invalid theme fails validation")
    except Exception as e:
        results.record_fail("Invalid theme validation", str(e))

    # Test empty theme
    try:
        is_valid, errors = manager.validate_json_theme({})
        assert not is_valid, "Empty theme should fail"
        results.record_pass("Empty theme fails validation")
    except Exception as e:
        results.record_fail("Empty theme validation", str(e))


def test_theme_manager_metadata(results):
    """Test theme metadata extraction."""
    print("\n" + "="*70)
    print("THEME MANAGER METADATA TESTS")
    print("="*70)

    manager = ThemeManager()

    try:
        metadata = manager.get_json_theme_metadata("foundation")
        assert metadata is not None, "Should get metadata for foundation"
        assert hasattr(metadata, 'name'), "Metadata should have name"
        assert hasattr(metadata, 'version'), "Metadata should have version"
        assert hasattr(metadata, 'style'), "Metadata should have style"
        results.record_pass("get_json_theme_metadata() works")
    except Exception as e:
        results.record_fail("Theme metadata extraction", str(e))

    # Test non-existent theme metadata
    try:
        metadata = manager.get_json_theme_metadata("nonexistent")
        assert metadata is None, "Non-existent theme metadata should be None"
        results.record_pass("Non-existent theme metadata returns None")
    except Exception as e:
        results.record_fail("Non-existent metadata handling", str(e))


def test_theme_manager_preview(results):
    """Test theme preview functionality."""
    print("\n" + "="*70)
    print("THEME MANAGER PREVIEW TESTS")
    print("="*70)

    manager = ThemeManager()

    try:
        preview = manager.preview_json_theme("foundation")
        assert preview is not None, "Preview should return content"
        assert isinstance(preview, str), "Preview should be string"
        assert len(preview) > 0, "Preview should have content"
        results.record_pass("preview_json_theme('foundation') works")
    except Exception as e:
        results.record_fail("Theme preview", str(e))

    # Test preview of non-existent theme
    try:
        preview = manager.preview_json_theme("nonexistent")
        # Should handle gracefully (None or error message)
        results.record_pass("Preview handles non-existent theme")
    except Exception as e:
        results.record_fail("Preview error handling", str(e))


def test_theme_manager_stats(results):
    """Test theme statistics."""
    print("\n" + "="*70)
    print("THEME MANAGER STATISTICS TESTS")
    print("="*70)

    manager = ThemeManager()

    try:
        stats = manager.get_json_theme_stats()
        assert stats is not None, "Stats should return content"
        assert isinstance(stats, str), "Stats should be string"
        results.record_pass("get_json_theme_stats() works")
    except Exception as e:
        results.record_fail("Theme statistics", str(e))


def test_theme_manager_export_import(results):
    """Test theme export and import."""
    print("\n" + "="*70)
    print("THEME MANAGER EXPORT/IMPORT TESTS")
    print("="*70)

    manager = ThemeManager()

    with tempfile.TemporaryDirectory() as tmpdir:
        export_path = Path(tmpdir) / "test_theme.udostheme"

        # Test export
        try:
            success = manager.export_json_theme("foundation", str(export_path))
            assert success, "Export should succeed"
            assert export_path.exists(), "Export file should exist"
            results.record_pass("export_json_theme() works")
        except Exception as e:
            results.record_fail("Theme export", str(e))
            return

        # Verify export file structure
        try:
            with open(export_path, 'r') as f:
                exported = json.load(f)
            # Export format includes metadata in theme data
            assert "EXPORTED" in exported or "THEME_NAME" in exported, "Should have export metadata or theme data"
            results.record_pass("Exported .udostheme format valid")
        except Exception as e:
            results.record_fail("Export format validation", str(e))

        # Test import
        try:
            import_name = f"imported_test_theme_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            success = manager.import_json_theme(str(export_path), import_name)
            assert success, "Import should succeed"

            # Verify imported theme exists
            imported_theme = manager.load_json_theme(import_name)
            assert imported_theme is not None, "Imported theme should be loadable"

            # Clean up imported theme
            imported_file = Path(manager.json_themes_dir) / f"{import_name}.json"
            if imported_file.exists():
                imported_file.unlink()

            results.record_pass("import_json_theme() works")
        except Exception as e:
            results.record_fail("Theme import", str(e))
def test_theme_builder_initialization(results):
    """Test ThemeBuilder initialization."""
    print("\n" + "="*70)
    print("THEME BUILDER INITIALIZATION TESTS")
    print("="*70)

    try:
        builder = ThemeBuilder()
        results.record_pass("ThemeBuilder instantiation")
    except Exception as e:
        results.record_fail("ThemeBuilder instantiation", str(e))
        return

    # Test attributes
    try:
        assert hasattr(builder, 'output_dir'), "Missing output_dir"
        results.record_pass("ThemeBuilder has required attributes")
    except AssertionError as e:
        results.record_fail("ThemeBuilder attributes", str(e))


def test_theme_builder_templates(results):
    """Test ThemeBuilder template methods."""
    print("\n" + "="*70)
    print("THEME BUILDER TEMPLATE TESTS")
    print("="*70)

    builder = ThemeBuilder()

    # Test internal templates
    templates = ['minimal', 'scifi', 'fantasy', 'corporate']

    for template_name in templates:
        try:
            method_name = f"_get_{template_name.replace('-', '_')}_template"
            if hasattr(builder, method_name):
                template = getattr(builder, method_name)()
                assert isinstance(template, dict), f"{template_name} should return dict"
                assert "THEME_NAME" in template, f"{template_name} should have THEME_NAME"
                results.record_pass(f"Internal template '{template_name}' works")
            else:
                results.record_fail(f"Template method {method_name}", "Method not found")
        except Exception as e:
            results.record_fail(f"Internal template '{template_name}'", str(e))

    # Test list_templates
    try:
        template_list = builder.list_templates()
        assert isinstance(template_list, str), "Template list should be string"
        results.record_pass("list_templates() works")
    except Exception as e:
        results.record_fail("Template listing", str(e))


def test_theme_builder_create_from_template(results):
    """Test creating themes from templates."""
    print("\n" + "="*70)
    print("THEME BUILDER CREATE FROM TEMPLATE TESTS")
    print("="*70)

    builder = ThemeBuilder()

    try:
        customizations = {
            "THEME_NAME": "TEST_MINIMAL",
            "NAME": "Test Minimal Theme",
            "DESCRIPTION": "Test theme from minimal template"
        }

        theme = builder.create_from_template("minimal", customizations)
        assert theme is not None, "Should create theme"
        assert isinstance(theme, dict), "Should return dict"
        assert theme["THEME_NAME"] == "TEST_MINIMAL", "Should apply customizations"
        results.record_pass("create_from_template('minimal') works")
    except Exception as e:
        results.record_fail("Create from minimal template", str(e))

    # Test invalid template (falls back to minimal)
    try:
        theme = builder.create_from_template("invalid_template_xyz", {})
        assert theme is not None, "Invalid template should fallback to minimal"
        results.record_pass("Invalid template falls back to minimal")
    except Exception as e:
        results.record_fail("Invalid template handling", str(e))


def test_theme_builder_validation(results):
    """Test ThemeBuilder validation and auto-fix."""
    print("\n" + "="*70)
    print("THEME BUILDER VALIDATION TESTS")
    print("="*70)

    builder = ThemeBuilder()

    # Test valid theme
    valid_theme = {
        "THEME_NAME": "VALID",
        "VERSION": "1.0.0",
        "NAME": "Valid Theme",
        "STYLE": "Test",
        "DESCRIPTION": "Valid test theme",
        "ICON": "✅"
    }

    try:
        fixed, warnings = builder.validate_and_fix(valid_theme)
        assert fixed is not None, "Should return fixed theme"
        assert isinstance(warnings, list), "Should return warnings list"
        results.record_pass("validate_and_fix() with valid theme")
    except Exception as e:
        results.record_fail("Validation with valid theme", str(e))

    # Test theme with missing optional fields
    incomplete_theme = {
        "THEME_NAME": "INCOMPLETE",
        "VERSION": "1.0.0",
        "NAME": "Incomplete Theme"
        # Missing STYLE, DESCRIPTION, ICON
    }

    try:
        fixed, warnings = builder.validate_and_fix(incomplete_theme)
        assert fixed is not None, "Should auto-fix incomplete theme"
        assert "STYLE" in fixed or len(warnings) > 0, "Should fix or warn about missing fields"
        results.record_pass("validate_and_fix() auto-fixes missing fields")
    except Exception as e:
        results.record_fail("Auto-fix validation", str(e))


def test_theme_builder_save(results):
    """Test saving themes."""
    print("\n" + "="*70)
    print("THEME BUILDER SAVE TESTS")
    print("="*70)

    builder = ThemeBuilder()

    test_theme = {
        "THEME_NAME": "SAVE_TEST",
        "VERSION": "1.0.0",
        "NAME": "Save Test Theme",
        "STYLE": "Test",
        "DESCRIPTION": "Theme for save testing",
        "ICON": "💾"
    }

    try:
        success = builder.save_theme(test_theme, "save_test")
        assert success, "Save should succeed"

        # Verify file exists
        theme_file = Path(builder.output_dir) / "save_test.json"
        assert theme_file.exists(), "Theme file should exist"

        # Verify content
        with open(theme_file, 'r') as f:
            saved = json.load(f)
        assert saved["THEME_NAME"] == "SAVE_TEST", "Saved content should match"

        results.record_pass("save_theme() works")

        # Clean up
        theme_file.unlink()
    except Exception as e:
        results.record_fail("Theme save", str(e))
def test_theme_builder_copy(results):
    """Test copying themes."""
    print("\n" + "="*70)
    print("THEME BUILDER COPY TESTS")
    print("="*70)

    builder = ThemeBuilder()

    try:
        modifications = {
            "NAME": "Copied Foundation Theme",
            "DESCRIPTION": "A copy of foundation for testing"
        }

        copied = builder.copy_theme("foundation", "foundation_copy", modifications)
        assert copied is not None, "Should copy theme"
        assert isinstance(copied, dict), "Should return dict"
        assert copied["NAME"] == "Copied Foundation Theme", "Should apply modifications"
        results.record_pass("copy_theme() works")
    except Exception as e:
        results.record_fail("Theme copying", str(e))

    # Test copying non-existent theme
    try:
        copied = builder.copy_theme("nonexistent", "new_theme", {})
        assert copied is None, "Copying non-existent should return None"
        results.record_pass("Copy non-existent theme returns None")
    except Exception as e:
        results.record_fail("Copy non-existent handling", str(e))


def test_theme_builder_color_suggestions(results):
    """Test color palette suggestions."""
    print("\n" + "="*70)
    print("THEME BUILDER COLOR SUGGESTIONS TESTS")
    print("="*70)

    builder = ThemeBuilder()

    styles = ['sci-fi', 'fantasy', 'corporate', 'cyberpunk']

    for style in styles:
        try:
            suggestions = builder.get_color_palette_suggestions(style)
            assert suggestions is not None, f"Should get suggestions for {style}"
            assert isinstance(suggestions, dict), "Suggestions should be dict"
            results.record_pass(f"Color suggestions for '{style}'")
        except Exception as e:
            results.record_fail(f"Color suggestions '{style}'", str(e))


def test_template_files(results):
    """Test external template files."""
    print("\n" + "="*70)
    print("TEMPLATE FILES TESTS")
    print("="*70)

    templates_dir = Path("/Users/fredbook/Code/uDOS/data/themes/templates")

    if not templates_dir.exists():
        results.record_fail("Templates directory", "Directory not found")
        return

    template_files = [
        "minimal.json",
        "dark-modern.json",
        "light-professional.json",
        "high-contrast.json"
    ]

    for filename in template_files:
        template_path = templates_dir / filename

        try:
            assert template_path.exists(), f"{filename} not found"

            # Load and validate
            with open(template_path, 'r') as f:
                template_data = json.load(f)

            assert "THEME_NAME" in template_data, f"{filename} missing THEME_NAME"
            assert "VERSION" in template_data, f"{filename} missing VERSION"

            results.record_pass(f"Template file '{filename}' valid")
        except Exception as e:
            results.record_fail(f"Template file '{filename}'", str(e))

    # Test README exists
    try:
        readme_path = templates_dir / "README.md"
        assert readme_path.exists(), "README.md not found"
        results.record_pass("Templates README.md exists")
    except AssertionError as e:
        results.record_fail("Templates README", str(e))


def test_integration_full_workflow(results):
    """Test complete theme creation workflow."""
    print("\n" + "="*70)
    print("INTEGRATION: FULL WORKFLOW TESTS")
    print("="*70)

    builder = ThemeBuilder()
    manager = ThemeManager()

    workflow_theme_name = "integration_test_theme"

    try:
        # 1. Create from template
        customizations = {
            "THEME_NAME": "INTEGRATION_TEST",
            "NAME": "Integration Test Theme",
            "DESCRIPTION": "Theme for integration testing"
        }
        theme = builder.create_from_template("minimal", customizations)
        assert theme is not None, "Step 1: Create from template failed"
        results.record_pass("Integration: Create from template")

        # 2. Validate and fix
        fixed, warnings = builder.validate_and_fix(theme)
        assert fixed is not None, "Step 2: Validation failed"
        results.record_pass("Integration: Validate theme")

        # 3. Save theme
        success = builder.save_theme(fixed, workflow_theme_name)
        assert success, "Step 3: Save failed"
        results.record_pass("Integration: Save theme")

        # 4. Load with ThemeManager
        loaded = manager.load_json_theme(workflow_theme_name)
        assert loaded is not None, "Step 4: Load failed"
        results.record_pass("Integration: Load theme")

        # 5. Validate with ThemeManager
        is_valid, errors = manager.validate_json_theme(loaded)
        assert is_valid, f"Step 5: Validation failed: {errors}"
        results.record_pass("Integration: Validate loaded theme")

        # 6. Preview
        preview = manager.preview_json_theme(workflow_theme_name)
        assert preview is not None, "Step 6: Preview failed"
        results.record_pass("Integration: Preview theme")

        # 7. Export
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "integration.udostheme"
            success = manager.export_json_theme(workflow_theme_name, str(export_path))
            assert success, "Step 7: Export failed"
            assert export_path.exists(), "Export file not created"
            results.record_pass("Integration: Export theme")

            # 8. Import
            import_name = "integration_imported"
            success = manager.import_json_theme(str(export_path), import_name)
            assert success, "Step 8: Import failed"
            results.record_pass("Integration: Import theme")

        # Clean up
        theme_file = Path(builder.output_dir) / f"{workflow_theme_name}.json"
        if theme_file.exists():
            theme_file.unlink()
        imported_file = Path(builder.output_dir) / f"{import_name}.json"
        if imported_file.exists():
            imported_file.unlink()

        results.record_pass("Integration: Complete workflow successful")

    except Exception as e:
        results.record_fail("Integration workflow", str(e))


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("uDOS v1.0.13 THEME SYSTEM TEST SUITE")
    print("="*70)
    print("Testing: ThemeManager, ThemeBuilder, Templates, Import/Export")
    print("Target: 100% Pass Rate")
    print("="*70)

    results = TestResults()

    # Run all test suites
    test_theme_manager_initialization(results)
    test_theme_manager_list_themes(results)
    test_theme_manager_load_theme(results)
    test_theme_manager_validation(results)
    test_theme_manager_metadata(results)
    test_theme_manager_preview(results)
    test_theme_manager_stats(results)
    test_theme_manager_export_import(results)

    test_theme_builder_initialization(results)
    test_theme_builder_templates(results)
    test_theme_builder_create_from_template(results)
    test_theme_builder_validation(results)
    test_theme_builder_save(results)
    test_theme_builder_copy(results)
    test_theme_builder_color_suggestions(results)

    test_template_files(results)
    test_integration_full_workflow(results)

    # Print summary
    success = results.summary()

    if success:
        print(f"\n{'='*70}")
        print("✅ ALL TESTS PASSED - 100% SUCCESS RATE!")
        print(f"{'='*70}\n")
        return 0
    else:
        print(f"\n{'='*70}")
        print("❌ SOME TESTS FAILED - SEE DETAILS ABOVE")
        print(f"{'='*70}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
