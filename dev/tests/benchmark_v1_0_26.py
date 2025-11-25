#!/usr/bin/env python3
"""
v1.0.26 Performance Baseline Benchmark

This script measures the performance of core uDOS commands to establish
a baseline for optimization work.

Usage:
    python3 memory/tests/benchmark_v1_0_26.py

Output:
    - Performance metrics for each command
    - Average response times
    - Identification of slow operations (>50ms)
    - Recommendations for optimization
"""

import time
import statistics
import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime


class PerformanceBenchmark:
    """Benchmark uDOS command performance via subprocess execution"""

    def __init__(self):
        self.results = {}
        self.project_root = Path(__file__).parent.parent.parent
        self.core = None

    def benchmark_command_via_script(self, command, iterations=5):
        """
        Benchmark a command by running it through a uDOS script

        Args:
            command: Command string to execute
            iterations: Number of times to run the command

        Returns:
            dict with timing statistics
        """
        times = []

        for i in range(iterations):
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.uscript', delete=False) as f:
                f.write(f"{command}\n")
                f.write("EXIT\n")
                script_path = f.name

            try:
                start = time.perf_counter()

                # Run uDOS with the script
                result = subprocess.run(
                    [sys.executable, str(self.project_root / 'uDOS.py'), script_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                end = time.perf_counter()
                elapsed_ms = (end - start) * 1000

                # Only record if command succeeded
                if result.returncode == 0:
                    times.append(elapsed_ms)
                else:
                    print(f"   ⚠️  Command failed with code {result.returncode}")

            except subprocess.TimeoutExpired:
                print(f"   ⚠️  Command timed out")
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
            finally:
                # Clean up script file
                try:
                    os.unlink(script_path)
                except:
                    pass

        if not times:
            return None

        return {
            'command': command,
            'iterations': len(times),
            'min_ms': min(times),
            'max_ms': max(times),
            'avg_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'raw_times': times
        }

    def run_benchmarks(self):
        """Run all benchmarks"""
        print("📊 Running performance benchmarks...\n")
        print("⚠️  Note: Times include full uDOS startup overhead\n")

        # Lightweight commands to benchmark
        commands = [
            "VERSION",
            "HELP",
            "STATUS",
        ]

        for cmd in commands:
            print(f"⏱️  Benchmarking: {cmd}")
            result = self.benchmark_command_via_script(cmd, iterations=3)

            if result:
                self.results[cmd] = result
                avg = result['avg_ms']

                # Color code based on speed (accounting for startup overhead)
                if avg < 500:
                    icon = "🟢"  # Fast
                elif avg < 1000:
                    icon = "🟡"  # Acceptable
                elif avg < 2000:
                    icon = "🟠"  # Slow
                else:
                    icon = "🔴"  # Very slow

                print(f"   {icon} Average: {avg:.2f}ms (min: {result['min_ms']:.2f}ms, max: {result['max_ms']:.2f}ms)")
            else:
                print(f"   ❌ Failed to benchmark")

            print()

    def analyze_results(self):
        """Analyze benchmark results and provide recommendations"""
        print("\n" + "="*70)
        print("📈 PERFORMANCE ANALYSIS")
        print("="*70 + "\n")

        if not self.results:
            print("❌ No results to analyze")
            return

        # Calculate overall statistics
        all_avgs = [r['avg_ms'] for r in self.results.values()]
        overall_avg = statistics.mean(all_avgs)
        overall_median = statistics.median(all_avgs)

        print(f"Overall Average: {overall_avg:.2f}ms (includes startup overhead)")
        print(f"Overall Median: {overall_median:.2f}ms")
        print(f"Total Commands Tested: {len(self.results)}")
        print()

        # Categorize by performance (adjusted for subprocess overhead)
        fast = []      # < 500ms
        acceptable = [] # 500-1000ms
        slow = []      # 1000-2000ms
        very_slow = []  # > 2000ms

        for cmd, result in self.results.items():
            avg = result['avg_ms']
            if avg < 500:
                fast.append((cmd, avg))
            elif avg < 1000:
                acceptable.append((cmd, avg))
            elif avg < 2000:
                slow.append((cmd, avg))
            else:
                very_slow.append((cmd, avg))

        print("🟢 Fast Commands (<500ms):")
        if fast:
            for cmd, avg in sorted(fast, key=lambda x: x[1]):
                print(f"   • {cmd}: {avg:.2f}ms")
        else:
            print("   None")
        print()

        print("🟡 Acceptable Commands (500-1000ms):")
        if acceptable:
            for cmd, avg in sorted(acceptable, key=lambda x: x[1]):
                print(f"   • {cmd}: {avg:.2f}ms")
        else:
            print("   None")
        print()

        if slow:
            print("🟠 Slow Commands (1000-2000ms) - OPTIMIZATION TARGET:")
            for cmd, avg in sorted(slow, key=lambda x: x[1]):
                print(f"   • {cmd}: {avg:.2f}ms")
            print()

        if very_slow:
            print("🔴 Very Slow Commands (>2000ms) - CRITICAL OPTIMIZATION NEEDED:")
            for cmd, avg in sorted(very_slow, key=lambda x: x[1]):
                print(f"   • {cmd}: {avg:.2f}ms")
            print()

        # Recommendations
        print("💡 RECOMMENDATIONS:")
        print()
        print("⚠️  Note: These times include full uDOS startup overhead (~300-500ms)")
        print("    For pure command performance, subtract startup time from results")
        print()

        if overall_avg < 1000:
            print("✅ Overall performance is EXCELLENT (<1000ms average with startup)")
            print("   Focus: Measure pure command times without startup overhead")
        elif overall_avg < 2000:
            print("⚠️  Overall performance is ACCEPTABLE but could improve")
            print("   Focus: Optimize startup time or slow commands")
        else:
            print("❌ Overall performance needs improvement")
            print("   Focus: Identify major bottlenecks in startup or commands")

        print()
        print("="*70)

    def export_results(self, filename=None):
        """Export results to JSON"""
        if filename is None:
            filename = str(self.project_root / "memory" / "tests" / f"benchmark_results_v1_0_26_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        output = {
            'version': '1.0.26',
            'timestamp': datetime.now().isoformat(),
            'note': 'Times include full uDOS startup overhead (subprocess execution)',
            'results': self.results,
            'summary': {
                'total_commands': len(self.results),
                'overall_avg_ms': statistics.mean([r['avg_ms'] for r in self.results.values()]) if self.results else 0,
                'overall_median_ms': statistics.median([r['avg_ms'] for r in self.results.values()]) if self.results else 0,
            }
        }

        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n💾 Results exported to: {filename}")


def main():
    """Main benchmark execution"""
    print("="*70)
    print("🚀 uDOS v1.0.26 Performance Baseline Benchmark")
    print("="*70)
    print()

    benchmark = PerformanceBenchmark()

    try:
        benchmark.run_benchmarks()
        benchmark.analyze_results()
        benchmark.export_results()

        print("\n✅ Benchmark complete!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
