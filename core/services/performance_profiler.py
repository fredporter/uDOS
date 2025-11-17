"""
Performance Profiler - v1.0.23 Phase 7
Profile and optimize command execution performance

Features:
- Command execution timing
- Performance benchmarks
- Bottleneck identification
- Optimization suggestions

Author: uDOS Development Team
Version: 1.0.23
"""

import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import statistics


@dataclass
class ExecutionMetric:
    """Single execution metric"""
    command: str
    execution_time: float
    timestamp: datetime
    success: bool
    args: List[str]
    metadata: Optional[Dict] = None


class PerformanceProfiler:
    """Profile command execution performance"""

    # Performance targets
    TARGET_P50 = 0.025  # 25ms (50th percentile)
    TARGET_P90 = 0.050  # 50ms (90th percentile)
    TARGET_P99 = 0.100  # 100ms (99th percentile)

    def __init__(self, logger=None):
        """Initialize profiler"""
        self.logger = logger
        self._metrics: List[ExecutionMetric] = []
        self._command_stats: Dict[str, List[float]] = {}
        self._slow_commands: List[ExecutionMetric] = []
        self._enabled = True

    def profile_command(self, command: str, args: List[str], func: Callable) -> Any:
        """
        Profile a command execution

        Args:
            command: Command name
            args: Command arguments
            func: Function to execute

        Returns:
            Result of function execution
        """
        if not self._enabled:
            return func()

        start_time = time.time()
        success = True
        result = None

        try:
            result = func()
        except Exception as e:
            success = False
            raise
        finally:
            execution_time = time.time() - start_time

            # Record metric
            metric = ExecutionMetric(
                command=command,
                execution_time=execution_time,
                timestamp=datetime.now(),
                success=success,
                args=args
            )

            self._metrics.append(metric)

            # Track per-command stats
            if command not in self._command_stats:
                self._command_stats[command] = []
            self._command_stats[command].append(execution_time)

            # Track slow commands
            if execution_time > self.TARGET_P90:
                self._slow_commands.append(metric)

                if self.logger:
                    self.logger.warning(
                        f"Slow command: {command} took {execution_time*1000:.2f}ms "
                        f"(target: {self.TARGET_P90*1000:.0f}ms)"
                    )

        return result

    def get_percentile(self, times: List[float], percentile: float) -> float:
        """Calculate percentile from list of times"""
        if not times:
            return 0.0

        sorted_times = sorted(times)
        index = int(len(sorted_times) * percentile)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def get_command_stats(self, command: str) -> Optional[Dict]:
        """Get statistics for specific command"""
        if command not in self._command_stats:
            return None

        times = self._command_stats[command]

        return {
            'command': command,
            'count': len(times),
            'min': min(times) * 1000,  # Convert to ms
            'max': max(times) * 1000,
            'mean': statistics.mean(times) * 1000,
            'median': statistics.median(times) * 1000,
            'p90': self.get_percentile(times, 0.90) * 1000,
            'p99': self.get_percentile(times, 0.99) * 1000,
            'total_time': sum(times) * 1000
        }

    def get_overall_stats(self) -> Dict:
        """Get overall performance statistics"""
        if not self._metrics:
            return {'error': 'No metrics collected'}

        all_times = [m.execution_time for m in self._metrics]
        successful = sum(1 for m in self._metrics if m.success)

        return {
            'total_commands': len(self._metrics),
            'successful': successful,
            'failed': len(self._metrics) - successful,
            'min_time': min(all_times) * 1000,
            'max_time': max(all_times) * 1000,
            'mean_time': statistics.mean(all_times) * 1000,
            'median_time': statistics.median(all_times) * 1000,
            'p50': self.get_percentile(all_times, 0.50) * 1000,
            'p90': self.get_percentile(all_times, 0.90) * 1000,
            'p99': self.get_percentile(all_times, 0.99) * 1000,
            'slow_commands': len(self._slow_commands),
            'unique_commands': len(self._command_stats)
        }

    def get_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        stats = self.get_overall_stats()

        if 'error' in stats:
            return "No performance data available"

        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│  PERFORMANCE REPORT                                            │",
            "├─────────────────────────────────────────────────────────────────┤",
            f"│  Total Commands:     {stats['total_commands']:<44} │",
            f"│  Successful:         {stats['successful']:<44} │",
            f"│  Failed:             {stats['failed']:<44} │",
            f"│  Unique Commands:    {stats['unique_commands']:<44} │",
            "│                                                                 │",
            "│  Execution Time (ms):                                           │",
            f"│    Min:              {stats['min_time']:>6.2f}ms {' '*40} │",
            f"│    Mean:             {stats['mean_time']:>6.2f}ms {' '*40} │",
            f"│    Median:           {stats['median_time']:>6.2f}ms {' '*40} │",
            f"│    Max:              {stats['max_time']:>6.2f}ms {' '*40} │",
            "│                                                                 │",
            "│  Percentiles:                                                   │",
            f"│    P50 (median):     {stats['p50']:>6.2f}ms (target: {self.TARGET_P50*1000:.0f}ms) {' '*22} │",
            f"│    P90:              {stats['p90']:>6.2f}ms (target: {self.TARGET_P90*1000:.0f}ms) {' '*22} │",
            f"│    P99:              {stats['p99']:>6.2f}ms (target: {self.TARGET_P99*1000:.0f}ms) {' '*21} │",
            "│                                                                 │",
            f"│  Slow Commands:      {stats['slow_commands']:<44} │",
        ]

        # Add target comparison
        output.append("│                                                                 │")
        output.append("│  Target Comparison:                                             │")

        p50_status = "✅" if stats['p50'] <= self.TARGET_P50 * 1000 else "❌"
        p90_status = "✅" if stats['p90'] <= self.TARGET_P90 * 1000 else "❌"
        p99_status = "✅" if stats['p99'] <= self.TARGET_P99 * 1000 else "❌"

        output.append(f"│    P50: {p50_status} {stats['p50']:>6.2f}ms vs {self.TARGET_P50*1000:.0f}ms target {' '*28} │")
        output.append(f"│    P90: {p90_status} {stats['p90']:>6.2f}ms vs {self.TARGET_P90*1000:.0f}ms target {' '*28} │")
        output.append(f"│    P99: {p99_status} {stats['p99']:>6.2f}ms vs {self.TARGET_P99*1000:.0f}ms target {' '*27} │")

        output.append("└─────────────────────────────────────────────────────────────────┘")

        return "\n".join(output)

    def get_slowest_commands(self, limit: int = 10) -> List[Dict]:
        """Get slowest commands"""
        slowest = sorted(self._slow_commands, key=lambda m: m.execution_time, reverse=True)

        return [{
            'command': m.command,
            'args': m.args,
            'time': m.execution_time * 1000,
            'timestamp': m.timestamp.isoformat()
        } for m in slowest[:limit]]

    def get_command_leaderboard(self, limit: int = 10) -> str:
        """Get leaderboard of commands by execution time"""
        if not self._command_stats:
            return "No command data available"

        # Calculate average time per command
        command_avgs = []
        for cmd, times in self._command_stats.items():
            avg_time = statistics.mean(times) * 1000
            count = len(times)
            command_avgs.append((cmd, avg_time, count))

        # Sort by average time (slowest first)
        command_avgs.sort(key=lambda x: x[1], reverse=True)

        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│  COMMAND LEADERBOARD (Slowest First)                           │",
            "├─────────────────────────────────────────────────────────────────┤",
            "│  Command                 Avg Time    Count                      │",
            "├─────────────────────────────────────────────────────────────────┤"
        ]

        for cmd, avg_time, count in command_avgs[:limit]:
            output.append(f"│  {cmd:<20} {avg_time:>8.2f}ms {count:>8} execs {' '*15} │")

        output.append("└─────────────────────────────────────────────────────────────────┘")

        return "\n".join(output)

    def get_optimization_suggestions(self) -> List[str]:
        """Get optimization suggestions based on profiling data"""
        suggestions = []
        stats = self.get_overall_stats()

        if 'error' in stats:
            return ["No data available for suggestions"]

        # Check overall performance
        if stats['p90'] > self.TARGET_P90 * 1000:
            suggestions.append(
                f"⚠️  P90 ({stats['p90']:.2f}ms) exceeds target ({self.TARGET_P90*1000:.0f}ms) - "
                f"optimize slow commands"
            )

        if stats['mean_time'] > self.TARGET_P90 * 1000:
            suggestions.append(
                f"⚠️  Mean execution time ({stats['mean_time']:.2f}ms) is high - "
                f"consider caching or lazy loading"
            )

        # Check for slow commands
        if stats['slow_commands'] > 0:
            suggestions.append(
                f"⚠️  {stats['slow_commands']} slow commands detected - "
                f"review command implementations"
            )

        # Check for outliers
        if stats['max_time'] > stats['mean_time'] * 10:
            suggestions.append(
                f"⚠️  Large variance in execution times (max: {stats['max_time']:.2f}ms, "
                f"mean: {stats['mean_time']:.2f}ms) - investigate outliers"
            )

        # Suggest specific optimizations
        for cmd, times in self._command_stats.items():
            avg = statistics.mean(times) * 1000
            if avg > self.TARGET_P90 * 1000:
                suggestions.append(f"⚠️  '{cmd}' averages {avg:.2f}ms - consider optimization")

        if not suggestions:
            suggestions.append("✅ Performance looks good! All targets met.")

        return suggestions

    def reset(self):
        """Reset all metrics"""
        self._metrics.clear()
        self._command_stats.clear()
        self._slow_commands.clear()

    def enable(self):
        """Enable profiling"""
        self._enabled = True

    def disable(self):
        """Disable profiling"""
        self._enabled = False

    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        import json

        data = {
            'metrics': [
                {
                    'command': m.command,
                    'execution_time': m.execution_time,
                    'timestamp': m.timestamp.isoformat(),
                    'success': m.success,
                    'args': m.args
                }
                for m in self._metrics
            ],
            'stats': self.get_overall_stats(),
            'command_stats': {
                cmd: self.get_command_stats(cmd)
                for cmd in self._command_stats.keys()
            }
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Global profiler instance
_profiler = None


def get_profiler(logger=None) -> PerformanceProfiler:
    """Get global profiler instance"""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler(logger=logger)
    return _profiler


def profile(command: str, args: List[str] = None):
    """
    Decorator for profiling functions

    Usage:
        @profile("DOCS", ["git"])
        def handle_docs_command():
            ...
    """
    def decorator(func):
        def wrapper(*func_args, **func_kwargs):
            profiler = get_profiler()
            return profiler.profile_command(
                command,
                args or [],
                lambda: func(*func_args, **func_kwargs)
            )
        return wrapper
    return decorator
