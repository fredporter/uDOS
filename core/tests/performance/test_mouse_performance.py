#!/usr/bin/env python3
"""
Performance tests for MouseHandler with many clickable regions.

Tests mouse handler performance with 100+ regions to ensure:
- Fast region registration
- Quick click detection
- Efficient region lookup
- Responsive event processing
"""

import pytest
import time
from core.input.mouse_handler import (
    MouseHandler, ClickableRegion, MouseEvent, 
    MousePosition, MouseEventType, MouseButton
)


class TestMousePerformance:
    """Test MouseHandler performance with many regions."""
    
    @pytest.fixture
    def mouse_handler(self):
        """Create mouse handler for testing."""
        return MouseHandler()
    
    def test_register_100_regions_performance(self, mouse_handler):
        """Test registering 100 regions completes quickly (< 50ms)."""
        # Measure registration time
        start_time = time.perf_counter()
        for i in range(10):
            for j in range(10):
                region = ClickableRegion(
                    name=f'region_{i}_{j}',
                    x1=j * 10,
                    y1=i * 3,
                    x2=(j + 1) * 10 - 1,
                    y2=(i + 1) * 3 - 1,
                    callback=lambda e: None
                )
                mouse_handler.add_region(region)
        
        register_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert len(mouse_handler.regions) == 100
        assert register_time < 50, f"Registration took {register_time:.2f}ms (should be < 50ms)"
        print(f"\n✓ Registered 100 regions in {register_time:.2f}ms")
    
    def test_click_detection_100_regions_performance(self, mouse_handler):
        """Test click detection with 100 regions is fast (< 10ms per click)."""
        # Register 100 regions
        callback_count = {'count': 0}
        
        def test_callback(event):
            callback_count['count'] += 1
        
        for i in range(10):
            for j in range(10):
                region = ClickableRegion(
                    name=f'region_{i}_{j}',
                    x1=j * 10,
                    y1=i * 3,
                    x2=(j + 1) * 10 - 1,
                    y2=(i + 1) * 3 - 1,
                    callback=test_callback
                )
                mouse_handler.add_region(region)
        
        # Measure click detection times
        click_times = []
        for i in range(10):
            for j in range(10):
                pos = MousePosition(x=j * 10 + 5, y=i * 3 + 1)
                event = MouseEvent(
                    event_type=MouseEventType.CLICK,
                    button=MouseButton.LEFT,
                    position=pos,
                    timestamp=time.time()
                )
                
                start_time = time.perf_counter()
                mouse_handler.process_event(event)
                click_time = (time.perf_counter() - start_time) * 1000
                click_times.append(click_time)
        
        # Calculate statistics
        avg_click_time = sum(click_times) / len(click_times)
        max_click_time = max(click_times)
        
        # Assertions
        assert callback_count['count'] == 100
        assert avg_click_time < 10, f"Avg click time {avg_click_time:.2f}ms (should be < 10ms)"
        assert max_click_time < 50, f"Max click time {max_click_time:.2f}ms (should be < 50ms)"
        print(f"\n✓ Click detection: avg={avg_click_time:.4f}ms, max={max_click_time:.4f}ms")
    
    def test_hover_detection_100_regions_performance(self, mouse_handler):
        """Test hover/move detection with 100 regions is fast."""
        # Register 100 regions
        for i in range(10):
            for j in range(10):
                region = ClickableRegion(
                    name=f'region_{i}_{j}',
                    x1=j * 10,
                    y1=i * 3,
                    x2=(j + 1) * 10 - 1,
                    y2=(i + 1) * 3 - 1,
                    callback=lambda e: None
                )
                mouse_handler.add_region(region)
        
        # Measure hover detection times
        hover_times = []
        for i in range(10):
            for j in range(10):
                pos = MousePosition(x=j * 10 + 5, y=i * 3 + 1)
                event = MouseEvent(
                    event_type=MouseEventType.HOVER,
                    button=None,
                    position=pos,
                    timestamp=time.time()
                )
                
                start_time = time.perf_counter()
                mouse_handler.process_event(event)
                hover_time = (time.perf_counter() - start_time) * 1000
                hover_times.append(hover_time)
        
        # Calculate statistics
        avg_hover_time = sum(hover_times) / len(hover_times)
        max_hover_time = max(hover_times)
        
        # Assertions
        assert avg_hover_time < 10, f"Avg hover time {avg_hover_time:.2f}ms (should be < 10ms)"
        assert max_hover_time < 50, f"Max hover time {max_hover_time:.2f}ms (should be < 50ms)"
        print(f"\n✓ Hover detection: avg={avg_hover_time:.4f}ms, max={max_hover_time:.4f}ms")
    
    def test_region_lookup_performance(self, mouse_handler):
        """Test region lookup is fast even with many regions."""
        # Register 100 regions
        for i in range(10):
            for j in range(10):
                region = ClickableRegion(
                    name=f'region_{i}_{j}',
                    x1=j * 10,
                    y1=i * 3,
                    x2=(j + 1) * 10 - 1,
                    y2=(i + 1) * 3 - 1,
                    callback=lambda e: None
                )
                mouse_handler.add_region(region)
        
        # Measure region lookup times
        lookup_times = []
        for i in range(10):
            for j in range(10):
                pos = MousePosition(x=j * 10 + 5, y=i * 3 + 1)
                
                start_time = time.perf_counter()
                region = mouse_handler.find_region_at(pos)
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
                region = ClickableRegion(
                    name=f'region_{i}_{j}',
                    x1=j * 10,
                    y1=i * 3,
                    x2=(j + 1) * 10 - 1,
                    y2=(i + 1) * 3 - 1,
                    callback=lambda e: None
                )
                mouse_handler.add_region(region)
        
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
        region_names = []
        for i in range(10):
            for j in range(10):
                region_name = f'region_{i}_{j}'
                region_names.append(region_name)
                region = ClickableRegion(
                    name=region_name,
                    x1=j * 10,
                    y1=i * 3,
                    x2=(j + 1) * 10 - 1,
                    y2=(i + 1) * 3 - 1,
                    callback=lambda e: None
                )
                mouse_handler.add_region(region)
        
        # Measure unregister times
        unregister_times = []
        for region_name in region_names:
            start_time = time.perf_counter()
            mouse_handler.remove_region(region_name)
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
                region = ClickableRegion(
                    name=f'layer_{layer}_region_{i}',
                    x1=i * 5,
                    y1=layer * 2,
                    x2=(i + 2) * 5,
                    y2=(layer + 2) * 2,
                    callback=lambda e: None
                )
                mouse_handler.add_region(region)
        
        # Measure click detection with overlaps
        click_times = []
        for i in range(20):
            pos = MousePosition(x=i * 5 + 2, y=5)
            event = MouseEvent(
                event_type=MouseEventType.CLICK,
                button=MouseButton.LEFT,
                position=pos,
                timestamp=time.time()
            )
            
            start_time = time.perf_counter()
            mouse_handler.process_event(event)
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
                region = ClickableRegion(
                    name=f'region_{i}_{j}',
                    x1=j * 10,
                    y1=i * 2,
                    x2=(j + 1) * 10 - 1,
                    y2=(i + 1) * 2 - 1,
                    callback=lambda e: None
                )
                mouse_handler.add_region(region)
        
        # Measure operations
        start_time = time.perf_counter()
        
        # Test clicks across the grid (sample every 5th row)
        for i in range(0, 50, 5):
            for j in range(10):
                pos = MousePosition(x=j * 10 + 5, y=i * 2 + 1)
                event = MouseEvent(
                    event_type=MouseEventType.CLICK,
                    button=MouseButton.LEFT,
                    position=pos,
                    timestamp=time.time()
                )
                mouse_handler.process_event(event)
        
        total_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert len(mouse_handler.regions) == 500
        assert total_time < 500, f"Stress test took {total_time:.2f}ms (should be < 500ms)"
        print(f"\n✓ Stress test: 500 regions, 100 clicks in {total_time:.2f}ms")


