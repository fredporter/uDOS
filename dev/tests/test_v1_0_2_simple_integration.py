#!/usr/bin/env python3
"""
uDOS v1.0.2 - Simple Integration Test

Test v1.0.2 features with session log monitoring
and virtual environment validation.

Version: 1.0.2
Author: Fred Porter
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime


def check_venv():
    """Verify virtual environment is active."""
    if 'VIRTUAL_ENV' not in os.environ:
        print("⚠️  Virtual environment not detected!")
        print("💡 Run: source .venv/bin/activate")
        return False

    venv_path = os.environ['VIRTUAL_ENV']
    print(f"✅ Virtual environment active: {venv_path}")
    return True


def check_session_logs():
    """Check for recent session logs and errors."""
    log_dir = Path("memory/logs")
    if not log_dir.exists():
        print("📋 No session logs directory found")
        return {"status": "no_logs"}

    recent_files = []
    current_time = time.time()

    for log_file in log_dir.glob("**/*.log"):
        if log_file.stat().st_mtime > current_time - 300:  # Last 5 minutes
            recent_files.append(log_file)

    print(f"📋 Found {len(recent_files)} recent log files")

    errors = []
    warnings = []

    for log_file in recent_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed']):
                        errors.append(line[:100])
                    elif any(keyword in line.lower() for keyword in ['warning', 'warn']):
                        warnings.append(line[:100])
        except Exception as e:
            errors.append(f"Log read error: {e}")

    return {
        "status": "checked",
        "files": len(recent_files),
        "errors": errors[:5],  # Limit to first 5
        "warnings": warnings[:5]
    }


def test_file_operations():
    """Test FILE operations by checking command definitions."""
    commands_file = Path("data/system/commands.json")

    if not commands_file.exists():
        print("❌ Commands configuration not found")
        return False

    try:
        with open(commands_file, 'r') as f:
            commands = json.load(f)

        file_commands = ['NEW', 'DELETE', 'COPY', 'MOVE', 'RENAME', 'SHOW', 'EDIT', 'RUN']
        routing_issues = []

        print("🔍 Checking FILE command routing:")

        for cmd in file_commands:
            if cmd in commands:
                ucode_template = commands[cmd].get('UCODE_TEMPLATE', '')
                if ucode_template.startswith('[SYSTEM|'):
                    routing_issues.append(f"{cmd}: {ucode_template}")
                    print(f"  ❌ {cmd}: Routed to SYSTEM (should be FILE)")
                elif ucode_template.startswith('[FILE|'):
                    print(f"  ✅ {cmd}: Correctly routed to FILE")
                else:
                    print(f"  ⚠️  {cmd}: Unknown routing: {ucode_template}")
            else:
                print(f"  ❌ {cmd}: Command not found")

        if routing_issues:
            print(f"\n🚨 Found {len(routing_issues)} routing issues:")
            for issue in routing_issues:
                print(f"  - {issue}")
            return False

        print("\n✅ All FILE commands correctly routed")
        return True

    except Exception as e:
        print(f"❌ Error checking commands: {e}")
        return False


def test_enhanced_features():
    """Test that enhanced feature files exist."""
    print("\n🆕 Checking enhanced features:")

    # Check smart picker
    smart_picker = Path("core/utils/smart_picker.py")
    if smart_picker.exists():
        print("  ✅ Smart file picker exists")
        size = smart_picker.stat().st_size
        print(f"    📊 Size: {size} bytes")
    else:
        print("  ❌ Smart file picker missing")
        return False

    # Check enhanced file handler
    enhanced_handler = Path("core/commands/enhanced_file_handler.py")
    if enhanced_handler.exists():
        print("  ✅ Enhanced file handler exists")
        size = enhanced_handler.stat().st_size
        print(f"    📊 Size: {size} bytes")
    else:
        print("  ❌ Enhanced file handler missing")
        return False

    # Check test files
    standalone_test = Path("sandbox/tests/test_v1_0_2_standalone.py")
    if standalone_test.exists():
        print("  ✅ Standalone tests exist")
    else:
        print("  ❌ Standalone tests missing")
        return False

    return True


def test_workspace_structure():
    """Test workspace structure for file operations."""
    print("\n📁 Checking workspace structure:")

    required_dirs = ['sandbox', 'memory', 'data/system', 'core/commands', 'core/utils']
    missing_dirs = []

    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path}")
            missing_dirs.append(dir_path)

    if missing_dirs:
        print(f"\n🚨 Missing directories: {missing_dirs}")
        return False

    print("\n✅ Workspace structure complete")
    return True


def question_break():
    """Interactive question break for development review."""
    print("\n" + "=" * 80)
    print("🤔 DEVELOPMENT ROUND QUESTION BREAK")
    print("=" * 80)
    print("Review the test results above and consider:")
    print()
    print("1. ✅ Are FILE commands properly routed?")
    print("2. ✅ Do enhanced features exist and have reasonable size?")
    print("3. ✅ Is the workspace structure complete?")
    print("4. ✅ Are session logs being monitored?")
    print("5. ✅ Is the virtual environment active?")
    print()

    response = input("🔧 Do you want to proceed with integration? (Y/n): ").strip().lower()

    if response == 'n':
        print("\n📝 What changes would you like to make?")
        changes = input("Enter your changes (or press Enter to continue): ").strip()

        if changes:
            print(f"\n📋 Noted changes: {changes}")
            print("💡 Make your changes and run the test again.")
            return False, changes

    print("\n✅ Proceeding with integration...")
    return True, None


def main():
    """Run simple integration validation."""
    print("🚀 uDOS v1.0.2 SIMPLE INTEGRATION VALIDATION")
    print("=" * 80)

    # Check environment
    if not check_venv():
        return False

    print(f"\n📅 Test session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run validation tests
    tests_passed = 0
    total_tests = 4

    # 1. Test FILE command routing
    if test_file_operations():
        tests_passed += 1

    # 2. Test enhanced features
    if test_enhanced_features():
        tests_passed += 1

    # 3. Test workspace structure
    if test_workspace_structure():
        tests_passed += 1

    # 4. Check session logs
    log_check = check_session_logs()
    if log_check["status"] != "error":
        tests_passed += 1
        if log_check.get("errors"):
            print(f"⚠️  Found {len(log_check['errors'])} recent log errors")
        if log_check.get("warnings"):
            print(f"ℹ️  Found {len(log_check['warnings'])} recent log warnings")

    # Summary
    print("\n" + "=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    print(f"📈 Tests passed: {tests_passed}/{total_tests}")
    success_rate = (tests_passed / total_tests) * 100
    print(f"📊 Success rate: {success_rate:.1f}%")

    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")

        # Question break
        proceed, changes = question_break()

        if not proceed:
            print("\n🔄 Please make your changes and re-run the validation")
            return False

        print("\n✅ v1.0.2 FILE operations ready for integration!")

        # Save validation results
        results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': tests_passed,
            'total_tests': total_tests,
            'success_rate': success_rate,
            'log_check': log_check,
            'status': 'PASSED'
        }

        results_file = Path('sandbox/tests/v1_0_2_validation_results.json')
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Validation results saved to: {results_file}")
        return True
    else:
        print(f"\n⚠️  VALIDATION INCOMPLETE ({tests_passed}/{total_tests} passed)")
        print("🔧 Address issues before proceeding with integration")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
