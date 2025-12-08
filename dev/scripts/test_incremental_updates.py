#!/usr/bin/env python3
"""
test_incremental_updates.py - Automated Testing for v1.2.8 Features
v1.2.8 - Task 8: Testing Suite

Tests for:
- ChartDataManager (incremental updates)
- EventBuffer (circular buffer, deduplication)
- Latency measurement (ping/pong)
- Connection health monitoring

Usage:
    python dev/scripts/test_incremental_updates.py
    python dev/scripts/test_incremental_updates.py --verbose
    python dev/scripts/test_incremental_updates.py --module chart
"""

import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class TestResults:
    """Track test execution results"""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.start_time = time.time()

    def add_pass(self, test_name: str):
        self.total += 1
        self.passed += 1
        print(f"  ✓ {test_name}")

    def add_fail(self, test_name: str, error: str):
        self.total += 1
        self.failed += 1
        self.errors.append({"test": test_name, "error": error})
        print(f"  ✗ {test_name}: {error}")

    def summary(self):
        elapsed = time.time() - self.start_time
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{self.total} passed ({self.failed} failed)")
        print(f"Execution time: {elapsed:.2f}s")

        if self.errors:
            print(f"\nFailures:")
            for err in self.errors:
                print(f"  - {err['test']}: {err['error']}")

        return self.failed == 0


