#!/usr/bin/env python3
"""
Performance tests for KeypadHandler with rapid input.

Tests keypad handler performance with fast key sequences to ensure:
- Fast key processing
- Efficient mode switching
- Quick pagination
- Responsive command execution
"""

import pytest
import time
from unittest.mock import Mock, patch
from core.input.keypad_handler import KeypadHandler
from core.services.device_manager import DeviceManager


class TestKeypadPerformance:
    """Test KeypadHandler performance with rapid input."""
    
    @pytest.fixture
    def mock_device_manager(self):
        """Create mock device manager."""
        dm = Mock(spec=DeviceManager)
        dm.get_input_mode.return_value = 'keypad'
        return dm
    
    @pytest.fixture
    def keypad_handler(self, mock_device_manager):
        """Create keypad handler with mock device manager."""
        return KeypadHandler(device_manager=mock_device_manager)
    
    def test_rapid_key_processing(self, keypad_handler):
        """Test processing 1000 rapid key presses (< 100ms)."""
        # Process 1000 key presses
        start_time = time.perf_counter()
        for i in range(1000):
            key = str((i % 9) + 1)  # Keys 1-9
            keypad_handler.handle_key(key)
        process_time = (time.perf_counter() - start_time) * 1000
        
        # Calculate average per key
        avg_time = process_time / 1000
        
        # Assertions
        assert process_time < 100, f"Processing 1000 keys took {process_time:.2f}ms (should be < 100ms)"
        assert avg_time < 0.1, f"Avg key time {avg_time:.4f}ms (should be < 0.1ms)"
        print(f"\n✓ Processed 1000 keys in {process_time:.2f}ms (avg={avg_time:.4f}ms)")
    
    def test_mode_switching_performance(self, keypad_handler):
        """Test rapid mode switching is fast (< 1ms per switch)."""
        modes = ['keypad', 'full_keyboard', 'hybrid']
        
        # Measure mode switching times
        switch_times = []
        for _ in range(100):
            for mode in modes:
                start_time = time.perf_counter()
                keypad_handler.set_mode(mode)
                switch_time = (time.perf_counter() - start_time) * 1000
                switch_times.append(switch_time)
        
        # Calculate statistics
        avg_switch_time = sum(switch_times) / len(switch_times)
        max_switch_time = max(switch_times)
        
        # Assertions
        assert avg_switch_time < 1, f"Avg switch time {avg_switch_time:.4f}ms (should be < 1ms)"
        assert max_switch_time < 5, f"Max switch time {max_switch_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Mode switching: avg={avg_switch_time:.4f}ms, max={max_switch_time:.4f}ms")
    
    def test_callback_execution_performance(self, keypad_handler):
        """Test callback execution overhead is minimal."""
        callback_count = 0
        
        def test_callback():
            nonlocal callback_count
            callback_count += 1
        
        # Register callbacks for keys 1-9
        for i in range(1, 10):
            keypad_handler.register_key(str(i), test_callback)
        
        # Measure execution times
        exec_times = []
        for _ in range(100):
            for i in range(1, 10):
                start_time = time.perf_counter()
                keypad_handler.handle_key(str(i))
                exec_time = (time.perf_counter() - start_time) * 1000
                exec_times.append(exec_time)
        
        # Calculate statistics
        avg_exec_time = sum(exec_times) / len(exec_times)
        
        # Assertions
        assert callback_count == 900
        assert avg_exec_time < 1, f"Avg callback time {avg_exec_time:.4f}ms (should be < 1ms)"
        print(f"\n✓ Callback execution: avg={avg_exec_time:.4f}ms (900 callbacks)")
    
    def test_pagination_performance(self, keypad_handler):
        """Test pagination commands are instant (< 1ms)."""
        # Register pagination callback
        pagination_count = 0
        
        def pagination_callback():
            nonlocal pagination_count
            pagination_count += 1
        
        keypad_handler.register_key('0', pagination_callback)
        
        # Measure pagination times
        pagination_times = []
        for _ in range(100):
            start_time = time.perf_counter()
            keypad_handler.handle_key('0')
            pagination_time = (time.perf_counter() - start_time) * 1000
            pagination_times.append(pagination_time)
        
        # Calculate average
        avg_pagination_time = sum(pagination_times) / len(pagination_times)
        
        # Assertions
        assert pagination_count == 100
        assert avg_pagination_time < 1, f"Avg pagination {avg_pagination_time:.4f}ms (should be < 1ms)"
        print(f"\n✓ Pagination: avg={avg_pagination_time:.4f}ms")
    
    def test_undo_redo_performance(self, keypad_handler):
        """Test undo/redo operations are fast (< 2ms)."""
        undo_count = 0
        redo_count = 0
        
        def undo_callback():
            nonlocal undo_count
            undo_count += 1
        
        def redo_callback():
            nonlocal redo_count
            redo_count += 1
        
        keypad_handler.register_key('7', undo_callback)
        keypad_handler.register_key('9', redo_callback)
        
        # Measure undo/redo times
        undo_times = []
        redo_times = []
        
        for _ in range(100):
            start_time = time.perf_counter()
            keypad_handler.handle_key('7')
            undo_times.append((time.perf_counter() - start_time) * 1000)
            
            start_time = time.perf_counter()
            keypad_handler.handle_key('9')
            redo_times.append((time.perf_counter() - start_time) * 1000)
        
        # Calculate averages
        avg_undo_time = sum(undo_times) / len(undo_times)
        avg_redo_time = sum(redo_times) / len(redo_times)
        
        # Assertions
        assert undo_count == 100
        assert redo_count == 100
        assert avg_undo_time < 2, f"Avg undo {avg_undo_time:.4f}ms (should be < 2ms)"
        assert avg_redo_time < 2, f"Avg redo {avg_redo_time:.4f}ms (should be < 2ms)"
        print(f"\n✓ Undo: avg={avg_undo_time:.4f}ms, Redo: avg={avg_redo_time:.4f}ms")
    
    def test_help_display_performance(self, keypad_handler):
        """Test help display is fast (< 5ms)."""
        # Register help callback
        help_count = 0
        
        def help_callback():
            nonlocal help_count
            help_count += 1
        
        keypad_handler.register_key('*', help_callback)
        
        # Measure help display times
        help_times = []
        for _ in range(50):
            start_time = time.perf_counter()
            keypad_handler.handle_key('*')
            help_time = (time.perf_counter() - start_time) * 1000
            help_times.append(help_time)
        
        # Calculate average
        avg_help_time = sum(help_times) / len(help_times)
        
        # Assertions
        assert help_count == 50
        assert avg_help_time < 5, f"Avg help display {avg_help_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Help display: avg={avg_help_time:.4f}ms")
    
    def test_unregister_performance(self, keypad_handler):
        """Test unregistering keys is instant (< 1ms)."""
        # Register all keys
        for i in range(1, 10):
            keypad_handler.register_key(str(i), lambda: None)
        
        # Measure unregister times
        unregister_times = []
        for i in range(1, 10):
            start_time = time.perf_counter()
            keypad_handler.unregister_key(str(i))
            unregister_time = (time.perf_counter() - start_time) * 1000
            unregister_times.append(unregister_time)
        
        # Calculate average
        avg_unregister_time = sum(unregister_times) / len(unregister_times)
        
        # Assertions
        assert avg_unregister_time < 1, f"Avg unregister {avg_unregister_time:.4f}ms (should be < 1ms)"
        print(f"\n✓ Unregister: avg={avg_unregister_time:.4f}ms")
    
    def test_get_available_keys_performance(self, keypad_handler):
        """Test getting available keys is fast (< 1ms)."""
        # Register some keys
        for i in range(1, 10):
            keypad_handler.register_key(str(i), lambda: None)
        
        # Measure get_available_keys times
        get_times = []
        for _ in range(100):
            start_time = time.perf_counter()
            keys = keypad_handler.get_available_keys()
            get_time = (time.perf_counter() - start_time) * 1000
            get_times.append(get_time)
            assert len(keys) == 9
        
        # Calculate average
        avg_get_time = sum(get_times) / len(get_times)
        
        # Assertions
        assert avg_get_time < 1, f"Avg get keys {avg_get_time:.4f}ms (should be < 1ms)"
        print(f"\n✓ Get available keys: avg={avg_get_time:.4f}ms")
    
    def test_stress_test_rapid_input_sequence(self, keypad_handler):
        """Stress test with rapid input sequence."""
        # Register callbacks for all navigation keys
        callback_count = 0
        
        def callback():
            nonlocal callback_count
            callback_count += 1
        
        for key in ['2', '4', '5', '6', '8', '0', '7', '9']:
            keypad_handler.register_key(key, callback)
        
        # Simulate rapid navigation sequence (1000 keys)
        keys = ['8', '8', '8', '5', '2', '2', '4', '6', '0'] * 111
        
        start_time = time.perf_counter()
        for key in keys[:1000]:
            keypad_handler.handle_key(key)
        total_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert callback_count == 1000
        assert total_time < 200, f"Stress test took {total_time:.2f}ms (should be < 200ms)"
        print(f"\n✓ Stress test: 1000 rapid keys in {total_time:.2f}ms")


class TestKeypadMemoryPerformance:
    """Test keypad handler memory efficiency."""
    
    def test_memory_efficiency_many_callbacks(self):
        """Test memory usage with many registered callbacks."""
        import sys
        from unittest.mock import Mock
        
        dm = Mock(spec=DeviceManager)
        dm.get_input_mode.return_value = 'keypad'
        handler = KeypadHandler(device_manager=dm)
        
        # Register many callbacks
        for i in range(100):
            handler.register_key(f'key_{i}', lambda: None)
        
        # Measure memory
        handler_size = sys.getsizeof(handler.__dict__)
        
        # Memory should be reasonable (< 100KB)
        assert handler_size < 100_000, f"Handler memory {handler_size} bytes (should be < 100KB)"
        print(f"\n✓ Memory usage: {handler_size:,} bytes with 100 callbacks")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
