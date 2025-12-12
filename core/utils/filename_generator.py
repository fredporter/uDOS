"""
Filename Generator Utility

Universal filename generation with optional date-time-location formatting.
Implements uDOS filename convention: YYYY-MM-DD-HH-MM-SS-TILE-basename.ext

Part of v1.2.23 - Time-Space Integration Enhancement
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import re


class FilenameGenerator:
    """Generate standardized filenames with optional date-time-location."""
    
    # Standard separators
    DATE_SEP = "-"
    TIME_SEP = "-"
    COMPONENT_SEP = "-"
    
    # Format patterns
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H-%M-%S"
    DATETIME_FORMAT = f"{DATE_FORMAT}{COMPONENT_SEP}{TIME_FORMAT}"
    MILLISECOND_FORMAT = f"{DATETIME_FORMAT}{COMPONENT_SEP}%f"
    
    def __init__(self, config=None):
        """
        Initialize filename generator.
        
        Args:
            config: Optional Config instance for TILE detection
        """
        self.config = config
    
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
            "2025-12-12-backup.json"
            
            >>> gen.generate("workflow", ".upy", include_time=True)
            "2025-12-12-14-30-45-workflow.upy"
            
            >>> gen.generate("mission", ".upy", include_time=True, 
            ...              include_location=True, tile_code="AA340")
            "2025-12-12-14-30-45-AA340-mission.upy"
            
            >>> gen.generate("error", ".json", include_milliseconds=True)
            "2025-12-12-14-30-45-123-error.json"
        """
        parts = []
        
        # Use provided timestamp or current time
        now = timestamp or datetime.now()
        
        # Date component
        if include_date or include_time or include_milliseconds:
            parts.append(now.strftime(self.DATE_FORMAT))
        
        # Time component
        if include_time or include_milliseconds:
            parts.append(now.strftime(self.TIME_FORMAT))
        
        # Milliseconds component (first 3 digits)
        if include_milliseconds:
            ms = now.strftime("%f")[:3]  # First 3 digits of microseconds
            parts.append(ms)
        
        # Location component
        if include_location:
            location = tile_code or self._detect_tile()
            if location:
                parts.append(location)
        
        # Base name
        parts.append(base_name)
        
        # Combine parts
        filename = self.COMPONENT_SEP.join(parts)
        
        # Add extension
        if extension:
            if not extension.startswith("."):
                extension = "." + extension
            filename += extension
        
        return filename
    
    def generate_daily(self, base_name: str, extension: str = "") -> str:
        """Generate daily filename: YYYY-MM-DD-basename.ext"""
        return self.generate(base_name, extension, include_date=True)
    
    def generate_session(self, base_name: str, extension: str = "") -> str:
        """Generate session filename: YYYY-MM-DD-HH-MM-SS-basename.ext"""
        return self.generate(base_name, extension, include_time=True)
    
    def generate_instance(self, base_name: str, extension: str = "") -> str:
        """Generate instance filename: YYYY-MM-DD-HH-MM-SS-mmm-basename.ext"""
        return self.generate(base_name, extension, include_milliseconds=True)
    
    def generate_located(
        self, 
        base_name: str, 
        extension: str = "",
        tile_code: Optional[str] = None
    ) -> str:
        """Generate location-aware filename: YYYY-MM-DD-HH-MM-SS-TILE-basename.ext"""
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
                - date: YYYY-MM-DD or None
                - time: HH-MM-SS or None
                - milliseconds: mmm or None
                - tile: TILE code or None
                - base_name: Base filename
                - extension: File extension
        
        Example:
            >>> gen = FilenameGenerator()
            >>> gen.parse_filename("2025-12-12-14-30-45-AA340-mission.upy")
            {
                'date': '2025-12-12',
                'time': '14-30-45',
                'milliseconds': None,
                'tile': 'AA340',
                'base_name': 'mission',
                'extension': '.upy'
            }
        """
        result = {
            'date': None,
            'time': None,
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
        
        idx = 0
        
        # Check for date (YYYY-MM-DD pattern)
        if idx < len(parts) and self._is_date(parts[idx]):
            result['date'] = parts[idx]
            idx += 1
        
        # Check for time (HH-MM-SS pattern)
        if idx < len(parts) and self._is_time(parts[idx]):
            result['time'] = parts[idx]
            idx += 1
        
        # Check for milliseconds (3-digit pattern)
        if idx < len(parts) and self._is_milliseconds(parts[idx]):
            result['milliseconds'] = parts[idx]
            idx += 1
        
        # Check for TILE code (2-letter + digits pattern)
        if idx < len(parts) and self._is_tile(parts[idx]):
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
    
    def _is_date(self, part: str) -> bool:
        """Check if part matches YYYY-MM-DD pattern."""
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', part))
    
    def _is_time(self, part: str) -> bool:
        """Check if part matches HH-MM-SS pattern."""
        return bool(re.match(r'^\d{2}-\d{2}-\d{2}$', part))
    
    def _is_milliseconds(self, part: str) -> bool:
        """Check if part matches mmm pattern (3 digits)."""
        return bool(re.match(r'^\d{3}$', part))
    
    def _is_tile(self, part: str) -> bool:
        """Check if part matches TILE code pattern (e.g., AA340, JF57)."""
        return bool(re.match(r'^[A-Z]{2}\d+$', part))
    
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
        
        # Build timestamp string
        if parsed['time']:
            if parsed['milliseconds']:
                # Full timestamp with milliseconds
                ts_str = f"{parsed['date']} {parsed['time']}.{parsed['milliseconds']}"
                fmt = "%Y-%m-%d %H-%M-%S.%f"
            else:
                # Date and time only
                ts_str = f"{parsed['date']} {parsed['time']}"
                fmt = "%Y-%m-%d %H-%M-%S"
        else:
            # Date only
            ts_str = parsed['date']
            fmt = "%Y-%m-%d"
        
        try:
            # Replace separators for parsing
            ts_str = ts_str.replace('-', ' ')
            return datetime.strptime(ts_str, fmt.replace('-', ' '))
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
        "2025-12-12-backup.json",
        "2025-12-12-14-30-45-export.json",
        "2025-12-12-14-30-45-123-error-context.json",
        "2025-12-12-14-30-45-AA340-mission.upy",
    ]
    
    for filename in test_files:
        print(f"{filename}:")
        parsed = gen.parse_filename(filename)
        for key, value in parsed.items():
            if value:
                print(f"  {key}: {value}")
        print()