class TestMouseEventPerformance:
    """Test mouse event processing performance."""
    
    def test_event_processing_overhead(self):
        """Test that event processing overhead is minimal."""
        handler = MouseHandler()
        
        # Register 50 regions
        for i in range(50):
            region = ClickableRegion(
                name=f'region_{i}',
                x1=i * 2,
                y1=i,
                x2=(i + 1) * 2,
                y2=i + 1,
                callback=lambda e: None
            )
            handler.add_region(region)
        
        # Measure rapid-fire clicks
        click_times = []
        for i in range(100):
            pos = MousePosition(x=i % 100, y=i % 50)
            event = MouseEvent(
                event_type=MouseEventType.CLICK,
                button=MouseButton.LEFT,
                position=pos,
                timestamp=time.time()
            )
            
            start_time = time.perf_counter()
            handler.process_event(event)
            click_time = (time.perf_counter() - start_time) * 1000
            click_times.append(click_time)
        
        # Calculate statistics
        avg_time = sum(click_times) / len(click_times)
        max_time = max(click_times)
        
        # Assertions
        assert avg_time < 5, f"Avg event processing {avg_time:.4f}ms (should be < 5ms)"
        assert max_time < 20, f"Max event processing {max_time:.4f}ms (should be < 20ms)"
        print(f"\n✓ Event processing: avg={avg_time:.4f}ms, max={max_time:.4f}ms")
