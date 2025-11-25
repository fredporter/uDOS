#!/usr/bin/env python3
"""
v1.0.26 Phase 2: Startup Time Profiler

Instruments the complete uDOS startup sequence to identify bottlenecks.
Tracks timing for each initialization phase.

Usage:
    python3 memory/tests/startup_profiler_v1_0_26.py

Target: <500ms total startup time

Author: uDOS Development Team
Version: 1.0.26
"""

import time
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class StartupProfiler:
    """Profile uDOS startup sequence"""

    TARGET_STARTUP_MS = 500.0
    WARNING_THRESHOLD_MS = 50.0  # Warn if any operation takes >50ms

    def __init__(self):
        self.timings: List[Dict] = []
        self.start_time = None

    def start(self):
        """Start profiling"""
        self.start_time = time.perf_counter()
        self.timings = []

    def record(self, operation: str, start: float):
        """Record an operation timing"""
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000

        self.timings.append({
            'operation': operation,
            'time_ms': elapsed_ms,
            'relative_time_ms': (end - self.start_time) * 1000
        })

        return elapsed_ms

    def profile_startup(self):
        """Profile complete startup sequence"""
        print()
        print("╔════════════════════════════════════════════════════════════╗")
        print("║  uDOS v1.0.26 Startup Profiler                            ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print()
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: <{self.TARGET_STARTUP_MS}ms total startup")
        print()
        print("=" * 60)
        print()

        self.start()

        # 1. Core imports
        print("⏱️  Core imports...")
        t = time.perf_counter()
        from core.uDOS_parser import Parser
        from core.uDOS_commands import CommandHandler
        from core.uDOS_grid import Grid
        from core.uDOS_logger import Logger
        from core.uDOS_settings import SettingsManager
        elapsed = self.record('Core imports', t)
        print(f"   ✓ {elapsed:.2f}ms")

        # 2. Parser initialization
        print("⏱️  Parser initialization...")
        t = time.perf_counter()
        parser = Parser()
        elapsed = self.record('Parser init', t)
        print(f"   ✓ {elapsed:.2f}ms")

        # 3. Grid initialization
        print("⏱️  Grid initialization...")
        t = time.perf_counter()
        grid = Grid()
        elapsed = self.record('Grid init', t)
        print(f"   ✓ {elapsed:.2f}ms")

        # 4. Logger initialization
        print("⏱️  Logger initialization...")
        t = time.perf_counter()
        logger = Logger()
        elapsed = self.record('Logger init', t)
        print(f"   ✓ {elapsed:.2f}ms")

        # 5. Settings manager
        print("⏱️  Settings manager initialization...")
        t = time.perf_counter()
        settings = SettingsManager()
        elapsed = self.record('Settings manager init', t)
        print(f"   ✓ {elapsed:.2f}ms")

        # 6. CommandHandler initialization (most expensive)
        print("⏱️  CommandHandler initialization...")
        t = time.perf_counter()
        handler = CommandHandler(theme='dungeon', logger=logger)
        elapsed = self.record('CommandHandler init', t)
        print(f"   ✓ {elapsed:.2f}ms")

        print()
        self.report()

    def report(self):
        """Generate startup profiling report"""
        print("=" * 60)
        print("📊 Startup Breakdown")
        print("=" * 60)
        print()

        total_time = sum(t['time_ms'] for t in self.timings)

        # Sort by time (descending)
        sorted_timings = sorted(self.timings, key=lambda x: x['time_ms'], reverse=True)

        print(f"{'Operation':<40} {'Time (ms)':<12} {'% of Total'}")
        print("-" * 60)

        for timing in sorted_timings:
            pct = (timing['time_ms'] / total_time) * 100 if total_time > 0 else 0
            status = "⚠️ " if timing['time_ms'] > self.WARNING_THRESHOLD_MS else "  "
            print(f"{status}{timing['operation']:<38} {timing['time_ms']:>8.2f}     {pct:>5.1f}%")

        print("-" * 60)
        print(f"{'TOTAL STARTUP TIME':<40} {total_time:>8.2f}ms")
        print()

        # Assessment
        if total_time < self.TARGET_STARTUP_MS:
            print(f"✅ PASS: Startup time <{self.TARGET_STARTUP_MS}ms target")
        else:
            print(f"⚠️  FAIL: Startup time >{self.TARGET_STARTUP_MS}ms target")

        print()

        # Identify bottlenecks
        slow_operations = [t for t in self.timings if t['time_ms'] > self.WARNING_THRESHOLD_MS]
        if slow_operations:
            print("⚠️  Bottlenecks (>50ms):")
            for op in sorted(slow_operations, key=lambda x: x['time_ms'], reverse=True):
                print(f"   • {op['operation']}: {op['time_ms']:.2f}ms")
            print()

        # Recommendations
        print("🔧 Optimization Recommendations:")
        if total_time < 100:
            print("   ✅ Excellent startup performance!")
            print("   • No optimization needed at this time")
        elif total_time < self.TARGET_STARTUP_MS:
            print("   ✅ Good startup performance")
            print("   • Monitor for regression as features are added")
        else:
            print("   1. Profile slow operations (>50ms)")
            print("   2. Implement lazy loading for handlers")
            print("   3. Defer non-critical initializations")
            print("   4. Cache loaded theme/config data")

        print()
        print("=" * 60)
        print()


def main():
    """Run startup profiler"""
    profiler = StartupProfiler()
    profiler.profile_startup()


if __name__ == "__main__":
    main()
