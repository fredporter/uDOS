#!/usr/bin/env python3
"""
Sonic modular plugin verification script.

Tests that the external `uDOS-sonic` integration is properly provisioned.
"""

import sys
from pathlib import Path

from core.services.external_repo_service import ensure_sonic_python_paths


ensure_sonic_python_paths()


def test_imports():
    """Test that all plugin components can be imported."""
    print("=== Testing Plugin Imports ===\n")

    tests = []

    # Test 1: External Sonic service
    try:
        from installers.usb.service import SonicService
        print("✅ Sonic USB service loaded")
        tests.append(("service", True, None))
    except Exception as e:
        print(f"❌ Sonic USB service failed: {e}")
        tests.append(("service", False, str(e)))

    # Test 2: Verification
    try:
        from installers.usb.verify import verify_sonic_ready, verify_release_bundle
        print("✅ Sonic verification module loaded")
        tests.append(("verify", True, None))
    except Exception as e:
        print(f"❌ Sonic verification module failed: {e}")
        tests.append(("verify", False, str(e)))

    # Test 3: Planner
    try:
        from installers.usb.plan import write_plan
        print("✅ Sonic planner module loaded")
        tests.append(("plan", True, None))
    except Exception as e:
        print(f"❌ Sonic planner module failed: {e}")
        tests.append(("plan", False, str(e)))

    # Test 4: Loader
    try:
        from extensions.sonic_loader import (
            SonicPluginLoader, get_sonic_loader, load_sonic_plugin
        )
        print("✅ Plugin loader loaded")
        tests.append(("loader", True, None))
    except Exception as e:
        print(f"❌ Plugin loader failed: {e}")
        tests.append(("loader", False, str(e)))

    # Test 5: Wizard routes
    try:
        from wizard.routes.sonic_plugin_routes import create_sonic_plugin_routes
        print("✅ Wizard routes loaded")
        tests.append(("wizard_routes", True, None))
    except Exception as e:
        print(f"❌ Wizard routes failed: {e}")
        tests.append(("wizard_routes", False, str(e)))

    # Test 6: Wizard service
    try:
        from wizard.services.sonic_plugin_service import SonicPluginService
        print("✅ Wizard service loaded")
        tests.append(("wizard_service", True, None))
    except Exception as e:
        print(f"❌ Wizard service failed: {e}")
        tests.append(("wizard_service", False, str(e)))

    # Test 7: TUI handler
    try:
        from core.commands.sonic_plugin_handler import SonicPluginHandler
        print("✅ TUI handler loaded")
        tests.append(("tui_handler", True, None))
    except Exception as e:
        print(f"❌ TUI handler failed: {e}")
        tests.append(("tui_handler", False, str(e)))

    return tests


def test_plugin_loading():
    """Test dynamic plugin loading."""
    print("\n=== Testing Plugin Loading ===\n")

    try:
        from extensions.sonic_loader import load_sonic_plugin

        plugin = load_sonic_plugin()

        print("✅ Plugin loaded successfully")
        print(f"  - Schemas: {plugin['schemas']}")
        print(f"  - API: {plugin['api']}")
        print(f"  - Sync: {plugin['sync']}")
        print(f"  - Loader: {plugin['loader']}")

        return True
    except Exception as e:
        print(f"❌ Plugin loading failed: {e}")
        return False


def test_api_service():
    """Test API service instantiation."""
    print("\n=== Testing API Service ===\n")

    try:
        from installers.usb.service import SonicService

        api = SonicService()
        health = api.get_health()

        print("✅ API service instantiated")
        print(f"  Status: {health.get('status')}")
        print(f"  DB exists: {health.get('database_compiled')}")
        print(f"  Records: {health.get('record_count', 0)}")

        return True
    except Exception as e:
        print(f"❌ API service failed: {e}")
        return False


def test_sync_service():
    """Test sync service instantiation."""
    print("\n=== Testing Sync Service ===\n")

    try:
        from installers.usb.service import SonicService

        sync = SonicService()
        status = sync.get_db_status()

        print("✅ Sync service instantiated")
        print(f"  DB exists: {status.get('artifacts', {}).get('legacy_db_present')}")
        print(f"  DB path: {status.get('paths', {}).get('legacy_db')}")
        print(f"  Records: {status.get('summary', {}).get('device_count')}")

        return True
    except Exception as e:
        print(f"❌ Sync service failed: {e}")
        return False


def test_plugin_info():
    """Test plugin information retrieval."""
    print("\n=== Testing Plugin Info ===\n")

    try:
        from extensions.sonic_loader import get_sonic_loader

        loader = get_sonic_loader()
        info = loader.get_plugin_info()
        available = loader.is_available()

        print(f"✅ Plugin info retrieved")
        print(f"  Available: {available}")
        print(f"  Installed: {info.get('installed')}")
        print(f"  Name: {info.get('name')}")
        print(f"  Version: {info.get('version')}")
        print(f"  Path: {info.get('path')}")

        return available
    except Exception as e:
        print(f"❌ Plugin info failed: {e}")
        return False


def test_file_structure():
    """Test that all expected files exist."""
    print("\n=== Testing File Structure ===\n")

    repo_root = Path(__file__).resolve().parents[1]

    expected_files = [
        "../uDOS-sonic/installers/usb/service.py",
        "../uDOS-sonic/installers/usb/verify.py",
        "../uDOS-sonic/installers/usb/plan.py",
        "extensions/sonic_loader.py",
        "wizard/routes/sonic_plugin_routes.py",
        "wizard/services/sonic_plugin_service.py",
        "core/commands/sonic_handler.py",
        "docs/howto/SONIC-UHOME-EXTERNAL-INTEGRATION.md",
    ]

    all_exist = True
    for file_path in expected_files:
        full_path = repo_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False

    return all_exist


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("SONIC MODULAR PLUGIN VERIFICATION")
    print("=" * 60)

    results = {}

    # Test imports
    import_results = test_imports()
    results['imports'] = all(success for _, success, _ in import_results)

    # Test plugin loading
    results['loading'] = test_plugin_loading()

    # Test API service
    results['api'] = test_api_service()

    # Test sync service
    results['sync'] = test_sync_service()

    # Test plugin info
    results['info'] = test_plugin_info()

    # Test file structure
    results['files'] = test_file_structure()

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Plugin system ready")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
