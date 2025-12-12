"""
Disk Monitor - Track disk usage with progress bars and configurable limits

Monitors /core, /extensions, /knowledge, /memory with visual progress bars.
Supports scaling uDOS into small distributions (16MB, 32MB, 64MB, 128MB, 256MB+).

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import gzip
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.config import Config


@dataclass
class DiskUsage:
    """Disk usage information for a path."""
    path: str
    size_bytes: int
    size_mb: float
    file_count: int
    limit_mb: Optional[float] = None
    usage_percent: Optional[float] = None
    
    @property
    def size_kb(self) -> float:
        """Size in kilobytes."""
        return self.size_bytes / 1024
    
    @property
    def size_gb(self) -> float:
        """Size in gigabytes."""
        return self.size_mb / 1024
    
    def format_size(self) -> str:
        """Format size for display."""
        if self.size_mb < 1:
            return f"{self.size_kb:.1f}KB"
        elif self.size_mb < 1024:
            return f"{self.size_mb:.1f}MB"
        else:
            return f"{self.size_gb:.2f}GB"


class DiskMonitor:
    """
    Monitor disk usage across uDOS directories with configurable limits.
    
    Supports scaling to small distributions:
    - Minimal (16MB): core only, no extensions
    - Compact (32MB): core + essential extensions
    - Standard (64MB): core + extensions, limited knowledge
    - Full (128MB): core + extensions + knowledge
    - Extended (256MB+): everything + user data
    
    Example:
        monitor = DiskMonitor(config)
        usage = monitor.scan_all()
        monitor.print_report(usage)
    """
    
    # Default size limits (MB)
    DEFAULT_LIMITS = {
        'core': 16,        # Core system
        'extensions': 48,  # Extensions (3x core)
        'knowledge': 64,   # Knowledge bank
        'memory': 256,     # User workspace
        'total': 384,      # Total uDOS installation
    }
    
    # Distribution presets
    PRESETS = {
        'minimal': {
            'core': 16,
            'extensions': 0,
            'knowledge': 0,
            'memory': 0,
            'total': 16,
        },
        'compact': {
            'core': 16,
            'extensions': 16,
            'knowledge': 0,
            'memory': 0,
            'total': 32,
        },
        'standard': {
            'core': 16,
            'extensions': 32,
            'knowledge': 16,
            'memory': 0,
            'total': 64,
        },
        'full': {
            'core': 16,
            'extensions': 48,
            'knowledge': 64,
            'memory': 0,
            'total': 128,
        },
        'extended': {
            'core': 16,
            'extensions': 64,
            'knowledge': 128,
            'memory': 256,
            'total': 464,
        },
    }
    
    def __init__(self, config: Config):
        """
        Initialize disk monitor.
        
        Args:
            config: Config instance
        """
        self.config = config
        self.project_root = Path(config.project_root)
        
        # Load limits from config
        self.limits = self._load_limits()
        
        # Cache settings
        self.cache_duration = timedelta(minutes=5)
        self.cache_file = self.project_root / "memory" / "system" / "disk_cache.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Last scan time
        self._last_scan: Optional[datetime] = None
        self._cached_usage: Optional[Dict[str, DiskUsage]] = None
    
    def _load_limits(self) -> Dict[str, float]:
        """Load disk limits from config or use defaults."""
        # Check for preset
        preset = self.config.get('disk_preset', 'extended')
        if preset in self.PRESETS:
            return self.PRESETS[preset].copy()
        
        # Load custom limits
        limits = {}
        for key, default in self.DEFAULT_LIMITS.items():
            limits[key] = float(self.config.get(f'disk_limit_{key}', default))
        
        return limits
    
    def set_preset(self, preset: str) -> bool:
        """
        Set disk limits using preset.
        
        Args:
            preset: Preset name (minimal/compact/standard/full/extended)
        
        Returns:
            True if preset applied successfully
        """
        if preset not in self.PRESETS:
            return False
        
        self.limits = self.PRESETS[preset].copy()
        self.config.set('disk_preset', preset)
        # Note: Config.set() only updates runtime state, not persisted
        
        return True
    
    def set_custom_limit(self, path: str, limit_mb: float):
        """
        Set custom limit for a path.
        
        Args:
            path: Path key (core/extensions/knowledge/memory/total)
            limit_mb: Limit in megabytes
        """
        if path in self.limits:
            self.limits[path] = limit_mb
            self.config.set(f'disk_limit_{path}', limit_mb)
            self.config.set('disk_preset', 'custom')
            # Note: Config.set() only updates runtime state, not persisted
    
    def scan_path(self, path: Path, limit_mb: Optional[float] = None) -> DiskUsage:
        """
        Scan a path and calculate disk usage.
        
        Args:
            path: Path to scan
            limit_mb: Size limit in MB (optional)
        
        Returns:
            DiskUsage object
        """
        if not path.exists():
            return DiskUsage(
                path=str(path),
                size_bytes=0,
                size_mb=0.0,
                file_count=0,
                limit_mb=limit_mb,
                usage_percent=0.0
            )
        
        total_size = 0
        file_count = 0
        
        # Walk directory tree
        for root, dirs, files in os.walk(path):
            # Skip .archive folders (counted separately)
            dirs[:] = [d for d in dirs if d not in ['.archive', '__pycache__', '.git']]
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                except (OSError, PermissionError):
                    continue
        
        size_mb = total_size / (1024 * 1024)
        usage_percent = (size_mb / limit_mb * 100) if limit_mb else None
        
        return DiskUsage(
            path=str(path.relative_to(self.project_root)),
            size_bytes=total_size,
            size_mb=size_mb,
            file_count=file_count,
            limit_mb=limit_mb,
            usage_percent=usage_percent
        )
    
    def scan_all(self, use_cache: bool = True) -> Dict[str, DiskUsage]:
        """
        Scan all major uDOS directories.
        
        Args:
            use_cache: Use cached results if recent (default: True)
        
        Returns:
            Dictionary of path -> DiskUsage
        """
        # Check cache
        if use_cache and self._is_cache_valid():
            return self._cached_usage
        
        usage = {}
        
        # Scan core directories
        usage['core'] = self.scan_path(
            self.project_root / 'core',
            self.limits.get('core')
        )
        
        usage['extensions'] = self.scan_path(
            self.project_root / 'extensions',
            self.limits.get('extensions')
        )
        
        usage['knowledge'] = self.scan_path(
            self.project_root / 'knowledge',
            self.limits.get('knowledge')
        )
        
        usage['memory'] = self.scan_path(
            self.project_root / 'memory',
            self.limits.get('memory')
        )
        
        # Calculate total
        total_bytes = sum(u.size_bytes for u in usage.values())
        total_mb = total_bytes / (1024 * 1024)
        total_limit = self.limits.get('total')
        
        usage['total'] = DiskUsage(
            path='TOTAL',
            size_bytes=total_bytes,
            size_mb=total_mb,
            file_count=sum(u.file_count for u in usage.values()),
            limit_mb=total_limit,
            usage_percent=(total_mb / total_limit * 100) if total_limit else None
        )
        
        # Update cache
        self._cached_usage = usage
        self._last_scan = datetime.now()
        self._save_cache(usage)
        
        return usage
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._last_scan or not self._cached_usage:
            return False
        
        age = datetime.now() - self._last_scan
        return age < self.cache_duration
    
    def _save_cache(self, usage: Dict[str, DiskUsage]):
        """Save usage cache to disk."""
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'usage': {
                key: {
                    'path': u.path,
                    'size_mb': u.size_mb,
                    'file_count': u.file_count,
                    'limit_mb': u.limit_mb,
                    'usage_percent': u.usage_percent,
                }
                for key, u in usage.items()
            }
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def get_progress_bar(self, usage: DiskUsage, width: int = 40) -> str:
        """
        Generate ASCII progress bar for disk usage.
        
        Args:
            usage: DiskUsage object
            width: Width of progress bar in characters
        
        Returns:
            Formatted progress bar string
        """
        if not usage.limit_mb or usage.limit_mb == 0:
            return "[" + "?" * width + "]"
        
        percent = min(usage.usage_percent or 0, 100)
        filled = int(width * percent / 100)
        
        # Color based on usage
        if percent >= 90:
            bar_char = "█"  # Critical (red)
        elif percent >= 75:
            bar_char = "▓"  # Warning (yellow)
        elif percent >= 50:
            bar_char = "▒"  # Medium (blue)
        else:
            bar_char = "░"  # Low (green)
        
        bar = bar_char * filled + "·" * (width - filled)
        return f"[{bar}]"
    
    def print_report(self, usage: Optional[Dict[str, DiskUsage]] = None, show_bars: bool = True):
        """
        Print formatted disk usage report.
        
        Args:
            usage: Usage data (scans if None)
            show_bars: Show progress bars (default: True)
        """
        if usage is None:
            usage = self.scan_all()
        
        # Get current preset
        preset = self.config.get('disk_preset', 'custom')
        
        print("=" * 70)
        print(f"DISK USAGE REPORT - Preset: {preset.upper()}")
        print("=" * 70)
        print("ℹ️  Size limits are GUIDES (not blocks). uDOS can exceed allocations.")
        print()
        
        # Print each directory
        for key in ['core', 'extensions', 'knowledge', 'memory']:
            u = usage[key]
            
            # Header line
            print(f"{key.upper():12} {u.format_size():>10} / {u.limit_mb or 0:>6.0f}MB  {u.usage_percent or 0:>5.1f}%")
            
            # Progress bar
            if show_bars:
                bar = self.get_progress_bar(u, width=50)
                print(f"             {bar}")
            
            # File count
            print(f"             {u.file_count:,} files")
            print()
        
        # Total line
        u = usage['total']
        print("-" * 70)
        print(f"{'TOTAL':12} {u.format_size():>10} / {u.limit_mb or 0:>6.0f}MB  {u.usage_percent or 0:>5.1f}%")
        if show_bars:
            bar = self.get_progress_bar(u, width=50)
            print(f"             {bar}")
        print(f"             {u.file_count:,} files")
        print("=" * 70)
    
    def check_limits(self, usage: Optional[Dict[str, DiskUsage]] = None) -> List[str]:
        """
        Check for paths exceeding limits (informational - not blocking).
        
        NOTE: Disk size limits are GUIDES, not hard blocks. uDOS can use 250%+
        of allocation. Limits help understand device requirements and plan distributions.
        
        Args:
            usage: Usage data (scans if None)
        
        Returns:
            List of informational messages
        """
        if usage is None:
            usage = self.scan_all()
        
        warnings = []
        
        for key, u in usage.items():
            if u.limit_mb and u.usage_percent:
                if u.usage_percent >= 150:
                    warnings.append(f"📊 {key.upper()} at {u.usage_percent:.1f}% ({u.format_size()} / {u.limit_mb}MB) - Consider larger preset")
                elif u.usage_percent >= 100:
                    warnings.append(f"ℹ️  {key.upper()} at {u.usage_percent:.1f}% ({u.format_size()} / {u.limit_mb}MB) - Over guide size")
                elif u.usage_percent >= 75:
                    warnings.append(f"⚡ {key.upper()} at {u.usage_percent:.1f}% ({u.format_size()} / {u.limit_mb}MB) - Approaching guide")
        
        return warnings
    
    def get_optimization_suggestions(self, usage: Dict[str, DiskUsage]) -> List[str]:
        """
        Get suggestions for reducing disk usage.
        
        Args:
            usage: Usage data
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        # Check each directory
        if usage['core'].usage_percent and usage['core'].usage_percent > 80:
            suggestions.append("Core is large - consider removing unused commands/services")
        
        if usage['extensions'].usage_percent and usage['extensions'].usage_percent > 80:
            suggestions.append("Extensions are large - run: EXTENSION CLEAN to remove unused")
        
        if usage['knowledge'].usage_percent and usage['knowledge'].usage_percent > 80:
            suggestions.append("Knowledge bank is large - consider smaller preset or selective categories")
        
        if usage['memory'].usage_percent and usage['memory'].usage_percent > 80:
            suggestions.append("Memory workspace is full - run: CLEAN to remove old files")
            suggestions.append("Run: ARCHIVE to compress old workflows/missions")
        
        # Check .archive folders
        archive_paths = [
            self.project_root / 'memory' / '.archive',
            self.project_root / 'memory' / 'workflows' / '.archive',
            self.project_root / 'memory' / 'logs' / '.archive',
        ]
        
        for archive_path in archive_paths:
            if archive_path.exists():
                archive_usage = self.scan_path(archive_path)
                if archive_usage.size_mb > 50:
                    suggestions.append(f"Archive {archive_path.relative_to(self.project_root)} is {archive_usage.format_size()} - consider purging old archives")
        
        return suggestions
    
    def suggest_preset(self, current_total_mb: float) -> str:
        """
        Suggest appropriate preset based on current usage.
        
        Args:
            current_total_mb: Current total usage in MB
        
        Returns:
            Recommended preset name
        """
        if current_total_mb <= 16:
            return 'minimal'
        elif current_total_mb <= 32:
            return 'compact'
        elif current_total_mb <= 64:
            return 'standard'
        elif current_total_mb <= 128:
            return 'full'
        else:
            return 'extended'
    
    def export_report(self, filepath: Path, usage: Optional[Dict[str, DiskUsage]] = None):
        """
        Export disk usage report to JSON file.
        
        Uses uDOS filename format: YYYY-MM-DD-HH-MM-SS-disk-report.json
        
        Args:
            filepath: Output file path
            usage: Usage data (scans if None)
        """
        if usage is None:
            usage = self.scan_all()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'preset': self.config.get('disk_preset', 'custom'),
            'usage': {
                key: {
                    'path': u.path,
                    'size_mb': u.size_mb,
                    'file_count': u.file_count,
                    'limit_mb': u.limit_mb,
                    'usage_percent': u.usage_percent,
                }
                for key, u in usage.items()
            },
            'warnings': self.check_limits(usage),
            'suggestions': self.get_optimization_suggestions(usage),
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)


# CLI interface for testing
if __name__ == '__main__':
    from core.config import Config
    
    config = Config()
    monitor = DiskMonitor(config)
    
    print("Scanning disk usage...")
    usage = monitor.scan_all(use_cache=False)
    
    print()
    monitor.print_report(usage, show_bars=True)
    
    # Check limits
    warnings = monitor.check_limits(usage)
    if warnings:
        print("\nWARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
    
    # Suggestions
    suggestions = monitor.get_optimization_suggestions(usage)
    if suggestions:
        print("\nOPTIMIZATION SUGGESTIONS:")
        for suggestion in suggestions:
            print(f"  • {suggestion}")
    
    # Preset suggestion
    total_mb = usage['total'].size_mb
    suggested = monitor.suggest_preset(total_mb)
    print(f"\nSuggested preset for {total_mb:.1f}MB: {suggested.upper()}")
