"""
Device Monitor - System resource awareness and capability detection

Monitors device capabilities:
- Available disk space
- RAM (total/available)
- CPU cores and speed
- System load
- Network connectivity
- Battery status (if applicable)

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from core.config import Config


@dataclass
class DeviceCapabilities:
    """Device hardware and software capabilities."""
    # System info
    system: str  # Darwin, Linux, Windows
    platform: str  # macOS, Ubuntu, Windows 10
    architecture: str  # x86_64, arm64, aarch64
    hostname: str
    
    # Disk
    disk_total_gb: float
    disk_used_gb: float
    disk_free_gb: float
    disk_usage_percent: float
    
    # Memory
    ram_total_gb: float
    ram_available_gb: float
    ram_usage_percent: float
    
    # CPU
    cpu_cores: int
    cpu_threads: int
    cpu_frequency_mhz: Optional[float]
    cpu_load_1min: Optional[float]
    cpu_load_5min: Optional[float]
    cpu_load_15min: Optional[float]
    
    # Network
    network_connected: bool
    network_type: Optional[str]  # wifi, ethernet, cellular
    
    # Battery (if applicable)
    has_battery: bool
    battery_percent: Optional[float]
    battery_charging: Optional[bool]
    
    # Timestamp
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'system': self.system,
            'platform': self.platform,
            'architecture': self.architecture,
            'hostname': self.hostname,
            'disk': {
                'total_gb': self.disk_total_gb,
                'used_gb': self.disk_used_gb,
                'free_gb': self.disk_free_gb,
                'usage_percent': self.disk_usage_percent,
            },
            'ram': {
                'total_gb': self.ram_total_gb,
                'available_gb': self.ram_available_gb,
                'usage_percent': self.ram_usage_percent,
            },
            'cpu': {
                'cores': self.cpu_cores,
                'threads': self.cpu_threads,
                'frequency_mhz': self.cpu_frequency_mhz,
                'load_1min': self.cpu_load_1min,
                'load_5min': self.cpu_load_5min,
                'load_15min': self.cpu_load_15min,
            },
            'network': {
                'connected': self.network_connected,
                'type': self.network_type,
            },
            'battery': {
                'has_battery': self.has_battery,
                'percent': self.battery_percent,
                'charging': self.battery_charging,
            },
            'timestamp': self.timestamp,
        }


class DeviceMonitor:
    """
    Monitor device capabilities and system resources.
    
    Provides system awareness for:
    - Resource allocation (disk size limits are guides, not blocks)
    - Performance optimization (adjust based on available resources)
    - Feature availability (disable heavy features on low-end devices)
    
    Example:
        monitor = DeviceMonitor(config)
        caps = monitor.get_capabilities()
        
        if caps.ram_total_gb < 4:
            print("Low memory device - disable heavy features")
        
        if caps.disk_free_gb < 1:
            print("Low disk space - suggest cleanup")
    """
    
    def __init__(self, config: Config):
        """
        Initialize device monitor.
        
        Args:
            config: Config instance
        """
        self.config = config
        self.cache_file = Path(config.project_root) / "memory" / "system" / "device_capabilities.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._cached_capabilities: Optional[DeviceCapabilities] = None
        self._last_scan: Optional[datetime] = None
    
    def get_capabilities(self, use_cache: bool = True) -> DeviceCapabilities:
        """
        Get device capabilities.
        
        Args:
            use_cache: Use cached results if recent (default: True)
        
        Returns:
            DeviceCapabilities object
        """
        # Check cache (valid for 5 minutes)
        if use_cache and self._cached_capabilities and self._last_scan:
            age = (datetime.now() - self._last_scan).total_seconds()
            if age < 300:  # 5 minutes
                return self._cached_capabilities
        
        # Scan system
        caps = self._scan_system()
        
        # Update cache
        self._cached_capabilities = caps
        self._last_scan = datetime.now()
        self._save_cache(caps)
        
        return caps
    
    def _scan_system(self) -> DeviceCapabilities:
        """Scan system and detect capabilities."""
        return DeviceCapabilities(
            # System info
            system=platform.system(),
            platform=self._get_platform_name(),
            architecture=platform.machine(),
            hostname=platform.node(),
            
            # Disk
            **self._get_disk_info(),
            
            # Memory
            **self._get_memory_info(),
            
            # CPU
            **self._get_cpu_info(),
            
            # Network
            **self._get_network_info(),
            
            # Battery
            **self._get_battery_info(),
            
            # Timestamp
            timestamp=datetime.now().isoformat(),
        )
    
    def _get_platform_name(self) -> str:
        """Get human-readable platform name."""
        system = platform.system()
        
        if system == 'Darwin':
            return f"macOS {platform.mac_ver()[0]}"
        elif system == 'Linux':
            try:
                with open('/etc/os-release') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            return line.split('=')[1].strip().strip('"')
            except:
                pass
            return f"Linux {platform.release()}"
        elif system == 'Windows':
            return f"Windows {platform.release()}"
        else:
            return f"{system} {platform.release()}"
    
    def _get_disk_info(self) -> Dict:
        """Get disk usage information."""
        try:
            stat = shutil.disk_usage(self.config.project_root)
            total_gb = stat.total / (1024**3)
            used_gb = stat.used / (1024**3)
            free_gb = stat.free / (1024**3)
            usage_percent = (stat.used / stat.total) * 100
            
            return {
                'disk_total_gb': round(total_gb, 2),
                'disk_used_gb': round(used_gb, 2),
                'disk_free_gb': round(free_gb, 2),
                'disk_usage_percent': round(usage_percent, 1),
            }
        except Exception:
            return {
                'disk_total_gb': 0.0,
                'disk_used_gb': 0.0,
                'disk_free_gb': 0.0,
                'disk_usage_percent': 0.0,
            }
    
    def _get_memory_info(self) -> Dict:
        """Get memory information."""
        system = platform.system()
        
        try:
            if system == 'Darwin':
                # macOS - get total memory
                result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True, timeout=2)
                total_bytes = int(result.stdout.strip())
                total_gb = total_bytes / (1024**3)
                
                # Get available memory via vm_stat
                result = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=2)
                lines = result.stdout.split('\n')
                
                # Parse vm_stat output
                page_size = 4096  # Default
                pages_free = 0
                pages_inactive = 0
                pages_speculative = 0
                
                for line in lines:
                    if 'page size of' in line:
                        page_size = int(line.split('of')[1].strip().split()[0])
                    elif 'Pages free:' in line:
                        pages_free = int(line.split(':')[1].strip().replace('.', ''))
                    elif 'Pages inactive:' in line:
                        pages_inactive = int(line.split(':')[1].strip().replace('.', ''))
                    elif 'Pages speculative:' in line:
                        pages_speculative = int(line.split(':')[1].strip().replace('.', ''))
                
                # Calculate available (free + inactive + speculative)
                available_pages = pages_free + pages_inactive + pages_speculative
                available_bytes = available_pages * page_size
                available_gb = available_bytes / (1024**3)
                usage_percent = ((total_bytes - available_bytes) / total_bytes) * 100 if total_bytes > 0 else 0
                
            elif system == 'Linux':
                # Linux
                with open('/proc/meminfo') as f:
                    lines = f.readlines()
                
                mem_info = {}
                for line in lines:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = int(parts[1].strip().split()[0])  # kB
                        mem_info[key] = value
                
                total_gb = mem_info.get('MemTotal', 0) / (1024**2)
                available_gb = mem_info.get('MemAvailable', 0) / (1024**2)
                usage_percent = ((total_gb - available_gb) / total_gb) * 100 if total_gb > 0 else 0
                
            else:
                # Windows or unknown - use psutil if available
                try:
                    import psutil
                    mem = psutil.virtual_memory()
                    total_gb = mem.total / (1024**3)
                    available_gb = mem.available / (1024**3)
                    usage_percent = mem.percent
                except ImportError:
                    return {
                        'ram_total_gb': 0.0,
                        'ram_available_gb': 0.0,
                        'ram_usage_percent': 0.0,
                    }
            
            return {
                'ram_total_gb': round(total_gb, 2),
                'ram_available_gb': round(available_gb, 2),
                'ram_usage_percent': round(usage_percent, 1),
            }
            
        except Exception:
            return {
                'ram_total_gb': 0.0,
                'ram_available_gb': 0.0,
                'ram_usage_percent': 0.0,
            }
    
    def _get_cpu_info(self) -> Dict:
        """Get CPU information."""
        try:
            cores = os.cpu_count() or 1
            threads = cores  # Assume 1 thread per core if can't detect
            
            # Get CPU frequency (if available)
            freq = None
            system = platform.system()
            
            if system == 'Darwin':
                try:
                    result = subprocess.run(['sysctl', 'hw.cpufrequency'], capture_output=True, text=True)
                    freq_hz = int(result.stdout.split(':')[1].strip())
                    freq = freq_hz / (1024**2)  # Convert to MHz
                except:
                    pass
            
            # Get load average
            load_1min, load_5min, load_15min = None, None, None
            try:
                if hasattr(os, 'getloadavg'):
                    load_1min, load_5min, load_15min = os.getloadavg()
            except:
                pass
            
            return {
                'cpu_cores': cores,
                'cpu_threads': threads,
                'cpu_frequency_mhz': round(freq, 0) if freq else None,
                'cpu_load_1min': round(load_1min, 2) if load_1min is not None else None,
                'cpu_load_5min': round(load_5min, 2) if load_5min is not None else None,
                'cpu_load_15min': round(load_15min, 2) if load_15min is not None else None,
            }
            
        except Exception:
            return {
                'cpu_cores': 1,
                'cpu_threads': 1,
                'cpu_frequency_mhz': None,
                'cpu_load_1min': None,
                'cpu_load_5min': None,
                'cpu_load_15min': None,
            }
    
    def _get_network_info(self) -> Dict:
        """Get network connectivity information."""
        try:
            # Simple connectivity test (ping)
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', '8.8.8.8'],
                capture_output=True,
                timeout=2
            )
            connected = result.returncode == 0
            
            # Try to detect network type (basic)
            network_type = None
            if connected:
                system = platform.system()
                if system == 'Darwin':
                    try:
                        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                        output = result.stdout.lower()
                        if 'en0' in output or 'wi-fi' in output:
                            network_type = 'wifi'
                        elif 'en1' in output or 'ethernet' in output:
                            network_type = 'ethernet'
                    except:
                        pass
            
            return {
                'network_connected': connected,
                'network_type': network_type,
            }
            
        except Exception:
            return {
                'network_connected': False,
                'network_type': None,
            }
    
    def _get_battery_info(self) -> Dict:
        """Get battery information (if applicable)."""
        try:
            system = platform.system()
            
            if system == 'Darwin':
                # macOS
                result = subprocess.run(['pmset', '-g', 'batt'], capture_output=True, text=True)
                output = result.stdout
                
                if 'Battery' not in output:
                    return {
                        'has_battery': False,
                        'battery_percent': None,
                        'battery_charging': None,
                    }
                
                # Parse battery percentage
                import re
                match = re.search(r'(\d+)%', output)
                percent = int(match.group(1)) if match else None
                
                charging = 'AC Power' in output or 'charging' in output.lower()
                
                return {
                    'has_battery': True,
                    'battery_percent': float(percent) if percent else None,
                    'battery_charging': charging,
                }
            
            else:
                # Linux/Windows - use psutil if available
                try:
                    import psutil
                    battery = psutil.sensors_battery()
                    
                    if battery:
                        return {
                            'has_battery': True,
                            'battery_percent': round(battery.percent, 1),
                            'battery_charging': battery.power_plugged,
                        }
                except ImportError:
                    pass
                
                return {
                    'has_battery': False,
                    'battery_percent': None,
                    'battery_charging': None,
                }
            
        except Exception:
            return {
                'has_battery': False,
                'battery_percent': None,
                'battery_charging': None,
            }
    
    def _save_cache(self, caps: DeviceCapabilities):
        """Save capabilities to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(caps.to_dict(), f, indent=2)
        except Exception:
            pass
    
    def get_device_class(self, caps: Optional[DeviceCapabilities] = None) -> str:
        """
        Classify device based on capabilities.
        
        Args:
            caps: DeviceCapabilities (scans if None)
        
        Returns:
            Device class: minimal, compact, standard, full, workstation
        """
        if caps is None:
            caps = self.get_capabilities()
        
        # Classify based on RAM and disk
        if caps.ram_total_gb < 2 or caps.disk_free_gb < 1:
            return 'minimal'
        elif caps.ram_total_gb < 4 or caps.disk_free_gb < 5:
            return 'compact'
        elif caps.ram_total_gb < 8 or caps.disk_free_gb < 20:
            return 'standard'
        elif caps.ram_total_gb < 16 or caps.disk_free_gb < 50:
            return 'full'
        else:
            return 'workstation'
    
    def suggest_udos_preset(self, caps: Optional[DeviceCapabilities] = None) -> str:
        """
        Suggest appropriate uDOS disk preset based on device.
        
        Args:
            caps: DeviceCapabilities (scans if None)
        
        Returns:
            Preset name: minimal/compact/standard/full/extended
        """
        if caps is None:
            caps = self.get_capabilities()
        
        # Map device class to uDOS preset
        device_class = self.get_device_class(caps)
        
        preset_map = {
            'minimal': 'minimal',
            'compact': 'compact',
            'standard': 'standard',
            'full': 'full',
            'workstation': 'extended',
        }
        
        return preset_map.get(device_class, 'standard')


