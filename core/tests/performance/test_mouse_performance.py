#!/usr/bin/env python3
"""
Performance tests for MouseHandler with many clickable regions.

Tests mouse handler performance with 100+ regions to ensure:
- Fast region registration
- Quick click detection
- Efficient region lookup
- Responsive hover detection
"""

import pytest
import time
from unittest.mock import Mock, patch
from core.input.mouse_handler import MouseHandler
from core.services.device_manager import DeviceManager


class TestMousePerformance:
    """Test MouseHandler performance with many regions."""
    
    @pytest.fixture
    def mock_device_manager(self):
        """Create mock device manager."""
        dm = Mock(spec=DeviceManager)
        dm.has_mouse.return_value = True
        dm.is_mouse_enabled.return_value = True
        return dm
    
    @pytest.fixture
    def mouse_handler(self, mock_device_manager):
        """Create mouse handler with mock device manager."""
        return MouseHandler(device_manager=mock_device_manager)
    
    def test_register_100_regions_performance(self, mouse_handler):
        """Test registering 100 regions completes quickly (< 50ms)."""
        # Generate 100 regions (10x10 grid)
        regions = []
        for i in range(10):
            for j in range(10):
                regions.append({
                    'id': f'region_{i}_{j}',
                    'x1': j * 10,
                    'y1': i * 3,
                    'x2': (j + 1) * 10 - 1,
                    'y2': (i + 1) * 3 - 1,
                    'callback': lambda: None
                })
        
        # Measure registration time
        start_time = time.perf_counter()
        for region in regions:
            mouse_handler.register_region(
                region['id'],
                region['x1'],
                region['y1'],
                region['x2'],
                region['y2'],
                region['callback']
            )
        register_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert len(mouse_handler.regions) == 100
        assert register_time < 50, f"Registration took {register_time:.2f}ms (should be < 50ms)"
        print(f"\n✓ Registered 100 regions in {register_time:.2f}ms")
    
    def test_click_detection_100_regions_performance(self, mouse_handler):
        """Test click detection with 100 regions is fast (< 10ms)."""
        # Register 100 regions
        callback_count = 0
        
        def test_callback():
            nonlocal callback_count
            callback_count += 1
        
        for i in range(10):
            for j in range(10):
                mouse_handler.register_region(
                    f'region_{i}_{j}',
                    j * 10, i * 3,
                    (j + 1) * 10 - 1, (i + 1) * 3 - 1,
                    test_callback
                )
        
        # Measure click detection times
        click_times = []
        for i in range(10):
            for j in range(10):
                x = j * 10 + 5  # Center of region
                y = i * 3 + 1
                
                start_time = time.perf_counter()
                mouse_handler.handle_click(x, y)
                click_time = (time.perf_counter() - start_time) * 1000
                click_times.append(click_time)
        
        # Calculate statistics
        avg_click_time = sum(click_times) / len(click_times)
        max_click_time = max(click_times)
        
        # Assertions
        assert callback_count == 100
        assert avg_click_time < 10, f"Avg click time {avg_click_time:.2f}ms (should be < 10ms)"
        assert max_click_time < 50, f"Max click time {max_click_time:.2f}ms (should be < 50ms)"
        print(f"\n✓ Click detection: avg={avg_click_time:.4f}ms, max={max_click_time:.4f}ms")
    
    def test_hover_detection_100_regions_performance(self, mouse_handler):
        """Test hover detection with 100 regions is fast (< 10ms)."""
        # Register 100 regions with hover callbacks
        hover_count = 0
        
        def hover_callback():
            nonlocal hover_count
            hover_count += 1
        
        for i in range(10):
            for j in range(10):
                mouse_handler.register_region(
                    f'region_{i}_{j}',
                    j * 10, i * 3,
                    (j + 1) * 10 - 1, (i + 1) * 3 - 1,
                    lambda: None,
                    hover_callback=hover_callback
                )
        
        # Measure hover detection times
        hover_times = []
        for i in range(10):
            for j in range(10):
                x = j * 10 + 5
                y = i * 3 + 1
                
                start_time = time.perf_counter()
                mouse_handler.handle_hover(x, y)
                hover_time = (time.perf_counter() - start_time) * 1000
                hover_times.append(hover_time)
        
        # Calculate statistics
        avg_hover_time = sum(hover_times) / len(hover_times)
        max_hover_time = max(hover_times)
        
        # Assertions
        assert hover_count == 100
        assert avg_hover_time < 10, f"Avg hover time {avg_hover_time:.2f}ms (should be < 10ms)"
        assert max_hover_time < 50, f"Max hover time {max_hover_time:.2f}ms (should be < 50ms)"
        print(f"\n✓ Hover detection: avg={avg_hover_time:.4f}ms, max={max_hover_time:.4f}ms")
    
    def test_region_lookup_performance(self, mouse_handler):
        """Test region lookup is fast even with many regions."""
        # Register 100 regions
        for i in range(10):
            for j in range(10):
                mouse_handler.register_region(
                    f'region_{i}_{j}',
                    j * 10, i * 3,
                    (j + 1) * 10 - 1, (i + 1) * 3 - 1,
                    lambda: None
                )
        
        # Measure region lookup times (direct method call)
        lookup_times = []
        for i in range(10):
            for j in range(10):
                x = j * 10 + 5
                y = i * 3 + 1
                
                start_time = time.perf_counter()
                region = mouse_handler.get_region_at(x, y)
                lookup_time = (time.perf_counter() - start_time) * 1000
                lookup_times.append(lookup_time)
                assert region is not None
        
        # Calculate statistics
        avg_lookup_time = sum(lookup_times) / len(lookup_times)
        
        # Assertions
        assert avg_lookup_time < 5, f"Avg lookup time {avg_lookup_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Region lookup: avg={avg_lookup_time:.4f}ms")
    
    def test_clear_regions_performance(self, mouse_handler):
        """Test clearing many regions is fast (< 10ms)."""
        # Register 100 regions
        for i in range(10):
            for j in range(10):
                mouse_handler.register_region(
                    f'region_{i}_{j}',
                    j * 10, i * 3,
                    (j + 1) * 10 - 1, (i + 1) * 3 - 1,
                    lambda: None
                )
        
        # Measure clear time
        start_time = time.perf_counter()
        mouse_handler.clear_regions()
        clear_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert len(mouse_handler.regions) == 0
        assert clear_time < 10, f"Clear took {clear_time:.2f}ms (should be < 10ms)"
        print(f"\n✓ Clear 100 regions in {clear_time:.4f}ms")
    
    def test_unregister_performance(self, mouse_handler):
        """Test unregistering individual regions is fast."""
        # Register 100 regions
        region_ids = []
        for i in range(10):
            for j in range(10):
                region_id = f'region_{i}_{j}'
                region_ids.append(region_id)
                mouse_handler.register_region(
                    region_id,
                    j * 10, i * 3,
                    (j + 1) * 10 - 1, (i + 1) * 3 - 1,
                    lambda: None
                )
        
        # Measure unregister times
        unregister_times = []
        for region_id in region_ids:
            start_time = time.perf_counter()
            mouse_handler.unregister_region(region_id)
            unregister_time = (time.perf_counter() - start_time) * 1000
            unregister_times.append(unregister_time)
        
        # Calculate statistics
        avg_unregister_time = sum(unregister_times) / len(unregister_times)
        
        # Assertions
        assert len(mouse_handler.regions) == 0
        assert avg_unregister_time < 5, f"Avg unregister {avg_unregister_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Unregister: avg={avg_unregister_time:.4f}ms")
    
    def test_overlapping_regions_performance(self, mouse_handler):
        """Test performance with overlapping regions."""
        # Register overlapping regions (5 layers of 20 regions each)
        for layer in range(5):
            for i in range(20):
                mouse_handler.register_region(
                    f'layer_{layer}_region_{i}',
                    i * 5, layer * 2,
                    (i + 2) * 5, (layer + 2) * 2,
                    lambda: None
                )
        
        # Measure click detection with overlaps
        click_times = []
        for i in range(20):
            x = i * 5 + 2
            y = 5
            
            start_time = time.perf_counter()
            mouse_handler.handle_click(x, y)
            click_time = (time.perf_counter() - start_time) * 1000
            click_times.append(click_time)
        
        # Calculate statistics
        avg_click_time = sum(click_times) / len(click_times)
        
        # Assertions (slightly higher threshold for overlapping regions)
        assert avg_click_time < 20, f"Avg click time {avg_click_time:.2f}ms (should be < 20ms)"
        print(f"\n✓ Overlapping regions click: avg={avg_click_time:.4f}ms")
    
    def test_stress_test_500_regions(self, mouse_handler):
        """Stress test with 500 regions."""
        # Register 500 regions (50x10 grid)
        for i in range(50):
            for j in range(10):
                mouse_handler.register_region(
                    f'region_{i}_{j}',
                    j * 10, i * 2,
                    (j + 1) * 10 - 1, (i + 1) * 2 - 1,
                    lambda: None
                )
        
        # Measure operations
        start_time = time.perf_counter()
        
        # Test clicks across the grid
        for i in range(0, 50, 5):  # Sample every 5th row
            for j in range(10):
                x = j * 10 + 5
                y = i * 2 + 1
                mouse_handler.handle_click(x, y)
        
        total_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert len(mouse_handler.regions) == 500
        assert total_time < 500, f"Stress test took {total_time:.2f}ms (should be < 500ms)"
        print(f"\n✓ Stress test: 500 regions, 100 clicks in {total_time:.2f}ms")


class TestMouseEventPerformance:
    """Test mouse event processing performance."""
    
    @pytest.fixture
    def mock_device_manager(self):
        """Create mock device manager."""
        dm = Mock(spec=DeviceManager)
        dm.has_mouse.return_value = True
        dm.is_mouse_enabled.return_value = True
        return dm
    
    def test_event_processing_overhead(self, mock_device_manager):
        """Test that event processing overhead is minimal."""
        handler = MouseHandler(device_manager=mock_device_manager)
        
        # Register 50 regions
        for i in range(50):
            handler.register_region(
                f'region_{i}',
                i * 2, i,
                (i + 1) * 2, i + 1,
                lambda: None
            )
        
        # Measure rapid-fire clicks
        start_time = time.perf_counter()
        for _ in range(100):
            handler.handle_click(25, 25)
        total_time = (time.perf_counter() - start_time) * 1000
        
        avg_time = total_time / 100
        
        # Assertions
        assert avg_time < 10, f"Avg event time {avg_time:.4f}ms (should be < 10ms)"
        print(f"\n✓ Event processing: {avg_time:.4f}ms per event (100 events)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
