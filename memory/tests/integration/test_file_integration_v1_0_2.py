#!/usr/bin/env python3
"""
uDOS v1.0.2 File Operations Integration Test

Simple integration test that works with actual uDOS commands
Tests FILE operations by simulating command execution.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path


def run_udos_command(command_input):
    """Run a uDOS command and capture output."""
    try:
        # Use echo to pipe command to uDOS
        process = subprocess.run(
            f'echo "{command_input}" | python3 uDOS.py',
            shell=True,
            capture_output=True,
            text=True,
            cwd='/Users/fredbook/Code/uDOS'
        )
        return process.stdout, process.stderr, process.returncode
    except Exception as e:
        return "", str(e), 1


def test_help_file_commands():
    """Test that HELP shows FILE commands."""
    print("🧪 Testing HELP for FILE commands...")

    stdout, stderr, returncode = run_udos_command("HELP")

    required_commands = ['NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME', 'SHOW', 'EDIT', 'RUN']
    found_commands = []

    for cmd in required_commands:
        if cmd in stdout:
            found_commands.append(cmd)

    print(f"   Found {len(found_commands)}/{len(required_commands)} FILE commands")

    if len(found_commands) == len(required_commands):
        print("✅ All FILE commands are available in HELP")
        return True
    else:
        missing = set(required_commands) - set(found_commands)
        print(f"❌ Missing commands: {missing}")
        return False


def test_workspace_listing():
    """Test WORKSPACE command."""
    print("🧪 Testing WORKSPACE command...")

    stdout, stderr, returncode = run_udos_command("WORKSPACE")

    # Check for workspace-related content
    workspace_indicators = ['sandbox', 'memory', 'WORKSPACE']
    found = any(indicator in stdout for indicator in workspace_indicators)

    if found:
        print("✅ WORKSPACE command working")
        return True
    else:
        print("❌ WORKSPACE command not working properly")
        print(f"Output: {stdout[:200]}...")
        return False


def test_file_security():
    """Test file security restrictions."""
    print("🧪 Testing file security...")

    # Try to show a restricted file
    stdout, stderr, returncode = run_udos_command("SHOW /etc/passwd")

    if "Access denied" in stdout or "not found" in stdout.lower():
        print("✅ File security restrictions working")
        return True
    else:
        print("❌ File security may not be working")
        print(f"Output: {stdout[:200]}...")
        return False


def check_file_structure():
    """Check that file-related directories exist."""
    print("🧪 Checking file structure...")

    base_path = Path('/Users/fredbook/Code/uDOS')
    required_dirs = ['sandbox', 'memory', 'data', 'core/commands']

    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if not dir_path.exists():
            missing_dirs.append(dir_name)

    if not missing_dirs:
        print("✅ All required directories exist")
        return True
    else:
        print(f"❌ Missing directories: {missing_dirs}")
        return False


def check_file_handler():
    """Check that file handler exists."""
    print("🧪 Checking file handler...")

    handler_path = Path('/Users/fredbook/Code/uDOS/core/commands/file_handler.py')

    if handler_path.exists():
        print("✅ File handler exists")

        # Check for key methods
        content = handler_path.read_text()
        methods = ['_handle_new', '_handle_delete', '_handle_copy', '_handle_move',
                  '_handle_rename', '_handle_show', '_handle_edit', '_handle_run']

        found_methods = [method for method in methods if method in content]

        print(f"   Found {len(found_methods)}/{len(methods)} handler methods")

        if len(found_methods) == len(methods):
            print("✅ All FILE handler methods present")
            return True
        else:
            missing = set(methods) - set(found_methods)
            print(f"❌ Missing handler methods: {missing}")
            return False
    else:
        print("❌ File handler not found")
        return False


def check_workspace_manager():
    """Check workspace manager implementation."""
    print("🧪 Checking workspace manager...")

    workspace_path = Path('/Users/fredbook/Code/uDOS/core/uDOS_files.py')

    if workspace_path.exists():
        content = workspace_path.read_text()

        # Check for key workspace features
        features = ['WorkspaceManager', 'WORKSPACES', 'TEMPLATES', 'list_files', 'new_file']
        found_features = [feature for feature in features if feature in content]

        print(f"   Found {len(found_features)}/{len(features)} workspace features")

        if len(found_features) == len(features):
            print("✅ Workspace manager fully implemented")
            return True
        else:
            missing = set(features) - set(found_features)
            print(f"❌ Missing workspace features: {missing}")
            return False
    else:
        print("❌ Workspace manager not found")
        return False


def main():
    """Run all integration tests."""
    print("=" * 80)
    print("🔍 uDOS v1.0.2 FILE OPERATIONS INTEGRATION TEST")
    print("=" * 80)

    tests = [
        ("File Structure", check_file_structure),
        ("File Handler", check_file_handler),
        ("Workspace Manager", check_workspace_manager),
        ("HELP Command", test_help_file_commands),
        ("WORKSPACE Command", test_workspace_listing),
        ("File Security", test_file_security)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Running: {test_name}")
        print(f"{'='*40}")

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} - ERROR: {e}")

    # Summary
    print("\n" + "=" * 80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")

    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ FILE operations infrastructure is ready")
        print("✅ Ready to proceed with v1.0.2 DEVELOPMENT phase")
    else:
        print(f"\n⚠️  {failed} tests failed.")
        print("🔧 Review the issues above before proceeding")

    print("\n" + "=" * 80)
    print("📋 NEXT STEPS FOR v1.0.2 DEVELOPMENT:")
    print("=" * 80)
    print("1. ✅ Smart file picker with fuzzy search")
    print("2. ✅ Batch operations (delete multiple, copy folders)")
    print("3. ✅ File preview before opening")
    print("4. ✅ Recently used files list")
    print("5. ✅ Workspace bookmarks")
    print("6. ✅ Enhanced templates and file management")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
