"""
Location Service - Query and manipulate location data
Provides utilities for timezone calculations, distance, pathfinding, etc.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path


class LocationService:
    """Service for managing game world locations and timezone calculations."""

    def __init__(self, locations_file: Optional[str] = None):
        """
        Initialize location service.

        Args:
            locations_file: Path to locations.json (defaults to core/locations.json)
        """
        if locations_file is None:
            # Auto-locate from core directory
            core_path = Path(__file__).parent
            locations_file = core_path / "locations.json"

        self.locations_file = locations_file
        self._locations_data = None
        self._locations_by_id = None
        self._load_locations()

    def _load_locations(self):
        """Load locations from JSON file."""
        try:
            with open(self.locations_file, "r") as f:
                self._locations_data = json.load(f)

            # Build index by ID for fast lookup
            self._locations_by_id = {}
            for loc in self._locations_data.get("locations", []):
                self._locations_by_id[loc["id"]] = loc
        except FileNotFoundError:
            raise FileNotFoundError(f"Locations file not found: {self.locations_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in locations file: {self.locations_file}")

    def get_location(self, location_id: str) -> Optional[Dict]:
        """Get a location by ID."""
        return self._locations_by_id.get(location_id)

    def get_all_locations(self) -> List[Dict]:
        """Get all locations."""
        return self._locations_data.get("locations", [])

    def get_locations_by_region(self, region: str) -> List[Dict]:
        """Get all locations in a region."""
        return [loc for loc in self.get_all_locations() if loc.get("region") == region]

    def get_locations_by_continent(self, continent: str) -> List[Dict]:
        """Get all locations on a continent."""
        return [
            loc for loc in self.get_all_locations() if loc.get("continent") == continent
        ]

    def get_locations_by_type(self, location_type: str) -> List[Dict]:
        """Get locations by type (major-city, geographical-landmark, etc.)."""
        return [
            loc for loc in self.get_all_locations() if loc.get("type") == location_type
        ]

    def get_locations_by_scale(self, scale: str) -> List[Dict]:
        """Get locations by distance scale (terrestrial, orbital, etc.)."""
        return [loc for loc in self.get_all_locations() if loc.get("scale") == scale]

    def parse_timezone(self, tz_str: str) -> timezone:
        """
        Parse timezone string to Python timezone object.

        Examples: "UTC+0", "UTC+9", "UTC-5", "UTC+5:30"
        """
        # Remove 'UTC' prefix
        tz_str = tz_str.replace("UTC", "")

        # Parse offset
        if ":" in tz_str:
            # Format: +5:30 or -5:30
            sign = 1 if tz_str[0] != "-" else -1
            parts = tz_str.lstrip("+-").split(":")
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            offset_seconds = sign * (hours * 3600 + minutes * 60)
        else:
            # Format: +9, -5, etc.
            offset_hours = int(tz_str)
            offset_seconds = offset_hours * 3600

        return timezone(timedelta(seconds=offset_seconds))

    def get_local_time(self, location_id: str) -> datetime:
        """Get current local time at a location."""
        location = self.get_location(location_id)
        if not location:
            raise ValueError(f"Location not found: {location_id}")

        tz_str = location.get("timezone", "UTC+0")
        tz = self.parse_timezone(tz_str)

        # Get current time in that timezone
        utc_now = datetime.now(timezone.utc)
        local_time = utc_now.astimezone(tz)

        return local_time

    def get_local_time_str(
        self, location_id: str, format_str: str = "%H:%M:%S %Z"
    ) -> str:
        """Get formatted local time string for a location."""
        try:
            local_time = self.get_local_time(location_id)
            return local_time.strftime(format_str)
        except ValueError:
            return "Unknown"

    def get_time_difference(self, location1_id: str, location2_id: str) -> float:
        """
        Get time difference between two locations in hours.

        Returns:
            Hours ahead of location2 (negative if behind)
        """
        loc1 = self.get_location(location1_id)
        loc2 = self.get_location(location2_id)

        if not loc1 or not loc2:
            raise ValueError("One or both locations not found")

        tz1 = self.parse_timezone(loc1.get("timezone", "UTC+0"))
        tz2 = self.parse_timezone(loc2.get("timezone", "UTC+0"))

        # Get offset in seconds
        now = datetime.now(timezone.utc)
        offset1 = tz1.utcoffset(now).total_seconds() / 3600
        offset2 = tz2.utcoffset(now).total_seconds() / 3600

        return offset1 - offset2

    def get_location_info(self, location_id: str) -> str:
        """Get human-readable location information."""
        location = self.get_location(location_id)
        if not location:
            return f"Location not found: {location_id}"

        local_time = self.get_local_time_str(location_id, "%H:%M")

        info = [
            f"📍 {location['name']}",
            f"   Region: {location.get('region', 'Unknown')}",
            f"   Continent: {location.get('continent', 'Unknown')}",
            f"   Type: {location.get('type', 'Unknown')}",
            f"   Scale: {location.get('scale', 'Unknown')}",
            f"   Timezone: {location.get('timezone', 'Unknown')} (Local: {local_time})",
            f"   Description: {location['description'][:60]}...",
        ]

        return "\n".join(info)

    def find_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """
        Find shortest path between two locations using BFS.

        Returns:
            List of location IDs from start to end, or None if no path exists
        """
        from collections import deque

        if not self.get_location(start_id) or not self.get_location(end_id):
            return None

        if start_id == end_id:
            return [start_id]

        # Build adjacency graph
        graph = {}
        for loc in self.get_all_locations():
            loc_id = loc["id"]
            graph[loc_id] = []
            for conn in loc.get("connections", []):
                graph[loc_id].append(conn["to"])

        # BFS
        queue = deque([(start_id, [start_id])])
        visited = {start_id}

        while queue:
            current, path = queue.popleft()

            if current == end_id:
                return path

            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  # No path found

    def get_connections(self, location_id: str) -> List[Dict]:
        """Get list of connected locations from a location."""
        location = self.get_location(location_id)
        if not location:
            return []

        connections = []
        for conn in location.get("connections", []):
            target = self.get_location(conn["to"])
            if target:
                connections.append(
                    {
                        "id": conn["to"],
                        "name": target["name"],
                        "direction": conn["direction"],
                        "label": conn.get("label", ""),
                        "requires": conn.get("requires", None),
                    }
                )

        return connections

    def get_tiles(self, location_id: str) -> Dict[str, Any]:
        """Get tile content for a location."""
        location = self.get_location(location_id)
        if not location:
            return {}

        return location.get("tiles", {})

    def count_locations(self) -> int:
        """Count total locations."""
        return len(self.get_all_locations())

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about the location database."""
        locations = self.get_all_locations()

        stats = {
            "total": len(locations),
            "terrestrial": len(
                [l for l in locations if l.get("scale") == "terrestrial"]
            ),
            "orbital": len([l for l in locations if l.get("scale") == "orbital"]),
            "planetary": len([l for l in locations if l.get("scale") == "planetary"]),
            "stellar": len([l for l in locations if l.get("scale") == "stellar"]),
            "galactic": len([l for l in locations if l.get("scale") == "galactic"]),
            "cosmic": len([l for l in locations if l.get("scale") == "cosmic"]),
            "major_cities": len(
                [l for l in locations if l.get("type") == "major-city"]
            ),
            "landmarks": len(
                [l for l in locations if l.get("type") == "geographical-landmark"]
            ),
        }

        return stats


def main():
    """Test location service."""
    service = LocationService()

    print(f"✅ Loaded {service.count_locations()} locations")

    # Show statistics
    stats = service.get_statistics()
    print("\nLocation Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Example: Get info about Tokyo
    print("\n" + "=" * 60)
    print(service.get_location_info("L300-BJ10"))

    # Example: Find path from Tokyo to Sydney
    print("\n" + "=" * 60)
    path = service.find_path("L300-BJ10", "L300-FA00")
    if path:
        location_names = [service.get_location(loc_id)["name"] for loc_id in path]
        print(f"Path from Tokyo to Sydney ({len(path)} stops):")
        for i, name in enumerate(location_names, 1):
            print(f"  {i}. {name}")

    # Example: Get time differences
    print("\n" + "=" * 60)
    diff = service.get_time_difference("L300-BJ10", "L300-EA00")
    print(f"Time difference Tokyo → London: {diff:+.1f} hours")

    print("\nLocal times:")
    for loc_id in ["L300-BJ10", "L300-EA00", "L300-DA00"]:
        loc = service.get_location(loc_id)
        time_str = service.get_local_time_str(loc_id)
        print(f"  {loc['name']:30} {time_str}")


if __name__ == "__main__":
    main()
