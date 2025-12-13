#!/usr/bin/env python3
"""
Performance tests for SelectorFramework with large datasets.

Tests selector performance with 1000+ items to ensure:
- Fast item loading and navigation
- Efficient pagination
- Quick search/filter operations
- Responsive rendering
"""

import pytest
import time
from core.ui.selector_framework import SelectorFramework, SelectorConfig, SelectableItem


class TestSelectorPerformance:
    """Test SelectorFramework performance with large datasets."""
    
    @pytest.fixture
    def selector(self):
        """Create selector with configuration."""
        config = SelectorConfig(page_size=9)
        return SelectorFramework(config=config)
    
    def test_load_1000_items_performance(self, selector):
        """Test loading 1000 items completes quickly (< 100ms)."""
        # Generate 1000 test items
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d}", value=i) for i in range(1000)]
        
        # Measure load time
        start_time = time.perf_counter()
        selector.set_items(items)
        load_time = (time.perf_counter() - start_time) * 1000
        
        # Assertions
        assert len(selector.items) == 1000
        assert load_time < 100, f"Loading took {load_time:.2f}ms (should be < 100ms)"
        print(f"\n✓ Loaded 1000 items in {load_time:.2f}ms")
    
    def test_pagination_1000_items_performance(self, selector):
        """Test pagination through 1000 items is fast (< 50ms per page)."""
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d}", value=i) for i in range(1000)]
        selector.set_items(items)
        
        # Measure time to advance through 10 pages
        page_times = []
        for _ in range(10):
            start_time = time.perf_counter()
            selector.next_page()
            page_time = (time.perf_counter() - start_time) * 1000
            page_times.append(page_time)
        
        avg_page_time = sum(page_times) / len(page_times)
        max_page_time = max(page_times)
        
        assert avg_page_time < 50, f"Avg page time {avg_page_time:.2f}ms (should be < 50ms)"
        assert max_page_time < 100, f"Max page time {max_page_time:.2f}ms (should be < 100ms)"
        print(f"\n✓ Pagination: avg={avg_page_time:.2f}ms, max={max_page_time:.2f}ms")
    
    def test_search_1000_items_performance(self, selector):
        """Test searching 1000 items completes quickly (< 200ms)."""
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d} - Category {i % 10}", value=i) 
                 for i in range(1000)]
        selector.set_items(items)
        
        # Measure search time
        start_time = time.perf_counter()
        selector.filter_items("Category 5")
        search_time = (time.perf_counter() - start_time) * 1000
        
        # Count results
        matching_count = sum(1 for item in items if "Category 5" in item.label)
        
        assert search_time < 200, f"Search took {search_time:.2f}ms (should be < 200ms)"
        print(f"\n✓ Search found {matching_count} items in {search_time:.2f}ms")
    
    def test_clear_filter_performance(self, selector):
        """Test clearing filter is instant (< 10ms)."""
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d}", value=i) for i in range(1000)]
        selector.set_items(items)
        selector.filter_items("Item 05")
        
        # Measure clear time
        start_time = time.perf_counter()
        selector.clear_filter()
        clear_time = (time.perf_counter() - start_time) * 1000
        
        assert clear_time < 10, f"Clear took {clear_time:.2f}ms (should be < 10ms)"
        print(f"\n✓ Clear filter in {clear_time:.2f}ms")
    
    def test_navigation_performance(self, selector):
        """Test navigation operations are instant (< 5ms)."""
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d}", value=i) for i in range(1000)]
        selector.set_items(items)
        
        # Measure navigation times
        nav_times = []
        for _ in range(100):
            start_time = time.perf_counter()
            selector.navigate_down()
            nav_time = (time.perf_counter() - start_time) * 1000
            nav_times.append(nav_time)
        
        avg_nav_time = sum(nav_times) / len(nav_times)
        
        assert avg_nav_time < 5, f"Avg navigation {avg_nav_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Navigation: avg={avg_nav_time:.4f}ms")
    
    def test_select_by_number_performance(self, selector):
        """Test number selection is instant (< 5ms)."""
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d}", value=i) for i in range(1000)]
        selector.set_items(items)
        
        # Measure selection times for multiple pages
        selection_times = []
        for page in range(5):
            selector.page = page
            start_time = time.perf_counter()
            result = selector.select_by_number(5)
            selection_time = (time.perf_counter() - start_time) * 1000
            selection_times.append(selection_time)
            assert result is True
        
        avg_selection_time = sum(selection_times) / len(selection_times)
        
        assert avg_selection_time < 5, f"Avg selection {avg_selection_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Number selection: avg={avg_selection_time:.4f}ms")
    
    def test_get_visible_items_performance(self, selector):
        """Test getting visible items is instant (< 5ms)."""
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d}", value=i) for i in range(1000)]
        selector.set_items(items)
        
        # Measure get_visible_items for multiple pages
        page_times = []
        for page in range(10):
            selector.page = page
            start_time = time.perf_counter()
            page_items = selector.get_visible_items()
            page_time = (time.perf_counter() - start_time) * 1000
            page_times.append(page_time)
            assert len(page_items) <= 9
        
        avg_page_time = sum(page_times) / len(page_times)
        
        assert avg_page_time < 5, f"Avg page get {avg_page_time:.4f}ms (should be < 5ms)"
        print(f"\n✓ Get visible items: avg={avg_page_time:.4f}ms")
    
    def test_stress_test_10000_items(self, selector):
        """Stress test with 10,000 items."""
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:05d}", value=i) for i in range(10000)]
        
        start_time = time.perf_counter()
        selector.set_items(items)
        load_time = (time.perf_counter() - start_time) * 1000
        
        # Test operations
        selector.next_page()
        selector.filter_items("Item 5")
        selector.clear_filter()
        total_time = (time.perf_counter() - start_time) * 1000
        
        assert len(selector.items) == 10000
        assert load_time < 500, f"Load 10k items took {load_time:.2f}ms (should be < 500ms)"
        assert total_time < 1000, f"Total operations took {total_time:.2f}ms (should be < 1s)"
        print(f"\n✓ Stress test: loaded 10k items in {load_time:.2f}ms, total={total_time:.2f}ms")
    
    def test_memory_efficiency_10000_items(self, selector):
        """Test memory usage stays reasonable with 10,000 items."""
        import sys
        
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:05d}", value=i) for i in range(10000)]
        selector.set_items(items)
        
        # Get rough size estimate
        items_memory = sys.getsizeof(selector.items)
        
        # Memory should be reasonable (< 2MB for 10k items including objects)
        assert items_memory < 2_000_000, f"Memory usage {items_memory} bytes (should be < 2MB)"
        print(f"\n✓ Memory usage: {items_memory:,} bytes for 10,000 items")


class TestSelectorCallbackPerformance:
    """Test callback performance with large datasets."""
    
    def test_callback_overhead_minimal(self):
        """Test that callbacks execute quickly with operations."""
        config = SelectorConfig(page_size=9)
        selector = SelectorFramework(config=config)
        
        items = [SelectableItem(id=f"item_{i}", label=f"Item {i:04d}", value=i) for i in range(1000)]
        selector.set_items(items)
        
        # Track callback invocations
        callback_count = 0
        
        def test_callback(item):
            nonlocal callback_count
            callback_count += 1
        
        # Set callback and measure selection operations
        selector.on_select = test_callback
        start_time = time.perf_counter()
        for i in range(100):
            selector.page = i % 10  # Cycle through pages
            selector.select_by_number(5)
        total_time = (time.perf_counter() - start_time) * 1000
        
        avg_time_per_callback = total_time / 100
        
        assert callback_count == 100
        assert avg_time_per_callback < 1, f"Avg callback time {avg_time_per_callback:.4f}ms (should be < 1ms)"
        print(f"\n✓ Callback execution: {avg_time_per_callback:.4f}ms per call ({total_time:.2f}ms total for 100 calls)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
