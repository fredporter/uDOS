#!/usr/bin/env python3
"""
v1.0.26 Phase 2: Performance Optimization - In-Process Benchmarks

ACCURATE performance measurement using direct function calls (not subprocess).
Measures actual command execution time to meet <50ms P90 target.

Usage:
    python3 memory/tests/performance_v1_0_26.py

Targets (Phase 2 Week 2: Nov 25-Dec 1):
    - Command Response: <50ms P90, <25ms P50
    - Startup Time: <500ms total
    - File I/O: <10ms per operation
    - Memory Usage: <100MB for core system

Author: uDOS Development Team
Version: 1.0.26
"""

import time
import statistics
import sys
from pathlib import Path
from typing import List, Dict, Callable
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.uDOS_parser import Parser
from core.uDOS_commands import CommandHandler
from core.uDOS_grid import Grid


class PerformanceBaseline:
    """Measure v1.0.26 performance baselines"""

    # Phase 2 Performance Targets
    TARGET_P50_MS = 25.0  # 50th percentile: 25ms
    TARGET_P90_MS = 50.0  # 90th percentile: 50ms
    TARGET_P99_MS = 100.0  # 99th percentile: 100ms
    TARGET_STARTUP_MS = 500.0  # Total startup time
    TARGET_FILE_IO_MS = 10.0  # File operations

    def __init__(self):
        self.results = {}
        self.startup_times = {}

    def time_function(self, func: Callable, iterations: int = 10) -> Dict:
        """
        Time a function execution over multiple iterations

        Args:
            func: Function to time
            iterations: Number of iterations

        Returns:
            Dict with timing statistics
        """
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            try:
                func()
                end = time.perf_counter()
                times.append((end - start) * 1000)  # Convert to ms
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                continue

        if not times:
            return None

        times_sorted = sorted(times)
        return {
            'count': len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'p50_ms': times_sorted[int(len(times_sorted) * 0.50)],
            'p90_ms': times_sorted[int(len(times_sorted) * 0.90)],
            'p99_ms': times_sorted[int(len(times_sorted) * 0.99)] if len(times_sorted) > 2 else max(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0.0,
            'raw_times': times
        }

    def benchmark_startup_sequence(self):
        """Benchmark individual startup operations"""
        print("🚀 Benchmarking Startup Sequence")
        print("=" * 60)
        print()

        # 1. Parser initialization
        print("⏱️  Parser initialization...")
        result = self.time_function(lambda: Parser(), iterations=5)
        self.startup_times['parser_init'] = result['mean_ms']
        print(f"   ✓ {result['mean_ms']:.2f}ms (median: {result['median_ms']:.2f}ms)")

        # 2. Grid initialization
        print("⏱️  Grid initialization...")
        result = self.time_function(lambda: Grid(), iterations=5)
        self.startup_times['grid_init'] = result['mean_ms']
        print(f"   ✓ {result['mean_ms']:.2f}ms (median: {result['median_ms']:.2f}ms)")

        # 3. CommandHandler initialization
        print("⏱️  CommandHandler initialization...")
        result = self.time_function(lambda: CommandHandler(theme='dungeon'), iterations=3)
        self.startup_times['handler_init'] = result['mean_ms']
        print(f"   ✓ {result['mean_ms']:.2f}ms (median: {result['median_ms']:.2f}ms)")

        print()

        # Total startup time
        total = sum(self.startup_times.values())
        print(f"📊 Total Startup Time: {total:.2f}ms")

        if total < self.TARGET_STARTUP_MS:
            print(f"   ✅ PASS: <{self.TARGET_STARTUP_MS}ms target")
        else:
            print(f"   ⚠️  FAIL: >{self.TARGET_STARTUP_MS}ms target (needs optimization)")

        print()
        print("=" * 60)
        print()

        return self.startup_times

    def benchmark_command_execution(self):
        """Benchmark actual command execution times"""
        print("⚡ Benchmarking Command Execution")
        print("=" * 60)
        print()

        # Initialize components once
        parser = Parser()
        grid = Grid()
        handler = CommandHandler(theme='dungeon')

        # Commands to benchmark (fast commands first)
        commands = [
            ('VERSION', 'Show version'),
            ('HELP', 'Show help'),
            ('STATUS', 'Show status'),
            ('HISTORY', 'Show history'),
            ('MEMORY STATUS', 'Memory status'),
            ('GRID STATUS', 'Grid status'),
        ]

        command_results = {}

        for command, description in commands:
            print(f"⏱️  {command} ({description})...")

            def run_command():
                ucode = parser.parse(command)
                handler.handle_command(ucode, grid, parser)

            result = self.time_function(run_command, iterations=10)

            if result:
                command_results[command] = result
                p50 = result['p50_ms']
                p90 = result['p90_ms']

                # Status indicator
                if p90 < self.TARGET_P90_MS:
                    status = "✅"
                elif p90 < self.TARGET_P90_MS * 1.5:
                    status = "🟡"
                else:
                    status = "⚠️"

                print(f"   {status} P50: {p50:.2f}ms | P90: {p90:.2f}ms | P99: {result['p99_ms']:.2f}ms")

        print()
        print("=" * 60)
        print()

        return command_results

    def analyze_results(self, command_results: Dict):
        """Analyze and report on performance results"""
        print("📊 Performance Analysis")
        print("=" * 60)
        print()

        # Extract all P90 times
        p90_times = [result['p90_ms'] for result in command_results.values()]

        if not p90_times:
            print("⚠️  No results to analyze")
            return

        # Overall P90
        overall_p90 = statistics.mean(p90_times)
        max_p90 = max(p90_times)

        print(f"Overall P90: {overall_p90:.2f}ms")
        print(f"Worst P90:   {max_p90:.2f}ms")
        print(f"Target P90:  {self.TARGET_P90_MS:.2f}ms")
        print()

        # Pass/Fail assessment
        passing = sum(1 for p90 in p90_times if p90 < self.TARGET_P90_MS)
        total = len(p90_times)

        print(f"Commands Meeting Target: {passing}/{total} ({passing/total*100:.1f}%)")
        print()

        # Identify slow commands
        slow_commands = [(cmd, result['p90_ms'])
                        for cmd, result in command_results.items()
                        if result['p90_ms'] > self.TARGET_P90_MS]

        if slow_commands:
            print("⚠️  Commands Exceeding Target:")
            for cmd, p90 in sorted(slow_commands, key=lambda x: x[1], reverse=True):
                print(f"   • {cmd}: {p90:.2f}ms (over by {p90 - self.TARGET_P90_MS:.2f}ms)")
            print()
        else:
            print("✅ All commands meeting P90 target!")
            print()

        # Recommendations
        print("🔧 Optimization Recommendations:")
        if overall_p90 > self.TARGET_P90_MS:
            print("   1. Profile slow commands to identify bottlenecks")
            print("   2. Implement lazy loading for handler initialization")
            print("   3. Cache frequently accessed data (commands.json, themes)")
            print("   4. Optimize file I/O operations")
            print("   5. Reduce import overhead in command handlers")
        else:
            print("   ✅ System performance meets targets!")
            print("   • Continue monitoring with regression tests")
            print("   • Maintain performance as new features are added")

        print()
        print("=" * 60)

    def run_full_benchmark(self):
        """Run complete performance benchmark suite"""
        print()
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  uDOS v1.0.26 Phase 2: Performance Baseline               ║")
        print("║  In-Process Command Execution Timing                       ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Targets: P50<{self.TARGET_P50_MS}ms | P90<{self.TARGET_P90_MS}ms | Startup<{self.TARGET_STARTUP_MS}ms")
        print()
        print("=" * 60)
        print()

        # 1. Startup sequence
        startup_times = self.benchmark_startup_sequence()

        # 2. Command execution
        command_results = self.benchmark_command_execution()

        # 3. Analysis
        self.analyze_results(command_results)

        # 4. Summary
        print()
        print("=" * 60)
        print("✅ Benchmark Complete!")
        print()
        print("Next Steps (Phase 2):")
        print("  1. Review slow commands and profile bottlenecks")
        print("  2. Implement optimizations for commands >50ms")
        print("  3. Create regression tests to prevent degradation")
        print("  4. Document performance baselines in PERFORMANCE-v1.0.26.md")
        print()


def main():
    """Run performance benchmark"""
    baseline = PerformanceBaseline()
    baseline.run_full_benchmark()


if __name__ == "__main__":
    main()
