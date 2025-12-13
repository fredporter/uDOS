"""
Time-Date Manager Service

Handles timezone tracking, city lookup, grid-aware time display,
and multiple timezone management for uDOS.

Part of v1.2.22 - Self-Healing & Auto-Error-Awareness System
"""

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False

try:
    import tzlocal
    TZLOCAL_AVAILABLE = True
except ImportError:
    TZLOCAL_AVAILABLE = False


@dataclass
class TimeZoneInfo:
    """Timezone information."""
    name: str  # IANA timezone name (e.g., "America/New_York")
    abbreviation: str  # Short form (e.g., "EST", "PDT")
    offset: str  # UTC offset (e.g., "+10:00", "-05:00")
    city: Optional[str] = None  # Associated city
    tile: Optional[str] = None  # Associated TILE code


class TimeDateManager:
    """Manages timezone, date/time display, and grid-aware time."""
    
    def __init__(self, config):
        """
        Initialize time-date manager.
        
        Args:
            config: Config instance
        """
        self.config = config
        
        # Load timezone data
        self.timezones_file = Path(config.project_root) / "core" / "data" / "timezones.json"
        self.timezones_data = self._load_timezones()
        
        # Current timezone (from config or system)
        self._current_tz = None
        
        # Multiple timezone tracking
        self.tracked_zones: List[str] = []  # IANA timezone names
        
        # Grid-aware time cache
        self._tile_time_cache: Dict[str, str] = {}
    
    def _load_timezones(self) -> Dict:
        """Load timezone data from JSON file."""
        if self.timezones_file.exists():
            try:
                with open(self.timezones_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load timezones.json: {e}")
                return self._get_default_timezones()
        else:
            # Create default timezones file
            default_data = self._get_default_timezones()
            self.timezones_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.timezones_file, 'w') as f:
                json.dump(default_data, f, indent=2)
            return default_data
    
    def _get_default_timezones(self) -> Dict:
        """Get default timezone data."""
        return {
            "zones": {
                "UTC": {
                    "name": "UTC",
                    "offset": "+00:00",
                    "cities": ["Greenwich"]
                },
                "America/New_York": {
                    "name": "America/New_York",
                    "offset": "-05:00",
                    "cities": ["New York", "Washington DC", "Miami"]
                },
                "America/Los_Angeles": {
                    "name": "America/Los_Angeles",
                    "offset": "-08:00",
                    "cities": ["Los Angeles", "San Francisco", "Seattle"]
                },
                "Europe/London": {
                    "name": "Europe/London",
                    "offset": "+00:00",
                    "cities": ["London", "Edinburgh", "Cardiff"]
                },
                "Europe/Paris": {
                    "name": "Europe/Paris",
                    "offset": "+01:00",
                    "cities": ["Paris", "Berlin", "Rome"]
                },
                "Asia/Tokyo": {
                    "name": "Asia/Tokyo",
                    "offset": "+09:00",
                    "cities": ["Tokyo", "Osaka", "Kyoto"]
                },
                "Australia/Sydney": {
                    "name": "Australia/Sydney",
                    "offset": "+10:00",
                    "cities": ["Sydney", "Melbourne", "Brisbane"]
                }
            },
            "tiles": {
                "AA340": "Australia/Sydney",
                "JF57": "Europe/London",
                "LE180": "America/New_York",
                "LK220": "America/Los_Angeles",
                "KH110": "Asia/Tokyo",
                "JH85": "Europe/Paris"
            }
        }
    
    @property
    def current_timezone(self) -> str:
        """Get current timezone (IANA name)."""
        if self._current_tz:
            return self._current_tz
        
        # Try config
        tz = self.config.get('timezone')
        if tz:
            self._current_tz = tz
            return tz
        
        # Try system timezone
        try:
            if TZLOCAL_AVAILABLE:
                # Get local timezone using tzlocal
                local_tz = tzlocal.get_localzone()
                tz_name = str(local_tz)
                # Verify it's a valid IANA name
                if tz_name and '/' in tz_name:
                    self._current_tz = tz_name
                else:
                    self._current_tz = "UTC"
            elif PYTZ_AVAILABLE:
                # Fallback: try to use time module
                import time
                if hasattr(time, 'tzname'):
                    # Try to map to IANA
                    local_tz = time.tzname[0]
                    self._current_tz = self._map_to_iana(local_tz) or "UTC"
                else:
                    self._current_tz = "UTC"
            else:
                self._current_tz = "UTC"
        except Exception:
            self._current_tz = "UTC"
        
        return self._current_tz
    
    def _map_to_iana(self, tz_name: str) -> Optional[str]:
        """Map timezone abbreviation to IANA name."""
        mapping = {
            'EST': 'America/New_York',
            'EDT': 'America/New_York',
            'PST': 'America/Los_Angeles',
            'PDT': 'America/Los_Angeles',
            'GMT': 'Europe/London',
            'BST': 'Europe/London',
            'CET': 'Europe/Paris',
            'CEST': 'Europe/Paris',
            'JST': 'Asia/Tokyo',
            'AEDT': 'Australia/Sydney',
            'AEST': 'Australia/Sydney'
        }
        return mapping.get(tz_name.upper())
    
    def set_timezone(self, tz_name: str) -> bool:
        """
        Set current timezone.
        
        Args:
            tz_name: IANA timezone name or city name
            
        Returns:
            True if successful
        """
        # Try exact match
        if tz_name in self.timezones_data.get('zones', {}):
            self._current_tz = tz_name
            self.config.set('timezone', tz_name)
            return True
        
        # Try city lookup
        tz = self.lookup_city(tz_name)
        if tz:
            self._current_tz = tz
            self.config.set('timezone', tz)
            return True
        
        return False
    
    def lookup_city(self, city_name: str) -> Optional[str]:
        """
        Lookup timezone by city name.
        
        Args:
            city_name: City name (case-insensitive)
            
        Returns:
            IANA timezone name or None
        """
        city_lower = city_name.lower()
        
        for tz_name, tz_data in self.timezones_data.get('zones', {}).items():
            cities = tz_data.get('cities', [])
            for city in cities:
                if city.lower() == city_lower or city_lower in city.lower():
                    return tz_name
        
        return None
    
    def lookup_tile(self, tile_code: str) -> Optional[str]:
        """
        Lookup timezone by TILE code.
        
        Args:
            tile_code: TILE code (e.g., "AA340")
            
        Returns:
            IANA timezone name or None
        """
        return self.timezones_data.get('tiles', {}).get(tile_code)
    
    def get_time_info(self, tz_name: Optional[str] = None) -> TimeZoneInfo:
        """
        Get timezone information.
        
        Args:
            tz_name: IANA timezone name (None = current)
            
        Returns:
            TimeZoneInfo object
        """
        if not tz_name:
            tz_name = self.current_timezone
        
        # Get timezone data
        tz_data = self.timezones_data.get('zones', {}).get(tz_name, {})
        
        if PYTZ_AVAILABLE:
            try:
                tz = pytz.timezone(tz_name)
                now = datetime.now(tz)
                offset_seconds = now.utcoffset().total_seconds()
                offset_hours = int(offset_seconds // 3600)
                offset_minutes = int((offset_seconds % 3600) // 60)
                offset_str = f"{offset_hours:+03d}:{offset_minutes:02d}"
                abbr = now.strftime('%Z')
            except Exception:
                offset_str = tz_data.get('offset', '+00:00')
                abbr = tz_name.split('/')[-1][:3].upper()
        else:
            # Fallback without pytz
            offset_str = tz_data.get('offset', '+00:00')
            abbr = tz_name.split('/')[-1][:3].upper()
        
        # Get associated city
        cities = tz_data.get('cities', [])
        city = cities[0] if cities else None
        
        # Get associated TILE
        tile = None
        for tile_code, tile_tz in self.timezones_data.get('tiles', {}).items():
            if tile_tz == tz_name:
                tile = tile_code
                break
        
        return TimeZoneInfo(
            name=tz_name,
            abbreviation=abbr,
            offset=offset_str,
            city=city,
            tile=tile
        )
    
    def get_current_time(self, tz_name: Optional[str] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get current time in specified timezone.
        
        Args:
            tz_name: IANA timezone name (None = current)
            format_str: strftime format string
            
        Returns:
            Formatted time string
        """
        if not tz_name:
            tz_name = self.current_timezone
        
        if PYTZ_AVAILABLE:
            try:
                tz = pytz.timezone(tz_name)
                now = datetime.now(tz)
                return now.strftime(format_str)
            except Exception:
                pass
        
        # Fallback without pytz
        return datetime.now().strftime(format_str)
    
    def get_tile_time(self, tile_code: str) -> Optional[str]:
        """
        Get current time for a TILE location.
        
        Args:
            tile_code: TILE code (e.g., "AA340")
            
        Returns:
            Formatted time string or None
        """
        # Check cache
        if tile_code in self._tile_time_cache:
            cached_time, cached_at = self._tile_time_cache[tile_code]
            if (datetime.now() - cached_at).seconds < 30:  # 30-second cache
                return cached_time
        
        # Lookup timezone
        tz_name = self.lookup_tile(tile_code)
        if not tz_name:
            return None
        
        # Get time
        time_str = self.get_current_time(tz_name, "%H:%M:%S")
        
        # Cache result
        self._tile_time_cache[tile_code] = (time_str, datetime.now())
        
        return time_str
    
    def add_tracked_zone(self, tz_name: str) -> bool:
        """
        Add timezone to tracked list.
        
        Args:
            tz_name: IANA timezone name or city name
            
        Returns:
            True if successful
        """
        # Resolve to IANA name
        if tz_name not in self.timezones_data.get('zones', {}):
            tz_name = self.lookup_city(tz_name)
            if not tz_name:
                return False
        
        if tz_name not in self.tracked_zones:
            self.tracked_zones.append(tz_name)
            return True
        
        return False
    
    def remove_tracked_zone(self, tz_name: str) -> bool:
        """
        Remove timezone from tracked list.
        
        Args:
            tz_name: IANA timezone name
            
        Returns:
            True if successful
        """
        if tz_name in self.tracked_zones:
            self.tracked_zones.remove(tz_name)
            return True
        return False
    
    def get_multiple_times(self, tz_names: Optional[List[str]] = None) -> List[Tuple[TimeZoneInfo, str]]:
        """
        Get times for multiple timezones.
        
        Args:
            tz_names: List of IANA timezone names (None = tracked zones)
            
        Returns:
            List of (TimeZoneInfo, time_string) tuples
        """
        if not tz_names:
            tz_names = self.tracked_zones if self.tracked_zones else [self.current_timezone]
        
        results = []
        for tz_name in tz_names:
            info = self.get_time_info(tz_name)
            time_str = self.get_current_time(tz_name, "%H:%M:%S")
            results.append((info, time_str))
        
        return results
    
    def format_duration(self, seconds: int) -> str:
        """
        Format duration in human-readable form.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted string (e.g., "1h 23m 45s")
        """
        if seconds < 0:
            return "0s"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """
        Parse duration string to seconds.
        
        Args:
            duration_str: Duration string (e.g., "1h 30m", "45s", "2:30:00")
            
        Returns:
            Seconds or None if invalid
        """
        import re
        
        # Try HH:MM:SS format
        if ':' in duration_str:
            parts = duration_str.split(':')
            try:
                if len(parts) == 3:
                    h, m, s = map(int, parts)
                    return h * 3600 + m * 60 + s
                elif len(parts) == 2:
                    m, s = map(int, parts)
                    return m * 60 + s
            except ValueError:
                pass
        
        # Try shorthand format (1h 30m 45s)
        total_seconds = 0
        pattern = r'(\d+)([hms])'
        matches = re.findall(pattern, duration_str.lower())
        
        for value, unit in matches:
            value = int(value)
            if unit == 'h':
                total_seconds += value * 3600
            elif unit == 'm':
                total_seconds += value * 60
            elif unit == 's':
                total_seconds += value
        
        return total_seconds if total_seconds > 0 else None


# Global singleton instance
_timedate_manager = None


def get_timedate_manager():
    """Get global TimeDateManager singleton."""
    global _timedate_manager
    if _timedate_manager is None:
        from core.config import Config
        config = Config()
        _timedate_manager = TimeDateManager(config)
    return _timedate_manager