# CLI interface for testing
if __name__ == '__main__':
    from core.config import Config
    
    config = Config()
    monitor = DeviceMonitor(config)
    
    print("=" * 70)
    print("DEVICE CAPABILITIES SCAN")
    print("=" * 70)
    print()
    
    caps = monitor.get_capabilities(use_cache=False)
    
    print(f"System: {caps.platform} ({caps.architecture})")
    print(f"Hostname: {caps.hostname}")
    print()
    
    print("DISK:")
    print(f"  Total: {caps.disk_total_gb}GB")
    print(f"  Used: {caps.disk_used_gb}GB ({caps.disk_usage_percent}%)")
    print(f"  Free: {caps.disk_free_gb}GB")
    print()
    
    print("MEMORY:")
    print(f"  Total: {caps.ram_total_gb}GB")
    print(f"  Available: {caps.ram_available_gb}GB")
    print(f"  Usage: {caps.ram_usage_percent}%")
    print()
    
    print("CPU:")
    print(f"  Cores: {caps.cpu_cores}")
    if caps.cpu_frequency_mhz:
        print(f"  Frequency: {caps.cpu_frequency_mhz}MHz")
    if caps.cpu_load_1min is not None:
        print(f"  Load: {caps.cpu_load_1min} (1min), {caps.cpu_load_5min} (5min), {caps.cpu_load_15min} (15min)")
    print()
    
    print("NETWORK:")
    print(f"  Connected: {'Yes' if caps.network_connected else 'No'}")
    if caps.network_type:
        print(f"  Type: {caps.network_type}")
    print()
    
    if caps.has_battery:
        print("BATTERY:")
        print(f"  Level: {caps.battery_percent}%")
        print(f"  Charging: {'Yes' if caps.battery_charging else 'No'}")
        print()
    
    device_class = monitor.get_device_class(caps)
    suggested_preset = monitor.suggest_udos_preset(caps)
    
    print("RECOMMENDATIONS:")
    print(f"  Device Class: {device_class.upper()}")
    print(f"  Suggested uDOS Preset: {suggested_preset.upper()}")
    print()
    
    print("=" * 70)
