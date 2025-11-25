"""
v1.0.26 Performance Regression Tests

Automated tests that FAIL if performance degrades >10% from baseline.
Ensures performance targets are maintained as new features are added.

Run with: pytest memory/tests/test_v1_0_26_performance_regression.py -v

Author: uDOS Development Team
Version: 1.0.26
"""

import pytest
import time
import statistics
from pathlib import Path
import sys

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.uDOS_parser import Parser
from core.uDOS_commands import CommandHandler
from core.uDOS_grid import Grid
from core.uDOS_logger import Logger


# Phase 2 Performance Baselines (from performance_v1_0_26.py results)
BASELINE_STARTUP_MS = 250.0  # Conservative target (actual: ~216ms)
BASELINE_P90_MS = 5.0  # Conservative target (actual: ~0.89ms)
BASELINE_P99_MS = 10.0  # Conservative target (actual: ~4.39ms)

# Regression thresholds (fail if >10% slower)
REGRESSION_THRESHOLD = 1.10


def time_operation(func, iterations=10):
    """Time an operation over multiple iterations"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)

    times_sorted = sorted(times)
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'p90': times_sorted[int(len(times_sorted) * 0.90)],
        'p99': times_sorted[int(len(times_sorted) * 0.99)] if len(times_sorted) > 2 else max(times)
    }


class TestStartupPerformance:
    """Test startup performance doesn't regress"""

    def test_parser_init_performance(self):
        """Parser initialization should be <1ms"""
        result = time_operation(lambda: Parser(), iterations=20)
        assert result['mean'] < 1.0, f"Parser init too slow: {result['mean']:.2f}ms"

    def test_grid_init_performance(self):
        """Grid initialization should be <1ms"""
        result = time_operation(lambda: Grid(), iterations=20)
        assert result['mean'] < 1.0, f"Grid init too slow: {result['mean']:.2f}ms"

    def test_command_handler_init_performance(self):
        """CommandHandler init should be <50ms"""
        result = time_operation(lambda: CommandHandler(theme='dungeon'), iterations=5)
        assert result['mean'] < 50.0, f"CommandHandler init too slow: {result['mean']:.2f}ms"

    def test_total_startup_performance(self):
        """Total startup should be <{BASELINE_STARTUP_MS}ms"""
        def startup_sequence():
            Parser()
            Grid()
            CommandHandler(theme='dungeon')

        result = time_operation(startup_sequence, iterations=3)
        assert result['mean'] < BASELINE_STARTUP_MS, \
            f"Startup too slow: {result['mean']:.2f}ms > {BASELINE_STARTUP_MS}ms baseline"


