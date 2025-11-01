#!/usr/bin/env python3
"""
uDOS v1.0.2 - Comprehensive Integration Test Framework

Enhanced testing with:
- Session log checking and analysis
- Command option and fallback testing
- Integration verification
- Virtual environment validation
- Question break for dev round review

Version: 1.0.2
Author: Fred Porter
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime


class SessionLogChecker:
    """Monitor and analyze uDOS session logs."""

    def __init__(self, log_dir="memory/logs"):
        self.log_dir = Path(log_dir)
        self.session_logs = []
        self.errors = []
        self.warnings = []

    def capture_session_start(self):
        """Capture timestamp for session monitoring."""
        self.start_time = time.time()

    def analyze_logs(self):
        """Analyze recent session logs for errors and patterns."""
        if not self.log_dir.exists():
            return {"status": "no_logs", "message": "No log directory found"}

        # Find recent log files
        log_files = list(self.log_dir.glob("**/*.log"))
        recent_logs = [f for f in log_files if f.stat().st_mtime > self.start_time - 300]  # Last 5 minutes

        analysis = {
            "files_checked": len(recent_logs),
            "errors": [],
            "warnings": [],
            "commands_executed": [],
            "performance_issues": [],
            "memory_usage": []
        }

        for log_file in recent_logs:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                for line in lines:
                    line = line.strip()

                    # Check for errors
                    if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', 'traceback']):
                        analysis["errors"].append(line)

                    # Check for warnings
                    elif any(keyword in line.lower() for keyword in ['warning', 'warn', 'deprecated']):
                        analysis["warnings"].append(line)

                    # Track command execution
                    elif 'uDOS>' in line or 'INPUT' in line:
                        analysis["commands_executed"].append(line)

                    # Performance issues
                    elif any(keyword in line.lower() for keyword in ['slow', 'timeout', 'memory']):
                        analysis["performance_issues"].append(line)

            except Exception as e:
                analysis["errors"].append(f"Log read error: {e}")

        return analysis


class CommandTester:
    """Test commands with various options and fallbacks."""

    def __init__(self):
        self.test_results = []
        self.log_checker = SessionLogChecker()

    def check_venv(self):
        """Verify virtual environment is active."""
        if 'VIRTUAL_ENV' not in os.environ:
            print("⚠️  Virtual environment not detected!")
            print("💡 Run: source .venv/bin/activate")
            return False

        venv_path = os.environ['VIRTUAL_ENV']
        print(f"✅ Virtual environment active: {venv_path}")
        return True

    def run_udos_command(self, command, timeout=30):
        """Run a uDOS command and capture comprehensive output."""
        self.log_checker.capture_session_start()

        try:
            # Create a simple script to handle the timeout and command execution
            script_content = f'''#!/bin/bash
echo "{command}" | python3 uDOS.py
'''

            # Write temporary script
            script_path = Path("temp_test_script.sh")
            with open(script_path, 'w') as f:
                f.write(script_content)

            # Make executable and run
            os.chmod(script_path, 0o755)

            process = subprocess.run(
                ['./temp_test_script.sh'],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                timeout=timeout
            )

            # Clean up
            if script_path.exists():
                script_path.unlink()

            # Analyze logs after command execution
            time.sleep(1)  # Allow logs to be written
            log_analysis = self.log_checker.analyze_logs()

            return {
                'command': command,
                'stdout': process.stdout,
                'stderr': process.stderr,
                'returncode': process.returncode,
                'log_analysis': log_analysis,
                'timestamp': datetime.now().isoformat()
            }

        except subprocess.TimeoutExpired:
            return {
                'command': command,
                'error': 'Command timed out',
                'returncode': 124,
                'log_analysis': {'errors': ['Command timed out']},
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'command': command,
                'error': str(e),
                'returncode': -1,
                'log_analysis': {'errors': [str(e)]},
                'timestamp': datetime.now().isoformat()
            }

    def test_command_options(self, base_command, options_list):
        """Test a command with various option combinations."""
        results = []

        for options in options_list:
            full_command = f"{base_command} {options}".strip()
            print(f"  Testing: {full_command}")

            result = self.run_udos_command(full_command)
            results.append(result)

            # Brief analysis
            if result['returncode'] == 0:
                print(f"    ✅ Success")
            else:
                print(f"    ❌ Failed (code: {result.get('returncode', 'unknown')})")
                if result.get('stderr'):
                    print(f"    Error: {result['stderr'][:100]}...")

            # Check logs for issues
            log_errors = result.get('log_analysis', {}).get('errors', [])
            if log_errors:
                print(f"    ⚠️  Log errors: {len(log_errors)}")

        return results

    def test_fallback_scenarios(self, command, scenarios):
        """Test command fallback behaviors."""
        results = []

        for scenario_name, test_command in scenarios.items():
            print(f"  Testing fallback: {scenario_name}")
            result = self.run_udos_command(test_command)
            result['scenario'] = scenario_name
            results.append(result)

            # Check if fallback worked properly
            output = result.get('stdout', '')
            if any(indicator in output.lower() for indicator in ['error', 'not found', 'invalid']):
                if any(fallback in output.lower() for fallback in ['fallback', 'alternative', 'try']):
                    print(f"    ✅ Fallback triggered correctly")
                else:
                    print(f"    ⚠️  Error without clear fallback")
            else:
                print(f"    ✅ Command succeeded")

        return results


class IntegrationValidator:
    """Validate v1.0.2 integration with existing uDOS system."""

    def __init__(self):
        self.tester = CommandTester()

    def validate_file_command_routing(self):
        """Test that FILE commands are properly routed."""
        print("🔀 Testing FILE Command Routing")
        print("=" * 40)

        file_commands = {
            'NEW': ['NEW', 'NEW test.md', 'NEW --help'],
            'SHOW': ['SHOW', 'SHOW README.MD', 'SHOW --web README.MD'],
            'EDIT': ['EDIT', 'EDIT test.txt', 'EDIT --cli test.txt'],
            'COPY': ['COPY', 'COPY file1.txt file2.txt'],
            'MOVE': ['MOVE', 'MOVE file1.txt memory'],
            'RENAME': ['RENAME', 'RENAME old.txt new.txt'],
            'DELETE': ['DELETE', 'DELETE temp.txt'],
            'RUN': ['RUN', 'RUN script.uscript']
        }

        all_results = {}

        for command, options in file_commands.items():
            print(f"\n📂 Testing {command} command:")
            results = self.tester.test_command_options(command, options)
            all_results[command] = results

            # Check if command is recognized (not showing "unknown command")
            for result in results:
                output = result.get('stdout', '')
                if 'unknown command' in output.lower() or 'error_unknown' in output.lower():
                    print(f"    ❌ Command not recognized: {result['command']}")
                else:
                    print(f"    ✅ Command recognized: {result['command']}")

        return all_results

    def validate_enhanced_features(self):
        """Test v1.0.2 enhanced features."""
        print("\n🆕 Testing Enhanced Features")
        print("=" * 40)

        enhanced_commands = {
            'SEARCH': ['SEARCH test', 'SEARCH test sandbox', 'SEARCH'],
            'RECENT': ['RECENT', 'RECENT clear'],
            'BOOKMARK': ['BOOKMARK', 'BOOKMARK add test file.txt'],
            'BATCH': ['BATCH list', 'BATCH list *.txt sandbox'],
            'PREVIEW': ['PREVIEW file.txt', 'PREVIEW']
        }

        enhanced_results = {}

        for command, options in enhanced_commands.items():
            print(f"\n🔍 Testing {command} command:")
            results = self.tester.test_command_options(command, options)
            enhanced_results[command] = results

        return enhanced_results

    def test_workspace_operations(self):
        """Test workspace-related operations."""
        print("\n📁 Testing Workspace Operations")
        print("=" * 40)

        workspace_tests = {
            'workspace_listing': 'WORKSPACE',
            'workspace_status': 'WORKSPACE STATUS',
            'sandbox_file_ops': 'SHOW sandbox/',
            'memory_file_ops': 'SHOW memory/',
            'cross_workspace_copy': 'COPY test.txt memory'
        }

        return self.tester.test_fallback_scenarios('WORKSPACE', workspace_tests)

    def test_error_handling(self):
        """Test error handling and fallbacks."""
        print("\n⚠️  Testing Error Handling")
        print("=" * 40)

        error_scenarios = {
            'nonexistent_file': 'SHOW nonexistent.txt',
            'invalid_workspace': 'SHOW invalid_workspace/',
            'malformed_command': 'INVALID_COMMAND',
            'empty_command': '',
            'restricted_access': 'SHOW /etc/passwd',
            'missing_parameters': 'COPY',
            'invalid_options': 'SHOW --invalid-flag'
        }

        return self.tester.test_fallback_scenarios('ERROR', error_scenarios)


def create_session_summary(test_results):
    """Create a comprehensive session summary."""
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_commands_tested': 0,
        'successful_commands': 0,
        'failed_commands': 0,
        'log_errors': [],
        'log_warnings': [],
        'performance_issues': [],
        'recommendations': []
    }

    # Analyze all test results
    for category, results in test_results.items():
        if isinstance(results, list):
            for result in results:
                summary['total_commands_tested'] += 1

                if result.get('returncode') == 0:
                    summary['successful_commands'] += 1
                else:
                    summary['failed_commands'] += 1

                # Collect log analysis
                log_analysis = result.get('log_analysis', {})
                summary['log_errors'].extend(log_analysis.get('errors', []))
                summary['log_warnings'].extend(log_analysis.get('warnings', []))
                summary['performance_issues'].extend(log_analysis.get('performance_issues', []))

    # Generate recommendations
    if summary['failed_commands'] > 0:
        summary['recommendations'].append("Review failed commands for error handling improvements")

    if summary['log_errors']:
        summary['recommendations'].append("Address log errors before production")

    if summary['performance_issues']:
        summary['recommendations'].append("Investigate performance issues")

    success_rate = (summary['successful_commands'] / summary['total_commands_tested'] * 100) if summary['total_commands_tested'] > 0 else 0
    summary['success_rate'] = round(success_rate, 2)

    return summary


def question_break():
    """Interactive question break for dev round review."""
    print("\n" + "=" * 80)
    print("🤔 DEVELOPMENT ROUND QUESTION BREAK")
    print("=" * 80)
    print("Review the test results above and consider the following questions:")
    print()
    print("1. Are all FILE commands working as expected?")
    print("2. Do the enhanced features (SEARCH, RECENT, BOOKMARK, etc.) work properly?")
    print("3. Are error messages clear and helpful?")
    print("4. Is the performance acceptable for all operations?")
    print("5. Are there any security concerns with file access?")
    print("6. Do the fallback mechanisms work correctly?")
    print()

    response = input("🔧 Do you want to make any changes before final testing? (y/N): ").strip().lower()

    if response == 'y':
        print("\n📝 What changes would you like to make?")
        changes = input("Enter your changes (or press Enter to continue): ").strip()

        if changes:
            print(f"\n📋 Noted changes: {changes}")
            print("💡 Make your changes and run the test again.")
            return True, changes

    print("\n✅ Proceeding with final integration...")
    return False, None


def main():
    """Run comprehensive v1.0.2 integration tests."""
    print("🚀 uDOS v1.0.2 COMPREHENSIVE INTEGRATION TESTS")
    print("=" * 80)

    # Check environment
    tester = CommandTester()
    if not tester.check_venv():
        print("❌ Please activate virtual environment first")
        return False

    validator = IntegrationValidator()

    print(f"\n📅 Test session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run comprehensive tests
    test_results = {}

    try:
        # 1. Validate FILE command routing
        test_results['file_routing'] = validator.validate_file_command_routing()

        # 2. Test enhanced features
        test_results['enhanced_features'] = validator.validate_enhanced_features()

        # 3. Test workspace operations
        test_results['workspace_ops'] = validator.test_workspace_operations()

        # 4. Test error handling
        test_results['error_handling'] = validator.test_error_handling()

        # 5. Create session summary
        summary = create_session_summary(test_results)

        # Display summary
        print("\n" + "=" * 80)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 80)
        print(f"📈 Commands tested: {summary['total_commands_tested']}")
        print(f"✅ Successful: {summary['successful_commands']}")
        print(f"❌ Failed: {summary['failed_commands']}")
        print(f"📊 Success rate: {summary['success_rate']}%")

        if summary['log_errors']:
            print(f"\n⚠️  Log errors: {len(summary['log_errors'])}")
            for error in summary['log_errors'][:5]:  # Show first 5
                print(f"  - {error[:100]}...")

        if summary['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"  - {rec}")

        # Question break
        needs_changes, changes = question_break()

        if needs_changes:
            print("\n🔄 Please make your changes and re-run the test")
            return False

        # Save detailed results
        results_file = Path('sandbox/tests/v1_0_2_integration_results.json')
        with open(results_file, 'w') as f:
            json.dump({
                'summary': summary,
                'detailed_results': test_results,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2, default=str)

        print(f"\n💾 Detailed results saved to: {results_file}")

        # Final assessment
        if summary['success_rate'] >= 80 and not summary['log_errors']:
            print("\n🎉 INTEGRATION TESTS PASSED!")
            print("✅ v1.0.2 FILE operations ready for production")
            return True
        else:
            print("\n⚠️  INTEGRATION TESTS NEED REVIEW")
            print("🔧 Address issues before proceeding")
            return False

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
