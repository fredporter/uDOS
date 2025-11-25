#!/usr/bin/env python3
"""
v1.0.26 Test Coverage Analysis

Analyzes current test coverage and identifies gaps.

Usage:
    python3 memory/tests/analyze_coverage_v1_0_26.py
"""

import os
import re
from pathlib import Path
from collections import defaultdict


class CoverageAnalyzer:
    """Analyze test coverage across uDOS"""

    def __init__(self):
        self.test_dir = Path("memory/tests")
        self.core_dir = Path("core")
        self.commands_dir = Path("core/commands")

        self.test_files = []
        self.command_handlers = []
        self.coverage_map = defaultdict(list)

    def scan_test_files(self):
        """Scan all test files"""
        print("📂 Scanning test files...")

        for test_file in self.test_dir.rglob("test_*.py"):
            self.test_files.append(test_file)

        print(f"   Found {len(self.test_files)} test files\n")

    def scan_command_handlers(self):
        """Scan command handler files"""
        print("📂 Scanning command handlers...")

        if self.commands_dir.exists():
            for handler_file in self.commands_dir.glob("*.py"):
                if handler_file.name != "__init__.py":
                    self.command_handlers.append(handler_file)

        print(f"   Found {len(self.command_handlers)} command handlers\n")

    def analyze_test_coverage(self):
        """Analyze which components have tests"""
        print("🔍 Analyzing test coverage...\n")

        # Read all test files and identify what they test
        for test_file in self.test_files:
            with open(test_file, 'r') as f:
                content = f.read()

            # Extract test function names
            test_functions = re.findall(r'def (test_\w+)', content)

            # Try to identify what's being tested
            imports = re.findall(r'from ([\w.]+) import', content)

            self.coverage_map[test_file.name] = {
                'path': str(test_file),
                'test_count': len(test_functions),
                'imports': imports,
                'functions': test_functions
            }

    def identify_gaps(self):
        """Identify gaps in test coverage"""
        print("🎯 Identifying coverage gaps...\n")

        # Commands that should have tests
        core_commands = [
            "HELP", "STATUS", "VERSION", "BLANK", "SETUP",
            "FILE", "EDIT", "RUN", "HISTORY", "RESTORE",
            "MAP", "TILE", "EXPLORE",
            "THEME", "GUIDE", "DIAGRAM",
            "KNOWLEDGE", "KB", "MEMORY", "PRIVATE", "SHARED",
            "PANEL", "POKE",
            "DEBUG", "BREAK", "STEP", "INSPECT",
            "PLAY", "XP", "RESOURCE", "SCENARIO",
            "ASK", "DEV",
        ]

        # Check which commands have dedicated tests
        tested_commands = set()
        for test_info in self.coverage_map.values():
            for func in test_info['functions']:
                # Extract command name from test function
                match = re.search(r'test_(\w+)_', func)
                if match:
                    cmd = match.group(1).upper()
                    tested_commands.add(cmd)

        # Identify untested commands
        untested = set(core_commands) - tested_commands

        if untested:
            print("❌ Commands without dedicated tests:")
            for cmd in sorted(untested):
                print(f"   • {cmd}")
            print()
        else:
            print("✅ All core commands have tests!\n")

        return untested

    def generate_report(self):
        """Generate coverage report"""
        print("="*70)
        print("📊 TEST COVERAGE REPORT")
        print("="*70)
        print()

        # Summary statistics
        total_tests = sum(info['test_count'] for info in self.coverage_map.values())

        print(f"Total Test Files: {len(self.test_files)}")
        print(f"Total Test Functions: {total_tests}")
        print(f"Command Handlers: {len(self.command_handlers)}")
        print()

        # Distribution
        integration_count = len([f for f in self.test_files if 'integration' in str(f)])
        unit_count = len([f for f in self.test_files if 'unit' in str(f)])
        other_count = len(self.test_files) - integration_count - unit_count

        print("Test Distribution:")
        print(f"   Integration Tests: {integration_count} files")
        print(f"   Unit Tests: {unit_count} files")
        print(f"   Other Tests: {other_count} files")
        print()

        # Top test files by test count
        print("Top 10 Test Files (by test count):")
        sorted_tests = sorted(
            self.coverage_map.items(),
            key=lambda x: x[1]['test_count'],
            reverse=True
        )[:10]

        for filename, info in sorted_tests:
            print(f"   • {filename}: {info['test_count']} tests")
        print()

        # Identify gaps
        untested = self.identify_gaps()

        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print()

        target_tests = 1000
        current_tests = total_tests
        tests_needed = target_tests - current_tests

        print(f"Current: {current_tests} tests")
        print(f"Target: {target_tests} tests")
        print(f"Gap: {tests_needed} tests needed")
        print()

        if tests_needed > 0:
            print("🎯 Priority Areas for New Tests:")
            print("   1. Extension integration tests (dashboard, teletext, terminal)")
            print("   2. Performance regression tests")
            print("   3. Error handling and edge cases")
            print("   4. Cross-platform compatibility tests")
            print("   5. Data validation tests")

            if untested:
                print(f"\n   6. Create tests for {len(untested)} untested commands")
        else:
            print("✅ Test coverage target exceeded!")

        print()
        print("="*70)

    def run(self):
        """Run the analysis"""
        print("="*70)
        print("🔬 uDOS v1.0.26 Test Coverage Analysis")
        print("="*70)
        print()

        self.scan_test_files()
        self.scan_command_handlers()
        self.analyze_test_coverage()
        self.generate_report()

        print("\n✅ Analysis complete!")


def main():
    analyzer = CoverageAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
