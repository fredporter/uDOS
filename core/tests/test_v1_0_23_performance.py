"""
Tests for v1.0.23 Phase 7 - Performance Optimization

Tests:
- Lazy loading system
- Module caching
- Performance profiling
- Startup optimization

Author: uDOS Development Team
Version: 1.0.23
"""

import unittest
import time
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.services.lazy_loader import LazyLoader, ModuleCache, StartupOptimizer
from core.services.performance_profiler import PerformanceProfiler, ExecutionMetric


class TestLazyLoader(unittest.TestCase):
    """Test lazy loading system"""
    
    def setUp(self):
        """Set up test loader"""
        self.loader = LazyLoader()
    
    def test_register_handler(self):
        """Test handler registration"""
        self.loader.register_handler(
            'test_handler',
            'core.commands.docs_unified_handler',
            'DocsUnifiedHandler'
        )
        
        self.assertIn('test_handler', self.loader._handler_configs)
        self.assertFalse(self.loader._handler_configs['test_handler']['loaded'])
    
    def test_handler_not_loaded_on_registration(self):
        """Test handler is not loaded on registration"""
        self.loader.register_handler(
            'test_handler',
            'core.commands.docs_unified_handler',
            'DocsUnifiedHandler'
        )
        
        # Should not be in loaded handlers yet
        self.assertNotIn('test_handler', self.loader._handlers)
    
    def test_get_unregistered_handler(self):
        """Test getting unregistered handler returns None"""
        handler = self.loader.get_handler('nonexistent')
        self.assertIsNone(handler)
    
    def test_access_counting(self):
        """Test access count tracking"""
        self.loader.register_handler(
            'test_handler',
            'core.commands.docs_unified_handler',
            'DocsUnifiedHandler'
        )
        
        # Access multiple times
        self.loader.get_handler('test_handler')
        self.loader.get_handler('test_handler')
        self.loader.get_handler('test_handler')
        
        self.assertEqual(self.loader._access_counts['test_handler'], 3)
    
    def test_get_stats(self):
        """Test statistics generation"""
        self.loader.register_handler('h1', 'sys', 'path')
        self.loader.register_handler('h2', 'sys', 'path')
        self.loader.get_handler('h1')
        
        stats = self.loader.get_stats()
        
        self.assertEqual(stats['total_registered'], 2)
        # Handler may not load if class not found, just check it was accessed
        self.assertIn('h1', stats['access_counts'])
    
    def test_load_report_generation(self):
        """Test load report output"""
        self.loader.register_handler('test', 'sys', 'path')
        report = self.loader.get_load_report()
        
        self.assertIn("LAZY LOADING REPORT", report)
        self.assertIn("Registered Handlers", report)


class TestModuleCache(unittest.TestCase):
    """Test module caching system"""
    
    def setUp(self):
        """Set up test cache"""
        self.cache = ModuleCache(max_size=3)
    
    def test_cache_miss(self):
        """Test cache miss"""
        result = self.cache.get('nonexistent')
        self.assertIsNone(result)
        self.assertEqual(self.cache._misses, 1)
    
    def test_cache_hit(self):
        """Test cache hit"""
        self.cache.put('key1', 'value1')
        result = self.cache.get('key1')
        
        self.assertEqual(result, 'value1')
        self.assertEqual(self.cache._hits, 1)
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        self.cache.put('key1', 'value1')
        self.cache.put('key2', 'value2')
        self.cache.put('key3', 'value3')
        
        # This should evict key1 (least recently used)
        self.cache.put('key4', 'value4')
        
        self.assertIsNone(self.cache.get('key1'))
        self.assertEqual(self.cache.get('key4'), 'value4')
    
    def test_access_updates_order(self):
        """Test that accessing an item moves it to end (most recent)"""
        self.cache.put('key1', 'value1')
        self.cache.put('key2', 'value2')
        self.cache.put('key3', 'value3')
        
        # Access key1 (moves to end)
        self.cache.get('key1')
        
        # Add key4 (should evict key2, not key1)
        self.cache.put('key4', 'value4')
        
        self.assertIsNotNone(self.cache.get('key1'))
        self.assertIsNone(self.cache.get('key2'))
    
    def test_cache_clear(self):
        """Test cache clearing"""
        self.cache.put('key1', 'value1')
        self.cache.put('key2', 'value2')
        
        self.cache.clear()
        
        self.assertEqual(len(self.cache._cache), 0)
        self.assertEqual(self.cache._hits, 0)
        self.assertEqual(self.cache._misses, 0)
    
    def test_get_stats(self):
        """Test statistics generation"""
        self.cache.put('key1', 'value1')
        self.cache.get('key1')  # Hit
        self.cache.get('key2')  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['size'], 1)
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_rate'], '50.0%')
    
    def test_cache_report(self):
        """Test cache report generation"""
        self.cache.put('key1', 'value1')
        report = self.cache.get_report()
        
        self.assertIn("CACHE STATISTICS", report)
        self.assertIn("Current Size", report)


