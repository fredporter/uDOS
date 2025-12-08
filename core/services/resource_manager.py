"""
Resource Manager for uDOS Mission Control

Tracks and manages system resources across missions:
- API quota tracking (Gemini, GitHub, etc.)
- Rate limiting (requests per minute)
- Disk space monitoring
- CPU and memory tracking
- Resource allocation per mission
- Conflict detection and priority system
- Throttling when resources are low

Author: uDOS Development Team
Version: 1.1.2
"""

import json
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import psutil


class ResourceManager:
    """
    Manages system resources for mission execution.

    Tracks:
    - API quotas (daily/hourly limits per provider)
    - Rate limits (requests per minute)
    - Disk space (memory usage + warnings)
    - CPU usage (background monitoring)
    - Memory usage (system + process)
    - Resource allocation per mission
    - Conflict detection
    - Throttling policies

    Example:
        >>> rm = ResourceManager()
        >>> rm.check_api_quota('gemini')
        {'available': 1450, 'limit': 1500, 'used': 50, 'percent': 3.33}

        >>> rm.allocate_resources('mission-123', api_calls=100, disk_mb=500)
        True  # Allocation successful

        >>> rm.track_api_call('gemini')
        {'quota_remaining': 1449, 'rate_ok': True}
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ResourceManager.

        Args:
            config_path: Path to resource config JSON (default: core/data/resource-config.json)
        """
        self.config_path = config_path or "core/data/resource-config.json"
        from core.utils.paths import PATHS
        self.state_path = str(PATHS.RESOURCE_STATE)
        self.log_path = str(PATHS.MEMORY_LOGS / "resources.log")

        # Ensure directories exist
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Load state (quota usage, allocations)
        self.state = self._load_state()

        # Rate limiting sliding windows (provider -> deque of timestamps)
        self.rate_windows: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Mission resource allocations
        self.allocations: Dict[str, Dict[str, Any]] = self.state.get('allocations', {})

        # Active mission priorities
        self.priorities: Dict[str, str] = {}

        # System monitoring cache (updated periodically)
        self._last_system_check = 0
        self._system_cache = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load resource configuration from JSON."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)

        # Default configuration
        return {
            'api_quotas': {
                'gemini': {
                    'daily_limit': 1500,
                    'hourly_limit': 100,
                    'reset_time': '00:00'  # UTC midnight
                },
                'github': {
                    'hourly_limit': 5000,
                    'reset_time': 'hourly'
                }
            },
            'rate_limits': {
                'gemini': {'requests_per_minute': 15},
                'github': {'requests_per_minute': 60}
            },
            'disk_thresholds': {
                'warning_percent': 80,
                'critical_percent': 90,
                'max_mission_mb': 1000
            },
            'cpu_thresholds': {
                'warning_percent': 75,
                'critical_percent': 90
            },
            'memory_thresholds': {
                'warning_percent': 80,
                'critical_percent': 90
            }
        }

    def _load_state(self) -> Dict[str, Any]:
        """Load resource state from JSON."""
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                return json.load(f)

        # Default state
        return {
            'api_usage': {},
            'allocations': {},
            'last_reset': {}
        }

    def _save_state(self) -> None:
        """Save resource state to JSON (atomic write)."""
        temp_path = f"{self.state_path}.tmp"

        with open(temp_path, 'w') as f:
            json.dump(self.state, f, indent=2)

        os.replace(temp_path, self.state_path)

    def _log(self, message: str, level: str = 'INFO') -> None:
        """Write to resource log file."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        with open(self.log_path, 'a') as f:
            f.write(log_entry)

    def check_api_quota(self, provider: str) -> Dict[str, Any]:
        """
        Check API quota status for a provider.

        Args:
            provider: Provider name (e.g., 'gemini', 'github')

        Returns:
            Dict with keys: available, limit, used, percent, reset_at
        """
        # Get quota config
        quota_config = self.config.get('api_quotas', {}).get(provider, {})
        if not quota_config:
            return {'error': f'Unknown provider: {provider}'}

        # Check if reset needed
        self._check_quota_reset(provider)

        # Get current usage
        usage_key = f"{provider}_daily"
        used = self.state.get('api_usage', {}).get(usage_key, 0)
        limit = quota_config.get('daily_limit', 0)
        available = max(0, limit - used)
        percent = (used / limit * 100) if limit > 0 else 0

        # Calculate next reset time
        reset_time = quota_config.get('reset_time', '00:00')
        if reset_time == 'hourly':
            reset_at = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0)
        else:
            # Daily reset at specified time
            now = datetime.now()
            hour, minute = map(int, reset_time.split(':'))
            reset_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if reset_at <= now:
                reset_at += timedelta(days=1)

        return {
            'provider': provider,
            'available': available,
            'limit': limit,
            'used': used,
            'percent': round(percent, 2),
            'reset_at': reset_at.isoformat()
        }

    def _check_quota_reset(self, provider: str) -> None:
        """Check if quota needs to be reset based on time."""
        quota_config = self.config.get('api_quotas', {}).get(provider, {})
        reset_time = quota_config.get('reset_time', '00:00')

        last_reset_key = f"{provider}_last_reset"
        last_reset = self.state.get('last_reset', {}).get(last_reset_key)

        now = datetime.now()
        should_reset = False

        if reset_time == 'hourly':
            # Reset every hour
            if not last_reset:
                should_reset = True
            else:
                last = datetime.fromisoformat(last_reset)
                if (now - last).total_seconds() >= 3600:
                    should_reset = True
        else:
            # Daily reset at specific time
            if not last_reset:
                should_reset = True
            else:
                last = datetime.fromisoformat(last_reset)
                hour, minute = map(int, reset_time.split(':'))
                reset_today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

                if last < reset_today <= now:
                    should_reset = True

        if should_reset:
            usage_key = f"{provider}_daily"
            self.state.setdefault('api_usage', {})[usage_key] = 0
            self.state.setdefault('last_reset', {})[last_reset_key] = now.isoformat()
            self._save_state()
            self._log(f"Reset quota for {provider}")

    def check_rate_limit(self, provider: str) -> Dict[str, Any]:
        """
        Check if rate limit allows another request.

        Args:
            provider: Provider name

        Returns:
            Dict with keys: allowed, requests_in_window, limit, wait_seconds
        """
        rate_config = self.config.get('rate_limits', {}).get(provider, {})
        limit = rate_config.get('requests_per_minute', 60)

        # Clean old entries from sliding window (older than 60 seconds)
        now = time.time()
        window = self.rate_windows[provider]

        while window and now - window[0] > 60:
            window.popleft()

        requests_in_window = len(window)
        allowed = requests_in_window < limit

        # Calculate wait time if not allowed
        wait_seconds = 0
        if not allowed and window:
            # Wait until oldest request exits the window
            wait_seconds = 60 - (now - window[0])

        return {
            'provider': provider,
            'allowed': allowed,
            'requests_in_window': requests_in_window,
            'limit': limit,
            'wait_seconds': max(0, wait_seconds)
        }

    def track_api_call(self, provider: str, mission_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Track an API call (updates quota and rate limit).

        Args:
            provider: Provider name
            mission_id: Optional mission ID for tracking

        Returns:
            Dict with quota and rate limit status
        """
        # Check quota
        quota = self.check_api_quota(provider)
        if quota.get('available', 0) <= 0:
            self._log(f"API quota exhausted for {provider}", 'WARN')
            return {'error': 'Quota exhausted', 'quota': quota}

        # Check rate limit
        rate = self.check_rate_limit(provider)
        if not rate['allowed']:
            self._log(f"Rate limit exceeded for {provider}", 'WARN')
            return {'error': 'Rate limit exceeded', 'rate': rate, 'quota': quota}

        # Record the call
        now = time.time()
        self.rate_windows[provider].append(now)

        # Update quota usage
        usage_key = f"{provider}_daily"
        self.state.setdefault('api_usage', {})[usage_key] = \
            self.state.get('api_usage', {}).get(usage_key, 0) + 1

        # Track per-mission usage if mission_id provided
        if mission_id:
            mission_key = f"{mission_id}_{provider}"
            self.state.setdefault('api_usage', {})[mission_key] = \
                self.state.get('api_usage', {}).get(mission_key, 0) + 1

        self._save_state()

        # Log the call
        msg = f"API call tracked: {provider}"
        if mission_id:
            msg += f" (mission: {mission_id})"
        self._log(msg)

        return {
            'success': True,
            'quota_remaining': quota['available'] - 1,
            'rate_ok': True
        }

    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Get disk usage statistics for memory directory.

        Returns:
            Dict with memory_mb, total_mb, percent, status (ok/warning/critical)
        """
        memory_path = Path('memory')

        # Calculate memory directory size
        memory_mb = 0
        if memory_path.exists():
            for file in memory_path.rglob('*'):
                if file.is_file():
                    memory_mb += file.stat().st_size

        memory_mb = memory_mb / (1024 * 1024)  # Convert to MB

        # Get total disk space
        disk = psutil.disk_usage('.')
        total_mb = disk.total / (1024 * 1024)
        used_mb = disk.used / (1024 * 1024)
        free_mb = disk.free / (1024 * 1024)
        percent = disk.percent

        # Determine status
        thresholds = self.config.get('disk_thresholds', {})
        if percent >= thresholds.get('critical_percent', 90):
            status = 'critical'
        elif percent >= thresholds.get('warning_percent', 80):
            status = 'warning'
        else:
            status = 'ok'

        return {
            'memory_mb': round(memory_mb, 2),
            'total_mb': round(total_mb, 2),
            'used_mb': round(used_mb, 2),
            'free_mb': round(free_mb, 2),
            'percent': round(percent, 2),
            'status': status
        }

    def get_system_stats(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Get system statistics (CPU, memory). Cached for performance.

        Args:
            force_update: Force refresh even if cache is recent

        Returns:
            Dict with cpu_percent, memory_percent, memory_mb, status
        """
        now = time.time()

        # Use cache if recent (within 5 seconds)
        if not force_update and (now - self._last_system_check < 5):
            return self._system_cache

        # Get CPU usage (non-blocking, interval=0.1)
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Get memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_mb = memory.used / (1024 * 1024)

        # Determine status
        cpu_thresh = self.config.get('cpu_thresholds', {})
        mem_thresh = self.config.get('memory_thresholds', {})

        cpu_status = 'ok'
        if cpu_percent >= cpu_thresh.get('critical_percent', 90):
            cpu_status = 'critical'
        elif cpu_percent >= cpu_thresh.get('warning_percent', 75):
            cpu_status = 'warning'

        mem_status = 'ok'
        if memory_percent >= mem_thresh.get('critical_percent', 90):
            mem_status = 'critical'
        elif memory_percent >= mem_thresh.get('warning_percent', 80):
            mem_status = 'warning'

        result = {
            'cpu_percent': round(cpu_percent, 2),
            'cpu_status': cpu_status,
            'memory_percent': round(memory_percent, 2),
            'memory_mb': round(memory_mb, 2),
            'memory_status': mem_status,
            'timestamp': datetime.now().isoformat()
        }

        # Update cache
        self._system_cache = result
        self._last_system_check = now

        return result

    def allocate_resources(
        self,
        mission_id: str,
        api_calls: int = 0,
        disk_mb: int = 0,
        priority: str = 'MEDIUM'
    ) -> Tuple[bool, str]:
        """
        Allocate resources for a mission.

        Args:
            mission_id: Mission identifier
            api_calls: Number of API calls to reserve
            disk_mb: Disk space to reserve (MB)
            priority: Mission priority (CRITICAL, HIGH, MEDIUM, LOW)

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check if resources are available
        conflicts = self._check_resource_conflicts(api_calls, disk_mb)

        if conflicts:
            # Check priority - higher priority can preempt
            if not self._can_preempt(mission_id, priority, conflicts):
                return False, f"Resource conflicts: {', '.join(conflicts)}"

        # Allocate resources
        self.allocations[mission_id] = {
            'api_calls': api_calls,
            'disk_mb': disk_mb,
            'priority': priority,
            'allocated_at': datetime.now().isoformat()
        }

        self.priorities[mission_id] = priority

        # Save state
        self.state['allocations'] = self.allocations
        self._save_state()

        self._log(f"Resources allocated for {mission_id}: {api_calls} API calls, {disk_mb} MB disk")

        return True, "Resources allocated successfully"

    def _check_resource_conflicts(self, api_calls: int, disk_mb: int) -> List[str]:
        """Check if requested resources conflict with current allocations."""
        conflicts = []

        # Check total API calls allocated
        total_api = sum(alloc.get('api_calls', 0) for alloc in self.allocations.values())
        # Assume we don't want to over-allocate more than 80% of quota
        # (simplified - in real system would check per-provider)
        if total_api + api_calls > 1200:  # 80% of default 1500
            conflicts.append('API quota')

        # Check total disk allocated
        total_disk = sum(alloc.get('disk_mb', 0) for alloc in self.allocations.values())
        max_disk = self.config.get('disk_thresholds', {}).get('max_mission_mb', 1000) * len(self.allocations or [1])

        if total_disk + disk_mb > max_disk:
            conflicts.append('Disk space')

        return conflicts

    def _can_preempt(self, mission_id: str, priority: str, conflicts: List[str]) -> bool:
        """
        Check if a mission can preempt existing allocations based on priority.

        Priority order: CRITICAL > HIGH > MEDIUM > LOW
        """
        priority_order = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        my_priority = priority_order.get(priority, 2)

        # Check if all conflicting missions have lower priority
        for other_id, other_alloc in self.allocations.items():
            if other_id == mission_id:
                continue

            other_priority = priority_order.get(other_alloc.get('priority', 'MEDIUM'), 2)
            if other_priority >= my_priority:
                return False  # Can't preempt equal or higher priority

        return True

    def release_resources(self, mission_id: str) -> None:
        """Release resources allocated to a mission."""
        if mission_id in self.allocations:
            del self.allocations[mission_id]
            self.state['allocations'] = self.allocations
            self._save_state()
            self._log(f"Resources released for {mission_id}")

        if mission_id in self.priorities:
            del self.priorities[mission_id]

    def should_throttle(self, mission_id: str, provider: str = 'gemini') -> Tuple[bool, str]:
        """
        Check if a mission should be throttled based on resource availability.

        Args:
            mission_id: Mission identifier
            provider: API provider to check

        Returns:
            Tuple of (should_throttle: bool, reason: str)
        """
        # Check API quota
        quota = self.check_api_quota(provider)
        if quota.get('percent', 0) > 80:
            return True, f"API quota at {quota['percent']}%"

        # Check rate limit
        rate = self.check_rate_limit(provider)
        if not rate['allowed']:
            return True, f"Rate limit exceeded (wait {rate['wait_seconds']:.1f}s)"

        # Check disk space
        disk = self.get_disk_usage()
        if disk['status'] == 'critical':
            return True, f"Disk space critical ({disk['percent']}% full)"

        # Check system resources
        system = self.get_system_stats()
        if system['cpu_status'] == 'critical':
            return True, f"CPU usage critical ({system['cpu_percent']}%)"

        if system['memory_status'] == 'critical':
            return True, f"Memory usage critical ({system['memory_percent']}%)"

        return False, ""

    def get_resource_summary(self) -> Dict[str, Any]:
        """Get complete resource summary for dashboard."""
        return {
            'quotas': {
                'gemini': self.check_api_quota('gemini'),
                'github': self.check_api_quota('github')
            },
            'disk': self.get_disk_usage(),
            'system': self.get_system_stats(),
            'allocations': self.allocations,
            'timestamp': datetime.now().isoformat()
        }


# Singleton instance
_resource_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """Get singleton ResourceManager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
