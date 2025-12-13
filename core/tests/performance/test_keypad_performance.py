#!/usr/bin/env python3
"""
Performance tests for KeypadHandler with rapid input.

Tests keypad handler performance with:
- Rapid key processing (1000+ keys/sec)
- Many registered callbacks
- Mode switching overhead
- Context updates
"""

import pytest
import time
from core.input.keypad_handler import KeypadHandler, KeypadMode


class TestKeypadPerformance:
    """Test KeypadHandler performance with rapid input."""
    
    @pytest.fixture
    def keypad_handler(self):
        """Create keypad handler for testing."""
        return KeypadHandler()
    
    def test_rapid_key_processing(self, keypad_handler):
        """Test processing 1000 rapid key presses (< 100ms)."""
        # Measure processing time for 1000 keys
        start_time = time.perf_counter()
        for i in range(1000):
            key = str(i % 10)
            keypad_handler.handle_key(key)
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert processing_time < 100, f"Processing took {processing_time:.2f}ms (should be < 100ms)"
        print(f"\n✓ Processed 1000 keys in {processing_time:.2f}ms ({1000/processing_time*1000:.0f} keys/sec)")
    
    def test_mode_switching_performance(self, keypad_handler):
        """Test mode switching is fast (< 1ms per switch)."""
        modes = [KeypadMode.NAVIGATION, KeypadMode.SELECTION, 
                 KeypadMode.EDITING, KeypadMode.MENU]
        
        # Measure mode switching time
        switch_times = []
        for _ in range(100):
            for mode in modes:
                start_time = time.perf_counter()
                keypad_handler.set_mode(mode)
                switch_time = (time.perf_counter() - start_time) * 1000
                switch_times.append(switch_time)
        
        # Calculate statistics
        avg_switch_time = sum(switch_times) / len(switch_times)
        
        # Assertions
        assert avg_switch_time < 1, f"Avg mode switch {avg_switch_time:.4f}ms (should be < 1ms)"
        print(f"\n✓ Mode switching: avg={avg_switch_time:.4f}ms")
    
    def test_callback_execution_performance(self, keypad_handler):
        """Test callbacks execute quickly."""
        callback_count = {'count': 0}
        
        def fast_callback():
            callback_count['count'] += 1
            return 'executed'
        
        # Register callbacks for all keys
        for i in range(10):
            keypad_handler.register_callback(str(i), fast_callback)
        
        # Measure callback execution times
        execution_times = []
        for _ in range(100):
            for i in range(10):
                start_time = time.perf_counter()
                keypad_handler.handle_key(str(i))
                execution_time = (time.perf_counter() - start_time) * 1000
                execution_times.append(execution_time)
        
        # Calculate statistics
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        # Assertions
        assert callback_count['count'] == 1000
        assert avg_execution_time < 5, f"Avg callback time {avg_execution_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Callback execution: avg={avg_execution_time:.4f}ms, {callback_count['count']} calls")
    
    def test_pagination_performance(self, keypad_handler):
        """Test pagination with many items is fast."""
        # Set up 1000 items for selection
        items = [f'item_{i}' for i in range(1000)]
        keypad_handler.set_mode(KeypadMode.SELECTION)
        keypad_handler.set_items(items)
        
        # Measure pagination operations
        page_times = []
        for _ in range(100):
            start_time = time.perf_counter()
            keypad_handler.handle_key('2')  # Down key
            page_time = (time.perf_counter() - start_time) * 1000
            page_times.append(page_time)
        
        # Calculate statistics
        avg_page_time = sum(page_times) / len(page_times)
        
        # Assertions
        assert avg_page_time < 5, f"Avg pagination {avg_page_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Pagination (1000 items): avg={avg_page_time:.4f}ms")
    
    def test_undo_redo_performance(self, keypad_handler):
        """Test undo/redo operations are fast."""
        # Perform operations that can be undone
        operations = []
        for i in range(50):
            keypad_handler.handle_key('5')  # Select operations
            operations.append(f'op_{i}')
        
        # Measure undo/redo times
        undo_times = []
        redo_times = []
        
        for _ in range(50):
            start_time = time.perf_counter()
            keypad_handler.handle_key('9')  # Undo
            undo_time = (time.perf_counter() - start_time) * 1000
            undo_times.append(undo_time)
        
        for _ in range(50):
            start_time = time.perf_counter()
            keypad_handler.handle_key('7')  # Redo
            redo_time = (time.perf_counter() - start_time) * 1000
            redo_times.append(redo_time)
        
        # Calculate statistics
        avg_undo_time = sum(undo_times) / len(undo_times)
        avg_redo_time = sum(redo_times) / len(redo_times)
        
        # Assertions
        assert avg_undo_time < 5, f"Avg undo {avg_undo_time:.4f}ms (should be < 5ms)"
        assert avg_redo_time < 5, f"Avg redo {avg_redo_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Undo/Redo: undo={avg_undo_time:.4f}ms, redo={avg_redo_time:.4f}ms")
    
    def test_help_display_performance(self, keypad_handler):
        """Test help display is fast."""
        # Register many callbacks with help text
        for i in range(10):
            keypad_handler.register_callback(str(i), lambda: None)
        
        # Measure help display times
        help_times = []
        for _ in range(100):
            start_time = time.perf_counter()
            keypad_handler.handle_key('0')  # Menu/help key
            help_time = (time.perf_counter() - start_time) * 1000
            help_times.append(help_time)
        
        # Calculate statistics
        avg_help_time = sum(help_times) / len(help_times)
        
        # Assertions
        assert avg_help_time < 10, f"Avg help display {avg_help_time:.4f}ms (should be < 10ms)"
        print(f"\n✓ Help display: avg={avg_help_time:.4f}ms")
    
    def test_unregister_performance(self, keypad_handler):
        """Test unregistering callbacks is fast."""
        # Register callbacks for all keys
        for i in range(10):
            keypad_handler.register_callback(str(i), lambda: None)
        
        # Measure unregister times (via clearing callbacks dict)
        start_time = time.perf_counter()
        keypad_handler.callbacks.clear()
        unregister_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert len(keypad_handler.callbacks) == 0
        assert unregister_time < 1, f"Unregister took {unregister_time:.4f}ms (should be < 1ms)"
        print(f"\n✓ Unregister all callbacks: {unregister_time:.4f}ms")
    
    def test_get_available_keys_performance(self, keypad_handler):
        """Test getting available keys is fast."""
        # Register some callbacks
        for i in [0, 2, 4, 6, 8]:
            keypad_handler.register_callback(str(i), lambda: None)
        
        # Measure key lookup times
        lookup_times = []
        for _ in range(1000):
            start_time = time.perf_counter()
            _ = list(keypad_handler.callbacks.keys())
            lookup_time = (time.perf_counter() - start_time) * 1000
            lookup_times.append(lookup_time)
        
        # Calculate statistics
        avg_lookup_time = sum(lookup_times) / len(lookup_times)
        
        # Assertions
        assert avg_lookup_time < 1, f"Avg key lookup {avg_lookup_time:.4f}ms (should be < 1ms)"
        print(f"\n✓ Key lookup: avg={avg_lookup_time:.4f}ms")
    
    def test_stress_test_rapid_input_sequence(self, keypad_handler):
        """Stress test with rapid random key sequence."""
        import random
        
        # Generate random key sequence
        sequence = [str(random.randint(0, 9)) for _ in range(10000)]
        
        # Register some callbacks
        for i in range(10):
            keypad_handler.register_callback(str(i), lambda: f'result_{i}')
        
        # Measure processing time for entire sequence
        start_time = time.perf_counter()
        for key in sequence:
            keypad_handler.handle_key(key)
        
        total_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        keys_per_sec = len(sequence) / (total_time / 1000)
        assert total_time < 1000, f"Stress test took {total_time:.2f}ms (should be < 1000ms)"
        print(f"\n✓ Stress test: 10000 keys in {total_time:.2f}ms ({keys_per_sec:.0f} keys/sec)")


class TestKeypadMemoryPerformance:
    """Test memory efficiency of KeypadHandler."""
    
    def test_memory_efficiency_many_callbacks(self):
        """Test memory usage with many registered callbacks."""
        import sys
        
        handler = KeypadHandler()
        
        # Register many callbacks
        for i in range(10):
            handler.register_callback(str(i), lambda: None)
        
        # Measure memory
        handler_size = sys.getsizeof(handler.__dict__)
        
        # Memory should be reasonable (< 100KB)
        assert handler_size < 100_000, f"Handler memory {handler_size} bytes (should be < 100KB)"
        print(f"\n✓ Memory usage: {handler_size:,} bytes with 10 callbacks")
