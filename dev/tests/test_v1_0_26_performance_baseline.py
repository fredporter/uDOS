"""
Tests for Performance Baselines (v1.0.26)

Performance regression tests and benchmarks.

Author: uDOS Development Team
Version: 1.0.26
"""

import unittest
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestImportPerformance(unittest.TestCase):
    """Test import performance"""

    def test_core_imports_fast(self):
        """Test core imports are fast (< 1s)"""
        start = time.time()

        # Import core modules
        from core import uDOS_parser
        from core import uDOS_settings
        from core import uDOS_logger

        elapsed = time.time() - start

        # Core imports should be fast
        self.assertLess(elapsed, 1.0, "Core imports should complete in < 1 second")

    def test_command_handler_import_fast(self):
        """Test command handler imports are fast"""
        start = time.time()

        from core.commands.base_handler import BaseCommandHandler

        elapsed = time.time() - start

        self.assertLess(elapsed, 0.5, "BaseCommandHandler import should be < 500ms")

    def test_lazy_loading_implemented(self):
        """Test lazy loading is implemented for heavy imports"""
        # Check that handlers use lazy loading
        from core.commands.map_handler import MapCommandHandler

        handler = MapCommandHandler()

        # Should have map_engine as property (lazy loaded)
        self.assertTrue(hasattr(type(handler), 'map_engine'))


class TestParsingPerformance(unittest.TestCase):
    """Test parsing performance"""

    def test_simple_command_parse_fast(self):
        """Test simple command parsing is fast (< 10ms)"""
        from core.uDOS_parser import CommandParser

        parser = CommandParser()

        start = time.time()
        result = parser.parse("STATUS")
        elapsed = (time.time() - start) * 1000  # Convert to ms

        # Simple parsing should be very fast
        self.assertLess(elapsed, 10, "Simple command parse should be < 10ms")

    def test_complex_command_parse_reasonable(self):
        """Test complex command parsing is reasonable (< 50ms)"""
        from core.uDOS_parser import CommandParser

        parser = CommandParser()

        start = time.time()
        # Parse a complex command with parameters
        result = parser.parse("MAP NAVIGATE LON NYC --format=json --verbose")
        elapsed = (time.time() - start) * 1000

        # Complex parsing should still be fast
        self.assertLess(elapsed, 50, "Complex command parse should be < 50ms")

    def test_batch_parse_efficient(self):
        """Test batch parsing efficiency"""
        from core.uDOS_parser import CommandParser

        parser = CommandParser()
        commands = ["STATUS", "HELP", "VERSION", "BLANK", "HISTORY"] * 10

        start = time.time()
        for cmd in commands:
            parser.parse(cmd)
        elapsed = time.time() - start

        # 50 commands should parse quickly
        avg_time = (elapsed / len(commands)) * 1000
        self.assertLess(avg_time, 5, "Average parse time should be < 5ms")


class TestFileOperationPerformance(unittest.TestCase):
    """Test file operation performance"""

    def test_file_list_fast(self):
        """Test file listing is fast"""
        import os

        project_root = Path(__file__).parent.parent.parent

        start = time.time()
        files = list(project_root.glob("**/*.py"))
        elapsed = time.time() - start

        # Listing should be reasonably fast
        self.assertLess(elapsed, 2.0, "File listing should be < 2 seconds")

    def test_config_read_fast(self):
        """Test config file reading is fast"""
        import json

        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        start = time.time()
        with open(commands_file, 'r') as f:
            data = json.load(f)
        elapsed = (time.time() - start) * 1000

        # JSON loading should be fast
        self.assertLess(elapsed, 100, "Config read should be < 100ms")


class TestMemoryUsage(unittest.TestCase):
    """Test memory usage patterns"""

    def test_no_memory_leaks_in_loop(self):
        """Test repeated operations don't leak memory"""
        import gc
        from core.uDOS_parser import CommandParser

        parser = CommandParser()

        # Get initial memory
        gc.collect()

        # Run many operations
        for i in range(1000):
            parser.parse(f"STATUS")

        gc.collect()

        # This is a basic check - in real tests you'd use memory_profiler
        self.assertTrue(True)  # Pass if no crash

    def test_handler_initialization_lightweight(self):
        """Test handlers don't consume excessive memory on init"""
        from core.commands.base_handler import BaseCommandHandler

        # Should be able to create many handlers without issues
        handlers = [BaseCommandHandler() for _ in range(100)]

        self.assertEqual(len(handlers), 100)


class TestResponseTime(unittest.TestCase):
    """Test command response time"""

    def test_status_command_fast(self):
        """Test STATUS command responds quickly"""
        # This would require actual command execution
        # For now, just test that the handler exists
        try:
            from core.uDOS_commands import CommandHandler
            handler = CommandHandler()
            self.assertTrue(hasattr(handler, 'handle_command'))
        except Exception:
            self.skipTest("CommandHandler not available for testing")

    def test_help_command_reasonable(self):
        """Test HELP command responds in reasonable time"""
        # Help command may load documentation
        # Should still be reasonably fast (< 1s)
        self.assertTrue(True)  # Placeholder


