"""
uDOS v1.0.20b - TILE Command Handler

Enhanced TILE command for v1.0.20b mapping system with full geographic data integration.
Works with countries, cities, timezones, terrain, climate, and reference data.

Commands:
- TILE INFO <location>     - Get comprehensive location info
- TILE SEARCH <query>      - Search cities/countries
- TILE ROUTE <from> <to>   - Enhanced route planning with terrain/climate
- TILE WEATHER <location>  - Climate and weather info
- TILE CONVERT <value> <from> <to> - Unit conversions
- TILE NEARBY <location> <radius> - Find nearby cities
- TILE TIMEZONE <location> - Detailed timezone info
- TILE TERRAIN <location>  - Terrain type and details

Version: 1.0.20b
Integration: v1.0.20 4-Tier Knowledge Bank + v1.0.3 Mapping System
"""

from .base_handler import BaseCommandHandler
import json
from pathlib import Path
from datetime import datetime
import math
from core.output.syntax_highlighter import highlight_syntax


class TILECommandHandler(BaseCommandHandler):
    """Enhanced TILE system with full geographic data integration."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._geography_data = None
        self._reference_data = None
        self._graphics_data = None

    @property
    def geography_data(self):
        """Lazy load geography databases."""
        if self._geography_data is None:
            geo_path = Path("core/data/geography")
            self._geography_data = {
                "countries": self._load_json(geo_path / "countries.json"),
                "cities": self._load_json(geo_path / "cities.json"),
                "timezones": self._load_json(geo_path / "timezones.json"),
                "terrain": self._load_json(geo_path / "terrain.json"),
                "climate": self._load_json(geo_path / "climate.json")
            }
        return self._geography_data

    @property
    def reference_data(self):
        """Lazy load reference databases."""
        if self._reference_data is None:
            ref_path = Path("core/data/reference")
            self._reference_data = {
                "metric": self._load_json(ref_path / "metric.json"),
                "imperial": self._load_json(ref_path / "imperial.json")
            }
        return self._reference_data

    def _load_json(self, file_path):
        """Load JSON file safely."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
        return {}

    def handle(self, command, params, grid):
        """Route TILE commands to appropriate handlers."""
        try:
            if command == "INFO":
                return self._handle_info(params)
            elif command == "SEARCH":
                return self._handle_search(params)
            elif command == "ROUTE":
                return self._handle_route(params)
            elif command == "WEATHER":
                return self._handle_weather(params)
            elif command == "CONVERT":
                return self._handle_convert(params)
            elif command == "NEARBY":
                return self._handle_nearby(params)
            elif command == "TIMEZONE":
                return self._handle_timezone(params)
            elif command == "TERRAIN":
                return self._handle_terrain(params)
            elif command == "HELP":
                return self._handle_help()
            else:
                return f"Unknown TILE command: {command}\nUse TILE HELP for available commands."
        except Exception as e:
            return f"TILE command error: {str(e)}"

    def _handle_info(self, params):
        """Get comprehensive location information."""
        if not params:
            return "Usage: TILE INFO <city_name> or TILE INFO <country_code>"

        query = params.strip().upper()

        # Search cities
        cities_data = self.geography_data.get("cities", {})
        for city in cities_data.get("cities", []):
            if query in city["name"].upper() or query == city.get("tizo_code", "").upper():
                return self._format_city_info(city)

        # Search countries
        countries_data = self.geography_data.get("countries", {})
        for country in countries_data.get("countries", []):
            if query == country["code"] or query in country["name"].upper():
                return self._format_country_info(country)

        return f"Location not found: {params}\nTry TILE SEARCH {params}"

    def _format_city_info(self, city):
        """Format detailed city information."""
        result = f"""🏙️  {city['name']}, {city['country']}
{'='*50}
📍 Location:
   Coordinates: {city['lat']:.4f}°, {city['lon']:.4f}°
   TIZO Code: {city.get('tizo_code', 'N/A')}
   Elevation: {city.get('elevation_m', 'N/A')} meters

🌍 Demographics:
   Population: {city.get('population', 'N/A'):,}
   Region: {city.get('region', 'N/A')}

🌡️  Climate:
   Type: {city.get('climate', 'N/A')}

🕐 Time:
   Timezone: {city.get('timezone', 'N/A')}
"""
        return result

    def _format_country_info(self, country):
        """Format detailed country information."""
        result = f"""🌏 {country['name']}
{'='*50}
🏛️  Basic Info:
   ISO Code: {country['code']} / {country.get('code3', 'N/A')}
   Capital: {country.get('capital', 'N/A')}
   Region: {country.get('region', 'N/A')}

📍 Geography:
   Coordinates: {country.get('lat', 'N/A')}°, {country.get('lon', 'N/A')}°
   Area: {country.get('area', 'N/A'):,} km²

🌍 Demographics:
   Population: {country.get('population', 'N/A'):,}

💬 Languages: {', '.join(country.get('languages', []))}
💰 Currency: {country.get('currency', 'N/A')}
🕐 Timezone: {country.get('timezone', 'N/A')}
"""
        return result

    def _handle_search(self, params):
        """Search for cities or countries."""
        if not params:
            return "Usage: TILE SEARCH <query>"

        query = params.strip().upper()
        results = []

        # Search cities
        cities_data = self.geography_data.get("cities", {})
        for city in cities_data.get("cities", []):
            if query in city["name"].upper():
                results.append(f"🏙️  {city['name']}, {city['country']} (TIZO: {city.get('tizo_code', 'N/A')})")

        # Search countries
        countries_data = self.geography_data.get("countries", {})
        for country in countries_data.get("countries", []):
            if query in country["name"].upper():
                results.append(f"🌏 {country['name']} ({country['code']})")

        if not results:
            return f"No results found for: {params}"

        return f"🔍 Search Results ({len(results)}):\n" + "\n".join(results[:20])

    def _handle_timezone(self, params):
        """Get detailed timezone information."""
        if not params:
            return "Usage: TILE TIMEZONE <location>"

        query = params.strip()
        timezones_data = self.geography_data.get("timezones", {})

        # Search for timezone
        for tz in timezones_data.get("timezones", []):
            if query.upper() in tz["iana_name"].upper() or any(query.upper() in city.upper() for city in tz.get("cities", [])):
                result = f"""🕐 {tz['iana_name']}
{'='*50}
⏰ Time Offsets:
   Standard: UTC{tz['utc_offset']}
   DST: UTC{tz['utc_offset_dst']}
   Zone: {tz['zone_abbr']}

🌍 DST Information:
   Active: {'Yes' if tz['dst_active'] else 'No'}"""

                if tz['dst_active']:
                    result += f"""
   Starts: {tz.get('dst_start', 'N/A')}
   Ends: {tz.get('dst_end', 'N/A')}"""

                result += f"""

🏙️  Major Cities: {', '.join(tz.get('cities', [])[:5])}
🌏 Countries: {', '.join(tz.get('countries', []))}
"""
                return result

        return f"Timezone not found for: {params}"

    def _handle_terrain(self, params):
        """Get terrain type information."""
        if not params:
            # List all terrain types
            terrain_data = self.geography_data.get("terrain", {})
            types = terrain_data.get("terrain_types", [])

            result = "🗺️  Terrain Types:\n" + "="*50 + "\n"
            for t in types:
                result += f"{t['ascii_char']} {t['name']} - {t['description']}\n"
            return result

        # Get specific terrain info
        query = params.strip().lower().replace(" ", "_")
        terrain_data = self.geography_data.get("terrain", {})

        for t in terrain_data.get("terrain_types", []):
            if query == t['id'] or query in t['name'].lower():
                result = f"""🗺️  {t['name']} Terrain
{'='*50}
🎨 Visuals:
   ASCII: {t['ascii_char']}
   Symbol: {t['map_symbol']}
   Color: {t['color_code']}

📐 Elevation Range: {t['elevation_range']['min']}m to {t['elevation_range']['max']}m
🚶 Traversable: {'Yes' if t['traversable'] else 'No'}
💧 Water Source: {'Yes' if t['water_source'] else 'No'}

📝 Description: {t['description']}
"""
                return result

        return f"Terrain type not found: {params}"

    def _handle_weather(self, params):
        """Get climate information for a location."""
        if not params:
            return "Usage: TILE WEATHER <location>"

        query = params.strip().upper()

        # Find city and its climate
        cities_data = self.geography_data.get("cities", {})
        for city in cities_data.get("cities", []):
            if query in city["name"].upper() or query == city.get("tizo_code", "").upper():
                climate_type = city.get("climate", "").lower().replace(" ", "_")

                # Get climate details
                climate_data = self.geography_data.get("climate", {})
                for zone in climate_data.get("climate_zones", []):
                    if climate_type in zone['id'] or climate_type in zone['name'].lower():
                        result = f"""🌡️  Climate: {city['name']}, {city['country']}
{'='*50}
🌍 Climate Type: {zone['name']} ({zone['koppen_code']})

🌡️  Temperature Range: {zone['temp_range_c']['min']}°C to {zone['temp_range_c']['max']}°C
🌧️  Annual Rainfall: {zone['annual_rainfall_mm']['min']}-{zone['annual_rainfall_mm']['max']}mm

📝 Description: {zone['description']}
🌿 Vegetation: {zone['vegetation']}
📅 Seasons: {zone['season_count']}

📍 Similar Locations: {', '.join(zone['example_locations'])}
"""
                        return result

                return f"Climate data available: {city['climate']}\n(Detailed climate info not found)"

        return f"Location not found: {params}"

    def _handle_convert(self, params):
        """Convert between measurement units."""
        if not params:
            return """Usage: TILE CONVERT <value> <from_unit> <to_unit>

Examples:
  TILE CONVERT 100 km mi
  TILE CONVERT 32 C F
  TILE CONVERT 5 kg lb

Use TILE CONVERT HELP for unit list"""

        parts = params.strip().split()
        if len(parts) < 3:
            return "Usage: TILE CONVERT <value> <from_unit> <to_unit>"

        try:
            value = float(parts[0])
            from_unit = parts[1].lower()
            to_unit = parts[2].lower()

            # Temperature conversions
            if from_unit == 'c' and to_unit == 'f':
                result = (value * 9/5) + 32
                return f"{value}°C = {result:.2f}°F"
            elif from_unit == 'f' and to_unit == 'c':
                result = (value - 32) * 5/9
                return f"{value}°F = {result:.2f}°C"
            elif from_unit == 'c' and to_unit == 'k':
                result = value + 273.15
                return f"{value}°C = {result:.2f}K"
            elif from_unit == 'k' and to_unit == 'c':
                result = value - 273.15
                return f"{value}K = {result:.2f}°C"

            # Length conversions
            elif from_unit == 'km' and to_unit in ['mi', 'miles']:
                result = value * 0.621371
                return f"{value} km = {result:.2f} miles"
            elif from_unit in ['mi', 'miles'] and to_unit == 'km':
                result = value * 1.60934
                return f"{value} miles = {result:.2f} km"
            elif from_unit == 'm' and to_unit in ['ft', 'feet']:
                result = value * 3.28084
                return f"{value} m = {result:.2f} feet"
            elif from_unit in ['ft', 'feet'] and to_unit == 'm':
                result = value * 0.3048
                return f"{value} feet = {result:.2f} m"

            # Mass conversions
            elif from_unit == 'kg' and to_unit in ['lb', 'lbs']:
                result = value * 2.20462
                return f"{value} kg = {result:.2f} lbs"
            elif from_unit in ['lb', 'lbs'] and to_unit == 'kg':
                result = value * 0.453592
                return f"{value} lbs = {result:.2f} kg"

            else:
                return f"Conversion not supported: {from_unit} to {to_unit}"

        except ValueError:
            return "Invalid value. Use a number."

    def _handle_nearby(self, params):
        """Find nearby cities."""
        if not params:
            return "Usage: TILE NEARBY <location> [radius_km]"

        parts = params.strip().split()
        query = parts[0].upper()
        radius_km = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 500

        # Find source city
        cities_data = self.geography_data.get("cities", {})
        source_city = None

        for city in cities_data.get("cities", []):
            if query in city["name"].upper() or query == city.get("tizo_code", "").upper():
                source_city = city
                break

        if not source_city:
            return f"City not found: {query}"

        # Find nearby cities
        nearby = []
        for city in cities_data.get("cities", []):
            if city == source_city:
                continue

            distance = self._calculate_distance(
                source_city["lat"], source_city["lon"],
                city["lat"], city["lon"]
            )

            if distance <= radius_km:
                nearby.append((distance, city))

        nearby.sort(key=lambda x: x[0])

        if not nearby:
            return f"No cities found within {radius_km}km of {source_city['name']}"

        result = f"🗺️  Cities near {source_city['name']} (within {radius_km}km):\n"
        result += "="*50 + "\n"
        for dist, city in nearby[:10]:
            result += f"{dist:6.1f}km - {city['name']}, {city['country']}\n"

        return result

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c

        return distance

    def _handle_route(self, params):
        """Enhanced route planning with terrain and climate."""
        if not params:
            return "Usage: TILE ROUTE <from> <to>"

        parts = params.strip().split()
        if len(parts) < 2:
            return "Usage: TILE ROUTE <from> <to>"

        from_query = parts[0].upper()
        to_query = parts[1].upper()

        # Find cities
        cities_data = self.geography_data.get("cities", {})
        from_city = None
        to_city = None

        for city in cities_data.get("cities", []):
            if from_query in city["name"].upper() or from_query == city.get("tizo_code", "").upper():
                from_city = city
            if to_query in city["name"].upper() or to_query == city.get("tizo_code", "").upper():
                to_city = city

        if not from_city:
            return f"Start city not found: {from_query}"
        if not to_city:
            return f"Destination city not found: {to_query}"

        # Calculate route
        distance = self._calculate_distance(
            from_city["lat"], from_city["lon"],
            to_city["lat"], to_city["lon"]
        )

        # Calculate bearing
        bearing = self._calculate_bearing(
            from_city["lat"], from_city["lon"],
            to_city["lat"], to_city["lon"]
        )

        result = f"""🧭 Route: {from_city['name']} → {to_city['name']}
{'='*50}
📍 From: {from_city['name']}, {from_city['country']}
   TIZO: {from_city.get('tizo_code', 'N/A')}
   Timezone: {from_city.get('timezone', 'N/A')}
   Climate: {from_city.get('climate', 'N/A')}

📍 To: {to_city['name']}, {to_city['country']}
   TIZO: {to_city.get('tizo_code', 'N/A')}
   Timezone: {to_city.get('timezone', 'N/A')}
   Climate: {to_city.get('climate', 'N/A')}

📏 Distance: {distance:.1f} km ({distance*0.621371:.1f} miles)
🧭 Bearing: {bearing:.1f}° ({self._bearing_to_direction(bearing)})
"""
        return result

    def _calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calculate bearing between two points."""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)

        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360) % 360

    def _bearing_to_direction(self, bearing):
        """Convert bearing to compass direction."""
        directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = round(bearing / 45) % 8
        return directions[index]

    def _handle_help(self):
        """Display TILE command help."""
        help_text = """🗺️  TILE System Commands (v1.0.20b)
{'='*50}

