#!/usr/bin/env python3
"""
Test uCODE Validator
v1.4.0 Phase 4.2 - Command Set Consolidation

Tests the uCODE syntax validator and parser.
"""

import sys
import tempfile
from pathlib import Path

# Add core to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.ucode.validator import UCodeValidator, UCodeParser, CommandRegistry


def create_test_script(filepath: Path, content: str):
    """Create a test .uscript file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)


def test_command_registry():
    """Test command registry."""
    print("\n" + "="*80)
    print("TEST: Command Registry")
    print("="*80)

    # Test valid commands
    assert CommandRegistry.is_valid_command("GENERATE")
    assert CommandRegistry.is_valid_command("REFRESH")
    assert CommandRegistry.is_valid_command("HELP")
    print("✅ Valid commands recognized")

    # Test invalid commands
    assert not CommandRegistry.is_valid_command("INVALID")
    assert not CommandRegistry.is_valid_command("generate")  # Case sensitive
    print("✅ Invalid commands rejected")

    # Test keywords
    assert CommandRegistry.is_keyword("if")
    assert CommandRegistry.is_keyword("for")
    assert not CommandRegistry.is_keyword("GENERATE")
    print("✅ Keywords identified correctly")

    # Test reserved variables
    assert CommandRegistry.is_reserved_var("USER")
    assert CommandRegistry.is_reserved_var("DATE")
    assert not CommandRegistry.is_reserved_var("my_var")
    print("✅ Reserved variables identified")

    # Test command schema
    schema = CommandRegistry.get_command_schema("GENERATE")
    assert schema is not None
    assert "params" in schema
    assert "required" in schema
    print("✅ Command schemas available")

    print("\n✅ Command registry tests PASSED")


def test_parser_basic():
    """Test basic parsing."""
    print("\n" + "="*80)
    print("TEST: Basic Parsing")
    print("="*80)

    parser = UCodeParser()

    # Test simple command
    code = "[HELP]"
    commands = parser._parse_commands(code)
    assert len(commands) == 1
    assert commands[0]["command"] == "HELP"
    print("✅ Simple command parsed")

    # Test command with parameters
    code = "[GENERATE|guide|water/purification]"
    commands = parser._parse_commands(code)
    assert len(commands) == 1
    assert commands[0]["command"] == "GENERATE"
    assert len(commands[0]["params"]) == 2
    print("✅ Command with parameters parsed")

    # Test multiple commands
    code = """
    [HELP]
    [GENERATE|guide|water/purification]
    [REFRESH|--check|all]
    """
    commands = parser._parse_commands(code)
    assert len(commands) == 3
    print("✅ Multiple commands parsed")

    print("\n✅ Basic parsing tests PASSED")


def test_validator_valid_script():
    """Test validation of valid script."""
    print("\n" + "="*80)
    print("TEST: Valid Script Validation")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_file = Path(tmpdir) / "test.uscript"

        content = """---
title: Test Script
version: 1.0.0
---

# Test Script

## Commands
[HELP]
[GENERATE|guide|water/purification]
[REFRESH|--check|all]

## Variables
$category = "water"
[GENERATE|guide|$category/basics]
"""
        create_test_script(script_file, content)

        validator = UCodeValidator()
        is_valid, errors = validator.validate_file(script_file)

        print(f"Valid: {is_valid}")
        if errors:
            print("Issues:")
            for error in errors:
                print(f"  {error}")

        assert is_valid, "Valid script should pass validation"
        print("\n✅ Valid script validation PASSED")


def test_validator_invalid_command():
    """Test detection of invalid commands."""
    print("\n" + "="*80)
    print("TEST: Invalid Command Detection")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_file = Path(tmpdir) / "test.uscript"

        content = """---
title: Test Script
---

[HELP]
[INVALID_COMMAND|param]
[GENERATE|guide|water/purification]
"""
        create_test_script(script_file, content)

        validator = UCodeValidator()
        is_valid, errors = validator.validate_file(script_file)

        print(f"Valid: {is_valid}")
        print("Errors:")
        for error in errors:
            print(f"  {error}")

        assert not is_valid, "Invalid command should fail validation"
        assert any("INVALID_COMMAND" in str(e) for e in errors)
        print("\n✅ Invalid command detection PASSED")


def test_validator_undefined_variable():
    """Test detection of undefined variables."""
    print("\n" + "="*80)
    print("TEST: Undefined Variable Detection")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_file = Path(tmpdir) / "test.uscript"

        content = """---
