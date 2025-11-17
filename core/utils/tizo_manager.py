#!/usr/bin/env python3
"""
TIZO Location Code System - Timezone-Integrated Zone Optimization

Utility for detecting nearest TIZO city and setting up user location codes.
Integrates with uDOS worldmap and city database.

Version: 1.0.0
Author: Fred Porter
"""

import json
import math
import os
import time
from pathlib import Path
from datetime import datetime, timezone


class TIZOLocationManager:
    """Manage TIZO location codes and nearest city detection."""

    def __init__(self, data_dir="knowledge/system"):
        self.data_dir = Path(data_dir)
        self.tizo_cities = self.load_tizo_cities()
        self.worldmap = self.load_worldmap()

    def load_tizo_cities(self):
        """Load TIZO cities database."""
        tizo_file = self.data_dir / "tizo_cities.json"
        if tizo_file.exists():
            with open(tizo_file, 'r') as f:
                return json.load(f)
        return {}

    def load_worldmap(self):
        """Load worldmap data."""
        worldmap_file = self.data_dir / "worldmap.json"
        if worldmap_file.exists():
            with open(worldmap_file, 'r') as f:
                return json.load(f)
        return {}

    def detect_system_timezone(self):
        """Detect system timezone automatically."""
        try:
            # Get system timezone
            local_tz = time.tzname
            utc_offset = time.timezone / -3600  # Convert to hours, flip sign

            # Format offset
            offset_hours = int(utc_offset)
            offset_minutes = int((abs(utc_offset) - abs(offset_hours)) * 60)
            offset_str = f"{'+' if utc_offset >= 0 else '-'}{abs(offset_hours):02d}:{offset_minutes:02d}"

            return {
                "timezone_name": local_tz[0] if local_tz else "UTC",
                "offset": offset_str,
                "utc_offset_hours": utc_offset
            }
        except Exception:
            return {
                "timezone_name": "UTC",
                "offset": "+00:00",
                "utc_offset_hours": 0
            }

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula."""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Earth radius in kilometers
        r = 6371
        return c * r

    def find_nearest_tizo_city(self, lat, lon, max_distance_km=500):
        """Find nearest TIZO city to given coordinates."""
        if not self.tizo_cities.get("TIZO_CITIES"):
            return None

        nearest_city = None
        min_distance = float('inf')

        for code, city_data in self.tizo_cities["TIZO_CITIES"].items():
            city_lat = city_data["coordinates"]["lat"]
            city_lon = city_data["coordinates"]["lon"]

            distance = self.calculate_distance(lat, lon, city_lat, city_lon)

            if distance < min_distance and distance <= max_distance_km:
                min_distance = distance
                nearest_city = {
                    "code": code,
                    "name": city_data["name"],
                    "country": city_data["country"],
                    "distance_km": round(distance, 1),
                    "timezone": city_data["timezone"],
                    "timezone_offset": city_data["timezone_offset"],
                    "coordinates": city_data["coordinates"]
                }

        return nearest_city

    def get_city_by_timezone(self, timezone_offset):
        """Get TIZO cities matching a timezone offset."""
        if not self.tizo_cities.get("TIMEZONE_MAPPINGS"):
            return []

        matching_cities = []
        for tz_name, tz_data in self.tizo_cities["TIMEZONE_MAPPINGS"].items():
            if tz_data["offset"] == timezone_offset:
                for city_code in tz_data["cities"]:
                    if city_code in self.tizo_cities["TIZO_CITIES"]:
                        city_data = self.tizo_cities["TIZO_CITIES"][city_code]
                        matching_cities.append({
                            "code": city_code,
                            "name": city_data["name"],
                            "country": city_data["country"],
                            "timezone": tz_name,
                            "timezone_offset": timezone_offset
                        })

        return matching_cities

    def auto_detect_location(self):
        """Auto-detect user location based on system timezone."""
        system_tz = self.detect_system_timezone()

        # Try to find cities matching system timezone
        matching_cities = self.get_city_by_timezone(system_tz["offset"])

        if matching_cities:
            # For now, return the first matching major city
            # In a real implementation, this could be enhanced with IP geolocation
            recommended = matching_cities[0]

            return {
                "recommended_city": recommended,
                "system_timezone": system_tz,
                "all_timezone_matches": matching_cities,
                "detection_method": "timezone_based"
            }
        else:
            # Fallback to UTC/London
            return {
                "recommended_city": {
                    "code": "UTC",
                    "name": "Coordinated Universal Time",
                    "country": "Global",
                    "timezone": "UTC",
                    "timezone_offset": "+00:00"
                },
                "system_timezone": system_tz,
                "all_timezone_matches": [],
                "detection_method": "fallback"
            }

    def get_nearby_cities(self, center_city_code, max_distance_km=2000):
        """Get nearby TIZO cities within specified distance."""
        if center_city_code not in self.tizo_cities.get("TIZO_CITIES", {}):
            return []

        center_city = self.tizo_cities["TIZO_CITIES"][center_city_code]
        center_lat = center_city["coordinates"]["lat"]
        center_lon = center_city["coordinates"]["lon"]

        nearby_cities = []

        for code, city_data in self.tizo_cities["TIZO_CITIES"].items():
            if code == center_city_code:
                continue

            city_lat = city_data["coordinates"]["lat"]
            city_lon = city_data["coordinates"]["lon"]

            distance = self.calculate_distance(center_lat, center_lon, city_lat, city_lon)

            if distance <= max_distance_km:
                nearby_cities.append({
                    "code": code,
                    "name": city_data["name"],
                    "country": city_data["country"],
                    "distance_km": round(distance, 1),
                    "timezone": city_data["timezone"],
                    "timezone_offset": city_data["timezone_offset"]
                })

        # Sort by distance
        nearby_cities.sort(key=lambda x: x["distance_km"])
        return nearby_cities

    def generate_user_profile_data(self, city_code=None):
        """Generate user profile data for a specific TIZO city."""
        if not city_code:
            detection = self.auto_detect_location()
            city_code = detection["recommended_city"]["code"]

        if city_code == "UTC":
            # Special case for UTC fallback
            return {
                "tizo_code": "UTC",
                "city_name": "Coordinated Universal Time",
                "country": "Global",
                "timezone": "UTC",
                "timezone_offset": "+00:00",
                "continent": "GLOBAL",
                "region": "Universal",
                "nearby_cities": [],
                "udos_layers": ["SURFACE", "CLOUD", "SATELLITE"],
                "connection_quality": {"global": "STANDARD"}
            }

        if city_code not in self.tizo_cities.get("TIZO_CITIES", {}):
            raise ValueError(f"Unknown TIZO city code: {city_code}")

        city_data = self.tizo_cities["TIZO_CITIES"][city_code]
        nearby_cities = self.get_nearby_cities(city_code, 2000)

        return {
            "tizo_code": city_code,
            "city_name": city_data["name"],
            "country": city_data["country"],
            "continent": city_data["continent"],
            "coordinates": city_data["coordinates"],
            "timezone": city_data["timezone"],
            "timezone_offset": city_data["timezone_offset"],
            "region": city_data["region"],
            "population_code": city_data["population_code"],
            "nearby_cities": nearby_cities[:5],  # Top 5 nearest
            "udos_layers": city_data["udos_layers"],
            "connection_quality": city_data["connection_quality"]
        }


def main():
    """Test the TIZO location system."""
    print("🌍 TIZO Location Code System Test")
    print("=" * 50)

    manager = TIZOLocationManager()

    # Test auto-detection
    print("\n🔍 Auto-detecting location...")
    detection = manager.auto_detect_location()

    print(f"System timezone: {detection['system_timezone']['timezone_name']} ({detection['system_timezone']['offset']})")
    print(f"Recommended city: {detection['recommended_city']['name']} ({detection['recommended_city']['code']})")
    print(f"Detection method: {detection['detection_method']}")

    # Test profile generation for Melbourne (current user)
    print("\n📍 Generating profile for Melbourne (MEL)...")
    mel_profile = manager.generate_user_profile_data("MEL")

    print(f"TIZO Code: {mel_profile['tizo_code']}")
    print(f"City: {mel_profile['city_name']}, {mel_profile['country']}")
    print(f"Timezone: {mel_profile['timezone']} ({mel_profile['timezone_offset']})")
    print(f"Continent: {mel_profile['continent']}")
    print(f"Nearby cities: {[city['name'] for city in mel_profile['nearby_cities'][:3]]}")

    # Test nearby cities
    print(f"\n🗺️  Cities near Melbourne:")
    nearby = manager.get_nearby_cities("MEL", 1500)
    for city in nearby[:5]:
        print(f"  {city['name']} ({city['code']}) - {city['distance_km']} km")

    print(f"\n✅ TIZO system test complete!")


if __name__ == "__main__":
    main()
