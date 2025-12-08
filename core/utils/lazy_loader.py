"""
Lazy Loading System - v1.0.23 Phase 7
Load command handlers and modules only when needed for faster startup

Features:
- Deferred handler initialization
- Module caching
- Import optimization
- Memory-efficient loading

Author: uDOS Development Team
Version: 1.0.23
"""

from typing import Dict, Type, Optional, Any, Callable
from pathlib import Path
import importlib
import sys
import time


class LazyLoader:
    """Lazy loading manager for command handlers and modules"""

    def __init__(self, logger=None):
        """Initialize lazy loader"""
        self.logger = logger
        self._handlers: Dict[str, Any] = {}
        self._modules: Dict[str, Any] = {}
        self._handler_configs: Dict[str, Dict] = {}
        self._load_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}

    def register_handler(self, name: str, module_path: str, class_name: str,
                        init_args: Optional[Dict] = None):
        """
        Register a handler for lazy loading

        Args:
            name: Handler name (e.g., 'docs', 'learn', 'memory')
            module_path: Python module path (e.g., 'core.commands.docs_unified_handler')
            class_name: Class name to instantiate
            init_args: Optional initialization arguments
        """
        self._handler_configs[name] = {
            'module_path': module_path,
            'class_name': class_name,
            'init_args': init_args or {},
            'loaded': False
        }

        if self.logger:
            self.logger.debug(f"Registered lazy handler: {name}")

    def get_handler(self, name: str) -> Optional[Any]:
        """
        Get handler, loading it if necessary

        Args:
            name: Handler name

        Returns:
            Handler instance or None if not found
        """
        # Track access
        self._access_counts[name] = self._access_counts.get(name, 0) + 1

        # Return cached handler if already loaded
        if name in self._handlers:
            return self._handlers[name]

        # Check if registered
        if name not in self._handler_configs:
            if self.logger:
                self.logger.warning(f"Handler '{name}' not registered")
            return None

        # Load the handler
        return self._load_handler(name)

    def _load_handler(self, name: str) -> Optional[Any]:
        """Load and instantiate a handler"""
        config = self._handler_configs[name]

        start_time = time.time()

        try:
            # Import module
            module_path = config['module_path']
            if module_path not in self._modules:
                module = importlib.import_module(module_path)
                self._modules[module_path] = module
            else:
                module = self._modules[module_path]

            # Get class
            class_name = config['class_name']
            handler_class = getattr(module, class_name)

            # Instantiate with args
            init_args = config['init_args']
            handler = handler_class(**init_args)

            # Cache the handler
            self._handlers[name] = handler
            config['loaded'] = True

            # Track load time
            load_time = time.time() - start_time
            self._load_times[name] = load_time

            if self.logger:
                self.logger.debug(f"Loaded handler '{name}' in {load_time*1000:.2f}ms")

            return handler

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load handler '{name}': {e}")
            return None

    def preload_handlers(self, handler_names: list):
        """
        Preload specific handlers (for frequently used ones)

        Args:
            handler_names: List of handler names to preload
        """
        for name in handler_names:
            if name in self._handler_configs and name not in self._handlers:
                self._load_handler(name)

    def unload_handler(self, name: str):
        """
        Unload a handler to free memory

        Args:
            name: Handler name
        """
        if name in self._handlers:
            del self._handlers[name]
            if name in self._handler_configs:
                self._handler_configs[name]['loaded'] = False

            if self.logger:
                self.logger.debug(f"Unloaded handler: {name}")

    def get_stats(self) -> Dict[str, Any]:
        """Get lazy loading statistics"""
        total_handlers = len(self._handler_configs)
        loaded_handlers = len(self._handlers)

        return {
            'total_registered': total_handlers,
            'currently_loaded': loaded_handlers,
            'memory_efficiency': f"{(1 - loaded_handlers/total_handlers)*100:.1f}%" if total_handlers > 0 else "0%",
            'load_times': self._load_times.copy(),
            'access_counts': self._access_counts.copy(),
            'most_accessed': max(self._access_counts.items(), key=lambda x: x[1])[0] if self._access_counts else None
        }

    def get_load_report(self) -> str:
        """Generate human-readable load report"""
        stats = self.get_stats()

        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│  LAZY LOADING REPORT                                           │",
            "├─────────────────────────────────────────────────────────────────┤",
            f"│  Registered Handlers:  {stats['total_registered']:<43} │",
            f"│  Currently Loaded:     {stats['currently_loaded']:<43} │",
            f"│  Memory Efficiency:    {stats['memory_efficiency']:<43} │",
            "│                                                                 │",
        ]

        if stats['load_times']:
            output.append("│  Load Times:                                                    │")
            for name, load_time in sorted(stats['load_times'].items(), key=lambda x: x[1], reverse=True):
                output.append(f"│    {name:<20} {load_time*1000:>6.2f}ms {' '*28} │")

        if stats['access_counts']:
            output.append("│                                                                 │")
            output.append("│  Access Counts:                                                 │")
            for name, count in sorted(stats['access_counts'].items(), key=lambda x: x[1], reverse=True)[:5]:
                output.append(f"│    {name:<20} {count:>6} accesses {' '*24} │")

        output.extend([
            "├─────────────────────────────────────────────────────────────────┤",
            f"│  Most Accessed: {stats['most_accessed'] or 'None':<48} │",
            "└─────────────────────────────────────────────────────────────────┘"
        ])

        return "\n".join(output)


