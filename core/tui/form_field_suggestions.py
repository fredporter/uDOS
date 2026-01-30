"""
Form Field Suggestions - Smart Autocomplete & Predictions

Provides intelligent suggestions for setup form fields:
- Timezone autocomplete from IANA list + aliases
- Location lookup via location_service (city names, grid locations)
- OS type detection from system
- DOB suggestion (optional)
- Username suggestion from system user
- Password strength tips

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-31
"""

import subprocess
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from core.services.logging_manager import get_logger

logger = get_logger('form-suggestions')

# Common IANA timezones by region
IANA_TIMEZONES = {
    'UTC': 'UTC',
    'Australia': [
        'Australia/Sydney', 'Australia/Adelaide', 'Australia/Brisbane',
        'Australia/Perth', 'Australia/Hobart', 'Australia/Darwin'
    ],
    'US': [
        'US/Eastern', 'US/Central', 'US/Mountain', 'US/Pacific',
        'America/New_York', 'America/Los_Angeles', 'America/Chicago',
        'America/Denver', 'America/Anchorage', 'US/Hawaii'
    ],
    'Europe': [
        'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Madrid',
        'Europe/Rome', 'Europe/Amsterdam', 'Europe/Brussels', 'Europe/Vienna',
        'Europe/Prague', 'Europe/Warsaw', 'Europe/Athens', 'Europe/Dublin'
    ],
    'Asia': [
        'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Hong_Kong', 'Asia/Singapore',
        'Asia/Bangkok', 'Asia/Dubai', 'Asia/Kolkata', 'Asia/Seoul',
        'Asia/Manila', 'Asia/Jakarta', 'Asia/Ho_Chi_Minh'
    ],
    'Pacific': [
        'Pacific/Auckland', 'Pacific/Fiji', 'Pacific/Honolulu',
        'Pacific/Apia', 'Pacific/Tongatapu'
    ],
    'Africa': [
        'Africa/Cairo', 'Africa/Johannesburg', 'Africa/Lagos',
        'Africa/Nairobi', 'Africa/Casablanca', 'Africa/Tunis'
    ],
    'South America': [
        'America/Sao_Paulo', 'America/Argentina/Buenos_Aires',
        'America/Santiago', 'America/Lima', 'America/Bogota'
    ],
    'Canada': [
        'Canada/Eastern', 'Canada/Central', 'Canada/Mountain',
        'Canada/Pacific', 'Canada/Atlantic', 'Canada/Newfoundland'
    ]
}