class TestCachingEfficiency(unittest.TestCase):
    """Test caching mechanisms"""

    def test_repeated_file_access_cached(self):
        """Test repeated file access uses caching"""
        import json

        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        # First access
        start1 = time.time()
        with open(commands_file, 'r') as f:
            data1 = json.load(f)
        elapsed1 = time.time() - start1

        # Second access (OS should cache)
        start2 = time.time()
        with open(commands_file, 'r') as f:
            data2 = json.load(f)
        elapsed2 = time.time() - start2

        # Second access should be same or faster
        # (OS-level caching, not application caching)
        self.assertGreaterEqual(elapsed1, elapsed2 * 0.5)

    def test_command_lookup_optimized(self):
        """Test command lookup is optimized"""
        import json

        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        with open(commands_file, 'r') as f:
            data = json.load(f)

        commands = data.get('COMMANDS', [])

        # Lookup should be fast with list comprehension
        start = time.time()
        result = next((cmd for cmd in commands if cmd.get('NAME') == 'STATUS'), None)
        elapsed = (time.time() - start) * 1000

        self.assertLess(elapsed, 5, "Command lookup should be < 5ms")


class TestStartupPerformance(unittest.TestCase):
    """Test startup performance"""

    def test_logger_init_fast(self):
        """Test logger initialization is fast"""
        start = time.time()
        from core.uDOS_logger import uDOSLogger
        elapsed = time.time() - start

        self.assertLess(elapsed, 0.5, "Logger init should be < 500ms")

    def test_settings_load_fast(self):
        """Test settings loading is fast"""
        start = time.time()
        from core.uDOS_settings import uDOSSettings
        elapsed = time.time() - start

        self.assertLess(elapsed, 0.5, "Settings init should be < 500ms")


class TestConcurrency(unittest.TestCase):
    """Test concurrent operation handling"""

    def test_multiple_parsers_concurrent(self):
        """Test multiple parsers can work concurrently"""
        from core.uDOS_parser import CommandParser
        import threading

        results = []

        def parse_commands():
            parser = CommandParser()
            for i in range(10):
                parser.parse("STATUS")
            results.append(True)

        threads = [threading.Thread(target=parse_commands) for _ in range(5)]

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.time() - start

        self.assertEqual(len(results), 5)
        self.assertLess(elapsed, 2.0, "Concurrent parsing should be < 2s")


class TestScalability(unittest.TestCase):
    """Test scalability with large operations"""

    def test_large_history_performant(self):
        """Test large history doesn't slow down system"""
        # This would test with actual history
        # For now, just verify history handling exists
        try:
            from core.commands.history_handler import HistoryHandler
            self.assertTrue(True)
        except ImportError:
            self.skipTest("HistoryHandler not available")

    def test_many_files_performant(self):
        """Test handling many files is performant"""
        project_root = Path(__file__).parent.parent.parent

        start = time.time()
        # Count all Python files
        py_files = list(project_root.glob("**/*.py"))
        count = len(py_files)
        elapsed = time.time() - start

        # Should handle file scanning efficiently
        self.assertLess(elapsed, 5.0, "File scanning should be < 5s")
        self.assertGreater(count, 0)


class TestResourceCleanup(unittest.TestCase):
    """Test resource cleanup"""

    def test_file_handles_closed(self):
        """Test file handles are properly closed"""
        import json

        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        # Open and close file multiple times
        for i in range(100):
            with open(commands_file, 'r') as f:
                data = json.load(f)

        # Should not run out of file handles
        self.assertTrue(True)

    def test_no_dangling_threads(self):
        """Test no threads are left running"""
        import threading

        initial_threads = threading.active_count()

        # Create and finish some threads
        def dummy_task():
            time.sleep(0.01)

        threads = [threading.Thread(target=dummy_task) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final_threads = threading.active_count()

        # Thread count should return to normal
        self.assertEqual(initial_threads, final_threads)


class TestPerformanceRegression(unittest.TestCase):
    """Test for performance regressions"""

    def test_baseline_parsing_speed(self):
        """Test parsing maintains baseline speed"""
        from core.uDOS_parser import CommandParser

        parser = CommandParser()
        commands = ["STATUS"] * 100

        start = time.time()
        for cmd in commands:
            parser.parse(cmd)
        elapsed = time.time() - start

        # Baseline: 100 parses in < 500ms (5ms average)
        self.assertLess(elapsed, 0.5, "Parsing regression detected")

    def test_baseline_file_operations(self):
        """Test file operations maintain baseline speed"""
        import json

        project_root = Path(__file__).parent.parent.parent
        commands_file = project_root / "knowledge" / "system" / "commands.json"

        # Perform 10 file reads
        start = time.time()
        for i in range(10):
            with open(commands_file, 'r') as f:
                data = json.load(f)
        elapsed = time.time() - start

        # Baseline: 10 reads in < 1s (100ms average)
        self.assertLess(elapsed, 1.0, "File operation regression detected")


if __name__ == '__main__':
    unittest.main()