class ModuleCache:
    """Cache for frequently accessed data"""

    def __init__(self, max_size: int = 100, logger=None):
        """
        Initialize cache

        Args:
            max_size: Maximum number of cached items (LRU eviction)
            logger: Optional logger
        """
        self.max_size = max_size
        self.logger = logger
        self._cache: Dict[str, Any] = {}
        self._access_order: list = []
        self._hits: int = 0
        self._misses: int = 0

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            self._hits += 1
            return self._cache[key]

        self._misses += 1
        return None

    def put(self, key: str, value: Any):
        """Put item in cache"""
        # Remove if exists (will re-add at end)
        if key in self._cache:
            self._access_order.remove(key)

        # Add to cache
        self._cache[key] = value
        self._access_order.append(key)

        # Evict least recently used if over limit
        while len(self._cache) > self.max_size:
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]

            if self.logger:
                self.logger.debug(f"Evicted from cache: {lru_key}")

    def clear(self):
        """Clear cache"""
        self._cache.clear()
        self._access_order.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'total_requests': total_requests
        }

    def get_report(self) -> str:
        """Generate cache report"""
        stats = self.get_stats()

        return f"""
┌─────────────────────────────────────────────────────────────────┐
│  CACHE STATISTICS                                              │
├─────────────────────────────────────────────────────────────────┤
│  Current Size:      {stats['size']}/{stats['max_size']:<47} │
│  Cache Hits:        {stats['hits']:<47} │
│  Cache Misses:      {stats['misses']:<47} │
│  Hit Rate:          {stats['hit_rate']:<47} │
│  Total Requests:    {stats['total_requests']:<47} │
└─────────────────────────────────────────────────────────────────┘
"""


class StartupOptimizer:
    """Optimize uDOS startup sequence"""

    def __init__(self, logger=None):
        """Initialize optimizer"""
        self.logger = logger
        self._startup_times: Dict[str, float] = {}
        self._total_startup_time: float = 0

    def time_operation(self, operation_name: str, operation: Callable) -> Any:
        """
        Time an operation during startup

        Args:
            operation_name: Name of operation
            operation: Callable to execute

        Returns:
            Result of operation
        """
        start_time = time.time()
        result = operation()
        elapsed = time.time() - start_time

        self._startup_times[operation_name] = elapsed
        self._total_startup_time += elapsed

        if self.logger:
            self.logger.debug(f"Startup: {operation_name} took {elapsed*1000:.2f}ms")

        return result

    def defer_operation(self, operation: Callable):
        """
        Mark operation as deferred (not run during startup)

        Args:
            operation: Callable to defer
        """
        # Store for later execution
        # This is a placeholder - actual implementation would queue operations
        pass

    def get_startup_report(self) -> str:
        """Generate startup performance report"""
        if not self._startup_times:
            return "No startup timing data available"

        output = [
            "┌─────────────────────────────────────────────────────────────────┐",
            "│  STARTUP PERFORMANCE REPORT                                    │",
            "├─────────────────────────────────────────────────────────────────┤",
            f"│  Total Startup Time: {self._total_startup_time*1000:>6.2f}ms {' '*33} │",
            "│                                                                 │",
            "│  Operation Breakdown:                                           │"
        ]

        # Sort by time (slowest first)
        sorted_ops = sorted(self._startup_times.items(), key=lambda x: x[1], reverse=True)

        for op_name, op_time in sorted_ops:
            percentage = (op_time / self._total_startup_time * 100) if self._total_startup_time > 0 else 0
            output.append(f"│    {op_name:<30} {op_time*1000:>6.2f}ms ({percentage:>5.1f}%) {'':>10} │")

        output.append("└─────────────────────────────────────────────────────────────────┘")

        return "\n".join(output)

    def get_recommendations(self) -> list:
        """Get optimization recommendations"""
        recommendations = []

        # Check if startup is slow
        if self._total_startup_time > 1.0:
            recommendations.append("⚠️  Startup time exceeds 1 second target")

        # Identify slow operations
        for op_name, op_time in self._startup_times.items():
            if op_time > 0.1:  # 100ms
                recommendations.append(f"⚠️  '{op_name}' is slow ({op_time*1000:.0f}ms) - consider deferring or optimizing")

        if not recommendations:
            recommendations.append("✅ Startup performance looks good!")

        return recommendations


# Global instances
_lazy_loader = None
_module_cache = None
_startup_optimizer = None


def get_lazy_loader(logger=None) -> LazyLoader:
    """Get global lazy loader instance"""
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = LazyLoader(logger=logger)
    return _lazy_loader


def get_cache(max_size: int = 100, logger=None) -> ModuleCache:
    """Get global cache instance"""
    global _module_cache
    if _module_cache is None:
        _module_cache = ModuleCache(max_size=max_size, logger=logger)
    return _module_cache


def get_startup_optimizer(logger=None) -> StartupOptimizer:
    """Get global startup optimizer instance"""
    global _startup_optimizer
    if _startup_optimizer is None:
        _startup_optimizer = StartupOptimizer(logger=logger)
    return _startup_optimizer