class FormFieldSuggestions:
    """Smart suggestion system for form fields."""

    def __init__(self):
        """Initialize suggestion provider."""
        self.timezone_cache = None
        self.location_cache = None

    def get_timezone_suggestions(self, partial: str = '') -> List[str]:
        """Get timezone suggestions with autocomplete.
        
        Args:
            partial: Partial timezone string entered by user
            
        Returns:
            List of matching timezone suggestions
        """
        suggestions = []
        
        # First add UTC and aliases
        if not partial or 'utc' in partial.lower():
            suggestions.append('UTC')
        
        # Load full IANA timezone list and filter
        all_timezones = self._get_all_iana_timezones()
        
        partial_lower = partial.lower()
        for tz in all_timezones:
            if partial_lower in tz.lower():
                suggestions.append(tz)
        
        # Limit to top 5 suggestions
        return suggestions[:5]

    def get_location_suggestions(self, partial: str = '') -> List[str]:
        """Get location suggestions via location_service.
        
        Args:
            partial: Partial location string entered by user
            
        Returns:
            List of matching location suggestions
        """
        if not partial or len(partial) < 2:
            return []
        
        suggestions = []
        
        try:
            # Try to use location_service if available
            from core.location_service import LocationService
            service = LocationService()
            
            # Search for matching cities
            matches = service.search_cities(partial, limit=5)
            for match in matches:
                if isinstance(match, dict):
                    city = match.get('city', '')
                    region = match.get('region', '')
                    if city:
                        display = f"{city}, {region}" if region else city
                        suggestions.append(display)
                else:
                    suggestions.append(str(match))
            
            logger.debug(f"[LOCAL] Location suggestions for '{partial}': {suggestions}")
            return suggestions
            
        except ImportError:
            logger.debug("location_service not available, using fallback suggestions")
        except Exception as e:
            logger.debug(f"[LOCAL] Error getting location suggestions: {e}")
        
        # Fallback: common cities
        common_cities = [
            'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide',
            'London', 'Paris', 'Berlin', 'New York', 'Los Angeles',
            'San Francisco', 'Chicago', 'Toronto', 'Vancouver',
            'Tokyo', 'Shanghai', 'Hong Kong', 'Singapore', 'Bangkok',
            'Mumbai', 'Delhi', 'Cairo', 'Dubai', 'Moscow',
            'São Paulo', 'Mexico City', 'Buenos Aires', 'Toronto'
        ]
        
        partial_lower = partial.lower()
        for city in common_cities:
            if partial_lower in city.lower():
                suggestions.append(city)
        
        return suggestions[:5]

    def get_os_detection(self) -> Optional[str]:
        """Detect OS type from system.
        
        Returns:
            Detected OS type: 'alpine', 'ubuntu', 'mac', 'windows', or None
        """
        try:
            # Check platform
            import platform
            system = platform.system().lower()
            
            if system == 'darwin':
                return 'mac'
            elif system == 'linux':
                # Check if Alpine, Ubuntu, etc.
                try:
                    with open('/etc/os-release', 'r') as f:
                        content = f.read().lower()
                        if 'alpine' in content:
                            return 'alpine'
                        elif 'ubuntu' in content:
                            return 'ubuntu'
                        else:
                            return 'ubuntu'  # Default to ubuntu for Linux
                except:
                    return 'ubuntu'
            elif system == 'windows':
                return 'windows'
            
            logger.debug(f"[LOCAL] Detected OS: {system}")
            return system
        except Exception as e:
            logger.debug(f"[LOCAL] Could not detect OS: {e}")
            return None

    def get_username_suggestion(self) -> Optional[str]:
        """Suggest username from system user.
        
        Returns:
            Suggested username or None
        """
        try:
            # Try to get current user
            import getpass
            username = getpass.getuser()
            
            # Clean up: lowercase, remove special chars if any
            username = username.lower()
            username = ''.join(c for c in username if c.isalnum() or c in '-_')
            
            if username and len(username) >= 3:
                logger.debug(f"[LOCAL] Username suggestion: {username}")
                return username
        except Exception as e:
            logger.debug(f"[LOCAL] Could not get username suggestion: {e}")
        
        return None

    def get_timezone_from_location(self, location: str) -> Optional[str]:
        """Infer timezone from location name.
        
        Args:
            location: Location/city name
            
        Returns:
            Suggested IANA timezone or None
        """
        if not location:
            return None
        
        # Simple mapping of common cities to timezones
        city_tz_map = {
            'sydney': 'Australia/Sydney',
            'melbourne': 'Australia/Melbourne',
            'brisbane': 'Australia/Brisbane',
            'perth': 'Australia/Perth',
            'adelaide': 'Australia/Adelaide',
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'berlin': 'Europe/Berlin',
            'new york': 'US/Eastern',
            'los angeles': 'US/Pacific',
            'san francisco': 'US/Pacific',
            'chicago': 'US/Central',
            'denver': 'US/Mountain',
            'toronto': 'Canada/Eastern',
            'vancouver': 'Canada/Pacific',
            'tokyo': 'Asia/Tokyo',
            'shanghai': 'Asia/Shanghai',
            'hong kong': 'Asia/Hong_Kong',
            'singapore': 'Asia/Singapore',
            'bangkok': 'Asia/Bangkok',
            'mumbai': 'Asia/Kolkata',
            'delhi': 'Asia/Kolkata',
            'dubai': 'Asia/Dubai',
            'cairo': 'Africa/Cairo',
            'moscow': 'Europe/Moscow',
            'são paulo': 'America/Sao_Paulo',
            'buenos aires': 'America/Argentina/Buenos_Aires',
            'mexico city': 'America/Mexico_City',
        }
        
        location_lower = location.lower().strip()
        
        # Direct match
        if location_lower in city_tz_map:
            tz = city_tz_map[location_lower]
            logger.debug(f"[LOCAL] Location '{location}' → timezone '{tz}'")
            return tz
        
        # Try location_service for more accurate mapping
        try:
            from core.location_service import LocationService
            service = LocationService()
            location_data = service.lookup(location)
            
            if location_data and 'timezone' in location_data:
                tz = location_data['timezone']
                logger.debug(f"[LOCAL] Location service: '{location}' → '{tz}'")
                return tz
        except Exception as e:
            logger.debug(f"[LOCAL] Could not lookup location in service: {e}")
        
        return None

    @staticmethod
    def _get_all_iana_timezones() -> List[str]:
        """Get complete list of IANA timezones.
        
        Returns:
            List of IANA timezone strings
        """
        all_timezones = ['UTC']
        
        for region, zones in IANA_TIMEZONES.items():
            if isinstance(zones, list):
                all_timezones.extend(zones)
            else:
                all_timezones.append(zones)
        
        return sorted(list(set(all_timezones)))

    def get_dob_format_hint(self) -> str:
        """Get a helpful DOB format hint with today's date.
        
        Returns:
            Formatted string like "YYYY-MM-DD (e.g., 1990-01-15)"
        """
        today = datetime.now().strftime('%Y-%m-%d')
        return f"YYYY-MM-DD format (e.g., 1990-01-15 or today: {today})"

    def get_password_strength_tips(self) -> str:
        """Get password strength requirements.
        
        Returns:
            Formatted string with password tips
        """
        return (
            "Minimum 8 characters: at least 1 uppercase, "
            "1 lowercase, and 1 number (e.g., MyPass123)"
        )

    def get_role_description(self, role: str) -> Optional[str]:
        """Get description for a role.
        
        Args:
            role: Role name
            
        Returns:
            Role description or None
        """
        descriptions = {
            'admin': 'Full access to all features and settings',
            'user': 'Standard user with most features available',
            'ghost': 'Demo/test mode with limited access (default)',
        }
        return descriptions.get(role.lower())

    def get_os_description(self, os_type: str) -> Optional[str]:
        """Get description for OS type.
        
        Args:
            os_type: OS type
            
        Returns:
            OS description or None
        """
        descriptions = {
            'alpine': 'Alpine Linux (lightweight, minimal)',
            'ubuntu': 'Ubuntu Linux (standard, full-featured)',
            'mac': 'macOS (Apple)',
            'windows': 'Windows',
        }
        return descriptions.get(os_type.lower())

    def format_suggestion(self, value: str, hint: str = '') -> str:
        """Format a suggestion for display.
        
        Args:
            value: Suggestion value
            hint: Optional hint text
            
        Returns:
            Formatted suggestion string
        """
        if hint:
            return f"{value} — {hint}"
        return value
