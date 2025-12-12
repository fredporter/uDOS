"""
Device Manager - System Hardware & Capabilities

Manages device.json with hardware specs, capabilities, and monitoring settings.
Syncs with system information (CPU, memory, disk, network).

Part of v1.2.23 Tasks 3 & 4 - Device Integration
"""

import json
import platform
import psutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import socket


class DeviceManager:
    """Manage device information and system monitoring."""
    
    def __init__(self, config=None):
        """Initialize device manager."""
        self.config = config
        self.device_file = Path("memory/bank/system/device.json")
        self.device_data = self._load_or_create()
    
    def _load_or_create(self) -> dict:
        """Load existing device.json or create from system scan."""
        if self.device_file.exists():
            try:
                with open(self.device_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Create new device profile
        return self._create_device_profile()
    
    def _create_device_profile(self) -> dict:
        """Create device profile from system scan."""
        now = datetime.now(timezone.utc).isoformat()
        
        # Get timezone info
        tz_name = self.config.get_env('TIMEZONE', 'UTC') if self.config else 'UTC'
        tile_code = self.config.get('current_tile', 'AA340') if self.config else 'AA340'
        
        profile = {
            "device": {
                "id": f"udos-{socket.gethostname()}",
                "name": socket.gethostname(),
                "type": "terminal",
                "platform": platform.system().lower(),
                "architecture": platform.machine(),
                "initialized": now
            },
            "hardware": self._scan_hardware(),
            "system": self._scan_system(),
            "network": self._scan_network(),
            "location": {
                "timezone": tz_name,
                "timezone_abbr": self._get_tz_abbr(tz_name),
                "timezone_offset": self._get_tz_offset(),
                "tile_code": tile_code,
                "city": self._get_city_from_tile(tile_code),
                "country": self._get_country_from_tile(tile_code),
                "last_updated": now
            },
            "capabilities": self._detect_capabilities(),
            "monitoring": {
                "disk_scan_interval_minutes": 30,
                "memory_check_interval_minutes": 5,
                "network_check_interval_minutes": 1,
                "last_full_scan": now,
                "auto_sync_system_time": True,
                "warn_disk_threshold_percent": 85,
                "warn_memory_threshold_percent": 90
            },
            "metadata": {
                "created": now,
                "modified": now,
                "version": "1.0.0",
                "schema": "device-v1"
            }
        }
        
        return profile
    
    def _scan_hardware(self) -> dict:
        """Scan hardware specifications."""
        cpu_freq = psutil.cpu_freq()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "cores": psutil.cpu_count(logical=False) or psutil.cpu_count(),
                "threads": psutil.cpu_count(logical=True),
                "frequency_ghz": round(cpu_freq.current / 1000, 2) if cpu_freq else 0,
                "usage_percent": psutil.cpu_percent(interval=0.1)
            },
            "memory": {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_percent": mem.percent
            },
            "storage": {
                "total_gb": round(disk.total / (1024**3), 2),
                "available_gb": round(disk.free / (1024**3), 2),
                "used_percent": disk.percent,
                "filesystem": self._get_filesystem_type()
            }
        }
    
    def _scan_system(self) -> dict:
        """Scan system information."""
        boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        uptime = (datetime.now(timezone.utc) - boot_time).total_seconds() / 3600
        
        return {
            "os": platform.system(),
            "version": platform.version(),
            "kernel": platform.release(),
            "hostname": socket.gethostname(),
            "uptime_hours": round(uptime, 1),
            "boot_time": boot_time.isoformat(),
            "python_version": platform.python_version()
        }
    
    def _scan_network(self) -> dict:
        """Scan network configuration."""
        interfaces = []
        
        # Get network interfaces
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for iface_name, addrs in net_if_addrs.items():
            if iface_name.startswith(('lo', 'utun')):
                continue
            
            iface_info = {
                "name": iface_name,
                "type": "ethernet" if iface_name.startswith('en') else "other",
                "status": "up" if net_if_stats.get(iface_name, None) and net_if_stats[iface_name].isup else "down"
            }
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    iface_info["ipv4"] = addr.address
                elif addr.family == socket.AF_INET6:
                    iface_info["ipv6"] = addr.address
                elif addr.family == psutil.AF_LINK:
                    iface_info["mac"] = addr.address
            
            if "ipv4" in iface_info or "ipv6" in iface_info:
                interfaces.append(iface_info)
        
        return {
            "hostname": socket.gethostname() + ".local",
            "interfaces": interfaces,
            "dns_servers": self._get_dns_servers(),
            "gateway": self._get_default_gateway()
        }
    
    def _detect_capabilities(self) -> dict:
        """Detect system capabilities."""
        return {
            "audio": True,  # Assume present
            "video": False,  # Terminal-based
            "network": True,
            "bluetooth": platform.system() in ["Darwin", "Linux"],
            "usb": True,
            "virtualization": self._has_virtualization(),
            "containers": self._has_docker()
        }
    
    def _get_filesystem_type(self) -> str:
        """Get filesystem type."""
        system = platform.system()
        if system == "Darwin":
            return "APFS"
        elif system == "Linux":
            return "ext4"
        elif system == "Windows":
            return "NTFS"
        return "unknown"
    
    def _get_dns_servers(self) -> list:
        """Get DNS servers (simplified)."""
        # This is platform-specific, simplified version
        return ["8.8.8.8", "8.8.4.4"]
    
    def _get_default_gateway(self) -> str:
        """Get default gateway."""
        try:
            gws = psutil.net_if_stats()
            # Simplified - would need platform-specific code
            return "192.168.1.1"
        except Exception:
            return "unknown"
    
    def _has_virtualization(self) -> bool:
        """Check if virtualization is available."""
        # Simplified check
        return platform.system() in ["Darwin", "Linux"]
    
    def _has_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            import subprocess
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, timeout=2)
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_tz_abbr(self, tz_name: str) -> str:
        """Get timezone abbreviation."""
        abbr_map = {
            "UTC": "UTC",
            "America/New_York": "EST",
            "America/Los_Angeles": "PST",
            "Europe/London": "GMT",
            "Europe/Paris": "CET",
            "Asia/Tokyo": "JST",
            "Australia/Sydney": "AEST",
        }
        return abbr_map.get(tz_name, "UTC")
    
    def _get_tz_offset(self) -> str:
        """Get timezone offset."""
        from datetime import datetime, timezone as tz
        local_offset = datetime.now().astimezone().utcoffset()
        if local_offset:
            hours = int(local_offset.total_seconds() // 3600)
            return f"{hours:+03d}:00"
        return "+00:00"
    
    def _get_city_from_tile(self, tile: str) -> str:
        """Get city name from TILE code."""
        tile_cities = {
            "AA340": "Sydney",
            "JF57": "London",
            "LE180": "New York",
            "LK220": "Los Angeles",
            "KH110": "Tokyo",
            "JH85": "Paris"
        }
        return tile_cities.get(tile, "Unknown")
    
    def _get_country_from_tile(self, tile: str) -> str:
        """Get country from TILE code."""
        tile_countries = {
            "AA340": "Australia",
            "JF57": "United Kingdom",
            "LE180": "United States",
            "LK220": "United States",
            "KH110": "Japan",
            "JH85": "France"
        }
        return tile_countries.get(tile, "Unknown")
    
    def save(self) -> bool:
        """Save device profile to disk."""
        try:
            self.device_file.parent.mkdir(parents=True, exist_ok=True)
            self.device_data["metadata"]["modified"] = datetime.now(timezone.utc).isoformat()
            
            with open(self.device_file, 'w') as f:
                json.dump(self.device_data, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️  Failed to save device.json: {e}")
            return False
    
    def refresh(self) -> dict:
        """Refresh hardware statistics."""
        self.device_data["hardware"] = self._scan_hardware()
        self.device_data["system"] = self._scan_system()
        self.device_data["monitoring"]["last_full_scan"] = datetime.now(timezone.utc).isoformat()
        return self.device_data
    
    def get_info(self, section: str = None) -> dict:
        """Get device information."""
        if section:
            return self.device_data.get(section, {})
        return self.device_data
    
    def update_location(self, tile_code: str, timezone: str = None) -> bool:
        """Update location and timezone."""
        self.device_data["location"]["tile_code"] = tile_code
        self.device_data["location"]["city"] = self._get_city_from_tile(tile_code)
        self.device_data["location"]["country"] = self._get_country_from_tile(tile_code)
        
        if timezone:
            self.device_data["location"]["timezone"] = timezone
            self.device_data["location"]["timezone_abbr"] = self._get_tz_abbr(timezone)
        
        self.device_data["location"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        return self.save()
    
    def get_monitoring_thresholds(self) -> dict:
        """Get monitoring alert thresholds."""
        return {
            "disk": self.device_data["monitoring"]["warn_disk_threshold_percent"],
            "memory": self.device_data["monitoring"]["warn_memory_threshold_percent"]
        }
    
    def check_health(self) -> dict:
        """Check system health against thresholds."""
        thresholds = self.get_monitoring_thresholds()
        hardware = self.device_data["hardware"]
        
        return {
            "disk": {
                "status": "warning" if hardware["storage"]["used_percent"] >= thresholds["disk"] else "ok",
                "used_percent": hardware["storage"]["used_percent"],
                "threshold": thresholds["disk"]
            },
            "memory": {
                "status": "warning" if hardware["memory"]["used_percent"] >= thresholds["memory"] else "ok",
                "used_percent": hardware["memory"]["used_percent"],
                "threshold": thresholds["memory"]
            },
            "cpu": {
                "status": "ok",
                "usage_percent": hardware["cpu"]["usage_percent"]
            }
        }