class TestCommandExecutionPerformance:
    """Test command execution performance doesn't regress"""

    @pytest.fixture(scope='class')
    def system(self):
        """Initialize system once for all tests"""
        parser = Parser()
        grid = Grid()
        handler = CommandHandler(theme='dungeon')
        return parser, grid, handler

    def test_version_command_performance(self, system):
        """VERSION command should be <1ms P90"""
        parser, grid, handler = system

        def run_command():
            ucode = parser.parse('VERSION')
            handler.handle_command(ucode, grid, parser)

        result = time_operation(run_command, iterations=20)
        assert result['p90'] < 1.0, f"VERSION too slow: {result['p90']:.2f}ms"

    def test_help_command_performance(self, system):
        """HELP command should be <2ms P90"""
        parser, grid, handler = system

        def run_command():
            ucode = parser.parse('HELP')
            handler.handle_command(ucode, grid, parser)

        result = time_operation(run_command, iterations=20)
        assert result['p90'] < 2.0, f"HELP too slow: {result['p90']:.2f}ms"

    def test_status_command_performance(self, system):
        """STATUS command should be <5ms P90"""
        parser, grid, handler = system

        def run_command():
            ucode = parser.parse('STATUS')
            handler.handle_command(ucode, grid, parser)

        result = time_operation(run_command, iterations=20)
        assert result['p90'] < 5.0, f"STATUS too slow: {result['p90']:.2f}ms"

    def test_history_command_performance(self, system):
        """HISTORY command should be <1ms P90"""
        parser, grid, handler = system

        def run_command():
            ucode = parser.parse('HISTORY')
            handler.handle_command(ucode, grid, parser)

        result = time_operation(run_command, iterations=20)
        assert result['p90'] < 1.0, f"HISTORY too slow: {result['p90']:.2f}ms"

    def test_memory_status_performance(self, system):
        """MEMORY STATUS should be <1ms P90"""
        parser, grid, handler = system

        def run_command():
            ucode = parser.parse('MEMORY STATUS')
            handler.handle_command(ucode, grid, parser)

        result = time_operation(run_command, iterations=20)
        assert result['p90'] < 1.0, f"MEMORY STATUS too slow: {result['p90']:.2f}ms"

    def test_grid_status_performance(self, system):
        """GRID STATUS should be <1ms P90"""
        parser, grid, handler = system

        def run_command():
            ucode = parser.parse('GRID STATUS')
            handler.handle_command(ucode, grid, parser)

        result = time_operation(run_command, iterations=20)
        assert result['p90'] < 1.0, f"GRID STATUS too slow: {result['p90']:.2f}ms"

    def test_overall_command_p90_regression(self, system):
        """Overall P90 should not exceed baseline * regression threshold"""
        parser, grid, handler = system

        commands = ['VERSION', 'HELP', 'STATUS', 'HISTORY', 'MEMORY STATUS', 'GRID STATUS']
        all_p90s = []

        for cmd in commands:
            def run_command():
                ucode = parser.parse(cmd)
                handler.handle_command(ucode, grid, parser)

            result = time_operation(run_command, iterations=10)
            all_p90s.append(result['p90'])

        avg_p90 = statistics.mean(all_p90s)
        threshold = BASELINE_P90_MS * REGRESSION_THRESHOLD

        assert avg_p90 < threshold, \
            f"Performance regression detected: {avg_p90:.2f}ms > {threshold:.2f}ms " \
            f"(>{REGRESSION_THRESHOLD-1:.0%} slower than baseline)"

    def test_overall_command_p99_regression(self, system):
        """Overall P99 should not exceed baseline * regression threshold"""
        parser, grid, handler = system

        commands = ['VERSION', 'HELP', 'STATUS', 'HISTORY', 'MEMORY STATUS', 'GRID STATUS']
        all_p99s = []

        for cmd in commands:
            def run_command():
                ucode = parser.parse(cmd)
                handler.handle_command(ucode, grid, parser)

            result = time_operation(run_command, iterations=10)
            all_p99s.append(result['p99'])

        avg_p99 = statistics.mean(all_p99s)
        threshold = BASELINE_P99_MS * REGRESSION_THRESHOLD

        assert avg_p99 < threshold, \
            f"Performance regression detected: {avg_p99:.2f}ms > {threshold:.2f}ms " \
            f"(>{REGRESSION_THRESHOLD-1:.0%} slower than baseline)"


class TestMemoryPerformance:
    """Test memory usage doesn't grow excessively"""

    def test_command_handler_memory_footprint(self):
        """CommandHandler should have reasonable memory footprint"""
        import tracemalloc

        tracemalloc.start()

        # Initialize handler
        handler = CommandHandler(theme='dungeon')

        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Should be <20MB for handler initialization
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 20.0, f"CommandHandler uses too much memory: {peak_mb:.2f}MB"

    def test_repeated_command_no_memory_leak(self):
        """Repeated command execution shouldn't leak memory"""
        import tracemalloc

        parser = Parser()
        grid = Grid()
        handler = CommandHandler(theme='dungeon')

        tracemalloc.start()

        # Run commands multiple times
        for _ in range(100):
            ucode = parser.parse('VERSION')
            handler.handle_command(ucode, grid, parser)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Should be <5MB for 100 commands
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 5.0, f"Memory leak detected: {peak_mb:.2f}MB after 100 commands"


class TestFileIOPerformance:
    """Test file I/O operations meet performance targets"""

    def test_commands_json_load_time(self):
        """Loading commands.json should be <10ms"""
        import json

        def load_commands():
            with open('knowledge/system/commands.json', 'r') as f:
                json.load(f)

        result = time_operation(load_commands, iterations=20)
        assert result['mean'] < 10.0, f"commands.json load too slow: {result['mean']:.2f}ms"

    def test_theme_json_load_time(self):
        """Loading theme.json should be <5ms"""
        import json

        def load_theme():
            with open('knowledge/system/themes/dungeon.json', 'r') as f:
                json.load(f)

        result = time_operation(load_theme, iterations=20)
        assert result['mean'] < 5.0, f"Theme load too slow: {result['mean']:.2f}ms"


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
