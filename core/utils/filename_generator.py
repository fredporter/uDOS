"""
Filename Generator Utility

Universal filename generation with compact date-time-timezone-location formatting.
Implements uDOS filename convention: YYYYMMDD-HHMMSSTZ-TILE-basename.ext

Format Examples:
- Date only: 20251212-backup.json
- Session: 20251212-143045AEST-workflow.upy
- Located: 20251212-143045AEST-AA340-mission.upy

Part of v1.2.23 - Time-Space Integration Enhancement
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import re
import json


class FilenameGenerator:
    """Generate standardized filenames with compact date-time-timezone-location format."""
    
    # Standard separators
    COMPONENT_SEP = "-"
    
    # Compact format patterns (no internal separators)
    DATE_FORMAT = "%Y%m%d"    # YYYYMMDD
    TIME_FORMAT = "%H%M%S"    # HHMMSS
    
    # Timezone abbreviation mapping
    TIMEZONE_ABBR = {
        "UTC": "UTC",
        "America/New_York": "EST",
        "America/Los_Angeles": "PST",
        "Europe/London": "GMT",
        "Europe/Paris": "CET",
        "Asia/Tokyo": "JST",
        "Australia/Sydney": "AEST",
    }
    
    def __init__(self, config=None):
        """
        Initialize filename generator.
        
        Args:
            config: Optional Config instance for location detection
        """
        self.config = config
        self.timezones_data = self._load_timezones()
        self.current_timezone = self._get_current_timezone()
    
    def _load_timezones(self) -> dict:
        """Load timezone data from timezones.json."""
        try:
            from pathlib import Path
            # Try to find timezones.json in core/data/
            project_root = Path(__file__).parent.parent.parent
            tz_file = project_root / "core" / "data" / "timezones.json"
            if tz_file.exists():
                with open(tz_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"zones": {}, "tiles": {}}
    
    def _get_current_timezone(self) -> str:
        """Get current timezone from config or environment."""
        if self.config:
            tz = self.config.get_env('TIMEZONE', 'UTC')
            return tz
        return 'UTC'
    
    def _get_timezone_abbr(self, timezone_name: str = None) -> str:
        """Get timezone abbreviation (2-4 characters)."""
        tz = timezone_name or self.current_timezone
        return self.TIMEZONE_ABBR.get(tz, 'UTC')
    
    def generate(
        self,
        base_name: str,
        extension: str = "",
        include_date: bool = False,
        include_time: bool = False,
        include_milliseconds: bool = False,
        include_location: bool = False,
        tile_code: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> str:
        """
        Generate standardized filename.
        
        Args:
            base_name: Base filename (e.g., "backup", "workflow")
            extension: File extension (with or without leading dot)
            include_date: Include YYYY-MM-DD prefix
            include_time: Include HH-MM-SS after date
            include_milliseconds: Include milliseconds (implies time+date)
            include_location: Include TILE code
            tile_code: Explicit TILE code (or detect from config)
            timestamp: Explicit timestamp (or use current time)
        
        Returns:
            Formatted filename following uDOS convention
        
        Examples:
            >>> gen = FilenameGenerator()
            >>> gen.generate("backup", ".json", include_date=True)
            "20251212-backup.json"
            
            >>> gen.generate("workflow", ".upy", include_time=True)
            "20251212-143045AEST-workflow.upy"
            
            >>> gen.generate("mission", ".upy", include_time=True, 
            ...              include_location=True, tile_code="AA340")
            "20251212-143045AEST-AA340-mission.upy"
            
            >>> gen.generate("error", ".json", include_milliseconds=True)
            "20251212-143045AEST-123-error.json"
        """
        parts = []
        
        # Use provided timestamp or current time
        now = timestamp or datetime.now()
        
        # Date component (always included if time is included)
        if include_date or include_time or include_milliseconds:
            date_str = now.strftime(self.DATE_FORMAT)  # YYYYMMDD
            
            # Time component (compact with timezone)
            if include_time or include_milliseconds:
                time_str = now.strftime(self.TIME_FORMAT)  # HHMMSS
                tz_abbr = self._get_timezone_abbr()  # AEST, UTC, etc.
                
                # Milliseconds component (appended after timezone if needed)
                if include_milliseconds:
                    ms = now.strftime("%f")[:3]  # First 3 digits
                    time_tz = f"{date_str}{self.COMPONENT_SEP}{time_str}{tz_abbr}{self.COMPONENT_SEP}{ms}"
                else:
                    time_tz = f"{date_str}{self.COMPONENT_SEP}{time_str}{tz_abbr}"
                parts.append(time_tz)
            else:
                # Date only (no timezone suffix)
                parts.append(date_str)
        
        # Location component
        if include_location:
            location = tile_code or self._detect_tile()
            if location:
                parts.append(location)
        
        # Base name
        parts.append(base_name)
        
        # Combine parts (only separate with - if multiple components)
        if len(parts) == 1:
            filename = parts[0]
        else:
            # First part is date-time-tz, rest are separate
            filename = self.COMPONENT_SEP.join(parts)
        
        # Add extension
        if extension:
            if not extension.startswith("."):
                extension = "." + extension
            filename += extension
        
        return filename
    
    def generate_daily(self, base_name: str, extension: str = "") -> str:
        """Generate daily filename: YYYYMMDD-basename.ext"""
        return self.generate(base_name, extension, include_date=True)
    
    def generate_session(self, base_name: str, extension: str = "") -> str:
        """Generate session filename: YYYYMMDD-HHMMSSTZ-basename.ext"""
        return self.generate(base_name, extension, include_time=True)
    
    def generate_instance(self, base_name: str, extension: str = "") -> str:
        """Generate instance filename: YYYYMMDD-HHMMSSTZ-mmm-basename.ext"""
        return self.generate(base_name, extension, include_milliseconds=True)
    
    def generate_located(
        self, 
        base_name: str, 
        extension: str = "",
        tile_code: Optional[str] = None
    ) -> str:
        """Generate location-aware filename: YYYYMMDD-HHMMSSTZ-TILE-basename.ext"""
        return self.generate(
            base_name, 
            extension, 
            include_time=True,
            include_location=True,
            tile_code=tile_code
        )
    
    def parse_filename(self, filename: str) -> dict:
        """
        Parse uDOS-formatted filename into components.
        
        Args:
            filename: Filename to parse
        
        Returns:
            Dictionary with parsed components:
                - date: YYYYMMDD or None
                - time: HHMMSS or None
                - timezone: TZ abbreviation or None
                - milliseconds: mmm or None
                - tile: TILE code or None
                - base_name: Base filename
                - extension: File extension
        
        Example:
            >>> gen = FilenameGenerator()
            >>> gen.parse_filename("20251212-143045AEST-AA340-mission.upy")
            {
                'date': '20251212',
                'time': '143045',
                'timezone': 'AEST',
                'milliseconds': None,
                'tile': 'AA340',
                'base_name': 'mission',
                'extension': '.upy'
            }
        """
        result = {
            'date': None,
            'time': None,
            'timezone': None,
            'milliseconds': None,
            'tile': None,
            'base_name': None,
            'extension': None
        }
        
        # Split extension
        path = Path(filename)
        name = path.stem
        result['extension'] = path.suffix
        
        # Split components
        parts = name.split(self.COMPONENT_SEP)
        
        if not parts:
            return result
        
        idx = 0
        
        # Check first part for date (YYYYMMDD) or date-time combo
        if idx < len(parts):
            first_part = parts[idx]
            
            # Check for YYYYMMDD (exactly 8 digits)
            if re.match(r'^\d{8}$', first_part):
                result['date'] = first_part
                idx += 1
        
        # Check next part for time+timezone (HHMMSSTZ where TZ is 2-4 letters)
        if idx < len(parts):
            time_part = parts[idx]
            # Match HHMMSS (6 digits) followed by 2-4 uppercase letters
            time_match = re.match(r'^(\d{6})([A-Z]{2,4})$', time_part)
            if time_match:
                result['time'] = time_match.group(1)
                result['timezone'] = time_match.group(2)
                idx += 1
        
        # Check for milliseconds (3-digit pattern)
        if idx < len(parts) and re.match(r'^\d{3}$', parts[idx]):
            result['milliseconds'] = parts[idx]
            idx += 1
        
        # Check for TILE code (2-letter column + number, optional -layer)
        if idx < len(parts) and re.match(r'^[A-Z]{2}\d+(-\d+)?$', parts[idx]):
            result['tile'] = parts[idx]
            idx += 1
        
        # Remaining parts are base name
        if idx < len(parts):
            result['base_name'] = self.COMPONENT_SEP.join(parts[idx:])
        
        return result
    
    def _detect_tile(self) -> Optional[str]:
        """Detect current TILE code from config."""
        if not self.config:
            return None
        
        # Try to get from config
        tile = self.config.get('current_tile')
        if tile:
            return tile
        
        # Try to detect from timezone
        try:
            from core.services.timedate_manager import TimeDateManager
            tdm = TimeDateManager(self.config)
            info = tdm.get_current_timezone_info()
            if info and info.tile:
                return info.tile
        except Exception:
            pass
        
        return None
    

    
    def get_timestamp_from_filename(self, filename: str) -> Optional[datetime]:
        """
        Extract timestamp from filename.
        
        Args:
            filename: Filename to parse
        
        Returns:
            datetime object or None if no timestamp found
        """
        parsed = self.parse_filename(filename)
        
        if not parsed['date']:
            return None
        
        # Build timestamp string from compact format
        date_str = parsed['date']  # YYYYMMDD
        
        if parsed['time']:
            time_str = parsed['time']  # HHMMSS
            if parsed['milliseconds']:
                # Full timestamp with milliseconds
                ts_str = f"{date_str}{time_str}{parsed['milliseconds']}"
                fmt = "%Y%m%d%H%M%S%f"
            else:
                # Date and time only
                ts_str = f"{date_str}{time_str}"
                fmt = "%Y%m%d%H%M%S"
        else:
            # Date only
            ts_str = date_str
            fmt = "%Y%m%d"
        
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            return None


# Convenience functions for direct use
def generate_filename(
    base_name: str,
    extension: str = "",
    include_date: bool = False,
    include_time: bool = False,
    include_milliseconds: bool = False,
    include_location: bool = False,
    tile_code: Optional[str] = None,
    config=None
) -> str:
    """
    Generate standardized filename (convenience wrapper).
    
    See FilenameGenerator.generate() for full documentation.
    """
    gen = FilenameGenerator(config)
    return gen.generate(
        base_name=base_name,
        extension=extension,
        include_date=include_date,
        include_time=include_time,
        include_milliseconds=include_milliseconds,
        include_location=include_location,
        tile_code=tile_code
    )


def generate_daily(base_name: str, extension: str = "", config=None) -> str:
    """Generate daily filename: YYYY-MM-DD-basename.ext (convenience wrapper)."""
    gen = FilenameGenerator(config)
    return gen.generate_daily(base_name, extension)


def generate_session(base_name: str, extension: str = "", config=None) -> str:
    """Generate session filename: YYYY-MM-DD-HH-MM-SS-basename.ext (convenience wrapper)."""
    gen = FilenameGenerator(config)
    return gen.generate_session(base_name, extension)


def generate_instance(base_name: str, extension: str = "", config=None) -> str:
    """Generate instance filename with milliseconds: YYYY-MM-DD-HH-MM-SS-mmm-basename.ext (convenience wrapper)."""
    gen = FilenameGenerator(config)
    return gen.generate_instance(base_name, extension)


def generate_located(base_name: str, extension: str = "", tile_code: Optional[str] = None, config=None) -> str:
    """Generate located filename: YYYY-MM-DD-HH-MM-SS-TILE-basename.ext (convenience wrapper)."""
    gen = FilenameGenerator(config)
    return gen.generate_located(base_name, extension, tile_code)


def parse_filename(filename: str) -> dict:
    """
    Parse uDOS-formatted filename (convenience wrapper).
    
    See FilenameGenerator.parse_filename() for full documentation.
    """
    gen = FilenameGenerator()
    return gen.parse_filename(filename)


if __name__ == "__main__":
    # Demo usage
    gen = FilenameGenerator()
    
    print("=== Filename Generation Examples ===")
    print()
    
    print("Daily file:")
    print(f"  {gen.generate_daily('backup', '.json')}")
    print()
    
    print("Session file:")
    print(f"  {gen.generate_session('export', '.json')}")
    print()
    
    print("Instance file (with milliseconds):")
    print(f"  {gen.generate_instance('error-context', '.json')}")
    print()
    
    print("Located file (with TILE code):")
    print(f"  {gen.generate_located('mission', '.upy', tile_code='AA340')}")
    print()
    
    print("Custom combination:")
    print(f"  {gen.generate('workflow', '.upy', include_time=True, include_location=True, tile_code='JF57')}")
    print()
    
    print("=== Filename Parsing Examples ===")
    print()
    
    test_files = [
        "20251212-backup.json",
        "20251212-143045AEST-export.json",
        "20251212-143045AEST-123-error-context.json",
        "20251212-143045AEST-AA340-mission.upy",
    ]
    
    for filename in test_files:
        print(f"{filename}:")
        parsed = gen.parse_filename(filename)
        for key, value in parsed.items():
            if value:
                print(f"  {key}: {value}")
        print()
