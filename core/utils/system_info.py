"""
uDOS v1.0.29 - System Information Utilities

Provides system information detection for user configuration.
"""

import os
import platform
from pathlib import Path
from typing import Tuple


def get_system_timezone() -> Tuple[str, str]:
    """
    Detect system timezone and extract city name.

    Returns:
        Tuple of (timezone_string, city_name)
        Example: ("America/New_York", "New York")
                 ("Australia/Sydney", "Sydney")
                 ("Europe/London", "London")

    Falls back to UTC if detection fails.
    """
    try:
        # Try to read timezone from /etc/localtime symlink (macOS/Linux)
        if os.path.islink('/etc/localtime'):
            tz_link = os.readlink('/etc/localtime')
            # Extract timezone from path like: /var/db/timezone/zoneinfo/Australia/Sydney
            parts = tz_link.split('/')

            if len(parts) >= 2:
                # Get last two parts: Region/City
                region = parts[-2]
                city_raw = parts[-1]
                timezone = f"{region}/{city_raw}"

                # Convert city name: Sydney -> Sydney, New_York -> New York
                city_name = city_raw.replace('_', ' ')

                return (timezone, city_name)

        # Fallback: Try reading /etc/timezone file (some Linux distros)
        timezone_file = Path('/etc/timezone')
        if timezone_file.exists():
            timezone = timezone_file.read_text().strip()
            # Extract city from timezone string
            if '/' in timezone:
                city_raw = timezone.split('/')[-1]
                city_name = city_raw.replace('_', ' ')
                return (timezone, city_name)
            return (timezone, timezone)

        # Last resort: Use environment variable
        tz_env = os.environ.get('TZ', '')
        if tz_env and '/' in tz_env:
            city_raw = tz_env.split('/')[-1]
            city_name = city_raw.replace('_', ' ')
            return (tz_env, city_name)

    except Exception:
        pass

    # Final fallback
    return ("UTC", "UTC")


def get_system_info() -> dict:
    """
    Get comprehensive system information.

    Returns:
        dict with system details including OS, hostname, timezone, etc.
    """
    timezone, city = get_system_timezone()

    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'hostname': platform.node(),
        'timezone': timezone,
        'location_default': city,
        'python_version': platform.python_version(),
        'architecture': platform.machine()
    }


if __name__ == '__main__':
    # Test the functions
    print("System Information Test")
    print("=" * 50)

    tz, city = get_system_timezone()
    print(f"Timezone: {tz}")
    print(f"Default Location: {city}")
    print()

    info = get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