class TestStartupOptimizer(unittest.TestCase):
    """Test startup optimization"""
    
    def setUp(self):
        """Set up test optimizer"""
        self.optimizer = StartupOptimizer()
    
    def test_time_operation(self):
        """Test timing an operation"""
        def slow_operation():
            time.sleep(0.01)  # 10ms
            return "result"
        
        result = self.optimizer.time_operation('test_op', slow_operation)
        
        self.assertEqual(result, "result")
        self.assertIn('test_op', self.optimizer._startup_times)
        self.assertGreater(self.optimizer._startup_times['test_op'], 0.009)
    
    def test_total_startup_time(self):
        """Test total startup time calculation"""
        def op1():
            time.sleep(0.01)
        
        def op2():
            time.sleep(0.01)
        
        self.optimizer.time_operation('op1', op1)
        self.optimizer.time_operation('op2', op2)
        
        self.assertGreater(self.optimizer._total_startup_time, 0.018)
    
    def test_startup_report(self):
        """Test startup report generation"""
        def fast_op():
            pass
        
        self.optimizer.time_operation('fast_op', fast_op)
        report = self.optimizer.get_startup_report()
        
        self.assertIn("STARTUP PERFORMANCE REPORT", report)
        self.assertIn("Total Startup Time", report)
    
    def test_recommendations_slow_startup(self):
        """Test recommendations for slow startup"""
        def slow_op():
            time.sleep(1.1)  # Over 1 second
        
        self.optimizer.time_operation('slow', slow_op)
        recommendations = self.optimizer.get_recommendations()
        
        # Should warn about slow startup
        self.assertTrue(any("exceeds 1 second" in r for r in recommendations))
    
    def test_recommendations_slow_operation(self):
        """Test recommendations for slow operations"""
        def very_slow_op():
            time.sleep(0.15)  # 150ms
        
        self.optimizer.time_operation('very_slow', very_slow_op)
        recommendations = self.optimizer.get_recommendations()
        
        # Should warn about slow operation
        self.assertTrue(any("is slow" in r for r in recommendations))
    
    def test_recommendations_good_performance(self):
        """Test recommendations when performance is good"""
        def fast_op():
            time.sleep(0.001)  # 1ms
        
        self.optimizer.time_operation('fast', fast_op)
        recommendations = self.optimizer.get_recommendations()
        
        # Should indicate good performance
        self.assertTrue(any("looks good" in r for r in recommendations))


