#!/usr/bin/env python3
"""
Test REFRESH Command System
v1.4.0 Phase 3.4 - Content Refresh System

Tests quality checking, version tracking, and content refresh functionality.
"""

import sys
import tempfile
from pathlib import Path

# Add core commands to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.commands.refresh_command import (
    ContentVersion, QualityChecker, RefreshCommand
)


def create_test_guide(filepath: Path, quality: str = "good"):
    """Create a test guide with specified quality level."""
    if quality == "good":
        content = """# Water Purification Guide

## Description
Comprehensive guide to water purification methods.

## Steps
1. Collect water from cleanest available source
2. Pre-filter to remove large debris
3. Purify using one of these methods:
   - Boiling (1 minute at sea level)
   - Chemical treatment (tablets or bleach)
   - Filtration (multi-barrier system)

## Safety
⚠️ Always purify water before drinking in survival situations.

## Related Topics
- [[water/collection-methods]]
- [[water/storage-containers]]

**OK Assist Generated:** ✅
**Version:** 1.0.0
"""
    elif quality == "poor":
        content = """# Water

Some info about water purification.
"""
    else:  # minimal
        content = """# Water Purification

Brief guide.

OK Assist Generated: ✅
"""

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)


def create_test_svg(filepath: Path, size: str = "good"):
    """Create a test SVG diagram."""
    if size == "good":
        content = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" width="800" height="600">
  <title>Water Filter Diagram</title>
  <rect x="100" y="100" width="200" height="300" fill="none" stroke="#000" stroke-width="2"/>
  <text x="200" y="250" text-anchor="middle" font-family="monospace" font-size="14">Filter</text>
  <path d="M 200 100 L 200 50" stroke="#00F" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="220" y="70" font-family="monospace" font-size="12">Input</text>
</svg>
"""
    else:  # large
        # Create a very large SVG (simulate >75KB)
        paths = "\n".join([f'<path d="M {i} {i} L {i+10} {i+10}"/>' for i in range(1000)])
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
{paths}
</svg>
"""

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write(content)


def test_version_tracking():
    """Test version tracking system."""
    print("\n" + "="*80)
    print("TEST: Version Tracking")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_guide.md"
        create_test_guide(test_file, "good")

        # Initialize version
        version = ContentVersion(test_file)
        print(f"✅ Initial version: {version.get_version()}")
        assert version.get_version() == "1.0.0"

        # Bump patch
        new_version = version.bump_version("patch")
        print(f"✅ Patch bump: {new_version}")
        assert new_version == "1.0.1"

        # Bump minor
        new_version = version.bump_version("minor")
        print(f"✅ Minor bump: {new_version}")
        assert new_version == "1.1.0"

        # Bump major
        new_version = version.bump_version("major")
        print(f"✅ Major bump: {new_version}")
        assert new_version == "2.0.0"

        # Check history
        print(f"✅ History entries: {len(version.metadata['history'])}")
        assert len(version.metadata['history']) == 3

        # Test quality score
        version.set_quality_score(0.85)
        assert version.metadata['quality_score'] == 0.85
        print(f"✅ Quality score set: {version.metadata['quality_score']}")

        print("\n✅ Version tracking tests PASSED")


def test_quality_checker():
    """Test quality checking system."""
    print("\n" + "="*80)
    print("TEST: Quality Checker")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Test good guide
        good_guide = tmppath / "good_guide.md"
        create_test_guide(good_guide, "good")
        score, issues = QualityChecker.check_guide(good_guide)
        print(f"\nGood Guide:")
        print(f"  Score: {score:.2f}/1.0")
        print(f"  Issues: {len(issues)}")
        for issue in issues:
            print(f"    - {issue}")
        assert score >= 0.8, f"Good guide should score >= 0.8, got {score}"

        # Test poor guide
        poor_guide = tmppath / "poor_guide.md"
        create_test_guide(poor_guide, "poor")
        score, issues = QualityChecker.check_guide(poor_guide)
        print(f"\nPoor Guide:")
        print(f"  Score: {score:.2f}/1.0")
        print(f"  Issues: {len(issues)}")
        for issue in issues:
            print(f"    - {issue}")
        assert score < 0.8, f"Poor guide should score < 0.8, got {score}"

        # Test good SVG
        good_svg = tmppath / "good_diagram.svg"
        create_test_svg(good_svg, "good")
        score, issues = QualityChecker.check_diagram(good_svg)
        print(f"\nGood SVG:")
        print(f"  Score: {score:.2f}/1.0")
        print(f"  Issues: {len(issues)}")
        assert score >= 0.8, f"Good SVG should score >= 0.8, got {score}"

        # Test large SVG
        large_svg = tmppath / "large_diagram.svg"
        create_test_svg(large_svg, "large")
        score, issues = QualityChecker.check_diagram(large_svg)
        print(f"\nLarge SVG:")
        print(f"  Score: {score:.2f}/1.0")
        print(f"  Issues: {len(issues)}")
        for issue in issues:
            print(f"    - {issue}")
        assert score < 1.0, f"Large SVG should have quality issues"

        print("\n✅ Quality checker tests PASSED")


