"""
Timezone Fuzzy Matching & Alias Resolution
=============================================

Provides:
  - IANA timezone validation
  - Common timezone alias support (AEST → Australia/Brisbane, EST → America/New_York)
  - Fuzzy matching for typos and partial matches
  - Case-insensitive matching

Usage:
    tz_resolver = TimezoneFuzzyResolver()
    result = tz_resolver.resolve("aest")  # Returns "Australia/Brisbane"
    result = tz_resolver.resolve("EST")   # Returns "America/New_York"
    result = tz_resolver.resolve("America/los_angeles")  # Returns "America/Los_Angeles"

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-01-31
"""

from typing import Optional, Dict, List
from difflib import get_close_matches

from core.services.logging_api import get_logger

logger = get_logger("timezone-fuzzy")


class TimezoneFuzzyResolver:
    """Resolve timezone strings with fuzzy matching and aliases."""

    # Common timezone aliases (short → IANA)
    TIMEZONE_ALIASES = {
        # Australian
        "aest": "Australia/Brisbane",      # Australian Eastern Standard
        "aedt": "Australia/Sydney",         # Australian Eastern Daylight
        "acst": "Australia/Adelaide",       # Australian Central Standard
        "acdt": "Australia/Adelaide",       # Australian Central Daylight
        "awst": "Australia/Perth",          # Australian Western Standard
        "aswt": "Australia/Perth",          # Australian Western (alternate)

        # US/North America
        "est": "America/New_York",         # Eastern Standard
        "edt": "America/New_York",         # Eastern Daylight
        "cst": "America/Chicago",          # Central Standard
        "cdt": "America/Chicago",          # Central Daylight
        "mst": "America/Denver",           # Mountain Standard
        "mdt": "America/Denver",           # Mountain Daylight
        "pst": "America/Los_Angeles",      # Pacific Standard
        "pdt": "America/Los_Angeles",      # Pacific Daylight
        "akst": "America/Anchorage",       # Alaska Standard
        "akdt": "America/Anchorage",       # Alaska Daylight
        "hst": "Pacific/Honolulu",         # Hawaii-Aleutian Standard
        "hdt": "Pacific/Honolulu",         # Hawaii-Aleutian Daylight

        # Europe
        "gmt": "Europe/London",            # Greenwich Mean Time
        "bst": "Europe/London",            # British Summer Time
        "cet": "Europe/Paris",             # Central European Time
        "cedt": "Europe/Paris",            # Central European Daylight
        "wet": "Europe/Lisbon",            # Western European Time
        "wedt": "Europe/Lisbon",           # Western European Daylight

        # Asia
        "ist": "Asia/Kolkata",             # Indian Standard Time
        "jst": "Asia/Tokyo",               # Japan Standard Time
        "cst_cn": "Asia/Shanghai",         # China Standard Time
        "sgt": "Asia/Singapore",           # Singapore Time
        "myt": "Asia/Kuala_Lumpur",        # Malaysia Time
        "bkt": "Asia/Bangkok",             # Bangkok Time
        "ict": "Asia/Bangkok",             # Indochina Time

        # UTC variants
        "utc": "UTC",
        "utc+0": "UTC",
        "gmt+0": "UTC",

        # City aliases (common shortcuts)
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "tokyo": "Asia/Tokyo",
        "sydney": "Australia/Sydney",
        "brisbane": "Australia/Brisbane",
        "perth": "Australia/Perth",
        "newyork": "America/New_York",
        "losangeles": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "denver": "America/Denver",
        "toronto": "America/Toronto",
        "vancouver": "America/Vancouver",
        "mexico": "America/Mexico_City",
        "santiag": "America/Santiago",
        "saopau": "America/Sao_Paulo",
        "buenos": "America/Argentina/Buenos_Aires",
        "johannesburg": "Africa/Johannesburg",
        "dubai": "Asia/Dubai",
        "bangkok": "Asia/Bangkok",
        "singapore": "Asia/Singapore",
        "hongkong": "Asia/Hong_Kong",
        "shanghai": "Asia/Shanghai",
        "delhi": "Asia/Kolkata",
        "mumbai": "Asia/Kolkata",
        "istanbul": "Europe/Istanbul",
        "moscow": "Europe/Moscow",
        "auckland": "Pacific/Auckland",
    }

    def __init__(self):
        """Initialize resolver with timezone dataset."""
        self.aliases = self.TIMEZONE_ALIASES.copy()
        self.aliases_lower = {k.lower(): v for k, v in self.aliases.items()}

    def resolve(self, timezone_str: str) -> Optional[str]:
        """Resolve a timezone string to IANA format.

        Args:
            timezone_str: Timezone as IANA string, alias, or partial match

        Returns:
            IANA timezone string if valid, None otherwise

        Examples:
            "aest" → "Australia/Brisbane"
            "America/los_angeles" → "America/Los_Angeles"
            "EST" → "America/New_York"
            "tokyo" → "Asia/Tokyo"
        """
        if not timezone_str:
            return None

        tz_input = timezone_str.strip()

        # 1. Try exact IANA match (case-insensitive)
        tz_normalized = self._normalize_iana(tz_input)
        if tz_normalized and self._is_valid_iana(tz_normalized):
            return tz_normalized

        # 2. Try alias match (case-insensitive)
        tz_lower = tz_input.lower()
        if tz_lower in self.aliases_lower:
            return self.aliases_lower[tz_lower]

        # 3. Try fuzzy match on aliases
        close_aliases = get_close_matches(tz_lower, self.aliases_lower.keys(), n=1, cutoff=0.6)
        if close_aliases:
            matched_alias = close_aliases[0]
            logger.debug(f"[LOCAL] Fuzzy matched '{tz_input}' → alias '{matched_alias}'")
            return self.aliases_lower[matched_alias]

        # 4. Try fuzzy match on IANA zones (if we have the list)
        try:
            from zoneinfo import available_timezones
            iana_zones = sorted(available_timezones())
            close_iana = get_close_matches(tz_lower, [z.lower() for z in iana_zones], n=1, cutoff=0.75)
            if close_iana:
                # Find the original-case zone
                matched_zone = next((z for z in iana_zones if z.lower() == close_iana[0]), None)
                if matched_zone:
                    logger.debug(f"[LOCAL] Fuzzy matched '{tz_input}' → IANA '{matched_zone}'")
                    return matched_zone
        except Exception as e:
            logger.debug(f"[LOCAL] Could not load IANA zones for fuzzy match: {e}")

        logger.warning(f"[LOCAL] Could not resolve timezone: {tz_input}")
        return None

    def is_valid(self, timezone_str: str) -> bool:
        """Check if a timezone string is valid (resolvable).

        Args:
            timezone_str: Timezone string to validate

        Returns:
            True if valid and resolvable, False otherwise
        """
        return self.resolve(timezone_str) is not None

    def _normalize_iana(self, tz_str: str) -> Optional[str]:
        """Normalize IANA timezone string (fix casing).

        Examples:
            "america/los_angeles" → "America/Los_Angeles"
            "Europe/paris" → "Europe/Paris"

        Args:
            tz_str: Timezone string (potentially mis-cased)

        Returns:
            Properly cased IANA timezone, or None if invalid
        """
        if "/" not in tz_str:
            return None

        parts = tz_str.split("/")
        normalized = "/".join(part.capitalize() if part else "" for part in parts)

        if self._is_valid_iana(normalized):
            return normalized

        return None

    @staticmethod
    def _is_valid_iana(tz_str: str) -> bool:
        """Check if a timezone string is a valid IANA timezone.

        Args:
            tz_str: Timezone string to validate

        Returns:
            True if valid IANA timezone, False otherwise
        """
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(tz_str)
            return True
        except Exception:
            return False

    def get_suggestions(self, partial: str, limit: int = 5) -> List[str]:
        """Get timezone suggestions for partial input.

        Args:
            partial: Partial timezone string or alias
            limit: Maximum number of suggestions

        Returns:
            List of matching timezone strings (IANA)

        Example:
            get_suggestions("aus") → ["Australia/Brisbane", "Australia/Sydney", ...]
        """
        if not partial:
            return []

        partial_lower = partial.lower()
        matches = []

        # Match aliases
        for alias, iana in self.aliases_lower.items():
            if alias.startswith(partial_lower) and iana not in matches:
                matches.append(iana)

        # Match IANA zones
        try:
            from zoneinfo import available_timezones
            iana_zones = sorted(available_timezones())
            for zone in iana_zones:
                if zone.lower().startswith(partial_lower):
                    matches.append(zone)
        except Exception:
            pass

        return matches[:limit]


# Singleton instance
_resolver = None


def get_timezone_resolver() -> TimezoneFuzzyResolver:
    """Get or create singleton resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = TimezoneFuzzyResolver()
    return _resolver