class TestPerformanceProfiler(unittest.TestCase):
    """Test performance profiling"""
    
    def setUp(self):
        """Set up test profiler"""
        self.profiler = PerformanceProfiler()
    
    def test_profile_command_success(self):
        """Test profiling successful command"""
        def fast_command():
            return "result"
        
        result = self.profiler.profile_command('TEST', [], fast_command)
        
        self.assertEqual(result, "result")
        self.assertEqual(len(self.profiler._metrics), 1)
        self.assertTrue(self.profiler._metrics[0].success)
    
    def test_profile_command_failure(self):
        """Test profiling failed command"""
        def failing_command():
            raise ValueError("Test error")
        
        with self.assertRaises(ValueError):
            self.profiler.profile_command('FAIL', [], failing_command)
        
        # Metric should still be recorded
        self.assertEqual(len(self.profiler._metrics), 1)
        self.assertFalse(self.profiler._metrics[0].success)
    
    def test_slow_command_detection(self):
        """Test slow command detection"""
        def slow_command():
            time.sleep(0.06)  # 60ms (over 50ms target)
        
        self.profiler.profile_command('SLOW', [], slow_command)
        
        self.assertEqual(len(self.profiler._slow_commands), 1)
    
    def test_command_stats_tracking(self):
        """Test per-command statistics tracking"""
        def test_command():
            time.sleep(0.001)
        
        # Run same command multiple times
        self.profiler.profile_command('CMD', [], test_command)
        self.profiler.profile_command('CMD', [], test_command)
        self.profiler.profile_command('CMD', [], test_command)
        
        stats = self.profiler.get_command_stats('CMD')
        
        self.assertEqual(stats['count'], 3)
        self.assertGreater(stats['mean'], 0)
    
    def test_get_percentile(self):
        """Test percentile calculation"""
        times = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
        
        p50 = self.profiler.get_percentile(times, 0.50)
        p90 = self.profiler.get_percentile(times, 0.90)
        
        # P50 should be around middle value
        self.assertGreater(p50, 0.04)
        self.assertLess(p50, 0.07)
        
        # P90 should be high value
        self.assertGreater(p90, 0.08)
    
    def test_overall_stats(self):
        """Test overall statistics"""
        def cmd1():
            time.sleep(0.001)
        
        def cmd2():
            time.sleep(0.002)
        
        self.profiler.profile_command('CMD1', [], cmd1)
        self.profiler.profile_command('CMD2', [], cmd2)
        
        stats = self.profiler.get_overall_stats()
        
        self.assertEqual(stats['total_commands'], 2)
        self.assertEqual(stats['successful'], 2)
        self.assertEqual(stats['unique_commands'], 2)
    
    def test_performance_report_generation(self):
        """Test performance report output"""
        def test_cmd():
            time.sleep(0.001)
        
        self.profiler.profile_command('TEST', [], test_cmd)
        report = self.profiler.get_performance_report()
        
        self.assertIn("PERFORMANCE REPORT", report)
        self.assertIn("Total Commands", report)
        self.assertIn("Percentiles", report)
    
    def test_slowest_commands(self):
        """Test getting slowest commands"""
        def fast():
            time.sleep(0.001)
        
        def slow():
            time.sleep(0.1)
        
        self.profiler.profile_command('FAST', [], fast)
        self.profiler.profile_command('SLOW', [], slow)
        
        slowest = self.profiler.get_slowest_commands(limit=5)
        
        # SLOW should be first
        self.assertEqual(slowest[0]['command'], 'SLOW')
    
    def test_optimization_suggestions(self):
        """Test optimization suggestions"""
        def very_slow():
            time.sleep(0.2)  # Way over targets
        
        self.profiler.profile_command('VERY_SLOW', [], very_slow)
        suggestions = self.profiler.get_optimization_suggestions()
        
        # Should have warnings
        self.assertTrue(any("⚠️" in s for s in suggestions))
    
    def test_enable_disable(self):
        """Test enabling/disabling profiler"""
        self.profiler.disable()
        
        def test_cmd():
            return "result"
        
        result = self.profiler.profile_command('TEST', [], test_cmd)
        
        # Should still execute but not record metrics
        self.assertEqual(result, "result")
        
        self.profiler.enable()
        self.profiler.profile_command('TEST2', [], test_cmd)
        
        # Should now record metrics
        self.assertGreater(len(self.profiler._metrics), 0)
    
    def test_reset(self):
        """Test resetting profiler"""
        def test_cmd():
            pass
        
        self.profiler.profile_command('TEST', [], test_cmd)
        self.profiler.reset()
        
        self.assertEqual(len(self.profiler._metrics), 0)
        self.assertEqual(len(self.profiler._command_stats), 0)


if __name__ == '__main__':
    unittest.main()