def test_refresh_command():
    """Test REFRESH command functionality."""
    print("\n" + "="*80)
    print("TEST: REFRESH Command")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create test workspace structure
        knowledge = tmppath / "knowledge"
        water_cat = knowledge / "water"
        water_cat.mkdir(parents=True)

        diagrams = knowledge / "diagrams" / "water"
        diagrams.mkdir(parents=True)

        # Create test files
        guide1 = water_cat / "purification.md"
        guide2 = water_cat / "collection.md"
        diagram1 = diagrams / "filter.svg"

        create_test_guide(guide1, "good")
        create_test_guide(guide2, "poor")
        create_test_svg(diagram1, "good")

        # Initialize refresh command
        refresh = RefreshCommand(tmppath)

        # Test single file refresh (check only)
        print("\n1. Testing check-only mode:")
        result = refresh.refresh_file(guide1, check_only=True)
        print(f"   File: {result['file']}")
        print(f"   Action: {result['action']}")
        print(f"   Quality: {result['quality_score']:.2f}")
        assert result['action'] == "check"
        assert result['success'] is True

        # Test single file refresh (good quality - should skip)
        print("\n2. Testing good quality file (should skip):")
        result = refresh.refresh_file(guide1)
        print(f"   File: {result['file']}")
        print(f"   Action: {result['action']}")
        print(f"   Quality: {result['quality_score']:.2f}")
        assert result['action'] == "skip"

        # Test single file refresh (poor quality - should update)
        print("\n3. Testing poor quality file (should update):")
        result = refresh.refresh_file(guide2)
        print(f"   File: {result['file']}")
        print(f"   Action: {result['action']}")
        print(f"   Old version: {result['old_version']}")
        print(f"   New version: {result['new_version']}")
        print(f"   Quality: {result['quality_score']:.2f}")
        assert result['action'] in ["major_update", "minor_update"]
        assert result['new_version'] != result['old_version']

        # Test force refresh
        print("\n4. Testing force refresh:")
        result = refresh.refresh_file(guide1, force=True)
        print(f"   File: {result['file']}")
        print(f"   Action: {result['action']}")
        assert result['action'] in ["refresh", "minor_update", "patch"]

        # Test category refresh
        print("\n5. Testing category refresh:")
        results = refresh.refresh_category("water")
        print(f"   Files processed: {len(results)}")
        for r in results:
            print(f"     - {r['file']}: {r['action']}")
        assert len(results) == 3  # 2 guides + 1 diagram

        print("\n✅ REFRESH command tests PASSED")


def test_report_generation():
    """Test report generation."""
    print("\n" + "="*80)
    print("TEST: Report Generation")
    print("="*80)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create minimal test structure
        knowledge = tmppath / "knowledge" / "water"
        knowledge.mkdir(parents=True)

        guide = knowledge / "test.md"
        create_test_guide(guide, "good")

        # Initialize and run refresh
        refresh = RefreshCommand(tmppath)
        summary = refresh.refresh_all(check_only=True)

        # Generate report
        report = refresh.generate_report(summary)
        print("\n" + report)

        assert "REFRESH COMMAND REPORT" in report
        assert "Total Files Processed:" in report
        assert "Average Quality Score:" in report

        print("\n✅ Report generation tests PASSED")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("REFRESH COMMAND TEST SUITE")
    print("v1.4.0 Phase 3.4 - Content Refresh System")
    print("="*80)

    try:
        test_version_tracking()
        test_quality_checker()
        test_refresh_command()
        test_report_generation()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\nREFRESH command system is working correctly!")
        print("\nUsage examples:")
        print("  python -m core.commands.refresh_command --check all")
        print("  python -m core.commands.refresh_command water")
        print("  python -m core.commands.refresh_command --force knowledge/water/purification.md")

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
