#!/usr/bin/env python3
"""
uDOS v1.0.4 - Teletext Integration Test Suite

Comprehensive test suite for teletext web extension integration with
the uDOS mapping system.

Tests:
- Teletext renderer functionality
- MAP command integration
- Web extension server
- HTML/CSS generation
- Mosaic character rendering
- Interactive controls

Version: 1.0.4
"""

import sys
import time
import webbrowser
from pathlib import Path
import subprocess

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.commands.map_handler import MapCommandHandler
from core.services.teletext_renderer import TeletextMosaicRenderer, TeletextMapIntegration
from core.services.integrated_map_engine import IntegratedMapEngine
from extensions.web.teletext_extension import TeletextWebExtension


def test_teletext_renderer():
    """Test core teletext renderer functionality."""
    print("🖥️  Testing Teletext Renderer")
    print("-" * 30)

    renderer = TeletextMosaicRenderer()

    # Test mosaic data loading
    assert len(renderer.mosaic_data) == 64, "Should have 64 mosaic characters"
    print("✅ Mosaic data loaded")

    # Test map conversion
    test_map = [
        "~..~..~..~..~",
        ".     ◉     .",
        "~           ~",
        ".           .",
        "~..~..~..~..~"
    ]

    html_output = renderer.generate_map_html(test_map, "Test Map", 15, 5)
    assert "teletext" in html_output, "Should contain teletext CSS class"
    assert "◉" in html_output or "&#x" in html_output, "Should contain position marker"
    print("✅ HTML generation working")

    return True


def test_map_integration():
    """Test integration with MAP command system."""
    print("\n🗺️  Testing MAP Command Integration")
    print("-" * 35)

    integration = TeletextMapIntegration()
    map_engine = IntegratedMapEngine()

    # Test teletext map generation
    try:
        html_content = integration.render_map_as_teletext(map_engine, "JN196", 30, 15)
        assert "teletext" in html_content, "Should contain teletext markup"
        assert "Melbourne" in html_content or "JN196" in html_content, "Should contain location info"
        print("✅ Map engine integration working")
    except Exception as e:
        print(f"⚠️  Map integration test failed: {e}")
        return False

    # Test file saving
    try:
        filepath = integration.save_teletext_map(html_content, "test_integration.html")
        assert Path(filepath).exists(), "File should be saved"
        print(f"✅ File saving working: {filepath}")
    except Exception as e:
        print(f"⚠️  File saving test failed: {e}")
        return False

    return True


def test_map_commands():
    """Test MAP TELETEXT and MAP WEB commands."""
    print("\n🎮 Testing MAP Commands")
    print("-" * 23)

    handler = MapCommandHandler()

    # Test MAP TELETEXT
    try:
        result = handler.handle("TELETEXT", "25 12", None)
        assert "Teletext Map Generated" in result, "Should confirm generation"
        assert "File saved:" in result, "Should show file path"
        print("✅ MAP TELETEXT command working")
    except Exception as e:
        print(f"⚠️  MAP TELETEXT test failed: {e}")
        return False

    # Test MAP WEB
    try:
        result = handler.handle("WEB", "", None)
        # Note: This might fail if no browser is available, but should not error
        print("✅ MAP WEB command executed")
    except Exception as e:
        print(f"⚠️  MAP WEB test failed: {e}")
        return False

    return True


def test_web_extension():
    """Test teletext web extension."""
    print("\n🌐 Testing Web Extension")
    print("-" * 24)

    try:
        extension = TeletextWebExtension(port=8081)  # Use different port

        # Test web file generation
        extension.setup_web_files()

        # Check if files were created
        web_root = extension.web_root
        required_files = ["index.html", "teletext-web.css", "teletext-api.js"]

        for filename in required_files:
            filepath = web_root / filename
            if filepath.exists():
                print(f"✅ {filename} created")
            else:
                print(f"❌ {filename} missing")
                return False

        print("✅ Web extension files generated")
        return True

    except Exception as e:
        print(f"⚠️  Web extension test failed: {e}")
        return False


def test_complete_workflow():
    """Test complete teletext workflow."""
    print("\n🔄 Testing Complete Workflow")
    print("-" * 29)

    try:
        # Step 1: Generate teletext map
        handler = MapCommandHandler()
        result = handler.handle("TELETEXT", "40 20", None)
        print("✅ Step 1: Teletext map generated")

        # Step 2: Check output directory
        output_dir = Path("output/teletext")
        html_files = list(output_dir.glob("*.html"))
        assert len(html_files) > 0, "Should have HTML files"
        print(f"✅ Step 2: Found {len(html_files)} HTML files")

        # Step 3: Test web interface files
        extension = TeletextWebExtension(port=8082)
        extension.setup_web_files()

        web_files = list(extension.web_root.glob("*"))
        assert len(web_files) >= 3, "Should have web interface files"
        print(f"✅ Step 3: Web interface has {len(web_files)} files")

        return True

    except Exception as e:
        print(f"⚠️  Complete workflow test failed: {e}")
        return False


def generate_demo_maps():
    """Generate demo teletext maps for testing."""
    print("\n🎨 Generating Demo Maps")
    print("-" * 22)

    handler = MapCommandHandler()

    # Demo configurations
    demos = [
        ("Melbourne Standard", "MEL", "40 20"),
        ("London Compact", "LON", "30 15"),
        ("Tokyo Large", "TYO", "60 30"),
        ("Sydney Mobile", "SYD", "25 12")
    ]

    generated_files = []

    for name, location, size in demos:
        try:
            # Update location if possible
            # (In real implementation, this would update user config)

            result = handler.handle("TELETEXT", size, None)
            if "File saved:" in result:
                # Extract filename from result
                import re
                match = re.search(r'File saved: (.+\.html)', result)
                if match:
                    filepath = match.group(1)
                    generated_files.append((name, filepath))
                    print(f"✅ {name}: {Path(filepath).name}")

        except Exception as e:
            print(f"⚠️  {name} failed: {e}")

    print(f"\n📁 Generated {len(generated_files)} demo maps")
    for name, filepath in generated_files:
        print(f"   {name}: {filepath}")

    return generated_files


def main():
    """Run complete teletext integration test suite."""
    print("🖥️ ✨ uDOS v1.0.4 - TELETEXT INTEGRATION TEST SUITE ✨ 🖥️")
    print("=" * 65)

    tests = [
        ("Teletext Renderer", test_teletext_renderer),
        ("MAP Integration", test_map_integration),
        ("MAP Commands", test_map_commands),
        ("Web Extension", test_web_extension),
        ("Complete Workflow", test_complete_workflow)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Generate demo maps
    demo_files = generate_demo_maps()

    # Summary
    print(f"\n🏆 TEST SUMMARY")
    print("=" * 15)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\nResults: {passed}/{total} tests passed")
    print(f"Demo maps: {len(demo_files)} generated")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Teletext integration ready!")
        print("🌐 Try: MAP TELETEXT, MAP WEB, or start web extension")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check implementation.")

    # Show usage examples
    print(f"\n📖 USAGE EXAMPLES:")
    print("=" * 17)
    print("MAP TELETEXT 40 20    # Generate 40×20 teletext map")
    print("MAP WEB               # Open latest map in browser")
    print("MAP WEB SERVER        # Start HTTP server")
    print("python3 extensions/web/teletext_extension.py  # Start web interface")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