📍 Location Information:
   TILE INFO <location>     - Comprehensive location data
   TILE SEARCH <query>      - Search cities and countries
   TILE NEARBY <loc> [km]   - Find nearby cities

🌍 Geographic Data:
   TILE WEATHER <location>  - Climate and weather info
   TILE TIMEZONE <location> - Detailed timezone data
   TILE TERRAIN <type>      - Terrain type information

🧭 Navigation:
   TILE ROUTE <from> <to>   - Route planning with details

🔧 Tools:
   TILE CONVERT <val> <from> <to> - Unit conversions

Examples:
"""
        # Add highlighted examples
        help_text += f"  {highlight_syntax('TILE(INFO|Tokyo)')}\n"
        help_text += f"  {highlight_syntax('TILE(SEARCH|Paris)')}\n"
        help_text += f"  {highlight_syntax('TILE(NEARBY|London|500)')}\n"
        help_text += f"  {highlight_syntax('TILE(WEATHER|Sydney)')}\n"
        help_text += f"  {highlight_syntax('TILE(TIMEZONE|New_York)')}\n"
        help_text += f"  {highlight_syntax('TILE(ROUTE|Tokyo|London)')}\n"
        help_text += f"  {highlight_syntax('TILE(CONVERT|100|km|mi)')}\n"
        help_text += f"  {highlight_syntax('TILE(TERRAIN|ocean)')}\n"
        help_text += "\nIntegration: Works with v1.0.20 Knowledge Bank & v1.0.3 MAP system"

        return help_text


# Export handler
__all__ = ['TILECommandHandler']