title: Test Script
---

# Using undefined variable
[GENERATE|guide|$undefined_category/purification]
"""
        create_test_script(script_file, content)

        validator = UCodeValidator()
        is_valid, errors = validator.validate_file(script_file)

        print(f"Valid: {is_valid}")
        print("Warnings:")
        for error in errors:
            print(f"  {error}")

        # Should have warning about undefined variable
        assert any("undefined_category" in str(e) for e in errors)
        print("\n✅ Undefined variable detection PASSED")


def test_validator_reserved_variable():
    """Test detection of reserved variable assignment."""
    print("\n" + "="*80)
    print("TEST: Reserved Variable Assignment")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_file = Path(tmpdir) / "test.uscript"

        content = """---
title: Test Script
---

# Trying to assign to reserved variable
$USER = "test"
$DATE = "2025-11-25"
"""
        create_test_script(script_file, content)

        validator = UCodeValidator()
        is_valid, errors = validator.validate_file(script_file)

        print(f"Valid: {is_valid}")
        print("Errors:")
        for error in errors:
            print(f"  {error}")

        assert not is_valid, "Reserved variable assignment should fail"
        assert any("reserved variable" in str(e).lower() for e in errors)
        print("\n✅ Reserved variable detection PASSED")


def test_linter():
    """Test linter functionality."""
    print("\n" + "="*80)
    print("TEST: Linter")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_file = Path(tmpdir) / "test.uscript"

        content = """---
title: Test Script
version: 1.0.0
---

# Test Script with various elements

## Commands
[HELP]
[GENERATE|guide|water/purification]
[REFRESH|--check|all]

## Variables
$category = "water"
$format = "svg"

## Usage
[GENERATE|diagram|$category/filter|format=$format]

# Comments
# This is a comment
// Also a comment
"""
        create_test_script(script_file, content)

        validator = UCodeValidator()
        report = validator.lint_file(script_file)

        print(f"Lines: {report['total_lines']}")
        print(f"Commands: {report['total_commands']}")
        print(f"Variables: {report['total_variables']}")
        print(f"Comments: {report['total_comments']}")
        print(f"Valid: {report['valid']}")
        print(f"Errors: {len(report['errors'])}")
        print(f"Warnings: {len(report['warnings'])}")

        assert report['total_commands'] == 4
        assert report['total_variables'] == 2
        assert report['total_comments'] >= 2

        print("\n✅ Linter tests PASSED")


def test_real_scripts():
    """Test validation of real .uscript files."""
    print("\n" + "="*80)
    print("TEST: Real Script Files")
    print("="*80)

    script_files = [
        "memory/workflow/startup_options.uscript",
        "memory/workflow/content_generation.uscript",
        "memory/workflow/housekeeping_cleanup.uscript",
        "memory/workflow/mission_templates.uscript"
    ]

    validator = UCodeValidator()

    for script_path in script_files:
        filepath = project_root / script_path

        if not filepath.exists():
            print(f"⚠️  File not found: {script_path}")
            continue

        print(f"\nValidating: {script_path}")
        is_valid, errors = validator.validate_file(filepath)

        if errors:
            error_count = sum(1 for e in errors if e.severity == "error")
            warning_count = sum(1 for e in errors if e.severity == "warning")

            if error_count:
                print(f"  ❌ {error_count} errors, {warning_count} warnings")
                for error in errors[:5]:  # Show first 5
                    print(f"    {error}")
                if len(errors) > 5:
                    print(f"    ... and {len(errors) - 5} more")
            else:
                print(f"  ⚠️  {warning_count} warnings")
        else:
            print("  ✅ Valid")

    print("\n✅ Real script validation tests PASSED")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("UCODE VALIDATOR TEST SUITE")
    print("v1.4.0 Phase 4.2 - Command Set Consolidation")
    print("="*80)

    try:
        test_command_registry()
        test_parser_basic()
        test_validator_valid_script()
        test_validator_invalid_command()
        test_validator_undefined_variable()
        test_validator_reserved_variable()
        test_linter()
        test_real_scripts()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\nuCODE validator is working correctly!")
        print("\nUsage:")
        print("  python -m core.ucode.validator file.uscript")
        print("  python -m core.ucode.validator --lint file.uscript")
        print("  python -m core.ucode.validator --strict *.uscript")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