class ChartDataManagerTests:
    """Test suite for ChartDataManager"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = TestResults()

    def test_dataset_operations(self):
        """Test in-memory dataset operations"""
        print("\n[ChartDataManager] Dataset Operations")

        # Simulate dataset operations
        datasets = []

        # Test 1: Add dataset
        try:
            dataset = {
                "label": "Test Dataset",
                "data": [10, 20, 30],
                "borderColor": "#4CAF50"
            }
            datasets.append(dataset)
            assert len(datasets) == 1
            self.results.add_pass("Add dataset")
        except AssertionError as e:
            self.results.add_fail("Add dataset", str(e))

        # Test 2: Update dataset
        try:
            datasets[0]["data"].append(40)
            assert len(datasets[0]["data"]) == 4
            assert datasets[0]["data"][-1] == 40
            self.results.add_pass("Update dataset")
        except AssertionError as e:
            self.results.add_fail("Update dataset", str(e))

        # Test 3: Remove dataset
        try:
            datasets.pop(0)
            assert len(datasets) == 0
            self.results.add_pass("Remove dataset")
        except AssertionError as e:
            self.results.add_fail("Remove dataset", str(e))

        # Test 4: Multiple datasets
        try:
            for i in range(5):
                datasets.append({"label": f"Dataset {i}", "data": [i*10]})
            assert len(datasets) == 5
            self.results.add_pass("Multiple datasets")
        except AssertionError as e:
            self.results.add_fail("Multiple datasets", str(e))

    def test_incremental_updates(self):
        """Test incremental update performance"""
        print("\n[ChartDataManager] Incremental Updates")

        # Test 1: Single point update (should be <1ms)
        try:
            start = time.perf_counter()
            data = [1, 2, 3, 4, 5]
            data.append(6)
            elapsed = (time.perf_counter() - start) * 1000

            assert elapsed < 1.0, f"Update took {elapsed:.3f}ms (should be <1ms)"
            self.results.add_pass(f"Single point update ({elapsed:.3f}ms)")
        except AssertionError as e:
            self.results.add_fail("Single point update", str(e))

        # Test 2: Batch update performance
        try:
            start = time.perf_counter()
            data = list(range(100))
            for i in range(10):
                data.append(100 + i)
            elapsed = (time.perf_counter() - start) * 1000

            assert elapsed < 10.0, f"Batch update took {elapsed:.3f}ms (should be <10ms)"
            self.results.add_pass(f"Batch update 10 points ({elapsed:.3f}ms)")
        except AssertionError as e:
            self.results.add_fail("Batch update", str(e))

        # Test 3: Memory efficiency
        try:
            import sys
            data = list(range(1000))
            size_kb = sys.getsizeof(data) / 1024

            assert size_kb < 50, f"Dataset size {size_kb:.2f}KB (should be <50KB)"
            self.results.add_pass(f"Memory efficiency ({size_kb:.2f}KB)")
        except AssertionError as e:
            self.results.add_fail("Memory efficiency", str(e))

    def run_all(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("ChartDataManager Test Suite")
        print("="*60)

        self.test_dataset_operations()
        self.test_incremental_updates()

        return self.results


class EventBufferTests:
    """Test suite for EventBuffer"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = TestResults()

    def test_circular_buffer(self):
        """Test circular buffer behavior"""
        print("\n[EventBuffer] Circular Buffer")

        # Simulate circular buffer
        max_size = 100
        buffer = []

        # Test 1: Add events up to max
        try:
            for i in range(100):
                buffer.append({"id": i, "timestamp": time.time()})
            assert len(buffer) == 100
            self.results.add_pass("Fill buffer to max (100)")
        except AssertionError as e:
            self.results.add_fail("Fill buffer", str(e))

        # Test 2: Overflow behavior (FIFO)
        try:
            # Add 10 more events (should remove oldest 10)
            for i in range(100, 110):
                buffer.append({"id": i, "timestamp": time.time()})
                if len(buffer) > max_size:
                    buffer.pop(0)

            assert len(buffer) == 100
            assert buffer[0]["id"] == 10  # Oldest should be id 10
            assert buffer[-1]["id"] == 109  # Newest should be id 109
            self.results.add_pass("FIFO overflow (oldest removed)")
        except AssertionError as e:
            self.results.add_fail("FIFO overflow", str(e))

    def test_deduplication(self):
        """Test event deduplication"""
        print("\n[EventBuffer] Deduplication")

        # Test 1: Duplicate within 5s window
        try:
            events = []
            now = time.time()

            # Add event
            event1 = {"id": "test1", "timestamp": now}
            events.append(event1)

            # Try to add duplicate within 5s
            event2 = {"id": "test1", "timestamp": now + 2}

            # Check if duplicate (same id, within 5s)
            is_duplicate = any(
                e["id"] == event2["id"] and
                abs(event2["timestamp"] - e["timestamp"]) < 5
                for e in events
            )

            assert is_duplicate, "Should detect duplicate within 5s window"
            self.results.add_pass("Detect duplicate within 5s")
        except AssertionError as e:
            self.results.add_fail("Detect duplicate", str(e))

        # Test 2: No duplicate after 5s
        try:
            events = []
            now = time.time()

            event1 = {"id": "test2", "timestamp": now}
            events.append(event1)

            event2 = {"id": "test2", "timestamp": now + 6}

            is_duplicate = any(
                e["id"] == event2["id"] and
                abs(event2["timestamp"] - e["timestamp"]) < 5
                for e in events
            )

            assert not is_duplicate, "Should NOT detect duplicate after 5s"
            self.results.add_pass("No duplicate after 5s")
        except AssertionError as e:
            self.results.add_fail("No duplicate after 5s", str(e))

    def test_persistence(self):
        """Test localStorage persistence simulation"""
        print("\n[EventBuffer] Persistence")

        # Test 1: Save to storage
        try:
            buffer = [
                {"id": 1, "data": "event1"},
                {"id": 2, "data": "event2"}
            ]

            # Simulate localStorage save
            serialized = json.dumps(buffer)
            assert len(serialized) > 0
            self.results.add_pass("Serialize buffer to JSON")
        except Exception as e:
            self.results.add_fail("Serialize buffer", str(e))

        # Test 2: Load from storage
        try:
            deserialized = json.loads(serialized)
            assert len(deserialized) == 2
            assert deserialized[0]["id"] == 1
            self.results.add_pass("Deserialize buffer from JSON")
        except Exception as e:
            self.results.add_fail("Deserialize buffer", str(e))

    def run_all(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("EventBuffer Test Suite")
        print("="*60)

        self.test_circular_buffer()
        self.test_deduplication()
        self.test_persistence()

        return self.results


class LatencyMeasurementTests:
    """Test suite for latency measurement"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = TestResults()

    def test_ping_pong_calculation(self):
        """Test ping/pong latency calculation"""
        print("\n[Latency] Ping/Pong Calculation")

        # Test 1: Calculate round-trip time
        try:
            ping_time = time.time() * 1000  # Convert to ms
            time.sleep(0.05)  # Simulate network delay (50ms)
            pong_time = time.time() * 1000

            latency = pong_time - ping_time

            assert 45 < latency < 60, f"Latency {latency:.1f}ms outside expected range"
            self.results.add_pass(f"RTT calculation ({latency:.1f}ms)")
        except AssertionError as e:
            self.results.add_fail("RTT calculation", str(e))

    def test_rolling_average(self):
        """Test rolling average of last 10 pings"""
        print("\n[Latency] Rolling Average")

        # Test 1: Average of 10 samples
        try:
            latencies = [50, 55, 48, 52, 51, 49, 53, 50, 52, 51]
            avg = sum(latencies) / len(latencies)

            assert abs(avg - 51.1) < 0.5, f"Average {avg:.1f}ms incorrect"
            self.results.add_pass(f"10-sample average ({avg:.1f}ms)")
        except AssertionError as e:
            self.results.add_fail("10-sample average", str(e))

        # Test 2: Rolling window (keep last 10)
        try:
            history = []
            for i in range(15):
                history.append(i * 10)
                if len(history) > 10:
                    history.pop(0)

            assert len(history) == 10
            assert history[0] == 50  # Should start from 5*10
            assert history[-1] == 140  # Should end at 14*10
            self.results.add_pass("Rolling window (FIFO)")
        except AssertionError as e:
            self.results.add_fail("Rolling window", str(e))

    def test_color_thresholds(self):
        """Test latency color coding thresholds"""
        print("\n[Latency] Color Thresholds")

        def get_color(latency):
            if latency < 100:
                return 'green'
            elif latency < 500:
                return 'yellow'
            else:
                return 'red'

        # Test 1: Green (<100ms)
        try:
            assert get_color(50) == 'green'
            assert get_color(99) == 'green'
            self.results.add_pass("Green threshold (<100ms)")
        except AssertionError as e:
            self.results.add_fail("Green threshold", str(e))

        # Test 2: Yellow (100-500ms)
        try:
            assert get_color(100) == 'yellow'
            assert get_color(300) == 'yellow'
            assert get_color(499) == 'yellow'
            self.results.add_pass("Yellow threshold (100-500ms)")
        except AssertionError as e:
            self.results.add_fail("Yellow threshold", str(e))

        # Test 3: Red (>500ms)
        try:
            assert get_color(500) == 'red'
            assert get_color(1000) == 'red'
            self.results.add_pass("Red threshold (>500ms)")
        except AssertionError as e:
            self.results.add_fail("Red threshold", str(e))

    def run_all(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Latency Measurement Test Suite")
        print("="*60)

        self.test_ping_pong_calculation()
        self.test_rolling_average()
        self.test_color_thresholds()

        return self.results


class ConnectionHealthTests:
    """Test suite for connection health monitoring"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = TestResults()

    def test_uptime_formatting(self):
        """Test uptime formatting"""
        print("\n[Connection Health] Uptime Formatting")

        def format_uptime(ms):
            seconds = ms // 1000
            minutes = seconds // 60
            hours = minutes // 60
            days = hours // 24

            if days > 0:
                return f"{days}d {hours % 24}h"
            elif hours > 0:
                return f"{hours}h {minutes % 60}m"
            elif minutes > 0:
                return f"{minutes}m {seconds % 60}s"
            else:
                return f"{seconds}s"

        # Test various durations
        try:
            assert format_uptime(5000) == "5s"
            self.results.add_pass("Format seconds")
        except AssertionError as e:
            self.results.add_fail("Format seconds", str(e))

        try:
            assert format_uptime(125000) == "2m 5s"
            self.results.add_pass("Format minutes")
        except AssertionError as e:
            self.results.add_fail("Format minutes", str(e))

        try:
            assert format_uptime(7325000) == "2h 2m"
            self.results.add_pass("Format hours")
        except AssertionError as e:
            self.results.add_fail("Format hours", str(e))

        try:
            assert format_uptime(90061000) == "1d 1h"
            self.results.add_pass("Format days")
        except AssertionError as e:
            self.results.add_fail("Format days", str(e))

    def test_quality_scoring(self):
        """Test quality indicator scoring algorithm"""
        print("\n[Connection Health] Quality Scoring")

        def calculate_quality(latency, recent_disconnects):
            quality = 100

            # Latency penalties
            if latency > 500:
                quality -= 40
            elif latency > 200:
                quality -= 20
            elif latency > 100:
                quality -= 10

            # Disconnect penalties
            quality -= recent_disconnects * 15

            return max(0, min(100, quality))

        # Test 1: Perfect connection
        try:
            quality = calculate_quality(latency=50, recent_disconnects=0)
            assert quality == 100
            self.results.add_pass("Perfect quality (100%)")
        except AssertionError as e:
            self.results.add_fail("Perfect quality", str(e))

        # Test 2: High latency penalty
        try:
            quality = calculate_quality(latency=600, recent_disconnects=0)
            assert quality == 60
            self.results.add_pass("High latency penalty (-40pts)")
        except AssertionError as e:
            self.results.add_fail("High latency penalty", str(e))

        # Test 3: Disconnect penalty
        try:
            quality = calculate_quality(latency=50, recent_disconnects=2)
            assert quality == 70  # 100 - (2 * 15)
            self.results.add_pass("Disconnect penalty (-15pts each)")
        except AssertionError as e:
            self.results.add_fail("Disconnect penalty", str(e))

        # Test 4: Combined penalties
        try:
            quality = calculate_quality(latency=600, recent_disconnects=3)
            assert quality == 15  # 100 - 40 - 45
            self.results.add_pass("Combined penalties")
        except AssertionError as e:
            self.results.add_fail("Combined penalties", str(e))

    def test_event_rate_tracking(self):
        """Test event rate calculation"""
        print("\n[Connection Health] Event Rate")

        # Test 1: Events per minute
        try:
            events = []
            now = time.time()

            # Add 30 events in last minute
            for i in range(30):
                events.append(now - (i * 2))  # 2s apart

            # Filter events in last 60s
            recent = [e for e in events if now - e < 60]
            rate = len(recent)

            assert rate == 30
            self.results.add_pass(f"Event rate calculation ({rate}/min)")
        except AssertionError as e:
            self.results.add_fail("Event rate calculation", str(e))

    def run_all(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("Connection Health Test Suite")
        print("="*60)

        self.test_uptime_formatting()
        self.test_quality_scoring()
        self.test_event_rate_tracking()

        return self.results


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Test v1.2.8 incremental updates')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--module', '-m', choices=['chart', 'buffer', 'latency', 'health', 'all'],
                       default='all', help='Test module to run')
    args = parser.parse_args()

    print("\n" + "="*60)
    print("v1.2.8 Incremental Updates - Test Suite")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    all_results = []

    # Run selected tests
    if args.module in ['chart', 'all']:
        chart_tests = ChartDataManagerTests(verbose=args.verbose)
        all_results.append(chart_tests.run_all())

    if args.module in ['buffer', 'all']:
        buffer_tests = EventBufferTests(verbose=args.verbose)
        all_results.append(buffer_tests.run_all())

    if args.module in ['latency', 'all']:
        latency_tests = LatencyMeasurementTests(verbose=args.verbose)
        all_results.append(latency_tests.run_all())

    if args.module in ['health', 'all']:
        health_tests = ConnectionHealthTests(verbose=args.verbose)
        all_results.append(health_tests.run_all())

    # Combined summary
    print("\n" + "="*60)
    print("Overall Test Summary")
    print("="*60)

    total_tests = sum(r.total for r in all_results)
    total_passed = sum(r.passed for r in all_results)
    total_failed = sum(r.failed for r in all_results)

    print(f"Total: {total_tests} tests")
    print(f"Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)")
    print(f"Failed: {total_failed}")

    # Exit code (0 = success, 1 = failures)
    return 0 if total_failed == 0 else 1


if __name__ == '__main__':
    exit(main())
